from uuid import UUID
from datetime import datetime

from cattrs import Converter
from sqlalchemy.orm import DeclarativeBase


converter = Converter()
converter.register_unstructure_hook(datetime, lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ"))
converter.register_structure_hook(datetime, lambda d, datetime: datetime.fromisoformat(d))

converter.register_unstructure_hook(UUID, lambda u: str(u))
converter.register_structure_hook(UUID, lambda u, UUID: UUID(u))


class Base(DeclarativeBase):
    pass
