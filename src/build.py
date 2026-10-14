"""Build every dataset file from src/scenario.py and src/comms.py.

Usage: uv run python src/build.py
Output is deterministic: running it twice gives identical files.
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import json
import random
import re
import shutil
import zipfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

import comms as C
import scenario as S

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dataset"
FIXED_TIME = dt.datetime(2026, 4, 1, 9, 0, 0)  # metadata timestamp for xlsx/pptx

GL_COLUMNS = ["entry_id", "posting_date", "period", "journal", "account", "account_name",
              "cost_centre", "counterparty", "document_ref", "description", "debit", "credit"]
JOURNAL = {"4": "SAL", "5": "PUR", "6": "PUR"}
COST_CENTRE = {"4000": "SALES", "4010": "SALES", "4020": "SALES", "5000": "PROD", "5010": "PROD",
               "5100": "PROD", "5110": "PROD", "5200": "LOG", "6000": "ADMIN", "6100": "ADMIN",
               "6200": "ADMIN", "6300": "ADMIN", "6400": "ADMIN"}
PAYROLL = {"5100", "6400"}


def party_name(pid):
    if pid is None:
        return ""
    if pid in S.PEOPLE:
        return S.PEOPLE[pid]["name"]
    return S.PARTIES[pid]["name"]


def email_of(pid):
    if pid in S.PEOPLE:
        return f'{S.PEOPLE[pid]["email"]}@{S.COMPANY["domain"]}'
    return S.PARTIES[pid]["email"]


def display_of(pid):
    if pid in S.PEOPLE:
        return f'{S.PEOPLE[pid]["name"]} <{email_of(pid)}>'
    p = S.PARTIES[pid]
    return f'{p.get("contact", p["name"])} ({p["name"]}) <{p["email"]}>'


def money(x):
    return f"{x:,.0f}"


def iso(date_str):
    """'2026-03-05 09:00' or '2026-03-05' -> ISO UTC string."""
    fmt = "%Y-%m-%d %H:%M" if " " in date_str else "%Y-%m-%d"
    d = dt.datetime.strptime(date_str, fmt)
    if " " not in date_str:
        d = d.replace(hour=9)
    return d.strftime("%Y-%m-%dT%H:%M:00Z")


def account_for_line(line):
    return next(a for a, v in S.ACCOUNTS.items() if v[1] == line)


# ---------------------------------------------------------------- figures

def pnl(month, source):
    """Return {line: amount} for actual or budget."""
    return dict((S.ACTUALS if source == "actual" else S.BUDGET)[month])


def ebitda(values):
    return sum(values[k] * S.LINE_SIGN[k] for k in values)


def variance_table(month):
    act, bud = pnl(month, "actual"), pnl(month, "budget")
    rows = []
    for code, name, sign in S.LINES:
        var = (act[code] - bud[code]) * sign
        rows.append({
            "line_code": code, "line_name": name, "actual": act[code], "budget": bud[code],
            "variance_favourable_positive": var,
            "variance_pct": round(var / bud[code] * 100, 1) if bud[code] else None,
            "above_threshold": abs(var) >= S.COMPANY["variance_threshold"],
        })
    return rows


# ---------------------------------------------------------------- general ledger

def month_days(month):
    y, m = map(int, month.split("-"))
    d = dt.date(y, m, 1)
    days = []
    while d.month == m:
        if d.weekday() < 5:
            days.append(d)
        d += dt.timedelta(days=1)
    return days


def split_amount(rng, total_cents, n):
    if n == 1:
        return [total_cents]
    weights = [rng.uniform(0.6, 1.4) for _ in range(n)]
    s = sum(weights)
    parts = [int(total_cents * w / s) for w in weights]
    parts[-1] += total_cents - sum(parts)
    return parts


def build_gl(month):
    rng = random.Random(f"pipeline-{month}")
    rows = []
    stories = [t for t in S.STORY_TX if t["month"] == month]
    for account, (acc_name, line, since) in S.ACCOUNTS.items():
        if month < since:
            continue
        sign = S.LINE_SIGN[line]
        target = round(S.ACTUALS[month][line] * 100)
        story_net = 0
        for t in stories:
            if t["account"] != account:
                continue
            cents = round(t["amount"] * 100)
            credit_note = t.get("credit_note", False)
            if sign == 1:
                debit, credit = 0, cents
                story_net += cents
            elif credit_note:
                debit, credit = 0, cents
                story_net -= cents
            else:
                debit, credit = cents, 0
                story_net += cents
            rows.append({"date": t["date"], "account": account, "party": t["party"], "doc": t["doc"],
                         "desc": t["desc"], "debit": debit, "credit": credit})
        filler = target - story_net
        assert filler > 0, (month, account, filler)
        parties = [p for p in S.FILLER_PARTIES[account] if (month, account, p) not in S.NO_FILLER]
        n = S.FILLER_COUNT[account]
        days = month_days(month)
        for i, cents in enumerate(split_amount(rng, filler, n)):
            party = parties[i % len(parties)]
            if account in PAYROLL:
                day = days[-1]
            elif account in {"6200"}:
                day = days[0]
            else:
                day = days[min(len(days) - 1, int((i + rng.random()) * len(days) / n))]
            doc = (f"PAY-{month.replace('-', '')}-{i + 1}" if account in PAYROLL else
                   f"SI-{month[2:4]}{month[5:7]}{rng.randint(100, 999)}" if sign == 1 else
                   f"PI-{month[2:4]}{month[5:7]}{rng.randint(1000, 9999)}")
            debit, credit = (0, cents) if sign == 1 else (cents, 0)
            rows.append({"date": day.isoformat(), "account": account, "party": party, "doc": doc,
                         "desc": S.FILLER_DESC[account], "debit": debit, "credit": credit})
    rows.sort(key=lambda r: (r["date"], r["account"], r["doc"]))
    out = []
    for i, r in enumerate(rows, start=1):
        out.append({
            "entry_id": f"JE-{month.replace('-', '')}-{i:04d}",
            "posting_date": r["date"], "period": month,
            "journal": "PAY" if r["account"] in PAYROLL else JOURNAL[r["account"][0]],
            "account": r["account"], "account_name": S.ACCOUNTS[r["account"]][0],
            "cost_centre": COST_CENTRE[r["account"]], "counterparty": party_name(r["party"]),
            "document_ref": r["doc"], "description": r["desc"],
            "debit": f'{r["debit"] / 100:.2f}', "credit": f'{r["credit"] / 100:.2f}',
        })
    return out


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def build_invalid_march(gl):
    """Simulate a bad merge of the split export plus a locale-formatted amount."""
    rows = [dict(r) for r in gl]
    dup = next(r for r in rows if r["document_ref"] == "AFS-0326-A")  # posted on the 14th (boundary day)
    idx = rows.index(dup)
    rows.insert(idx + 1, dict(dup))
    bad = next(r for r in rows if r["account"] == "6300")
    value = float(bad["debit"])
    whole, frac = f"{value:.2f}".split(".")
    bad["debit"] = f"{int(whole):,}".replace(",", ".") + "," + frac
    return rows, {"duplicate_entry_id": dup["entry_id"], "malformed_entry_id": bad["entry_id"],
                  "malformed_value": bad["debit"]}


def normalize_zip(path):
    """Rewrite an Office file with fixed ZIP timestamps so builds are byte-identical."""
    with zipfile.ZipFile(path) as src:
        members = [(i, src.read(i.filename)) for i in src.infolist()]
    with zipfile.ZipFile(path, "w") as dst:
        for info, data in members:
            if info.filename == "docProps/core.xml":  # openpyxl stamps the save time here
                stamp = FIXED_TIME.strftime("%Y-%m-%dT%H:%M:%SZ").encode()
                data = re.sub(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*(<)", rb"\g<1>" + stamp + rb"\g<2>", data)
            fixed = zipfile.ZipInfo(info.filename, date_time=FIXED_TIME.timetuple()[:6])
            fixed.compress_type = zipfile.ZIP_DEFLATED
            fixed.external_attr = 0o644 << 16
            dst.writestr(fixed, data)


# ---------------------------------------------------------------- workbooks

HEADER_FILL = PatternFill("solid", fgColor="1F3A5F")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def style_header(ws, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill, cell.font = HEADER_FILL, HEADER_FONT
    ws.freeze_panes = "A2"


def autosize(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def set_wb_meta(wb, title):
    wb.properties.creator = "Claire Donnelly"
    wb.properties.title = title
    wb.properties.created = FIXED_TIME
    wb.properties.modified = FIXED_TIME


def build_budget_xlsx(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Budget_2026"
    ws.append(["line_code", "line_name"] + S.BUDGET_MONTHS + ["FY2026"])
    for code, name, _ in S.LINES:
        vals = [S.BUDGET[m][code] for m in S.BUDGET_MONTHS]
        ws.append([code, name] + vals + [sum(vals)])
    ws.append(["EBITDA", "EBITDA"] + [ebitda(S.BUDGET[m]) for m in S.BUDGET_MONTHS]
              + [sum(ebitda(S.BUDGET[m]) for m in S.BUDGET_MONTHS)])
    style_header(ws, 15)
    autosize(ws, [14, 28] + [11] * 13)
    a = wb.create_sheet("Assumptions")
    a.append(["#", "Budget assumption (approved December 2025)"])
    for i, t in enumerate(S.BUDGET_ASSUMPTIONS, 1):
        a.append([i, t])
    style_header(a, 2)
    autosize(a, [4, 110])
    set_wb_meta(wb, "Budget 2026")
    wb.save(path)
    normalize_zip(path)


def build_closing_workbook(path, month, gl, commentary_rows, mapping, status):
    wb = Workbook()
    ws = wb.active
    ws.title = "README"
    for line in [
        f"Pipeline Office Systems - monthly close workbook - {month}",
        f"Status: {status}",
        "",
        "Steps (as done by Claire Donnelly, Financial Controller):",
        "1. Export GL detail for the month from the ERP (P&L accounts 4000-6999).",
        "2. Paste the export into GL_import (replace last month's rows).",
        "3. Check Mapping: no account may show UNMAPPED in GL_import column M.",
        "4. Check total: sum of net in GL_import equals the ERP P&L total.",
        "5. Review PnL_vs_Budget; every line with |variance| >= 5,000 EUR needs a comment.",
        "6. Write the explanations in Commentary, with the source of each explanation.",
        "7. Update the management pack slides and send to the CFO.",
        "",
        "Sign convention: variance > 0 is favourable, < 0 is adverse.",
        "Fictional data for the 42 Paris x screenpipe hackathon.",
    ]:
        ws.append([line])
    ws["A1"].font = Font(bold=True, size=14)
    autosize(ws, [100])

    g = wb.create_sheet("GL_import")
    g.append(GL_COLUMNS + ["line_code", "net"])
    for i, r in enumerate(gl, start=2):
        g.append([r[c] if c not in ("debit", "credit") else float(r[c]) for c in GL_COLUMNS]
                 + [f'=IFERROR(VLOOKUP(E{i},Mapping!$A:$B,2,FALSE),"UNMAPPED")', f"=L{i}-K{i}"])
    style_header(g, 14)
    autosize(g, [16, 12, 9, 8, 9, 34, 8, 26, 15, 46, 12, 12, 14, 12])

    m = wb.create_sheet("Mapping")
    m.append(["account", "line_code", "line_name"])
    for acc, line in sorted(mapping.items()):
        m.append([acc, line, S.LINE_NAME[line]])
    style_header(m, 3)
    autosize(m, [10, 16, 30])

    p = wb.create_sheet("PnL_vs_Budget")
    p.append(["line_code", "line_name", "sign", "actual", "budget", "variance (fav +)", "variance %", "comment needed"])
    n = len(gl) + 1
    for i, (code, name, sign) in enumerate(S.LINES, start=2):
        p.append([code, name, sign,
                  f"=SUMIFS(GL_import!$N$2:$N${n},GL_import!$M$2:$M${n},A{i})*C{i}",
                  S.BUDGET[month][code],
                  f"=(D{i}-E{i})*C{i}",
                  f'=IF(E{i}=0,"",F{i}/E{i})',
                  f'=IF(ABS(F{i})>={S.COMPANY["variance_threshold"]},"YES","")'])
    last = len(S.LINES) + 1
    u = last + 1
    p.append(["UNMAPPED", "Accounts missing from Mapping", 1,
              f'=SUMIFS(GL_import!$N$2:$N${n},GL_import!$M$2:$M${n},"UNMAPPED")', 0, f"=D{u}", "",
              f'=IF(D{u}<>0,"FIX MAPPING","")'])
    e = u + 1
    p.append(["EBITDA", "EBITDA", 1, f"=SUMPRODUCT(D2:D{u},C2:C{u})", f"=SUMPRODUCT(E2:E{last},C2:C{last})",
              f"=D{e}-E{e}", f'=IF(E{e}=0,"",F{e}/E{e})', ""])
    for row in p.iter_rows(min_row=2, min_col=4, max_col=6):
        for cell in row:
            cell.number_format = "#,##0;[Red]-#,##0"
    for row in p.iter_rows(min_row=2, min_col=7, max_col=7):
        for cell in row:
            cell.number_format = "0.0%"
    style_header(p, 8)
    autosize(p, [14, 30, 6, 13, 13, 15, 11, 15])

    c = wb.create_sheet("Commentary")
    c.append(["line_code", "line_name", "variance (fav +)", "explanation", "repeats next month?", "source"])
    for r in commentary_rows:
        c.append([r["line_code"], S.LINE_NAME[r["line_code"]], r["variance"], r["explanation"], r["repeats"], r["source"]])
    for row in c.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    style_header(c, 6)
    autosize(c, [14, 26, 15, 70, 18, 40])
    set_wb_meta(wb, f"Close {month}")
    wb.save(path)
    normalize_zip(path)


# ---------------------------------------------------------------- commentary (validated months)

def commentary(month):
    vt = {r["line_code"]: r for r in variance_table(month)}
    if month == "2026-01":
        material = []
        notes = [
            ("FREIGHT", vt["FREIGHT"]["variance_favourable_positive"], "Winter fuel surcharge from Atlantic Freight in January (below threshold, no comment required).", "Possibly in February", "Atlantic Freight January invoices"),
            ("ENERGY", vt["ENERGY"]["variance_favourable_positive"], "Cold January, higher heating in the workshop (below threshold).", "No", "Celtic Energy January invoice"),
        ]
    else:  # 2026-02
        material = [
            ("MAT_TIMBER", vt["MAT_TIMBER"]["variance_favourable_positive"],
             "Brightwood Timber price list +8% on veneer panels from 1 February 2026 (letter of 28 January). About EUR 12k per month at normal volume. Niamh is negotiating a volume rebate.",
             "Yes, every month until a rebate or a new supplier", "Email E01 (Brightwood, 28 Jan) and E02 (Niamh, 29 Jan); GL account 5000, invoices BW-INV-10588/10631/10690"),
        ]
        notes = []
    rows = [{"line_code": a, "variance": b, "explanation": c, "repeats": d, "source": e} for a, b, c, d, e in material + notes]
    return rows


def commentary_md(month, rows):
    vt = variance_table(month)
    act, bud = ebitda(S.ACTUALS[month]), ebitda(S.BUDGET[month])
    label = dt.datetime.strptime(month, "%Y-%m").strftime("%B %Y")
    lines = [f"# Monthly commentary - {label}", "",
             "Fictional company (Pipeline Furniture Ltd). Validated by the CFO.", "",
             f"EBITDA EUR {money(act)} vs budget EUR {money(bud)} ({act - bud:+,.0f}).", ""]
    material = [r for r in vt if r["above_threshold"]]
    if not material:
        lines.append("No P&L line is above the EUR 5,000 threshold this month.")
    for r in rows:
        if abs(r["variance"]) >= S.COMPANY["variance_threshold"]:
            lines += [f"## {S.LINE_NAME[r['line_code']]}: {r['variance']:+,.0f}", "", r["explanation"], "",
                      f"- Repeats next month: {r['repeats']}", f"- Source: {r['source']}", ""]
    others = [r for r in rows if abs(r["variance"]) < S.COMPANY["variance_threshold"]]
    if others:
        lines += ["", "## Notes below threshold", ""]
        lines += [f"- {S.LINE_NAME[r['line_code']]} {r['variance']:+,.0f}: {r['explanation']}" for r in others]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- presentations
# Corporate look of the fictional Pipeline Furniture: navy, teal accent, Arial.

PX = 6350  # EMU per pixel of a 1920x1080 canvas
M = 112
CW = 1920 - 2 * M
P_NAVY, P_TEAL, P_INK, P_BODY, P_MUTED = "1F3A5F", "1E7F74", "1B2733", "3B4856", "6B7785"
P_BG, P_PANEL, P_ZEBRA, P_LINE = "F7F9FB", "E9EEF3", "F0F4F7", "C9D3DD"


def _rgb(h):
    return RGBColor.from_string(h)


def _text(s, x, y, w, h, paras, size, color, bold=False, align=PP_ALIGN.LEFT, spacing=1.15):
    box = s.shapes.add_textbox(Emu(x * PX), Emu(y * PX), Emu(w * PX), Emu(h * PX))
    tf = box.text_frame
    tf.word_wrap = True
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, 0)
    for i, para in enumerate([paras] if isinstance(paras, str) else paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.line_spacing = align, spacing
        for t, b in ([(para, bold)] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = t
            r.font.name, r.font.size, r.font.bold = "Arial", Pt(size / 2), b
            r.font.color.rgb = _rgb(color)
    return box


def _rect(s, x, y, w, h, fill):
    shape = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(x * PX), Emu(y * PX), Emu(w * PX), Emu(h * PX))
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(fill)
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _new(prs, bg=P_BG):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = _rgb(bg)
    return s


def _content(prs, title, subtitle=None):
    s = _new(prs)
    _rect(s, 0, 0, 1920, 16, P_NAVY)
    _text(s, M, 80, CW, 70, title, 56, P_NAVY, bold=True)
    _rect(s, M, 168, 96, 6, P_TEAL)
    if subtitle:
        _text(s, M, 196, CW, 40, subtitle, 28, P_MUTED)
    n = len(prs.slides)
    _text(s, M, 1080 - 70, CW - 100, 30, "Pipeline Furniture Ltd - Finance - fictional data for the 42 Paris x screenpipe hackathon", 20, P_MUTED)
    _text(s, 1920 - M - 80, 1080 - 70, 80, 30, str(n), 20, P_MUTED, align=PP_ALIGN.RIGHT)
    return s


def add_title(prs, title, subtitle, eyebrow):
    s = _new(prs, P_NAVY)
    _rect(s, 0, 0, 24, 1080, P_TEAL)
    _text(s, 160, 330, 1600, 40, eyebrow.upper(), 28, "8FD3C9", bold=True)
    _text(s, 160, 390, 1600, 200, title, 88, "FFFFFF", bold=True, spacing=1.05)
    _text(s, 160, 620, 1600, 60, subtitle, 32, "C9D6E3")
    _text(s, 160, 960, 1600, 30, "Pipeline Furniture Ltd - fictional company", 20, "9FB2C6")
    return s


def add_bullets(prs, title, bullets, subtitle=None):
    s = _content(prs, title, subtitle)
    y = 290
    for b in bullets:
        _rect(s, M, y + 14, 12, 12, P_TEAL)
        lines = -(-len(b) // 110)
        _text(s, M + 40, y, CW - 40, 50 * lines, b, 32, P_BODY, spacing=1.25)
        y += 50 * lines + 26
    return s


def add_kpis(prs, title, tiles, subtitle=None, note=None):
    s = _content(prs, title, subtitle)
    n = len(tiles)
    tw = (CW - (n - 1) * 32) // n
    for i, (label, value, detail) in enumerate(tiles):
        x = M + i * (tw + 32)
        _rect(s, x, 300, tw, 300, "FFFFFF")
        _rect(s, x, 300, tw, 8, P_TEAL if i < n - 1 else P_NAVY)
        _text(s, x + 40, 340, tw - 80, 40, label, 26, P_MUTED, bold=True)
        _text(s, x + 40, 400, tw - 80, 90, value, 72, P_INK, bold=True)
        _text(s, x + 40, 510, tw - 80, 60, detail, 26, P_BODY)
    if note:
        _rect(s, M, 660, CW, 2, P_LINE)
        _text(s, M, 700, CW, 200, note, 30, P_BODY, spacing=1.3)
    return s


def add_table(prs, title, header, rows, widths, subtitle=None, size=24, row_h=52, bold_last=False, numeric_from=1):
    s = _content(prs, title, subtitle)
    shape = s.shapes.add_table(len(rows) + 1, len(header), Emu(M * PX), Emu(250 * PX), Emu(CW * PX), Emu(row_h * (len(rows) + 1) * PX))
    t = shape.table
    for j, frac in enumerate(widths):
        t.columns[j].width = Emu(int(CW * frac) * PX)
    for i, row in enumerate([header] + rows):
        t.rows[i].height = Emu(row_h * PX)
        last = bold_last and i == len(rows)
        for j, v in enumerate(row):
            cell = t.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = _rgb(P_NAVY if i == 0 else (P_PANEL if last else ("FFFFFF" if i % 2 else P_ZEBRA)))
            cell.margin_left = cell.margin_right = Emu(16 * PX)
            cell.margin_top = cell.margin_bottom = 0
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT if j >= numeric_from else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = str(v)
            r.font.name, r.font.size = "Arial", Pt(size / 2)
            r.font.bold = i == 0 or last
            r.font.color.rgb = _rgb("FFFFFF" if i == 0 else P_INK)
    return s


def add_comment_cards(prs, title, items, subtitle=None):
    s = _content(prs, title, subtitle)
    y = 280
    for head, value, body, repeat in items:
        _rect(s, M, y, CW, 230, "FFFFFF")
        _rect(s, M, y, 10, 230, P_TEAL)
        _text(s, M + 48, y + 28, 1100, 44, head, 36, P_NAVY, bold=True)
        _text(s, M + CW - 360, y + 28, 320, 44, value, 36, P_INK, bold=True, align=PP_ALIGN.RIGHT)
        _text(s, M + 48, y + 84, CW - 96, 80, body, 26, P_BODY, spacing=1.2)
        _text(s, M + 48, y + 180, CW - 96, 34, f"Repeats next month: {repeat}", 24, P_TEAL, bold=True)
        y += 260
    return s


def add_todo(prs, title, text_):
    s = _content(prs, title)
    box = _rect(s, M, 300, CW, 360, "FFFFFF")
    box.line.color.rgb = _rgb(P_LINE)
    box.line.dash_style = 4
    box.line.width = Emu(3 * PX)
    _text(s, M + 64, 420, CW - 128, 140, text_, 36, P_MUTED, align=PP_ALIGN.CENTER)
    return s


def set_prs_meta(prs, title):
    prs.core_properties.author = "Claire Donnelly"
    prs.core_properties.title = title
    prs.core_properties.created = FIXED_TIME
    prs.core_properties.modified = FIXED_TIME
    prs.core_properties.last_modified_by = "Claire Donnelly"
    prs.core_properties.revision = 1


def _prs():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(1920 * PX), Emu(1080 * PX)
    return prs


def pnl_rows(month):
    rows = []
    for r in variance_table(month):
        rows.append([r["line_name"], money(r["actual"]), money(r["budget"]), f'{r["variance_favourable_positive"]:+,.0f}',
                     "Comment" if r["above_threshold"] else ""])
    a, b = ebitda(S.ACTUALS[month]), ebitda(S.BUDGET[month])
    rows.append(["EBITDA", money(a), money(b), f"{a - b:+,.0f}", ""])
    return rows


def build_budget_deck(path):
    prs = _prs()
    add_title(prs, "Budget 2026", "Board meeting, 16 December 2025", "Pipeline Furniture Ltd - Finance")
    fy = {code: sum(S.BUDGET[m][code] for m in S.BUDGET_MONTHS) for code, _, _ in S.LINES}
    rev = sum(v for c, v in fy.items() if S.LINE_SIGN[c] == 1)
    fy_e = sum(ebitda(S.BUDGET[m]) for m in S.BUDGET_MONTHS)
    add_kpis(prs, "FY2026 at a glance", [
        ("REVENUE", f"{rev / 1e6:.1f}M", "EUR, contract and dealer channels"),
        ("EBITDA", f"{fy_e / 1e6:.2f}M", f"EUR, {fy_e / rev * 100:.1f}% of revenue"),
        ("MONTHLY EBITDA", f"{ebitda(S.BUDGET['2026-01']) / 1000:.0f}k", "EUR, flat profile (April: KPC kickoff)"),
    ], "All figures in EUR", note="A flat monthly plan: timber prices held at the 2025 list, temporary labour limited to holiday cover, the new web shop not budgeted.")
    rows = [[S.LINE_NAME[c], money(v), money(v / 12)] for c, v in fy.items()]
    rows.append(["EBITDA", money(fy_e), money(fy_e / 12)])
    add_table(prs, "FY2026 budget by P&L line", ["P&L line", "FY2026", "Per month (avg)"], rows, [0.56, 0.22, 0.22],
              "EUR", size=20, row_h=42, bold_last=True)
    add_bullets(prs, "Key assumptions", S.BUDGET_ASSUMPTIONS)
    add_bullets(prs, "Reporting rules", [
        "Monthly management pack sent to the CFO by working day 5.",
        "Every P&L line with a variance of EUR 5,000 or more is explained: the cause, and whether it repeats next month.",
        "Variances are shown favourable positive, adverse negative.",
    ])
    set_prs_meta(prs, "Budget 2026")
    prs.save(path)
    normalize_zip(path)


SUMMARY_NOTE = {
    "2026-01": "A quiet month: EBITDA 7k below budget, spread across small items. No line above the EUR 5,000 threshold.",
    "2026-02": "EBITDA 11.2k below budget, almost entirely timber: Brightwood's +8% price list applies from 1 February.",
    "2026-03": "EBITDA 47.1k below budget with seven lines above the threshold. Commentary in progress.",
}


def build_pack(path, month, rows, draft=False):
    label = dt.datetime.strptime(month, "%Y-%m").strftime("%B %Y")
    prs = _prs()
    add_title(prs, f"Management pack - {label}", "DRAFT - commentary to be written" if draft else "Prepared by Claire Donnelly, Financial Controller",
              "Pipeline Furniture Ltd - Finance")
    a, b = ebitda(S.ACTUALS[month]), ebitda(S.BUDGET[month])
    rev_a = sum(S.ACTUALS[month][c] for c, _, s in S.LINES if s == 1)
    rev_b = sum(S.BUDGET[month][c] for c, _, s in S.LINES if s == 1)
    n_mat = sum(1 for r in variance_table(month) if r["above_threshold"])
    add_kpis(prs, "Summary", [
        ("EBITDA", f"{a / 1000:.1f}k", f"vs budget {b / 1000:.1f}k ({(a - b) / 1000:+.1f}k)"),
        ("REVENUE", f"{rev_a / 1e6:.2f}M", f"vs budget {rev_b / 1e6:.2f}M ({(rev_a - rev_b) / 1000:+.1f}k)"),
        ("LINES TO EXPLAIN", str(n_mat), "variance of EUR 5,000 or more"),
    ], f"{label} - EUR", note=SUMMARY_NOTE[month])
    add_table(prs, "P&L vs budget", ["P&L line", "Actual", "Budget", "Variance (fav +)", "Over 5k"], pnl_rows(month),
              [0.36, 0.16, 0.16, 0.18, 0.14], f"{label} - EUR - favourable variances are positive", size=20, row_h=40, bold_last=True)
    if draft:
        add_todo(prs, "Variance commentary", "To do: explain every line marked Comment, with the cause, the source and whether it repeats next month.")
    else:
        material = [r for r in rows if abs(r["variance"]) >= S.COMPANY["variance_threshold"]]
        if material:
            add_comment_cards(prs, "Variance commentary", [
                (S.LINE_NAME[r["line_code"]], f'{r["variance"]:+,.0f}', r["explanation"], r["repeats"]) for r in material])
        else:
            notes = [f'{S.LINE_NAME[r["line_code"]]} {r["variance"]:+,.0f}: {r["explanation"]}' for r in rows]
            add_bullets(prs, "Variance commentary", ["No line above the EUR 5,000 threshold this month."] + notes)
        outlook = {
            "2026-01": ["No recurring issue identified.", "Watch: Brightwood Timber announced a +8% price list from 1 February."],
            "2026-02": ["Brightwood +8% will repeat every month (about EUR 12k per month).",
                        "March: Belvedere order BHG-2291 (EUR 45k) planned for delivery."],
        }[month]
        add_bullets(prs, "Outlook", outlook)
    set_prs_meta(prs, f"Management pack {month}")
    prs.save(path)
    normalize_zip(path)


# ---------------------------------------------------------------- documents and viewer

def doc_html(d):
    rows = "".join("<tr>" + "".join(f"<{'th' if i == 0 else 'td'}>{html.escape(c)}</{'th' if i == 0 else 'td'}>" for c in r) + "</tr>"
                   for i, r in enumerate(d["rows"]))
    party = S.PARTIES[d["party"]]["name"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(d['title'])}</title>
<style>body{{font-family:Georgia,serif;max-width:760px;margin:40px auto;padding:0 16px;color:#222;background:#fff}}
table{{border-collapse:collapse;width:100%;margin:24px 0}}th,td{{border:1px solid #bbb;padding:8px;text-align:left}}th{{background:#eee}}
.meta{{color:#555}}.fict{{margin-top:48px;font-size:12px;color:#888}}</style></head><body>
<h1>{html.escape(party)}</h1><h2>{html.escape(d['title'])}</h2>
<p class="meta">Date: {d['date']} &middot; Customer: Pipeline Furniture Ltd, Cork</p>
<table>{rows}</table><p>{html.escape(d['note'])}</p>
<p class="fict">Fictional document created for the 42 Paris x screenpipe hackathon.</p></body></html>
"""


