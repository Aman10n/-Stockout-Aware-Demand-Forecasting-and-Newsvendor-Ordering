import { useEffect, useMemo, useState } from 'react';
import { api, C, fmt, useApp, MODEL_COLOR } from '../lib.js';
import { Panel, Kpi, Seg, Slider, Loader } from '../ui.jsx';
import { HBars } from '../charts.jsx';
import CityTowers from '../three/CityTowers.jsx';

const sum = (rows, k) => rows.reduce((a, r) => a + r[k], 0);

export default function Command() {
  const meta = useApp((s) => s.meta), setPage = useApp((s) => s.setPage);
  const [net, setNet] = useState(null);
  const [pbi, setPbi] = useState([]);
  const [scen, setScen] = useState(2);
  const [ratio, setRatio] = useState(1);
  const [city, setCity] = useState(null);
  const [zoom, setZoom] = useState(null);
  useEffect(() => { api('network').then(setNet); api('pbi').then(setPbi); }, []);

  const codeOf = useMemo(() => Object.fromEntries((meta?.models || []).map((m) => [m.model_key, m])), [meta]);
  const view = useMemo(() => {
    if (!net) return null;
    const orders = net.orders.filter((r) => r.scenario_key === scen && (!city || r.city === city));
    const byPol = [1, 2, 3, 4, 5].map((k) => {
      const rows = orders.filter((r) => r.policy_key === k);
      const n = sum(rows, 'n');
      return { k, n, fill: sum(rows, 'sold') / sum(rows, 'demand'), cost: sum(rows, 'cost') / n,
        whatif: (ratio * sum(rows, 'short') + sum(rows, 'left')) / n, leftShare: sum(rows, 'left') / sum(rows, 'ordered') };
    });
    const cities = net.cities.map((c) => {
      const o = net.orders.filter((r) => r.scenario_key === scen && r.city === c.city);
      const cost = (k) => sum(o.filter((r) => r.policy_key === k), 'cost');
      return { ...c, saving: 1 - cost(1) / cost(5) };
    });
    const cs = city ? net.cities.filter((c) => c.city === city) : net.cities;
    const stockout = cs.reduce((a, c) => a + c.stockout_rate * c.series, 0) / sum(cs, 'series');
    const acc = net.accuracy.filter((r) => r.model_key === 1 && (!city || r.city === city));
    const paper = net.paper.filter((r) => r.scenario_key === scen && r.matched_cell === 1);
    const pol = [...new Set(paper.map((r) => r.policy))].map((p) => {
      const rows = paper.filter((r) => r.policy === p);
      return { policy: p, deep: rows[0].population === 'deep subsample', cost: sum(rows, 'mean_cost') / rows.length,
        whatif: (ratio * sum(rows, 'total_shortage') + sum(rows, 'total_leftover')) / sum(rows, 'n') };
    }).sort((a, b) => a.whatif - b.whatif);
    return { byPol, cities, stockout, accuracy: 1 - sum(acc, 'abs_err') / sum(acc, 'actual'), paper: pol };
  }, [net, scen, ratio, city]);

  if (!view || !meta) return <div className="page"><Loader text="Loading network…" /></div>;
  const head = view.byPol[0], sn = view.byPol[4];
  const race = [...view.byPol].sort((a, b) => a.whatif - b.whatif);
  const raceMax = Math.max(...race.map((r) => r.whatif));
  return (
    <div className="page grid fade-in" style={{ gap: 18 }}>
      <div className="hero row" style={{ alignItems: 'flex-end' }}>
        <div>
          <div className="eyebrow">Stockout-aware demand forecasting · FreshRetailNet-50K · 5,000 store-products</div>
          <h1>When a shelf runs empty, sales stop telling the truth.</h1>
          <p>Every number here is computed by the real trained LightGBM models ({meta.engine.models} models, {meta.engine.trees.toLocaleString()} trees) running in this app's engine, verified to match Python to the last bit. Held-out week: 26 Jun – 2 Jul 2024.</p>
        </div>
        <div className="spacer" />
        <div className="row">
          <button className="btn go" onClick={() => setPage('game')}>▶ Run the store</button>
          <button className="btn" onClick={() => setPage('lab')}>Censoring lab</button>
          <button className="btn" onClick={() => setPage('xray')}>Model X-ray</button>
        </div>
      </div>

      <div className="row">
        <Seg value={scen} onChange={setScen} options={meta.scenarios.map((s) => ({ value: s.scenario_key, label: s.scenario_name }))} />
        <div style={{ width: 330 }}>
          <Slider label="What-if: cost of a unit short ÷ cost of a unit left over" value={ratio} min={0.25} max={5} step={0.25} onChange={setRatio} display={(v) => `${v.toFixed(2)}×`} />
        </div>
        <div className="spacer" />
        {city ? <span className="tag">{city} <button className="btn sm ghost" onClick={() => setCity(null)}>✕</button></span> : <span className="muted small">All 18 cities · click a tower to filter</span>}
      </div>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <Kpi label="Fill rate · stockout-aware policy" value={fmt.pct(head.fill)} note={`seasonal naive ${fmt.pct(sn.fill)}`} />
        <Kpi label="Observed stockout rate (97 days)" value={fmt.pct(view.stockout)} note="store-product-days with ≥1 empty hour" color={C.red} />
        <Kpi label="Forecast accuracy (1 − WAPE, q50)" value={fmt.pct(view.accuracy)} note="full-stock days, held-out week" />
        <Kpi label="Cost saving vs seasonal naive" value={fmt.pct(1 - head.cost / sn.cost)} note={`waste ${fmt.pct(head.leftShare)} of orders vs ${fmt.pct(sn.leftShare)}`} color={C.aqua} />
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1.25fr 1fr' }}>
        <CityTowers cities={view.cities} selected={city} onSelect={setCity} height={460} />
        <Panel title="Policy race" sub={`Orders placed for "${meta.scenarios[scen - 1].scenario_name}", re-scored at a ${ratio.toFixed(2)}× shortage cost. Lower is better.`}>
          <div className="grid" style={{ gap: 10, marginTop: 6 }}>
            {race.map((r, i) => (
              <div key={r.k} className="race-row">
                <div className="small" style={{ color: i === 0 ? C.text : C.text2, fontWeight: i === 0 ? 700 : 500 }}>{i === 0 ? '🏆 ' : `${i + 1}. `}{codeOf[r.k].model_name}</div>
                <div style={{ background: '#ffffff08', borderRadius: 6 }}><div className="race-bar" style={{ width: `${(r.whatif / raceMax) * 100}%`, background: MODEL_COLOR[codeOf[r.k].model_code] }} /></div>
                <div className="mono small" style={{ textAlign: 'right' }}>{r.whatif.toFixed(3)}</div>
              </div>
            ))}
          </div>
          <table className="t" style={{ marginTop: 16 }}>
            <thead><tr><th>Policy</th><th className="n">Fill rate</th><th className="n">Waste share</th><th className="n">Cost</th><th className="n">vs naive</th></tr></thead>
            <tbody>
              {view.byPol.map((r) => (
                <tr key={r.k} className={r.k === 1 ? 'hl' : ''}><td><span className="sw" style={{ background: MODEL_COLOR[codeOf[r.k].model_code], marginRight: 8 }} />{codeOf[r.k].model_name}</td>
                  <td className="n">{fmt.pct(r.fill)}</td><td className="n">{fmt.pct(r.leftShare)}</td><td className="n">{r.cost.toFixed(3)}</td><td className="n">{fmt.spct(r.cost / sn.cost - 1)}</td></tr>
              ))}
            </tbody>
          </table>
          <p className="small muted" style={{ marginTop: 10 }}>Scored on {sum(net.orders.filter((r) => r.scenario_key === scen && r.policy_key === 1 && (!city || r.city === city)), 'n').toLocaleString()} store-product-days with full stock (exact demand). Costs in relative units.</p>
        </Panel>
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <Panel title="The paper: 9 ordering policies under simulated stockouts" sub="Run E, models trained on histories censored by mechanisms A/B/C, matched train/test cells, same what-if ratio.">
          <HBars rows={view.paper.map((p, i) => ({ label: `${p.policy}${p.deep ? ' *' : ''}`, value: p.whatif, color: i === 0 ? C.blue : '#3a4458', strong: i === 0 }))} />
          <p className="small muted">* TFT policies were scored on a 600-series subset only.</p>
        </Panel>
        <Panel title="Power BI report" sub="The planning manager's view of the same star schema: KPIs, drill-through, row-level security by city.">
          <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
            {pbi.map((f) => (
              <button key={f} className="btn ghost" style={{ padding: 0, overflow: 'hidden' }} onClick={() => setZoom(f)} title={f}>
                <img src={`/pbi/${f}`} alt={f} style={{ width: '100%', display: 'block' }} />
              </button>
            ))}
          </div>
          {!pbi.length && <p className="muted small">Screenshots appear here once planner/powerbi/screenshots exists.</p>}
        </Panel>
      </div>
      {zoom && <div className="modal" onClick={() => setZoom(null)}><img src={`/pbi/${zoom}`} alt={zoom} /></div>}
    </div>
  );
}
