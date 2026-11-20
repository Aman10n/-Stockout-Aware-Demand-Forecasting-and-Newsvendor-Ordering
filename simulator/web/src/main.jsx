import { StrictMode, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { api, useApp } from './lib.js';
import Command from './pages/Command.jsx';
import Game from './pages/Game.jsx';
import Lab from './pages/Lab.jsx';
import XRay from './pages/XRay.jsx';

const PAGES = [
  ['command', 'Command center', Command],
  ['game', 'Run the store', Game],
  ['lab', 'Censoring lab', Lab],
  ['xray', 'Model X-ray', XRay],
];

function App() {
  const { page, setPage, meta, set } = useApp();
  useEffect(() => {
    api('meta').then((m) => set({ meta: m }));
    api('series-index').then((ix) => set({ index: ix }));
    const fromHash = () => { const h = window.location.hash.slice(1); if (PAGES.some((p) => p[0] === h)) setPage(h); };
    fromHash();
    window.addEventListener('hashchange', fromHash);
    return () => window.removeEventListener('hashchange', fromHash);
  }, [set, setPage]);
  useEffect(() => { if (window.location.hash.slice(1) !== page) window.location.hash = page; window.scrollTo(0, 0); }, [page]);
  const Page = PAGES.find((p) => p[0] === page)?.[2] ?? Command;
  return (
    <>
      <header className="topbar">
        <div className="brand"><div className="brand-mark" /><div>STOCKOUT/SIM<small>stockout-aware forecasting &amp; newsvendor ordering</small></div></div>
        <nav className="nav">{PAGES.map(([k, label]) => <button key={k} className={page === k ? 'active' : ''} onClick={() => setPage(k)}>{label}</button>)}</nav>
        <div className="verified" title="JavaScript engine re-implements LightGBM and the feature pipeline; verified against Python on 3,000 rows (features bit-exact, scores identical).">
          <span className="dot" />{meta ? `${meta.engine.models} LightGBM models · ${meta.engine.trees.toLocaleString()} trees · verified vs Python` : 'loading model…'}
        </div>
      </header>
      <Page key={page} />
    </>
  );
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
