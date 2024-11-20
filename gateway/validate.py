import subprocess
from abc import ABC, abstractmethod
from typing import List, Optional

class OCFLFixityValidator(ABC):
    @abstractmethod
    def validate_repository(self, no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def validate_object(self, object_id: str, no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def validate_multiple_objects(self, object_paths: List[str], no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def _run_rocfl_command(self, command: List[str]) -> str:
        pass


class RocflOCFLFixityValidator(OCFLFixityValidator):
    def __init__(self, repository_path: str):
        self.repository_path = repository_path

    def validate_repository(self, no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = ['rocfl', 'validate', '--repo', self.repository_path]

        # Add flags based on the function arguments
        if no_fixity:
            command.append('-n')  # Disable content fixity checks
        if log_level:
            command.extend(['-l', log_level])  # Set the log level (Error, Warning, etc.)
        if suppress_warning:
            command.extend(['-w', suppress_warning])  # Suppress a specific warning

        return self._run_rocfl_command(command)

    def validate_object(self, object_id: str, no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = ['rocfl', 'validate', f'{object_id}']

        # Add flags based on the function arguments
        if no_fixity:
            command.append('-n')  # Disable content fixity checks
        if log_level:
            command.extend(['-l', log_level])  # Set the log level (Error, Warning, etc.)
        if suppress_warning:
            command.extend(['-w', suppress_warning])  # Suppress a specific warning

        return self._run_rocfl_command(command)

    def validate_multiple_objects(self, object_paths: List[str], no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = ['rocfl', 'validate', '-p'] + object_paths

        # Add flags based on the function arguments
        if no_fixity:
            command.append('-n')  # Disable content fixity checks
        if log_level:
            command.extend(['-l', log_level])  # Set the log level (Error, Warning, etc.)
        if suppress_warning:
            command.extend(['-w', suppress_warning])  # Suppress a specific warning

        return self._run_rocfl_command(command)

    def _run_rocfl_command(self, command: List[str]) -> str:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
