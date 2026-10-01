import { Alert, Pressable, StyleSheet, Text, View } from 'react-native';
import { Body, Eyebrow, Page, PrimaryButton, StepLabel, Title, VideoPlaceholder } from '../../shared/Components';
import { SampleSection } from '../../shared/sampleData';
import { SectionDecision } from '../../shared/sampleData';
import { palette } from '../../shared/theme';

type Props = {
  profile: string;
  previewMode: 'template' | 'reference';
  includedSections: SampleSection[];
  decisions: Record<string, SectionDecision>;
  runtime: number;
  onProfileChange: (profile: string) => void;
  onPreviewModeChange: (mode: 'template' | 'reference') => void;
  onSave: () => void;
};
export function TemplatePreviewScreen({ profile, previewMode, includedSections, decisions, runtime, onProfileChange, onPreviewModeChange, onSave }: Props) {
  const selectProfile = () => Alert.alert('Output preview', 'Choose a framing guide', [
    ...['Vertical social · 9:16', 'TikTok guide · 9:16', 'Reels guide · 9:16', 'Shorts guide · 9:16'].map((value) => ({ text: value, onPress: () => onProfileChange(value) })),
    { text: 'Cancel', style: 'cancel' },
  ]);
  return <Page footer={<View style={styles.footer}><PrimaryButton title="Save my template" onPress={onSave} /><Text style={styles.footnote}>Keep it private · edit it whenever you want</Text></View>}>
    <StepLabel number="04">TEMPLATE PREVIEW</StepLabel><Title>Here’s your recipe.</Title><Body>A reusable structure, ready for a fresh take.</Body>
    <VideoPlaceholder label={previewMode === 'template' ? 'YOUR TEMPLATE' : 'REFERENCE · SAMPLE ONLY'} caption={previewMode === 'template' ? 'Your moment goes here' : 'Wait… what?'} height={250} />
    <View style={styles.modes}><ModeButton active={previewMode === 'template'} label="Template structure" onPress={() => onPreviewModeChange('template')} /><ModeButton active={previewMode === 'reference'} label="Reference" onPress={() => onPreviewModeChange('reference')} /></View>
    <View style={styles.stats}><Stat label="RUNTIME" value={`${runtime} sec`} /><Stat label="REPLACEABLE MOMENTS" value={`${includedSections.length} sections`} /><Stat label="FORMAT" value="Vertical 9:16" /></View>
    <View style={styles.included}><View style={styles.includedHead}><Text style={styles.includedTitle}>In this template</Text><Text style={styles.includedCount}>{includedSections.length} moments</Text></View>{includedSections.map((section) => <View key={section.id} style={styles.row}><Text style={styles.check}>✓</Text><Text style={styles.rowLabel}>{section.label}</Text><Text style={styles.rowMeta}>{decisions[section.id] === 'keep' ? 'Kept as-is' : 'Replaceable'}</Text></View>)}</View>
    <Pressable onPress={selectProfile} style={styles.profile}><View><Eyebrow>PREVIEW FOR</Eyebrow><Text style={styles.profileText}>{profile}</Text></View><Text style={styles.chevron}>⌄</Text></Pressable>
    <View style={styles.safeArea}><View style={styles.safePhone}><Text style={styles.safeTop}>Creator · audio</Text><View style={styles.safeFrame}><Text style={styles.safeCopy}>Keep text{ '\n' }inside this area</Text></View><Text style={styles.safeBottom}>♡　◉　➤　Caption…</Text></View><Text style={styles.safeNote}>Interface overlays are guidance.{ '\n' }Check in the destination app.</Text></View>
    <View style={styles.rights}><Text style={styles.rightsIcon}>◇</Text><Text style={styles.rightsText}>Private recipe. Only your new video will be exported.</Text></View>
  </Page>;
}

