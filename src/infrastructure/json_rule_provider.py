import json
from pathlib import Path
from typing import Optional


class JsonRuleProvider:
    """JSON dosyasındaki uzantı-kategori eşleşmelerini yükler."""

    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._default_folder = "Diğer"
        self._extension_map: dict[str, str] = {}
        self._load()

    def destination_folder_for(self, file_path: Path) -> Optional[str]:
        return self._extension_map.get(file_path.suffix.lower())

    def default_folder(self) -> str:
        return self._default_folder

    def _load(self) -> None:
        if not self._config_path.exists():
            return

        # utf-8-sig safely handles files saved as UTF-8 with BOM.
        with self._config_path.open("r", encoding="utf-8-sig") as config_file:
            payload = json.load(config_file)

        self._default_folder = payload.get("default_folder", "Diğer")
        raw_rules: dict[str, list[str]] = payload.get("rules", {})

        for folder_name, extensions in raw_rules.items():
            for extension in extensions:
                normalized = self._normalize_extension(extension)
                self._extension_map[normalized] = folder_name

    @staticmethod
    def _normalize_extension(extension: str) -> str:
        cleaned = extension.strip().lower()
        if not cleaned.startswith("."):
            cleaned = f".{cleaned}"
        return cleaned
