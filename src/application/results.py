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
