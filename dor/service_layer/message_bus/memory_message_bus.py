from typing import Callable, Type
from dor.domain.events import Event
from dor.service_layer.unit_of_work import UnitOfWork


class MemoryMessageBus:
    def __init__(self, handlers: dict[Type[Event], list[Callable]]):
        # In-memory storage for event handlers
        self.event_handlers = handlers

    def register_event_handler(self, event_type: Type[Event], handler: Callable):
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)    

    def handle(self, message, uow: UnitOfWork):
        # Handles a message, which must be an event.
        if isinstance(message, Event):
            self._handle_event(message, uow)
        else:
            raise ValueError(f"Message of type {type(message)} is not a valid Event")

    def _handle_event(self, event: Event, uow: UnitOfWork):
        # Handles an event by executing its registered handlers.
        if event.__class__ not in self.event_handlers:
            raise NoHandlerForEventError(f"No handler found for event type {type(event)}")
    
        queue = [event]
        while queue:
            next_event = queue.pop(0)
            for handler in self.event_handlers[type(next_event)]:
                handler(next_event)
            another_event = uow.pop_event()
            if another_event:
                queue.append(another_event)
              
class NoHandlerForEventError(Exception):
    pass             