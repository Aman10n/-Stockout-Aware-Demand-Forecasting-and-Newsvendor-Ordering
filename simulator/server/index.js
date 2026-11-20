// Stockout Simulator API + static front end.   npm start  ->  http://localhost:3000
import express from 'express';
import compression from 'compression';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { loadService } from './engine/service.js';
import { simulateSeries, deplete } from './engine/censor.js';
import { orderAt, newsvendor } from './engine/policy.js';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const PORT = Number(process.env.PORT || 3000);
console.log('loading model assets ...');
const t0 = Date.now();
const svc = loadService(path.join(ROOT, 'data'));
const { cfg } = svc;
const FINAL = Array.from({ length: 7 }, (_, i) => 90 + i);
console.log(`ready in ${((Date.now() - t0) / 1000).toFixed(1)}s: ${cfg.n_series} series, ${Object.keys(svc.boosters).length} models`);

const app = express();
app.use(compression());
app.use(express.json({ limit: '2mb' }));
const label = (m) => ({
  city: `City ${String(m.city_id).padStart(2, '0')}`, store: `Store ${String(m.store_id).padStart(3, '0')}`,
  product: `Product ${String(m.product_id).padStart(3, '0')}`, category: `Cat ${String(m.first_category_id).padStart(2, '0')}`,
});
const seriesInfo = (sid) => ({ sid, ...svc.series[sid], ...label(svc.series[sid]) });
const wrap = (fn) => (req, res) => {
  try { res.json(fn(req)); } catch (e) { console.error(e); res.status(400).json({ error: String(e.message || e) }); }
};
const sidOf = (v) => {
  const s = Number(v);
  if (!Number.isInteger(s) || s < 0 || s >= cfg.n_series) throw new Error('unknown series');
  return s;
};

// ---------------------------------------------------------------------------------------------- meta
app.get('/api/meta', wrap(() => ({
  dates: cfg.dates, split: cfg.split, scenarios: cfg.scenarios, models: cfg.models, taus: cfg.taus,
  features: cfg.features, summary: cfg.summary, simParams: svc.simParams,
  engine: { models: cfg.model_files.length, trees: Object.values(svc.boosters).reduce((a, b) => a + b.trees.length, 0) },
  stores: svc.stores.map((s) => ({ ...s, city: `City ${String(s.city_id).padStart(2, '0')}`, store: `Store ${String(s.store_id).padStart(3, '0')}` })),
})));

app.get('/api/network', wrap(() => svc.network));

// compact index for the city -> store -> product pickers: [sid, city_id, store_id, product_id, category]
app.get('/api/series-index', wrap(() => svc.series.map((m) => [m.sid, m.city_id, m.store_id, m.product_id, m.first_category_id])));

app.get('/api/store/:storeId', wrap((req) => {
  const id = Number(req.params.storeId);
  return svc.series.filter((m) => m.store_id === id).map((m) => seriesInfo(m.sid));
}));

app.get('/api/find', wrap((req) => {
  const { store, product } = req.query;
  const m = svc.series.find((s) => s.store_id === Number(store) && s.product_id === Number(product));
  return m ? seriesInfo(m.sid) : null;
}));

// ------------------------------------------------------------------------------- one series in full
app.get('/api/series/:sid', wrap((req) => {
  const sid = sidOf(req.params.sid);
  const s = svc.seriesData(sid);
  const days = Array.from({ length: 37 }, (_, i) => 60 + i);
  const fc = svc.forecast(sid, days).map((r) => ({ d: r.d, models: r.models, donor: r.donor, actual: r.actual }));
  return { info: seriesInfo(sid), Y: s.Y, SO: s.SO, hours: s.hours, stock: s.stock, ctx: s.ctx, forecasts: fc };
}));

// ------------------------------------------------------------------------------- game: one store, one day
app.post('/api/game/day', wrap((req) => {
  const { storeId, d } = req.body;
  if (!FINAL.includes(d)) throw new Error('day must be in the held-out week');
  const list = svc.series.filter((m) => m.store_id === Number(storeId)).slice(0, 8);
  return list.map((m) => {
    const s = svc.seriesData(m.sid);
    const [f] = svc.forecast(m.sid, [d]);
    return {
      ...seriesInfo(m.sid), d, donor: f.donor, actual: f.actual, recorded: f.recorded, stockoutHours: f.stockoutHours,
      hours16: s.hours[d].slice(6, 22), stock16: s.stock[d].slice(6, 22), models: f.models, pools: f.pools,
      history: { Y: s.Y.slice(d - 21, d), SO: s.SO.slice(d - 21, d) },
    };
  });
}));

// ------------------------------------------------------------------------------- model x-ray
app.post('/api/xray', wrap((req) => {
  const sid = sidOf(req.body.sid);
  const d = Number(req.body.d);
  const overrides = req.body.overrides || null;
  const [base] = svc.forecast(sid, [d]);
  const [edit] = overrides && Object.keys(overrides).length ? svc.forecast(sid, [d], null, overrides) : [base];
  const b = svc.boosters.demand_q50;
  const trees = b.trees.map((_, i) => b.path(edit.x, i)).map((p) => ({ v: p.value, depth: p.nodes.length, f: p.nodes.map((n) => n.feature) }));
  const usage = {};
  trees.forEach((t) => new Set(t.f).forEach((f) => { usage[f] = (usage[f] || 0) + 1; })); // each tree counted once
  return {
    info: seriesInfo(sid), d, date: cfg.dates[d], features: cfg.features, baseX: base.x, x: edit.x,
    base: { models: base.models, raw: base.raw }, edit: { models: edit.models, raw: edit.raw, pools: edit.pools },
    actual: base.actual, donor: base.donor, shap: svc.shap(sid, d),
    trees: trees.map((t) => ({ v: t.v, depth: t.depth })), featureUsage: usage,
  };
}));

