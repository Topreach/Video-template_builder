import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { Body, Eyebrow, Page, PrimaryButton, StepLabel, Title } from '../../shared/Components';
import { SectionDecision } from '../../shared/sampleData';
import { EditableSectionSpan, sectionDuration } from './types';
import { palette } from '../../shared/theme';
import { ImportedVideo } from '../import/types';
import { ReviewVideoPlayer } from './ReviewVideoPlayer';

type Props = {
  sections: EditableSectionSpan[];
  decisions: Record<string, SectionDecision>;
  onDecision: (id: string, decision: SectionDecision) => void;
  onSplitAt: (seconds: number) => boolean;
  includedCount: number;
  runtime: number;
  onNext: () => void;
  sourceVideo: ImportedVideo | null;
};

export function ReviewScreen({ sections, decisions, onDecision, onSplitAt, includedCount, runtime, onNext, sourceVideo }: Props) {
  const [splitAt, setSplitAt] = useState('');
  const [splitMessage, setSplitMessage] = useState('');
  const [playhead, setPlayhead] = useState(0);
  const pendingCount = sections.filter((section) => !decisions[section.id]).length;
  const sourceDuration = Math.max(sourceVideo?.durationSeconds ?? 0, ...sections.map((section) => section.endSeconds));
  const canContinue = sections.length > 0 && pendingCount === 0 && includedCount > 0;

  const addSplit = () => {
    const seconds = Number(splitAt.trim().replace(',', '.'));
    if (!Number.isFinite(seconds) || !onSplitAt(seconds)) {
      setSplitMessage('Enter a time inside one of the moments.');
      return;
    }
    setSplitAt('');
    setSplitMessage('Moment split. Choose an action for each new part.');
  };

  const splitAtPlayhead = () => {
    if (!onSplitAt(playhead)) {
      setSplitMessage('Move the playhead inside a moment before splitting.');
      return;
    }
    setSplitAt('');
    setSplitMessage(`Moment split at ${playhead.toFixed(1)} seconds. Choose an action for each new part.`);
  };

  return <Page footer={<View style={styles.footer}>
    <PrimaryButton title={pendingCount ? `Choose an action for ${pendingCount} moment${pendingCount === 1 ? '' : 's'}` : 'Review replacement ideas'} disabled={!canContinue} onPress={onNext} />
    <Text style={styles.footnote}>{includedCount} moments included | {runtime.toFixed(1)} sec</Text>
  </View>}>
    <StepLabel number="02">YOUR REMIX MAP</StepLabel>
    <Title>Shape the story.</Title>
    <Body>Review each moment and choose what to change, keep, or leave out.</Body>
    {sourceVideo && <>
      <Text style={styles.videoLabel}>REVIEW THE VIDEO | {sourceVideo.fileName}</Text>
      <ReviewVideoPlayer uri={sourceVideo.uri} durationSeconds={sourceDuration} onTimeChange={setPlayhead} />
    </>}
    <View style={styles.analysisNote}>
      <Text style={styles.analysisMark}>i</Text>
      <Text style={styles.analysisText}>Automatic scene analysis is not connected yet. Your clip starts as one manual moment; split it at the times you choose.</Text>
    </View>
    <View style={styles.mapHead}>
      <View>
        <Eyebrow>{sections.length} {sections.length === 1 ? 'MOMENT' : 'MOMENTS'}</Eyebrow>
        <Text style={styles.mapTitle}>{runtime.toFixed(1)} seconds included</Text>
      </View>
    </View>
    <View style={styles.timeline} accessibilityLabel="Your manually divided video timeline">
      {sections.map((section, index) => <View key={section.id} style={[styles.segment, { flex: Math.max(sectionDuration(section), 0.1), backgroundColor: decisions[section.id] === 'exclude' ? '#D8D7DE' : sectionColors[index % sectionColors.length] }]} />)}
    </View>
    <View style={styles.sectionList}>
      {sections.map((section, index) => {
        const selected = decisions[section.id];
        const color = sectionColors[index % sectionColors.length];
        const start = section.startSeconds;
        const end = section.endSeconds;
        return <View key={section.id} style={[styles.card, selected === 'exclude' && styles.cardExcluded]}>
          <View style={[styles.thumb, { backgroundColor: color }]}>
            <Text style={styles.thumbIndex}>{String(index + 1).padStart(2, '0')}</Text>
            <Text style={styles.thumbTime}>{formatTimecode(start)}</Text>
          </View>
          <View style={styles.cardBody}>
            <View style={styles.cardTitleRow}>
              <Text style={styles.cardTitle}>Moment {index + 1}</Text>
              <Text style={styles.time}>{formatTimecode(start)}-{formatTimecode(end)}</Text>
            </View>
            <Text style={styles.description}>Set by you. Confirm whether to edit, keep, or exclude this moment.</Text>
            <Text style={[styles.certainty, styles.uncertain]}>Manual boundary | confirm timing</Text>
            <View style={styles.decisions}>
              {(['edit', 'keep', 'exclude'] as const).map((decision) => <Pressable
                key={decision}
                onPress={() => onDecision(section.id, decision)}
                accessibilityRole="button"
                accessibilityState={{ selected: selected === decision }}
                style={[styles.decision, selected === decision && styles.decisionSelected, selected === decision && decision === 'exclude' && styles.excludeSelected]}>
                <Text style={[styles.decisionText, selected === decision && styles.decisionTextSelected]}>{decision[0].toUpperCase() + decision.slice(1)}</Text>
              </Pressable>)}
            </View>
          </View>
        </View>;
      })}
    </View>
    <View style={styles.splitBox}>
      <Text style={styles.splitLabel}>SPLIT THIS MOMENT</Text>
      <Pressable style={styles.playheadSplit} onPress={splitAtPlayhead} accessibilityRole="button">
        <Text style={styles.playheadSplitText}>Split at playhead · {formatTimecode(playhead)}</Text>
      </Pressable>
      <Text style={styles.exactLabel}>Or enter an exact time in seconds</Text>
      <View style={styles.splitRow}>
        <TextInput value={splitAt} onChangeText={setSplitAt} keyboardType="decimal-pad" placeholder="For example, 4.5" accessibilityLabel="Time in seconds to split the video" style={styles.splitInput} />
        <Pressable style={styles.addSection} onPress={addSplit} accessibilityRole="button"><Text style={styles.addText}>Split moment</Text></Pressable>
      </View>
      <Text style={styles.splitMessage}>{splitMessage || 'The split must fall inside an existing moment.'}</Text>
    </View>
    <View style={styles.note}>
      <Text style={styles.noteIcon}>i</Text>
      <View><Text style={styles.noteTitle}>Your choice wins</Text><Text style={styles.noteBody}>Nothing is kept or excluded until you decide. This screen does not claim to detect scenes.</Text></View>
    </View>
  </Page>;
}

