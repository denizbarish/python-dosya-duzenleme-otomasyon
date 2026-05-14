# Dosya ve Klasör Düzenleme Otomasyon Aracı

Bu proje, Doğuş Üniversitesi Bilgisayar Programcılığı 2. sınıf Python final projesi gereksinimleri dikkate alınarak geliştirilmiş modüler bir konsol uygulamasıdır.

## Proje Amacı

Kullanıcının belirlediği dizinlerde dosya ve klasörleri yönetmesini, aramasını, silmesini ve uzantı kurallarına göre otomatik olarak düzenlemesini sağlamak.

## Temel Özellikler

- Klasör içeriğini listeleme (opsiyonel filtreleme ile)
- Dosya/klasör oluşturma
- Dosya/klasör yeniden adlandırma
- Dosya/klasör silme (güvenli recursive kontrol ile)
- Uzantı bazlı otomatik dosya düzenleme
- Arama ve temel istatistik alma

## İleri Özellikler (Faz 3)

- **Gelişmiş Filtreleme**: Boyut aralığı, tarih aralığı, uzantı filtresi ile detaylı seçim
- **Dosya Türü Analizi**: Klasördeki dosyaların türlerine göre dağılım
- **Klasör Derinlik Analizi**: Klasör yapısının maksimum derinliği ve dağılımı
- **Geliştirilmiş UI**: Yeni menü seçenekleriyle (8 ve 9) daha işlevsel arayüz

## Mimari Yapı

Proje SOLID prensiplerine uygun olacak şekilde 4 katmanda tasarlanmıştır:

- `src/domain`: Entity modelleri, protokoller, özel hatalar
- `src/application`: İş kuralları ve uygulama servisleri
- `src/infrastructure`: Dosya sistemi ve JSON kural sağlayıcı
- `src/presentation`: Konsol arayüzü

Bu ayrım sayesinde bağımlılıklar somut sınıflara değil, soyut protokollere bağlanır (Dependency Inversion).

## Çalıştırma

1. Proje klasörüne girin.
2. Aşağıdaki komutu çalıştırın:

```bash
python -m src.main
```

## Testler

```bash
python -m unittest discover -s tests -v
```

## Kural Dosyası

Uzantı-kategori eşlemeleri `config/organizasyon_kurallari.json` dosyasından okunur.

Örnek:

- `.pdf` -> `Belgeler`
- `.png` -> `Görseller`
- tanımsız uzantılar -> `Diğer`

## Proje Kriterleri ile Uyum

- Python dili ile geliştirme: Sağlandı
- Modüler kod yapısı: Sağlandı
- OOP ve sınıf tabanlı tasarım: Sağlandı
- CRUD işlevleri: Sağlandı
- Hata kontrolleri ve try-except yaklaşımı: Sağlandı
- Test senaryoları: Sağlandı
- README ve düzenli dosya yapısı: Sağlandı

## Gelişim ve Raporlama

- Faz planı: [docs/gelisim_ve_raporlama_plani.md](docs/gelisim_ve_raporlama_plani.md)
- Durum raporu şablonu: [docs/durum_raporu_sablonu.md](docs/durum_raporu_sablonu.md)
- Düzenli rapor kayıtları: [docs/durum_raporlari.md](docs/durum_raporlari.md)
- Doldurulmuş Rapor-1: [docs/BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_1.md](docs/BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_1.md)
- Doldurulmuş Rapor-2: [docs/BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_2.md](docs/BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_2.md)
- Doldurulmuş Rapor-3: [docs/BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_3.md](docs/BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_3.md)
- Doldurulmuş Rapor-4: [docs/BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_4.md](docs/BLP_sube_no_Grup_17_dosya_ve_klasor_duzenleme_otomasyon_araci_rapor_4.md)
