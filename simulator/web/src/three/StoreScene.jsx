// 3D fresh-food store: one shelf per product, crates that empty as the day runs, customers who either
// leave with a product or walk away red-faced when the shelf is empty.
import { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, ContactShadows, RoundedBox } from '@react-three/drei';
import * as THREE from 'three';

const SLOTS = 12; // crates per shelf (3 columns x 4 rows)
const DOOR = new THREE.Vector3(9.5, 0, 6.5), EXIT = new THREE.Vector3(-9.5, 0, 6.5);

function Shelf({ p, x }) {
  const boxes = Math.max(0, Math.min(SLOTS, Math.ceil(p.frac * SLOTS - 1e-9)));
  return (
    <group position={[x, 0, 0]}>
      {[-0.95, 0.95].map((dx) => (
        <mesh key={dx} position={[dx, 1.25, 0]} castShadow><boxGeometry args={[0.08, 2.5, 0.9]} /><meshStandardMaterial color="#6b7891" metalness={0.5} roughness={0.35} /></mesh>
      ))}
      {[0.12, 0.72, 1.32, 1.92].map((y) => (
        <mesh key={y} position={[0, y, 0]} receiveShadow castShadow><boxGeometry args={[1.95, 0.06, 0.9]} /><meshStandardMaterial color="#566278" metalness={0.4} roughness={0.45} /></mesh>
      ))}
      {Array.from({ length: SLOTS }, (_, k) => {
        const row = Math.floor(k / 3), col = k % 3;
        const filled = k < boxes;
        return (
          <group key={k} position={[(col - 1) * 0.6, 0.15 + row * 0.6 + 0.2, 0]} scale={filled ? 1 : 0.001}>
            <RoundedBox args={[0.52, 0.38, 0.7]} radius={0.05} smoothness={3} castShadow>
              <meshStandardMaterial color={p.censored ? '#6b6f78' : p.color} roughness={0.55} />
            </RoundedBox>
          </group>
        );
      })}
      <mesh position={[0, 2.7, 0]}>
        <boxGeometry args={[1.95, 0.32, 0.06]} />
        <meshStandardMaterial color={p.out ? '#e66767' : '#1b2232'} emissive={p.out ? '#e66767' : p.color} emissiveIntensity={p.out ? 1.4 : 0.35} />
      </mesh>
      {p.out && <pointLight position={[0, 2.2, 1.2]} color="#e66767" intensity={6} distance={4} />}
      <Html position={[0, 3.25, 0]} center zIndexRange={[10, 0]} style={{ pointerEvents: 'none', whiteSpace: 'nowrap' }}>
        <div className={`chip3d ${p.out ? 'out' : p.censored ? 'cen' : ''}`} style={{ whiteSpace: 'nowrap' }}>
          {p.name}
          <div style={{ fontWeight: 500, opacity: 0.85 }}>
            {p.censored ? 'censored' : p.out ? 'SOLD OUT' : `${p.stock.toFixed(1)} left`}
          </div>
        </div>
      </Html>
    </group>
  );
}

function Customer({ c, shelfX, speed }) {
  const ref = useRef(), mat = useRef();
  const start = useRef(null);
  const shelf = useMemo(() => new THREE.Vector3(shelfX + (Math.random() - 0.5) * 0.8, 0, 1.25 + Math.random() * 0.5), [shelfX]);
  const life = 3.4;
  useFrame((state) => {
    if (!ref.current) return;
    if (start.current === null) start.current = state.clock.elapsedTime;
    const t = ((state.clock.elapsedTime - start.current) * speed) / life;
    if (t >= 1) { ref.current.visible = false; return; }
    const p = ref.current.position;
    if (t < 0.42) p.lerpVectors(DOOR, shelf, t / 0.42);
    else if (t < 0.58) p.copy(shelf);
    else p.lerpVectors(shelf, EXIT, (t - 0.58) / 0.42);
    p.y = Math.abs(Math.sin(t * 40)) * 0.06;
    if (mat.current) mat.current.color.set(c.lost && t > 0.48 ? '#e66767' : '#c9ced8');
  });
  return (
    <group ref={ref} position={DOOR.toArray()}>
      <mesh position={[0, 0.45, 0]} castShadow><capsuleGeometry args={[0.18, 0.5, 4, 8]} /><meshStandardMaterial ref={mat} color="#c9ced8" /></mesh>
      <mesh position={[0, 1.02, 0]} castShadow><sphereGeometry args={[0.16, 16, 16]} /><meshStandardMaterial color="#e8d5c0" /></mesh>
      {!c.lost && <mesh position={[0.22, 0.55, 0.05]}><boxGeometry args={[0.18, 0.14, 0.18]} /><meshStandardMaterial color={c.color} /></mesh>}
    </group>
  );
}

export default function StoreScene({ products, customers, speed = 1, height = 470, hour }) {
  const n = products.length;
  const xs = products.map((_, i) => (i - (n - 1) / 2) * 2.35);
  const night = hour == null || hour >= 22 || hour < 6;
  return (
    <div className="stage" style={{ height }}>
      <Canvas shadows camera={{ position: [0, 5.2, 10.5], fov: 48 }}>
        <color attach="background" args={['#101622']} />
        <hemisphereLight args={['#dfe9ff', '#1a2233', night ? 0.6 : 1.1]} />
        <ambientLight intensity={night ? 0.35 : 0.6} />
        <directionalLight position={[5, 10, 8]} intensity={night ? 0.8 : 1.8} castShadow shadow-mapSize={[1024, 1024]} />
        <pointLight position={[0, 5, 4]} intensity={night ? 20 : 45} color="#cfe0ff" distance={20} />
        <spotLight position={[0, 8, 6]} angle={0.7} penumbra={0.6} intensity={night ? 30 : 80} color="#ffffff" target-position={[0, 1, 0]} />
        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow><planeGeometry args={[26, 16]} /><meshStandardMaterial color="#2a3243" roughness={0.85} /></mesh>
        <gridHelper args={[26, 26, '#3a4558', '#323c4e']} position={[0, 0.01, 0]} />
        <mesh position={[0, 2, -1.2]} receiveShadow><boxGeometry args={[24, 4, 0.2]} /><meshStandardMaterial color="#1d2535" /></mesh>
        <mesh position={[0, 3.6, -1.08]}><boxGeometry args={[23.5, 0.08, 0.02]} /><meshBasicMaterial color="#3987e5" /></mesh>
        {[DOOR, EXIT].map((v, i) => (
          <group key={i} position={[v.x, 0, v.z]}>
            <mesh position={[0, 1.2, 0]}><boxGeometry args={[0.12, 2.4, 1.6]} /><meshStandardMaterial color={i ? '#5a2a2a' : '#1f5a46'} emissive={i ? '#e66767' : '#199e70'} emissiveIntensity={0.5} /></mesh>
            <Html position={[0, 2.8, 0]} center zIndexRange={[10, 0]} style={{ pointerEvents: 'none', whiteSpace: 'nowrap' }}><div className="chip3d">{i ? 'exit' : 'entrance'}</div></Html>
          </group>
        ))}
        {products.map((p, i) => <Shelf key={p.sid} p={p} x={xs[i]} />)}
        {customers.map((c) => <Customer key={c.id} c={c} shelfX={xs[c.idx] ?? 0} speed={speed} />)}
        <ContactShadows position={[0, 0.02, 0]} opacity={0.45} scale={26} blur={2.2} far={5} />
        <OrbitControls enablePan={false} minDistance={8} maxDistance={22} maxPolarAngle={1.35} target={[0, 1.4, 0.5]} />
      </Canvas>
    </div>
  );
}
