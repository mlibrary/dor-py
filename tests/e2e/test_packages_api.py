import json
from datetime import UTC, datetime
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
    body = {
        "deposit_group": {
            "identifier": "1bfbeda4-ca62-4922-b104-73931ade1d21",
            "date": datetime(2025, 5, 23, 12, tzinfo=UTC).isoformat()
        },
        "package_metadata": package_metadata
    }
    response = test_client.post("api/v1/packages", json=body)
    assert response.status_code == 200
