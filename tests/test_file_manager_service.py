import json
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep

from src.application.file_manager_service import FileManagerService
from src.domain.exceptions import InvalidOperationError, InvalidPathError
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

    # ============ SENARYO BAZLI (UÇTAN UCA) TESTLER ============

    def test_end_to_end_workflow_create_organize_search(self) -> None:
        """Tam iş akışı: dosya oluştur → düzenle → ara → istatistik al"""
        workspace = self.root / "workspace"
        workspace.mkdir(exist_ok=True)

        # 1. Dosya oluştur
        (workspace / "rapor_01.pdf").write_text("content1", encoding="utf-8")
        (workspace / "rapor_02.pdf").write_text("content2", encoding="utf-8")
        (workspace / "gorsel.png").write_text("img_data", encoding="utf-8")
        (workspace / "note.txt").write_text("text", encoding="utf-8")

        # 2. Listele (tüm dosyalar)
        items = self.service.list_items(workspace, recursive=False)
        self.assertEqual(len(items), 4)

        # 3. Düzenle (kural tabanlı)
        summary = self.service.organize_by_rules(workspace, dry_run=False)
        self.assertGreater(len(summary.moved), 0)

        # 4. Ara (düzenleme sonrası)
        search_results = self.service.search_items(workspace, "rapor", recursive=True)
        self.assertEqual(len(search_results), 2)

        # 5. İstatistik (sonuç)
        stats = self.service.collect_stats(workspace, recursive=True)
        self.assertEqual(stats.file_count, 4)

    def test_end_to_end_advanced_filter_workflow(self) -> None:
        """Gelişmiş filtreleme iş akışı: boyut ve tarih ile seçim"""
        workspace = self.root / "filter_workspace"
        workspace.mkdir(exist_ok=True)

        # Farklı boyutlarda dosyalar
        (workspace / "small_10.txt").write_text("x" * 10, encoding="utf-8")
        (workspace / "medium_100.txt").write_text("y" * 100, encoding="utf-8")
        (workspace / "large_1000.txt").write_text("z" * 1000, encoding="utf-8")

        # Boyut filtreleri ile çeşitli seçimler
        small = self.service.list_items_advanced(workspace, max_size_bytes=50)
        self.assertEqual(len(small), 1)

        medium = self.service.list_items_advanced(
            workspace, min_size_bytes=50, max_size_bytes=150
        )
        self.assertEqual(len(medium), 1)

        large = self.service.list_items_advanced(workspace, min_size_bytes=500)
        self.assertEqual(len(large), 1)

    # ============ SINIR DURUM (EDGE CASE) TESTLER ============

    def test_edge_case_empty_directory(self) -> None:
        """Boş klasörde operasyonlar"""
        empty_dir = self.root / "empty_folder"
        empty_dir.mkdir(exist_ok=True)

        # Boş klasörü listele
        items = self.service.list_items(empty_dir, recursive=False)
        self.assertEqual(len(items), 0)

        # Boş klasör istatistiği
        stats = self.service.collect_stats(empty_dir, recursive=True)
        self.assertEqual(stats.file_count, 0)
        self.assertEqual(stats.directory_count, 0)

    def test_edge_case_files_without_extension(self) -> None:
        """Uzantısız dosyaları işleme"""
        workspace = self.root / "no_ext_workspace"
        workspace.mkdir(exist_ok=True)

        (workspace / "LICENSE").write_text("license content", encoding="utf-8")
        (workspace / "README").write_text("readme content", encoding="utf-8")
        (workspace / "Makefile").write_text("make commands", encoding="utf-8")

        # Düzenle
        summary = self.service.organize_by_rules(workspace, dry_run=False)

        # Tüm dosyalar varsayılan klasöre taşınmalı
        self.assertEqual(len(summary.moved), 3)
        self.assertTrue((workspace / "Diğer" / "LICENSE").exists())

    def test_edge_case_very_deep_directory_structure(self) -> None:
        """Çok derin klasör yapısında analiz"""
        root_dir = self.root / "very_deep"
        root_dir.mkdir(exist_ok=True)
        
        current = root_dir
        for i in range(8):
            current = current / f"level_{i}"
            current.mkdir(parents=True, exist_ok=True)

        analysis = self.service.analyze_directory_depth(root_dir)
        self.assertEqual(analysis.max_depth, 8)

    def test_edge_case_special_characters_in_filenames(self) -> None:
        """Özel karakterler içeren dosya adları"""
        workspace = self.root / "special_chars_workspace"
        workspace.mkdir(exist_ok=True)

        special_names = [
            "dosya@2024.txt",
            "rapor#final.pdf",
            "veri$analiz.csv",
            "özet_şablon.docx",
        ]

        for name in special_names:
            (workspace / name).write_text("content", encoding="utf-8")

        items = self.service.list_items(workspace, recursive=False)
        self.assertEqual(len(items), 4)

        # Arama
        search = self.service.search_items(workspace, "şablon")
        self.assertEqual(len(search), 1)

    def test_edge_case_file_name_collision_handling(self) -> None:
        """Dosya adı çakışması güvenli şekilde yönetilme"""
        workspace = self.root / "collision_workspace"
        workspace.mkdir(exist_ok=True)

        # Aynı isimde birden fazla dosya
        (workspace / "rapor.pdf").write_text("content1", encoding="utf-8")

        rules_config = workspace / "rules.json"
        rules_config.write_text(
            json.dumps(
                {
                    "default_folder": "Belgeler",
                    "rules": {"Belgeler": [".pdf"]},
                }
            ),
            encoding="utf-8",
        )

        service = FileManagerService(
            LocalFileSystemGateway(), JsonRuleProvider(rules_config)
        )

        # Aynı ada sahip dosya ekle (simule)
        belgeler = workspace / "Belgeler"
        belgeler.mkdir(exist_ok=True)
        (belgeler / "rapor.pdf").write_text("existing", encoding="utf-8")

        # Yenisini taşıma (çakışma kontrolü)
        summary = service.organize_by_rules(workspace, dry_run=False)

        # İki farklı dosya var (biri rapor.pdf, diğeri rapor_1.pdf)
        belgeler_items = list(belgeler.iterdir())
        self.assertGreaterEqual(len(belgeler_items), 2)

    def test_edge_case_delete_nonexistent_file_raises_error(self) -> None:
        """Mevcut olmayan dosyayı silmeye çalışma"""
        nonexistent = self.root / "nonexistent_file.txt"

        with self.assertRaises(InvalidPathError):
            self.service.delete_item(nonexistent, recursive=False)

    def test_edge_case_rename_with_empty_string(self) -> None:
        """Boş isim ile yeniden adlandırmaya çalışma"""
        test_file = self.root / "test.txt"
        test_file.write_text("content", encoding="utf-8")

        with self.assertRaises(InvalidOperationError):
            self.service.rename_item(test_file, "")

    # ============ REGRESYON TESTLER ============

    def test_regression_turkish_characters_after_advanced_features(self) -> None:
        """Türkçe karakterlerin ileri özellikler ile uyumluluğu"""
        workspace = self.root / "turkish_regression"
        workspace.mkdir(exist_ok=True)

        # Türkçe karakterler
        (workspace / "Türkçe_Rapor.pdf").write_text("İçerik", encoding="utf-8")
        (workspace / "Öğrenci_Verileri.csv").write_text("Veriler", encoding="utf-8")
        (workspace / "Şehir_Listesi.txt").write_text("Şehirler", encoding="utf-8")

        # Gelişmiş filtreleme ile Türkçe karakteri ara
        items = self.service.list_items_advanced(
            workspace, extension_filter=".pdf"
        )
        self.assertEqual(len(items), 1)
        self.assertIn("Türkçe", items[0].path.name)

        # Arama ile Türkçe karakteri ara
        search = self.service.search_items(workspace, "Öğrenci")
        self.assertEqual(len(search), 1)

    def test_regression_previous_functionality_preserved(self) -> None:
        """Önceki fazlardaki fonksiyonların korunması"""
        workspace = self.root / "regression_workspace"
        workspace.mkdir(exist_ok=True)

        # Eski işlevler
        self.service.create_item(workspace / "test.txt", is_directory=False)
        self.assertTrue((workspace / "test.txt").exists())

        self.service.rename_item(workspace / "test.txt", "renamed.txt")
        self.assertTrue((workspace / "renamed.txt").exists())

        self.service.delete_item(workspace / "renamed.txt")
        self.assertFalse((workspace / "renamed.txt").exists())

    def test_regression_json_rule_provider_validation(self) -> None:
        """JSON kural doğrulama mekanizmasının korunması"""
        invalid_config = self.root / "invalid_config.json"

        # Geçersiz config (default_folder sayı olması gerekli)
        invalid_config.write_text(
            json.dumps({"default_folder": 999, "rules": {}}),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            JsonRuleProvider(invalid_config)

    def test_regression_file_count_accuracy(self) -> None:
        """Dosya sayım doğruluğunun korunması"""
        workspace = self.root / "count_workspace"
        workspace.mkdir(exist_ok=True)

        # 7 dosya oluştur
        for i in range(7):
            (workspace / f"file_{i}.txt").write_text(f"content_{i}", encoding="utf-8")

        stats = self.service.collect_stats(workspace, recursive=False)
        self.assertEqual(stats.file_count, 7)
        self.assertEqual(stats.total_items, 7)


if __name__ == "__main__":
    unittest.main()
