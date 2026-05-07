from datetime import datetime
from pathlib import Path
from typing import Optional

from src.application.results import (
    DirectoryDepthAnalysis,
    DirectoryStats,
    ExtensionAnalysis,
    FileTypeDistribution,
    MoveRecord,
    OperationResult,
    OrganizationSummary,
)
from src.domain.entities import FileEntry
from src.domain.exceptions import InvalidOperationError, InvalidPathError
from src.domain.protocols import FileSystemGateway, RuleProvider


class FileManagerService:
    """Uygulamanın tüm dosya/klasör operasyonlarını yöneten servis."""

    def __init__(self, file_system: FileSystemGateway, rule_provider: RuleProvider) -> None:
        self._file_system = file_system
        self._rule_provider = rule_provider

    def list_items(
        self,
        root: Path,
        recursive: bool = False,
        extension_filter: Optional[str] = None,
        min_size_bytes: Optional[int] = None,
    ) -> list[FileEntry]:
        self._validate_existing_directory(root)
        items = self._file_system.list_entries(root=root, recursive=recursive, include_hidden=False)

        if extension_filter:
            normalized_extension = self._normalize_extension(extension_filter)
            items = [
                item
                for item in items
                if (not item.is_directory and item.path.suffix.lower() == normalized_extension)
            ]

        if min_size_bytes is not None:
            items = [item for item in items if item.size_bytes >= min_size_bytes]

        return sorted(items, key=lambda item: item.path.name.lower())

    def search_items(self, root: Path, keyword: str, recursive: bool = True) -> list[FileEntry]:
        self._validate_existing_directory(root)
        term = keyword.strip().lower()
        if not term:
            raise InvalidOperationError("Arama ifadesi boş bırakılamaz.")

        items = self._file_system.list_entries(root=root, recursive=recursive, include_hidden=False)
        return [item for item in items if term in item.path.name.lower()]

    def create_item(self, target: Path, is_directory: bool) -> OperationResult:
        if self._file_system.exists(target):
            raise InvalidOperationError(f"Hedef zaten mevcut: {target}")

        if is_directory:
            self._file_system.create_directory(target)
            return OperationResult(success=True, message=f"Klasör oluşturuldu: {target}")

        self._file_system.create_file(target)
        return OperationResult(success=True, message=f"Dosya oluşturuldu: {target}")

    def rename_item(self, source: Path, new_name: str) -> OperationResult:
        self._validate_existing_path(source)

        cleaned_name = new_name.strip()
        if not cleaned_name:
            raise InvalidOperationError("Yeni isim boş bırakılamaz.")

        renamed_path = self._file_system.rename(source, cleaned_name)
        return OperationResult(success=True, message=f"Yeniden adlandırıldı: {renamed_path}")

    def delete_item(self, target: Path, recursive: bool = False) -> OperationResult:
        self._validate_existing_path(target)

        if self._file_system.is_directory(target) and not recursive:
            raise InvalidOperationError(
                "Klasör silmek için recursive=True seçilmeli. Güvenlik için zorunludur."
            )

        self._file_system.delete(target=target, recursive=recursive)
        return OperationResult(success=True, message=f"Silindi: {target}")

    def organize_by_rules(self, root: Path, dry_run: bool = False) -> OrganizationSummary:
        self._validate_existing_directory(root)
        summary = OrganizationSummary()

        entries = self._file_system.list_entries(root=root, recursive=False, include_hidden=False)
        files = [entry for entry in entries if not entry.is_directory]

        for file_entry in files:
            destination_folder = (
                self._rule_provider.destination_folder_for(file_entry.path)
                or self._rule_provider.default_folder()
            )
            destination_dir = root / destination_folder
            candidate_path = destination_dir / file_entry.path.name
            unique_destination = self._next_available_path(candidate_path)

            if file_entry.path == unique_destination:
                summary.skipped.append(f"Atlandı (zaten doğru yerde): {file_entry.path}")
                continue

            if dry_run:
                summary.moved.append(
                    MoveRecord(source=file_entry.path, destination=unique_destination, applied=False)
                )
                continue

            self._file_system.ensure_directory(destination_dir)
            moved_path = self._file_system.move(file_entry.path, unique_destination)
            summary.moved.append(
                MoveRecord(source=file_entry.path, destination=moved_path, applied=True)
            )

        return summary

    def collect_stats(self, root: Path, recursive: bool = True) -> DirectoryStats:
        self._validate_existing_directory(root)
        entries = self._file_system.list_entries(root=root, recursive=recursive, include_hidden=False)

        file_count = sum(1 for item in entries if not item.is_directory)
        directory_count = sum(1 for item in entries if item.is_directory)
        total_size = sum(item.size_bytes for item in entries if not item.is_directory)

        return DirectoryStats(
            total_items=len(entries),
            file_count=file_count,
            directory_count=directory_count,
            total_size_bytes=total_size,
        )

    def _next_available_path(self, destination: Path) -> Path:
        if not self._file_system.exists(destination):
            return destination

        stem = destination.stem
        suffix = destination.suffix
        index = 1

        while True:
            candidate = destination.with_name(f"{stem}_{index}{suffix}")
            if not self._file_system.exists(candidate):
                return candidate
            index += 1

    def _validate_existing_directory(self, root: Path) -> None:
        if not self._file_system.exists(root):
            raise InvalidPathError(f"Klasör bulunamadı: {root}")
        if not self._file_system.is_directory(root):
            raise InvalidPathError(f"Klasör bekleniyordu fakat dosya geldi: {root}")

    def _validate_existing_path(self, path: Path) -> None:
        if not self._file_system.exists(path):
            raise InvalidPathError(f"Yol bulunamadı: {path}")

    @staticmethod
    def _normalize_extension(value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise InvalidOperationError("Uzantı filtresi boş olamaz.")
        if not normalized.startswith("."):
            normalized = f".{normalized}"
        return normalized

    def list_items_advanced(
        self,
        root: Path,
        recursive: bool = False,
        extension_filter: Optional[str] = None,
        min_size_bytes: Optional[int] = None,
        max_size_bytes: Optional[int] = None,
        modified_after: Optional[datetime] = None,
        modified_before: Optional[datetime] = None,
    ) -> list[FileEntry]:
        """Gelişmiş filtreleme ile öğeleri listele."""
        self._validate_existing_directory(root)
        items = self._file_system.list_entries(root=root, recursive=recursive, include_hidden=False)

        # Uzantı filtresi
        if extension_filter:
            normalized_extension = self._normalize_extension(extension_filter)
            items = [
                item
                for item in items
                if (not item.is_directory and item.path.suffix.lower() == normalized_extension)
            ]

        # Boyut filtreleri
        if min_size_bytes is not None:
            items = [item for item in items if item.size_bytes >= min_size_bytes]

        if max_size_bytes is not None:
            items = [item for item in items if item.size_bytes <= max_size_bytes]

        # Tarih filtreleri
        if modified_after is not None:
            items = [
                item
                for item in items
                if datetime.fromtimestamp(item.modified_time_unix) >= modified_after
            ]

        if modified_before is not None:
            items = [
                item
                for item in items
                if datetime.fromtimestamp(item.modified_time_unix) <= modified_before
            ]

        return sorted(items, key=lambda item: item.path.name.lower())

    def analyze_file_types(self, root: Path, recursive: bool = True) -> FileTypeDistribution:
        """Dosya türlerine göre dağılımı analiz et."""
        self._validate_existing_directory(root)
        entries = self._file_system.list_entries(root=root, recursive=recursive, include_hidden=False)
        files = [entry for entry in entries if not entry.is_directory]

        distribution: dict[str, int] = {}
        for file_entry in files:
            suffix = file_entry.path.suffix.lower()
            if not suffix:
                suffix = "(uzantısız)"
            distribution[suffix] = distribution.get(suffix, 0) + 1

        return FileTypeDistribution(distribution=distribution)

    def analyze_extensions(self, root: Path, recursive: bool = True) -> ExtensionAnalysis:
        """Uzantıların dağılımını analiz et (dosya sayısı)."""
        analysis = self.analyze_file_types(root, recursive)
        return ExtensionAnalysis(distribution=analysis.distribution)

    def analyze_directory_depth(self, root: Path) -> DirectoryDepthAnalysis:
        """Klasör derinliğini analiz et."""
        self._validate_existing_directory(root)

        def calculate_depth(path: Path, current_depth: int = 0) -> int:
            """Rekursif olarak maksimum derinliği hesapla."""
            max_d = current_depth
            try:
                for item in path.iterdir():
                    if item.is_dir() and not item.name.startswith("."):
                        max_d = max(max_d, calculate_depth(item, current_depth + 1))
            except (OSError, PermissionError):
                pass
            return max_d

        def collect_depth_distribution(path: Path, current_depth: int = 0) -> dict[int, int]:
            """Derinliğe göre klasör sayısını topla."""
            dist: dict[int, int] = {}
            if current_depth > 0:
                dist[current_depth] = dist.get(current_depth, 0) + 1
            try:
                for item in path.iterdir():
                    if item.is_dir() and not item.name.startswith("."):
                        sub_dist = collect_depth_distribution(item, current_depth + 1)
                        for depth, count in sub_dist.items():
                            dist[depth] = dist.get(depth, 0) + count
            except (OSError, PermissionError):
                pass
            return dist

        max_depth = calculate_depth(root)
        depth_distribution = collect_depth_distribution(root)

        return DirectoryDepthAnalysis(max_depth=max_depth, depth_distribution=depth_distribution)
