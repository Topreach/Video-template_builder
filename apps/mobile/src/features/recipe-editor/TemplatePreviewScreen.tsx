import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { Body, Eyebrow, Page, PrimaryButton, StepLabel, Title } from '../../shared/Components';
import { palette } from '../../shared/theme';
import { TemplateRecipe } from '../template-library/types';

type Props = {
  title: string;
  sections: TemplateRecipe['sections'];
  sourceDurationSeconds: number;
  runtime: number;
  isSaved: boolean;
  saving: boolean;
  error: string | null;
  onTitleChange: (title: string) => void;
  onSave: () => void;
};

export function TemplatePreviewScreen({ title, sections, sourceDurationSeconds, runtime, isSaved, saving, error, onTitleChange, onSave }: Props) {
  const included = sections.filter((section) => section.decision !== 'exclude');
  const keptCount = included.filter((section) => section.decision === 'keep').length;
  const canSave = title.trim().length > 0 && included.length > 0 && !saving;

  return <Page footer={<View style={styles.footer}>
    <PrimaryButton title={saving ? 'Saving...' : isSaved ? 'Save changes' : 'Save to My Templates'} disabled={!canSave} onPress={onSave} />
    <Text style={styles.footnote}>Saved recipes contain structure and choices, not the original video.</Text>
  </View>}>
    <StepLabel number="04">TEMPLATE DETAILS</StepLabel>
    <Title>Save a reusable structure.</Title>
    <Body>Check the moments and give this private template a name.</Body>

    <View style={styles.titleBox}>
      <Eyebrow>TEMPLATE NAME</Eyebrow>
      <TextInput value={title} onChangeText={onTitleChange} maxLength={120} placeholder="My video template" accessibilityLabel="Template name" style={styles.titleInput} />
    </View>

    <View style={styles.stats}>
      <Stat label="SOURCE LENGTH" value={`${sourceDurationSeconds.toFixed(1)} sec`} />
      <Stat label="INCLUDED" value={`${included.length} moments`} />
      <Stat label="TEMPLATE LENGTH" value={`${runtime.toFixed(1)} sec`} />
    </View>

    <View style={styles.timelineCard}>
      <View style={styles.timelineHead}><Eyebrow>STRUCTURE PREVIEW</Eyebrow><Text style={styles.format}>Vertical 9:16</Text></View>
      <View style={styles.timeline} accessibilityLabel="Template section structure">
        {sections.map((section, index) => <View key={section.id} style={[styles.segment, { flex: Math.max(section.endSeconds - section.startSeconds, 0.1), backgroundColor: section.decision === 'exclude' ? '#D8D7DE' : sectionColors[index % sectionColors.length] }]} />)}
      </View>
      <Text style={styles.previewNote}>This is a timing and decision preview, not a rendered video.</Text>
    </View>

    <View style={styles.sectionCard}>
      <Text style={styles.sectionHeading}>Sections</Text>
      {sections.map((section, index) => <View key={section.id} style={[styles.sectionRow, section.decision === 'exclude' && styles.excludedRow]}>
        <View style={[styles.sectionMark, { backgroundColor: section.decision === 'exclude' ? '#D8D7DE' : sectionColors[index % sectionColors.length] }]} />
        <View style={styles.sectionCopy}>
          <Text style={styles.sectionName}>Moment {index + 1}</Text>
          <Text style={styles.sectionTime}>{formatTime(section.startSeconds)} - {formatTime(section.endSeconds)}</Text>
        </View>
        <Text style={[styles.decision, section.decision === 'exclude' && styles.excludedText]}>{section.decision === 'edit' ? 'Replaceable' : section.decision === 'keep' ? 'Kept' : 'Excluded'}</Text>
      </View>)}
    </View>

    {keptCount > 0 && <View style={styles.notice}>
      <Text style={styles.noticeTitle}>Original media is not saved</Text>
      <Text style={styles.noticeText}>{keptCount} kept {keptCount === 1 ? 'moment points' : 'moments point'} to the imported video. Before saving, choose whether to turn these into replaceable slots. This keeps the recipe independent of the source file.</Text>
    </View>}
    {error && <View style={styles.error}><Text style={styles.errorText}>{error}</Text></View>}
  </Page>;
}

function Stat({ label, value }: { label: string; value: string }) {
  return <View style={styles.stat}><Text style={styles.statLabel}>{label}</Text><Text style={styles.statValue}>{value}</Text></View>;
}

function formatTime(seconds: number): string {
  return `0:${seconds.toFixed(1).padStart(4, '0')}`;
}

const sectionColors = ['#DFA798', '#87ADB9', '#D39C69', '#AAA8B3'];

const styles = StyleSheet.create({
  titleBox: { backgroundColor: '#FFF', borderWidth: 1, borderColor: palette.line, borderRadius: 12, padding: 12, marginTop: 18 },
  titleInput: { color: palette.ink, fontSize: 14, fontWeight: '700', paddingVertical: 8 },
  stats: { flexDirection: 'row', paddingVertical: 14, borderBottomWidth: 1, borderColor: palette.line },
  stat: { flex: 1, gap: 5 },
  statLabel: { fontSize: 7, fontWeight: '700', color: '#9694A0', letterSpacing: .6 },
  statValue: { color: palette.ink, fontSize: 9, fontWeight: '700' },
  timelineCard: { backgroundColor: '#FFF', borderWidth: 1, borderColor: palette.line, borderRadius: 12, padding: 12, marginTop: 13 },
  timelineHead: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  format: { color: '#777582', fontSize: 8 },
  timeline: { height: 12, flexDirection: 'row', gap: 3, marginVertical: 12 },
  segment: { borderRadius: 4 },
  previewNote: { color: '#777582', fontSize: 8, lineHeight: 12 },
  sectionCard: { backgroundColor: '#FFF', borderWidth: 1, borderColor: palette.line, borderRadius: 12, marginTop: 12, overflow: 'hidden' },
  sectionHeading: { color: palette.ink, fontSize: 10, fontWeight: '700', padding: 12 },
  sectionRow: { flexDirection: 'row', alignItems: 'center', gap: 9, padding: 10, borderTopWidth: 1, borderColor: '#F1F0F4' },
  excludedRow: { opacity: .65 },
  sectionMark: { width: 8, height: 33, borderRadius: 4 },
  sectionCopy: { flex: 1 },
  sectionName: { color: palette.ink, fontSize: 9, fontWeight: '700' },
  sectionTime: { color: '#898793', fontSize: 8, marginTop: 4 },
  decision: { color: '#5B54A4', fontSize: 8, fontWeight: '700' },
  excludedText: { color: '#777582' },
  notice: { backgroundColor: '#F0EFF8', padding: 11, borderRadius: 10, marginTop: 11 },
  noticeTitle: { color: palette.ink, fontSize: 9, fontWeight: '700' },
  noticeText: { color: '#777582', fontSize: 8, lineHeight: 12, marginTop: 4 },
  error: { padding: 10, marginTop: 10, borderRadius: 9, backgroundColor: palette.coralSoft },
  errorText: { color: '#8A514A', fontSize: 9, lineHeight: 14 },
  footer: { padding: 12, paddingHorizontal: 20, backgroundColor: '#FFF', borderTopWidth: 1, borderTopColor: palette.line },
  footnote: { color: '#888692', fontSize: 8, textAlign: 'center', marginTop: 7 },
});
