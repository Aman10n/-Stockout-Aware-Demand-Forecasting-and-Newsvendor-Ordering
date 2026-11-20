// Turn raw booster scores into the five forecast models' quantiles and newsvendor orders,
// exactly as planner/pipeline.py does: clip at 0 -> pooled residual shift -> clip -> monotone sort.
export const LEVELS = ['category_x_sales_tier', 'category', 'management_group', 'global'];

export function poolLabels(meta) {
  return {
    category_x_sales_tier: `${meta.first_category_id}|${meta.sales_tier}`,
    category: String(meta.first_category_id),
    management_group: String(meta.management_group_id),
    global: 'global',
  };
}

export function lookup(table, meta) {
  const labs = poolLabels(meta);
  for (const lvl of LEVELS) {
    const v = table[lvl]?.[labs[lvl]];
    if (v !== undefined) return { value: v, level: lvl };
  }
  return { value: 0, level: 'none' };
}

const clip0 = (v) => Math.max(0, v);
const sortAsc = (a) => [...a].sort((x, y) => x - y);

/** Seasonal naive on the (possibly censored) daily history: t-7, else t-14, else past mean, else 0. */
export function seasonalNaive(Y, d) {
  if (d - 7 >= 0) return Y[d - 7];
  if (d - 14 >= 0) return Y[d - 14];
  let s = 0;
  for (let i = 0; i < d; i++) s += Y[i];
  return d > 0 ? s / d : 0;
}

/**
 * @param {object} ctx {boosters, tables, Q: ['q25',..], meta, x (feature row), Y (history), d}
 * @returns {{models: Record<string, number[]>, raw: object, pools: object}}
 */
export function forecastAll({ boosters, tables, QN, meta, x, Y, d }) {
  const raw = {};
  for (const q of QN) {
    raw[`demand_${q}`] = boosters[`demand_${q}`].predict(x);
    raw[`raw_${q}`] = boosters[`raw_${q}`].predict(x);
  }
  raw.point = boosters.raw_point_point.predict(x);
  const sn = seasonalNaive(Y, d);
  const models = {}, pools = {};
  const shifted = (code, base) => sortAsc(QN.map((q) => {
    const { value, level } = lookup(tables[`${code}|${q}`], meta);
    if (q === 'q50') pools[code] = level;
    return clip0(base(q) + value);
  }));
  models.demand_conformal = shifted('demand_conformal', (q) => clip0(raw[`demand_${q}`]));
  models.demand_uncal = sortAsc(QN.map((q) => clip0(raw[`demand_${q}`])));
  models.raw_quantile = sortAsc(QN.map((q) => clip0(raw[`raw_${q}`])));
  models.raw_point_resid = shifted('raw_point_resid', () => clip0(raw.point));
  models.seasonal_naive = shifted('seasonal_naive', () => sn);
  return { models, raw, pools, seasonalNaive: sn };
}

/** Newsvendor order: the demand quantile at beta = c_u / (c_u + c_o), linear between q25..q90. */
export function orderAt(q, taus, beta) {
  const b = Math.min(Math.max(beta, taus[0]), taus[taus.length - 1]);
  for (let i = 0; i < taus.length - 1; i++) {
    if (b <= taus[i + 1]) return q[i] + ((q[i + 1] - q[i]) * (b - taus[i])) / (taus[i + 1] - taus[i]);
  }
  return q[q.length - 1];
}

export function newsvendor(Q, D, cu, co) {
  const short = Math.max(D - Q, 0), left = Math.max(Q - D, 0);
  return { short, left, sold: Math.min(Q, D), cost: cu * short + co * left };
}