def eml(e):
    to = ", ".join(display_of(p) for p in e["to"])
    cc = ", ".join(display_of(p) for p in e.get("cc", []))
    d = dt.datetime.strptime(e["date"], "%Y-%m-%d %H:%M")
    att = ""
    if e.get("attachments"):
        att = "\n\nAttachments: " + ", ".join(e["attachments"])
    headers = [f"From: {display_of(e['from'])}", f"To: {to}"]
    if cc:
        headers.append(f"Cc: {cc}")
    headers += [f"Subject: {e['subject']}", f"Date: {d.strftime('%a, %d %b %Y %H:%M:00 +0000')}",
                f"Message-ID: <{e['id'].lower()}@{S.COMPANY['domain']}>", "MIME-Version: 1.0",
                "Content-Type: text/plain; charset=utf-8", "X-Dataset: fictional (42 Paris x screenpipe hackathon)"]
    return "\n".join(headers) + "\n\n" + e["body"] + att + "\n"


def viewer_data(gls):
    return {
        "company": S.COMPANY,
        "people": {k: {"name": v["name"], "role": v["role"], "email": email_of(k)} for k, v in S.PEOPLE.items()},
        "parties": {k: {"name": v["name"], "type": v["type"]} for k, v in S.PARTIES.items()},
        "emails": [dict(e, from_display=display_of(e["from"]), to_display=[display_of(p) for p in e["to"]],
                        cc_display=[display_of(p) for p in e.get("cc", [])]) for e in sorted(C.EMAILS, key=lambda x: x["date"], reverse=True)],
        "channels": C.CHANNELS,
        "chats": [dict(c, author_name=S.PEOPLE[c["author"]]["name"]) for c in sorted(C.CHATS, key=lambda x: x["date"])],
        "meetings": [{"id": m["id"], "date": m["date"], "title": m["title"],
                      "attendees": [S.PEOPLE[a]["name"] for a in m["attendees"]],
                      "lines": [{"speaker": S.PEOPLE[s]["name"], "text": t} for s, t in m["lines"]]} for m in C.MEETINGS],
        "documents": [{"id": d["id"], "date": d["date"], "title": d["title"], "file": f"../documents/{d['id']}.html"} for d in C.DOCUMENTS],
        "gl": gls,
        "lines": [{"code": c, "name": n, "sign": s} for c, n, s in S.LINES],
        "accounts": {a: {"name": v[0], "line": v[1]} for a, v in S.ACCOUNTS.items()},
    }


