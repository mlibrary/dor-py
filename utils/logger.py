import requests

from typing import Any

from dor.providers.package_generator import PackageResult
from enum import Enum


class LogLevel(Enum):
    INFO = "Info"
    ERROR = "Error"


class LoggerException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Logger:
    def __init__(self, collection_name: str, pb_username: str, pb_password: str, pb_url: str):
        self.collection_name = collection_name
        self.token = None
        self.impersonate_token = None
        self.user_id = None
        self.pb_url = pb_url
        self.pb_username = pb_username
        self.pb_password = pb_password
        self._authenticate()

    def _authenticate(self):
        url = f"{self.pb_url}/api/collections/_superusers/auth-with-password"
        payload = {
            "identity": self.pb_username,
            "password": self.pb_password,
        }
        response = requests.post(url, data=payload)

        if response.ok:
            auth_data = response.json()
            self.token = auth_data["token"]
            self.user_id = auth_data["record"]["id"]
            self._impersonate_user()
        else:
            raise LoggerException(
                f"Failed to save logs: {response.status_code}, {response.text}"
            )

    def _impersonate_user(self):
        if not self.token:
            raise LoggerException("Impersonate token is missing")

        url = f"{self.pb_url}/api/collections/_superusers/impersonate/{self.user_id}"
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
            raise LoggerException(f"Failed to impersonate: {err}")

    def _collection_exists(self):
        if not self.impersonate_token:
            raise LoggerException("Impersonate token is missing")

        url = f"{self.pb_url}/api/collections/{self.collection_name}"
        headers = {
            "Authorization": f"Bearer {self.impersonate_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        if not response.ok:
            return False # Collection does not exist
        return True # Collection exists

    def _create_log_collection(self):
        if not self.impersonate_token:
            raise LoggerException("Impersonate token is missing")

        url = f"{self.pb_url}/api/collections"
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

        if not response.ok:
            raise LoggerException(
                f"Failed to save logs: {response.status_code}, {response.text}"
            )

    def _write_log(self, log_data: dict[str, Any]):
        if not self.impersonate_token:
            raise LoggerException("Impersonate token is missing")

        if not self._collection_exists():
            raise LoggerException(f"Log collection {self.collection_name} does not exist.")

        url = f"{self.pb_url}/api/collections/{self.collection_name}/records"
        headers = {
            "Authorization": f"Bearer {self.impersonate_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=log_data, headers=headers)

        if not response.ok:
            raise LoggerException(
                f"Failed to save logs: {response.status_code}, {response.text}"
            )

    def _log(self, package_result: PackageResult):
        try:
            log_entry: dict[str, Any] = {
                "PackageIdentifier": package_result.package_identifier,
                "DepositGroupIdentifier": package_result.deposit_group_identifier,
                "Level": (
                    LogLevel.INFO if (package_result.success) else LogLevel.ERROR
                ).value,
                "Message": package_result.message,
            }
            self._write_log(log_entry)
        except LoggerException as e:
            raise LoggerException(f"Failed to save logs: {e}")

    def log_result(self, package_result: PackageResult):
        self._log(package_result)

    def search(self, package_identifier: str) -> PackageResult | None:
        params: dict[str, Any] = {
            "page": 1,
            "perPage": 1,
            "filter": f"PackageIdentifier='{package_identifier}'",
            "sort": "-Timestamp",
        }
        url = f"{self.pb_url}/api/collections/{self.collection_name}/records"

        response = requests.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {self.impersonate_token}"},
        )

        data = response.json()
        items = data["items"]
        if len(items) == 0:
            return None

        item = items[0]
        return PackageResult(
            package_identifier=item["PackageIdentifier"],
            deposit_group_identifier=item["DepositGroupIdentifier"],
            success=item["Level"] == LogLevel.INFO.value,
            message=item["Message"]
        )


    def _delete_log_collection(self) -> None:
        url = f"{self.pb_url}/api/collections/{self.collection_name}"

        response = requests.delete(
            url,
            headers={"Authorization": f"Bearer {self.impersonate_token}"},
        )
        response.raise_for_status()

    def reset_log_collection(self) -> None:
        if self._collection_exists():
            self._delete_log_collection()
        self._create_log_collection()
