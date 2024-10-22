import os

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

def set_up_rabbitmq_broker():
    rabbitmq_url = os.environ.get("RABBITMQ_URL")
    if not rabbitmq_url:
        raise ValueError("RABBITMQ_URL environment variable not configured!")
    rabbitmq_broker = RabbitmqBroker(url=rabbitmq_url)
    dramatiq.set_broker(rabbitmq_broker)