# ---------------------------------------------------------------- screenpipe-style records

def rec(rid, ts, app, text):
    return {"id": rid, "timestamp": ts, "app": app, "text": text}


def feb_close_session():
    gl = len(build_gl("2026-02"))
    vt = {r["line_code"]: r for r in variance_table("2026-02")}
    e = ebitda(S.ACTUALS["2026-02"])
    return [
        rec("f01", "2026-03-02T08:40:00Z", "Pipeline ERP", "Reports > GL detail export. Period 2026-02, accounts 4000 to 6999. Export started for 01/02/2026 - 28/02/2026."),
        rec("f02", "2026-03-02T08:42:00Z", "Pipeline ERP", "Error: request timed out after 120 s. Export not completed."),
        rec("f03", "2026-03-02T08:44:00Z", "Mail", "Searched mail for 'export timing out'. Opened Mark Fallon's email of 27 Feb: export 1-14 and 15-end of month separately and merge, do not paste the boundary day twice."),
        rec("f04", "2026-03-02T08:51:00Z", "Pipeline ERP", f"Exported 01/02-14/02 and 15/02-28/02. Merged into gl_2026-02.csv: {gl} rows, columns entry_id, posting_date, period, journal, account, account_name, cost_centre, counterparty, document_ref, description, debit, credit."),
        rec("f05", "2026-03-02T08:58:00Z", "Excel", f"closing_workbook_2026-02.xlsx, tab GL_import: deleted January rows, pasted {gl} February rows. Formulas in columns M (line_code) and N (net) copied down."),
        rec("f06", "2026-03-02T09:03:00Z", "Excel", "Tab Mapping checked: filter column M on UNMAPPED in GL_import returns 0 rows. All accounts mapped."),
        rec("f07", "2026-03-02T09:06:00Z", "Excel", "Check: sum of net in GL_import matches the ERP P&L total for February. OK."),
        rec("f08", "2026-03-02T09:10:00Z", "Excel", f"Tab PnL_vs_Budget refreshed. EBITDA actual {money(e)} vs budget {money(ebitda(S.BUDGET['2026-02']))}."),
        rec("f09", "2026-03-02T09:12:00Z", "Excel", f"Filter comment needed = YES: 1 line. Timber & panels {vt['MAT_TIMBER']['variance_favourable_positive']:+,.0f}."),
        rec("f10", "2026-03-02T09:20:00Z", "Excel", "GL_import filtered on account 5000 and counterparty Brightwood Timber Ltd: 3 invoices BW-INV-10588, BW-INV-10631, BW-INV-10690, description 'price list 2026-02', total 156,600.00."),
        rec("f11", "2026-03-02T09:26:00Z", "Mail", "Searched mail for 'Brightwood'. Found E01 (Brightwood price list +8% from 1 February) and E02 (Niamh: about EUR 12k a month, rebate requested)."),
        rec("f12", "2026-03-02T09:31:00Z", "Browser", "Opened news site during the close. Not related to the procedure."),
        rec("f13", "2026-03-02T09:40:00Z", "Excel", "Tab Commentary: Timber & panels -11,600. Brightwood Timber price list +8% from 1 February (letter of 28 January). Repeats every month until a rebate or a new supplier. Source: E01, E02, GL 5000."),
        rec("f14", "2026-03-02T09:44:00Z", "Mail", "Reopened Tom Avery's email of 5 Feb: comment every line above EUR 5,000, nothing below. No other comment written."),
        rec("f15", "2026-03-03T10:05:00Z", "PowerPoint", "management_pack_2026-02.pptx: updated Summary, P&L vs budget table and Variance commentary slides from the workbook."),
        rec("f16", "2026-03-04T18:22:00Z", "Mail", "Sent 'February management pack' to Tom Avery with management_pack_2026-02.pptx attached."),
        rec("f17", "2026-03-04T18:30:00Z", "Chat", "Posted in #finance-close: February close done, pack sent to Tom. Only material line: timber (Brightwood +8%)."),
    ]


