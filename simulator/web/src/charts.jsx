// Small SVG chart kit: thin marks, recessive grid, hover tooltips on every chart.
import { useState } from 'react';
import { useWidth } from './ui.jsx';
import { C } from './lib.js';

const lin = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) / (d1 - d0 || 1)) * (r1 - r0);
const niceMax = (v) => {
  if (!(v > 0)) return 1;
  const p = 10 ** Math.floor(Math.log10(v)), m = v / p;
  return ([1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].find((k) => m <= k + 1e-9) ?? 10) * p;
};
const ticks = (max) => {
  // pick a tick count that gives round steps (25 -> 5 steps of 5, 1.2 -> 4 steps of 0.3, ...)
  const n = [4, 5, 3, 6].find((k) => Math.abs((max / k) * 100 - Math.round((max / k) * 100)) < 1e-6 && String(+(max / k).toFixed(4)).replace('.', '').replace(/^0+/, '').length <= 2) ?? 4;
  return Array.from({ length: n + 1 }, (_, i) => (max * i) / n);
};

function Tip({ tip }) {
  if (!tip) return null;
  return (
    <div className="tooltip" style={{ left: tip.x + 14, top: tip.y - 10, transform: tip.flip ? 'translateX(calc(-100% - 28px))' : undefined }}>
      {tip.title && <div className="t">{tip.title}</div>}
      {tip.rows.map((r) => (
        <div key={r.label} className="row" style={{ gap: 6 }}>
          {r.color && <span className="sw" style={{ background: r.color }} />}<span>{r.label}</span><span className="spacer" /><b className="mono">{r.value}</b>
        </div>
      ))}
    </div>
  );
}

/**
 * Time series with optional band, lines, markers and shaded spans. x is an index (day).
 * series: [{key,label,color,values:[], dash, width}], band: {lo:[], hi:[], color}, markers: [{x,y,color,shape,label}]
 */
