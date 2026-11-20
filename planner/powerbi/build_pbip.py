"""Generate the Power BI project (PBIP: TMDL semantic model + PBIR report) from the warehouse CSVs.

Run after planner/pipeline.py:   python planner/powerbi/build_pbip.py
Then open planner/powerbi/StockoutPlanner.pbip in Power BI Desktop and click Refresh.
"""
from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
WH = HERE.parent / "output" / "warehouse"
NAME = "StockoutPlanner"
SM = HERE / f"{NAME}.SemanticModel"
RP = HERE / f"{NAME}.Report"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"

DATE_COLS = {("dim_date", "date"), ("dim_date", "week_start")}
HIDDEN_DIM_COLS = {"date_key", "series_key", "model_key", "policy_key", "scenario_key", "day_index", "weekday_num",
                   "period_order", "city_id", "store_id", "product_id", "row_key"}
SORT_BY = {("dim_date", "weekday_name"): "weekday_num", ("dim_date", "period"): "period_order",
           ("dim_scenario", "scenario_name"): "scenario_key", ("dim_policy", "policy_name"): "policy_key",
           ("dim_model", "model_name"): "model_key"}
FORMATS = {("dim_date", "date"): "dd mmm yyyy", ("dim_date", "week_start"): "dd mmm yyyy"}
TABLES = ["dim_date", "dim_series", "dim_model", "dim_policy", "dim_scenario", "fact_sales_daily", "fact_forecast",
          "fact_order", "fact_paper_policy_results", "security_user_city"]
RELS = [("fact_sales_daily", "date_key", "dim_date"), ("fact_sales_daily", "series_key", "dim_series"),
        ("fact_forecast", "date_key", "dim_date"), ("fact_forecast", "series_key", "dim_series"),
        ("fact_forecast", "model_key", "dim_model"), ("fact_order", "date_key", "dim_date"),
        ("fact_order", "series_key", "dim_series"), ("fact_order", "policy_key", "dim_policy"),
        ("fact_order", "scenario_key", "dim_scenario"), ("fact_paper_policy_results", "scenario_key", "dim_scenario")]

# ----------------------------------------------------------------------------------------- DAX measures
G_MODEL = "VAR _m = IF ( HASONEVALUE ( dim_model[model_key] ), VALUES ( dim_model[model_key] ), 1 )"
G_SCEN = "VAR _s = IF ( HASONEVALUE ( dim_scenario[scenario_key] ), VALUES ( dim_scenario[scenario_key] ), 2 )"
G_POL = "VAR _p = IF ( HASONEVALUE ( dim_policy[policy_key] ), VALUES ( dim_policy[policy_key] ), 1 )"


def order_sum(expr: str) -> str:
    return (f"{G_SCEN}\n{G_POL}\nRETURN\n    CALCULATE ( {expr}, dim_scenario[scenario_key] = _s, "
            f"dim_policy[policy_key] = _p )")


def fc(expr: str) -> str:
    return f"{G_MODEL}\nRETURN\n    CALCULATE ( {expr}, dim_model[model_key] = _m )"


