import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Alert } from 'react-native';
import { Body, InfoCard, Page, PrimaryButton, StepLabel, Title, VideoPlaceholder } from '../../shared/Components';
import { palette } from '../../shared/theme';

type Props = { ideaSelected: boolean; onSelectIdea: () => void; onPreview: () => void };
export function AdaptScreen({ ideaSelected, onSelectIdea, onPreview }: Props) {
  const [showTools, setShowTools] = useState(false);
  const [muted, setMuted] = useState(false);
  return <Page footer={<View style={styles.footer}><PrimaryButton title="Preview template" onPress={onPreview} /><Text style={styles.footnote}>You can edit every choice later.</Text></View>}>
    <StepLabel number="03">MAKE IT YOURS</StepLabel><Title>Keep the rhythm.{ '\n' }Change the scene.</Title><Body>Ideas for <Text style={styles.bold}>The reveal</Text>. Pick one, change it, or skip for now.</Body>
    <View style={styles.ideaCard}><View style={styles.scene}><Text style={styles.sceneTag}>SUGGESTED SHOT</Text><View style={styles.scenePerson}><View style={styles.sceneHead} /><View style={styles.sceneBody} /></View><Text style={styles.sceneText}>YOUR MOMENT{ '\n' }GOES HERE</Text></View><View style={styles.ideaBody}><Text style={styles.ideaLabel}>IDEA 01 · YOUR FOOTAGE</Text><Text style={styles.ideaTitle}>Show your product{ '\n' }in the reveal.</Text><Text style={styles.ideaWhy}>It keeps the visual payoff, but makes this moment yours.</Text><Pressable onPress={onSelectIdea} style={[styles.useIdea, ideaSelected && styles.ideaChosen]}><Text style={[styles.useIdeaText, ideaSelected && styles.ideaChosenText]}>{ideaSelected ? 'Idea selected ✓' : 'Use this idea  →'}</Text></Pressable></View></View>
    <View style={styles.sourceChoices}><SourceChoice icon="▣" title="My video or photo" detail="Pick something you own" onPress={() => Alert.alert('Media picker comes next', 'The app will connect to your device library in the media-import implementation slice.')} /><SourceChoice icon="◎" title="Licensed media" detail="See usage rights first" onPress={() => Alert.alert('Licensed library is a later feature', 'This option depends on asset-provider and licensing research.')} /></View>
    <Pressable style={styles.editRow} onPress={() => setShowTools((value) => !value)}><View><Text style={styles.editTitle}>Words & sound</Text><Text style={styles.editDetail}>Change the caption, audio, or both.</Text></View><Text style={styles.editAction}>{showTools ? 'Done' : 'Edit'}  ›</Text></Pressable>
    {showTools && <View style={styles.tools}><Text style={styles.inputLabel}>NEW CAPTION</Text><View style={styles.input}><Text style={styles.inputText}>Plot twist: it’s mine.</Text></View><View style={styles.audioRow}><Text style={styles.audioLabel}>Original sound</Text><Pressable onPress={() => setMuted((value) => !value)} style={[styles.switch, muted && styles.switchOn]}><View style={[styles.switchKnob, muted && styles.switchKnobOn]} /></Pressable></View><Pressable onPress={() => Alert.alert('Sound library comes later', 'A selected audio asset will show its source and usage rights here.')}><Text style={styles.link}>Choose replacement sound  →</Text></Pressable></View>}
    <InfoCard title="A rights reminder" icon="ⓘ">Changing sound or text does not automatically clear rights to the rest of a video.</InfoCard>
  </Page>;
}

function SourceChoice({ icon, title, detail, onPress }: { icon: string; title: string; detail: string; onPress: () => void }) {
  return <Pressable onPress={onPress} style={styles.source}><Text style={styles.sourceIcon}>{icon}</Text><Text style={styles.sourceTitle}>{title}</Text><Text style={styles.sourceDetail}>{detail}</Text><Text style={styles.sourceArrow}>↗</Text></Pressable>;
}

