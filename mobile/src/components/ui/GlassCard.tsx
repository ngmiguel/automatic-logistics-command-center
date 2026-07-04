import { ReactNode } from 'react';
import { View, StyleSheet, ViewStyle, StyleProp } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { FadeIn } from 'react-native-reanimated';
import { colors } from '@/theme/colors';

interface Props {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  glow?: boolean;
}

export function GlassCard({ children, style, glow }: Props) {
  return (
    <Animated.View entering={FadeIn.duration(400)} style={[styles.outer, glow && styles.glow, style]}>
      <LinearGradient
        colors={['rgba(30,41,59,0.95)', 'rgba(15,23,42,0.9)']}
        style={styles.gradient}
      >
        {children}
      </LinearGradient>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  outer: {
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: colors.border,
  },
  glow: {
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  gradient: { padding: 16 },
});
