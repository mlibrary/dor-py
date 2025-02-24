from faker import Faker
from datetime import UTC

from .parts import get_faker, get_datetime

def build_event(event_type: str, linking_agent_type: str):
    fake = get_faker()
    return dict(
        identifier=fake.uuid4(),
        type=event_type,
        date_time=get_datetime(),
        detail=fake.sentence(),
        linking_agent=dict(type=linking_agent_type, value=fake.email()),
    )
