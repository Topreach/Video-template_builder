import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useEvent } from 'expo';
import { useVideoPlayer, VideoView } from 'expo-video';
import { palette } from '../../shared/theme';

type Props = {
  uri: string;
  durationSeconds: number;
  onTimeChange: (seconds: number) => void;
};

export function ReviewVideoPlayer({ uri, durationSeconds, onTimeChange }: Props) {
  const player = useVideoPlayer(uri, (instance) => {
    instance.loop = false;
    instance.timeUpdateEventInterval = 0.1;
  });
  const timeUpdate = useEvent(player, 'timeUpdate', {
    currentTime: 0,
    currentLiveTimestamp: null,
    currentOffsetFromLive: null,
    bufferedPosition: 0,
  });
  const playing = useEvent(player, 'playingChange', { isPlaying: player.playing });
  const [trackWidth, setTrackWidth] = useState(1);
  const currentTime = Math.min(durationSeconds, Math.max(0, timeUpdate?.currentTime ?? 0));

  useEffect(() => onTimeChange(currentTime), [currentTime, onTimeChange]);

  const seekTo = (seconds: number) => {
    const bounded = Math.min(Math.max(seconds, 0), durationSeconds);
    player.pause();
    // expo-video documents currentTime as its cross-platform seek setter.
    // eslint-disable-next-line react-hooks/immutability
    player.currentTime = bounded;
    onTimeChange(bounded);
  };

  const seekFromTouch = (localX: number) => seekTo((localX / trackWidth) * durationSeconds);

  return <View style={styles.card}>
    <View style={styles.videoFrame}>
      <VideoView player={player} style={styles.video} nativeControls={false} contentFit="contain" />
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={playing.isPlaying ? 'Pause video' : 'Play video'}
        onPress={() => playing.isPlaying ? player.pause() : player.play()}
        style={styles.playButton}>
        <Text style={styles.playText}>{playing.isPlaying ? 'Pause' : 'Play'}</Text>
      </Pressable>
    </View>
    <View style={styles.transport}>
      <Text style={styles.time}>{formatTime(currentTime)}</Text>
      <View
        onLayout={(event) => setTrackWidth(Math.max(event.nativeEvent.layout.width, 1))}
        onTouchStart={(event) => seekFromTouch(event.nativeEvent.locationX)}
        onTouchMove={(event) => seekFromTouch(event.nativeEvent.locationX)}
        accessibilityRole="adjustable"
        accessibilityLabel="Seek through the selected video"
        accessibilityActions={[{ name: 'decrement', label: 'Seek backward 0.1 seconds' }, { name: 'increment', label: 'Seek forward 0.1 seconds' }]}
        onAccessibilityAction={(event) => seekTo(currentTime + (event.nativeEvent.actionName === 'increment' ? 0.1 : -0.1))}
        accessibilityValue={{ min: 0, max: durationSeconds, now: currentTime, text: `${currentTime.toFixed(1)} seconds` }}
        style={styles.seekHitArea}>
        <View style={styles.seekTrack}>
          <View style={[styles.seekProgress, { width: `${durationSeconds ? currentTime / durationSeconds * 100 : 0}%` }]} />
          <View style={[styles.seekThumb, { left: `${durationSeconds ? currentTime / durationSeconds * 100 : 0}%` }]} />
        </View>
      </View>
      <Text style={styles.time}>{formatTime(durationSeconds)}</Text>
    </View>
    <View style={styles.seekActions}>
      <Pressable onPress={() => seekTo(currentTime - 0.1)} accessibilityRole="button" accessibilityLabel="Back 0.1 seconds" style={styles.nudge}><Text style={styles.nudgeText}>−0.1s</Text></Pressable>
      <Text style={styles.seekHint}>Scrub to a moment, then split</Text>
      <Pressable onPress={() => seekTo(currentTime + 0.1)} accessibilityRole="button" accessibilityLabel="Forward 0.1 seconds" style={styles.nudge}><Text style={styles.nudgeText}>+0.1s</Text></Pressable>
    </View>
  </View>;
}

function formatTime(seconds: number): string {
  const safe = Math.max(0, seconds);
  const minutes = Math.floor(safe / 60);
  return `${minutes}:${(safe - minutes * 60).toFixed(1).padStart(4, '0')}`;
}

const styles = StyleSheet.create({
  card: { marginTop: 12, padding: 10, borderRadius: 13, backgroundColor: '#FFF', borderWidth: 1, borderColor: palette.line },
  videoFrame: { height: 195, borderRadius: 10, overflow: 'hidden', backgroundColor: '#211F29', justifyContent: 'center', alignItems: 'center' },
  video: { width: '100%', height: '100%' },
  playButton: { position: 'absolute', minWidth: 66, minHeight: 40, paddingHorizontal: 13, borderRadius: 20, backgroundColor: '#211F29C9', alignItems: 'center', justifyContent: 'center' },
  playText: { color: '#FFF', fontSize: 11, fontWeight: '700' },
  transport: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 12 },
  time: { minWidth: 39, color: palette.ink, fontSize: 9, fontVariant: ['tabular-nums'] },
  seekHitArea: { flex: 1, minHeight: 34, justifyContent: 'center' },
  seekTrack: { height: 5, borderRadius: 3, backgroundColor: '#E6E4ED', justifyContent: 'center' },
  seekProgress: { position: 'absolute', left: 0, height: 5, borderRadius: 3, backgroundColor: palette.accent },
  seekThumb: { position: 'absolute', width: 13, height: 13, marginLeft: -6.5, borderRadius: 7, backgroundColor: palette.accent, borderWidth: 2, borderColor: '#FFF' },
  seekActions: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8 },
  nudge: { minWidth: 44, minHeight: 32, alignItems: 'center', justifyContent: 'center', borderRadius: 8, backgroundColor: '#F1EFFB' },
  nudgeText: { color: palette.accent, fontSize: 9, fontWeight: '700' },
  seekHint: { color: '#85828F', fontSize: 8 },
});
