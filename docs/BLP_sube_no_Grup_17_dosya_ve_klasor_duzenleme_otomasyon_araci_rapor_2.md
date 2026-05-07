# RAPOR 2 - Çekirdek Fonksiyonlar ve Hata Yönetimi

## Teslim Bilgileri
- Ders: Python Programlama
- Dönem: 2025-2026 Bahar
- Grup No: 17
- Proje Adı: Dosya ve Klasör Düzenleme Otomasyon Aracı
- Rapor Türü: 2. Rapor (Çekirdek Fonksiyonlar)
- Resmi Teslim Tarihi: 30.04.2026
- Teslim Platformu: OneDrive / Proje Dosyaları
- Teslim Adı Kuralı: BLP_sube_no_Grup_grup_no_proje_adi
- Bu dosya için önerilen teslim adı: BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_2

Not: sube_no bilgisi, öğrenci/grup bilgisine göre güncellenmelidir.

## 1) Bu Raporun Kapsamı
Bu rapor; projede çekirdek fonksiyonların tamamlandığını, CRUD işlemlerinin çalıştığını, hata yönetiminin uygulandığını ve testlerle doğrulama yapıldığını göstermektedir.

## 2) Tamamlanan Çekirdek Fonksiyonlar
- Dosya/klasör oluşturma
- Dosya/klasör listeleme
- Dosya/klasör yeniden adlandırma
- Dosya/klasör silme
- Uzantıya göre otomatik klasörleme
- Anahtar kelime ile arama
- Klasör istatistikleri alma

## 3) Veri Yapısı ve Kural Yönetimi
Bu aşamada proje, JSON tabanlı yapılandırma ile çalışmaktadır. Uzantı-kategori eşlemeleri `config/organizasyon_kurallari.json` dosyasından okunmakta ve farklı dosya türleri uygun klasörlere yönlendirilmektedir.

Kullanılan yaklaşım:
- JSON ile esnek kural yönetimi
- Varsayılan klasör mantığı
- Çakışma durumunda benzersiz ad üretimi

## 4) CRUD İşlemleri
Create:
- Dosya ve klasör oluşturma desteklenmektedir.

Read:
- Listeleme, arama ve istatistik alma işlemleri desteklenmektedir.

Update:
- Dosya ve klasör yeniden adlandırma desteklenmektedir.

Delete:
- Dosya ve klasör silme desteklenmektedir.
- Klasör silme işlemi için recursive onayı zorunlu tutulmuştur.

## 5) Hata Yönetimi
Projede hata yönetimi için özel istisnalar ve kontrollü mesajlar kullanılmıştır.

Örnekler:
- Boş arama ifadesi reddedilmektedir.
- Boş yeni isim reddedilmektedir.
- Mevcut olmayan yol için hata döndürülmektedir.
- Recursive olmadan klasör silme engellenmektedir.

Türkçe karakter uyumluluğu da korunmuştur.

## 6) Uygulama Mimarisi
Proje katmanları:
- Domain: varlıklar, protokoller, özel hatalar
- Application: iş kuralları
- Infrastructure: yerel dosya sistemi ve JSON kural sağlayıcı
- Presentation: konsol menüsü

Bu yapı sayesinde kod modüler, test edilebilir ve sürdürülebilir kalmaktadır.

## 7) Testler ve Doğrulama
- Birim testler başarıyla çalıştırılmıştır.
- Türkçe karakterli yol ve dosya adı senaryoları doğrulanmıştır.
- Kural bazlı taşıma ve CRUD akışları test edilmiştir.

Komut:
- /Users/deniz/Projects/python-dosya-duzenleme-otomasyon/.venv/bin/python -m unittest discover -s tests -v

Sonuç:
- 4 / 4 test başarılı

## 8) Riskler ve Alınan Önlemler
Risk 1: Dosya adı çakışması
- Önlem: Benzersiz hedef adı üretme

Risk 2: Yanlış kullanıcı girişi
- Önlem: Validasyon ve açıklayıcı hata mesajları

Risk 3: Türkçe karakter sorunları
- Önlem: UTF-8 stdio ve UTF-8/UTF-8-SIG okuma kullanımı

## 9) Sonraki Faz Planı (07.05.2026)
- İleri özellikler ve UI/UX iyileştirmeleri
- Filtreleme ve analiz senaryoları
- Modüler yapı ve rapor sunumu için ek kanıtlar

## 10) Kanıtlar
- Kaynak kod: src/
- Testler: tests/test_file_manager_service.py
- Kurallar: config/organizasyon_kurallari.json
- Dokümantasyon: README.md, docs/

## 11) Sonuç
Rapor 2 kapsamında beklenen çekirdek fonksiyonlar ve hata yönetimi tamamlanmış, testlerle doğrulanmış ve teslim edilebilir hale getirilmiştir.
