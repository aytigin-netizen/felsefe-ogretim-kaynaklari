#!/usr/bin/env python3
"""Gecici: uret_site.py'ye haftalik plan sayfasi destegi ekler (bir kez calistirilir)."""
from pathlib import Path

p = Path("tools/uret_site.py")
s = p.read_text(encoding="utf-8")

a = '    "report": "rapor",'
assert a in s, "anchor a bulunamadi"
if '"plan": "haftalik-plan"' not in s:
    s = s.replace(a, a + '
    "plan": "haftalik-plan",', 1)

b = '        for supplement in sorted((MUFREDAT / grade).glob("ek-soru-setleri-*.md")):'
assert b in s, "anchor b bulunamadi"
if 'gunluk-planlar' not in s:
    block = (
        '        for plan in sorted((MUFREDAT / grade / "gunluk-planlar").glob("*.md")):
'
        '            pages.append((plan, SITE / "site" / grade / "gunluk-planlar" / f"{plan.stem}.html", "Haftalik ders plani", "plan"))
'
    )
    s = s.replace(b, block + b, 1)

c = '            ("supplement", f"{label} Ek Soru Setleri"),'
assert c in s, "anchor c bulunamadi"
if 'Haftalik Ders Planlari' not in s:
    s = s.replace(c, c + '
            ("plan", f"{label} Haftalik Ders Planlari"),', 1)

p.write_text(s, encoding="utf-8")
print("uret_site.py yamasi uygulandi")
