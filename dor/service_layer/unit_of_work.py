from dor.domain.events import Event
from gateway.fake_repository_gateway import FakeRepositoryGateway


class UnitOfWork:

    def __init__(self, gateway: FakeRepositoryGateway) -> None:
        self.gateway = gateway
        self.events: list[Event] = []

    def add_event(self, event: Event):
        self.events.append(event)

    def pop_event(self) -> Event | None:
        if len(self.events) > 0:
            return self.events.pop(0)
        return None