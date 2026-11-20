// Censoring Lab: hide demand behind simulated stockouts (the paper's mechanisms A/B/C, or your own clicks),
// rebuild every feature from the censored history and watch the real models' forecasts react.
import { useEffect, useMemo, useState } from 'react';
import { api, C, fmt, useApp, MODEL_COLOR, MODEL_SHORT } from '../lib.js';
import { Panel, Seg, Slider, SeriesPicker, Loader } from '../ui.jsx';
import { TimeChart, HourChart } from '../charts.jsx';

const CODES = ['demand_conformal', 'raw_quantile', 'seasonal_naive'];

export default function Lab() {
  const meta = useApp((s) => s.meta), focusSid = useApp((s) => s.focusSid), set = useApp((s) => s.set);
  const [sid, setSid] = useState(focusSid);
  const [mech, setMech] = useState('A');
  const [forced, setForced] = useState({});
  const [frac, setFrac] = useState(0.5);
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [picked, setPicked] = useState(null);
  const [batch, setBatch] = useState(null);
  const [batchBusy, setBatchBusy] = useState(false);

  useEffect(() => {
    let live = true;
    setBusy(true);
    api('censor', { sid, mech: mech === 'manual' ? 'none' : mech, forced: mech === 'manual' ? forced : {} })
      .then((d) => { if (!live) return; setData(d); setBusy(false);
        setPicked((p) => (p != null ? p : Number(Object.keys(d.detail)[0] ?? 80))); })
      .catch(() => setBusy(false));
    return () => { live = false; };
  }, [sid, mech, forced]);

  const view = useMemo(() => {
    if (!data) return null;
    const cen = Object.keys(data.detail).map(Number);
    const shift = CODES.map((c) => {
      const a = data.real.reduce((s, r) => s + r.models[c][1], 0), b = data.censored.reduce((s, r) => s + r.models[c][1], 0);
      const don = data.real.map((r, i) => [r, data.censored[i]]).filter(([r]) => r.donor);
      const act = don.reduce((s, [r]) => s + r.actual, 0);
      const err = (k) => don.reduce((s, pair) => s + Math.abs(pair[k].models[c][1] - pair[0].actual), 0) / (act || 1);
      return { c, shift: b / a - 1, wReal: err(0), wCen: err(1), n: don.length };
    });
    return { cen, shift, hidden: cen.reduce((s, d) => s + (data.trueY[d] - data.Y[d]), 0) };
  }, [data]);

  const onPick = (d) => {
    setPicked(d);
    if (mech === 'manual' && data && data.trueSO[d] === 0) {
      setForced((f) => { const n = { ...f }; if (n[d] != null) delete n[d]; else n[d] = frac; return n; });
    }
  };
  const runBatch = async () => {
    setBatchBusy(true);
    try { setBatch(await api('censor/batch', { mech: mech === 'manual' || mech === 'none' ? 'A' : mech, n: 60, seed: 11 })); } finally { setBatchBusy(false); }
  };

  if (!meta) return <div className="page"><Loader /></div>;
  const P = meta.simParams;
  const det = data && picked != null ? data.detail[picked] : null;
  const dates = meta.dates;
  return (
    <div className="page grid fade-in" style={{ gap: 16 }}>
      <div className="hero">
        <div className="eyebrow">Censoring lab · the core problem of the project</div>
        <h1>Hide demand behind stockouts, then watch the model react.</h1>
        <p>On a day with no stockout, hourly sales are the true demand. Here the paper's simulator gives the shelf a limited stock and replays that day hour by hour; once the shelf is empty, demand still arrives but sales stop. The censored history is fed back through the real feature pipeline and both models re-forecast the held-out week.</p>
      </div>
      <div className="row">
        <SeriesPicker sid={sid} onChange={(v) => { setSid(v); set({ focusSid: v }); setForced({}); setPicked(null); setBatch(null); }} />
        <div className="spacer" />
        <Seg value={mech} onChange={(m) => { setMech(m); setPicked(null); }} options={[{ value: 'none', label: 'Real history' }, { value: 'A', label: 'Mechanism A' }, { value: 'B', label: 'B · promos' }, { value: 'C', label: 'C · no refill' }, { value: 'manual', label: '✋ Manual' }]} />
        {mech === 'manual' && <div style={{ width: 220 }}><Slider label="Stock as share of demand" value={frac} min={0} max={1} step={0.05} onChange={setFrac} display={fmt.pct} /></div>}
        {busy && <span className="loader" />}
      </div>

      <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <Panel><div className="kpi"><span className="label">Mechanism</span><span className="small" style={{ color: C.text2 }}>
          {mech === 'A' && `Stock = 14-day mean × e^(${P.sigma}·z), refill ${(P.p_refill * 100).toFixed(1)}% of days at +1–3 h with ${P.refill_frac * 100}% of stock.`}
          {mech === 'B' && `As A, but stock ×${P.promo_factor} on promotion days: promotions sell out more often.`}
          {mech === 'C' && `Stock = ${P.k_C} × 14-day mean × e^(${P.sigma_C}·z), never refilled: heavy censoring.`}
          {mech === 'none' && 'The recorded history as it is, with its real stockouts.'}
          {mech === 'manual' && 'Click full-stock days in the chart to give them only part of their demand as stock.'}
        </span></div></Panel>
        <Panel><div className="kpi"><span className="label">Days censored</span><span className="value">{view?.cen.length ?? '–'}</span><span className="note">of {data ? data.trueSO.filter((v) => v === 0).length : '–'} full-stock days</span></div></Panel>
        <Panel><div className="kpi"><span className="label">Demand hidden from the model</span><span className="value" style={{ color: C.red }}>{view ? view.hidden.toFixed(1) : '–'}</span><span className="note">units that customers wanted but could not buy</span></div></Panel>
        <Panel><div className="kpi"><span className="label">Forecast shift, held-out week (q50)</span>
          <span className="small">{view?.shift.map((s) => <div key={s.c} className="row" style={{ gap: 6 }}><span className="sw" style={{ background: MODEL_COLOR[s.c] }} />{MODEL_SHORT[s.c]}<span className="spacer" /><b className="mono" style={{ color: s.shift < -0.005 ? C.red : C.text }}>{fmt.spct(s.shift)}</b></div>)}</span></div></Panel>
      </div>

      <Panel title="97 days of this store-product" sub="Grey = what really happened · orange = what the model sees after censoring · × = day censored here · ○ = real stockout day. Click a day for its hour-by-hour view.">
        {data ? (
          <>
            <TimeChart n={97} height={290} xLabel={(i, short) => (short ? dates[i].slice(5) : fmt.date(dates[i]))} picked={picked} onPick={onPick}
              shade={[{ from: 90, to: 96, label: 'held-out week' }]}
              series={[{ key: 't', label: 'recorded sales', color: '#8b909b', values: data.trueY, width: 1.5 }, { key: 'v', label: 'visible after censoring', color: C.orange, values: data.Y }]}
              markers={[...view.cen.map((d) => ({ x: d, y: data.Y[d], color: C.red, shape: 'x' })), ...data.trueSO.map((v, d) => (v > 0 ? { x: d, y: data.trueY[d], color: C.red, hollow: true, r: 3.5 } : null)).filter(Boolean)]}
              extraTip={(i) => [{ label: data.trueSO[i] > 0 ? `real stockout ${data.trueSO[i]} h` : 'full stock (exact demand)', value: '' }]} />
            <div className="legend"><span><i className="sw" style={{ background: '#8b909b' }} />recorded sales</span><span><i className="sw" style={{ background: C.orange }} />visible to the model</span><span style={{ color: C.red }}>× censored here · ○ real stockout</span></div>
          </>
        ) : <Loader />}
      </Panel>

      <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <Panel title={picked != null ? `${fmt.date(dates[picked])} · hour by hour (06:00–22:00)` : 'Hour by hour'}
          sub={det ? `Opening stock ${det.Q.toFixed(2)} vs true demand ${det.demand.reduce((a, b) => a + b, 0).toFixed(2)}${det.first >= 0 ? ` · empty from ${fmt.hour(det.first + 6)}` : ' · never ran out'}` : 'Real recorded hours for this day (dashed = sales; on a real stockout day the true demand is unknown).'}>
          {data && picked != null && (det
            ? <HourChart demand={det.demand} visible={det.vis} stock={det.stockPath} flags={det.flag} q={det.Q} refillHour={det.refillHour} />
            : <HourChart demand={data.hours16[picked]} visible={data.hours16[picked]} flags={data.stock16[picked]} />)}
          <div className="legend"><span><i className="sw" style={{ border: '1px dashed #fff8' }} />true demand</span><span><i className="sw" style={{ background: C.blue }} />sales the model sees</span><span><i className="sw" style={{ background: C.aqua }} />stock on shelf</span><span><i className="sw" style={{ background: '#e6676740' }} />out of stock</span></div>
        </Panel>
        <Panel title="Held-out week: forecasts from real vs censored history" sub="Solid = forecast from the real history · dashed = forecast from the censored history · red dots = actual demand (full-stock days).">
          {data && (
            <TimeChart n={7} height={240} xLabel={(i) => fmt.date(dates[90 + i])}
              series={CODES.flatMap((c) => [
                { key: `${c}r`, label: `${MODEL_SHORT[c]} · real`, color: MODEL_COLOR[c], values: data.real.map((r) => r.models[c][1]) },
                { key: `${c}c`, label: `${MODEL_SHORT[c]} · censored`, color: MODEL_COLOR[c], values: data.censored.map((r) => r.models[c][1]), dash: '5 4' }])}
              markers={data.real.map((r, i) => (r.donor ? { x: i, y: r.actual, color: C.red } : null)).filter(Boolean)} />
          )}
          {view && (
            <table className="t" style={{ marginTop: 8 }}>
              <thead><tr><th>Model (q50)</th><th className="n">WAPE · real history</th><th className="n">WAPE · censored</th><th className="n">shift</th></tr></thead>
              <tbody>{view.shift.map((s) => <tr key={s.c}><td><span className="sw" style={{ background: MODEL_COLOR[s.c], marginRight: 8 }} />{MODEL_SHORT[s.c]}</td><td className="n">{s.n ? fmt.pct(s.wReal) : '–'}</td><td className="n">{s.n ? fmt.pct(s.wCen) : '–'}</td><td className="n">{fmt.spct(s.shift)}</td></tr>)}</tbody>
            </table>
          )}
        </Panel>
      </div>

      <Panel title="Scale it up: censor 60 random store-products" sub="Same mechanism on a random sample; scored on their full-stock days of the held-out week."
        right={<button className="btn primary" onClick={runBatch} disabled={batchBusy}>{batchBusy ? 'Running…' : `Run mechanism ${mech === 'manual' || mech === 'none' ? 'A' : mech}`}</button>}>
        {batchBusy && <Loader text="Rebuilding features and re-scoring 60 series × 7 days with 9 models…" />}
        {batch && !batchBusy && (
          <table className="t">
            <thead><tr><th>Model</th><th className="n">WAPE · real</th><th className="n">WAPE · censored</th><th className="n">bias · real</th><th className="n">bias · censored</th><th className="n">forecast shift</th></tr></thead>
            <tbody>{batch.models.map((m) => <tr key={m.code}><td><span className="sw" style={{ background: MODEL_COLOR[m.code], marginRight: 8 }} />{MODEL_SHORT[m.code]}</td>
              <td className="n">{fmt.pct(m.wapeReal)}</td><td className="n">{fmt.pct(m.wapeCen)}</td><td className="n">{fmt.spct(m.biasReal)}</td><td className="n">{fmt.spct(m.biasCen)}</td><td className="n" style={{ color: C.red }}>{fmt.spct(m.shift)}</td></tr>)}</tbody>
          </table>
        )}
        {batch && <p className="small muted">{batch.series} series · {batch.censoredDays.toLocaleString()} history days censored · {batch.rows} scored forecasts. Both models here were trained on the real recorded history, so heavier censoring at forecast time pulls their inputs down. The paper trains on censored histories and measures exactly this transfer gap.</p>}
      </Panel>
    </div>
  );
}
