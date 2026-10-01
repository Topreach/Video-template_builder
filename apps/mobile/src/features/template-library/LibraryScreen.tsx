import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Body, Eyebrow, Page, PrimaryButton, SectionHeading, Title } from '../../shared/Components';
import { palette } from '../../shared/theme';

type Props = { saved: boolean; onCreate: () => void; onOpenSaved: () => void };
export function LibraryScreen({ saved, onCreate, onOpenSaved }: Props) {
  return <Page><Eyebrow>YOUR CREATIVE WORKSPACE</Eyebrow><Title>My recipes.</Title><Body>Preview saved recipes and their reusable structure.</Body>
    <View style={styles.filters}><Text style={[styles.filter, styles.filterActive]}>All</Text><Text style={styles.filter}>Drafts</Text><Text style={styles.filter}>Ready</Text></View>
    {saved ? <Pressable onPress={onOpenSaved} style={styles.recipe}><View style={styles.recipeArt}><Text style={styles.artWords}>THE{ '\n' }REVEAL</Text><Text style={styles.artPlay}>▶</Text></View><View style={styles.recipeCopy}><Text style={styles.badge}>READY TO REMIX</Text><Text style={styles.recipeTitle}>My reveal recipe</Text><Text style={styles.recipeMeta}>3 moments · 13 sec · Vertical</Text><Text style={styles.open}>Open recipe  ›</Text></View></Pressable> : <View style={styles.empty}><View style={styles.emptyIcon}>▤</View><Text style={styles.emptyTitle}>Your first recipe starts here.</Text><Text style={styles.emptyBody}>Turn a video into a structure you can reuse with your own moments.</Text><PrimaryButton title="Create from a video" onPress={onCreate} /></View>}
    <SectionHeading eyebrow="STARTER IDEAS" title="Try a recipe" />
    <View style={styles.ideaRow}><View style={[styles.miniArt, { backgroundColor: '#E1AD97' }]}><Text style={styles.miniMark}>01</Text></View><View style={styles.ideaCopy}><Text style={styles.ideaTitle}>The quick reveal</Text><Text style={styles.recipeMeta}>A tiny setup, a satisfying payoff.</Text></View><Text style={styles.chevron}>›</Text></View>
    <View style={styles.localNote}><Text style={styles.lock}>◇</Text><Text style={styles.noteCopy}><Text style={styles.noteStrong}>Preview session only</Text>{'\n'}Recipe storage is not connected yet; closing the app clears this sample state.</Text></View>
  </Page>;
}

const styles = StyleSheet.create({
  filters: { flexDirection: 'row', gap: 8, marginTop: 19, marginBottom: 12 },
  filter: { borderRadius: 18, overflow: 'hidden', backgroundColor: '#FFF', borderWidth: 1, borderColor: palette.line, color: '#777582', paddingHorizontal: 13, paddingVertical: 7, fontSize: 9, fontWeight: '600' },
  filterActive: { color: '#5146B7', backgroundColor: palette.accentSoft, borderColor: '#E1DEFC' },
  empty: { borderWidth: 1, borderColor: palette.line, borderRadius: 15, padding: 19, backgroundColor: '#FFF', alignItems: 'flex-start', marginTop: 5 },
  emptyIcon: { width: 40, height: 40, backgroundColor: palette.accentSoft, color: palette.accent, borderRadius: 12, textAlign: 'center', textAlignVertical: 'center', fontSize: 20, overflow: 'hidden', paddingTop: 8 },
  emptyTitle: { color: palette.ink, fontSize: 15, fontWeight: '800', marginTop: 13 },
  emptyBody: { color: palette.muted, fontSize: 10, lineHeight: 15, marginVertical: 7 },
  recipe: { flexDirection: 'row', backgroundColor: '#FFF', borderRadius: 14, borderWidth: 1, borderColor: palette.line, overflow: 'hidden', marginTop: 5 },
  recipeArt: { width: 111, minHeight: 125, backgroundColor: '#D69686', justifyContent: 'flex-end', padding: 11 },
  artWords: { color: '#FFF', fontSize: 15, lineHeight: 15, letterSpacing: 1, fontWeight: '900' },
  artPlay: { position: 'absolute', top: 42, alignSelf: 'center', color: '#FFF', fontSize: 14 },
  recipeCopy: { flex: 1, padding: 12, justifyContent: 'center' },
  badge: { color: palette.green, fontSize: 7, letterSpacing: .7, fontWeight: '800' },
  recipeTitle: { color: palette.ink, fontWeight: '800', fontSize: 12, marginTop: 7 },
  recipeMeta: { color: '#878590', fontSize: 8, marginTop: 4 },
  open: { color: palette.accent, fontSize: 9, fontWeight: '700', marginTop: 12 },
  ideaRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 9 },
  miniArt: { width: 47, height: 50, borderRadius: 9, justifyContent: 'flex-end', padding: 5 },
  miniMark: { color: '#FFF', fontWeight: '700', fontSize: 7 },
  ideaCopy: { flex: 1, marginLeft: 10 },
  ideaTitle: { color: palette.ink, fontWeight: '700', fontSize: 10 },
  chevron: { color: '#9896A1', fontSize: 20, paddingHorizontal: 5 },
  localNote: { flexDirection: 'row', gap: 8, padding: 11, marginTop: 17, backgroundColor: '#F0EFF8', borderRadius: 10 },
  lock: { color: palette.accent, fontSize: 14 },
  noteCopy: { color: '#85838F', fontSize: 8, lineHeight: 13 },
  noteStrong: { color: '#393744', fontWeight: '700' },
});
