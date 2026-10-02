import * as SQLite from 'expo-sqlite';
import { RecipeRepository, TemplateRecipe, TemplateSummary } from './types';

const DATABASE_NAME = 'video-templates.db';
const DATABASE_SCHEMA_VERSION = 1;
const RECIPE_SCHEMA_VERSION = 1;

type RecipeRow = {
  id: string;
  schema_version: number;
  title: string;
  section_count: number;
  runtime_seconds: number;
  updated_at: string;
  payload_json: string;
};

let databasePromise: Promise<SQLite.SQLiteDatabase> | null = null;

async function getDatabase(): Promise<SQLite.SQLiteDatabase> {
  if (!databasePromise) {
    databasePromise = initializeDatabase();
  }
  try {
    return await databasePromise;
  } catch (error) {
    databasePromise = null;
    throw error;
  }
}

async function initializeDatabase(): Promise<SQLite.SQLiteDatabase> {
  const database = await SQLite.openDatabaseAsync(DATABASE_NAME);
  await database.execAsync('PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON;');
  const versionRow = await database.getFirstAsync<{ user_version: number }>('PRAGMA user_version');
  const currentVersion = versionRow?.user_version ?? 0;

  if (currentVersion > DATABASE_SCHEMA_VERSION) {
    throw new Error('This app version cannot open the saved template library. Update the app and try again.');
  }

  if (currentVersion < 1) {
    await database.execAsync(`
      CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY NOT NULL,
        schema_version INTEGER NOT NULL,
        title TEXT NOT NULL,
        section_count INTEGER NOT NULL,
        runtime_seconds REAL NOT NULL,
        updated_at TEXT NOT NULL,
        payload_json TEXT NOT NULL
      );
      CREATE INDEX IF NOT EXISTS recipes_updated_at ON recipes(updated_at DESC);
      PRAGMA user_version = 1;
    `);
  }
  return database;
}

export class SqliteRecipeRepository implements RecipeRepository {
  async list(): Promise<TemplateSummary[]> {
    const database = await getDatabase();
    const rows = await database.getAllAsync<RecipeRow>(
      'SELECT id, schema_version, title, section_count, runtime_seconds, updated_at, payload_json FROM recipes ORDER BY updated_at DESC',
    );
    return rows.map((row) => ({
      id: row.id,
      schemaVersion: row.schema_version,
      title: row.title,
      sectionCount: row.section_count,
      runtimeSeconds: row.runtime_seconds,
      updatedAt: row.updated_at,
    }));
  }

  async get(id: string): Promise<TemplateRecipe | null> {
    const database = await getDatabase();
    const row = await database.getFirstAsync<Pick<RecipeRow, 'schema_version' | 'payload_json'>>(
      'SELECT schema_version, payload_json FROM recipes WHERE id = ?',
      id,
    );
    if (!row) return null;
    if (row.schema_version > RECIPE_SCHEMA_VERSION) {
      throw new Error('This template was saved by a newer app version. Its data is still safe; update the app to open it.');
    }
    if (row.schema_version !== RECIPE_SCHEMA_VERSION) {
      throw new Error('This template version cannot be opened safely. Its saved data has been preserved.');
    }
    const recipe: unknown = JSON.parse(row.payload_json);
    if (!isTemplateRecipe(recipe) || recipe.schemaVersion !== row.schema_version) {
      throw new Error('This template data could not be read safely. The saved copy has been preserved.');
    }
    return recipe;
  }

  async save(recipe: TemplateRecipe): Promise<void> {
    if (!isTemplateRecipe(recipe)) throw new Error('The template is incomplete and was not saved.');
    const database = await getDatabase();
    const included = recipe.sections.filter((section) => section.decision !== 'exclude');
    const runtimeSeconds = included.reduce((sum, section) => sum + (section.endSeconds - section.startSeconds), 0);
    await database.runAsync(
      `INSERT INTO recipes (id, schema_version, title, section_count, runtime_seconds, updated_at, payload_json)
       VALUES (?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET
         schema_version = excluded.schema_version,
         title = excluded.title,
         section_count = excluded.section_count,
         runtime_seconds = excluded.runtime_seconds,
         updated_at = excluded.updated_at,
         payload_json = excluded.payload_json`,
      recipe.id,
      recipe.schemaVersion,
      recipe.title,
      included.length,
      runtimeSeconds,
      recipe.updatedAt,
      JSON.stringify(recipe),
    );
  }

  async delete(id: string): Promise<void> {
    const database = await getDatabase();
    await database.runAsync('DELETE FROM recipes WHERE id = ?', id);
  }
}

export const recipeRepository: RecipeRepository = new SqliteRecipeRepository();

function isTemplateRecipe(value: unknown): value is TemplateRecipe {
  if (!value || typeof value !== 'object') return false;
  const recipe = value as Partial<TemplateRecipe>;
  return recipe.schemaVersion === RECIPE_SCHEMA_VERSION
    && typeof recipe.id === 'string'
    && typeof recipe.title === 'string'
    && recipe.title.trim().length > 0
    && typeof recipe.createdAt === 'string'
    && typeof recipe.updatedAt === 'string'
    && typeof recipe.sourceDurationSeconds === 'number'
    && Number.isFinite(recipe.sourceDurationSeconds)
    && recipe.sourceDurationSeconds > 0
    && recipe.sourceDurationSeconds <= 30
    && recipe.aspectRatio === '9:16'
    && Array.isArray(recipe.sections)
    && recipe.sections.length > 0
    && new Set(recipe.sections.map((section) => section.id)).size === recipe.sections.length
    && new Set(recipe.sections.map((section) => section.order)).size === recipe.sections.length
    && recipe.sections.every((section) => section
      && typeof section.id === 'string'
      && section.id.length > 0
      && typeof section.order === 'number'
      && typeof section.startSeconds === 'number'
      && typeof section.endSeconds === 'number'
      && section.startSeconds >= 0
      && section.endSeconds > section.startSeconds
      && section.endSeconds <= 30
      && section.endSeconds <= recipe.sourceDurationSeconds!
      && ['edit', 'keep', 'exclude'].includes(section.decision));
}
