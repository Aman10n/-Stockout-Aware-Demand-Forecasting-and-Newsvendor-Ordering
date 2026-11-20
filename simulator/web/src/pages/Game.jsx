// Run the Store: the paper's held-out-week protocol as a game. Each morning the real model forecasts every
// shelf from the real history up to yesterday; you order; the day plays out hour by hour against the product's
// real hourly demand. Days on which the real store sold out have no known demand and are not scored.
import { useEffect, useMemo, useRef, useState } from 'react';
import { api, C, fmt, useApp, PALETTE, MODEL_COLOR, orderAt, deplete, newsvendor } from '../lib.js';
import { Panel, Slider, CostControls, Seg, Loader, Kpi } from '../ui.jsx';
import { Fan, Spark, TimeChart } from '../charts.jsx';
import StoreScene from '../three/StoreScene.jsx';

const DAYS = [90, 91, 92, 93, 94, 95, 96];
const POL = { you: { label: 'You', color: C.aqua }, ai: { label: 'AI · stockout-aware + conformal', color: C.blue }, base: { label: 'Seasonal naive', color: C.yellow }, raw: { label: 'Raw-sales quantile', color: C.orange } };
const emptyScore = () => Object.fromEntries(Object.keys(POL).map((k) => [k, { cost: 0, short: 0, left: 0, sold: 0, demand: 0 }]));

