from dataclasses import dataclass
from pathlib import Path
from typing import Any, Type

from dor.providers.accumulator import Accumulator
from dor.providers.file_set_identifier import FileSetIdentifier
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.operations import CopySource, Operation, OrientSourceImage


@dataclass
class Command:
    operation: Type[Operation]
    kwargs: dict[str, Any]


@dataclass
class Input:
    file_path: Path
    commands: list[Command]


def create_file_set_directories(file_set_directory: Path) -> None:
    file_provider = FilesystemFileProvider()
    file_provider.create_directory(file_set_directory)
    file_provider.create_directory(file_set_directory / "data")
    file_provider.create_directory(file_set_directory / "metadata")
    file_provider.create_directory(file_set_directory / "descriptor")


def build_file_set(
    file_set_identifier: FileSetIdentifier, # fsid
    inputs: list[Input], # a.k.a. [Input(file_path=./src/file_set_identifier.file_name, commands=[]]
    output_path: Path, # a.k.a. ./build
    collection_manager_email: str = "example@org.edu",
) -> bool:
    file_set_directory = output_path / file_set_identifier.identifier
    # file_set_identifier.file_name == primary source file
    create_file_set_directories(file_set_directory)

    accumulator = Accumulator(
        file_set_identifier=file_set_identifier,
        file_set_directory=file_set_directory,
        collection_manager_email=collection_manager_email,
    )

    for input in inputs:
        CopySource(accumulator=accumulator, file_path=input.file_path).run()
        OrientSourceImage(accumulator).run()
        for command in input.commands:
            command.operation(accumulator=accumulator, **command.kwargs).run()

    accumulator.write()
    return True
