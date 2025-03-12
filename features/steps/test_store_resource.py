import uuid
from functools import partial

from pytest_bdd import scenario, given, when, then

from dor.config import config
from dor.domain.events import PackageSubmitted
from dor.domain.models import WorkflowEventType
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import AbstractUnitOfWork


scenario = partial(scenario, '../store_resource.feature')


@scenario('Storing a new resource for immediate release')
def test_store_resource():
    pass


@given(u'a package containing the scanned pages, OCR, and metadata')
def _(unit_of_work: AbstractUnitOfWork):
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(path=config.storage_path)
    file_provider.create_directory(path=config.storage_path)
    file_provider.delete_dir_and_contents(path=config.workspaces_path)
    file_provider.create_directory(path=config.workspaces_path)

    unit_of_work.gateway.create_repository()


@when(
    u'the Collection Manager places the packaged resource in the incoming location',
    target_fixture="tracking_identifier"
)
def _(message_bus: MemoryMessageBus, unit_of_work: AbstractUnitOfWork):
    submission_id = "xyzzy-00000000-0000-0000-0000-000000000001-v1"
    tracking_identifier = str(uuid.uuid4())

    event = PackageSubmitted(
        package_identifier=submission_id,
        tracking_identifier=tracking_identifier
    )
    message_bus.handle(event, unit_of_work)
    return tracking_identifier


@then(u'the Collection Manager can see that it was preserved.')
def _(unit_of_work: AbstractUnitOfWork, tracking_identifier: str):
    expected_identifier = "00000000-0000-0000-0000-000000000001"
    assert unit_of_work.gateway.has_object(expected_identifier)

    with unit_of_work:
        revision = unit_of_work.catalog.get(expected_identifier)
        assert revision is not None

        workflow_events = unit_of_work.event_store.get_all_for_tracking_identifier(
            tracking_identifier)
        assert len(workflow_events) != 0
        assert workflow_events[0].event_type == WorkflowEventType.REVISION_CATALOGED
