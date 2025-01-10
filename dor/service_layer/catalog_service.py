import uuid
from typing import Any
from pydantic_core import to_jsonable_python

from dor.domain.models import Bin


def summarize(bin: Bin):
    return to_jsonable_python(dict(
        identifier=bin.identifier,
        alternate_identifiers=bin.alternate_identifiers,
        common_metadata=bin.common_metadata
    ))

def get_file_sets(bin: Bin):
    return [
        to_jsonable_python(resource) 
        for resource in bin.package_resources if resource.type == 'Asset'
    ]
