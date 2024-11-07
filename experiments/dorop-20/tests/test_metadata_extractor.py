import os
from pathlib import Path
from unittest import TestCase

from metadata.models import (
    Asset, AssetFile, FileMetadataFile, FileMetadataFileType, RecordStatus
)
from metadata.exceptions import MetadataFileNotFoundError
from metadata.mets_metadata_extractor import MetsMetadataExtractor

class MetsMetadataExtractorTest(TestCase):

    def setUp(self):
        fixtures_path = Path("tests/fixtures")
        test_submission_package_path = fixtures_path / "test_submission_package"
        bag_path = test_submission_package_path / "xyzzy-01929af3-dd86-7579-8c1b-6a5b6e1cd6b9-v1"
        self.content_path = bag_path / "data" / "xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P"

        self.empty_content_path = fixtures_path / "test_empty_content_path"
        if not self.empty_content_path.exists():
            os.makedirs(self.empty_content_path)

        return super().setUp()
    
    def test_extractor_raises_when_metadata_file_not_found(self):
        with self.assertRaises(MetadataFileNotFoundError):
            MetsMetadataExtractor(self.empty_content_path)

    def test_extractor_can_get_identifier(self):
        identifier = MetsMetadataExtractor(self.content_path).get_identifier()
        self.assertEqual("xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P", identifier)

    def test_extractor_can_get_record_status(self):
        record_status = MetsMetadataExtractor(self.content_path).get_record_status()
        self.assertEqual("store", record_status)

    def test_extractor_can_get_asset_order(self):
        asset_order = MetsMetadataExtractor(self.content_path).get_asset_order()
        expected_asset_order = [
            "ced165163e51e06e01dc44c35fea3eaf",
            "cc540920e91f05e4f6e4beb72dd441ac",
            "82cf9fa647dd1b3fbd9de71bbfb83fb2",
            "a527173445d117cbf177084bd34e60f2",
            "d438e94a39b7f7986e0cefb826801769"
        ]
        self.assertEqual(expected_asset_order, asset_order)

    def test_extractor_can_get_asset_with_path(self):
        asset_id = "cc540920e91f05e4f6e4beb72dd441ac"
        asset_metadata_path = self.content_path / "descriptor" / f"{asset_id}.mets2.xml"
        asset = MetsMetadataExtractor.get_asset(asset_metadata_path)
        expected_asset = Asset(
            id="cc540920e91f05e4f6e4beb72dd441ac",
            files=[
                AssetFile(
                    id="_1cc90346d5f1fe485fc8a3c55d10e753",
                    path=Path("data/00000002.access.jpg"),
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

    def test_extractor_can_get_repository_item(self):
        item = MetsMetadataExtractor(self.content_path).get_repository_item()
        print(item)
        self.assertEqual("xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P", item.id)
        self.assertEqual(RecordStatus.STORE, item.record_status)
        expected_asset_order = [
            "ced165163e51e06e01dc44c35fea3eaf",
            "cc540920e91f05e4f6e4beb72dd441ac",
            "82cf9fa647dd1b3fbd9de71bbfb83fb2",
            "a527173445d117cbf177084bd34e60f2",
            "d438e94a39b7f7986e0cefb826801769"
        ]

        self.assertEqual(expected_asset_order, item.asset_order)
        self.assertEqual(5, len(item.assets))
        self.assertTrue(all(isinstance(asset, Asset) for asset in item.assets))
