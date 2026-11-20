// Port of planner/pipeline.py build_features() for one series. Every feature for day d uses days < d only.
// Arithmetic follows numpy's order (sequential cumsum, pairwise 8-accumulator sums) so values match bit for bit.

/** numpy pairwise sum for n <= 128 (the 8-accumulator unrolled loop in numpy's pairwise_sum). */
export function npSum(a) {
  const n = a.length;
  if (n < 8) {
    let res = 0;
    for (let i = 0; i < n; i++) res += a[i];
    return res;
  }
  const r = [a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]];
  let i = 8;
  for (; i < n - (n % 8); i += 8) for (let j = 0; j < 8; j++) r[j] += a[i + j];
  let res = ((r[0] + r[1]) + (r[2] + r[3])) + ((r[4] + r[5]) + (r[6] + r[7]));
  for (; i < n; i++) res += a[i];
  return res;
}

const shift = (a, k) => a.map((_, d) => (d >= k ? a[d - k] : NaN));

function rollPast(a, w, fn = 'mean') {
  const n = a.length;
  const cs = new Float64Array(n + 1), cc = new Float64Array(n + 1), c2 = new Float64Array(n + 1);
  for (let i = 0; i < n; i++) {
    const ok = Number.isFinite(a[i]);
    const z = ok ? a[i] : 0;
    cs[i + 1] = cs[i] + z;
    cc[i + 1] = cc[i] + (ok ? 1 : 0);
    c2[i + 1] = c2[i] + z * z;
  }
  const out = new Array(n);
  for (let d = 0; d < n; d++) {
    const lo = Math.max(d - w, 0);
    const s = cs[d] - cs[lo], c = cc[d] - cc[lo], s2 = c2[d] - c2[lo];
    const mean = s / c;
    if (fn === 'mean') out[d] = c > 0 ? mean : NaN;
    else {
      const v = s2 / c - mean * mean;
      out[d] = c > 1 ? Math.sqrt(Math.max(v, 0)) : NaN;
    }
  }
  return out;
}

/** Daily 06:00-21:59 sales total from 24 hourly float32 values, summed like numpy (astype float64, sum). */
export function y16(hours24) {
  return npSum(Array.from(hours24.subarray ? hours24.subarray(6, 22) : hours24.slice(6, 22)));
}

/**
 * Build all features for every day of one series.
 * @param {object} s  {Y: number[], SO: number[], ctx: {discount,holiday_flag,activity_flag,precpt,avg_temperature}: number[][],
 *                     cats: {city_id,...}, dates: string[]}
 * @param {string[]} FEATURES  feature order of the models
 * @returns {number[][]} matrix [day][feature]
 */
export function buildFeatures(s, FEATURES) {
  const { Y, SO, ctx, cats, dates } = s;
  const n = Y.length;
  const DON = SO.map((v) => v === 0);
  const soPos = SO.map((v) => (v > 0 ? 1 : 0));
  const f = {
    y_lag1: shift(Y, 1), y_lag2: shift(Y, 2), y_lag7: shift(Y, 7), y_lag14: shift(Y, 14),
    y_roll7: rollPast(Y, 7), y_roll14: rollPast(Y, 14), y_roll28: rollPast(Y, 28), y_std14: rollPast(Y, 14, 'std'),
    y_don_roll14: rollPast(Y.map((v, i) => (DON[i] ? v : NaN)), 14),
    y_don_roll28: rollPast(Y.map((v, i) => (DON[i] ? v : NaN)), 28),
    so_lag1: shift(SO, 1), so_rate7: rollPast(soPos, 7), so_rate14: rollPast(soPos, 14),
    don_frac7: rollPast(DON.map((v) => (v ? 1 : 0)), 7),
    disc_lag1: shift(ctx.discount, 1), disc_roll7: rollPast(ctx.discount, 7),
    act_lag1: shift(ctx.activity_flag, 1), act_roll7: rollPast(ctx.activity_flag, 7),
    hol_lag1: shift(ctx.holiday_flag, 1), precpt_lag1: shift(ctx.precpt, 1), temp_lag1: shift(ctx.avg_temperature, 1),
  };
  const ew = new Array(n).fill(NaN), dowm = new Array(n).fill(NaN);
  for (let d = 1; d < n; d++) {
    const prev = ew[d - 1];
    ew[d] = Number.isNaN(prev) ? Y[d - 1] : 0.2 * Y[d - 1] + 0.8 * prev;
    if (d >= 7) {
      const same = [];
      for (let k = d - 7; k >= 0; k -= 7) same.push(Y[k]);
      dowm[d] = npSum(same) / same.length;
    }
  }
  f.y_ewm = ew;
  f.y_dow_mean = dowm;
  const dow = dates.map((ds) => {
    const days = Math.round(Date.parse(ds + 'T00:00:00Z') / 86400000);
    return (((days - 4) % 7) + 7) % 7; // 0 = Monday
  });
  f.dow = dow;
  f.is_weekend = dow.map((v) => (v >= 5 ? 1 : 0));
  f.n_hist_days = dow.map((_, d) => d);
  for (const [k, v] of Object.entries(cats)) f[k] = new Array(n).fill(v);
  const rows = [];
  for (let d = 0; d < n; d++) rows.push(FEATURES.map((name) => Math.fround(f[name][d])));
  return rows;
}
