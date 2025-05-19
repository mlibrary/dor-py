from pathlib import Path
import pytest


@pytest.fixture
def fixture_path() -> Path:
    return Path("tests/fixtures/test_generate_profiles")

def test_generate_profiles_creates_profiles_for_image(fixture_path):
    data = {"image":["compress-source", "extract-text"]}
    folder_path = fixture_path
    result = generate_profiles(folder_path, data)
    assert result == {"test_image.jpg": ["compress-source", "extract-text"]}