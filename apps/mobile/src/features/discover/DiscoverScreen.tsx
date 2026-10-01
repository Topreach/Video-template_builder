import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { Body, CategoryChips, Eyebrow, InfoCard, Page, PrimaryButton, SecondaryButton, SectionHeading, Title } from '../../shared/Components';
import { palette } from '../../shared/theme';

type Props = { onCreate: () => void; onBrowse: () => void; onUseRecipe: () => void };
export function DiscoverScreen({ onCreate, onBrowse, onUseRecipe }: Props) {
  return <Page><Eyebrow>YOUR NEXT VIDEO STARTS HERE</Eyebrow><Title>Make the moment{ '\n' }your own.</Title><Body>Turn a video you love into a reusable recipe for your next one.</Body>
    <View style={styles.actions}><PrimaryButton title="Create from a video" onPress={onCreate} /><SecondaryButton title="✳   Start with an idea" onPress={onBrowse} /></View>
    <SectionHeading eyebrow="A LITTLE INSPIRATION" title="Recipes to remix" action="See all" onAction={onBrowse} />
    <CategoryChips values={['For you', 'Funny', 'Music', 'Story', 'How-to']} />
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.cards}>
      <RecipeCard title="Wait for it…" meta="Funny · 12 sec · 3 clips" label="THE REVEAL" color="#DC9A8C" onPress={onUseRecipe} />
      <RecipeCard title="Two sides of me" meta="Story · 18 sec · 4 clips" label="THEN / NOW" color="#84AABD" onPress={onUseRecipe} />
    </ScrollView>
    <InfoCard title="Your ideas stay yours">Start privately. Sign in only when you want cloud backup.</InfoCard>
  </Page>;
}

function RecipeCard({ title, meta, label, color, onPress }: { title: string; meta: string; label: string; color: string; onPress: () => void }) {
  return <Pressable onPress={onPress} style={styles.card} accessibilityRole="button" accessibilityLabel={`${title}, ${meta}`}>
    <View style={[styles.art, { backgroundColor: color }]}><View style={styles.artShape} /><Text style={styles.artLabel}>{label}</Text><View style={styles.play}><Text style={styles.playText}>▶</Text></View></View>
    <Text style={styles.cardTitle}>{title}</Text><Text style={styles.meta}>{meta}</Text>
  </Pressable>;
}

const styles = StyleSheet.create({
  actions: { gap: 9, marginTop: 21 },
  cards: { gap: 12, paddingTop: 2, paddingRight: 20 },
  card: { width: 158 },
  art: { height: 142, borderRadius: 15, overflow: 'hidden', alignItems: 'center', justifyContent: 'center', position: 'relative' },
  artShape: { position: 'absolute', width: 85, height: 125, bottom: -10, borderRadius: 45, backgroundColor: '#FFFFFF45', transform: [{ rotate: '-7deg' }] },
  artLabel: { position: 'absolute', bottom: 11, left: 10, fontSize: 8, letterSpacing: 1.2, fontWeight: '800', color: '#FFF' },
  play: { width: 30, height: 30, borderRadius: 15, backgroundColor: '#FFFFFFDC', justifyContent: 'center', alignItems: 'center' },
  playText: { color: '#514C60', fontSize: 9, marginLeft: 2 },
  cardTitle: { color: palette.ink, fontSize: 12, fontWeight: '700', marginTop: 8 },
  meta: { color: '#85838F', fontSize: 9, marginTop: 3 },
});
