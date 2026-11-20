// The q50 model as a forest of 208 columns: each column is one tree, its height the leaf value this row
// lands in (blue pushes the forecast up, orange pulls it down). Columns grow live as features change.
import { useLayoutEffect, useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

const UP = new THREE.Color('#3987e5'), DOWN = new THREE.Color('#d95926');

function Columns({ values }) {
  const ref = useRef();
  const n = values.length, cols = Math.ceil(Math.sqrt(n * 1.6)), rows = Math.ceil(n / cols);
  const max = useMemo(() => Math.max(...values.slice(1).map(Math.abs), 1e-6), [values]);
  const cur = useRef(new Float32Array(n));
  const tmp = useMemo(() => new THREE.Object3D(), []);
  useLayoutEffect(() => {
    values.forEach((v, i) => ref.current.setColorAt(i, v >= 0 ? UP : DOWN));
    ref.current.instanceColor.needsUpdate = true;
  }, [values]);
  useFrame((_, dt) => {
    if (!ref.current) return;
    for (let i = 0; i < n; i++) {
      // tree 0 also carries the model's starting value (boost from average): show it capped
      const target = 0.04 + Math.min(Math.abs(values[i]) / max, 1.6) * 2.6;
      cur.current[i] += (target - cur.current[i]) * Math.min(1, dt * 5);
      const r = Math.floor(i / cols), c = i % cols;
      tmp.position.set((c - (cols - 1) / 2) * 0.42, cur.current[i] / 2, (r - (rows - 1) / 2) * 0.42);
      tmp.scale.set(1, cur.current[i], 1);
      tmp.updateMatrix();
      ref.current.setMatrixAt(i, tmp.matrix);
    }
    ref.current.instanceMatrix.needsUpdate = true;
  });
  return (
    <instancedMesh ref={ref} args={[null, null, n]} castShadow>
      <boxGeometry args={[0.32, 1, 0.32]} />
      <meshStandardMaterial roughness={0.4} metalness={0.2} />
    </instancedMesh>
  );
}

export default function Forest({ values, height = 330 }) {
  return (
    <div className="stage" style={{ height }}>
      <Canvas shadows camera={{ position: [5.5, 5.5, 7.5], fov: 42 }}>
        <color attach="background" args={['#0c1018']} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[4, 9, 5]} intensity={1.3} castShadow />
        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow><planeGeometry args={[14, 14]} /><meshStandardMaterial color="#121926" /></mesh>
        <gridHelper args={[14, 28, '#1d2535', '#161d2a']} position={[0, 0.005, 0]} />
        {values?.length ? <Columns values={values} /> : null}
        <OrbitControls enablePan={false} autoRotate autoRotateSpeed={0.6} minDistance={5} maxDistance={16} maxPolarAngle={1.3} />
      </Canvas>
    </div>
  );
}
