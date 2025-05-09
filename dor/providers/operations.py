import json
import shutil
import tempfile
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path

from dor.adapters.generate_service_variant import generate_service_variant, ServiceImageProcessingError
from dor.adapters.image_text_extractor import AltoDoc, AnnotationData, ImageTextExtractor
from dor.adapters.make_intermediate_file import make_intermediate_file
from dor.adapters.technical_metadata import ImageTechnicalMetadata, JHOVEDocError, Mimetype, TechnicalMetadata
from dor.builders.parts import FileInfo, UseFormat, UseFunction
from dor.providers.accumulator import Accumulator, AccumulatorError, ResultFile
from dor.providers.models import Agent, PreservationEvent


def create_preservation_event(
    event_type: str, collection_manager_email: str, detail: str = ""
):
    event = PreservationEvent(
        identifier=str(uuid.uuid4()),
        type=event_type,
        datetime=datetime.now(tz=UTC),
        detail=detail,
        agent=Agent(role="image_processing", address=collection_manager_email),
    )
    return event


@dataclass
class Operation(ABC):
    accumulator: Accumulator

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError


@dataclass
class CopySource(Operation):
    file_path: Path

    @staticmethod
    def copy_source_file(source_path: Path, destination_path: Path) -> None:
        shutil.copyfile(source_path, destination_path)

    def run(self) -> None:
        try:
            source_tech_metadata = TechnicalMetadata.create(self.file_path)
        except JHOVEDocError:
            return None

        file_info = FileInfo(
            identifier=self.accumulator.file_set_identifier.identifier,
            basename=self.accumulator.file_set_identifier.basename,
            uses=[UseFunction.source, UseFormat.from_mimetype(source_tech_metadata.mimetype.value)],
            mimetype=source_tech_metadata.mimetype.value,
        )

        source_file_path = self.accumulator.file_set_directory / file_info.path
        self.copy_source_file(source_path=self.file_path, destination_path=source_file_path)

        event = create_preservation_event(
            "copy source file", self.accumulator.collection_manager_email
        )

        self.accumulator.add_file(
            ResultFile(
                file_path=source_file_path,
                tech_metadata=source_tech_metadata,
                file_info=file_info,
                event=event
            )
        )
        return None


@dataclass
class OrientSourceImage(Operation):

    def run(self) -> None:
        source_result_file = self.accumulator.get_file(
            function=[UseFunction.source], format=UseFormat.image
        )
        if source_result_file.file_path is None:
            return None

        if not isinstance(source_result_file.tech_metadata, ImageTechnicalMetadata):
            return None

        if not source_result_file.tech_metadata.rotated:
            return None

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".tiff", delete=False)
        compressible_file_path = Path(temp_file.name)
        make_intermediate_file(source_result_file.file_path, compressible_file_path)

        try:
            tech_metadata = TechnicalMetadata.create(compressible_file_path)
        except JHOVEDocError:
            return None

        file_info = FileInfo(
            identifier=self.accumulator.file_set_identifier.identifier,
            basename=self.accumulator.file_set_identifier.basename,
            uses=[UseFunction.intermediate, UseFormat.image],
            mimetype=tech_metadata.mimetype.value,
        )

        event = create_preservation_event(
            "rotated source file", self.accumulator.collection_manager_email
        )

        self.accumulator.add_file(
            ResultFile(
                file_path=compressible_file_path,
                tech_metadata=tech_metadata,
                file_info=file_info,
                event=event
            )
        )
        return None


@dataclass
class CompressSourceImage(Operation):

    def run(self) -> None:
        source_result_file = self.accumulator.get_file(
            function=[UseFunction.intermediate, UseFunction.source], format=UseFormat.image
        )

        if source_result_file.tech_metadata.mimetype == Mimetype.JP2:
            source_result_file.file_info.uses.append(UseFunction.service)
            # TODO: Revisit once file-naming scheme is assessed
            new_file_path = self.accumulator.file_set_directory / source_result_file.file_info.path
            source_result_file.file_path.rename(new_file_path)
            source_result_file.file_path = new_file_path
            return None

        file_info = FileInfo(
            identifier=self.accumulator.file_set_identifier.identifier,
            basename=self.accumulator.file_set_identifier.basename,
            uses=[UseFunction.service, UseFormat.image],
            mimetype=Mimetype.JP2.value,
        )

        service_file_path = self.accumulator.file_set_directory / file_info.path
        try:
            generate_service_variant(source_result_file.file_path, service_file_path)
        except ServiceImageProcessingError:
            return None

        try:
            service_tech_metadata = TechnicalMetadata.create(service_file_path)
        except JHOVEDocError:
            return None

        event = create_preservation_event(
            "create JPEG2000 service file", self.accumulator.collection_manager_email
        )

        self.accumulator.add_file(
            ResultFile(
                file_path=service_file_path,
                tech_metadata=service_tech_metadata,
                file_info=file_info,
                source_file_result=source_result_file,
                event=event,
            )
        )
        return None


