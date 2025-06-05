from typing import Callable, Type, Union
from dor.domain.commands import Command
from dor.domain.events import Event
from dor.service_layer.unit_of_work import AbstractUnitOfWork

Message = Union[Command, Event]

class MemoryMessageBus:
    def __init__(
        self,
        event_handlers: dict[Type[Event], list[Callable]],
        command_handlers: dict[Type[Command], Callable]
    ):
        # In-memory storage for event handlers
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def register_event_handler(self, event_type: Type[Event], handler: Callable):
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)    

    def register_command_handler(self, command_type: Type[Command], handler: Callable):
        if command_type in self.command_handlers:
            raise CommandHandlerAlreadyRegistered(command_type)
        self.command_handlers[command_type] = handler

    def handle(self, message: Message, uow: AbstractUnitOfWork):
        # Handles a message, which must be an event.
        if isinstance(message, Event):
            self._handle_event(message, uow)
        elif isinstance(message, Command):
            return self._handle_command(message, uow)
        else:
            raise ValueError(f"Message of type {type(message)} is not a valid Command or Event")

    def _handle_event(self, event: Event, uow: AbstractUnitOfWork):
        # Handles an event by executing its registered handlers.
        if event.__class__ not in self.event_handlers:
            raise NoHandlerForEventError(f"No handler found for event type {type(event)}")
    
        queue = [event]
        while queue:
            next_event = queue.pop(0)
            for handler in self.event_handlers[type(next_event)]:
                handler(next_event, uow)
            another_event = uow.pop_event()
            if another_event:
                queue.append(another_event)

    def _handle_command(self, command: Command, uow: AbstractUnitOfWork):
        try:
            handler = self.command_handlers[type(command)]
            return handler(command, uow)
        except:
            # TODO: log missing command handler
            raise
              
class NoHandlerForEventError(Exception):
    pass

class CommandHandlerAlreadyRegistered(Exception):
    def __init__(self, command: Type[Command]):
        super().__init__(self._message(command))
        self.command = command

    def _message(self, command):
        return f"The command type '{command.__name__}' already has a handler registered; "
        "refusing to override."
