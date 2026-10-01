import { useMemo, useState } from 'react';
import { Alert, StatusBar, StyleSheet, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader, TabBar } from './src/shared/Navigation';
import { DiscoverScreen } from './src/features/discover/DiscoverScreen';
import { ImportScreen } from './src/features/import/ImportScreen';
import { ReviewScreen } from './src/features/section-review/ReviewScreen';
import { AdaptScreen } from './src/features/recipe-editor/AdaptScreen';
import { TemplatePreviewScreen } from './src/features/recipe-editor/TemplatePreviewScreen';
import { LibraryScreen } from './src/features/template-library/LibraryScreen';
import { ProfileScreen } from './src/features/settings/ProfileScreen';
import { palette } from './src/shared/theme';
import { sampleSections, SectionDecision, ScreenName } from './src/shared/sampleData';
import { ImportedVideo } from './src/features/import/types';

const flow: ScreenName[] = ['discover', 'import', 'review', 'adapt', 'template-preview'];

export default function App() {
  const [screen, setScreen] = useState<ScreenName>('discover');
  const [decisions, setDecisions] = useState<Record<string, SectionDecision>>({
    hook: 'edit', setup: 'edit', reveal: 'edit', outro: 'exclude',
  });
  const [ideaSelected, setIdeaSelected] = useState(false);
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState('Vertical social · 9:16');
  const [previewMode, setPreviewMode] = useState<'template' | 'reference'>('template');
  const [selectedVideo, setSelectedVideo] = useState<ImportedVideo | null>(null);

  const includedSections = useMemo(
    () => sampleSections.filter((section) => decisions[section.id] !== 'exclude'),
    [decisions],
  );
  const runtime = includedSections.reduce((sum, section) => sum + section.duration, 0);
  const goBack = () => {
    const index = flow.indexOf(screen);
    setScreen(index > 0 ? flow[index - 1] : 'discover');
  };
  const saveTemplate = () => {
    setSaved(true);
    setScreen('library');
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.app} edges={['top', 'bottom']}>
        <StatusBar barStyle="dark-content" backgroundColor={palette.canvas} />
        <AppHeader showBack={screen !== 'discover' && screen !== 'library'} onBack={goBack} onProfile={() => setScreen('profile')} />
        <View style={styles.content}>
          {screen === 'discover' && <DiscoverScreen onCreate={() => setScreen('import')} onBrowse={() => setScreen('library')} onUseRecipe={() => setScreen('adapt')} />}
          {screen === 'import' && <ImportScreen selectedVideo={selectedVideo} onVideoSelected={setSelectedVideo} onDurationReady={(duration) => setSelectedVideo((video) => video ? { ...video, durationSeconds: duration } : video)} onChooseVideoError={(message) => Alert.alert('Can’t use this video yet', message)} onAnalyze={() => setScreen('review')} />}
          {screen === 'review' && <ReviewScreen sourceVideo={selectedVideo} decisions={decisions} onDecision={(id, decision) => setDecisions((old) => ({ ...old, [id]: decision }))} includedCount={includedSections.length} runtime={runtime} onNext={() => setScreen('adapt')} />}
          {screen === 'adapt' && <AdaptScreen ideaSelected={ideaSelected} onSelectIdea={() => setIdeaSelected(true)} onPreview={() => setScreen('template-preview')} />}
          {screen === 'template-preview' && <TemplatePreviewScreen profile={profile} previewMode={previewMode} includedSections={includedSections} decisions={decisions} runtime={runtime} onProfileChange={setProfile} onPreviewModeChange={setPreviewMode} onSave={saveTemplate} />}
          {screen === 'library' && <LibraryScreen saved={saved} onCreate={() => setScreen('import')} onOpenSaved={() => setScreen('template-preview')} />}
          {screen === 'profile' && <ProfileScreen onSignIn={() => Alert.alert('Sign-in is not connected yet', 'The first release is planned to support local creation without an account.')} />}
        </View>
        {['discover', 'library', 'profile'].includes(screen) && (
          <TabBar active={screen} onSelect={(name) => setScreen(name)} onCreate={() => setScreen('import')} />
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  app: { flex: 1, backgroundColor: palette.canvas },
  content: { flex: 1 },
});
