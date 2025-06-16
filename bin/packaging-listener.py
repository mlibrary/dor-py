import json

import pika

from dor.adapters import eventpublisher
from dor.domain.commands import IngestPackage
from dor.config import config

conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=config.rabbitmq.host,
    credentials=pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
))

channel = conn.channel()

channel.exchange_declare('packaging', exchange_type='fanout')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(queue=queue_name, exchange="packaging")


def callback(ch, method, properties, body):
    print("topic callback")
    message = json.loads(body.decode('utf-8'))
    print(message)
    eventpublisher.publish(IngestPackage(
        package_identifier=message["package_identifier"]
    ))


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True
)

channel.start_consuming()