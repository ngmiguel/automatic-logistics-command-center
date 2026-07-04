import { Suspense } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment } from '@react-three/drei';
import { fleetApi } from '@/api/services';
import { VehicleModel, VehicleModelByName } from '@/components/3d/VehicleModel';
import { PageTransition, SlideUp } from '@/components/ui/PageTransition';
import { VARIANT_LABELS, type VehicleVariant } from '@/types';
import { Fuel, Gauge, MapPin } from 'lucide-react';

function VehiclePreview3D({ model }: { model: string }) {
  return (
    <Canvas camera={{ position: [4, 2, 4], fov: 40 }}>
      <ambientLight intensity={0.4} />
      <spotLight position={[5, 10, 5]} intensity={1.5} castShadow />
      <VehicleModelByName model={model} scale={0.5} position={[0, -0.5, 0]} />
      <OrbitControls enablePan={false} autoRotate autoRotateSpeed={1} />
      <Environment preset="night" />
    </Canvas>
  );
}

const stateColors: Record<string, string> = {
  idle: 'bg-blue-500/20 text-blue-400',
  en_route: 'bg-green-500/20 text-green-400',
  incident: 'bg-red-500/20 text-red-400',
  maintenance: 'bg-amber-500/20 text-amber-400',
};

export function FleetPage() {
  const { data: vehicles = [], isLoading } = useQuery({
    queryKey: ['fleet-vehicles'],
    queryFn: () => fleetApi.listVehicles({ limit: 50 }).then((r) => r.data),
    refetchInterval: 5000,
  });

  const { data: drivers = [] } = useQuery({
    queryKey: ['fleet-drivers'],
    queryFn: () => fleetApi.listDrivers().then((r) => r.data),
  });

  return (
    <PageTransition className="p-6 space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="font-display text-2xl font-bold">Fleet Management</h1>
        <p className="text-gray-500 text-sm">{vehicles.length} autonomous vehicles · {drivers.length} virtual drivers</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {(['executive', 'crossover', 'hauler'] as VehicleVariant[]).map((v, i) => (
          <SlideUp key={v} delay={i * 0.1}>
            <div className="glass-panel glow-border h-48 overflow-hidden relative">
              <Canvas camera={{ position: [3, 2, 3] }}>
                <ambientLight intensity={0.5} />
                <spotLight position={[5, 5, 5]} intensity={1} />
                <VehicleModel variant={v} scale={0.45} />
                <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.8} />
              </Canvas>
              <div className="absolute bottom-0 inset-x-0 p-3 bg-gradient-to-t from-alcc-bg to-transparent">
                <p className="text-xs font-display text-blue-400">{VARIANT_LABELS[v].brand}</p>
                <p className="text-[10px] text-gray-500">{VARIANT_LABELS[v].name}</p>
              </div>
            </div>
          </SlideUp>
        ))}
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500 animate-pulse">Loading fleet...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {vehicles.slice(0, 12).map((v, i) => (
            <motion.div
              key={v.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ scale: 1.02 }}
              className="glass-panel glow-border overflow-hidden"
            >
              <div className="h-36 bg-alcc-surface">
                <Suspense fallback={null}>
                  <VehiclePreview3D model={v.model} />
                </Suspense>
              </div>
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <span className="font-display font-semibold">{v.license_plate}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${stateColors[v.state] || ''}`}>{v.state}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{v.model}</p>
                <div className="flex gap-4 mt-3 text-xs text-gray-400">
                  <span className="flex items-center gap-1"><Fuel className="w-3 h-3" />{v.fuel_level.toFixed(0)}%</span>
                  <span className="flex items-center gap-1"><Gauge className="w-3 h-3" />{v.speed_kmh.toFixed(0)} km/h</span>
                  <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{v.latitude.toFixed(1)}°</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </PageTransition>
  );
}
