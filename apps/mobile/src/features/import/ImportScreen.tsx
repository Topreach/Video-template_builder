import { useState } from 'react';
import { Alert, Platform, Pressable, StyleSheet, Text, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Body, Eyebrow, InfoCard, Page, PrimaryButton, SecondaryButton, StepLabel, Title } from '../../shared/Components';
import { palette } from '../../shared/theme';
import { ImportedVideo } from './types';
import { SelectedVideoPreview } from './SelectedVideoPreview';

type Props = {
  selectedVideo: ImportedVideo | null;
  onVideoSelected: (video: ImportedVideo) => void;
  onDurationReady: (duration: number) => void;
  onChooseVideoError: (message: string) => void;
  onContinue: () => void;
};

export function ImportScreen({ selectedVideo, onVideoSelected, onDurationReady, onChooseVideoError, onContinue }: Props) {
  const [selecting, setSelecting] = useState(false);
  const duration = selectedVideo?.durationSeconds;
  const exceedsLimit = duration !== null && duration !== undefined && duration > 30;
  const ready = !!selectedVideo && duration !== null && duration !== undefined && duration > 0 && !exceedsLimit;

  async function chooseVideo() {
    setSelecting(true);
    try {
      // Request iOS access only after the person asks to choose a source video.
      // Android opens the system photo picker without broad library permission.
      if (Platform.OS === 'ios') {
        const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (!permission.granted) {
          onChooseVideoError('Allow access to the video you choose so the app can preview and inspect it.');
          return;
        }
      }
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['videos'],
        allowsEditing: false,
        videoMaxDuration: 0,
        exif: false,
      });
      if (result.canceled || !result.assets?.[0]) return;
      const asset = result.assets[0];
      if (asset.type !== 'video') {
        onChooseVideoError('Choose a video file to continue.');
        return;
      }
      onVideoSelected({
        uri: asset.uri,
        fileName: asset.fileName || 'Selected video',
        durationSeconds: typeof asset.duration === 'number' && asset.duration > 0 ? asset.duration / 1000 : null,
        width: asset.width,
        height: asset.height,
        fileSizeBytes: asset.fileSize,
      });
    } catch {
      onChooseVideoError('The video picker could not open. Try again or choose another video.');
    } finally {
      setSelecting(false);
    }
  }

  return <Page footer={<View style={styles.footer}><PrimaryButton title={exceedsLimit ? 'Choose a video under 30 seconds' : ready ? 'Set up video moments' : 'Choose a video to continue'} disabled={!ready} onPress={onContinue} /><Text style={styles.footnote}>Your original file is not modified.</Text></View>}>
    <StepLabel number="01">START WITH A REFERENCE</StepLabel><Title>Bring the video.{'\n'}Keep the good parts.</Title><Body>Set up moments to reuse. Automatic scene suggestions are planned for a later step.</Body>
    {!selectedVideo ? <View style={styles.upload}><View style={styles.uploadIcon}><Text style={styles.uploadArrow}>↑</Text></View><Text style={styles.uploadTitle}>Choose a video</Text><Text style={styles.uploadMeta}>From your device · up to 30 seconds</Text><SecondaryButton title={selecting ? 'Opening library…' : 'Choose from library'} onPress={chooseVideo} /></View> : <>
      <SelectedVideoPreview uri={selectedVideo.uri} onDuration={onDurationReady} />
      <View style={styles.fileRow}><View style={{ flex: 1 }}><Text style={styles.fileName} numberOfLines={1}>{selectedVideo.fileName}</Text><Text style={styles.fileMeta}>{duration && duration > 0 ? `${duration.toFixed(1)} sec` : 'Checking duration…'} · {selectedVideo.width} × {selectedVideo.height}</Text></View><Pressable onPress={chooseVideo} accessibilityRole="button"><Text style={styles.change}>Change</Text></Pressable></View>
      {exceedsLimit ? <View style={styles.error}><Text style={styles.errorTitle}>This video is over the 30-second limit.</Text><Text style={styles.errorBody}>Choose a shorter source. We won’t trim it silently.</Text></View> : <Text style={styles.hint}>The 30-second check uses the source duration. We won’t shorten the video for you.</Text>}
    </>}
    <View style={styles.explainer}><View style={styles.or}><View style={styles.rule} /><Text style={styles.orText}>WHAT HAPPENS NEXT</Text><View style={styles.rule} /></View><InfoCard title="You choose every moment" icon="i">Divide the clip into moments, then mark each Edit, Keep, or Exclude before saving.</InfoCard></View>
    <View style={styles.previewNote}><Eyebrow>BUILD STATUS</Eyebrow><Text style={styles.previewNoteText}>Video picking, local preview, and the 30-second gate are connected. Manual moment setup works now; automatic scene detection is still to come.</Text></View>
  </Page>;
}

const styles = StyleSheet.create({
  upload: { minHeight: 210, marginTop: 24, borderWidth: 1.5, borderStyle: 'dashed', borderColor: '#CCC8EB', backgroundColor: '#F3F2FC', borderRadius: 17, alignItems: 'center', justifyContent: 'center', gap: 9, padding: 16 },
  uploadIcon: { width: 42, height: 42, borderRadius: 14, backgroundColor: '#E4E1FC', alignItems: 'center', justifyContent: 'center', marginBottom: 3 },
  uploadArrow: { color: palette.accent, fontSize: 20, fontWeight: '600' },
  uploadTitle: { color: '#343240', fontSize: 14, fontWeight: '700' },
  uploadMeta: { color: '#85828F', fontSize: 10 },
  footer: { padding: 12, paddingHorizontal: 20, backgroundColor: '#FFF', borderTopWidth: 1, borderTopColor: palette.line },
  footnote: { textAlign: 'center', color: '#85838F', fontSize: 9, marginTop: 7 },
  fileRow: { flexDirection: 'row', alignItems: 'center', gap: 12, marginTop: 10, paddingVertical: 7 },
  fileName: { color: palette.ink, fontSize: 10, fontWeight: '700' },
  fileMeta: { color: '#85838F', fontSize: 9, marginTop: 3 },
  change: { color: palette.accent, fontSize: 9, fontWeight: '700', padding: 8 },
  error: { borderRadius: 10, backgroundColor: palette.coralSoft, padding: 10, marginBottom: 6 },
  errorTitle: { color: '#A64F42', fontSize: 9, fontWeight: '700' },
  errorBody: { color: '#8A665F', fontSize: 8, marginTop: 3 },
  hint: { color: '#797783', fontSize: 8, lineHeight: 12, marginBottom: 4 },
  explainer: { marginTop: 10 },
  or: { flexDirection: 'row', alignItems: 'center', gap: 10, marginVertical: 6 },
  rule: { flex: 1, height: 1, backgroundColor: palette.line },
  orText: { color: '#A3A0AD', fontSize: 8, letterSpacing: .8 },
  previewNote: { backgroundColor: '#FFF', borderRadius: 10, borderColor: palette.line, borderWidth: 1, padding: 10, marginTop: 16 },
  previewNoteText: { color: '#777582', fontSize: 9, lineHeight: 14, marginTop: 5 },
});