// ------------------------------------------------------------------------------- censoring lab
function labRun(sid, mech, forced = {}) {
  const s = svc.seriesData(sid);
  const hours16 = s.hours.map((h) => h.slice(6, 22));
  const activity = s.ctx.activity_flag;
  let cen = { Y: [...s.Y], SO: [...s.SO], detail: {} };
  if (mech && mech !== 'none') {
    cen = simulateSeries({ key: s.key, Y: s.Y, SO: s.SO, hours16, activity, params: svc.simParams, mech });
  }
  for (const [dk, frac] of Object.entries(forced)) {
    const d = Number(dk);
    if (s.SO[d] !== 0 || d >= 97) continue; // only full-stock days have known demand to censor
    const Q = Math.max(0, Number(frac)) * s.Y[d];
    const r = deplete(hours16[d], Q);
    cen.Y[d] = r.vis.reduce((a, b) => a + b, 0);
    cen.SO[d] = r.flag.reduce((a, b) => a + b, 0);
    cen.detail[d] = { Q, ...r, demand: hours16[d], forced: true };
  }
  const real = svc.forecast(sid, FINAL);
  const censored = svc.forecast(sid, FINAL, { Y: cen.Y, SO: cen.SO });
  return { s, cen, real, censored };
}

app.post('/api/censor', wrap((req) => {
  const sid = sidOf(req.body.sid);
  const { s, cen, real, censored } = labRun(sid, req.body.mech, req.body.forced || {});
  const pick = (r) => ({ d: r.d, models: r.models, actual: r.actual, donor: r.donor });
  return {
    info: seriesInfo(sid), trueY: s.Y, trueSO: s.SO, Y: cen.Y, SO: cen.SO, detail: cen.detail,
    hours16: s.hours.map((h) => h.slice(6, 22)), stock16: s.stock.map((h) => h.slice(6, 22)), activity: s.ctx.activity_flag,
    real: real.map(pick), censored: censored.map(pick),
  };
}));

app.post('/api/censor/batch', wrap((req) => {
  const mech = req.body.mech || 'A';
  const n = Math.min(Number(req.body.n) || 60, 200);
  let seed = Number(req.body.seed) || 7;
  const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
  const codes = ['demand_conformal', 'raw_quantile', 'seasonal_naive'];
  const acc = Object.fromEntries(codes.map((c) => [c, { realErr: 0, cenErr: 0, realSum: 0, cenSum: 0 }]));
  let actualSum = 0, rows = 0, censoredDays = 0;
  for (let i = 0; i < n; i++) {
    const sid = Math.floor(rnd() * cfg.n_series);
    const { s, cen, real, censored } = labRun(sid, mech);
    censoredDays += cen.SO.slice(0, 90).filter((v, d) => v > 0 && s.SO[d] === 0).length;
    real.forEach((r, k) => {
      if (!r.donor) return;
      rows++; actualSum += r.actual;
      codes.forEach((c) => {
        const a = r.models[c][1], b = censored[k].models[c][1];
        acc[c].realErr += Math.abs(a - r.actual); acc[c].cenErr += Math.abs(b - r.actual);
        acc[c].realSum += a; acc[c].cenSum += b;
      });
    });
  }
  return {
    mech, series: n, rows, censoredDays,
    models: codes.map((c) => ({
      code: c, wapeReal: acc[c].realErr / actualSum, wapeCen: acc[c].cenErr / actualSum,
      biasReal: (acc[c].realSum - actualSum) / actualSum, biasCen: (acc[c].cenSum - actualSum) / actualSum,
      shift: (acc[c].cenSum - acc[c].realSum) / acc[c].realSum,
    })),
  };
}));

// ------------------------------------------------------------------------------- newsvendor helper
app.post('/api/newsvendor', wrap((req) => {
  const { q, beta, D, cu, co } = req.body;
  const Q = orderAt(q, cfg.taus, beta);
  return { Q, ...(D == null ? {} : newsvendor(Q, D, cu, co)) };
}));

// ------------------------------------------------------------------------------- static
const pbi = path.join(ROOT, '..', 'planner', 'powerbi', 'screenshots');
if (fs.existsSync(pbi)) app.use('/pbi', express.static(pbi));
app.get('/api/pbi', wrap(() => (fs.existsSync(pbi) ? fs.readdirSync(pbi).filter((f) => f.endsWith('.png')) : [])));
const dist = path.join(ROOT, 'web', 'dist');
app.use(express.static(dist));
app.get('*', (req, res) => {
  const index = path.join(dist, 'index.html');
  if (fs.existsSync(index)) res.sendFile(index);
  else res.status(404).send('Front end not built yet: run `npm run build` (or `npm run dev` for development).');
});
app.listen(PORT, () => console.log(`Stockout Simulator on http://localhost:${PORT}`));
