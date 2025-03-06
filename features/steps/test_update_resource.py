"""Update Resource feature tests."""
from functools import partial
from pytest_bdd import scenario, given, when, then

from dor.domain.events import PackageSubmitted
from dor.domain.models import PathData, WorkflowEventType
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import AbstractUnitOfWork


scenario = partial(scenario, '../update_resource.feature')


@scenario('Updating a resource for immediate release')
def test_updating_a_resource_for_immediate_release():
    """Updating a resource for immediate release."""


@given('a package containing all the scanned pages, OCR, and metadata')
def _(path_data: PathData, unit_of_work: AbstractUnitOfWork, message_bus: MemoryMessageBus):
    """a package containing all the scanned pages, OCR, and metadata."""
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(path=path_data.scratch)
    file_provider.create_directory(path_data.scratch)
    file_provider.create_directory(path_data.storage)
    file_provider.create_directory(path_data.workspaces)

    unit_of_work.gateway.create_repository()

    submission_id = "xyzzy-00000000-0000-0000-0000-000000000001-v1"
    tracking_identifier = "first-load" # str(uuid.uuid4())

    event = PackageSubmitted(
        package_identifier=submission_id,
        tracking_identifier=tracking_identifier
    )
    message_bus.handle(event, unit_of_work)


@when('the Collection Manager places the packaged resource in the incoming location',
    target_fixture="tracking_identifier"
)
def _(message_bus: MemoryMessageBus, unit_of_work: AbstractUnitOfWork):
    """the Collection Manager places the packaged resource in the incoming location."""
    submission_id = "xyzzy-00000000-0000-0000-0000-000000000001-v1"
    tracking_identifier = "second-load"  # str(uuid.uuid4())

    event = PackageSubmitted(
        package_identifier=submission_id,
        tracking_identifier=tracking_identifier,
        update_flag=True,
    )
    message_bus.handle(event, unit_of_work)
    return tracking_identifier


@then('the Collection Manager can see that it was revised.')
def _(unit_of_work: AbstractUnitOfWork, tracking_identifier: str):
    """the Collection Manager can see that it was revised.."""
    expected_identifier = "00000000-0000-0000-0000-000000000001"
    assert unit_of_work.gateway.has_object(expected_identifier)

    with unit_of_work:
        revision = unit_of_work.catalog.get(expected_identifier)
        assert revision is not None

        workflow_events = unit_of_work.event_store.get_all_for_tracking_identifier(tracking_identifier)
        assert len(workflow_events) != 0
        assert workflow_events[0].event_type == WorkflowEventType.REVISION_CATALOGED


@scenario("Updating only metadata of a resource for immediate release")
def test_updating_only_metadata_of_a_resource_for_immediate_release():
    """Updating only metadata of a resource for immediate release."""


@given("a package containing updated resource metadata")
def _(
    path_data: PathData, unit_of_work: AbstractUnitOfWork, message_bus: MemoryMessageBus
):
    """a package containing updated resource metadata"""
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(path=path_data.scratch)
    file_provider.create_directory(path_data.scratch)
    file_provider.create_directory(path_data.storage)
    file_provider.create_directory(path_data.workspaces)

    unit_of_work.gateway.create_repository()

    submission_id = "xyzzy-00000000-0000-0000-0000-000000000001-v1"
    tracking_identifier = "third-load" # str(uuid.uuid4())

    event = PackageSubmitted(
        package_identifier=submission_id,
        tracking_identifier=tracking_identifier,
        update_flag=False,
    )
    message_bus.handle(event, unit_of_work)


@when(
    "the Collection Manager places the packaged resource in the incoming location",
    target_fixture="tracking_identifier",
)
def _(message_bus: MemoryMessageBus, unit_of_work: AbstractUnitOfWork):
    """the Collection Manager places the packaged resource in the incoming location."""
    submission_id = "xyzzy-00000000-0000-0000-0000-000000000001-v2"
    tracking_identifier = "fourth-load" # str(uuid.uuid4())

    event = PackageSubmitted(
        package_identifier=submission_id,
        tracking_identifier=tracking_identifier,
        update_flag=True,
    )
    message_bus.handle(event, unit_of_work)
    return tracking_identifier


@then("the Collection Manager can see that it was revised.")
def _(unit_of_work: AbstractUnitOfWork, tracking_identifier: str):
    """the Collection Manager can see that it was revised.."""
    expected_identifier = "00000000-0000-0000-0000-000000000001"
    assert unit_of_work.gateway.has_object(expected_identifier)

    with unit_of_work:
        revision = unit_of_work.catalog.get(expected_identifier)
        assert revision is not None

        workflow_events = unit_of_work.event_store.get_all_for_tracking_identifier(
            tracking_identifier
        )
        assert len(workflow_events) != 0
        assert workflow_events[0].event_type == WorkflowEventType.REVISION_CATALOGED
