from pathlib import Path
from typing import Optional, Protocol

from src.domain.entities import FileEntry


class FileSystemGateway(Protocol):
    """Dosya sistemi islemlerini soyutlar."""

    def list_entries(self, root: Path, recursive: bool, include_hidden: bool) -> list[FileEntry]:
        ...

    def create_file(self, path: Path) -> None:
        ...

    def create_directory(self, path: Path) -> None:
        ...

    def rename(self, source: Path, new_name: str) -> Path:
        ...

    def delete(self, target: Path, recursive: bool) -> None:
        ...

    def move(self, source: Path, destination: Path) -> Path:
        ...

    def ensure_directory(self, path: Path) -> None:
        ...

    def exists(self, path: Path) -> bool:
        ...

    def is_directory(self, path: Path) -> bool:
        ...


class RuleProvider(Protocol):
    """Dosya duzenleme kurallarini saglar."""

    def destination_folder_for(self, file_path: Path) -> Optional[str]:
        ...

    def default_folder(self) -> str:
        ...
