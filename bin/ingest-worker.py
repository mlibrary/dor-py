#!/usr/bin/env python
import json
import pika
from datetime import datetime

from dor.config import config
from dor.providers.ingest import ingest_package

inbox_path = config.inbox_path

conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=config.rabbitmq.host,
    credentials=pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
))

channel = conn.channel()
channel.queue_declare('packaging')
channel.queue_declare('ingest')


def route_message(ch, method, properties, body):
    if properties.type == 'package.generated':
        handle_package_generated(json.loads(body.decode("utf-8")))
    else:
        print(properties)
        print(body.decode("utf-8"))

def handle_package_generated(message):
    # Consider translating to an explicit ingest command
    ingest_package(message["package_identifier"])

## This should listen to a topic, rather than packaging's work queue
channel.basic_consume(queue='packaging', on_message_callback=route_message, auto_ack=True)
channel.start_consuming()
