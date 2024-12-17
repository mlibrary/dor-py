from dor.domain.events import Event
from gateway.repository_gateway import RepositoryGateway


class UnitOfWork:

    def __init__(self, gateway: RepositoryGateway) -> None:
        self.gateway = gateway
        self.events: list[Event] = []

    def add_event(self, event: Event):
        self.events.append(event)

    def pop_event(self) -> Event | None:
        if len(self.events) > 0:
            return self.events.pop(0)
        return None