const styles = StyleSheet.create({
  mapHead: { flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between', marginTop: 5, marginBottom: 9 },
  mapTitle: { fontSize: 11, fontWeight: '700', color: palette.ink, marginTop: 3 },
  timeline: { height: 5, flexDirection: 'row', gap: 3, marginBottom: 12 },
  segment: { borderRadius: 4 },
  sectionList: { gap: 8 },
  card: { flexDirection: 'row', gap: 9, backgroundColor: '#FFF', borderWidth: 1, borderColor: '#ECEBF1', borderRadius: 13, padding: 8 },
  cardExcluded: { opacity: .55, backgroundColor: '#F3F3F5' },
  thumb: { width: 53, minHeight: 94, borderRadius: 9, justifyContent: 'flex-end', alignItems: 'center', overflow: 'hidden' },
  thumbIndex: { alignSelf: 'flex-start', position: 'absolute', top: 5, left: 5, color: '#FFF', backgroundColor: '#201D3859', borderRadius: 4, overflow: 'hidden', paddingHorizontal: 4, paddingVertical: 2, fontSize: 7, fontWeight: '700' },
  thumbTime: { color: '#FFF', fontSize: 9, fontWeight: '700', paddingBottom: 9 },
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
  splitBox: { marginTop: 12, borderRadius: 11, borderWidth: 1, borderColor: palette.line, backgroundColor: '#FFF', padding: 11 },
  splitLabel: { color: '#8A8795', fontSize: 8, letterSpacing: 1, fontWeight: '700' },
  playheadSplit: { minHeight: 40, marginTop: 8, borderRadius: 9, backgroundColor: palette.accent, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 12 },
  playheadSplitText: { color: '#FFF', fontSize: 10, fontWeight: '700' },
  exactLabel: { color: '#8A8795', fontSize: 8, marginTop: 10 },
  splitRow: { flexDirection: 'row', gap: 8, alignItems: 'center', marginTop: 8 },
  splitInput: { flex: 1, minHeight: 40, paddingHorizontal: 11, borderWidth: 1, borderColor: palette.line, borderRadius: 8, color: palette.ink, fontSize: 12 },
  addSection: { minHeight: 40, borderRadius: 9, borderWidth: 1, borderColor: '#DAD7EB', justifyContent: 'center', alignItems: 'center', paddingHorizontal: 12 },
  addText: { color: palette.accent, fontSize: 9, fontWeight: '700' },
  splitMessage: { color: '#777582', fontSize: 8, marginTop: 6 },
  note: { marginTop: 10, flexDirection: 'row', gap: 8, borderRadius: 11, backgroundColor: '#F0EFF8', padding: 10 },
  noteIcon: { color: palette.green, fontWeight: '800', fontSize: 12 },
  noteTitle: { color: '#353340', fontSize: 9, fontWeight: '700' },
  noteBody: { color: '#777582', fontSize: 8, marginTop: 3, flex: 1 },
  footer: { padding: 12, paddingHorizontal: 20, backgroundColor: '#FFF', borderTopWidth: 1, borderTopColor: palette.line },
  footnote: { color: '#888692', fontSize: 9, textAlign: 'center', marginTop: 7 },
  videoLabel: { marginTop: 11, fontSize: 7, letterSpacing: .8 },
  analysisNote: { flexDirection: 'row', gap: 7, backgroundColor: '#F0EFF8', borderRadius: 9, padding: 9, marginTop: 10, marginBottom: 10 },
  analysisMark: { width: 15, height: 15, borderRadius: 8, color: palette.accent, backgroundColor: '#E1DDFB', textAlign: 'center', textAlignVertical: 'center', fontSize: 9, fontWeight: '800' },
  analysisText: { flex: 1, color: '#72707E', fontSize: 8, lineHeight: 12 },
});

const sectionColors = ['#DFA798', '#87ADB9', '#D39C69', '#AAA8B3'];

function formatTimecode(seconds: number): string {
  return `0:${seconds.toFixed(1).padStart(4, '0')}`;
}
