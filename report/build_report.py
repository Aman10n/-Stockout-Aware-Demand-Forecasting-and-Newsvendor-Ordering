"""Build the SRM-format project report (DOCX + PDF) for the stockout-aware forecasting project.

Usage (from report/):  python build_report.py
Pass 1 writes the document with blank page numbers and exports a PDF through Microsoft Word;
the page of every heading, figure and table is read back from that PDF, and pass 2 fills in the
contents, list-of-tables and list-of-figures pages.
"""
import json
import re
import sys
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

import docx_helpers as H
from content import build_content, REFERENCES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DOCX = HERE / "Stockout_Aware_Forecasting_Project_Report.docx"
OUT_PDF = HERE / "Stockout_Aware_Forecasting_Project_Report.pdf"

TITLE = "STOCKOUT-AWARE DEMAND FORECASTING AND NEWSVENDOR ORDERING ON FRESHRETAILNET-50K"
TITLE_CASE = "Stockout-Aware Demand Forecasting and Newsvendor Ordering on FreshRetailNet-50K"
STUDENTS = [("AMAN KOLEY", "RA2411027010135"), ("AKSHARA KUMARI", "RA2411027010123"), ("SHIVAM SINGH", "RA2411027010126")]
GUIDE = "G. PREMALATHA"
HOD = "Dr. KAVITHA V"

FRONT = ["ABSTRACT", "ACKNOWLEDGEMENT", "LIST OF TABLES", "LIST OF FIGURES", "LIST OF SYMBOLS AND ABBREVIATIONS"]


# ------------------------------------------------------------------------------------- content model
class Report:
    def __init__(self):
        self.ops, self.chapters, self.h2s = [], [], []
        self.figs, self.tabs = {}, {}
        self.fig_list, self.tab_list = [], []
        self.ch = 0
        self._f = self._t = 0

    # structure
    def chapter(self, title):
        self.ch += 1; self._f = self._t = 0
        self.chapters.append((self.ch, title)); self.ops.append(("chapter", self.ch, title))

    def unnumbered_chapter(self, title, toc=True):
        self.ops.append(("uchapter", title, toc))

    def h2(self, num, title):
        self.h2s.append((num, title)); self.ops.append(("h2", num, title))

    def h3(self, num, title):
        self.ops.append(("h3", num, title))

    def p(self, text, **kw):
        self.ops.append(("p", text, kw))

    def bullets(self, items):
        for it in items:
            self.ops.append(("bullet", it))

    def numbers(self, items):
        for i, it in enumerate(items, 1):
            self.ops.append(("num", i, it))

    def eq(self, text):
        self.ops.append(("eq", text))

    def code(self, text, size=7.5):
        self.ops.append(("code", text, size))

    def pagebreak(self):
        self.ops.append(("pb",))

    def fig(self, key, path, cap, width=None, max_h=None):
        self._f += 1; no = f"{self.ch}.{self._f}"
        self.figs[key] = no; self.fig_list.append((no, cap))
        self.ops.append(("fig", no, cap, Path(path), width, max_h))

    def tab(self, key, cap, headers, rows, widths, align=None, size=10, bold_rows=(), bold_first_col=False):
        self._t += 1; no = f"{self.ch}.{self._t}"
        self.tabs[key] = no; self.tab_list.append((no, cap))
        self.ops.append(("tab", no, cap, headers, rows, widths, align, size, bold_rows, bold_first_col))

    def resolve(self, text):
        def rep(m):
            kind, key = m.group(1), m.group(2)
            d = self.figs if kind == "fig" else self.tabs
            if key not in d:
                raise KeyError(f"unknown reference @{kind}:{key}")
            return ("Fig. " if kind == "fig" else "Table ") + d[key]
        return re.sub(r"@(fig|tab):([A-Za-z0-9_]+)", rep, text)