const styles = StyleSheet.create({
  bold: { color: palette.ink, fontWeight: '700' },
  ideaCard: { marginTop: 17, backgroundColor: '#FFF', borderWidth: 1, borderColor: palette.line, borderRadius: 16, overflow: 'hidden' },
  scene: { height: 185, backgroundColor: '#9C95AD', justifyContent: 'flex-end', padding: 14, overflow: 'hidden' },
  sceneTag: { position: 'absolute', top: 11, left: 12, zIndex: 3, color: '#FFF', backgroundColor: '#24222A66', overflow: 'hidden', borderRadius: 5, paddingHorizontal: 7, paddingVertical: 5, fontSize: 7, letterSpacing: 1, fontWeight: '700' },
  scenePerson: { position: 'absolute', width: 100, height: 160, left: '38%', bottom: 0, alignItems: 'center', justifyContent: 'flex-end' },
  sceneHead: { width: 52, height: 52, borderRadius: 26, backgroundColor: '#F0D6C1', zIndex: 1, marginBottom: -3 },
  sceneBody: { width: 100, height: 105, borderTopLeftRadius: 50, borderTopRightRadius: 50, backgroundColor: '#77667D' },
  sceneText: { zIndex: 2, color: '#FFF', fontSize: 11, lineHeight: 14, fontWeight: '800', letterSpacing: 1, textShadowColor: '#332C3C', textShadowRadius: 5 },
  ideaBody: { padding: 14 },
  ideaLabel: { color: '#6B5FD0', fontSize: 8, letterSpacing: 1, fontWeight: '700' },
  ideaTitle: { color: palette.ink, fontSize: 19, lineHeight: 23, fontWeight: '800', marginTop: 7 },
  ideaWhy: { color: palette.muted, fontSize: 10, lineHeight: 15, marginTop: 6 },
  useIdea: { alignSelf: 'flex-start', marginTop: 10, backgroundColor: palette.accent, borderRadius: 9, paddingVertical: 9, paddingHorizontal: 12 },
  useIdeaText: { color: '#FFF', fontWeight: '700', fontSize: 10 },
  ideaChosen: { backgroundColor: palette.greenSoft },
  ideaChosenText: { color: palette.green },
  sourceChoices: { flexDirection: 'row', gap: 8, marginTop: 12 },
  source: { flex: 1, borderRadius: 11, padding: 10, backgroundColor: '#FFF', borderColor: palette.line, borderWidth: 1 },
  sourceIcon: { color: palette.accent, fontSize: 14, marginBottom: 5 },
  sourceTitle: { color: palette.ink, fontSize: 9, fontWeight: '700' },
  sourceDetail: { color: '#85838F', fontSize: 8, marginTop: 4 },
  sourceArrow: { position: 'absolute', top: 8, right: 9, color: '#9B99A5', fontSize: 10 },
  editRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 13, borderTopWidth: 1, borderBottomWidth: 1, borderColor: palette.line, paddingVertical: 12 },
  editTitle: { fontSize: 11, fontWeight: '700', color: palette.ink },
  editDetail: { color: '#85838F', fontSize: 9, marginTop: 3 },
  editAction: { color: palette.accent, fontSize: 10, fontWeight: '700' },
  tools: { borderRadius: 11, backgroundColor: '#F0EFF5', padding: 12, marginTop: 9 },
  inputLabel: { fontSize: 8, color: '#8A8795', letterSpacing: 1, fontWeight: '700' },
  input: { backgroundColor: '#FFF', borderRadius: 8, borderWidth: 1, borderColor: palette.line, padding: 10, marginTop: 6 },
  inputText: { color: '#45434F', fontSize: 10 },
  audioRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginVertical: 12 },
  audioLabel: { color: '#4A4855', fontSize: 10 },
  switch: { width: 38, height: 22, borderRadius: 12, backgroundColor: '#D6D5DC', padding: 2, justifyContent: 'center' },
  switchOn: { backgroundColor: palette.accent },
  switchKnob: { width: 18, height: 18, backgroundColor: '#FFF', borderRadius: 10 },
  switchKnobOn: { alignSelf: 'flex-end' },
  link: { color: palette.accent, fontSize: 9, fontWeight: '700' },
  footer: { padding: 12, paddingHorizontal: 20, backgroundColor: '#FFF', borderTopWidth: 1, borderTopColor: palette.line },
  footnote: { textAlign: 'center', color: '#888692', fontSize: 9, marginTop: 7 },
});
