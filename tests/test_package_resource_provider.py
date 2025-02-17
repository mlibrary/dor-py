from pathlib import Path
from unittest import TestCase

from dor.providers.package_resource_provider import PackageResourceProvider
from dor.providers.file_system_file_provider import FilesystemFileProvider


class PackageResourceProviderTest(TestCase):
    def setUp(self):
        self.file_provider = FilesystemFileProvider()
        self.test_submission_path = Path("tests/fixtures/test_submission_package")
        self.data_path = (
            self.test_submission_path
            / "xyzzy-00000000-0000-0000-0000-000000000001-v1"
            / "data"
        )

        return super().setUp()

    def test_provider_can_be_set_up(self):
        provider = PackageResourceProvider(self.data_path, self.file_provider)

    def test_provider_can_find_descriptors(self):

        expected_files = []

        expected_files.append(
            self.data_path
            / "00000000-0000-0000-0000-000000000001"
            / "descriptor"
            / "00000000-0000-0000-0000-000000000001.monograph.mets2.xml"
        )
        expected_files.append(
            self.data_path
            / "00000000-0000-0000-0000-000000001001"
            / "descriptor"
            / "00000000-0000-0000-0000-000000001001.file_set.mets2.xml"
        )
        expected_files.append(
            self.data_path
            / "00000000-0000-0000-0000-000000001002"
            / "descriptor"
            / "00000000-0000-0000-0000-000000001002.file_set.mets2.xml"
        )

        provider = PackageResourceProvider(self.data_path, self.file_provider)
        descriptor_files = provider.descriptor_files
        self.assertSetEqual(set(descriptor_files), set(expected_files))

    def test_provider_can_parse_resources(self):

        provider = PackageResourceProvider(self.data_path, self.file_provider)

        resources = provider.get_resources()
        self.assertEqual(len(resources), 3)