def mar_close_session():
    gl = len(build_gl("2026-03"))
    vt = variance_table("2026-03")
    n_mat = sum(1 for r in vt if r["above_threshold"])
    return [
        rec("m01", "2026-04-02T08:35:00Z", "Pipeline ERP", "Reports > GL detail export. Period 2026-03. Exported 01/03-14/03 and 15/03-31/03 separately (timeout workaround)."),
        rec("m02", "2026-04-02T08:47:00Z", "Pipeline ERP", f"Merged into gl_2026-03.csv: {gl} rows. Checked that no entry of 14 March appears twice."),
        rec("m03", "2026-04-02T08:55:00Z", "Excel", f"closing_workbook_2026-03.xlsx, tab GL_import: deleted February rows, pasted {gl} March rows."),
        rec("m04", "2026-04-02T09:01:00Z", "Excel", "Filter column M on UNMAPPED: 6 rows, account 4020 Sales - online web shop, total 6,400.00. PnL_vs_Budget shows FIX MAPPING."),
        rec("m05", "2026-04-02T09:04:00Z", "Mail", "Read Ellen Walsh's email: account 4020 opened on 1 March for the new web shop, not in the mapping tab yet."),
        rec("m06", "2026-04-02T09:08:00Z", "Excel", "Tab Mapping: added account 4020 -> REV_ONLINE (Revenue - Online). UNMAPPED now returns 0 rows."),
        rec("m07", "2026-04-02T09:11:00Z", "Excel", "Check: sum of net in GL_import matches the ERP P&L total for March. OK."),
        rec("m08", "2026-04-02T09:15:00Z", "Excel", f"Tab PnL_vs_Budget refreshed. EBITDA actual {money(ebitda(S.ACTUALS['2026-03']))} vs budget {money(ebitda(S.BUDGET['2026-03']))}. Comment needed = YES on {n_mat} lines."),
        rec("m09", "2026-04-02T09:40:00Z", "Excel", "GL_import filtered on account 5000, Brightwood Timber Ltd: 3 invoices, price list 2026-02, total 162,000.00. Same cause as February."),
        rec("m10", "2026-04-02T10:30:00Z", "Mail", "Searched mail for 'Belvedere', 'StaffBridge', 'Celtic', 'KPC', 'Atlantic'. Found E06, E07, E09, E10, E11, E14."),
        rec("m11", "2026-04-02T11:15:00Z", "Excel", "Atlantic Freight: 3 lines 'Surcharge - service code EXP', 6,200.00 in total. No email or chat explains why. Left as open question."),
        rec("m12", "2026-04-03T09:50:00Z", "Excel", "Tab Commentary: wrote explanations for 7 lines above threshold, with sources."),
        rec("m13", "2026-04-03T16:30:00Z", "PowerPoint", "management_pack_2026-03.pptx: updated Summary, P&L vs budget and Variance commentary slides."),
    ]


