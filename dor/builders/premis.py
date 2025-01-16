from faker import Faker
from datetime import UTC
from .parts import generate_uuid, Identifier


def build_event(event_type: str, linking_agent_type: str):
    fake = Faker()
    fake.seed_instance(1001)
    return dict(
        identifier=fake.uuid4(),
        type=event_type,
        date_time=fake.date_time(tzinfo=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        detail=fake.sentence(),
        linking_agent=dict(type=linking_agent_type, value=fake.email()),
    )
