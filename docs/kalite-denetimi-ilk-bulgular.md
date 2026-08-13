# Depo Genel Kalite Denetimi — İlk Bulgular

**Denetim tarihi:** 13 Ağustos 2026  
**Kapsam:** 10. ve 11. sınıf Felsefe dersi için 15 ünite materyali ve 15 çalışma kâğıdı  
**Denetim türü:** İlk tur yapısal denetim  
**Resmî dayanak:** MEB Felsefe Dersi Öğretim Programı [1]

## 1. Kapsam ve Yöntem

Bu ilk tur, her ünite için çalışma kâğıdı varlığını, öğrenme çıktısı kodunun sınıf ve üniteyle tutarlılığını, ölçme puanı toplamını, etkinlik sürelerinin resmî ders saatiyle ilişkisini, ortak değerlendirme formu yönlendirmelerini, yerel Markdown bağlantılarını ve satır sonu biçimini topluca taramıştır. Denetim, yalnızca dosya yapısı ve açık biçimde yazılmış sayısal göstergeler üzerinden yapılmıştır; felsefi doğruluk, sınıf uygulamasının gerçekçi süresi, dış bağlantıların HTTP erişilebilirliği ve kaynakların güncelliği sonraki turlarda ayrıca denetlenecektir.

> **Önemli ayrım:** “Yapısal olarak doğrulanamadı” bulgusu, içeriğin kesinlikle hatalı olduğu anlamına gelmez. Bu bulgu; sürenin eşitlik denetimine uygun biçimde yazılmadığını, ev ödevi gibi sınıfta harcanan zamanın dışında bir öğe kullanıldığını veya eski şablonun güncel standardı izlemeyebileceğini gösterir.

## 2. İlk Tur Sonuç Özeti

| Denetim alanı | Sonuç | Değerlendirme |
|---|---:|---|
| Ünite materyali varlığı | 15/15 | Tüm ünite dosyaları mevcut |
| Çalışma kâğıdı varlığı | 15/15 | Tüm üniteler için en az bir çalışma kâğıdı mevcut |
| Öğrenme çıktısı kodu | 15/15 | Kodlar ilgili sınıf ve üniteyle tutarlı görünüyor |
| 100 puanlık ölçme yapısı | 15/15 | Puan bileşenleri toplamı 100 |
| Yerel Markdown bağlantıları | 15/15 | İlk taramada bozuk yerel bağlantı bulunmadı |
| Satır sonu boşlukları | 15/15 | İlk taramada biçim sorunu bulunmadı |
| Süresi açıkça resmî toplamla eşleşen ünite | 15/15 | Dört eski ünite düzeltildikten sonra tüm ünitelerin ders içi süreleri resmî toplamla eşleşmektedir |
| Süre planı öncelikli inceleme gerektiren ünite | 0/15 | İlk turda saptanan dört süre planı eksikliği giderildi |
| Ortak form linki standardizasyonu gereken ünite | 0/15 | İlk turda saptanan beş eski ünite yönlendirmesi doğrudan yerel Markdown bağlantılarına dönüştürüldü |

## 3. Doğrulanmış İlk Bulgular

### 3.1. Öncelik 1 — Dört Eski Ünitenin Ders Süresi Planı Giderildi

İlk taramada 10. sınıf 1, 3, 8 ve 9. ünitelerinde sınıf içi etkinlik süreleri, resmî ders saatiyle eşitlenecek açıklıkta değildi. Bu bulgu kalite protokolündeki **önemli** hata düzeyinde ele alındı. Her üniteye öğrenci ürünü, öğretmen modellemesi veya akran dönütü içeren ders içi uygulama aşamaları eklenerek süre akışı resmî toplamla eşitlendi. [2]

| Ünite | Resmî süre | İlk taramadaki ders içi süre | Giderilen eksiklik | Güncel ders içi süre |
|---:|---:|---:|---|---:|
| 10.1 Felsefenin Doğası | 400 dk / 10 saat | 190 dk | Etkinlik süreleri genişletildi; röportaj sorusu tasarlama ve akran provası eklendi | 400 dk |
| 10.3 Varlık Felsefesi | 320 dk / 8 saat | 160 dk | Resmî ders saati 10 saatten 8 saate düzeltildi; akım karşılaştırması ve metin inceleme provası eklendi | 320 dk |
| 10.8 Din Felsefesi | 240 dk / 6 saat | 110 dk + “ev ödevi olarak 1 hafta” | Metin inceleme laboratuvarı eklendi; ev ödevi ders içi süre dışında tutuldu | 240 dk |
| 10.9 Bilim Felsefesi | 240 dk / 6 saat | 100 dk + “ev ödevi olarak 1 hafta” | Metin inceleme laboratuvarı ve kanıt–yorum ayrımı eklendi; ev ödevi ders içi süre dışında tutuldu | 240 dk |

