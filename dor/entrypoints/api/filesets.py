import json

from typing import Annotated, Optional
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from dor.adapters import eventpublisher
from dor.domain.commands import CreateFileset
from dor.providers.filesets import setup_job_dir, creates_a_file_set_from_uploaded_materials
from dor.providers.file_set_identifier import FileSetIdentifier

filesets_router = APIRouter(prefix="/filesets")


@filesets_router.post("/")
async def create_fileset(
    files: Annotated[list[UploadFile], File(description="Source files to process into a fileset; often a single file, but may include supplemental configuration or metadata. [DECIDE: Handle primary/supplemental together? Use first file as primary? Allow fileset name/id to be supplied separately?]")],
    name: Annotated[str, Form(description="PROVISIONAL: The name of the fileset; typically the name of the primary file")],
    project_id: Annotated[str, Form(description="The 'project' under which this file is being handled; often a shorthand for an upcoming collection to which this file or item will notionally belong")],
    file_profiles: Annotated[str, Form(description="A mapping of files to the profiles to execute on them")]
):
    file_profiles_ = json.loads(file_profiles)

    fsid = FileSetIdentifier(project_id=project_id, file_name=name)
    job_dir = setup_job_dir(fsid, files)
    job_idx = int(job_dir.name)

    # TODO: Think about how we want to handle logging
    # with (job_dir / "fileset.log").open("a") as log:
    #     log.write(f'[{now()}] - (totally fake) {profile} - Processing Queued for fileset: {name} [fsid: {fsid.identifier}]\n')

    eventpublisher.publish(
        CreateFileset(project_id, name, job_idx, file_profiles_)
    )

    return {
        "id": fsid.identifier,
        "project_id": project_id,
        "name": name,
        "alt_id": fsid.alternate_identifier,
        "file_profiles": file_profiles_,
        "files": [file.filename for file in files],
        "job_path": job_dir.absolute(),
        "job_index": job_idx,
    }


# TODO: Sample data for uploads To be replaced with real data from a database or other source
UPLOADS = [
    {
        "name": "file1.txt",
        "status": "completed",
        "project": "dor123",
        "isid": "batch001",
        "date": "2025-05-01",
    },
    {
        "name": "file2.txt",
        "status": "queued",
        "project": "dor123",
        "isid": "batch001",
        "date": "2025-05-02",
    },
    {
        "name": "file3.txt",
        "status": "failed",
        "project": "dor123",
        "isid": "batch001",
        "date": "2025-05-03",
    },
    {
        "name": "file4.txt",
        "status": "completed",
        "project": "dor123",
        "isid": "batch005",
        "date": "2025-05-04",
    },
    {
        "name": "file5.txt",
        "status": "queued",
        "project": "dor1234",
        "isid": "batch005",
        "date": "2025-05-05",
    },
]


@filesets_router.get("/status")
async def get_upload_status(
    project: str,  # Required parameter for project name like gage, tinder, etc.
    isid: Optional[str] = None,  # Optional batch or delivery ID for filtering
    group_by: Optional[str] = "isid",  # Group by 'isid', 'date', or 'status'
    status: Optional[str] = None,  # Optional filter by status (e.g., completed, queued)
):
    """
    Retrieve the upload status of filesets for a given project, optionally filtered
    by status, batch ID, and grouped by a specified field.
    """
    # Validate project existence
    filtered_uploads = [upload for upload in UPLOADS if upload["project"] == project]
    if not filtered_uploads:
        raise HTTPException(status_code=404, detail=f"Project '{project}' not found")

    # Apply optional filters
    if status:
        filtered_uploads = [
            upload for upload in filtered_uploads if upload["status"] == status
        ]
    if isid:
        filtered_uploads = [
            upload for upload in filtered_uploads if upload["isid"] == isid
        ]

    if not filtered_uploads:
        raise HTTPException(
            status_code=404,
            detail=f"No uploads found for project '{project}' with the specified filters",
        )

    # Group the results based on the provided group_by field
    grouped = {}
    valid_group_by_fields = {"status", "date", "isid"}
    if group_by not in valid_group_by_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid group_by value '{group_by}'. Must be one of {valid_group_by_fields}",
        )

    for upload in filtered_uploads:
        key = upload.get(group_by, "unknown")
        grouped.setdefault(key, []).append(upload)

    return grouped
