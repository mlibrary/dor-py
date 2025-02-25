"""Generate Packages feature tests."""
import json
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import Any, Callable

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from dor.adapters.bag_adapter import BagAdapter
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_generator import PackageGenerator, PackageResult


class Packager:

    def __init__(
        self,
        dump_file_path: Path,
        pending_path: Path,
        inbox_path: Path,
        timestamper: Callable[[], datetime]
    ):
        self.dump_file_path = dump_file_path
        self.pending_path = pending_path
        self.inbox_path = inbox_path
        self.timestamper = timestamper

    def generate_package(self, metadata: dict[str, Any]) -> PackageResult:
        result = PackageGenerator(
            file_provider=FilesystemFileProvider(),
            metadata=metadata,
            output_path=self.inbox_path,
            file_set_path=self.pending_path,
            timestamp=self.timestamper()
        ).generate()

        return result

    def generate(self) -> list[PackageResult]:
        package_results: list[PackageResult] = []
        more_lines = True

        with open(self.dump_file_path, "r") as file:
            while more_lines:
                line = file.readline()
                if line != "":
                    metadata = json.loads(line)
                    package_result = self.generate_package(metadata)
                    package_results.append(package_result)
                else:
                    more_lines = False

        return package_results


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


@when('the Collection Manager invokes the packager', target_fixture="package_results")
def _(inbox_path):
    """the Collection Manager invokes the packager."""
    
    packager_fixtures_path = Path("features/fixtures/packager/")
    jsonl_dump_file_path = packager_fixtures_path / "sample-dump-1.jsonl"
    pending_path = packager_fixtures_path / "pending"

    packager = Packager(
        dump_file_path=jsonl_dump_file_path,
        pending_path=pending_path, 
        inbox_path=inbox_path,
        timestamper=lambda: datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    package_results = packager.generate()
    return package_results


@then('the submission packages are generated in the inbox')
def _(inbox_path):
    """the submission packages are generated in the inbox."""

    package_paths = list(inbox_path.iterdir())
    assert len(package_paths) == 1
    for package_path in package_paths:
        bag = BagAdapter(package_path, FilesystemFileProvider())
        bag.validate()


@then('the Collection Manager gets notified upon completion of the batch')
def _(package_results):
    """the Collection Manager gets notified upon completion of the batch."""

    assert package_results == [PackageResult(
        package_identifier=f"00000000-0000-0000-0000-000000000001_19700101000000",
        success=True,
        message="Generated package successfully!"
    )]
