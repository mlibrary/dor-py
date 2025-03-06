import json
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_generator import PackageGenerator
from dor.providers.packager_models import (
    BatchResult, config_converter, DepositGroup, metadata_converter,
    PackageMetadata, PackageResult, ValidationError
)


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
        config = config_converter.convert(config_data)
        self.deposit_group = DepositGroup(
            identifier=config.deposit_group.identifier,
            date=config.deposit_group.date
        )

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

    def generate(self) -> BatchResult:
        package_results: list[PackageResult] = []
        validation_errors = []

        with open(self.dump_file_path, "r") as file:
            for line in file:
                if not line.strip(): continue
                metadata_data = json.loads(line)
                try:
                    package_metadata = metadata_converter.convert(metadata_data)
                except ValidationError as error:
                    validation_errors.append(error)
                    continue
                package_result = self.generate_package(package_metadata)
                package_results.append(package_result)
        return BatchResult(
            package_results=package_results,
            validation_errors=validation_errors
        )
