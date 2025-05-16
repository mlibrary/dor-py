#!/usr/bin/env python
from rq import Worker
from dor.providers.filesets import redis

# This is called generic-worker.py because I do not want to imply whether
# it would be specific to fileset processing or overall orchestration; we
# simply have not made any decisions on the dispatch or job-type boundaries.

w = Worker(['fileset'], connection=redis)
w.work()
