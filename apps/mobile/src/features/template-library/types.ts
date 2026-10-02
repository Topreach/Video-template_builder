import { EditableSectionSpan } from '../section-review/types';

export type SavedSectionDecision = 'edit' | 'keep' | 'exclude';

export type TemplateRecipe = {
  id: string;
  schemaVersion: 1;
  title: string;
  createdAt: string;
  updatedAt: string;
  sourceDurationSeconds: number;
  aspectRatio: '9:16';
  sections: Array<EditableSectionSpan & {
    order: number;
    decision: SavedSectionDecision;
  }>;
};

export type TemplateSummary = {
  id: string;
  schemaVersion: number;
  title: string;
  sectionCount: number;
  runtimeSeconds: number;
  updatedAt: string;
};

export interface RecipeRepository {
  list(): Promise<TemplateSummary[]>;
  get(id: string): Promise<TemplateRecipe | null>;
  save(recipe: TemplateRecipe): Promise<void>;
  delete(id: string): Promise<void>;
}
