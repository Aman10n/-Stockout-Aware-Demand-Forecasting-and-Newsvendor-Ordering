// The paper's stockout simulator (notebook Phase 2): stock Q = max(MU * k * exp(sigma * z), q_floor) is
// depleted hour by hour against the true donor-day demand; mechanism A refills with probability p_refill,
// B is A with lower stock on promotion days, C has lower stock and no refill. Same parameters and the same
// splitmix64 hash streams as the notebook.
const M64 = (1n << 64n) - 1n;

function splitmix64(x) {
  x = (x + 0x9e3779b97f4a7c15n) & M64;
  x = ((x ^ (x >> 30n)) * 0xbf58476d1ce4e5b9n) & M64;
  x = ((x ^ (x >> 27n)) * 0x94d049bb133111ebn) & M64;
  return (x ^ (x >> 31n)) & M64;
}

/** Same as notebook hash_uniform(keys, seed, stream) for one series key: uniform(0,1) per day. */
export function hashUniform(key, seed, stream, nDays) {
  const s = splitmix64(BigInt(seed * 1000003 + stream) & M64);
  const out = new Float64Array(nDays);
  for (let d = 0; d < nDays; d++) {
    const base = (BigInt(key) * 1000n + BigInt(d)) & M64;
    const z = splitmix64(splitmix64(base ^ s));
    out[d] = (Number(z >> 11n) + 0.5) / 2 ** 53;
  }
  return out;
}

/** Inverse standard normal CDF: Wichura (1988) algorithm AS241 PPND16, accurate to about 1e-16. */
export function ndtri(p) {
  const q = p - 0.5;
  if (Math.abs(q) <= 0.425) {
    const r = 0.180625 - q * q;
    return q * (((((((2509.0809287301226727 * r + 33430.575583588128105) * r + 67265.770927008700853) * r +
      45921.953931549871457) * r + 13731.693765509461125) * r + 1971.5909503065514427) * r + 133.14166789178437745) * r +
      3.387132872796366608) / (((((((5226.495278852545925 * r + 28729.085735721942674) * r + 39307.89580009271061) * r +
      21213.794301586595867) * r + 5394.1960214247511077) * r + 687.1870074920579083) * r + 42.313330701600911252) * r + 1);
  }
  let r = q < 0 ? p : 1 - p;
  r = Math.sqrt(-Math.log(r));
  let x;
  if (r <= 5) {
    r -= 1.6;
    x = (((((((7.7454501427834140764e-4 * r + 0.0227238449892691845833) * r + 0.24178072517745061177) * r +
      1.27045825245236838258) * r + 3.64784832476320460504) * r + 5.7694972214606914055) * r + 4.6303378461565452959) * r +
      1.42343711074968357734) / (((((((1.05075007164441684324e-9 * r + 5.475938084995344946e-4) * r +
      0.0151986665636164571966) * r + 0.14810397642748007459) * r + 0.68976733498510000455) * r + 1.6763848301838038494) * r +
      2.05319162663775882187) * r + 1);
  } else {
    r -= 5;
    x = (((((((2.01033439929228813265e-7 * r + 2.71155556874348757815e-5) * r + 0.0012426609473880784386) * r +
      0.026532189526576123093) * r + 0.29656057182850489123) * r + 1.7848265399172913358) * r + 5.4637849111641143699) * r +
      6.6579046435011037772) / (((((((2.04426310338993978564e-15 * r + 1.4215117583164458887e-7) * r +
      1.8463183175100546818e-5) * r + 7.868691311456132591e-4) * r + 0.0148753612908506148525) * r +
      0.13692988092273580531) * r + 0.59983220655588793769) * r + 1);
  }
  return q < 0 ? -x : x;
}

/** Hour-by-hour depletion (notebook deplete): returns visible sales, stockout flags and first stockout hour. */
export function deplete(demand, Q, refillLag = null, refillAmt = 0) {
  let stock = Q, refillHour = 1e6, first = -1;
  const vis = [], flag = [], stockPath = [];
  for (let h = 0; h < demand.length; h++) {
    if (refillLag !== null && refillHour === h) stock += refillAmt;
    const dd = demand[h], s = Math.min(dd, stock);
    const out = dd > stock + 1e-12 || stock <= 1e-12;
    vis.push(s); flag.push(out ? 1 : 0); stock -= s; stockPath.push(stock);
    if (out && first < 0) { first = h; if (refillLag !== null) refillHour = h + refillLag; }
  }
  return { vis, flag, first, stockPath, refillHour: refillHour < 1e6 ? refillHour : null };
}

/**
 * Apply a mechanism to one series. hours16[d] = 16 true hourly values (only donor days are eligible).
 * Returns per-day visible totals, stockout hours, and the per-day hourly detail of eligible days.
 */
export function simulateSeries({ key, Y, SO, hours16, activity, params, mech, seed = 20240628, days }) {
  const n = Y.length;
  const MU = Y.map((_, d) => {
    if (d === 0) return NaN;
    const lo = Math.max(d - 14, 0);
    let s = 0;
    for (let i = lo; i < d; i++) s += Y[i];
    return s / (d - lo);
  });
  const u1 = hashUniform(key, seed, 1, n), u2 = hashUniform(key, seed, 2, n), u3 = hashUniform(key, seed, 3, n);
  const Yv = [...Y], SOv = [...SO], detail = {};
  for (let d = 0; d < n; d++) {
    if (days && !days.includes(d)) continue;
    if (SO[d] !== 0 || !Number.isFinite(MU[d])) continue;
    const z = ndtri(u1[d]);
    let k = params.k, sig = params.sigma, refill = true;
    if (mech === 'B') k = params.k * (activity[d] === 1 ? params.promo_factor : 1);
    if (mech === 'C') { k = params.k_C; sig = params.sigma_C; refill = false; }
    const Q = Math.max(MU[d] * k * Math.exp(sig * z), params.q_floor);
    let res;
    if (refill) {
      const has = u2[d] < params.p_refill;
      const lag = has ? 1 + Math.floor(u3[d] * 3) : 1e6;
      res = deplete(hours16[d], Q, lag, params.refill_frac * Q);
    } else res = deplete(hours16[d], Q);
    const vsum = res.vis.reduce((a, b) => a + b, 0);
    Yv[d] = vsum;
    SOv[d] = res.flag.reduce((a, b) => a + b, 0);
    detail[d] = { Q, ...res, demand: hours16[d] };
  }
  return { Y: Yv, SO: SOv, detail, MU };
}
