from pathlib import Path

import pytest

from gateway.exceptions import ObjectDoesNotExistError, StagedObjectAlreadyExistsError
from gateway.coordinator import Coordinator
from gateway.fake_repository_gateway import FakePackage, FakeRepositoryGateway
from gateway.object_file import ObjectFile


@pytest.fixture
def package_A() -> FakePackage:
    return FakePackage(
        root_path=Path("/"), entries=[Path("some"), Path("some/path")]
    )

@pytest.fixture
def gateway_with_committed_package(package_A: FakePackage) -> FakeRepositoryGateway:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", package_A)
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

def test_gateway_can_stage_changes(package_A: FakePackage) -> None:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", package_A)

    assert gateway.store["A"].staged_files == set([Path("some"), Path("some/path")])

def test_gateway_raises_when_staging_changes_when_no_object_exists(package_A: FakePackage) -> None:
    gateway = FakeRepositoryGateway()
    with pytest.raises(ObjectDoesNotExistError):
        gateway.stage_object_files("A", package_A)

def test_gateway_can_commit_changes(package_A: FakePackage) -> None:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", package_A)
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
    gateway_with_committed_package: FakeRepositoryGateway
) -> None:
    assert gateway_with_committed_package.has_object("A")

def test_gateway_can_indicate_it_does_not_have_an_object() -> None:
    gateway = FakeRepositoryGateway()
    assert not gateway.has_object("A")

def test_gateway_can_indicate_it_does_not_have_an_object_even_if_staged() -> None:
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    assert not gateway.has_object("A")

def test_gateway_can_get_object_files(
    gateway_with_committed_package: FakeRepositoryGateway
) -> None:
    object_files = gateway_with_committed_package.get_object_files("A")

    expected_object_files = [
        ObjectFile(logical_path=Path("some"), literal_path=Path("some")),
        ObjectFile(logical_path=Path("some/path"), literal_path=Path("some/path"))
    ]
    assert set(expected_object_files) == set(object_files)

def test_gateway_can_get_object_files_when_some_are_staged(
    gateway_with_committed_package: FakeRepositoryGateway
) -> None:
    gateway = gateway_with_committed_package
    update_package = FakePackage(root_path=Path("/"), entries=[Path("some/other/path")])
    gateway.stage_object_files("A", update_package)

    object_files = gateway.get_object_files("A", include_staged=True)

    expected_object_files = [
        ObjectFile(logical_path=Path("some"), literal_path=Path("some")),
        ObjectFile(logical_path=Path("some/path"), literal_path=Path("some/path")),
        ObjectFile(logical_path=Path("some/other/path"), literal_path=Path("some/other/path"))
    ]
    assert set(expected_object_files) == set(object_files)

def test_gateway_can_get_object_files_when_only_staged(package_A: FakePackage):
    gateway = FakeRepositoryGateway()
    gateway.create_staged_object("A")
    gateway.stage_object_files("A", package_A)

    object_files = gateway.get_object_files("A", include_staged=True)
    expected_object_files = [
        ObjectFile(logical_path=Path("some"), literal_path=Path("some")),
        ObjectFile(logical_path=Path("some/path"), literal_path=Path("some/path"))
    ]
    assert set(object_files) == set(expected_object_files)

def test_gateway_only_gets_committed_files_when_excluding_staged_files(
    gateway_with_committed_package: FakeRepositoryGateway
) -> None:
    gateway = gateway_with_committed_package
    update_package = FakePackage(root_path=Path("/"), entries=[Path("some/other/path")])
    gateway.stage_object_files("A", update_package)

    object_files = gateway.get_object_files("A", include_staged=False)

    expected_object_files = [
        ObjectFile(logical_path=Path("some"), literal_path=Path("some")),
        ObjectFile(logical_path=Path("some/path"), literal_path=Path("some/path"))
    ]
    assert set(expected_object_files) == set(object_files)

def test_gateway_purges_object(
    gateway_with_committed_package: FakeRepositoryGateway
) -> None:
    gateway = gateway_with_committed_package
    gateway.purge_object("A")
    assert not gateway.has_object("A")

def test_gateway_does_not_raise_when_purging_object_that_does_not_exist() -> None:
    gateway = FakeRepositoryGateway()
    gateway.purge_object("Z")
