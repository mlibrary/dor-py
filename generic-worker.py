#!/usr/bin/env python
from redis import Redis
from rq import Worker
import dor.jobs


# This is called generic-worker.py because I do not want to imply whether
# it would be specific to fileset processing or overall orchestration; we
# simply have not made any decisions on the dispatch or job-type boundaries.

w = Worker(['fileset.basic-image'], connection=dor.jobs.redis)
w.work()
