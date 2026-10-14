#!/usr/bin/env python3
"""Resmî Felsefe Dersi Öğretim Programı'ndan makine denetlenebilir özet üretir.

Araç, MEB'in yayımladığı program PDF'sini okuyup ünite/çıktı/süre tablosunu
`mufredat/program-2026-ozet.json` dosyasına yazar. Böylece materyallerin
uyumu elle yazılmış bir listeye değil, resmî programa dayanır.

Kullanım:
    python tools/program-ozeti-uret.py                 # kayıtlı bağlantıdan indirir
    python tools/program-ozeti-uret.py /tmp/prog.pdf   # yerel PDF'yi kullanır

Gereksinim: `pdftotext` (poppler-utils). Betik denetim sırasında çalışmaz;
PDF'den özet üretildikten sonra JSON depoda durur.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "mufredat" / "program-2026-ozet.json"

SOURCE = {
    "title": "Felsefe Dersi Öğretim Programı (10 ve 11. Sınıflar)",
    "year": 2026,
    "publisher": "Millî Eğitim Bakanlığı, Türkiye Yüzyılı Maarif Modeli",
    "url": "https://tymm.meb.gov.tr/assets/pdf/felsefe-dersi_20260819_142831_736.pdf",
    "sha256": "26ada7a42aea65c5e2b1155a0b49c4fbf9d2fa30a59df46bfeeeaaf4cbb8b55f",
    "pageCount": 76,
    "landmarks": {"unitTable": "1.3. bölüm, sayfa 9", "units": "2. bölüm"},
}
LOWER_CASE_WORDS = {"VE", "İLE", "DE", "DA", "IÇİN", "YA", "VEYA"}
UNIT_ROW = re.compile(
    r"^\s*(?P<no>\d{1,2})\.\s+(?P<title>[A-ZÇĞİÖŞÜ0-9 ,'’()/\-*]+?)\s{2,}"
    r"(?P<count>\d+|-)\s+(?P<hours>\d+)\s+(?P<percent>\d+)\s*$"
)
SCHOOL_ROW = re.compile(
    r"^\s*OKUL\s+TEMELL[İI]\s+PLANLAMA\*?\s+(?P<count>\d+|-)\s+(?P<hours>\d+)\s+(?P<percent>\d+)\s*$"
)
OUTCOME_VERB = re.compile(r"(?:ebilme|abilme|edebilme|ebilir|abilir|edebilir)$", re.IGNORECASE)
OUTCOME = re.compile(r"FEL\.(?P<grade>10|11)\.(?P<unit>\d+)\.(?P<no>\d+)\.\s*(?P<text>[A-ZÇĞİÖŞÜa-zçğıöşü][^\n]*)")


def turkish_lower(value: str) -> str:
    """Python'un varsayılan lower() işlevi 'İ' harfini 'i̇' yapıyor; Türkçede 'i' olmalı."""
    return value.replace("İ", "i").replace("I", "ı").lower()


def turkish_upper(value: str) -> str:
    return value.replace("i", "İ").replace("ı", "I").upper()


def turkish_title(value: str) -> str:
    words: list[str] = []
    for word in value.strip().split():
        if word in LOWER_CASE_WORDS:
            words.append({"VE": "ve", "İLE": "ile", "DE": "de", "DA": "da", "IÇİN": "için", "YA": "ya", "VEYA": "veya"}[word])
            continue
        lowered = turkish_lower(word)
        words.append(turkish_upper(lowered[:1]) + lowered[1:])
    return " ".join(words)


