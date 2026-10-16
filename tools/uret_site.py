#!/usr/bin/env python3
"""Markdown materyallerinden GitHub Pages okuma sitesini üretir.

Kullanım:
    python tools/uret_site.py           # docs/ altındaki sayfaları yeniden üretir
    python tools/uret_site.py --check   # depodaki sayfalar üretimle uyuşuyor mu diye bakar

Araç bağımlılık gerektirmez ve felsefi içerik üretmez: yalnızca depodaki
Markdown dosyalarını HTML'e çevirir ve sayfalar arası bağlantıları kurar.

Üretim ayrıca ana sayfa araması için docs/arama-index.json, arama motorları
için docs/sitemap.xml ve docs/robots.txt dosyalarını yazar.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
MUFREDAT = ROOT / "mufredat"

REPO = "aytigin-netizen/felsefe-ogretim-kaynaklari"
REPO_URL = f"https://github.com/{REPO}"
BLOB = f"{REPO_URL}/blob/main"
SITE_URL = "https://aytigin-netizen.github.io/felsefe-ogretim-kaynaklari/"
SITE_NAME = "Felsefe Öğretim Kaynakları"
PROGRAM_RECORD = MUFREDAT / "program-2026-ozet.json"
SUPPLEMENT_LABELS = {
    "ek-soru-setleri-diyalog": "Diyalog Kurgulu Ek Soru Setleri",
    "ek-soru-setleri-forum": "Forum Kurgulu Ek Soru Setleri",
}
FEEDBACK_LABEL = "Geri bildirim"


def program_source() -> dict:
    """Resmî programın yılı ve bağlantısı tek yerden: program kaydı."""
    record = json.loads(PROGRAM_RECORD.read_text(encoding="utf-8"))
    return record["source"]

PAGE_CSS = (
    ":root{color-scheme:light dark;"
    "--metin:#1f2430;--arka:#f7f8fa;--vurgu:#2b4c7e;--vurgu2:#3a5a8c;--kenar:#d5dae2;"
    "--panel:#fff;--panel2:#eef1f6;--altmetin:#5a6472;--odak:#2b4c7e}"
    ':root[data-tema="gece"]{--metin:#e6e8eb;--arka:#14181f;--vurgu:#8ab4f8;--vurgu2:#a8c7fa;'
    "--kenar:#39424e;--panel:#1b222c;--panel2:#232c38;--altmetin:#a7b0bd;--odak:#8ab4f8}"
    '@media (prefers-color-scheme:dark){:root:not([data-tema="gunduz"]){'
    "--metin:#e6e8eb;--arka:#14181f;--vurgu:#8ab4f8;--vurgu2:#a8c7fa;--kenar:#39424e;"
    "--panel:#1b222c;--panel2:#232c38;--altmetin:#a7b0bd;--odak:#8ab4f8}}"
    'body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.7;'
    "color:var(--metin);background:var(--arka);margin:0}"
    "main{max-width:880px;margin:0 auto;padding:24px 20px 80px}"
    "h1{font-size:1.7rem;border-bottom:3px solid var(--vurgu);padding-bottom:.4rem}"
    "h2{margin-top:2rem;color:var(--vurgu)}"
    "h3{margin-top:1.4rem;color:var(--vurgu2)}"
    "table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.95rem}"
    "th,td{border:1px solid var(--kenar);padding:8px 10px;text-align:left;vertical-align:top}"
    "th{background:var(--panel2)}"
    "blockquote{border-left:4px solid var(--vurgu);background:var(--panel2);margin:1rem 0;padding:.6rem 1rem}"
    "code{background:var(--panel2);padding:2px 5px;border-radius:4px;font-size:.92em}"
    "pre{background:#22272e;color:#e6e8eb;padding:14px;border-radius:8px;overflow-x:auto}"
    "hr{border:none;border-top:1px solid var(--kenar);margin:2rem 0}"
    "a{color:var(--vurgu)}"
    "nav.top{background:var(--vurgu);color:#fff;padding:10px 20px}"
    "nav.top a{color:#fff;text-decoration:none;font-weight:600}"
    "footer{margin-top:60px;padding-top:16px;border-top:1px solid var(--kenar);font-size:.85rem;color:var(--altmetin)}"
    ".page-actions{margin:20px 0 4px;display:flex;gap:10px;flex-wrap:wrap}"
    ".page-actions button,.page-actions a.dugme{background:var(--vurgu);color:#fff;border:none;border-radius:8px;"
    "padding:8px 16px;font-size:14px;cursor:pointer;text-decoration:none;display:inline-block}"
    ".page-actions button:hover,.page-actions a.dugme:hover{filter:brightness(.85)}"
    ".icindekiler{border:1px solid var(--kenar);border-radius:8px;background:var(--panel);margin:20px 0;padding:12px 18px}"
    ".icindekiler h2{margin:0 0 8px;font-size:1.1rem}"
    ".icindekiler ul{list-style:none;margin:0;padding:0;columns:2;column-gap:28px}"
    ".icindekiler li{margin:3px 0;break-inside:avoid}"
    ".icindekiler li.d3{padding-left:16px;font-size:.93em}"
    ".icindekiler a{text-decoration:none}"
    ".cink{opacity:0;margin-left:6px;font-size:.8em;text-decoration:none}"
    "h2:hover .cink,h3:hover .cink,.cink:focus{opacity:.6}"
    "details.cevap{border:1px solid var(--kenar);border-radius:8px;margin:1.5rem 0;background:var(--panel)}"
    "details.cevap>summary{cursor:pointer;padding:10px 14px;background:var(--panel2);"
    "font-weight:600;color:var(--vurgu);border-radius:8px}"
    "details.cevap[open]>summary{border-bottom:1px solid var(--kenar);border-radius:8px 8px 0 0}"
    "details.cevap h2{margin-top:14px}"
    "details.cevap>*:last-child{margin-bottom:14px}"
    ":focus-visible{outline:3px solid var(--odak);outline-offset:2px}"
    ".atla{position:absolute;left:-9999px;top:0;background:var(--panel);color:var(--vurgu);"
    "padding:10px 16px;z-index:10;font-weight:600;text-decoration:none}"
    ".atla:focus{left:0}"
    "details.cevap>summary:focus-visible{outline-offset:-3px}"
    "@media print{nav.top,footer,.page-actions,.cink,.atla{display:none!important}"
    "body{background:#fff;color:#000}main{max-width:none;padding:0}"
    "a{color:#1f2430}pre,blockquote,table,tr{page-break-inside:avoid}}"
    "@media (max-width:640px){.icindekiler ul{columns:1}}"
)

INDEX_CSS = (
    ":root{color-scheme:light dark;"
    "--metin:#222;--arka:#fdfcf8;--vurgu:#3b2f14;--kenar:#e5ddc8;--panel:#fff;"
    "--altmetin:#6b6350;--altin:#c9a227;--odak:#c9a227}"
    ':root[data-tema="gece"]{--metin:#e6e8eb;--arka:#14181f;--vurgu:#d7b95c;--kenar:#39424e;'
    "--panel:#1b222c;--altmetin:#a7b0bd;--altin:#d7b95c;--odak:#d7b95c}"
    '@media (prefers-color-scheme:dark){:root:not([data-tema="gunduz"]){'
    "--metin:#e6e8eb;--arka:#14181f;--vurgu:#d7b95c;--kenar:#39424e;--panel:#1b222c;"
    "--altmetin:#a7b0bd;--altin:#d7b95c;--odak:#d7b95c}}"
    "body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;margin:0;"
    "background:var(--arka);color:var(--metin);line-height:1.6}"
    ".wrap{max-width:1080px;margin:0 auto;padding:24px}"
    ".hero{background:linear-gradient(135deg,#3b2f14,#7a5c2e);color:#fdfcf8;border-radius:14px;"
    "padding:44px 32px;margin-bottom:28px}"
    ".hero h1{margin:0 0 10px;font-size:2.2rem;border:none;color:#fdfcf8}"
    ".hero p{margin:0;opacity:.9;max-width:640px}"
    ".badges{margin-top:18px;display:flex;flex-wrap:wrap;gap:8px}"
    ".badge{background:rgba(253,252,248,.16);border:1px solid rgba(253,252,248,.4);"
    "border-radius:999px;padding:4px 14px;font-size:14px}"
    "h2{font-size:1.3rem;color:var(--vurgu);margin:36px 0 14px;border-bottom:2px solid var(--altin);"
    "padding-bottom:6px}"
    ".cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}"
    ".card{display:block;background:var(--panel);border:1px solid var(--kenar);border-radius:10px;padding:16px;"
    "text-decoration:none;color:var(--metin);transition:box-shadow .15s,transform .15s}"
    ".card:hover{box-shadow:0 4px 14px rgba(59,47,20,.14);transform:translateY(-2px)}"
    ".card-title{font-weight:600;color:var(--vurgu);margin-bottom:4px}"
    ".card-sub{font-size:13px;color:var(--altmetin)}"
    "footer{margin-top:48px;padding-top:18px;border-top:1px solid var(--kenar);font-size:14px;"
    "color:var(--altmetin)}"
    "footer a{color:var(--altin)}"
    ".arama{margin:0 0 20px}"
    ".arama input{width:100%;box-sizing:border-box;padding:12px 16px;font-size:16px;"
    "border:1px solid var(--kenar);border-radius:10px;background:var(--panel);color:var(--metin)}"
    ".arama input:focus{outline:2px solid var(--odak);border-color:var(--odak)}"
    ".cips{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}"
    ".cip{border:1px solid var(--kenar);background:var(--panel);color:var(--vurgu);border-radius:999px;"
    "padding:5px 14px;font-size:14px;cursor:pointer}"
    ".cip.aktif{background:var(--vurgu);color:var(--arka);border-color:var(--vurgu)}"
    ".tema-satir{display:flex;justify-content:flex-end;margin:0 0 8px}"
    ".tema-satir button{background:var(--panel);border:1px solid var(--kenar);color:var(--vurgu);"
    "border-radius:999px;padding:6px 14px;font-size:14px;cursor:pointer}"
    ".tema-satir button:hover{filter:brightness(.92)}"
    ".sonuclar{margin:0 0 24px}"
    ".sonuc{display:block;background:var(--panel);border:1px solid var(--kenar);border-radius:10px;"
    "padding:12px 16px;margin-bottom:8px;text-decoration:none;color:var(--metin)}"
    ".sonuc:hover{box-shadow:0 4px 14px rgba(59,47,20,.14)}"
    ".sonuc-baslik{font-weight:600;color:var(--vurgu)}"
    ".sonuc-alt{font-size:13px;color:var(--altmetin);margin-top:2px}"
    ".sonuc-yok{color:var(--altmetin)}"
    ":focus-visible{outline:3px solid var(--odak);outline-offset:2px}"
    ".atla{position:absolute;left:-9999px;top:0;background:var(--panel);color:var(--vurgu);"
    "padding:10px 16px;z-index:10;font-weight:600;text-decoration:none}"
    ".atla:focus{left:0}"
    "@media (prefers-reduced-motion:reduce){.card,.card:hover{transition:none;transform:none}}"
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
    parts = ['<table><thead><tr>']
    parts += [f'<th scope="col">{render_inline(cell, source, references)}</th>' for cell in header]
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


FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
    '<text y="0.9em" font-size="90">📚</text></svg>'
)


def favicon_link(output: Path) -> str:
    """Sayfa derinliğine göre favicon.svg bağlantısı üretir."""
    prefix = "../" * (len(output.relative_to(SITE).parts) - 1)
    return f'<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">'

INDEX_DESCRIPTION = (
    "MEB 2026 Felsefe Dersi Öğretim Programı için açık kaynaklı 10. ve 11. sınıf felsefe "
    "öğretim materyalleri: üniteler, çalışma kâğıtları, ek soru setleri, ortak formlar ve "
    "denetim raporları."
)

KIND_TR = {
    "unit": "unite",
    "worksheet": "calisma-kagidi",
    "supplement": "ek-soru-seti",
    "school": "okul-temelli",
    "shared": "ortak-materyal",
    "report": "rapor",
}

INDEX_SCRIPT = """<script>
(function () {
"use strict";
var veriler = null;
var giris = document.getElementById("arama");
var cipler = Array.prototype.slice.call(document.querySelectorAll(".cip"));
var bolumler = Array.prototype.slice.call(document.querySelectorAll(".bolum"));
var sonuclar = document.getElementById("sonuclar");
var aktif = { g: "", k: "" };

function kucuk(metin) { return metin.toLocaleLowerCase("tr"); }

function kosul(g, k) {
  return (!aktif.g || g === aktif.g) && (!aktif.k || k === aktif.k);
}

function kacis(metin) {
  return metin.replace(/&/g, "&amp;").replace(/</g, "&lt;");
}

function kartlariFiltrele() {
  bolumler.forEach(function (bolum) {
    var gorunen = 0;
    Array.prototype.slice.call(bolum.querySelectorAll(".card")).forEach(function (kart) {
      var uygun = kosul(kart.getAttribute("data-g") || "", kart.getAttribute("data-k") || "");
      kart.style.display = uygun ? "" : "none";
      if (uygun) { gorunen += 1; }
    });
    bolum.style.display = gorunen ? "" : "none";
  });
}

function sonuclariGoster(sorgu) {
  var kucukSorgu = kucuk(sorgu);
  var eslesen = [];
  veriler.forEach(function (kayit) {
    if (!kosul(kayit.g, kayit.k)) { return; }
    var vurus = kucuk(kayit.x).indexOf(kucukSorgu);
    if (vurus === -1 && kucuk(kayit.t + " " + kayit.s).indexOf(kucukSorgu) === -1) { return; }
    eslesen.push({ kayit: kayit, vurus: vurus });
  });
  var icerik = "";
  eslesen.slice(0, 15).forEach(function (buluntu) {
    var kayit = buluntu.kayit;
    var metin = kayit.x;
    var bas = Math.max(0, buluntu.vurus - 60);
    var son = Math.min(metin.length, bas + 170);
    var parcacik = (bas > 0 ? "…" : "") + metin.slice(bas, son) + (son < metin.length ? "…" : "");
    icerik += '<a class="sonuc" href="' + kayit.u + '">' +
      '<div class="sonuc-baslik">' + kacis(kayit.t) + '</div>' +
      '<div class="sonuc-alt">' + kacis(parcacik) + '</div></a>';
  });
  if (!icerik) { icerik = '<p class="sonuc-yok">Aramanıza uyan materyal bulunamadı.</p>'; }
  sonuclar.innerHTML = icerik;
  sonuclar.hidden = false;
  bolumler.forEach(function (bolum) { bolum.style.display = "none"; });
}

function uygula() {
  var sorgu = giris.value.trim();
  if (sorgu.length >= 2 && veriler) {
    sonuclariGoster(sorgu);
  } else {
    sonuclar.hidden = true;
    sonuclar.innerHTML = "";
    kartlariFiltrele();
  }
}

cipler.forEach(function (cip) {
  cip.addEventListener("click", function () {
    aktif = { g: cip.getAttribute("data-g") || "", k: cip.getAttribute("data-k") || "" };
    cipler.forEach(function (c) {
      c.classList.toggle("aktif", c === cip);
      c.setAttribute("aria-pressed", c === cip ? "true" : "false");
    });
    uygula();
  });
});
giris.addEventListener("input", uygula);
fetch("arama-index.json")
  .then(function (yanit) { return yanit.json(); })
  .then(function (veri) { veriler = veri; uygula(); });
})();
</script>"""


TEMA_FLASH = (
    '<script>try{var t=localStorage.getItem("tema");'
    'if(t)document.documentElement.setAttribute("data-tema",t)}catch(e){}</script>'
)

TEMA_SCRIPT = """<script>
(function () {
"use strict";
var kok = document.documentElement;
var dugme = document.getElementById("tema-dugme");
var geri = document.getElementById("geri-bildirim");
var geriTaban = geri ? geri.href : "";
function etiket() {
  dugme.textContent = kok.getAttribute("data-tema") === "gece" ? "☀ Açık tema" : "☾ Karanlık tema";
}
function temaAdi() {
  var t = kok.getAttribute("data-tema");
  return t === "gece" ? "karanlık" : t === "gunduz" ? "açık" : "otomatik (sistem)";
}
function geriGuncelle() {
  if (geri) { geri.href = geriTaban.replace("__TEMA__", encodeURIComponent(temaAdi())); }
}
if (dugme) {
  dugme.addEventListener("click", function () {
    var yeni = kok.getAttribute("data-tema") === "gece" ? "gunduz" : "gece";
    kok.setAttribute("data-tema", yeni);
    try { localStorage.setItem("tema", yeni); } catch (e) {}
    etiket();
    geriGuncelle();
  });
  etiket();
}
geriGuncelle();
})();
</script>"""


def meta_description(body: str) -> str:
    """Sayfa gövdesinden arama motorları için kısa açıklama üretir."""
    text = re.sub(r"<[^>]+>", " ", body)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 157:
        return text[:157].rstrip() + "…"
    return text


ANSWER_KEY_HEADING = re.compile(
    r"(<h2[^>]*>[^<]*cevap anahtar[^<]*</h2>)(.*?)(?=<h2|\Z)", re.IGNORECASE | re.DOTALL
)


def wrap_answer_keys(body: str) -> str:
    """"Cevap Anahtarı" başlıklı bölümleri katlanabilir öğeye sarar."""

    def wrap(match: re.Match) -> str:
        return (
            '<details class="cevap"><summary>Cevap anahtarı — göstermek için tıklayın</summary>'
            + match.group(1)
            + match.group(2)
            + "</details>"
        )

    return ANSWER_KEY_HEADING.sub(wrap, body)


ANSWER_KEY_BLOCK = re.compile(r'(<details class="cevap">.*?</details>)', re.DOTALL)
HEADING_TAG = re.compile(r"<h([23])>(.*?)</h\1>", re.DOTALL)
TR_SLUG = str.maketrans(
    {
        "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i", "I": "i",
        "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
    }
)


def slugify(text: str) -> str:
    """Başlık metninden URL dostu, Türkçe karakterlerden arındırılmış kimlik üretir."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", text))
    plain = plain.translate(TR_SLUG).lower()
    plain = re.sub(r"[^a-z0-9]+", "-", plain).strip("-")
    return plain or "bolum"


