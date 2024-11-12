import os
from datetime import datetime, timezone
from pathlib import Path
from unittest import TestCase

from lxml import etree

from metadata.models import (
    Actor, Asset, AssetFile, AssetFileUse, FileMetadataFile, FileMetadataFileType, PreservationEvent,
    RecordStatus, StructMap, StructMapItem, StructMapType
)
from metadata.exceptions import MetadataFileNotFoundError
from metadata.mets_metadata_parser import MetsAssetParser, MetsMetadataParser, PremisEventParser

class PremisEventParserTest(TestCase):

    def setUp(self):
        fixtures_path = Path("tests/fixtures")
        test_submission_package_path = fixtures_path / "test_submission_package"
        bag_path = test_submission_package_path / "xyzzy-01929af3-dd86-7579-8c1b-6a5b6e1cd6b9-v1"
        content_path = bag_path / "data" / "xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P"
        mets_root_metadata_file = content_path / "descriptor" / "xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P.root.mets2.xml"
        root_tree = etree.fromstring(mets_root_metadata_file.read_text())

        namespaces = {"PREMIS": "http://www.loc.gov/premis/v3"}
        self.event_elem = root_tree.findall(".//PREMIS:event", namespaces)[0]

    def test_parser_can_get_event(self):
        event = PremisEventParser(self.event_elem).get_event()
        expected_event = PreservationEvent(
            identifier="4463f8a7-d532-4028-8f63-5808e33a0906",
            type="ingest",
            datetime=datetime(2024, 8, 19, 22, 32, 2, tzinfo=timezone.utc),
            detail="Need authority social region three.",
            actor=Actor(address="brandonwright@example.org", role="collection manager")
        )
        self.assertEqual(expected_event, event)

class MetsAssetParserTest(TestCase):

    def setUp(self):
        fixtures_path = Path("tests/fixtures")
        test_submission_package_path = fixtures_path / "test_submission_package"
        bag_path = test_submission_package_path / "xyzzy-01929af3-dd86-7579-8c1b-6a5b6e1cd6b9-v1"
        content_path = bag_path / "data" / "xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P"
        asset_id = "cc540920e91f05e4f6e4beb72dd441ac"
        self.asset_metadata_path = content_path / "descriptor" / f"{asset_id}.mets2.xml"

        return super().setUp()

    def test_parser_can_get_asset_with_path(self):
        asset = MetsAssetParser(self.asset_metadata_path).get_asset()
        expected_asset = Asset(
            id="cc540920e91f05e4f6e4beb72dd441ac",
            events=[
                PreservationEvent(
                    identifier="1a94b657-7efd-4675-8339-01f2b211fea3",
                    type="generate access derivative",
                    datetime=datetime(1991, 3, 13, 19, 37, 49, tzinfo=timezone.utc),
                    detail="Pass mind or long effect.",
                    actor=Actor(role="image processing", address="moyermelanie@example.com")
                )
            ],
            files=[
                AssetFile(
                    id="_1cc90346d5f1fe485fc8a3c55d10e753",
                    path=Path("data/00000002.access.jpg"),
                    use=AssetFileUse.ACCESS,
                    metadata_file=
                        FileMetadataFile(
                            id="_01929af3-df09-7d40-b0b4-8db2d23de0db",
                            type=FileMetadataFileType.TECHNICAL,
                            path=Path("metadata/00000002.access.jpg.mix.xml")
                        )
                ),
                AssetFile(
                    id="_f442339a2731f043f72460c64ad66fee",
                    path=Path("data/00000002.source.jpg"),
                    use=AssetFileUse.SOURCE,
                    metadata_file=
                        FileMetadataFile(
                            id="_01929af3-df0c-7e20-b7f3-b7a8260ca651",
                            type=FileMetadataFileType.TECHNICAL,
                            path=Path("metadata/00000002.source.jpg.mix.xml")
                        )
                ),
                AssetFile(
                    id="_59472df4b090349a7440a32ca575f87e",
                    path=Path("data/00000002.plaintext.txt"),
                    use=AssetFileUse.SOURCE,
                    metadata_file=
                        FileMetadataFile(
                            id="_01929af3-df0f-7cf6-9de2-f0cc276464cd",
                            type=FileMetadataFileType.TECHNICAL,
                            path=Path("metadata/00000002.plaintext.txt.textmd.xml")
                        )
                )
            ]
        )
        self.assertEqual(expected_asset, asset)

class MetsMetadataParserTest(TestCase):

    def setUp(self):
        fixtures_path = Path("tests/fixtures")
        test_submission_package_path = fixtures_path / "test_submission_package"
        bag_path = test_submission_package_path / "xyzzy-01929af3-dd86-7579-8c1b-6a5b6e1cd6b9-v1"
        self.content_path = bag_path / "data" / "xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P"

        self.empty_content_path = fixtures_path / "test_empty_content_path"
        if not self.empty_content_path.exists():
            os.makedirs(self.empty_content_path)

        return super().setUp()

    def test_parser_raises_when_metadata_file_not_found(self):
        with self.assertRaises(MetadataFileNotFoundError):
            MetsMetadataParser(self.empty_content_path)

    def test_parser_can_get_identifier(self):
        identifier = MetsMetadataParser(self.content_path).get_identifier()
        self.assertEqual("xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P", identifier)

    def test_parser_can_get_record_status(self):
        record_status = MetsMetadataParser(self.content_path).get_record_status()
        self.assertEqual("store", record_status)

    def test_parser_can_get_repository_item(self):
        item = MetsMetadataParser(self.content_path).get_repository_item()
        self.assertEqual("xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P", item.id)
        self.assertEqual(RecordStatus.STORE, item.record_status)

        self.assertEqual(1, len(item.events))
        event = item.events[0]
        self.assertTrue(isinstance(item.events[0], PreservationEvent))
        self.assertEqual("4463f8a7-d532-4028-8f63-5808e33a0906", event.identifier)

        expected_struct_map = StructMap(
            id="SM1",
            type=StructMapType.PHYSICAL,
            items=[
                StructMapItem(order=1, label="Page 1", asset_id="ced165163e51e06e01dc44c35fea3eaf"),
                StructMapItem(order=2, label="Page 2", asset_id="cc540920e91f05e4f6e4beb72dd441ac"),
                StructMapItem(order=3, label="Page 3", asset_id="82cf9fa647dd1b3fbd9de71bbfb83fb2"),
                StructMapItem(order=4, label="Page 4", asset_id="a527173445d117cbf177084bd34e60f2"),
                StructMapItem(order=5, label="Page 5", asset_id="d438e94a39b7f7986e0cefb826801769")
            ]
        )
        self.assertEqual(expected_struct_map, item.struct_map)

        self.assertEqual(5, len(item.assets))
        self.assertTrue(all(isinstance(asset, Asset) for asset in item.assets))
