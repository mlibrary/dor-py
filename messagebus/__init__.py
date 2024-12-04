from messagebus.memory import MessageBus as InMemoryMessageBus
from messagebus.rabbitmq import MessageBus as RabbitMQMessageBus

# This helps to switch between in-memory and RabbitMQ.
def get_message_bus(use_rabbitmq=False, rabbitmq_url=None):
    if use_rabbitmq:
        if not rabbitmq_url:
            raise ValueError("RabbitMQ URL must be provided when using RabbitMQ.")
        return RabbitMQMessageBus(rabbitmq_url)
    return InMemoryMessageBus()
