import json
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep

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

    def test_invalid_rule_config_should_raise_clear_error(self) -> None:
        broken_config_path = self.root / "broken_rules.json"
        broken_config_path.write_text(
            json.dumps({"default_folder": 123, "rules": []}), encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            JsonRuleProvider(broken_config_path)

    def test_advanced_filter_by_size_range(self) -> None:
        target_dir = self.root / "hedef"
        target_dir.mkdir(exist_ok=True)

        (target_dir / "küçük.txt").write_text("x", encoding="utf-8")
        (target_dir / "orta.txt").write_text("y" * 100, encoding="utf-8")
        (target_dir / "büyük.txt").write_text("z" * 1000, encoding="utf-8")

        # Sadece 50-500 byte aralığındaki dosyaları getir
        items = self.service.list_items_advanced(
            root=target_dir, recursive=False, min_size_bytes=50, max_size_bytes=500
        )

        # "orta.txt" sadece alınmalı (100 byte)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].path.name, "orta.txt")

    def test_advanced_filter_by_extension(self) -> None:
        target_dir = self.root / "hedef"
        target_dir.mkdir(exist_ok=True)

        (target_dir / "doc.txt").write_text("text", encoding="utf-8")
        (target_dir / "doc.pdf").write_text("pdf", encoding="utf-8")
        (target_dir / "doc.png").write_text("img", encoding="utf-8")

        items = self.service.list_items_advanced(
            root=target_dir, recursive=False, extension_filter=".txt"
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].path.suffix.lower(), ".txt")

    def test_analyze_file_types_produces_distribution(self) -> None:
        target_dir = self.root / "hedef"
        target_dir.mkdir(exist_ok=True)

        (target_dir / "rapor.pdf").write_text("content", encoding="utf-8")
        (target_dir / "özet.pdf").write_text("content", encoding="utf-8")
        (target_dir / "görsel.png").write_text("img", encoding="utf-8")
        (target_dir / "veri").write_text("data", encoding="utf-8")  # Uzantısız

        analysis = self.service.analyze_file_types(target_dir, recursive=False)

        self.assertEqual(analysis.distribution.get(".pdf"), 2)
        self.assertEqual(analysis.distribution.get(".png"), 1)
        self.assertEqual(analysis.distribution.get("(uzantısız)"), 1)

    def test_analyze_directory_depth(self) -> None:
        root_dir = self.root / "depth_test"
        root_dir.mkdir(exist_ok=True)

        level1 = root_dir / "level1"
        level1.mkdir(exist_ok=True)

        level2 = level1 / "level2"
        level2.mkdir(exist_ok=True)

        level3 = level2 / "level3"
        level3.mkdir(exist_ok=True)

        analysis = self.service.analyze_directory_depth(root_dir)

        self.assertEqual(analysis.max_depth, 3)
        self.assertGreater(len(analysis.depth_distribution), 0)


if __name__ == "__main__":
    unittest.main()
