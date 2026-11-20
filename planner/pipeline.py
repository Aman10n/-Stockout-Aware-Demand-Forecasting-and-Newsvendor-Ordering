"""Build the demo model, the order simulation and the Power BI star schema.

Reads data/train.parquet + data/eval.parquet (FreshRetailNet-50K v1.0) for the 5,000 series selected in
run S (results/phase0_4/demo5000/manifests/selected_series.parquet) and writes everything to planner/output/.

It follows the paper's protocol on the *real recorded* history (no simulated censoring):
  days  1-60  model fit          (LightGBM weights)
  days 61-75  tuning             (early stopping)
  days 76-90  calibration        (pooled conformal residuals, seasonal-naive/point residual quantiles)
  days 91-97  final evaluation   (2024-06-26 .. 2024-07-02, held out; scored on donor rows only)

Demand = sales between 06:00 and 21:59. A "donor" day has zero stockout hours in that window, so its sales
are exact demand. Censored days never get a demand value. Every feature for day t uses days < t only.

Run:  python planner/pipeline.py            (about 3-6 minutes on a laptop)
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SERIES_FILE = ROOT / "results" / "phase0_4" / "demo5000" / "manifests" / "selected_series.parquet"
PAPER_ORDERS = ROOT / "results" / "phase0_9_5k" / "phase5_9" / "phase9_evaluation" / "final_order_metrics.csv"
OUT = Path(__file__).resolve().parent / "output"
WH = OUT / "warehouse"          # star schema CSVs for Power BI / PostgreSQL
APP = OUT / "app"               # files the Streamlit app reads
MODELS = OUT / "models"

SEED = 20240628
START = np.datetime64("2024-03-28")
N_DAYS = 97
DATES = START + np.arange(N_DAYS)
FIT_D, TUNE_D, CAL_D, FINAL_D = np.arange(0, 60), np.arange(60, 75), np.arange(75, 90), np.arange(90, 97)
PERIOD = np.array(["model fit"] * 60 + ["tuning"] * 15 + ["calibration"] * 15 + ["final (held out)"] * 7)
H16 = slice(6, 22)
KEY_COLS = ["city_id", "store_id", "product_id"]
STATIC_COLS = ["management_group_id", "first_category_id", "second_category_id", "third_category_id"]
CTX_COLS = ["discount", "holiday_flag", "activity_flag", "precpt", "avg_temperature"]
TAUS = [0.25, 0.50, 0.75, 0.90]
QN = ["q25", "q50", "q75", "q90"]
MIN_POOL = 200
SCENARIOS = [  # same three cost scenarios as the paper; beta = c_u / (c_u + c_o)
    dict(scenario_key=1, scenario_name="Excess stock more costly", c_u=1, c_o=3, beta=0.25, quantile="q25"),
    dict(scenario_key=2, scenario_name="Equal costs", c_u=1, c_o=1, beta=0.50, quantile="q50"),
    dict(scenario_key=3, scenario_name="Shortage more costly", c_u=3, c_o=1, beta=0.75, quantile="q75"),
]
MODEL_DIM = [  # forecast models (each gives q25..q90)
    dict(model_key=1, model_code="demand_conformal", model_name="Demand-quantile LightGBM + pooled conformal",
         stockout_aware=True, description="Quantile LightGBM trained on donor (uncensored) days, then shifted by pooled conformal residuals."),
    dict(model_key=2, model_code="demand_uncal", model_name="Demand-quantile LightGBM (uncalibrated)",
         stockout_aware=True, description="Quantile LightGBM trained on donor (uncensored) days only."),
    dict(model_key=3, model_code="raw_quantile", model_name="Raw-sales quantile LightGBM",
         stockout_aware=False, description="Quantile LightGBM trained on all recorded sales, including sold-out days."),
    dict(model_key=4, model_code="raw_point_resid", model_name="Raw-sales LightGBM + residual quantile",
         stockout_aware=False, description="L2 LightGBM on recorded sales plus pooled residual quantiles from calibration donor days."),
    dict(model_key=5, model_code="seasonal_naive", model_name="Seasonal naive (t-7) + residual quantile",
         stockout_aware=False, description="Sales of the same weekday last week plus pooled residual quantiles (baseline)."),
]
BASE_LGB = dict(learning_rate=0.05, num_leaves=31, min_data_in_leaf=200, feature_fraction=0.9, bagging_fraction=0.8,
                bagging_freq=1, lambda_l2=1.0, max_bin=255, cat_smooth=10, max_cat_to_onehot=4, seed=SEED,
                deterministic=True, force_col_wise=True, verbose=-1)
CAT_FEATS = KEY_COLS + STATIC_COLS


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ----------------------------------------------------------------------------------------------- data
def pack_key(city, store, product):
    return city.astype(np.int64) * 1_000_000 + store.astype(np.int64) * 1_000 + product.astype(np.int64)


def load_panel(series: pd.DataFrame) -> dict:
    keys = series.key.to_numpy()
    n = len(keys)
    H = np.zeros((n, N_DAYS, 24), np.float32)
    S = np.zeros((n, N_DAYS, 24), np.int8)
    SA = np.full((n, N_DAYS), np.nan)
    CTX = {c: np.full((n, N_DAYS), np.nan, np.float32) for c in CTX_COLS}
    seen = np.zeros((n, N_DAYS), np.int16)
    cols = KEY_COLS + ["dt", "sale_amount", "hours_sale", "hours_stock_status"] + CTX_COLS
    for f in ["train.parquet", "eval.parquet"]:
        for b in pq.ParquetFile(DATA / f).iter_batches(batch_size=250_000, columns=cols):
            k = pack_key(*(b.column(c).to_numpy() for c in KEY_COLS))
            pos = np.minimum(np.searchsorted(keys, k), n - 1)
            m = keys[pos] == k
            if not m.any():
                continue
            b = b.filter(pa.array(m))
            pos = pos[m]
            d = (np.array(b.column("dt").to_pylist(), dtype="datetime64[D]") - START).astype(np.int64)
            hs = b.column("hours_sale")
            st = b.column("hours_stock_status")
            assert (pc.list_value_length(hs).to_numpy() == 24).all() and (pc.list_value_length(st).to_numpy() == 24).all()
            H[pos, d] = hs.values.to_numpy(zero_copy_only=False).reshape(-1, 24)
            S[pos, d] = st.values.to_numpy(zero_copy_only=False).reshape(-1, 24)
            SA[pos, d] = b.column("sale_amount").to_numpy()
            for c in CTX_COLS:
                CTX[c][pos, d] = b.column(c).to_numpy().astype(np.float32)
            np.add.at(seen, (pos, d), 1)
    assert seen.max() == 1, "duplicate series-days"
    assert seen.min() == 1, f"missing series-days: {(seen == 0).sum()}"
    Y = H[:, :, H16].astype(np.float64).sum(-1)
    SO = S[:, :, H16].sum(-1).astype(np.int16)
    return dict(Y=Y, SO=SO, DON=SO == 0, SA=SA, CTX=CTX)


# ------------------------------------------------------------------------------------- past-only features
def shift(a, k):
    out = np.full(a.shape, np.nan)
    out[:, k:] = a[:, :-k]
    return out


def roll_past(a, w, fn="mean"):
    """Value at day d summarises days d-w .. d-1 (NaN-aware). NaN when no past value exists."""
    a = np.asarray(a, float)
    ok = np.isfinite(a)
    z = np.where(ok, a, 0.0)
    pad = lambda x: np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(x, 1)], 1)
    cs, cc, c2 = pad(z), pad(ok.astype(float)), pad(z * z)
    d = np.arange(a.shape[1])
    lo = np.maximum(d - w, 0)
    s, c, s2 = cs[:, d] - cs[:, lo], cc[:, d] - cc[:, lo], c2[:, d] - c2[:, lo]
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = s / c
        if fn == "mean":
            return np.where(c > 0, mean, np.nan)
        var = s2 / c - mean ** 2
        return np.where(c > 1, np.sqrt(np.maximum(var, 0)), np.nan)


def build_features(P: dict, series: pd.DataFrame) -> pd.DataFrame:
    Y, SO, DON = P["Y"], P["SO"].astype(float), P["DON"]
    n = Y.shape[0]
    feats = {
        "y_lag1": shift(Y, 1), "y_lag2": shift(Y, 2), "y_lag7": shift(Y, 7), "y_lag14": shift(Y, 14),
        "y_roll7": roll_past(Y, 7), "y_roll14": roll_past(Y, 14), "y_roll28": roll_past(Y, 28),
        "y_std14": roll_past(Y, 14, "std"),
        "y_don_roll14": roll_past(np.where(DON, Y, np.nan), 14),
        "y_don_roll28": roll_past(np.where(DON, Y, np.nan), 28),
        "so_lag1": shift(SO, 1), "so_rate7": roll_past((SO > 0).astype(float), 7),
        "so_rate14": roll_past((SO > 0).astype(float), 14), "don_frac7": roll_past(DON.astype(float), 7),
        "disc_lag1": shift(P["CTX"]["discount"], 1), "disc_roll7": roll_past(P["CTX"]["discount"], 7),
        "act_lag1": shift(P["CTX"]["activity_flag"], 1), "act_roll7": roll_past(P["CTX"]["activity_flag"], 7),
        "hol_lag1": shift(P["CTX"]["holiday_flag"], 1), "precpt_lag1": shift(P["CTX"]["precpt"], 1),
        "temp_lag1": shift(P["CTX"]["avg_temperature"], 1),
    }
    # exponentially weighted past mean and same-weekday past mean
    ew = np.full(Y.shape, np.nan)
    dowm = np.full(Y.shape, np.nan)
    for d in range(1, N_DAYS):
        prev = ew[:, d - 1]
        ew[:, d] = np.where(np.isnan(prev), Y[:, d - 1], 0.2 * Y[:, d - 1] + 0.8 * prev)
        same = Y[:, d - 7::-7] if d >= 7 else None
        if same is not None and same.shape[1]:
            dowm[:, d] = same.mean(1)
    feats["y_ewm"] = ew
    feats["y_dow_mean"] = dowm
    dow = ((DATES.astype("datetime64[D]").view("int64") - 4) % 7)  # 0 = Monday
    F = pd.DataFrame({"sid": np.repeat(np.arange(n), N_DAYS).astype(np.int32),
                      "d": np.tile(np.arange(N_DAYS), n).astype(np.int16)})
    for k, v in feats.items():
        F[k] = v.reshape(-1).astype(np.float32)
    F["dow"] = np.tile(dow, n).astype(np.float32)
    F["is_weekend"] = (F["dow"] >= 5).astype(np.float32)
    F["n_hist_days"] = F["d"].astype(np.float32)
    for c in CAT_FEATS:
        F[c] = np.repeat(series[c].to_numpy(), N_DAYS).astype(np.float32)
    F["y"] = Y.reshape(-1)
    F["donor"] = DON.reshape(-1)
    return F


FEATURES: list[str] = []  # filled in main()


def Xm(df):
    return df[FEATURES].to_numpy(np.float32)


def train(df_tr, df_va, objective, alpha=None):
    p = dict(BASE_LGB, objective=objective, metric="quantile" if objective == "quantile" else "l2")
    if alpha is not None:
        p["alpha"] = alpha
    dtr = lgb.Dataset(Xm(df_tr), df_tr.y.to_numpy(), feature_name=FEATURES, categorical_feature=CAT_FEATS,
                      params={"feature_pre_filter": False})
    dva = lgb.Dataset(Xm(df_va), df_va.y.to_numpy(), reference=dtr)
    b = lgb.train(p, dtr, 2000, valid_sets=[dva], callbacks=[lgb.early_stopping(50, verbose=False)])
    return b


# ----------------------------------------------------------------------------------- pooled residual tables
def pool_labels(meta: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "category_x_sales_tier": (meta.first_category_id.astype(str) + "|" + meta.sales_tier.astype(str)).to_numpy(),
        "category": meta.first_category_id.astype(str).to_numpy(),
        "management_group": meta.management_group_id.astype(str).to_numpy(),
        "global": np.array(["global"] * len(meta)),
    }


def residual_table(resid: np.ndarray, meta: pd.DataFrame, tau: float, conformal: bool) -> dict:
    """Per pool: conformal order statistic r_(ceil((n+1)tau)) or plain empirical tau-quantile; pools with < MIN_POOL rows are skipped."""
    tab = {}
    for lvl, lab in pool_labels(meta).items():
        s = pd.Series(resid).groupby(lab)
        t = {}
        for pool, g in s:
            v = np.sort(g.to_numpy())
            if len(v) < MIN_POOL and lvl != "global":
                continue
            if conformal:
                k = min(int(np.ceil((len(v) + 1) * tau)), len(v))
                t[pool] = float(v[k - 1])
            else:
                t[pool] = float(np.quantile(v, tau))
        tab[lvl] = t
    return tab


def apply_table(tab: dict, meta: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    labs = pool_labels(meta)
    out = np.full(len(meta), np.nan)
    lvl_used = np.array([""] * len(meta), dtype=object)
    for lvl in ["category_x_sales_tier", "category", "management_group", "global"]:
        need = np.isnan(out)
        if not need.any():
            break
        vals = pd.Series(labs[lvl][need]).map(tab[lvl]).to_numpy(dtype=float)
        idx = np.nonzero(need)[0]
        hit = np.isfinite(vals)
        out[idx[hit]] = vals[hit]
        lvl_used[idx[hit]] = lvl
    return out, lvl_used


def seasonal_naive(Y: np.ndarray, sid: np.ndarray, d: np.ndarray) -> np.ndarray:
    pred = np.full(len(sid), np.nan)
    for k in (7, 14):
        ok = np.isnan(pred) & (d - k >= 0)
        pred[ok] = Y[sid[ok], d[ok] - k]
    pm = roll_past(Y, N_DAYS)
    ok = np.isnan(pred)
    pred[ok] = np.nan_to_num(pm[sid[ok], d[ok]])
    return pred


# ------------------------------------------------------------------------------------------------- main
def main() -> None:
    global FEATURES
    t0 = time.time()
    for p in (WH, APP, MODELS):
        p.mkdir(parents=True, exist_ok=True)

    series = pd.read_parquet(SERIES_FILE).sort_values("key").reset_index(drop=True)
    series["sid"] = np.arange(len(series))
    log(f"{len(series):,} series selected")
    P = load_panel(series)
    log(f"panel loaded: {P['Y'].shape[0]:,} series x {N_DAYS} days, donor share {P['DON'].mean():.4f}")

    F = build_features(P, series)
    FEATURES = [c for c in F.columns if c not in ("sid", "d", "y", "donor")]
    meta_all = series.set_index("sid").loc[F.sid, ["first_category_id", "management_group_id", "sales_tier"]].reset_index(drop=True)
    log(f"features built: {F.shape}, {len(FEATURES)} features")

    fit, tune, cal = F.d.isin(FIT_D) & (F.d >= 7), F.d.isin(TUNE_D), F.d.isin(CAL_D)
    don = F.donor.to_numpy()

    # ---- train models
    boosters, info = {}, {}
    for tau, q in zip(TAUS, QN):
        b = train(F[fit & don], F[tune & don], "quantile", tau)
        boosters[("demand", q)] = b
        b2 = train(F[fit], F[tune], "quantile", tau)
        boosters[("raw", q)] = b2
        info[q] = {"demand_best_iter": b.best_iteration, "raw_best_iter": b2.best_iteration}
        log(f"trained {q}: demand iters {b.best_iteration}, raw iters {b2.best_iteration}")
    bp = train(F[fit], F[tune], "regression")
    boosters[("raw_point", "point")] = bp
    info["point"] = {"raw_best_iter": bp.best_iteration}
    for (fam, q), b in boosters.items():
        b.save_model(str(MODELS / f"{fam}_{q}.txt"), num_iteration=b.best_iteration)
    log("models saved")

    # ---- raw predictions for days 61-97
    scope = F.d >= TUNE_D[0]
    S = F[scope].reset_index(drop=True)
    meta = meta_all[scope.to_numpy()].reset_index(drop=True)
    X = Xm(S)
    pred = {}
    for q in QN:
        pred[("demand_uncal", q)] = np.clip(boosters[("demand", q)].predict(X, num_iteration=boosters[("demand", q)].best_iteration), 0, None)
        pred[("raw_quantile", q)] = np.clip(boosters[("raw", q)].predict(X, num_iteration=boosters[("raw", q)].best_iteration), 0, None)
    point = np.clip(bp.predict(X, num_iteration=bp.best_iteration), 0, None)
    sn = seasonal_naive(P["Y"], S.sid.to_numpy(), S.d.to_numpy().astype(int))

    # ---- calibration tables from donor rows of days 76-90 (outcomes of these days only)
    calm = (S.d.isin(CAL_D) & S.donor).to_numpy()
    ycal = S.y.to_numpy()[calm]
    tables = {}
    for tau, q in zip(TAUS, QN):
        tables[("demand_conformal", q)] = residual_table(ycal - pred[("demand_uncal", q)][calm], meta[calm], tau, True)
        tables[("raw_point_resid", q)] = residual_table(ycal - point[calm], meta[calm], tau, False)
        tables[("seasonal_naive", q)] = residual_table(ycal - sn[calm], meta[calm], tau, False)
    base = {"demand_conformal": None, "raw_point_resid": point, "seasonal_naive": sn}
    pool_used = None
    for code in ["demand_conformal", "raw_point_resid", "seasonal_naive"]:
        cols = []
        for q in QN:
            corr, lvl = apply_table(tables[(code, q)], meta)
            b0 = pred[("demand_uncal", q)] if code == "demand_conformal" else base[code]
            cols.append(np.maximum(0.0, b0 + corr))
            if code == "demand_conformal" and q == "q50":
                pool_used = lvl
        arr = np.sort(np.stack(cols, 1), 1)  # monotone rearrangement
        for i, q in enumerate(QN):
            pred[(code, q)] = arr[:, i]
    for code in ["demand_uncal", "raw_quantile"]:
        arr = np.sort(np.stack([pred[(code, q)] for q in QN], 1), 1)
        for i, q in enumerate(QN):
            pred[(code, q)] = arr[:, i]
    json.dump({f"{c}|{q}": t for (c, q), t in tables.items()}, open(APP / "residual_tables.json", "w"))
    log("calibration done")

    # ---------------------------------------------------------------- star schema
    date_key = lambda d: np.array([int(str(DATES[i]).replace("-", "")) for i in d])
    dts = pd.to_datetime(DATES.astype(str))
    dim_date = pd.DataFrame({
        "date_key": date_key(range(N_DAYS)), "date": dts.date, "day_index": np.arange(1, N_DAYS + 1),
        "weekday_num": dts.dayofweek + 1, "weekday_name": dts.day_name().str[:3],
        "week_start": (dts - pd.to_timedelta(dts.dayofweek, unit="D")).date,
        "iso_week": dts.isocalendar().week.to_numpy(), "month_name": dts.month_name().str[:3],
        "is_weekend": dts.dayofweek >= 5, "period": PERIOD,
        "period_order": pd.Series(PERIOD).map({"model fit": 1, "tuning": 2, "calibration": 3, "final (held out)": 4}).to_numpy(),
    })
    # product categories must be a product attribute for dim_series to stay consistent
    dim_series = pd.DataFrame({
        "series_key": series.sid, "city_id": series.city_id, "store_id": series.store_id, "product_id": series.product_id,
        "city": "City " + series.city_id.astype(str).str.zfill(2),
        "store": "Store " + series.store_id.astype(str).str.zfill(3),
        "product": "Product " + series.product_id.astype(str).str.zfill(3),
        "store_product": "S" + series.store_id.astype(str).str.zfill(3) + " / P" + series.product_id.astype(str).str.zfill(3),
        "management_group": "Group " + series.management_group_id.astype(str),
        "category_l1": "Cat " + series.first_category_id.astype(str).str.zfill(2),
        "category_l2": "Sub " + series.second_category_id.astype(str).str.zfill(2),
        "category_l3": "Leaf " + series.third_category_id.astype(str).str.zfill(3),
        "sales_tier": series.sales_tier, "stockout_tier": series.stockout_tier,
        "planner_url": "http://localhost:8501/?series=" + series.sid.astype(str),
    })
    dim_model = pd.DataFrame(MODEL_DIM)
    dim_policy = dim_model.rename(columns={"model_key": "policy_key", "model_code": "policy_code", "model_name": "policy_name"})
    dim_policy["description"] = "Order the scenario's critical-ratio quantile of: " + dim_model.model_name
    dim_scenario = pd.DataFrame(SCENARIOS)

    Y, SO, DON = P["Y"], P["SO"], P["DON"]
    n = Y.shape[0]
    fact_sales = pd.DataFrame({
        "date_key": np.tile(date_key(range(N_DAYS)), n), "series_key": np.repeat(np.arange(n), N_DAYS),
        "units_sold": Y.reshape(-1).round(4), "units_sold_24h": P["SA"].reshape(-1).round(4),
        "stockout_hours": SO.reshape(-1), "stockout_flag": (SO > 0).reshape(-1).astype(int),
        "donor_flag": DON.reshape(-1).astype(int),
        "demand_proxy": np.where(DON, Y, np.nan).reshape(-1).round(4),
        "discount": P["CTX"]["discount"].reshape(-1).round(4),
        "activity_flag": P["CTX"]["activity_flag"].reshape(-1).astype(int),
        "holiday_flag": P["CTX"]["holiday_flag"].reshape(-1).astype(int),
    })

    dk = date_key(S.d.to_numpy())
    yv = S.y.to_numpy()
    dn = S.donor.to_numpy()
    fc = []
    for m in MODEL_DIM:
        fc.append(pd.DataFrame({
            "date_key": dk, "series_key": S.sid.to_numpy(), "model_key": m["model_key"],
            **{q: pred[(m["model_code"], q)].round(4) for q in QN},
            "actual_demand": np.where(dn, yv, np.nan).round(4), "is_scored": dn.astype(int),
        }))
    fact_forecast = pd.concat(fc, ignore_index=True)

    fin = S.d.isin(FINAL_D).to_numpy()
    orders = []
    for m in MODEL_DIM:
        for sc in SCENARIOS:
            Q = pred[(m["model_code"], sc["quantile"])][fin]
            D = np.where(dn[fin], yv[fin], np.nan)
            short, left = np.maximum(D - Q, 0), np.maximum(Q - D, 0)
            orders.append(pd.DataFrame({
                "date_key": dk[fin], "series_key": S.sid.to_numpy()[fin], "policy_key": m["model_key"],
                "scenario_key": sc["scenario_key"], "order_qty": Q.round(4), "demand": D.round(4),
                "sold_units": np.minimum(Q, D).round(4), "shortage_units": short.round(4), "leftover_units": left.round(4),
                "cost": (sc["c_u"] * short + sc["c_o"] * left).round(4),
            }))
    fact_order = pd.concat(orders, ignore_index=True)

    # paper's 9-policy results (aggregates, run E, simulated censoring) for the policy comparison page
    pap = pd.read_csv(PAPER_ORDERS)
    pap = pap.copy()  # 'deep subsample' rows = the two TFT policies, scored on a 600-series subset only
    pap.columns = [c.replace(" ", "_") for c in pap.columns]
    pap["matched_cell"] = (pap.train_mech == pap.test_hist).astype(int)
    pap["scenario_key"] = pap.beta.map({s["beta"]: s["scenario_key"] for s in SCENARIOS}).astype(int)
    pap.insert(0, "row_key", np.arange(len(pap)))

    tables_out = {"dim_date": dim_date, "dim_series": dim_series, "dim_model": dim_model, "dim_policy": dim_policy,
                  "dim_scenario": dim_scenario, "fact_sales_daily": fact_sales, "fact_forecast": fact_forecast,
                  "fact_order": fact_order, "fact_paper_policy_results": pap}
    for name, df in tables_out.items():
        df.to_csv(WH / f"{name}.csv", index=False)
    log("warehouse CSVs written: " + ", ".join(f"{k}={len(v):,}" for k, v in tables_out.items()))

    # ---------------------------------------------------------------- app files
    F[F.d.isin(FINAL_D)].reset_index(drop=True).to_parquet(APP / "features_final.parquet", index=False)
    meta_all[F.d.isin(FINAL_D).to_numpy()].reset_index(drop=True).to_parquet(APP / "meta_final.parquet", index=False)

    # ---------------------------------------------------------------- headline metrics (final week, donor rows)
    fo = fact_order[fact_order.demand.notna()]
    summ = (fo.groupby(["scenario_key", "policy_key"])
              .agg(n=("cost", "size"), mean_cost=("cost", "mean"), demand=("demand", "sum"), sold=("sold_units", "sum"),
                   leftover=("leftover_units", "sum"), ordered=("order_qty", "sum"))
              .reset_index())
    summ["fill_rate"] = summ.sold / summ.demand
    sn_cost = summ[summ.policy_key == 5].set_index("scenario_key").mean_cost
    summ["saving_vs_seasonal_naive"] = 1 - summ.mean_cost / summ.scenario_key.map(sn_cost)
    ff = fact_forecast[(fact_forecast.is_scored == 1) & fact_forecast.date_key.isin(date_key(FINAL_D))]
    acc = ff.groupby("model_key").apply(lambda g: pd.Series({
        "n": len(g), "wape_q50": (g.q50 - g.actual_demand).abs().sum() / g.actual_demand.sum(),
        "bias_q50": (g.q50 - g.actual_demand).sum() / g.actual_demand.sum(),
        "coverage_q90": (g.actual_demand <= g.q90).mean(),
        "coverage_q25_q75": ((g.actual_demand >= g.q25) & (g.actual_demand <= g.q75)).mean()}), include_groups=False).reset_index()
    summary = {
        "series": int(n), "days": N_DAYS, "donor_share_all_days": float(DON.mean()),
        "final_week_donor_rows": int(dn[fin].sum()), "model_iterations": info,
        "conformal_q50_pool_levels": pd.Series(pool_used[fin]).value_counts().to_dict(),
        "order_summary": summ.merge(dim_policy[["policy_key", "policy_name"]]).merge(dim_scenario[["scenario_key", "scenario_name"]]).to_dict("records"),
        "forecast_accuracy": acc.merge(dim_model[["model_key", "model_name"]]).to_dict("records"),
        "features": FEATURES, "runtime_s": round(time.time() - t0, 1),
    }
    json.dump(summary, open(OUT / "summary.json", "w"), indent=2, default=float)
    pd.set_option("display.width", 200)
    print(summ.merge(dim_policy[["policy_key", "policy_code"]]).round(4).to_string(index=False))
    print(acc.merge(dim_model[["model_key", "model_code"]]).round(4).to_string(index=False))
    log(f"done in {time.time() - t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
