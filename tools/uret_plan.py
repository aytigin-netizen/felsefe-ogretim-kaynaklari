#!/usr/bin/env python3
"""Ünite içerik çerçevelerinden TYMM formatında haftalık günlük (ders) planları üretir.

Kullanım:
    python tools/uret_plan.py           # haftalık plan dosyalarını (yeniden) üretir
    python tools/uret_plan.py --check   # depodaki planlar üretimle uyuşuyor mu diye bakar

Plan, MEB "Eğitim ve Öğretim Çalışmalarının Planlı Yürütülmesine Dair Yönerge"
bölümleriyle TYMM günlük plan bileşenlerini (öğrenme çıktısı + süreç bileşenleri,
alan becerisi, eğilim, öğretme-öğrenme akışı, ölçme-değerlendirme, farklılaştırma)
birleştirir. Araç felsefi içerik üretmez: pedagojik haftalık eşleme WEEK_CONFIG
yapılandırmasında açıkça tanımlıdır ve ünite dosyasındaki resmî verilerle
eşleşmezse hata verir.

Takvim verisi MEB 2026-2027 Çalışma Takvimi'ne (2026/68 sayılı genelge) göredir:
1. dönem 14 Eylül 2026 – 22 Ocak 2027, 1. dönem ara tatili 16–20 Kasım 2026,
yarıyıl tatili 25 Ocak – 5 Şubat 2027, 2. dönem 8 Şubat – 25 Haziran 2027,
2. dönem ara tatili 8–12 Mart 2027.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUFREDAT = ROOT / "mufredat"
PROGRAM = json.loads((MUFREDAT / "program-2026-ozet.json").read_text(encoding="utf-8"))

GRADE = "10-sinif"
UNIT_FILE = "01-felsefenin-dogasi.md"
UNIT_NO = 1
UNIT_TITLE = PROGRAM["units"]["10"][UNIT_NO - 1]["title"]
UNIT_CODE = PROGRAM["units"]["10"][UNIT_NO - 1]["code"]
UNIT_HOURS = PROGRAM["units"]["10"][UNIT_NO - 1]["hours"]
OUTCOME_CODE = PROGRAM["units"]["10"][UNIT_NO - 1]["outcomes"][0]
OUTCOME_TEXT = PROGRAM["outcomes"][OUTCOME_CODE]

OUTPUT_DIR = MUFREDAT / GRADE / "gunluk-planlar"
UNIT_PATH = MUFREDAT / GRADE / UNIT_FILE

# --- MEB 2026-2027 çalışma takvimi -------------------------------------------

SEMESTER_1 = (date(2026, 9, 14), date(2027, 1, 22))
SEMESTER_2 = (date(2027, 2, 8), date(2027, 6, 25))
BREAKS = [
    (date(2026, 11, 16), date(2026, 11, 20)),   # 1. dönem ara tatili
    (date(2027, 1, 25), date(2027, 2, 5)),      # yarıyıl tatili
    (date(2027, 3, 8), date(2027, 3, 12)),      # 2. dönem ara tatili
]
SINGLE_DAY_HOLIDAYS = {
    date(2026, 10, 29): "Cumhuriyet Bayramı",
    date(2027, 1, 1): "Yılbaşı",
    date(2027, 4, 23): "Ulusal Egemenlik ve Çocuk Bayramı",
    date(2027, 5, 19): "Atatürk'ü Anma, Gençlik ve Spor Bayramı ve Kurban Bayramı",
}

MONTHS_TR = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
             "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def teaching_weeks() -> list[tuple[int, date, date, list[str]]]:
    """(yıl haftası, pazartesi, cuma, o haftadaki tatil günleri) listesi."""
    weeks: list[tuple[int, date, date, list[str]]] = []
    for start, end in (SEMESTER_1, SEMESTER_2):
        monday = start
        while monday <= end:
            friday = monday + timedelta(days=4)
            if not any(b_start <= monday and friday <= b_end for b_start, b_end in BREAKS):
                holidays = [
                    name for day, name in SINGLE_DAY_HOLIDAYS.items()
                    if monday <= day <= friday
                ]
                weeks.append((len(weeks) + 1, monday, friday, holidays))
            monday += timedelta(days=7)
    return weeks


def format_range(monday: date, friday: date) -> str:
    if monday.month == friday.month:
        return f"{monday.day}–{friday.day} {MONTHS_TR[monday.month]} {monday.year}"
    return (
        f"{monday.day} {MONTHS_TR[monday.month]} – "
        f"{friday.day} {MONTHS_TR[friday.month]} {friday.year}"
    )

# --- Ünite dosyasından resmî verilerin okunması -------------------------------


def parse_unit(text: str) -> tuple[list[str], list[str], list[tuple[int, str, float]], list[tuple[int, str]]]:
    """(süreç bileşenleri, anahtar kavramlar, (no, başlık, saat), (etkinlik no, adı))."""
    outcome_block = re.search(
        r"^###\s+" + re.escape(OUTCOME_CODE) + r"\s+—.*?$(.*?)(?=^###\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    components = []
    if outcome_block:
        components = [
            line[2:].strip()
            for line in outcome_block.group(1).splitlines()
            if line.startswith("- ")
        ]

    concepts = re.findall(r"^\|\s*\*\*(.+?)\*\*\s*\|", text, flags=re.MULTILINE)

    topics = [
        (int(no), title.strip(), float(hours.replace(",", ".")))
        for no, title, hours in re.findall(
            r"^###\s+(\d+)\.\s+(.+?)\s+\((\d+(?:,\d+)?)\s+saat\)",
            text,
            flags=re.MULTILINE,
        )
    ]

    activities = [
        (int(no), name.strip())
        for no, name in re.findall(r"^###\s+Etkinlik\s+(\d+):\s*(.+)$", text, flags=re.MULTILINE)
    ]
    return components, concepts, topics, activities


# --- Haftalık pedagojik eşleme (ünite 1 pilot) --------------------------------
# topics: (içerik no, o haftadaki saat, ek not); ders saati başına 2 saat/hafta.
# components: süreç bileşeni indeksi (0 tabanlı); activities: (etkinlik no, dk).

WEEK_CONFIG = [
    {
        "year_week": 1,
        "unit_week": 1,
        "topics": [(1, 2.0, "tamamı")],
        "components": [0, 1, 2],
        "concepts": ["Felsefe", "Bilgelik", "Filozof"],
        "tendencies": "E1.1. Merak, E3.5. Açık Fikirlilik",
        "skill": "SBAB13. Felsefi Sorgulama",
        "activities": [(1, 40, "tam süre"), (2, 40, "25–40 dk arası uyarlanabilir")],
        "methods": "Konuşma halkası / akvaryum, bireysel yazma, ortak pano oluşturma",
        "tools": "Görsel/işitsel köprü materyali, post-it/kâğıt, filozof tanım kartları, tahta",
        "lessons": [
            {
                "title": "1. ders saati — Güdüleme ve keşfetme",
                "steps": [
                    "Ön değerlendirme (≈5 dk): \"Felsefe kelimesini duyunca aklınıza ne geliyor?\" sorusuna kısa yanıtlar alınır; notlandırılmaz, öğretmene başlangıç verisi sağlar (ünite dosyası: Öğrenme-Öğretme Yaşantıları).",
                    "Köprü kurma + Etkinlik 1 (≈35 dk): kısa bir yazılı/görsel/işitsel materyal gösterilir; \"Felsefe sizin için ne anlama geliyor?\" sorusuyla bireysel görüşler yazılır, gönüllüler paylaşır, iki sütunlu \"felsefe duvarı\" panosu oluşturulur.",
                ],
            },
            {
                "title": "2. ders saati — Derinleştirme",
                "steps": [
                    "Kısa anlatım (≈15 dk): philo–sophia kökeni, \"bilgelik sevgisi\", hikmet–sevgi–arayış üçlüsü ve filozofun kimliği (ünite dosyası: İçerik Çerçevesi 1).",
                    "Etkinlik 2 (≈25 dk): Platon, Aristoteles, Descartes ve Kant tanım kartları dağıtılır; \"hangi tanım en güçlü, neden?\" sorusuyla grup görüşü oluşturulur ve \"Felsefenin ortak bir tanımı yapılabilir mi?\" sorusu kısaca tartışmaya açılır.",
                    "Kapanış (≈2 dk): iki ders saatine ilişkin kazanım özeti ve gelecek hafta köprüsü.",
                ],
            },
        ],
        "assessment": "Sınıfın ortak ön kavram haritası ve Etkinlik 2'nin gerekçeli grup görüşü toplanır. Bu haftanın kanıtları, ünitenin izlenebilirlik matrisinde `FEL.10.1.1` \"Felsefenin anlamını ve gelişim sürecini sorgular\" satırının (25 puan) girdisidir.",
        "differentiation": [
            "Zenginleştirme: \"Felsefe üzerine felsefe yapılabilir mi?\" sorusu üzerine kısa görüş yazısı (ünitenin Farklılaştırma bölümü).",
            "Destekleme: tanım kartlarına resim/somut örnek ekleme; tahta özeti ile ana kavramların görünür kılması.",
        ],
    },
    {
        "year_week": 2,
        "unit_week": 2,
        "topics": [(2, 2.0, "tamamı")],
        "components": [2, 3],
        "concepts": ["Felsefe", "Filozof"],
        "tendencies": "E3.7. Sistematik Olma, E3.5. Açık Fikirlilik",
        "skill": "SBAB13. Felsefi Sorgulama",
        "activities": [(3, 80, "tam süre; iki ders saatine yayılır")],
        "methods": "İş birlikli grup çalışması, tarih şeridi/infografik analizi, karşılaştırma tablosu",
        "tools": "Tarih şeridi infografiği, filozof kartları, büyük kâğıt",
        "lessons": [
            {
                "title": "1. ders saati — Keşfetme",
                "steps": [
                    "Köprü (≈5 dk): geçen haftanın \"felsefe duvarı\" panosuna dönülür; \"felsefe tek bir yerde mi doğdu?\" sorusu sorulur.",
                    "Etkinlik 3, ilk bölüm (≈35 dk): felsefi düşüncenin ortaya çıkışı ve tarihsel dönemlerin sosyal/kültürel/siyasal/ekonomik koşulları tarih şeridi üzerine yerleştirilir (Milet Okulu, Atina demokrasisi, bilimsel devrim, Dewey'in demokrasisi, Mengüşoğlu ve Türk düşünce ortamı).",
                ],
            },
            {
                "title": "2. ders saati — Derinleştirme",
                "steps": [
                    "Etkinlik 3, ikinci bölüm (≈40 dk): gruplara bir dünya felsefe geleneği (Hint, Çin, Antik Yunan, Türk İslam, Fransız, Alman, Anglosakson, Amerikan, Türkiye) atanır; temsilciler ve konu alanları incelenip benzer/farklı yönler iş birlikli ayırt edilir.",
                    "Kapanış (≈5 dk): gelenekler karşılaştırma tablosu panoya asılır; koşul–soru ilişkisi tek cümleyle özetlenir.",
                ],
            },
        ],
        "assessment": "Gelenekler karşılaştırma tablosu (KB2.7, OB5) toplanır; izlenebilirlik matrisinde `FEL.10.1.1` \"anlamını ve gelişim sürecini sorgular\" satırının kanıtıdır.",
        "differentiation": [
            "Zenginleştirme: farklı medeniyetlerde felsefeye katkı veren kadın düşünürler hakkında kısa sunum hazırlama (ünitenin Farklılaştırma bölümü).",
            "Destekleme: gelenek kartlarına görsel ekleme; karşılaştırma tablosunda hazır sütun başlıkları verme.",
        ],
    },
    {
        "year_week": 3,
        "unit_week": 3,
        "topics": [(3, 2.0, "tamamı")],
        "components": [4],
        "concepts": ["Refleksiyon", "Sorgulama", "Hayret"],
        "tendencies": "E3.2. Odaklanma, E3.7. Sistematik Olma",
        "skill": "SBAB13. Felsefi Sorgulama",
        "activities": [(4, 60, "tam süre; ders saatlerine bölünür")],
        "methods": "Bireysel yazım, kelime ilişkilendirme, kavram haritası, dönüt verme",
        "tools": "Çalışma kâğıdı, dijital kavram haritası aracı (alternatif: eksik harita)",
        "lessons": [
            {
                "title": "1. ders saati — Keşfetme",
                "steps": [
                    "Etkinlik 4, Bölüm A (≈15 dk): çalışma kâğıdındaki kelime ilişkilendirme testi sınıfça çözülür.",
                    "Etkinlik 4, Bölüm B (≈25 dk): felsefi düşüncenin özellikleri tablosu (hayret, merak, şüphe, sorgulama, yığılımlı ilerleme; rasyonel, tutarlı, refleksif, eleştirel, sistematik, evrensel) doldurulmaya başlanır; her özellik kendi cümlesiyle ve günlük hayattan bir örnekle açıklanır.",
                ],
            },
            {
                "title": "2. ders saati — Derinleştirme",
                "steps": [
                    "Etkinlik 4, Bölüm B tamamlama (≈15 dk) ve Bölüm C (≈15 dk): açık uçlu sorular bireysel yazım için kullanılır; bireysel veya grup kavram haritası oluşturulur (eksik harita tamamlama alternatifi).",
                    "Dönüt (≈10 dk): kavram yanılgıları ve öğrenme eksiklikleri üzerine sınıfça dönüt verilir.",
                ],
            },
        ],
        "assessment": "Çalışma kâğıdı ve kavram haritası (OB1) toplanır; izlenebilirlik matrisinde `FEL.10.1.1` \"özelliklerini sorgular\" satırının (kısa cevap soruları bloğu) kanıtıdır.",
        "differentiation": [
            "Zenginleştirme: hayret ve refleksiyon özelliklerini bir film karesi ya da güncel olay üzerinden çözümleme.",
            "Destekleme: eksik verilmiş kavram haritası tamamlama alternatifi; özellik tanımları için cümle başlatıcıları (ünitenin Destekleme bölümü).",
        ],
    },
    {
        "year_week": 4,
        "unit_week": 4,
        "topics": [(4, 1.0, "tamamı"), (5, 1.0, "ilk yarısı")],
        "components": [5, 6],
        "concepts": ["Felsefi soru", "Sorgulama"],
        "tendencies": "E3.9. Şüphe Duyma, E1.1. Merak",
        "skill": "SBAB13. Felsefi Sorgulama",
        "activities": [(5, 50, "tam süre; iki yarım blok hâlinde"), (6, 50, "tam süre")],
        "methods": "Düşün–eşleş–paylaş, büyük grup tartışması, yapılandırılmış grid",
        "tools": "Akademik metin kartları, yapılandırılmış grid formu",
        "lessons": [
            {
                "title": "1. ders saati — İçerik 4: Felsefi Sorunun Temel Özellikleri",
                "steps": [
                    "Kısa anlatım (≈15 dk): felsefi sorunun beş ölçütü ve ayrıştırma örnek tablosu (bilimsel/günlük/felsefi sorular) üzerinden soru türleri ayırt edilir (ünite dosyası: İçerik Çerçevesi 4).",
                    "Etkinlik 5 (≈25 dk): öğrenciler yakın ve uzak çevrelerinden (okul, şehir, teknoloji, çevre) kendi felsefi sorularını türetir; her öğrenci sorusunun neden felsefi olduğunu açıklar; \"düşün, eşleş, paylaş\" tekniğiyle paylaşılır (KB2.10, KB2.18).",
                ],
            },
            {
                "title": "2. ders saati — İçerik 5 (başlangıç): Felsefenin Diğer Alanlarla İlişkisi",
                "steps": [
                    "Kısa anlatım (≈15 dk): felsefenin bilim, din ve sanatla benzerlik ve farklılıkları; bilim felsefesi, din felsefesi ve estetik dallarına giriş (ünite dosyası: İçerik Çerçevesi 5).",
                    "Etkinlik 6 (≈25 dk): benzerlik ve farklılıklar yapılandırılmış grid üzerine işaretlenir (E3.2); \"Bir yapay zekâ tablosu sanat mıdır?\" sorusu üç alan merceğinden değerlendirilmeye başlanır.",
                ],
            },
        ],
        "assessment": "Kişisel felsefi soru listesi ve gerekçeler (kısa cevap bloğu) ile yapılandırılmış grid (pratik etkinlikler bloğu) toplanır.",
        "differentiation": [
            "Zenginleştirme: bir yapay zekâ ya da sosyal medya sorusunu hem bilim hem felsefe sorusu olarak yeniden formüle etme çalışması.",
            "Destekleme: felsefi soru ölçütleri için kontrol listesi; grid örnek satırının öğretmence doldurulmuş gösterimi.",
        ],
    },
    {
        "year_week": 5,
        "unit_week": 5,
        "topics": [(5, 0.5, "tamamlama"), (6, 1.5, "tamamı")],
        "components": [7, 6],
        "concepts": ["Felsefe", "Felsefi soru"],
        "tendencies": "E2.1. Empati, E3.5. Açık Fikirlilik",
        "skill": "SBAB13. Felsefi Sorgulama",
        "activities": [(6, 10, "grid tartışması kapanışı"), (7, 50, "tam süre"), (8, 20, "tam süre")],
        "methods": "Savunma paneli, konuşma halkası, öz/akran değerlendirme, röportaj provası",
        "tools": "Öz/akran değerlendirme formları, performans görevi rubriği",
        "lessons": [
            {
                "title": "1. ders saati — İçerik 5 (kapanış) ve İçerik 6: Felsefenin İşlevleri",
                "steps": [
                    "Grid tartışmasının kapanışı (≈10 dk): \"Bir yapay zekâ tablosu sanat mıdır?\" değerlendirmesi üç alan merceğiyle tamamlanır.",
                    "Kısa anlatım (≈15 dk): felsefenin bireysel işlevleri (eleştirel düşünme, önyargı farkındalığı, anlam duruşu, gerekçelendirme) ve toplumsal işlevleri (demokratik kültür, sorun tartışması, bilimsel/hukuki düşünce, kültürel eleştiri) (ünite dosyası: İçerik Çerçevesi 6).",
                    "Etkinlik 7 başlangıcı (≈15 dk): \"Felsefe hayatta ne işe yarar?\" sorusuyla gruplar işlev listesi ve mantıksal temellendirme (KB2.8) hazırlar.",
                ],
            },
            {
                "title": "2. ders saati — Derinleştirme ve Performans Görevi Tanıtımı",
                "steps": [
                    "Etkinlik 7 tamamlama (≈20 dk): savunma paneli; görüşlerin tutarlılığı ve geçerliliği tartışılarak kabul edilir ya da reddedilir (E3.7, KB3.3); öz/akran değerlendirme formu kullanılır (E3.5).",
                    "Etkinlik 8 (≈20 dk): performans görevi (Felsefe Röportajı) tanıtılır; en az iki röportaj sorusu seçilir, iki dakikalık akran provası yapılır; görüşme etiği, anonimleştirme ve teslim ölçütleri planlanır.",
                ],
            },
        ],
        "assessment": "Felsefe işlevleri listesi ve gerekçeli kabul/red metni (pratik etkinlikler) ile röportaj soru taslağı ve teslim planı (performans görevi, 30 puan) toplanır. Röportaj ürünü 1 hafta içinde teslim edilir.",
        "differentiation": [
            "Zenginleştirme: Âşık Veysel ve Neşet Ertaş türkülerindeki felsefi ifadelerle işlev tartışmasını derinleştirme (ünitenin Farklılaştırma bölümü).",
            "Destekleme: röportaj için soru başlatıcıları ve örnek görüşme akışı; dijital araç rehberli kullanım (ünitenin Destekleme bölümü).",
        ],
    },
]

# --- Doğrulama ----------------------------------------------------------------


def validate_config(components: list[str], concepts: list[str], topics: list[tuple[int, str, float]], activities: list[tuple[int, str]]) -> None:
    assert abs(sum(hours for _, hours, _ in [t for w in WEEK_CONFIG for t in w["topics"]]) - UNIT_HOURS) < 0.01, (
        "Haftalık saat toplamı ünite saatine eşit değil"
    )
    per_week = [sum(hours for _, hours, _ in w["topics"]) for w in WEEK_CONFIG]
    for total, week in zip(per_week, WEEK_CONFIG):
        assert abs(total - 2.0) < 0.01, f"Yıl haftası {week['year_week']}: 2 saat bekleniyordu, {total} bulundu"
    topic_hours: dict[int, float] = {}
    for week in WEEK_CONFIG:
        for no, hours, _ in week["topics"]:
            topic_hours[no] = topic_hours.get(no, 0.0) + hours
    for no, _, expected in topics:
        assert abs(topic_hours.get(no, 0.0) - expected) < 0.01, (
            f"İçerik {no}: {expected} saat bekleniyordu, {topic_hours.get(no, 0.0)} dağıtıldı"
        )
    for week in WEEK_CONFIG:
        for index in week["components"]:
            assert 0 <= index < len(components), f"Geçersiz süreç bileşeni indeksi: {index}"
        for concept in week["concepts"]:
            assert concept in concepts, f"Anahtar kavram ünite tablosunda yok: {concept}"
        for no, _, _ in week["activities"]:
            assert any(a_no == no for a_no, _ in activities), f"Geçersiz etkinlik numarası: {no}"


# --- Üretim -------------------------------------------------------------------


def render_week(
    week: dict,
    year_week: int,
    monday: date,
    friday: date,
    holidays: list[str],
    components: list[str],
    concepts: list[str],
    topics: list[tuple[int, str, float]],
    activities: list[tuple[int, str]],
) -> str:
    topic_lookup = {no: title for no, title, _ in topics}
    unit_week = week["unit_week"]
    topic_lines = []
    for no, hours, note in week["topics"]:
        if hours == int(hours):
            display = str(int(hours))
        elif hours == 0.5:
            display = "0,5"
        else:
            display = str(hours).replace(".", ",")
        topic_lines.append("- İçerik {}: {} ({} saat — {})".format(no, topic_lookup[no], display, note))
    component_lines = ["- " + components[i] for i in week["components"]]
    activity_lookup = dict(activities)
    activity_lines = [
        "- Etkinlik {}: {} ({} dk — {})".format(no, activity_lookup[no], minutes, note)
        for no, minutes, note in week["activities"]
    ]
    lesson_blocks = []
    for lesson in week["lessons"]:
        steps = "\n".join("{}. {}".format(i, step) for i, step in enumerate(lesson["steps"], start=1))
        lesson_blocks.append("### {}\n\n{}".format(lesson["title"], steps))
    lessons = "\n\n".join(lesson_blocks)
    date_note = format_range(monday, friday)
    if holidays:
        date_note += " — bu hafta resmî tatil: " + ", ".join(holidays)
    differentiation = "\n".join("- " + item for item in week["differentiation"])
    concepts_line = ", ".join("**{}**".format(c) for c in week["concepts"])
    topic_block = "\n".join(topic_lines)
    component_block = "\n".join(component_lines)
    activity_block = "\n".join(activity_lines)
    week_skill = week["skill"]
    week_tendencies = week["tendencies"]
    week_methods = week["methods"]
    week_tools = week["tools"]
    week_assessment = week["assessment"]

    return f"""# Haftalık Ders Planı — 10. Sınıf Felsefe, {UNIT_NO}. Ünite: {UNIT_TITLE}, {unit_week}. Hafta

