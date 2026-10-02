export type EditableSectionSpan = {
  id: string;
  startSeconds: number;
  endSeconds: number;
};

export function sectionDuration(section: EditableSectionSpan): number {
  return Math.max(0, section.endSeconds - section.startSeconds);
}
