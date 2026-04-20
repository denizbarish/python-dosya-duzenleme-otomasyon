import sys
from pathlib import Path

from src.application.file_manager_service import FileManagerService
from src.infrastructure.json_rule_provider import JsonRuleProvider
from src.infrastructure.local_file_system import LocalFileSystemGateway
from src.presentation.console_app import ConsoleApplication


def _configure_utf8_stdio() -> None:
    """Try to enforce UTF-8 for terminal I/O to avoid Turkish character issues."""
    streams = (sys.stdin, sys.stdout, sys.stderr)
    for stream in streams:
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                continue


def build_app() -> ConsoleApplication:
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "config" / "organizasyon_kurallari.json"

    file_system = LocalFileSystemGateway()
    rule_provider = JsonRuleProvider(config_path)
    service = FileManagerService(file_system=file_system, rule_provider=rule_provider)
    return ConsoleApplication(service=service)


if __name__ == "__main__":
    _configure_utf8_stdio()
    app = build_app()
    app.run()
