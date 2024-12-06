from typing import List, Callable, Dict, Type
from domain.events import Event

class MessageBus:
    def __init__(self):
        # In-memory storage for event handlers
        self.event_handlers: Dict[Type[Event], List[Callable]] = {}

    def register_event_handler(self, event_type: Type[Event], handler: Callable):
        # Registers an event handler for a specific event type.
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def handle(self, message, uow=None):
        # Handles a message, which must be an event.
        if isinstance(message, Event):
            self._handle_event(message, uow)
        else:
            raise ValueError(f"Message of type {type(message)} is not a valid Event")

    def _handle_event(self, event: Event, uow=None):
        # Handles an event by executing its registered handlers.
        if event.__class__ in self.event_handlers:
            for handler in self.event_handlers[event.__class__]:
                handler(event, uow)