# ------------------------------------------------------------------------------------------ rendering
def title_page(doc):
    H.para(doc, "STOCKOUT-AWARE DEMAND FORECASTING\nAND NEWSVENDOR ORDERING ON\nFRESHRETAILNET-50K",
           "center", 17, True, before=30, after=18, spacing=1.3)
    H.para(doc, "A PROJECT REPORT", "center", 13, True, after=14)
    H.para(doc, "Submitted by", "center", 12, italic=True, after=6)
    for n, r in STUDENTS:
        H.para(doc, f"{n} [Reg. No: {r}]", "center", 13, True, after=0, spacing=1.3)
    H.para(doc, "Under the Guidance of", "center", 12, italic=True, before=16, after=4)
    H.para(doc, GUIDE, "center", 13, True, after=0)
    H.para(doc, "(Assistant Professor, Department of Data Science and Business Systems)", "center", 11, after=14)
    H.para(doc, "In partial fulfillment of the Requirements for the Degree of", "center", 12, italic=True, after=4)
    H.para(doc, "BACHELOR OF TECHNOLOGY", "center", 14, True, after=0, spacing=1.25)
    H.para(doc, "in COMPUTER SCIENCE AND ENGINEERING", "center", 12, True, after=0, spacing=1.25)
    H.para(doc, "with specialization in BIG DATA ANALYTICS", "center", 12, True, after=10, spacing=1.25)
    logo = HERE / "assets/misc/srm_logo_0.png"
    if logo.exists():
        p = H.para(doc, align="center", after=10, spacing=1.0)
        p.add_run().add_picture(str(logo), width=Cm(6.2))
    for line in ["DEPARTMENT OF DATA SCIENCE AND BUSINESS SYSTEMS", "FACULTY OF ENGINEERING AND TECHNOLOGY",
                 "SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", "KATTANKULATHUR – 603203"]:
        H.para(doc, line, "center", 13, True, after=0, spacing=1.3)
    H.para(doc, "NOVEMBER 2026", "center", 13, True, before=14, after=0)


def bonafide(doc):
    H.page_break(doc)
    H.para(doc, "SRM INSTITUTE OF SCIENCE AND TECHNOLOGY", "center", 16, True, before=24, after=0)
    H.para(doc, "KATTANKULATHUR – 603203", "center", 13, True, after=28)
    p = H.para(doc, "", "center", after=20)
    r = p.add_run("BONAFIDE CERTIFICATE"); H._set_run_font(r, 15, True); r.underline = True
    names = ", ".join(f"**{n} [Reg. No: {r}]**" for n, r in STUDENTS)
    H.para(doc, f"Certified that this project report titled “**{TITLE_CASE}**” is the bonafide work of {names}, "
                "who carried out the project work under my supervision. Certified further, that to the best of my "
                "knowledge the work reported herein does not form part of any other thesis or dissertation on the basis "
                "of which a degree or award was conferred on an earlier occasion for this or any other candidate.", after=90)
    t = doc.add_table(rows=3, cols=2)
    left = [f"**{GUIDE}**", "Assistant Professor", "Dept. of DSBS"]
    right = [f"**{HOD}**", "HEAD OF THE DEPARTMENT", "Dept. of DSBS"]
    for i in range(3):
        for j, txt in enumerate((left[i], right[i])):
            c = t.cell(i, j); c.width = Cm(7.5)
            pp = c.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            pp.paragraph_format.space_after = Pt(2)
            H.add_rich(pp, txt, 12)
    H.para(doc, "", after=150)
    t2 = doc.add_table(rows=1, cols=2)
    for j, txt in enumerate(("Signature of Internal Examiner", "Signature of External Examiner")):
        c = t2.cell(0, j); c.width = Cm(7.5)
        pp = c.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.RIGHT
        H.add_rich(pp, txt, 12)


def front_heading(doc, text):
    H.para(doc, text, "center", 16, True, before=12, after=18, spacing=1.2)


def abstract_and_ack(doc, R, abstract_paras, keywords, ack_paras):
    front_heading(doc, "ABSTRACT")
    for t in abstract_paras:
        H.para(doc, R.resolve(t), spacing=1.4)
    H.para(doc, f"**Keywords:** {keywords}", before=4)
    H.page_break(doc)
    front_heading(doc, "ACKNOWLEDGEMENT")
    for t in ack_paras:
        H.para(doc, t, spacing=1.6, after=8)
    for n, r in STUDENTS:
        H.para(doc, f"**{n} – {r}**", "right", after=0, before=0)


def pg(pages, key):
    return str(pages.get(key, "")) if pages else ""


