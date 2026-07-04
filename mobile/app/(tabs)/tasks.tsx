import { ScrollView, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useMutation } from '@tanstack/react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { FadeInRight, FadeInUp } from 'react-native-reanimated';
import { tasksApi } from '@/api/services';
import { GlassCard } from '@/components/ui/GlassCard';
import { SlideIn } from '@/components/ui/AnimatedScreen';
import { colors } from '@/theme/colors';

const TASKS = [
  { key: 'optimize', label: 'Optimiser les routes', desc: 'Celery — recalcul des itinéraires optimaux', fn: () => tasksApi.optimizeRoutes(), icon: '🗺️' },
  { key: 'maintenance', label: 'Planifier maintenance', desc: 'Celery — scheduling préventif flotte', fn: () => tasksApi.scheduleMaintenance(), icon: '🔧' },
  { key: 'analytics', label: 'Calculer analytics', desc: 'Celery — agrégation KPIs en arrière-plan', fn: () => tasksApi.computeAnalytics(), icon: '📊' },
];

export default function TasksScreen() {
  const optimize = useMutation({ mutationFn: () => tasksApi.optimizeRoutes() });
  const maintenance = useMutation({ mutationFn: () => tasksApi.scheduleMaintenance() });
  const analytics = useMutation({ mutationFn: () => tasksApi.computeAnalytics() });

  const muts: Record<string, typeof optimize> = { optimize, maintenance, analytics };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Animated.Text entering={FadeInRight} style={styles.title}>Async Tasks</Animated.Text>
        <Text style={styles.sub}>Déclenchez les workers Celery depuis mobile</Text>

        {TASKS.map((task, i) => {
          const mut = muts[task.key];
          return (
            <SlideIn key={task.key} index={i}>
              <GlassCard style={styles.card} glow={mut.isSuccess}>
                <View style={styles.row}>
                  <Text style={styles.icon}>{task.icon}</Text>
                  <View style={styles.info}>
                    <Text style={styles.label}>{task.label}</Text>
                    <Text style={styles.desc}>{task.desc}</Text>
                    {mut.isSuccess && (
                      <Animated.Text entering={FadeInUp} style={styles.success}>✓ Tâche lancée</Animated.Text>
                    )}
                    {mut.isError && <Text style={styles.error}>Erreur — vérifiez le worker Celery</Text>}
                  </View>
                </View>
                <TouchableOpacity
                  style={[styles.btn, mut.isPending && styles.btnDisabled]}
                  onPress={() => mut.mutate()}
                  disabled={mut.isPending}
                >
                  {mut.isPending ? (
                    <ActivityIndicator color="#fff" size="small" />
                  ) : (
                    <Text style={styles.btnText}>Exécuter</Text>
                  )}
                </TouchableOpacity>
              </GlassCard>
            </SlideIn>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  scroll: { padding: 16 },
  title: { fontSize: 26, fontWeight: '800', color: colors.text },
  sub: { color: colors.muted, fontSize: 13, marginBottom: 20 },
  card: { marginBottom: 14 },
  row: { flexDirection: 'row', gap: 12, marginBottom: 14 },
  icon: { fontSize: 32 },
  info: { flex: 1 },
  label: { color: colors.text, fontWeight: '700', fontSize: 15 },
  desc: { color: colors.muted, fontSize: 12, marginTop: 4 },
  success: { color: colors.success, fontSize: 12, marginTop: 6, fontWeight: '600' },
  error: { color: colors.danger, fontSize: 12, marginTop: 6 },
  btn: { backgroundColor: colors.accent, borderRadius: 10, padding: 12, alignItems: 'center' },
  btnDisabled: { opacity: 0.6 },
  btnText: { color: '#fff', fontWeight: '700' },
});