> Bu plan `tools/uret_plan.py` tarafından üretilmiştir ve [ünite materyali](../{UNIT_FILE}) ile birlikte okunur. Etkinlik ayrıntıları, rubrikler ve ölçme araçları ünite dosyasındadır.

## 1. Ders Kimliği

| Alan | Değer |
|---|---|
| **Ders / Sınıf** | Felsefe / 10. Sınıf |
| **Ünite** | {UNIT_NO}. Ünite: {UNIT_TITLE} (`{UNIT_CODE}`) |
| **Yılın haftası / Ünitenin haftası** | {year_week}. hafta / {unit_week}. hafta |
| **Tahmini tarih** | {date_note} (okul takvimine göre değişebilir) |
| **Süre** | 2 ders saati |
| **Öğrenme çıktısı** | `{OUTCOME_CODE}` — {OUTCOME_TEXT} |
| **Alan becerisi** | {week_skill} |
| **Eğilimler** | {week_tendencies} |

### Bu haftanın içeriği

{topic_block}

### Bu haftanın süreç bileşenleri

{component_block}

### Bu haftanın anahtar kavramları

{concepts_line}

## 2. Öğretme-Öğrenme Akışı

{lessons}

### Bu haftanın etkinlikleri

{activity_block}

**Yöntem ve teknikler:** {week_methods}