@dataclass
class ExtractImageTextCoordinates(Operation):
    language: str = "eng"

    def run(self) -> None:
        # TODO: reevaluate how we're constructing file_info before
        # TechnicalMetadata.create captures the actual mimetype.
        file_info = FileInfo(
            identifier=self.accumulator.file_set_identifier.identifier,
            basename=self.accumulator.file_set_identifier.basename,
            uses=[UseFunction.service, UseFormat.text_coordinates],
            mimetype=Mimetype.XML.value,
        )

        service_result_file = self.accumulator.get_file(
            function=[UseFunction.service], format=UseFormat.image
        )

        alto_xml = ImageTextExtractor(image_path=service_result_file.file_path, language=self.language).alto
        alto_file_path = self.accumulator.file_set_directory / file_info.path
        alto_file_path.write_text(alto_xml)

        try:
            tech_metadata = TechnicalMetadata.create(alto_file_path)
        except JHOVEDocError:
            return None

        event = create_preservation_event(
            "extract text coordinates with OCR", self.accumulator.collection_manager_email
        )

        self.accumulator.add_file(
            ResultFile(
                file_path=alto_file_path,
                tech_metadata=tech_metadata,
                file_info=file_info,
                source_file_result=service_result_file,
                event=event,
            )
        )


@dataclass
class ExtractImageText(Operation):
    language: str = "eng"

    def run(self) -> None:
        # TODO: reevaluate how we're constructing file_info before
        # TechnicalMetadata.create captures the actual mimetype.
        file_info = FileInfo(
            identifier=self.accumulator.file_set_identifier.identifier,
            basename=self.accumulator.file_set_identifier.basename,
            uses=[UseFunction.service, UseFormat.text_plain],
            mimetype=Mimetype.TXT.value
        )

        service_result_file = self.accumulator.get_file(
            function=[UseFunction.service], format=UseFormat.image
        )

        try:
            text_coordinates_result_file = self.accumulator.get_file(
                function=[UseFunction.service], format=UseFormat.text_coordinates
            )
        except AccumulatorError:
            text_coordinates_result_file = None

        if text_coordinates_result_file:
            alto_xml = text_coordinates_result_file.file_path.read_text()
            alto_doc = AltoDoc.create(alto_xml)
            plain_text = alto_doc.plain_text
        else:
            plain_text = ImageTextExtractor(image_path=service_result_file.file_path, language=self.language).text

        text_file_path = self.accumulator.file_set_directory / file_info.path
        text_file_path.write_text(plain_text)

        try:
            tech_metadata = TechnicalMetadata.create(text_file_path)
        except JHOVEDocError:
            return None

        event = create_preservation_event(
            "extract plain text with OCR", self.accumulator.collection_manager_email
        )

        self.accumulator.add_file(
            ResultFile(
                file_path=text_file_path,
                tech_metadata=tech_metadata,
                file_info=file_info,
                source_file_result=service_result_file,
                event=event,
            )
        )


@dataclass
class CreateTextAnnotationData(Operation):

    def run(self) -> None:
        # TODO: reevaluate how we're constructing file_info before
        # TechnicalMetadata.create captures the actual mimetype.
        file_info = FileInfo(
            identifier=self.accumulator.file_set_identifier.identifier,
            basename=self.accumulator.file_set_identifier.basename,
            uses=[UseFunction.service, UseFormat.text_annotations],
            mimetype=Mimetype.JSON.value,
        )

        service_result_file = self.accumulator.get_file(
            function=[UseFunction.service], format=UseFormat.image
        )

        text_coordinates_result_file = self.accumulator.get_file(
            function=[UseFunction.service], format=UseFormat.text_coordinates
        )

        alto_xml = text_coordinates_result_file.file_path.read_text()
        alto_doc = AltoDoc.create(alto_xml)
        annotation_data = AnnotationData(alto_doc).data
        annotation_data_file_path = self.accumulator.file_set_directory / file_info.path
        annotation_data_file_path.write_text(json.dumps(annotation_data, indent=4))

        try:
            tech_metadata = TechnicalMetadata.create(annotation_data_file_path)
        except JHOVEDocError:
            return None

        event = create_preservation_event(
            "create annotation data from text coordinates", self.accumulator.collection_manager_email
        )

        self.accumulator.add_file(
            ResultFile(
                file_path=annotation_data_file_path,
                tech_metadata=tech_metadata,
                file_info=file_info,
                source_file_result=service_result_file,
                event=event,
            )
        )


@dataclass
class AppendUses(Operation):
    target: dict
    uses: list[UseFunction]

    def run(self) -> None:
        target_result_file = self.accumulator.get_file(function=self.target["function"], format=self.target["format"])
        for use in self.uses:
            target_result_file.file_info.uses.append(UseFunction(use))
        target_result_file.file_path.rename(self.accumulator.file_set_directory / target_result_file.file_info.path)
        return None
