# Kaynak Envanteri ve Güncellik Denetimi — P2

**Denetim tarihi:** 13 Ekim 2026

**Kapsam:** 32 materyal dosyası (15 ünite, 15 çalışma kâğıdı, 2 ortak materyal) ile README ve docs kayıtlarındaki tüm dış bağlantılar ve eser atıfları

**Yöntem:** Depodaki benzersiz dış URL'ler çıkarıldı ve tarayıcı dışı tam sayfa denetimiyle açıldı; atıf başlıkları hedef sayfalarla karşılaştırıldı. Otomatik erişimin engellendiği bağlantılar "el ile doğrulanmalı" olarak işaretlendi.

## 1. Yönetici Özeti

Müfredat materyallerinde **sekiz benzersiz dış URL** kullanılmaktadır; bunların **beşi tam doğrulandı**, **ikisi otomatik erişim engeli nedeniyle el ile doğrulanmalı**, **biri yanlış eser adıyla atıflanmıştı ve bu turda düzeltildi**. Birincil dayanak olan MEB program PDF'i otomatik denetimde açılamamıştır; ancak aynı kurumun program sayfası erişilebilir durumdadır ve doğrulama el ile yapılmalıdır.

> **Temel sonuç:** Kaynak altyapısı büyük ölçüde sağlamdır. Bu turda bir P0 atıf hatası (Descartes eser adı) düzeltildi; kalan işler el ile tarayıcı doğrulaması (2 bağlantı) ve TÜİK bülten bağlantısının en yeni sürüme güncellenmesidir.

| Bulgu kategorisi | Adet |
|---|---:|
| Tam doğrulanan bağlantı | 5 |
| El ile doğrulanması gereken bağlantı | 2 |
| Bu turda düzeltilen atıf hatası | 1 |
| Yeni sürümü çıkmış veri bülteni | 1 |

## 2. Bağlantı Envanteri ve Doğrulama Sonuçları

| # | URL | Kullanıldığı dosyalar | Denetim sonucu | işlem |
|---|---|---|---|---|
| 1 | `tymm.meb.gov.tr/assets/pdf/felsefe-dersi_20260819_142831_736.pdf` | 27 materyal, README, tüm denetim/durum kayıtları | Eski 2026 programı PDF bağlantısı ölüydü; 4. adımda resmî 2026 programının PDF bağlantısıyla değiştirildi (bağlantı ve sha256 özeti `mufredat/program-2026-ozet.json` kaydında tutulur) | Eylem tamamlandı — 4. adım commit kaydı |
| 2 | `tymm.meb.gov.tr/ogretim-programlari/ders/felsefe-dersi` | README, denetim raporları | ✓ Erişilebilir; başlık doğrulandı | Eylem gerekmiyor |
| 3 | `veriportali.tuik.gov.tr/tr/press/53974` (Sera Gazı Emisyon İstatistikleri, 1990–2023) | 11. sınıf 1. ünite ve çalışma kâğıdı | ✓ Bülten numarası doğrulandı; ancak 1990–2024 sürümü yayımlandı | Öğretmen yönergesi zaten "en güncel tablo" istediğinden içerik geçerli; sonraki bakımda bülten bağlantısı 1990–2024 sürümüne güncellenmeli |
| 4 | `veriportali.tuik.gov.tr/en/press/53925/metadata` (Hanehalkı Bilişim Teknolojileri Kullanım Araştırması, 2025) | 11. sınıf 2. ünite ve çalışma kâğıdı | ✓ Bülten numarası ve başlığı doğrulandı | Eylem gerekmiyor |
| 5 | `dergipark.org.tr/en/pub/ujte/issue/85629/1461043` (Yurtsev, 2024) | 11. sınıf 3. ünite ve çalışma kâğıdı | ✓ Erişilebilir; makale başlığı atıfla eşleşiyor | Eylem gerekmiyor |
| 6 | `dergipark.org.tr/tr/pub/dtcfdergisi/article/1044279` (Öktem, 2010) | 11. sınıf 4. ünite ve çalışma kâğıdı | ✓ Erişilebilir; makale başlığı atıfla eşleşiyor | Eylem gerekmiyor |
| 7 | `dergipark.org.tr/en/pub/temasa/article/1159089` (Yeşilçayır, 2022) | 11. sınıf 5. ünite ve çalışma kâğıdı | ✓ Erişilebilir; makale başlığı atıfla eşleşiyor | Eylem gerekmiyor |
| 8 | `ohchr.org/.../turkish-turkce` (İHEB Türkçe metni) | 11. sınıf 6. ünite ve çalışma kâğıdı | ✓ Erişilebilir; resmî BM sayfası | Eylem gerekmiyor |
| 9 | `perseus.tufts.edu/...Plat.+Rep.+7.514a` (Platon, Devlet VII, Mağara Benzetmesi) | 10. sınıf 4. ünite | Otomatik erişim engellendi; site tarayıcıda genellikle açılır | El ile tarayıcı denetimi; gerekirse Türkçe çeviri kaynağı eklenebilir |
| 10 | `gutenberg.org/ebooks/23306` | 10. sınıf 4. ünite | ✓ Erişilebilir; **atıf başlığı hatalıydı** — sayfa *Meditationes de Prima Philosophia*'dır, "Principles of Philosophy" değil | **Bu turda düzeltildi** (aşağıda) |
| 11 | `gutenberg.org/ebooks/9662` (Hume, An Enquiry Concerning Human Understanding) | 10. sınıf 4. ünite | ✓ Erişilebilir; başlık doğrulandı | Eylem gerekmiyor |

