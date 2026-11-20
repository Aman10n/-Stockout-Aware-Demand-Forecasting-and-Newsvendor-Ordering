"""Export everything the web simulator needs from the trained pipeline (planner/output) and the raw data.

Run after `python planner/pipeline.py`:      python simulator/export/export_assets.py
Writes simulator/data/ (git-ignored).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "planner"))
import pipeline as P  # noqa: E402  (reuse the exact loaders and feature code)

PL = ROOT / "planner" / "output"
OUT = ROOT / "simulator" / "data"
SIM_PARAMS = ROOT / "results" / "phase0_9_5k" / "phase0_4" / "sim" / "simulator_params.json"
DTYPES = {"<=": 0, "==": 1}
MISSING = {"None": 0, "Zero": 1, "NaN": 2}


def compact_tree(node: dict) -> dict:
    """Flatten a dump_model tree into parallel arrays. Leaves are encoded as ~leaf_index (negative)."""
    sf, th, dt, dl, mt, lc, rc, cats, leaves = [], [], [], [], [], [], [], [], []

    def visit(n):
        if "leaf_value" in n:
            leaves.append(float(n["leaf_value"]))
            return ~(len(leaves) - 1)
        i = len(sf)
        sf.append(n["split_feature"]); dt.append(DTYPES[n["decision_type"]]); dl.append(int(n["default_left"]))
        mt.append(MISSING[n["missing_type"]]); lc.append(0); rc.append(0)
        if n["decision_type"] == "==":
            th.append(len(cats)); cats.append([int(c) for c in str(n["threshold"]).split("||")])
        else:
            th.append(float(n["threshold"]))
        lc[i] = visit(n["left_child"])
        rc[i] = visit(n["right_child"])
        return i

    root = visit(node)
    return {"root": root, "f": sf, "t": th, "d": dt, "l": dl, "m": mt, "lc": lc, "rc": rc, "c": cats, "v": leaves}


def export_models() -> list[str]:
    (OUT / "models").mkdir(parents=True, exist_ok=True)
    names = []
    for p in sorted((PL / "models").glob("*.txt")):
        b = lgb.Booster(model_file=str(p))
        d = b.dump_model()
        trees = [compact_tree(t["tree_structure"]) for t in d["tree_info"]]
        json.dump({"name": p.stem, "features": d["feature_names"], "objective": d["objective"], "trees": trees},
                  open(OUT / "models" / f"{p.stem}.json", "w"), separators=(",", ":"))
        names.append(p.stem)
        print(f"  model {p.stem}: {len(trees)} trees")
    return names


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = json.load(open(PL / "summary.json"))
    features = summary["features"]
    series = pd.read_parquet(P.SERIES_FILE).sort_values("key").reset_index(drop=True)
    series["sid"] = np.arange(len(series))
    print("loading panel ...")
    panel = P.load_panel(series)
    n = len(series)

    # ---- hourly panel: recorded sales and stockout status, all 24 hours (binary, row-major sid, day, hour)
    import pyarrow.parquet as pq
    H = np.zeros((n, P.N_DAYS, 24), np.float32)
    S = np.zeros((n, P.N_DAYS, 24), np.uint8)
    keys = series.key.to_numpy()
    for f in ["train.parquet", "eval.parquet"]:
        for b in pq.ParquetFile(P.DATA / f).iter_batches(batch_size=250_000, columns=P.KEY_COLS + ["dt", "hours_sale", "hours_stock_status"]):
            k = P.pack_key(*(b.column(c).to_numpy() for c in P.KEY_COLS))
            pos = np.minimum(np.searchsorted(keys, k), n - 1)
            m = keys[pos] == k
            if not m.any():
                continue
            import pyarrow as pa
            b = b.filter(pa.array(m)); pos = pos[m]
            d = (np.array(b.column("dt").to_pylist(), dtype="datetime64[D]") - P.START).astype(np.int64)
            H[pos, d] = b.column("hours_sale").values.to_numpy(zero_copy_only=False).reshape(-1, 24)
            S[pos, d] = b.column("hours_stock_status").values.to_numpy(zero_copy_only=False).reshape(-1, 24)
    assert np.allclose(H[:, :, P.H16].astype(np.float64).sum(-1), panel["Y"]), "hourly panel mismatch"
    H.tofile(OUT / "hours_sale.f32")
    S.tofile(OUT / "hours_stock.u8")
    ctx = np.stack([panel["CTX"][c] for c in P.CTX_COLS], -1).astype(np.float32)  # n, days, 5
    ctx.tofile(OUT / "ctx.f32")

    # ---- series metadata
    meta = series[["sid", "city_id", "store_id", "product_id"] + P.STATIC_COLS + ["sales_tier", "stockout_tier"]].copy()
    meta.to_json(OUT / "series.json", orient="records")

    # ---- models, residual tables, simulator parameters
    print("exporting models ...")
    names = export_models()
    tables = json.load(open(PL / "app" / "residual_tables.json"))
    json.dump(tables, open(OUT / "residual_tables.json", "w"), separators=(",", ":"))
    json.dump(json.load(open(SIM_PARAMS))["params"], open(OUT / "sim_params.json", "w"))

    # ---- config shared with the server
    dates = [str(d) for d in P.DATES]
    cfg = {"features": features, "cat_features": P.CAT_FEATS, "ctx_cols": P.CTX_COLS, "dates": dates, "n_series": n,
           "n_days": P.N_DAYS, "taus": P.TAUS, "quantiles": P.QN, "min_pool": P.MIN_POOL, "scenarios": P.SCENARIOS,
           "models": P.MODEL_DIM, "model_files": names, "split": {"fit": [0, 59], "tune": [60, 74], "cal": [75, 89], "final": [90, 96]},
           "summary": {k: summary[k] for k in ["donor_share_all_days", "final_week_donor_rows", "order_summary", "forecast_accuracy"]}}
    json.dump(cfg, open(OUT / "config.json", "w"), indent=1, default=float)

    # ---- network aggregates per city x policy x scenario (final week, scored rows) + stockout by city/day
    wh = PL / "warehouse"
    ds = pd.read_csv(wh / "dim_series.csv")
    fo = pd.read_csv(wh / "fact_order.csv")
    fo = fo[fo.demand.notna()].merge(ds[["series_key", "city"]], on="series_key")
    agg = fo.groupby(["city", "policy_key", "scenario_key"]).agg(
        n=("cost", "size"), demand=("demand", "sum"), sold=("sold_units", "sum"), short=("shortage_units", "sum"),
        left=("leftover_units", "sum"), ordered=("order_qty", "sum"), cost=("cost", "sum")).reset_index()
    fs = pd.read_csv(wh / "fact_sales_daily.csv").merge(ds[["series_key", "city"]], on="series_key")
    dd = pd.read_csv(wh / "dim_date.csv")
    fs = fs.merge(dd[["date_key", "weekday_num", "period"]], on="date_key")
    city = fs.groupby("city").agg(stockout_rate=("stockout_flag", "mean"), stockout_hours=("stockout_hours", "sum"),
                                  donor_share=("donor_flag", "mean"), series=("series_key", "nunique")).reset_index()
    dow = fs.groupby(["city", "weekday_num"]).stockout_flag.mean().reset_index()
    daily = fs.groupby("date_key").agg(stockout_rate=("stockout_flag", "mean")).reset_index()
    ff = pd.read_csv(wh / "fact_forecast.csv")
    ff = ff[(ff.is_scored == 1) & (ff.date_key >= 20240626)].merge(ds[["series_key", "city"]], on="series_key")
    acc = ff.groupby(["city", "model_key"]).apply(lambda g: pd.Series({
        "abs_err": (g.q50 - g.actual_demand).abs().sum(), "actual": g.actual_demand.sum(), "q50": g.q50.sum(),
        "cov90": (g.actual_demand <= g.q90).sum(), "n": len(g)}), include_groups=False).reset_index()
    paper = pd.read_csv(wh / "fact_paper_policy_results.csv")
    json.dump({"orders": agg.to_dict("records"), "cities": city.to_dict("records"), "city_dow": dow.to_dict("records"),
               "daily": daily.to_dict("records"), "accuracy": acc.to_dict("records"), "paper": paper.to_dict("records")},
              open(OUT / "network.json", "w"), separators=(",", ":"), default=float)

    # ---- stores (for the game): products per store and final-week scored days
    final_donor = panel["DON"][:, 90:97].sum(1)
    st = series.assign(final_donor=final_donor).groupby(["city_id", "store_id"]).agg(
        products=("sid", "size"), scored_days=("final_donor", "sum"), sales=("fit_mean_y16", "sum")).reset_index()
    st.to_json(OUT / "stores.json", orient="records")

    # ---- SHAP for the q50 demand model on final-week rows (base explanations for the X-ray)
    F = pd.read_parquet(PL / "app" / "features_final.parquet")
    b50 = lgb.Booster(model_file=str(PL / "models" / "demand_q50.txt"))
    contrib = b50.predict(F[features].to_numpy(np.float32), pred_contrib=True).astype(np.float32)
    idx = (F.sid.to_numpy() * 7 + (F.d.to_numpy() - 90)).astype(np.int64)
    out = np.zeros((n * 7, contrib.shape[1]), np.float32)
    out[idx] = contrib
    out.tofile(OUT / "shap_q50_final.f32")

    # ---- verification fixtures: features from the Python builder + raw booster outputs + final quantiles
    Ffull = P.build_features(panel, series)
    rng = np.random.default_rng(7)
    pick = np.concatenate([rng.choice(np.nonzero(Ffull.d >= 90)[0], 2000, replace=False),
                           rng.choice(np.nonzero((Ffull.d >= 14) & (Ffull.d < 90))[0], 1000, replace=False)])
    fx = Ffull.iloc[pick].reset_index(drop=True)
    X = fx[features].to_numpy(np.float32)
    raw = {}
    for nm in names:
        bb = lgb.Booster(model_file=str(PL / "models" / f"{nm}.txt"))
        raw[nm] = bb.predict(X).tolist()
    fc = pd.read_csv(wh / "fact_forecast.csv")
    fc["d"] = fc.date_key.map(dict(zip(dd.date_key, dd.day_index - 1)))
    fcw = fc.pivot_table(index=["series_key", "d"], columns="model_key", values=["q25", "q50", "q75", "q90"])
    finals = []
    for s_, d_ in zip(fx.sid, fx.d):
        if (s_, d_) in fcw.index:
            r = fcw.loc[(s_, d_)]
            finals.append({str(mk): [float(r[(q, mk)]) for q in P.QN] for mk in range(1, 6)})
        else:
            finals.append(None)
    json.dump({"rows": [{"sid": int(s_), "d": int(d_), "x": [None if not np.isfinite(v) else float(v) for v in row]}
                        for s_, d_, row in zip(fx.sid, fx.d, X)],
               "raw": raw, "final": finals}, open(OUT / "fixtures.json", "w"), separators=(",", ":"))
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
