# Felsefe Öğretim Kaynakları

MEB Türkiye Yüzyılı Maarif Modeli Felsefe Dersi Öğretim Programı (2024 onaylı) için açık kaynak öğretim kaynakları ve pratik ders materyalleri.

## İçerik

- **Müfredat**: 10. ve 11. sınıf felsefe programı (yapılandırılmış Markdown ünite dosyaları)
- **Ders Planları**: Hazır ders planı şablonları
- **Etkinlikler**: Tartışma soruları, sınıf etkinlikleri, performans görevleri
- **Sunumlar**: pptxgenjs ile üretilmiş dinamik sunumlar
- **Değerlendirme**: Rubrikler, dereceli puanlama anahtarları, kontrol listeleri

## Klasör Yapısı

```
├── mufredat/
│   ├── template.md                              # Ortak ünite şablonu
│   ├── ortak-materyaller/                       # Üniteler arası ortak formlar
│   │   ├── metin-inceleme-formu.md              # Performans görevi metin inceleme formu
│   │   └── degerlendirme-formlari.md            # Öz ve akran değerlendirme şablonları
│   ├── 10-sinif/
│   │   ├── 01-felsefenin-dogasi.md
│   │   ├── 02-felsefe-mantik-argumantasyon.md
│   │   ├── 03-varlik-felsefesi.md
│   │   ├── 04-bilgi-felsefesi.md
│   │   ├── 05-ahlak-felsefesi.md
│   │   ├── 06-estetik-sanat-felsefesi.md
│   │   ├── 07-siyaset-felsefesi.md
│   │   ├── 08-din-felsefesi.md
│   │   ├── 09-bilim-felsefesi.md
│   │   └── calisma-kagitlari/                   # Birim bazlı çalışma kâğıtları
│   └── 11-sinif/
├── materyaller/
│   ├── tartisma-sorulari/
│   ├── ders-planlari/
│   └── etkinlikler/
├── web/
│   └── (Web sitesi dosyaları)
├── docs/
│   └── denetim-raporu.md                        # Resmî program uyum denetim raporu
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
| 6 | Estetik ve Sanat Felsefesi | 6 | %8 | Şablon düzeyinde |
| 7 | Siyaset Felsefesi | 8 | %11 | Şablon düzeyinde |
| 8 | Din Felsefesi | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |
| 9 | Bilim Felsefesi | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |

## Katkıda Bulunma

Yeni ünite eklerken `mufredat/template.md` dosyasındaki ortak şablonu kullanın. Kazanım kodları (FEL.10.x.x) ve süreç bileşenleri [MEB Felsefe Dersi Öğretim Programı](https://tymm.meb.gov.tr/ogretim-programlari/ders/felsefe-dersi) ile birebir uyumlu olmalıdır.
