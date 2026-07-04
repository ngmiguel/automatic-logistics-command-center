import { useEffect } from 'react';
import { Redirect } from 'expo-router';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useAuthStore } from '@/store/authStore';
import { colors } from '@/theme/colors';

export default function Index() {
  const { token, hydrated } = useAuthStore();

  if (!hydrated) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return token ? <Redirect href="/(tabs)/dashboard" /> : <Redirect href="/login" />;
}

const styles = StyleSheet.create({
  loader: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.bg },
});
