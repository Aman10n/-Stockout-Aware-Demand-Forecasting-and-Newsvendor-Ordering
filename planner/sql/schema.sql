-- Star schema for the Stockout-Aware Order Planner (PostgreSQL 14+).
-- Safe to re-run: CREATE ... IF NOT EXISTS, views are CREATE OR REPLACE.
CREATE SCHEMA IF NOT EXISTS stockout;
SET search_path = stockout;

-- ------------------------------------------------------------------ dimensions
CREATE TABLE IF NOT EXISTS dim_date (
    date_key      integer PRIMARY KEY,          -- yyyymmdd
    date          date    NOT NULL UNIQUE,
    day_index     smallint NOT NULL,            -- 1..97
    weekday_num   smallint NOT NULL,            -- 1 = Monday
    weekday_name  text    NOT NULL,
    week_start    date    NOT NULL,
    iso_week      smallint NOT NULL,
    month_name    text    NOT NULL,
    is_weekend    boolean NOT NULL,
    period        text    NOT NULL,             -- model fit / tuning / calibration / final (held out)
    period_order  smallint NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_series (           -- one row per store-product (item-location)
    series_key       integer PRIMARY KEY,
    city_id          integer NOT NULL,
    store_id         integer NOT NULL,
    product_id       integer NOT NULL,
    city             text NOT NULL,
    store            text NOT NULL,
    product          text NOT NULL,
    store_product    text NOT NULL,
    management_group text NOT NULL,
    category_l1      text NOT NULL,
    category_l2      text NOT NULL,
    category_l3      text NOT NULL,
    sales_tier       text NOT NULL,
    stockout_tier    text NOT NULL,
    planner_url      text NOT NULL,
    UNIQUE (store_id, product_id)
);
CREATE INDEX IF NOT EXISTS ix_dim_series_city ON dim_series (city);

CREATE TABLE IF NOT EXISTS dim_model (
    model_key      smallint PRIMARY KEY,
    model_code     text NOT NULL UNIQUE,
    model_name     text NOT NULL,
    stockout_aware boolean NOT NULL,
    description    text NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_policy (
    policy_key     smallint PRIMARY KEY,
    policy_code    text NOT NULL UNIQUE,
    policy_name    text NOT NULL,
    stockout_aware boolean NOT NULL,
    description    text NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_scenario (
    scenario_key  smallint PRIMARY KEY,
    scenario_name text NOT NULL,
    c_u           numeric NOT NULL,             -- cost of one unit short
    c_o           numeric NOT NULL,             -- cost of one unit left over
    beta          numeric NOT NULL,             -- critical ratio c_u / (c_u + c_o)
    quantile      text NOT NULL
);

-- ------------------------------------------------------------------ facts
CREATE TABLE IF NOT EXISTS fact_sales_daily (     -- grain: store-product x day (97 days, real data)
    date_key       integer  NOT NULL REFERENCES dim_date,
    series_key     integer  NOT NULL REFERENCES dim_series,
    units_sold     double precision NOT NULL,   -- 06:00-21:59
    units_sold_24h double precision NOT NULL,
    stockout_hours smallint NOT NULL,
    stockout_flag  smallint NOT NULL,
    donor_flag     smallint NOT NULL,           -- 1 = no stockout, demand observed exactly
    demand_proxy   double precision,            -- NULL on censored days, never imputed
    discount       double precision,
    activity_flag  smallint,
    holiday_flag   smallint,
    PRIMARY KEY (series_key, date_key)
);
CREATE INDEX IF NOT EXISTS ix_sales_date ON fact_sales_daily (date_key);

CREATE TABLE IF NOT EXISTS fact_forecast (        -- grain: store-product x day x model (days 61-97)
    date_key      integer  NOT NULL REFERENCES dim_date,
    series_key    integer  NOT NULL REFERENCES dim_series,
    model_key     smallint NOT NULL REFERENCES dim_model,
    q25           double precision NOT NULL,
    q50           double precision NOT NULL,
    q75           double precision NOT NULL,
    q90           double precision NOT NULL,
    actual_demand double precision,             -- NULL when the day was censored
    is_scored     smallint NOT NULL,
    PRIMARY KEY (series_key, date_key, model_key)
);
CREATE INDEX IF NOT EXISTS ix_forecast_date_model ON fact_forecast (date_key, model_key);

CREATE TABLE IF NOT EXISTS fact_order (           -- grain: store-product x day x policy x scenario (final week)
    date_key       integer  NOT NULL REFERENCES dim_date,
    series_key     integer  NOT NULL REFERENCES dim_series,
    policy_key     smallint NOT NULL REFERENCES dim_policy,
    scenario_key   smallint NOT NULL REFERENCES dim_scenario,
    order_qty      double precision NOT NULL,
    demand         double precision,
    sold_units     double precision,
    shortage_units double precision,
    leftover_units double precision,
    cost           double precision,
    PRIMARY KEY (series_key, date_key, policy_key, scenario_key)
);
CREATE INDEX IF NOT EXISTS ix_order_scenario_policy ON fact_order (scenario_key, policy_key, date_key);

CREATE TABLE IF NOT EXISTS fact_paper_policy_results (   -- grain: scenario x policy x train mechanism x test history
    row_key                 integer PRIMARY KEY,
    scenario                text NOT NULL,
    beta                    numeric NOT NULL,
    policy                  text NOT NULL,
    train_mech              text NOT NULL,
    test_hist               text NOT NULL,
    population              text NOT NULL,
    unsupported_order_share double precision,
    pool_fallback_share     double precision,
    n                       integer NOT NULL,
    mean_cost               double precision NOT NULL,
    median_cost             double precision,
    total_shortage          double precision,
    total_leftover          double precision,
    fill_rate               double precision,
    leftover_share          double precision,
    cycle_service           double precision,
    mean_order              double precision,
    median_order            double precision,
    matched_cell            smallint NOT NULL,
    scenario_key            smallint NOT NULL REFERENCES dim_scenario
);

CREATE TABLE IF NOT EXISTS security_user_city (  -- row-level security mapping used by Power BI
    user_email text NOT NULL,
    city       text NOT NULL,
    PRIMARY KEY (user_email, city)
);

-- ------------------------------------------------------------------ clean views for Power BI
CREATE OR REPLACE VIEW v_policy_kpis_final AS        -- one row per scenario x policy, scored days only
SELECT s.scenario_name, p.policy_name,
       count(o.demand)                                      AS scored_days,
       sum(o.sold_units) / nullif(sum(o.demand), 0)         AS fill_rate,
       sum(o.leftover_units) / nullif(sum(o.order_qty) FILTER (WHERE o.demand IS NOT NULL), 0) AS leftover_share,
       avg(o.cost)                                          AS mean_cost
FROM fact_order o
JOIN dim_policy p   USING (policy_key)
JOIN dim_scenario s USING (scenario_key)
WHERE o.demand IS NOT NULL
GROUP BY s.scenario_key, s.scenario_name, p.policy_key, p.policy_name;

CREATE OR REPLACE VIEW v_forecast_accuracy_final AS  -- WAPE, bias and coverage per model, held-out week
SELECT m.model_name,
       count(*)                                                         AS scored_rows,
       1 - sum(abs(f.q50 - f.actual_demand)) / nullif(sum(f.actual_demand), 0) AS accuracy,
       sum(f.q50 - f.actual_demand) / nullif(sum(f.actual_demand), 0)     AS bias,
       avg((f.actual_demand <= f.q90)::int)                              AS q90_coverage,
       avg((f.actual_demand BETWEEN f.q25 AND f.q75)::int)               AS q25_q75_coverage
FROM fact_forecast f
JOIN dim_model m USING (model_key)
JOIN dim_date d  USING (date_key)
WHERE f.is_scored = 1 AND d.period = 'final (held out)'
GROUP BY m.model_key, m.model_name;

CREATE OR REPLACE VIEW v_stockout_city_weekday AS    -- the heatmap on report page 3
SELECT ds.city, dd.weekday_num, dd.weekday_name,
       avg(f.stockout_flag::numeric) AS stockout_rate,
       sum(f.stockout_hours)         AS stockout_hours
FROM fact_sales_daily f
JOIN dim_series ds USING (series_key)
JOIN dim_date dd   USING (date_key)
GROUP BY ds.city, dd.weekday_num, dd.weekday_name;
