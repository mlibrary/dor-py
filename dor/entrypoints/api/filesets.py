import uuid
import hashlib
import re

from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, File, Form, UploadFile
from dor.config import config

filesets_router = APIRouter(prefix="/filesets")


def setup_job_dir(id: str, files: list[UploadFile]) -> Path:
    basepath = config.workspaces_path / id
    basepath.mkdir(parents=True, exist_ok=True)
    p = re.compile(r'\d+')
    jobs = [int(d.name) for d in basepath.glob('*') if d.is_dir() and p.match(d.name)]
    if len(jobs) > 0:
        job_idx = max(jobs) + 1
    else:
        job_idx = 1

    job_dir = basepath / str(job_idx)
    src_dir = job_dir / "src"
    build_dir = job_dir / "build"
    job_dir.mkdir()
    src_dir.mkdir()
    build_dir.mkdir()

    for file in files:
        (src_dir / file.filename).write_bytes(file.file.read())

    return job_dir


@filesets_router.post("/")
async def create_fileset(
    files: Annotated[list[UploadFile], File(description="Source files to process into a fileset; often a single file, but may include supplemental configuration or metadata. The first will be considered primary.")],
    name: Annotated[str, Form(description="The name of the fileset; typically the name of the primary file")],
    collection: Annotated[str, Form(description="The collection to which this file or item will notionally belong")],
    profile: Annotated[str, Form(description="The profile of this file/fileset; determines the processing to conduct and type of result")],
):
    id = str(uuid.UUID(hashlib.md5(f'{collection}:{name}'.encode()).hexdigest()))
    job_dir = setup_job_dir(id, files)
    job_idx = job_dir.name

    return {
        "id": id,
        "coll": collection,
        "name": name,
        "profile": profile,
        "files": [file.filename for file in files],
        "workspaces_path": config.workspaces_path,
        "job_path": job_dir.absolute(),
        "job_index": job_idx,
    }
