// Verification gate: the JavaScript engine must reproduce the Python pipeline.
//  1. features rebuilt in JS == Python features (exact float32 equality)
//  2. every booster's raw score in JS == LightGBM's Python score (|diff| < 1e-9)
//  3. final quantiles of all five models == the warehouse (rounded to 4 dp, |diff| <= 6e-5)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadService } from './engine/service.js';

const DATA = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'data');
const svc = loadService(DATA);
const fx = JSON.parse(fs.readFileSync(path.join(DATA, 'fixtures.json'), 'utf8'));
const F = svc.cfg.features;
let featBad = 0, featWorst = null, rawMax = 0, finMax = 0, finRows = 0;
const cache = new Map();

fx.rows.forEach((r, i) => {
  if (!cache.has(r.sid)) cache.set(r.sid, svc.features(r.sid).rows);
  const js = cache.get(r.sid)[r.d];
  for (let j = 0; j < F.length; j++) {
    const a = js[j], b = r.x[j] === null ? NaN : r.x[j];
    const same = (Number.isNaN(a) && Number.isNaN(b)) || a === b;
    if (!same) { featBad++; if (!featWorst) featWorst = { row: i, sid: r.sid, d: r.d, feature: F[j], js: a, py: b }; }
  }
  const x = r.x.map((v) => (v === null ? NaN : v));
  for (const name of svc.cfg.model_files) rawMax = Math.max(rawMax, Math.abs(svc.boosters[name].predict(x) - fx.raw[name][i]));
  if (fx.final[i]) {
    const [out] = svc.forecast(r.sid, [r.d]);
    svc.cfg.models.forEach((m) => {
      out.models[m.model_code].forEach((v, k) => { finMax = Math.max(finMax, Math.abs(v - fx.final[i][String(m.model_key)][k])); });
    });
    finRows++;
  }
});

const ok1 = featBad === 0, ok2 = rawMax < 1e-9, ok3 = finMax <= 6e-5;
console.log(`[${ok1 ? 'PASS' : 'FAIL'}] features: ${fx.rows.length} rows x ${F.length} features, ${featBad} mismatches`, featWorst ?? '');
console.log(`[${ok2 ? 'PASS' : 'FAIL'}] booster scores: 9 models, max |JS - Python| = ${rawMax.toExponential(2)}`);
console.log(`[${ok3 ? 'PASS' : 'FAIL'}] final quantiles vs warehouse: ${finRows} rows x 5 models x 4 quantiles, max diff = ${finMax.toExponential(2)}`);
process.exit(ok1 && ok2 && ok3 ? 0 : 1);