def toc(doc, R, pages):
    front_heading(doc, "TABLE OF CONTENTS")
    rows, bold = [], []
    for k in FRONT:
        rows.append(("", f"**{k}**", pg(pages, "front:" + k)))
    for no, title in R.chapters:
        bold.append(len(rows)); rows.append((str(no), f"**{title.upper()}**", pg(pages, f"chapter:{no}")))
        for num, t in R.h2s:
            if num.split(".")[0] == str(no):
                rows.append(("", f"      {num} {t.upper()}", pg(pages, f"h2:{num}")))
    for op in R.ops:
        if op[0] == "uchapter" and op[2]:
            rows.append(("", f"**{op[1]}**", pg(pages, "u:" + op[1])))
        if op[0] == "h3" and op[1].startswith("A."):
            rows.append(("", f"      {op[1]} {op[2]}", pg(pages, "h3:" + op[1])))
    H.table(doc, ["CHAPTER\nNO.", "TITLE", "PAGE NO."], rows, [2.2, 10.6, 2.2], align=["center", "left", "center"], size=10.5)


def lists(doc, R, pages):
    H.page_break(doc)
    front_heading(doc, "LIST OF TABLES")
    H.table(doc, ["TABLE NO.", "TITLE", "PAGE NO."], [(n, c, pg(pages, "tab:" + n)) for n, c in R.tab_list],
            [2.2, 10.6, 2.2], align=["center", "left", "center"], size=10)
    H.page_break(doc)
    front_heading(doc, "LIST OF FIGURES")
    H.table(doc, ["FIGURE NO.", "TITLE", "PAGE NO."], [(n, c, pg(pages, "fig:" + n)) for n, c in R.fig_list],
            [2.2, 10.6, 2.2], align=["center", "left", "center"], size=10)


def symbols(doc, sym_rows):
    H.page_break(doc)
    front_heading(doc, "LIST OF SYMBOLS AND ABBREVIATIONS")
    H.table(doc, ["S.No.", "ABBREVIATION / SYMBOL", "EXPANSION"], [(str(i), f"**{a}**", b) for i, (a, b) in enumerate(sym_rows, 1)],
            [1.4, 4.6, 9.0], align=["center", "left", "left"], size=10.5)


def render_body(doc, R):
    first = True
    for op in R.ops:
        k = op[0]
        if k == "chapter":
            if not first:
                H.page_break(doc)
            first = False
            H.para(doc, f"CHAPTER {op[1]}", "center", 16, True, before=6, after=2, spacing=1.2, keep_next=True)
            H.para(doc, op[2].upper(), "center", 16, True, after=18, spacing=1.2, keep_next=True)
        elif k == "uchapter":
            H.page_break(doc)
            H.para(doc, op[1], "center", 16, True, before=6, after=18, spacing=1.2, keep_next=True)
        elif k == "h2":
            H.para(doc, f"{op[1]} {op[2].upper()}", "left", 14, True, before=12, after=6, spacing=1.2, keep_next=True)
        elif k == "h3":
            H.para(doc, f"{op[1]} {op[2]}" if op[1].startswith("A.") else f"{op[1]} {op[2].upper()}",
                   "left", 12.5 if op[1].startswith("A.") else 12, True, before=8, after=4, spacing=1.2, keep_next=True)
        elif k == "p":
            H.para(doc, R.resolve(op[1]), **op[2])
        elif k == "bullet":
            H.bullet(doc, R.resolve(op[1]))
        elif k == "num":
            H.numbered(doc, op[1], R.resolve(op[2]))
        elif k == "eq":
            H.equation(doc, op[1])
        elif k == "code":
            H.code_block(doc, op[1], op[2])
        elif k == "pb":
            H.page_break(doc)
        elif k == "fig":
            _, no, cap, path, width, max_h = op
            H.figure(doc, path, width, max_h or H.MAX_FIG_H_CM)
            H.caption(doc, f"Fig. {no}: {R.resolve(cap)}")
        elif k == "tab":
            _, no, cap, headers, rows, widths, align, size, bold_rows, bfc = op
            H.caption(doc, f"Table {no}: {R.resolve(cap)}", "table")
            H.table(doc, headers, [[R.resolve(str(c)) for c in r] for r in rows], widths, size, align=align,
                    bold_rows=bold_rows, bold_first_col=bfc)


