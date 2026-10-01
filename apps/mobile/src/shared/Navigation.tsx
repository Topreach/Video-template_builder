import { Pressable, StyleSheet, Text, View } from 'react-native';
import { ScreenName } from './sampleData';
import { palette } from './theme';

type HeaderProps = { showBack: boolean; onBack: () => void; onProfile: () => void };
export function AppHeader({ showBack, onBack, onProfile }: HeaderProps) {
  return (
    <View style={styles.header}>
      {showBack ? <Pressable onPress={onBack} accessibilityRole="button" accessibilityLabel="Go back" style={styles.back}><Text style={styles.backText}>‹</Text></Pressable> : <View style={styles.backSpacer} />}
      <View style={styles.brand}><View style={styles.brandMark}><Text style={styles.brandLetter}>r</Text></View><Text style={styles.brandName}>remix<Text style={styles.period}>.</Text></Text></View>
      <Pressable onPress={onProfile} accessibilityRole="button" accessibilityLabel="Open profile" style={styles.avatar}><Text style={styles.avatarText}>A</Text></Pressable>
    </View>
  );
}

type TabBarProps = { active: string; onSelect: (name: ScreenName) => void; onCreate: () => void };
const tabs: { id: ScreenName | 'create'; label: string; icon: string }[] = [
  { id: 'discover', label: 'Discover', icon: '⌂' },
  { id: 'create', label: 'Create', icon: '+' },
  { id: 'library', label: 'My recipes', icon: '▤' },
  { id: 'profile', label: 'Profile', icon: '○' },
];
export function TabBar({ active, onSelect, onCreate }: TabBarProps) {
  return (
    <View style={styles.tabBar} accessibilityRole="tablist">
      {tabs.map((tab) => {
        const selected = active === tab.id || (tab.id === 'create' && active === 'import');
        return <Pressable key={tab.id} onPress={() => tab.id === 'create' ? onCreate() : onSelect(tab.id)} style={styles.tab} accessibilityRole="tab" accessibilityState={{ selected }}>
          <View style={[styles.tabIcon, tab.id === 'create' && styles.createIcon, selected && tab.id !== 'create' && styles.tabSelected]}><Text style={[styles.tabIconText, (selected || tab.id === 'create') && styles.tabIconTextSelected]}>{tab.icon}</Text></View>
          <Text style={[styles.tabLabel, selected && styles.tabLabelSelected]}>{tab.label}</Text>
        </Pressable>;
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  header: { height: 56, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', backgroundColor: palette.canvas },
  back: { width: 35, height: 40, justifyContent: 'center' },
  backText: { color: palette.ink, fontSize: 34, lineHeight: 38, fontWeight: '300' },
  backSpacer: { width: 35 },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  brandMark: { width: 26, height: 26, borderRadius: 9, backgroundColor: palette.accent, alignItems: 'center', justifyContent: 'center' },
  brandLetter: { color: '#FFF', fontSize: 18, fontWeight: '800', marginTop: -2 },
  brandName: { fontSize: 22, fontWeight: '800', letterSpacing: -1.2, color: palette.ink },
  period: { color: palette.accent },
  avatar: { width: 32, height: 32, borderRadius: 16, alignItems: 'center', justifyContent: 'center', backgroundColor: '#E2DEFF' },
  avatarText: { fontSize: 12, fontWeight: '700', color: '#4E42B1' },
  tabBar: { height: 67, backgroundColor: palette.surface, borderTopWidth: 1, borderTopColor: palette.line, flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center', paddingBottom: 4 },
  tab: { flex: 1, alignItems: 'center', justifyContent: 'center', minHeight: 55, gap: 1 },
  tabIcon: { minWidth: 28, height: 27, alignItems: 'center', justifyContent: 'center', borderRadius: 9 },
  tabSelected: { backgroundColor: palette.accentSoft },
  createIcon: { width: 28, height: 27, backgroundColor: palette.accent },
  tabIconText: { fontSize: 19, color: '#92919D', lineHeight: 23 },
  tabIconTextSelected: { color: palette.accent, fontWeight: '700' },
  tabLabel: { color: '#8D8B97', fontSize: 9, fontWeight: '600' },
  tabLabelSelected: { color: palette.accent },
});