def normalize_outcome(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip().rstrip(".")
    return text[:1].upper() + text[1:]


def pdf_text(pdf: Path) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        txt = Path(tmp) / "program.txt"
        subprocess.run(
            ["pdftotext", "-layout", str(pdf), str(txt)],
            check=True,
            capture_output=True,
        )
        return txt.read_text(encoding="utf-8", errors="ignore")


def parse(text: str) -> dict:
    units: dict[str, list[dict]] = {"10": [], "11": []}
    school_based: dict[str, dict] = {}
    grade = None

    for line in text.splitlines():
        heading = re.search(r"(10|11)\. SINIF FELSEFE DERSİ", line)
        if heading:
            grade = heading.group(1)
            continue
        if "OKUL TEMELLİ PLANLAMA" in line or "OKUL TEMELLI PLANLAMA" in line:
            row = SCHOOL_ROW.match(line)
            if row and grade:
                school_based[grade] = {"hours": int(row["hours"]), "percent": int(row["percent"])}
            continue
        if line.strip().startswith("TOPLAM") or not grade:
            continue
        row = UNIT_ROW.match(line)
        if row:
            units[grade].append(
                {
                    "no": int(row["no"]),
                    "code": f"FEL.{grade}.{int(row['no'])}",
                    "title": turkish_title(row["title"]),
                    "hours": int(row["hours"]),
                    "percent": int(row["percent"]),
                    "outcomeCount": int(row["count"]) if row["count"].isdigit() else 0,
                }
            )

    # Programda çıktı cümlesi "…bilme/…bilir" eylemiyle biter; sayfa başlığı
    # tekrarı ("FEL.10.2.2." satırı gibi) yanlış aday olur, onları eleriz.
    # Metin PDF'de satıra bölünmüş olabildiği için aday eksikse bir sonraki
    # satır eklenir; "edebil-\nme" gibi tireli kırılmalar birleştirilir.
    lines = text.splitlines()
    candidates: dict[str, list[str]] = {}
    for index, line in enumerate(lines):
        match = OUTCOME.search(line)
        if not match:
            continue
        code = f"FEL.{match['grade']}.{int(match['unit'])}.{int(match['no'])}"
        value = normalize_outcome(match["text"])
        cursor = index
        while value and not OUTCOME_VERB.search(value) and cursor + 1 < len(lines):
            cursor += 1
            following = lines[cursor].strip()
            if not following or OUTCOME.search(lines[cursor]):
                break
            # "edebil-\nme" gibi kırılmalar boşluksuz birleşir.
            hyphenated = bool(re.search(r"\w-\s*$", value))
            value = re.sub(r"(\w)-\s*$", r"\1", value) + ("" if hyphenated else " ") + following
        if value:
            candidates.setdefault(code, []).append(value)

    outcomes: dict[str, str] = {}
    for code, values in candidates.items():
        statements = [value for value in values if OUTCOME_VERB.search(value)]
        outcomes[code] = max(statements or values, key=len).rstrip(" -")

    for grade, rows in units.items():
        for row in rows:
            row["outcomes"] = sorted(
                (code for code in outcomes if code.startswith(f"{row['code']}.")),
                key=lambda code: int(code.rsplit(".", 1)[1]),
            )
            if row["outcomeCount"] and len(row["outcomes"]) != row["outcomeCount"]:
                print(
                    f"UYARI: {row['code']} programda {row['outcomeCount']} çıktı diyor, metinden {len(row['outcomes'])} çıktı okundu.",
                    file=sys.stderr,
                )

    return {
        "schemaVersion": "1.0.0",
        "discipline": "Felsefe",
        "datasetVersion": "2026.1",
        "source": SOURCE,
        "generatedBy": "tools/program-ozeti-uret.py",
        "schoolBasedPlanning": school_based,
        "units": units,
        "outcomes": dict(sorted(outcomes.items())),
    }


def main() -> int:
    if len(sys.argv) > 1:
        pdf = Path(sys.argv[1])
    else:
        request = urllib.request.Request(SOURCE["url"], headers={"User-Agent": "Mozilla/5.0"})
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as handle:
            handle.write(urllib.request.urlopen(request, timeout=60).read())
            pdf = Path(handle.name)

    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest != SOURCE["sha256"]:
        print(
            f"UYARI: PDF özeti beklenen SHA-256 ile eşleşmiyor.\n  beklenen: {SOURCE['sha256']}\n  gelen   : {digest}",
            file=sys.stderr,
        )

    summary = parse(pdf_text(pdf))
    total = {grade: sum(row["hours"] for row in rows) for grade, rows in summary["units"].items()}
    print(
        "10. sınıf: {} ünite, {} ders saati\n11. sınıf: {} ünite, {} ders saati\nçıktı kodu: {}".format(
            len(summary["units"]["10"]),
            total["10"],
            len(summary["units"]["11"]),
            total["11"],
            len(summary["outcomes"]),
        )
    )
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"yazıldı: {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
