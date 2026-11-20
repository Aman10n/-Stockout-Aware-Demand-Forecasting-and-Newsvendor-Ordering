// Loads the exported assets once and exposes the model as functions of (series, day, history).
import fs from 'node:fs';
import path from 'node:path';
import { Booster } from './lgbm.js';
import { buildFeatures, y16 } from './features.js';
import { forecastAll, orderAt } from './policy.js';

export function loadService(dataDir) {
  const read = (f) => JSON.parse(fs.readFileSync(path.join(dataDir, f), 'utf8'));
  const cfg = read('config.json');
  const series = read('series.json');
  const tables = read('residual_tables.json');
  const simParams = read('sim_params.json');
  const network = read('network.json');
  const stores = read('stores.json');
  const N = cfg.n_series, D = cfg.n_days;
  const buf = (f) => fs.readFileSync(path.join(dataDir, f));
  const hb = buf('hours_sale.f32'), sb = buf('hours_stock.u8'), cb = buf('ctx.f32'), shb = buf('shap_q50_final.f32');
  const H = new Float32Array(hb.buffer, hb.byteOffset, hb.byteLength / 4);
  const S = new Uint8Array(sb.buffer, sb.byteOffset, sb.byteLength);
  const C = new Float32Array(cb.buffer, cb.byteOffset, cb.byteLength / 4);
  const SHAP = new Float32Array(shb.buffer, shb.byteOffset, shb.byteLength / 4);
  const boosters = {};
  for (const name of cfg.model_files) boosters[name] = new Booster(read(path.join('models', `${name}.json`)));
  const keyOf = (m) => m.city_id * 1_000_000 + m.store_id * 1_000 + m.product_id;

  /** Recorded history of one series: daily Y (06-22h), SO (stockout hours), hourly arrays, context. */
  function seriesData(sid) {
    const hours = [], stock = [], Y = [], SO = [];
    for (let d = 0; d < D; d++) {
      const off = (sid * D + d) * 24;
      const h = H.subarray(off, off + 24), s = S.subarray(off, off + 24);
      hours.push(Array.from(h));
      stock.push(Array.from(s));
      Y.push(y16(h));
      let so = 0;
      for (let k = 6; k < 22; k++) so += s[k];
      SO.push(so);
    }
    const ctx = {};
    cfg.ctx_cols.forEach((c, j) => { ctx[c] = Array.from({ length: D }, (_, d) => C[(sid * D + d) * cfg.ctx_cols.length + j]); });
    return { meta: series[sid], key: keyOf(series[sid]), hours, stock, Y, SO, ctx };
  }

  function catsOf(m) {
    const o = {};
    for (const c of cfg.cat_features) o[c] = m[c];
    return o;
  }

  /** Features for every day of a series, from its recorded history or an override {Y, SO}. */
  function features(sid, override = null) {
    const s = seriesData(sid);
    const Y = override?.Y ?? s.Y, SO = override?.SO ?? s.SO;
    return { s, Y, SO, rows: buildFeatures({ Y, SO, ctx: s.ctx, cats: catsOf(s.meta), dates: cfg.dates }, cfg.features) };
  }

  /** Forecast every model for the given days of one series. */
  function forecast(sid, days, override = null, featureOverrides = null) {
    const { s, Y, SO, rows } = features(sid, override);
    return days.map((d) => {
      const x = [...rows[d]];
      if (featureOverrides) for (const [k, v] of Object.entries(featureOverrides)) x[cfg.features.indexOf(k)] = v;
      const out = forecastAll({ boosters, tables, QN: cfg.quantiles, meta: s.meta, x, Y, d });
      const donor = s.SO[d] === 0;
      return { d, date: cfg.dates[d], x, donor, actual: donor ? s.Y[d] : null, recorded: s.Y[d], stockoutHours: s.SO[d], historyY: Y[d], historySO: SO[d], ...out };
    });
  }

  function shap(sid, d) {
    if (d < 90) return null;
    const k = cfg.features.length + 1, off = (sid * 7 + (d - 90)) * k;
    return Array.from(SHAP.subarray(off, off + k));
  }

  return { cfg, series, tables, simParams, network, stores, boosters, seriesData, features, forecast, shap, orderAt };
}
