import pika
import json
from typing import List, Callable, Dict, Type
from domain.events import Event

class MessageBus:
    def __init__(self, rabbitmq_url: str):
        self.event_handlers: Dict[Type[Event], List[Callable]] = {}
        if rabbitmq_url:
            try:
                self.connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
                self.channel = self.connection.channel()
            except pika.exceptions.AMQPConnectionError as e:
                raise Exception(f"Failed to connect to RabbitMQ at {rabbitmq_url}: {e}")

    def register_event_handler(self, event_type: Type[Event], handler: Callable):
        # Registers an event handler for a specific event type.
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        # Declare a queue for each event type
        self.channel.queue_declare(queue=event_type.__name__)

    def handle(self, message, uow=None):
        # Handles a message, which must be an event.
        if isinstance(message, Event):
            self._handle_event(message, uow)
        else:
            raise ValueError(f"Message of type {type(message)} is not a valid Event")

    def _handle_event(self, event: Event, uow=None):
        # Handles an event by executing its registered handlers and sending to RabbitMQ.
        if event.__class__ in self.event_handlers:
            for handler in self.event_handlers[event.__class__]:
                # Call the registered event handler
                handler(event, uow)

                # Simulate sending event to RabbitMQ (In reality, you’d send it to a queue)
                self.channel.basic_publish(
                    exchange='',
                    routing_key=event.__class__.__name__,
                    body=json.dumps(event.__dict__)  # Serialize the event
                )

    def close(self):
        # Close the RabbitMQ connection.
        self.connection.close()
