import { Suspense, useRef } from 'react';
import { View, StyleSheet, ActivityIndicator } from 'react-native';
import { Canvas, useFrame } from '@react-three/fiber/native';
import { VehicleModel, VehicleModelByName } from './VehicleModel';
import type { VehicleVariant } from '@/types';
import { colors } from '@/theme/colors';

function RotatingPlatform() {
  const ref = useRef<any>(null);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.3;
  });
  return (
    <mesh ref={ref} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
      <cylinderGeometry args={[2.5, 2.5, 0.15, 32]} />
      <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.2} />
    </mesh>
  );
}

function Particles() {
  const ref = useRef<any>(null);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.1;
  });
  const pts = Array.from({ length: 40 }, (_, i) => {
    const angle = (i / 40) * Math.PI * 2;
    const r = 4 + (i % 3) * 0.5;
    return [Math.cos(angle) * r, (i % 5) * 0.4, Math.sin(angle) * r] as [number, number, number];
  });
  return (
    <group ref={ref}>
      {pts.map((p, i) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[0.04, 6, 6]} />
          <meshStandardMaterial color="#3b82f6" emissive="#3b82f6" emissiveIntensity={0.8} />
        </mesh>
      ))}
    </group>
  );
}

interface Props {
  variant?: VehicleVariant;
  model?: string;
  height?: number;
}

function Scene({ variant = 'executive', model }: Props) {
  return (
    <>
      <ambientLight intensity={0.5} />
      <spotLight position={[5, 8, 5]} intensity={1.2} />
      <pointLight position={[-3, 2, -3]} intensity={0.6} color="#8b5cf6" />
      <RotatingPlatform />
      <Particles />
      {model ? (
        <VehicleModelByName model={model} scale={0.45} position={[0, -0.35, 0]} />
      ) : (
        <VehicleModel variant={variant} scale={0.45} position={[0, -0.35, 0]} />
      )}
    </>
  );
}

export function ShowroomCanvas({ variant, model, height = 220 }: Props) {
  return (
    <View style={[styles.container, { height }]}>
      <Suspense fallback={<ActivityIndicator color={colors.primary} style={styles.loader} />}>
        <Canvas camera={{ position: [4, 2.5, 4], fov: 45 }}>
          <Scene variant={variant} model={model} />
        </Canvas>
      </Suspense>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { width: '100%', borderRadius: 16, overflow: 'hidden', backgroundColor: colors.surface },
  loader: { flex: 1, alignSelf: 'center' },
});
