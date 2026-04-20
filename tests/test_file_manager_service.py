import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.application.file_manager_service import FileManagerService
from src.domain.exceptions import InvalidOperationError
from src.infrastructure.json_rule_provider import JsonRuleProvider
from src.infrastructure.local_file_system import LocalFileSystemGateway


class FileManagerServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.config_path = self.root / "rules.json"

        payload = {
            "default_folder": "Diğer",
            "rules": {
                "Belgeler": [".pdf", ".txt"],
                "Görseller": [".png", ".jpg"],
            },
        }
        self.config_path.write_text(json.dumps(payload), encoding="utf-8")

        self.file_system = LocalFileSystemGateway()
        self.rule_provider = JsonRuleProvider(self.config_path)
        self.service = FileManagerService(self.file_system, self.rule_provider)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_organize_by_rules_moves_files_to_expected_folders(self) -> None:
        target_dir = self.root / "hedef"
        target_dir.mkdir(exist_ok=True)

        (target_dir / "rapor.pdf").write_text("içerik", encoding="utf-8")
        (target_dir / "gorsel.png").write_text("img", encoding="utf-8")
        (target_dir / "bilinmeyen.xyz").write_text("diğer", encoding="utf-8")

        summary = self.service.organize_by_rules(target_dir, dry_run=False)

        self.assertEqual(len(summary.moved), 3)
        self.assertTrue((target_dir / "Belgeler" / "rapor.pdf").exists())
        self.assertTrue((target_dir / "Görseller" / "gorsel.png").exists())
        self.assertTrue((target_dir / "Diğer" / "bilinmeyen.xyz").exists())

    def test_crud_flow_create_rename_delete(self) -> None:
        draft_file = self.root / "taslak.txt"
        self.service.create_item(draft_file, is_directory=False)
        self.assertTrue(draft_file.exists())

        self.service.rename_item(draft_file, "son.txt")
        renamed = self.root / "son.txt"
        self.assertTrue(renamed.exists())

        self.service.delete_item(renamed)
        self.assertFalse(renamed.exists())

    def test_delete_non_recursive_directory_should_raise(self) -> None:
        folder = self.root / "örnek_klasör"
        self.service.create_item(folder, is_directory=True)

        with self.assertRaises(InvalidOperationError):
            self.service.delete_item(folder, recursive=False)

        self.service.delete_item(folder, recursive=True)
        self.assertFalse(folder.exists())

    def test_turkish_character_paths_are_supported(self) -> None:
        target_dir = self.root / "hedef_calisma_ç"
        target_dir.mkdir(exist_ok=True)

        turkish_name = "özet_şablon.txt"
        (target_dir / turkish_name).write_text("İçerik", encoding="utf-8")

        summary = self.service.organize_by_rules(target_dir, dry_run=False)

        self.assertEqual(len(summary.moved), 1)
        self.assertTrue((target_dir / "Belgeler" / turkish_name).exists())


if __name__ == "__main__":
    unittest.main()
