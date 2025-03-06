import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_generator import DepositGroup, PackageGenerator, PackageResult


class Packager:

    def __init__(
        self,
        dump_file_path: Path,
        config_file_path: Path,
        pending_path: Path,
        inbox_path: Path,
        timestamper: Callable[[], datetime]
    ):
        self.dump_file_path = dump_file_path
        self.pending_path = pending_path
        self.inbox_path = inbox_path
        self.timestamper = timestamper

        config = json.loads(config_file_path.read_text())
        deposit_group_data = config["deposit_group"]
        self.deposit_group = DepositGroup(
            identifier=deposit_group_data["identifier"],
            date=datetime.fromisoformat(deposit_group_data["date"])
        )

    def generate_package(self, metadata: dict[str, Any]) -> PackageResult:
        result = PackageGenerator(
            file_provider=FilesystemFileProvider(),
            metadata=metadata,
            deposit_group=self.deposit_group,
            output_path=self.inbox_path,
            file_set_path=self.pending_path,
            timestamp=self.timestamper()
        ).generate()
        return result

    def generate(self) -> list[PackageResult]:
        package_results: list[PackageResult] = []
        with open(self.dump_file_path, "r") as file:
            for line in file:
                if not line.strip(): continue
                metadata = json.loads(line)
                package_result = self.generate_package(metadata)
                package_results.append(package_result)
        return package_results
