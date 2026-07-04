import { ScrollView, View, Text, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { FadeInRight } from 'react-native-reanimated';
import { trackingApi } from '@/api/services';
import { useWebSocket } from '@/hooks/useWebSocket';
import { FleetGlobe } from '@/components/3d/FleetGlobe';
import { GlassCard } from '@/components/ui/GlassCard';
import { SlideIn } from '@/components/ui/AnimatedScreen';
import { colors } from '@/theme/colors';
import type { Telemetry } from '@/types';

export default function TrackingScreen() {
  const { data: live = [] } = useQuery({
    queryKey: ['tracking-live'],
    queryFn: () => trackingApi.live().then((r) => r.data),
    refetchInterval: 2000,
  });

  const { connected, lastMessage } = useWebSocket('/ws/dashboard');

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Animated.Text entering={FadeInRight} style={styles.title}>Live Tracking</Animated.Text>
        <Text style={styles.sub}>
          {connected ? '🟢 WebSocket connecté' : '🟡 Reconnexion...'} · {live.length} positions
        </Text>

        <SlideIn index={0}>
          <FleetGlobe telemetry={live} height={300} />
        </SlideIn>

        {live.slice(0, 8).map((t, i) => (
          <SlideIn key={t.vehicle_id} index={i + 1}>
            <GlassCard style={styles.card}>
              <View style={styles.row}>
                <View style={[styles.dot, { backgroundColor: t.state === 'incident' ? colors.danger : colors.success }]} />
                <View style={styles.info}>
                  <Text style={styles.vid}>{t.vehicle_id.slice(0, 12)}…</Text>
                  <Text style={styles.coords}>
                    {t.latitude.toFixed(3)}°, {t.longitude.toFixed(3)}° · {t.speed_kmh.toFixed(0)} km/h
                  </Text>
                </View>
                <Text style={styles.fuel}>{t.fuel_level.toFixed(0)}%</Text>
              </View>
            </GlassCard>
          </SlideIn>
        ))}

        {lastMessage?.channel === 'telemetry' && (
          <View style={styles.wsBox}>
            <Text style={styles.wsLabel}>Dernier événement WS</Text>
            <Text style={styles.wsText}>
              {(lastMessage.data as Telemetry).vehicle_id?.slice(0, 8)} @ {(lastMessage.data as Telemetry).speed_kmh?.toFixed(0)} km/h
            </Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: 16 },
  title: { fontSize: 26, fontWeight: '800', color: colors.text },
  sub: { color: colors.muted, fontSize: 13, marginBottom: 16 },
  card: { marginBottom: 8 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  info: { flex: 1 },
  vid: { color: colors.text, fontWeight: '600', fontSize: 13 },
  coords: { color: colors.muted, fontSize: 11, marginTop: 2 },
  fuel: { color: colors.primary, fontWeight: '700', fontSize: 14 },
  wsBox: { marginTop: 12, padding: 12, backgroundColor: colors.surface, borderRadius: 10 },
  wsLabel: { color: colors.muted, fontSize: 10, textTransform: 'uppercase' },
  wsText: { color: colors.text, marginTop: 4 },
});
