import uuid
from dor.adapters.converter import converter

from dor.builders.parts import UseFunction
from dor.domain.models import Revision
from dor.providers.models import AlternateIdentifier


def summarize(revision: Revision):
    return converter.unstructure(dict(
        identifier=revision.identifier,
        alternate_identifiers=revision.alternate_identifiers,
        revision_number=revision.revision_number,
        created_at=revision.created_at,
        common_metadata=revision.common_metadata
    ))


def summarize_filesets(revision: Revision, file_set_identifier: uuid.UUID):
    referenced_file_set_identifier = AlternateIdentifier(
        type=UseFunction.copy_of.value,
        id=str(file_set_identifier)
    )
    return [
        str(resource.id)
        for resource in revision.package_resources
        if resource.id == file_set_identifier or referenced_file_set_identifier in resource.alternate_identifiers
    ]

def get_file_sets(revision: Revision):
    return [
        converter.unstructure(resource)
        for resource in revision.package_resources if resource.type == 'File Set'
    ]


def index_by_file_set(revisions: list[Revision], file_set_identifier: str):
    key = str(file_set_identifier)
    mapping = {key: []}
    referenced_file_set_identifier = AlternateIdentifier(
        type=UseFunction.copy_of.value,
        id=str(file_set_identifier)
    )

    for revision in revisions:
        for resource in revision.package_resources:
            if resource.id == file_set_identifier or \
                    referenced_file_set_identifier in resource.alternate_identifiers:
                mapping[key].append(dict(
                    file_set_identifier=str(resource.id),
                    bin_identifier=str(revision.identifier)
                ))

    return mapping


def summarize_with_file_sets(revisions: list[Revision], file_set_identifier: uuid.UUID):
    summaries = []
    for revision in revisions:
        summary = summarize(revision)
        summary['file_sets'] = summarize_filesets(revision, file_set_identifier)
        summaries.append(summary)
    return summaries