def add_heading_anchors(body: str) -> tuple[str, list[tuple[int, str, str]]]:
    """h2/h3 başlıklarına sayfa içi kimlik ve çıpa bağlantısı ekler.

    Katlanabilir cevap anahtarı bloklarının içindeki başlıklar bilinçli olarak
    dokunulmaz: içindekiler listesi öğrenciden gizli tutulan cevaplara bağlantı vermez.
    Dönen liste (seviye, kimlik, başlık) üçlüleri içindekiler kutusu içindir.
    """
    entries: list[tuple[int, str, str]] = []
    used: dict[str, int] = {}

    def replace(match: re.Match) -> str:
        level = int(match.group(1))
        inner = match.group(2)
        slug = slugify(inner)
        used[slug] = used.get(slug, 0) + 1
        if used[slug] > 1:
            slug = f"{slug}-{used[slug]}"
        entries.append((level, slug, inner))
        anchor = (
            f' <a class="cink" href="#{slug}" aria-label="Bu başlığın bağlantısı">#</a>'
        )
        return f'<h{level} id="{slug}">{inner}{anchor}</h{level}>'

    rebuilt = []
    for segment in ANSWER_KEY_BLOCK.split(body):
        if segment.startswith('<details class="cevap">'):
            rebuilt.append(segment)
        else:
            rebuilt.append(HEADING_TAG.sub(replace, segment))
    return "".join(rebuilt), entries


