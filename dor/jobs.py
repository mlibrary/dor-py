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

redis = Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db)
profiles: dict[str, Queue] = {
    "basic-image": Queue("fileset.basic-image", connection=redis),
    "bogus-profile": Queue("fileset.bogus-profile", connection=redis),
}


def fileset_workdir(id: str):
    return config.filesets_path / id


def setup_job_dir(id: str, files: list[UploadFile]) -> Path:
    basepath = fileset_workdir(id)
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


def now():
    return datetime.now().isoformat()

def process_fileset(id: str, job_idx: int, collection: str, name: str, profile: str):
    job_dir = fileset_workdir(id) / str(job_idx)
    src_dir = job_dir / "src"
    build_dir = job_dir / "build"

    (build_dir / "technical.md").write_text(f'technical metadata for {name}\n')
    (build_dir / "descriptive.mets.xml").write_text(f'<?xml version="1.0" encoding="UTF-8" ?>\n<mets>descriptive metadata for {name}</mets>\n')
    for file in src_dir.glob('*'):
        _ = (build_dir / file.name).write_bytes(file.read_bytes())

    with (job_dir / "fileset.log").open("a") as log:
        log.write(f'[{now()}] - (totally fake) {profile} - File Set tagged as destined for collection: {collection}.\n')
        log.write(f'[{now()}] - (totally fake) {profile} - Doing some pretend work...\n')
        time.sleep(2)
        log.write(f'[{now()}] - (totally fake) {profile} - File Set processing complete in <some amount of time>\n')
