from pathlib import Path

import pytest

from dor.providers.pending_file_set_accessor import PendingFileSetAccessor, PendingFileSetStatus
from dor.providers.file_system_file_provider import FilesystemFileProvider


@pytest.fixture
def fixtures_path() -> Path:
    return Path(__file__).parent / "fixtures/test_pending_file_set_accessor"


@pytest.fixture
def file_provider() -> FilesystemFileProvider:
    return FilesystemFileProvider()


@pytest.fixture
def pending_file_set_accessor(file_provider: FilesystemFileProvider, fixtures_path: Path) -> PendingFileSetAccessor:
    return PendingFileSetAccessor(file_provider=file_provider, path=fixtures_path)


def test_pending_file_set_count(pending_file_set_accessor: PendingFileSetAccessor) -> None:
    files = dirs = 0
    for entry in pending_file_set_accessor.path.iterdir():
        if entry.is_dir():
            dirs += 1
        elif entry.is_file():
            files += 1

    assert files == 0
    assert pending_file_set_accessor.count() == dirs


def test_pending_file_set_status_not_found(pending_file_set_accessor: PendingFileSetAccessor) -> None:
    assert pending_file_set_accessor.status(file_set_id="not_found") is PendingFileSetStatus.NOT_FOUND


def test_pending_file_set_status_undefined(pending_file_set_accessor: PendingFileSetAccessor) -> None:
    assert pending_file_set_accessor.status(file_set_id="undefined") is PendingFileSetStatus.UNDEFINED


def test_pending_file_set_status_unknown(pending_file_set_accessor: PendingFileSetAccessor) -> None:
    assert pending_file_set_accessor.status(file_set_id="unknown") is PendingFileSetStatus.UNKNOWN


def test_pending_file_set_status_processing(pending_file_set_accessor: PendingFileSetAccessor) -> None:
    assert pending_file_set_accessor.status(file_set_id="processing") is PendingFileSetStatus.PROCESSING


def test_pending_file_set_status_defective(pending_file_set_accessor: PendingFileSetAccessor) -> None:
    assert pending_file_set_accessor.status(file_set_id="defective") is PendingFileSetStatus.DEFECTIVE


def test_pending_file_set_status_finished(pending_file_set_accessor: PendingFileSetAccessor) -> None:
    assert pending_file_set_accessor.status(file_set_id="finished") is PendingFileSetStatus.FINISHED


def test_pending_file_set_status_precedence(pending_file_set_accessor: PendingFileSetAccessor) -> None:
    assert pending_file_set_accessor.status(file_set_id="precedence") is PendingFileSetStatus.DEFECTIVE