export function TimeChart({ height = 280, n, xLabel, series = [], band, markers = [], shade = [], onPick, picked, yLabel, extraTip }) {
  const [ref, w] = useWidth();
  const [tip, setTip] = useState(null);
  const m = { l: 40, r: 12, t: 12, b: 26 };
  const all = [...series.flatMap((s) => s.values), ...(band ? band.hi : []), ...markers.map((k) => k.y)].filter(Number.isFinite);
  const yMax = niceMax(Math.max(...all, 0.1) * 1.05);
  const x = lin(0, n - 1, m.l, w - m.r), y = lin(0, yMax, height - m.b, m.t);
  const path = (vals) => vals.map((v, i) => (Number.isFinite(v) ? `${i === 0 || !Number.isFinite(vals[i - 1]) ? 'M' : 'L'}${x(i)},${y(v)}` : '')).join('');
  const area = band ? (() => {
    const idx = band.lo.map((v, i) => i).filter((i) => Number.isFinite(band.lo[i]));
    if (!idx.length) return '';
    return `M${idx.map((i) => `${x(i)},${y(band.hi[i])}`).join('L')}L${[...idx].reverse().map((i) => `${x(i)},${y(band.lo[i])}`).join('L')}Z`;
  })() : '';
  const step = Math.max(1, Math.ceil(n / Math.max(4, Math.floor(w / 90))));
  const onMove = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    const px = e.clientX - r.left;
    const i = Math.round(((px - m.l) / (w - m.l - m.r)) * (n - 1));
    if (i < 0 || i >= n) return setTip(null);
    const rows = series.filter((s) => Number.isFinite(s.values[i])).map((s) => ({ label: s.label, color: s.color, value: s.values[i].toFixed(2) }));
    if (band && Number.isFinite(band.lo[i])) rows.push({ label: band.label || 'band', color: band.color, value: `${band.lo[i].toFixed(2)}–${band.hi[i].toFixed(2)}` });
    if (extraTip) rows.push(...extraTip(i));
    setTip({ x: px, y: e.clientY - r.top, flip: px > w * 0.65, title: xLabel(i), rows, i });
  };
  return (
    <div ref={ref} style={{ position: 'relative', width: '100%', minWidth: 0, overflow: 'hidden' }}>
      <svg className="chart" width={w} height={height} onMouseMove={onMove} onMouseLeave={() => setTip(null)}
        onClick={() => tip && onPick && onPick(tip.i)} style={{ cursor: onPick ? 'pointer' : 'default' }}>
        {shade.map((s) => (
          <g key={s.label}>
            <rect x={x(s.from) - 3} y={m.t} width={x(s.to) - x(s.from) + 6} height={height - m.t - m.b} fill={s.color || '#ffffff08'} />
            <text x={x(s.from) + 2} y={m.t + 12} style={{ fill: C.muted }}>{s.label}</text>
          </g>
        ))}
        {ticks(yMax).map((t) => (
          <g key={t}>
            <line x1={m.l} x2={w - m.r} y1={y(t)} y2={y(t)} stroke={C.grid} />
            <text x={m.l - 6} y={y(t) + 4} textAnchor="end">{t >= 10 ? t.toFixed(0) : t.toFixed(1)}</text>
          </g>
        ))}
        {yLabel && <text x={4} y={m.t + 2} style={{ fontSize: 10 }}>{yLabel}</text>}
        {Array.from({ length: n }, (_, i) => i).filter((i) => i % step === 0).map((i) => (
          <text key={i} x={x(i)} y={height - 8} textAnchor="middle">{xLabel(i, true)}</text>
        ))}
        {band && <path d={area} fill={band.color} opacity={0.18} />}
        {series.map((s) => <path key={s.key} d={path(s.values)} fill="none" stroke={s.color} strokeWidth={s.width || 2} strokeDasharray={s.dash} strokeLinejoin="round" />)}
        {markers.map((k, j) => (k.shape === 'x'
          ? <g key={j} stroke={k.color} strokeWidth={2}><line x1={x(k.x) - 4} x2={x(k.x) + 4} y1={y(k.y) - 4} y2={y(k.y) + 4} /><line x1={x(k.x) - 4} x2={x(k.x) + 4} y1={y(k.y) + 4} y2={y(k.y) - 4} /></g>
          : <circle key={j} cx={x(k.x)} cy={y(k.y)} r={k.r || 4.5} fill={k.hollow ? 'var(--bg)' : k.color} stroke={k.hollow ? k.color : 'var(--bg)'} strokeWidth={2} />))}
        {picked != null && <line x1={x(picked)} x2={x(picked)} y1={m.t} y2={height - m.b} stroke={C.text2} strokeDasharray="3 3" />}
        {tip && <line x1={x(tip.i)} x2={x(tip.i)} y1={m.t} y2={height - m.b} stroke="#ffffff30" />}
      </svg>
      <Tip tip={tip} />
    </div>
  );
}

