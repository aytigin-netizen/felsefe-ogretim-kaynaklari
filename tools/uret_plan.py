#!/usr/bin/env python3
"""Ünite içerik çerçevelerinden TYMM formatında haftalık günlük (ders) planları üretir.

Kullanım:
    python tools/uret_plan.py           # haftalık plan dosyalarını (yeniden) üretir
    python tools/uret_plan.py --check   # depodaki planlar üretimle uyuşuyor mu diye bakar

Plan, MEB "Eğitim ve Öğretim Çalışmalarının Planlı Yürütülmesine Dair Yönerge"
bölümleriyle TYMM günlük plan bileşenlerini (öğrenme çıktısı + süreç bileşenleri,
alan becerisi, eğilim, öğretme-öğrenme akışı, ölçme-değerlendirme, farklılaştırma)
birleştirir. Araç felsefi içerik üretmez: haftalık eşleme kuralı açık ve
deterministiktir ve ünite dosyasındaki resmî verilerle eşleşmezse hata verir.

Eşleme kuralı:
- Her hafta 2 ders saatidir; ünite ders saati / 2 = hafta sayısı.
- Haftanın içeriği, ünite dosyasındaki "N Ders Saati Akışı" tablosundan (varsa)
  veya saatli İçerik Çerçevesi başlıklarından belirlenir.
- Etkinlikler, ünite dosyasındaki sırayla ve süreleriyle orantılı olarak
  haftalara dağıtılır (haftalık öğretim süresi 80 dk kabul edilir).
- İzlenebilirlik matrisi satırları, satırda anılan etkinliklerin düştüğü
  haftaya puan ve kanıt bilgisiyle yerleştirilir.
- 10. sınıf 1. ünite pilotu onaylanmış el yapımı haftalık eşlemeyi (WEEK_CONFIG)
  kullanır; kalan üniteler yukarıdaki kurala göre otomatik üretilir.
- Okul temelli planlama (4 saat = 2 hafta) her sınıf düzeyinde ayrı üretilir.

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

WEEK_MINUTES = 80          # 2 ders saati
HAND_UNIT = ("10-sinif", "01-felsefenin-dogasi.md")   # onaylanmış pilot

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


# --- Ünite dosyası ayrıştırma --------------------------------------------------

def section(text: str, start_pattern: str, stop_pattern: str = r"^##\s+") -> str:
    """`start_pattern` ile başlayan bölümün metnini bir sonraki ## başlığına kadar döndürür."""
    match = re.search(start_pattern, text, flags=re.MULTILINE)
    if not match:
        return ""
    remainder = text[match.end():]
    stop = re.search(stop_pattern, remainder, flags=re.MULTILINE)
    return remainder[:stop.start()] if stop else remainder


def parse_flow(text: str, hours: int) -> list[str] | None:
    """"N Ders Saati Akışı" tablosundan ders saati başına odak metni çıkarır."""
    block = section(text, r"^##\s+.*Ders Saati Akışı")
    if not block:
        return None
    focuses: dict[int, str] = {}
    for raw in re.findall(r"^\|\s*(\d+)\s*(?:[–-]\s*(\d+))?\s*\|(.*?)\|", block, flags=re.MULTILINE):
        start = int(raw[0])
        end = int(raw[1]) if raw[1] else start
        focus = raw[2].strip()
        for slot in range(start, end + 1):
            focuses[slot] = focus
    if len(focuses) != hours or any(not focuses.get(i, "").strip() for i in range(1, hours + 1)):
        return None
    return [focuses[i] for i in range(1, hours + 1)]


def parse_topics(text: str) -> list[tuple[int, str, float | None]]:
    """İçerik Çerçevesi bölümündeki (no, başlık, saat) başlıklarını döndürür."""
    block = section(text, r"^##\s+İçerik Çerçevesi")
    topics: list[tuple[int, str, float | None]] = []
    for no, title, hours in re.findall(
        r"^###\s+(\d+)\.\s+(.+?)(?:\s+\((\d+(?:,\d+)?)\s+saat\))?\s*$",
        block,
        flags=re.MULTILINE,
    ):
        parsed = float(hours.replace(",", ".")) if hours else None
        topics.append((int(no), title.strip(), parsed))
    return topics


