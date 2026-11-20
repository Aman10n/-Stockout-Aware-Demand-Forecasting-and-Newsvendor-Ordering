"""Stockout-Aware Order Planner - interactive front end for the trained models.

Run from the repository root:   streamlit run planner/app.py
Needs planner/output/ (create it with: python planner/pipeline.py).
"""
from __future__ import annotations

import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from pipeline import MODEL_DIM, QN, SCENARIOS, TAUS, apply_table

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
WH = OUT / "warehouse"
APP = OUT / "app"
SHOTS = BASE / "powerbi" / "screenshots"
CONFIG = BASE / "config.json"

# reference palette (validated categorical order) + recessive inks
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
HEADLINE = "demand_conformal"
FRIENDLY = {
    "y_lag1": "sales yesterday", "y_lag2": "sales 2 days ago", "y_lag7": "sales same day last week",
    "y_lag14": "sales 2 weeks ago", "y_roll7": "7-day avg sales", "y_roll14": "14-day avg sales",
    "y_roll28": "28-day avg sales", "y_std14": "14-day sales volatility", "y_don_roll14": "14-day avg on full-stock days",
    "y_don_roll28": "28-day avg on full-stock days", "so_lag1": "stockout hours yesterday", "so_rate7": "7-day stockout rate",
    "so_rate14": "14-day stockout rate", "don_frac7": "share of full-stock days (7d)", "disc_lag1": "discount yesterday",
    "disc_roll7": "7-day avg discount", "act_lag1": "promotion yesterday", "act_roll7": "7-day promotion share",
    "hol_lag1": "holiday yesterday", "precpt_lag1": "rain yesterday", "temp_lag1": "temperature yesterday",
    "y_ewm": "smoothed sales level", "y_dow_mean": "avg for this weekday", "dow": "weekday", "is_weekend": "weekend",
    "n_hist_days": "days of history", "city_id": "city", "store_id": "store", "product_id": "product",
    "management_group_id": "management group", "first_category_id": "category", "second_category_id": "sub-category",
    "third_category_id": "leaf category",
}

st.set_page_config(page_title="Stockout-Aware Order Planner", page_icon="📦", layout="wide")


# ------------------------------------------------------------------------------------------ loading
@st.cache_data(show_spinner="Loading warehouse tables ...")
def load_tables():
    t = {n: pd.read_csv(WH / f"{n}.csv") for n in
         ["dim_date", "dim_series", "dim_model", "dim_policy", "dim_scenario", "fact_sales_daily", "fact_order",
          "fact_forecast", "fact_paper_policy_results"]}
    t["dim_date"]["date"] = pd.to_datetime(t["dim_date"]["date"])
    return t


@st.cache_resource(show_spinner="Loading LightGBM models ...")
def load_models():
    m = {}
    for p in (OUT / "models").glob("*.txt"):
        fam, q = p.stem.rsplit("_", 1)
        m[(fam, q)] = lgb.Booster(model_file=str(p))
    return m


@st.cache_data
def load_app_files():
    feats = pd.read_parquet(APP / "features_final.parquet")
    meta = pd.read_parquet(APP / "meta_final.parquet")
    tables = {tuple(k.split("|")): v for k, v in json.load(open(APP / "residual_tables.json")).items()}
    summary = json.load(open(OUT / "summary.json"))
    return feats, meta, tables, summary


if not (OUT / "summary.json").exists():
    st.error("No model outputs found. Run `python planner/pipeline.py` from the repository root first.")
    st.stop()

T = load_tables()
BOOST = load_models()
FEATS, META, RTAB, SUMMARY = load_app_files()
FEATURES = SUMMARY["features"]
DATE = T["dim_date"].set_index("date_key")
SER = T["dim_series"].set_index("series_key")
MODEL_NAME = {m["model_code"]: m["model_name"] for m in MODEL_DIM}
FINAL_KEYS = DATE.index[DATE.period == "final (held out)"].tolist()
cfg = json.load(open(CONFIG)) if CONFIG.exists() else {}


def style(fig, h=340, ytitle=None):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(color=INK2, size=12), hovermode="x unified",
                      legend=dict(orientation="h", y=1.08, x=0, font=dict(color=INK2)))
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED), title=ytitle)
    return fig


