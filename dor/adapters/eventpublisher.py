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

channel.queue_declare('filesets.work')
channel.queue_declare('packaging.work')
channel.queue_declare('ingest.work')

channel.exchange_declare(exchange="filesets", exchange_type="fanout")
channel.exchange_declare(exchange="packaging", exchange_type="fanout")

router = {
    commands.CreateFileset: 'filesets.work',
    commands.CreatePackage: 'packaging.work',
    commands.DepositPackage: 'ingest.work',
}


def publish(command: commands.Command) -> None:
    key = router.get(type(command))
    if key is None:
        raise Exception("Unhandled message type")

    props = pika.BasicProperties(type=command.type)
    channel.basic_publish(
        exchange='',
        routing_key=key,
        body=json.dumps(asdict(command)),
        properties=props
    )


exchange_router: dict[type[events.Event], str] = {
    events.PackageGenerated: 'packaging',
    events.FileSetCreated: 'filesets',
}


def publish_to_exchange(event: events.Event) -> None:
    exchange = exchange_router.get(type(event))
    if exchange is None:
        raise Exception("Unhandled message type")

    props = pika.BasicProperties(type=event.type)
    channel.basic_publish(
        exchange=exchange,
        routing_key='',
        body=json.dumps(asdict(event)),
        properties=props
    )