def build(pages=None):
    R = Report()
    meta = build_content(R)
    doc = H.new_document()
    H.configure_section(doc.sections[0], numbered=False)
    title_page(doc)
    bonafide(doc)
    sec = H.new_section(doc); H.configure_section(sec, True, "lowerRoman", 1)
    abstract_and_ack(doc, R, meta["abstract"], meta["keywords"], meta["ack"])
    H.page_break(doc)
    toc(doc, R, pages)
    lists(doc, R, pages)
    symbols(doc, meta["symbols"])
    sec = H.new_section(doc); H.configure_section(sec, True, "decimal", 1)
    render_body(doc, R)
    doc.save(OUT_DOCX)
    return R


# ------------------------------------------------------------------------------- PDF + page lookup
def export_pdf():
    import win32com.client
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(str(OUT_DOCX), ReadOnly=True)
        d.Repaginate()
        d.ExportAsFixedFormat(str(OUT_PDF), 17)
        d.Close(False)
    finally:
        word.Quit()


def norm(s):
    s = re.sub(r"\s+", " ", s.replace("–", "-").replace("—", "-")).strip()
    return re.sub(r"-\s+", "-", s)


def find_pages(R):
    from pypdf import PdfReader
    # drop a page number that the text extractor may place before the page body
    texts = [re.sub(r"^(?:[ivxlc]+|\d+)\s+(?=[A-Z])", "", norm(p.extract_text() or "")) for p in PdfReader(str(OUT_PDF)).pages]
    def first(pred, start=0):
        for i in range(start, len(texts)):
            if pred(texts[i]):
                return i
        return None
    abs_i = first(lambda t: t.startswith("ABSTRACT"))
    ch1 = first(lambda t: t.startswith("CHAPTER 1 "), abs_i)
    pages = {}
    roman = lambda i: to_roman(i - abs_i + 1)
    arabic = lambda i: i - ch1 + 1
    for k in FRONT:
        i = first(lambda t, k=k: t.startswith(k), abs_i)
        pages["front:" + k] = roman(i)
    for no, title in R.chapters:
        i = first(lambda t, no=no: t.startswith(f"CHAPTER {no} "), ch1)
        pages[f"chapter:{no}"] = arabic(i)
    for num, t in R.h2s:
        key = norm(f"{num} {t.upper()}")
        i = first(lambda s, key=key: key in s, ch1)
        if i is None:
            print("WARN heading not found:", key)
        else:
            pages[f"h2:{num}"] = arabic(i)
    for op in R.ops:
        if op[0] == "uchapter":
            i = first(lambda s, k=norm(op[1]): s.startswith(k), ch1)
            pages["u:" + op[1]] = arabic(i) if i is not None else ""
        if op[0] == "h3" and op[1].startswith("A."):
            i = first(lambda s, k=norm(f"{op[1]} {op[2]}"): k in s, ch1)
            pages["h3:" + op[1]] = arabic(i) if i is not None else ""
    for no, _ in R.fig_list:
        i = first(lambda s, no=no: f"Fig. {no}:" in s, ch1)
        pages["fig:" + no] = arabic(i) if i is not None else ""
        if i is None: print("WARN figure not found", no)
    for no, _ in R.tab_list:
        i = first(lambda s, no=no: f"Table {no}:" in s, ch1)
        pages["tab:" + no] = arabic(i) if i is not None else ""
        if i is None: print("WARN table not found", no)
    pages["_total_pdf_pages"] = len(texts)
    return pages


def to_roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s; n -= v
    return out


if __name__ == "__main__":
    pages = None
    for it in range(3):
        R = build(pages)
        export_pdf()
        new = find_pages(R)
        print(f"pass {it + 1}: {new['_total_pdf_pages']} PDF pages")
        if new == pages:
            break
        pages = new
    R = build(pages)
    export_pdf()
    json.dump(pages, open(HERE / "assets/page_map.json", "w"), indent=1)
    print("figures:", len(R.fig_list), "tables:", len(R.tab_list))
    print("written", OUT_DOCX.name, OUT_PDF.name)
