# Felsefe Öğretim Kaynakları

MEB Türkiye Yüzyılı Maarif Modeli Felsefe Dersi Öğretim Programı (2024 onaylı) için açık kaynak öğretim kaynakları ve pratik ders materyalleri.

## İçerik

- **Müfredat**: 10. ve 11. sınıf felsefe programı (yapılandırılmış Markdown ünite dosyaları, 15 ünite)
- **Çalışma kâğıtları**: Her üniteye karşılık gelen öğrenci çalışma kâğıdı ve öğretmen cevap anahtarı (15 kâğıt)
- **Ek soru setleri**: 10. sınıf için diyalog, 11. sınıf için forum kurgulu özgün ölçme görevleri
- **Ortak materyaller**: Öz/akran/grup değerlendirme formları ve metin inceleme formu
- **Etkinlikler ve performans görevleri**: Ünite dosyalarının içinde, süreye bağlı öğretim akışı olarak
- **Ölçme**: Her ünitede 100 puanlık ölçme yapısı, dereceli puanlama anahtarı ve farklılaştırma önerileri
- **Denetim kayıtları**: Müfredat denetimi, pedagojik denetim, ders kitabı ve ölçme hizalama raporları

## Klasör Yapısı

```
├── mufredat/
│   ├── template.md                              # Ortak ünite şablonu
│   ├── ortak-materyaller/                       # Üniteler arası ortak formlar
│   │   ├── metin-inceleme-formu.md              # Performans görevi metin inceleme formu
│   │   └── degerlendirme-formlari.md            # Öz ve akran değerlendirme şablonları
│   ├── 10-sinif/
│   │   ├── 01-felsefenin-dogasi.md              # 9 ünite materyali
│   │   ├── …
│   │   ├── 09-bilim-felsefesi.md
│   │   ├── calisma-kagitlari/                   # 9 çalışma kâğıdı + cevap anahtarı
│   │   └── ek-soru-setleri-diyalog.md          # 9 ünite için ek ölçme görevleri
│   └── 11-sinif/
│       ├── 01-cevre-sorunlari-felsefe.md        # 6 ünite materyali
│       ├── …
│       ├── 06-hukuk-ve-felsefe.md
│       ├── calisma-kagitlari/                   # 6 çalışma kâğıdı + cevap anahtarı
│       └── ek-soru-setleri-forum.md             # 6 ünite için ek ölçme görevleri
├── docs/                                        # Denetim ve durum kayıtları (Markdown)
│   ├── index.html                               # Statik sitenin ana sayfası (GitHub Pages)
│   └── site/                                    # Statik site sayfaları
│       ├── 10-sinif/  11-sinif/                # Ünite ve çalışma kâğıdı sayfaları
│       ├── ortak-materyaller/                   # Ortak form sayfaları
│       └── raporlar/                            # Denetim raporlarının sayfaları
├── tools/
│   └── denetle_yapisal_kalite.py                # Tekrarlanabilir yapısal denetim
├── .github/workflows/
│   └── yapisal-kalite-denetimi.yml              # Ana dal kalite kontrolü
└── README.md
```

## 10. Sınıf Üniteleri

MEB onaylı programda 10. sınıf toplam 72 ders saati ve 9 üniteden oluşur:

| Ünite | Başlık | Saat | Oran | Durum |
|-------|--------|------|------|-------|
| 1 | Felsefenin Doğası | 10 | %15 | Tamamlandı (resmî program doğrulamalı) |
| 2 | Felsefe, Mantık ve Argümantasyon | 8 | %11 | Tamamlandı (resmî program doğrulamalı) |
| 3 | Varlık Felsefesi | 8 | %11 | Tamamlandı (resmî program doğrulamalı) |
| 4 | Bilgi Felsefesi | 8 | %11 | Tamamlandı (resmî program doğrulamalı) |
| 5 | Ahlak Felsefesi | 8 | %11 | Tamamlandı (resmî program doğrulamalı) |
| 6 | Estetik ve Sanat Felsefesi | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |
| 7 | Siyaset Felsefesi | 8 | %11 | Tamamlandı (resmî program doğrulamalı) |
| 8 | Din Felsefesi | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |
| 9 | Bilim Felsefesi | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |

## 11. Sınıf Üniteleri

MEB onaylı programda 11. sınıf altı üniteden oluşur. Altı ünitenin tamamı için resmî programla hizalı materyal ve çalışma kâğıdı hazırlanmıştır.

| Ünite | Başlık | Saat | Durum |
|-------:|---|---:|---|
| 1 | Çevre Sorunları ve Felsefe | 12 | Tamamlandı (resmî program doğrulamalı) |
| 2 | Teknoloji ve Hayat | 12 | Tamamlandı (resmî program doğrulamalı) |
| 3 | Akıl ve İnanç | 10 | Tamamlandı (resmî program doğrulamalı) |
| 4 | Edebiyat ve Felsefe | 12 | Tamamlandı (resmî program doğrulamalı) |
| 5 | Hayatın Anlamı | 12 | Tamamlandı (resmî program doğrulamalı) |
| 6 | Hukuk ve Felsefe | 10 | Tamamlandı (resmî program doğrulamalı) |

11. sınıf ünite denetim kayıtları için [`docs/denetim-raporu-11-sinif.md`](docs/denetim-raporu-11-sinif.md) dosyasına bakınız.

## Web Sitesi

Depodaki tüm materyaller okunabilir statik HTML sayfaları olarak `docs/` klasöründe üretilmiştir ve GitHub Pages üzerinden yayımlanmaktadır:

**https://aytigin-netizen.github.io/felsefe-ogretim-kaynaklari/**

Ana sayfa `docs/index.html`; ünite ve çalışma kâğıdı sayfaları `docs/site/10-sinif/`, `docs/site/11-sinif/`, `docs/site/ortak-materyaller/` ve `docs/site/raporlar/` klasörlerindedir.

Yayım `main` dalının `/docs` klasöründen yapılır; bir `main` birleştirmesi siteyi otomatik olarak günceller. Markdown kaynaklar güncellendiğinde ilgili HTML sayfalarının da yeniden üretilmesi gerekir: sayfa köklerindeki `← Ana Sayfa` bağlantısı site kökünden iki seviye aşağıda olduğu için `../../index.html` olmalıdır. Yapısal denetim, sitedeki yerel ve depo içi GitHub bağlantılarını her değişiklikte doğrular.

## Yapısal Kalite Denetimi

Depodaki her değişiklikte ünite ve çalışma kâğıdı sayısı, ders saati ve öğrenme çıktısı üst verileri, 100 puanlık ölçme yapısı ile yerel Markdown bağlantıları denetlenir. Kontrolü yerelde çalıştırmak için aşağıdaki komut kullanılır:

```bash
python tools/denetle_yapisal_kalite.py
```

Ana dala gönderilen değişiklikler ve ana dala açılan birleştirme istekleri için aynı kontrol otomatik olarak çalışır. Bu denetim yalnızca yapısal tutarlılığı doğrular; program uyumu, felsefi doğruluk, telif, kaynak güncelliği ve sınıf içi uygulanabilirlik ayrıca pedagojik inceleme gerektirir.

## Katkıda Bulunma

Yeni ünite eklerken `mufredat/template.md` dosyasındaki ortak şablonu kullanın. Kazanım kodları (FEL.10.x.x veya FEL.11.x.x) ve süreç bileşenleri [MEB Felsefe Dersi Öğretim Programı](https://tymm.meb.gov.tr/ogretim-programlari/ders/felsefe-dersi) ile birebir uyumlu olmalıdır.
