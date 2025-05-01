from typing import Annotated
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from dor.providers.filesets import profiles, setup_job_dir, now, process_fileset
from dor.providers.file_set_identifier import FileSetIdentifier

filesets_router = APIRouter(prefix="/filesets")


@filesets_router.post("/")
async def create_fileset(
    files: Annotated[list[UploadFile], File(description="Source files to process into a fileset; often a single file, but may include supplemental configuration or metadata. The first will be considered primary.")],
    name: Annotated[str, Form(description="The name of the fileset; typically the name of the primary file")],
    collection: Annotated[str, Form(description="The collection to which this file or item will notionally belong")],
    profile: Annotated[str, Form(description="The profile of this file/fileset; determines the processing to conduct and type of result")],
):
    if profile not in profiles:
        raise HTTPException(status_code=400, detail="Invalid File Set Profile requested")

    id = FileSetIdentifier(project_id=collection, file_name=name).identifier
    job_dir = setup_job_dir(id, files)
    job_idx = job_dir.name

    with (job_dir / "fileset.log").open("a") as log:
        log.write(f'[{now()}] - (totally fake) {profile} - Processing Queued for fileset: {name}\n')

    profiles.get(profile).enqueue(process_fileset, id, int(job_idx), collection, name, profile)

    return {
        "id": id,
        "coll": collection,
        "name": name,
        "profile": profile,
        "files": [file.filename for file in files],
        "job_path": job_dir.absolute(),
        "job_index": job_idx,
    }
