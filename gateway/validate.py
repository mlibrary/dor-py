from dataclasses import dataclass
import subprocess
from abc import ABC, abstractmethod
from typing import List, Optional

@dataclass
class FixityCheckResult:
    is_valid: bool
    message: str

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

class RocflOCFLFixityValidator(OCFLFixityValidator):
    def __init__(self, repository_path: str):
        self.repository_path = repository_path

    def validate_repository(self, no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = self._build_command(['rocfl', 'validate', self.repository_path], no_fixity, log_level, suppress_warning)
        return self._run_rocfl_command(command)

    def validate_object(self, object_id: str, no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = self._build_command(['rocfl', 'validate', object_id], no_fixity, log_level, suppress_warning)
        return self._run_rocfl_command(command)

    def validate_multiple_objects(self, object_paths: List[str], no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = self._build_command(['rocfl', 'validate', '-p'] + object_paths, no_fixity, log_level, suppress_warning)
        return self._run_rocfl_command(command)

    def _run_rocfl_command(self, command: List[str]) -> str:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            error_message = f"STDOUT:\n{e.stdout.strip()}\n" if e.stdout else ""
            error_message += f"STDERR:\n{e.stderr.strip()}\n" if e.stderr else ""
            return error_message

    def _build_command(self, base_command: List[str], no_fixity: bool, log_level: Optional[str], suppress_warning: Optional[str]) -> List[str]:
        if no_fixity:
            base_command.append('-n')  # Disable content fixity checks
        if log_level:
            base_command.extend(['-l', log_level])  # Set the log level (Error, Warning, etc.)
        if suppress_warning:
            base_command.extend(['-w', suppress_warning])  # Suppress a specific warning   
        return base_command
    
class FixityValidator():
    def __init__(self, rocflvalidator: RocflOCFLFixityValidator):
        self.rocflvalidator = rocflvalidator

    def check_object_fixity(self, object_id: str) -> FixityCheckResult:
        result = self.rocflvalidator.validate_object(object_id)
        if "error" in result.lower():
            return FixityCheckResult(False, result)
        return FixityCheckResult(True, result)