# --------------------------------------------------------------------------------- live model scoring
def live_quantiles(rows: pd.DataFrame, meta: pd.DataFrame, sales_hist: pd.DataFrame) -> dict[str, np.ndarray]:
    """Score rows with every model, exactly as the pipeline does (predict -> pooled residual shift -> sort)."""
    X = rows[FEATURES].to_numpy(np.float32)
    raw = {q: np.clip(BOOST[("demand", q)].predict(X), 0, None) for q in QN}
    rawq = {q: np.clip(BOOST[("raw", q)].predict(X), 0, None) for q in QN}
    point = np.clip(BOOST[("raw_point", "point")].predict(X), 0, None)
    # seasonal naive = recorded sales of the same weekday last week
    hist = sales_hist.set_index(["series_key", "d"]).units_sold
    sn = np.array([hist.get((s, d - 7), np.nan) for s, d in zip(rows.sid, rows.d)])
    sn = np.nan_to_num(sn)
    out = {}
    for code, base in [("demand_conformal", raw), ("raw_point_resid", point), ("seasonal_naive", sn)]:
        cols = []
        for q in QN:
            corr, _ = apply_table(RTAB[(code, q)], meta)
            b0 = base[q] if isinstance(base, dict) else base
            cols.append(np.maximum(0.0, b0 + corr))
        out[code] = np.sort(np.stack(cols, 1), 1)
    out["demand_uncal"] = np.sort(np.stack([raw[q] for q in QN], 1), 1)
    out["raw_quantile"] = np.sort(np.stack([rawq[q] for q in QN], 1), 1)
    return out


def order_at(qarr: np.ndarray, beta: float) -> np.ndarray:
    """Newsvendor order = demand quantile at the critical ratio, interpolated between q25..q90."""
    b = float(np.clip(beta, TAUS[0], TAUS[-1]))
    return np.array([np.interp(b, TAUS, r) for r in np.atleast_2d(qarr)])


@st.cache_data
def sales_with_d():
    s = T["fact_sales_daily"].merge(T["dim_date"][["date_key", "day_index"]], on="date_key")
    s["d"] = s.day_index - 1
    return s


SALES = sales_with_d()

# --------------------------------------------------------------------------------------------- sidebar
st.sidebar.title("📦 Order Planner")
qp = st.query_params
DEMO_SID = 1476  # high-selling series with frequent stockouts
default_sid = int(qp.get("series")) if str(qp.get("series", "")).isdigit() else DEMO_SID
default_sid = default_sid if default_sid in SER.index else DEMO_SID
d0 = SER.loc[default_sid]

cities = sorted(SER.city.unique())
city = st.sidebar.selectbox("City", cities, index=cities.index(d0.city))
stores = sorted(SER[SER.city == city].store.unique())
store = st.sidebar.selectbox("Store", stores, index=stores.index(d0.store) if d0.store in stores else 0)
prods = SER[(SER.store == store)].sort_values("product")
pnames = prods["product"].tolist()
product = st.sidebar.selectbox("Product", pnames, index=pnames.index(d0["product"]) if d0["product"] in pnames else 0)
sid = int(prods[prods["product"] == product].index[0])
fdates = DATE.loc[FINAL_KEYS, "date"].dt.strftime("%a %d %b %Y").tolist()
dsel = st.sidebar.selectbox("Order date (held-out final week)", fdates, index=0)
date_key = FINAL_KEYS[fdates.index(dsel)]

st.sidebar.markdown("**Unit costs** (newsvendor)")
c_u = st.sidebar.slider("Cost of 1 unit short (lost margin)", 0.5, 5.0, 1.0, 0.25)
c_o = st.sidebar.slider("Cost of 1 unit left over (waste)", 0.5, 5.0, 1.0, 0.25)
beta = c_u / (c_u + c_o)
st.sidebar.metric("Critical ratio β = c_u / (c_u + c_o)", f"{beta:.2f}")
if beta < TAUS[0] or beta > TAUS[-1]:
    st.sidebar.warning(f"β is outside the modelled quantiles ({TAUS[0]}-{TAUS[-1]}); orders use the nearest quantile.")
st.sidebar.caption("Data: FreshRetailNet-50K (CC BY 4.0), 5,000 store-product series, 2024-03-28 to 2024-07-02.")

