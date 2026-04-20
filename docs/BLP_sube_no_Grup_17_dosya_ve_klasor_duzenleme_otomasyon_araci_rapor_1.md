# RAPOR 1 - Problem Tanımı ve Sistem Tasarımı

## Teslim Bilgileri
- Ders: Python Programlama
- Dönem: 2025-2026 Bahar
- Grup No: 17
- Proje Adı: Dosya ve Klasör Düzenleme Otomasyon Aracı
- Rapor Türü: 1. Rapor (Problem Tanımı ve Sistem Tasarımı)
- Resmi Teslim Tarihi: 20.04.2026
- Teslim Platformu: OneDrive / Proje Dosyaları
- Teslim Adı Kuralı: BLP_sube_no_Grup_grup_no_proje_adi
- Bu dosya için önerilen teslim adı: BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci

Not: sube_no bilgisi, öğrenci/grup bilgisine göre güncellenmelidir.

## 1) Problem Tanımı
Kullanıcıların çalışma dizinlerinde bulunan dosya ve klasörlerin manuel olarak düzenlenmesi zaman kaybına ve hata riskine neden olmaktadır. Özellikle farklı uzantı türlerinin aynı klasörde birikmesi, arama süreçlerini uzatmakta ve bakım maliyetini artırmaktadır.

Bu çalışma kapsamında, dosya ve klasör yönetim işlemlerini tek bir konsol uygulamasında birleştiren, modüler bir otomasyon aracı geliştirilmiştir. Araç, temel dosya yönetimi (oluşturma, listeleme, güncelleme/yeniden adlandırma, silme), arama, istatistik alma ve uzantı bazlı otomatik düzenleme işlevlerini sağlamaktadır.

## 2) Proje Amacı
- Dosya/klasör yönetimini standartlaştırmak
- CRUD işlemlerini güvenli ve izlenebilir şekilde sağlamak
- Kural tabanlı otomatik düzenleme ile kullanıcı verimliliğini artırmak
- Modüler mimariyle test edilebilir ve sürdürülebilir bir yapı kurmak

## 3) Kapsam ve Sınırlar
Kapsam:
- Konsol arayüzü üzerinden dosya/klasör işlemleri
- JSON tabanlı uzantı-kategori eşleme
- Hata yönetimi ve kullanıcıya anlamlı geri bildirim
- Birim testler ile doğrulama

Kapsam dışı:
- Çok kullanıcılı yetkilendirme
- Bulut depolama entegrasyonu
- Web arayüzü

## 4) Sistem Tasarımı
Proje 4 katmanlı mimari ile tasarlanmıştır:

1. Domain Katmanı
- Varlıklar ve istisnalar bu katmanda tanımlanmıştır.
- Dosya sistemi ve kural sağlayıcı soyutlamaları (protocol) içerir.

2. Application Katmanı
- İş kurallarını içeren servis katmanıdır.
- Listeleme, arama, oluşturma, yeniden adlandırma, silme, düzenleme ve istatistik akışları burada yürütülür.

3. Infrastructure Katmanı
- Yerel dosya sistemi erişimi ve JSON kural okuma bu katmanda somutlanır.

4. Presentation Katmanı
- Kullanıcı menüsü ve giriş/çıkış etkileşimleri bu katmanda yönetilir.

Bu tasarım ile bağımlılıklar soyut katmanlara bağlanmış, değiştirme maliyeti azaltılmıştır.

## 5) Belirlenen Özellikler (Rapor-1 Çıktısı)
- Klasör içeriğini listeleme
- Dosya/klasör oluşturma
- Dosya/klasör yeniden adlandırma
- Dosya/klasör silme (güvenli recursive kontrol)
- Uzantı bazlı otomatik düzenleme
- Anahtar kelime ile arama
- Klasör istatistikleri
- UTF-8/Türkçe karakter uyumluluğu

## 6) Kullanılan Veri Yapıları ve Konfigürasyon Yaklaşımı
- Kural yönetimi için JSON dosyası kullanılmıştır.
- Uzantı-kategori eşlemeleri yapılandırılabilir biçimde tutulmuştur.
- Tanımsız uzantılar için varsayılan klasör stratejisi uygulanmıştır.

## 7) Riskler ve Önlemler
Risk 1: Yanlış giriş yolundan kaynaklı işlem hataları
- Önlem: Yol doğrulama ve açıklayıcı hata mesajları

Risk 2: Dosya adı çakışmaları
- Önlem: Hedefte benzersiz ad üretme (_1, _2, ...)

Risk 3: Türkçe karakter kaynaklı okuma/yazma sorunları
- Önlem: UTF-8 stdio yapılandırması ve UTF-8/UTF-8-SIG güvenli dosya okuma

## 8) Ölçümler ve Durum
- Faz: Faz 1
- Durum: Yeşil
- Test Komutu: /Users/deniz/Projects/python-dosya-duzenleme-otomasyon/.venv/bin/python -m unittest discover -s tests -v
- Test Sonucu: 4 / 4 (OK)
- Açık Kritik Hata: 0

## 9) Sonraki Faz Planı (Faz 2 - 30.04.2026)
- CRUD ve hata yönetimi kanıtlarının rapor metnine detaylı işlenmesi
- Kural dosyası doğrulama senaryolarının genişletilmesi
- Test kapsamının çekirdek fonksiyonlar için artırılması

## 10) Kanıtlar
- Mimari ve proje özeti: README.md
- Çekirdek servis: src/application/file_manager_service.py
- Konsol arayüzü: src/presentation/console_app.py
- Kural sağlayıcı: src/infrastructure/json_rule_provider.py
- Dosya sistemi katmanı: src/infrastructure/local_file_system.py
- Testler: tests/test_file_manager_service.py

## 11) Teslim Öncesi Kontrol
- Rapor içeriği faz hedefiyle uyumludur.
- Akademik Türkçe dili kullanılmıştır.
- Teslim adı kuralı belirtilmiştir.
- Test çıktısı rapora eklenmiştir.
- Sonraki faz planı belirtilmiştir.