/** Horizontal bars. rows: [{label, value, color, note}] */
export function HBars({ rows, format = (v) => v.toFixed(3), height = 26, refLine, refLabel }) {
  const [ref, w] = useWidth();
  const [tip, setTip] = useState(null);
  const labelW = Math.min(330, w * 0.5), valW = 64;
  const maxChars = Math.floor((labelW - 12) / 6.2);
  const cut = (t) => (t.length > maxChars ? `${t.slice(0, maxChars - 1)}…` : t);
  const max = Math.max(...rows.map((r) => Math.abs(r.value)), refLine || 0, 1e-9);
  const hasNeg = rows.some((r) => r.value < 0);
  const x0 = hasNeg ? labelW + (w - labelW - valW) / 2 : labelW;
  const sc = (v) => (v / max) * (hasNeg ? (w - labelW - valW) / 2 : w - labelW - valW - 8);
  return (
    <div ref={ref} style={{ position: 'relative', width: '100%', minWidth: 0, overflow: 'hidden' }}>
      <svg className="chart" width={w} height={rows.length * height + 6}>
        {rows.map((r, i) => {
          const bw = sc(r.value);
          return (
            <g key={r.label} transform={`translate(0,${i * height + 3})`} onMouseMove={(e) => { const b = e.currentTarget.ownerSVGElement.getBoundingClientRect(); setTip({ x: e.clientX - b.left, y: e.clientY - b.top, flip: e.clientX - b.left > w * 0.6, title: r.label, rows: [{ label: 'value', value: format(r.value), color: r.color }, ...(r.note ? [{ label: r.note, value: '' }] : [])] }); }} onMouseLeave={() => setTip(null)}>
              <text x={labelW - 8} y={height / 2 + 1} textAnchor="end" dominantBaseline="middle" style={{ fill: r.strong ? C.text : C.text2, fontWeight: r.strong ? 700 : 400 }}>{cut(r.label)}</text>
              <rect x={bw >= 0 ? x0 : x0 + bw} y={4} width={Math.max(1, Math.abs(bw))} height={height - 9} rx={4} fill={r.color} />
              <text x={bw >= 0 ? x0 + bw + 6 : x0 + 6} y={height / 2 + 1} dominantBaseline="middle" style={{ fill: C.text2 }} className="mono">{format(r.value)}</text>
            </g>
          );
        })}
        {refLine != null && <g><line x1={x0 + sc(refLine)} x2={x0 + sc(refLine)} y1={0} y2={rows.length * height} stroke={C.red} strokeWidth={2} /><text x={x0 + sc(refLine) + 4} y={10} style={{ fill: C.red, fontSize: 10 }}>{refLabel}</text></g>}
        {hasNeg && <line x1={x0} x2={x0} y1={0} y2={rows.length * height} stroke={C.grid} />}
      </svg>
      <Tip tip={tip} />
    </div>
  );
}

/** Hourly view: true demand (outline), visible sales (filled), stock line, stockout hours shaded. */
export function HourChart({ demand, visible, stock, flags, height = 220, refillHour, q }) {
  const [ref, w] = useWidth();
  const [tip, setTip] = useState(null);
  const m = { l: 36, r: 10, t: 12, b: 24 };
  const yMax = niceMax(Math.max(...demand, ...(stock || []), q || 0, 0.1) * 1.08);
  const bw = (w - m.l - m.r) / 16;
  const y = lin(0, yMax, height - m.b, m.t);
  return (
    <div ref={ref} style={{ position: 'relative', width: '100%', minWidth: 0, overflow: 'hidden' }}>
      <svg className="chart" width={w} height={height} onMouseLeave={() => setTip(null)}>
        {ticks(yMax).map((t) => <g key={t}><line x1={m.l} x2={w - m.r} y1={y(t)} y2={y(t)} stroke={C.grid} /><text x={m.l - 6} y={y(t) + 4} textAnchor="end">{t.toFixed(1)}</text></g>)}
        {demand.map((d, h) => {
          const x0 = m.l + h * bw;
          return (
            <g key={h} onMouseMove={(e) => { const b = e.currentTarget.ownerSVGElement.getBoundingClientRect(); setTip({ x: e.clientX - b.left, y: e.clientY - b.top, flip: h > 10, title: `${h + 6}:00–${h + 7}:00`, rows: [{ label: 'true demand', value: d.toFixed(2), color: '#ffffff80' }, { label: 'visible sales', value: visible[h].toFixed(2), color: C.blue }, ...(stock ? [{ label: 'stock after hour', value: stock[h].toFixed(2), color: C.aqua }] : []), { label: flags[h] ? 'OUT OF STOCK' : 'in stock', value: '', color: flags[h] ? C.red : undefined }] }); }}>
              {flags[h] ? <rect x={x0} y={m.t} width={bw} height={height - m.t - m.b} fill="#e6676718" /> : null}
              <rect x={x0 + 3} y={y(d)} width={bw - 6} height={y(0) - y(d)} rx={3} fill="none" stroke="#ffffff70" strokeDasharray="3 2" />
              <rect x={x0 + 3} y={y(visible[h])} width={bw - 6} height={y(0) - y(visible[h])} rx={3} fill={C.blue} />
              {h % 2 === 0 && <text x={x0 + bw / 2} y={height - 8} textAnchor="middle">{h + 6}h</text>}
            </g>
          );
        })}
        {stock && <path d={stock.map((s, h) => `${h ? 'L' : 'M'}${m.l + (h + 1) * bw},${y(s)}`).join('')} fill="none" stroke={C.aqua} strokeWidth={2} />}
        {q != null && <g><line x1={m.l} x2={w - m.r} y1={y(q)} y2={y(q)} stroke={C.aqua} strokeDasharray="4 3" opacity={0.6} /><text x={w - m.r - 4} y={y(q) - 4} textAnchor="end" style={{ fill: C.aqua }}>opening stock {q.toFixed(2)}</text></g>}
        {refillHour != null && refillHour < 16 && <g><line x1={m.l + refillHour * bw} x2={m.l + refillHour * bw} y1={m.t} y2={height - m.b} stroke={C.aqua} strokeWidth={2} /><text x={m.l + refillHour * bw + 4} y={m.t + 10} style={{ fill: C.aqua }}>refill</text></g>}
      </svg>
      <Tip tip={tip} />
    </div>
  );
}