tabs = st.tabs(["Order planner (live model)", "Network KPIs", "Research results (9 policies)",
                "Power BI report", "Batch scoring", "About the data"])

# ================================================================================ 1. ORDER PLANNER
with tabs[0]:
    s = SER.loc[sid]
    st.subheader(f"{s.store_product} · {s.category_l1} · {s.city}")
    st.caption(f"Sales tier: **{s.sales_tier}** · stockout tier: **{s.stockout_tier}** · "
               f"every number on this tab is computed live from the saved LightGBM models.")
    d_idx = int(DATE.loc[date_key, "day_index"]) - 1
    row = FEATS[(FEATS.sid == sid) & (FEATS.d == d_idx)]
    meta = META[(FEATS.sid == sid).to_numpy() & (FEATS.d == d_idx).to_numpy()]
    Q = live_quantiles(row, meta.reset_index(drop=True), SALES[SALES.series_key == sid])
    orders = {k: float(order_at(v, beta)[0]) for k, v in Q.items()}
    act = SALES[(SALES.series_key == sid) & (SALES.date_key == date_key)].iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Recommended order", f"{orders[HEADLINE]:.2f} units", help=MODEL_NAME[HEADLINE])
    k2.metric("Median demand forecast (q50)", f"{Q[HEADLINE][0, 1]:.2f}")
    k3.metric("80% band (q25 - q90)", f"{Q[HEADLINE][0, 0]:.2f} - {Q[HEADLINE][0, 3]:.2f}")
    if act.donor_flag == 1:
        d = act.units_sold
        cost = c_u * max(d - orders[HEADLINE], 0) + c_o * max(orders[HEADLINE] - d, 0)
        k4.metric("Actual demand (full-stock day)", f"{d:.2f}", delta=f"cost {cost:.2f}", delta_color="off")
    else:
        k4.metric("Actual demand", "unknown (censored)",
                  delta=f"sold {act.units_sold:.2f}, out of stock {int(act.stockout_hours)} h", delta_color="off")

    # history + forecast band
    hs = SALES[SALES.series_key == sid].merge(T["dim_date"][["date_key", "date"]], on="date_key")
    fc = T["fact_forecast"]
    fc = fc[(fc.series_key == sid) & (fc.model_key == 1)].merge(T["dim_date"][["date_key", "date"]], on="date_key")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fc.date, y=fc.q90, line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=fc.date, y=fc.q25, fill="tonexty", fillcolor="rgba(42,120,214,0.15)",
                             line=dict(width=0), name="forecast band q25-q90"))
    fig.add_trace(go.Scatter(x=fc.date, y=fc.q50, line=dict(color=BLUE, width=2, dash="dot"), name="forecast q50"))
    fig.add_trace(go.Scatter(x=hs.date, y=hs.units_sold, line=dict(color=INK2, width=2), name="units sold (06-22h)"))
    so = hs[hs.stockout_flag == 1]
    fig.add_trace(go.Scatter(x=so.date, y=so.units_sold, mode="markers",
                             marker=dict(color=ORANGE, size=8, symbol="x", line=dict(width=1, color="white")),
                             name="sold out that day (sales < demand)",
                             customdata=so.stockout_hours, hovertemplate="%{y:.2f} sold, %{customdata} h out of stock"))
    sel_date = DATE.loc[date_key, "date"]
    fig.add_vline(x=sel_date, line=dict(color=MUTED, width=1, dash="dash"))
    fig.add_vrect(x0=DATE.loc[FINAL_KEYS[0], "date"] - pd.Timedelta(hours=12),
                  x1=DATE.loc[FINAL_KEYS[-1], "date"] + pd.Timedelta(hours=12), fillcolor="#f3f2ee", line_width=0, layer="below",
                  annotation_text="held-out week", annotation_position="top left", annotation_font_color=MUTED)
    st.plotly_chart(style(fig, 360, "units"), width="stretch")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Order by policy at this cost ratio**")
        names = [MODEL_NAME[k] for k in orders]
        vals = list(orders.values())
        colors = [BLUE if k == HEADLINE else "#c9c8c2" for k in orders]
        f2 = go.Figure(go.Bar(y=names, x=vals, orientation="h", marker=dict(color=colors, cornerradius=4),
                              text=[f"{v:.2f}" for v in vals], textposition="outside", textfont=dict(color=INK2),
                              hovertemplate="%{y}: %{x:.3f} units<extra></extra>"))
        if act.donor_flag == 1:
            f2.add_vline(x=act.units_sold, line=dict(color=ORANGE, width=2),
                         annotation_text="actual demand", annotation_font_color=INK2)
        f2.update_yaxes(autorange="reversed")
        st.plotly_chart(style(f2, 300).update_layout(hovermode="closest"), width="stretch")
        if act.donor_flag == 1:
            d = act.units_sold
            tbl = pd.DataFrame({"policy": names, "order": vals,
                                "short": [max(d - v, 0) for v in vals], "left over": [max(v - d, 0) for v in vals]})
            tbl["cost"] = c_u * tbl["short"] + c_o * tbl["left over"]
            st.dataframe(tbl.round(3), hide_index=True, width="stretch")
    with c2:
        st.markdown("**Why this forecast? (q50 feature contributions, SHAP)**")
        X = row[FEATURES].to_numpy(np.float32)
        contrib = BOOST[("demand", "q50")].predict(X, pred_contrib=True)[0]
        cdf = pd.DataFrame({"feature": FEATURES, "value": row[FEATURES].iloc[0].values, "contrib": contrib[:-1]})
        cdf = cdf.reindex(cdf.contrib.abs().sort_values(ascending=False).index).head(8)
        cdf["label"] = [f"{FRIENDLY.get(f, f)} = {v:.2f}" if np.isfinite(v) else f"{FRIENDLY.get(f, f)} = n/a"
                        for f, v in zip(cdf.feature, cdf.value)]
        f3 = go.Figure(go.Bar(y=cdf.label, x=cdf.contrib, orientation="h",
                              marker=dict(color=[BLUE if c > 0 else ORANGE for c in cdf.contrib], cornerradius=4),
                              hovertemplate="%{y}<br>effect %{x:+.3f} units<extra></extra>"))
        f3.update_yaxes(autorange="reversed")
        st.plotly_chart(style(f3, 300).update_layout(hovermode="closest"), width="stretch")
        st.caption(f"Baseline (average prediction) {contrib[-1]:.2f} + contributions = raw q50 "
                   f"{contrib.sum():.2f}, before the conformal shift. Blue raises the forecast, orange lowers it.")

