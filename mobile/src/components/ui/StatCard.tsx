import { View, Text, StyleSheet } from 'react-native';
import Animated, { FadeInDown, useAnimatedStyle, withSpring, useSharedValue } from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '@/theme/colors';

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: keyof typeof Ionicons.glyphMap;
  color?: string;
  index?: number;
}

export function StatCard({ title, value, subtitle, icon, color = colors.primary, index = 0 }: Props) {
  const scale = useSharedValue(0.9);
  scale.value = withSpring(1, { damping: 12 });

  const animStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));

  return (
    <Animated.View entering={FadeInDown.delay(index * 100).springify()} style={[styles.card, animStyle]}>
      <View style={styles.row}>
        <View style={styles.textBlock}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.value}>{value}</Text>
          {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
        </View>
        <View style={[styles.iconWrap, { backgroundColor: `${color}22` }]}>
          <Ionicons name={icon} size={22} color={color} />
        </View>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    flex: 1,
    minWidth: '45%',
  },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  textBlock: { flex: 1 },
  title: { fontSize: 10, color: colors.muted, textTransform: 'uppercase', letterSpacing: 1 },
  value: { fontSize: 26, fontWeight: '700', color: colors.text, marginTop: 4 },
  subtitle: { fontSize: 11, color: colors.muted, marginTop: 2 },
  iconWrap: { padding: 8, borderRadius: 10 },
});
