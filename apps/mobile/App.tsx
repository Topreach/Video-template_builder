import { useMemo, useRef, useState } from 'react';
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
import { SectionDecision, ScreenName } from './src/shared/sampleData';
import { EditableSectionSpan, sectionDuration } from './src/features/section-review/types';
import { ImportedVideo } from './src/features/import/types';

const flow: ScreenName[] = ['discover', 'import', 'review', 'adapt', 'template-preview'];

export default function App() {
  const [screen, setScreen] = useState<ScreenName>('discover');
  const [sections, setSections] = useState<EditableSectionSpan[]>([]);
  const [decisions, setDecisions] = useState<Record<string, SectionDecision>>({});
  const [ideaSelected, setIdeaSelected] = useState(false);
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState('Vertical social · 9:16');
  const [previewMode, setPreviewMode] = useState<'template' | 'reference'>('template');
  const [selectedVideo, setSelectedVideo] = useState<ImportedVideo | null>(null);
  const nextSectionId = useRef(1);

  const includedSections = useMemo(
    () => sections.filter((section) => decisions[section.id] !== 'exclude'),
    [sections, decisions],
  );
  const runtime = includedSections.reduce((sum, section) => sum + sectionDuration(section), 0);
  const setImportedVideo = (video: ImportedVideo) => {
    setSelectedVideo(video);
    setDecisions({});
    nextSectionId.current = 2;
    setSections(video.durationSeconds && video.durationSeconds > 0 && video.durationSeconds <= 30
      ? [makeManualSection(1, 0, video.durationSeconds)]
      : []);
  };
  const updateDetectedDuration = (duration: number) => {
    if (selectedVideo?.durationSeconds !== null && selectedVideo?.durationSeconds !== undefined
      && Math.abs(selectedVideo.durationSeconds - duration) < 0.1) return;
    setSelectedVideo((video) => video ? { ...video, durationSeconds: duration } : video);
    if (sections.length <= 1 && sections.every((section) => !decisions[section.id])) {
      setSections(duration > 0 && duration <= 30 ? [makeManualSection(1, 0, duration)] : []);
      setDecisions({});
      nextSectionId.current = 2;
    }
  };
  const splitSectionAt = (seconds: number) => {
    const target = sections.find((section) => seconds > section.startSeconds && seconds < section.endSeconds);
    if (!target) return false;
    const firstId = nextSectionId.current++;
    const secondId = nextSectionId.current++;
    const replacement = [makeManualSection(firstId, target.startSeconds, seconds), makeManualSection(secondId, seconds, target.endSeconds)];
    setSections((current) => current.flatMap((section) => section.id === target.id ? replacement : [section]));
    setDecisions((current) => {
      const next = { ...current };
      delete next[target.id];
      return next;
    });
    return true;
  };
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
          {screen === 'import' && <ImportScreen selectedVideo={selectedVideo} onVideoSelected={setImportedVideo} onDurationReady={updateDetectedDuration} onChooseVideoError={(message) => Alert.alert('Can’t use this video yet', message)} onContinue={() => setScreen('review')} />}
          {screen === 'review' && <ReviewScreen sourceVideo={selectedVideo} sections={sections} decisions={decisions} onDecision={(id, decision) => setDecisions((old) => ({ ...old, [id]: decision }))} onSplitAt={splitSectionAt} includedCount={includedSections.length} runtime={runtime} onNext={() => setScreen('adapt')} />}
          {screen === 'adapt' && <AdaptScreen ideaSelected={ideaSelected} onSelectIdea={() => setIdeaSelected(true)} onPreview={() => setScreen('template-preview')} />}
          {screen === 'template-preview' && <TemplatePreviewScreen profile={profile} previewMode={previewMode} includedSections={includedSections.map((section, index) => ({ id: section.id, label: `Moment ${index + 1}` }))} decisions={decisions} runtime={runtime} onProfileChange={setProfile} onPreviewModeChange={setPreviewMode} onSave={saveTemplate} />}
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

function makeManualSection(id: number, startSeconds: number, endSeconds: number): EditableSectionSpan {
  return { id: `manual-${id}`, startSeconds, endSeconds };
}
