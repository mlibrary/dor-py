from pathlib import Path

import pytest

from gateway.bundle import Bundle
from gateway.coordinator import Coordinator
from gateway.exceptions import ObjectDoesNotExistError, RepositoryGatewayError, StagedObjectAlreadyExistsError
from gateway.fake_repository_gateway import FakeRepositoryGateway
from gateway.object_file import ObjectFile


@pytest.fixture
def bundle_a() -> Bundle:
    return Bundle(root_path=Path("/"), entries=[Path("some"), Path("some/path")])


@pytest.fixture
def bundle_a_update() -> Bundle:
    return Bundle(root_path=Path("/"), entries=[Path("some/other/path")])


@pytest.fixture
def gateway_with_committed_bundle(bundle_a: Bundle) -> FakeRepositoryGateway:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", bundle_a)
    gateway.commit_object_changes(
        "A", Coordinator("test", "test@example.edu"), "First version!"
    )
    return gateway


def test_gateway_can_create_repository() -> None:
    FakeRepositoryGateway().create_repository()


def test_gateway_can_created_staged_object() -> None:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    assert "A" in gateway.store


def test_gateway_raises_when_creating_staged_object_that_already_exists() -> None:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("Z")
    with pytest.raises(StagedObjectAlreadyExistsError):
        gateway.create_staged_object("Z")


def test_gateway_can_stage_changes(bundle_a: Bundle) -> None:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", bundle_a)
    assert gateway.store["A"].staged_files == set([Path("some"), Path("some/path")])


def test_gateway_raises_when_staging_changes_when_no_object_exists(bundle_a: Bundle) -> None:
    gateway = FakeRepositoryGateway()
    with pytest.raises(ObjectDoesNotExistError):
        gateway.stage_object_files("A", bundle_a)


def test_gateway_can_commit_changes(bundle_a: Bundle) -> None:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", bundle_a)
    gateway.commit_object_changes(
        "A", Coordinator("test", "test@example.edu"), "First version!"
    )
    assert gateway.store["A"].staged_files == set()
    assert gateway.store["A"].versions[0].files == set([Path("some"), Path("some/path")])


def test_gateway_raises_when_committing_changes_when_no_object_exists() -> None:
    gateway = FakeRepositoryGateway()
    with pytest.raises(ObjectDoesNotExistError):
        gateway.commit_object_changes(
            "A", Coordinator("test", "test@example.edu"), "First version!"
        )


def test_gateway_can_indicate_it_has_an_object(
    gateway_with_committed_bundle: FakeRepositoryGateway
) -> None:
    assert gateway_with_committed_bundle.has_object("A")


def test_gateway_can_indicate_it_does_not_have_an_object() -> None:
    gateway = FakeRepositoryGateway()
    assert not gateway.has_object("A")


def test_gateway_can_indicate_it_does_not_have_an_object_even_if_staged() -> None:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    assert not gateway.has_object("A")


def test_gateway_can_get_object_files(
    gateway_with_committed_bundle: FakeRepositoryGateway
) -> None:
    object_files = gateway_with_committed_bundle.get_object_files("A")

    expected_object_files = [
        ObjectFile(logical_path=Path("some"), literal_path=Path("some")),
        ObjectFile(logical_path=Path("some/path"), literal_path=Path("some/path"))
    ]
    assert set(expected_object_files) == set(object_files)


def test_gateway_can_get_object_files_when_some_are_staged(
    gateway_with_committed_bundle: FakeRepositoryGateway
) -> None:
    gateway = gateway_with_committed_bundle
    update_bundle = Bundle(root_path=Path("/"), entries=[Path("some/other/path")])
    gateway.stage_object_files("A", update_bundle)

    object_files = gateway.get_object_files("A", include_staged=True)

    expected_object_files = [
        ObjectFile(logical_path=Path("some"), literal_path=Path("some")),
        ObjectFile(logical_path=Path("some/path"), literal_path=Path("some/path")),
        ObjectFile(logical_path=Path("some/other/path"), literal_path=Path("some/other/path"))
    ]
    assert set(expected_object_files) == set(object_files)


def test_gateway_can_get_object_files_when_only_staged(bundle_a: Bundle):
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", bundle_a)

    object_files = gateway.get_object_files("A", include_staged=True)

    expected_object_files = [
        ObjectFile(logical_path=Path("some"), literal_path=Path("some")),
        ObjectFile(logical_path=Path("some/path"), literal_path=Path("some/path"))
    ]
    assert set(object_files) == set(expected_object_files)


def test_gateway_only_gets_committed_files_when_excluding_staged_files(
    gateway_with_committed_bundle: FakeRepositoryGateway
) -> None:
    gateway = gateway_with_committed_bundle
    update_bundle = Bundle(root_path=Path("/"), entries=[Path("some/other/path")])
    gateway.stage_object_files("A", update_bundle)

    object_files = gateway.get_object_files("A", include_staged=False)

    expected_object_files = [
        ObjectFile(logical_path=Path("some"), literal_path=Path("some")),
        ObjectFile(logical_path=Path("some/path"), literal_path=Path("some/path"))
    ]
    assert set(expected_object_files) == set(object_files)


def test_gateway_purges_object(
    gateway_with_committed_bundle: FakeRepositoryGateway
) -> None:
    gateway = gateway_with_committed_bundle
    gateway.purge_object("A")
    assert not gateway.has_object("A")


def test_gateway_does_not_raise_when_purging_object_that_does_not_exist() -> None:
    gateway = FakeRepositoryGateway()
    gateway.purge_object("Z")


def test_gateway_log_raises_for_object_that_does_not_exist(gateway_with_committed_bundle: FakeRepositoryGateway):
    gateway = gateway_with_committed_bundle

    with pytest.raises(RepositoryGatewayError):
        gateway.log("Z")


def test_gateway_log_raises_for_a_staged_object(bundle_a: Bundle):
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", bundle_a)

    with pytest.raises(RepositoryGatewayError):
        gateway.log("A")


def test_gateway_log_committed_object(bundle_a: Bundle):
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", bundle_a)
    gateway.commit_object_changes(
        "A", Coordinator("test", "test@example.edu"), "First version!"
    )

    log = gateway.log("A")
    assert len(log) == 1


def test_gateway_log_committed_staged_object(gateway_with_committed_bundle: FakeRepositoryGateway):
    gateway = gateway_with_committed_bundle
    update_bundle = Bundle(root_path=Path("/"), entries=[Path("some/other/path")])
    gateway.stage_object_files("A", update_bundle)

    log = gateway.log("A")
    assert len(log) == 1


def test_gateway_log_default_descending_order(gateway_with_committed_bundle: FakeRepositoryGateway, bundle_a_update: Bundle):
    gateway = gateway_with_committed_bundle
    gateway.stage_object_files("A", bundle_a_update)
    gateway.commit_object_changes("A", Coordinator("test", "test@example.edu"), "Second version!")

    log = gateway.log("A")
    assert log[0].version == 2
    assert log[1].version == 1


def test_gateway_log_optional_ascending_order(gateway_with_committed_bundle: FakeRepositoryGateway, bundle_a_update: Bundle):
    gateway = gateway_with_committed_bundle
    gateway.stage_object_files("A", bundle_a_update)
    gateway.commit_object_changes("A", Coordinator("test", "test@example.edu"), "Second version!")

    log = gateway.log("A", reverse=False)
    assert log[0].version == 1
    assert log[1].version == 2
