"""Independent checks on the saved artefacts, used for the test-case table in the report."""
import json, hashlib
from pathlib import Path
import pandas as pd, numpy as np
R = Path(__file__).resolve().parents[1]
WH = R / "planner/output/warehouse"
S = json.loads((R / "planner/output/summary.json").read_text())
out = {}
rows = {t: sum(1 for _ in open(WH / f"{t}.csv", encoding="utf-8")) - 1 for t in
        ["dim_date","dim_series","dim_model","dim_policy","dim_scenario","fact_sales_daily","fact_forecast","fact_order","fact_paper_policy_results","security_user_city"]}
out["rows"] = rows
fs = pd.read_csv(WH/"fact_sales_daily.csv"); dd = pd.read_csv(WH/"dim_date.csv")
out["days_per_series_min_max"] = [int(fs.groupby("series_key").size().min()), int(fs.groupby("series_key").size().max())]
out["donor_share_all"] = float(fs.donor_flag.mean())
out["stockout_rate_97d"] = float(fs.stockout_flag.mean())
fk = dd.loc[dd.period=="final (held out)","date_key"]
out["stockout_rate_final_week"] = float(fs[fs.date_key.isin(fk)].stockout_flag.mean())
out["donor_rows_final"] = int(fs[fs.date_key.isin(fk)].donor_flag.sum())
out["demand_blank_iff_censored"] = bool(((fs.donor_flag==1) == fs.demand_proxy.notna()).all())
fo = pd.read_csv(WH/"fact_order.csv")
fo = fo[fo.demand.notna()]
g = fo.groupby(["scenario_key","policy_key"]).agg(mean_cost=("cost","mean"), sold=("sold_units","sum"), dem=("demand","sum"), n=("cost","size")).reset_index()
g["fill"] = g.sold/g.dem
ref = pd.DataFrame(S["order_summary"])[["scenario_key","policy_key","mean_cost","fill_rate"]]
m = g.merge(ref, on=["scenario_key","policy_key"])
out["policy_cells"] = len(m); out["max_cost_diff"] = float((m.mean_cost_x-m.mean_cost_y).abs().max()); out["max_fill_diff"] = float((m.fill-m.fill_rate).abs().max())
out["scored_rows_per_cell"] = sorted(set(g.n.tolist()))
orph = ~fo.series_key.isin(pd.read_csv(WH/"dim_series.csv").series_key)
out["orphan_series_keys"] = int(orph.sum())
ff = pd.read_csv(WH/"fact_forecast.csv")
ff = ff[(ff.is_scored==1) & ff.date_key.isin(fk)]
acc = ff.groupby("model_key").apply(lambda x: pd.Series({"wape": (x.q50-x.actual_demand).abs().sum()/x.actual_demand.sum(),
        "cov90": (x.actual_demand<=x.q90).mean(), "cross": int(((x.q25>x.q50)|(x.q50>x.q75)|(x.q75>x.q90)).sum())}))
out["forecast"] = acc.round(6).to_dict(orient="index")
P = pd.read_csv(WH/"fact_paper_policy_results.csv")
pe = P[(P.scenario_key==2)&(P.matched_cell==1)].groupby("policy").mean_cost.mean()
out["paper_saving_equal"] = float(1 - pe[pe.index.str.startswith("demand-quantile LightGBM + pooled")].iloc[0]/pe[pe.index.str.startswith("seasonal")].iloc[0])
lock = R/"results/phase0_9_5k/phase5_9/manifests/final_test_lock.json"
out["lock_sha256"] = hashlib.sha256(lock.read_bytes()).hexdigest()
json.dump(out, open(R/"report/assets/checks.json","w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
