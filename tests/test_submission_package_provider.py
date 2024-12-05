from pathlib import Path
from unittest import TestCase

from dor.providers.submission_package_provider import SubmissionPackageProvider
from dor.providers.submission_package_provider import *


class SubmissionPackageProviderTest(TestCase):

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
        provider = SubmissionPackageProvider(self.data_path)

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

        provider = SubmissionPackageProvider(self.data_path)
        descriptor_files = provider.descriptor_files
        self.assertSetEqual(set(descriptor_files), set(expected_files))

    def test_provider_can_parse_resources(self):

        provider = SubmissionPackageProvider(self.data_path)

        resources = provider.get_resources()
        self.assertEqual(len(resources), 3)
