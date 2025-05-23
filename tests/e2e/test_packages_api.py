import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_packages_api")


@pytest.mark.usefixtures("test_client")
def test_packages_api_returns_200_and_summary(test_client: TestClient, fixtures_path: Path):
    package_metadata_path = fixtures_path / "sample_package_metadata.json"
    package_metadata = json.loads(package_metadata_path.read_text())
    response = test_client.post("api/v1/packages", json=package_metadata)
    assert response.status_code == 200
