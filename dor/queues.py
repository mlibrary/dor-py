from redis import Redis
from rq import Queue

from dor.config import config


redis = Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db)

queues: dict[str, Queue] = {
    "fileset": Queue("fileset", connection=redis),
    "automation": Queue("automation", connection=redis),
    "package": Queue("package", connection=redis),
    "ingest": Queue("ingest", connection=redis)
}