PAPER_SN = "\"seasonal_naive + residual quantile\""
MEASURES = [  # (folder, name, DAX, format, description)
    # --- sales and stockouts (real recorded data, all 97 days)
    ("1 Sales & stockouts", "Units Sold", "SUM ( fact_sales_daily[units_sold] )", "#,0.00",
     "Recorded sales 06:00-21:59. On stockout days this understates demand."),
    ("1 Sales & stockouts", "Total Demand", "SUM ( fact_sales_daily[demand_proxy] )", "#,0.00",
     "Exact demand, known only on full-stock (donor) days; censored days are blank, never imputed."),
    ("1 Sales & stockouts", "Store-Product Days", "COUNTROWS ( fact_sales_daily )", "#,0",
     "Number of store-product-days in the filter context."),
    ("1 Sales & stockouts", "Stockout Days", "SUM ( fact_sales_daily[stockout_flag] )", "#,0",
     "Store-product-days with at least one out-of-stock hour between 06:00 and 21:59."),
    ("1 Sales & stockouts", "Stockout Rate %", "DIVIDE ( [Stockout Days], [Store-Product Days] )", "0.0%",
     "Share of store-product-days with a stockout (real data)."),
    ("1 Sales & stockouts", "Stockout Hours", "SUM ( fact_sales_daily[stockout_hours] )", "#,0",
     "Out-of-stock hours between 06:00 and 21:59."),
    ("1 Sales & stockouts", "Full-Stock Day Share %", "DIVIDE ( SUM ( fact_sales_daily[donor_flag] ), [Store-Product Days] )", "0.0%",
     "Share of days with no stockout, i.e. days where demand is observed exactly."),
    ("1 Sales & stockouts", "Stockout Rate % (7-Day Rolling)",
     "CALCULATE ( [Stockout Rate %], DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -7, DAY ) )", "0.0%",
     "Time intelligence: stockout rate over the 7 days ending on the current date."),
    ("1 Sales & stockouts", "Stockout Rate % (Prior Week)",
     "CALCULATE ( [Stockout Rate %], DATEADD ( dim_date[date], -7, DAY ) )", "0.0%",
     "Stockout rate for the same dates one week earlier."),
    ("1 Sales & stockouts", "Stockout Rate WoW Change",
     "IF ( NOT ISBLANK ( [Stockout Rate % (Prior Week)] ), [Stockout Rate %] - [Stockout Rate % (Prior Week)] )", "+0.0%;-0.0%;0.0%",
     "Week-over-week change in stockout rate, in percentage points."),
    # --- forecast accuracy (fact_forecast; defaults to the headline model when no single model is in context)
    ("2 Forecast", "Forecast Actual Demand", fc("SUM ( fact_forecast[actual_demand] )"), "#,0.00",
     "Actual demand on scored (full-stock) forecast days."),
    ("2 Forecast", "Forecast q50", fc("SUM ( fact_forecast[q50] )"), "#,0.00",
     "Median forecast. Summing quantiles across rows is not a quantile of the sum: read at store-product-day level."),
    ("2 Forecast", "Forecast q25", fc("SUM ( fact_forecast[q25] )"), "#,0.00", "25th percentile forecast."),
    ("2 Forecast", "Forecast q90", fc("SUM ( fact_forecast[q90] )"), "#,0.00", "90th percentile forecast."),
    ("2 Forecast", "Forecast q50 (Scored Days)", fc("SUM ( fact_forecast[q50] ), fact_forecast[is_scored] = 1"), "#,0.00",
     "Median forecast on scored days only, comparable with Forecast Actual Demand."),
    ("2 Forecast", "Scored Forecast Rows", fc("COUNTROWS ( fact_forecast ), fact_forecast[is_scored] = 1"), "#,0",
     "Forecast rows with known demand."),
    ("2 Forecast", "Forecast Abs Error",
     fc("SUMX ( FILTER ( fact_forecast, fact_forecast[is_scored] = 1 ), ABS ( fact_forecast[q50] - fact_forecast[actual_demand] ) )"),
     "#,0.00", "Sum of |q50 - actual| on scored days."),
    ("2 Forecast", "WAPE %", "DIVIDE ( [Forecast Abs Error], [Forecast Actual Demand] )", "0.0%",
     "Weighted absolute percentage error of the median forecast."),
    ("2 Forecast", "Forecast Accuracy %", "IF ( NOT ISBLANK ( [WAPE %] ), 1 - [WAPE %] )", "0.0%",
     "1 - WAPE of the median forecast."),
    ("2 Forecast", "Forecast Bias %", "DIVIDE ( [Forecast q50 (Scored Days)] - [Forecast Actual Demand], [Forecast Actual Demand] )",
     "+0.0%;-0.0%;0.0%", "Positive = over-forecast, negative = under-forecast."),
    ("2 Forecast", "q90 Coverage %",
     fc("COUNTROWS ( FILTER ( fact_forecast, fact_forecast[is_scored] = 1 && fact_forecast[actual_demand] <= fact_forecast[q90] ) )")
     .replace("RETURN\n    CALCULATE", "RETURN\n    DIVIDE ( CALCULATE").rstrip() + ", [Scored Forecast Rows] )", "0.0%",
     "Share of scored days with actual demand at or below q90 (nominal 90%)."),
    ("2 Forecast", "q25-q75 Band Coverage %",
     fc("COUNTROWS ( FILTER ( fact_forecast, fact_forecast[is_scored] = 1 && fact_forecast[actual_demand] >= fact_forecast[q25] && fact_forecast[actual_demand] <= fact_forecast[q75] ) )")
     .replace("RETURN\n    CALCULATE", "RETURN\n    DIVIDE ( CALCULATE").rstrip() + ", [Scored Forecast Rows] )", "0.0%",
     "Share of scored days with actual demand inside the q25-q75 band (nominal 50%). The model has no P10."),
    ("2 Forecast", "Forecast Accuracy % (7-Day Rolling)",
     "CALCULATE ( [Forecast Accuracy %], DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -7, DAY ) )", "0.0%",
     "Accuracy over the 7 days ending on the current date."),
    ("2 Forecast", "Forecast Accuracy % (Prior Week)",
     "CALCULATE ( [Forecast Accuracy %], DATEADD ( dim_date[date], -7, DAY ) )", "0.0%",
     "Accuracy for the same dates one week earlier (forecasts exist from day 61)."),
    ("2 Forecast", "Forecast Accuracy WoW Change",
     "IF ( NOT ISBLANK ( [Forecast Accuracy % (Prior Week)] ), [Forecast Accuracy %] - [Forecast Accuracy % (Prior Week)] )",
     "+0.0%;-0.0%;0.0%", "Week-over-week change in accuracy, in percentage points."),
    # --- order simulation (final week; defaults to Equal costs + headline policy)
    ("3 Orders", "Order Qty", order_sum("SUM ( fact_order[order_qty] )"), "#,0.00", "Units ordered, all final-week days."),
    ("3 Orders", "Order Qty (Scored Days)", order_sum("SUM ( fact_order[order_qty] ), NOT ISBLANK ( fact_order[demand] )"),
     "#,0.00", "Units ordered on days with known demand."),
    ("3 Orders", "Scored Order Days", order_sum("COUNT ( fact_order[demand] )"), "#,0", "Order rows with known demand."),
    ("3 Orders", "Order Demand", order_sum("SUM ( fact_order[demand] )"), "#,0.00", "Demand on scored order days."),
    ("3 Orders", "Sold Units", order_sum("SUM ( fact_order[sold_units] )"), "#,0.00", "min(order, demand)."),
    ("3 Orders", "Lost Sales (units)", order_sum("SUM ( fact_order[shortage_units] )"), "#,0.00",
     "Simulated: max(demand - order, 0) on scored days."),
    ("3 Orders", "Leftover Units", order_sum("SUM ( fact_order[leftover_units] )"), "#,0.00",
     "Simulated end-of-day excess, max(order - demand, 0). Fresh goods: nothing carries over."),
    ("3 Orders", "Total Cost", order_sum("SUM ( fact_order[cost] )"), "#,0.00",
     "Newsvendor cost c_u x shortage + c_o x leftover, at the scenario's unit costs (relative units)."),
    ("3 Orders", "Fill Rate %", "DIVIDE ( [Sold Units], [Order Demand] )", "0.0%", "Units sold / demand on scored days."),
    ("3 Orders", "Leftover Share %", "DIVIDE ( [Leftover Units], [Order Qty (Scored Days)] )", "0.0%",
     "Share of ordered units left over."),
    ("3 Orders", "Avg Leftover per Store-Product Day", "DIVIDE ( [Leftover Units], [Scored Order Days] )", "0.000",
     "Stand-in for average ending inventory in a no-carry-over newsvendor. Days of supply is not defined here."),
    ("3 Orders", "Cycle Service Level %",
     order_sum("COUNTROWS ( fact_order ), NOT ISBLANK ( fact_order[demand] ), fact_order[shortage_units] = 0")
     .replace("RETURN\n    CALCULATE", "RETURN\n    DIVIDE ( CALCULATE").rstrip() + ", [Scored Order Days] )", "0.0%",
     "Share of scored days with no shortage."),
    ("3 Orders", "Mean Cost", "DIVIDE ( [Total Cost], [Scored Order Days] )", "0.000",
     "Average newsvendor cost per scored store-product-day."),
    ("3 Orders", "Mean Cost (Seasonal Naive)",
     "CALCULATE ( [Mean Cost], REMOVEFILTERS ( dim_policy ), dim_policy[policy_key] = 5 )", "0.000",
     "Baseline: the same cost for the seasonal-naive policy."),
    ("3 Orders", "Fill Rate % (Seasonal Naive)",
     "CALCULATE ( [Fill Rate %], REMOVEFILTERS ( dim_policy ), dim_policy[policy_key] = 5 )", "0.0%",
     "Baseline fill rate."),
    ("3 Orders", "Cost Saving % vs Seasonal Naive",
     "IF ( NOT ISBLANK ( [Mean Cost] ), 1 - DIVIDE ( [Mean Cost], [Mean Cost (Seasonal Naive)] ) )", "0.0%",
     "Relative cost reduction against the seasonal-naive baseline."),
    ("3 Orders", "Fill Rate % (7-Day Rolling)",
     "CALCULATE ( [Fill Rate %], DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -7, DAY ) )", "0.0%",
     "Orders exist for the 7 final days only, so this is cumulative within that week."),
    ("3 Orders", "Fill Rate WoW Change",
     "VAR _prev = CALCULATE ( [Fill Rate %], DATEADD ( dim_date[date], -7, DAY ) )\nRETURN\n    IF ( NOT ISBLANK ( _prev ), [Fill Rate %] - _prev )",
     "+0.0%;-0.0%;0.0%", "Blank by design: there is no order simulation for the week before the final week."),
    # --- what-if
    ("4 What-if", "Shortage Cost Ratio Value", "SELECTEDVALUE ( 'Shortage Cost Ratio'[Shortage Cost Ratio], 1 )", "0.00",
     "Selected cost of a unit short relative to a unit left over (c_u / c_o)."),
    ("4 What-if", "What-if Mean Cost",
     "DIVIDE ( [Lost Sales (units)] * [Shortage Cost Ratio Value] + [Leftover Units], [Scored Order Days] )", "0.000",
     "Re-scores the orders placed for the selected scenario at the chosen cost ratio (orders are not re-optimised)."),
    ("4 What-if", "What-if Rank",
     "IF ( HASONEVALUE ( dim_policy[policy_name] ), RANKX ( ALLSELECTED ( dim_policy[policy_name] ), [What-if Mean Cost], , ASC, DENSE ) )",
     "0", "1 = cheapest policy at the chosen cost ratio."),
    # --- paper results (run E, 9 policies, simulated censoring)
    ("5 Paper (9 policies)", "Paper Mean Cost",
     f"{G_SCEN}\nRETURN\n    CALCULATE ( AVERAGE ( fact_paper_policy_results[mean_cost] ), dim_scenario[scenario_key] = _s )",
     "0.000", "Mean newsvendor cost from the paper's final-week evaluation, averaged over train/test cells."),
    ("5 Paper (9 policies)", "Paper Fill Rate %",
     f"{G_SCEN}\nRETURN\n    CALCULATE ( AVERAGE ( fact_paper_policy_results[fill_rate] ), dim_scenario[scenario_key] = _s )",
     "0.0%", "Fill rate from the paper, averaged over cells."),
    ("5 Paper (9 policies)", "Paper What-if Mean Cost",
     f"{G_SCEN}\nRETURN\n    CALCULATE ( DIVIDE ( SUM ( fact_paper_policy_results[total_shortage] ) * [Shortage Cost Ratio Value] "
     "+ SUM ( fact_paper_policy_results[total_leftover] ), SUM ( fact_paper_policy_results[n] ) ), dim_scenario[scenario_key] = _s )",
     "0.000", "Paper orders re-scored at the chosen cost ratio."),
    ("5 Paper (9 policies)", "Paper Saving % vs Seasonal Naive",
     "IF ( SELECTEDVALUE ( fact_paper_policy_results[population] ) = \"deep subsample\", BLANK (),\n"
     "    1 - DIVIDE ( [Paper Mean Cost], CALCULATE ( [Paper Mean Cost], REMOVEFILTERS ( fact_paper_policy_results[policy], "
     f"fact_paper_policy_results[population] ), fact_paper_policy_results[policy] = {PAPER_SN} ) ) )",
     "0.0%", "Blank for the two TFT policies, which were scored on a 600-series subset."),
]


