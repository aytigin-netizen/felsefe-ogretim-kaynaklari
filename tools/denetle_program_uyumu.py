#!/usr/bin/env python3
"""Materyallerin resmî Felsefe Dersi Öğretim Programı ile uyumunu denetler.

Denetim kaydı `mufredat/program-2026-ozet.json` dosyasıdır; bu kayıt
`tools/program-ozeti-uret.py` aracıyla MEB'in yayımladığı program PDF'sinden
üretilir. Denetim şunları karşılaştırır:

- her ünite dosyasının Ders Saati / Yüzde Oranı / Öğrenme Çıktısı Sayısı değerleri
- materyallerde geçen her FEL öğrenme çıktı kodunun programda var olması
- program yılına ilişkin atıf ve bağlantıların kayıttaki yıl ve bağlantıyla eşleşmesi

Bilinen ve kayıt altına alınmış sapmalar `tools/program-2026-bilinen-ayrismalar.json`
dosyasında tutulur. Liste dışındaki sapma denetimi düşürür; listedeki sapmalar
gürültü değildir, açıkça görünür bir borç kaydıdır ve 2./3. adımlarda kapatılır.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUFREDAT = ROOT / "mufredat"
RECORD = MUFREDAT / "program-2026-ozet.json"
DEVIATIONS = ROOT / "tools" / "program-2026-bilinen-ayrismalar.json"

UNIT_FILE = re.compile(r"^\d\d-")
FIELD = re.compile(r"^\|\s*\*\*(?P<key>[^*|]+)\*\*\s*\|\s*(?P<value>[^|]+?)\s*\|", re.MULTILINE)
OUTCOME_CODE = re.compile(r"FEL\.(?:10|11)\.\d+\.\d+")
YEAR_MENTION = re.compile(r"(?P<year>20\d\d)\s*(?:onaylı|yılı|öğretim programı|programı)", re.IGNORECASE)
# 2024 programına ait, artık erişilemeyen bağlantı kalıpları. Programın ders
# sayfası (tymm.meb.gov.tr/ogretim-programlari/ders/felsefe-dersi) geçerlidir.
DEAD_SOURCE_MARKERS = ("2024programfel1011Onayli", "tymm.meb.gov.tr/upload/program/")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def field(text: str, key: str) -> str | None:
    for match in FIELD.finditer(text):
        if match["key"].strip().lower() == key.lower():
            return match["value"].strip()
    return None


def hours_of(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def percent_of(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"(\d+)\s*%", value)
    return int(match.group(1)) if match else None


def count_of(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def material_files() -> list[Path]:
    files = [p for p in sorted(MUFREDAT.rglob("*.md")) if p.name != "template.md"]
    return files + sorted((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]


def validate_record(record: dict, errors: list[str]) -> None:
    """Kaydın kendisi programla tutarlı mı: saat ve yüzde toplamları 72 / 100 olmalı."""
    for grade, rows in record["units"].items():
        hours = sum(row["hours"] for row in rows) + record["schoolBasedPlanning"][grade]["hours"]
        percent = sum(row["percent"] for row in rows) + record["schoolBasedPlanning"][grade]["percent"]
        if hours != 72:
            errors.append(f"program kaydı: {grade}. sınıf toplamı {hours} saat, 72 olmalı")
        if percent != 100:
            errors.append(f"program kaydı: {grade}. sınıf toplamı %{percent}, %100 olmalı")
        for row in rows:
            if len(row["outcomes"]) != row["outcomeCount"]:
                errors.append(
                    f"program kaydı: {row['code']} {row['outcomeCount']} çıktı diyor, {len(row['outcomes'])} kod var"
                )


def validate_units(record: dict, findings: list[str]) -> None:
    known_codes = set(record["outcomes"])
    by_unit = {row["code"]: row for rows in record["units"].values() for row in rows}

    for grade, rows in record["units"].items():
        for row in rows:
            # Ünite dosya adı sıfır doldurulmuş numarayla başlar (01-felsefenin-dogasi.md)
            prefix = f"{int(row['code'].split('.')[2]):02d}"
            unit_files = sorted(
                p
                for p in (MUFREDAT / f"{grade}-sinif").glob("*.md")
                if UNIT_FILE.match(p.name) and p.name.startswith(f"{prefix}-")
            )
            if not unit_files:
                continue
            path = unit_files[0]
            label = str(path.relative_to(ROOT))
            text = path.read_text(encoding="utf-8")

            hours = hours_of(field(text, "Ders Saati"))
            if hours is not None and hours != row["hours"]:
                findings.append(f"{label}: ders saati {hours}, programda {row['hours']}")

            percent = percent_of(field(text, "Yüzde Oranı (%)"))
            if percent is not None and percent != row["percent"]:
                findings.append(f"{label}: yüzde oranı %{percent}, programda %{row['percent']}")

            count = count_of(field(text, "Öğrenme Çıktısı Sayısı"))
            if count is not None and count != row["outcomeCount"]:
                findings.append(
                    f"{label}: öğrenme çıktısı sayısı {count}, programda {row['outcomeCount']}"
                )

            declared = {code for code in OUTCOME_CODE.findall(text) if code.startswith(row["code"] + ".")}
            for code in sorted(declared - set(row["outcomes"])):
                findings.append(f"{label}: {code} kodu programda yok (program çıktıları: {', '.join(row['outcomes'])})")
            for code in sorted(set(row["outcomes"]) - declared):
                findings.append(f"{label}: programın {code} çıktısı materyalde geçmiyor")

    for path in material_files():
        text = path.read_text(encoding="utf-8")
        for code in sorted(set(OUTCOME_CODE.findall(text)) - known_codes):
            findings.append(f"{str(path.relative_to(ROOT))}: {code} kodu programda tanımlı değil")


def validate_citation(record: dict, findings: list[str]) -> None:
    year = str(record["source"]["year"])
    for path in material_files():
        label = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        problems: list[str] = []
        years = {match["year"] for match in YEAR_MENTION.finditer(text)} - {year}
        if years:
            problems.append(f"program yılı {'/'.join(sorted(years))} yazılmış, kayıt {year}")
        dead = sorted(marker for marker in DEAD_SOURCE_MARKERS if marker in text)
        if dead:
            problems.append(f"ölü program bağlantısı ({', '.join(dead)})")
        if problems:
            findings.append(f"{label}: " + "; ".join(problems))


CITATION = "atıf"
CONTENT = "içerik"
STEP_HINTS = {
    "içerik": "2. adım: ders saati, yüzde ve çıktı sayısı düzeltmeleri",
    "atıf": "4. adım: program yılı ve bağlantısının güncellenmesi",
}


def save_deviations() -> int:
    """Denetimin o anki bulgularını sapma listesine yazar (gözden geçirilip gönderilir)."""
    record = load_json(RECORD)
    findings: list[str] = []
    validate_record(record, findings)
    validate_units(record, findings)
    validate_citation(record, findings)

    deviations = []
    for finding in sorted(set(findings)):
        path, _, detail = finding.partition(": ")
        kind = CITATION if "bağlantı" in detail or "yılı" in detail else CONTENT
        deviations.append(
            {
                "file": path,
                "detail": detail,
                "kind": kind,
                "note": STEP_HINTS[kind],
            }
        )

    payload = {
        "schemaVersion": "1.0.0",
        "programYear": record["source"]["year"],
        "recordedAt": "2026-10-14",
        "description": (
            "Materyaller resmî 2026 programına göre yeniden yazılana kadar açık kalan sapmalar. "
            "Her madde 2. ve 3. adımda kapatılır; kapandıkça bu listeden düşer."
        ),
        "deviations": deviations,
    }
    DEVIATIONS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(deviations)} sapma kaydedildi: {DEVIATIONS.relative_to(ROOT)}")
    return 0


def main() -> int:
    if "--kaydet" in sys.argv[1:]:
        return save_deviations()

    if not RECORD.exists():
        print(f"Program kaydı yok: {RECORD.relative_to(ROOT)}")
        return 1
    record = load_json(RECORD)
    known = load_json(DEVIATIONS)["deviations"] if DEVIATIONS.exists() else []

    errors: list[str] = []
    findings: list[str] = []
    validate_record(record, errors)
    if not errors:
        validate_units(record, findings)
        validate_citation(record, findings)

    allow = {(item["file"], item["detail"]) for item in known}
    outstanding = set()
    for finding in findings:
        path, _, detail = finding.partition(": ")
        if (path, detail) in allow:
            outstanding.add((path, detail))
        else:
            errors.append(finding)
    for path, detail in sorted(allow - outstanding):
        errors.append(f"kayıtlı sapma artık geçerli değil, listeden çıkarın: {path}: {detail}")

    if errors:
        print("Program uyumu denetimi BAŞARISIZ.")
        for error in sorted(set(errors)):
            print(f"- {error}")
        if known:
            print(f"\nKayıtlı ve kapatılması beklenen sapma: {len(known)}")
        return 1

    print("Program uyumu denetimi BAŞARILI (kayıtlı sapmalar hariç).")
    print(f"- Kaynak: {record['source']['title']} ({record['source']['year']}, {record['source']['pageCount']} sayfa)")
    total_units = sum(len(rows) for rows in record["units"].values())
    deviating_files = {item["file"] for item in known if item["kind"] == CONTENT}
    clean_units = total_units - len({path for path in deviating_files if path.startswith("mufredat/")})
    print(f"- {clean_units}/{total_units} ünitenin ders saati, yüzde oranı ve çıktı sayıları programla birebir eşleşiyor")
    print(f"- Materyallerde geçen {len(record['outcomes'])} öğrenme çıktı kodunun tamamı programda tanımlı")
    if known:
        content = sum(1 for item in known if item["kind"] == CONTENT)
        citation = len(known) - content
        print(f"- Açık sapma: {content} içerik, {citation} atıf — aşağıdaki liste 2., 3. ve 4. adımda kapatılacak")
        for item in known:
            print(f"  · [{item['kind']}] {item['file']}: {item['detail']}")
    else:
        print("- Açık sapma yok: materyaller resmî programla tam uyumlu")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
