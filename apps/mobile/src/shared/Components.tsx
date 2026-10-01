import { PropsWithChildren } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View, ViewStyle } from 'react-native';
import { palette, space } from './theme';

export function Page({ children, footer }: PropsWithChildren<{ footer?: React.ReactNode }>) {
  return <View style={styles.page}><ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>{children}</ScrollView>{footer}</View>;
}

export function Eyebrow({ children }: PropsWithChildren) { return <Text style={styles.eyebrow}>{children}</Text>; }
export function Title({ children }: PropsWithChildren) { return <Text style={styles.title}>{children}</Text>; }
export function Body({ children, style }: PropsWithChildren<{ style?: ViewStyle }>) { return <Text style={[styles.body, style]}>{children}</Text>; }

export function StepLabel({ number, children }: PropsWithChildren<{ number: string }>) {
  return <View style={styles.step}><Text style={styles.stepNum}>{number}</Text><Text style={styles.stepText}>{children}</Text></View>;
}

export function PrimaryButton({ title, onPress, disabled = false }: { title: string; onPress: () => void; disabled?: boolean }) {
  return <Pressable onPress={onPress} disabled={disabled} accessibilityRole="button" style={({ pressed }) => [styles.primary, disabled && styles.disabled, pressed && !disabled && styles.pressed]}><Text style={styles.primaryText}>{title}</Text><Text style={styles.arrow}>›</Text></Pressable>;
}

export function SecondaryButton({ title, onPress, outlined = false }: { title: string; onPress: () => void; outlined?: boolean }) {
  return <Pressable onPress={onPress} accessibilityRole="button" style={({ pressed }) => [styles.secondary, outlined && styles.outlined, pressed && styles.pressed]}><Text style={styles.secondaryText}>{title}</Text></Pressable>;
}

export function SectionHeading({ eyebrow, title, action, onAction }: { eyebrow: string; title: string; action?: string; onAction?: () => void }) {
  return <View style={styles.sectionHeading}><View><Eyebrow>{eyebrow}</Eyebrow><Text style={styles.sectionTitle}>{title}</Text></View>{action && <Pressable onPress={onAction}><Text style={styles.action}>{action}</Text></Pressable>}</View>;
}

export function VideoPlaceholder({ label = 'SAMPLE PREVIEW', caption = 'Your moment goes here', height = 250 }: { label?: string; caption?: string; height?: number }) {
  return <View style={[styles.video, { height }]}><View style={styles.videoGlow} /><View style={styles.videoHead}><View style={styles.liveDot} /><Text style={styles.videoLabel}>{label}</Text><Text style={styles.videoSound}>♫</Text></View><View style={styles.subject}><View style={styles.subjectHead} /><View style={styles.subjectBody} /></View><Text style={styles.videoCaption}>{caption}</Text><View style={styles.play}><Text style={styles.playText}>▶</Text></View><View style={styles.scrubber}><Text>0:04</Text><View style={styles.scrubLine}><View /></View><Text>0:13</Text></View></View>;
}

export function InfoCard({ title, children, icon = '✦' }: PropsWithChildren<{ title: string; icon?: string }>) {
  return <View style={styles.infoCard}><Text style={styles.infoIcon}>{icon}</Text><View style={{ flex: 1 }}><Text style={styles.infoTitle}>{title}</Text><Text style={styles.infoBody}>{children}</Text></View></View>;
}