# --------------------------------------------------------------------------------------- TMDL writing
def q(name: str) -> str:
    return name if name.replace("_", "").isalnum() else "'" + name.replace("'", "''") + "'"


_TAG = [0]


def tag() -> str:
    """Deterministic lineage tags, so re-running the script gives a stable diff."""
    _TAG[0] += 1
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{NAME}/{_TAG[0]}"))


def indent(text: str, tabs: int) -> str:
    return "\n".join("\t" * tabs + line for line in text.splitlines())


def col_type(table: str, col: str, s: pd.Series):
    if (table, col) in DATE_COLS:
        return "dateTime", "type date"
    if s.dtype == bool or set(s.dropna().astype(str).unique()) <= {"True", "False"} and s.dtype == object:
        return "boolean", "type logical"
    if pd.api.types.is_integer_dtype(s):
        return "int64", "Int64.Type"
    if pd.api.types.is_float_dtype(s):
        return "double", "type number"
    return "string", "type text"


def table_tmdl(table: str) -> str:
    df = pd.read_csv(WH / f"{table}.csv", nrows=5000)
    is_fact = table.startswith("fact_") or table == "security_user_city"
    lines = [f"table {table}", f"\tlineageTag: {tag()}"]
    if table == "dim_date":
        lines.append("\tdataCategory: Time")
    if table == "security_user_city":
        lines.append("\tisHidden")
    lines.append("")
    mtypes, numeric = [], []
    for c in df.columns:
        dt, mt = col_type(table, c, df[c])
        mtypes.append(f'{{"{c}", {mt}}}')
        if dt in ("int64", "double", "boolean", "dateTime"):
            numeric.append(f'"{c}"')
        lines.append(f"\tcolumn {c}")
        lines.append(f"\t\tdataType: {dt}")
        if is_fact or c in HIDDEN_DIM_COLS:
            lines.append("\t\tisHidden")
        if table == "dim_date" and c == "date":
            lines.append("\t\tisKey")
        fmt = FORMATS.get((table, c)) or ("0" if dt == "int64" else "0.00" if dt == "double" else None)
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        lines.append(f"\t\tlineageTag: {tag()}")
        lines.append("\t\tsummarizeBy: none")
        lines.append(f"\t\tsourceColumn: {c}")
        if c == "planner_url":
            lines.append("\t\tdataCategory: WebUrl")
        if (table, c) in SORT_BY:
            lines.append(f"\t\tsortByColumn: {SORT_BY[(table, c)]}")
        if dt == "dateTime":
            lines.append("")
            lines.append("\t\tannotation UnderlyingDateTimeDataType = Date")
        lines.append("")
    m = (f'let\n    Source = Csv.Document(File.Contents(DataFolder & "{table}.csv"), [Delimiter = ",", Columns = {len(df.columns)}, '
         f'Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),\n'
         f'    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),\n'
         f'    Blanks = Table.ReplaceValue(Promoted, "", null, Replacer.ReplaceValue, {{{", ".join(numeric)}}}),\n'
         f'    Typed = Table.TransformColumnTypes(Blanks, {{{", ".join(mtypes)}}}, "en-US")\nin\n    Typed')
    lines += [f"\tpartition {table} = m", "\t\tmode: import", "\t\tsource =", indent(m, 4), "",
              "\tannotation PBI_ResultType = Table", ""]
    return "\n".join(lines)


