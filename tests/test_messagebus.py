import pytest
from domain.events import Event
from messagebus import get_message_bus
from service_layer.unit_of_work import UnitOfWork

# Sample events for testing
class PackageSubmittedEvent(Event):
    def __init__(self, package_identifier: str):
        self.package_identifier = package_identifier

def run_message_bus_test(event_class, event_data, use_rabbitmq=False, rabbitmq_url=None):
    message_bus = get_message_bus(use_rabbitmq=use_rabbitmq, rabbitmq_url=rabbitmq_url)
    
    handled_event = None
    def handler(event: Event, uow=None):
        nonlocal handled_event
        handled_event = event
    
    message_bus.register_event_handler(event_class, handler)
    
    uow = UnitOfWork()
    
    event = event_class(**event_data)
    message_bus.handle(event, uow)

    # Assert 
    assert handled_event is not None
    for key, value in event_data.items():
        assert getattr(handled_event, key) == value
    assert uow.pop_event() is None  # No more events after handling

# Test case for the InMemory
def test_in_memory_message_bus():
    event_data = {'package_identifier': 'object123'}
    run_message_bus_test(PackageSubmittedEvent, event_data, use_rabbitmq=False)

# Test case for the RabbitMQ
@pytest.mark.parametrize("use_rabbitmq", [True,False])
def test_rabbitmq_message_bus(use_rabbitmq):
    event_data = {'package_identifier': 'object123'}
    rabbitmq_url = "amqp://guest:guest@localhost:5672" if use_rabbitmq else None 
    run_message_bus_test(PackageSubmittedEvent, event_data, use_rabbitmq=use_rabbitmq, rabbitmq_url=rabbitmq_url)
