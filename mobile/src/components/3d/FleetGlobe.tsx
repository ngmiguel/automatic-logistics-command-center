import { Suspense, useMemo, useRef, useEffect } from 'react';
import { View, StyleSheet, ActivityIndicator, Text } from 'react-native';
import { Canvas, useFrame } from '@react-three/fiber/native';
import * as THREE from 'three';
import type { Telemetry } from '@/types';
import { colors } from '@/theme/colors';

function latLngToVec3(lat: number, lng: number, radius: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta),
  );
}

function Globe({ telemetry }: { telemetry: Telemetry[] }) {
  const globeRef = useRef<THREE.Mesh>(null);
  const dotsRef = useRef<THREE.InstancedMesh>(null);

  useFrame((_, delta) => {
    if (globeRef.current) globeRef.current.rotation.y += delta * 0.08;
  });

  const { positions, colors: dotColors } = useMemo(() => {
    const positions: THREE.Vector3[] = [];
    const dotColors: THREE.Color[] = [];
    telemetry.slice(0, 200).forEach((t) => {
      positions.push(latLngToVec3(t.latitude, t.longitude, 2.02));
      const c = t.state === 'incident' ? '#ef4444' : t.state === 'en_route' ? '#10b981' : '#3b82f6';
      dotColors.push(new THREE.Color(c));
    });
    return { positions, colors: dotColors };
  }, [telemetry]);

  useEffect(() => {
    if (!dotsRef.current || positions.length === 0) return;
    const dummy = new THREE.Object3D();
    positions.forEach((pos, i) => {
      dummy.position.copy(pos);
      dummy.scale.setScalar(0.05);
      dummy.updateMatrix();
      dotsRef.current!.setMatrixAt(i, dummy.matrix);
      dotsRef.current!.setColorAt(i, dotColors[i]);
    });
    dotsRef.current.instanceMatrix.needsUpdate = true;
    if (dotsRef.current.instanceColor) dotsRef.current.instanceColor.needsUpdate = true;
  }, [positions, dotColors]);

  return (
    <group>
      <mesh ref={globeRef}>
        <sphereGeometry args={[2, 32, 32]} />
        <meshStandardMaterial color="#1e3a5f" wireframe transparent opacity={0.35} />
      </mesh>
      <mesh>
        <sphereGeometry args={[1.98, 32, 32]} />
        <meshStandardMaterial color="#0f172a" metalness={0.3} roughness={0.8} />
      </mesh>
      {positions.length > 0 && (
        <instancedMesh ref={dotsRef} args={[undefined, undefined, positions.length]}>
          <sphereGeometry args={[1, 6, 6]} />
          <meshStandardMaterial emissive="#3b82f6" emissiveIntensity={0.6} />
        </instancedMesh>
      )}
    </group>
  );
}

interface Props {
  telemetry: Telemetry[];
  height?: number;
}

export function FleetGlobe({ telemetry, height = 280 }: Props) {
  return (
    <View style={[styles.container, { height }]}>
      <Suspense fallback={<ActivityIndicator color={colors.primary} />}>
        <Canvas camera={{ position: [0, 0, 5.5], fov: 50 }}>
          <ambientLight intensity={0.4} />
          <pointLight position={[5, 5, 5]} intensity={1} />
          <Globe telemetry={telemetry} />
        </Canvas>
      </Suspense>
      <View style={styles.badge}>
        <Text style={styles.badgeText}>{telemetry.length} véhicules live</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { width: '100%', borderRadius: 16, overflow: 'hidden', backgroundColor: colors.surface },
  badge: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    backgroundColor: 'rgba(59,130,246,0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: { color: colors.primary, fontSize: 11, fontWeight: '600' },
});
