import { useEffect, useMemo, useRef, useState } from 'react';
import { useApp } from './lib.js';

export function useWidth() {
  const ref = useRef(null);
  const [w, setW] = useState(280);
  useEffect(() => {
    if (!ref.current) return undefined;
    const ro = new ResizeObserver(([e]) => setW(Math.max(200, Math.floor(e.contentRect.width))));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);
  return [ref, w];
}

export const Panel = ({ title, sub, right, children, style, className = '' }) => (
  <div className={`panel ${className}`} style={style}>
    {(title || right) && (
      <div className="row" style={{ alignItems: 'flex-start', marginBottom: sub ? 0 : 8 }}>
        <div style={{ minWidth: 0 }}>
          {title && <h3>{title}</h3>}
          {sub && <p className="sub">{sub}</p>}
        </div>
        <div className="spacer" />
        {right}
      </div>
    )}
    {children}
  </div>
);

export const Kpi = ({ label, value, note, color }) => (
  <div className="panel kpi">
    <span className="label">{label}</span>
    <span className="value" style={color ? { color } : undefined}>{value}</span>
    {note && <span className="note">{note}</span>}
  </div>
);

export function Slider({ label, value, min, max, step = 0.01, onChange, display, marks = [] }) {
  const pct = (v) => `${((v - min) / (max - min)) * 100}%`;
  return (
    <div className="slider">
      <div className="top"><span>{label}</span><b className="mono">{display ? display(value) : value}</b></div>
      <div style={{ position: 'relative' }}>
        <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))}
          style={{ background: `linear-gradient(90deg, var(--blue) ${pct(value)}, var(--grid) ${pct(value)})` }} />
        {marks.map((m) => (
          <div key={m.label} title={m.label} style={{ position: 'absolute', left: pct(Math.min(Math.max(m.value, min), max)), top: -3, width: 2, height: 12, background: m.color, transform: 'translateX(-1px)', borderRadius: 2, pointerEvents: 'none' }} />
        ))}
      </div>
    </div>
  );
}

export const Seg = ({ options, value, onChange }) => (
  <div className="seg">
    {options.map((o) => (
      <button key={o.value} className={o.value === value ? 'on' : ''} onClick={() => onChange(o.value)}>{o.label}</button>
    ))}
  </div>
);

export const Loader = ({ text = 'Running the model…' }) => (
  <div className="row muted small" style={{ padding: 12 }}><span className="loader" /> {text}</div>
);

export const CostControls = ({ compact = false }) => {
  const { cu, co, set } = useApp();
  const beta = cu / (cu + co);
  return (
    <div className="grid" style={{ gridTemplateColumns: compact ? '1fr 1fr auto' : '1fr', alignItems: 'end' }}>
      <Slider label="Cost of 1 unit short (lost margin)" value={cu} min={0.25} max={5} step={0.25} onChange={(v) => set({ cu: v })} display={(v) => v.toFixed(2)} />
      <Slider label="Cost of 1 unit left over (waste)" value={co} min={0.25} max={5} step={0.25} onChange={(v) => set({ co: v })} display={(v) => v.toFixed(2)} />
      <div className="kpi" style={{ minWidth: 120 }}>
        <span className="label">Critical ratio β</span>
        <span className="mono" style={{ fontSize: 22, fontWeight: 800 }}>{beta.toFixed(2)}</span>
      </div>
    </div>
  );
};

/** City -> store -> product picker over the compact series index. */
export function SeriesPicker({ sid, onChange }) {
  const index = useApp((s) => s.index);
  const cur = index?.find((r) => r[0] === sid) ?? index?.[0];
  const cities = useMemo(() => (index ? [...new Set(index.map((r) => r[1]))].sort((a, b) => a - b) : []), [index]);
  if (!index || !cur) return null;
  const stores = [...new Set(index.filter((r) => r[1] === cur[1]).map((r) => r[2]))].sort((a, b) => a - b);
  const prods = index.filter((r) => r[2] === cur[2]).sort((a, b) => a[3] - b[3]);
  const pad = (v, n) => String(v).padStart(n, '0');
  return (
    <div className="row">
      <label className="field">City
        <select value={cur[1]} onChange={(e) => onChange(index.find((r) => r[1] === Number(e.target.value))[0])}>
          {cities.map((c) => <option key={c} value={c}>City {pad(c, 2)}</option>)}
        </select>
      </label>
      <label className="field">Store
        <select value={cur[2]} onChange={(e) => onChange(index.find((r) => r[2] === Number(e.target.value))[0])}>
          {stores.map((s) => <option key={s} value={s}>Store {pad(s, 3)}</option>)}
        </select>
      </label>
      <label className="field">Product
        <select value={cur[0]} onChange={(e) => onChange(Number(e.target.value))}>
          {prods.map((r) => <option key={r[0]} value={r[0]}>Product {pad(r[3], 3)} · Cat {pad(r[4], 2)}</option>)}
        </select>
      </label>
    </div>
  );
}
