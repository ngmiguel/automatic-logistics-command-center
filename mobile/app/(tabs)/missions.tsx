import { useState } from 'react';
import {
  ScrollView, View, Text, TextInput, TouchableOpacity, StyleSheet,
} from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { FadeInRight, Layout } from 'react-native-reanimated';
import { routingApi, fleetApi } from '@/api/services';
import { GlassCard } from '@/components/ui/GlassCard';
import { SlideIn } from '@/components/ui/AnimatedScreen';
import { colors } from '@/theme/colors';

const statusColors: Record<string, string> = {
  pending: colors.muted,
  assigned: colors.primary,
  in_progress: colors.success,
  completed: colors.success,
  cancelled: colors.danger,
};

export default function MissionsScreen() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    origin_lat: '48.85', origin_lng: '2.35', dest_lat: '51.5', dest_lng: '-0.12',
    cargo_description: '', priority: '1',
  });

  const { data: missions = [] } = useQuery({
    queryKey: ['missions'],
    queryFn: () => routingApi.listMissions().then((r) => r.data),
    refetchInterval: 5000,
  });

  const { data: idleVehicles = [] } = useQuery({
    queryKey: ['idle-vehicles'],
    queryFn: () => fleetApi.listVehicles({ state: 'idle', limit: 10 }).then((r) => r.data),
  });

  const createMut = useMutation({
    mutationFn: () => routingApi.createMission({
      origin_lat: parseFloat(form.origin_lat),
      origin_lng: parseFloat(form.origin_lng),
      dest_lat: parseFloat(form.dest_lat),
      dest_lng: parseFloat(form.dest_lng),
      cargo_description: form.cargo_description,
      priority: parseInt(form.priority, 10),
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['missions'] }); setShowForm(false); },
  });

  const assignMut = useMutation({
    mutationFn: ({ mid, vid }: { mid: string; vid: string }) => routingApi.assignMission(mid, vid),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['missions'] }),
  });

  const completeMut = useMutation({
    mutationFn: (id: string) => routingApi.completeMission(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['missions'] }),
  });

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
          <Animated.Text entering={FadeInRight} style={styles.title}>Missions</Animated.Text>
          <TouchableOpacity style={styles.addBtn} onPress={() => setShowForm(!showForm)}>
            <Text style={styles.addBtnText}>{showForm ? '✕' : '+ Nouvelle'}</Text>
          </TouchableOpacity>
        </View>

        {showForm && (
          <Animated.View entering={FadeInRight} layout={Layout.springify()} style={styles.form}>
            <TextInput style={styles.input} placeholder="Description cargo" placeholderTextColor={colors.muted}
              value={form.cargo_description} onChangeText={(t) => setForm({ ...form, cargo_description: t })} />
            <View style={styles.row}>
              <TextInput style={[styles.input, styles.half]} placeholder="Origine lat" placeholderTextColor={colors.muted}
                value={form.origin_lat} onChangeText={(t) => setForm({ ...form, origin_lat: t })} keyboardType="numeric" />
              <TextInput style={[styles.input, styles.half]} placeholder="Origine lng" placeholderTextColor={colors.muted}
                value={form.origin_lng} onChangeText={(t) => setForm({ ...form, origin_lng: t })} keyboardType="numeric" />
            </View>
            <TouchableOpacity style={styles.submitBtn} onPress={() => createMut.mutate()}>
              <Text style={styles.submitText}>Créer mission</Text>
            </TouchableOpacity>
          </Animated.View>
        )}

        {missions.slice(0, 15).map((m, i) => (
          <SlideIn key={m.id} index={i}>
            <GlassCard style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.missionId}>#{m.id.slice(0, 8)}</Text>
                <Text style={[styles.status, { color: statusColors[m.status] || colors.muted }]}>{m.status}</Text>
              </View>
              <Text style={styles.cargo}>{m.cargo_description || 'Sans description'}</Text>
              <Text style={styles.coords}>
                ({m.origin_lat.toFixed(1)}, {m.origin_lng.toFixed(1)}) → ({m.dest_lat.toFixed(1)}, {m.dest_lng.toFixed(1)})
              </Text>
              <View style={styles.actions}>
                {m.status === 'pending' && idleVehicles[0] && (
                  <TouchableOpacity
                    style={styles.actionBtn}
                    onPress={() => assignMut.mutate({ mid: m.id, vid: idleVehicles[0].id })}
                  >
                    <Text style={styles.actionText}>Assigner</Text>
                  </TouchableOpacity>
                )}
                {(m.status === 'assigned' || m.status === 'in_progress') && (
                  <TouchableOpacity style={[styles.actionBtn, styles.completeBtn]} onPress={() => completeMut.mutate(m.id)}>
                    <Text style={styles.actionText}>Compléter</Text>
                  </TouchableOpacity>
                )}
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
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  title: { fontSize: 26, fontWeight: '800', color: colors.text },
  addBtn: { backgroundColor: colors.primary, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 10 },
  addBtnText: { color: '#fff', fontWeight: '600', fontSize: 13 },
  form: { gap: 10, marginBottom: 16 },
  input: { backgroundColor: colors.surface, borderRadius: 10, padding: 12, color: colors.text, borderWidth: 1, borderColor: colors.border },
  row: { flexDirection: 'row', gap: 8 },
  half: { flex: 1 },
  submitBtn: { backgroundColor: colors.accent, borderRadius: 10, padding: 14, alignItems: 'center' },
  submitText: { color: '#fff', fontWeight: '700' },
  card: { marginBottom: 10 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between' },
  missionId: { color: colors.text, fontWeight: '700' },
  status: { fontSize: 11, fontWeight: '600', textTransform: 'uppercase' },
  cargo: { color: colors.muted, fontSize: 13, marginTop: 6 },
  coords: { color: colors.muted, fontSize: 11, marginTop: 4 },
  actions: { flexDirection: 'row', gap: 8, marginTop: 10 },
  actionBtn: { backgroundColor: colors.primary, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  completeBtn: { backgroundColor: colors.success },
  actionText: { color: '#fff', fontSize: 12, fontWeight: '600' },
});
