#!/usr/bin/env python
import json
import pika

from dor.config import config
from dor.providers.file_set_identifier import FileSetIdentifier
from dor.providers.filesets import creates_a_file_set_from_uploaded_materials

conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=config.rabbitmq.host,
    credentials=pika.PlainCredentials(config.rabbitmq.username, config.rabbitmq.password)
))

channel = conn.channel()
channel.queue_declare('filesets.work')

def handle_fileset_create(command):
    fsid = FileSetIdentifier(command["project_id"], command["file_name"])
    creates_a_file_set_from_uploaded_materials(
        fsid,
        command["job_idx"],
        command["file_profiles"]
    )

def route_message(ch, method, properties, body):
    if properties.type == 'fileset.create':
        handle_fileset_create(json.loads(body.decode("utf-8")))
    else:
        print(properties)
        print(body.decode("utf-8"))


channel.basic_consume(
    queue='filesets.work', on_message_callback=route_message, auto_ack=True
)
channel.start_consuming()

conn.close()
