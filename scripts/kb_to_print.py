#!/usr/bin/env python3
"""Render TG-PETPROJECT-KB.md into a printable PDF and a plain-text copy.

Usage:
    python3 kb_to_print.py TG-PETPROJECT-KB.md

Writes <name>.pdf (via headless Google Chrome) and <name>.txt next to the source.
The Markdown file stays the source of truth: it carries the grep-able statuses.
Plain text drops all markup so it reads cleanly in a Telegram preview.
"""
import html
import os
import re
import subprocess
import sys

STATUS = {
    "дословно": ("подтверждено дословно", "ok"),
    "пересказ агента": ("цитата пересказана агентом", "mid"),
    "связь слабая": ("связь с постом слабая", "weak"),
    "найдено поиском по тексту": ("источник найден поиском по словам", "rec"),
    "не сверено": ("не сверено", "no"),
}


def to_plain(md_text: str) -> str:
    out, n = [], 0
    for line in md_text.split("\n"):
        s = line.rstrip()
        if s.startswith("### "):
            out += ["", "=" * 70, s[4:].upper(), "=" * 70]
        elif s.startswith("## "):
            out += ["", "-" * 70, s[3:].upper(), "-" * 70]
        elif s.startswith("# "):
            out += ["", s[2:].upper(), "=" * len(s[2:])]
        elif s.startswith("- **Тезис.**"):
            n += 1
            out.append("")
            out.append(f"{n}. {s[len('- **Тезис.** '):]}")
        elif s.startswith("  - "):
            body = s.strip()[2:]
            if body.startswith("Сверка:"):
                v = body.split(":", 1)[1].strip()
                out.append(f"   Сверка: {STATUS.get(v, (v, ''))[0]}")
            elif body.startswith("⚠"):
                out.append(f"   ВНИМАНИЕ: {body.lstrip('⚠ ')}")
            else:
                out.append(f"   {body}")
        elif s.startswith("- "):
            body = re.sub(r"\*\*(.+?)\*\*", r"\1", s.strip()[2:]).replace("`", "")
            out.append(f"   • {body}")
        elif s.startswith("| "):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            out.append("   " + " | ".join(cells))
        elif s.strip():
            out.append(re.sub(r"\*\*(.+?)\*\*", r"\1", s).replace("`", ""))
    return "\n".join(out)


def to_html(md_text: str) -> str:
    out, in_list = [], False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in md_text.split("\n"):
        s = line.rstrip()
        if s.startswith("# "):
            close_list(); out.append(f"<h1>{html.escape(s[2:])}</h1>")
        elif s.startswith("## "):
            close_list(); out.append(f"<h2>{html.escape(s[3:])}</h2>")
        elif s.startswith("### "):
            close_list(); out.append(f"<h3>{html.escape(s[4:])}</h3>")
        elif s.startswith("- **Тезис.**"):
            if not in_list:
                out.append("<ul class='items'>"); in_list = True
            out.append(f"<li class='item'><span class='thesis'>{html.escape(s[len('- **Тезис.** '):])}</span>")
        elif s.startswith("  - "):
            body = s.strip()[2:]
            cls = ""
            m = re.match(r"Сверка:\s*(.+)", body)
            if m:
                cls = f" class='st {STATUS.get(m.group(1).strip(), ('no', 'no'))[1]}'"
            if body.startswith("⚠"):
                cls = " class='warn'"
            if body.startswith("Цитата"):
                cls = " class='quote'"
            if body.startswith("Источник"):
                cls = " class='src'"
            out.append(f"<div{cls}>{html.escape(body)}</div>")
        elif s.startswith("- "):
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{html.escape(s[2:])}</li>")
        elif s.strip():
            close_list(); out.append(f"<p>{html.escape(s)}</p>")
        else:
            close_list()
    close_list()
    return """<!doctype html><html lang="ru"><head><meta charset="utf-8">
<title>База знаний: практики соло-запуска</title><style>
@page { size: A4; margin: 16mm 14mm; }
body { font-family: "DejaVu Serif","Liberation Serif",Georgia,serif; font-size: 9.6pt; line-height: 1.45; color:#141414; }
h1 { font-family:"DejaVu Sans","Liberation Sans",sans-serif; font-size:20pt; margin:0 0 6pt; border-bottom:2px solid #333; padding-bottom:4pt; page-break-after:avoid; }
h2 { font-family:"DejaVu Sans","Liberation Sans",sans-serif; font-size:14pt; margin:16pt 0 6pt; border-bottom:1px solid #bbb; padding-bottom:2pt; page-break-after:avoid; }
h3 { font-family:"DejaVu Sans","Liberation Sans",sans-serif; font-size:12pt; margin:12pt 0 4pt; color:#333; page-break-after:avoid; }
ul.items { list-style:none; padding-left:0; }
li.item { margin:0 0 7pt; padding:5pt 7pt 5pt 8pt; border-left:3px solid #e0e0e0; page-break-inside:avoid; }
.thesis { font-weight:bold; }
.quote { font-family:"DejaVu Sans Mono","Liberation Mono",monospace; font-size:8.3pt; color:#1a2b45; margin:2pt 0 0 8pt; }
.src { font-size:8.4pt; color:#555; margin:2pt 0 0 8pt; }
.st { font-size:8.4pt; margin:2pt 0 0 8pt; }
.st.ok { color:#0a6b2d; } .st.mid { color:#8a5b00; } .st.weak { color:#8a2b00; } .st.rec { color:#00456b; } .st.no { color:#8a8a8a; }
.warn { font-size:8.4pt; color:#a3320b; margin:2pt 0 0 8pt; }
</style></head><body>""" + "".join(out) + "</body></html>"


def main() -> int:
    src = sys.argv[1] if len(sys.argv) > 1 else "TG-PETPROJECT-KB.md"
    md = open(src, encoding="utf-8-sig").read()
    base = os.path.splitext(src)[0]

    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(to_plain(md))

    html_path = base + ".print.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(to_html(md))

    chrome = ["google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
              f"--print-to-pdf={os.path.abspath(base + '.pdf')}",
              "--print-to-pdf-no-header", "--no-pdf-header-footer",
              f"file://{os.path.abspath(html_path)}"]
    subprocess.run(chrome, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for p in (base + ".txt", base + ".pdf"):
        print(f"{p}: {os.path.getsize(p)} bytes" if os.path.exists(p) else f"{p}: MISSING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
