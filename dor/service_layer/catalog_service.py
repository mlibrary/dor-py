from pydantic_core import to_jsonable_python

from dor.domain.models import Revision


def summarize(revision: Revision):
    return to_jsonable_python(dict(
        identifier=revision.identifier,
        alternate_identifiers=revision.alternate_identifiers,
        revision_number=revision.revision_number,
        created_at=revision.created_at,
        common_metadata=revision.common_metadata
    ))

def get_file_sets(revision: Revision):
    return [
        to_jsonable_python(resource) 
        for resource in revision.package_resources if resource.type == 'Asset'
    ]