def task_runs():
    runs = [
        ("Export GL detail from ERP", [("close-2026-01", 22), ("close-2026-02", 48), ("close-2026-03", 41)]),
        ("Paste export into closing workbook", [("close-2026-01", 14), ("close-2026-02", 13), ("close-2026-03", 15)]),
        ("Check mapping and control totals", [("close-2026-01", 18), ("close-2026-02", 17), ("close-2026-03", 34)]),
        ("Investigate variances above threshold", [("close-2026-01", 35), ("close-2026-02", 85), ("close-2026-03", 230)]),
        ("Write monthly commentary", [("close-2026-01", 30), ("close-2026-02", 45), ("close-2026-03", 95)]),
        ("Update management pack slides", [("close-2026-01", 40), ("close-2026-02", 38), ("close-2026-03", 44)]),
        ("Answer auditor sample request", [("audit-2026-03", 70)]),
    ]
    out, i = [], 1
    for task, rs in runs:
        for run, minutes in rs:
            ts = {"close-2026-01": "2026-02-03", "close-2026-02": "2026-03-02", "close-2026-03": "2026-04-02", "audit-2026-03": "2026-03-19"}[run]
            out.append(rec(f"time{i}", f"{ts}T17:00:00Z", "Reviewed task log", f"Task: {task}\nRun: {run}\nMinutes: {minutes}"))
            i += 1
    # duplicate capture of one run (must not be counted twice)
    out.append(rec(f"time{i}", "2026-04-02T17:05:00Z", "Reviewed task log", "Task: Investigate variances above threshold\nRun: close-2026-03\nMinutes: 230"))
    return out


