#!/usr/bin/env python3
"""Felsefe öğretim kaynakları için bağımlılıksız yapısal kalite denetimi.

Bu araç felsefi yorum veya pedagojik hüküm üretmez. Yalnızca depo içindeki
tekrar üretilebilir dosya, bağlantı, üst veri ve puanlama kontrollerini yapar.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MUFREDAT = ROOT / "mufredat"
SITE = ROOT / "docs"
BLOB_BASE = "https://github.com/aytigin-netizen/felsefe-ogretim-kaynaklari/blob/main/"
GRADE_SPECS = {
    "10-sinif": {
        "expected_units": 9,
        "code_prefix": "FEL.10.",
        "supplements": {"file": "ek-soru-setleri-diyalog.md", "expected_sets": 9},
    },
    "11-sinif": {
        "expected_units": 6,
        "code_prefix": "FEL.11.",
        "supplements": {"file": "ek-soru-setleri-forum.md", "expected_sets": 6},
    },
}
UNIT_FILE_PATTERN = re.compile(r"^\d\d-")


def unit_files(grade: str) -> list[Path]:
    """Yalnızca numaralı ünite dosyaları; ek soru setleri ünite sayımına girmez."""
    return sorted(p for p in (MUFREDAT / grade).glob("*.md") if UNIT_FILE_PATTERN.match(p.name))


def site_files() -> list[Path]:
    return sorted(SITE.rglob("*.html")) if SITE.exists() else []


def markdown_files() -> list[Path]:
    files: list[Path] = []
    readme = ROOT / "README.md"
    if readme.exists():
        files.append(readme)
    for directory in (ROOT / "docs", MUFREDAT):
        if directory.exists():
            files.extend(sorted(directory.rglob("*.md")))
    return files


def assessment_total(text: str) -> int | None:
    """Değerlendirme bölümündeki iki kullanılan biçimden puan toplamını hesaplar."""
    marker = re.search(r"^##\s+Değerlendirme\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    if not marker:
        return None
    remainder = text[marker.end() :]
    next_section = re.search(r"^##\s+", remainder, flags=re.MULTILINE)
    section = remainder[: next_section.start()] if next_section else remainder

    heading_points = [
        int(value)
        for value in re.findall(
            r"^####\s+[^\n]*?\((\d+)\s*puan\)",
            section,
            flags=re.MULTILINE | re.IGNORECASE,
        )
    ]
    if heading_points:
        return sum(heading_points)

    table_marker = re.search(
        r"^###\s+100\s+Puanlık\s+Ölçme\s+Araçları\s*$",
        section,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    if not table_marker:
        return None
    table_remainder = section[table_marker.end() :]
    next_heading = re.search(r"^###\s+", table_remainder, flags=re.MULTILINE)
    table = table_remainder[: next_heading.start()] if next_heading else table_remainder

    points: list[int] = []
    for line in table.splitlines():
        if not line.startswith("|") or "Toplam" in line:
            continue
        cells = [cell.strip().replace("**", "") for cell in line.strip("|").split("|")]
        if len(cells) >= 2 and cells[1].isdigit():
            points.append(int(cells[1]))
    return sum(points) if points else None


def local_link_error(source: Path, target: str) -> str | None:
    target = target.strip()
    if not target or target.startswith("#") or re.match(r"^(?:https?|mailto|tel):", target, re.IGNORECASE):
        return None
    target = target.split("#", 1)[0].strip().strip("<>")
    if not target:
        return None
    destination = (source.parent / unquote(target)).resolve()
    try:
        destination.relative_to(ROOT.resolve())
    except ValueError:
        return f"{source.relative_to(ROOT)} → {target}: depo dışındaki hedef"
    if not destination.exists():
        return f"{source.relative_to(ROOT)} → {target}: hedef bulunamadı"
    return None


def validate_units(errors: list[str]) -> None:
    for grade, spec in GRADE_SPECS.items():
        units = unit_files(grade)
        if len(units) != spec["expected_units"]:
            errors.append(
                f"{grade}: {spec['expected_units']} ünite bekleniyordu, {len(units)} bulundu."
            )
        worksheet_directory = MUFREDAT / grade / "calisma-kagitlari"
        worksheets = sorted(worksheet_directory.glob("*-ck.md"))
        if len(worksheets) != spec["expected_units"]:
            errors.append(
                f"{grade}: {spec['expected_units']} çalışma kâğıdı bekleniyordu, {len(worksheets)} bulundu."
            )

        for unit in units:
            text = unit.read_text(encoding="utf-8")
            label = str(unit.relative_to(ROOT))
            prefix = unit.stem.split("-", 1)[0]
            if not any(worksheet_directory.glob(f"{prefix}-*-ck.md")):
                errors.append(f"{label}: {prefix} numaralı çalışma kâğıdı bulunamadı.")
            if not re.search(r"\|\s*\*\*Ders Saati\*\*\s*\|\s*[^|\n]+\|", text, re.IGNORECASE):
                errors.append(f"{label}: 'Ders Saati' üst verisi bulunamadı.")
            if not re.search(re.escape(spec["code_prefix"]) + r"\d+\.\d+", text, re.IGNORECASE):
                errors.append(f"{label}: {spec['code_prefix']} ile başlayan öğrenme çıktısı kodu bulunamadı.")
            total = assessment_total(text)
            if total != 100:
                display = "hesaplanamadı" if total is None else str(total)
                errors.append(f"{label}: ölçme puanı toplamı 100 yerine {display} bulundu.")


def validate_links(errors: list[str]) -> None:
    link_pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
    for source in markdown_files():
        text = source.read_text(encoding="utf-8")
        for target in link_pattern.findall(text):
            issue = local_link_error(source, target)
            if issue:
                errors.append(issue)


def validate_supplements(errors: list[str]) -> None:
    """Ek soru setleri her üniteyi bir kez kapsamalı ve öğretmen notu taşımalı."""
    for grade, spec in GRADE_SPECS.items():
        supplement = spec.get("supplements")
        if not supplement:
            continue
        path = MUFREDAT / grade / supplement["file"]
        label = str(path.relative_to(ROOT))
        if not path.exists():
            errors.append(f"{label}: ek soru seti dosyası bulunamadı.")
            continue
        text = path.read_text(encoding="utf-8")
        sections = [
            section
            for section in re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]
            if section.lstrip().startswith("Ünite")
        ]
        numbers = []
        for section in sections:
            match = re.match(r"Ünite\s+(\d+)", section)
            if match:
                numbers.append(int(match.group(1)))
        expected = supplement["expected_sets"]
        if numbers != list(range(1, expected + 1)):
            errors.append(
                f"{label}: {expected} ünite için sıralı bölüm bekleniyordu, {numbers} bulundu."
            )
        for section in sections:
            title = section.splitlines()[0].strip()
            if "**Kurgu:**" not in section and "> **Konu:**" not in section:
                errors.append(f"{label}: '{title}' bölümünde kurgu metni eksik.")
            for marker in ("**Sorular:**", "**Öğretmen Notu:**"):
                if marker not in section:
                    errors.append(f"{label}: '{title}' bölümünde {marker.strip('*: ')} eksik.")


def site_link_errors(source: Path) -> list[str]:
    """Statik sayfadaki yerel ve depo içi GitHub bağlantılarını doğrular."""
    issues: list[str] = []
    text = source.read_text(encoding="utf-8")
    label = str(source.relative_to(ROOT))
    for target in re.findall(r'(?:href|src)="([^"]+)"', text):
        issue = local_link_error(source, target)
        if issue:
            issues.append(f"{label} → {target}: yerel hedef bulunamadı")
            continue
        if target.startswith(BLOB_BASE):
            relative = unquote(target[len(BLOB_BASE) :].split("#", 1)[0])
            if relative and not (ROOT / relative).exists():
                issues.append(f"{label} → {target}: depoda böyle bir dosya yok")
    return issues


def validate_site(errors: list[str]) -> None:
    for page in site_files():
        errors.extend(site_link_errors(page))


def main() -> int:
    errors: list[str] = []
    validate_units(errors)
    validate_supplements(errors)
    validate_links(errors)
    validate_site(errors)

    if errors:
        print("Yapısal kalite denetimi BAŞARISIZ.")
        for error in sorted(set(errors)):
            print(f"- {error}")
        return 1

    print("Yapısal kalite denetimi BAŞARILI.")
    print("- 10. sınıf: 9 ünite ve 9 çalışma kâğıdı")
    print("- 11. sınıf: 6 ünite ve 6 çalışma kâğıdı")
    print("- Her ünitede ders saati, öğrenme çıktısı kodu ve 100 puanlık ölçme yapısı doğrulandı")
    print("- Her sınıf düzeyinde ek soru setleri tüm üniteleri kurgu, soru ve öğretmen notuyla kapsıyor")
    print("- Depo kapsamındaki Markdown dosyalarında bozuk yerel bağlantı bulunmadı")
    print(f"- Statik sitedeki {len(site_files())} sayfanın yerel ve depo bağlantıları doğrulandı")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
