from pathlib import Path

import pytest

from dor.providers.file_set_identifier import FileSetIdentifier
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.operations import (
    AppendUses,
    CompressSourceImage, BitonalSourceImage,
)

from dor.providers.process_basic_image import (
    Command,
    Input,
    build_file_set,
)


@pytest.fixture
def file_set_identifier() -> FileSetIdentifier:
    return FileSetIdentifier(project_id="collid", file_name="image.tiff")


@pytest.fixture
def input_path() -> Path:
    return Path("tests/fixtures/test_basic_copy_contone_transcribed")


@pytest.fixture
def output_path() -> Path:
    file_provider = FilesystemFileProvider()
    output_path = Path("tests/output/test_basic_copy_contone_transcribed")
    file_provider.delete_dir_and_contents(output_path)
    file_provider.create_directory(output_path)
    return output_path


@pytest.fixture
def inputs(input_path: Path) -> list[Input]:
    return [
        Input(file_path=input_path / "image.tiff", commands=[
            Command(operation=CompressSourceImage, kwargs={}),
            Command(operation=BitonalSourceImage, kwargs={}),
        ]),
        Input(file_path=input_path / "text.txt", commands=[
            Command(operation=AppendUses, kwargs={
                "target": {
                    "function": ["function:source"],
                    "format": "format:text-plain"},
                "uses": ["function:service"]
            }),
        ])
    ]


def test_process_contone_transcribed_copies_source_files(file_set_identifier, inputs, output_path):
    source_image_file = output_path / file_set_identifier.identifier / "data" / \
        "image.function:source.format:image.tiff"
    source_image_event_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:source.format:image.tiff.function:event.premis.xml"
    source_image_technical_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:source.format:image.tiff.function:technical.mix.xml"

    source_text_file = output_path / file_set_identifier.identifier / "data" / \
        "image.function:source.function:service.format:text-plain.txt"
    source_text_event_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:source.function:service.format:text-plain.txt.function:event.premis.xml"
    source_text_technical_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:source.function:service.format:text-plain.txt.function:technical.textmd.xml"

    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=inputs,
        output_path=output_path
    )
    assert source_image_file.exists()
    assert source_image_event_metadata.exists()
    assert source_image_technical_metadata.exists()

    assert source_text_file.exists()
    assert source_text_event_metadata.exists()
    assert source_text_technical_metadata.exists()


def test_process_contone_transcribed_creates_service_files(file_set_identifier, inputs, output_path):
    service_image_file = output_path / file_set_identifier.identifier / "data" / \
        "image.function:service.format:image.jp2"
    service_image_event_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:service.format:image.jp2.function:event.premis.xml"
    service_image_technical_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:service.format:image.jp2.function:technical.mix.xml"

    service_text_file = output_path / file_set_identifier.identifier / "data" / \
        "image.function:source.function:service.format:text-plain.txt"
    service_text_event_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:source.function:service.format:text-plain.txt.function:event.premis.xml"
    service_text_technical_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:source.function:service.format:text-plain.txt.function:technical.textmd.xml"

    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=inputs,
        output_path=output_path
    )
    assert service_image_file.exists()
    assert service_image_event_metadata.exists()
    assert service_image_technical_metadata.exists()

    assert service_text_file.exists()
    assert service_text_event_metadata.exists()
    assert service_text_technical_metadata.exists()


def test_process_contone_transcribed_creates_preservation_files(file_set_identifier, inputs, output_path):
    preservation_image_file = output_path / file_set_identifier.identifier / "data" / \
        "image.function:preservation.format:image.tiff"
    preservation_image_event_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:preservation.format:image.tiff.function:event.premis.xml"
    preservation_image_technical_metadata = output_path / file_set_identifier.identifier / "metadata" / \
        "image.function:preservation.format:image.tiff.function:technical.mix.xml"

    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=inputs,
        output_path=output_path
    )

    assert preservation_image_file.exists()
    assert preservation_image_event_metadata.exists()
    assert preservation_image_technical_metadata.exists()


def test_process_contone_transcribed_creates_descriptor_file(file_set_identifier, inputs, output_path):
    descriptor_file = output_path / file_set_identifier.identifier / \
        "descriptor" / f"{file_set_identifier.uuid}.file_set.mets2.xml"

    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=inputs,
        output_path=output_path
    )
    assert descriptor_file.exists()
