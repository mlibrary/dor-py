"""Generate Packages feature tests."""
from datetime import UTC, datetime
from functools import partial
from pathlib import Path

import pytest
from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from dor.adapters.bag_adapter import BagAdapter
from dor.config import config
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.packager import Packager
from dor.providers.package_generator import PackageResult
from utils.logger import Logger


@pytest.fixture
def logger() -> Logger:
    collection_name = "test_generate_packages"
    logger = Logger(
        collection_name=collection_name,
        pb_username=config.pocketbase.pb_username,
        pb_password=config.pocketbase.pb_password,
        pb_url=config.pocketbase.pb_url
    )
    return logger


scenario = partial(scenario, '../generate_packages.feature')

@scenario('Generate submission information packages')
def test_generate_submission_information_packages():
    pass


@given('a JSONL dump file and file sets in pending', target_fixture="inbox_path")
def _(logger: Logger):
    """a JSONL dump file and file sets in pending."""

    file_provider = FilesystemFileProvider()
    test_path = Path("tests/output/test_packager")
    inbox_path = test_path / Path("inbox")

    file_provider.delete_dir_and_contents(path=test_path)
    file_provider.create_directories(inbox_path)

    logger.reset_log_collection()

    return inbox_path


@when('the Collection Manager invokes the packager')
def _(inbox_path: Path, logger: Logger):
    """the Collection Manager invokes the packager."""
    
    packager_fixtures_path = Path("tests/fixtures/packager/")
    jsonl_dump_file_path = packager_fixtures_path / "sample-dump-1.jsonl"
    config_file_path = packager_fixtures_path / "config.json"
    pending_path = packager_fixtures_path / "pending"

    packager = Packager(
        dump_file_path=jsonl_dump_file_path,
        config_file_path=config_file_path,
        pending_path=pending_path,
        inbox_path=inbox_path,
        timestamper=lambda: datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    package_results = packager.generate()

    for package_result in package_results:
        logger.log_result(package_result)


@then('the submission packages are generated in the inbox')
def _(inbox_path):
    """the submission packages are generated in the inbox."""

    package_paths = list(inbox_path.iterdir())
    assert len(package_paths) == 1
    package_path = package_paths[0]
    bag = BagAdapter.load(package_path, FilesystemFileProvider())
    bag.validate()


@then('the Collection Manager gets notified upon completion of the batch')
def _(logger: Logger):
    """the Collection Manager gets notified upon completion of the batch."""

    expected_package_identifier = "00000000-0000-0000-0000-000000000001_19700101000000"
    package_result = logger.search(expected_package_identifier)
    assert package_result == PackageResult(
        package_identifier=expected_package_identifier,
        deposit_group_identifier="23312082-44d8-489e-97f4-383329de9ac5",
        success=True,
        message="Generated package successfully!"
    )
