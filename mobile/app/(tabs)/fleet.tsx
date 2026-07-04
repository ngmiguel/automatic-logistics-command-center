import { ScrollView, View, Text, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { FadeInRight } from 'react-native-reanimated';
import { fleetApi } from '@/api/services';
import { ShowroomCanvas } from '@/components/3d/ShowroomCanvas';
import { GlassCard } from '@/components/ui/GlassCard';
import { SlideIn } from '@/components/ui/AnimatedScreen';
import { VARIANT_LABELS, type VehicleVariant } from '@/types';
import { colors } from '@/theme/colors';

const stateColors: Record<string, string> = {
  idle: colors.primary,
  en_route: colors.success,
  incident: colors.danger,
  maintenance: colors.warning,
};

export default function FleetScreen() {
  const { data: vehicles = [] } = useQuery({
    queryKey: ['fleet-vehicles'],
    queryFn: () => fleetApi.listVehicles({ limit: 30 }).then((r) => r.data),
    refetchInterval: 5000,
  });

  const { data: drivers = [] } = useQuery({
    queryKey: ['fleet-drivers'],
    queryFn: () => fleetApi.listDrivers().then((r) => r.data),
  });

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Animated.Text entering={FadeInRight} style={styles.title}>Fleet Management</Animated.Text>
        <Text style={styles.sub}>{vehicles.length} véhicules · {drivers.length} chauffeurs virtuels</Text>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.showcase}>
          {(['executive', 'crossover', 'hauler'] as VehicleVariant[]).map((v, i) => (
            <SlideIn key={v} index={i}>
              <View style={styles.showcaseCard}>
                <ShowroomCanvas variant={v} height={160} />
                <Text style={styles.brand}>{VARIANT_LABELS[v].brand}</Text>
                <Text style={styles.model}>{VARIANT_LABELS[v].name}</Text>
              </View>
            </SlideIn>
          ))}
        </ScrollView>

        {vehicles.slice(0, 10).map((v, i) => (
          <SlideIn key={v.id} index={i}>
            <GlassCard style={styles.card} glow={v.state === 'incident'}>
              <View style={styles.cardRow}>
                <View style={styles.cardPreview}>
                  <ShowroomCanvas model={v.model} height={100} />
                </View>
                <View style={styles.cardInfo}>
                  <Text style={styles.plate}>{v.license_plate}</Text>
                  <Text style={styles.modelName}>{v.model}</Text>
                  <View style={[styles.badge, { borderColor: stateColors[v.state] || colors.muted }]}>
                    <Text style={[styles.badgeText, { color: stateColors[v.state] || colors.muted }]}>
                      {v.state}
                    </Text>
                  </View>
                  <Text style={styles.meta}>⛽ {v.fuel_level.toFixed(0)}% · 🏎 {v.speed_kmh.toFixed(0)} km/h</Text>
                </View>
              </View>
            </GlassCard>
          </SlideIn>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: 16 },
  title: { fontSize: 26, fontWeight: '800', color: colors.text },
  sub: { color: colors.muted, fontSize: 13, marginBottom: 16 },
  showcase: { marginBottom: 20 },
  showcaseCard: { width: 200, marginRight: 12 },
  brand: { color: colors.primary, fontSize: 11, fontWeight: '600', marginTop: 8 },
  model: { color: colors.muted, fontSize: 10 },
  card: { marginBottom: 12 },
  cardRow: { flexDirection: 'row', gap: 12 },
  cardPreview: { width: 120, borderRadius: 10, overflow: 'hidden' },
  cardInfo: { flex: 1, justifyContent: 'center' },
  plate: { fontSize: 16, fontWeight: '700', color: colors.text },
  modelName: { fontSize: 12, color: colors.muted, marginTop: 2 },
  badge: { alignSelf: 'flex-start', borderWidth: 1, borderRadius: 8, paddingHorizontal: 8, paddingVertical: 2, marginTop: 6 },
  badgeText: { fontSize: 10, fontWeight: '600', textTransform: 'uppercase' },
  meta: { fontSize: 11, color: colors.muted, marginTop: 6 },
});
