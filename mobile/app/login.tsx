import { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ScrollView, ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';
import { authApi } from '@/api/services';
import { useAuthStore } from '@/store/authStore';
import { ShowroomCanvas } from '@/components/3d/ShowroomCanvas';
import { colors } from '@/theme/colors';

const DEMO_ACCOUNTS = [
  { email: 'admin@alcc.io', password: 'admin1234', role: 'Admin' },
  { email: 'dispatcher@alcc.io', password: 'dispatch123', role: 'Dispatcher' },
  { email: 'operator@alcc.io', password: 'operator123', role: 'Operator' },
];

export default function LoginScreen() {
  const [email, setEmail] = useState('operator@alcc.io');
  const [password, setPassword] = useState('operator123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const setAuth = useAuthStore((s) => s.setAuth);

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const { data: tokenData } = await authApi.login(email, password);
      useAuthStore.setState({ token: tokenData.access_token });
      const { data: user } = await authApi.me();
      await setAuth(tokenData.access_token, user);
      router.replace('/(tabs)/dashboard');
    } catch {
      setError('Identifiants invalides');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient colors={['#0a0e1a', '#1e1b4b', '#0a0e1a']} style={styles.container}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.flex}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          <Animated.View entering={FadeInDown.duration(800)}>
            <Text style={styles.logo}>ALCC</Text>
            <Text style={styles.tagline}>Autonomous Logistics Command</Text>
          </Animated.View>

          <Animated.View entering={FadeInUp.delay(200).duration(800)} style={styles.showroom}>
            <ShowroomCanvas variant="executive" height={240} />
          </Animated.View>

          <Animated.View entering={FadeInUp.delay(400).duration(600)} style={styles.form}>
            <TextInput
              style={styles.input}
              placeholder="Email"
              placeholderTextColor={colors.muted}
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
            />
            <TextInput
              style={styles.input}
              placeholder="Mot de passe"
              placeholderTextColor={colors.muted}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />
            {error ? <Text style={styles.error}>{error}</Text> : null}
            <TouchableOpacity style={styles.btn} onPress={handleLogin} disabled={loading}>
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.btnText}>Accéder au centre de commande</Text>
              )}
            </TouchableOpacity>
          </Animated.View>

          <Animated.View entering={FadeInUp.delay(600)} style={styles.demos}>
            <Text style={styles.demoTitle}>Comptes démo</Text>
            {DEMO_ACCOUNTS.map((acc) => (
              <TouchableOpacity
                key={acc.email}
                style={styles.demoBtn}
                onPress={() => { setEmail(acc.email); setPassword(acc.password); }}
              >
                <Text style={styles.demoRole}>{acc.role}</Text>
                <Text style={styles.demoEmail}>{acc.email}</Text>
              </TouchableOpacity>
            ))}
          </Animated.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  flex: { flex: 1 },
  scroll: { flexGrow: 1, padding: 24, paddingTop: 60 },
  logo: { fontSize: 42, fontWeight: '800', color: colors.text, letterSpacing: 6 },
  tagline: { fontSize: 13, color: colors.muted, marginTop: 4, letterSpacing: 1 },
  showroom: { marginVertical: 24 },
  form: { gap: 12 },
  input: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    color: colors.text,
    borderWidth: 1,
    borderColor: colors.border,
    fontSize: 15,
  },
  error: { color: colors.danger, fontSize: 13 },
  btn: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 4,
  },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  demos: { marginTop: 28, gap: 8 },
  demoTitle: { color: colors.muted, fontSize: 11, textTransform: 'uppercase', letterSpacing: 1 },
  demoBtn: {
    backgroundColor: colors.surface,
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  demoRole: { color: colors.primary, fontWeight: '600', fontSize: 13 },
  demoEmail: { color: colors.muted, fontSize: 11, marginTop: 2 },
});
