import React from 'react';
import { ScrollView, View, Text, StyleSheet, Dimensions } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { FadeInRight } from 'react-native-reanimated';
import Svg, { Rect, Text as SvgText } from 'react-native-svg';
import { analyticsApi } from '@/api/services';
import { StatCard } from '@/components/ui/StatCard';
import { GlassCard } from '@/components/ui/GlassCard';
import { SlideIn } from '@/components/ui/AnimatedScreen';
import { colors } from '@/theme/colors';

const { width } = Dimensions.get('window');

function BarChart({ data }: { data: { label: string; value: number; color: string }[] }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  const chartW = width - 64;
  const barW = chartW / data.length - 8;

  return (
    <Svg width={chartW} height={160}>
      {data.map((d, i) => {
        const h = (d.value / max) * 120;
        return (
          <React.Fragment key={d.label}>
            <Rect
              x={i * (barW + 8) + 4}
              y={140 - h}
              width={barW}
              height={h}
              fill={d.color}
              rx={4}
              opacity={0.85}
            />
            <SvgText
              x={i * (barW + 8) + barW / 2 + 4}
              y={155}
              fill={colors.muted}
              fontSize={9}
              textAnchor="middle"
            >
              {d.label}
            </SvgText>
          </React.Fragment>
        );
      })}
    </Svg>
  );
}

export default function AnalyticsScreen() {
  const { data: summary } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => analyticsApi.summary().then((r) => r.data),
    refetchInterval: 10000,
  });

  const { data: fleetAnalytics } = useQuery({
    queryKey: ['analytics-fleet'],
    queryFn: () => analyticsApi.fleet().then((r) => r.data),
  });

  const fleet = summary?.fleet;
  const missions = summary?.missions || {};

  const chartData = [
    { label: 'Idle', value: fleet?.idle_vehicles ?? 0, color: colors.primary },
    { label: 'Route', value: fleet?.en_route_vehicles ?? 0, color: colors.success },
    { label: 'Incid.', value: fleet?.incident_vehicles ?? 0, color: colors.danger },
    { label: 'Maint.', value: fleet?.maintenance_vehicles ?? 0, color: colors.warning },
  ];

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Animated.Text entering={FadeInRight} style={styles.title}>Analytics</Animated.Text>
        <Text style={styles.sub}>KPIs flotte et missions en temps réel</Text>

        <View style={styles.grid}>
          <StatCard title="Véhicules" value={fleet?.total_vehicles ?? '—'} icon="car" index={0} />
          <StatCard title="Carburant moy." value={fleet ? `${fleet.average_fuel_level.toFixed(0)}%` : '—'} icon="water" index={1} />
          <StatCard title="Vitesse moy." value={fleet ? `${fleet.average_speed_kmh.toFixed(0)}` : '—'} icon="speedometer" index={2} />
          <StatCard title="Utilisation" value={fleet ? `${(fleet.fleet_utilization_rate * 100).toFixed(0)}%` : '—'} icon="trending-up" color={colors.accent} index={3} />
        </View>

        <SlideIn index={0}>
          <GlassCard glow>
            <Text style={styles.chartTitle}>Répartition flotte</Text>
            <BarChart data={chartData} />
          </GlassCard>
        </SlideIn>

        <SlideIn index={1}>
          <GlassCard style={styles.missionsCard}>
            <Text style={styles.chartTitle}>Missions</Text>
            {Object.entries(missions).slice(0, 6).map(([k, v]) => (
              <View key={k} style={styles.missionRow}>
                <Text style={styles.missionKey}>{k}</Text>
                <Text style={styles.missionVal}>{String(v)}</Text>
              </View>
            ))}
          </GlassCard>
        </SlideIn>

        {fleetAnalytics && (
          <SlideIn index={2}>
            <GlassCard>
              <Text style={styles.chartTitle}>Fleet Analytics (API)</Text>
              <Text style={styles.raw}>{JSON.stringify(fleetAnalytics, null, 2).slice(0, 300)}…</Text>
            </GlassCard>
          </SlideIn>
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
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 16 },
  chartTitle: { color: colors.text, fontWeight: '700', marginBottom: 12, fontSize: 14 },
  missionsCard: { marginTop: 12 },
  missionRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: colors.border },
  missionKey: { color: colors.muted, fontSize: 13 },
  missionVal: { color: colors.text, fontWeight: '600' },
  raw: { color: colors.muted, fontSize: 10, fontFamily: 'monospace' },
});
