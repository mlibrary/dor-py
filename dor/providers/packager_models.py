from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

from cattrs import Converter, transform_error


@dataclass
class DepositGroup():
    identifier: str
    date: datetime


@dataclass
class PackagerConfig:
    deposit_group: DepositGroup


@dataclass
class PackageFileMetadata:
    use: str
    mimetype: str
    data: Any
    mdtype: Optional[str] = None


@dataclass
class PackageStructureItem:
    order: str
    orderlabel: str
    type: str
    locref: str


@dataclass
class PackageStructure:
    type: str
    items: list[PackageStructureItem]


@dataclass
class PackageMetadata:
    identifier: str
    type: str
    md: list[PackageFileMetadata]
    structure: list[PackageStructure]


class ValidationError(Exception):

    def __init__(self, message):
        super().__init__(message)

        self.message = message


@dataclass
class PackageResult:
    package_identifier: str
    success: bool
    message: str


@dataclass
class BatchResult:
    package_results: list[PackageResult]
    validation_errors: list[ValidationError]


# Converters

converter = Converter()
converter.register_structure_hook(datetime, lambda timestamp, datetime: datetime.fromisoformat(timestamp))


class ConfigConverter():

    def __init__(self, converter: Converter):
        self.converter = converter

    def convert(self, data: dict[str, Any]) -> PackagerConfig:
        try:
            config = self.converter.structure(data, PackagerConfig)
        except Exception as error:
            raise ValidationError(
                message=(
                    "Validation of configuration data failed. "
                    "Cattrs error: " + ";".join(transform_error(error))
                )
            )
        return config
    

class MetadataConverter():

    def __init__(self, converter: Converter):
        self.converter = converter

    def convert(self, data: dict[str, Any]) -> PackageMetadata:
        try:
            package_metadata = self.converter.structure(data, PackageMetadata)
        except Exception as error:
            raise ValidationError(
                message=(
                    "Validation of package metadata data failed. " + 
                    "Cattrs error: " + ";".join(transform_error(error))
                )
            )
        return package_metadata


config_converter = ConfigConverter(converter)
metadata_converter = MetadataConverter(converter)