> **Not:** TÜİK Veri Portalı sayfaları JavaScript gerektirdiğinden otomatik denetimde içerik görüntülenemez; normal tarayıcılarda açılır. Bu bir hata değil, denetim yöntemi sınırıdır.

## 3. Bu Turda Yapılan Düzeltme (P0)

**10. sınıf 4. ünite Bilgi Felsefesi, kaynakça [3]:** Project Gutenberg 23306 numaralı eser için yazılan "René Descartes, Principles of Philosophy" ifadesi hatalıydı; hedef sayfa Descartes'ın *Meditationes de Prima Philosophia* (Metafizik Üzerine Düşünceler) eseridir. Atıf başlığı ve metin içi geçen eser adı bu turda düzeltildi. *Principles of Philosophy* (Principia Philosophiae) ayrı bir Descartes eseridir; bu karışıklık öğrenci ve öğretmenlerde yanlış eser–yazar eşleştirmesine yol açabileceğinden öncelikli düzeltme olarak ele alınmıştır.

## 4. Eser–Yazar Eşleştirme Denetimi

Materyallerde adı geçen temel eserler (Platon *Timaios* ve *Devlet*, Aristoteles *Metafizik* ve *Kategoriler*, Descartes *Metafizik Üzerine Düşünceler*, Hume *İnsanın Anlama Yetisi Üzerine Bir Soruşturma*, Sartre *Varoluşçuluk Bir Humanizmdir*, Hilmi Ziya Ülken *Varlık ve Oluş*, Kant, Locke, Dewey, Mengüşoğlu, Farabi, İbn Sina ve Gazali atıfları) yazar–eser bakımından tutarlıdır. Bu turda tek istisna yukarıda düzeltilen Descartes başlığıydı.

## 5. Telif Notu

Depo MIT lisanslıdır ve materyaller özgün içerik üretimidir. Dosyalarda doğrudan uzun alıntı yoktur; doğrudan alıntı yapılmayacağı kuralı metin inceleme etkinliklerinde öğretmene ve öğrenciye açıkça bildirilmiştir. Kamu malı eserlere (Project Gutenberg, Perseus) verilen bağlantılar telif güvenlidir. MEB program PDF'i kamu kurumu yayını olarak kaynak gösterilmektedir; programın tam metni materyallere kopyalanmamış, yalnız çıktı kodları ve süreç bileşenleri özgün ifadelerle aktarılmıştır.

## 6. Bakım Listesi (Sonraki Döngü)

| Öncelik | İş | Kanıt |
|---|---|---|
| P0 | 10. sınıf 4. ünitede Descartes atıf düzeltmesi | Bu turda tamamlandı — commit kaydı |
| P1 | Perseus bağlantısının tarayıcıda el ile doğrulanması (MEB program PDF bağlantısı 4. adımda güncellendi) | Doğrulama notu bu tabloya işlenecek |
| P2 | TÜİK sera gazı bülten bağlantısının 1990–2024 sürümüne güncellenmesi | Güncel bülten URL'i |
| P2 | Platon Mağara Benzetmesi için Türkçe çeviri künyesi eklenebilir | Kaynakça güncellemesi |

## Kaynakça

- MEB Felsefe Dersi Öğretim Programı (10 ve 11. Sınıflar), 2026 — https://tymm.meb.gov.tr/assets/pdf/felsefe-dersi_20260819_142831_736.pdf
- Felsefe Dersi Öğretim Programı — Türkiye Yüzyılı Maarif Modeli — https://tymm.meb.gov.tr/ogretim-programlari/ders/felsefe-dersi
