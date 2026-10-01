import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Body, Eyebrow, Page, PrimaryButton, StepLabel, Title, VideoPlaceholder } from '../../shared/Components';
import { sampleSections, SectionDecision, timecode } from '../../shared/sampleData';
import { palette } from '../../shared/theme';
import { ImportedVideo } from '../import/types';
import { SelectedVideoPreview } from '../import/SelectedVideoPreview';

type Props = {
  decisions: Record<string, SectionDecision>;
  onDecision: (id: string, decision: SectionDecision) => void;
  includedCount: number;
  runtime: number;
  onNext: () => void;
  sourceVideo: ImportedVideo | null;
};
export function ReviewScreen({ decisions, onDecision, includedCount, runtime, onNext, sourceVideo }: Props) {
  return <Page footer={<View style={styles.footer}><PrimaryButton title="Review replacement ideas" onPress={onNext} /><Text style={styles.footnote}>{includedCount} moments included · {runtime} sec preview</Text></View>}>
    <StepLabel number="02">YOUR REMIX MAP</StepLabel><Title>Shape the story.</Title><Body>Review each moment and choose what to change, keep, or leave out.</Body>
    {sourceVideo ? <><Text style={styles.videoLabel}>YOUR SELECTED VIDEO · {sourceVideo.fileName}</Text><SelectedVideoPreview uri={sourceVideo.uri} onDuration={() => {}} /></> : <VideoPlaceholder label="REFERENCE PREVIEW · EXAMPLE" caption="Wait… what?" height={230} />}
    <View style={styles.analysisNote}><Text style={styles.analysisMark}>i</Text><Text style={styles.analysisText}>The cards below are sample section data. Automatic scene detection and suggested boundaries are not connected yet.</Text></View>
    <View style={styles.mapHead}><View><Eyebrow>4 MOMENTS</Eyebrow><Text style={styles.mapTitle}>{runtime} seconds included</Text></View><Pressable onPress={() => {}}><Text style={styles.fineTune}>Fine-tune timing</Text></Pressable></View>
    <View style={styles.timeline} accessibilityLabel="Sample section timeline">{sampleSections.map((section) => <View key={section.id} style={[styles.segment, { flex: section.duration, backgroundColor: decisions[section.id] === 'exclude' ? '#D8D7DE' : section.color }]} />)}</View>
    <View style={styles.sectionList}>{sampleSections.map((section, index) => {
      const selected = decisions[section.id];
      return <View key={section.id} style={[styles.card, selected === 'exclude' && styles.cardExcluded]}>
        <View style={[styles.thumb, { backgroundColor: section.color }]}><Text style={styles.thumbIndex}>{String(index + 1).padStart(2, '0')}</Text><View style={styles.thumbPerson} /></View>
        <View style={styles.cardBody}>
          <View style={styles.cardTitleRow}><Text style={styles.cardTitle}>{section.label}</Text><Text style={styles.time}>{timecode(section.start)}–{timecode(section.end)}</Text></View>
          <Text style={styles.description}>{section.description}</Text>
          <Text style={[styles.certainty, section.certainty === 'check' && styles.uncertain]}>{section.certainty === 'clear' ? '◉  Boundary looks clear' : '◌  App suggestion · review it'}</Text>
          <View style={styles.decisions}>{(['edit', 'keep', 'exclude'] as const).map((decision) => <Pressable key={decision} onPress={() => onDecision(section.id, decision)} accessibilityRole="button" accessibilityState={{ selected: selected === decision }} style={[styles.decision, selected === decision && styles.decisionSelected, selected === decision && decision === 'exclude' && styles.excludeSelected]}><Text style={[styles.decisionText, selected === decision && styles.decisionTextSelected]}>{decision[0].toUpperCase() + decision.slice(1)}</Text></Pressable>)}</View>
        </View>
      </View>;
    })}</View>
    <Pressable style={styles.addSection} onPress={() => {}}><Text style={styles.addText}>＋  Add or split a moment</Text></Pressable>
    <View style={styles.note}><Text style={styles.noteIcon}>✓</Text><View><Text style={styles.noteTitle}>Your choice wins</Text><Text style={styles.noteBody}>Suggestions are never applied automatically.</Text></View></View>
  </Page>;
}

