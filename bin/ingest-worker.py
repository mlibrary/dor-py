#!/usr/bin/env python
import json
from typing import Any

import pika

from dor.adapters import eventpublisher
from dor.config import config
from dor.domain.commands import DepositPackage
from dor.providers.ingest import ingest_package


conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=config.rabbitmq.host,
    credentials=pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
))

channel = conn.channel()


# Packaging events
channel.exchange_declare('packaging', exchange_type='fanout')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(queue=queue_name, exchange="packaging")


def handle_package_generated(message: dict[str, Any]):
    eventpublisher.publish(DepositPackage(
        package_identifier=message["package_identifier"]
    ))


def route_packaging_message(ch, method, properties, body):
    if properties.type == 'package.generated':
        handle_package_generated(json.loads(body.decode("utf-8")))
    else:
        print(properties)
        print(body.decode("utf-8"))


channel.basic_consume(
    queue=queue_name,
    on_message_callback=route_packaging_message,
    auto_ack=True
)


# Ingest commands
channel.queue_declare('ingest.work')


def route_ingest_message(ch, method, properties, body):
    if properties.type == 'package.deposit':
        handle_package_deposit(json.loads(body.decode("utf-8")))
    else:
        print(properties)
        print(body.decode("utf-8"))


def handle_package_deposit(message):
    ingest_package(message["package_identifier"])


channel.basic_consume(
    queue='ingest.work',
    on_message_callback=route_ingest_message,
    auto_ack=True
)

channel.start_consuming()

conn.close()