def measures_tmdl() -> str:
    lines = ["table _Measures", f"\tlineageTag: {tag()}", ""]
    for folder, name, dax, fmt, desc in MEASURES:
        lines.append(f"\t/// {desc}")
        if "\n" in dax:
            lines.append(f"\tmeasure {q(name)} =")
            lines.append(indent(dax, 3))
        else:
            lines.append(f"\tmeasure {q(name)} = {dax}")
        lines.append(f"\t\tformatString: {fmt}")
        lines.append(f"\t\tdisplayFolder: {folder}")
        lines.append(f"\t\tlineageTag: {tag()}")
        lines.append("")
    lines += ["\tcolumn Value", "\t\tdataType: int64", "\t\tisHidden", f"\t\tlineageTag: {tag()}", "\t\tsummarizeBy: none",
              "\t\tisNameInferred", "\t\tsourceColumn: [Value]", "",
              "\tpartition _Measures = calculated", "\t\tmode: import", "\t\tsource = {0}", "",
              "\tannotation PBI_Id = measures", ""]
    return "\n".join(lines)


def whatif_tmdl() -> str:
    return "\n".join([
        "table 'Shortage Cost Ratio'", f"\tlineageTag: {tag()}", "",
        "\tcolumn 'Shortage Cost Ratio'", "\t\tdataType: double", "\t\tformatString: 0.00", f"\t\tlineageTag: {tag()}",
        "\t\tsummarizeBy: none", "\t\tsourceColumn: [Value]", "",
        "\tpartition 'Shortage Cost Ratio' = calculated", "\t\tmode: import", "\t\tsource = GENERATESERIES(0.25, 5, 0.25)", "",
        "\tannotation PBI_Id = whatif", ""])


