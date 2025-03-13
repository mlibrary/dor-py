from dor.adapters.converter import converter

from dor.domain.models import Revision


def summarize(revision: Revision):
    return converter.unstructure(dict(
        identifier=revision.identifier,
        alternate_identifiers=revision.alternate_identifiers,
        revision_number=revision.revision_number,
        created_at=revision.created_at,
        common_metadata=revision.common_metadata
    ))

def get_file_sets(revision: Revision):
    return [
        converter.unstructure(resource)
        for resource in revision.package_resources if resource.type == 'File Set'
    ]
