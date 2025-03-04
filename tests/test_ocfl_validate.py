import hashlib
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch, MagicMock, mock_open

from dor.providers.file_system_file_provider import FilesystemFileProvider
from gateway.validate import  FixityValidator, RocflOCFLFixityValidator

class TestRocflOCFLFixityValidator(unittest.TestCase):
    def setUp(self):
        # Setup for testing
        self.fixture_path = Path("tests/fixtures/test_ocfl_repo")
        self.repository_path = str(self.fixture_path)
        self.validator = RocflOCFLFixityValidator(repository_path=self.fixture_path)
        self.file_provider = FilesystemFileProvider()

        # Common patches
        self.mock_makedirs = patch.object(self.file_provider, "create_directories").start()
        self.mock_open = patch('builtins.open', mock_open(read_data='{"content": [{"sha1": "some_sha1_hash_value", "sha512": "some_sha512_hash_value"}]}')).start()
        self.mock_rmtree = patch.object(self.file_provider, "delete_dir_and_contents").start()
        self.mock_run = patch('subprocess.run').start()

        # calling protected method
        self.build_command = getattr(self.validator, '_build_command')

    def tearDown(self):
        # Stop all patches
        patch.stopall()

    def test_validate_repository_success(self):
        # Mock the return value for subprocess.run
        self.mock_run.return_value = MagicMock(stdout="Valid repository.\n", returncode=0)

        # Run the validation
        result = self.validator.validate_repository()

        # Assert subprocess.run was called with the correct arguments
        self.mock_run.assert_called_once_with(['rocfl', '-r', self.repository_path, 'validate'], capture_output=True, text=True, check=True)
        self.assertEqual(result, "Valid repository.\n")

    def test_validate_repository_with_flags(self):
        self.mock_run.return_value = MagicMock(stdout="Valid repository.\n", returncode=0)
        result = self.validator.validate_repository(no_fixity=True, log_level="Error", suppress_warning="Warning123")

        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate', '-n', '-l', 'Error', '-w', 'Warning123'
        ], capture_output=True, text=True, check=True)
        self.assertEqual(result, "Valid repository.\n")

    def test_validate_object_success(self):
        self.mock_run.return_value = MagicMock(stdout="Object urn:example:rocfl:object-1 is valid.\n", returncode=0)
        result = self.validator.validate_objects(["urn:example:rocfl:object-1"])

        self.mock_run.assert_called_once_with(['rocfl',  '-r', self.repository_path, 'validate', 'urn:example:rocfl:object-1'], capture_output=True, text=True, check=True)
        self.assertEqual(result, "Object urn:example:rocfl:object-1 is valid.\n")

    def test_validate_repository_missing_versions_E008(self):
        self.mock_run.return_value = MagicMock(
            stdout="Error: E008 OCFL Object content must be stored as a sequence of one or more versions.\n",
            returncode=1
        )

        # Call the validate method and check the result
        result = self.validator.validate_repository(log_level='Error')

        # Assert that the subprocess.run was called with the expected arguments
        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate', '-l', 'Error'
        ], capture_output=True, text=True, check=True)

        # Assert that the result contains the expected error message for E008
        self.assertIn("Error: E008", result)
        self.assertIn("OCFL Object content must be stored as a sequence of one or more versions.", result)

    def test_validate_object_with_flags(self):
        self.mock_run.return_value = MagicMock(stdout="Object urn:example:rocfl:object-1 is valid.\n", returncode=0)
        result = self.validator.validate_objects(["urn:example:rocfl:object-1"], no_fixity=True, log_level="Warning", suppress_warning="FileNotFound")

        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate', 'urn:example:rocfl:object-1', '-n', '-l', 'Warning', '-w', 'FileNotFound'
        ], capture_output=True, text=True, check=True)
        self.assertEqual(result, "Object urn:example:rocfl:object-1 is valid.\n")

    def test_validate_multiple_objects_success(self):
        self.mock_run.return_value = MagicMock(stdout="Valid object object-1/\nValid object object-2/\n", returncode=0)
        result = self.validator.validate_multiple_objects_by_path(["object-1/", "object-2/"])

        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate', '-p', 'object-1/', 'object-2/'
        ], capture_output=True, text=True, check=True)
        self.assertEqual(result, "Valid object object-1/\nValid object object-2/\n")

    def test_validate_multiple_objects_with_flags(self):
        self.mock_run.return_value = MagicMock(stdout="Valid object object-1/\nValid object object-2/\n", returncode=0)

        # Simulate the flags and call the function
        result = self.validator.validate_multiple_objects_by_path(
            ["object-1/", "object-2/"], no_fixity=True, log_level="Error", suppress_warning="ObjectMissing"
        )

        # Ensure subprocess.run was called with the expected arguments, including flags
        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate', '-p', 'object-1/', 'object-2/', '-n', '-l', 'Error', '-w', 'ObjectMissing'
        ], capture_output=True, text=True, check=True)

        # Assert the correct result output
        self.assertEqual(result, "Valid object object-1/\nValid object object-2/\n")

    def test_validate_invalid_object(self):
        self.mock_run.return_value = MagicMock(stdout="Error: Object urn:example:rocfl:object-3 not found.\n", returncode=1)
        result = self.validator.validate_objects(["urn:example:rocfl:object-3"])

        self.mock_run.assert_called_once_with(['rocfl', '-r', self.repository_path, 'validate', 'urn:example:rocfl:object-3'], capture_output=True, text=True, check=True)
        self.assertEqual(result, "Error: Object urn:example:rocfl:object-3 not found.\n")

    def test_fixity_check_failure(self):
        # Simulate a fixity check failure by changing the content and hashing
        new_sha512 = hashlib.sha512(b"modified content").hexdigest()

        self.mock_run.return_value = MagicMock(
            stdout=f"Error: Content fixity check failed for urn:example:rocfl:object-1 v1.\nExpected SHA-512 hash: dummy_sha512_hash_value_here\nActual SHA-512 hash: {new_sha512}\n",
            returncode=1
        )
        result = self.validator.validate_objects(["urn:example:rocfl:object-1"])

        self.mock_run.assert_called_once_with(['rocfl', '-r', self.repository_path, 'validate', 'urn:example:rocfl:object-1'], capture_output=True, text=True, check=True)
        self.assertIn("Error: Content fixity check failed", result)
        self.assertIn("Expected SHA-512 hash", result)
        self.assertIn("Actual SHA-512 hash", result)

    def test_validate_repo_trigger_warning_W004(self):
        # Simulate a warning in the validation output
        self.mock_run.return_value = MagicMock(
            stdout="Valid repository.\nWarning W004: 'For content-addressing, OCFL Objects SHOULD use sha512.'\n",
            returncode=0
        )

        result = self.validator.validate_repository()

        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate'
        ], capture_output=True, text=True, check=True)

        self.assertIn("Warning W004:", result)
        self.assertIn("For content-addressing, OCFL Objects SHOULD use sha512.", result)

    def test_validate_repo_with_suppress_warning_W004(self):
        # Simulate suppression of a warning
        self.mock_run.return_value = MagicMock(
            stdout="Valid repository. Warning W004 suppressed: 'For content-addressing, OCFL Objects SHOULD use sha512.'\n",
            returncode=0
        )

        result = self.validator.validate_repository(suppress_warning="W004")

        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate', '-w', "W004"
        ], capture_output=True, text=True, check=True)

        self.assertEqual(result, "Valid repository. Warning W004 suppressed: 'For content-addressing, OCFL Objects SHOULD use sha512.'\n")

    def test_validate_object_trigger_warning_W004(self):
        # Simulate a warning for a specific object
        self.mock_run.return_value = MagicMock(
            stdout="Valid repository.\nWarning W004: 'For content-addressing, OCFL Objects SHOULD use sha512.'\n",
            returncode=0
        )

        result = self.validator.validate_objects(object_ids=["urn:example:rocfl:object-1"])

        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate', 'urn:example:rocfl:object-1'
        ], capture_output=True, text=True, check=True)

        self.assertIn("Warning W004:", result)
        self.assertIn("For content-addressing, OCFL Objects SHOULD use sha512.", result)

    def test_validate_object_suppress_warning_W004(self):
        # Simulate the suppression of warning W004
        self.mock_run.return_value = MagicMock(
            stdout="Valid repository. Warning W004 suppressed: 'For content-addressing, OCFL Objects SHOULD use sha512.'\n",
            returncode=0
        )
        result = self.validator.validate_objects(object_ids=["urn:example:rocfl:object-1"], suppress_warning="W004")

        # Assert
        self.mock_run.assert_called_once_with([
            'rocfl', '-r', self.repository_path, 'validate', 'urn:example:rocfl:object-1', '-w', 'W004'
        ], capture_output=True, text=True, check=True)

        self.assertIn("Warning W004 suppressed:", result)
        self.assertIn("For content-addressing, OCFL Objects SHOULD use sha512.", result)
        self.assertNotIn("Error", result)

    def test_build_command_no_flags(self):
        base_command = ['rocfl', '-r', self.repository_path, 'validate']      
        result = self.build_command(base_command, no_fixity=False, log_level=None, suppress_warning=None)

        # Assert that no flags are added
        self.assertEqual(result, ['rocfl', '-r', self.repository_path, 'validate'])

    def test_build_command_with_no_fixity(self):
        base_command = ['rocfl', '-r', self.repository_path, 'validate']
        result = self.build_command(base_command, no_fixity=True, log_level=None, suppress_warning=None)

        # Assert that '-n' flag is added
        self.assertEqual(result, ['rocfl', '-r', self.repository_path, 'validate', '-n'])

    def test_build_command_with_log_level(self):
        base_command = ['rocfl', '-r', self.repository_path, 'validate']
        result = self.build_command(base_command, no_fixity=False, log_level='Error', suppress_warning=None)

        # Assert that '-l Error' is added
        self.assertEqual(result, ['rocfl', '-r', self.repository_path, 'validate', '-l', 'Error'])

    def test_build_command_with_suppress_warning(self):
        base_command = ['rocfl', '-r', self.repository_path, 'validate']
        result = self.build_command(base_command, no_fixity=False, log_level=None, suppress_warning='Warning123')

        # Assert that '-w Warning123' is added
        self.assertEqual(result, ['rocfl', '-r', self.repository_path, 'validate', '-w', 'Warning123'])

    def test_build_command_with_all_flags(self):
        base_command = ['rocfl', '-r', self.repository_path, 'validate']
        result = self.build_command(base_command, no_fixity=True, log_level='Error', suppress_warning='Warning123')

        # Assert that all flags are correctly added
        self.assertEqual(result, ['rocfl', '-r', self.repository_path, 'validate', '-n', '-l', 'Error', '-w', 'Warning123'])


