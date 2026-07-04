import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Float, PerspectiveCamera } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import { VehicleModel } from './VehicleModel';
import type { VehicleVariant } from '@/types';

const SHOWROOM_VEHICLES: { variant: VehicleVariant; position: [number, number, number]; label: string }[] = [
  { variant: 'executive', position: [-4, 0, 0], label: 'M-Series Inspired' },
  { variant: 'crossover', position: [0, 0, 0], label: 'X-Drive Inspired' },
  { variant: 'hauler', position: [4, 0, 0], label: 'i-Freight Inspired' },
];

function RotatingPlatform() {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((_, d) => { if (ref.current) ref.current.rotation.y += d * 0.05; });
  return (
    <mesh ref={ref} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
      <ringGeometry args={[5, 8, 64]} />
      <meshStandardMaterial color="#1e3a5f" metalness={0.9} roughness={0.2} side={THREE.DoubleSide} />
    </mesh>
  );
}

function ParticleRing() {
  const count = 200;
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const r = 6 + Math.random() * 2;
      arr[i * 3] = Math.cos(angle) * r;
      arr[i * 3 + 1] = Math.random() * 3;
      arr[i * 3 + 2] = Math.sin(angle) * r;
    }
    return arr;
  }, []);

  const ref = useRef<THREE.Points>(null);
  useFrame((_, d) => { if (ref.current) ref.current.rotation.y += d * 0.08; });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.06} color="#60a5fa" transparent opacity={0.8} sizeAttenuation />
    </points>
  );
}

function Scene() {
  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 3, 12]} fov={50} />
      <ambientLight intensity={0.3} />
      <spotLight position={[10, 15, 10]} angle={0.3} penumbra={1} intensity={2} castShadow color="#93c5fd" />
      <spotLight position={[-10, 10, -5]} angle={0.4} intensity={1} color="#a78bfa" />
      <pointLight position={[0, 5, 0]} intensity={0.5} color="#3b82f6" />
      <Stars radius={80} depth={40} count={3000} factor={3} saturation={0} fade speed={0.5} />
      <RotatingPlatform />
      <ParticleRing />
      {SHOWROOM_VEHICLES.map(({ variant, position }) => (
        <Float key={variant} speed={1.5} rotationIntensity={0.1} floatIntensity={0.3}>
          <VehicleModel variant={variant} position={position} scale={0.55} />
        </Float>
      ))}
      <OrbitControls enablePan={false} minDistance={8} maxDistance={20} maxPolarAngle={Math.PI / 2.1} autoRotate autoRotateSpeed={0.3} />
      <EffectComposer>
        <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.9} intensity={0.8} />
        <Vignette eskil={false} offset={0.1} darkness={0.8} />
      </EffectComposer>
    </>
  );
}

export function ShowroomScene({ className = 'h-full w-full' }: { className?: string }) {
  return (
    <div className={className}>
      <Canvas shadows dpr={[1, 2]} gl={{ antialias: true, alpha: true }}>
        <color attach="background" args={['#030712']} />
        <fog attach="fog" args={['#030712', 15, 35]} />
        <Scene />
      </Canvas>
    </div>
  );
}

export { SHOWROOM_VEHICLES };
