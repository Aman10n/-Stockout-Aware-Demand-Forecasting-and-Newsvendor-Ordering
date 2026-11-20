# Stockout Simulator

An interactive 3D web app that runs the project's trained models live. It has four screens:

| Screen | What you do | What it shows |
|---|---|---|
| **Command center** | Pick a cost scenario, drag the shortage/waste cost ratio, click a city tower | Network KPIs, 18 cities as 3D towers (height = stockout rate, colour = cost saving), a live policy race, the paper's 9-policy results, the Power BI report |
| **Run the store** (game) | Pick a real store, then order for every shelf each morning of the held-out week | Customers arrive in a 3D store following each product's **real hourly demand**. Shelves empty, stockouts and waste happen, and your cost is scored against the AI, the seasonal-naive rule and a raw-sales model |
| **Censoring lab** | Apply the paper's stockout mechanisms A/B/C, or click days to force stockouts | Hour-by-hour depletion, how much demand gets hidden, and how each model's forecast for the held-out week shifts when it sees the censored history. A batch run repeats this on 60 random series |
| **Model X-ray** | Drag any of the 33 model inputs for one store-product-day | All 5 forecast models re-score instantly, with the conformal shift, the newsvendor order, the q50 model as a 3D forest of 208 trees, and TreeSHAP contributions |

**Presenting it?** See [docs/Stockout_Simulator_Guide.pdf](docs/Stockout_Simulator_Guide.pdf): setup, a screen-by-screen guide with screenshots, a 10-minute demo script and Q&A. Rebuild it with `python simulator/docs/build_guide.py <screenshot folder>`. Tip: `http://localhost:3000/?store=891#game` opens the game with Store 891 pre-selected.

## Exactness

The server does not call Python. `server/engine/` re-implements:

- LightGBM inference (`lgbm.js`): numerical and categorical splits, missing-value rules, float32 inputs, from the 9 exported boosters (4,008 trees)
- the 33-feature builder (`features.js`), following numpy's summation order
- pooled conformal / residual quantiles, the seasonal naive and the newsvendor order (`policy.js`)
- the paper's stockout simulator (`censor.js`), with the same parameters, the same splitmix64 hash streams, and an AS241 inverse normal

`npm run verify` checks the JavaScript engine against Python on 3,000 rows:

```
[PASS] features: 3000 rows x 33 features, 0 mismatches
[PASS] booster scores: 9 models, max |JS - Python| = 0.00e+0
[PASS] final quantiles vs warehouse: 2433 rows x 5 models x 4 quantiles, max diff = 5.00e-5   (CSV rounding)
```

The simulator's random streams match the notebook exactly, and the inverse normal matches scipy to 1.3e-15.

## Run

You need Node 18+ and Python 3.11+, plus the dataset in `data/` at the repository root.

```powershell
python planner/pipeline.py                 # trains the models (about 2 min), if planner/output/ does not exist yet
cd simulator
npm install
npm run export                             # Python: exports models, hourly panel, SHAP, fixtures to simulator/data/
npm run verify                             # JS engine vs Python
npm run build                              # builds the front end
npm start                                  # http://localhost:3000
```

For development with hot reload, run `npm start` and `npm run dev` together, then open http://localhost:5173.

## Stack

Node.js + Express (API and engine), React 18 + Vite, three.js through @react-three/fiber and drei (3D scenes),
zustand (state), hand-written SVG charts.

## Honest notes

- The game follows the paper's evaluation protocol. Forecasts for day t use the real history up to day t-1, and days
  on which the real store sold out have no known demand, so they are shown but not scored.
- The demo models were retrained on the real recorded history (`planner/pipeline.py`). The paper's 9-policy
  results, trained on simulated censored histories, appear on the Command center. In the Censoring lab, heavy
  censoring pulls both demo models' forecasts down, because neither was trained on censored inputs. Measuring that
  gap is what the paper's transfer experiments do.
- Sales are in the dataset's units, and costs are relative (the data has no prices).
