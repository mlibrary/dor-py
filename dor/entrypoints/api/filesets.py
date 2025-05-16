import json

from typing import Annotated
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from dor.providers.filesets import queues, setup_job_dir, creates_a_file_set_from_uploaded_materials
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
    job_idx = job_dir.name

    # TODO: Think about how we want to handle logging
    # with (job_dir / "fileset.log").open("a") as log:
    #     log.write(f'[{now()}] - (totally fake) {profile} - Processing Queued for fileset: {name} [fsid: {fsid.identifier}]\n')

    queues.get("fileset").enqueue(creates_a_file_set_from_uploaded_materials, fsid, int(job_idx), file_profiles_)

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
