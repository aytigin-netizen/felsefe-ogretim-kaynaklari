#!/usr/bin/env python3
"""Markdown materyallerinden GitHub Pages okuma sitesini üretir.

Kullanım:
    python tools/uret_site.py           # docs/ altındaki sayfaları yeniden üretir
    python tools/uret_site.py --check   # depodaki sayfalar üretimle uyuşuyor mu diye bakar

Araç bağımlılık gerektirmez ve felsefi içerik üretmez: yalnızca depodaki
Markdown dosyalarını HTML'e çevirir ve sayfalar arası bağlantıları kurar.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
MUFREDAT = ROOT / "mufredat"

REPO = "aytigin-netizen/felsefe-ogretim-kaynaklari"
REPO_URL = f"https://github.com/{REPO}"
BLOB = f"{REPO_URL}/blob/main"
SITE_NAME = "Felsefe Öğretim Kaynakları"
PROGRAM_RECORD = MUFREDAT / "program-2026-ozet.json"
SUPPLEMENT_LABELS = {
    "ek-soru-setleri-diyalog": "Diyalog Kurgulu Ek Soru Setleri",
    "ek-soru-setleri-forum": "Forum Kurgulu Ek Soru Setleri",
}


def program_source() -> dict:
    """Resmî programın yılı ve bağlantısı tek yerden: program kaydı."""
    record = json.loads(PROGRAM_RECORD.read_text(encoding="utf-8"))
    return record["source"]

PAGE_CSS = (
    'body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.7;'
    "color:#1f2430;background:#f7f8fa;margin:0}"
    "main{max-width:880px;margin:0 auto;padding:24px 20px 80px}"
    "h1{font-size:1.7rem;border-bottom:3px solid #2b4c7e;padding-bottom:.4rem}"
    "h2{margin-top:2rem;color:#2b4c7e}"
    "h3{margin-top:1.4rem;color:#3a5a8c}"
    "table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.95rem}"
    "th,td{border:1px solid #d5dae2;padding:8px 10px;text-align:left;vertical-align:top}"
    "th{background:#eef1f6}"
    "blockquote{border-left:4px solid #2b4c7e;background:#eef1f6;margin:1rem 0;padding:.6rem 1rem}"
    "code{background:#eef1f6;padding:2px 5px;border-radius:4px;font-size:.92em}"
    "pre{background:#22272e;color:#e6e8eb;padding:14px;border-radius:8px;overflow-x:auto}"
    "hr{border:none;border-top:1px solid #d5dae2;margin:2rem 0}"
    "a{color:#2b4c7e}"
    "nav.top{background:#2b4c7e;color:#fff;padding:10px 20px}"
    "nav.top a{color:#fff;text-decoration:none;font-weight:600}"
    "footer{margin-top:60px;padding-top:16px;border-top:1px solid #d5dae2;font-size:.85rem;color:#889}"
)

INDEX_CSS = (
    "body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;margin:0;"
    "background:#fdfcf8;color:#222;line-height:1.6}"
    ".wrap{max-width:1080px;margin:0 auto;padding:24px}"
    ".hero{background:linear-gradient(135deg,#3b2f14,#7a5c2e);color:#fdfcf8;border-radius:14px;"
    "padding:44px 32px;margin-bottom:28px}"
    ".hero h1{margin:0 0 10px;font-size:2.2rem;border:none;color:#fdfcf8}"
    ".hero p{margin:0;opacity:.9;max-width:640px}"
    ".badges{margin-top:18px;display:flex;flex-wrap:wrap;gap:8px}"
    ".badge{background:rgba(253,252,248,.16);border:1px solid rgba(253,252,248,.4);"
    "border-radius:999px;padding:4px 14px;font-size:14px}"
    "h2{font-size:1.3rem;color:#3b2f14;margin:36px 0 14px;border-bottom:2px solid #c9a227;"
    "padding-bottom:6px}"
    ".cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}"
    ".card{display:block;background:#fff;border:1px solid #e5ddc8;border-radius:10px;padding:16px;"
    "text-decoration:none;color:#222;transition:box-shadow .15s,transform .15s}"
    ".card:hover{box-shadow:0 4px 14px rgba(59,47,20,.14);transform:translateY(-2px)}"
    ".card-title{font-weight:600;color:#3b2f14;margin-bottom:4px}"
    ".card-sub{font-size:13px;color:#8a8062}"
    "footer{margin-top:48px;padding-top:18px;border-top:1px solid #e5ddc8;font-size:14px;"
    "color:#8a8062}"
    "footer a{color:#7a5c2e}"
)

REFERENCE_DEFINITION = re.compile(r"^\[([^\]]+)\]:\s*(\S+)(?:\s+\"(.*)\")?\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
# Yalnızca yıldız ve tire gerili satırlar ayırıcıdır: çalışma kâğıtlarındaki
# boş doldurma satırları (_ _ _) kesinti değildir, düz metin olarak korunur.
HORIZONTAL_RULE = re.compile(r"^\s*(?:-{3,}|\*{3,})\s*$")
TABLE_DIVIDER = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
BLOCKQUOTE = re.compile(r"^\s*>\s?(.*)$")

INLINE_TOKEN = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<link>\[[^\]]+\]\([^)\s]+(?:\s+\"[^\"]*\")?\))"
    r"|(?P<reference>\[\d+\])"
    r"|(?P<strong>\*\*(?!\s)(?P<strong_text>[^*\n]+?)(?<!\s)\*\*)"
    r"|(?P<del>~~(?!\s)(?P<del_text>[^\n]+?)(?<!\s)~~)"
    r"|(?P<em>(?<![*\w])\*(?!\s)(?P<em_star_text>[^*\n]+?)(?<!\s)\*(?!\*)"
    r"|(?<![_\w])_(?!\s)(?P<em_text>[^_\n]+?)(?<!\s)_(?![_\w]))"
)


def escape(text: str, quote: bool = False) -> str:
    return html.escape(text, quote=quote)


def resolve_href(target: str, source: Path) -> str:
    """Markdown içindeki göreli bağlantıyı depodaki gerçek dosyaya çevirir."""
    clean = target.split("#", 1)[0]
    if not clean or re.match(r"^(?:https?|mailto|tel|data):", clean, re.IGNORECASE):
        return target
    if clean.startswith("/"):
        return f"{BLOB}{clean}"
    try:
        resolved = (source.parent / clean).resolve().relative_to(ROOT.resolve())
    except ValueError:
        return target
    return f"{BLOB}/{resolved.as_posix()}"


def render_inline(text: str, source: Path, references: dict[str, tuple[str, str]]) -> str:
    out: list[str] = []
    position = 0
    for match in INLINE_TOKEN.finditer(text):
        out.append(escape(text[position : match.start()]))
        position = match.end()
        token = match.group(0)
        if token.startswith("`"):
            out.append(f"<code>{escape(token[1:-1])}</code>")
        elif match.group("link"):
            label, _, rest = token[1:-1].partition("](")
            href, _, title = rest.partition(" ")
            anchor = f' title="{escape(title.strip(chr(34)))}"' if title.strip() else ""
            out.append(f'<a href="{escape(resolve_href(href, source), quote=True)}"{anchor}>{render_inline(label, source, references)}</a>')
        elif match.group("reference"):
            label = token[1:-1]
            if label in references:
                out.append(f'<a class="ref" href="#kaynak-{label}">[{label}]</a>')
            else:
                out.append(escape(token))
        elif match.group("strong"):
            out.append(f"<strong>{render_inline(match.group('strong_text'), source, references)}</strong>")
        elif match.group("del"):
            out.append(f"<del>{render_inline(match.group('del_text'), source, references)}</del>")
        else:
            body = match.group("em_star_text") or match.group("em_text") or ""
            out.append(f"<em>{render_inline(body, source, references)}</em>")
    out.append(escape(text[position:]))
    return "".join(out)


def split_references(text: str) -> tuple[str, dict[str, tuple[str, str]]]:
    """Kaynakça tanımlarını ([1]: url "başlık") gövdeden ayırır."""
    body: list[str] = []
    references: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        match = REFERENCE_DEFINITION.match(line)
        if match:
            references[match.group(1)] = (match.group(2), match.group(3) or "")
        else:
            body.append(line)
    return "\n".join(body), references


def table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def render_table(rows: list[list[str]], source: Path, references: dict) -> str:
    header, *body = rows
    parts = ["<table><thead><tr>"]
    parts += [f"<th>{render_inline(cell, source, references)}</th>" for cell in header]
    parts.append("</tr></thead><tbody>")
    for row in body:
        parts.append("<tr>")
        parts += [f"<td>{render_inline(cell, source, references)}</td>" for cell in row]
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def unwrap_paragraph(body: str) -> str:
    """Tek paragraftan oluşan liste öğesini <p> sarmalayıcısından çıkarır."""
    stripped = body.strip()
    if stripped.startswith("<p>") and stripped.endswith("</p>") and stripped.count("<p>") == 1:
        return stripped[3:-4]
    return stripped


def parse_list(
    lines: list[str], index: int, source: Path, references: dict
) -> tuple[str, int]:
    """İç içe listeleri doğru derinlikte <ul>/<ol> öğelerine çevirir."""
    first = LIST_ITEM.match(lines[index])
    assert first is not None
    base_indent = len(first.group(1))
    ordered = bool(re.match(r"\d", first.group(2)))
    tag = "ol" if ordered else "ul"
    items: list[list[str]] = [[first.group(3)]]
    index += 1

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            following = lines[index + 1] if index + 1 < len(lines) else ""
            if following.strip() and (len(following) - len(following.lstrip())) > base_indent:
                items[-1].append("")
                index += 1
                continue
            index += 1
            break
        item = LIST_ITEM.match(line)
        indent = len(item.group(1)) if item else len(line) - len(line.lstrip())
        if item and indent < base_indent:
            break
        if item and indent == base_indent:
            items.append([item.group(3)])
            index += 1
            continue
        if indent > base_indent or item is not None:
            items[-1].append(line.strip())
            index += 1
            continue
        break

    parts = [f"<{tag}>"]
    for item_lines in items:
        parts.append(f"<li>{unwrap_paragraph(render_blocks(item_lines, source, references))}</li>")
    parts.append(f"</{tag}>")
    return "".join(parts), index


def render_blocks(lines: list[str], source: Path, references: dict) -> str:
    out: list[str] = []
    index = 0

    def paragraph(buffer: list[str]) -> None:
        if not buffer:
            return
        joined = " ".join(part.strip() for part in buffer if part.strip())
        if joined:
            out.append(f"<p>{render_inline(joined, source, references)}</p>")

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue

        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{render_inline(heading.group(2).strip(), source, references)}</h{level}>")
            index += 1
            continue

        if HORIZONTAL_RULE.match(line):
            out.append("<hr>")
            index += 1
            continue

        if line.strip().startswith("|"):
            rows = [table_row(line)]
            index += 1
            if index < len(lines) and TABLE_DIVIDER.match(lines[index]) and "|" in lines[index]:
                index += 1
                while index < len(lines) and lines[index].strip().startswith("|"):
                    rows.append(table_row(lines[index]))
                    index += 1
            out.append(render_table(rows, source, references))
            continue

        if BLOCKQUOTE.match(line):
            quoted: list[str] = []
            while index < len(lines) and (BLOCKQUOTE.match(lines[index]) or (quoted and lines[index].strip())):
                match = BLOCKQUOTE.match(lines[index])
                quoted.append(match.group(1) if match else lines[index].strip())
                index += 1
            out.append(f"<blockquote>{render_blocks(quoted, source, references)}</blockquote>")
            continue

        item = LIST_ITEM.match(line)
        if item:
            rendered, index = parse_list(lines, index, source, references)
            out.append(rendered)
            continue

        buffer = [line]
        index += 1
        while index < len(lines) and lines[index].strip():
            following = lines[index]
            if (
                HEADING.match(following)
                or HORIZONTAL_RULE.match(following)
                or LIST_ITEM.match(following)
                or BLOCKQUOTE.match(following)
                or following.strip().startswith("|")
            ):
                break
            buffer.append(following)
            index += 1
        paragraph(buffer)

    return "".join(out)


REFERENCE_HEADING = re.compile(r"^##\s+.*(?:kaynak|referans)", re.IGNORECASE | re.MULTILINE)


def render_references(references: dict[str, tuple[str, str]], body: str) -> str:
    if not references:
        return ""
    parts = []
    if not REFERENCE_HEADING.search(body):
        parts.append('<h2 id="kaynaklar">Kaynakça</h2>')
    parts.append("<ol>")
    for label, (url, title) in references.items():
        suffix = f" — {escape(title)}" if title else ""
        parts.append(
            f'<li id="kaynak-{escape(label, quote=True)}">'
            f'<a href="{escape(url, quote=True)}">{escape(url)}</a>{suffix}</li>'
        )
    parts.append("</ol>")
    return "".join(parts)


def markdown_to_html(text: str, source: Path) -> str:
    body, references = split_references(text)
    return render_blocks(body.splitlines(), source, references) + render_references(references, body)


def page_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        heading = HEADING.match(line)
        if heading:
            title = re.sub(r"[*_`]", "", heading.group(2)).strip()
            return title or fallback
    return fallback


def relative_home(output: Path) -> str:
    return "../" * (len(output.relative_to(SITE).parts) - 1) + "index.html"


def render_page(title: str, body: str, output: Path, source: Path, source_label: str) -> str:
    source_href = f"{BLOB}/{source.relative_to(ROOT).as_posix()}"
    program = program_source()
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{escape(title)}</title>"
        f"<style>{PAGE_CSS}</style></head><body>"
        f'<nav class="top"><a href="{relative_home(output)}">← Ana Sayfa · {escape(SITE_NAME)}</a></nav>'
        f"<main>\n{body}\n</main><footer>Bu sayfa <a href=\"{source_href}\">{escape(source_label)}</a> "
        f"Markdown materyalinden üretilmiştir. Resmî kaynak: "
        f'<a href="{program["url"]}">MEB Felsefe Dersi Öğretim Programı ({program["year"]})</a>.</footer></body></html>'
    )


def card(href: str, title: str, subtitle: str) -> str:
    return (
        f'<a class="card" href="{escape(href, quote=True)}">'
        f'<div class="card-title">{escape(title)}</div>'
        f'<div class="card-sub">{escape(subtitle)}</div></a>'
    )


def page_href(output: Path) -> str:
    """Ana sayfadan çıktı sayfasına göreli adres."""
    return output.relative_to(SITE).as_posix()


def render_index(sections: list[tuple[str, list[tuple[str, str, str]]]]) -> str:
    unit_total = sum(
        len(items) for title, items in sections if title in {"10. Sınıf Üniteleri", "11. Sınıf Üniteleri"}
    )
    worksheet_total = sum(
        len(items)
        for title, items in sections
        if title in {"10. Sınıf Çalışma Kâğıtları", "11. Sınıf Çalışma Kâğıtları"}
    )
    parts = [
        "<!DOCTYPE html>",
        '<html lang="tr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{escape(SITE_NAME)}</title>",
        f"<style>{INDEX_CSS}</style></head><body><div class=\"wrap\">",
        '<div class="hero">',
        f"<h1>{escape(SITE_NAME)}</h1>",
        "<p>MEB Türkiye Yüzyılı Maarif Modeli Felsefe Dersi Öğretim Programı "
        f"({program_source()['year']} onaylı) için açık kaynaklı, doğrudan uygulanabilir "
        "10. ve 11. sınıf öğretim materyalleri.</p>",
        '<div class="badges">',
        f'<span class="badge">{unit_total} ünite materyali</span>',
        f'<span class="badge">{worksheet_total} çalışma kâğıdı</span>',
        f'<span class="badge">{worksheet_total} cevap anahtarı</span>',
        '<span class="badge">2 ek soru seti</span>',
        "</div></div>",
    ]
    for title, items in sections:
        parts.append(f"<h2>{escape(title)}</h2>")
        parts.append('<div class="cards">')
        parts += [card(href, item_title, subtitle) for href, item_title, subtitle in items]
        parts.append("</div>")
    parts.append(
        f'<footer>{escape(SITE_NAME)} · Kaynak dosyalar ve sürüm geçmişi: '
        f'<a href="{REPO_URL}">GitHub deposunda</a>.</footer>'
    )
    parts.append("</div></body></html>")
    return "\n".join(parts) + "\n"


def slide_number(text: str) -> int:
    match = re.search(r"^(\d+)", text)
    return int(match.group(1)) if match else 0


def strip_unit_prefix(title: str) -> str:
    """'3. Ünite: Varlık Felsefesi' gibi başlıkları 'Varlık Felsefesi' biçimine indirger."""
    return re.sub(r"^Ünite:\s*", "", re.sub(r"^\d+\.\s*", "", title)).strip()


def humanize(stem: str) -> str:
    return stem.replace("-", " ").strip().title()


def discover() -> tuple[list[tuple[Path, Path, str, str]], list[tuple[str, list[tuple[str, str, str]]]]]:
    """(kaynak, çıktı, üstveri sütunu, altveri) sayfa listesi ve ana sayfa bölümlerini döndürür."""
    pages: list[tuple[Path, Path, str, str]] = []

    def grade_of(path: Path) -> str:
        return path.relative_to(MUFREDAT).parts[0]

    for grade in sorted(p.name for p in MUFREDAT.iterdir() if p.is_dir() and p.name.endswith("-sinif")):
        units = sorted(
            (p for p in (MUFREDAT / grade).glob("*.md") if re.match(r"^\d\d-", p.name)),
            key=lambda p: slide_number(p.name),
        )
        for unit in units:
            pages.append((unit, SITE / "site" / grade / f"{unit.stem}.html", "Ünite materyali", "unit"))
        worksheets = sorted((MUFREDAT / grade / "calisma-kagitlari").glob("*-ck.md"))
        for worksheet in worksheets:
            pages.append(
                (worksheet, SITE / "site" / grade / f"{worksheet.stem}.html", "Öğrenci çalışma kâğıdı + cevap anahtarı", "worksheet")
            )
        for supplement in sorted((MUFREDAT / grade).glob("ek-soru-setleri-*.md")):
            unit_word = "Dokuz" if grade == "10-sinif" else "Altı"
            pages.append(
                (
                    supplement,
                    SITE / "site" / grade / f"{supplement.stem}.html",
                    f"{unit_word} ünite · öğretmen notlu",
                    "supplement",
                )
            )

    shared_subtitles = {
        "degerlendirme-formlari": "Öz, akran ve grup değerlendirme formları",
        "metin-inceleme-formu": "Performans görevi metin inceleme formu",
    }
    for document in sorted((MUFREDAT / "ortak-materyaller").glob("*.md")):
        pages.append(
            (
                document,
                SITE / "site" / "ortak-materyaller" / f"{document.stem}.html",
                shared_subtitles.get(document.stem, "Ortak form şablonu"),
                "shared",
            )
        )

    reports = sorted(p for p in SITE.glob("*.md"))
    for report in reports:
        pages.append((report, SITE / "site" / "raporlar" / f"{report.stem}.html", "Rapor", "report"))

    sections: list[tuple[str, list[tuple[str, str, str]]]] = []

    def unit_labels(grade: str) -> dict[str, str]:
        return {
            path.name.split("-", 1)[0]: strip_unit_prefix(page_title(path.read_text(encoding="utf-8"), humanize(path.stem)))
            for path in sorted((MUFREDAT / grade).glob("*.md"))
            if re.match(r"^\d\d-", path.name)
        }

    def card_title(source: Path, page_kind: str, grade: str | None) -> str:
        if page_kind in {"unit", "worksheet"} and grade:
            number, _, slug = source.name.partition("-")
            label = unit_labels(grade).get(number, humanize(slug))
            suffix = " — Çalışma Kâğıdı" if page_kind == "worksheet" else ""
            return f"{int(number)}. {label}{suffix}"
        if page_kind == "supplement":
            return SUPPLEMENT_LABELS.get(source.stem, page_title(source.read_text(encoding="utf-8"), humanize(source.stem)))
        return page_title(source.read_text(encoding="utf-8"), humanize(source.stem))

    for grade, label in (("10-sinif", "10. Sınıf"), ("11-sinif", "11. Sınıf")):
        for kind, title in (
            ("unit", f"{label} Üniteleri"),
            ("worksheet", f"{label} Çalışma Kâğıtları"),
            ("supplement", f"{label} Ek Soru Setleri"),
        ):
            items = [
                (page_href(output), card_title(source, page_kind, grade), subtitle)
                for source, output, subtitle, page_kind in pages
                if page_kind == kind and output.relative_to(SITE).parts[1] == grade
            ]
            if items:
                sections.append((title, items))

    for kind, title in (("shared", "Ortak Materyaller"), ("report", "Denetim ve Durum Raporları")):
        items = [
            (page_href(output), page_title(source.read_text(encoding="utf-8"), humanize(source.stem)), subtitle)
            for source, output, subtitle, page_kind in pages
            if page_kind == kind
        ]
        if items:
            sections.append((title, items))

    return pages, sections


def build() -> dict[Path, str]:
    pages, sections = discover()
    produced: dict[Path, str] = {}
    for source, output, _, _ in pages:
        markdown = source.read_text(encoding="utf-8")
        produced[output] = render_page(
            page_title(markdown, humanize(source.stem)),
            markdown_to_html(markdown, source),
            output,
            source,
            source.name,
        )
    produced[SITE / "index.html"] = render_index(sections)
    return produced


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="yalnızca denetle, dosya yazma")
    args = parser.parse_args()

    produced = build()
    stale: list[str] = []
    for path, content in sorted(produced.items()):
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(str(path.relative_to(ROOT)))

    if args.check:
        if stale:
            print("Statik site güncel değil. Şu dosyalar üretimle uyuşmuyor:")
            for item in stale:
                print(f"- {item}")
            print("\nYeniden üretmek için: python tools/uret_site.py")
            return 1
        print(f"Statik site güncel: {len(produced)} dosya üretimle birebir aynı.")
        return 0

    for path, content in produced.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"{len(produced)} sayfa üretildi: {SITE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
