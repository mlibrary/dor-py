from dataclasses import dataclass
from pathlib import Path
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
    def validate_objects(self, object_ids: List[str], no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def validate_multiple_objects_by_path(self, object_paths: List[str], no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        pass

class RocflOCFLFixityValidator(OCFLFixityValidator):
    def __init__(self, repository_path: Path):
        self.repository_path = repository_path

    def validate_repository(self, no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = self._build_command(['rocfl', '-r', self.repository_path, 'validate'], no_fixity, log_level, suppress_warning)
        return self._run_rocfl_command(command)

    def validate_objects(self, object_ids: List[str], no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = self._build_command(['rocfl', '-r', self.repository_path, 'validate'] + object_ids, no_fixity, log_level, suppress_warning)
        return self._run_rocfl_command(command)

    def validate_multiple_objects_by_path(self, object_paths: List[str], no_fixity: bool = False, log_level: Optional[str] = None, suppress_warning: Optional[str] = None) -> str:
        command = self._build_command(['rocfl', '-r', self.repository_path, 'validate', '-p'] + object_paths, no_fixity, log_level, suppress_warning)
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

    def check_objects_fixity(self, object_ids: List[str]) -> FixityCheckResult:
        result = self.rocflvalidator.validate_objects(object_ids)
        if "error" in result.lower():
            return FixityCheckResult(False, result)
        return FixityCheckResult(True, result)
    