def write_semantic_model() -> None:
    d = SM / "definition"
    if d.exists():  # keep .pbi (Power BI's local data cache) and other files Desktop adds
        shutil.rmtree(d)
    (d / "tables").mkdir(parents=True, exist_ok=True)
    (d / "roles").mkdir()
    (SM / "definition.pbism").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {}}, indent=2))
    (d / "database.tmdl").write_text("database\n\tcompatibilityLevel: 1600\n\n")
    all_tables = TABLES + ["_Measures", "Shortage Cost Ratio"]
    (d / "model.tmdl").write_text("\n".join([
        "model Model", "\tculture: en-US", "\tdefaultPowerBIDataSourceVersion: powerBI_V3", "\tsourceQueryCulture: en-US",
        "\tdataAccessOptions", "\t\tlegacyRedirects", "\t\treturnErrorValuesAsNull", "",
        "annotation __PBI_TimeIntelligenceEnabled = 0", "",
        'annotation PBI_QueryOrder = ["DataFolder",' + ",".join(f'"{t}"' for t in TABLES) + "]", "",
        *[f"ref table {q(t)}" for t in all_tables], ""]))
    folder = str(WH) + "\\"
    (d / "expressions.tmdl").write_text(
        f'expression DataFolder = "{folder}" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]\n'
        f"\tlineageTag: {tag()}\n\n\tannotation PBI_ResultType = Text\n\n")
    for t in TABLES:
        (d / "tables" / f"{t}.tmdl").write_text(table_tmdl(t))
    (d / "tables" / "_Measures.tmdl").write_text(measures_tmdl())
    (d / "tables" / "Shortage Cost Ratio.tmdl").write_text(whatif_tmdl())
    rel = []
    for f, c, dim in RELS:
        rel += [f"relationship {tag()}", f"\tfromColumn: {f}.{c}", f"\ttoColumn: {dim}.{c}", ""]
    (d / "relationships.tmdl").write_text("\n".join(rel))
    (d / "roles" / "City Manager.tmdl").write_text("\n".join([
        "/// Dynamic RLS: a signed-in manager sees only the cities mapped to their e-mail in security_user_city.",
        "role 'City Manager'", "\tmodelPermission: read", "",
        "\ttablePermission dim_series = [city] IN CALCULATETABLE ( VALUES ( security_user_city[city] ), "
        "security_user_city[user_email] = USERPRINCIPALNAME () )", ""]))
    (d / "roles" / "City 00 Manager (demo).tmdl").write_text("\n".join([
        "/// Static demo role: only City 00.",
        "role 'City 00 Manager (demo)'", "\tmodelPermission: read", "",
        "\ttablePermission dim_series = [city] = \"City 00\"", ""]))


# ----------------------------------------------------------------------------------------- PBIR report
def lit(v) -> dict:
    return {"expr": {"Literal": {"Value": v}}}


def M(name):  # measure field
    return {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": name}}, f"_Measures.{name}", name


def C(table, col):  # column field
    return {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col}}, f"{table}.{col}", col


def proj(f, display=None):
    field, ref, native = f
    p = {"field": field, "queryRef": ref, "nativeQueryRef": native}
    if display:
        p["displayName"] = display
    return p


def title_obj(text):
    return {"title": [{"properties": {"show": lit("true"), "text": lit(f"'{text}'")}}]}


def in_filter(name, table, col, values, how=None):
    flt = {"name": name, "field": C(table, col)[0], "type": "Categorical",
           "filter": {"Version": 2, "From": [{"Name": "t", "Entity": table, "Type": 0}],
                      "Where": [{"Condition": {"In": {
                          "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": col}}],
                          "Values": [[{"Literal": {"Value": v}}] for v in values]}}}]}}
    if how:
        flt["howCreated"] = how
    return flt


def topn_filter(name, table, col, measure, n):
    return {"name": name, "field": C(table, col)[0], "type": "TopN",
            "filter": {"Version": 2, "From": [
                {"Name": "subquery", "Expression": {"Subquery": {"Query": {
                    "Version": 2, "From": [{"Name": "d", "Entity": table, "Type": 0}, {"Name": "m", "Entity": "_Measures", "Type": 0}],
                    "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": col}, "Name": "field"}],
                    "OrderBy": [{"Direction": 2, "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": measure}}}],
                    "Top": n}}}, "Type": 2},
                {"Name": "d", "Entity": table, "Type": 0}],
                "Where": [{"Condition": {"In": {
                    "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": col}}],
                    "Table": {"SourceRef": {"Source": "subquery"}}}}}]}}