def parse_activities(text: str) -> list[tuple[int, str, int]]:
    """(etkinlik no, ad, dakika) listesi; süre bulunamazsa 40 dk kabul edilir."""
    activities: list[tuple[int, str, int]] = []
    for match in re.finditer(r"^###\s+Etkinlik\s+(\d+):\s*(.+)$", text, flags=re.MULTILINE):
        no = int(match.group(1))
        name = match.group(2).strip()
        following = text[match.end():match.end() + 600]
        duration = re.search(r"S[üu]re:\*\*\s*(\d+)", following)
        activities.append((no, name, int(duration.group(1)) if duration else 40))
    return activities


def parse_components(text: str, outcome_codes: list[str]) -> list[tuple[str, str]]:
    """Her öğrenme çıktısının süreç bileşenlerini (çıktı kodu, bileşen) olarak döndürür."""
    components: list[tuple[str, str]] = []
    # Başlangıç noktaları: "### FEL.10.2.1 — ..." veya "**FEL.10.2.1 — ...:**" biçimleri.
    starts: list[tuple[int, str]] = []
    for code in outcome_codes:
        for match in re.finditer(
            r"(?:^###|^\*\*)\s*" + re.escape(code) + r"\s+—",
            text,
            flags=re.MULTILINE,
        ):
            starts.append((match.start(), code))
    starts.sort()
    for index, (position, code) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else len(text)
        heading = re.search(r"^##\s+", text[position:end], flags=re.MULTILINE)
        if heading:
            end = position + heading.start()
        block = text[position:end]
        block = re.sub(
            r"^\*\*\s*" + re.escape(code) + r"[^:]*:\*\*\s*",
            "", block, count=1, flags=re.MULTILINE,
        )
        bullets = [line[2:].strip() for line in block.splitlines() if line.startswith("- ")]
        if bullets:
            components.extend((code, bullet) for bullet in bullets)
            continue
        paragraph = " ".join(line.strip() for line in block.splitlines() if line.strip())
        paragraph = re.sub(r"Öğrenciler(\s+\w+)?\s*", "", paragraph, count=1)
        parts = [part.strip(" .;") for part in paragraph.split(";") if part.strip(" .;")]
        for part in parts:
            part = re.sub(r"\[\d+\]$", "", part).strip()
            part = re.sub(r"^\*\*|\*\*$", "", part).strip()
            if part and not part.lower().startswith("bu ünite"):
                components.append((code, part))
    return components


def parse_concepts(text: str) -> list[str]:
    block = section(text, r"^##\s+Anahtar Kavramlar")
    concepts = re.findall(r"^\|\s*\*\*(.+?)\*\*\s*\|", block, flags=re.MULTILINE)
    if not concepts:
        # "Anahtar Kavramlar" bölümü yoksa Felsefi Çekirdek içindeki "Kavram" tablosu kullanılır.
        block = section(text, r"^##\s+Felsefi Çekirdek")
        if re.search(r"^\|\s*Kavram\s*\|", block, flags=re.MULTILINE):
            concepts = re.findall(r"^\|\s*\*\*(.+?)\*\*\s*\|", block, flags=re.MULTILINE)
    return concepts


def parse_matrix(text: str) -> list[dict]:
    """İzlenebilirlik matrisi satırlarını sözlük olarak döndürür."""
    block = section(text, r"^###\s+İzlenebilirlik Matrisi", stop_pattern=r"^###\s+")
    rows: list[dict] = []
    for line in block.splitlines():
        if not line.strip().startswith("|") or "Resmî çıktı" in line or set(line.strip()) <= {"|", "-", " ", ":"}:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        rows.append({
            "component": cells[0],
            "activities": [int(n) for n in re.findall(r"Etkinlik\s+(\d+)", cells[1])],
            "activity_label": cells[1],
            "product": cells[2],
            "tool": cells[3],
            "rubric": cells[4],
            "points": cells[5],
        })
    return rows


def parse_bold_component_line(text: str, *labels: str) -> str:
    for label in labels:
        match = re.search(r"\*\*" + label + r":?\*\*\s*\|?\s*(.+)", text)
        if match:
            value = match.group(1).strip().strip("|").strip()
            if value:
                return value
    return "ünite dosyasındaki Alan Becerileri ve Süreç Bileşenleri bölümü"


