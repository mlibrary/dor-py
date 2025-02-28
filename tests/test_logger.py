from unittest import TestCase
import requests
from utils.logger import Logger 


class TestLoggerIntegration(TestCase):

    def setUp(self):
        """Set up the Logger instance before each test"""
        self.collection_name = "test_logs"
        self.logger = Logger(collection_name=self.collection_name)
        self.pocket_base_url = 'http://pocketbase:8080'  
        self.pocket_base_username = 'test@umich.edu'  
        self.pocket_base_password = 'testumich'  

    def test_debug_log(self):
        try:
            self.logger.debug("Debug message", packageIdentifier="package_123_debug")
            url = f"{self.pocket_base_url}/api/collections/{self.collection_name}/records?filter=(packageIdentifier = 'package_123_debug')"
            response = requests.get(url, headers={'Authorization': f'Bearer {self.logger.impersonate_token}'})
            self.assertEqual(response.status_code, 200)
            data = response.json()

            logs = data.get('items', [])
            self.assertGreater(len(logs), 0)
            self.assertEqual(logs[0]['message'], "Debug message")
            self.assertEqual(logs[0]['level'], 'debug')

        except Exception as e:
            self.fail(f"Debug log test failed: {e}")

    def test_info_log(self):
        try:
            self.logger.info("Info message", packageIdentifier="package_123_info")
            url = f"{self.pocket_base_url}/api/collections/{self.collection_name}/records?filter=(packageIdentifier = 'package_123_info')"
            response = requests.get(url, headers={'Authorization': f'Bearer {self.logger.impersonate_token}'})
            self.assertEqual(response.status_code, 200)
            data = response.json()

            logs = data.get('items', [])
            self.assertGreater(len(logs), 0)
            self.assertEqual(logs[0]['message'], "Info message")
            self.assertEqual(logs[0]['level'], 'info')

        except Exception as e:
            self.fail(f"Info log test failed: {e}")

    def test_warn_log(self):
        try:
            self.logger.warn("Warn message", packageIdentifier="package_123_warn")
            url = f"{self.pocket_base_url}/api/collections/{self.collection_name}/records?filter=(packageIdentifier = 'package_123_warn')"
            response = requests.get(url, headers={'Authorization': f'Bearer {self.logger.impersonate_token}'})
            self.assertEqual(response.status_code, 200)
            data = response.json()

            logs = data.get('items', [])
            self.assertGreater(len(logs), 0)
            self.assertEqual(logs[0]['message'], "Warn message")
            self.assertEqual(logs[0]['level'], 'warn')

        except Exception as e:
            self.fail(f"Warn log test failed: {e}")

    def test_error_log(self):
        try:
            self.logger.error("Error message", packageIdentifier="package_123_error")
            url = f"{self.pocket_base_url}/api/collections/{self.collection_name}/records?filter=(packageIdentifier = 'package_123_error')"
            response = requests.get(url, headers={'Authorization': f'Bearer {self.logger.impersonate_token}'})
            self.assertEqual(response.status_code, 200)
            data = response.json()

            logs = data.get('items', [])
            self.assertGreater(len(logs), 0)
            self.assertEqual(logs[0]['message'], "Error message")
            self.assertEqual(logs[0]['level'], 'error')

        except Exception as e:
            self.fail(f"Error log test failed: {e}")

    def test_failed_log(self):
        try:
            url = f"{self.pocket_base_url}/api/collections/{self.collection_name}/records"
            invalid_log_data = {"invalid_field": "Test"}
            response = requests.post(url, json=invalid_log_data, headers={'Authorization': f'Bearer {self.logger.impersonate_token}'})
            self.assertNotEqual(response.status_code, 200)

        except Exception as e:
            self.fail(f"Failed log test failed: {e}")
