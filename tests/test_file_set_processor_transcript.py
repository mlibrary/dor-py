from pathlib import Path

import pytest

from dor.providers.file_set_identifier import FileSetIdentifier
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.operations import (
    AppendUses,
)

from dor.providers.process_basic_image import (
    Command,
    Input,
    process_basic_image,
)


@pytest.fixture
def file_set_identifier() -> FileSetIdentifier:
    return FileSetIdentifier(project_id="collid", file_name="text.txt")


@pytest.fixture
def input_path() -> Path:
    return Path("tests/fixtures/test_basic_copy_transcript")


@pytest.fixture
def output_path() -> Path:
    file_provider = FilesystemFileProvider()
    output_path = Path("tests/output/test_basic_copy_transcript")
    file_provider.delete_dir_and_contents(output_path)
    file_provider.create_directory(output_path)
    return output_path


@pytest.fixture
def inputs(input_path: Path) -> list[Input]:
    return [
        Input(file_path=input_path / "text.txt", commands=[
            Command(operation=AppendUses, kwargs={
                "target": {
                    "function": ["function:source"],
                    "format": "format:text-plain"},
                "uses": ["function:service"]
            }),
        ])
    ]


def test_process_transcript_copies_source_files(file_set_identifier, inputs, output_path):
    source_text_file = output_path / file_set_identifier.identifier / "data" / \
        "text.function:source.function:service.format:text-plain.txt"
    source_text_event_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "text.function:source.function:service.format:text-plain.txt.function:event.premis.xml"
    source_text_technical_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "text.function:source.function:service.format:text-plain.txt.function:technical.textmd.xml"

    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        inputs=inputs,
        output_path=output_path
    )

    assert source_text_file.exists()
    assert source_text_event_metadata.exists()
    assert source_text_technical_metadata.exists()


def test_process_transcript_creates_service_files(file_set_identifier, inputs, output_path):
    service_text_file = output_path / file_set_identifier.identifier / "data" / \
        "text.function:source.function:service.format:text-plain.txt"
    service_text_event_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "text.function:source.function:service.format:text-plain.txt.function:event.premis.xml"
    service_text_technical_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "text.function:source.function:service.format:text-plain.txt.function:technical.textmd.xml"

    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        inputs=inputs,
        output_path=output_path
    )

    assert service_text_file.exists()
    assert service_text_event_metadata.exists()
    assert service_text_technical_metadata.exists()


def test_process_transcript_creates_descriptor_file(file_set_identifier, inputs, output_path):
    descriptor_file = output_path / file_set_identifier.identifier / \
        "descriptor" / f"{file_set_identifier.uuid}.file_set.mets2.xml"

    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        inputs=inputs,
        output_path=output_path
    )
    assert descriptor_file.exists()
