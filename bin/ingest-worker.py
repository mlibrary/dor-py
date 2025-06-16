#!/usr/bin/env python
import json
import pika

from dor.config import config
from dor.providers.ingest import ingest_package

inbox_path = config.inbox_path

conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=config.rabbitmq.host,
    credentials=pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
))

channel = conn.channel()
channel.queue_declare('ingest.work')


def route_message(ch, method, properties, body):
    if properties.type == 'package.ingest':
        handle_package_ingest(json.loads(body.decode("utf-8")))
    else:
        print(properties)
        print(body.decode("utf-8"))


def handle_package_ingest(message):
    ingest_package(message["package_identifier"])


channel.basic_consume(queue='ingest.work', on_message_callback=route_message, auto_ack=True)
channel.start_consuming()