**Araç-gereç:** {week_tools}

## 3. Ölçme ve Değerlendirme (Süreç Odaklı)

{week_assessment}

Değerlendirme formları: [ortak değerlendirme formları](../../ortak-materyaller/degerlendirme-formlari.md).

## 4. Farklılaştırma

{differentiation}

## 5. Kaynak ve Materyal Bağlantıları

- [Ünite materyali: {UNIT_NO}. {UNIT_TITLE}](../{UNIT_FILE})
- [Çalışma kâğıdı ve cevap anahtarı](../calisma-kagitlari/01-felsefenin-dogasi-ck.md)
- MEB Felsefe Dersi Öğretim Programı (2026): resmî öğrenme çıktısı ve süreç bileşenleri bu programdan alınmıştır.
"""


def build() -> dict[Path, str]:
    text = UNIT_PATH.read_text(encoding="utf-8")
    components, concepts, topics, activities = parse_unit(text)
    validate_config(components, concepts, topics, activities)
    weeks = teaching_weeks()
    produced: dict[Path, str] = {}
    for week in WEEK_CONFIG:
        year_week, monday, friday, holidays = weeks[week["year_week"] - 1]
        unit_slug = Path(UNIT_FILE).stem.partition("-")[2]
        name = "hafta-{:02d}-{}.md".format(week["unit_week"], unit_slug)
        produced[OUTPUT_DIR / name] = render_week(
            week, year_week, monday, friday, holidays, components, concepts, topics, activities
        )
    return produced


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="yalnızca denetle, dosya yazma")
    args = parser.parse_args()

    produced = build()
    stale = [
        str(path.relative_to(ROOT))
        for path, content in sorted(produced.items())
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]

    if args.check:
        if stale:
            print("Haftalık planlar güncel değil. Şu dosyalar üretimle uyuşmuyor:")
            for item in stale:
                print(f"- {item}")
            print("\nYeniden üretmek için: python tools/uret_plan.py")
            return 1
        print(f"Haftalık planlar güncel: {len(produced)} dosya üretimle birebir aynı.")
        return 0

    for path, content in produced.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"{len(produced)} haftalık plan üretildi: {OUTPUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
