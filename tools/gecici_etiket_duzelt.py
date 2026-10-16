#!/usr/bin/env python3
from pathlib import Path

p = Path("tools/uret_site.py")
s = p.read_text(encoding="utf-8")
duzeltmeler = [
    ("Haftalik Ders Planlari", "Haftal\u0131k Ders Planlar\u0131"),
    ("Haftalik ders plani", "Haftal\u0131k ders plan\u0131"),
]
for eski, yeni in duzeltmeler:
    if eski in s and yeni not in s:
        s = s.replace(eski, yeni)
p.write_text(s, encoding="utf-8")
print("Turkce etiket duzeltmesi uygulandi")