# ================================================================================ 2. NETWORK KPIs
with tabs[1]:
    st.subheader("Final-week network KPIs (held-out 2024-06-26 to 2024-07-02)")
    f1, f2c, f3c = st.columns(3)
    sel_city = f1.multiselect("City", cities, placeholder="All cities")
    sel_cat = f2c.multiselect("Category", sorted(SER.category_l1.unique()), placeholder="All categories")
    scen_names = [s["scenario_name"] for s in SCENARIOS]
    scen = f3c.selectbox("Orders placed for scenario", scen_names, index=1)
    sk = scen_names.index(scen) + 1
    mask = pd.Series(True, index=SER.index)
    if sel_city:
        mask &= SER.city.isin(sel_city)
    if sel_cat:
        mask &= SER.category_l1.isin(sel_cat)
    keep = SER.index[mask]
    if len(keep) == 0:
        st.warning("No store-products match these filters.")
        st.stop()
    fo = T["fact_order"]
    fo = fo[(fo.scenario_key == sk) & fo.series_key.isin(keep) & fo.demand.notna()].copy()
    fo["cost_whatif"] = c_u * fo.shortage_units + c_o * fo.leftover_units
    agg = fo.groupby("policy_key").agg(rows=("cost", "size"), mean_cost=("cost", "mean"), whatif=("cost_whatif", "mean"),
                                       demand=("demand", "sum"), sold=("sold_units", "sum"), left=("leftover_units", "sum"),
                                       ordered=("order_qty", "sum")).reset_index()
    agg = agg.merge(T["dim_policy"][["policy_key", "policy_code", "policy_name"]])
    agg["fill_rate"] = agg.sold / agg.demand
    agg["leftover_share"] = agg.left / agg.ordered
    sn_cost = agg.loc[agg.policy_code == "seasonal_naive", "mean_cost"].iloc[0]
    agg["saving"] = 1 - agg.mean_cost / sn_cost
    h = agg[agg.policy_code == HEADLINE].iloc[0]
    fs = SALES[SALES.series_key.isin(keep) & SALES.date_key.isin(FINAL_KEYS)]
    ff = T["fact_forecast"]
    ff = ff[(ff.model_key == 1) & (ff.is_scored == 1) & ff.series_key.isin(keep) & ff.date_key.isin(FINAL_KEYS)]
    acc = 1 - (ff.q50 - ff.actual_demand).abs().sum() / ff.actual_demand.sum()
    a, b, c, d = st.columns(4)
    a.metric("Fill rate (headline policy)", f"{h.fill_rate:.1%}", help="units sold / demand, full-stock days")
    b.metric("Observed stockout rate", f"{fs.stockout_flag.mean():.1%}", help="share of store-product-days with ≥1 stockout hour (real data)")
    c.metric("Forecast accuracy (1 - WAPE, q50)", f"{acc:.1%}")
    d.metric("Cost saving vs seasonal naive", f"{h.saving:.1%}")
    st.caption(f"Scored on {int(h.rows):,} store-product-days with full stock (exact demand). Headline policy: {MODEL_NAME[HEADLINE]}.")

    l, r = st.columns([1.1, 1])
    with l:
        st.markdown("**Cost vs fill rate by policy** (lower-right is better)")
        fig = go.Figure()
        for _, p in agg.iterrows():
            hl = p.policy_code == HEADLINE
            fig.add_trace(go.Scatter(x=[p.fill_rate], y=[p.mean_cost], mode="markers+text", text=[p.policy_name],
                                     textposition="top center", textfont=dict(color=INK if hl else INK2, size=11),
                                     marker=dict(size=14 if hl else 10, color=BLUE if hl else "#b5b4ad",
                                                 line=dict(width=2, color="white")), showlegend=False,
                                     hovertemplate=f"{p.policy_name}<br>fill rate %{{x:.1%}}<br>mean cost %{{y:.3f}}<extra></extra>"))
        fig.update_xaxes(tickformat=".0%", title="fill rate")
        st.plotly_chart(style(fig, 380, "mean cost per store-product-day").update_layout(hovermode="closest"), width="stretch")
    with r:
        st.markdown(f"**What-if: re-score these orders at your sidebar costs** (c_u={c_u}, c_o={c_o})")
        w = agg.sort_values("whatif")
        f2 = go.Figure(go.Bar(y=w.policy_name, x=w.whatif, orientation="h",
                              marker=dict(color=[BLUE if c == HEADLINE else "#c9c8c2" for c in w.policy_code], cornerradius=4),
                              text=[f"{v:.3f}" for v in w.whatif], textposition="outside", textfont=dict(color=INK2),
                              hovertemplate="%{y}: %{x:.3f}<extra></extra>"))
        f2.update_yaxes(autorange="reversed")
        st.plotly_chart(style(f2, 380, None).update_layout(hovermode="closest"), width="stretch")
        st.caption("Orders stay as placed for the chosen scenario; only the cost weights change.")

    st.markdown("**Daily fill rate: headline policy vs seasonal-naive baseline**")
    dd = fo[fo.policy_key.isin([1, 5])].groupby(["date_key", "policy_key"])[["sold_units", "demand"]].sum().reset_index()
    dd["fill"] = dd.sold_units / dd.demand
    dd = dd.merge(T["dim_date"][["date_key", "date"]])
    fig = go.Figure()
    for pk, col, nm in [(1, BLUE, MODEL_NAME[HEADLINE]), (5, ORANGE, MODEL_NAME["seasonal_naive"])]:
        x = dd[dd.policy_key == pk]
        fig.add_trace(go.Scatter(x=x.date, y=x.fill, name=nm, line=dict(color=col, width=2), mode="lines+markers",
                                 marker=dict(size=8, line=dict(width=2, color="white"))))
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(style(fig, 300, "fill rate"), width="stretch")

    st.markdown("**Top 10 problem store-products** (highest total cost, headline policy)")
    top = fo[fo.policy_key == 1].groupby("series_key").agg(cost=("cost", "sum"), short=("shortage_units", "sum"),
                                                           left=("leftover_units", "sum"), days=("cost", "size"))
    top = top.join(SER[["store_product", "city", "category_l1", "planner_url"]]).sort_values("cost", ascending=False).head(10)
    so_h = fs.groupby("series_key").stockout_hours.sum()
    top["stockout_h_week"] = so_h.reindex(top.index).values
    st.dataframe(top[["store_product", "city", "category_l1", "cost", "short", "left", "days", "stockout_h_week", "planner_url"]].round(3),
                 hide_index=True, width="stretch",
                 column_config={"planner_url": st.column_config.LinkColumn("open in planner", display_text="open")})

