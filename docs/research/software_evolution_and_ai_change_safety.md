# Software Evolution and AI Change-Safety Plan

**Status:** Required architecture constraint for future implementation. Framework remains undecided.  
**Goal:** Add, upgrade, or replace one identifiable part of the application with minimal risk to unrelated features and existing user projects.

## 1. Architecture direction

Start as a **modular monolith**, not a collection of microservices. Organize code around user-visible capabilities and stable domain contracts. Split a feature into a separately deployed service or package only when deployment, scale, ownership, or platform constraints justify the additional operational burden.

This balances upgrade isolation with the cost of maintaining modules. Android's architecture guidance recommends high cohesion, low coupling, minimal public interfaces, and warns against both over-fragmentation and overly broad modules. [Android modularization guide](https://developer.android.com/topic/modularization), [module patterns](https://developer.android.com/topic/modularization/patterns).

## 2. Proposed capability map

Keep these as named feature boundaries even if the selected framework initially represents some boundaries as folders/packages rather than independently compiled modules:

| Feature ID | Responsibility | Depends on shared contracts |
|---|---|---|
| `discover` | Curated recipe browsing/search/details. | `TemplateRecipe`, catalog API |
| `import` | Select media, probe metadata, validate inputs, manage temporary source. | media asset, permissions, storage adapter |
| `analysis` | Submit/run analysis and return candidate sections/evidence. | `AnalysisProposal`, processing adapter |
| `section-review` | Edit/keep/exclude, split/merge/reorder/trim and confirm sections. | `AnalysisProposal`, `TemplateRecipe` |
| `recipe-editor` | Edit slots, text, audio, visual operations and recipe metadata. | `TemplateRecipe`, capability registry |
| `template-library` | Drafts, saved versions, duplicate/archive/delete. | recipe repository, local/cloud storage adapter |
| `render-preview` | Preview a supported recipe/edit session. | renderer interface, recipe contract |
| `export` | Render, cancel/retry, save and share MP4. | renderer interface, output profile |
| `account` | Identity, optional sync entitlement, session lifecycle. | auth provider interface |
| `settings-privacy` | Preferences, permission status, retention and deletion. | settings/privacy contracts |
| `notifications` | Opt-in operational/user notifications. | notification adapter, preference contract |
| `billing` (later) | Entitlements and store transactions. | entitlement interface, provider adapters |

Shared capabilities should be few and explicit: design system, navigation shell, media contracts, recipe schema, storage/repository interfaces, logging/redaction, feature flags, and platform adapters. A shared module must not become a dumping ground for unrelated helpers.

## 3. Dependency rules

- Feature UI depends on its feature application logic and public contracts; features do not import each other's internal files.
- Domain types and contracts must not depend on UI widgets, database tables, vendors, or a native renderer.
- Platform services (photo library, renderer, notifications, secure storage, billing) sit behind narrow interfaces. Platform-specific code implements those interfaces.
- Rendering engine details must not leak into `TemplateRecipe`; the recipe describes intent, supported operations, and profile-specific composition.
- `analysis` proposes findings; `section-review` records user decisions. Model output must never be treated as an approved recipe implicitly.
- `export` consumes an immutable render snapshot. Edits made after export starts create a new snapshot/job rather than mutating the in-progress output.
- Enforce dependency direction with static checks/lint rules where the selected toolchain supports them.

## 4. Upgrade and compatibility strategy

### Every persisted or exchanged contract

