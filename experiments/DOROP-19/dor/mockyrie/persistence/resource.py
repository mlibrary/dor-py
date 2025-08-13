from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.dialects.postgresql import JSONB, JSONPATH
from sqlalchemy.sql import func

import datetime

class Base(DeclarativeBase):
    pass

class Resource(Base):
    __tablename__ = "mock_resource"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    internal_resource: Mapped[str]
    data: Mapped[dict] = mapped_column(JSONB)

    def __repr__(self) -> str:
        try:
            s = f"<{self.id} {self.data['metadata']['common']['title']}>"
        except:
            s = f"<{self.id} {self.__class__.__name__}>"
        return s
