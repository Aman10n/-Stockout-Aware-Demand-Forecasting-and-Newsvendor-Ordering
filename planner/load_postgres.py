"""Load the warehouse CSVs into PostgreSQL and run the validation checks. Safe to re-run.

    docker run -d --name stockout-pg -e POSTGRES_PASSWORD=stockout -p 5432:5432 postgres:16
    python planner/load_postgres.py            # or set PG_URL=postgresql://user:pass@host:5432/db

Each run creates missing tables, then truncates and reloads all of them in one transaction,
so a failed load leaves the previous data in place.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import psycopg2

BASE = Path(__file__).resolve().parent
WH = BASE / "output" / "warehouse"
PG_URL = os.environ.get("PG_URL", "postgresql://postgres:stockout@localhost:5432/postgres")
LOAD_ORDER = ["dim_date", "dim_series", "dim_model", "dim_policy", "dim_scenario", "fact_sales_daily",
              "fact_forecast", "fact_order", "fact_paper_policy_results", "security_user_city"]


def load(cur) -> None:
    cur.execute((BASE / "sql" / "schema.sql").read_text())
    cur.execute("SET search_path = stockout")
    cur.execute("TRUNCATE " + ", ".join(LOAD_ORDER) + " CASCADE")
    for t in LOAD_ORDER:
        path = WH / f"{t}.csv"
        cols = path.open(encoding="utf-8").readline().strip()
        with path.open(encoding="utf-8") as fh:
            cur.copy_expert(f"COPY {t} ({cols}) FROM STDIN WITH (FORMAT csv, HEADER true, NULL '')", fh)
        print(f"  loaded {t}")


def validate(cur) -> bool:
    """The five validation queries: counts, orphans, duplicates, totals vs pipeline, paper reconciliation."""
    ok = True

    def check(name, passed, detail=""):
        nonlocal ok
        ok &= bool(passed)
        print(f"  [{'PASS' if passed else 'FAIL'}] {name} {detail}")

    # 1. row counts match the source CSVs
    for t in LOAD_ORDER:
        n_csv = sum(1 for _ in (WH / f"{t}.csv").open(encoding="utf-8")) - 1
        cur.execute(f"SELECT count(*) FROM {t}")
        n_db = cur.fetchone()[0]
        check(f"row count {t}", n_db == n_csv, f"db={n_db:,} csv={n_csv:,}")
    # 2. no orphan keys (FKs enforce this; the query proves it for the reviewer)
    cur.execute("""SELECT count(*) FROM fact_order o LEFT JOIN dim_series s USING (series_key)
                   LEFT JOIN dim_date d USING (date_key) WHERE s.series_key IS NULL OR d.date_key IS NULL""")
    check("no orphan keys in fact_order", cur.fetchone()[0] == 0)
    # 3. one row per store-product-day and every series has all 97 days
    cur.execute("SELECT count(*) FROM (SELECT series_key FROM fact_sales_daily GROUP BY series_key HAVING count(*) <> 97) x")
    check("97 days for every store-product", cur.fetchone()[0] == 0)
    # 4. policy KPIs reconcile with the pipeline's summary.json
    summ = pd.DataFrame(json.load(open(BASE / "output" / "summary.json"))["order_summary"])
    cur.execute("SELECT scenario_name, policy_name, mean_cost, fill_rate FROM v_policy_kpis_final")
    db = pd.DataFrame(cur.fetchall(), columns=["scenario_name", "policy_name", "mean_cost_db", "fill_db"])
    m = summ.merge(db, on=["scenario_name", "policy_name"])
    diff = max((m.mean_cost - m.mean_cost_db.astype(float)).abs().max(), (m.fill_rate - m.fill_db.astype(float)).abs().max())
    check("policy mean cost and fill rate match the pipeline", len(m) == 15 and diff < 1e-3, f"(max diff {diff:.2e})")
    # 5. paper headline: pooled conformal beats seasonal naive by 14.8% at equal costs (matched cells)
    cur.execute("""SELECT 1 - avg(mean_cost) FILTER (WHERE policy = 'demand-quantile LightGBM + pooled conformal')
                         / avg(mean_cost) FILTER (WHERE policy = 'seasonal_naive + residual quantile')
                   FROM fact_paper_policy_results WHERE matched_cell = 1 AND scenario_key = 2""")
    saving = float(cur.fetchone()[0])
    check("paper saving vs seasonal naive (equal costs) = 14.8%", abs(saving - 0.1483) < 5e-4, f"({saving:.4f})")
    return ok


def main() -> None:
    with psycopg2.connect(PG_URL) as conn:
        with conn.cursor() as cur:
            print("loading ...")
            load(cur)
            print("validating ...")
            passed = validate(cur)
    print("all checks passed" if passed else "SOME CHECKS FAILED")
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
