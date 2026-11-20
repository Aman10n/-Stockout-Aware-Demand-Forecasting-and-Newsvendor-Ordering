import { useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

const LOW = new THREE.Color('#1d3a63'), HIGH = new THREE.Color('#6da7ec');

function Tower({ c, i, n, hMin, hMax, sMin, sMax, selected, onSelect }) {
  const ref = useRef();
  const [hover, setHover] = useState(false);
  const ang = (i / n) * Math.PI * 2;
  const R = 6.2;
  const target = 0.5 + ((c.stockout_rate - hMin) / (hMax - hMin || 1)) * 3.0;
  const t = (c.saving - sMin) / (sMax - sMin || 1);
  const color = LOW.clone().lerp(HIGH, Number.isFinite(t) ? t : 0.5);
  useFrame((_, dt) => {
    if (!ref.current) return;
    const s = ref.current.scale;
    s.y += (target - s.y) * Math.min(1, dt * 3);
    ref.current.position.y = s.y / 2;
  });
  const on = selected === c.city;
  return (
    <group position={[Math.cos(ang) * R, 0, Math.sin(ang) * R]}>
      <mesh ref={ref} scale={[1, 0.01, 1]} castShadow
        onPointerOver={(e) => { e.stopPropagation(); setHover(true); document.body.style.cursor = 'pointer'; }}
        onPointerOut={() => { setHover(false); document.body.style.cursor = 'default'; }}
        onClick={(e) => { e.stopPropagation(); onSelect(on ? null : c.city); }}>
        <cylinderGeometry args={[0.55, 0.62, 1, 6]} />
        <meshStandardMaterial color={color} emissive={on ? '#3987e5' : hover ? '#24456f' : '#000000'} emissiveIntensity={on ? 0.9 : 0.5} metalness={0.25} roughness={0.35} />
      </mesh>
      <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.72, on ? 0.95 : 0.8, 6]} />
        <meshBasicMaterial color={on ? '#3987e5' : '#2a3448'} />
      </mesh>
      <Html position={[0, target + 0.45, 0]} center zIndexRange={[10, 0]} style={{ pointerEvents: 'none', whiteSpace: 'nowrap' }}>
        <div className="chip3d" style={{ whiteSpace: 'nowrap', opacity: hover || on ? 1 : 0.8, fontSize: 10, padding: '2px 6px', borderColor: on ? '#3987e5' : undefined }}>
          {c.city.replace('City ', 'C')} · {(c.stockout_rate * 100).toFixed(0)}%
          {(hover || on) && <div style={{ fontWeight: 500, color: '#c3c2b7' }}>saving {(c.saving * 100).toFixed(1)}% · {c.series} items</div>}
        </div>
      </Html>
    </group>
  );
}

export default function CityTowers({ cities, selected, onSelect, height = 420 }) {
  const ext = useMemo(() => {
    const h = cities.map((c) => c.stockout_rate), s = cities.map((c) => c.saving);
    return { hMin: Math.min(...h), hMax: Math.max(...h), sMin: Math.min(...s), sMax: Math.max(...s) };
  }, [cities]);
  return (
    <div className="stage" style={{ height }}>
      <Canvas shadows camera={{ position: [0, 10.5, 15.5], fov: 40 }} onPointerMissed={() => onSelect(null)}>
        <color attach="background" args={['#0c1018']} />
        <fog attach="fog" args={['#0c1018', 18, 34]} />
        <ambientLight intensity={0.45} />
        <directionalLight position={[6, 12, 6]} intensity={1.3} castShadow shadow-mapSize={[1024, 1024]} />
        <pointLight position={[0, 4, 0]} intensity={18} color="#3987e5" distance={14} />
        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <circleGeometry args={[9, 64]} />
          <meshStandardMaterial color="#121926" roughness={0.9} />
        </mesh>
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
          <ringGeometry args={[2.2, 2.28, 64]} />
          <meshBasicMaterial color="#3987e5" transparent opacity={0.5} />
        </mesh>
        <gridHelper args={[18, 18, '#1d2535', '#161d2a']} position={[0, 0.005, 0]} />
        {cities.map((c, i) => <Tower key={c.city} c={c} i={i} n={cities.length} {...ext} selected={selected} onSelect={onSelect} />)}
        <ContactShadows position={[0, 0.01, 0]} opacity={0.5} scale={20} blur={2} far={6} />
        <OrbitControls enablePan={false} autoRotate={!selected} autoRotateSpeed={0.5} minDistance={9} maxDistance={22} maxPolarAngle={1.25} />
      </Canvas>
      <div className="overlay small muted" style={{ left: 14, bottom: 10 }}>
        Tower height = stockout rate · colour = cost saving vs seasonal naive (lighter = more) · click a tower to filter
      </div>
    </div>
  );
}
