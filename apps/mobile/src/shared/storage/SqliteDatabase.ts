import * as SQLite from 'expo-sqlite';

const DATABASE_NAME = 'video-templates.db';
const DATABASE_SCHEMA_VERSION = 2;

let databasePromise: Promise<SQLite.SQLiteDatabase> | null = null;

export async function getAppDatabase(): Promise<SQLite.SQLiteDatabase> {
  if (!databasePromise) databasePromise = initializeDatabase();
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
    throw new Error('This app version cannot open the saved project library. Update the app and try again.');
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

  if (currentVersion < 2) {
    await database.execAsync(`
      CREATE TABLE IF NOT EXISTS project_drafts (
        id TEXT PRIMARY KEY NOT NULL,
        schema_version INTEGER NOT NULL,
        updated_at TEXT NOT NULL,
        payload_json TEXT NOT NULL
      );
      PRAGMA user_version = 2;
    `);
  }
  return database;
}
