// Model X-ray: one store-product-day, all 33 inputs exposed. Drag an input and the real models re-score.
import { useEffect, useMemo, useRef, useState } from 'react';
import { api, C, fmt, useApp, MODEL_COLOR, MODEL_SHORT, orderAt } from '../lib.js';
import { Panel, Slider, SeriesPicker, Loader, Kpi, Seg } from '../ui.jsx';
import { Fan, HBars } from '../charts.jsx';
import Forest from '../three/Forest.jsx';

export const NAMES = {
  y_lag1: 'sales yesterday', y_lag2: 'sales 2 days ago', y_lag7: 'sales same weekday last week', y_lag14: 'sales 2 weeks ago',
  y_roll7: '7-day average sales', y_roll14: '14-day average sales', y_roll28: '28-day average sales', y_std14: '14-day volatility',
  y_ewm: 'smoothed sales level', y_dow_mean: 'average for this weekday', y_don_roll14: '14-day avg on full-stock days',
  y_don_roll28: '28-day avg on full-stock days', so_lag1: 'stockout hours yesterday', so_rate7: '7-day stockout rate',
  so_rate14: '14-day stockout rate', don_frac7: 'full-stock share, 7 days', disc_lag1: 'discount yesterday', disc_roll7: '7-day avg discount',
  act_lag1: 'promotion yesterday', act_roll7: '7-day promotion share', hol_lag1: 'holiday yesterday', precpt_lag1: 'rain yesterday',
  temp_lag1: 'temperature yesterday', dow: 'weekday (0 = Mon)', is_weekend: 'weekend', n_hist_days: 'days of history',
  city_id: 'city', store_id: 'store', product_id: 'product', management_group_id: 'management group', first_category_id: 'category',
  second_category_id: 'sub-category', third_category_id: 'leaf category',
};
const GROUPS = [
  ['Sales history', ['y_lag1', 'y_lag2', 'y_lag7', 'y_lag14', 'y_roll7', 'y_roll14', 'y_roll28', 'y_std14', 'y_ewm', 'y_dow_mean', 'y_don_roll14', 'y_don_roll28']],
  ['Stockout history', ['so_lag1', 'so_rate7', 'so_rate14', 'don_frac7']],
  ['Promotions & weather', ['disc_lag1', 'disc_roll7', 'act_lag1', 'act_roll7', 'hol_lag1', 'precpt_lag1', 'temp_lag1']],
  ['Calendar', ['dow', 'is_weekend']],
];
function range(f, base) {
  const b = Number.isFinite(base) ? base : 0;
  if (['so_rate7', 'so_rate14', 'don_frac7', 'disc_lag1', 'disc_roll7', 'act_roll7'].includes(f)) return [0, 1, 0.01];
  if (['act_lag1', 'hol_lag1', 'is_weekend'].includes(f)) return [0, 1, 1];
  if (f === 'so_lag1') return [0, 16, 1];
  if (f === 'dow') return [0, 6, 1];
  if (f === 'temp_lag1') return [-10, 40, 0.5];
  if (f === 'precpt_lag1') return [0, Math.max(60, b * 2), 0.5];
  return [0, Math.max(5, Math.ceil(b * 3)), 0.05];
}