function ModeButton({ active, label, onPress }: { active: boolean; label: string; onPress: () => void }) {
  return <Pressable onPress={onPress} style={[styles.mode, active && styles.modeActive]}><Text style={[styles.modeText, active && styles.modeTextActive]}>{label}</Text></Pressable>;
}
function Stat({ label, value }: { label: string; value: string }) {
  return <View style={styles.stat}><Text style={styles.statLabel}>{label}</Text><Text style={styles.statValue}>{value}</Text></View>;
}

const styles = StyleSheet.create({
  modes: { flexDirection: 'row', backgroundColor: '#ECEBF0', borderRadius: 9, padding: 3, marginTop: 1 },
  mode: { flex: 1, alignItems: 'center', paddingVertical: 8, borderRadius: 7 },
  modeActive: { backgroundColor: '#FFF' },
  modeText: { color: '#85838F', fontSize: 9, fontWeight: '600' },
  modeTextActive: { color: '#494196' },
  stats: { flexDirection: 'row', paddingVertical: 13, borderBottomWidth: 1, borderColor: palette.line },
  stat: { flex: 1, gap: 5 },
  statLabel: { fontSize: 7, fontWeight: '700', color: '#9694A0', letterSpacing: .6 },
  statValue: { color: palette.ink, fontSize: 9, fontWeight: '700' },
  included: { marginVertical: 13, borderWidth: 1, borderColor: palette.line, borderRadius: 12, backgroundColor: '#FFF', overflow: 'hidden' },
  includedHead: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 12, paddingVertical: 10 },
  includedTitle: { color: palette.ink, fontSize: 10, fontWeight: '700' },
  includedCount: { color: '#898793', fontSize: 8 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 12, paddingVertical: 8, borderTopWidth: 1, borderColor: '#F1F0F4' },
  check: { color: palette.green, fontSize: 10, fontWeight: '800' },
  rowLabel: { color: '#4C4A56', fontSize: 9 },
  rowMeta: { color: '#898793', fontSize: 8, marginLeft: 'auto' },
  profile: { borderWidth: 1, borderColor: palette.line, borderRadius: 10, backgroundColor: '#FFF', padding: 11, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  profileText: { color: palette.ink, fontSize: 10, fontWeight: '700', marginTop: 4 },
  chevron: { color: '#777582', fontSize: 18 },
  safeArea: { marginTop: 10, backgroundColor: '#F0EFF5', borderRadius: 11, padding: 10, flexDirection: 'row', alignItems: 'center', gap: 11 },
  safePhone: { width: 68, height: 103, borderRadius: 8, backgroundColor: '#B29BAA', overflow: 'hidden', alignItems: 'center', justifyContent: 'center' },
  safeTop: { position: 'absolute', top: 0, width: '100%', paddingVertical: 4, textAlign: 'center', color: '#FFF', backgroundColor: '#28243B55', fontSize: 5 },
  safeFrame: { borderWidth: 1, borderColor: '#FFFFFFB0', borderStyle: 'dashed', width: 48, height: 60, alignItems: 'center', justifyContent: 'center' },
  safeCopy: { color: '#FFF', fontSize: 6, textAlign: 'center', fontWeight: '700' },
  safeBottom: { position: 'absolute', bottom: 0, width: '100%', paddingVertical: 4, textAlign: 'center', color: '#FFF', backgroundColor: '#28243B55', fontSize: 5 },
  safeNote: { color: '#797783', fontSize: 8, lineHeight: 13 },
  rights: { flexDirection: 'row', gap: 7, marginTop: 13, alignItems: 'center' },
  rightsIcon: { color: palette.accent, fontSize: 12 },
  rightsText: { color: '#85838F', fontSize: 8 },
  footer: { padding: 12, paddingHorizontal: 20, backgroundColor: '#FFF', borderTopWidth: 1, borderTopColor: palette.line },
  footnote: { textAlign: 'center', color: '#888692', fontSize: 9, marginTop: 7 },
});
