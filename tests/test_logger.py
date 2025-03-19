from typing import Any
from unittest import TestCase

import requests

from dor.config import config
from dor.providers.package_generator import PackageResult
from utils.logger import LogLevel, Logger


class TestLoggerIntegration(TestCase):

    def setUp(self):
        self.collection_name = "test_logs"
        self.logger = Logger(
            collection_name=self.collection_name,
            pb_username=config.pocketbase.pb_username,
            pb_password=config.pocketbase.pb_password,
            pb_url=config.pocketbase.pb_url
        )
        self.package_identifier = "package_123"
        self.deposit_group_identifier = "group_123"
        self.success = True
        self.success_message = "Test package success"
        self.error = False
        self.error_message = "Test package Error"

        self.logger.reset_log_collection()

    def test_log_success_result(self):
        try:
            test_package_result: PackageResult = PackageResult(
                package_identifier=self.package_identifier,
                deposit_group_identifier=self.deposit_group_identifier,
                success=self.success,
                message=self.success_message,
            )
            self.logger.log_result(test_package_result)

            params: dict[str, Any] = {
                "page": 1,
                "perPage": 1,
                "filter": f"PackageIdentifier='{self.package_identifier}' && Level='{LogLevel.INFO.value}'",
                "sort": "-Timestamp",
            }
            url = f"{self.logger.pb_url}/api/collections/{self.collection_name}/records"

            response = requests.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {self.logger.impersonate_token}"},
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()

            logs = data.get("items", [])
            self.assertGreater(len(logs), 0)
            self.assertEqual(logs[0]["Message"], "Test package success")
            self.assertEqual(logs[0]["Level"], LogLevel.INFO.value)

        except Exception as e:
            self.fail(f"test_log_success_result test failed: {e}")

    def test_log_error_result(self):
        try:
            test_package_result: PackageResult = PackageResult(
                package_identifier=self.package_identifier,
                deposit_group_identifier=self.deposit_group_identifier,
                success=self.error,
                message=self.error_message,
            )
            self.logger.log_result(test_package_result)

            params: dict[str, Any] = {
                "page": 1,
                "perPage": 1,
                "filter": f"PackageIdentifier='{self.package_identifier}' && Level='{LogLevel.ERROR.value}'",
                "sort": "-Timestamp",
            }
            url = (
                f"{self.logger.pb_url}/api/collections/{self.collection_name}/records"
            )
            response = requests.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {self.logger.impersonate_token}"},
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            logs = data.get("items", [])
            self.assertGreater(len(logs), 0)
            self.assertEqual(logs[0]["Message"], "Test package Error")
            self.assertEqual(logs[0]["Level"], LogLevel.ERROR.value)

        except Exception as e:
            self.fail(f"test_log_error_result test failed: {e}")
            