// LightGBM inference in plain JavaScript, reproducing the C++ decision rules:
//  - numerical split: NaN -> 0 unless missing_type == NaN; missing values follow default_left
//  - categorical split: NaN or negative -> right; otherwise left if the category is in the split's set
//  - inputs are rounded to float32 first, exactly like the float32 matrix the Python pipeline passes in.
const NUM = 0;
const MISSING_ZERO = 1;
const MISSING_NAN = 2;
const ZERO_THRESHOLD = 1e-35;

export class Booster {
  constructor(json) {
    this.name = json.name;
    this.features = json.features;
    this.trees = json.trees.map((t) => ({ ...t, cs: t.c.map((arr) => new Set(arr)) }));
  }

  static next(t, node, x) {
    const fval = x[t.f[node]];
    if (t.d[node] !== NUM) {
      if (Number.isNaN(fval)) return t.rc[node];
      const iv = Math.trunc(fval);
      if (iv < 0) return t.rc[node];
      return t.cs[t.t[node]].has(iv) ? t.lc[node] : t.rc[node];
    }
    let v = fval;
    const mt = t.m[node];
    if (Number.isNaN(v) && mt !== MISSING_NAN) v = 0;
    if ((mt === MISSING_ZERO && Math.abs(v) <= ZERO_THRESHOLD) || (mt === MISSING_NAN && Number.isNaN(v))) {
      return t.l[node] ? t.lc[node] : t.rc[node];
    }
    return v <= t.t[node] ? t.lc[node] : t.rc[node];
  }

  /** x: array of feature values in model order (NaN = missing). Returns the raw score. */
  predict(x) {
    const xf = Float64Array.from(x, (v) => (v === null || v === undefined ? NaN : Math.fround(v)));
    let sum = 0;
    for (const t of this.trees) {
      let node = t.root;
      while (node >= 0) node = Booster.next(t, node, xf);
      sum += t.v[~node];
    }
    return sum;
  }

  /** Decision path through one tree (for the X-ray visual). */
  path(x, treeIndex) {
    const xf = Float64Array.from(x, (v) => (v === null || v === undefined ? NaN : Math.fround(v)));
    const t = this.trees[treeIndex];
    const nodes = [];
    let node = t.root;
    while (node >= 0) {
      const nxt = Booster.next(t, node, xf);
      nodes.push({ node, feature: this.features[t.f[node]], left: nxt === t.lc[node] });
      node = nxt;
    }
    return { nodes, leaf: ~node, value: t.v[~node] };
  }
}
