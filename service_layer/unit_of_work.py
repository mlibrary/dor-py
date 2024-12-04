# service_layer/unit_of_work.py

from domain.events import Event


class UnitOfWork:
    def __init__(self):
        self._events: list[Event] = []

    def add_event(self, event):
        self._events.append(event)

    def pop_event(self):
        return self._events.pop(0) if self._events else None

    def notify_subscriber(self):
        #  notify subscribers
        for event in self._events:
            print(f"Committing event: {event}")
        # clear the list once committed
        self._events.clear()

    def rollback(self):
        # In case of any error can the events be cleared?
        self._events.clear()

    def get_all_events(self):
        # Returns all events that were added to this unit of work.
        return self._events
    