class TestFixityValidator(unittest.TestCase):
    def test_validator_checks_object_fixity(self):
        self.mockrocflvalidator = MagicMock(spec = RocflOCFLFixityValidator)
        self.mockrocflvalidator.validate_objects.return_value = "Object object-1 is valid"
        self.fixityValidator = FixityValidator(self.mockrocflvalidator)
        result = self.fixityValidator.check_objects_fixity(object_ids=["object-1"])
        
        self.mockrocflvalidator.validate_objects.assert_called_once_with(["object-1"])
        self.assertTrue(result.is_valid)
        self.assertEqual("Object object-1 is valid", result.message)

class RocflOCFLFixityValidatorIntegrationTest(unittest.TestCase):   
    def setUp(self):
        # Link to fixtures -> https://github.com/OCFL/fixtures
        # Link to Validation Codes -> https://ocfl.io/1.1/spec/validation-codes.html
        self.repository_path = Path("tests/fixtures/test_rocfl_repo/")
        self.validator = RocflOCFLFixityValidator(repository_path=self.repository_path)

    def test_rocfl_validate_objects(self):
        try:
            object_id = ["ark:/12345/bcd987"]
            result = self.validator.validate_objects(object_ids = object_id)
            self.assertIn(f"Object {object_id[0]} is valid", result)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")   

    def test_rocfl_invalid_object(self):
        try:
            object_id = ["invalid-object-1"]
            result = self.validator.validate_objects(object_ids = object_id)
            self.assertIn(f"[ERROR] Not found: Object {object_id[0]}\n", result)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")   

    def test_rocfl_multiple_validate_objects_by_path(self):
        try:
            object_paths = [
                str("object-1/"),
                str("object-2/")
            ]

            object_identifiers = [
                "ark:/12345/bcd987",  
                "ark:123/abc"         
            ]
            result = self.validator.validate_multiple_objects_by_path(object_paths)

            for object_id in object_identifiers:
                self.assertIn(f"Object {object_id} is valid", result)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")  

    def test_rocfl_multiple_validate_objects(self):
        try:
            object_identifiers = [
                "ark:/12345/bcd987",  
                "ark:123/abc"         
            ]
            result = self.validator.validate_objects(object_identifiers)

            for object_id in object_identifiers:
                self.assertIn(f"Object {object_id} is valid", result)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")                 

    def test_rocfl_validate_object_trigger_warning_W004(self):
        try:
            object_id = ["ark:123/abc1"]
            result = self.validator.validate_objects(object_ids = object_id)
            self.assertIn(f"Object {object_id[0]} is valid", result)
            self.assertIn("Warning", result)
            self.assertIn("[W004]", result)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")  

    def test_rocfl_validate_object_suppress_warning(self):
        try:
            object_id = ["ark:123/abc1"]
            result = self.validator.validate_objects(object_ids = object_id, suppress_warning="W004")
            self.assertIn(f"Object {object_id[0]} is valid", result)
            self.assertNotIn("Warning", result)
            self.assertNotIn("[W004]", result)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")      

    def test_rocfl_validate_object_suppress_warning_w008_not_w004(self):
        try:
            object_id = ["ark:123/abc1"]
            result = self.validator.validate_objects(object_ids = object_id, suppress_warning="W008")
            self.assertIn(f"Object {object_id[0]} is valid", result)
            self.assertIn("Warning", result)
            self.assertIn("[W004]", result)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")              

    def test_validate_object_E023_extra_file_check_only_errors(self):
        try:
            # Return only the Errors
            object_id = ["info:bad05"]
            result = self.validator.validate_objects(object_ids = object_id, log_level="Error")
            self.assertIn("[E023]", result)
            self.assertNotIn("Warning", result)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")   

    def test_validate_object_E023_extra_file_check_warnings_and_errors(self):
        try:
            # Return both the Errors and Warning
            object_id = ["info:bad05"]
            result_without_log_level = self.validator.validate_objects(object_ids = object_id)
            self.assertIn("[E023]", result_without_log_level)
            self.assertIn("Warning", result_without_log_level)
        except subprocess.CalledProcessError as e:
            self.fail(f"ROCFL validation failed: {e.stderr}")                   
                
    def test_validate_specific_object_no_fixity_check(self):   
        try:
            # Updated the content file 
            #Test validating an object without fixity checks, does not throw fixity check error.
            object_id = ["http://example.org/minimal_mixed_digests"]
            result = self.validator.validate_objects(object_id, no_fixity=True)
            self.assertIn(f"Object {object_id[0]} is valid", result)
            self.assertNotIn("fixity check", result)  
        except RuntimeError as e:
            self.fail(f"ROCFL validation failed with error: {e}")   

    def test_validate_specific_object_with_fixity_check(self):      
        try:
            # Updated the content file 
            # validating an object with fixity checks, throws fixity error.
            object_id = ["http://example.org/minimal_mixed_digests"]
            result_fixity = self.validator.validate_objects(object_id)
            self.assertIn(f"Object {object_id[0]} is invalid", result_fixity)
            self.assertIn("fixity check", result_fixity)  
        except RuntimeError as e:
            self.fail(f"ROCFL validation failed with error: {e}")   
            
    def test_validate_fixity_repository(self):      
        try:
            result_fixity = self.validator.validate_repository()

            remove_space_result = ' '.join(result_fixity.split())
            self.assertIn("Total objects: 5", remove_space_result)
            self.assertIn("Invalid objects: 2", remove_space_result)  
                        
            self.assertIn("[E023]", result_fixity)
            self.assertIn("Warning", result_fixity)
            self.assertIn("[W004]", result_fixity)
            
            self.assertIn("Object ark:123/abc is valid", result_fixity)
            self.assertIn("Object ark:/12345/bcd987 is valid", result_fixity)
            self.assertIn("Object ark:123/abc1 is valid", result_fixity)
            self.assertIn("Object http://example.org/minimal_mixed_digests is invalid", result_fixity)
            self.assertIn("Object info:bad05 is invalid", result_fixity)           
        except RuntimeError as e:
            self.fail(f"ROCFL validation failed with error: {e}")          
