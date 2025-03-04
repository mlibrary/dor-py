import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.models import PackagerConfig, PackageMetadata
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

        config_data = json.loads(config_file_path.read_text())
        config = PackagerConfig.model_validate(config_data)
        self.deposit_group = config.deposit_group

    def generate_package(self, metadata: PackageMetadata) -> PackageResult:
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
        more_lines = True

        with open(self.dump_file_path, "r") as file:
            while more_lines:
                line = file.readline()
                if line != "":
                    metadata = json.loads(line)
                    package_metadata = PackageMetadata.model_validate(metadata)
                    package_result = self.generate_package(package_metadata)
                    package_results.append(package_result)
                else:
                    more_lines = False

        return package_results
