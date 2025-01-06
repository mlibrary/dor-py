from pathlib import Path
from unittest import TestCase

from dor.providers.package_resource_provider import PackageResourceProvider
from dor.providers.package_resource_provider import *


class PackageResourceProviderTest(TestCase):

    def setUp(self):
        self.test_submission_path = Path("tests/fixtures/test_submission_package")
        self.data_path = (
            self.test_submission_path
            / "xyzzy-0001-v1"
            / "data"
            / "00000000-0000-0000-0000-000000000001"
        )

        return super().setUp()

    def test_provider_can_be_set_up(self):
        provider = PackageResourceProvider(self.data_path / "descriptor")

    def test_provider_can_find_descriptors(self):

        expected_files = []

        expected_files.append(
            self.data_path
            / "descriptor"
            / "00000000-0000-0000-0000-000000000001.monograph.mets2.xml"
        )
        expected_files.append(
            self.data_path
            / "descriptor"
            / "00000000-0000-0000-0000-000000001001.asset.mets2.xml"
        )
        expected_files.append(
            self.data_path
            / "descriptor"
            / "00000000-0000-0000-0000-000000001002.asset.mets2.xml"
        )

        provider = PackageResourceProvider(self.data_path / "descriptor")
        descriptor_files = provider.descriptor_files
        self.assertSetEqual(set(descriptor_files), set(expected_files))

    def test_provider_can_parse_resources(self):

        provider = PackageResourceProvider(self.data_path / "descriptor")

        resources = provider.get_resources()
        self.assertEqual(len(resources), 3)