- Give recipes, analysis proposals, output profiles, local database records, backend APIs, and render jobs explicit schema/API versions.
- Include an app-generated stable ID, `schemaVersion`, creation/update timestamps, and provenance where applicable.
- Keep a registry of migrations from each supported old version to the current version. Migrations must be deterministic and must preserve user-confirmed edits and provenance.
- Preserve the original data until a migration succeeds; keep backups or a recoverable copy for destructive transformations.
- For API and database changes, prefer **expand → migrate → contract**: add compatible fields/path, migrate consumers/data, then remove old behavior only after compatibility is confirmed. [Parallel Change / Expand-Contract](https://martinfowler.com/bliki/ParallelChange.html)
- Refuse unknown future schema versions safely: retain the project and explain that this app version cannot edit it, rather than overwriting or “repairing” it silently.
- Version output profiles independently of recipes so platform guidance can update without rewriting every saved template.
- Track renderer capabilities explicitly. Unsupported effects must be flagged before render, never dropped silently.

### Feature releases

- Assign each independently upgradeable feature a stable ID, owner/responsible area, dependencies, data contracts, flags, and migration notes in a feature registry.
- Isolate optional features behind a capability/feature flag; a disabled or unavailable feature should not prevent app startup or access to unrelated saved templates.
- Roll out risky server-backed changes gradually and retain a rollback path. For client-only features, keep old saved recipes readable and provide a controlled migration.
- Keep third-party and native dependency versions centralized; audit version changes because duplicated native modules can break mobile builds. Expo's documentation specifically highlights duplicate native dependencies as a monorepo risk. [Expo monorepo guide](https://docs.expo.dev/guides/monorepos/), [Expo autolinking](https://docs.expo.dev/modules/autolinking/)

## 5. AI-assisted change protocol

Any AI or developer task that changes implementation must follow this sequence:

1. **Identify:** Name the feature ID and desired behavior. Locate its implementation, public contracts, dependencies, and related requirements before editing.
2. **Bound:** State which files/modules should change and which contracts could be affected. Avoid broad rewrites for a local feature request.
3. **Plan migration:** If persisted data, API contracts, renderer semantics, or permissions change, write the migration/compatibility plan before code.
4. **Make a small change:** Keep the patch narrow and reviewable. Do not remove unrelated code, change generated files by hand, or reformat the whole repository as a side effect.
5. **Verify impact:** Run the checks required by the project for the touched modules and affected integration boundaries; inspect the diff for unrelated edits. Do not claim verification that was not run.
6. **Record:** Update the feature registry, decision record, changelog, schema version/migration notes, and user-facing docs as applicable.
7. **Recover:** Keep a clean source-control checkpoint before the change; revert only the scoped patch if verification fails. Never use a destructive reset/cleanup to make a failed task appear clean.

For AI-generated changes, require a human-readable summary: behavior changed, files/feature IDs touched, data compatibility impact, checks run and results, known limitations, and rollback/recovery step. If the AI cannot determine impact confidently, it must stop before broad edits and report the uncertainty.

## 6. Required repository artifacts before production app code

- `docs/architecture/feature-map.md` — feature IDs, responsibilities, ownership, dependencies, data touched, rollout and recovery.
- `docs/architecture/decisions/` — short dated decision records for stack, storage, rendering, auth, and major schema changes; include context, alternatives, evidence, decision, consequences, and revisit trigger.
- `docs/architecture/contracts/` — schemas and compatibility rules for recipes, analysis, output profiles, and render jobs.
- A migration registry and representative fixtures for every persisted schema version.
- A `CHANGELOG.md` organized by user-facing area and migration impact.
- Repository-level contributor/AI instructions that require scoped changes, diff inspection, and truthful verification reporting.
- Automated checks in CI for type/lint/build, contract/schema compatibility, migrations, and feature integrations. Define them when the framework is chosen; they complement—not replace—review and runtime checks.

### Current workspace note

The workspace was not recognized as a Git repository during this research session. Establish a source-control baseline and verify recovery procedures before production implementation. Without version history, a narrow patch is harder to review and safely roll back.

## 7. Modularity without overengineering

- Start with feature-oriented folders and strict import boundaries in a single app/backend deployment.
- Extract a separately compiled module only if there is a clear reason: platform-specific implementation, independent release/update, reuse, build-time improvement, or ownership boundary.
- Do not create one module per screen or one microservice per feature.
- Keep media analysis as a separable adapter because it may move on-device/server-side; do not split it into a production service until privacy/cost/latency evidence supports that choice.
- Keep the renderer behind a stable interface so native or server rendering can change without redesigning templates or the UI.

## 8. Acceptance bar for safe upgrades

A feature upgrade is ready when:

- Its scope and affected feature IDs are listed.
- Public contracts remain compatible or have a reviewed migration path.
- Existing project fixtures remain readable and user choices/provenance survive conversion.
- Unsupported renderer/API capability produces an explicit, recoverable state.
- The affected feature and its integration boundaries pass the agreed checks.
- The patch contains no unrelated changes and has an identified rollback path.
- Release notes state any visible behavior, permission, storage, or compatibility change.

## 9. Sources and limits

The Android modularization and Expo package guidance informs general boundary and dependency recommendations; these patterns must be adapted to the selected stack. Expand-contract is a general migration pattern, not a specific database commitment. No framework, backend, database, CI provider, feature-flag service, or rollout vendor is selected by this document.