def parse_first_bullet(text: str, heading: str, fallback: str) -> str:
    block = section(text, r"^###\s+" + heading, stop_pattern=r"^###\s+")
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return stripped[2:].strip()
    return fallback


# --- El yapımı haftalık eşleme: 10. sınıf 1. ünite (onaylanmış pilot) ----------

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


# --- Otomatik haftalık eşleme: kalan üniteler -----------------------------------


def distribute(total: int, buckets: int) -> list[int]:
    """`total` öğeyi `buckets` kovaya olabildiğince eşit dağıtır (önden yüklenen)."""
    if buckets <= 0:
        return []
    base, extra = divmod(total, buckets)
    return [base + (1 if i < extra else 0) for i in range(buckets)]


def assign_activities(activities: list[tuple[int, str, int]], week_count: int) -> list[list[tuple[int, str, int]]]:
    """Etkinlikleri, sürelerinin Oranına göre haftalara sırayla dağıtır."""
    assignment: list[list[tuple[int, str, int]]] = [[] for _ in range(week_count)]
    cumulative = 0
    for activity in activities:
        midpoint = cumulative + activity[2] / 2
        index = min(int(midpoint // WEEK_MINUTES), week_count - 1)
        assignment[index].append(activity)
        cumulative += activity[2]
    return assignment


def chunk_topics(
    topics: list[tuple[int, str, float | None]],
    flow: list[str] | None,
    week_count: int,
) -> list[list[tuple[int, str, float | None]]]:
    """Konuları haftalara dağıtır; saat bilgisi varsa saatle, yoksa eşit ağırlıkla."""
    if flow is not None:
        # Akış tablosu hafta içeriğini zaten belirliyorsa konu başlıkları yalız bilgilendirme amaçlıdır.
        # Konuları, akıştaki hafta sayısıyla orantılı dağıt.
        counts = distribute(len(topics), week_count) if topics else [0] * week_count
    elif all(hours is not None for _, _, hours in topics):
        # Saat bazlı ardışık doldurma
        result: list[list[tuple[int, str, float | None]]] = [[] for _ in range(week_count)]
        queue = list(topics)
        for w in range(week_count):
            capacity = 2.0
            while queue and capacity > 0:
                no, title, hours = queue[0]
                take = min(hours, capacity)
                result[w].append((no, title, take))
                capacity -= take
                if take >= hours - 1e-9:
                    queue.pop(0)
                else:
                    queue[0] = (no, title, hours - take)
        return result
    else:
        counts = distribute(len(topics), week_count) if topics else [0] * week_count
    result = [[] for _ in range(week_count)]
    index = 0
    for w, count in enumerate(counts):
        for _ in range(count):
            if index < len(topics):
                result[w].append(topics[index])
                index += 1
    # Dağıtılamayan konular son haftaya eklenir
    while index < len(topics):
        result[-1].append(topics[index])
        index += 1
    return result


def render_auto_week(
    grade_num: str,
    unit: dict,
    week_index: int,
    week_count: int,
    year_week: int,
    monday: date,
    friday: date,
    holidays: list[str],
    week_topics: list[tuple[int, str, float | None]],
    week_flow: list[str],
    week_activities: list[tuple[int, str, int]],
    week_components: list[tuple[str, str]],
    week_concepts: list[str],
    week_matrix: list[dict],
    skill_line: str,
    tendencies_line: str,
    enrichment: str,
    support: str,
    unit_file: str,
    ck_file: str,
) -> str:
    unit_week = week_index + 1
    unit_no = unit["no"]
    title = unit["title"]
    code = unit["code"]
    outcome_lines = "; ".join(
        "`{}` — {}".format(oc, PROGRAM["outcomes"][oc]) for oc in unit["outcomes"]
    )
    if week_flow:
        topic_lines = [
            "- Ders saati {}: {}".format(unit_week * 2 - 1, week_flow[0]),
            "- Ders saati {}: {}".format(unit_week * 2, week_flow[1]),
        ]
    else:
        topic_lines = []
        for no, name, hours in week_topics:
            if hours is None:
                topic_lines.append("- İçerik {}: {}".format(no, name))
            elif hours == int(hours):
                topic_lines.append("- İçerik {}: {} ({} saat)".format(no, name, int(hours)))
            else:
                topic_lines.append("- İçerik {}: {} ({} saat)".format(no, name, str(hours).replace(".", ",")))
    component_lines = ["`{}` — {}".format(oc, text) for oc, text in week_components]
    component_block = "\n".join("- " + c for c in component_lines) or "- (Bu haftaya özgü süreç bileşeni ünite akışıyla belirlenir)"
    concepts_line = ", ".join("**{}**".format(c) for c in week_concepts) or "Ünite dosyasındaki Anahtar Kavramlar tablosu"

    # Etkinlikleri iki ders saatine dakika oranıyla böl
    total_minutes = sum(a[2] for a in week_activities) or WEEK_MINUTES
    first_lesson: list[tuple[int, str, int]] = []
    second_lesson: list[tuple[int, str, int]] = []
    cumulative = 0
    for activity in week_activities:
        if cumulative < total_minutes / 2 or not first_lesson:
            first_lesson.append(activity)
        else:
            second_lesson.append(activity)
        cumulative += activity[2]
    if not second_lesson:
        second_lesson = first_lesson[len(first_lesson) // 2:] or []
        first_lesson = first_lesson[: len(first_lesson) // 2] or first_lesson

    def activity_step(activity: tuple[int, str, int]) -> str:
        return "Etkinlik {}: {} ({} dk) — ünite dosyasındaki adımlar uygulanır; belirtilen ürün toplanır.".format(
            activity[0], activity[1], activity[2]
        )

    first_steps = []
    if week_index == 0:
        first_steps.append(
            "Güdüleme ve ön değerlendirme (≈10 dk): ünite dosyasındaki açılış/köprü kurma önerisi uygulanır; öğrencilerin ön kavramları notlandırılmadan açığa çıkarılır."
        )
    focus = "; ".join(dict.fromkeys([name for _, name, _ in week_topics])) or "; ".join(week_flow)
    first_steps.append("Kısa anlatım (≈15 dk): {} (ünite dosyası: İçerik Çerçevesi ve ilgili bölüm).".format(focus))
    for activity in first_lesson:
        first_steps.append(activity_step(activity))

    second_steps = [activity_step(activity) for activity in second_lesson]
    second_steps.append(
        "Kapanış (≈5 dk): haftanın öğrenme kanıtları tek cümleyle özetlenir ve gelecek haftanın içeriğine köprü kurulur."
    )

    is_last = week_index == week_count - 1
    lessons = "### 1. ders saati — {}\n\n{}\n\n### 2. ders saati — {}\n\n{}".format(
        "Keşfetme" if week_index == 0 else "Keşfetme ve uygulama",
        "\n".join("{}. {}".format(i, s) for i, s in enumerate(first_steps, start=1)),
        "Derinleştirme" + (" ve performans görevi" if is_last else ""),
        "\n".join("{}. {}".format(i, s) for i, s in enumerate(second_steps, start=1)),
    )

    activity_block = "\n".join(
        "- Etkinlik {}: {} ({} dk)".format(no, name, minutes) for no, name, minutes in week_activities
    ) or "- Bu haftada ünite dosyasındaki sonraki etkinliğe hazırlık ve dönüt çalışması yapılır."

    matrix_lines = []
    for row in week_matrix:
        matrix_lines.append(
            "- {} — kanıt: {} ({}; {})".format(
                row["component"].strip("`"), row["product"], row["activity_label"], row["points"]
            )
        )
    if matrix_lines:
        assessment = (
            "Bu haftanın öğrenme kanıtları, ünitenin izlenebilirlik matrisinde şu satırların girdisidir:\n\n"
            + "\n".join(matrix_lines)
            + "\n\nRubrik ölçütleri ve puanlama ayrıntıları ünite dosyasındaki Dereceli Puanlama Anahtarı bölümündedir."
        )
    else:
        assessment = (
            "Bu haftada toplanan ürünler, ünitenin izlenebilirlik matrisindeki ilgili satırların öğrenme kanıtı girdisidir; "
            "ölçme aracı ve rubrik ölçütleri ünite dosyasındadır."
        )

    date_note = format_range(monday, friday)
    if holidays:
        date_note += " — bu hafta resmî tatil: " + ", ".join(holidays)
    differentiation = "- Zenginleştirme: {}\n- Destekleme: {}".format(enrichment, support)

    return f"""# Haftalık Ders Planı — {grade_num}. Sınıf Felsefe, {unit_no}. Ünite: {title}, {unit_week}. Hafta

> Bu plan `tools/uret_plan.py` tarafından üretilmiştir ve [ünite materyali](../{unit_file}) ile birlikte okunur. Etkinlik ayrıntıları, rubrikler ve ölçme araçları ünite dosyasındadır.

## 1. Ders Kimliği

| Alan | Değer |
|---|---|
| **Ders / Sınıf** | Felsefe / {grade_num}. Sınıf |
| **Ünite** | {unit_no}. Ünite: {title} (`{code}`) |
| **Yılın haftası / Ünitenin haftası** | {year_week}. hafta / {unit_week}. hafta |
| **Tahmini tarih** | {date_note} (okul takvimine göre değişebilir) |
| **Süre** | 2 ders saati |
| **Öğrenme çıktısı** | {outcome_lines} |
| **Alan becerisi** | {skill_line} |
| **Eğilimler** | {tendencies_line} |

### Bu haftanın içeriği

{chr(10).join(topic_lines) or "Ünite dosyasındaki İçerik Çerçevesi bu haftanın kapsamını belirler."}

### Bu haftanın süreç bileşenleri

{component_block}

### Bu haftanın anahtar kavramları

{concepts_line}

## 2. Öğretme-Öğrenme Akışı

{lessons}

### Bu haftanın etkinlikleri

{activity_block}

**Yöntem ve teknikler:** Ünite dosyasındaki etkinlik tanımlarında belirtilen yöntem ve teknikler (iş birlikli çalışma, tartışma, bireysel yazım, karşılaştırma tablosu vb.) uygulanır.

**Araç-gereç:** Ünite dosyasındaki etkinlik materyalleri ve [çalışma kâğıdı](../calisma-kagitlari/{ck_file}).

## 3. Ölçme ve Değerlendirme (Süreç Odaklı)

{assessment}

Değerlendirme formları: [ortak değerlendirme formları](../../ortak-materyaller/degerlendirme-formlari.md).

## 4. Farklılaştırma

{differentiation}

## 5. Kaynak ve Materyal Bağlantıları

- [Ünite materyali: {unit_no}. {title}](../{unit_file})
- [Çalışma kâğıdı ve cevap anahtarı](../calisma-kagitlari/{ck_file})
- MEB Felsefe Dersi Öğretim Programı (2026): resmî öğrenme çıktısı ve süreç bileşenleri bu programdan alınmıştır.
"""


def render_school_week(
    grade_num: str,
    week_index: int,
    year_week: int,
    monday: date,
    friday: date,
    holidays: list[str],
) -> str:
    unit_week = week_index + 1
    date_note = format_range(monday, friday)
    if holidays:
        date_note += " — bu hafta resmî tatil: " + ", ".join(holidays)
    if week_index == 0:
        content = [
            "- 1. ders saati: Yerel çalışma / gözlem — okulun, mahallenin veya çevrenin bir felsefi sorununu gözlemleme",
            "- 2. ders saati: Okuma çalışması — seçilmiş bir felsefe metnini okuma ve notlandırma",
        ]
        steps1 = "Yerel çalışma kapsamında öğrenciler çevrelerinde gözlemleyebilecekleri bir kural, uygulama veya sorunu seçer (ör. okul kuralının meşruiyeti); gözlem notu tutar."
        steps2 = "Seçilmiş kısa felsefe metni sınıfta okunur; öğrenciler metne ilişkin notlarını okuma çalışması dosyasına işler."
        assessment = "Gözlem notu ve okuma çalışması dosyası toplanır; bu çalışmalar ayrı puanlanmaz, kanıtlar okul temelli planlama dosyasındaki esasa göre işlenir."
    else:
        content = [
            "- 1. ders saati: Proje / araştırma — öğrencinin seçtiği bir felsefi problemi kısa bir araştırmayla belgeleme",
            "- 2. ders saati: Kariyer rehberliği — felsefe alanının hangi mesleklere açıldığının birlikte konuşulması",
        ]
        steps1 = "Öğrenciler seçtikleri felsefi problem için kısa bir araştırma planı yapar; kaynak notu ve araştırma özeti hazırlar."
        steps2 = "Felsefe alanının açtığı meslekler ve kariyer yolları sınıfta birlikte tartışılır; öğrencinin mesleki rehberlik dosyasına işlenecek görüşmeler planlanır."
        assessment = "Araştırma özeti ve kariyer görüşme planı toplanır; çalışmalar ayrı puanlanmaz, öğrencinin rehberlik dosyasına işlenir."

    return f"""# Haftalık Ders Planı — {grade_num}. Sınıf Felsefe, Okul Temelli Planlama, {unit_week}. Hafta

> Bu plan `tools/uret_plan.py` tarafından üretilmiştir ve [okul temelli planlama materyali](../../okul-temelli-planlama.md) ile birlikte okunur.

## 1. Ders Kimliği

| Alan | Değer |
|---|---|
| **Ders / Sınıf** | Felsefe / {grade_num}. Sınıf |
| **Bölüm** | Okul Temelli Planlama (4 ders saati, programın %{'5' if grade_num == '10' else '6'} oranı) |
| **Yılın haftası / Bölümün haftası** | {year_week}. hafta / {unit_week}. hafta |
| **Tahmini tarih** | {date_note} (okul takvimine göre değişebilir) |
| **Süre** | 2 ders saati |
| **Not** | Bu bölüm ünite materyali değildir; öğrenme çıktısı kodu taşımaz. Zümre kararı ve okul yıllık planı esastır. |

### Bu haftanın içeriği

{chr(10).join(content)}

## 2. Öğretme-Öğrenme Akışı

### 1. ders saati

1. {steps1}

### 2. ders saati

1. {steps2}

2. Kapanış (≈5 dk): haftanın çalışmaları özetlenir ve sonraki okul temelli haftaya köprü kurulur.

**Yöntem ve teknikler:** Gözlem, iş birlikli tartışma, bireysel araştırma, rehberlik görüşmesi.

**Araç-gereç:** Gözlem/okuma formu, araştırma notu şablonu; formlar: [ortak değerlendirme formları](../../ortak-materyaller/degerlendirme-formlari.md).

## 3. Ölçme ve Değerlendirme

{assessment}

## 4. Farklılaştırma

- Zenginleştirme: gözlem ya da araştırma konusunu felsefi bir soruya dönüştürüp kısa sunum yapma.
- Destekleme: görsel bilgi kartları ve yapılandırılmış gözlem şablonu; akran destekli okuma.

## 5. Kaynak ve Materyal Bağlantıları

- [Okul temelli planlama materyali](../../okul-temelli-planlama.md)
- MEB Felsefe Dersi Öğretim Programı (2026), 1.3 bölümü: okul temelli planlama tanımı.
"""


def build() -> dict[Path, str]:
    produced: dict[Path, str] = {}
    weeks = teaching_weeks()

    # --- El yapımı pilot: 10. sınıf 1. ünite ---------------------------------
    text = UNIT_PATH.read_text(encoding="utf-8")
    components, concepts, topics, activities = parse_unit(text)
    validate_config(components, concepts, topics, activities)
    unit_slug = Path(UNIT_FILE).stem.partition("-")[2]
    for week in WEEK_CONFIG:
        year_week, monday, friday, holidays = weeks[week["year_week"] - 1]
        name = "hafta-{:02d}-{}.md".format(week["unit_week"], unit_slug)
        produced[OUTPUT_DIR / name] = render_week(
            week, year_week, monday, friday, holidays, components, concepts, topics, activities
        )

    # --- Otomatik üniteler ------------------------------------------------------
    for grade_dir, grade_num in (("10-sinif", "10"), ("11-sinif", "11")):
        unit_metas = PROGRAM["units"][grade_num]
        assert sum(u["hours"] for u in unit_metas) == 68, f"{grade_num}. sınıf ünite saatleri 68 değil"
        year_week_cursor = 1
        for meta in unit_metas:
            unit_file = sorted((MUFREDAT / grade_dir).glob("{:02d}-*.md".format(meta["no"])))[0].name
            if (grade_dir, unit_file) == HAND_UNIT:
                year_week_cursor += meta["hours"] // 2
                continue
            hours = meta["hours"]
            assert hours % 2 == 0, f"{unit_file}: ders saati çift değil"
            week_count = hours // 2
            unit_text = (MUFREDAT / grade_dir / unit_file).read_text(encoding="utf-8")

            flow = parse_flow(unit_text, hours)
            topics_auto = parse_topics(unit_text)
            if flow is None and topics_auto:
                hours_sum = sum(h for _, _, h in topics_auto if h is not None)
                if hours_sum and abs(hours_sum - hours) > 0.01:
                    topics_auto = [(no, name, None) for no, name, _ in topics_auto]
            activities_auto = parse_activities(unit_text)
            components_auto = parse_components(unit_text, meta["outcomes"])
            concepts_auto = parse_concepts(unit_text)
            matrix = parse_matrix(unit_text)
            skill_line = parse_bold_component_line(unit_text, "Alan becerileri", "Alan becerisi")
            tendencies_line = parse_bold_component_line(unit_text, "Eğilimler")
            enrichment = parse_first_bullet(unit_text, "Zenginleştirme", "ünite dosyasındaki Farklılaştırma bölümündeki ileri öğrenme önerileri uygulanır")
            support = parse_first_bullet(unit_text, "Destekleme", "ünite dosyasındaki Farklılaştırma bölümündeki destekleme önerileri uygulanır")

            assert components_auto, f"{unit_file}: süreç bileşenleri ayrıştırılamadı"
            assert activities_auto, f"{unit_file}: etkinlikler ayrıştırılamadı"
            assert matrix, f"{unit_file}: izlenebilirlik matrisi ayrıştırılamadı"
            assert concepts_auto, f"{unit_file}: anahtar kavramlar ayrıştırılamadı"

            topic_chunks = chunk_topics(topics_auto, flow, week_count)
            flow_chunks = [
                flow[w * 2:w * 2 + 2] if flow else [] for w in range(week_count)
            ]
            activity_chunks = assign_activities(activities_auto, week_count)
            component_counts = distribute(len(components_auto), week_count)
            concept_counts = distribute(len(concepts_auto), week_count)

            # Matris satırlarını etkinlik numarasına göre haftalara yerleştir
            activity_week: dict[int, int] = {}
            for w, chunk in enumerate(activity_chunks):
                for no, _, _ in chunk:
                    activity_week[no] = w
            matrix_chunks: list[list[dict]] = [[] for _ in range(week_count)]
            for row in matrix:
                target = max((activity_week[n] for n in row["activities"] if n in activity_week), default=week_count - 1)
                matrix_chunks[target].append(row)

            component_cursor = 0
            concept_cursor = 0
            unit_slug = Path(unit_file).stem.partition("-")[2]
            ck_candidates = sorted((MUFREDAT / grade_dir / "calisma-kagitlari").glob("{:02d}-*-ck.md".format(meta["no"])))
            assert ck_candidates, f"{unit_file}: çalışma kâğıdı bulunamadı"
            ck_file = ck_candidates[0].name
            for w in range(week_count):
                c_count = component_counts[w]
                k_count = concept_counts[w]
                week_components = components_auto[component_cursor:component_cursor + c_count]
                week_concepts = concepts_auto[concept_cursor:concept_cursor + k_count]
                component_cursor += c_count
                concept_cursor += k_count
                year_week, monday, friday, holidays = weeks[year_week_cursor + w - 1]
                name = "hafta-{:02d}-{}.md".format(w + 1, unit_slug)
                produced[MUFREDAT / grade_dir / "gunluk-planlar" / name] = render_auto_week(
                    grade_num, meta, w, week_count, year_week, monday, friday, holidays,
                    topic_chunks[w], flow_chunks[w], activity_chunks[w],
                    week_components, week_concepts, matrix_chunks[w],
                    skill_line, tendencies_line, enrichment, support,
                    unit_file, ck_file,
                )
            year_week_cursor += week_count

        # --- Okul temelli planlama (4 saat = 2 hafta) --------------------------
        assert year_week_cursor == 35, f"{grade_num}. sınıf: okul temelli haftalar 35'te başlamalı, {year_week_cursor}"
        for w in range(2):
            year_week, monday, friday, holidays = weeks[year_week_cursor + w - 1]
            name = "okul-temelli-hafta-{:02d}.md".format(w + 1)
            produced[MUFREDAT / grade_dir / "gunluk-planlar" / name] = render_school_week(
                grade_num, w, year_week, monday, friday, holidays
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
    print(f"{len(produced)} haftalık plan üretildi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
