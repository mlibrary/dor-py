from typing import Any
from pydantic_core import to_jsonable_python

from dor.domain.models import Version


def summarize(version: Version):
    return to_jsonable_python(dict(
        identifier=version.identifier,
        alternate_identifiers=version.alternate_identifiers,
        common_metadata=version.common_metadata
    ))

def get_file_sets(version: Version):
    return [
        to_jsonable_python(resource) 
        for resource in version.package_resources if resource.type == 'Asset'
    ]