export default function Game() {
  const meta = useApp((s) => s.meta), cu = useApp((s) => s.cu), co = useApp((s) => s.co);
  const beta = cu / (cu + co);
  // busy stores first (a store with no sales has no stockouts and would look 'fully scored'), with enough scored shelf-days
  const stores = useMemo(() => (meta ? meta.stores.filter((s) => s.products >= 4 && s.products <= 8 && s.sales / s.products >= 0.8 && s.scored_days / s.products >= 3)
    .sort((a, b) => b.sales - a.sales).slice(0, 40) : []), [meta]);
  const [storeId, setStoreId] = useState(null);
  const [phase, setPhase] = useState('setup');
  const [day, setDay] = useState(0);
  const [prods, setProds] = useState(null);
  const [orders, setOrders] = useState({});
  const [hour, setHour] = useState(null);
  const [speed, setSpeed] = useState(1);
  const [customers, setCustomers] = useState([]);
  const [feed, setFeed] = useState([]);
  const [result, setResult] = useState(null);
  const [score, setScore] = useState(emptyScore());
  const [daily, setDaily] = useState([]);
  const sim = useRef(null);
  const cid = useRef(0);

  // ?store=891 in the URL pre-selects a store (handy for a rehearsed demo)
  const urlStore = Number(new URLSearchParams(window.location.search).get('store')) || null;
  const options = useMemo(() => {
    const extra = urlStore && !stores.some((s) => s.store_id === urlStore) ? meta?.stores.filter((s) => s.store_id === urlStore) ?? [] : [];
    return [...extra, ...stores];
  }, [stores, urlStore, meta]);
  useEffect(() => { if (!storeId && options.length) setStoreId(urlStore && options.some((s) => s.store_id === urlStore) ? urlStore : options[0].store_id); }, [options, storeId, urlStore]);

  const loadDay = async (i) => {
    setProds(null);
    const p = await api('game/day', { storeId, d: DAYS[i] });
    setProds(p.map((x, k) => ({ ...x, color: PALETTE[k % PALETTE.length], ai: orderAt(x.models.demand_conformal, beta), base: orderAt(x.models.seasonal_naive, beta), raw: orderAt(x.models.raw_quantile, beta) })));
    setOrders(Object.fromEntries(p.map((x) => [x.sid, Math.round(orderAt(x.models.demand_conformal, beta) * 10) / 10])));
    setHour(null); setCustomers([]); setFeed([]); setResult(null);
  };

  const start = () => { setScore(emptyScore()); setDaily([]); setDay(0); setPhase('morning'); loadDay(0); };

  // ------------------------------------------------------------------ the day plays out
  const openStore = () => {
    const plan = prods.map((p) => {
      if (p.donor) {
        const Q = orders[p.sid] ?? 0;
        return { ...p, Q, run: deplete(p.hours16, Q), demand: p.hours16 };
      }
      // real stockout day: replay what the real store recorded (true demand unknown)
      const tot = p.hours16.reduce((a, b) => a + b, 0) || 1;
      let cum = 0;
      const stockPath = p.hours16.map((v, h) => { cum += v; return p.stock16[h] ? 0 : Math.max(0, 1 - cum / tot) * tot; });
      return { ...p, Q: tot, run: { vis: p.hours16, flag: p.stock16, stockPath, first: p.stock16.indexOf(1) }, demand: p.hours16 };
    });
    const unit = Math.max(...plan.map((p) => p.demand.reduce((a, b) => a + b, 0))) / 16 || 1;
    sim.current = { plan, unit, h: 0, announced: new Set() };
    setPhase('open'); setHour(6);
  };

  useEffect(() => {
    if (phase !== 'open' || !sim.current) return undefined;
    const t = setInterval(() => {
      const s = sim.current;
      if (s.h >= 16) { clearInterval(t); finishDay(); return; }
      const h = s.h;
      const spawn = [], events = [];
      s.plan.forEach((p, idx) => {
        const d = p.demand[h], v = p.run.vis[h];
        const count = Math.min(3, Math.round(d / s.unit) || (d > 0.05 ? 1 : 0));
        const lostN = d > 0 ? Math.round((count * (d - v)) / d) || (d - v > 0.05 && p.donor ? 1 : 0) : 0;
        for (let k = 0; k < count; k++) spawn.push({ id: cid.current++, idx, lost: k < lostN, color: p.color });
        if (p.run.flag[h] && !s.announced.has(p.sid)) {
          s.announced.add(p.sid);
          events.push(p.donor
            ? { out: true, text: `${fmt.hour(h + 6)} · ${p.product} sold out. Your order was ${p.Q.toFixed(1)}; customers are walking away.` }
            : { out: false, text: `${fmt.hour(h + 6)} · ${p.product}: the real store sold out here, so true demand is unknown (not scored).` });
        }
      });
      setCustomers((c) => [...c, ...spawn].slice(-70));
      if (events.length) setFeed((f) => [...events, ...f].slice(0, 30));
      s.h = h + 1;
      setHour(6 + s.h);
    }, 1300 / speed);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, speed]);

  const finishDay = () => {
    const { plan } = sim.current;
    const rows = plan.filter((p) => p.donor).map((p) => {
      const D = p.actual;
      return { p, D, you: newsvendor(p.Q, D, cu, co), ai: newsvendor(p.ai, D, cu, co), base: newsvendor(p.base, D, cu, co), raw: newsvendor(p.raw, D, cu, co) };
    });
    const tot = Object.fromEntries(Object.keys(POL).map((k) => [k, rows.reduce((a, r) => a + r[k].cost, 0)]));
    setScore((sc) => {
      const n = structuredClone(sc);
      rows.forEach((r) => Object.keys(POL).forEach((k) => {
        n[k].cost += r[k].cost; n[k].short += r[k].short; n[k].left += r[k].left; n[k].sold += r[k].sold; n[k].demand += r.D;
      }));
      return n;
    });
    setDaily((dl) => [...dl, { d: DAYS[day], ...tot }]);
    setResult({ rows, tot, censored: plan.filter((p) => !p.donor) });
    setPhase('close'); setHour(22);
  };

  const next = () => {
    if (day >= 6) { setPhase('final'); return; }
    setDay(day + 1); setPhase('morning'); loadDay(day + 1);
  };

  // ------------------------------------------------------------------ 3D props
  const scene = useMemo(() => {
    if (!prods) return [];
    const h = hour == null ? -1 : hour - 7;
    return prods.map((p) => {
      const plan = sim.current?.plan?.find((x) => x.sid === p.sid);
      if (!plan || h < 0 || phase === 'morning') {
        const Q = p.donor ? orders[p.sid] ?? 0 : 1;
        return { sid: p.sid, name: p.product, color: p.color, frac: p.donor ? Math.min(1, Q / Math.max(p.models.demand_conformal[3], 0.1)) : 0.8, stock: Q, out: false, censored: !p.donor };
      }
      const hh = Math.min(h, 15);
      const stock = plan.run.stockPath[hh];
      const out = plan.run.flag.slice(0, hh + 1).some(Boolean) && stock <= 1e-9;
      return { sid: p.sid, name: p.product, color: p.color, frac: plan.Q > 0 ? stock / plan.Q : 0, stock, out, censored: !p.donor };
    });
  }, [prods, hour, orders, phase]);

  if (!meta) return <div className="page"><Loader /></div>;

  // ------------------------------------------------------------------ setup screen
  if (phase === 'setup') {
    const st = options.find((s) => s.store_id === storeId);
    return (
      <div className="page grid fade-in" style={{ gap: 18 }}>
        <div className="hero">
          <div className="eyebrow">Game · the paper's held-out-week protocol</div>
          <h1>Run a real fresh-food store for one week. Can you beat the model?</h1>
          <p>Every morning the stockout-aware LightGBM model forecasts each shelf from the real sales history up to yesterday. You decide how much to order. Then the store opens and customers arrive following that product's <b>real hourly demand</b> from the dataset. Run out and they walk away (lost sales); over-order and the rest is thrown away at closing (waste).</p>
        </div>
        <div className="grid" style={{ gridTemplateColumns: '1.2fr 1fr' }}>
          <Panel title="1 · Pick your store" sub="Real stores from the 5,000-series sample, busiest first. A scored shelf-day is one where demand is fully known.">
            <select style={{ width: '100%', marginBottom: 12 }} value={storeId ?? ''} onChange={(e) => setStoreId(Number(e.target.value))}>
              {options.map((s) => <option key={s.store_id} value={s.store_id}>{s.city} · {s.store} · {s.products} products · {s.scored_days} scored shelf-days · {(s.sales / s.products).toFixed(1)} units/product/day</option>)}
            </select>
            {st && <div className="row small muted">Each scored shelf-day is a day on which the real store never ran out, so the full demand is known. Days with a real stockout are shown but excluded, exactly as in the paper.</div>}
          </Panel>
          <Panel title="2 · Set the economics" sub="The newsvendor rule orders the demand quantile at β = c_u / (c_u + c_o).">
            <CostControls />
          </Panel>
        </div>
        <div className="row">
          <button className="btn go" style={{ fontSize: 16, padding: '12px 26px' }} onClick={start} disabled={!storeId}>▶ Start the week</button>
          <span className="muted small">7 days · 26 Jun – 2 Jul 2024 · scored against the AI, the seasonal-naive baseline and a raw-sales model</span>
        </div>
      </div>
    );
  }

  // ------------------------------------------------------------------ final screen
  if (phase === 'final') {
    const ratio = score.you.cost / score.ai.cost;
    const grade = ratio < 0.97 ? ['You beat the model', C.aqua] : ratio <= 1.03 ? ['Dead heat with the model', C.blue] : ['The model wins this week', C.orange];
    return (
      <div className="page grid fade-in" style={{ gap: 18 }}>
        <div className="hero"><div className="eyebrow">Week complete</div><div className="grade" style={{ color: grade[1] }}>{grade[0]}</div>
          <p>Your total cost was {fmt.spct(ratio - 1)} vs the AI. Lower cost is better: cost = {cu} × units short + {co} × units wasted.</p></div>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
          {Object.entries(POL).map(([k, v]) => (
            <Kpi key={k} label={v.label} value={score[k].cost.toFixed(2)} color={v.color}
              note={`fill ${fmt.pct(score[k].sold / score[k].demand)} · short ${score[k].short.toFixed(1)} · waste ${score[k].left.toFixed(1)}`} />
          ))}
        </div>
        <Panel title="Daily cost" sub="Scored shelf-days only">
          <TimeChart n={daily.length} xLabel={(i) => fmt.date(meta.dates[daily[i].d])} height={260}
            series={Object.entries(POL).map(([k, v]) => ({ key: k, label: v.label, color: v.color, values: daily.map((r) => r[k]), width: k === 'you' ? 3 : 2 }))} />
          <div className="legend">{Object.entries(POL).map(([k, v]) => <span key={k}><i className="sw" style={{ background: v.color }} />{v.label}</span>)}</div>
        </Panel>
        <div className="row"><button className="btn primary" onClick={() => setPhase('setup')}>Play another store</button></div>
      </div>
    );
  }

  // ------------------------------------------------------------------ in-game
  const date = meta.dates[DAYS[day]];
  return (
    <div className="page grid fade-in" style={{ gap: 14 }}>
      <div className="row">
        <div>
          <div className="eyebrow">Day {day + 1} of 7 · {fmt.date(date)}</div>
          <h2 style={{ margin: '2px 0 0' }}>{prods?.[0]?.city} · {prods?.[0]?.store}</h2>
        </div>
        <div className="spacer" />
        <div className="hud">
          <div className="panel" style={{ padding: '8px 16px' }}><div className="muted small">Store clock</div><div className="clock mono">{hour == null ? '05:30' : fmt.hour(Math.min(hour, 22))}</div></div>
          {Object.entries(POL).slice(0, 3).map(([k, v]) => (
            <div key={k} className="panel" style={{ padding: '8px 16px' }}><div className="muted small">{v.label.split(' ·')[0]} · week cost</div><div className="big mono" style={{ color: v.color }}>{score[k].cost.toFixed(2)}</div></div>
          ))}
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1fr 340px' }}>
        {prods ? <StoreScene products={scene} customers={customers} speed={speed} hour={hour} /> : <div className="stage" style={{ height: 470 }}><Loader text="The model is forecasting today's shelves…" /></div>}
        <div className="grid" style={{ alignContent: 'start' }}>
          {phase === 'morning' && (
            <Panel title="Morning briefing" sub={`β = ${beta.toFixed(2)}. The AI orders the β-quantile of its demand forecast.`}>
              <div className="grid" style={{ gap: 8 }}>
                <div className="row"><button className="btn sm" onClick={() => setOrders(Object.fromEntries(prods.map((p) => [p.sid, +p.ai.toFixed(1)])))}>Use AI orders</button>
                  <button className="btn sm" onClick={() => setOrders(Object.fromEntries(prods.map((p) => [p.sid, +p.base.toFixed(1)])))}>Use seasonal naive</button></div>
                <button className="btn go" onClick={openStore} disabled={!prods}>▶ Open the store</button>
              </div>
            </Panel>
          )}
          {phase === 'open' && (
            <Panel title="Live" right={<Seg value={speed} onChange={setSpeed} options={[{ value: 1, label: '1×' }, { value: 2, label: '2×' }, { value: 4, label: '4×' }]} />}>
              <div className="feed">{feed.length ? feed.map((f, i) => <div key={i} className={f.out ? 'out' : ''}>{f.text}</div>) : <div className="muted">Doors open 06:00. Watching the shelves…</div>}</div>
            </Panel>
          )}
          {phase === 'close' && result && (
            <Panel title="Closing time" sub="Today's cost on scored shelves (lower is better)">
              {Object.entries(POL).map(([k, v]) => (
                <div key={k} className="row" style={{ padding: '4px 0' }}><span className="sw" style={{ background: v.color }} /><span className="small">{v.label}</span><span className="spacer" /><b className="mono">{result.tot[k].toFixed(2)}</b></div>
              ))}
              <button className="btn primary" style={{ marginTop: 10, width: '100%' }} onClick={next}>{day >= 6 ? 'See the week results' : 'Next day ▶'}</button>
            </Panel>
          )}
          <Panel title="How the model sees today" sub="Forecast from real history up to yesterday — the paper's sequential protocol.">
            <div className="legend small">
              <span><i className="sw" style={{ background: C.blue }} />AI</span><span><i className="sw" style={{ background: C.yellow }} />seasonal naive</span><span><i className="sw" style={{ background: C.orange }} />raw-sales</span><span><i className="sw" style={{ background: C.red }} />actual (after close)</span>
            </div>
          </Panel>
        </div>
      </div>

      {prods && (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(330px, 1fr))' }}>
          {prods.map((p) => {
            const res = result?.rows.find((r) => r.p.sid === p.sid);
            const maxQ = Math.ceil(Math.max(p.models.demand_conformal[3], p.models.seasonal_naive[3], p.models.raw_quantile[3], 1) * 1.7);
            return (
              <div key={p.sid} className={`pcard ${p.donor ? '' : 'cen'}`}>
                <div className="hd"><span className="sw" style={{ background: p.color }} /><b>{p.product}</b><span className="muted small">{p.category}</span><span className="spacer" />
                  {p.donor ? <span className="tag good">scored</span> : <span className="tag warn">real stockout · {p.stockoutHours}h</span>}</div>
                <div className="row small muted"><span>last 21 days</span><Spark values={p.history.Y} flags={p.history.SO.map((v) => v > 0)} width={150} /><span>● = sold out</span></div>
                <Fan height={26} actual={phase === 'close' && p.donor ? p.actual : null}
                  rows={[{ label: 'AI', q: p.models.demand_conformal, color: MODEL_COLOR.demand_conformal, order: p.ai },
                    { label: 'Seasonal naive', q: p.models.seasonal_naive, color: MODEL_COLOR.seasonal_naive, order: p.base },
                    { label: 'Raw-sales', q: p.models.raw_quantile, color: MODEL_COLOR.raw_quantile, order: p.raw }]} />
                {p.donor ? (
                  <Slider label="Your order (units)" value={orders[p.sid] ?? 0} min={0} max={maxQ} step={0.1} display={(v) => v.toFixed(1)}
                    onChange={(v) => phase === 'morning' && setOrders((o) => ({ ...o, [p.sid]: v }))}
                    marks={[{ label: 'AI', value: p.ai, color: C.blue }, { label: 'naive', value: p.base, color: C.yellow }, ...(phase === 'close' ? [{ label: 'actual', value: p.actual, color: C.red }] : [])]} />
                ) : <div className="small muted">The real store ran out for {p.stockoutHours} h this day. Its demand is censored, so this shelf is not scored (same rule as the paper).</div>}
                {res && (
                  <table className="t"><thead><tr><th /><th className="n">order</th><th className="n">short</th><th className="n">waste</th><th className="n">cost</th></tr></thead>
                    <tbody>{['you', 'ai', 'base'].map((k) => (
                      <tr key={k}><td style={{ color: POL[k].color }}>{POL[k].label.split(' ·')[0]}</td><td className="n">{(k === 'you' ? res.p.Q : res.p[k]).toFixed(2)}</td><td className="n">{res[k].short.toFixed(2)}</td><td className="n">{res[k].left.toFixed(2)}</td><td className="n"><b>{res[k].cost.toFixed(2)}</b></td></tr>
                    ))}<tr><td className="muted">actual demand</td><td className="n" colSpan={4}>{res.D.toFixed(2)}</td></tr></tbody></table>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
