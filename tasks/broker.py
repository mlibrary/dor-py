import os
from typing import Self

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

class DramatiqRabbitmqBroker:

    @classmethod
    def from_env(cls) -> Self:
        rabbitmq_url = os.environ.get("RABBITMQ_URL")
        if not rabbitmq_url:
            raise ValueError("RABBITMQ_URL environment variable not configured!")
        return cls(rabbitmq_url)

    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_broker = RabbitmqBroker(url=rabbitmq_url)
        dramatiq.set_broker(self.rabbitmq_broker)

    def set_up_queue(self, name: str):
        if name not in self.rabbitmq_broker.get_declared_queues():
            self.rabbitmq_broker.declare_queue(name)

