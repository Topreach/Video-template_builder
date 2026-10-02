import { getAppDatabase } from '../../shared/storage/SqliteDatabase';
import { ProjectDraft, ProjectDraftRepository } from './types';

const ACTIVE_DRAFT_ID = 'active-project';

type DraftRow = { schema_version: number; payload_json: string };

export class SqliteProjectDraftRepository implements ProjectDraftRepository {
  private operationQueue: Promise<void> = Promise.resolve();

  async getActive(): Promise<ProjectDraft | null> {
    const database = await getAppDatabase();
    const row = await database.getFirstAsync<DraftRow>(
      'SELECT schema_version, payload_json FROM project_drafts WHERE id = ?',
      ACTIVE_DRAFT_ID,
    );
    if (!row) return null;
    if (row.schema_version !== 1) {
      throw new Error('This unfinished project uses a newer format and has been preserved. Update the app to continue.');
    }
    const draft: unknown = JSON.parse(row.payload_json);
    if (!isProjectDraft(draft)) {
      throw new Error('The unfinished project could not be read safely. Its saved data has been preserved.');
    }
    return draft;
  }

  save(draft: ProjectDraft): Promise<void> {
    if (!isProjectDraft(draft)) throw new Error('The unfinished project is incomplete and was not saved.');
    return this.enqueue(async () => {
      const database = await getAppDatabase();
      await database.runAsync(
        `INSERT INTO project_drafts (id, schema_version, updated_at, payload_json)
         VALUES (?, ?, ?, ?)
         ON CONFLICT(id) DO UPDATE SET
           schema_version = excluded.schema_version,
           updated_at = excluded.updated_at,
           payload_json = excluded.payload_json`,
        ACTIVE_DRAFT_ID,
        draft.schemaVersion,
        draft.updatedAt,
        JSON.stringify(draft),
      );
    });
  }

  deleteActive(): Promise<void> {
    return this.enqueue(async () => {
      const database = await getAppDatabase();
      await database.runAsync('DELETE FROM project_drafts WHERE id = ?', ACTIVE_DRAFT_ID);
    });
  }

  private enqueue(operation: () => Promise<void>): Promise<void> {
    const result = this.operationQueue.then(operation, operation);
    this.operationQueue = result.then(() => undefined, () => undefined);
    return result;
  }
}

export const projectDraftRepository: ProjectDraftRepository = new SqliteProjectDraftRepository();

function isProjectDraft(value: unknown): value is ProjectDraft {
  if (!value || typeof value !== 'object') return false;
  const draft = value as Partial<ProjectDraft>;
  const source = draft.sourceFacts;
  if (draft.schemaVersion !== 1
    || typeof draft.id !== 'string'
    || typeof draft.updatedAt !== 'string'
    || !['import', 'review', 'adapt'].includes(draft.stage ?? '')
    || !source
    || !Number.isFinite(source.durationSeconds)
    || source.durationSeconds <= 0
    || source.durationSeconds > 30
    || !Number.isInteger(source.width)
    || source.width <= 0
    || !Number.isInteger(source.height)
    || source.height <= 0
    || (source.fileSizeBytes !== undefined && (!Number.isFinite(source.fileSizeBytes) || source.fileSizeBytes < 0))
    || !Array.isArray(draft.sections)
    || draft.sections.length === 0
    || !draft.decisions
    || typeof draft.decisions !== 'object') return false;

  const ids = new Set<string>();
  return draft.sections.every((section) => {
    if (!section || typeof section.id !== 'string' || !section.id || ids.has(section.id)
      || !Number.isFinite(section.startSeconds) || section.startSeconds < 0
      || !Number.isFinite(section.endSeconds) || section.endSeconds <= section.startSeconds
      || section.endSeconds > source.durationSeconds) return false;
    ids.add(section.id);
    const decision = draft.decisions?.[section.id];
    return decision === undefined || ['edit', 'keep', 'exclude'].includes(decision);
  });
}
