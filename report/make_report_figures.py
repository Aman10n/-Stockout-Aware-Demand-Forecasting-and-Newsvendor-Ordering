"""Diagrams and data charts drawn for the project report (PNG, 200 dpi)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

R = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "assets" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
EDGE = "#34495e"


def box(ax, x, y, w, h, head, body="", face="#e8f0f5", hs=10.5, bs=8.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", lw=1.1, ec=EDGE, fc=face))
    if body:
        ax.text(x + w / 2, y + h - 0.28, head, ha="center", va="center", fontsize=hs, weight="bold")
        ax.text(x + w / 2, y + (h - 0.45) / 2, body, ha="center", va="center", fontsize=bs, linespacing=1.35)
    else:
        ax.text(x + w / 2, y + h / 2, head, ha="center", va="center", fontsize=hs, weight="bold")


def arrow(ax, a, b, color=EDGE, ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, lw=1.2, color=color,
                                 linestyle=ls, shrinkA=0, shrinkB=0))


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, w * 1.6), ylim=(0, h * 1.6))
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, facecolor="white")
    plt.close(fig)
    print(name)


def architecture():
    fig, ax = canvas(10, 7.6)  # 16 x 12.16 units
    box(ax, 0.3, 10.5, 15.4, 1.35, "Data layer",
        "FreshRetailNet-50K v1.0 (Dingdong-Inc, CC BY 4.0):  train.parquet 4,500,000 rows (50,000 series x 90 days)"
        "  +  eval.parquet 350,000 rows (7 days)\nhourly sales + hourly stock-status flags, discount, promotion, holiday,"
        " weather  |  verified by SHA-256 (scripts/verify_data.py)", "#e3ecf7")
    box(ax, 0.3, 6.6, 7.4, 3.3, "Research pipeline (notebooks)",
        "Phase 0  data audit, stratified 5,000-series sample\nPhase 1  past-only features (leakage test)\n"
        "Phase 2  simulated stockouts A / B / C\nPhase 3-4  baselines + LightGBM demand quantiles\n"
        "Phase 5-7  TimesNet/TFT, Kaplan-Meier, conformal\nPhase 8  9 ordering policies + protocol lock\n"
        "Phase 9  locked final-week evaluation", "#e9f4ec", bs=8.4)
    box(ax, 8.3, 6.6, 7.4, 3.3, "Decision-support pipeline (planner/pipeline.py)",
        "same split: fit 1-60, tune 61-75, calibrate 76-90, test 91-97\n33 past-only features, 9 LightGBM boosters\n"
        "(demand q25-q90, raw q25-q90, raw point)\npooled conformal shift + monotone rearrangement\n"
        "newsvendor orders for 3 cost scenarios x 5 policies\nwrites star-schema CSVs + models + residual tables",
        "#fdf3e1", bs=8.4)
    box(ax, 0.3, 3.75, 7.4, 2.25, "Saved results  (results/)",
        "run S (5K, Phases 0-4)  |  run P (50K, Phases 0-4)\nrun E (5K, Phases 0-9): metrics, figures, manifests,\n"
        "final_test_lock.json, bootstrap intervals", "#eef3e9", bs=8.4)
    box(ax, 8.3, 3.75, 3.55, 2.25, "Warehouse", "10 CSV tables\nstar schema\n(planner/output/warehouse)", "#f6eadb", bs=8.2)
    box(ax, 12.15, 3.75, 3.55, 2.25, "PostgreSQL", "schema stockout\n3 views, loader with\nvalidation checks", "#f6eadb", bs=8.2)
    box(ax, 0.3, 0.35, 4.8, 2.75, "IEEE paper", "paper/main.tex, main.pdf\ntables regenerated from\nresults/ by scripts", "#f1ecf7", bs=8.4)
    box(ax, 5.6, 0.35, 3.3, 2.75, "Power BI report", "5 pages + tooltip\n51 DAX measures\nrow-level security", "#f1ecf7", bs=8.4)
    box(ax, 9.25, 0.35, 3.1, 2.75, "Streamlit planner", "live LightGBM scoring\nSHAP, what-if,\nbatch scoring", "#f1ecf7", bs=8.4)
    box(ax, 12.7, 0.35, 3.0, 2.75, "3D simulator", "Node.js engine +\nReact / three.js\n4 screens", "#f1ecf7", bs=8.4)
    ax.text(0.3, 3.3, "Presentation layer", fontsize=9, style="italic", color="#6b5b95")
    for x in (4.0, 12.0):
        arrow(ax, (x, 10.5), (x, 9.9))
    arrow(ax, (4.0, 6.6), (4.0, 6.0))
    arrow(ax, (10.0, 6.6), (10.0, 6.0))
    arrow(ax, (11.85, 4.85), (12.15, 4.85))
    arrow(ax, (2.7, 3.75), (2.7, 3.1))
    arrow(ax, (7.2, 3.75), (7.2, 3.1))
    arrow(ax, (9.3, 3.75), (7.6, 3.1))
    arrow(ax, (10.2, 3.75), (10.8, 3.1))
    arrow(ax, (11.6, 3.75), (14.0, 3.1))
    arrow(ax, (7.7, 7.8), (8.3, 7.8))
    ax.text(8.0, 8.05, "selected\nseries", ha="center", fontsize=7, color=EDGE)
    arrow(ax, (8.9, 1.7), (9.25, 1.7), color="#9a3d2d", ls="--")
    ax.text(9.07, 2.05, "drill-\nthrough", ha="center", fontsize=6.5, color="#9a3d2d")
    save(fig, "fig_architecture.png")


def workflow():
    fig, ax = canvas(10, 6.2)  # 16 x 9.92
    phases = [("Phase 0", "data audit,\nstratified sample"), ("Phase 1", "past-only\nfeatures + audit"),
              ("Phase 2", "simulated\nstockouts A/B/C"), ("Phase 3", "conventional\nbaselines"),
              ("Phase 4", "LightGBM demand\nquantiles (x12)"), ("Phase 5", "TimesNet\nrecovery + TFT"),
              ("Phase 6", "Kaplan-Meier\npools"), ("Phase 7", "pooled conformal\ncalibration"),
              ("Phase 8", "9 ordering\npolicies + LOCK"), ("Phase 9", "locked final-week\nevaluation")]
    w, h, gap = 2.8, 1.75, 0.4
    for i, (hd, bd) in enumerate(phases):
        r, c = divmod(i, 5)
        c = c if r == 0 else 4 - c
        x = 0.3 + c * (w + gap)
        y = 6.9 if r == 0 else 3.9
        face = "#e9f4ec" if i < 5 else ("#fdf3e1" if i < 9 else "#f6e1e1")
        box(ax, x, y, w, h, hd, bd, face, hs=10, bs=8.6)
        if i < 9:
            if i == 4:
                arrow(ax, (x + w / 2, y), (x + w / 2, 3.9 + h))
            elif r == 0:
                arrow(ax, (x + w, y + h / 2), (x + w + gap, y + h / 2))
            else:
                arrow(ax, (x, y + h / 2), (x - gap, y + h / 2))
    ax.text(8.0, 9.25, "Runs S (5K) and P (50K): Phases 0-4 only      Run E (5K): Phases 0-9",
            ha="center", fontsize=9.5, style="italic", color="#9a3d2d")
    box(ax, 0.3, 0.35, 15.4, 2.6, "Locked final week (days 91-97, 2024-06-26 to 2024-07-02)",
        "3 x 3 transfer matrix (train mechanism x test history)  x  3 cost ratios (beta = 0.25 / 0.50 / 0.75)  x  9 policies\n"
        "scored only on 20,641 exact donor rows  |  paired cluster bootstrap (200 reps, 866 city-store clusters)\n"
        "plus a definite-miss lower bound for q90 on 35,000 real rows per model (105,000 records)", "#f3f0f8", bs=9)
    arrow(ax, (0.3 + w / 2, 3.9), (0.3 + w / 2, 2.95))
    save(fig, "fig_workflow.png")


def split():
    fig, ax = plt.subplots(figsize=(10, 2.5))
    segs = [(1, 60, "Model fit\ndays 1-60\n2024-03-28 to 05-26", "#5b8fd6"),
            (61, 75, "Tuning\ndays 61-75\nto 06-10", "#7cb87c"),
            (76, 90, "Calibration\ndays 76-90\nto 06-25", "#e2a447"),
            (91, 97, "Final\n91-97\n06-26\nto 07-02", "#d65f5f")]
    for a, b, lab, col in segs:
        ax.barh(0, b - a + 1, left=a - 0.5, color=col, edgecolor="white", height=0.6)
        ax.text((a + b) / 2, 0, lab, ha="center", va="center", fontsize=8.2, color="white", weight="bold")
    ax.set_xlim(0, 98)
    ax.set_ylim(-0.6, 0.75)
    ax.set_yticks([])
    ax.set_xticks([1, 30, 60, 75, 90, 97])
    ax.set_xlabel("day index (97 days; train.parquet = days 1-90, eval.parquet = days 91-97)")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.text(48.5, 0.55, "every feature for day t uses only days < t; the final week was scored once, after the Phase 8 lock",
            ha="center", fontsize=8.5, style="italic")
    fig.tight_layout()
    save(fig, "fig_split.png")


def star():
    fig, ax = canvas(10, 6.4)  # 16 x 10.24
    facts = [("fact_sales_daily", "485,000 rows\nstore-product x day\nunits_sold, stockout_hours,\ndonor_flag, demand_proxy", 0.4),
             ("fact_forecast", "925,000 rows\nx model, days 61-97\nq25, q50, q75, q90,\nactual_demand, is_scored", 5.65),
             ("fact_order", "525,000 rows\nx policy x scenario\norder_qty, shortage,\nleftover, cost", 10.9)]
    for t, b, x in facts:
        box(ax, x, 3.9, 4.7, 2.45, t, b, "#fdf3e1", bs=8.4)
    dims = [("dim_date", "97 rows\nperiod, weekday", 0.4, 7.6),
            ("dim_series", "5,000 rows\ncity, store, product,\ncategories, tiers", 4.2, 7.6),
            ("dim_model", "5 forecast\nmodels", 8.0, 7.6), ("dim_policy", "5 ordering\npolicies", 11.8, 7.6),
            ("dim_scenario", "3 cost scenarios\nc_u, c_o, beta", 4.2, 0.5),
            ("security_user_city", "20 rows\nRLS e-mail -> city", 0.4, 0.5),
            ("fact_paper_policy_results", "243 rows: 9 policies\nx 3 x 3 cells x 3 costs", 8.0, 0.5),
            ("_Measures", "51 DAX measures\n(fact columns hidden)", 11.8, 0.5)]
    for t, b, x, y in dims:
        box(ax, x, y, 3.6, 2.0 if y > 5 else 2.1, t, b, "#e3ecf7" if t != "_Measures" else "#f1ecf7", hs=9.2, bs=8.2)
    links = [((2.75, 6.35), (2.2, 7.6)), ((2.75, 6.35), (6.0, 7.6)), ((8.0, 6.35), (2.6, 7.6)),
             ((8.0, 6.35), (6.4, 7.6)), ((8.0, 6.35), (9.8, 7.6)), ((13.25, 6.35), (3.0, 7.6)),
             ((13.25, 6.35), (6.8, 7.6)), ((13.25, 6.35), (13.6, 7.6)), ((13.25, 3.9), (6.0, 2.6)),
             ((9.8, 2.6), (7.8, 2.6))]
    for a, b in links:
        arrow(ax, a, b, color="#7a8a99")
    ax.annotate("", xy=(4.2, 8.3), xytext=(2.2, 2.6),
                arrowprops=dict(arrowstyle="-|>", color="#9a3d2d", ls="--", connectionstyle="arc3,rad=-0.35"))
    ax.text(0.12, 5.1, "RLS filter on city", fontsize=7.5, color="#9a3d2d", rotation=90, va="center")
    ax.text(8.0, 10.0, "Relationships are many-to-one and single-direction, from facts to dimensions (Power BI Import mode)",
            ha="center", fontsize=8.8, style="italic")
    save(fig, "fig_star_schema.png")


def newsvendor():
    from scipy.stats import gamma
    d = gamma(a=4, scale=2.0)
    Q = np.linspace(0, 25, 300)
    x = np.linspace(0, 45, 4501)
    pdf = d.pdf(x)
    dx = x[1] - x[0]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for cu, co, col in [(1, 3, "#5b8fd6"), (1, 1, "#7cb87c"), (3, 1, "#d65f5f")]:
        cost = [((co * np.clip(q - x, 0, None) + cu * np.clip(x - q, 0, None)) * pdf).sum() * dx for q in Q]
        beta = cu / (cu + co)
        qs = d.ppf(beta)
        ax.plot(Q, cost, color=col, lw=2, label=f"c_u={cu}, c_o={co}  ->  beta={beta:.2f}, Q*={qs:.1f}")
        ax.axvline(qs, color=col, ls=":", lw=1.2)
    ax.set_xlabel("order quantity Q (units)")
    ax.set_ylabel("expected cost")
    ax.legend(frameon=False, fontsize=8.5)
    ax.set_title("Illustration with Gamma(4, 2) demand: expected cost is lowest at the beta-quantile", fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, "fig_newsvendor.png")


def stockout_hours():
    fs = pd.read_csv(R / "planner/output/warehouse/fact_sales_daily.csv", usecols=["stockout_hours"])
    c = fs.stockout_hours.clip(0, 16).value_counts().sort_index().reindex(range(17), fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.bar(c.index, c.values / 1000, color=["#2e7d32"] + ["#c0392b"] * 16)
    ax.set_xlabel("stockout hours between 06:00 and 21:59 on a store-product-day")
    ax.set_ylabel("store-product-days (thousands)")
    ax.set_xticks(range(17))
    tot = c.sum()
    ax.text(0.6, c.iloc[0] / 1000 * 0.97, f"donor days\n{c.iloc[0]:,} ({c.iloc[0] / tot:.1%})",
            fontsize=8.5, va="top", ha="left", color="#2e7d32")
    ax.text(9.5, c.iloc[0] / 1000 * 0.55, f"censored days: {c.iloc[1:].sum():,} ({c.iloc[1:].sum() / tot:.1%})\n"
            "sales < demand, so demand is unknown", fontsize=8.5, color="#c0392b", ha="center")
    ax.set_title("5,000 sampled series x 97 days = 485,000 store-product-days", fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, "fig_stockout_hours.png")


def paper_schematics():
    sys.path.insert(0, str(R / "paper/scripts"))
    import make_diagrams as md

    def save_png(self, name):
        self.fig.savefig(OUT / name.replace(".pdf", ".png"), dpi=300, facecolor="white")
        plt.close(self.fig)
        print(name)

    md.Canvas.save = save_png
    md.lineage()
    md.mechanisms()


if __name__ == "__main__":
    architecture()
    workflow()
    split()
    star()
    newsvendor()
    stockout_hours()
    paper_schematics()