def render_toc(entries: list[tuple[int, str, str]]) -> str:
    """Uzun sayfaların başına içindekiler kutusu koyar; kısa sayfalarda boş döner."""
    if len(entries) < 3:
        return ""
    items = "".join(
        f'<li class="d{level}"><a href="#{slug}">{text}</a></li>'
        for level, slug, text in entries
    )
    return (
        '<nav class="icindekiler" aria-label="İçindekiler"><h2>İçindekiler</h2>'
        f"<ul>{items}</ul></nav>"
    )


def plain_text(markdown: str) -> str:
    """Markdown metni arama dizini için düz metne indirger."""
    body, _ = split_references(markdown)
    body = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"[#>*_`|~\[\]-]", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body


def page_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        heading = HEADING.match(line)
        if heading:
            title = re.sub(r"[*_`]", "", heading.group(2)).strip()
            return title or fallback
    return fallback


def relative_home(output: Path) -> str:
    return "../" * (len(output.relative_to(SITE).parts) - 1) + "index.html"


def feedback_href(page_url: str, title: str, source_href: str = "") -> str:
    """Sayfa URL'si ve tema bilgisiyle önceden doldurulmuş issue bağlantısı üretir.

    Tema istemci tarafında belirlendiği için gövdede __TEMA__ yer tutucusu
    bırakılır; sayfadaki tema betiği bu yer tutucuyu geçerli tema adıyla değiştirir.
    """
    body = (
        f"## {FEEDBACK_LABEL}\n\n"
        f"- Sayfa: {page_url}\n"
        "- Tema: __TEMA__\n"
    )
    if source_href:
        body += f"- Kaynak dosya: {source_href}\n"
    body += "\n### Sorun ya da öneri\n\n( geri bildiriminizi buraya yazın )\n"
    query = urlencode({"title": f"{FEEDBACK_LABEL}: {title}", "body": body})
    return f"{REPO_URL}/issues/new?{query}"


