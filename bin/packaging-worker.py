#!/usr/bin/env python
import json
import pika
from datetime import datetime
from dor.providers import package_generator
from dor.providers.packages import create_package_from_metadata
from dor.providers.package_generator import DepositGroup
from dor.config import config

inbox_path = config.inbox_path
pending_path = config.filesets_path

conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=config.rabbitmq.host,
    credentials=pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
))

channel = conn.channel()
channel.queue_declare('packaging')


def route_message(ch, method, properties, body):
    if properties.type == 'package.create':
        handle_package_create(json.loads(body.decode("utf-8")))
    else:
        print(properties)
        print(body.decode("utf-8"))

def handle_package_create(message):
    deposit_group = DepositGroup(
        message["deposit_group_identifier"],
        datetime.fromisoformat(message["date"])
    )
    metadata = message["package_metadata"]

    create_package_from_metadata(
        deposit_group=deposit_group,
        package_metadata=metadata,
        inbox_path=inbox_path,
        pending_path=pending_path
    )

channel.basic_consume(queue='packaging', on_message_callback=route_message, auto_ack=True)
channel.start_consuming()