/** Quantile fan for several models: q25-q90 range bar with q50 tick, plus optional order + actual markers. */
export function Fan({ rows, actual, order, height = 34 }) {
  const [ref, w] = useWidth();
  const labelW = Math.min(210, w * 0.4);
  const max = niceMax(Math.max(...rows.flatMap((r) => r.q), actual || 0, order || 0, 0.1) * 1.08);
  const x = lin(0, max, labelW, w - 16);
  return (
    <div ref={ref} style={{ width: '100%', minWidth: 0, overflow: 'hidden' }}>
      <svg className="chart" width={w} height={rows.length * height + 26}>
        {ticks(max).map((t) => <g key={t}><line x1={x(t)} x2={x(t)} y1={0} y2={rows.length * height} stroke={C.grid} /><text x={x(t)} y={rows.length * height + 16} textAnchor="middle">{t.toFixed(1)}</text></g>)}
        {rows.map((r, i) => (
          <g key={r.label} transform={`translate(0,${i * height})`}>
            <title>{`${r.label}: q25 ${r.q[0].toFixed(2)} · q50 ${r.q[1].toFixed(2)} · q75 ${r.q[2].toFixed(2)} · q90 ${r.q[3].toFixed(2)}`}</title>
            <text x={labelW - 10} y={height / 2} textAnchor="end" dominantBaseline="middle" style={{ fill: C.text2 }}>{r.label}</text>
            <rect x={x(r.q[0])} y={height / 2 - 8} width={Math.max(2, x(r.q[3]) - x(r.q[0]))} height={16} rx={8} fill={r.color} opacity={0.25} />
            <rect x={x(r.q[0])} y={height / 2 - 8} width={Math.max(2, x(r.q[2]) - x(r.q[0]))} height={16} rx={8} fill={r.color} opacity={0.45} />
            <rect x={x(r.q[1]) - 1.5} y={height / 2 - 11} width={3} height={22} rx={1.5} fill={C.text} />
            {r.order != null && <path d={`M${x(r.order)},${height / 2 - 13} l5,-7 h-10 z`} fill={r.color} />}
          </g>
        ))}
        {actual != null && <g><line x1={x(actual)} x2={x(actual)} y1={0} y2={rows.length * height} stroke={C.red} strokeWidth={2} /><text x={x(actual) + 4} y={10} style={{ fill: C.red }}>actual {actual.toFixed(2)}</text></g>}
      </svg>
    </div>
  );
}

export function Spark({ values, flags, width = 160, height = 34, color = C.text2 }) {
  const max = Math.max(...values, 0.1);
  const x = lin(0, values.length - 1, 2, width - 2), y = lin(0, max, height - 3, 3);
  return (
    <svg width={width} height={height}>
      <path d={values.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join('')} fill="none" stroke={color} strokeWidth={1.5} />
      {values.map((v, i) => (flags[i] ? <circle key={i} cx={x(i)} cy={y(v)} r={2.5} fill={C.red} /> : null))}
    </svg>
  );
}
