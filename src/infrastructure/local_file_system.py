import shutil
from datetime import datetime
from pathlib import Path

from src.domain.entities import FileEntry


class LocalFileSystemGateway:
    """Gerçek dosya sistemine erişen altyapı sınıfı."""

    def list_entries(self, root: Path, recursive: bool, include_hidden: bool) -> list[FileEntry]:
        if recursive:
            paths = [path for path in root.rglob("*")]
        else:
            paths = [path for path in root.iterdir()]

        entries: list[FileEntry] = []
        for path in paths:
            if not include_hidden and self._is_hidden(path):
                continue

            stat = path.stat()
            entries.append(
                FileEntry(
                    path=path,
                    is_directory=path.is_dir(),
                    size_bytes=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime),
                )
            )
        return entries

    def create_file(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=False)

    def create_directory(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=False)

    def rename(self, source: Path, new_name: str) -> Path:
        destination = source.with_name(new_name)
        if destination.exists():
            raise FileExistsError(f"Aynı isimde hedef mevcut: {destination}")
        return source.rename(destination)

    def delete(self, target: Path, recursive: bool) -> None:
        if target.is_dir():
            if recursive:
                shutil.rmtree(target)
            else:
                target.rmdir()
            return

        target.unlink()

    def move(self, source: Path, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(f"Hedef dosya zaten var: {destination}")
        moved = shutil.move(str(source), str(destination))
        return Path(moved)

    def ensure_directory(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_directory(self, path: Path) -> bool:
        return path.is_dir()

    @staticmethod
    def _is_hidden(path: Path) -> bool:
        return any(part.startswith(".") for part in path.parts)