10. sınıf 2. ünite için ilk betik `dk` kısaltmasını ayrıştıramadığı için başlangıçta uyarı üretmiştir. Manuel doğrulamada açık sürelerin toplamı **320 dakika / 8 ders saati** olduğundan bu ünite için süre uyumsuzluğu bulgusu kapatılmıştır. Toplu denetim aracı `dk` ve `dakika` biçimlerini birlikte destekleyecek şekilde güncellenmiştir.

### 3.2. Öncelik 2 — Ortak Değerlendirme Formu Bağlantıları Standardize Edildi

10. sınıf 1, 2, 3, 8 ve 9. ünitelerindeki öz/akran değerlendirme, kontrol listesi ve metin inceleme aracı atıfları; `mufredat/ortak-materyaller/` altındaki geçerli dosyalara yönelen yerel Markdown bağlantılarına dönüştürülmüştür. Bu değişiklik, bakım sürecinde dosya hedefinin görünürlüğünü artırır ve öğretmenin ilgili ortak araca doğrudan ulaşmasını sağlar.

| Ünite | Güncel bağlantı standardı | Durum |
|---:|---|---|
| 10.1 Felsefenin Doğası | `[Ortak değerlendirme formları](../ortak-materyaller/degerlendirme-formlari.md)` | Tamamlandı |
| 10.2 Felsefe, Mantık ve Argümantasyon | `[Ortak değerlendirme formları](../ortak-materyaller/degerlendirme-formlari.md)` | Tamamlandı |
| 10.3 Varlık Felsefesi | `[Metin inceleme formu](../ortak-materyaller/metin-inceleme-formu.md)` ve `[akran değerlendirme formu](../ortak-materyaller/degerlendirme-formlari.md)` | Tamamlandı |
| 10.8 Din Felsefesi | Metin inceleme ile ortak değerlendirme formlarına doğrudan bağlantılar | Tamamlandı |
| 10.9 Bilim Felsefesi | Metin inceleme ile ortak değerlendirme formlarına doğrudan bağlantılar | Tamamlandı |

### 3.3. Olumlu Bulgular

11. sınıfın altı ünitesinde ve 10. sınıfın 4–7. ünitelerinde etkinlik süreleri doğrudan resmî süreye eşitlenmiş, 100 puanlık ölçme yapısı açıkça kurulmuş ve ortak değerlendirme formu yönlendirmeleri görünür biçimde verilmiştir. İlk taramada 15 ünitenin tümünde öğrenme çıktısı kodları sınıf/ünite bağlamıyla uyumlu görünmüş; yerel Markdown bağlantısı veya satır sonu boşluğu kaynaklı teknik hata bulunmamıştır.

## 4. Sonraki Denetim Döngüsü

Süre planı ve ortak form bağlantısı düzeltmeleri tamamlandığından sonraki uygulama turu, dış bağlantıların erişilebilirliği ile kaynak güncelliğini denetlemeye odaklanmalıdır. Ardından bütün üniteler için süre, puan, yerel bağlantı ve çalışma kâğıdı kontrolleri yeniden çalıştırılmalıdır.

Ardından dış bağlantıların erişilebilirliği, kaynakların güncelliği, etkinlik–öğrenme çıktısı–ölçme hizası, felsefi kavramların doğruluğu ve öğretmen kullanım gerçekçiliği için ikinci bir pedagojik denetim turu yapılmalıdır. Bu ilk rapor, ikinci turu başlatacak teknik ve içerik önceliklerini tanımlar; tam kalite denetiminin nihai sonucu değildir.

## 5. Referanslar

[1]: https://tymm.meb.gov.tr/upload/program/2024programfel1011Onayli.pdf "MEB Felsefe Dersi Öğretim Programı (10 ve 11. Sınıflar), 2024"

[2]: `/home/ubuntu/skills/felsefe-ogretmeni/references/quality-protocol.md` "Felsefe öğretim kaynakları kalite protokolü"
