from dataclasses import dataclass
import uuid
from typing import Any

from dor.domain.models import Bin

@dataclass
class BinSummary:
    identifier: uuid.UUID
    alternate_identifiers: list[str]
    common_metadata: dict[str, Any]


def summarize(bin: Bin):
    return BinSummary(
        identifier=bin.identifier,
        alternate_identifiers=bin.alternate_identifiers,
        common_metadata=bin.common_metadata
    )

