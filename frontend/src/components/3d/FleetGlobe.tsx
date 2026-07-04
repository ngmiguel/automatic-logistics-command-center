import { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import type { Telemetry } from '@/types';

function Globe({ telemetry }: { telemetry: Telemetry[] }) {
  const globeRef = useRef<THREE.Mesh>(null);
  const dotsRef = useRef<THREE.InstancedMesh>(null);

  useFrame((_, d) => {
    if (globeRef.current) globeRef.current.rotation.y += d * 0.05;
  });

  const positions = useMemo(() => {
    return telemetry.slice(0, 200).map((t) => {
      const phi = ((90 - t.latitude) * Math.PI) / 180;
      const theta = ((t.longitude + 180) * Math.PI) / 180;
      const r = 2.05;
      return new THREE.Vector3(
        -r * Math.sin(phi) * Math.cos(theta),
        r * Math.cos(phi),
        r * Math.sin(phi) * Math.sin(theta),
      );
    });
  }, [telemetry]);

  const colors = useMemo(() => {
    const stateColor: Record<string, string> = {
      en_route: '#22c55e',
      idle: '#3b82f6',
      incident: '#ef4444',
      maintenance: '#f59e0b',
    };
    return telemetry.slice(0, 200).map((t) => new THREE.Color(stateColor[t.state] || '#6b7280'));
  }, [telemetry]);

  useEffect(() => {
    if (!dotsRef.current || positions.length === 0) return;
    const dummy = new THREE.Object3D();
    positions.forEach((pos, i) => {
      dummy.position.copy(pos);
      dummy.scale.setScalar(0.04);
      dummy.updateMatrix();
      dotsRef.current!.setMatrixAt(i, dummy.matrix);
      dotsRef.current!.setColorAt(i, colors[i]);
    });
    dotsRef.current.instanceMatrix.needsUpdate = true;
    if (dotsRef.current.instanceColor) dotsRef.current.instanceColor.needsUpdate = true;
  }, [positions, colors]);

  return (
    <group>
      <mesh ref={globeRef}>
        <sphereGeometry args={[2, 64, 64]} />
        <meshStandardMaterial
          color="#0c1929"
          metalness={0.8}
          roughness={0.4}
          transparent
          opacity={0.85}
          wireframe={false}
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[2.02, 32, 32]} />
        <meshBasicMaterial color="#1e40af" wireframe transparent opacity={0.08} />
      </mesh>
      {positions.length > 0 && (
        <instancedMesh ref={dotsRef} args={[undefined, undefined, positions.length]}>
          <sphereGeometry args={[1, 8, 8]} />
          <meshStandardMaterial emissive="#60a5fa" emissiveIntensity={2} toneMapped={false} />
        </instancedMesh>
      )}
    </group>
  );
}

function Scene({ telemetry }: { telemetry: Telemetry[] }) {
  return (
    <>
      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} intensity={1.5} color="#3b82f6" />
      <pointLight position={[-10, -5, -10]} intensity={0.5} color="#7c3aed" />
      <Stars radius={50} depth={30} count={2000} factor={2} saturation={0} fade />
      <Globe telemetry={telemetry} />
      <OrbitControls enablePan={false} minDistance={4} maxDistance={10} autoRotate autoRotateSpeed={0.2} />
      <EffectComposer>
        <Bloom luminanceThreshold={0.1} intensity={0.6} />
      </EffectComposer>
    </>
  );
}

export function FleetGlobe({ telemetry, className = 'h-full w-full' }: { telemetry: Telemetry[]; className?: string }) {
  return (
    <div className={className}>
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <color attach="background" args={['transparent']} />
        <Scene telemetry={telemetry} />
      </Canvas>
    </div>
  );
}
