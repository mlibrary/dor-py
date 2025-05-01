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
import time

from pathlib import Path
from datetime import datetime
from fastapi import UploadFile
from redis import Redis
from rq import Queue

from dor.config import config
from dor.providers.file_set_identifier import FileSetIdentifier

# FIXME: Move redis connection to a service?
redis = Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db)

# TODO: Move profile registry? Build out as a member of something? Leave here?
profiles: dict[str, Queue] = {
    "basic-image": Queue("fileset.basic-image", connection=redis),
    "bogus-profile": Queue("fileset.bogus-profile", connection=redis),
}


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


# This is the real "job":
def process_fileset(fsid: FileSetIdentifier, job_idx: int, profile: str):
    job_dir = fileset_workdir(fsid) / str(job_idx)
    src_dir = job_dir / "src"
    build_dir = job_dir / "build"

    (build_dir / "technical.md").write_text(f'technical metadata for {fsid.basename}\n')
    (build_dir / "descriptive.mets.xml").write_text(f'<?xml version="1.0" encoding="UTF-8" ?>\n<mets>descriptive metadata for {fsid.basename}</mets>\n')
    for file in src_dir.glob('*'):
        (build_dir / file.name).write_bytes(file.read_bytes())

    with (job_dir / "fileset.log").open("a") as log:
        log.write(f'[{now()}] - (totally fake) {profile} - File Set tagged as part of project: {fsid.project_id}\n')
        log.write(f'[{now()}] - (totally fake) {profile} - Doing some pretend work...\n')
        time.sleep(2)
        log.write(f'[{now()}] - (totally fake) {profile} - File Set processing complete in <some amount of time>\n')
