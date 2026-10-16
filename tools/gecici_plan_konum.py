#!/usr/bin/env python3
"""Gecici: haftalik plan bolumlerini unitelerin yanina tasi, unite basina katlanir grup yap."""
from pathlib import Path

p = Path("tools/uret_site.py")
s = p.read_text(encoding="utf-8")

# A) CSS: plan grup stilleri (reduced-motion satirindan once)
a = '    "@media (prefers-reduced-motion:reduce){.card,.card:hover{transition:none;transform:none}}"'
assert a in s, "anchor A yok"
css = (
    '    ".plan-grup{border:1px solid var(--kenar);border-radius:10px;background:var(--panel);margin:0}"\n'
    '    ".plan-grup+.plan-grup{margin-top:10px}"\n'
    '    ".plan-grup>summary{cursor:pointer;padding:12px 16px;font-weight:600;color:var(--vurgu);list-style:none;position:relative}"\n'
    '    ".plan-grup>summary::-webkit-details-marker{display:none}"\n'
    '    ".plan-grup>summary::after{content:\'▾\';position:absolute;right:16px}"\n'
    '    ".plan-grup[open]>summary::after{content:\'▴\'}"\n'
    '    ".plan-grup>summary:hover{background:var(--panel2)}"\n'
    '    ".plan-liste{padding:10px 16px 14px;display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px}"\n'
    '    ".plan-liste a{font-size:14px;text-decoration:none;color:var(--metin);padding:7px 10px;border:1px solid var(--kenar);border-radius:8px;background:var(--panel)}"\n'
    '    ".plan-liste a:hover{box-shadow:0 2px 8px rgba(59,47,20,.12);border-color:var(--altin)}"\n'
)
if "plan-grup" not in s:
    s = s.replace(a, css + a, 1)

# B) Filtre JS: plan gruplari da kapsansin
b = 'bolum.querySelectorAll(".card")'
assert b in s, "anchor B yok"
if '".card, .plan-grup"' not in s:
    s = s.replace(b, 'bolum.querySelectorAll(".card, .plan-grup")', 1)

# C) Filtre cipi: Haftalik Planlar
c = '<button type="button" class="cip" data-k="ek-soru-seti" aria-pressed="false">Ek Soru Setleri</button>'
assert c in s, "anchor C yok"
if "haftalik-plan" not in s.split("INDEX_SCRIPT")[0]:
    s = s.replace(c, c + '\n        <button type="button" class="cip" data-k="haftalik-plan" aria-pressed="false">Haftalık Planlar</button>', 1)

# D) Bolum sirasi: plan, unitelerin hemen ardindan
d_old = '            ("unit", f"{label} Üniteleri"),\n            ("worksheet", f"{label} Çalışma Kâğıtları"),\n            ("supplement", f"{label} Ek Soru Setleri"),\n            ("plan", f"{label} Haftalık Ders Planları"),'
d_new = '            ("unit", f"{label} Üniteleri"),\n            ("plan", f"{label} Haftalık Ders Planları"),\n            ("worksheet", f"{label} Çalışma Kâğıtları"),\n            ("supplement", f"{label} Ek Soru Setleri"),'
assert d_old in s, "anchor D yok"
if d_new not in s:
    s = s.replace(d_old, d_new, 1)

# E) Ana sayfa: plan bolumleri gruplu basilsin
e_old = '        parts.append(f"<h2>{escape(title)}</h2>")\n        parts.append(\'<div class="cards">\')\n        parts += [card(href, item_title, subtitle, grade, kind) for href, item_title, subtitle, grade, kind in items]\n        parts.append("</div></section>")'
e_new = '        parts.append(f"<h2>{escape(title)}</h2>")\n        if title.endswith("Haftalık Ders Planları"):\n            parts += render_plan_groups(items)\n        else:\n            parts.append(\'<div class="cards">\')\n            parts += [card(href, item_title, subtitle, grade, kind) for href, item_title, subtitle, grade, kind in items]\n            parts.append("</div>")\n        parts.append("</section>")'
assert e_old in s, "anchor E yok"
if "render_plan_groups(items)" not in s:
    s = s.replace(e_old, e_new, 1)

# F) render_plan_groups fonksiyonu (render_index oncesine)
f_anchor = "def render_index(sections:"
assert f_anchor in s, "anchor F yok"
func = '''def render_plan_groups(items: list) -> list[str]:
    """Haftalık plan kartlarını ünite başına katlanabilir grup olarak basar."""
    groups: dict[str, list[tuple[int, str, str]]] = {}
    for href, title, subtitle, grade, kind in items:
        match = re.match(r"Haftalık Ders Planı — .*?, (.*?), (\\d+)\\. Hafta$", title)
        if not match:
            continue
        label, week = match.group(1), int(match.group(2))
        groups.setdefault(label, []).append((week, href, grade))

    def sort_key(label: str) -> tuple[int, int]:
        number = re.match(r"(\\d+)\\. Ünite", label)
        return (2, 0) if number is None else (1, int(number.group(1)))

    parts: list[str] = []
    for label in sorted(groups, key=sort_key):
        weeks = sorted(groups[label])
        grade = weeks[0][2]
        links = "".join(
            \'<a href="{}">Hafta {}</a>\'.format(escape(href), week) for week, href, _ in weeks
        )
        parts.append(
            \'<details class="plan-grup" data-g="{}" data-k="haftalik-plan">\'.format(escape(grade))
            + "<summary>{}</summary>".format(escape(label))
            + \'<div class="plan-liste">{}</div>\'.format(links)
            + "</details>"
        )
    return parts


'''
if "def render_plan_groups" not in s:
    s = s.replace(f_anchor, func + f_anchor, 1)

p.write_text(s, encoding="utf-8")
print("plan yerlesim yamasi uygulandi")