class Page:
    def __init__(self, name, display, width=1280, height=720, ptype=None, filters=None, binding=None, hidden=False):
        self.name, self.display, self.width, self.height = name, display, width, height
        self.ptype, self.filters, self.binding, self.hidden = ptype, filters or [], binding, hidden
        self.visuals = []

    def add(self, vtype, x, y, w, h, roles, title=None, objects=None, sort=None, filters=None, sync=None, vc_objects=None):
        n = f"{self.name}_v{len(self.visuals):02d}"
        visual = {"visualType": vtype, "query": {"queryState": {r: {"projections": [proj(f) for f in fs]} for r, fs in roles.items()}},
                  "drillFilterOtherVisuals": True}
        if sort:
            field, direction = sort
            visual["query"]["sortDefinition"] = {"sort": [{"field": field[0], "direction": direction}], "isDefaultSort": False}
        if objects:
            visual["objects"] = objects
        vco = dict(title_obj(title)) if title else {}
        if vc_objects:
            vco.update(vc_objects)
        if vco:
            visual["visualContainerObjects"] = vco
        if sync:
            visual["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
        v = {"$schema": f"{SCHEMA}/visualContainer/2.4.0/schema.json", "name": n,
             "position": {"x": x, "y": y, "z": len(self.visuals) * 1000, "width": w, "height": h, "tabOrder": len(self.visuals) * 1000},
             "visual": visual}
        if filters:
            v["filterConfig"] = {"filters": filters}
        self.visuals.append(v)
        return self

    def card(self, x, y, w, h, measure, title):
        return self.add("card", x, y, w, h, {"Values": [M(measure)]}, title=title,
                        objects={"labels": [{"properties": {"labelDisplayUnits": lit("1D")}}]})

    def slicer(self, x, y, w, h, field, title, sync=None, single=False, dropdown=True, default=None):
        objs = {"data": [{"properties": {"mode": lit("'Dropdown'" if dropdown else "'Basic'")}}],
                "header": [{"properties": {"show": lit("false")}}]}
        if single:
            objs["selection"] = [{"properties": {"strictSingleSelect": lit("true")}}]
        if default is not None:  # pre-selected value, e.g. "'Equal costs'" or "1D"
            table, col = field[0]["Column"]["Expression"]["SourceRef"]["Entity"], field[0]["Column"]["Property"]
            objs["general"] = [{"properties": {"filter": {"filter": in_filter("x", table, col, [default])["filter"]}}}]
        return self.add("slicer", x, y, w, h, {"Values": [field]}, title=title, objects=objs, sync=sync)

    def write(self, root: Path):
        p = root / self.name
        (p / "visuals").mkdir(parents=True)
        page = {"$schema": f"{SCHEMA}/page/2.0.0/schema.json", "name": self.name, "displayName": self.display,
                "displayOption": "FitToPage", "height": self.height, "width": self.width}
        if self.filters:
            page["filterConfig"] = {"filters": self.filters}
        if self.ptype:
            page["type"] = self.ptype
        if self.binding:
            page["pageBinding"] = self.binding
        if self.hidden:
            page["visibility"] = "HiddenInViewMode"
        (p / "page.json").write_text(json.dumps(page, indent=2))
        for v in self.visuals:
            (p / "visuals" / v["name"]).mkdir()
            (p / "visuals" / v["name"] / "visual.json").write_text(json.dumps(v, indent=2))


FINAL = "'final (held out)'"
NO_TOTALS = {"total": [{"properties": {"totals": lit("false")}}]}
HEATMAP = {"values": [{"properties": {"backColor": {"solid": {"color": {"expr": {"FillRule": {
    "Input": M("Stockout Rate %")[0],
    "FillRule": {"linearGradient2": {"min": {"color": {"Literal": {"Value": "'#f3f8fe'"}}},
                                     "max": {"color": {"Literal": {"Value": "'#5598e7'"}}},
                                     "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}}}}}}}}}},
    "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": "_Measures.Stockout Rate %"}}]}


def build_pages() -> list[Page]:
    final_filter = lambda n: [in_filter(n, "dim_date", "period", [FINAL])]
    tooltip_ref = {"visualTooltip": [{"properties": {"type": lit("'ReportPage'"), "section": lit("'tooltip_kpis'")}}]}

    p1 = Page("overview", "1 Executive overview", filters=final_filter("f_overview_period"))
    p1.slicer(20, 12, 230, 76, C("dim_series", "city"), "City", sync="city")
    p1.slicer(262, 12, 230, 76, C("dim_series", "category_l1"), "Category", sync="category")
    p1.slicer(504, 12, 260, 76, C("dim_scenario", "scenario_name"), "Cost scenario", sync="scenario", single=True, default="'Equal costs'")
    for i, (m, t) in enumerate([("Fill Rate %", "Fill rate (headline policy)"), ("Stockout Rate %", "Observed stockout rate"),
                                ("Forecast Accuracy %", "Forecast accuracy (1 - WAPE)"),
                                ("Cost Saving % vs Seasonal Naive", "Cost saving vs seasonal naive")]):
        p1.card(20 + i * 312, 96, 300, 116, m, t)
    p1.add("lineChart", 20, 228, 610, 476, {"Category": [C("dim_date", "date")],
                                             "Y": [M("Fill Rate %"), M("Fill Rate % (Seasonal Naive)")]},
           title="Daily fill rate: headline policy vs seasonal naive")
    p1.add("tableEx", 646, 228, 614, 476,
           {"Values": [C("dim_series", "store_product"), C("dim_series", "city"), C("dim_series", "category_l1"),
                       M("Total Cost"), M("Lost Sales (units)"), M("Leftover Units"), M("Stockout Hours")]},
           title="Top 10 problem store-products (highest cost)", sort=(M("Total Cost"), "Descending"),
           filters=[topn_filter("f_top10", "dim_series", "store_product", "Total Cost", 10)])

    p2 = Page("forecast", "2 Forecast accuracy", filters=final_filter("f_forecast_period"))
    p2.slicer(20, 12, 330, 76, C("dim_model", "model_name"), "Forecast model", sync="model", single=True)
    p2.slicer(362, 12, 230, 76, C("dim_series", "city"), "City", sync="city")
    p2.slicer(604, 12, 230, 76, C("dim_series", "category_l1"), "Category", sync="category")
    for i, (m, t) in enumerate([("Forecast Accuracy %", "Accuracy (1 - WAPE)"), ("Forecast Bias %", "Bias"),
                                ("q90 Coverage %", "q90 coverage (nominal 90%)"),
                                ("q25-q75 Band Coverage %", "q25-q75 coverage (nominal 50%)")]):
        p2.card(20 + i * 312, 96, 300, 116, m, t)
    p2.add("clusteredBarChart", 20, 228, 400, 476, {"Category": [C("dim_series", "category_l1")], "Y": [M("Forecast Accuracy %")]},
           title="Accuracy by category", sort=(M("Forecast Accuracy %"), "Descending"), vc_objects=tooltip_ref)
    p2.add("clusteredBarChart", 436, 228, 400, 476, {"Category": [C("dim_series", "city")], "Y": [M("Forecast Bias %")]},
           title="Bias by city", vc_objects=tooltip_ref)
    p2.add("lineChart", 852, 228, 408, 476, {"Category": [C("dim_date", "date")],
                                              "Y": [M("Forecast Actual Demand"), M("Forecast q50 (Scored Days)")]},
           title="Median forecast vs actual (scored days)")

    p3 = Page("stockouts", "3 Stockouts and service")
    p3.slicer(20, 12, 230, 76, C("dim_series", "city"), "City", sync="city")
    p3.slicer(262, 12, 230, 76, C("dim_series", "category_l1"), "Category", sync="category")
    p3.slicer(504, 12, 260, 76, C("dim_date", "period"), "Period", sync="period")
    for i, (m, t) in enumerate([("Stockout Rate %", "Stockout rate"), ("Stockout Hours", "Stockout hours"),
                                ("Full-Stock Day Share %", "Full-stock days (exact demand)"),
                                ("Lost Sales (units)", "Lost sales, final week (simulated)")]):
        p3.card(20 + i * 312, 96, 300, 116, m, t)
    p3.add("pivotTable", 20, 228, 520, 476, {"Rows": [C("dim_series", "city")], "Columns": [C("dim_date", "weekday_name")],
                                             "Values": [M("Stockout Rate %")]},
           title="Stockout rate: city x weekday (heatmap)", objects=HEATMAP)
    p3.add("lineChart", 556, 228, 704, 230, {"Category": [C("dim_date", "date")],
                                              "Y": [M("Stockout Rate %"), M("Stockout Rate % (7-Day Rolling)")]},
           title="Stockout rate trend with 7-day rolling average")
    p3.add("lineChart", 556, 474, 704, 230, {"Category": [C("dim_date", "date")],
                                              "Y": [M("Fill Rate %"), M("Fill Rate % (7-Day Rolling)")]},
           title="Fill rate trend, final week (headline policy)")

    p4 = Page("policy", "4 Policy comparison", filters=final_filter("f_policy_period"))
    p4.slicer(20, 12, 260, 76, C("dim_scenario", "scenario_name"), "Cost scenario", sync="scenario", single=True, default="'Equal costs'")
    p4.slicer(292, 12, 300, 76, C("Shortage Cost Ratio", "Shortage Cost Ratio"), "What-if: cost of a unit short / unit left over",
              single=True, default="1D")
    p4.add("scatterChart", 20, 96, 520, 300, {"Category": [C("dim_policy", "policy_name")], "X": [M("Fill Rate %")],
                                               "Y": [M("Mean Cost")]},
           title="Demo policies: cost vs fill rate (lower-right is better)",
           objects={"categoryLabels": [{"properties": {"show": lit("true")}}]})
    p4.add("tableEx", 556, 96, 704, 300,
           {"Values": [C("dim_policy", "policy_name"), M("Mean Cost"), M("Fill Rate %"),
                       M("Cost Saving % vs Seasonal Naive"), M("What-if Mean Cost"), M("What-if Rank")]},
           title="Demo policies (retrained on real history)", sort=(M("What-if Rank"), "Ascending"), objects=NO_TOTALS)
    matched = [in_filter("f_matched", "fact_paper_policy_results", "matched_cell", ["1L"])]
    p4.add("clusteredBarChart", 20, 412, 520, 292, {"Category": [C("fact_paper_policy_results", "policy")], "Y": [M("Paper Mean Cost")]},
           title="Paper: 9 policies, mean cost (matched cells)", sort=(M("Paper Mean Cost"), "Ascending"), filters=matched)
    p4.add("tableEx", 556, 412, 704, 292,
           {"Values": [C("fact_paper_policy_results", "policy"), C("fact_paper_policy_results", "population"),
                       M("Paper Mean Cost"), M("Paper Fill Rate %"), M("Paper Saving % vs Seasonal Naive"), M("Paper What-if Mean Cost")]},
           title="Paper results (run E, simulated stockouts, matched cells)", sort=(M("Paper Mean Cost"), "Ascending"), objects=NO_TOTALS,
           filters=[in_filter("f_matched2", "fact_paper_policy_results", "matched_cell", ["1L"])])

    p5 = Page("detail", "5 Store-product detail", ptype="Drillthrough",
              binding={"name": "detail_binding", "type": "Drillthrough",
                       "parameters": [{"name": "p_store_product", "boundFilter": "f_drill",
                                       "fieldExpr": C("dim_series", "store_product")[0]}]},
              filters=[{"name": "f_drill", "field": C("dim_series", "store_product")[0], "type": "Categorical",
                        "howCreated": "Drillthrough"}])
    for i, (m, t) in enumerate([("Fill Rate %", "Fill rate (final week)"), ("Stockout Rate %", "Stockout rate (97 days)"),
                                ("Forecast Accuracy %", "Forecast accuracy (final week)"), ("Lost Sales (units)", "Lost sales (simulated)")]):
        p5.card(20 + i * 312, 16, 300, 110, m, t)
    p5.add("lineChart", 20, 142, 820, 340, {"Category": [C("dim_date", "date")],
                                             "Y": [M("Units Sold"), M("Forecast q25"), M("Forecast q50"), M("Forecast q90")]},
           title="Units sold vs forecast band (q25 / q50 / q90)")
    p5.add("tableEx", 856, 142, 404, 340, {"Values": [C("dim_series", "store_product"), C("dim_series", "category_l1"),
                                                      C("dim_series", "sales_tier"), C("dim_series", "stockout_tier"),
                                                      C("dim_series", "planner_url")]},
           title="Open this store-product in the planner app")
    p5.add("tableEx", 20, 498, 1240, 206, {"Values": [C("dim_date", "date"), M("Order Qty"), M("Order Demand"), M("Sold Units"),
                                                      M("Lost Sales (units)"), M("Leftover Units"), M("Total Cost")]},
           title="Final-week orders (headline policy, selected scenario)", filters=final_filter("f_detail_period"))

    p6 = Page("tooltip_kpis", "Tooltip KPIs", width=320, height=240, ptype="Tooltip", hidden=True,
              binding={"name": "tooltip_binding", "type": "Tooltip"})
    p6.card(8, 8, 304, 72, "Forecast Accuracy %", "Accuracy")
    p6.card(8, 84, 304, 72, "Fill Rate %", "Fill rate")
    p6.card(8, 160, 304, 72, "Stockout Rate %", "Stockout rate")
    return [p1, p2, p3, p4, p5, p6]


THEME = {
    "name": "Stockout Planner",
    "dataColors": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
    "background": "#FFFFFF", "foreground": "#0b0b0b", "tableAccent": "#2a78d6",
    "good": "#1baf7a", "neutral": "#eda100", "bad": "#e34948",
    "textClasses": {"title": {"fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#0b0b0b"},
                    "label": {"fontFace": "Segoe UI", "fontSize": 10, "color": "#52514e"},
                    "callout": {"fontFace": "Segoe UI Semibold", "fontSize": 28, "color": "#0b0b0b"}},
    "visualStyles": {"*": {"*": {"border": [{"show": True, "color": {"solid": {"color": "#e6e5e0"}}, "radius": 6}],
                                 "background": [{"show": True, "transparency": 0}]}}},
}


def write_report() -> None:
    d = RP / "definition"
    if d.exists():
        shutil.rmtree(d)
    (d / "pages").mkdir(parents=True)
    res = RP / "StaticResources" / "RegisteredResources"
    res.mkdir(parents=True, exist_ok=True)
    (res / "StockoutTheme.json").write_text(json.dumps(THEME, indent=2))
    (HERE / "theme.json").write_text(json.dumps(THEME, indent=2))
    (RP / "definition.pbir").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}}}, indent=2))
    (d / "version.json").write_text(json.dumps({"$schema": f"{SCHEMA}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"}, indent=2))
    (d / "report.json").write_text(json.dumps({
        "$schema": f"{SCHEMA}/report/3.0.0/schema.json",
        "themeCollection": {"customTheme": {"name": "StockoutTheme.json", "reportVersionAtImport": {"visual": "2.4.0", "report": "3.0.0", "page": "2.0.0"},
                                            "type": "RegisteredResources"}},
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources",
                              "items": [{"name": "StockoutTheme.json", "path": "StockoutTheme.json", "type": "CustomTheme"}]}],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized",
                     "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True, "useEnhancedTooltips": True},
    }, indent=2))
    pages = build_pages()
    (d / "pages" / "pages.json").write_text(json.dumps({"$schema": f"{SCHEMA}/pagesMetadata/1.0.0/schema.json",
                                                         "pageOrder": [p.name for p in pages], "activePageName": pages[0].name}, indent=2))
    for p in pages:
        p.write(d / "pages")
    (HERE / f"{NAME}.pbip").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": f"{NAME}.Report"}}], "settings": {"enableAutoRecovery": True}}, indent=2))


def write_security_table() -> None:
    cities = sorted(pd.read_csv(WH / "dim_series.csv").city.unique())
    rows = [{"user_email": f"manager.{c.lower().replace(' ', '')}@example.com", "city": c} for c in cities]
    rows.append({"user_email": "regional.north@example.com", "city": cities[0]})
    rows.append({"user_email": "regional.north@example.com", "city": cities[1]})
    pd.DataFrame(rows).to_csv(WH / "security_user_city.csv", index=False)


if __name__ == "__main__":
    write_security_table()
    write_semantic_model()
    write_report()
    print(f"wrote {HERE / (NAME + '.pbip')}")