# ================================================================================ 3. RESEARCH RESULTS
with tabs[2]:
    st.subheader("Paper results: 9 ordering policies under simulated stockouts (run E)")
    st.caption("From results/phase0_9_5k/phase5_9/phase9_evaluation/final_order_metrics.csv. Models were trained on histories "
               "censored by simulated stockout mechanisms A/B/C and scored on exact final-week donor rows. "
               "Matched cells = trained and tested on the same mechanism.")
    P = T["fact_paper_policy_results"]
    c1, c2 = st.columns(2)
    sc = c1.selectbox("Cost scenario", P.scenario.unique().tolist(), index=1, key="pscen")
    cells = c2.radio("Cells", ["matched (train = test)", "all 9 train/test cells"], horizontal=True)
    p = P[P.scenario == sc]
    if cells.startswith("matched"):
        p = p[p.matched_cell == 1]
    g = p.groupby(["policy", "population"]).agg(mean_cost=("mean_cost", "mean"), fill=("fill_rate", "mean"),
                                                short=("total_shortage", "sum"), left=("total_leftover", "sum"),
                                                n=("n", "sum")).reset_index()
    g["whatif"] = (c_u * g.short + c_o * g.left) / g.n
    snc = g.loc[g.policy.str.startswith("seasonal"), "mean_cost"].iloc[0]
    g["saving_vs_sn"] = np.where(g.population == "full sample", 1 - g.mean_cost / snc, np.nan)
    g = g.sort_values("mean_cost")
    best = g[g.population == "full sample"].iloc[0].policy
    fig = go.Figure(go.Bar(y=g.policy + np.where(g.population == "deep subsample", "  (600-series subset)", ""), x=g.mean_cost,
                           orientation="h", marker=dict(color=[BLUE if x == best else "#c9c8c2" for x in g.policy], cornerradius=4),
                           text=[f"{v:.3f}" for v in g.mean_cost], textposition="outside", textfont=dict(color=INK2),
                           hovertemplate="%{y}<br>mean cost %{x:.3f}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(style(fig, 380, None).update_layout(hovermode="closest", xaxis_title="mean newsvendor cost (lower is better)"),
                    width="stretch")
    st.dataframe(g[["policy", "population", "mean_cost", "fill", "saving_vs_sn", "whatif"]]
                 .rename(columns={"fill": "fill rate", "saving_vs_sn": "saving vs seasonal naive",
                                  "whatif": f"cost at your c_u={c_u}, c_o={c_o}"}).round(4),
                 hide_index=True, width="stretch")
    st.caption("TFT policies were scored on a 600-series subset, so their costs are not directly comparable and get no saving figure.")

# ================================================================================ 4. POWER BI
with tabs[3]:
    st.subheader("Power BI report")
    url = cfg.get("powerbi_embed_url", "")
    if url:
        components.iframe(url, height=720)
    shots = sorted(SHOTS.glob("*.png")) if SHOTS.exists() else []
    if shots:
        for p in shots:
            st.image(str(p), caption=p.stem.replace("_", " "), width="stretch")
    if not url and not shots:
        st.info("Open `planner/powerbi/StockoutPlanner.pbip` in Power BI Desktop. Export each page "
                "(File → Export → PDF, or a screenshot) into `planner/powerbi/screenshots/` to show it here. "
                "If you can use *Publish to web*, put the embed URL in `planner/config.json` as "
                '`{"powerbi_embed_url": "https://app.powerbi.com/view?r=..."}`.')
    st.markdown("""
**How the two front ends fit together**
- **Power BI** = the planning manager's report: KPIs, drill-through, row-level security by city, built on the star schema in `planner/output/warehouse/`.
- **This app** = the planner's tool: it runs the trained model live for one store-product-day. The Power BI drill-through page links here through `dim_series[planner_url]`.
""")

# ================================================================================ 5. BATCH
with tabs[4]:
    st.subheader("Batch scoring")
    st.write("Upload a CSV with columns `store_id, product_id, date` (dates in the held-out week). "
             "You get the recommended order for every row at the sidebar costs.")
    tmpl = SER.reset_index()[["store_id", "product_id"]].head(5).assign(date=str(DATE.loc[FINAL_KEYS[0], "date"].date()))
    st.download_button("Download a template", tmpl.to_csv(index=False), "order_request_template.csv", "text/csv")
    up = st.file_uploader("Order request CSV", type="csv")
    if up is not None:
        req = pd.read_csv(up)
        need = {"store_id", "product_id", "date"}
        if not need.issubset(req.columns):
            st.error(f"Missing columns: {sorted(need - set(req.columns))}")
        else:
            req["date"] = pd.to_datetime(req.date)
            m = req.merge(SER.reset_index()[["series_key", "store_id", "product_id"]], on=["store_id", "product_id"], how="left")
            m = m.merge(T["dim_date"][["date", "day_index", "period"]], on="date", how="left")
            ok = m.series_key.notna() & (m.period == "final (held out)")
            res = m[ok].copy()
            if len(res):
                res["sid"], res["d"] = res.series_key.astype(int), res.day_index.astype(int) - 1
                rows = res[["sid", "d"]].merge(FEATS, on=["sid", "d"], how="left")
                key = FEATS[["sid", "d"]].reset_index()
                mi = rows[["sid", "d"]].merge(key, on=["sid", "d"])["index"].to_numpy()
                q = live_quantiles(rows, META.iloc[mi].reset_index(drop=True), SALES[SALES.series_key.isin(res.sid)])
                res["q25"], res["q50"], res["q75"], res["q90"] = q[HEADLINE].T
                res["recommended_order"] = order_at(q[HEADLINE], beta)
                res["beta"] = round(beta, 4)
            st.write(f"{ok.sum():,} rows scored, {(~ok).sum():,} skipped (unknown series or date outside the held-out week).")
            out = res.drop(columns=["sid", "d", "day_index", "period"], errors="ignore")
            st.dataframe(out.round(3), hide_index=True, width="stretch")
            st.download_button("Download orders", out.to_csv(index=False), "recommended_orders.csv", "text/csv")

# ================================================================================ 6. ABOUT
with tabs[5]:
    st.subheader("About the data and the model")
    st.markdown(f"""
- **Data:** FreshRetailNet-50K v1.0 (Dingdong-Inc, CC BY 4.0), the 5,000 series from the repo's stratified sample,
  97 days (2024-03-28 to 2024-07-02). IDs are anonymised, so stores, products and categories are shown as codes.
- **Demand:** sales between 06:00 and 21:59. On a day with any stockout hour, sales understate demand, so those days
  have **no demand value**. Only full-stock ("donor") days have exact demand; they are {SUMMARY['donor_share_all_days']:.1%} of all days.
- **Split:** fit days 1-60, early stopping days 61-75, conformal calibration days 76-90, held-out evaluation days 91-97
  ({SUMMARY['final_week_donor_rows']:,} scored full-stock rows, the same count as the paper).
- **Model:** LightGBM quantile regressions (q25/q50/q75/q90) on donor days with {len(FEATURES)} features, all from day t-1 or
  earlier, shifted by pooled conformal residuals (category × sales tier, falling back to coarser pools below {200} rows).
- **Ordering:** newsvendor, order = demand quantile at β = c_u / (c_u + c_o). Fresh goods with no carry-over, so
  "leftover" is the end-of-day excess, not inventory carried into the next day.
- **Two result sets:** this demo retrains on the **real recorded** history (tabs 1-2). The paper's 9-policy comparison (tab 3)
  trains on **simulated** censored histories. On the real history, the raw-sales models are competitive with the
  demand-quantile models when scored on full-stock days. The paper's advantage of stockout-aware training appears when
  censoring is heavy and known (the simulation).
- **Limitations:** costs are in relative units (no prices in the data); scored rows are full-stock days only, which are a
  selected sample; no forecast beyond 2024-07-02 is possible because the features need the previous day's sales.
""")
