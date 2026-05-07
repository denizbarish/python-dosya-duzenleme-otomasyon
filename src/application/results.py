from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class OperationResult:
    success: bool
    message: str


@dataclass(frozen=True)
class MoveRecord:
    source: Path
    destination: Path
    applied: bool


@dataclass
class OrganizationSummary:
    moved: list[MoveRecord] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DirectoryStats:
    total_items: int
    file_count: int
    directory_count: int
    total_size_bytes: int


@dataclass(frozen=True)
class FileTypeDistribution:
    """Dosya türüne göre dağılım."""
    distribution: dict[str, int]  # Tür -> Sayı


@dataclass(frozen=True)
class ExtensionAnalysis:
    """Uzantıya göre dağılım."""
    distribution: dict[str, int]  # Uzantı -> Sayı


@dataclass(frozen=True)
class DirectoryDepthAnalysis:
    """Klasör derinlik analizi."""
    max_depth: int
    depth_distribution: dict[int, int]  # Derinlik -> Klasör sayısı
