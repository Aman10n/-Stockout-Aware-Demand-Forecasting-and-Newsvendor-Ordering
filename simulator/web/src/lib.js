import { create } from 'zustand';

export async function api(path, body) {
  const res = await fetch(`/api/${path}`, body === undefined ? undefined : {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error || res.statusText);
  return json;
}

export const C = {
  blue: '#3987e5', orange: '#d95926', aqua: '#199e70', yellow: '#c98500', magenta: '#d55181',
  green: '#0ca30c', violet: '#9085e9', red: '#e66767', text: '#f0efec', text2: '#c3c2b7', muted: '#8b909b', grid: '#222938',
};
export const PALETTE = [C.blue, C.orange, C.aqua, C.yellow, C.magenta, C.green, C.violet, C.red];
export const MODEL_COLOR = {
  demand_conformal: C.blue, demand_uncal: C.aqua, raw_quantile: C.orange, raw_point_resid: C.magenta, seasonal_naive: C.yellow,
};
export const MODEL_SHORT = {
  demand_conformal: 'Stockout-aware + conformal', demand_uncal: 'Stockout-aware (uncalibrated)',
  raw_quantile: 'Raw-sales quantile', raw_point_resid: 'Raw-sales point + residual', seasonal_naive: 'Seasonal naive',
};
export const TAUS = [0.25, 0.5, 0.75, 0.9];

export const fmt = {
  pct: (v, d = 1) => (v == null || !Number.isFinite(v) ? '–' : `${(v * 100).toFixed(d)}%`),
  spct: (v, d = 1) => (v == null || !Number.isFinite(v) ? '–' : `${v > 0 ? '+' : ''}${(v * 100).toFixed(d)}%`),
  n: (v, d = 2) => (v == null || !Number.isFinite(v) ? '–' : v.toFixed(d)),
  date: (s) => new Date(`${s}T00:00:00Z`).toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short', timeZone: 'UTC' }),
  hour: (h) => `${String(Math.floor(h)).padStart(2, '0')}:00`,
};

/** Newsvendor order: demand quantile at beta, linear between q25..q90 (same rule as the server). */
export function orderAt(q, beta) {
  const b = Math.min(Math.max(beta, TAUS[0]), TAUS[3]);
  for (let i = 0; i < 3; i++) if (b <= TAUS[i + 1]) return q[i] + ((q[i + 1] - q[i]) * (b - TAUS[i])) / (TAUS[i + 1] - TAUS[i]);
  return q[3];
}

/** Hour-by-hour shelf depletion with no refill (fresh goods, one delivery in the morning). */
export function deplete(demand, Q) {
  let stock = Q, first = -1;
  const vis = [], flag = [], stockPath = [];
  demand.forEach((d, h) => {
    const s = Math.min(d, stock);
    const out = d > stock + 1e-12 || stock <= 1e-12;
    vis.push(s); flag.push(out ? 1 : 0); stock -= s; stockPath.push(stock);
    if (out && first < 0) first = h;
  });
  return { vis, flag, first, stockPath };
}

export const newsvendor = (Q, D, cu, co) => {
  const short = Math.max(D - Q, 0), left = Math.max(Q - D, 0);
  return { short, left, sold: Math.min(Q, D), cost: cu * short + co * left };
};

export const useApp = create((set) => ({
  page: 'command',
  meta: null,
  index: null,
  cu: 1, co: 1,
  focusSid: 1476,
  setPage: (page) => set({ page }),
  set: (o) => set(o),
}));
