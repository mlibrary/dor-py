from pathlib import Path
import shutil

import pytest

from dor.providers.translocator import Translocator


@pytest.fixture
def workspaces_path() -> Path:
    return Path("tests/test_workspaces")

@pytest.fixture
def inbox_path() -> Path:
    return Path("tests/fixtures/test_inbox")

def test_create_translocator(inbox_path, workspaces_path) -> None:
    Translocator(
        inbox_path=inbox_path, workspaces_path=workspaces_path, minter=lambda: "some_id"
    )

def test_translocator_can_create_workspace(inbox_path, workspaces_path) -> None:
    shutil.rmtree(workspaces_path / "some_id", ignore_errors=True)
    translocator = Translocator(
        inbox_path=inbox_path, workspaces_path=workspaces_path, minter=lambda: "some_id"
    )
    workspace = translocator.create_workspace_for_package("xyzzy-0001-v1")

    assert workspace.identifier == str(workspaces_path / "some_id")
    assert Path(workspace.identifier).exists()
