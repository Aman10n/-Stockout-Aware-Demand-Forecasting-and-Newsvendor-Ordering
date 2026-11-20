"""Build the Stockout Simulator user & presentation guide (PDF).

    python simulator/docs/build_guide.py <folder with raw 1920x1080 screenshots>

Screenshots are cropped (browser chrome and taskbar removed), annotated with numbered markers and
written to simulator/docs/screenshots/; the PDF goes to simulator/docs/Stockout_Simulator_Guide.pdf.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image as RLImage, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

HERE = Path(__file__).resolve().parent
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "raw"
SHOTS = HERE / "screenshots"
OUT = HERE / "Stockout_Simulator_Guide.pdf"
FONTS = Path("C:/Windows/Fonts")
CROP = (0, 82, 1904, 1032)  # remove browser chrome (top) and the Windows taskbar (bottom)

BLUE, INK, INK2, MUTED, LINE, SOFT = "#2a78d6", "#0b0b0b", "#3d3c39", "#6b6a66", "#dcdad4", "#f3f2ee"
ORANGE, GREEN, RED = "#eb6834", "#1a8f63", "#c93b3a"

pdfmetrics.registerFont(TTFont("Segoe", str(FONTS / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Bold", str(FONTS / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Italic", str(FONTS / "segoeuii.ttf")))
pdfmetrics.registerFont(TTFont("Mono", str(FONTS / "consola.ttf")))
pdfmetrics.registerFontFamily("Segoe", normal="Segoe", bold="Segoe-Bold", italic="Segoe-Italic", boldItalic="Segoe-Bold")

# ----------------------------------------------------------------------------------- screenshot prep
# numbered markers: (x, y) in the original 1920x1080 screenshot
MARKS = {
    "s01_cmd_top": [(395, 314), (860, 336), (520, 395), (420, 640), (1250, 540), (1278, 246)],
    "s03_cmd_shortage": [(592, 314), (1150, 585), (1400, 835)],
    "s02_cmd_bottom": [(330, 627), (1080, 627)],
    "s04_game_setup": [(614, 391), (1370, 420), (300, 600)],
    "s05_game_morning": [(1105, 180), (1258, 180), (1388, 375), (1380, 418), (205, 760)],
    "s06_game_open": [(1105, 180), (318, 395), (470, 575), (1385, 343), (1545, 300)],
    "s07_game_close": [(1375, 290), (1375, 475), (318, 395)],
    "s08_game_close_cards": [(380, 420)],
    "s09_game_final": [(190, 213), (960, 342), (1690, 445)],
    "s10_lab_top": [(390, 330), (1440, 330), (1336, 385), (205, 518)],
    "s11_lab_mid": [(570, 420), (1330, 420), (1330, 790)],
    "s12_lab_mechC": [(1553, 330), (1336, 385)],
    "s13_lab_batch": [(1606, 740), (950, 840)],
    "s14_xray_top": [(390, 320), (1110, 310), (575, 362), (380, 700), (1140, 630)],
    "s15_xray_edit": [(380, 689), (380, 410), (1140, 590)],
    "s16_xray_bottom": [(868, 515), (1440, 460), (1140, 860)],
}


def prep_shots() -> None:
    SHOTS.mkdir(exist_ok=True)
    font = ImageFont.truetype(str(FONTS / "segoeuib.ttf"), 26)
    for name, marks in MARKS.items():
        src = RAW / f"{name}.png"
        if not src.exists():
            continue
        im = Image.open(src).convert("RGB").crop(CROP)
        d = ImageDraw.Draw(im)
        for i, (x, y) in enumerate(marks, 1):
            x, y = x - CROP[0], y - CROP[1]
            r = 21
            d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill="#ffffff")
            d.ellipse([x - r, y - r, x + r, y + r], fill="#eb6834")
            d.text((x, y + 1), str(i), fill="#ffffff", font=font, anchor="mm")
        im = im.resize((1500, round(1500 * im.height / im.width)), Image.LANCZOS)
        im.save(SHOTS / f"{name}.jpg", quality=88, optimize=True)
    for name in ["s01_cmd_top"]:  # clean cover image
        src = RAW / f"{name}.png"
        if src.exists():
            im = Image.open(src).convert("RGB").crop(CROP)
            im.resize((1500, round(1500 * im.height / im.width)), Image.LANCZOS).save(SHOTS / "cover.jpg", quality=90)


# ----------------------------------------------------------------------------------- styles
S = {
    "body": ParagraphStyle("body", fontName="Segoe", fontSize=9.6, leading=14, textColor=INK2, spaceAfter=5),
    "small": ParagraphStyle("small", fontName="Segoe", fontSize=8.4, leading=11.5, textColor=MUTED),
    "h1": ParagraphStyle("h1", fontName="Segoe-Bold", fontSize=20, leading=25, textColor=INK, spaceBefore=2, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Segoe-Bold", fontSize=13.5, leading=18, textColor=INK, spaceBefore=10, spaceAfter=5),
    "h3": ParagraphStyle("h3", fontName="Segoe-Bold", fontSize=10.8, leading=15, textColor=INK, spaceBefore=8, spaceAfter=3),
    "eyebrow": ParagraphStyle("eyebrow", fontName="Segoe-Bold", fontSize=8.5, leading=11, textColor=BLUE, spaceAfter=2),
    "caption": ParagraphStyle("caption", fontName="Segoe-Italic", fontSize=8.3, leading=11, textColor=MUTED, spaceBefore=3, spaceAfter=8),
    "cell": ParagraphStyle("cell", fontName="Segoe", fontSize=8.6, leading=11.5, textColor=INK2),
    "cellb": ParagraphStyle("cellb", fontName="Segoe-Bold", fontSize=8.6, leading=11.5, textColor=INK),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=8.4, leading=11.5, textColor=INK, backColor=SOFT, borderPadding=(6, 6, 6, 6),
                           spaceBefore=4, spaceAfter=10, leftIndent=4, rightIndent=4),
    "callout": ParagraphStyle("callout", fontName="Segoe", fontSize=9.2, leading=13, textColor=INK2),
    "cover_t": ParagraphStyle("cover_t", fontName="Segoe-Bold", fontSize=30, leading=36, textColor=INK),
    "cover_s": ParagraphStyle("cover_s", fontName="Segoe", fontSize=13, leading=18, textColor=INK2),
}
W = A4[0] - 32 * mm
BADGE = ParagraphStyle("badge", fontName="Segoe-Bold", fontSize=8.6, leading=10, textColor=colors.white, alignment=TA_CENTER)


def P(text, style="body"):
    return Paragraph(text, S[style])


def shot(name, caption, width=150 * mm):
    p = SHOTS / f"{name}.jpg"
    im = Image.open(p)
    h = width * im.height / im.width
    img = RLImage(str(p), width=width, height=h)
    frame = Table([[img]], colWidths=[width], style=TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor(LINE)), ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    cap = Table([[P(caption, "caption")]], colWidths=[width], style=TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    kt = KeepTogether([frame, cap])
    kt._shot = True
    return kt


def table(rows, widths, header=True, zebra=True):
    data = [[P(c, "cellb" if (header and i == 0) else "cell") if isinstance(c, str) else c for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor(LINE)),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 5)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(SOFT)), ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor(INK2))]
    t.setStyle(TableStyle(st))
    return t


def markers(items):
    """Numbered legend that matches the orange markers on a screenshot."""
    rows = []
    for i, txt in enumerate(items, 1):
        badge = Table([[Paragraph(f"<b>{i}</b>", BADGE)]], colWidths=[6 * mm], rowHeights=[6 * mm],
                      style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(ORANGE)), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1), ("ROUNDEDCORNERS", [3, 3, 3, 3])]))
        rows.append([badge, P(txt, "callout")])
    t = Table(rows, colWidths=[9 * mm, W - 9 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    t._legend = True
    return t


def steps(items):
    rows = [[P(f"<b>{i}.</b>", "cell"), P(t, "callout")] for i, t in enumerate(items, 1)]
    t = Table(rows, colWidths=[7 * mm, W - 7 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def box(title, body, color=BLUE, bg="#eef4fc"):
    t = Table([[P(f"<b>{title}</b>", "cellb")], [P(body, "callout")]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)), ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(color)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (0, 0), 7), ("BOTTOMPADDING", (0, -1), (-1, -1), 8)]))
    return KeepTogether([Spacer(1, 3), t, Spacer(1, 7)])


def on_page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("Segoe", 7.8)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(16 * mm, 10 * mm, "Stockout Simulator - user & presentation guide")
        canvas.drawRightString(A4[0] - 16 * mm, 10 * mm, f"{doc.page}")
        canvas.setStrokeColor(colors.HexColor(LINE))
        canvas.line(16 * mm, 13.5 * mm, A4[0] - 16 * mm, 13.5 * mm)
    canvas.restoreState()


# ----------------------------------------------------------------------------------- content
def build() -> None:
    st = []
    # ---------------------------------------------------------------- cover
    st += [Spacer(1, 18 * mm), P("STOCKOUT-AWARE DEMAND FORECASTING · FRESHRETAILNET-50K", "eyebrow"),
           P("Stockout Simulator", "cover_t"), Spacer(1, 2),
           P("User &amp; presentation guide: how to run the app, use every screen and present it in 10 minutes", "cover_s"),
           Spacer(1, 9 * mm)]
    st.append(shot("cover", "The Command center: every number on screen is computed live by the trained LightGBM models.", width=W))
    st += [Spacer(1, 5 * mm), table([
        ["What is inside", ""],
        ["Part 1 · Setup", "Start the app, check that it works, fix common problems"],
        ["Part 2 · Screen guide", "Command center, Run the store (game), Censoring lab, Model X-ray: what each control does, step by step"],
        ["Part 3 · Presenting", "A 10-minute demo script, the numbers to quote, a rehearsal checklist and a backup plan"],
        ["Part 4 · Questions", "Ten questions an evaluator is likely to ask, with honest answers"],
        ["Appendix", "How the engine works, verification results, glossary"],
    ], [42 * mm, W - 42 * mm]), Spacer(1, 6 * mm), P("Version of 19 November 2026 · app at http://localhost:3000", "small"), PageBreak()]

    # ---------------------------------------------------------------- overview
    st += [P("OVERVIEW", "eyebrow"), P("The app in one minute", "h1"),
           P("Recorded sales understate demand whenever a shelf runs empty: once the product is gone, customers still arrive but "
             "nothing more is sold. The project trains demand models that account for this, then turns their forecasts into order "
             "quantities with the newsvendor rule. The Stockout Simulator lets anyone see this happen. It runs the "
             "<b>real trained models</b> (9 LightGBM boosters, 4,008 trees) on the <b>real dataset</b> (5,000 store-products, "
             "28 Mar to 2 Jul 2024) inside a 3D, game-like web app."),
           table([
               ["Screen", "What you do", "What it shows"],
               ["Command center", "Pick a cost scenario, drag a cost-ratio slider, click a city", "Network KPIs, 18 cities as 3D towers, a live ranking of ordering policies, the paper's 9-policy results, the Power BI report"],
               ["Run the store", "Run a real store for the held-out week; order every morning", "Customers follow each product's real hourly demand; stockouts and waste happen; your cost is scored against the AI and two baselines"],
               ["Censoring lab", "Apply the paper's stockout mechanisms A/B/C or force stockouts by clicking", "How much demand gets hidden, hour by hour, and how each model's forecast shifts when it sees censored history"],
               ["Model X-ray", "Drag any of the 33 inputs of one forecast", "All five models re-score instantly; a 3D forest of the 208 trees; SHAP explanation"],
           ], [30 * mm, 55 * mm, W - 85 * mm]),
           box("Why the audience can trust the numbers",
               "The app does not imitate the model. The trees were exported from LightGBM and re-implemented in JavaScript, together with "
               "the feature pipeline. A verification script compares the two on 3,000 rows: <b>0 feature mismatches</b>, model scores "
               "<b>identical</b> to Python, and final forecasts equal to the Power BI warehouse up to its 4-decimal rounding. The badge "
               "in the top-right corner of every screen refers to this check."),
           P("Key terms", "h3"),
           table([
               ["Term", "Meaning"],
               ["Full-stock (donor) day", "A day with no stockout hour between 06:00 and 21:59. Its sales equal the true demand, so it can be scored."],
               ["Censored day", "A day on which the shelf ran empty. True demand is unknown, so the day is shown but never scored."],
               ["Newsvendor order", "Order the demand quantile at the critical ratio <b>β = c_u / (c_u + c_o)</b>, where c_u is the cost of a unit short and c_o the cost of a unit left over."],
               ["Held-out week", "26 Jun to 2 Jul 2024. Models never saw it during training; each day is forecast from the history up to the day before."],
           ], [38 * mm, W - 38 * mm]),
           PageBreak()]

    # ---------------------------------------------------------------- part 1 setup
    st += [P("PART 1", "eyebrow"), P("Setup", "h1"), P("1.1 What you need", "h2"),
           table([["Item", "Version / location"],
                  ["Windows laptop with a modern browser", "Chrome, Edge or Brave with hardware acceleration on (needed for the 3D scenes)"],
                  ["Node.js", "18 or newer (tested with 24.19)"],
                  ["Python", "3.11+ with pandas, numpy, pyarrow, lightgbm (only to regenerate the data)"],
                  ["Dataset", "data/train.parquet and data/eval.parquet in the repository (check with python scripts/verify_data.py)"],
                  ["Generated files", "planner/output/ (models) and simulator/data/ (exported assets) - both already built on this laptop"]],
                 [55 * mm, W - 55 * mm]),
           P("1.2 Start the app (everyday use)", "h2"),
           P("Everything is already built on this laptop, so one command is enough. Open PowerShell in the repository folder:"),
           P("cd \"C:\\ML project\\stockout\\stockout\\simulator\"<br/>npm start", "code"),
           P("Wait for the line <font face='Mono'>Stockout Simulator on http://localhost:3000</font> (about 5 seconds while the models load), "
             "then open <b>http://localhost:3000</b> in the browser. Keep the PowerShell window open during the demo; closing it stops the app."),
           P("1.3 Rebuild from scratch (new laptop or changed data)", "h2"),
           P("python planner/pipeline.py              # retrain models, ~2 min<br/>"
             "cd simulator<br/>npm install                             # once<br/>"
             "npm run export                          # export models + data for the app<br/>"
             "npm run verify                          # JS engine vs Python, must print 3x PASS<br/>"
             "npm run build                           # build the front end<br/>npm start", "code"),
           P("<b>Direct links:</b> <font face='Mono'>#command</font>, <font face='Mono'>?store=891#game</font> (game with Store 891 "
             "pre-selected, recommended for demos), <font face='Mono'>#lab</font> and <font face='Mono'>#xray</font> after "
             "http://localhost:3000/."),
           P("1.4 Troubleshooting", "h2"),
           table([["Symptom", "Cause", "Fix"],
                  ["Browser shows 'This site can't be reached'", "Server not running", "Run npm start in the simulator folder and wait for the ready line"],
                  ["'Front end not built yet'", "web/dist missing", "Run npm run build, then refresh"],
                  ["Error EADDRINUSE on start", "Port 3000 already used (an old server)", "Close the other window, or start on another port: $env:PORT=3001; npm start"],
                  ["3D areas stay black or empty", "WebGL disabled", "Browser settings → System → turn on 'Use graphics acceleration', restart the browser"],
                  ["Error about missing data/config.json", "Assets not exported", "Run npm run export (needs planner/output/ from pipeline.py)"]],
                 [45 * mm, 42 * mm, W - 87 * mm]),
           PageBreak()]

    # ---------------------------------------------------------------- part 2: command center
    st += [P("PART 2 · SCREEN GUIDE", "eyebrow"), P("2.1 Command center", "h1"),
           P("The landing page. It answers the manager's question: across the network, how often do shelves run empty and how much "
             "does each ordering policy cost? The numbers cover the held-out week, scored on the 20,641 store-product-days with full stock."),
           shot("s01_cmd_top", "Command center with the default scenario (Equal costs)."),
           markers([
               "<b>Cost scenario.</b> Which unit costs the orders were placed for: excess stock more costly (β = 0.25), equal costs (β = 0.50) or shortage more costly (β = 0.75).",
               "<b>What-if slider.</b> Re-scores the same orders at another ratio of shortage cost to waste cost. Orders are not re-optimised, only re-priced.",
               "<b>KPI tiles.</b> Fill rate of the stockout-aware policy, observed stockout rate (real data, 97 days), forecast accuracy (1 - WAPE) and cost saving against the seasonal-naive rule.",
               "<b>City towers.</b> One tower per city: height = stockout rate, lighter colour = bigger cost saving. Hover for details; click to filter every number on the page; click again (or empty space) to clear. Drag to rotate, scroll to zoom.",
               "<b>Policy race.</b> The five demo policies ranked by cost at the chosen ratio. Bars re-order live as you move the slider; the table below gives fill rate, waste share and cost.",
               "<b>Launch buttons</b> to the three other screens (also in the top navigation).",
           ]),
           P("Try this", "h3"),
           steps(["Read the four KPI tiles aloud: <b>77.1%</b> fill rate, <b>44.0%</b> of store-product-days with a stockout, <b>66.3%</b> accuracy, <b>15.2%</b> cheaper than seasonal naive.",
                  "Click the tallest tower (City 02, 49% stockout rate). All numbers now describe that city only.",
                  "Click <b>Shortage more costly</b>: the fill rate rises to 89.0% because the policy now orders more.",
                  "Drag the what-if slider to 3× and watch the ranking change. No single policy wins under every cost ratio, which is one of the paper's findings."]),
           shot("s03_cmd_shortage", "Shortage more costly: the policies order more, fill rate rises and the ranking changes."),
           markers(["Scenario switched to <b>Shortage more costly</b>.",
                    "At a 1× re-pricing the uncalibrated model now ranks first: rankings depend on costs.",
                    "The table keeps the scenario's own costs: the stockout-aware + conformal policy is 13.7% cheaper than seasonal naive."]),
           shot("s02_cmd_bottom", "Lower part of the page: the paper's 9 policies and the Power BI report."),
           markers(["<b>The paper's results</b> (run E): 9 ordering policies trained on histories censored by simulated stockouts, at the same what-if ratio. TFT policies (*) cover a 600-series subset only.",
                    "<b>Power BI report.</b> Thumbnails of the five report pages built on the same star schema. Click one to enlarge it."]),
           PageBreak()]

    # ---------------------------------------------------------------- game
    st += [P("PART 2 · SCREEN GUIDE", "eyebrow"), P("2.2 Run the store (the game)", "h1"),
           P("You manage a real fresh-food store for the held-out week. Each morning the stockout-aware model forecasts every shelf from "
             "the real sales history up to yesterday, and you decide how much to order. Then the store opens: customers arrive "
             "following that product's <b>real hourly demand</b>. If a shelf empties they walk away (lost sales); whatever is left at "
             "22:00 is thrown away (waste)."),
           box("Scoring rules (identical to the paper's evaluation)",
               "Daily cost = c_u × units short + c_o × units left over, summed over scored shelves. A shelf is scored only on days when the "
               "real store never ran out, because only then is the true demand known. Shelves where the real store sold out are replayed "
               "as they happened, labelled <b>censored</b>, and excluded from every score - yours, the AI's and the baselines'. You are "
               "compared with three policies: <b>AI</b> (stockout-aware LightGBM + pooled conformal), <b>seasonal naive</b> (last week's "
               "sales) and <b>raw-sales quantile LightGBM</b>."),
           shot("s04_game_setup", "Setup screen, opened with the link localhost:3000/?store=891#game."),
           markers(["<b>Store.</b> Real stores from the sample, busiest first. Each option shows the number of products and scored shelf-days.",
                    "<b>Unit costs.</b> c_u and c_o set the critical ratio β. Equal costs (1 and 1) give β = 0.50, so everyone orders the median forecast.",
                    "<b>Start the week.</b> Loads day 1 (Wed 26 Jun) and runs the model for every shelf."]),
           shot("s05_game_morning", "Morning of day 1: the 3D store before opening and the forecast cards."),
           markers(["<b>Store clock.</b> 05:30 before opening, then 06:00 to 22:00.",
                    "<b>Week cost so far</b> for you, the AI and seasonal naive (lower is better).",
                    "<b>Use AI orders / Use seasonal naive</b> copy one policy's orders into all your sliders.",
                    "<b>Open the store</b> starts the day.",
                    "<b>Forecast cards</b>, one per shelf: the last 21 days of sales (red dots = sold out), the forecast band of the three models (bar = q25-q90, white tick = median, triangle = that model's order) and <b>your order slider</b>. Coloured ticks on the slider mark the AI and seasonal-naive orders. Cards marked 'real stockout' are not scored."]),
           shot("s06_game_open", "The store at 12:00: customers buy products, shelves empty, censored shelves are labelled."),
           markers(["The clock advances one hour every 1.3 s (faster with 2× / 4×).",
                    "A <b>censored</b> shelf: the real store sold out here, so its demand is unknown.",
                    "Customers carry a box in the product's colour when served. A customer who finds an empty shelf turns red and leaves.",
                    "<b>Live feed</b>: stockout events with the hour they happened.",
                    "<b>Speed</b>: 1×, 2× or 4×."]),
           shot("s07_game_close", "22:00, closing time on day 1 in Store 891."),
           markers(["<b>Closing time</b> panel: today's cost per policy. Here: you 2.51, AI 2.58, seasonal naive 4.45, raw-sales 2.35.",
                    "<b>Next day</b> loads tomorrow; the model now forecasts from a history that includes today.",
                    "Shelf signs show SOLD OUT or what is left, i.e. tonight's waste."]),
           shot("s08_game_close_cards", "After closing, every scored card reveals the actual demand and a per-policy result table."),
           markers(["The red line on the forecast band is the actual demand. The table shows each policy's order, units short, waste and cost."]),
           shot("s09_game_final", "Week complete: Store 891 after 7 days (orders copied from the AI)."),
           markers(["<b>Verdict</b> comparing your total with the AI: beat the model, dead heat (within 3%) or the model wins.",
                    "<b>Week totals</b> with fill rate, units short and waste. In Store 891 the AI costs 11.58 against 20.93 for seasonal naive (45% lower) - exactly the figure in the project's warehouse.",
                    "<b>Daily cost chart</b> for all four policies. Play another store to start again."]),
           P("Step by step", "h3"),
           steps(["Open <b>localhost:3000/?store=891#game</b> and click <b>Start the week</b>.",
                  "Read one forecast card aloud: the band, the median and the order triangles. Point out a 'real stockout' card and explain why it is not scored.",
                  "Set your orders: drag sliders, or click <b>Use AI orders</b> and then change one or two shelves to show your own judgement.",
                  "Click <b>Open the store</b>. Switch to 2× if time is short. Point at a SOLD OUT sign and the live feed.",
                  "At 22:00 read the closing panel, scroll down to show a card's actual demand, then click <b>Next day</b>.",
                  "Repeat for 7 days (about 1 minute per day at 4×) or stop after one day and quote the full-week result from this guide."]),
           box("Choosing a store honestly",
               "Across the 143 busy stores offered in the list, the AI beats seasonal naive in <b>116 (81%)</b>. Store 891 is a clear win "
               "(-45%). Store 074, the first in the list, is close to a tie. Stores containing product P267 (for example 529, 297 or 89) are "
               "where the model fails: P267's demand jumped and the model under-forecasts it by 64%, the same item flagged in the Power BI "
               "memo. Showing one of these on purpose is a strong, honest talking point about planner overrides.", ORANGE, "#fdf1ec"),
           PageBreak()]

    # ---------------------------------------------------------------- lab
    st += [P("PART 2 · SCREEN GUIDE", "eyebrow"), P("2.3 Censoring lab", "h1"),
           P("This screen shows the core problem of the project. On a full-stock day the hourly sales are the true demand. The lab gives "
             "such a day a limited stock and replays it hour by hour: once the shelf is empty, demand keeps arriving but sales stop. The "
             "censored history is fed back through the real feature pipeline, and the models forecast the held-out week again."),
           shot("s10_lab_top", "Censoring lab on store-product S343 / P300 with mechanism A."),
           markers(["<b>Store-product picker</b> (city, store, product).",
                    "<b>Mechanism.</b> Real history (no change), A (stock around the 14-day mean, refills on 14.7% of days), B (A with lower stock on promotion days), C (half the stock, no refills: heavy censoring), or Manual.",
                    "<b>Summary tiles.</b> Days censored, units of demand hidden from the model, and how much each model's median forecast for the held-out week moves.",
                    "<b>97-day chart.</b> Grey = what really happened, orange = what the model sees, × = day censored here, ○ = real stockout day. Click any day to open its hour-by-hour view."]),
           box("The result to point at",
               "With mechanism A on S343 / P300, 53 of 54 full-stock days are censored and 106.1 units of demand disappear. The raw-sales "
               "model's forecast drops <b>10.2%</b> and seasonal naive <b>14.4%</b>, while the stockout-aware model moves <b>+0.5%</b>. "
               "With mechanism C the drops are 20.9% (stockout-aware) against 44.0% (raw-sales) and 39.4% (seasonal naive)."),
           shot("s11_lab_mid", "Hour-by-hour view of one censored day, and the forecast comparison for the held-out week."),
           markers(["<b>Hour by hour</b> (06:00-22:00): dashed bars = true demand, blue = sales the model sees, green line = stock on the shelf, red band = out of stock, green dashed line = opening stock, vertical green line = refill (mechanism A/B).",
                    "<b>Forecasts from real vs censored history</b>: solid lines from the real history, dashed lines from the censored one, red dots = actual demand on full-stock days.",
                    "<b>Accuracy table</b>: WAPE with real and censored history, and the forecast shift."]),
           shot("s12_lab_mechC", "Mechanism C (no refills) censors more demand."),
           markers(["Switch mechanisms with one click; every chart and number updates in under a second.",
                    "The shift tile shows the stockout-aware forecast falling far less than the other two."]),
           shot("s13_lab_batch", "Batch experiment: mechanism C on 60 random store-products."),
           markers(["<b>Run mechanism</b>: censors 60 random store-products, rebuilds their features and re-scores 7 days with every model (about 10 seconds).",
                    "<b>Result table.</b> In this run the stockout-aware forecast shifts -18.9%, raw-sales -22.8% and seasonal naive -32.8% across 2,404 censored days."]),
           P("Manual mode", "h3"),
           steps(["Click <b>Manual</b> and set 'Stock as share of demand' (for example 40%).",
                  "Click full-stock days on the 97-day chart (grey line, no ○). Each click gives that day only 40% of its demand as stock; click again to undo.",
                  "Watch the hidden-demand tile and the forecast shift grow as you add days, especially days in the last two weeks before the held-out week."]),
           box("Say it honestly",
               "Both demo models were trained on the real recorded history, so heavy censoring at forecast time pulls both down. The "
               "stockout-aware model is consistently less affected, but not immune. The paper trains on censored histories and measures "
               "exactly this transfer gap.", ORANGE, "#fdf1ec"),
           PageBreak()]

    # ---------------------------------------------------------------- xray
    st += [P("PART 2 · SCREEN GUIDE", "eyebrow"), P("2.4 Model X-ray", "h1"),
           P("Opens one forecast: one store-product on one held-out day. These are the exact 33 inputs the model receives, all computed "
             "from earlier days. Change any of them and the real models re-score immediately."),
           shot("s14_xray_top", "Model X-ray for S343 / P300 on Wed 26 Jun."),
           markers(["<b>Store-product picker.</b>", "<b>Day</b> in the held-out week.",
                    "<b>Result tiles</b>: median forecast, newsvendor order at the current β, the 80% interval with its conformal pool, and what really happened (15.40 units).",
                    "<b>Inputs</b> grouped by sales history, stockout history, promotions &amp; weather and calendar. A blue bar marks inputs you changed. <b>Reset inputs</b> (top right) restores them.",
                    "<b>All five models</b> for this day: bar = q25-q90 (darker = q25-q75), white tick = median, triangle = order at β, red line = actual demand."]),
           shot("s15_xray_edit", "'Average for this weekday' dragged from 9.04 down to 2.28: the median forecast falls 34.3%."),
           markers(["The changed input is marked blue.", "Tiles show the new value and the old one (8.77 → 5.76).", "Every model's band moves at once."]),
           box("Drag down, not up",
               "Tree models cannot extrapolate. For this row no tree splits on 'average for this weekday' above about 9, so raising it "
               "changes nothing, while lowering it has a large effect. If someone asks, this is the answer: gradient-boosted trees are "
               "flat outside the range they learned.", ORANGE, "#fdf1ec"),
           shot("s16_xray_bottom", "The q50 model as a 3D forest, SHAP contributions and the features used on this row's decision paths."),
           markers(["<b>Forest</b>: 208 columns, one per tree. Height = the leaf value this row lands in (blue raises the forecast, orange lowers it). Columns grow live as you edit. Drag to rotate.",
                    "<b>SHAP</b> (LightGBM TreeSHAP for the unedited row): baseline 0.85 plus contributions = 8.64 before the conformal shift. The largest driver is the weekday average (+2.56).",
                    "<b>Decision paths</b>: how many of the 208 trees asked about each feature. Product (116 trees) and store (102) dominate."]),
           PageBreak()]

    # ---------------------------------------------------------------- part 3 presenting
    st += [P("PART 3", "eyebrow"), P("Presenting the app", "h1"), P("3.1 Ten-minute demo script", "h2"),
           table([
               ["Time", "Screen and action", "What to say"],
               ["0:00-1:00", "Command center, top of page", "\"When a shelf runs empty, sales stop telling the truth. 44% of store-product-days in this data had a stockout, so a model trained on raw sales learns the wrong demand.\""],
               ["1:00-2:30", "Click City 02, then clear. Drag the what-if slider to 3×", "\"Every number here is computed live by the real trained models, checked against Python. The calibrated policy is 15.2% cheaper than ordering last week's sales and wastes 12% of orders instead of 20%. Watch the ranking change when shortages cost more: no policy wins everywhere.\""],
               ["2:30-5:30", "Run the store at ?store=891. Use AI orders, change one shelf, Open the store at 2×", "\"This is a real store and real hourly demand. The model forecasts from yesterday's history only, the paper's protocol. Shelves that really sold out are not scored, because their true demand is unknown. Over the full week the AI costs 11.58 here against 20.93 for the baseline.\""],
               ["5:30-7:30", "Censoring lab, mechanism A, click a censored day, then C, then Run batch", "\"Here I hide demand on purpose. Look at the hour view: the shelf is empty from 09:00, the demand after that is invisible. Raw-sales forecasts drop 10-44%; the stockout-aware model drops far less, though it is not immune.\""],
               ["7:30-9:00", "Model X-ray, drag 'average for this weekday' down", "\"These are the 33 inputs of one forecast. The weekday average is the biggest driver, and here are the 208 trees voting. This is not a black box.\""],
               ["9:00-10:00", "Back to Command center, Power BI thumbnails", "\"The same star schema feeds the Power BI report for managers; this app is the planner's tool. Limits: costs are relative, scoring uses full-stock days only, and the demo models were trained on real rather than censored history. Next step: train on censored histories and add planner overrides for items like P267.\""],
           ], [18 * mm, 52 * mm, W - 70 * mm]),
           P("3.2 Numbers to quote", "h2"),
           table([
               ["Fact", "Value", "Where it shows"],
               ["Store-products · days · held-out week", "5,000 · 97 (28 Mar-2 Jul 2024) · 26 Jun-2 Jul", "Header text"],
               ["Models · trees · inputs", "9 LightGBM · 4,008 trees · 33 features", "Badge, X-ray"],
               ["Verification vs Python", "0 feature mismatches on 3,000 rows; scores identical", "Badge (npm run verify)"],
               ["Fill rate (equal costs)", "77.1% (seasonal naive 81.0%)", "Command center"],
               ["Stockout rate", "44.0% of store-product-days", "Command center"],
               ["Forecast accuracy (1 - WAPE)", "66.3%", "Command center"],
               ["Cost saving vs seasonal naive", "15.2% (waste 12.3% vs 20.4% of orders)", "Command center"],
               ["Paper, equal costs, matched cells", "pooled conformal 0.398 vs seasonal naive 0.468 (-14.8%)", "Command center, lower panel"],
               ["Game, Store 891, full week", "AI 11.58 · seasonal naive 20.93 · raw-sales 12.16", "Run the store"],
               ["AI beats seasonal naive", "in 116 of 143 busy stores (81%)", "This guide"],
               ["Lab, S343 / P300, mechanism A", "forecast shift +0.5% (stockout-aware) vs -10.2% (raw) vs -14.4% (naive)", "Censoring lab"],
               ["Lab batch, mechanism C, 60 series", "-18.9% vs -22.8% vs -32.8%", "Censoring lab"],
           ], [52 * mm, 72 * mm, W - 124 * mm]),
           PageBreak(),
           P("3.3 Rehearsal checklist", "h2"),
           P("<b>The evening before</b>", "h3"),
           steps(["Run the full 10-minute script once with a timer.", "Play one complete week in Store 891 so you know the flow.",
                  "Run <font face='Mono'>npm run verify</font> and keep the three PASS lines visible in a terminal tab, in case someone asks for proof.",
                  "Charge the laptop; set Windows to never sleep while plugged in."]),
           P("<b>Ten minutes before</b>", "h3"),
           steps(["Close other heavy apps (games, video calls you are not presenting from) so the 3D scenes stay smooth.",
                  "Start the server (<font face='Mono'>npm start</font>) and wait for the ready line.",
                  "Open four browser tabs in this order: #command, ?store=891#game, #lab, #xray. Visit each once so the models are warm.",
                  "Press F11 for full screen; check the 3D towers rotate smoothly.",
                  "If presenting on a projector, set Windows display to Duplicate at 1920×1080."]),
           P("3.4 Backup plan", "h2"),
           table([["If this happens", "Do this"],
                  ["The server will not start", "Present from this PDF: every screen is here with the real numbers."],
                  ["3D scenes are slow on the projector", "Lower the browser zoom to 80%, or keep the store at 1× speed; the charts work without 3D."],
                  ["A number differs from this guide", "You changed the cost sliders or the store. Reload the page (F5) to reset the defaults."],
                  ["No internet", "Not needed. The app runs entirely on the laptop (only the font falls back to the system font)."]],
                 [55 * mm, W - 55 * mm]),
           PageBreak()]

    # ---------------------------------------------------------------- part 4 Q&A
    qa = [
        ("Is this really your model, or an animation?",
         "It is the real model. The 9 boosters were exported tree by tree and the feature pipeline re-implemented. On 3,000 test rows the features match Python exactly and the scores are identical; the final forecasts equal the Power BI warehouse. I can run the check live (npm run verify)."),
        ("Why is the AI's fill rate lower than seasonal naive's?",
         "Because the baseline over-orders: it serves 81.0% of demand but throws away 20.4% of what it orders. The calibrated policy serves 77.1% and wastes 12.3%, which is 15.2% cheaper at equal costs. The service level is a business choice set through β; at 'shortage more costly' the fill rate rises to 89%."),
        ("Why does seasonal naive win in some stores?",
         "The AI wins in 81% of busy stores. It loses where demand changes suddenly, such as product P267, whose demand jumped while the model under-forecast it by 64%. I would flag such items for planner review, which the Power BI drill-through and the app's planner link support."),
        ("What is a donor day and why exclude censored days?",
         "A donor day has no stockout hour, so sales equal demand. On a censored day we only know a lower bound of demand, so any cost computed on it would be wrong. The paper, the warehouse and the game all score donor days only."),
        ("If the model is 'stockout-aware', why does it also drop in the lab?",
         "The demo models were trained on the real history, where they learned from donor-day labels but see censored inputs at forecast time. Heavier censoring lowers those inputs. The stockout-aware model drops less (-18.9% vs -22.8% in the batch) but is not immune. The paper trains on simulated censored histories and measures this transfer gap explicitly."),
        ("On real history the raw-sales models are about as good. So why bother?",
         "Scored on full-stock days of real data, the two are close (0.373 vs 0.392 at equal costs). The advantage of stockout-aware training shows when censoring is heavy and known, which is what the paper's simulated mechanisms and the lab demonstrate."),
        ("How did you choose the costs?",
         "The data has no prices, so costs are relative. The three scenarios set c_u:c_o to 1:3, 1:1 and 3:1, i.e. β = 0.25, 0.50, 0.75. The what-if slider lets a manager plug in their own ratio."),
        ("Why does moving a slider sometimes do nothing?",
         "Tree ensembles are piecewise constant and flat outside the range they were trained on. Within the trained range the inputs have a clear effect, as the SHAP chart shows."),
        ("How would this run in production?",
         "Nightly batch scoring writes forecasts and orders to PostgreSQL; Power BI shows managers the KPIs with row-level security by city; planners use an app like this for overrides; models retrain weekly and conformal coverage is monitored."),
        ("What are the limitations?",
         "Costs are relative; lost sales are simulated, not recorded; scoring uses full-stock days, a selected sample; the evaluation covers one held-out week; and the demo cannot forecast beyond 2 July 2024 because features need the previous day's sales."),
    ]
    st += [P("PART 4", "eyebrow"), P("Questions you are likely to get", "h1")]
    for q, a in qa:
        st.append(KeepTogether([P(f"<b>Q. {q}</b>", "h3"), P(a)]))
    st.append(PageBreak())

    # ---------------------------------------------------------------- appendix
    st += [P("APPENDIX", "eyebrow"), P("How the app works", "h1"),
           table([["Layer", "Technology", "Role"],
                  ["Model pipeline", "Python, LightGBM (planner/pipeline.py)", "Trains q25/q50/q75/q90 demand models on full-stock days, raw-sales and point models, pooled conformal calibration, newsvendor orders"],
                  ["Asset export", "Python (simulator/export/export_assets.py)", "Writes the trees as JSON, the hourly sales/stock panel, SHAP values and 3,000 verification rows"],
                  ["Engine", "Node.js (simulator/server/engine)", "LightGBM tree-walker, 33-feature builder, conformal pools, newsvendor rule, the paper's stockout simulator"],
                  ["API", "Express (server/index.js)", "Endpoints for the network, game days, censoring runs and X-ray scoring"],
                  ["Front end", "React, three.js (react-three-fiber), zustand, SVG charts", "The four screens and the 3D scenes"]],
                 [30 * mm, 55 * mm, W - 85 * mm]),
           P("Verification output", "h3"),
           P("[PASS] features: 3000 rows x 33 features, 0 mismatches<br/>"
             "[PASS] booster scores: 9 models, max |JS - Python| = 0.00e+0<br/>"
             "[PASS] final quantiles vs warehouse: 2433 rows x 5 models x 4 quantiles, max diff = 5.00e-5", "code"),
           P("The stockout simulator's random streams (splitmix64 hashes) match the notebook exactly, and the inverse normal matches "
             "scipy to 1.3 × 10<super>-15</super>."),
           P("Glossary", "h3"),
           table([["Term", "Definition"],
                  ["WAPE", "Weighted absolute percentage error: Σ|forecast - actual| / Σ actual. Accuracy = 1 - WAPE."],
                  ["Quantile q25 … q90", "The value demand stays below with 25% … 90% probability. q50 is the median forecast."],
                  ["Pooled conformal calibration", "A shift added to each quantile, estimated from errors on calibration days pooled by category × sales tier, so that the q-levels are hit at the right rate."],
                  ["Fill rate", "Units sold / demand on scored days."],
                  ["Waste share", "Units left over / units ordered."],
                  ["Seasonal naive", "Order based on the same weekday last week (plus a residual quantile)."],
                  ["Mechanisms A / B / C", "The paper's stockout simulators: A with occasional refills, B with lower stock on promotions, C with half the stock and no refills."]],
                 [42 * mm, W - 42 * mm]),
           P("Files", "h3"),
           table([["Path", "Contents"],
                  ["simulator/README.md", "Short technical readme"],
                  ["simulator/server/", "Engine, API, verification script"],
                  ["simulator/web/src/", "Front end (pages, 3D scenes, charts)"],
                  ["simulator/docs/", "This guide, its screenshots and the script that builds it"],
                  ["planner/", "Model pipeline, Power BI project, PostgreSQL loader"]], [55 * mm, W - 55 * mm])]

    merged = []
    for item in st:
        if getattr(item, "_legend", False) and merged and getattr(merged[-1], "_shot", False):
            merged[-1] = KeepTogether([*merged[-1]._content, Spacer(1, 1), item])  # flat: nested KeepTogether always forces a break
        else:
            merged.append(item)
    st = merged
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=18 * mm,
                            title="Stockout Simulator - user & presentation guide", author="Stockout-aware demand forecasting project")
    doc.build(st, onFirstPage=on_page, onLaterPages=on_page)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    prep_shots()
    build()
