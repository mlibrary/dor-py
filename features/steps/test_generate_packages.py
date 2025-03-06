"""Generate Packages feature tests."""
from datetime import UTC, datetime
from functools import partial
from pathlib import Path

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from dor.adapters.bag_adapter import BagAdapter
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.packager import Packager
from dor.providers.package_generator import PackageResult


scenario = partial(scenario, '../generate_packages.feature')

@scenario('Generate submission information packages')
def test_generate_submission_information_packages():
    pass


@given('a JSONL dump file and file sets in pending', target_fixture="inbox_path")
def _():
    """a JSONL dump file and file sets in pending."""

    file_provider = FilesystemFileProvider()
    scratch_path = Path("features/packager_scratch")
    inbox_path = scratch_path / Path("inbox")

    file_provider.delete_dir_and_contents(path=scratch_path)
    file_provider.create_directories(inbox_path)
    return inbox_path


@when('the Collection Manager invokes the packager', target_fixture="batch_result")
def _(inbox_path):
    """the Collection Manager invokes the packager."""
    
    packager_fixtures_path = Path("features/fixtures/packager/")
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
    batch_result = packager.generate()
    return batch_result


@then('the submission packages are generated in the inbox')
def _(inbox_path):
    """the submission packages are generated in the inbox."""

    package_paths = list(inbox_path.iterdir())
    assert len(package_paths) == 1
    for package_path in package_paths:
        bag = BagAdapter.load(package_path, FilesystemFileProvider())
        bag.validate()


@then('the Collection Manager gets notified upon completion of the batch')
def _(batch_result):
    """the Collection Manager gets notified upon completion of the batch."""

    assert batch_result.package_results == [PackageResult(
        package_identifier=f"00000000-0000-0000-0000-000000000001_19700101000000",
        success=True,
        message="Generated package successfully!"
    )]
