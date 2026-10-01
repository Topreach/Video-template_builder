export type ScreenName = 'discover' | 'import' | 'review' | 'adapt' | 'template-preview' | 'library' | 'profile';
export type SectionDecision = 'edit' | 'keep' | 'exclude';

export type SampleSection = {
  id: string;
  label: string;
  role: string;
  description: string;
  start: number;
  end: number;
  duration: number;
  certainty: 'clear' | 'check';
  color: string;
};

// Demonstration data only; these values are not returned by a video analyzer.
export const sampleSections: SampleSection[] = [
  { id: 'hook', label: 'The hook', role: 'OPENING', description: 'Close-up, then a quick look to camera.', start: 0, end: 3, duration: 3, certainty: 'clear', color: '#DFA798' },
  { id: 'setup', label: 'The setup', role: 'BUILD', description: 'Builds anticipation before the reveal.', start: 3, end: 8, duration: 5, certainty: 'check', color: '#87ADB9' },
  { id: 'reveal', label: 'The reveal', role: 'PAYOFF', description: 'The main reaction. Keep the timing, change the scene.', start: 8, end: 13, duration: 5, certainty: 'clear', color: '#D39C69' },
  { id: 'outro', label: 'Attached outro', role: 'ENDING CARD', description: 'Looks like an ending card from the original post.', start: 13, end: 17, duration: 4, certainty: 'check', color: '#AAA8B3' },
];

export const timecode = (seconds: number) => `0:${String(seconds).padStart(2, '0')}`;