def render_page(title: str, body: str, output: Path, source: Path, source_label: str) -> str:
    source_href = f"{BLOB}/{source.relative_to(ROOT).as_posix()}"
    program = program_source()
    page_url = SITE_URL + output.relative_to(SITE).as_posix()
    description = meta_description(body)
    body, toc = add_heading_anchors(wrap_answer_keys(body))
    toc_html = render_toc(toc)
    if toc_html:
        h1 = re.search(r"<h1>.*?</h1>", body, re.DOTALL)
        if h1:
            body = body[: h1.end()] + "\n" + toc_html + body[h1.end() :]
        else:
            body = toc_html + body
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{escape(title)}</title>"
        f'<meta name="description" content="{escape(description, quote=True)}">'
        f'<link rel="canonical" href="{page_url}">'
        f'<meta property="og:title" content="{escape(title, quote=True)}">'
        f'<meta property="og:description" content="{escape(description, quote=True)}">'
        '<meta property="og:type" content="article">'
        f'<meta property="og:url" content="{page_url}">'
        '<meta property="og:locale" content="tr_TR">'
        f'<meta property="og:site_name" content="{escape(SITE_NAME, quote=True)}">'
        f"{favicon_link(output)}"
        f"{TEMA_FLASH}"
        f"<style>{PAGE_CSS}</style></head><body>"
        '<a class="atla" href="#icerik">İçeriğe atla</a>'
        f'<nav class="top"><a href="{relative_home(output)}">← Ana Sayfa · {escape(SITE_NAME)}</a></nav>'
        '<main id="icerik">\n<div class="page-actions"><button type="button" onclick="window.print()">🖨 Yazdır / PDF olarak kaydet</button>'
        '<button type="button" id="tema-dugme" aria-label="Karanlık/açık tema arasında geçiş">☾ Karanlık tema</button>'
        f'<a id="geri-bildirim" class="dugme" href="{escape(feedback_href(page_url, title, source_href), quote=True)}">💬 {FEEDBACK_LABEL}</a></div>\n'
        f"{body}\n</main><footer>Bu sayfa <a href=\"{source_href}\">{escape(source_label)}</a> "
        f"Markdown materyalinden üretilmiştir. Resmî kaynak: "
        f'<a href="{program["url"]}">MEB Felsefe Dersi Öğretim Programı ({program["year"]})</a>.</footer>'
        f"{TEMA_SCRIPT}</body></html>"
    )

