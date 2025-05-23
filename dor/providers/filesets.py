# This is definitely not the way or place to do this...
#
# There are lots of things here:
#
#   - setup/bootstrapping for the redis connection
#   - a profile/job registry
#   - a dependency on "workspaces_path", and general workspace prep
#   - some general "process fileset" logic, and a simulation of the one profile/job
#
# But it does give a way to enqueue the job from the API, and get set up to run
# it from the worker out in fileset-processor.py. Everything can be moved around
# and partitioned better as we go.
import re

from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

from dor.config import config
from dor.providers.operations import (
    AppendUses,
    CompressSourceImage,
    CreateTextAnnotationData,
    ExtractImageText,
    ExtractImageTextCoordinates
)
from dor.providers.build_file_set import build_file_set, Input, Command
from dor.providers.file_set_identifier import FileSetIdentifier


# Utility method, where should it live?
def fileset_workdir(fsid: FileSetIdentifier):
    return config.filesets_path / fsid.identifier


# Setup is used to drop the source files as they come in, needed from API
def setup_job_dir(fsid: FileSetIdentifier, files: list[UploadFile]) -> Path:
    basepath = fileset_workdir(fsid)
    basepath.mkdir(parents=True, exist_ok=True)
    p = re.compile(r'\d+')
    jobs = [int(d.name) for d in
            basepath.glob('*') if d.is_dir() and p.match(d.name)]
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


# FIXME: how do we ask what time is "now", globally?
def now():
    return datetime.now().isoformat()


PROFILE_COMMANDS: dict[str, list[Command]] = {
    "compress-source": [Command(operation=CompressSourceImage, kwargs={})],
    "extract-text": [
        Command(operation=ExtractImageTextCoordinates, kwargs={}),
        Command(operation=ExtractImageText, kwargs={}),
        Command(operation=CreateTextAnnotationData, kwargs={})
    ],
    "extract-text-plain": [
        Command(operation=ExtractImageText, kwargs={}),
    ],
    "label-service": [
        Command(operation=AppendUses, kwargs={
            "target": {
                "function": ["function:source"],
                "format": "format:text-plain"
            },
            "uses": ["function:service"]
        })
    ]
}


# This is the real "job":
def creates_a_file_set_from_uploaded_materials(
    fsid: FileSetIdentifier, job_idx: int, file_profiles: dict[str, list[str]]
):
    job_dir = fileset_workdir(fsid) / str(job_idx)
    src_dir = job_dir / "src"
    build_dir = job_dir / "build"

    inputs = []
    for file_name in file_profiles.keys():
        profiles = file_profiles[file_name]
        file_commands = [command for profile in profiles for command in PROFILE_COMMANDS[profile]]
        inputs.append(Input(file_path=src_dir / file_name, commands=file_commands))

    success = build_file_set(file_set_identifier=fsid, inputs=inputs, output_path=build_dir)