def workspace_memory():
    out = []
    for e in sorted(C.EMAILS, key=lambda x: x["date"]):
        out.append(rec(e["id"], iso(e["date"]), "Mail", f"From: {party_name(e['from'])}\nTo: {', '.join(party_name(p) for p in e['to'])}\nSubject: {e['subject']}\nDate: {e['date']}\n\n{e['body']}"))
    for c in sorted(C.CHATS, key=lambda x: x["date"]):
        out.append(rec(c["id"], iso(c["date"]), "Chat", f"#{c['channel']} - {S.PEOPLE[c['author']]['name']} ({c['date']}): {c['text']}"))
    for m in C.MEETINGS:
        body = "\n".join(f"{S.PEOPLE[s]['name']}: {t}" for s, t in m["lines"])
        out.append(rec(m["id"], iso(m["date"]), "Meeting", f"{m['title']} ({m['date']})\n{body}"))
    for d in C.DOCUMENTS:
        table = "\n".join(" | ".join(r) for r in d["rows"])
        out.append(rec(d["id"], iso(d["date"]), "Document", f"{d['title']} ({d['date']})\n{table}\n{d['note']}"))
    for month in ["2026-01", "2026-02"]:
        rows = commentary(month)
        txt = commentary_md(month, rows)
        out.append(rec(f"COMMENTARY:{month}", iso({"2026-01": "2026-02-04 17:00", "2026-02": "2026-03-04 18:20"}[month]), "Word", txt))
    out.sort(key=lambda r: r["timestamp"])
    return out


def meeting_records():
    out = []
    for m in C.MEETINGS:
        body = "\n".join(t if t.startswith(("Decision:", "Action (")) else f"{S.PEOPLE[s]['name']}: {t}" for s, t in m["lines"])
        out.append(rec(m["id"], iso(m["date"]), "Meeting", f"{m['title']}\n{body}"))
    return out


