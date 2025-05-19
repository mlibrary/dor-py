from pathlib import Path

import pytest

from dor.cli.client.upload_client import generate_profiles


@pytest.fixture
def fixture_path() -> Path:
    return Path("tests/fixtures/test_generate_profiles")


def test_generate_profiles_creates_profiles_for_image(fixture_path):
    type_profiles = {"image": ["compress-source", "extract-text"]}
    folder_path = fixture_path
    result = generate_profiles(folder_path, type_profiles)
    assert result == {"test_image.jpg": ["compress-source", "extract-text"]}


def test_generate_profiles_creates_profiles_for_text(fixture_path):
    type_profiles = {"text": ["label-service"]}
    folder_path = fixture_path
    result = generate_profiles(folder_path, type_profiles)
    assert result == {"text.txt": ["label-service"]}


def test_generate_profiles_creates_profiles_for_image_and_text(fixture_path):
    type_profiles = {"image": ["compress-source"], "text": ["label-service"]}
    folder_path = fixture_path
    result = generate_profiles(folder_path, type_profiles)
    assert result == {"test_image.jpg": ["compress-source"], "text.txt": ["label-service"]}
