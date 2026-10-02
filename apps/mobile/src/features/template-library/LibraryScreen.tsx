import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Body, Eyebrow, Page, PrimaryButton, Title } from '../../shared/Components';
import { palette } from '../../shared/theme';
import { TemplateSummary } from './types';

type Props = {
  templates: TemplateSummary[];
  loading: boolean;
  error: string | null;
  onCreate: () => void;
  onOpen: (id: string) => void;
  onDuplicate: (id: string) => void;
  onDelete: (id: string) => void;
  onRetry: () => void;
};

export function LibraryScreen({ templates, loading, error, onCreate, onOpen, onDuplicate, onDelete, onRetry }: Props) {
  return <Page>
    <Eyebrow>YOUR CREATIVE WORKSPACE</Eyebrow>
    <Title>My templates.</Title>
    <Body>Your private recipes are saved on this device.</Body>

    {error && <View style={styles.error}>
      <Text style={styles.errorText}>{error}</Text>
      <Pressable accessibilityRole="button" onPress={onRetry}><Text style={styles.retry}>Try again</Text></Pressable>
    </View>}
    {loading ? <View style={styles.empty}><Text style={styles.emptyBody}>Loading your templates...</Text></View>
      : templates.length === 0 ? <View style={styles.empty}>
        <Text style={styles.emptyTitle}>Your first template starts here.</Text>
        <Text style={styles.emptyBody}>Create a reusable structure from a short video. The original video stays on your device and is not saved with the recipe.</Text>
        <PrimaryButton title="Create from a video" onPress={onCreate} />
      </View>
        : <View style={styles.list}>{templates.map((template) => <View key={template.id} style={styles.card}>
          <Pressable onPress={() => onOpen(template.id)} accessibilityRole="button" style={styles.cardMain}>
            <View style={styles.art}><Text style={styles.artMark}>{String(template.sectionCount).padStart(2, '0')}</Text></View>
            <View style={styles.copy}>
              <Text style={styles.cardTitle} numberOfLines={2}>{template.title}</Text>
              <Text style={styles.meta}>{template.sectionCount} moments | {template.runtimeSeconds.toFixed(1)} sec | Vertical</Text>
              <Text style={styles.open}>Open template</Text>
              {template.schemaVersion > 1 && <Text style={styles.unavailable}>Saved by a newer app version; update to edit.</Text>}
            </View>
          </Pressable>
          <View style={styles.actions}>
            <Pressable onPress={() => onDuplicate(template.id)} accessibilityRole="button" accessibilityLabel={`Duplicate ${template.title}`} style={styles.action}><Text style={styles.actionText}>Duplicate</Text></Pressable>
            <Pressable onPress={() => onDelete(template.id)} accessibilityRole="button" accessibilityLabel={`Delete ${template.title}`} style={styles.action}><Text style={styles.deleteText}>Delete</Text></Pressable>
          </View>
        </View>)}</View>}

    <View style={styles.starter}>
      <Eyebrow>STARTER PATTERNS</Eyebrow>
      <Text style={styles.starterTitle}>The quick reveal</Text>
      <Text style={styles.emptyBody}>A tiny setup, a satisfying payoff. Starter examples are not saved user templates yet.</Text>
    </View>
    {templates.length > 0 && <Pressable style={styles.create} onPress={onCreate} accessibilityRole="button"><Text style={styles.createText}>Create another template</Text></Pressable>}
    <Text style={styles.localNote}>Template timing and decisions are stored locally. Source video files are not copied into saved recipes.</Text>
  </Page>;
}

const styles = StyleSheet.create({
  error: { marginTop: 14, padding: 12, borderRadius: 10, backgroundColor: palette.coralSoft },
  errorText: { color: '#8A514A', fontSize: 10, lineHeight: 15 },
  retry: { color: palette.accent, fontSize: 10, fontWeight: '700', marginTop: 7 },
  empty: { borderWidth: 1, borderColor: palette.line, borderRadius: 15, padding: 19, backgroundColor: '#FFF', alignItems: 'flex-start', marginTop: 15, gap: 8 },
  emptyTitle: { color: palette.ink, fontSize: 15, fontWeight: '800' },
  emptyBody: { color: palette.muted, fontSize: 10, lineHeight: 15, marginVertical: 4 },
  list: { gap: 10, marginTop: 15 },
  card: { borderWidth: 1, borderColor: palette.line, borderRadius: 14, backgroundColor: '#FFF', overflow: 'hidden' },
  cardMain: { flexDirection: 'row', alignItems: 'stretch' },
  art: { width: 66, minHeight: 100, backgroundColor: '#D69686', justifyContent: 'flex-end', padding: 10 },
  artMark: { color: '#FFF', fontSize: 12, fontWeight: '800' },
  copy: { flex: 1, padding: 12, justifyContent: 'center' },
  cardTitle: { color: palette.ink, fontSize: 12, lineHeight: 16, fontWeight: '800' },
  meta: { color: '#878590', fontSize: 8, marginTop: 5 },
  open: { color: palette.accent, fontSize: 9, fontWeight: '700', marginTop: 9 },
  unavailable: { color: '#9A614E', fontSize: 8, marginTop: 6 },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', gap: 8, paddingHorizontal: 10, paddingBottom: 8 },
  action: { paddingVertical: 7, paddingHorizontal: 10, borderRadius: 7, backgroundColor: '#F4F3F8' },
  actionText: { color: '#5B54A4', fontSize: 8, fontWeight: '700' },
  deleteText: { color: '#A45E55', fontSize: 8, fontWeight: '700' },
  starter: { padding: 12, marginTop: 18, borderRadius: 11, backgroundColor: '#F0EFF8' },
  starterTitle: { color: palette.ink, fontSize: 11, fontWeight: '700', marginTop: 8 },
  create: { alignItems: 'center', paddingVertical: 12, marginTop: 10 },
  createText: { color: palette.accent, fontSize: 10, fontWeight: '700' },
  localNote: { color: '#85838F', fontSize: 8, lineHeight: 13, marginTop: 13 },
});
