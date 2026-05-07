from pathlib import Path

from src.application.file_manager_service import FileManagerService
from src.domain.exceptions import DomainError


class ConsoleApplication:
    """Konsol tabanlı menü ve kullanıcı etkileşimi."""

    def __init__(self, service: FileManagerService) -> None:
        self._service = service

    def run(self) -> None:
        print("\nDosya ve Klasör Düzenleme Otomasyon Aracına hoş geldiniz.")
        print("Bu uygulama, proje kurallarına uygun şekilde modüler olarak geliştirilmiştir.\n")

        while True:
            self._print_menu()
            choice = input("Seçiminiz: ").strip()

            if choice == "0":
                print("Program sonlandirildi.")
                return

            try:
                self._handle_choice(choice)
            except (DomainError, OSError, ValueError) as exc:
                print(f"Hata: {exc}")

    @staticmethod
    def _print_menu() -> None:
        print("\n===== ANA MENÜ =====")
        print("1) Klasör içeriğini listele")
        print("2) Dosya/Klasör oluştur")
        print("3) Dosya/Klasör yeniden adlandır")
        print("4) Dosya/Klasör sil")
        print("5) Kurallara göre dosyaları düzenle")
        print("6) Dosya/Klasör ara")
        print("7) Klasör istatistiği al")
        print("8) Gelişmiş Filtreleme")
        print("9) Derinlemesine Analiz")
        print("0) Çıkış")

    def _handle_choice(self, choice: str) -> None:
        handlers = {
            "1": self._list_items,
            "2": self._create_item,
            "3": self._rename_item,
            "4": self._delete_item,
            "5": self._organize_items,
            "6": self._search_items,
            "7": self._show_stats,
            "8": self._advanced_filter,
            "9": self._deep_analysis,
        }

        action = handlers.get(choice)
        if not action:
            print("Geçersiz seçim yaptınız.")
            return
        action()

    def _list_items(self) -> None:
        root = Path(input("Listelemek istediğiniz klasör yolu: ").strip()).expanduser()
        recursive = input("Alt klasörler de taransın mı? (e/h): ").strip().lower() == "e"
        extension = input("Uzantı filtresi (örnek: .pdf, boş bırakabilirsiniz): ").strip() or None

        min_size_raw = input("Minimum boyut (byte, boş bırakabilirsiniz): ").strip()
        min_size = int(min_size_raw) if min_size_raw else None

        items = self._service.list_items(
            root=root,
            recursive=recursive,
            extension_filter=extension,
            min_size_bytes=min_size,
        )

        if not items:
            print("Kayıt bulunamadı.")
            return

        print("\nBulunan kayıtlar:")
        for item in items:
            kind = "Klasör" if item.is_directory else "Dosya"
            print(f"- [{kind}] {item.path} | Boyut: {item.size_bytes} byte")

    def _create_item(self) -> None:
        target = Path(input("Oluşturulacak yol: ").strip()).expanduser()
        is_directory = input("Klasör mü oluşturulsun? (e/h): ").strip().lower() == "e"

        result = self._service.create_item(target=target, is_directory=is_directory)
        print(result.message)

    def _rename_item(self) -> None:
        source = Path(input("Yeniden adlandırılacak yol: ").strip()).expanduser()
        new_name = input("Yeni ad: ").strip()

        result = self._service.rename_item(source=source, new_name=new_name)
        print(result.message)

    def _delete_item(self) -> None:
        target = Path(input("Silinecek yol: ").strip()).expanduser()
        recursive = input("Klasör ve içeriği tamamen silinsin mi? (e/h): ").strip().lower() == "e"

        result = self._service.delete_item(target=target, recursive=recursive)
        print(result.message)

    def _organize_items(self) -> None:
        root = Path(input("Düzenlenecek klasör yolu: ").strip()).expanduser()
        dry_run = input("Sadece önizleme yapılsın mı? (e/h): ").strip().lower() == "e"

        summary = self._service.organize_by_rules(root=root, dry_run=dry_run)

        print(f"\nTaşıma adedi: {len(summary.moved)}")
        for move in summary.moved:
            marker = "ÖNİZLEME" if not move.applied else "TAŞINDI"
            print(f"- [{marker}] {move.source} -> {move.destination}")

        if summary.skipped:
            print("Atlanan kayıtlar:")
            for reason in summary.skipped:
                print(f"- {reason}")

    def _search_items(self) -> None:
        root = Path(input("Arama yapılacak klasör: ").strip()).expanduser()
        keyword = input("Arama metni: ").strip()

        results = self._service.search_items(root=root, keyword=keyword, recursive=True)
        if not results:
            print("Sonuç bulunamadı.")
            return

        print("\nArama sonuçları:")
        for item in results:
            print(f"- {item.path}")

    def _show_stats(self) -> None:
        root = Path(input("İstatistik alınacak klasör yolu: ").strip()).expanduser()
        stats = self._service.collect_stats(root=root, recursive=True)

        print("\nKlasör istatistiği:")
        print(f"- Toplam kayıt: {stats.total_items}")
        print(f"- Dosya sayısı: {stats.file_count}")
        print(f"- Klasör sayısı: {stats.directory_count}")
        print(f"- Toplam boyut: {stats.total_size_bytes} byte")

    def _advanced_filter(self) -> None:
        from datetime import datetime

        root = Path(input("Filtreleme yapılacak klasör: ").strip()).expanduser()
        recursive = input("Alt klasörler de taransın mı? (e/h): ").strip().lower() == "e"
        extension = input("Uzantı filtresi (örnek: .pdf, boş bırakabilirsiniz): ").strip() or None

        min_size_raw = input("Minimum boyut (byte, boş bırakabilirsiniz): ").strip()
        min_size = int(min_size_raw) if min_size_raw else None

        max_size_raw = input("Maksimum boyut (byte, boş bırakabilirsiniz): ").strip()
        max_size = int(max_size_raw) if max_size_raw else None

        after_raw = input("Değişim tarihi (YYYY-MM-DD'den sonra, boş bırakabilirsiniz): ").strip()
        after_date = datetime.fromisoformat(after_raw) if after_raw else None

        before_raw = input("Değişim tarihi (YYYY-MM-DD'den önce, boş bırakabilirsiniz): ").strip()
        before_date = datetime.fromisoformat(before_raw) if before_raw else None

        items = self._service.list_items_advanced(
            root=root,
            recursive=recursive,
            extension_filter=extension,
            min_size_bytes=min_size,
            max_size_bytes=max_size,
            modified_after=after_date,
            modified_before=before_date,
        )

        if not items:
            print("Sonuç bulunamadı.")
            return

        print("\nGelişmiş Filtreleme Sonuçları:")
        for item in items:
            kind = "Klasör" if item.is_directory else "Dosya"
            print(f"- [{kind}] {item.path} | Boyut: {item.size_bytes} byte")

    def _deep_analysis(self) -> None:
        root = Path(input("Analiz yapılacak klasör yolu: ").strip()).expanduser()

        # Dosya türü analizi
        file_type_dist = self._service.analyze_file_types(root=root, recursive=True)
        print("\nDosya Türü Dağılımı:")
        for ext, count in sorted(file_type_dist.distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"- {ext}: {count} dosya")

        # Klasör derinlik analizi
        depth_analysis = self._service.analyze_directory_depth(root=root)
        print(f"\nKlasör Derinliği:")
        print(f"- Maksimum derinlik: {depth_analysis.max_depth}")
        if depth_analysis.depth_distribution:
            print("- Derinliğe göre klasör sayısı:")
            for depth in sorted(depth_analysis.depth_distribution.keys()):
                count = depth_analysis.depth_distribution[depth]
                print(f"  - Derinlik {depth}: {count} klasör")
