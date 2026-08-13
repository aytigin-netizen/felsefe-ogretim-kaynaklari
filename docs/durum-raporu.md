# Proje Durum Raporu — Felsefe Öğretim Kaynakları

**Depo:** [github.com/aytigin-netizen/felsefe-ogretim-kaynaklari](https://github.com/aytigin-netizen/felsefe-ogretim-kaynaklari)
**Rapor tarihi:** 13 Ağustos 2026
**Hazırlayan:** Manus AI

Bu rapor, proje kapsamında bugüne kadar yapılan çalışmaları, mevcut durumu ve yeni sohbette kaldığı yerden devam edilmesi için gerekli tüm bilgileri belgeler. **Sıradaki işlem, 4. ünite (Bilgi Felsefesi)nin aynı standartlarda ve detaylı çalışma kâğıtlarıyla güncellenmesidir.**

---

## 1. Proje Özeti ve Referans Kaynaklar

Proje, Türkiye Yüzyılı Maarif Modeli kapsamında MEB tarafından onaylanan **Felsefe Dersi Öğretim Programı** için açık kaynak öğretim materyalleri üretmektedir. 10. sınıf programı 9 üniteden ve toplam 72 ders saatinden oluşur.

> **Resmî kaynak (her zaman geçerli):** MEB onaylı program PDF'i depoda değil, kaynağında kullanılmalıdır. PDF: [https://tymm.meb.gov.tr/upload/program/2024programfel1011Onayli.pdf](https://tymm.meb.gov.tr/upload/program/2024programfel1011Onayli.pdf) — Paylaşılan adres: [https://share.google/7kfRpceUehLfXVCaI](https://share.google/7kfRpceUehLfXVCaI) (tymm.meb.gov.tr ders sayfasına yönlendirir).

**Çalışma yöntemi (bu rapordan sonraki her işte uygulanması gereken standart süreç):**
1. Resmî program PDF'inden ilgili ünitenin kazanım, beceri, değerler, içerik çerçevesi, anahtar kavramlar, öğrenme kanıtları, performans görevi, zenginleştirme ve destekleme bölümlerini birebir çıkarma
2. `mufredat/template.md` şablonuna göre ünite dosyasını yazma (eski uydurma içerikli dosya varsa silinip yenisi yazılır)
3. Birim bazlı çalışma kâğıdını `mufredat/10-sinif/calisma-kagitlari/` klasörüne oluşturma
4. Kalite kontrolü: saat toplamı resmî süreye, puan toplamı 100'e eşit olmalı
5. README durum tablosu güncellenir, commit mesajı dosyadan (`git commit -F`) okutularak push edilir

**Teknik not:** Çok satırlı commit mesajları shell üzerinden doğrudan gönderildiğinde oturum askıda kalıyor; commit mesajı `/home/ubuntu/commit_msg.txt` biçiminde bir dosyaya yazılıp `git commit -F /home/ubuntu/commit_msg.txt` ile işlenmelidir.

---

## 2. Mevcut Durum: Ünite Bazında

| Ünite | Başlık | Saat | Durum | Çalışma Kâğıdı | Commit |
|-------|--------|------|-------|----------------|--------|
| 1 | Felsefenin Doğası | 10 | Tamamlandı (resmî doğrulamalı) | `01-felsefenin-dogasi-ck.md` | `3fcac7f` |
| 2 | Felsefe, Mantık ve Argümantasyon | 8 | Tamamlandı (resmî doğrulamalı) | `02-mantik-argumantasyon-ck.md` | `b69ecbc` |
| 3 | Varlık Felsefesi | 8 | Tamamlandı (resmî doğrulamalı) | `03-varlik-felsefesi-ck.md` | `7e59ec0` |
| **4** | **Bilgi Felsefesi** | **8** | **ŞABlon düzeyinde — SIRADAKİ İŞ** | **henüz yok** | — |
| 5 | Ahlak Felsefesi | 8 | Şablon düzeyinde | henüz yok | — |
| 6 | Estetik ve Sanat Felsefesi | 6 | Şablon düzeyinde (içeriği zengin) | henüz yok | — |
| 7 | Siyaset Felsefesi | 8 | Şablon düzeyinde (içeriği zengin) | henüz yok | — |
| 8 | Din Felsefesi | 6 | Tamamlandı (resmî doğrulamalı) | `08-din-felsefesi-ck.md` | `646b77c` |
| 9 | Bilim Felsefesi | 6 | Tamamlandı (resmî doğrulamalı) | `09-bilim-felsefesi-ck.md` | `646b77c` |

Tamamlanan üniteler resmî programın kazanım kodları, saat, oran ve süreç bileşenleriyle birebir doğrulanmıştır. Şablon düzeyindeki 4, 5, 6 ve 7. üniteler ise eski içeriklerle (bazen uydurma kazanım kodları, örneğin eski 2. ünitede FEL.10.2.1/2/3 gibi var olmayan kodlar tespit edilmiş ve düzeltilmiştir) beklemektedir; bu nedenle her güncellemede eski dosya resmî programdan kontrol edilerek yeniden yazılmalıdır.

## 3. Kurulan Altyapı ve Ortak Materyaller

Çalışma sırasında yeniden üretim yerine ortak kullanım için bir altyapı kurulmuştur:

| Dosya/Klasör | İşlevi |
|--------------|--------|
| `mufredat/template.md` | Ortak ünite şablonu ve katkı kılavuzu |
| `mufredat/ortak-materyaller/metin-inceleme-formu.md` | Performans görevi metin inceleme formu (3, 8 ve 9. ünitelerde kullanıldı; 4. ünitede de kullanılacak) |
| `mufredat/ortak-materyaller/degerlendirme-formlari.md` | Öz ve akran değerlendirme şablonları + kontrol listesi + grup değerlendirme formu |
| `mufredat/10-sinif/calisma-kagitlari/` | Birim bazlı çalışma kâğıtları (her biri cevap anahtarlı) |
| `docs/denetim-raporu.md` | 1, 3, 8, 9. ünitelerin resmî kanıt gereklilikleri karşılama denetimi |

Standart bir tamamlanmış ünite dosyası şu bölümleri içerir: Ünite Bilgileri tablosu, Öğrenme Çıktıları (resmî kazanım kodu ve bentleri), Alan/Kavramsal Beceriler ve süreç bileşenleri (eğilimler, SDB, değerler, okuryazarlık, disiplinler arası, beceriler arası), Anahtar Kavramlar tablosu, saat dağılımlı İçerik Çerçevesi, 6 Sınıf Etkinliği, Değerlendirme (Öğrenme Kanıtları + 100 puanlık Ölçme Araçları: 25+20+25+30 dağılımı), 4 kriterli Dereceli Puanlama Anahtarı, Farklılaştırma (resmî zenginleştirme ve destekleme bölümleri birebir işlenerek), Ek Tartışma Soruları ve Kaynaklar (MEB PDF bağlantısı dahil).

## 4. Sıradaki İş: 4. Ünite (Bilgi Felsefesi) Güncellemesi

### 4.1 Resmî Program Verileri (hazır — yeni sohbette tekrar çıkarılmaya gerek yok)

| Alan | Resmî Değer |
|------|-------------|
| Ünite kodu / saat / oran | FEL.10.4 / 8 saat / %11 |
| Kazanım | FEL.10.4.1. Bilgi felsefesinin konusunu, kavramlarını ve problemlerini muhakeme edebilme (4 bent: a konu ve temel kavramlar, b temel problemler, c düşünce ve argümanları değerlendirme, ç metin inceleme) |
| Alan becerileri | SBAB14. Felsefi Muhakeme (SBAB14.1 Problemleri Anlama, SBAB14.2 Düşünce ve Argümanları Değerlendirme, SBAB14.3 Metin İnceleme) |
| Eğilimler | E3.4 Gerçeği Arama, E3.5 Açık Fikirlilik, E3.6 Analitik Düşünme, E3.9 Şüphe Duyma |
| SDB / Değerler | SDB1.2 Kendini Düzenleme; D3 Çalışkanlık, D12 Sabır, D14 Saygı, D16 Sorumluluk |
| Okuryazarlık | OB1 Bilgi, OB2 Dijital, OB4 Görsel |
| Disiplinler arası | Matematik, Mantık |
| Beceriler arası | KB2.7 Karşılaştırma, KB2.8 Sorgulama, KB2.10 Çıkarım, KB2.13 Yapılandırma, KB2.18 Tartışma, KB3.3 Eleştirel Düşünme |
| İçerik çerçevesi | (1) Bilgi Felsefesinin Konusu ve Temel Kavramları; (2) Bilgi Felsefesinin Temel Problemleri (Bilginin İmkânı, Kaynağı, Doğruluk Ölçütleri) |
| Anahtar kavramlar (resmî, 3 adet) | bilgi, doğruluk, gerçeklik |
| Öğrenme kanıtları (resmî) | öz değerlendirme formu, akran değerlendirme formu, dereceli puanlama anahtarı, dereceleme ölçeği ve performans görevi |

**Resmî uygulama adımları (etkinliklere dönüştürülecek):** ön değerlendirmede kelime ilişkilendirme testi; köprü kurmada dezenformasyon örnekleri; bilgi olan-olmayan ifadelerin ayırt edilmesi ve önerme-argüman-akıl yürütme ilişkisi; Platon mağara benzetmesiyle bilgi-sanı, gerçeklik-doğruluk sorgulaması; kuşkucu filozoflar (Gorgias, Pyrrhon) ile dogmatik filozoflar (Sokrates, Platon, Aristoteles) karşılaştırması; Descartes'ın Rüya Argümanı ve kuşku yönteminin farkı; bilginin kaynağında dört görüş (rasyonalizm, empirizm, kritisizm, entüisyonizm) ve duyu-akıl-sezgi tartışması; doğruluk ölçütleri (uygunluk, tutarlılık, tümel uzlaşım, yarar) ve gazete/TV örnekleri üzerinden disiplin bazlı tartışma.

**Resmî performans görevi ve metin havuzu:** Öğrenciler metin inceleme formu doldurur. Havuz: Platon *Theaitetos* veya *Sofist*; S. Empiricus *Kuşkuculuk*; Gazali *Hakikat Arayışı*; R. Descartes *Felsefenin İlkeleri*; J. Locke *İnsan Anlığı Üzerine Bir Deneme*; I. Kant *Saf Aklın Eleştirisi*; Necati Öner *Bilginin Serüveni*. Bu havuz için `ortak-materyaller/metin-inceleme-formu.md` zaten hazır; ünite dosyasına bağlanması yeterlidir.

**Resmî zenginleştirmeler:** bilgi türleri (tanışıklık, önermesel, nasılın bilgisi) dijital zihin haritası; Gazali'nin Descartes'a etkisi; D. Hume *İnsanın Anlama Yetisi Üzerine Bir Soruşturma*'dan nedensellik ilkesi metni. **Resmî destekleme:** görsel-işitsel ağırlıklı materyaller, akran öğretimi, kavram-problem-argümanların doğrudan verilip kendi cümleleriyle ifade ettirme.

### 4.2 Uygulanacak Adımlar

1. Resmî veriler `/home/ubuntu/felsefe-programi.txt` dosyasında satır 1080-1244 arasında zaten çıkarılmıştır (ayrıca `/home/ubuntu/4uznite-hazirlik.md` içinde özetlenmiştir); doğrulanmamış alan bırakılmamalıdır.
2. `mufredat/10-sinif/04-bilgi-felsefesi.md` mevcut dosyası (~753 kelime, şablon düzeyinde) resmî programa uygun yeni sürümle değiştirilmeli: önce `rm` ile silinip `template.md` yapısına göre yeniden yazılmalı. İçerik dağılımı önerisi: 2 saat konu ve kavramlar + 3 saat temel problemler (imkân ve kaynak) + 3 saat doğruluk ölçütleri ve metin inceleme = 8 saat.
3. `mufredat/10-sinif/calisma-kagitlari/04-bilgi-felsefesi-ck.md` hazırlanmalı: Bölüm A kelime ilişkilendirme testi (resmî ön değerlendirme), Bölüm B bilgi olan-olmayan ifadeler + önerme/argüman/akıl yürütme uygulaması, Bölüm C kuşkucu vs dogmatik tablo + Descartes Rüya Argümanı çözümleme, Bölüm D dört kaynak görüşü + duyu-akıl-sezgi hazırlığı, Bölüm E dört doğruluk ölçütü + disiplin eşleştirme, Bölüm F metin inceleme planı; cevap anahtarları A, B, D için.
4. Ünite dosyasının Etkinlik ve Değerlendirme bölümleri çalışma kâğıdına ve `ortak-materyaller/` formuna yönlendirmeli.
5. Kalite kontrolü: saat toplamı 8, puan toplamı 100 (önerilen: 25+20+25+30).
6. `README.md` durum tablosunda 4. ünite "Tamamlandı (resmî program doğrulamalı)" yapılmalı; `docs/denetim-raporu.md`'ye 4. ünite denetim satırı eklenmeli.
7. Commit mesajı `/home/ubuntu/commit_msg.txt` dosyasına yazılıp `git -c user.name="Manus AI" -c user.email="manus@manus.im" commit -F /home/ubuntu/commit_msg.txt && git push origin main` ile gönderilmeli.
8. Kullanıcıya sonuç mesajı tablo + özet + "önerdiğim sonraki adım: 5. ünite (Ahlak Felsefesi)" biçiminde iletilmeli.

### 4.3 Sonraki Ünitelerin Giriş Bilgileri (sırayla devam için)

4. ünite tamamlandıktan sonra sıradaki 5. ünite **Ahlak Felsefesi**dir (8 saat, %11, FEL.10.5.1, SBAB14 yapısı sürer; program dosyasında 1244. satırdan başlar). Onun ardından 6. ünite **Estetik ve Sanat Felsefesi** (6 saat, %8) ve 7. ünite **Siyaset Felsefesi** (8 saat, %11) gelir. 11. sınıf müfredatı henüz depoda yoktur; 10. sınıf tamamlandıktan sonra aynı yöntemle (resmî PDF'ten program bilgileri 2.595. satırdaki Edebiyat ve Felsefe ünitesinden sonra gelir) oluşturulması önerilir.

---

## 5. Önemli Kararlar ve Dersler (yeni sohbette tekrarlanmaması için)

İlk incelemede 3. ünitede *Being and Nothingness* eserinin Heidegger'a değil Sartre'a ait olduğu tespit edilmiş ve düzeltilmiştir; benzer şekilde resmî programdaki "Milgram'ın Otorite ve İtaat" deneyi adının bozuk yazımı diğer ünitelerde doğru biçimiyle kullanılmıştır. Eski dosyalarda uydurma kazanım kodları bulunduğundan, güncelleme öncesinde her ünite mutlaka resmî PDF ile karşılaştırılmalıdır. Ortak formlar (metin inceleme, öz/akran değerlendirme) ünite bazında çoğaltılmamalı, `ortak-materyaller/` klasöründen referans verilmelidir. Ayrıca her üniteye eklenen çalışma kâğıtları ve ölçme araçları, resmî programın "Öğrenme Kanıtları" bölümündeki liste esas alınarak denetlenmiştir; programda anılan ancak içeriği olmayan araçlar yeni kâğıtlarla giderilmiştir.