export default function XRay() {
  const meta = useApp((s) => s.meta), focusSid = useApp((s) => s.focusSid), set = useApp((s) => s.set), cu = useApp((s) => s.cu), co = useApp((s) => s.co);
  const beta = cu / (cu + co);
  const [sid, setSid] = useState(focusSid);
  const [d, setD] = useState(90);
  const [ov, setOv] = useState({});
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const timer = useRef(null);

  useEffect(() => {
    clearTimeout(timer.current);
    setBusy(true);
    timer.current = setTimeout(() => {
      api('xray', { sid, d, overrides: ov }).then((r) => { setRes(r); setBusy(false); }).catch(() => setBusy(false));
    }, 180);
  }, [sid, d, ov]);

  const shapRows = useMemo(() => {
    if (!res?.shap) return [];
    return res.features.map((f, i) => ({ f, v: res.shap[i], x: res.baseX[i] }))
      .sort((a, b) => Math.abs(b.v) - Math.abs(a.v)).slice(0, 10)
      .map((r) => ({ label: `${NAMES[r.f] || r.f} = ${Number.isFinite(r.x) ? +r.x.toFixed(2) : 'n/a'}`, value: r.v, color: r.v >= 0 ? C.blue : C.orange }));
  }, [res]);
  const usage = useMemo(() => (res ? Object.entries(res.featureUsage).sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([f, n]) => ({ label: NAMES[f] || f, value: n, color: '#4a5878' })) : []), [res]);

  if (!meta) return <div className="page"><Loader /></div>;
  const codes = meta.models.map((m) => m.model_code);
  const b50 = res?.base.models.demand_conformal[1], e50 = res?.edit.models.demand_conformal[1];
  const bQ = res && orderAt(res.base.models.demand_conformal, beta), eQ = res && orderAt(res.edit.models.demand_conformal, beta);
  const edited = Object.keys(ov).length > 0;
  const idx = (f) => res.features.indexOf(f);
  return (
    <div className="page grid fade-in" style={{ gap: 16 }}>
      <div className="hero">
        <div className="eyebrow">Model X-ray · demand-quantile LightGBM + pooled conformal</div>
        <h1>Open the model. Pull a lever. Watch 4,008 trees re-vote.</h1>
        <p>These are the exact 33 inputs the model receives for one store-product on one held-out day, all computed from days before it. Change any of them and the real boosters re-score instantly: quantiles, the conformal shift and the newsvendor order.</p>
      </div>
      <div className="row">
        <SeriesPicker sid={sid} onChange={(v) => { setSid(v); set({ focusSid: v }); setOv({}); }} />
        <Seg value={d} onChange={(v) => { setD(v); setOv({}); }} options={meta.dates.slice(90).map((ds, i) => ({ value: 90 + i, label: fmt.date(ds).slice(0, 6) }))} />
        <div className="spacer" />
        {busy && <span className="loader" />}
        <button className="btn sm" onClick={() => setOv({})} disabled={!edited}>Reset inputs</button>
      </div>

      {!res ? <Loader /> : (
        <>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            <Kpi label="Median forecast (q50)" value={fmt.n(e50)} note={edited ? `was ${fmt.n(b50)} (${fmt.spct(e50 / b50 - 1)})` : 'calibrated, units 06:00–22:00'} color={edited ? C.blue : undefined} />
            <Kpi label={`Newsvendor order at β = ${beta.toFixed(2)}`} value={fmt.n(eQ)} note={edited ? `was ${fmt.n(bQ)}` : 'β-quantile of the forecast'} />
            <Kpi label="80% interval (q25 – q90)" value={`${fmt.n(res.edit.models.demand_conformal[0], 1)} – ${fmt.n(res.edit.models.demand_conformal[3], 1)}`} note={`conformal pool: ${res.edit.pools.demand_conformal}`} />
            <Kpi label="What really happened" value={res.donor ? fmt.n(res.actual) : 'censored'} note={res.donor ? 'true demand (full-stock day)' : 'the store sold out: demand unknown'} color={res.donor ? C.red : C.yellow} />
          </div>
          <div className="grid" style={{ gridTemplateColumns: '360px 1fr' }}>
            <Panel title="Inputs" sub="Blue = you changed it. Identity features (city, store, product, category) are fixed.">
              <div className="grid" style={{ gap: 14, maxHeight: 760, overflow: 'auto', paddingRight: 6 }}>
                {GROUPS.map(([g, fs]) => (
                  <div key={g} className="grid" style={{ gap: 8 }}>
                    <div className="eyebrow" style={{ color: C.muted }}>{g}</div>
                    {fs.map((f) => {
                      const base = res.baseX[idx(f)], val = ov[f] ?? base, [mn, mx, st] = range(f, base);
                      return (
                        <div key={f} style={{ borderLeft: `3px solid ${ov[f] != null ? C.blue : 'transparent'}`, paddingLeft: 8 }}>
                          <Slider label={NAMES[f]} value={Number.isFinite(val) ? val : mn} min={mn} max={mx} step={st}
                            display={() => (Number.isFinite(val) ? (+val).toFixed(st >= 1 ? 0 : 2) : 'missing')}
                            onChange={(v) => setOv((o) => ({ ...o, [f]: v }))} />
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </Panel>
            <div className="grid" style={{ alignContent: 'start' }}>
              <Panel title="All five forecast models for this day" sub="Bar = q25–q90 (darker q25–q75), white tick = q50, triangle = order at β, red line = actual demand.">
                <Fan actual={res.donor ? res.actual : null}
                  rows={codes.map((c) => ({ label: MODEL_SHORT[c], q: res.edit.models[c], color: MODEL_COLOR[c], order: orderAt(res.edit.models[c], beta) }))} />
              </Panel>
              <div className="grid" style={{ gridTemplateColumns: '1.1fr 1fr' }}>
                <Panel title="The q50 model as a forest" sub={`${res.trees.length} trees. Height = the leaf value this row lands in · blue up, orange down. Sum = ${res.edit.raw.demand_q50.toFixed(3)} before the conformal shift.`}>
                  <Forest values={res.trees.map((t) => t.v)} height={300} />
                </Panel>
                <Panel title="Why: SHAP contributions (unedited row)" sub={res.shap ? `TreeSHAP from LightGBM. Baseline ${res.shap[res.shap.length - 1].toFixed(2)} + contributions = ${res.base.raw.demand_q50.toFixed(2)}.` : ''}>
                  <HBars rows={shapRows} format={(v) => `${v >= 0 ? '+' : ''}${v.toFixed(2)}`} height={24} />
                </Panel>
              </div>
              <Panel title="Features on this row's decision paths" sub="How many of the 208 trees asked about each feature to place this row.">
                <HBars rows={usage} format={(v) => `${v} trees`} height={22} />
              </Panel>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
