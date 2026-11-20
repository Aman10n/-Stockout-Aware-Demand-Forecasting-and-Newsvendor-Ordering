"""All text, tables and figures of the project report. Every number here comes from the saved project artefacts
(results/, planner/output/, paper/tables/) or from checks re-run for this report (report/assets/checks.json)."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
A = HERE / "assets"
RE = ROOT / "results/phase0_9_5k"
RS = ROOT / "results/phase0_4/demo5000"
PBI = ROOT / "planner/powerbi/screenshots"

REFERENCES = [
    ("Y. Wang, J. Gu, L. Long, X. Li, L. Shen, Z. Fu, X. Zhou and X. Jiang", "FreshRetailNet-50K: a stockout-annotated censored demand dataset for latent demand recovery and forecasting in fresh retail", "arXiv:2505.16319v5 [cs.LG]", "2025"),
    ("Dingdong-Inc", "FreshRetailNet-50K (dataset card, data version 1.0)", "Hugging Face, huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K", "2025"),
    ("Dingdong-Inc", "frn-50k-baseline (commit 8af694a)", "GitHub repository, github.com/Dingdong-Inc/frn-50k-baseline", "2026"),
    ("R. Fildes, S. Ma and S. Kolassa", "Retail forecasting: research and practice", "International Journal of Forecasting, vol. 38, no. 4, pp. 1283–1318", "2022"),
    ("S. Nahmias", "Demand estimation in lost sales inventory systems", "Naval Research Logistics, vol. 41, no. 6, pp. 739–757", "1994"),
    ("W. T. Huh, R. Levi, P. Rusmevichientong and J. B. Orlin", "Adaptive data-driven inventory control with censored demand based on Kaplan–Meier estimator", "Operations Research, vol. 59, no. 4, pp. 929–941", "2011"),
    ("E. L. Kaplan and P. Meier", "Nonparametric estimation from incomplete observations", "Journal of the American Statistical Association, vol. 53, no. 282, pp. 457–481", "1958"),
    ("O. Besbes and A. Muharremoglu", "On implications of demand censoring in the newsvendor problem", "Management Science, vol. 59, no. 6, pp. 1407–1424", "2013"),
    ("A.-L. Sachs and S. Minner", "The data-driven newsvendor with censored demand observations", "International Journal of Production Economics, vol. 149, pp. 28–36", "2014"),
    ("R. Kumar and O. Mouchtaki", "What is the value of censored data? An exact analysis for the data-driven newsvendor", "arXiv:2602.16842 [cs.LG]", "2026"),
    ("G.-Y. Ban and C. Rudin", "The big data newsvendor: practical insights from machine learning", "Operations Research, vol. 67, no. 1, pp. 90–108", "2019"),
    ("D. Bertsimas and N. Kallus", "From predictive to prescriptive analytics", "Management Science, vol. 66, no. 3, pp. 1025–1044", "2020"),
    ("A. Oroojlooyjadid, L. V. Snyder and M. Takáč", "Applying deep learning to the newsvendor problem", "IISE Transactions, vol. 52, no. 4, pp. 444–463", "2020"),
    ("R. Koenker and G. Bassett, Jr.", "Regression quantiles", "Econometrica, vol. 46, no. 1, pp. 33–50", "1978"),
    ("G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye and T.-Y. Liu", "LightGBM: a highly efficient gradient boosting decision tree", "Advances in Neural Information Processing Systems (NeurIPS), vol. 30", "2017"),
    ("S. Makridakis, E. Spiliotis and V. Assimakopoulos", "M5 accuracy competition: results, findings, and conclusions", "International Journal of Forecasting, vol. 38, no. 4, pp. 1346–1364", "2022"),
    ("A. Zeng, M. Chen, L. Zhang and Q. Xu", "Are transformers effective for time series forecasting?", "Proc. AAAI Conf. on Artificial Intelligence, vol. 37, no. 9, pp. 11121–11128", "2023"),
    ("H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang and M. Long", "TimesNet: temporal 2D-variation modeling for general time series analysis", "Int. Conf. on Learning Representations (ICLR)", "2023"),
    ("B. Lim, S. Ö. Arık, N. Loeff and T. Pfister", "Temporal fusion transformers for interpretable multi-horizon time series forecasting", "International Journal of Forecasting, vol. 37, no. 4, pp. 1748–1764", "2021"),
    ("Y. Romano, E. Patterson and E. Candès", "Conformalized quantile regression", "Advances in Neural Information Processing Systems (NeurIPS), vol. 32", "2019"),
    ("I. Gibbs and E. Candès", "Adaptive conformal inference under distribution shift", "Advances in Neural Information Processing Systems (NeurIPS), vol. 34", "2021"),
    ("V. Chernozhukov, I. Fernández-Val and A. Galichon", "Quantile and probability curves without crossing", "Econometrica, vol. 78, no. 3, pp. 1093–1125", "2010"),
    ("J. Cao", "A conformal approach to feature-based newsvendor under model misspecification", "arXiv:2412.13159 [cs.LG]", "2024"),
    ("R. F. Barber, E. J. Candès, A. Ramdas and R. J. Tibshirani", "Conformal prediction beyond exchangeability", "Annals of Statistics, vol. 51, no. 2", "2023"),
    ("J. Azar", "A reproducible, leakage-free pipeline for censored demand forecasting and inventory optimization on FreshRetailNet-50K", "Inventions, vol. 11, no. 5, art. no. 89", "2026"),
    ("D. O. Lebedev and A. A. Romanov", "Stockout-aware segmentation and model routing for daily store-SKU demand forecasting", "Proc. Int. Russian Smart Industry Conf. (SmartIndustryCon), pp. 768–774", "2026"),
    ("B. Szabłowski", "One global model, many behaviors: stockout-aware feature engineering and dynamic scaling for multi-horizon retail demand forecasting with a cost-aware ordering policy (VN2 winner report)", "arXiv:2601.18919 [cs.LG]", "2026"),
    ("B. Efron", "Bootstrap methods: another look at the jackknife", "Annals of Statistics, vol. 7, no. 1, pp. 1–26", "1979"),
]

SYMBOLS = [
    ("FRN-50K", "FreshRetailNet-50K dataset (Dingdong-Inc)"),
    ("SKU", "Stock-keeping unit (product)"),
    ("ML", "Machine Learning"),
    ("LightGBM", "Light Gradient Boosting Machine"),
    ("GBDT", "Gradient-Boosted Decision Trees"),
    ("TFT", "Temporal Fusion Transformer"),
    ("KM", "Kaplan–Meier estimator"),
    ("CQR", "Conformalized Quantile Regression"),
    ("WAPE", "Weighted Absolute Percentage Error"),
    ("RLS", "Row-Level Security (Power BI)"),
    ("DAX", "Data Analysis Expressions (Power BI formula language)"),
    ("PBIP / TMDL", "Power BI Project format / Tabular Model Definition Language"),
    ("SHAP", "SHapley Additive exPlanations (TreeSHAP feature contributions)"),
    ("RSS", "Resident Set Size (peak process memory)"),
    ("Donor day", "Series-day with no flagged stockout hour between 06:00 and 21:59; its sales equal demand"),
    ("A / B / C", "Simulated stockout mechanisms: ordinary depletion / promotion-sensitive / sustained scarcity"),
    ("Run S / P / E", "Saved runs: 5,000-series Phases 0–4 / 50,000-series Phases 0–4 / 5,000-series Phases 0–9"),
    ("D^proxy", "Donor-day demand proxy: recorded sales over the 06:00–21:59 window"),
    ("τ", "Quantile level (0.25, 0.50, 0.75, 0.90)"),
    ("q25 … q90", "Forecast quantiles at τ = 0.25, 0.50, 0.75, 0.90"),
    ("c_u, c_o", "Cost of one unit short (underage) and of one unit left over (overage)"),
    ("β", "Critical ratio c_u / (c_u + c_o); the newsvendor orders the β-quantile"),
    ("Q", "Order quantity (opening stock) for a store-product-day"),
    ("Δ", "Transfer gap: mean cost on an unseen history minus matched cost on the same rows"),
    ("L_miss", "Definite-miss lower bound for the q90 forecast on real censored rows"),
]


def build_content(R):
    # ============================================================================== CHAPTER 1
    R.chapter("Introduction")
    R.h2("1.1", "General")
    R.p("Retailers record **sales**, not **demand**. When a product sells out, every customer who arrives afterwards "
        "leaves without buying and leaves no trace in the data. A forecasting model fitted to such records therefore "
        "learns the store's past stocking policy along with customer behaviour, and in fresh retail its errors flow "
        "straight into the next morning's order. Fresh products have a shelf life of about one day, so every order is a "
        "trade-off between two costs: a lost sale when too little is stocked and a unit of waste when too much is stocked.")
    R.p("The problem is large in practice. In the 5,000 store-product series studied in this project, drawn from the "
        "public **FreshRetailNet-50K** dataset [1], [2], **44.0%** of all store-product-days (213,240 of 485,000) have at least one "
        "hour between 06:00 and 21:59 in which the shelf was empty. On those days recorded sales are only a lower bound on "
        "demand. Only the remaining **56.0%** of days, called *donor days* in this report, give an exact view of demand, and "
        "they are not a random sample: they are quieter days with fewer promotions.")
    R.p("FreshRetailNet-50K is unusual because it stores an **hourly stock-status flag** next to hourly sales for 50,000 "
        "(city, store, product) series. This makes a controlled experiment possible. Sales on donor days can be hidden "
        "with simulated stockouts, models can be trained on the censored history, and every forecast and every order can "
        "then be scored against the true, uncensored demand of the same rows. This project builds that experiment end to "
        "end, from the raw Parquet files to a locked final evaluation, and turns the trained models into tools that a "
        "supply planner can use: an interactive order planner, a Power BI management report and a 3D simulator.")
    R.h2("1.2", "Purpose")
    R.p("The purpose of the project is to find out, with a fair and reproducible protocol, **which forecasting and "
        "ordering policy gives the lowest newsvendor cost when demand is censored by stockouts**, and how much that "
        "answer depends on the cost of a shortage relative to the cost of waste and on the way the training history was "
        "censored. The second purpose is practical: to package the best-performing pipeline as decision-support software "
        "that recommends an order quantity for each store-product-day, explains the forecast, and reports service, waste "
        "and cost at network level.")
    R.h2("1.3", "Scope")
    R.p("The project covers the complete path from data to decisions:")
    R.bullets([
        "**Data engineering:** reading 4,500,000 training rows and 350,000 evaluation rows of hourly sales and stock "
        "status, verifying them against recorded SHA-256 hashes, and building a stratified sample of 5,000 series.",
        "**Censoring simulation:** three stockout mechanisms (A ordinary depletion, B promotion-sensitive, C sustained "
        "scarcity) that hide part of the demand on donor days, calibrated to real fit-period stockout patterns.",
        "**Modelling:** a seasonal-naive rule, LightGBM point and quantile models trained on recorded sales, LightGBM "
        "demand-quantile models trained on the donor proxy, TimesNet recovery of hidden hours with a Temporal Fusion "
        "Transformer (TFT) forecaster, and a Kaplan–Meier order-percentile baseline.",
        "**Calibration and ordering:** pooled conformal calibration of the quantiles, nine newsvendor ordering policies "
        "and three cost settings, all fixed in a protocol lock before the final week was scored.",
        "**Evaluation:** mean newsvendor cost, fill rate, leftover share, WAPE, quantile coverage and pinball loss on "
        "20,641 exact donor rows, a 3 × 3 train/test transfer matrix, paired cluster-bootstrap intervals, and a lower "
        "bound on forecast misses for real censored days.",
        "**Decision support:** a Streamlit order planner with live model scoring and SHAP explanations, a Power BI report "
        "with 51 DAX measures and row-level security on a star-schema warehouse, an optional PostgreSQL load with "
        "validation checks, and a 3D web simulator whose JavaScript engine reproduces the Python models exactly.",
        "**Documentation:** executed notebooks, saved run artefacts and an IEEE-format research paper whose tables are "
        "regenerated from the saved results.",
    ])
    R.p("The study is an offline evaluation on one public dataset. Live deployment at a retailer, price-based profit "
        "(the data has no prices), multi-day shelf life and the design of replenishment contracts are outside its scope.")
    R.h2("1.4", "Motivation")
    R.p("Three observations motivated the project. First, a lower forecast error does not show that one ordering policy "
        "is better than another: what matters to a store is the cost of the order, and that depends on the cost ratio "
        "and on which side of demand the forecast errs. Second, most published comparisons score forecasts against "
        "recorded sales, which are themselves censored, so the bias they measure cannot be separated from the bias of "
        "the data. Third, models are rarely tested on a history censored differently from the one they were trained "
        "on, although stocking policies change between stores and over time. A fair comparison needs the same outcome, "
        "the same cost ratio and the same scored rows for every policy; FreshRetailNet-50K makes that possible.")
    R.h2("1.5", "Problem Statement")
    R.p("Given the hourly sales, hourly stock status, promotion, holiday and weather records of fresh-retail "
        "store-product series up to day *t* − 1, forecast the demand distribution for day *t* over the 06:00–21:59 "
        "window and place the order *Q* that minimises the newsvendor cost *c_o*·max(*Q* − *D*, 0) + *c_u*·max(*D* − *Q*, 0), "
        "where demand *D* is not observed on days with a stockout. In addition, (i) compare policies on identical rows "
        "where demand is known exactly, (ii) measure how much the cost of a policy changes when it is trained on one "
        "censoring mechanism and applied to another, (iii) bound the forecast miss rate on real censored days, and "
        "(iv) deliver the recommended orders and their explanation to planners and managers.")
    R.h2("1.6", "Objectives")
    R.numbers([
        "To build a leakage-free pipeline on FreshRetailNet-50K in which every feature for day *t* uses only days "
        "before *t*, with a chronological split into fit, tuning, calibration and final days.",
        "To simulate three stockout mechanisms on donor days so that models trained on differently censored "
        "histories can be scored against the same uncensored outcomes.",
        "To train and compare conventional baselines, LightGBM demand-quantile models, TimesNet/TFT and "
        "Kaplan–Meier policies, and to calibrate the quantiles with pooled conformal residuals.",
        "To evaluate nine newsvendor ordering policies under three cost ratios on a final week that is used once, "
        "after a protocol lock, with paired cluster-bootstrap intervals.",
        "To quantify the transfer gap between censoring mechanisms and a definite-miss lower bound on real censored days.",
        "To deliver the trained models as an interactive Streamlit planner, a Power BI report on a star-schema "
        "warehouse and a 3D simulator, with automated checks that the delivered numbers match the pipeline.",
        "To document the work as an IEEE-format research paper and a reproducible repository.",
    ])
    R.h2("1.7", "Introduction to Gradient Boosting, LightGBM and Quantile Regression")
    R.p("A **decision tree** predicts by asking a sequence of questions about the inputs, for example “were yesterday's "
        "sales above 4.5 units?”, and returning the value stored in the leaf it reaches. **Gradient boosting** builds "
        "an ensemble of such trees one after another; each new tree is fitted to the gradient of the loss left by the "
        "trees so far, so the ensemble corrects its own errors step by step, and the prediction is the sum of all trees.")
    R.p("**LightGBM** [15] is a fast implementation of gradient-boosted decision trees. It bins continuous features "
        "into histograms, grows trees leaf-wise, handles missing values by learning a default direction at each split "
        "and treats integer identifiers such as city, store and product as native categorical features. Tree "
        "ensembles of this kind dominated the M5 retail forecasting competition [16], and simple models often match "
        "transformer forecasters on such data [17], which is why LightGBM is the main model family in this project.")
    R.p("**Quantile regression** [14] estimates a chosen quantile of the target instead of its mean. For a quantile "
        "level τ it minimises the pinball loss, which charges τ per unit of under-prediction and (1 − τ) per unit of "
        "over-prediction:")
    R.eq("ρ_τ(y, q) = τ · max(y − q, 0) + (1 − τ) · max(q − y, 0)")
    R.p("LightGBM supports this loss directly (objective = quantile), so one model is trained for each level "
        "τ ∈ {0.25, 0.50, 0.75, 0.90}. The newsvendor result in Section 1.8 shows why quantiles, rather than a mean "
        "forecast, are what an ordering decision needs.")
    R.h3("1.7.1", "Advantages of LightGBM for this problem")
    R.bullets([
        "Captures non-linear effects and interactions, for example a recent stockout mattering more for a "
        "high-selling product than for a slow one.",
        "Works on mixed numeric and categorical inputs without scaling, and tolerates missing lags early in a series.",
        "Trains 4,008 trees across nine boosters in about two minutes on a laptop for the 5,000-series planner.",
        "Gives exact per-feature contributions (TreeSHAP) through `predict(..., pred_contrib=True)`, which the "
        "planner app and the 3D simulator display for every forecast.",
    ])
    R.h3("1.7.2", "Challenges")
    R.bullets([
        "Separate quantile models can cross (q50 above q75); this is removed by sorting each row's quantiles "
        "(monotone rearrangement [22]).",
        "Quantile models trained on censored sales inherit the censoring bias; training on donor days removes the "
        "bias but uses a selected sample.",
        "Hyperparameters must be chosen without touching calibration or final days, which the chronological split enforces.",
    ])
    R.h2("1.8", "Introduction to the Newsvendor Model and Conformal Calibration")
    R.p("The **newsvendor model** describes a single-period stocking decision for a perishable product. If each unit "
        "short costs *c_u* (a lost margin) and each unit left over costs *c_o* (waste), the expected cost of ordering *Q* "
        "units is minimised by ordering the β-quantile of the demand distribution, where")
    R.eq("β = c_u / (c_u + c_o)")
    R.p("When a shortage is three times as costly as waste (*c_u* = 3, *c_o* = 1) the optimal order is the 75th percentile "
        "of demand; when waste is three times as costly it is the 25th percentile; at equal costs it is the median. "
        "@fig:newsvendor illustrates this for a hypothetical demand distribution. Because the order is a quantile, a "
        "forecast that is too low in its upper quantiles is costly exactly when shortages are expensive.")
    R.fig("newsvendor", A / "diagrams/fig_newsvendor.png", "Expected newsvendor cost for three cost ratios; each minimum lies at the β-quantile (illustration)", width=14)
    R.p("**Conformal calibration** [20] corrects a quantile forecast with residuals from a held-out calibration "
        "window. If *r*₁ ≤ … ≤ *r*ₙ are the sorted calibration residuals (actual minus forecast) for level τ, the "
        "calibrated forecast adds the order statistic *r*₍⌈(n+1)τ⌉₎. Under exchangeability this gives at least the "
        "nominal coverage on new data; real retail data are not exchangeable [24], so in this project coverage is "
        "measured rather than assumed. Residuals are **pooled** within groups of similar series (category × sales tier, "
        "falling back to coarser pools) so that each correction is estimated from at least 200 rows.")
    R.h2("1.9", "Organisation of the Report")
    R.p("Chapter 2 reviews related work on censored demand, retail forecasting, calibration and FreshRetailNet-50K, "
        "and identifies the research gap. Chapter 3 analyses the requirements of the system and Chapter 4 presents its "
        "design. Chapter 5 describes the methodology: data, donor days, the chronological split, features, simulated "
        "censoring, models, calibration, ordering and metrics. Chapter 6 describes how the system was tested. "
        "Chapter 7 reports the experimental results and the three decision-support front ends with screenshots. "
        "Chapter 8 concludes the report, Chapter 9 outlines future enhancements and Chapter 10 lists the references, "
        "followed by an appendix with key source code.")

    # ============================================================================== CHAPTER 2
    R.chapter("Literature Survey")
    R.p("This chapter reviews the work most closely related to the project in four groups: censored demand and the "
        "newsvendor problem, machine learning for retail forecasting and ordering, calibration of quantile forecasts, "
        "and earlier studies on FreshRetailNet-50K and stockout-aware forecasting.")
    R.h2("2.1", "Censored Demand and the Newsvendor Problem")
    R.p("**Demand estimation in lost sales inventory systems [5].** Nahmias studies how to estimate the parameters "
        "of a demand distribution when only sales, capped by stock, are observed. The approach is parametric: a "
        "distribution family is assumed and fitted to the censored observations. It establishes that ignoring "
        "censoring biases demand estimates downwards.")
    R.p("**Adaptive data-driven inventory control with censored demand based on the Kaplan–Meier estimator [6].** "
        "Huh et al. avoid a parametric assumption by estimating the demand distribution with the Kaplan–Meier "
        "product-limit estimator [7], treating stockout days as right-censored observations, and prove that the "
        "resulting order levels converge to the optimum. The Kaplan–Meier baseline of this project follows this route, "
        "estimating an order percentile within pools of similar series.")
    R.p("**On implications of demand censoring in the newsvendor problem [8].** Besbes and Muharremoglu analyse "
        "what censoring hides about the optimal order and show that the loss from censoring is concentrated in the "
        "upper tail. **The data-driven newsvendor with censored demand observations [9]** by Sachs and Minner adapts "
        "the data-driven newsvendor to censored samples. **What is the value of censored data? [10]** by Kumar and "
        "Mouchtaki gives an exact analysis showing that treating sales as demand can degrade badly as censored data "
        "accumulate. These results predict that the cost of censoring depends on the targeted quantile, which this "
        "project tests empirically.")
    R.h2("2.2", "Machine Learning for Retail Forecasting and Ordering")
    R.p("**Retail forecasting: research and practice [4].** Fildes, Ma and Kolassa review retail forecasting and "
        "note that unrecorded lost sales are a long-standing source of bias. **LightGBM [15]** introduced "
        "histogram-based, leaf-wise gradient boosting; the **M5 accuracy competition [16]** found that practically all "
        "of the top 50 entries used LightGBM, and **Zeng et al. [17]** showed that simple models often match transformer "
        "forecasters. **TimesNet [18]** models time series as 2D variations and is used by the FreshRetailNet-50K "
        "authors for demand recovery; the **Temporal Fusion Transformer [19]** is an attention-based multi-horizon "
        "forecaster.")
    R.p("Feature-based newsvendor methods learn orders directly from covariates: **Ban and Rudin [11]** with "
        "empirical risk minimisation, **Bertsimas and Kallus [12]** with prescriptive weights, and "
        "**Oroojlooyjadid et al. [13]** with deep networks. With linear costs the optimal order is a quantile, which "
        "links ordering to quantile regression [14] and justifies ordering from calibrated quantile forecasts.")
    R.h2("2.3", "Calibration of Quantile Forecasts")
    R.p("**Conformalized quantile regression [20]** adds a residual quantile from a calibration set to each "
        "quantile forecast and guarantees marginal coverage under exchangeability. **Adaptive conformal inference "
        "[21]** updates the correction online to cope with distribution shift; this project includes it as a "
        "sensitivity analysis. **Chernozhukov et al. [22]** show that sorting crossed quantile curves (monotone "
        "rearrangement) can only reduce error. **Cao [23]** applies conformal calibration to the feature-based "
        "newsvendor, and **Barber et al. [24]** bound the coverage loss when exchangeability fails — the situation on "
        "real censored days, where no coverage guarantee is available.")
    R.h2("2.4", "Studies on FreshRetailNet-50K and Stockout-Aware Forecasting")
    R.p("**FreshRetailNet-50K [1], [2].** Wang et al. release 50,000 store-product series with hourly sales and "
        "stock-status flags and evaluate demand recovery on synthetically masked non-stockout periods with an "
        "official baseline [3]; in this project that baseline could be reproduced only in part. **Azar [25]** builds a "
        "leakage-free pipeline on the same dataset and selects newsvendor policies, but scores profit on censored "
        "sales, whose bias relative to demand cannot be identified. **Lebedev and Romanov [26]** route store-SKU "
        "series to different models by stockout segment and exclude out-of-stock days from training and evaluation. "
        "**Szabłowski [27]** feeds a global stockout-aware forecaster into a cost-aware ordering rule (VN2 competition).")
    R.h2("2.5", "Summary and Research Gap")
    R.tab("related", "Summary of related work", ["S.No.", "Work", "Outcome used for scoring", "Varies censoring\nmechanism", "Scores ordering\ncost", "Calibrated\nquantiles"], [
        ("1", "Huh et al. (2011) [6]", "Theory / simulation", "No", "Yes", "No"),
        ("2", "Wang et al. (2025) [1]", "Masked non-stockout hours", "No (one masking rule)", "No", "No"),
        ("3", "Cao (2024) [23]", "Simulated demand", "No", "Yes", "Conformal"),
        ("4", "Azar (2026) [25]", "Censored sales", "No", "Yes (profit)", "No"),
        ("5", "Lebedev & Romanov (2026) [26]", "In-stock days only", "No", "No", "No"),
        ("6", "Szabłowski (2026) [27]", "Competition sales", "No", "Yes", "No"),
        ("7", "**This project**", "**Exact donor-day demand**", "**Yes (A, B, C; 3 × 3 cells)**", "**Yes (9 policies, 3 cost ratios)**", "**Pooled conformal**"),
    ], [1.1, 3.6, 3.4, 2.4, 2.4, 2.1], ["center", "left", "left", "center", "center", "center"], size=9.5)
    R.p("No study identified in this survey scores orders against an uncensored outcome while varying the censoring "
        "mechanism. Classical work provides theory for censored newsvendors, the dataset report provides recovery "
        "metrics, and the applied pipelines either score on censored sales or drop stockout days. This project closes "
        "the gap with a controlled design: donor days give the uncensored outcome, three simulated mechanisms give "
        "differently censored training histories, and nine locked policies are compared on identical rows.")

    # ============================================================================== CHAPTER 3
    R.chapter("System Analysis")
    R.h2("3.1", "Issues in the Existing System")
    R.p("In a typical fresh-retail store the next day's order is set by a simple rule — often “order what sold on the "
        "same weekday last week” — or by a forecast fitted to recorded sales. The analysis of the data and of earlier "
        "work shows several weaknesses:")
    R.bullets([
        "**Sales are treated as demand:** on 44.0% of store-product-days the shelf was empty for at least one hour, so "
        "recorded sales understate demand and a model fitted to them learns the stocking policy.",
        "**Accuracy is used instead of cost:** a lower WAPE does not mean a cheaper order, because the cost depends on "
        "the cost ratio and on the side of demand on which the forecast errs.",
        "**Evaluation on censored outcomes:** scoring against recorded sales hides the bias that matters most.",
        "**Hidden leakage:** target-day weather, promotions or stock flags are easily included in features, inflating "
        "test accuracy beyond what is achievable the evening before.",
        "**No common rows:** policies that cannot predict every row are often compared on different subsets.",
        "**Uncalibrated uncertainty:** raw quantile forecasts under-cover, which leads to systematic shortages when "
        "a high quantile is ordered.",
        "**Results stay in notebooks:** planners and managers cannot inspect an order, its reasons or the network KPIs.",
    ])
    R.h2("3.2", "Proposed System")
    R.p("The proposed system defines the outcome as the 06:00–21:59 sales of donor days only, rebuilds every feature "
        "from the past, simulates three censoring mechanisms to create differently censored training histories, and "
        "scores nine locked ordering policies on the same 20,641 donor rows of a final week that is used once. Quantile "
        "forecasts are calibrated with pooled conformal residuals and turned into newsvendor orders at three cost "
        "ratios. The same protocol drives a decision-support pipeline whose outputs feed a star-schema warehouse, a "
        "Power BI report, a Streamlit order planner and a 3D simulator, with automated reconciliation checks between them.")
    R.h2("3.3", "Functional Requirements")
    R.tab("fr", "Functional requirements", ["ID", "Requirement"], [
        ("FR1", "Read train.parquet and eval.parquet in batches and verify them against the recorded SHA-256 hashes."),
        ("FR2", "Select a stratified sample of 5,000 series (first category × sales tier × stockout tier) using fit-period data only."),
        ("FR3", "Compute the 06:00–21:59 outcome, stockout hours and the donor flag for every series-day."),
        ("FR4", "Build 33 features per series-day from days before the target day only, and test this with a target-day perturbation test."),
        ("FR5", "Simulate stockout mechanisms A, B and C on eligible donor days and rebuild features from each censored history."),
        ("FR6", "Train seasonal-naive, LightGBM point/quantile, demand-quantile, TimesNet→TFT and Kaplan–Meier models with early stopping on tuning days."),
        ("FR7", "Calibrate quantiles with pooled conformal residuals from calibration days and remove quantile crossings."),
        ("FR8", "Compute newsvendor orders for β = 0.25, 0.50, 0.75 for nine policies, and write a protocol lock before scoring."),
        ("FR9", "Score cost, fill rate, leftover share, WAPE, coverage and pinball loss on donor rows; compute transfer gaps, bootstrap intervals and the definite-miss bound."),
        ("FR10", "Write a star-schema warehouse (CSV), optionally load it into PostgreSQL, and run validation checks."),
        ("FR11", "Provide a Power BI report with KPIs, drill-through, what-if cost ratio and row-level security by city."),
        ("FR12", "Provide a planner app that scores the saved models live for any store-product-day and explains the forecast, and a 3D simulator that replays the held-out week."),
    ], [1.6, 13.4], ["center", "left"], size=10)
    R.h2("3.4", "Non-Functional Requirements")
    R.numbers([
        "**Correctness (no leakage):** no feature may use information from the target day or later; calibration and "
        "final days must not influence training or model selection.",
        "**Reproducibility:** fixed seeds (20240628 for sampling, simulation and LightGBM; 42 in run E's provenance), "
        "deterministic LightGBM, recorded package versions and file hashes for every run.",
        "**Auditability:** every run writes manifests, phase gates and runtime/memory logs; the final protocol is locked "
        "by a SHA-256 digest before the final week is read.",
        "**Exactness of the front ends:** the JavaScript engine of the simulator must reproduce the Python features and "
        "booster scores, and the Power BI and Streamlit figures must match the pipeline.",
        "**Performance:** the planner pipeline must run on a laptop in minutes; the apps must respond interactively by "
        "loading saved models and tables.",
        "**Usability:** planners and managers must be able to use the tools through selections and sliders without writing code.",
        "**Security:** managers see only their own cities in Power BI through row-level security.",
    ])
    R.h2("3.5", "Hardware Requirements")
    R.tab("hw", "Hardware used for the experiments and the applications", ["Component", "Experiment runs (S, P, E)", "Local machine (apps, report)"], [
        ("Machine / OS", "Linux x86_64 (kernel 6.18)", "HP OMEN 16 laptop, Windows 11"),
        ("Processor", "2 logical CPUs", "AMD Ryzen 7 7840HS, 8 cores / 16 threads"),
        ("Memory", "8.42 GB RAM (peak use 6.11 GB in run P)", "16 GB RAM"),
        ("GPU", "None (all training on CPU)", "Not used by the pipeline"),
        ("Storage", "≈ 115 MB dataset + run outputs", "≈ 115 MB dataset + warehouse, models and apps"),
    ], [3.2, 5.9, 5.9], ["left", "left", "left"], size=10)
    R.h2("3.6", "Software Requirements")
    R.tab("sw", "Software stack", ["Software / library", "Version", "Purpose"], [
        ("Python", "3.11.15 (runs), 3.13 (apps)", "Programming language"),
        ("pandas / NumPy / PyArrow", "2.3.3 / 2.4.4 / 25.0.1", "Data loading, Parquet streaming, aggregation"),
        ("DuckDB", "1.5.5", "SQL over Parquet in the notebooks"),
        ("LightGBM", "4.7.0", "Point and quantile gradient-boosted models"),
        ("SciPy", "1.17.1", "Statistics, inverse normal for the simulator"),
        ("PyTorch / pytorch-forecasting / Lightning", "2.14.0 (CPU) / 1.8.0 / 2.6.6", "TimesNet recovery and TFT forecaster"),
        ("lifelines", "0.30.3", "Kaplan–Meier estimation"),
        ("Matplotlib", "3.10.9", "Figures"),
        ("Streamlit / Plotly", "1.55.0 / 6.6.0", "Interactive order-planner app"),
        ("Node.js / Express", "24.19 (≥ 18) / 4.21.1", "Simulator server and JavaScript model engine"),
        ("React / Vite / three.js", "18.3.1 / 5.4.10 / 0.169.0", "3D simulator front end (@react-three/fiber 8.17.10)"),
        ("Power BI Desktop", "PBIP / TMDL project", "Management report, DAX measures, RLS"),
        ("PostgreSQL", "16 (Docker, optional)", "Star-schema warehouse with views"),
        ("LaTeX (IEEEtran, pdfLaTeX)", "–", "Research paper"),
        ("Jupyter / nbclient", "ipykernel 7.3.0 / 0.11.0", "Notebook execution, top to bottom in one kernel"),
    ], [5.2, 4.4, 5.4], ["left", "center", "left"], size=10)
    R.h2("3.7", "Feasibility Study")
    R.p("**Technical feasibility:** every component uses mature open-source libraries; the full Phase 0–9 run "
        "completed on two CPUs with 8.42 GB of RAM, and the planner pipeline trains its nine boosters in about two "
        "minutes (120.5 s recorded). **Economic feasibility:** the dataset is public under CC BY 4.0 and all software "
        "except Power BI Desktop (free to use) is open source, so the project has no licensing cost. **Operational "
        "feasibility:** planners use the Streamlit app through drop-downs and sliders, managers use a standard Power BI "
        "report, and the simulator runs in any modern browser from a single `npm start`.")

    # ============================================================================== CHAPTER 4
    R.chapter("System Design")
    R.h2("4.1", "System Architecture")
    R.p("The system is organised in four layers (@fig:arch). The **data layer** holds the two FreshRetailNet-50K "
        "Parquet files. Two pipelines read them: the **research pipeline** — three executed notebooks covering Phases 0–9 — "
        "and the **decision-support pipeline** (`planner/pipeline.py`), which applies the same protocol to the real "
        "recorded history of the same 5,000 series. The research pipeline writes its metrics, figures and manifests to "
        "`results/`; the decision-support pipeline writes saved models, residual tables and a ten-table star-schema "
        "warehouse. The **presentation layer** reads only these saved outputs: the IEEE paper, the Power BI report, the "
        "Streamlit planner and the 3D simulator.")
    R.fig("arch", A / "diagrams/fig_architecture.png", "Proposed system architecture")
    R.h2("4.2", "Workflow")
    R.p("@fig:workflow shows the ten phases of the research pipeline. Phases 0–4 prepare the data, simulate "
        "censoring and train the conventional and LightGBM models; Phases 5–7 add the neural, Kaplan–Meier and "
        "calibration components; Phase 8 builds the nine ordering policies and writes the protocol lock; and Phase 9 "
        "scores the locked final week once. Every phase ends with a gate that must pass before the next phase starts.")
    R.fig("workflow", A / "diagrams/fig_workflow.png", "Workflow of the ten-phase stockout-aware forecasting and ordering pipeline")
    R.p("The results come from three saved runs of the notebook pipeline (@fig:lineage). Runs S and P are independent "
        "development runs of Phases 0–4 on 5,000 and 50,000 series. Run E repeats Phases 0–4 on its own 5,000-series "
        "sample, passes an audit that rebuilds the simulator masks and features and checks 33 file hashes, and then runs "
        "Phases 5–9. Only run E feeds the locked final evaluation.")
    R.fig("lineage", A / "diagrams/run_lineage.png", "The three saved runs; only run E feeds the locked final evaluation", width=11)
    R.h2("4.3", "Module Description")
    R.tab("modules", "Modules of the system", ["Module", "File(s)", "Inputs → Outputs"], [
        ("Data verification", "scripts/verify_data.py", "data/*.parquet → OK / mismatch per file (exit status 1 on failure)"),
        ("Phases 0–4 notebook", "notebooks/FreshRetailNet_Phases_0_to_4.ipynb", "Parquet files → sample, features, A/B/C timelines, baselines, 12 demand-quantile models, manifests"),
        ("Phases 0–9 notebook", "notebooks/FreshRetailNet_Phases_0_to_9.ipynb", "Phase 0–4 artefacts → TimesNet/TFT, KM, calibration, 9 policies, lock, final evaluation"),
        ("Paper exhibits", "paper/scripts/make_exhibits.py, make_diagrams.py", "results/ → LaTeX tables and schematic figures (no retraining)"),
        ("Planner pipeline", "planner/pipeline.py", "Parquet + selected series → 9 boosters, residual tables, 10 warehouse CSVs, summary.json"),
        ("PostgreSQL loader", "planner/sql/schema.sql, load_postgres.py", "warehouse CSVs → schema stockout, 3 views, validation checks"),
        ("Power BI builder", "planner/powerbi/build_pbip.py", "warehouse CSVs → StockoutPlanner.pbip (semantic model, 51 measures, 2 RLS roles, report pages)"),
        ("Streamlit planner", "planner/app.py", "saved models + warehouse → 6-tab web app (live scoring, SHAP, what-if, batch)"),
        ("Simulator export", "simulator/export/export_assets.py", "models + panel → JSON boosters, hourly arrays, SHAP, fixtures"),
        ("Simulator engine", "simulator/server/engine/*.js", "lgbm.js, features.js, policy.js, censor.js, service.js: inference, features, orders, stockout simulator"),
        ("Simulator UI", "simulator/web/src/pages/*.jsx", "Command center, Run the store, Censoring lab, Model X-ray"),
    ], [3.3, 5.0, 6.7], ["left", "left", "left"], size=9.5)
    R.h2("4.4", "Data Flow and Data Warehouse")
    R.p("The raw files are streamed in batches of 250,000 rows and joined on the series key (city_id, store_id, "
        "product_id) and date. For every series-day the pipeline forms the 24-hour sales and stock-status arrays, the "
        "06:00–21:59 outcome and the donor flag, and then computes features from shifted and rolling windows that end "
        "on the previous day. Models are fitted on fit days, stopped early on tuning days and calibrated on "
        "calibration days; predictions for days 61–97 and orders for the final week are written to the warehouse.")
    R.p("The warehouse is a star schema (@fig:star; @tab:wh). Three fact tables hold daily sales, forecasts and "
        "orders at their natural grain; five dimensions describe dates, series, models, policies and cost scenarios; a "
        "separate fact table holds the paper's 243 policy results, and a security table maps manager e-mails to cities "
        "for row-level security. The same CSVs are loaded into Power BI (Import mode) and, optionally, PostgreSQL.")
    R.fig("star", A / "diagrams/fig_star_schema.png", "Star schema of the decision-support warehouse", width=14.5)
    R.tab("wh", "Warehouse tables (row counts re-checked for this report)", ["Table", "Grain", "Rows", "Key columns"], [
        ("dim_date", "day", "97", "date_key, date, weekday, period (fit / tuning / calibration / final)"),
        ("dim_series", "store-product", "5,000", "city, store, product, categories, sales_tier, stockout_tier, planner_url"),
        ("dim_model", "forecast model", "5", "model_code, model_name, stockout_aware"),
        ("dim_policy", "ordering policy", "5", "policy_code, policy_name"),
        ("dim_scenario", "cost scenario", "3", "c_u, c_o, β (0.25 / 0.50 / 0.75), quantile"),
        ("fact_sales_daily", "store-product × day", "485,000", "units_sold, stockout_hours, donor_flag, demand_proxy"),
        ("fact_forecast", "store-product × day × model (days 61–97)", "925,000", "q25, q50, q75, q90, actual_demand, is_scored"),
        ("fact_order", "store-product × day × policy × scenario", "525,000", "order_qty, demand, sold, shortage, leftover, cost"),
        ("fact_paper_policy_results", "scenario × policy × train × test", "243", "mean_cost, fill_rate, matched_cell"),
        ("security_user_city", "user × city", "20", "user_email, city (placeholder e-mails)"),
    ], [3.6, 4.0, 1.7, 5.7], ["left", "left", "right", "left"], size=9.5)
    R.h2("4.5", "User Interface Design")
    R.p("The project has three user interfaces, each for a different user:")
    R.bullets([
        "**Streamlit order planner (planner/app.py) — for the supply planner.** A sidebar selects city, store, "
        "product, order date in the held-out week and the unit costs *c_u* and *c_o*; the critical ratio β is shown "
        "live. Six tabs follow: *Order planner* (live forecast band, recommended order, order by policy, SHAP "
        "contributions), *Network KPIs*, *Research results (9 policies)*, *Power BI report*, *Batch scoring* "
        "(CSV upload and download) and *About the data*.",
        "**Power BI report (StockoutPlanner.pbip) — for the planning manager.** Five pages — Executive overview, "
        "Forecast accuracy, Stockouts and service, Policy comparison, Store-product detail (drill-through) — and a "
        "tooltip page, with slicers for city, category, cost scenario and a what-if shortage-cost ratio. The "
        "drill-through page links each store-product to the planner app through `dim_series[planner_url]`.",
        "**3D simulator (simulator/) — for demonstration and teaching.** Four screens: *Command center* (KPIs, 18 "
        "cities as 3D towers, policy race), *Run the store* (a game in which the user places orders for a real store "
        "and customers arrive following real hourly demand), *Censoring lab* (apply mechanisms A/B/C and watch "
        "forecasts react) and *Model X-ray* (edit the 33 inputs and watch 4,008 trees re-score).",
    ])

    # ============================================================================== CHAPTER 5
    R.chapter("Proposed Methodology")
    R.h2("5.1", "Procuring the Dataset")
    R.p("The project uses **FreshRetailNet-50K, version 1.0** [1], [2], released by Dingdong-Inc on Hugging Face "
        "under CC BY 4.0. A series is a (city_id, store_id, product_id) triple. The training file covers 90 days "
        "(2024-03-28 to 2024-06-25) and the evaluation file the following 7 days (2024-06-26 to 2024-07-02). The local "
        "files are identified by their SHA-256 hashes, which `scripts/verify_data.py` re-checked for this report "
        "(both files: OK).")
    R.tab("data", "FreshRetailNet-50K files and fields used", ["Item", "Value / description"], [
        ("train.parquet", "4,500,000 rows = 50,000 series × 90 days; SHA-256 6706832d…5de5a3d"),
        ("eval.parquet", "350,000 rows = 50,000 series × 7 days; SHA-256 1b118840…995e960e"),
        ("Distinct product_id", "865 in train.parquet (the dataset report states 863 SKUs)"),
        ("Identifiers", "city_id, store_id, product_id, management_group_id, first/second/third_category_id"),
        ("hours_sale", "24 hourly sales values per day (normalised units)"),
        ("hours_stock_status", "24 hourly flags per day: 1 = out of stock in that hour"),
        ("sale_amount", "daily sales total"),
        ("Context", "discount, holiday_flag, activity_flag (promotion), precpt (rain), avg_temperature"),
    ], [4.0, 11.0], ["left", "left"], size=10)
    R.h2("5.2", "Outcome Variable and Donor Days")
    R.p("The outcome is the recorded sales between **06:00 and 21:59**, the window that a next-day order has to "
        "cover. A series-day is a **donor day** when its stock-status flags *s*ⱼ,ₜ,ₕ are all zero over that window; only "
        "then do its window sales serve as the demand proxy:")
    R.eq("I^donor_j,t = 1{ Σ_{h=6..21} s_j,t,h = 0 },     D^proxy_j,t = Σ_{h=6..21} y^sale_j,t,h")
    R.p("@fig:sohours shows how the 485,000 store-product-days of the 5,000 sampled series split. Days with one or "
        "more stockout hours have no demand label and are never scored for error or cost. Donor days are a selected "
        "sample: in run S, mean sales over the two weeks before a fit-period donor day were 0.91 times those before "
        "other days, and donor days fell on promotion days less often (0.35 against 0.39). @fig:donors shows that donor "
        "availability falls steeply with a series' stockout frequency.")
    R.fig("sohours", A / "diagrams/fig_stockout_hours.png", "Distribution of daily stockout hours (06:00–21:59) in the 5,000-series sample", width=14)
    R.fig("donors", RE / "phase0_4/figures/p1_donors_vs_stockout.png", "Share of fit days that are donor days against the series' stockout-hour rate (run E)", width=14.5)
    R.h2("5.3", "Chronological Split")
    R.p("All runs use the same chronological split (@tab:split, @fig:split). Fit days train model weights, tuning days "
        "choose hyperparameters and early-stopping rounds, calibration days are used only for conformal and residual "
        "quantiles, and the final week is scored once. Until Phase 4 the evaluation file was read only for its schema, "
        "identifiers and dates.")
    R.tab("split", "Chronological split of the 97 days", ["Role", "Days", "Dates", "Use"], [
        ("Model fit", "1–60", "2024-03-28 to 2024-05-26", "model fitting (training rows from day 8, after the lags fill)"),
        ("Tuning", "61–75", "2024-05-27 to 2024-06-10", "model selection, early stopping"),
        ("Calibration", "76–90", "2024-06-11 to 2024-06-25", "conformal / residual quantiles only"),
        ("Final", "91–97", "2024-06-26 to 2024-07-02", "locked evaluation, used once"),
    ], [2.8, 1.6, 4.6, 6.0], ["left", "center", "center", "left"], size=10)
    R.fig("split", A / "diagrams/fig_split.png", "Data windows of the chronological split")
    R.h2("5.4", "Stratified Sampling")
    R.p("The full Phase 0–9 pipeline runs on 5,000 series. They are drawn by stratified sampling over first-level "
        "category × sales tier × stockout tier (241 non-empty strata) with proportional, largest-remainder allocation and "
        "a seeded permutation within each stratum (seed 20240628). Tier edges are computed from the fit period only: "
        "sales tiers at mean window sales of 0.498 and 0.800, stockout tiers at stockout-hour rates of 0.161 and 0.218. "
        "The 5,000-series sample has a donor share of 0.5580 against 0.5573 for all 50,000 series (run P).")
    R.h2("5.5", "Past-Only Feature Construction")
    R.p("For each target day *t* the pipeline builds 33 features from days before *t* only (@tab:features). Lags are "
        "shifted by at least one day, rolling windows end on day *t* − 1, and target-day flags, sales, weather and "
        "promotions are excluded. A **perturbation test** randomises every target-day field and confirms that the "
        "features of that day do not change while the next day's features do; it passed for the real history and for "
        "all three simulated histories.")
    R.tab("features", "The 33 model input features", ["Group", "Features", "Description"], [
        ("Sales lags", "y_lag1, y_lag2, y_lag7, y_lag14", "window sales 1, 2, 7 and 14 days earlier"),
        ("Sales windows", "y_roll7, y_roll14, y_roll28, y_std14, y_ewm, y_dow_mean", "rolling means, 14-day volatility, exponentially weighted level (α = 0.2), same-weekday mean"),
        ("Donor-only windows", "y_don_roll14, y_don_roll28", "rolling mean of sales on full-stock days only"),
        ("Stockout history", "so_lag1, so_rate7, so_rate14, don_frac7", "stockout hours yesterday, share of days with a stockout, share of donor days"),
        ("Promotion / price", "disc_lag1, disc_roll7, act_lag1, act_roll7", "discount and promotion flag, previous day and 7-day mean"),
        ("Calendar / weather", "hol_lag1, precpt_lag1, temp_lag1, dow, is_weekend, n_hist_days", "previous-day holiday, rain and temperature; weekday; days of history"),
        ("Identifiers (categorical)", "city_id, store_id, product_id, management_group_id, first/second/third_category_id", "native LightGBM categorical features"),
    ], [3.3, 5.6, 6.1], ["left", "left", "left"], size=9.5)
    R.h2("5.6", "Simulated Censoring Mechanisms")
    R.p("Each mechanism replaces the visible history of eligible donor days (those with enough past data) with a "
        "simulated censored one; real censored days keep their recorded values. Under mechanism *m* the opening stock of "
        "series *j* on day *t* is")
    R.eq("Q^(m)_j,t = max{ μ^past_j,t · k^(m)_j,t · exp(σ_m · z_j,t),  q_floor }")
    R.p("where μ^past is the mean recorded window sales over the previous two weeks, *k* a stock multiplier fitted to "
        "fit-period stockout patterns, *z* a seeded standard normal draw shared by all mechanisms (splitmix64 hash "
        "streams) and *q*_floor a small floor. The stock is depleted hour by hour against the true donor-day demand; once "
        "it runs out, demand still arrives but visible sales stop (@fig:mech).")
    R.bullets([
        "**Mechanism A — ordinary depletion:** may add one refill of half the opening stock one to three hours after the "
        "first simulated stockout, with a probability estimated from real within-day recoveries.",
        "**Mechanism B — promotion-sensitive:** A's stock factor multiplied by 0.6 on recorded promotion days (the "
        "promotion flag drives the simulator but is not a forecasting feature).",
        "**Mechanism C — sustained scarcity:** half of A's multiplier, a fixed noise scale and no refill.",
    ])
    R.fig("mech", A / "diagrams/mechanism_paths.png", "The three censoring mechanisms act on eligible donor days", width=10)
    R.p("@tab:sim summarises the simulation for run S. Mechanism C censors 83.2% of eligible donor days and hides "
        "52.6% of their demand, A censors 46.0%, and B sits between them. @fig:timeline shows one series under the real "
        "and the three simulated histories, and @fig:realsim compares simulated with real stockout patterns by tier.")
    R.tab("sim", "Simulation summary on 248,739 eligible donor days per mechanism (run S)", ["Quantity", "A", "B", "C"], [
        ("Masked donor days (≥ 1 simulated stockout hour)", "114,337", "140,861", "206,995"),
        ("Masked share", "0.460", "0.566", "0.832"),
        ("Mean outage hours on masked days", "6.39", "7.29", "9.17"),
        ("Visible sales / proxy demand (total)", "0.803", "0.718", "0.474"),
        ("Masked share on promotion days", "0.512", "0.808", "0.869"),
        ("Masked share on non-promotion days", "0.431", "0.431", "0.812"),
    ], [7.6, 2.4, 2.5, 2.5], ["left", "right", "right", "right"], size=10)
    R.fig("timeline", RE / "phase0_4/figures/p2_timeline_example.png", "One series (key 672) under the real and the three simulated histories", width=14.5)
    R.fig("realsim", RE / "phase0_4/figures/p2_real_vs_sim_by_tier.png", "Real versus simulated partial-stockout rate, first stockout hour and outage length by stockout tier (tuning dates)")
    R.h2("5.7", "Models")
    R.tab("models", "Models and key settings", ["Model", "Trained on", "Key settings"], [
        ("Seasonal naive", "–", "sales of the same weekday last week (t − 7, else t − 14, else past mean) + pooled residual quantiles"),
        ("Raw-sales LightGBM point (L2)", "visible sales, all days", "regression objective + pooled residual quantiles"),
        ("Raw-sales quantile LightGBM", "visible sales, all days", "quantile objective, τ ∈ {0.25, 0.50, 0.75, 0.90}"),
        ("Demand-quantile LightGBM", "donor proxy, donor days only", "quantile objective, one set of 4 per mechanism (12 models)"),
        ("LightGBM settings", "–", "learning rate 0.05, feature/bagging fraction 0.9/0.8, λ₂ = 1.0, grid num_leaves ∈ {31, 63} × min_data_in_leaf ∈ {200, 1000}, early stopping on tuning donors"),
        ("TimesNet → TFT", "600-series deep subset", "TimesNet recovers hidden hours; TFT forecasts the next day from the visible (direct) or recovered history; 4 epochs on CPU"),
        ("Kaplan–Meier percentile", "censored sales in pools", "product-limit estimate within category × sales tier, falling back to coarser pools; ≥ 200 observations and ≥ 20 exact events"),
    ], [4.0, 3.6, 7.4], ["left", "left", "left"], size=9.5)
    R.p("The demand-quantile models are the stockout-aware family: they are trained only on rows whose label is "
        "exact demand. The raw-sales models represent common practice: they treat recorded sales as demand.")
    R.h2("5.8", "Pooled Conformal Calibration")
    R.p("For each quantile level τ, calibration residuals *r* = *D*^proxy − *q̂*_τ are collected on calibration-window "
        "donor rows. Within each pool, the correction is the conformal order statistic")
    R.eq("c_τ(pool) = r_(⌈(n + 1) τ⌉),     q̃_τ = max(0, q̂_τ + c_τ(pool))")
    R.p("Pools fall back from first category × sales tier to category, management group and finally a global pool "
        "whenever a pool has fewer than 200 rows. After the shift, each row's four quantiles are sorted, which removes "
        "every crossing. Point forecasters become quantile forecasts by adding the pooled empirical τ-quantile of their "
        "residuals. An adaptive variant [21] is included as a sensitivity analysis.")
    R.h2("5.9", "Newsvendor Ordering Policies")
    R.p("Each policy orders the β-quantile of its forecast for the three locked cost settings "
        "(*c_u*, *c_o*, β) = (1, 3, 0.25), (1, 1, 0.50) and (3, 1, 0.75), called *excess stock more costly*, *equal costs* "
        "and *shortage more costly*. The cost of a row, evaluated against the unmasked proxy under a one-day shelf life, is")
    R.eq("C(Q, D) = c_o · max(Q − D, 0) + c_u · max(D − Q, 0)")
    R.tab("policies", "The nine locked ordering policies", ["No.", "Policy", "Population scored"], [
        ("1", "Seasonal naive + residual quantile", "full sample"),
        ("2", "Raw-sales LightGBM (point) + residual quantile", "full sample"),
        ("3", "Raw-sales quantile LightGBM", "full sample"),
        ("4", "Demand-quantile LightGBM (uncalibrated)", "full sample"),
        ("5", "Demand-quantile LightGBM + pooled conformal (headline policy)", "full sample"),
        ("6", "Kaplan–Meier order percentile", "rows where the percentile is estimable"),
        ("7", "Demand-quantile + adaptive calibration (sensitivity)", "full sample"),
        ("8", "TFT (direct) + residual quantile", "600-series deep subset"),
        ("9", "TimesNet → TFT + residual quantile", "600-series deep subset"),
    ], [1.2, 9.3, 4.5], ["center", "left", "left"], size=10)
    R.h2("5.10", "Evaluation Metrics")
    R.p("With *D* the donor proxy, *Q* the order and *q̂* the forecast, the following metrics are reported on donor rows:")
    R.eq("WAPE = Σ |q̂₅₀ − D| / Σ D          Fill rate = Σ min(Q, D) / Σ D")
    R.eq("Leftover share = Σ max(Q − D, 0) / Σ Q          Coverage_τ = (1/n) Σ 1{ D ≤ q̂_τ }")
    R.p("The **transfer gap** of a policy trained on mechanism *m* and evaluated on history *h* compares the mean cost "
        "on the unseen history with the matched cost on the same rows 𝓘:")
    R.eq("Δ_m→h = C̄_m→h(𝓘) − C̄_m→m(𝓘)")
    R.p("For a real final-week row with recorded window sales *S*_rec and q90 forecast *U*₉₀, demand is at least "
        "*S*_rec, so every row with *S*_rec > *U*₉₀ is a certain miss. The definite-miss rate")
    R.eq("L_miss = (1/n) Σ 1{ S_rec,i > U_90,i }")
    R.p("is therefore a **lower bound** on the real q90 miss rate; it is not a coverage estimate.")
    R.h2("5.11", "Statistical Inference and the Protocol Lock")
    R.p("Intervals are 95% percentile intervals from 200 paired cluster-bootstrap replicates [28] over the 866 "
        "(city, store) clusters of the sample, with the same sampled cluster multiplicities applied to both sides of each "
        "difference. Dates are not resampled separately and there is no multiplicity adjustment, so the intervals are "
        "descriptive. In Phase 8 run E wrote `final_test_lock.json` — policy names, cost settings, model and calibration "
        "files with their hashes, planned contrasts and bootstrap settings — with digest 4ab12c4b…80c1b6, before any "
        "final-week outcome was read.")

    # ============================================================================== CHAPTER 6
    R.chapter("Software Testing")
    R.p("Testing checks that every part of the system does what it is meant to do and that the reported numbers can "
        "be trusted. Because the project is a data pipeline with three front ends, testing concentrates on data "
        "integrity, the absence of leakage, exact reproduction of model outputs across languages and tools, and the "
        "behaviour of the user-facing applications.")
    R.h2("6.1", "Unit Testing")
    R.p("Individual components are tested against hand-computed or independent results. The Kaplan–Meier estimator "
        "passed all 8 of its unit tests in run E. The order and cost arithmetic of the nine policies passed 10 "
        "hand-computed checks before the protocol lock. In the simulator, `npm run verify` compares the JavaScript "
        "feature builder with the Python features on 3,000 rows (33 features each) and the JavaScript LightGBM "
        "inference with Python on the same rows for all nine boosters.")
    R.h2("6.2", "Integration Testing")
    R.p("Before Phases 5–9, run E executed a prerequisite audit of its own Phase 0–4 outputs: 10 checks, a rebuild "
        "of the simulator masks and feature matrices from the raw panel (exact agreement) and a SHA-256 check of 33 saved "
        "files. For the decision-support side, the warehouse was reconciled with the pipeline summary for this report: "
        "row counts, the number of scored rows per policy and scenario, orphan keys and the mean cost and fill rate of "
        "all 15 policy–scenario cells. `load_postgres.py` runs the same kind of checks after loading PostgreSQL.")
    R.h2("6.3", "System Testing")
    R.p("Each notebook was executed top to bottom in one kernel, and every phase wrote a gate status; run E finished "
        "with all gates PASS except the two upstream-reproduction items, which are recorded as PARTIAL (@fig:phases in "
        "Chapter 7). End to end, the planner pipeline was run from the raw Parquet files to the warehouse, the "
        "warehouse was loaded by Power BI, and both apps were started and exercised for this report.")
    R.h3("6.3.1", "Black-box testing")
    R.p("The Streamlit app was tested from the user's side: every tab, every cost slider, the city/store/product "
        "selectors, a censored and an uncensored order date, and the batch-scoring upload with valid and invalid rows "
        "(unknown series or dates outside the held-out week are skipped and counted, not scored). The simulator was "
        "tested by playing a full week in *Run the store*, applying every mechanism in the *Censoring lab* including the "
        "60-series batch run, and editing inputs in *Model X-ray*.")
    R.h3("6.3.2", "White-box testing")
    R.p("Code paths with special handling were exercised deliberately: censored days, which must have a blank demand "
        "and no cost; series with too little history for the 7- and 14-day lags (seasonal naive falls back to t − 14 and "
        "then to the past mean); pools below 200 rows, which fall back to a coarser pool; a critical ratio outside "
        "0.25–0.90, for which the app warns and uses the nearest modelled quantile; and Kaplan–Meier pools that cannot "
        "support the requested percentile, which are left unscored rather than filled from another policy.")
    R.h2("6.4", "Regression Testing")
    R.p("Three scripts protect against silent changes: `scripts/verify_data.py` checks the dataset hashes, "
        "`npm run verify` re-checks the JavaScript engine against Python, and `paper/scripts/make_exhibits.py` "
        "regenerates every paper table from `results/`, so any change in a saved metric shows up as a diff in the "
        "LaTeX tables.")
    R.h2("6.5", "Smoke Testing")
    R.p("Before a demonstration, a quick check confirms that `python -m streamlit run planner/app.py` serves the app "
        "on port 8501 with all six tabs, and that `npm start` serves the simulator on port 3000 with the status badge "
        "“9 LightGBM models · 4,008 trees · verified vs Python”. Both checks were performed while capturing the "
        "screenshots in Chapter 7.")
    R.h2("6.6", "Acceptance Testing")
    R.p("The system was checked against the objectives in Section 1.6 and the functional requirements in "
        "@tab:fr. @tab:tests lists the test cases. Cases marked *re-run* were executed on 19 November 2026 for this "
        "report; cases marked *recorded* are taken from the saved run manifests.")
    R.tab("tests", "Test cases and obtained outcomes", ["ID", "Test case", "Expected result", "Actual result", "Source", "Status"], [
        ("001", "Dataset files match recorded hashes", "both SHA-256 hashes match", "train.parquet OK, eval.parquet OK", "re-run", "Pass"),
        ("002", "Warehouse row counts", "97 / 5,000 / 485,000 / 925,000 / 525,000 / 243", "97 / 5,000 / 485,000 / 925,000 / 525,000 / 243", "re-run", "Pass"),
        ("003", "Every series has 97 days", "min = max = 97", "min 97, max 97", "re-run", "Pass"),
        ("004", "Demand is blank exactly on censored days", "demand_proxy present ⇔ donor_flag = 1", "true for all 485,000 rows", "re-run", "Pass"),
        ("005", "No target-day leakage (perturbation test)", "target-day features unchanged", "unchanged for real, A, B and C", "recorded", "Pass"),
        ("006", "Scored rows in the held-out week", "20,641 donor rows for every policy × scenario", "20,641 in all 15 cells", "re-run", "Pass"),
        ("007", "Warehouse KPIs match the pipeline", "mean cost and fill rate identical", "max difference 0.0 (15 cells)", "re-run", "Pass"),
        ("008", "No quantile crossing after rearrangement", "0 rows with q25 > q50 > q75 > q90 violated", "0 crossings for all 5 models", "re-run", "Pass"),
        ("009", "JS feature builder vs Python", "0 mismatches", "3,000 rows × 33 features, 0 mismatches", "re-run", "Pass"),
        ("010", "JS booster scores vs Python", "identical scores", "9 models, max |JS − Python| = 0.0", "re-run", "Pass"),
        ("011", "JS final quantiles vs warehouse", "difference ≤ CSV rounding", "2,433 rows × 5 models × 4 quantiles, max 5.0e-5", "re-run", "Pass"),
        ("012", "Kaplan–Meier unit tests", "all pass", "8 / 8", "recorded", "Pass"),
        ("013", "Order and cost arithmetic", "all hand checks pass", "10 / 10", "recorded", "Pass"),
        ("014", "Prerequisite audit before Phases 5–9", "checks, masks, features and hashes agree", "10 checks, exact rebuild, 33 hashes", "recorded", "Pass"),
        ("015", "Paper saving vs seasonal naive (equal costs)", "14.8%", "14.83%", "re-run", "Pass"),
        ("016", "Streamlit app renders all tabs", "6 tabs without error", "6 tabs rendered (@fig:st1 to @fig:st6)", "re-run", "Pass"),
        ("017", "Simulator screens and a full game week", "4 screens; week completes", "4 screens; week result shown (@fig:sim2d)", "re-run", "Pass"),
    ], [1.0, 3.6, 3.4, 3.8, 1.5, 1.2], ["center", "left", "left", "left", "center", "center"], size=8.5)
    R.p("All 17 test cases passed. The two items recorded as PARTIAL in run E (the upstream TimesNet and TFT "
        "repositories) are reproducibility notes about third-party code, not failures of this system, and are "
        "discussed in Section 7.3.")

    # ============================================================================== CHAPTER 7
    R.chapter("Experimental Results")
    R.h2("7.1", "Experimental Setup")
    R.p("The research results come from three saved runs on the hardware in @tab:hw. Runs S and P executed Phases 0–4 "
        "on 5,000 and 50,000 series; run E executed Phases 0–9 on 5,000 series, with a 600-series subset for the "
        "neural models. Run E's Phase 0–4 part took 1,483.8 s (peak 1.280 GB) and its Phase 5–9 part 10,786 s (peak "
        "5.064 GB). All figures and tables in Sections 7.2–7.9 are read from the saved artefacts in `results/`. The "
        "decision-support results in Sections 7.10–7.13 come from `planner/pipeline.py`, which retrains the models on "
        "the **real recorded** history of the same 5,000 series (120.5 s).")
    R.h2("7.2", "Development Runs and Model Training")
    R.p("@tab:scale compares the two development runs. The donor shares agree closely (0.5580 and 0.5573), as do the "
        "simulator summaries. Run P has a lower q50 tuning WAPE but used a reduced hyperparameter search, so neither the "
        "WAPE nor the runtime difference can be put down to scale alone. Run E reproduced run S's selected series, split, "
        "masks, donor counts and q50 WAPEs (0.333440, 0.336140, 0.335759) exactly.")
    R.tab("scale", "Standalone development runs S and P (Phases 0–4)", ["Measure", "Run S", "Run P"], [
        ("Selected series", "5,000", "50,000"), ("Selected series-days", "450,000", "4,500,000"),
        ("Hyperparameter search", "full", "reduced"), ("Fit donor days", "163,250", "1,630,675"),
        ("Tuning donor days", "45,097", "450,872"), ("Calibration donor days", "42,773", "426,447"),
        ("Overall donor share", "0.5580", "0.5573"), ("Training rows per mechanism", "144,078", "1,440,065"),
        ("q50 tuning WAPE, A / B / C", "0.3334 / 0.3361 / 0.3358", "0.3124 / 0.3144 / 0.3161"),
        ("Runtime (s)", "1,194.9", "4,210.4"), ("Peak memory (GB)", "1.292", "6.110"), ("Phase gates", "all pass", "all pass"),
    ], [6.4, 4.3, 4.3], ["left", "right", "right"], size=10)
    R.p("@tab:tuning and @fig:tuning compare point accuracy on identical tuning donors. Trained on donor labels, the "
        "demand-quantile q50 model keeps a WAPE of about 0.334 under every mechanism, whereas the raw-sales models degrade "
        "as censoring gets heavier: under mechanism C the raw-sales q50 model reaches 0.477 and the seasonal-naive rule "
        "0.512. The calibration curves in @fig:tuning show the raw-sales quantiles falling below the diagonal — they "
        "under-forecast demand.")
    R.tab("tuning", "q50 WAPE against the donor proxy on 45,097 tuning donor days (run S)", ["Model", "A", "B", "C"], [
        ("Seasonal naive (visible history)", "0.4105", "0.4305", "0.5122"),
        ("Raw-sales LightGBM L2", "0.3330", "0.3485", "0.4217"),
        ("Raw-sales LightGBM q50", "0.3315", "0.3602", "0.4767"),
        ("Demand-quantile LightGBM q50 (donor labels)", "**0.3334**", "**0.3361**", "**0.3358**"),
    ], [7.6, 2.4, 2.5, 2.5], ["left", "right", "right", "right"], size=10)
    R.fig("tuning", RE / "phase0_4/figures/p4_tuning_comparison.png", "Quantile calibration and point accuracy of demand and raw-sales models on identical tuning donors (preliminary)")
    R.h2("7.3", "Neural and Kaplan–Meier Baselines")
    R.p("The neural models were trained on CPU with two logical CPUs and four epochs per model on the declared "
        "600-series subset, so they are reference points compared only with each other. TimesNet scored 290,397 "
        "artificially hidden donor hours with a WAPE of 0.917–0.934 across mechanisms (@fig:timesnet); its error is "
        "highest in the early-morning hours. For TFT, the next-day WAPE on 5,407 matched tuning donor days falls from "
        "0.451–0.453 with the visible history to 0.413–0.415 with the TimesNet-recovered history. The official "
        "baseline [3] could be reproduced only in part: the as-documented TimesNet run finished only after a recorded "
        "patch for a blocked network download, and the upstream TFT prediction step was not run.")
    R.fig("timesnet", RE / "phase5_9/figures/p5_timesnet_recovery.png", "TimesNet recovery error by hour, sales tier and number of hidden hours (600-series subset)")
    R.p("The Kaplan–Meier implementation passed all 8 unit tests and built 207 support-counted pools (@fig:km). When a "
        "pool cannot support the requested percentile, the order is left unestimated rather than borrowed from another policy.")
    R.fig("km", RE / "phase5_9/figures/p6_km_pools.png", "Kaplan–Meier survival curves for one example pool per mechanism, and pool support")
    R.h2("7.4", "Calibration")
    R.p("Pooled conformal calibration used 513,276 residuals from the calibration window; 0.061 of the calibration "
        "rows were corrected from a pool coarser than category × sales tier. @fig:calib shows the reliability before and "
        "after calibration, the pool sizes and the size of the conformal shift, which grows with τ and is largest "
        "for mechanism C. Sorting removed every remaining quantile crossing, which makes the quantiles ordered but not "
        "necessarily calibrated.")
    R.fig("calib", RE / "phase5_9/figures/p7_calibration_diagnostics.png", "Calibration diagnostics on calibration donors: reliability, pool sizes and conformal shift")
    R.h2("7.5", "Locked Policy Comparison")
    R.p("Each of the nine transfer cells contains the same 20,641 final donor series-dates. The six full-sample "
        "policies other than Kaplan–Meier are scored on all of them; Kaplan–Meier on 6,012 to 20,641 rows per cell where "
        "its order is estimable; and the two neural policies on the 2,510 donor rows of the deep subset. @tab:panels "
        "gives the mean costs of the A-trained models on the A history.")
    R.tab("panels", "Mean newsvendor cost of every locked policy, A-trained models on the A history (lowest per panel in bold)",
          ["Policy", "Population", "n", "β = 0.25", "β = 0.50", "β = 0.75"], [
        ("Seasonal naive + residual quantile", "Full", "20,641", "0.6759", "0.4430", "0.7853"),
        ("Raw-sales LightGBM + residual quantile", "Full", "20,641", "**0.5448**", "**0.3868**", "0.7366"),
        ("Raw-sales quantile LightGBM", "Full", "20,641", "0.5749", "0.3999", "0.7503"),
        ("Demand-quantile LightGBM (uncalibrated)", "Full", "20,641", "0.5816", "0.3946", "0.7152"),
        ("Demand-quantile LightGBM + pooled conformal", "Full", "20,641", "0.5766", "0.3891", "**0.6831**"),
        ("Kaplan–Meier order percentile", "Full", "20,641", "0.8404", "0.6520", "1.3878"),
        ("Demand-quantile + adaptive calibration (sens.)", "Full", "20,641", "0.5815", "0.3932", "0.6963"),
        ("TFT (direct) + residual quantile", "Deep subset", "2,510", "0.6892", "0.4949", "0.9483"),
        ("TimesNet → TFT + residual quantile", "Deep subset", "2,510", "**0.6586**", "**0.4687**", "**0.8759**"),
    ], [5.8, 2.1, 1.5, 1.85, 1.85, 1.9], ["left", "left", "right", "right", "right", "right"], size=9.5)
    R.p("Which full-sample policy is cheapest depends on the cost ratio. The raw-sales LightGBM with residual "
        "quantiles wins when excess stock is more costly and, narrowly, at equal costs (0.3868 against 0.3891), whereas "
        "the pooled-conformal policy wins when shortage is more costly. On the C history pooled conformal is already "
        "the cheaper of the two at equal costs (0.4094 against 0.4411). Kaplan–Meier is the most expensive full-sample "
        "policy in every setting, and in the deep subset TFT on the recovered history beats direct TFT in every setting.")
    R.tab("costsc", "Pooled-conformal policy on its matched history: cost, fill rate and leftover share", ["Cost setting", "History", "n", "Mean cost", "Fill rate", "Leftover share"], [
        ("Excess stock more costly (β = 0.25)", "A / B / C", "20,641", "0.5766 / 0.5825 / 0.5978", "0.614 / 0.608 / 0.589", "0.056 / 0.056 / 0.055"),
        ("Equal costs (β = 0.50)", "A / B / C", "20,641", "0.3891 / 0.3967 / 0.4094", "0.775 / 0.769 / 0.753", "0.124 / 0.125 / 0.122"),
        ("Shortage more costly (β = 0.75)", "A / B / C", "20,641", "0.6831 / 0.6940 / 0.7248", "0.891 / 0.888 / 0.878", "0.226 / 0.228 / 0.227"),
    ], [4.4, 1.9, 1.5, 3.0, 2.4, 2.4], ["left", "center", "right", "center", "center", "center"], size=9)
    R.p("Raising β from 0.25 to 0.75 raises the pooled-conformal fill rate on the A history from 0.614 to 0.891 and "
        "the leftover share from 0.056 to 0.226 (@tab:costsc). @fig:costheat shows the mean cost in all nine train/test "
        "cells for each cost ratio, and @fig:fill places every policy on the fill-rate/leftover plane.")
    R.fig("costheat", RE / "phase5_9/figures/p9_cost_heatmaps.png", "Mean cost of the pooled-conformal policy in the 3 × 3 transfer matrix for each cost ratio")
    R.fig("fill", RE / "phase5_9/figures/p9_fill_vs_leftover.png", "Fill rate against leftover share for every policy in the matched cells (β = 0.5)", width=12)
    R.h2("7.6", "Paired Contrasts")
    R.p("@tab:contrasts reports the contrasts fixed in the protocol lock, pooled over the three matched histories "
        "(negative values favour pooled conformal). Calibration lowers cost against the uncalibrated demand quantiles "
        "in all three settings, and pooled conformal is cheaper than the seasonal-naive and Kaplan–Meier policies "
        "throughout. Against the raw-sales LightGBM with residual quantiles the sign depends on the cost ratio: pooled "
        "conformal costs more when excess stock is more costly, the equal-cost interval contains zero, and it costs "
        "less when shortage is more costly.")
    R.tab("contrasts", "Pre-specified paired contrasts: pooled conformal minus comparator (95% cluster-bootstrap intervals)",
          ["Comparator", "Cost setting", "n", "Difference", "95% interval"], [
        ("Uncalibrated demand quantile", "Excess stock", "61,923", "−0.0052", "[−0.0068, −0.0034]"),
        ("Uncalibrated demand quantile", "Equal", "61,923", "−0.0077", "[−0.0096, −0.0062]"),
        ("Uncalibrated demand quantile", "Shortage", "61,923", "−0.0420", "[−0.0483, −0.0365]"),
        ("Raw-sales LightGBM + residual", "Excess stock", "61,923", "+0.0208", "[0.0016, 0.0432]"),
        ("Raw-sales LightGBM + residual", "Equal", "61,923", "−0.0091", "[−0.0204, 0.0052]"),
        ("Raw-sales LightGBM + residual", "Shortage", "61,923", "−0.0790", "[−0.0946, −0.0615]"),
        ("Seasonal naive + residual", "Excess stock", "61,923", "−0.1213", "[−0.1465, −0.0876]"),
        ("Seasonal naive + residual", "Equal", "61,923", "−0.0694", "[−0.0872, −0.0439]"),
        ("Seasonal naive + residual", "Shortage", "61,923", "−0.1376", "[−0.1723, −0.0902]"),
        ("Kaplan–Meier percentile", "Excess stock", "61,523", "−0.4043", "[−0.4276, −0.3824]"),
        ("Kaplan–Meier percentile", "Equal", "58,183", "−0.3223", "[−0.3429, −0.3046]"),
        ("Kaplan–Meier percentile", "Shortage", "47,294", "−0.7475", "[−0.8175, −0.6812]"),
    ], [5.0, 2.6, 1.8, 2.2, 3.4], ["left", "left", "right", "right", "center"], size=9.5)
    R.h2("7.7", "Mechanism Transfer and Robustness")
    R.p("@tab:transfer fixes the pooled-conformal policy at β = 0.75 and varies the history used for training and "
        "calibration. The largest gap occurs for models trained on A and evaluated on C: 0.7303 against 0.6831, a gap "
        "of **+0.0472** [0.0391, 0.0554]. The C-trained models cost less on the A and B histories than on their own C "
        "history, the hardest of the three, so a negative gap points to an easier history rather than to better transfer.")
    R.tab("transfer", "Transfer gaps of the pooled-conformal policy when shortage is more costly (n = 20,641 per cell)",
          ["Train", "Test", "Matched cost", "Unseen cost", "Gap Δ", "95% interval"], [
        ("A", "B", "0.6831", "0.6932", "+0.0101", "[0.0076, 0.0128]"),
        ("A", "C", "0.6831", "0.7303", "**+0.0472**", "[0.0391, 0.0554]"),
        ("B", "A", "0.6940", "0.6908", "−0.0032", "[−0.0059, −0.0006]"),
        ("B", "C", "0.6940", "0.7306", "+0.0365", "[0.0275, 0.0447]"),
        ("C", "A", "0.7248", "0.7120", "−0.0128", "[−0.0219, −0.0050]"),
        ("C", "B", "0.7248", "0.7086", "−0.0162", "[−0.0242, −0.0083]"),
    ], [1.5, 1.5, 2.6, 2.6, 2.4, 3.4], ["center", "center", "right", "right", "right", "center"], size=10)
    R.p("The cost-ratio reversal holds in all nine train/test cells. When excess stock is more costly, the raw-sales "
        "LightGBM with residual quantiles is the cheapest full-sample policy in every cell, with pooled conformal 0.0007 "
        "to 0.0323 more expensive. When shortage is more costly, pooled conformal is the cheapest in every cell, 0.0441 "
        "to 0.1298 below the raw-sales policy. At equal costs four cells go to each of the two and one to the uncalibrated "
        "demand quantiles. Across the three settings the largest transfer gap of pooled conformal (+0.0472) is the "
        "smallest worst case among the six policies whose forecasts read the evaluation history; the raw-sales quantile "
        "LightGBM reaches +0.2258. @fig:gap shows the equal-cost transfer gaps.")
    R.fig("gap", RE / "phase5_9/figures/p9_transfer_gap_heatmap.png", "Cost transfer gap Δ of the pooled-conformal policy at equal costs", width=9.5)
    R.p("Calibration moves the q90 coverage of the 20,641 matched rows from 0.798–0.828 to 0.879–0.887 and lowers "
        "the q90 pinball loss from 0.119–0.131 to 0.109–0.114 (@fig:cov90); coverage still falls short of the nominal "
        "0.90. Over the seven final dates (2,507 to 3,385 donor rows each) the C history is the most expensive on every "
        "date and the daily q90 coverage ranges from 0.839 to 0.907 (@fig:daily). Under-coverage is concentrated in "
        "series with at most ten complete fit-period days (0.752–0.769 over 532 rows) and on promotion days "
        "(0.854–0.865) (@fig:subgroups). These breakdowns are descriptive and were not pre-specified.")
    R.fig("cov90", RE / "phase5_9/figures/p9_coverage_heatmap_tau90.png", "Coverage at τ = 0.9 before and after pooled conformal calibration in all train/test cells")
    R.fig("daily", RE / "phase5_9/figures/p9_date_by_date.png", "Daily q90 coverage and daily mean cost (equal costs) over the final week, matched cells")
    R.fig("subgroups", RE / "phase5_9/figures/p9_subgroups.png", "q90 coverage by sales tier, stockout tier and complete-day support (matched cells)")
    R.h2("7.8", "Real Recorded Histories")
    R.p("The q90 forecasts of the A-, B- and C-trained pooled-conformal models were applied to the same 35,000 real "
        "final-week rows, including the 14,359 rows with flagged stockouts (@tab:realmiss, @fig:realmiss). A smaller "
        "bound can come from a higher forecast, so on its own it does not mean better calibration. The bound is highest "
        "for rows with 1–4 recorded stockout hours and lowest for rows with 9–16 hours: when a product sells out early, "
        "recorded sales rarely exceed the forecast even when demand does. Only the complete-day stratum has an exact proxy.")
    R.tab("realmiss", "Definite-miss lower bound of the q90 forecast on real final-week rows", ["Recorded stockout hours", "Rows", "A-trained", "B-trained", "C-trained"], [
        ("All rows (95% interval)", "35,000", "0.0895 [0.0852, 0.0942]", "0.0854 [0.0808, 0.0896]", "0.0724 [0.0684, 0.0766]"),
        ("0 (complete day)", "20,641", "0.0730", "0.0708", "0.0579"),
        ("1–4", "4,614", "0.1797", "0.1708", "0.1465"),
        ("5–8", "4,980", "0.1283", "0.1169", "0.1044"),
        ("9–16", "4,765", "0.0334", "0.0327", "0.0298"),
    ], [4.0, 1.6, 3.15, 3.15, 3.1], ["left", "right", "center", "center", "center"], size=9.5)
    R.fig("realmiss", RE / "phase5_9/figures/p9_real_definite_miss.png", "Definite-miss lower bound on the real history by stockout severity and sales tier (dashed: 10% nominal)")
    R.h2("7.9", "Ablations and Run Status")
    R.tab("ablations", "Ablations recorded in run E (equal costs unless stated; lower cost is better)", ["Question", "Result", "Scope"], [
        ("Raw-sales point model vs demand-quantile + conformal", "0.4075 vs 0.3984", "matched cells"),
        ("Uncalibrated vs pooled-conformal q90 coverage", "0.8121 → 0.8832 (nominal 0.90)", "final donors"),
        ("Global vs category × sales-tier pooling (q90 coverage)", "0.8856 vs 0.8832", "mean over A/B/C"),
        ("A-only training vs mechanism-specific training", "0.4012 vs 0.3984", "all three histories"),
        ("Direct TFT vs TimesNet → TFT", "0.4999 vs 0.4690", "600-series subset"),
        ("Seasonal naive vs demand-quantile + conformal", "0.4678 vs 0.3984", "matched cells"),
        ("Short vs full lag set", "not run (not covered by the lock)", "–"),
        ("Static vs adaptive calibration", "0.3984 vs 0.4039", "sensitivity"),
        ("One-day expiry vs two-day carry-over", "0.3984 vs 0.2579", "hypothetical inventory rule"),
        ("Contract vs oracle target-day weather (q50 WAPE)", "33.48% vs 33.40%", "leakage sensitivity only"),
    ], [7.0, 4.6, 3.4], ["left", "left", "left"], size=9.5)
    R.p("The ablations point the same way as the main results: training on donor labels and calibrating both help, "
        "the adaptive drift correction did not pay off in this week, the cost level depends strongly on the one-day "
        "shelf life, and giving the model target-day weather and promotions — which are not known when the order is "
        "placed — would improve the q50 WAPE by only 0.08 percentage points. @fig:phases and @fig:runtime show the phase "
        "gates and the runtime and memory of run E's stages; TimesNet training dominates the runtime.")
    R.fig("phases", RE / "phase5_9/figures/final_phase_status.png", "Phase gate status of run E", width=12.5)
    R.fig("runtime", RE / "phase5_9/figures/final_runtime_memory.png", "Runtime and peak memory by stage of run E (2 logical CPUs, 8.42 GB RAM)", width=12.5)

    # ---- decision support
    R.h2("7.10", "Decision-Support Application (Streamlit Planner)")
    R.p("The planner pipeline applies the same protocol to the real recorded history of the 5,000 series: days 1–60 "
        "fit, 61–75 early stopping, 76–90 calibration and 91–97 held out, with 20,641 scored donor rows in the held-out "
        "week — the same count as run E. @tab:demo and @tab:demoacc summarise its results at equal costs.")
    R.tab("demo", "Held-out-week ordering results of the planner models at equal costs (20,641 scored rows)",
          ["Policy", "Mean cost", "Fill rate", "Leftover units", "Saving vs naive"], [
        ("Demand-quantile LightGBM + pooled conformal", "0.392", "77.1%", "2,607", "15.2%"),
        ("Demand-quantile LightGBM (uncalibrated)", "0.398", "76.3%", "2,521", "14.0%"),
        ("Raw-sales quantile LightGBM", "0.373", "78.9%", "2,641", "19.4%"),
        ("Raw-sales LightGBM + residual quantile", "0.374", "79.5%", "2,803", "19.2%"),
        ("Seasonal naive (t − 7) + residual quantile", "0.463", "81.0%", "4,981", "0.0%"),
    ], [6.4, 1.9, 1.9, 2.4, 2.4], ["left", "right", "right", "right", "right"], size=10)
    R.tab("demoacc", "Held-out-week forecast accuracy of the planner models", ["Model", "q50 WAPE", "Accuracy (1 − WAPE)", "q50 bias", "q90 coverage", "q25–q75 coverage"], [
        ("Demand-quantile + pooled conformal", "0.337", "66.3%", "−12.0%", "88.5%", "47.0%"),
        ("Demand-quantile (uncalibrated)", "0.342", "65.8%", "−13.2%", "83.5%", "40.5%"),
        ("Raw-sales quantile LightGBM", "0.321", "67.9%", "−10.1%", "87.3%", "46.2%"),
        ("Raw-sales LightGBM + residual", "0.321", "67.9%", "−8.8%", "87.8%", "47.5%"),
        ("Seasonal naive + residual", "0.398", "60.2%", "+1.7%", "91.7%", "52.5%"),
    ], [5.0, 1.8, 2.2, 1.8, 2.0, 2.2], ["left", "right", "right", "right", "right", "right"], size=9.5)
    R.p("On the real history the calibrated policy cuts cost by 15.2% and leftover units by 47.7% against the "
        "seasonal-naive rule, but gives up fill rate (77.1% against 81.0%) because the naive rule over-orders. Unlike the "
        "simulation, the raw-sales models are as good as the stockout-aware ones here (0.373 against 0.392): the paper's "
        "advantage for stockout-aware training appears when censoring is heavy and the cost of a shortage is high.")
    R.p("@fig:st1 shows the *Order planner* tab for store-product S343 / P300 (City 00) on 26 June 2024 at equal costs. "
        "Every number on the tab is computed live from the saved LightGBM boosters: the recommended order is 8.77 units "
        "with an 80% band of 6.39–13.15, while actual demand on this full-stock day was 15.40, giving a cost of 6.63. The "
        "chart marks the days on which the real store sold out (orange crosses), and the SHAP panel shows that the "
        "average for this weekday (+2.56) and yesterday's sales (+1.16) pushed the forecast up from a baseline of 0.85.")
    R.fig("st1", A / "streamlit/st1_order_planner.png", "Streamlit planner — Order planner tab: live forecast band, order by policy and SHAP explanation", max_h=19)
    R.p("The *Network KPIs* tab (@fig:st2) aggregates the held-out week with city and category filters: fill rate "
        "77.1%, observed stockout rate 41.0% in the final week, forecast accuracy 66.3% and a cost saving of 15.2% "
        "against seasonal naive. It also plots cost against fill rate, re-scores the orders at the sidebar costs, shows "
        "the daily fill rate and lists the ten most expensive store-products, each with a link back to the planner.")
    R.fig("st2", A / "streamlit/st2_network_kpis.png", "Streamlit planner — Network KPIs tab", max_h=19.5)
    R.p("The *Research results* tab (@fig:st3) shows the paper's nine-policy comparison from run E, here at equal "
        "costs over the matched cells, where the pooled-conformal policy is cheapest (0.398) and 14.83% below seasonal "
        "naive; the *About the data* tab (@fig:st6) documents the data, the split, the model and its limitations.")
    R.fig("st3", A / "streamlit/st3_research_results.png", "Streamlit planner — Research results tab (run E, equal costs, matched cells)")
    R.fig("st6", A / "streamlit/st6_about_the_data.png", "Streamlit planner — About the data tab")
    R.h2("7.11", "Power BI Management Report")
    R.p("The Power BI report is built as a PBIP project with a TMDL semantic model: ten tables, single-direction "
        "relationships from facts to dimensions, `dim_date` marked as the date table, 51 DAX measures in a `_Measures` "
        "table and two row-level-security roles (*City Manager*, filtering `dim_series[city]` by "
        "`USERPRINCIPALNAME()` through `security_user_city`, and a fixed *City 00 Manager (demo)* role).")
    R.p("The **Executive overview** (@fig:pbi1) shows the headline KPIs for the selected scenario, the daily fill rate "
        "of the headline policy against seasonal naive and the ten most expensive store-products. All ten are product "
        "P267 (category 21), whose median forecast is 64% below actual demand: 11 of the 5,000 store-products (0.2%) "
        "account for 11.9% of the headline policy's cost.")
    R.fig("pbi1", PBI / "1_executive_overview.png", "Power BI — Executive overview page")
    R.p("The **Forecast accuracy** page (@fig:pbi2) reports accuracy 66.3%, bias −12.0%, q90 coverage 88.5% "
        "(nominal 90%) and q25–q75 coverage 47.0% (nominal 50%), with accuracy by category, bias by city and the median "
        "forecast against actual demand on scored days.")
    R.fig("pbi2", PBI / "2_forecast_accuracy.png", "Power BI — Forecast accuracy page")
    R.p("The **Stockouts and service** page (@fig:pbi3) covers all 97 days: a 44.0% stockout rate, 1,531,170 "
        "stockout hours, a 56.0% full-stock day share and 5,484 units of simulated lost sales in the final week. The "
        "city × weekday heatmap shows the rate ranging from 37.3% in City 17 to 49.0% in City 02, with Sundays (47.7%) "
        "and Tuesdays (47.4%) the worst days and Fridays (38.6%) the best.")
    R.fig("pbi3", PBI / "3_stockouts_and_service.png", "Power BI — Stockouts and service page")
    R.p("The **Policy comparison** page (@fig:pbi4) places the five demo policies on the cost/fill-rate plane next to "
        "the paper's nine policies, with a what-if shortage-cost ratio that re-ranks the policies through the "
        "`What-if Mean Cost` and `What-if Rank` measures. The **Store-product detail** page (@fig:pbi5) is a "
        "drill-through target; for S529 / P267 it shows units sold far above the q90 band and a link that opens the "
        "same store-product in the Streamlit planner.")
    R.fig("pbi4", PBI / "4_policy_comparison.png", "Power BI — Policy comparison page")
    R.fig("pbi5", PBI / "5_store_product_drillthrough.png", "Power BI — Store-product detail (drill-through) page for S529 / P267")
    R.h2("7.12", "3D Stockout Simulator")
    R.p("The simulator runs the trained models in the browser without calling Python. Its Node.js engine "
        "re-implements LightGBM inference from the nine exported boosters (4,008 trees), the 33-feature builder, pooled "
        "conformal and residual quantiles, the newsvendor order and the paper's stockout simulator with the same "
        "parameters and hash streams; the verification in @tab:tests (cases 009–011) shows that it is exact.")
    R.p("The **Command center** (@fig:sim1) shows the network KPIs for a chosen cost scenario, the 18 cities as 3D "
        "towers whose height is the stockout rate (C08 lowest at 38%, C02 highest at 49%), and a live policy race. At "
        "equal costs the raw-sales quantile model leads (0.373) and the stockout-aware policy is third (0.392); switching "
        "to *Shortage more costly* (@fig:sim1b) raises the stockout-aware fill rate to 89.0% at a cost of 0.680.")
    R.fig("sim1", A / "simulator/sim1_command_top.png", "Simulator — Command center at equal costs")
    R.fig("sim1b", A / "simulator/sim1_command_shortage.png", "Simulator — Command center with the shortage-more-costly scenario selected")
    R.p("In **Run the store** the user picks a real store and orders for every shelf each morning of the held-out "
        "week (@fig:sim2a). The store then opens: customers arrive following each product's real hourly demand, shelves "
        "empty, and products whose real store sold out are marked *censored* and not scored, as in the paper "
        "(@fig:sim2b). At closing time each shelf card compares the user's order with the AI, seasonal-naive and "
        "raw-sales orders against actual demand (@fig:sim2c).")
    R.fig("sim2a", A / "simulator/sim2_game_setup.png", "Simulator — Run the store: choosing a store (City 11 · Store 891) and the cost ratio")
    R.fig("sim2b", A / "simulator/sim2_game_open.png", "Simulator — Run the store: the 3D store at 11:00 on day 1, with censored shelves marked")
    R.fig("sim2c", A / "simulator/sim2_game_close.png", "Simulator — Run the store: closing time, per-shelf orders, shortages, waste and cost", max_h=19.5)
    R.p("@fig:sim2d shows the end of a week played with the *Use AI orders* button (orders rounded to 0.1 unit). "
        "The week cost was 11.41 for the player, 11.58 for the stockout-aware AI, 12.16 for the raw-sales quantile model "
        "and 20.93 for seasonal naive, whose fill rate was only 72.4%.")
    R.fig("sim2d", A / "simulator/sim2_game_final.png", "Simulator — Run the store: week result for Store 891")
    R.p("The **Censoring lab** (@fig:sim3) is the core idea of the project made visible. For S343 / P300 mechanism A "
        "censors 53 of 54 full-stock days and hides 106.1 units of demand; the hour-by-hour panel shows a day on which "
        "the shelf empties at 14:00 although demand continues. Re-forecasting the held-out week from the censored "
        "history shifts the raw-sales forecast by −10.2% and seasonal naive by −14.4%, while the stockout-aware forecast "
        "moves by only +0.5%. The batch run on 60 random series "
        "(1,314 censored history days, 250 scored forecasts) shows forecast shifts of −9.2%, −5.1% and −11.4%: both demo "
        "models were trained on the real history, so heavier censoring at forecast time pulls their inputs down — "
        "exactly the transfer gap that the paper measures. Under mechanism C (@fig:sim3c) 314.3 units are hidden and "
        "the forecasts shift by −20.9% (stockout-aware), −44.0% (raw-sales) and −39.4% (seasonal naive).")
    R.fig("sim3", A / "simulator/sim3_lab_batch.png", "Simulator — Censoring lab with mechanism A and the 60-series batch run", max_h=19.5)
    R.fig("sim3c", A / "simulator/sim3_lab_mechC.png", "Simulator — Censoring lab with mechanism C (no refill)")
    R.p("**Model X-ray** (@fig:sim4) exposes the 33 inputs of one store-product-day. Changing any slider re-scores all "
        "five forecast models instantly; the panel shows the conformal pool (category × sales tier), the newsvendor "
        "order, the q50 booster as a 3D forest of 208 trees, the TreeSHAP contributions and how many trees consulted "
        "each feature (product: 116 trees, store: 102).")
    R.fig("sim4", A / "simulator/sim4_xray_full.png", "Simulator — Model X-ray for S343 / P300 on 26 June 2024", max_h=19.5)
    R.h2("7.13", "Business Insights")
    R.p("The decision-support results lead to three findings for a supply-planning manager (5,000 store-products, "
        "held-out week 26 June – 2 July 2024, 20,641 full-stock store-product-days scored):")
    R.numbers([
        "**The calibrated model cuts ordering cost by 15% and waste by 48%, at some cost in fill rate.** At equal "
        "costs it costs 0.392 per store-product-day against 0.463 for seasonal naive; leftover units fall from 4,981 to 2,607.",
        "**Stockouts are frequent and concentrated:** 44.0% of store-product-days have at least one stockout hour, from "
        "37.3% in City 17 to 49.0% in City 02, worst on Sundays and Tuesdays.",
        "**One item drives a disproportionate share of cost:** product P267 is 11 store-products (0.2%) but 11.9% of "
        "the headline policy's cost, and every top-10 problem row is P267.",
    ])
    R.p("The recommendations are to replace the seasonal-naive rule with the calibrated quantile policy for fresh items "
        "where waste costs at least as much as a lost sale, to put items such as P267 whose demand exceeds q90 on more "
        "than two of seven days on a manual review list, and to raise β for high-stockout cities and weekends while "
        "tracking the 7-day rolling stockout rate in the Power BI report.")
    R.h2("7.14", "Comparison with Prior Work")
    R.p("The dataset report [1] evaluates the recovery of masked hours and forecast accuracy; this project's TimesNet "
        "recovery on 290,397 hidden donor hours is a task-aligned counterpart, reproduced in part with the official code "
        "[3]. Azar [25] selects newsvendor policies on the same dataset but scores profit on censored sales; here every "
        "order is scored against an uncensored proxy on identical rows, and the training censoring is varied in a 3 × 3 "
        "design with paired intervals. The finding that the ranking of calibrated demand quantiles and a raw-sales "
        "model reverses with the cost ratio is consistent with the theoretical prediction that the cost of treating "
        "sales as demand is concentrated where high quantiles are ordered [8], [10]. Unlike these studies, the project "
        "also delivers the models as verified decision-support software.")

    # ============================================================================== CHAPTER 8
    R.chapter("Conclusion")
    R.p("This project set out to compare demand forecasting and ordering policies fairly when sales are censored by "
        "stockouts. Using the hourly stock-status flags of FreshRetailNet-50K, days without a stockout were turned into "
        "an exact demand proxy, three simulated stockout mechanisms produced differently censored training histories, "
        "and nine ordering policies were scored on the same 20,641 donor rows of a final week that was locked and used once.")
    R.p("No single policy wins under every cost ratio. When a shortage costs three times as much as a leftover unit, "
        "LightGBM demand quantiles with pooled conformal calibration are the cheapest full-sample policy in all nine "
        "train/test cells; when leftovers cost more, a raw-sales LightGBM with residual quantiles is cheapest in all "
        "nine. Calibration lowers cost in every setting and raises q90 coverage from about 0.81 to 0.88. Moving the "
        "calibrated policy to an unseen censoring mechanism raises its cost by at most 0.0472 normalized units "
        "(95% interval 0.0391–0.0554), the smallest worst case among the policies that read the evaluation history. "
        "On real censored days only a lower bound can be given: 0.072–0.090 of rows are certain q90 misses.")
    R.p("The models were delivered as three verified tools: a Streamlit planner that scores the boosters live and "
        "explains each forecast, a Power BI report with 51 DAX measures and row-level security on a star-schema "
        "warehouse, and a 3D simulator whose JavaScript engine reproduces the Python features and scores exactly. On the "
        "real history the calibrated policy cuts cost by 15.2% and waste by 47.7% against the seasonal-naive rule. "
        "Scoring against donor days makes stockout-aware comparisons testable, and the project shows that the right "
        "policy depends on the cost of a shortage.")
    R.h2("8.1", "Limitations")
    R.bullets([
        "Donor-day sales equal demand only on complete days, and whether a day is complete depends on both demand and "
        "stocking, so the proxy does not identify demand on censored days; there only a lower bound is reported.",
        "Mechanisms A, B and C are specified simulations, not counterfactual inventory paths, so the transfer results "
        "measure sensitivity to these histories rather than transport to another retailer.",
        "Kaplan–Meier is scored only on estimable rows, and the neural policies are budget-limited references on 600 series.",
        "The rankings depend on the locked cost ratios and the one-day shelf life, and one evaluated week cannot show "
        "seasonal effects; the bootstrap uses only 200 replicates.",
        "Costs are in relative units because the data has no prices, and the upstream dataset revision and download "
        "date were not recorded, so local file hashes identify the data.",
        "The complete Phase 0–9 run covers 5,000 series; the 45,000 series outside run E's sample have never been "
        "scored and would need only a new lock.",
    ])

    # ============================================================================== CHAPTER 9
    R.chapter("Future Enhancements")
    R.p("Several extensions would make the framework more general and more useful in practice:")
    R.bullets([
        "**Scale the locked evaluation to all 50,000 series:** run Phases 5–9 on the 45,000 unscored series under a new "
        "protocol lock.",
        "**Censoring-aware training objectives:** train quantile models with a censored pinball loss or a Tobit-style "
        "likelihood on all days instead of only on donor days.",
        "**Better neural baselines:** train TimesNet and TFT on GPU for more epochs and on the full sample, and add "
        "probabilistic deep forecasters.",
        "**Multi-day shelf life and carry-over:** extend the newsvendor to perishable inventory with two or more days of "
        "shelf life, which the carry-over ablation shows changes the cost level strongly.",
        "**Price-based costs:** connect *c_u* and *c_o* to margins and disposal costs per category with finance input.",
        "**Online deployment:** schedule the planner pipeline nightly, publish the Power BI report with the RLS roles, and "
        "monitor calibration drift with the adaptive conformal variant.",
        "**Intervention studies:** measure whether planners who follow the recommended orders reduce waste and lost sales.",
    ])

    # ============================================================================== CHAPTER 10
    R.chapter("References")
    R.tab("refs", "References", ["S.No.", "Authors", "Title", "Journal / Conference / Source", "Year"],
          [(str(i), a, t, j, y) for i, (a, t, j, y) in enumerate(REFERENCES, 1)],
          [1.1, 3.9, 5.0, 3.9, 1.1], ["center", "left", "left", "left", "center"], size=8.5)

    # ============================================================================== APPENDIX
    R.unnumbered_chapter("APPENDIX")
    R.p("This appendix reproduces key functions of the project's source code. The complete code is in the project "
        "folder (notebooks/, planner/, simulator/, paper/scripts/ and scripts/).")
    R.h3("A.1", "Past-only feature construction (planner/pipeline.py)")
    R.code('''def roll_past(a, w, fn="mean"):
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
    # ... exponentially weighted level, same-weekday mean, calendar and identifier columns''')
    R.h3("A.2", "Pooled conformal calibration (planner/pipeline.py)")
    R.code('''def residual_table(resid, meta, tau, conformal):
    """Per pool: conformal order statistic r_(ceil((n+1)tau)) or plain empirical tau-quantile;
    pools with < MIN_POOL rows are skipped."""
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


def apply_table(tab, meta):
    labs = pool_labels(meta)
    out = np.full(len(meta), np.nan)
    for lvl in ["category_x_sales_tier", "category", "management_group", "global"]:
        need = np.isnan(out)
        if not need.any():
            break
        vals = pd.Series(labs[lvl][need]).map(tab[lvl]).to_numpy(dtype=float)
        idx = np.nonzero(need)[0]
        hit = np.isfinite(vals)
        out[idx[hit]] = vals[hit]
    return out

# shift, clip at zero and sort each row's four quantiles (monotone rearrangement)
arr = np.sort(np.stack(cols, 1), 1)''')
    R.h3("A.3", "Hour-by-hour stockout simulation (simulator/server/engine/censor.js)")
    R.code('''// stock Q = max(MU * k * exp(sigma * z), q_floor) is depleted hour by hour against the true
// donor-day demand; A refills with probability p_refill, B is A with lower stock on promotion
// days, C has lower stock and no refill. Same parameters and splitmix64 streams as the notebook.
export function deplete(demand, Q, refillLag = null, refillAmt = 0) {
  let stock = Q, refillHour = 1e6, first = -1;
  const vis = [], flag = [], stockPath = [];
  for (let h = 0; h < demand.length; h++) {
    if (refillLag !== null && refillHour === h) stock += refillAmt;
    const dd = demand[h], s = Math.min(dd, stock);
    const out = dd > stock + 1e-12 || stock <= 1e-12;
    vis.push(s); flag.push(out ? 1 : 0); stock -= s; stockPath.push(stock);
    if (out && first < 0) { first = h; if (refillLag !== null) refillHour = h + refillLag; }
  }
  return { vis, flag, first, stockPath, refillHour: refillHour < 1e6 ? refillHour : null };
}''')
    R.h3("A.4", "DAX measures and SQL view (Power BI model and planner/sql/schema.sql)")
    R.code('''measure 'Fill Rate %' = DIVIDE ( [Sold Units], [Order Demand] )
measure 'Forecast Accuracy %' = IF ( NOT ISBLANK ( [WAPE %] ), 1 - [WAPE %] )
measure 'Cost Saving % vs Seasonal Naive' =
    IF ( NOT ISBLANK ( [Mean Cost] ), 1 - DIVIDE ( [Mean Cost], [Mean Cost (Seasonal Naive)] ) )
measure 'What-if Mean Cost' =
    DIVIDE ( [Lost Sales (units)] * [Shortage Cost Ratio Value] + [Leftover Units], [Scored Order Days] )
measure 'Stockout Rate % (7-Day Rolling)' =
    CALCULATE ( [Stockout Rate %], DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -7, DAY ) )

-- RLS role 'City Manager'
tablePermission dim_series = [city] IN CALCULATETABLE ( VALUES ( security_user_city[city] ),
                              security_user_city[user_email] = USERPRINCIPALNAME () )

CREATE OR REPLACE VIEW v_policy_kpis_final AS   -- one row per scenario x policy, scored days only
SELECT s.scenario_name, p.policy_name,
       count(o.demand)                                  AS scored_days,
       sum(o.sold_units) / nullif(sum(o.demand), 0)     AS fill_rate,
       sum(o.leftover_units) / nullif(sum(o.order_qty) FILTER (WHERE o.demand IS NOT NULL), 0) AS leftover_share,
       avg(o.cost)                                      AS mean_cost
FROM fact_order o JOIN dim_policy p USING (policy_key) JOIN dim_scenario s USING (scenario_key)
WHERE o.demand IS NOT NULL
GROUP BY s.scenario_key, s.scenario_name, p.policy_key, p.policy_name;''')

    R.unnumbered_chapter("PAPER PUBLICATION STATUS")
    R.p("A research paper based on this project, titled “**Stockout-Aware Demand Forecasting and Newsvendor "
        "Ordering on FreshRetailNet-50K**”, has been prepared in IEEE conference format by Akshara Kumari, Aman Koley, "
        "Shivam Singh and G. Premalatha (Department of Data Science and Business Systems, SRM Institute of Science and "
        "Technology). The manuscript and its LaTeX sources are in the project folder (paper/main.tex, paper/main.pdf).")
    R.p("**Status:** [[to be filled in — e.g. submitted to / accepted at <conference name and year>]]")

    R.unnumbered_chapter("PLAGIARISM REPORT")
    R.p("[[Insert the summary pages of the Turnitin similarity report and AI-writing report for the paper here "
        "(submission ID, date, overall similarity and AI-detection percentage).]]")

    # ------------------------------------------------------------------ front matter text
    abstract = [
        "Recorded sales understate demand whenever a product sells out, so forecasts and orders fitted to sales inherit "
        "the store's stocking policy. This project studies demand forecasting and newsvendor ordering for fresh retail "
        "on **FreshRetailNet-50K**, a public panel of 50,000 store-product series with hourly sales and hourly "
        "stock-status flags. In the 5,000-series study sample, 44.0% of store-product-days have at least one stockout "
        "hour; on the remaining *donor days* recorded sales give an exact, though selected, proxy for demand.",
        "Donor days are censored with three simulated stockout mechanisms (ordinary depletion, promotion-sensitive and "
        "sustained scarcity), so that models trained on differently censored histories can be scored against the same "
        "uncensored outcomes. A ten-phase, leakage-free pipeline compares a seasonal-naive rule, LightGBM models "
        "trained on recorded sales, LightGBM demand-quantile models trained on donor days, TimesNet/TFT and a "
        "Kaplan–Meier baseline, with pooled conformal calibration. Nine ordering policies and three cost ratios were "
        "locked before a final week of 20,641 donor rows was scored once.",
        "No policy wins under every cost ratio. When a shortage costs three times as much as a leftover unit, calibrated "
        "demand quantiles are the cheapest full-sample policy in all nine train/test cells; when leftovers cost more, a "
        "raw-sales LightGBM with residual quantiles is cheapest in all nine. Calibration raises q90 coverage from 0.81 "
        "to 0.88, and moving the calibrated policy to an unseen censoring mechanism raises its mean cost by at most 0.0472 "
        "normalized units, the smallest worst case among policies that read the evaluation history. On real censored "
        "days only a lower bound of 0.072–0.090 on q90 misses can be given.",
        "The models are delivered as a Streamlit order planner with live scoring and SHAP explanations, a Power BI "
        "report with row-level security on a star-schema warehouse, and a 3D web simulator that reproduces the Python "
        "models exactly. On the real history the calibrated policy cuts ordering cost by 15.2% and waste by 47.7% "
        "against the seasonal-naive rule.",
    ]
    keywords = ("censored demand, stockouts, demand forecasting, quantile regression, LightGBM, conformal "
                "calibration, newsvendor, fresh retail, Power BI, decision support.")
    ack = [
        "The success and final outcome of this project required guidance and assistance from many people, and we are "
        "extremely fortunate to have received it throughout the course of the work. Everything we have done is due to "
        "such supervision and assistance, and we would not forget to thank them.",
        "We express our sincere thanks to the Head of the Department, Department of Data Science and Business Systems, "
        "**Dr. KAVITHA V**, for providing the facilities and an encouraging environment to carry out this project.",
        "We owe our profound gratitude to our project guide **G. PREMALATHA**, who took keen interest in our project work "
        "and guided us all along, from shaping the research question to reviewing the methodology, results and paper, by "
        "providing all the necessary information and feedback.",
        "We are thankful to and fortunate enough to get constant encouragement, support and guidance from all the "
        "teaching and non-teaching staff of the Department of Data Science and Business Systems, which helped us "
        "successfully complete our project work. We also thank Dingdong-Inc for releasing the FreshRetailNet-50K "
        "dataset publicly for research.",
    ]
    return {"abstract": abstract, "keywords": keywords, "ack": ack, "symbols": SYMBOLS}
