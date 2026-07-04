import { ScrollView, View, Text, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { FadeInRight } from 'react-native-reanimated';
import { analyticsApi, trackingApi } from '@/api/services';
import { useWebSocket } from '@/hooks/useWebSocket';
import { StatCard } from '@/components/ui/StatCard';
import { FleetGlobe } from '@/components/3d/FleetGlobe';
import { SlideIn } from '@/components/ui/AnimatedScreen';
import { colors } from '@/theme/colors';
import type { Telemetry } from '@/types';

export default function DashboardScreen() {
  const { data: summary } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => analyticsApi.dashboard().then((r) => r.data),
    refetchInterval: 5000,
  });

  const { data: live = [] } = useQuery({
    queryKey: ['tracking-live'],
    queryFn: () => trackingApi.live().then((r) => r.data),
    refetchInterval: 3000,
  });

  const { connected, lastMessage } = useWebSocket('/ws/dashboard');
  const fleet = summary?.fleet;

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Animated.Text entering={FadeInRight} style={styles.title}>Command Center</Animated.Text>
        <Text style={styles.sub}>
          {connected ? '🟢 Live' : '🔴 Reconnexion...'} · {live.length} véhicules
        </Text>

        <SlideIn index={0}>
          <FleetGlobe telemetry={live} height={260} />
        </SlideIn>

        <View style={styles.grid}>
          <StatCard title="Flotte" value={fleet?.total_vehicles ?? '—'} icon="car" index={0} />
          <StatCard title="En route" value={fleet?.en_route_vehicles ?? '—'} icon="speedometer" color={colors.success} index={1} />
          <StatCard title="Incidents" value={fleet?.incident_vehicles ?? '—'} icon="warning" color={colors.danger} index={2} />
          <StatCard title="Utilisation" value={fleet ? `${(fleet.fleet_utilization_rate * 100).toFixed(0)}%` : '—'} icon="pulse" color={colors.accent} index={3} />
        </View>

        {lastMessage?.channel === 'telemetry' && (
          <SlideIn index={2}>
            <View style={styles.liveBox}>
              <Text style={styles.liveTitle}>Dernière télémétrie WS</Text>
              <Text style={styles.liveText}>
                Véhicule {(lastMessage.data as Telemetry).vehicle_id?.slice(0, 8)}… ·{' '}
                {(lastMessage.data as Telemetry).speed_kmh?.toFixed(0)} km/h
              </Text>
            </View>
          </SlideIn>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: 16, gap: 16 },
  title: { fontSize: 28, fontWeight: '800', color: colors.text },
  sub: { color: colors.muted, fontSize: 13, marginBottom: 8 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  liveBox: {
    backgroundColor: colors.card,
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.primary + '44',
  },
  liveTitle: { color: colors.primary, fontSize: 11, fontWeight: '600', textTransform: 'uppercase' },
  liveText: { color: colors.text, marginTop: 4, fontSize: 14 },
});
