import { ScrollView, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { FadeInRight } from 'react-native-reanimated';
import { notificationApi } from '@/api/services';
import { GlassCard } from '@/components/ui/GlassCard';
import { SlideIn } from '@/components/ui/AnimatedScreen';
import { colors } from '@/theme/colors';

const severityColors: Record<string, string> = {
  low: colors.primary,
  medium: colors.warning,
  high: colors.danger,
  critical: '#dc2626',
};

export default function NotificationsScreen() {
  const qc = useQueryClient();

  const { data: notifications = [] } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationApi.list().then((r) => r.data),
    refetchInterval: 5000,
  });

  const { data: incidents = [] } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => notificationApi.listIncidents().then((r) => r.data),
    refetchInterval: 5000,
  });

  const markRead = useMutation({
    mutationFn: (id: string) => notificationApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const resolve = useMutation({
    mutationFn: (id: string) => notificationApi.resolveIncident(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['incidents'] }),
  });

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Animated.Text entering={FadeInRight} style={styles.title}>Alertes & Incidents</Animated.Text>

        <Text style={styles.section}>Incidents actifs ({incidents.filter((i) => !i.resolved).length})</Text>
        {incidents.filter((i) => !i.resolved).slice(0, 10).map((inc, i) => (
          <SlideIn key={inc.id} index={i}>
            <GlassCard style={styles.card} glow>
              <View style={styles.row}>
                <Text style={[styles.severity, { color: severityColors[inc.severity] || colors.danger }]}>
                  {inc.severity.toUpperCase()}
                </Text>
                <Text style={styles.vid}>{inc.vehicle_id.slice(0, 8)}…</Text>
              </View>
              <Text style={styles.msg}>{inc.description}</Text>
              <TouchableOpacity style={styles.resolveBtn} onPress={() => resolve.mutate(inc.id)}>
                <Text style={styles.resolveText}>Résoudre</Text>
              </TouchableOpacity>
            </GlassCard>
          </SlideIn>
        ))}

        <Text style={[styles.section, { marginTop: 20 }]}>Notifications ({notifications.length})</Text>
        {notifications.slice(0, 15).map((n, i) => (
          <SlideIn key={n.id} index={i}>
            <GlassCard style={[styles.card, !n.is_read ? styles.unread : undefined]}>
              <View style={styles.row}>
                <Text style={styles.notifTitle}>{n.title}</Text>
                {!n.is_read && <View style={styles.unreadDot} />}
              </View>
              <Text style={styles.msg}>{n.message}</Text>
              {!n.is_read && (
                <TouchableOpacity onPress={() => markRead.mutate(n.id)}>
                  <Text style={styles.markRead}>Marquer lu</Text>
                </TouchableOpacity>
              )}
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
  title: { fontSize: 26, fontWeight: '800', color: colors.text, marginBottom: 16 },
  section: { color: colors.muted, fontSize: 11, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10 },
  card: { marginBottom: 10 },
  unread: { borderColor: colors.primary },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  severity: { fontSize: 10, fontWeight: '700' },
  vid: { color: colors.muted, fontSize: 11 },
  notifTitle: { color: colors.text, fontWeight: '600', flex: 1 },
  unreadDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.primary },
  msg: { color: colors.muted, fontSize: 13, marginTop: 6 },
  resolveBtn: { marginTop: 10, backgroundColor: colors.success, alignSelf: 'flex-start', paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8 },
  resolveText: { color: '#fff', fontWeight: '600', fontSize: 12 },
  markRead: { color: colors.primary, fontSize: 12, marginTop: 8 },
});