def card(href: str, title: str, subtitle: str, grade: str = "", kind: str = "") -> str:
    return (
        f'<a class="card" data-g="{escape(grade, quote=True)}" data-k="{escape(kind, quote=True)}" '
        f'href="{escape(href, quote=True)}">'
        f'<div class="card-title">{escape(title)}</div>'
        f'<div class="card-sub">{escape(subtitle)}</div></a>'
    )


def page_href(output: Path) -> str:
    """Ana sayfadan çıktı sayfasına göreli adres."""
    return output.relative_to(SITE).as_posix()


def render_index(sections: list[tuple[str, list]]) -> str:
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
        f'<meta name="description" content="{escape(INDEX_DESCRIPTION, quote=True)}">',
        f'<link rel="canonical" href="{SITE_URL}">',
        f'<meta property="og:title" content="{escape(SITE_NAME, quote=True)}">',
        f'<meta property="og:description" content="{escape(INDEX_DESCRIPTION, quote=True)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:url" content="{SITE_URL}">',
        '<meta property="og:locale" content="tr_TR">',
        f'<meta property="og:site_name" content="{escape(SITE_NAME, quote=True)}">',
        favicon_link(SITE / "index.html"),
        TEMA_FLASH,
        f"<style>{INDEX_CSS}</style></head><body>",
        '<a class="atla" href="#icerik">İçeriğe atla</a>',
        '<div class="wrap">',
        '<main id="icerik">',
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
        '<div class="tema-satir"><button type="button" id="tema-dugme" aria-label="Karanlık/açık tema arasında geçiş">☾ Karanlık tema</button></div>',
        '<div class="arama">',
        '<input id="arama" type="search" placeholder="Materyal ara: ünite, konu, filozof, kazanım…" '
        'aria-label="Materyal ara">',
        '<div class="cips" role="group" aria-label="Filtreler">',
        '<button type="button" class="cip aktif" aria-pressed="true">Tümü</button>',
        '<button type="button" class="cip" data-g="10" aria-pressed="false">10. Sınıf</button>',
        '<button type="button" class="cip" data-g="11" aria-pressed="false">11. Sınıf</button>',
        '<button type="button" class="cip" data-k="unite" aria-pressed="false">Üniteler</button>',
        '<button type="button" class="cip" data-k="calisma-kagidi" aria-pressed="false">Çalışma Kâğıtları</button>',
        '<button type="button" class="cip" data-k="ek-soru-seti" aria-pressed="false">Ek Soru Setleri</button>',
        '<button type="button" class="cip" data-k="ortak-materyal" aria-pressed="false">Ortak Materyaller</button>',
        '<button type="button" class="cip" data-k="rapor" aria-pressed="false">Raporlar</button>',
        "</div></div>",
        '<div id="sonuclar" class="sonuclar" hidden aria-live="polite"></div>',
    ]
    for title, items in sections:
        parts.append('<section class="bolum">')
        parts.append(f"<h2>{escape(title)}</h2>")
        parts.append('<div class="cards">')
        parts += [card(href, item_title, subtitle, grade, kind) for href, item_title, subtitle, grade, kind in items]
        parts.append("</div></section>")
    parts.append("</main>")
    parts.append(
        f'<footer>{escape(SITE_NAME)} · Kaynak dosyalar ve sürüm geçmişi: '
        f'<a href="{REPO_URL}">GitHub deposunda</a> · '
        f'<a id="geri-bildirim" href="{escape(feedback_href(SITE_URL, SITE_NAME), quote=True)}">{FEEDBACK_LABEL}</a>.</footer>'
    )
    parts.append("</div>")
    parts.append(INDEX_SCRIPT)
    parts.append(TEMA_SCRIPT)
    parts.append("</body></html>")
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

    school_based = MUFREDAT / "okul-temelli-planlama.md"
    if school_based.exists():
        pages.append((school_based, SITE / "site" / "okul-temelli-planlama.html", "Programda ayrılmış 4 + 4 ders saati", "school"))

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
                (page_href(output), card_title(source, page_kind, grade), subtitle, grade.split("-")[0], KIND_TR[page_kind])
                for source, output, subtitle, page_kind in pages
                if page_kind == kind and output.relative_to(SITE).parts[1] == grade
            ]
            if items:
                sections.append((title, items))

    for kind, title in (("school", "Okul Temelli Planlama"), ("shared", "Ortak Materyaller"), ("report", "Denetim ve Durum Raporları")):
        items = [
            (page_href(output), page_title(source.read_text(encoding="utf-8"), humanize(source.stem)), subtitle, "", KIND_TR[page_kind])
            for source, output, subtitle, page_kind in pages
            if page_kind == kind
        ]
        if items:
            sections.append((title, items))

    return pages, sections