def handoff_records():
    return [
        rec("h1", "2026-04-14T11:00:00Z", "Meeting", "Decision: Ellen Walsh leads the April close; Claire Donnelly is on leave from 20 April to 8 May.\nDecision: The commentary threshold stays at EUR 5,000 per line."),
        rec("h2", "2026-04-14T11:10:00Z", "Meeting", "Blocker: Atlantic Freight express surcharges (service code EXP, EUR 6,200 in March) are still unexplained.\nAction (Ellen): Ask Sofia Lindqvist which shipments used service code EXP in March."),
        rec("h3", "2026-04-14T11:20:00Z", "Mail", "Action (Ellen): Check that Belvedere order BHG-2291 (EUR 45,000) is invoiced on 14 April.\nAction (Ellen): Explain April professional fees as timing: KPC kickoff EUR 8,000 was invoiced in March but budgeted in April."),
        rec("h4", "2026-04-14T11:30:00Z", "Meeting", "Blocker: Brightwood +3% from 1 May is not in the Q2 forecast.\nAction (Unassigned): Update the Q2 forecast for Brightwood prices."),
        rec("h5", "2026-04-14T11:40:00Z", "Chat", "Decision: Account 4020 Sales - online web shop maps to Revenue - Online from March.\nAction (Owen): Shadow Ellen during the April close and note every question."),
        rec("h6", "2026-04-14T11:45:00Z", "Chat", "Claire mentioned she might change the deck template one day. Free text, not a decision."),
    ]


def escalation_records():
    return [
        rec("s1", "2026-03-02T08:42:00Z", "Pipeline ERP", "Symptom: GL detail export for a full month times out after 120 s (February close).\nQuestion: Is it the number of rows or the server load on the first working day?"),
        rec("s2", "2026-03-02T08:46:00Z", "Pipeline ERP", "Attempt: Re-run the full-month export.\nResult: Same timeout after 120 s."),
        rec("s3", "2026-03-02T08:51:00Z", "Pipeline ERP", "Attempt: Export 1-14 and 15-end of month separately and merge.\nResult: Two files download. The merge is manual; a single full-month export is still not working."),
        rec("s4", "2026-04-02T08:47:00Z", "Mail", "Symptom: The March export needed the same workaround.\nQuestion: Can the manual merge paste the boundary day (14th) twice and create duplicate entries?\nAction (Mark): Follow up the ERP vendor ticket on the export timeout."),
        rec("s5", "2026-04-02T08:50:00Z", "Chat", "Action (Unassigned): Add a duplicate entry_id check to the close procedure."),
    ]


# ---------------------------------------------------------------- curated procedure candidates

FEB_STEPS = [
    ("f01", "normal", "Export the GL detail for the month from the ERP, P&L accounts 4000 to 6999.", "GL detail export. Period 2026-02, accounts 4000 to 6999"),
    ("f02", "troubleshooting", "If the full-month export times out, use the split-export workaround. Not a standard step.", "Error: request timed out after 120 s."),
    ("f03", "troubleshooting", "Workaround: export 1-14 and 15-end separately, merge, and do not paste the boundary day twice.", "export 1-14 and 15-end of month separately and merge, do not paste the boundary day twice"),
    ("f04", "normal", "Save the export as gl_YYYY-MM.csv and check its columns.", "columns entry_id, posting_date, period, journal, account, account_name, cost_centre, counterparty, document_ref, description, debit, credit"),
    ("f05", "normal", "Replace last month's rows in the GL_import tab with the new export.", "deleted January rows"),
    ("f06", "normal", "Check that no account shows UNMAPPED in GL_import.", "returns 0 rows. All accounts mapped."),
    ("f07", "normal", "Check that the sum of net in GL_import equals the ERP P&L total.", "sum of net in GL_import matches the ERP P&L total"),
    ("f08", "normal", "Refresh PnL_vs_Budget and read EBITDA actual vs budget.", "Tab PnL_vs_Budget refreshed."),
    ("f09", "normal", "List the lines where comment needed = YES (variance of EUR 5,000 or more).", "Filter comment needed = YES"),
    ("f10", "normal", "For each of these lines, filter GL_import by account and counterparty to find the entries behind the variance.", "GL_import filtered on account 5000 and counterparty Brightwood Timber Ltd"),
    ("f11", "normal", "Search mail, chat and meeting notes for the cause.", "Searched mail for 'Brightwood'."),
    ("f12", "unclassified", "Unrelated browsing during the close.", "Opened news site during the close."),
    ("f13", "normal", "Write the explanation in the Commentary tab: cause, whether it repeats next month, and the source.", "Repeats every month until a rebate or a new supplier. Source: E01, E02, GL 5000."),
    ("f14", "normal", "Do not comment lines below the EUR 5,000 threshold (CFO rule).", "comment every line above EUR 5,000, nothing below"),
    ("f15", "normal", "Update the management pack slides from the workbook.", "updated Summary, P&L vs budget table and Variance commentary slides"),
    ("f16", "normal", "Send the pack to the CFO.", "Sent 'February management pack' to Tom Avery"),
    ("f17", "normal", "Post a short status in #finance-close.", "Posted in #finance-close"),
]
MAR_STEPS = [
    ("m01", "normal", "Export the GL detail for the month from the ERP, P&L accounts 4000 to 6999.", "Reports > GL detail export. Period 2026-03."),
    ("m02", "normal", "Check that no entry appears twice after merging the split export (duplicate entry_id).", "Checked that no entry of 14 March appears twice."),
    ("m03", "normal", "Replace last month's rows in the GL_import tab with the new export.", "deleted February rows"),
    ("m04", "exception", "If an account shows UNMAPPED, stop before calculating anything.", "Filter column M on UNMAPPED: 6 rows, account 4020"),
    ("m05", "exception", "Find out what the new account is and confirm with the GL owner.", "account 4020 opened on 1 March for the new web shop"),
    ("m06", "exception", "Add the account to the Mapping tab, then check that UNMAPPED returns 0 rows.", "UNMAPPED now returns 0 rows."),
    ("m07", "normal", "Check that the sum of net in GL_import equals the ERP P&L total.", "sum of net in GL_import matches the ERP P&L total"),
    ("m08", "normal", "Refresh PnL_vs_Budget and list the lines where comment needed = YES.", "Comment needed = YES on 7 lines."),
    ("m09", "normal", "For each of these lines, filter GL_import by account and counterparty, and compare with last month's explanation.", "Same cause as February."),
    ("m10", "normal", "Search mail, chat and meeting notes for the cause.", "Searched mail for 'Belvedere', 'StaffBridge', 'Celtic', 'KPC', 'Atlantic'."),
    ("m11", "exception", "If no source explains a variance, say so and ask the owner. Never invent a cause.", "No email or chat explains why. Left as open question."),
    ("m12", "normal", "Write the explanation in the Commentary tab: cause, whether it repeats next month, and the source.", "wrote explanations for 7 lines above threshold, with sources"),
    ("m13", "normal", "Update the management pack slides from the workbook.", "updated Summary, P&L vs budget and Variance commentary slides"),
]


def curated_procedure(records, steps, revision, context, questions):
    by_id = {r["id"]: r for r in records}
    out = []
    for sid, kind, text, quote in steps:
        assert quote in by_id[sid]["text"], (sid, quote)
        out.append({"text": text, "sourceId": sid, "quote": quote, "kind": kind, "reviewed": False})
    return {
        "title": "Monthly management close",
        "context": context,
        "revision": revision,
        "origin": "Curated synthetic candidate for the hackathon (fictional data). Not approved: review every step in the desk.",
        "evidence": records,
        "steps": out,
        "questions": [{"question": q, "answer": ""} for q in questions],
    }


# ---------------------------------------------------------------- answer key

