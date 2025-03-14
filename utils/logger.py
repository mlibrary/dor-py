import requests

from datetime import datetime
from typing import Any

from dor.config import config
from dor.providers.package_generator import PackageResult
from enum import Enum


class LogStatus(Enum):
    SUCCESS = "Info"
    FAILURE = "Error"


class Logger:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.token = None
        self.impersonate_token = None
        self.user_id = None
        self.url = config.pocket_base_url
        self.pocket_base_username = config.pocket_base_username
        self.pocket_base_password = config.pocket_base_password
        self._authenticate()

    def _authenticate(self):
        url = f"{self.url}/api/collections/_superusers/auth-with-password"
        payload = {
            "identity": self.pocket_base_username,
            "password": self.pocket_base_password,
        }
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            auth_data = response.json()
            self.token = auth_data["token"]
            self.user_id = auth_data["record"]["id"]
            self._impersonate_user()
        else:
            raise Exception(
                f"Failed to save logs: {response.status_code}, {response.text}"
            )

    def _impersonate_user(self):
        if not self.token:
            return

        url = f"{self.url}/api/collections/_superusers/impersonate/{self.user_id}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = {"duration": 86400}  # Set to 24 hours

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            impersonate_data = response.json()
            self.impersonate_token = impersonate_data["token"]

        except requests.exceptions.HTTPError as err:
            raise Exception(f"Failed to impersonate: {err}")

    def _collection_exists(self):
        if not self.impersonate_token:
            return False

        url = f"{self.url}/api/collections/{self.collection_name}"
        headers = {
            "Authorization": f"Bearer {self.impersonate_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        return response.status_code == 200

    def _create_log_collection(self):
        if not self.impersonate_token:
            return

        url = f"{self.url}/api/collections"
        headers = {
            "Authorization": f"Bearer {self.impersonate_token}",
            "Content-Type": "application/json",
        }

        collection_data: dict[str, Any] = {
            "name": self.collection_name,
            "type": "base",
            "fields": [
                {"name": "PackageIdentifier", "type": "text"},
                {"name": "DepositGroupIdentifier", "type": "text"},
                {"name": "Level", "type": "text", "required": True},
                {"name": "Message", "type": "text", "required": True},
                {
                    "name": "Timestamp",
                    "type": "autodate",
                    "onCreate": True,
                    "onUpdate": False,
                },
            ],
            "system": False,
        }

        response = requests.post(url, json=collection_data, headers=headers)

        if not response.status_code == 200:
            raise Exception(
                f"Failed to save logs: {response.status_code}, {response.text}"
            )

    def _write_log(self, log_data: dict[str, Any]):
        if not self.impersonate_token:
            return

        log_data["Timestamp"] = datetime.now().isoformat()
        if not self._collection_exists():
            self._create_log_collection()

        url = f"{self.url}/api/collections/{self.collection_name}/records"
        headers = {
            "Authorization": f"Bearer {self.impersonate_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=log_data, headers=headers)

        if not response.status_code == 200:
            raise Exception(
                f"Failed to save logs: {response.status_code}, {response.text}"
            )

    def _log(self, package_result: PackageResult):
        try:
            log_entry: dict[str, Any] = {
                "PackageIdentifier": package_result.package_identifier,
                "DepositGroupIdentifier": package_result.deposit_group_identifier,
                "Level": (
                    LogStatus.SUCCESS if (package_result.success) else LogStatus.FAILURE
                ).value,
                "Message": package_result.message,
            }
            self._write_log(log_entry)
        except Exception as e:
            raise Exception(f"Failed to save logs: {e}")

    def log_result(self, package_result: PackageResult):
        self._log(package_result)
        