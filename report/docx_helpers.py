"""Low-level python-docx helpers for the SRM-format project report."""
import re
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor
from PIL import Image

FONT = "Times New Roman"
TEXT_W_CM = 15.0      # A4 21 cm - 3.5 cm left - 2.5 cm right
MAX_FIG_H_CM = 19.5


def new_document():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin, sec.right_margin = Cm(3.5), Cm(2.5)
    sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.2)
    sec.footer_distance = Cm(1.0)
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    pf = st.paragraph_format
    pf.space_after = Pt(6)
    pf.space_before = Pt(0)
    pf.line_spacing = 1.5
    return doc


def _set_run_font(run, size=None, bold=None, italic=None, font=FONT, color=None):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    run._element.rPr.rFonts.set(qn("w:cs"), font)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


TOKEN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`|\[\[.+?\]\])")


def add_rich(par, text, size=None, bold=False, italic=False):
    """Inline markup: **bold**, *italic*, `code`, [[highlighted placeholder]]."""
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("**"):
            r = par.add_run(part[2:-2]); _set_run_font(r, size, True, italic)
        elif part.startswith("`"):
            r = par.add_run(part[1:-1]); _set_run_font(r, (size or 12) - 1.5, bold, False, font="Consolas")
        elif part.startswith("[["):
            r = par.add_run(part[2:-2]); _set_run_font(r, size, True, italic)
            hl = OxmlElement("w:highlight"); hl.set(qn("w:val"), "yellow"); r._element.rPr.append(hl)
        elif part.startswith("*"):
            r = par.add_run(part[1:-1]); _set_run_font(r, size, bold, True)
        else:
            r = par.add_run(part); _set_run_font(r, size, bold, italic)
    return par


def para(doc, text="", align="justify", size=12, bold=False, italic=False, before=0, after=6,
         spacing=1.5, keep_next=False, indent_cm=None, first_line_cm=None, page_break_before=False):
    p = doc.add_paragraph()
    p.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER,
                   "left": WD_ALIGN_PARAGRAPH.LEFT, "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), spacing
    pf.keep_with_next = keep_next
    pf.page_break_before = page_break_before
    if indent_cm is not None:
        pf.left_indent = Cm(indent_cm)
    if first_line_cm is not None:
        pf.first_line_indent = Cm(first_line_cm)
    if text:
        add_rich(p, text, size, bold, italic)
    return p


def bullet(doc, text, level=0, symbol="•"):
    p = para(doc, after=3, indent_cm=0.9 + 0.7 * level, first_line_cm=-0.5)
    r = p.add_run(symbol + "\t"); _set_run_font(r, 12)
    tabs = p.paragraph_format.tab_stops; tabs.add_tab_stop(Cm(0.9 + 0.7 * level))
    add_rich(p, text)
    return p


def numbered(doc, n, text):
    p = para(doc, after=3, indent_cm=0.9, first_line_cm=-0.6)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(0.9))
    r = p.add_run(f"{n}.\t"); _set_run_font(r, 12)
    add_rich(p, text)
    return p


def page_break(doc):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(0)
    p.add_run().add_break(WD_BREAK.PAGE)


def shade(cell, hexcolor):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def set_cell_margins(table, top=40, bottom=40, left=80, right=80):
    tblPr = table._element.tblPr
    mar = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        e = OxmlElement(f"w:{k}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); mar.append(e)
    tblPr.append(mar)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:tblHeader"); e.set(qn("w:val"), "true"); trPr.append(e)


def no_split(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit"); e.set(qn("w:val"), "true"); trPr.append(e)


def table(doc, headers, rows, widths_cm, size=10, header_fill="D9E2F3", align=None, bold_rows=(), bold_first_col=False):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    set_cell_margins(t)
    align = align or ["left"] * len(headers)
    amap = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT}

    def fill(cell, text, bold, a, w):
        cell.width = Cm(w)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = amap[a]
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        lines = str(text).split("\n")
        for i, ln in enumerate(lines):
            if i:
                p = cell.add_paragraph(); p.alignment = amap[a]
                p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            add_rich(p, ln, size, bold)

    hdr = t.rows[0]
    repeat_header(hdr)
    for i, h in enumerate(headers):
        fill(hdr.cells[i], h, True, "center", widths_cm[i])
        shade(hdr.cells[i], header_fill)
    for ri, r in enumerate(rows):
        row = t.add_row(); no_split(row)
        for i, v in enumerate(r):
            fill(row.cells[i], v, (ri in bold_rows) or (bold_first_col and i == 0), align[i], widths_cm[i])
    # keep the caption with the header and first row; keep short tables on one page
    n_keep = len(t.rows) - 1 if len(rows) <= 18 else 2
    for row in t.rows[:n_keep]:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    # also fix grid column widths
    for i, w in enumerate(widths_cm):
        for c in t.columns[i].cells:
            c.width = Cm(w)
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(4); sp.paragraph_format.line_spacing = 1.0
    return t


def caption(doc, text, kind="figure"):
    if kind == "table":
        p = para(doc, align="center", size=11, bold=True, before=6, after=6, spacing=1.15, keep_next=True)
    else:
        p = para(doc, align="center", size=11, before=2, after=10, spacing=1.15)
    add_rich(p, text, 11, kind == "table")
    return p


def figure(doc, path, width_cm=None, max_h_cm=MAX_FIG_H_CM):
    w_px, h_px = Image.open(path).size
    width_cm = width_cm or TEXT_W_CM
    if width_cm * h_px / w_px > max_h_cm:
        width_cm = max_h_cm * w_px / h_px
    p = para(doc, align="center", before=6, after=2, spacing=1.0, keep_next=True)
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    return p


def code_block(doc, code, size=7.5):
    for i, line in enumerate(code.rstrip("\n").split("\n")):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(0); pf.space_before = Pt(0); pf.line_spacing = 1.0
        pf.left_indent = Cm(0.2)
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "F2F2F2")
        pPr.append(shd)
        r = p.add_run(line if line else " ")
        _set_run_font(r, size, font="Courier New")
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(6); sp.paragraph_format.line_spacing = 1.0


def equation(doc, text):
    p = para(doc, align="center", before=4, after=8, spacing=1.3)
    add_rich(p, text, 12, False, True)
    return p


# ------------------------------------------------------------------- sections and page numbers
def _add_page_field(par):
    r = par.add_run(); _set_run_font(r, 12)
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = " PAGE "
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    r._r.append(f1); r._r.append(it); r._r.append(f2)


def configure_section(sec, numbered, fmt="decimal", start=1):
    sec.footer.is_linked_to_previous = False
    ft = sec.footer
    p = ft.paragraphs[0]
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if numbered:
        _add_page_field(p)
    sectPr = sec._sectPr
    for old in sectPr.findall(qn("w:pgNumType")):
        sectPr.remove(old)
    pg = OxmlElement("w:pgNumType"); pg.set(qn("w:fmt"), fmt); pg.set(qn("w:start"), str(start))
    sectPr.append(pg)


def new_section(doc):
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.left_margin, sec.right_margin = Cm(3.5), Cm(2.5)
    sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.2)
    return sec
