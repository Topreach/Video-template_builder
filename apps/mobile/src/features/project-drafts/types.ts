import { EditableSectionSpan } from '../section-review/types';
import { SectionDecision } from '../../shared/sampleData';

export type DraftSourceFacts = {
  durationSeconds: number;
  width: number;
  height: number;
  fileSizeBytes?: number;
};

export type ProjectDraft = {
  id: string;
  schemaVersion: 1;
  updatedAt: string;
  stage: 'import' | 'review' | 'adapt';
  sourceFacts: DraftSourceFacts;
  sections: EditableSectionSpan[];
  decisions: Record<string, SectionDecision>;
};

export interface ProjectDraftRepository {
  getActive(): Promise<ProjectDraft | null>;
  save(draft: ProjectDraft): Promise<void>;
  deleteActive(): Promise<void>;
}
