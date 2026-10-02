import { useEffect, useMemo, useRef, useState } from 'react';
import { Alert, StatusBar, StyleSheet, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { AppHeader, TabBar } from './src/shared/Navigation';
import { DiscoverScreen } from './src/features/discover/DiscoverScreen';
import { ImportScreen } from './src/features/import/ImportScreen';
import { ReviewScreen } from './src/features/section-review/ReviewScreen';
import { AdaptScreen } from './src/features/recipe-editor/AdaptScreen';
import { TemplatePreviewScreen } from './src/features/recipe-editor/TemplatePreviewScreen';
import { LibraryScreen } from './src/features/template-library/LibraryScreen';
import { recipeRepository } from './src/features/template-library/SqliteRecipeRepository';
import { TemplateRecipe, TemplateSummary } from './src/features/template-library/types';
import { ProfileScreen } from './src/features/settings/ProfileScreen';
import { palette } from './src/shared/theme';
import { SectionDecision, ScreenName } from './src/shared/sampleData';
import { EditableSectionSpan, sectionDuration } from './src/features/section-review/types';
import { ImportedVideo } from './src/features/import/types';
import { projectDraftRepository } from './src/features/project-drafts/SqliteProjectDraftRepository';
import { DraftSourceFacts, ProjectDraft } from './src/features/project-drafts/types';

export default function App() {
  const [screen, setScreen] = useState<ScreenName>('discover');
  const [sections, setSections] = useState<EditableSectionSpan[]>([]);
  const [decisions, setDecisions] = useState<Record<string, SectionDecision>>({});
  const [ideaSelected, setIdeaSelected] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<ImportedVideo | null>(null);
  const [templates, setTemplates] = useState<TemplateSummary[]>([]);
  const [libraryLoading, setLibraryLoading] = useState(true);
  const [libraryError, setLibraryError] = useState<string | null>(null);
  const [activeTemplate, setActiveTemplate] = useState<TemplateRecipe | null>(null);
  const [templateTitle, setTemplateTitle] = useState('My video template');
  const [templateSaving, setTemplateSaving] = useState(false);
  const [templateSaveError, setTemplateSaveError] = useState<string | null>(null);
  const [draftReady, setDraftReady] = useState(false);
  const [hasDraft, setHasDraft] = useState(false);
  const nextSectionId = useRef(1);
  const draftId = useRef<string | null>(null);
  const draftSourceFacts = useRef<DraftSourceFacts | null>(null);
  const restoringDraft = useRef(false);
  const restoredStage = useRef<ProjectDraft['stage']>('review');
  const draftGeneration = useRef(0);
  const deletingDraft = useRef(false);

  const includedSections = useMemo(
    () => sections.filter((section) => decisions[section.id] !== 'exclude'),
    [sections, decisions],
  );
  const runtime = includedSections.reduce((sum, section) => sum + sectionDuration(section), 0);

  const refreshLibrary = async () => {
    setLibraryLoading(true);
    try {
      setTemplates(await recipeRepository.list());
      setLibraryError(null);
    } catch {
      setLibraryError('The template library could not be opened. Your saved data has not been changed.');
    } finally {
      setLibraryLoading(false);
    }
  };
  useEffect(() => {
    void refreshLibrary();
    void projectDraftRepository.getActive().then((draft) => {
      setDraftReady(true);
      if (!draft) return;
      Alert.alert('Unfinished project found', 'Resume your saved section decisions? The source video was not stored, so you will need to choose it again.', [
        { text: 'Discard', style: 'destructive', onPress: () => {
          void projectDraftRepository.deleteActive().then(() => setHasDraft(false)).catch(() => Alert.alert('Project not discarded', 'The saved draft is still on this device.'));
        } },
        { text: 'Resume', onPress: () => {
          draftId.current = draft.id;
          draftSourceFacts.current = draft.sourceFacts;
          restoringDraft.current = true;
          restoredStage.current = draft.stage;
          setSections(draft.sections);
          setDecisions(draft.decisions);
          nextSectionId.current = Math.max(1, ...draft.sections.map((section) => {
            const match = /^(?:manual-)?(\d+)$/.exec(section.id);
            return match ? Number(match[1]) + 1 : 1;
          }));
          setHasDraft(true);
          setScreen('import');
        } },
      ]);
    }).catch(() => {
      setDraftReady(true);
      Alert.alert('Draft unavailable', 'The saved project could not be opened safely. Its data has been preserved.');
    });
  }, []);

  useEffect(() => {
    if (!draftReady || !draftId.current || !draftSourceFacts.current || sections.length === 0) return;
    const generation = draftGeneration.current;
    const timer = setTimeout(() => {
      if (generation !== draftGeneration.current || deletingDraft.current || !draftId.current) return;
      const stage: ProjectDraft['stage'] = restoringDraft.current
        ? restoredStage.current
        : screen === 'adapt' || screen === 'template-preview' ? 'adapt' : screen === 'review' ? 'review' : 'import';
      const draft: ProjectDraft = {
        id: draftId.current!,
        schemaVersion: 1,
        updatedAt: new Date().toISOString(),
        stage,
        sourceFacts: draftSourceFacts.current!,
        sections,
        decisions,
      };
      void projectDraftRepository.save(draft).then(() => setHasDraft(true)).catch(() => {
        Alert.alert('Draft could not be saved', 'Your current edits remain on screen, but may not survive closing the app.');
      });
    }, 450);
    return () => clearTimeout(timer);
  }, [draftReady, screen, sections, decisions]);

  const startNewTemplate = () => {
    if (draftId.current && hasDraft) {
      Alert.alert('Start a new template?', 'This replaces your current unfinished project.', [
        { text: 'Keep editing', style: 'cancel' },
        { text: 'Start new', style: 'destructive', onPress: () => {
          void deleteActiveDraft().then(() => resetForNewTemplate()).catch(() => Alert.alert('Could not start a new project', 'Your unfinished project is still saved.'));
        } },
      ]);
      return;
    }
    resetForNewTemplate();
  };

  const resetForNewTemplate = () => {
    draftId.current = null;
    draftSourceFacts.current = null;
    restoringDraft.current = false;
    setHasDraft(false);
    setSelectedVideo(null);
    setSections([]);
    setDecisions({});
    setActiveTemplate(null);
    setTemplateTitle('My video template');
    setTemplateSaveError(null);
    setScreen('import');
  };

  const deleteActiveDraft = async () => {
    draftGeneration.current += 1;
    deletingDraft.current = true;
    try {
      await projectDraftRepository.deleteActive();
      draftId.current = null;
      draftSourceFacts.current = null;
      restoringDraft.current = false;
      setHasDraft(false);
    } finally {
      deletingDraft.current = false;
    }
  };

  const goBack = () => {
    if (screen === 'template-preview') {
      setScreen(activeTemplate ? 'library' : 'adapt');
    } else if (screen === 'adapt') {
      setScreen('review');
    } else if (screen === 'review') {
      setScreen('import');
    } else {
      setScreen('discover');
    }
  };

  const setImportedVideo = (video: ImportedVideo) => {
    if (restoringDraft.current) {
      const expected = draftSourceFacts.current;
      const sameFacts = !!expected
        && Math.abs((video.durationSeconds ?? 0) - expected.durationSeconds) < 0.2
        && video.width === expected.width
        && video.height === expected.height
        && (expected.fileSizeBytes === undefined || video.fileSizeBytes === expected.fileSizeBytes);
      const resumeWithVideo = () => {
        if (!video.durationSeconds || video.durationSeconds <= 0 || video.durationSeconds > 30) {
          Alert.alert('This video cannot resume the project', 'Choose a readable source that is 30 seconds or shorter. Your saved section decisions are unchanged.');
          return;
        }
        restoringDraft.current = false;
        setSelectedVideo(video);
        setScreen(restoredStage.current);
      };
      if (!sameFacts) {
        Alert.alert('Video details differ', 'This does not appear to be the same source as the unfinished project. Continue with it anyway?', [
          { text: 'Choose another', style: 'cancel' },
          { text: 'Continue', onPress: resumeWithVideo },
        ]);
      } else {
        resumeWithVideo();
      }
      return;
    }
    if (draftId.current && hasDraft && selectedVideo) {
      const sameSource = selectedVideo.durationSeconds === video.durationSeconds
        && selectedVideo.width === video.width
        && selectedVideo.height === video.height
        && Math.abs((selectedVideo.durationSeconds ?? 0) - (video.durationSeconds ?? 0)) < 0.2
        && (selectedVideo.fileSizeBytes === undefined || video.fileSizeBytes === undefined || selectedVideo.fileSizeBytes === video.fileSizeBytes);
      if (!sameSource) {
        Alert.alert('Replace this unfinished project?', 'Choosing a different source starts a new project and removes the current draft.', [
          { text: 'Keep current project', style: 'cancel' },
          { text: 'Replace project', style: 'destructive', onPress: () => {
            void deleteActiveDraft().then(() => {
              setImportedVideo(video);
            }).catch(() => Alert.alert('Could not replace project', 'Your unfinished project is still saved.'));
          } },
        ]);
        return;
      }
    }
    const facts: DraftSourceFacts | null = video.durationSeconds && video.durationSeconds > 0 && video.durationSeconds <= 30
      ? { durationSeconds: video.durationSeconds, width: video.width, height: video.height, fileSizeBytes: video.fileSizeBytes }
      : null;
    if (facts) {
      draftId.current = createTemplateId();
      draftSourceFacts.current = facts;
    }
    setSelectedVideo(video);
    setActiveTemplate(null);
    setTemplateTitle('My video template');
    setDecisions({});
    nextSectionId.current = 2;
    setSections(video.durationSeconds && video.durationSeconds > 0 && video.durationSeconds <= 30
      ? [makeManualSection(1, 0, video.durationSeconds)]
      : []);
    setHasDraft(!!facts);
  };

  const updateDetectedDuration = (duration: number) => {
    if (selectedVideo?.durationSeconds !== null && selectedVideo?.durationSeconds !== undefined
      && Math.abs(selectedVideo.durationSeconds - duration) < 0.1) return;
    setSelectedVideo((video) => video ? { ...video, durationSeconds: duration } : video);
    if (!draftId.current && selectedVideo && duration > 0 && duration <= 30) {
      draftId.current = createTemplateId();
      draftSourceFacts.current = {
        durationSeconds: duration,
        width: selectedVideo.width,
        height: selectedVideo.height,
        fileSizeBytes: selectedVideo.fileSizeBytes,
      };
      setHasDraft(true);
    }
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

  const saveTemplate = () => {
    const saveSections: TemplateRecipe['sections'] = activeTemplate
      ? activeTemplate.sections
      : sections.map((section, order) => ({
        ...section,
        order,
        decision: decisions[section.id] ?? 'exclude',
      }));
    const keptIds = saveSections.filter((section) => section.decision === 'keep').map((section) => section.id);
    if (keptIds.length > 0) {
      Alert.alert('Original video will not be saved', `${keptIds.length} kept ${keptIds.length === 1 ? 'moment points' : 'moments point'} to the imported video. Convert them to replaceable slots so the recipe does not keep or copy the source footage?`, [
        { text: 'Go back', style: 'cancel' },
        { text: 'Convert to slots', onPress: () => {
          const converted = saveSections.map((section) => section.decision === 'keep' ? { ...section, decision: 'edit' as const } : section);
          void persistTemplate(converted);
        } },
      ]);
      return;
    }
    void persistTemplate(saveSections);
  };

  const persistTemplate = async (saveSections: TemplateRecipe['sections']) => {
    const now = new Date().toISOString();
    const recipe: TemplateRecipe = {
      id: activeTemplate?.id ?? createTemplateId(),
      schemaVersion: 1,
      title: templateTitle.trim(),
      createdAt: activeTemplate?.createdAt ?? now,
      updatedAt: now,
      sourceDurationSeconds: activeTemplate?.sourceDurationSeconds
        ?? selectedVideo?.durationSeconds
        ?? Math.max(0, ...sections.map((section) => section.endSeconds)),
      aspectRatio: activeTemplate?.aspectRatio ?? '9:16',
      sections: saveSections,
    };
    setTemplateSaving(true);
    setTemplateSaveError(null);
    try {
      await recipeRepository.save(recipe);
      if (!activeTemplate) {
        try {
          await deleteActiveDraft();
        } catch {
          Alert.alert('Template saved; draft cleanup is pending', 'Your template is in the library. The unfinished-project draft remains on this device and can be discarded from the import screen.');
        }
      }
      setActiveTemplate(recipe);
      setTemplateTitle(recipe.title);
      await refreshLibrary();
      setScreen('library');
    } catch {
      setTemplateSaveError('The template could not be saved. Your current edits are still on screen; try again.');
    } finally {
      setTemplateSaving(false);
    }
  };

  const openTemplate = async (id: string) => {
    try {
      const recipe = await recipeRepository.get(id);
      if (!recipe) {
        setLibraryError('That template is no longer in the library. Refresh and try again.');
        return;
      }
      setActiveTemplate(recipe);
      setTemplateTitle(recipe.title);
      setTemplateSaveError(null);
      setScreen('template-preview');
    } catch (error) {
      Alert.alert('Template could not be opened', error instanceof Error ? error.message : 'The saved template was preserved.');
    }
  };

  const duplicateTemplate = async (id: string) => {
    try {
      const recipe = await recipeRepository.get(id);
      if (!recipe) return;
      const now = new Date().toISOString();
      const copy: TemplateRecipe = {
        ...recipe,
        id: createTemplateId(),
        title: `Copy of ${recipe.title}`.slice(0, 120),
        createdAt: now,
        updatedAt: now,
        sections: recipe.sections.map((section, order) => ({ ...section, id: `section_${order + 1}` })),
      };
      await recipeRepository.save(copy);
      await refreshLibrary();
    } catch (error) {
      Alert.alert('Template could not be duplicated', error instanceof Error ? error.message : 'Please try again.');
    }
  };

  const deleteTemplate = (id: string) => {
    const selected = templates.find((template) => template.id === id);
    Alert.alert('Delete this template?', `Delete ${selected?.title ?? 'this template'} from this device? This cannot be undone.`, [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Delete', style: 'destructive', onPress: () => {
        void recipeRepository.delete(id).then(async () => {
          if (activeTemplate?.id === id) setActiveTemplate(null);
          await refreshLibrary();
        }).catch(() => setLibraryError('The template could not be deleted. Your saved data has not been changed.'));
      } },
    ]);
  };

  const previewSections: TemplateRecipe['sections'] = activeTemplate?.sections ?? sections.map((section, order) => ({
    ...section,
    order,
    decision: decisions[section.id] ?? 'exclude',
  }));
  const previewRuntime = previewSections
    .filter((section) => section.decision !== 'exclude')
    .reduce((sum, section) => sum + sectionDuration(section), 0);
  const sourceDuration = activeTemplate?.sourceDurationSeconds ?? selectedVideo?.durationSeconds ?? Math.max(0, ...sections.map((section) => section.endSeconds));

  return <SafeAreaProvider>
    <SafeAreaView style={styles.app} edges={['top', 'bottom']}>
      <StatusBar barStyle="dark-content" backgroundColor={palette.canvas} />
      <AppHeader showBack={screen !== 'discover' && screen !== 'library'} onBack={goBack} onProfile={() => setScreen('profile')} />
      <View style={styles.content}>
        {screen === 'discover' && <DiscoverScreen onCreate={startNewTemplate} onBrowse={() => setScreen('library')} onUseRecipe={() => setScreen('library')} />}
        {screen === 'import' && <ImportScreen selectedVideo={selectedVideo} restoringDraft={restoringDraft.current} hasDraft={hasDraft} onDiscardDraft={() => {
          Alert.alert('Discard unfinished project?', 'This removes its saved section decisions from this device.', [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Discard', style: 'destructive', onPress: () => { void deleteActiveDraft().then(() => resetForNewTemplate()).catch(() => Alert.alert('Project not discarded', 'The saved draft is still on this device.')); } },
          ]);
        }} onVideoSelected={setImportedVideo} onDurationReady={updateDetectedDuration} onChooseVideoError={(message) => Alert.alert('Video unavailable', message)} onContinue={() => setScreen('review')} />}
        {screen === 'review' && <ReviewScreen sourceVideo={selectedVideo} sections={sections} decisions={decisions} onDecision={(id, decision) => setDecisions((old) => ({ ...old, [id]: decision }))} onSplitAt={splitSectionAt} includedCount={includedSections.length} runtime={runtime} onNext={() => setScreen('adapt')} />}
        {screen === 'adapt' && <AdaptScreen ideaSelected={ideaSelected} onSelectIdea={() => setIdeaSelected(true)} onPreview={() => setScreen('template-preview')} />}
        {screen === 'template-preview' && <TemplatePreviewScreen title={templateTitle} sections={previewSections} sourceDurationSeconds={sourceDuration} runtime={previewRuntime} isSaved={activeTemplate !== null} saving={templateSaving} error={templateSaveError} onTitleChange={setTemplateTitle} onSave={saveTemplate} />}
        {screen === 'library' && <LibraryScreen templates={templates} loading={libraryLoading} error={libraryError} onCreate={startNewTemplate} onOpen={openTemplate} onDuplicate={duplicateTemplate} onDelete={deleteTemplate} onRetry={() => { void refreshLibrary(); }} />}
        {screen === 'profile' && <ProfileScreen onSignIn={() => Alert.alert('Sign-in is not connected yet', 'Local template creation works without an account.')} />}
      </View>
      {['discover', 'library', 'profile'].includes(screen) && <TabBar active={screen} onSelect={(name) => setScreen(name)} onCreate={startNewTemplate} />}
    </SafeAreaView>
  </SafeAreaProvider>;
}

const styles = StyleSheet.create({
  app: { flex: 1, backgroundColor: palette.canvas },
  content: { flex: 1 },
});

function makeManualSection(id: number, startSeconds: number, endSeconds: number): EditableSectionSpan {
  return { id: `manual-${id}`, startSeconds, endSeconds };
}

function createTemplateId(): string {
  return `template_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 9)}`;
}
