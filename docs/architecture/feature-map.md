# Feature Map

**Status:** Initial product-level boundaries; implementation packages and ownership depend on the selected stack.  
**Rule:** Keep responsibilities and contracts identifiable. Do not make every row a separate service or compiled module by default.

Track requirements and acceptance evidence in the [MVP coverage and traceability map](../product/mvp_coverage_and_traceability.md); this feature map assigns implementation ownership and dependency boundaries.

| Feature ID | User capability | Main dependency/contracts | Initial release |
|---|---|---|---|
| `discover` | Browse/search curated examples and recipes. | `TemplateRecipe`, catalog repository | Small curated set; optional after core loop proves value |
| `import` | Select and validate a local video; preview technical facts. | Media asset, permission/storage adapter | Yes |
| `analysis` | Build a time-aligned component inventory across shots, visual content, text, audio, creative-beat hypotheses, and source integrity; report coverage and uncertainty. | Versioned `AnalysisProposal`; local/server signal adapters | Yes; complete coverage is the product goal; manual fallback required |
| `section-review` | Review, split at a playhead or exact time, and edit/keep/exclude moments. | `AnalysisProposal` in, user-approved `TemplateRecipe` out | Yes; product differentiator |
| `recipe-editor` | Edit reusable media slots, text, audio, and supported visual operations. | Versioned `TemplateRecipe`, capability registry | Yes; constrained operations |
| `template-library` | Save, reopen, duplicate, revise, and delete private recipes. | Recipe repository and migrations | Yes |
| `render-preview` | Preview a chosen recipe/profile and flag unsupported operations. | Renderer interface, profile, immutable edit snapshot | Yes |
| `export` | Render, cancel/retry, save and share MP4. | Render job contract and renderer adapter | Yes |
| `account` | Optional sign-in, recovery, sync entitlement, sessions. | Auth-provider interface | Only if selected cloud features require it |
| `settings-privacy` | Profile preferences, privacy, retention, accessibility, help. | Settings and deletion contracts | Essential settings; profile is optional |
| `notifications` | Opt-in remote-render status or future update notices. | Notification adapter and user preferences | In-app status first; push only if needed and consented |
| `billing` | Store entitlements, purchase restore, subscription management. | Store/billing adapter and entitlement contract | Deferred; no launch paywall |
| `finishing-studio` | Add extra clips/audio/text after applying a recipe. | Timeline/edit-session schema and renderer | Deferred pending evidence |

## Boundary rules

- `analysis` cannot write user decisions directly; `section-review` converts chosen actions into the recipe.
- `recipe-editor` owns recipe editing; `template-library` owns persistence/version history.
- `render-preview` and `export` share a renderer capability contract so preview does not promise effects export cannot produce.
- `account`, `billing`, and `notifications` are optional integration areas; failure in one must not corrupt local drafts.
- `finishing-studio` must not expand the template recipe into a general editor until the separate roadmap decision is approved.
- Shared contracts have a named owner, schema version, compatibility policy, and migration entry when applicable.

## Implementation structure

Begin with feature-oriented packages/folders and explicit public interfaces in a modular monolith. Create separate deployables or compiled modules only when a measured platform, deployment, ownership, or reuse need justifies their overhead. See [software evolution and AI change-safety plan](../research/software_evolution_and_ai_change_safety.md).

## Current mobile implementation status

The isolated Expo candidate is in [`apps/mobile`](../../apps/mobile/README.md). Current state:

- `discover`: screen and sample recipe cards.
- `import`: iOS/Android library picker, local playback, and a source-duration gate at 30 seconds.
- `analysis`: a local Python CLI prototype proposes adaptive visual shot boundaries and ordered spans through schema-v2 `AnalysisProposal`; it explicitly reports the inventory as partial and lists unimplemented signal categories. It is not connected to the mobile app and has no calibrated confidence. See [ADR 0003](decisions/0003-experimental-local-shot-analysis.md).
- `project-drafts`: one active, versioned local draft persists source technical facts, manual section ranges, decisions, and workflow stage; media bytes and picker URIs are excluded. Resume requires source reselection.
- `section-review`: Local playback focused on a selected moment, timeline seeking, local generated frame previews for up to 16 moments, exact-time or playhead splitting, and explicit Edit/Keep/Exclude choices over the selected clip; choices autosave to the active draft. Automatic analysis is not connected.
- `recipe-editor`: suggestion and template-preview UI using sample data.
- `template-library`: local recipe metadata persists through `RecipeRepository` backed by Expo SQLite; the source video is not copied into recipe rows. Database schema v2 adds the project-draft table.
- `export`, backend analysis, accounts, notification delivery, and billing are not connected.

The Expo project is a reversible UI candidate, not a final framework or rendering decision. The Python analysis package and its closed technical contracts were not modified by the mobile spike.