export function CategoryChips({ values }: { values: string[] }) {
  return <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chips}>{values.map((value, i) => <View key={value} style={[styles.chip, i === 0 && styles.chipSelected]}><Text style={[styles.chipText, i === 0 && styles.chipTextSelected]}>{value}</Text></View>)}</ScrollView>;
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: palette.canvas },
  scroll: { paddingHorizontal: 21, paddingTop: 13, paddingBottom: 26 },
  eyebrow: { color: '#92909D', fontSize: 9, fontWeight: '700', letterSpacing: 1.5 },
  title: { color: palette.ink, fontSize: 29, lineHeight: 34, fontWeight: '800', letterSpacing: -1, marginTop: 9, marginBottom: 8 },
  body: { color: palette.muted, fontSize: 13, lineHeight: 20 },
  step: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 10 },
  stepNum: { width: 22, height: 22, textAlign: 'center', textAlignVertical: 'center', overflow: 'hidden', borderRadius: 7, backgroundColor: palette.accentSoft, color: palette.accent, fontSize: 9, fontWeight: '800', paddingTop: 5 },
  stepText: { color: '#777582', letterSpacing: 1.2, fontWeight: '700', fontSize: 9 },
  primary: { minHeight: 49, paddingHorizontal: 16, borderRadius: 13, backgroundColor: palette.accent, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', elevation: 1 },
  primaryText: { color: '#FFF', fontWeight: '700', fontSize: 13 },
  arrow: { color: '#FFF', fontSize: 22, position: 'absolute', right: 15, top: 8, fontWeight: '300' },
  disabled: { backgroundColor: '#C7C5D1', elevation: 0 },
  secondary: { minHeight: 43, paddingHorizontal: 15, borderRadius: 11, backgroundColor: palette.accentSoft, justifyContent: 'center', alignItems: 'center' },
  secondaryText: { color: '#5146B7', fontSize: 11, fontWeight: '700' },
  outlined: { backgroundColor: palette.surface, borderColor: palette.line, borderWidth: 1 },
  pressed: { opacity: .82, transform: [{ scale: .99 }] },
  sectionHeading: { marginTop: 26, marginBottom: 12, flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between' },
  sectionTitle: { marginTop: 4, fontWeight: '800', fontSize: 17, color: palette.ink, letterSpacing: -.35 },
  action: { color: palette.accent, fontSize: 10, fontWeight: '700', paddingVertical: 6 },
  video: { overflow: 'hidden', borderRadius: 16, backgroundColor: '#AD819C', position: 'relative', justifyContent: 'center', alignItems: 'center', marginVertical: 12 },
  videoGlow: { position: 'absolute', top: -20, right: -20, width: 220, height: 240, borderRadius: 130, backgroundColor: '#E5B7A5', opacity: .75 },
  videoHead: { position: 'absolute', top: 13, left: 13, right: 13, flexDirection: 'row', alignItems: 'center', gap: 6 },
  liveDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#A4F2CA' },
  videoLabel: { color: '#FFF', fontSize: 8, letterSpacing: 1, fontWeight: '800' },
  videoSound: { color: '#FFF', marginLeft: 'auto', fontSize: 14 },
  subject: { width: 130, height: '72%', alignItems: 'center', justifyContent: 'flex-end' },
  subjectHead: { width: 55, height: 55, borderRadius: 28, backgroundColor: '#F1D7C3', marginBottom: -4, zIndex: 1 },
  subjectBody: { width: 128, height: 145, borderTopLeftRadius: 65, borderTopRightRadius: 65, backgroundColor: '#976F79' },
  videoCaption: { position: 'absolute', bottom: 53, left: 15, color: '#FFF', fontSize: 18, fontWeight: '800', textShadowColor: '#3338', textShadowRadius: 8 },
  play: { position: 'absolute', top: '43%', width: 42, height: 42, borderRadius: 21, backgroundColor: '#FFFFFFDE', alignItems: 'center', justifyContent: 'center', paddingLeft: 3 },
  playText: { color: '#544C60', fontSize: 11 },
  scrubber: { position: 'absolute', bottom: 12, left: 13, right: 13, flexDirection: 'row', alignItems: 'center', gap: 8 },
  scrubLine: { flex: 1, height: 2, backgroundColor: '#FFFFFF75', borderRadius: 2 },
  chips: { gap: 7, paddingBottom: 3 },
  chip: { borderRadius: 18, borderColor: palette.line, borderWidth: 1, backgroundColor: '#FFF', paddingVertical: 8, paddingHorizontal: 12 },
  chipSelected: { backgroundColor: palette.accentSoft, borderColor: '#E2DFFF' },
  chipText: { color: '#777582', fontSize: 10, fontWeight: '600' },
  chipTextSelected: { color: '#5146B7' },
  infoCard: { flexDirection: 'row', gap: 10, borderRadius: 12, backgroundColor: '#F0EFF8', padding: 12, marginTop: space.lg },
  infoIcon: { color: palette.accent, fontSize: 15 },
  infoTitle: { color: '#33313F', fontSize: 11, fontWeight: '700', marginBottom: 2 },
  infoBody: { color: '#777582', fontSize: 10, lineHeight: 15 },
});
