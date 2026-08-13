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
| Süresi açıkça resmî toplamla eşleşen ünite | 11/15 | 10. sınıf 4–7 ile 11. sınıf 1–6 doğrudan doğrulandı; 10. sınıf 2’nin manuel süre toplamı da 320 dakikadır |
| Süre planı öncelikli inceleme gerektiren ünite | 4/15 | 10. sınıf 1, 3, 8 ve 9 |
| Ortak form linki standardizasyonu gereken ünite | 5/15 | 10. sınıf 1, 2, 3, 8 ve 9 |

## 3. Doğrulanmış İlk Bulgular

### 3.1. Öncelik 1 — Dört Eski Ünitede Ders Süresi Planı Tam Değil

10. sınıf 1, 3, 8 ve 9. ünitelerde etkinlik süreleri veya performans görevi süresi, resmî ders saatiyle eşitlenecek açık bir ders içi zaman planı oluşturmak için yeterli değildir. Bu bulgu, kalite protokolünde **önemli** hata düzeyindedir; çünkü süre planı öğrenme–öğretme uygulamasının sınıf içinde uygulanabilir olup olmadığını doğrudan etkiler. [2]

| Ünite | Resmî süre | Dosyada açıkça yazılmış ders içi süre | İlk bulgu | Öncelikli düzeltme |
|---:|---:|---:|---|---|
| 10.1 Felsefenin Doğası | 400 dk / 10 saat | 190 dk | 210 dakikalık ders içi zaman açıkça dağıtılmamış | Etkinlik akışını 400 dakikaya tamamla; öğretmen hamlesi ve öğrenci ürünü ekle |
| 10.3 Varlık Felsefesi | 400 dk / 10 saat | 160 dk | 240 dakikalık ders içi zaman açıkça dağıtılmamış | Akım karşılaştırma, metin inceleme ve performans görevi için ders içi aşamalar ekle |
| 10.8 Din Felsefesi | 240 dk / 6 saat | 110 dk + “ev ödevi olarak 1 hafta” | Ev ödevi, ders saati yerine geçmediği için sınıf içi toplam doğrulanamıyor | 130 dakikalık ders içi süreç ekle; ev ödevini ek/isteğe bağlı kanıt olarak ayır |
| 10.9 Bilim Felsefesi | 240 dk / 6 saat | 100 dk + “ev ödevi olarak 1 hafta” | Ev ödevi, ders saati yerine geçmediği için sınıf içi toplam doğrulanamıyor | 140 dakikalık ders içi süreç ekle; ev ödevini ek/isteğe bağlı kanıt olarak ayır |

10. sınıf 2. ünite için ilk betik `dk` kısaltmasını ayrıştıramadığı için başlangıçta uyarı üretmiştir. Manuel doğrulamada açık sürelerin toplamı **320 dakika / 8 ders saati** olduğundan bu ünite için süre uyumsuzluğu bulgusu kapatılmıştır. Bu durum, toplu denetim aracının `dk` ve `dakika` biçimlerini birlikte destekleyecek şekilde güncellenmesi gerektiğini gösterir.

### 3.2. Öncelik 2 — Ortak Değerlendirme Formlarına Açık Bağlantı Standardı Eski Beş Ünitede Farklı

10. sınıf 1, 2, 3, 8 ve 9. üniteler; öz/akran değerlendirme, kontrol listesi veya metin inceleme formunu metin içinde anmaktadır. Ancak yeni ünitelerdeki standart olan tam yerel Markdown bağlantısı (`mufredat/ortak-materyaller/degerlendirme-formlari.md`) tüm eski dosyalarda tutarlı biçimde kullanılmamıştır. Bu, dosyaların form içermediği anlamına gelmez; erişilebilirlik ve bakım açısından bağlantı biçiminin standardize edilmesi gerektiğini gösterir.

| Ünite | Mevcut durum | İyileştirme |
|---:|---|---|
| 10.1 Felsefenin Doğası | Ortak değerlendirme formu dosya yolu metin içinde belirtilmiş | Tam yerel Markdown bağlantısına dönüştür |
| 10.2 Felsefe, Mantık ve Argümantasyon | Ortak değerlendirme formu dosya yolu metin içinde belirtilmiş | Tam yerel Markdown bağlantısına dönüştür |
| 10.3 Varlık Felsefesi | Metin inceleme formuna atıf var; değerlendirme formu yönlendirmesi açık standarda bağlanmalı | İki ortak form için görünür bağlantı ekle |
| 10.8 Din Felsefesi | `ortak-materyaller/` klasörüne genel atıf var | Kullanılan formlara doğrudan bağlantı ekle |
| 10.9 Bilim Felsefesi | `ortak-materyaller/` klasörüne genel atıf var | Kullanılan formlara doğrudan bağlantı ekle |

### 3.3. Olumlu Bulgular

11. sınıfın altı ünitesinde ve 10. sınıfın 4–7. ünitelerinde etkinlik süreleri doğrudan resmî süreye eşitlenmiş, 100 puanlık ölçme yapısı açıkça kurulmuş ve ortak değerlendirme formu yönlendirmeleri görünür biçimde verilmiştir. İlk taramada 15 ünitenin tümünde öğrenme çıktısı kodları sınıf/ünite bağlamıyla uyumlu görünmüş; yerel Markdown bağlantısı veya satır sonu boşluğu kaynaklı teknik hata bulunmamıştır.

## 4. Sonraki Denetim Döngüsü

Bir sonraki uygulama turu önce 10. sınıf 1, 3, 8 ve 9. ünitelerin süre planını resmî ders saatiyle eşitlemelidir. Aynı değişiklik setinde, eski beş ünitedeki ortak form yönlendirmeleri yeni ünitelerin bağlantı standardına getirilmelidir. Düzeltmelerden sonra bütün üniteler için süre, puan, yerel bağlantı ve çalışma kâğıdı kontrolleri yeniden çalıştırılmalıdır.

Ardından dış bağlantıların erişilebilirliği, kaynakların güncelliği, etkinlik–öğrenme çıktısı–ölçme hizası, felsefi kavramların doğruluğu ve öğretmen kullanım gerçekçiliği için ikinci bir pedagojik denetim turu yapılmalıdır. Bu ilk rapor, ikinci turu başlatacak teknik ve içerik önceliklerini tanımlar; tam kalite denetiminin nihai sonucu değildir.

## 5. Referanslar

[1]: https://tymm.meb.gov.tr/upload/program/2024programfel1011Onayli.pdf "MEB Felsefe Dersi Öğretim Programı (10 ve 11. Sınıflar), 2024"

[2]: `/home/ubuntu/skills/felsefe-ogretmeni/references/quality-protocol.md` "Felsefe öğretim kaynakları kalite protokolü"
