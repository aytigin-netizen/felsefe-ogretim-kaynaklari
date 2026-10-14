# Felsefe Öğretim Kaynakları

MEB Türkiye Yüzyılı Maarif Modeli Felsefe Dersi Öğretim Programı (2026 onaylı) için açık kaynak öğretim kaynakları ve pratik ders materyalleri.

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
│   ├── program-2026-ozet.json                   # Resmî 2026 programının ünite/çıktı/süre kaydı
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
│   ├── denetle_yapisal_kalite.py                # Tekrarlanabilir yapısal denetim
│   ├── denetle_program_uyumu.py                 # Resmî programla uyum denetimi
│   ├── program-ozeti-uret.py                    # Program kaydının PDF'den üretimi
│   ├── program-2026-bilinen-ayrismalar.json     # Açık kalan program sapmaları
│   └── uret_site.py                             # Markdown materyallerinden site üretimi
├── .github/workflows/
│   └── yapisal-kalite-denetimi.yml              # Ana dal kalite kontrolü
└── README.md
```

## 10. Sınıf Üniteleri

Resmî 2026 programında 10. sınıf toplam 72 ders saati ve 9 üniteden oluşur (68 saat ünitelerde, 4 saat okul temelli planlamada):

| Ünite | Başlık | Saat | Oran | Durum |
|-------|--------|------|------|-------|
| 1 | Felsefenin Doğası | 10 | %15 | Tamamlandı (resmî program doğrulamalı) |
| 2 | Felsefe, Mantık ve Argümantasyon | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |
| 3 | Varlık Felsefesi | 10 | %15 | Tamamlandı (resmî program doğrulamalı) |
| 4 | Bilgi Felsefesi | 8 | %11 | Tamamlandı (resmî program doğrulamalı) |
| 5 | Ahlak Felsefesi | 8 | %11 | Tamamlandı (resmî program doğrulamalı) |
| 6 | Estetik ve Sanat Felsefesi | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |
| 7 | Siyaset Felsefesi | 8 | %11 | Tamamlandı (resmî program doğrulamalı) |
| 8 | Din Felsefesi | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |
| 9 | Bilim Felsefesi | 6 | %8 | Tamamlandı (resmî program doğrulamalı) |
| — | Okul Temelli Planlama | 4 | %5 | [`mufredat/okul-temelli-planlama.md`](mufredat/okul-temelli-planlama.md) |

## 11. Sınıf Üniteleri

Resmî 2026 programında 11. sınıf altı üniteden oluşur (68 saat ünitelerde, 4 saat okul temelli planlamada). Altı ünitenin tamamı için programla hizalı materyal ve çalışma kâğıdı hazırlanmıştır.

| Ünite | Başlık | Saat | Durum |
|-------:|---|---:|---|
| 1 | Çevre Sorunları ve Felsefe | 12 | Tamamlandı (resmî program doğrulamalı) |
| 2 | Teknoloji ve Hayat | 12 | Tamamlandı (resmî program doğrulamalı) |
| 3 | Akıl ve İnanç | 10 | Tamamlandı (resmî program doğrulamalı) |
| 4 | Edebiyat ve Felsefe | 12 | Tamamlandı (resmî program doğrulamalı) |
| 5 | Hayatın Anlamı | 12 | Tamamlandı (resmî program doğrulamalı) |
| 6 | Hukuk ve Felsefe | 10 | Tamamlandı (resmî program doğrulamalı) |
| — | Okul Temelli Planlama | 4 | [`mufredat/okul-temelli-planlama.md`](mufredat/okul-temelli-planlama.md) |

11. sınıf ünite denetim kayıtları için [`docs/denetim-raporu-11-sinif.md`](docs/denetim-raporu-11-sinif.md) dosyasına bakınız.

## Web Sitesi

Depodaki tüm materyaller okunabilir statik HTML sayfaları olarak `docs/` klasöründe üretilmiştir ve GitHub Pages üzerinden yayımlanmaktadır:

**https://aytigin-netizen.github.io/felsefe-ogretim-kaynaklari/**

Ana sayfa `docs/index.html`; ünite ve çalışma kâğıdı sayfaları `docs/site/10-sinif/`, `docs/site/11-sinif/`, `docs/site/ortak-materyaller/` ve `docs/site/raporlar/` klasörlerindedir.

Yayım `main` dalının `/docs` klasöründen yapılır; bir `main` birleştirmesi siteyi otomatik olarak günceller. Sayfalar elle yazılmaz: `tools/uret_site.py`, `mufredat/` altındaki ünite, çalışma kâğıdı, ek soru seti ve ortak materyal dosyaları ile `docs/` altındaki raporları okuyup 43 sayfayı üretir.

```bash
python tools/uret_site.py          # sayfaları yeniden üretir
python tools/uret_site.py --check  # depodaki sayfalar güncel mi diye bakar
```

Markdown kaynaklarını değiştirdikten sonra `--check` kırmızı verir; `python tools/uret_site.py` ile yeniden üretip aynı değişiklikle gönderin. CI, her değişiklikte `--check`'i çalıştırdığı için kaynak ile site arasındaki kayma birleşik isteği durdurur.

## Resmî Program Uyumu

Materyallerin dayandığı tek resmî kaynak, MEB'in yayımladığı **2026 Felsefe Dersi Öğretim Programı**'dır. Programın ünite, ders saati, yüzde oranı ve öğrenme çıktı bilgisi `mufredat/program-2026-ozet.json` kaydında tutulur. Bu kayıt elle yazılmamıştır: `tools/program-ozeti-uret.py` aracı program PDF'sini okuyup üretir ve kaydın `sha256` özetiyle birlikte kaynağını tutar.

```bash
python tools/program-ozeti-uret.py            # kaydı program PDF'sinden yeniden üretir (pdftotext gerekir)
python tools/denetle_program_uyumu.py         # materyallerin programla uyumunu denetler
python tools/denetle_program_uyumu.py --kaydet  # denetimin o anki bulgularını sapma listesine yazar
```

Denetim şunları karşılaştırır: her ünite dosyasının ders saati, yüzde oranı ve öğrenme çıktısı sayısı; materyallerde geçen her `FEL.x.x.x` kodunun programda tanımlı olması; program atıflarının kayıttaki yılı ve güncel bağlantıyı göstermesi.

Materyaller 2026 programına uyarlanana kadar açık kalan sapmalar `tools/program-2026-bilinen-ayrismalar.json` dosyasında açıkça listelenir. Denetim her koşuda bu listeyi de yazar: liste dışına çıkan yeni bir sapma CI'ı düşürür, listedeki madde kapatıldığında listeden silinir ve denetim "artık geçerli değil" uyarısı verir.

## Yapısal Kalite Denetimi

Depodaki her değişiklikte ünite ve çalışma kâğıdı sayısı, ders saati ve öğrenme çıktısı üst verileri, 100 puanlık ölçme yapısı ile yerel Markdown bağlantıları denetlenir. Kontrolü yerelde çalıştırmak için aşağıdaki komut kullanılır:

```bash
python tools/denetle_yapisal_kalite.py
```

Ana dala gönderilen değişiklikler ve ana dala açılan birleştirme istekleri için yapısal denetim, resmî program uyum denetimi ve `uret_site.py --check` otomatik olarak çalışır. Bu denetim yalnızca yapısal tutarlılığı doğrular; program uyumu, felsefi doğruluk, telif, kaynak güncelliği ve sınıf içi uygulanabilirlik ayrıca pedagojik inceleme gerektirir.

## Katkıda Bulunma

Yeni ünite eklerken `mufredat/template.md` dosyasındaki ortak şablonu kullanın. Kazanım kodları (FEL.10.x.x veya FEL.11.x.x) ve süreç bileşenleri [MEB Felsefe Dersi Öğretim Programı](https://tymm.meb.gov.tr/ogretim-programlari/ders/felsefe-dersi) ile birebir uyumlu olmalıdır.
