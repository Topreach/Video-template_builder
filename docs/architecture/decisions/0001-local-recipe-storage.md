# ADR 0001: Local Recipe Storage in the Expo Candidate

**Status:** Accepted for the current Expo mobile implementation; reversible if the mobile framework changes.  
**Date:** 3 October 2026  
**Decision owner:** Product/engineering  
**Related requirements:** SAV-001, PRIV-001, SEC-001, COMP-001; DEC-006 and DEC-015.

## Context

The MVP needs private templates that survive app restarts and can be listed, reopened, duplicated, renamed, and deleted. The current mobile candidate uses Expo SDK 57 and React Native. No backend or account is required for this local capability. Template data is structured and will need explicit schema versions and migrations as the renderer and recipe format evolve.

The imported reference video must not be kept merely to save a reusable template. The saved recipe stores timing, user decisions, prompts, and provenance metadata; it does not embed the video or retain its temporary picker URI. If a future operation needs source footage again, the app must request it explicitly and verify its availability.

## Decision

- Use `expo-sqlite` for local recipe metadata and one recoverable project draft in the Expo candidate.
- Access database operations only through feature-owned `RecipeRepository` and `ProjectDraftRepository` interfaces. Screens and domain models must not import SQLite or query tables directly.
- Store a versioned recipe payload and a small indexed library summary in one SQLite row per template. Use bound parameters for all user-supplied values.
- Use SQLite `PRAGMA user_version` for database migrations and a separate recipe schema version for saved payloads. Migrations must be additive or explicitly transform old rows; an unsupported future recipe version must be preserved and shown as unavailable, never overwritten or deleted automatically.
- Database schema v2 adds `project_drafts` while preserving the v1 `recipes` table. Draft payload schema v1 stores only technical source facts, workflow stage, section ranges, and user decisions. It excludes the picker URI and media bytes; resumption asks the user to reselect the source.
- Keep user media in app-managed media storage only when a defined feature needs a local copy. Do not store video bytes, picker URIs, credentials, transcripts, or extracted frames in the recipe database.
- Treat recipes as private local data. Use OS app sandbox/device protection, and keep backup inclusion, database encryption, source-media retention, and account/cloud sync as separate reviewed decisions; this ADR does not claim SQLite file-level encryption.

Expo SDK 57 documentation states that `expo-sqlite` persists its database across app restarts, exposes parameterized CRUD operations, and supports schema migration using `PRAGMA user_version`. [Expo SQLite SDK 57](https://docs.expo.dev/versions/v57.0.0/sdk/sqlite/)

## Alternatives considered

| Option | Decision |
|---|---|
| In-memory state | Rejected for saved recipes; it disappears when the process exits. |
| Plain key-value storage | Rejected for the recipe library; queries, updates, versioned migration, and atomic deletion are clearer with a database. It remains suitable for simple preferences if needed. |
| JSON files per recipe | Possible, but requires custom indexing, transactional updates, and corruption/recovery handling. Not selected for this candidate. |
| Cloud database | Deferred; not required for private local templates and would add identity, upload, hosting, retention, and deletion obligations. |
| Different mobile framework/store | Still possible if later framework/render evidence justifies a pivot; the repository interface isolates this choice. |

## Consequences and safeguards

- Add `expo-sqlite` as an SDK-compatible dependency and require a development build for native-device validation where the current runtime does not include the module.
- Add explicit database initialization and migration code before library operations. A database-init failure must leave recipes and drafts untouched and show a recoverable error.
- Keep save/update/delete operations behind a repository contract and refresh the library from that repository after each mutation.
- Do not use `execAsync` for dynamic user values; use `runAsync` with bound parameters.
- Preserve `created_at` during edits; update `updated_at`; duplicate creates a new ID and independent payload.
- Test create/list/reopen/update/duplicate/delete, interruption, first-launch upgrade/migration, and unsupported-future-schema behavior on iOS and Android before production release.
- Keep the app's actual source media out of fixtures, database snapshots, and Git.

## Revisit when

- The product selects a non-Expo framework or a cloud-first/sync architecture.
- Local database encryption or backup requirements are established by DEC-001/015 legal, threat, or platform review.
- Measured performance, migration, or recovery evidence shows SQLite is not suitable.
