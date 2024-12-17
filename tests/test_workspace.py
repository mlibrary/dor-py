from pathlib import Path
from dor.providers.translocator import Workspace
import pytest


def test_create_workspace() -> None:
    workspace = Workspace(identifier="/tmp/UID-00001")
    
def test_create_workspace_with_root_identifier() -> None:
    workspace = Workspace(identifier="/tmp/UID-00001", root_identifier="00000000-0000-0000-0000-000000000001")
        
def test_retrieve_package_identifier() -> None:
    workspace = Workspace(identifier="/tmp/UID-00001", root_identifier="00000000-0000-0000-0000-000000000001")
    result = workspace.package_directory()
    assert result == Path("/tmp/UID-00001")
    
def test_retrieve_object_data_directory() -> None:
    workspace = Workspace(identifier="/tmp/UID-00001", root_identifier="00000000-0000-0000-0000-000000000001")
    result = workspace.object_data_directory()
    assert result == Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001") 
    
def test_raises_when_no_root_identifier_provided() -> None:
    workspace = Workspace(identifier="/tmp/UID-00001")
    with pytest.raises(Exception):
        workspace.object_data_directory()
 
def test_provides_bundle() -> None:
    workspace = Workspace(identifier="/tmp/UID-00001", root_identifier="00000000-0000-0000-0000-000000000001")
    entries= [
        Path("../metadata/file.xml"),
        Path("../data/file.jpg")
    ]
    result = workspace.get_bundle(entries)
    assert result.root_path == Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001") 
    assert result.entries == [Path("metadata/file.xml"), Path("data/file.jpg")]
    