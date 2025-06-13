import json
import pika

from dataclasses import asdict
from typing import Union

from dor.config import config
from dor.domain import commands
from dor.domain import events

Message = Union[commands.Command, events.Event]

conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=config.rabbitmq.host,
    credentials=pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
))

channel = conn.channel()

channel.queue_declare('fileset')
channel.queue_declare('packaging')
channel.queue_declare('ingest')

router = {
    commands.CreatePackage: 'packaging',
    events.PackageGenerated: 'packaging'
}

def publish(message: Message) -> None:
    key = router.get(type(message))
    if key is None:
        raise Exception("Unhandled message type")

    props = pika.BasicProperties(type=message.type)
    channel.basic_publish(exchange='', routing_key=key, body=json.dumps(asdict(message)), properties=props)
