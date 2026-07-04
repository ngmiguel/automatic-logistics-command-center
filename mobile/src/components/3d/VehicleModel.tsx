import { useRef } from 'react';
import { useFrame } from '@react-three/fiber/native';
import { Group } from 'three';
import type { VehicleVariant } from '@/types';
import { MODEL_VARIANTS, VARIANT_LABELS } from '@/types';

interface Props {
  variant: VehicleVariant;
  scale?: number;
  autoRotate?: boolean;
  position?: [number, number, number];
}

function ExecutiveSedan({ color }: { color: string }) {
  return (
    <group>
      <mesh position={[0, 0.35, 0]}>
        <boxGeometry args={[2.2, 0.5, 4.2]} />
        <meshStandardMaterial color={color} metalness={0.9} roughness={0.15} />
      </mesh>
      <mesh position={[0, 0.75, -0.2]}>
        <boxGeometry args={[1.8, 0.45, 2.2]} />
        <meshStandardMaterial color="#111827" metalness={0.8} roughness={0.2} />
      </mesh>
      {[[-0.9, 0.35, 0.8], [0.9, 0.35, 0.8], [-0.9, 0.35, -0.8], [0.9, 0.35, -0.8]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.32, 0.32, 0.2, 12]} />
          <meshStandardMaterial color="#1f2937" metalness={0.6} roughness={0.4} />
        </mesh>
      ))}
      <mesh position={[0, 0.32, 2.15]}>
        <boxGeometry args={[1.7, 0.25, 0.15]} />
        <meshStandardMaterial color="#60a5fa" emissive="#3b82f6" emissiveIntensity={0.5} />
      </mesh>
    </group>
  );
}

function CrossoverSUV({ color }: { color: string }) {
  return (
    <group>
      <mesh position={[0, 0.55, 0]}>
        <boxGeometry args={[2.0, 0.7, 4.0]} />
        <meshStandardMaterial color={color} metalness={0.85} roughness={0.2} />
      </mesh>
      <mesh position={[0, 1.05, -0.3]}>
        <boxGeometry args={[1.85, 0.65, 2.4]} />
        <meshStandardMaterial color="#1e293b" metalness={0.75} roughness={0.25} />
      </mesh>
      {[[-0.85, 0.35, 1.2], [0.85, 0.35, 1.2], [-0.85, 0.35, -1.2], [0.85, 0.35, -1.2]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.38, 0.38, 0.25, 12]} />
          <meshStandardMaterial color="#111827" metalness={0.5} roughness={0.5} />
        </mesh>
      ))}
      <mesh position={[0, 0.6, 2.05]}>
        <boxGeometry args={[1.5, 0.3, 0.12]} />
        <meshStandardMaterial color="#34d399" emissive="#059669" emissiveIntensity={0.4} />
      </mesh>
    </group>
  );
}

function AutonomousHauler({ color }: { color: string }) {
  return (
    <group>
      <mesh position={[0, 0.7, -0.5]}>
        <boxGeometry args={[2.4, 1.0, 3.5]} />
        <meshStandardMaterial color={color} metalness={0.9} roughness={0.1} />
      </mesh>
      <mesh position={[0, 0.55, 2.0]}>
        <boxGeometry args={[2.3, 0.9, 4.5]} />
        <meshStandardMaterial color="#312e81" metalness={0.8} roughness={0.2} />
      </mesh>
      {[[-1.0, 0.35, 2.5], [1.0, 0.35, 2.5], [-1.0, 0.35, -1.5], [1.0, 0.35, -1.5]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.42, 0.42, 0.28, 12]} />
          <meshStandardMaterial color="#0f172a" metalness={0.6} roughness={0.4} />
        </mesh>
      ))}
    </group>
  );
}

export function VehicleModel({ variant, scale = 1, autoRotate = true, position = [0, 0, 0] }: Props) {
  const groupRef = useRef<Group>(null);
  const { color } = VARIANT_LABELS[variant];

  useFrame((_, delta) => {
    if (autoRotate && groupRef.current) {
      groupRef.current.rotation.y += delta * 0.5;
    }
  });

  const body = {
    executive: <ExecutiveSedan color={color} />,
    crossover: <CrossoverSUV color={color} />,
    hauler: <AutonomousHauler color={color} />,
  }[variant];

  return (
    <group ref={groupRef} position={position} scale={scale}>
      {body}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
        <circleGeometry args={[3, 24]} />
        <meshStandardMaterial color="#1e293b" transparent opacity={0.5} />
      </mesh>
    </group>
  );
}

export function VehicleModelByName({ model, ...props }: { model: string } & Omit<Props, 'variant'>) {
  const variant = MODEL_VARIANTS[model] || 'executive';
  return <VehicleModel variant={variant} {...props} />;
}