const styles = StyleSheet.create({
  mapHead: { flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between', marginTop: 5, marginBottom: 9 },
  mapTitle: { fontSize: 11, fontWeight: '700', color: palette.ink, marginTop: 3 },
  fineTune: { color: palette.accent, fontWeight: '700', fontSize: 9, paddingVertical: 5 },
  timeline: { height: 5, flexDirection: 'row', gap: 3, marginBottom: 12 },
  segment: { borderRadius: 4 },
  sectionList: { gap: 8 },
  card: { flexDirection: 'row', gap: 9, backgroundColor: '#FFF', borderWidth: 1, borderColor: '#ECEBF1', borderRadius: 13, padding: 8 },
  cardExcluded: { opacity: .55, backgroundColor: '#F3F3F5' },
  thumb: { width: 53, minHeight: 94, borderRadius: 9, justifyContent: 'flex-end', alignItems: 'center', overflow: 'hidden' },
  thumbIndex: { alignSelf: 'flex-start', position: 'absolute', top: 5, left: 5, color: '#FFF', backgroundColor: '#201D3859', borderRadius: 4, overflow: 'hidden', paddingHorizontal: 4, paddingVertical: 2, fontSize: 7, fontWeight: '700' },
  thumbPerson: { width: 38, height: 66, borderTopLeftRadius: 22, borderTopRightRadius: 22, backgroundColor: '#FFFFFF4D' },
  cardBody: { flex: 1, minWidth: 0 },
  cardTitleRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 4 },
  cardTitle: { color: palette.ink, fontSize: 10, fontWeight: '700', flexShrink: 1 },
  time: { color: '#92909D', fontSize: 8 },
  description: { color: '#797783', fontSize: 8, lineHeight: 12, marginVertical: 4 },
  certainty: { color: palette.green, fontSize: 7, marginBottom: 6 },
  uncertain: { color: palette.amber },
  decisions: { flexDirection: 'row', gap: 4 },
  decision: { backgroundColor: '#FAFAFC', borderWidth: 1, borderColor: '#E9E8ED', borderRadius: 6, paddingVertical: 5, paddingHorizontal: 8 },
  decisionSelected: { backgroundColor: palette.accentSoft, borderColor: '#DCD7FF' },
  excludeSelected: { backgroundColor: palette.coralSoft, borderColor: '#FFE0D8' },
  decisionText: { color: '#757380', fontSize: 8, fontWeight: '600' },
  decisionTextSelected: { color: '#5548BE' },
  addSection: { marginTop: 10, height: 40, borderRadius: 10, borderWidth: 1, borderColor: '#DAD7EB', borderStyle: 'dashed', justifyContent: 'center', alignItems: 'center' },
  addText: { color: palette.accent, fontSize: 9, fontWeight: '700' },
  note: { marginTop: 10, flexDirection: 'row', gap: 8, borderRadius: 11, backgroundColor: '#F0EFF8', padding: 10 },
  noteIcon: { color: palette.green, fontWeight: '800', fontSize: 12 },
  noteTitle: { color: '#353340', fontSize: 9, fontWeight: '700' },
  noteBody: { color: '#777582', fontSize: 8, marginTop: 3 },
  footer: { padding: 12, paddingHorizontal: 20, backgroundColor: '#FFF', borderTopWidth: 1, borderTopColor: palette.line },
  footnote: { color: '#888692', fontSize: 9, textAlign: 'center', marginTop: 7 },
  videoLabel: { marginTop: 11, fontSize: 7, letterSpacing: .8 },
  analysisNote: { flexDirection: 'row', gap: 7, backgroundColor: '#F0EFF8', borderRadius: 9, padding: 9, marginTop: 10, marginBottom: 10 },
  analysisMark: { width: 15, height: 15, borderRadius: 8, color: palette.accent, backgroundColor: '#E1DDFB', textAlign: 'center', textAlignVertical: 'center', fontSize: 9, fontWeight: '800' },
  analysisText: { flex: 1, color: '#72707E', fontSize: 8, lineHeight: 12 },
});
