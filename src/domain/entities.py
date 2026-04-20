from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class FileEntry:
    """Dosya sistemi girdisinin sade bir domain modeli."""

    path: Path
    is_directory: bool
    size_bytes: int
    modified_at: datetime
