import { useEffect, useRef } from 'react';
import { StyleSheet, View } from 'react-native';
import { useEvent } from 'expo';
import { useVideoPlayer, VideoView } from 'expo-video';

export function SelectedVideoPreview({ uri, onDuration }: { uri: string; onDuration: (duration: number) => void }) {
  const player = useVideoPlayer(uri, (instance) => { instance.loop = true; });
  const sourceLoad = useEvent(player, 'sourceLoad');
  const onDurationRef = useRef(onDuration);
  useEffect(() => {
    onDurationRef.current = onDuration;
  }, [onDuration]);
  useEffect(() => {
    const duration = sourceLoad?.duration;
    if (typeof duration === 'number' && Number.isFinite(duration) && duration > 0) onDurationRef.current(duration);
  }, [sourceLoad?.duration]);

  return <View style={styles.frame}><VideoView player={player} style={styles.video} nativeControls contentFit="contain" /></View>;
}

const styles = StyleSheet.create({
  frame: { height: 218, borderRadius: 15, overflow: 'hidden', backgroundColor: '#211F29', marginTop: 18 },
  video: { width: '100%', height: '100%' },
});