def build_search_index(
    pages: list[tuple[Path, Path, str, str]], sections: list[tuple[str, list]]
) -> str:
    """Ana sayfa araması için sayfa dizinini JSON olarak üretir."""
    sources = {page_href(output): source for source, output, _, _ in pages}
    entries = []
    for _, items in sections:
        for href, title, subtitle, grade, kind in items:
            entries.append(
                {
                    "t": title,
                    "s": subtitle,
                    "u": href,
                    "g": grade,
                    "k": kind,
                    "x": plain_text(sources[href].read_text(encoding="utf-8")),
                }
            )
    return json.dumps(entries, ensure_ascii=False, indent=1) + "\n"


def render_sitemap(pages: list[tuple[Path, Path, str, str]]) -> str:
    """Arama motorları için sitemap.xml üretir."""
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f"<url><loc>{SITE_URL}</loc></url>",
    ]
    for _, output, _, _ in pages:
        parts.append(f"<url><loc>{SITE_URL}{page_href(output)}</loc></url>")
    parts.append("</urlset>")
    return "\n".join(parts) + "\n"


def render_robots() -> str:
    """robots.txt üretir."""
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n"


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
    produced[SITE / "favicon.svg"] = FAVICON_SVG + "\n"
    produced[SITE / "arama-index.json"] = build_search_index(pages, sections)
    produced[SITE / "sitemap.xml"] = render_sitemap(pages)
    produced[SITE / "robots.txt"] = render_robots()
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
