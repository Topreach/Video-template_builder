# Mobile MVP Implementation Cross-check

**Reviewed:** 3 October 2026  
**Scope:** Static source review of `apps/mobile` against the MVP traceability map and mobile UI specification. This is a code-level cross-check, not an iOS/Android device acceptance run.

## Status meanings

- **Connected:** The described action is wired to real local behavior.
- **Partial:** Some behavior works, but an important acceptance requirement is missing.
- **Sample / nonfunctional:** The UI is illustrative, static, or its action does not complete the described task.
- **Not built:** No implementation is present.

## End-to-end journey check

| Journey step / requirement | Status | What currently works | Gap that users will notice |
|---|---|---|---|
| Open app and choose a path (`NAV-001`) | Partial | Discover, Create, My Templates, and Profile navigation render. | “Start with an idea” opens My Templates. It does not open a usable inspiration catalog. |
| Browse inspiration (`DISC-001`) | Sample / nonfunctional | Two static example cards render. | Cards do not contain playable examples or recipe details. Tapping them opens the saved-template library; it does not apply a recipe. Category chips do not filter. |
| Import a reference (`IMP-001`) | Partial | System video picker, selected-video playback, metadata display, and 30-second duration gate are connected. | No rights/processing declaration, durable source-media copy, or supported-format/size validation flow. A missing duration blocks continuation without a clear metadata-retry path. |
| Analyze and review moments (`ANA-001`, `ANA-002`, `SREV-001`, `SEC-002`) | Partial | The mobile app starts with one manual span; the user can seek through playback, inspect locally generated thumbnails for up to 16 moments, split at the playhead or an entered time, choose Edit / Keep / Exclude, and see included timing. A separate experimental Python CLI proposes local visual-cut ranges in a versioned contract. | The detector is not calibrated and is not connected to mobile. No trim handles, merge, reorder, rename, undo, or detected-boundary navigation. A visual cut is not a story section. Preview is the whole clip rather than following the selected moment. |
| Get replacement ideas (`REP-001`, `REP-002`) | Sample / nonfunctional | One hard-coded “reveal” idea can be visually selected. | It is unrelated to detected/user section roles, selection is not saved, and there are no category-specific alternatives, rationale data, or request-another/edit/skip behavior. |
| Add replacement media / edit sound or text (`FILL-001`, `TXT-001`, `AUD-001`, `VIS-001`) | Not built | UI examples show where these controls might appear. | “My video or photo” and replacement sound show later-feature alerts. Caption is static text; mute only changes a local switch. Nothing is attached to a template or persisted. |
| Preview a template (`PRE-001`) | Partial | Actual section timings and decisions are shown in a structure-only preview, with an explicit note that it is not rendered. | No reference/structure/your-version player, no footage replacement, audio/text layers, crop, output profiles, or rights summary. |
| Save and manage a recipe (`SAV-001`) | Connected for metadata | SQLite stores a versioned recipe; list/open, rename, duplicate, delete, and one local recoverable manual draft are implemented. | A saved recipe is a timing/decision map, not yet a usable remix template: it has no replacement prompts/media slots, filled edit session, version history, or rendered output. Draft resume asks the user to reselect the source. |
| Render and export (`EXP-001`, `EXP-002`) | Not built | None. | No renderer, MP4 export, progress/cancel/retry, validation, save-to-device, or share flow. |
| Profile and settings (`PROF-001`, `SET-001`, `ACCNT-001`) | Sample / nonfunctional | Information architecture is displayed. | Most rows have empty handlers; sign-in only displays a not-connected alert. No editable preferences, security, privacy controls, account, notifications, or billing. |
| Recovery (`UX-002`) | Partial | Section decisions persist locally and can be resumed after process restart. | Device lifecycle, backgrounding, low-memory, actual upgrade/migration, and source-file recovery have not been exercised on iOS/Android. |

## Highest impact gaps

1. **The central “reuse a template” loop is incomplete.** The library can reopen recipe metadata, but the user cannot fill its sections with new footage or generate a new video. This is the largest gap between the product objective and the current app.
2. **Discover/inspiration buttons imply functionality that is not connected.** The sample cards and “Start with an idea” route do not select or apply a recipe.
3. **The Adapt screen presents mock editing controls.** Selection, caption, and audio changes are not part of the saved recipe.
4. **Research-level editing and export acceptance remains unmet.** The current section editor supports manual seeking, splitting, and decisions; trimming, merging, output preview, and rendering are absent.
5. **The app has not been run through iOS and Android acceptance scenarios.** TypeScript validation does not prove picker permissions, SQLite migration, resume flow, or playback on target devices.

## Recommended implementation order

1. **Make the current UI truthful.** Mark inspiration and adaptation examples as previews, disable actions that imply completed media operations, and remove empty settings affordances until they have behavior. Keep the manual import/review/save path available.
2. **Define the reusable edit model before adding more screens.** Extend the recipe contract through an explicit migration to represent ordered replaceable slots and their duration/framing prompts. Keep source-analysis proposals separate from user-approved recipe data.
3. **Implement a real “Use template” flow with user media.** Open a saved recipe, choose replacement clips for slots, persist a separate edit session without modifying the original, and show missing-slot states. This does not require automatic scene detection.
4. **Run the researched iOS/Android renderer parity spike.** Prove that the same simple recipe preview and MP4 export agree on section timing, order, crop, audio handling, interruption, and output validation before enabling export claims.
5. **Add a real curated inspiration catalog only after recipes can be applied.** Every example needs provenance, details, and a working “Use this recipe” route.
6. **Evaluate the experimental cut proposal baseline** against the permissioned, annotated clip set and compare it with the documented alternatives. Decide processing location and build the mobile `AnalysisPort` adapter only after privacy, device, accuracy, and correction-cost evidence. Keep manual creation usable if analysis fails.

## Source references

- [MVP coverage and traceability](mvp_coverage_and_traceability.md)
- [Mobile frontend design specification](../design/mobile_frontend_design_spec.md)
- [Video-template workflow specification](video_template_workflow_spec.md)
- [Rendering capability and quality gate](rendering_capability_and_quality_gate.md)
- [Mobile app current limits](../../apps/mobile/README.md)