def answer_key():
    vt = variance_table("2026-03")
    out = []
    for r in vt:
        drivers = S.MARCH_DRIVERS.get(r["line_code"], [])
        out.append(dict(r, drivers=drivers, repeats_next_month=S.MARCH_REPEATS.get(r["line_code"])))
    return {
        "month": "2026-03",
        "threshold": S.COMPANY["variance_threshold"],
        "ebitda_actual": ebitda(S.ACTUALS["2026-03"]),
        "ebitda_budget": ebitda(S.BUDGET["2026-03"]),
        "lines": out,
        "expected_agent_behaviour": [
            "Calculates every figure with code, never with the language model.",
            "Stops and asks before calculating when account 4020 is UNMAPPED.",
            "Splits Revenue - Contract (-17,000) into two stories: Belvedere -45,000 (timing) and Harbour City +28,000.",
            "Recognises the timber variance as the same cause as February (memory) and asks whether it still holds.",
            "Links temporary labour to the production meeting of 5 March: the reason was only said aloud.",
            "Says it found no explanation for the freight surcharges and drafts a question to Sofia Lindqvist instead of inventing one.",
            "Flags the energy credit note as one-off and the KPC fees as timing (reverses in April).",
            "Rejects gl_2026-03_invalid.csv (duplicate entry and malformed amount) before producing any figure.",
        ],
    }


# ---------------------------------------------------------------- main

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ["erp-exports", "budget", "workbooks", "presentations", "mail", "documents", "chat",
                "meetings", "commentary", "screenpipe-records", "answer-key", "viewer"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    gls = {m: build_gl(m) for m in S.MONTHS}
    for m, gl in gls.items():
        write_csv(OUT / "erp-exports" / f"gl_{m}.csv", gl, GL_COLUMNS)
    invalid, invalid_info = build_invalid_march(gls["2026-03"])
    write_csv(OUT / "erp-exports" / "gl_2026-03_invalid.csv", invalid, GL_COLUMNS)

    write_csv(OUT / "budget" / "budget_2026.csv",
              [{"line_code": c, "line_name": n, "month": m, "amount": S.BUDGET[m][c]} for m in S.BUDGET_MONTHS for c, n, _ in S.LINES],
              ["line_code", "line_name", "month", "amount"])
    build_budget_xlsx(OUT / "budget" / "budget_2026.xlsx")
    write_csv(OUT / "budget" / "chart_of_accounts.csv",
              [{"account": a, "account_name": v[0], "line_code": v[1], "line_name": S.LINE_NAME[v[1]], "opened": v[2]} for a, v in S.ACCOUNTS.items()],
              ["account", "account_name", "line_code", "line_name", "opened"])

    for m in ["2026-01", "2026-02"]:
        rows = commentary(m)
        build_closing_workbook(OUT / "workbooks" / f"closing_workbook_{m}.xlsx", m, gls[m], rows, S.MAPPING_BEFORE_MARCH, "Closed and validated by the CFO")
        (OUT / "commentary" / f"commentary_{m}.md").write_text(commentary_md(m, rows), encoding="utf-8")
        build_pack(OUT / "presentations" / f"management_pack_{m}.pptx", m, rows)
    build_closing_workbook(OUT / "workbooks" / "closing_workbook_2026-03.xlsx", "2026-03", gls["2026-03"], [],
                           S.MAPPING_BEFORE_MARCH, "IN PROGRESS - mapping copied from February, commentary empty")
    build_pack(OUT / "presentations" / "management_pack_2026-03_DRAFT.pptx", "2026-03", [], draft=True)
    build_budget_deck(OUT / "presentations" / "budget_2026.pptx")

    for e in C.EMAILS:
        (OUT / "mail" / f"{e['id']}.eml").write_text(eml(e), encoding="utf-8")
    for d in C.DOCUMENTS:
        (OUT / "documents" / f"{d['id']}.html").write_text(doc_html(d), encoding="utf-8")
    write_csv(OUT / "chat" / "messages.csv",
              [{"id": c["id"], "channel": c["channel"], "date": c["date"], "author": S.PEOPLE[c["author"]]["name"], "text": c["text"]} for c in sorted(C.CHATS, key=lambda x: x["date"])],
              ["id", "channel", "date", "author", "text"])
    for m in C.MEETINGS:
        script = [f"# {m['title']} - {m['date']} (fictional)", "",
                  "Read aloud while screenpipe records audio. One person per role.", "",
                  "Roles: " + ", ".join(f"{S.PEOPLE[a]['name']} ({S.PEOPLE[a]['role']})" for a in m["attendees"]), ""]
        script += [f"**{S.PEOPLE[s]['name']}:** {t}" for s, t in m["lines"]]
        (OUT / "meetings" / f"{m['id']}_{m['title'].lower().replace(' ', '-')}.md").write_text("\n".join(script) + "\n", encoding="utf-8")

    recs = {
        "feb-close-session.json": feb_close_session(),
        "mar-close-session.json": mar_close_session(),
        "task-runs.json": task_runs(),
        "workspace-memory.json": workspace_memory(),
        "meetings.json": meeting_records(),
        "handoff.json": handoff_records(),
        "escalation.json": escalation_records(),
    }
    for name, data in recs.items():
        (OUT / "screenpipe-records" / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    procs = OUT / "screenpipe-records" / "procedures"
    procs.mkdir(exist_ok=True)
    feb_proc = curated_procedure(recs["feb-close-session.json"], FEB_STEPS, 1,
        "Financial Controller closing the February 2026 management accounts of a fictional furniture maker. One observed session.",
        ["Record f12 is unrelated browsing: remove it from the procedure?",
         "What is the deadline for sending the pack? The budget deck says working day 5.",
         "Who approves the mapping when a new GL account appears?"])
    mar_proc = curated_procedure(recs["mar-close-session.json"], MAR_STEPS, 2,
        "Financial Controller closing the March 2026 management accounts. Proposed change: a duplicate check after the split export, a stop on unmapped accounts, and an explicit rule for unexplained variances.",
        ["Should the duplicate entry_id check run on every export, or only when the split workaround is used?"])
    for name, data in (("feb-close-procedure.json", feb_proc), ("mar-close-procedure-rev2.json", mar_proc)):
        (procs / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    replay = OUT / "screenpipe-records" / "replay"
    replay.mkdir(exist_ok=True)
    for m in ["2026-02", "2026-03"]:
        shutil.copy(OUT / "erp-exports" / f"gl_{m}.csv", replay / f"gl_{m}.csv")
    shutil.copy(OUT / "erp-exports" / "gl_2026-03_invalid.csv", replay / "gl_2026-03_invalid.csv")

    key = answer_key()
    key["invalid_export"] = invalid_info
    (OUT / "answer-key" / "march_2026_variances.json").write_text(json.dumps(key, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(OUT / "answer-key" / "pnl_by_month.csv",
              [dict(r, month=m) for m in S.MONTHS for r in variance_table(m)],
              ["month", "line_code", "line_name", "actual", "budget", "variance_favourable_positive", "variance_pct", "above_threshold"])

    viewer_src = ROOT / "src" / "viewer"
    for f in viewer_src.iterdir():
        shutil.copy(f, OUT / "viewer" / f.name)
    data = viewer_data(gls)
    (OUT / "viewer" / "data.js").write_text("window.DATASET = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print("dataset built in", OUT)


if __name__ == "__main__":
    main()
