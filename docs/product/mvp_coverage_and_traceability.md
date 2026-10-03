# MVP Coverage and Implementation Traceability

**Purpose:** Keep product research, screen design, architecture, implementation, and release checks connected so agreed requirements do not disappear during development.
**Status:** Coverage baseline as of 2 October 2026. This is a living index; it is not a claim that every unknown or jurisdiction-specific obligation has been discovered.
**Related:** [Video-to-template workflow specification](video_template_workflow_spec.md), [MVP product blueprint](mvp_product_blueprint.md), [mobile UI specification](../design/mobile_frontend_design_spec.md), [architecture build plan](mvp_architecture_and_build_plan.md), [feature map](../architecture/feature-map.md), [account/security/settings research](../research/account_security_monetization_and_editor_scope.md), [media privacy and lifecycle plan](media_privacy_security_and_data_lifecycle.md), [copyright, rights, and provenance](copyright_rights_and_asset_provenance.md), [technology research](../research/mvp_technology_and_design_research.md), [change-safety plan](../research/software_evolution_and_ai_change_safety.md).

Latest source-level mobile implementation comparison: [Mobile MVP implementation cross-check](mobile_mvp_implementation_audit.md). The statuses below describe requirements/research coverage; they do not mean a feature is implemented unless the source-level audit says Connected.

## 1. How to use this map

Every user-visible or operational requirement must have:

1. A stable requirement ID in this document or a linked detailed spec.
2. A feature owner/boundary in `docs/architecture/feature-map.md`.
3. A source of truth for behavior and screen states.
4. An observable acceptance criterion or explicit research/decision gate.
5. An implementation status and evidence before release.

When a new requirement is found, add it here first, assign an ID, name its owner and dependencies, and update the detailed spec. Do not silently broaden MVP or mark an unresolved feature "done" because a button exists. Sample data and mock screens must remain identified as such.

### Coverage labels

- **Specified:** Product behavior and interaction are written down; technical implementation can still be pending.
- **Decision gate:** Multiple feasible options remain. Record prototype evidence and a decision before production commitment.
- **Deferred:** Intentionally outside MVP; preserve its boundary so implementation does not accidentally absorb it.
- **Release review:** Must be rechecked for chosen markets/platforms and the actual release date.

## 2. User journey requirement map

| ID | Capability / coverage | MVP requirement and acceptance evidence | Owner | State / source |
|---|---|---|---|---|
| NAV-001 | First launch and navigation | User understands Create, Discover/inspiration, and My Templates; can enter core creation without a forced account where local flow permits. | `discover`, navigation | Specified: [UI spec](../design/mobile_frontend_design_spec.md#3-navigation-and-app-shell) |
| DISC-001 | Curated inspiration | Recipe card explains purpose, format, runtime, slot count, required media, output profile, and rights/asset caveats; no false "trending" claims. Small curated catalog only if it does not delay core loop. | `discover` | Specified; catalog size is scope choice: [UI spec](../design/mobile_frontend_design_spec.md#4-screen-by-screen-specification); shipped examples need provenance/license evidence: [rights requirements](copyright_rights_and_asset_provenance.md#5-mvp-scope-and-operational-boundaries) |
| IMP-001 | Local reference selection | System picker; selected media preview and available metadata; user can cancel or choose another source. | `import` | Specified: [workflow section 4.1](video_template_workflow_spec.md#41-select-and-validate-a-reference) |
| IMP-002 | Input validation | 30-second maximum is checked before expensive processing and by the processing boundary; unsupported, undecodable, truncated, oversized, or unknown-duration files produce actionable errors and retain recoverable work. No silent auto-trim. | `import`, `analysis` | Specified; limits for bytes/dimensions await device/service decision. |
| IMP-003 | Rights and processing consent | Before analysis, explain purpose, on-device/cloud location, retention/deletion, model/provider use if any, and request a rights declaration separately from permission to publish; unknown rights can continue only through the explicitly described structure-only path or cancel. | `import`, `settings-privacy` | Specified; exact notice and processing path are decision-gated. [Rights requirements](copyright_rights_and_asset_provenance.md#3-user-experience-and-rights-checkpoints) |
| ANA-001 | Analysis progress and cancellation | Honest named stages; no fabricated percentage; cancel, retry, preserve draft; failure offers manual section creation. | `analysis` | Mobile progress/cancel/retry remains unimplemented. The local Python CLI reports named stages only; see [ADR 0003](../architecture/decisions/0003-experimental-local-shot-analysis.md). |
| ANA-002 | Boundary proposals | Candidate shot boundaries carry source/method/version and calibrated uncertainty; no automatic exclusion; a cut is not treated as a story section. | `analysis` | Experimental local PySceneDetect Adaptive proposal contract/CLI exists; uncertainty is explicitly unknown and thresholds are uncalibrated. No mobile integration. [ADR 0003](../architecture/decisions/0003-experimental-local-shot-analysis.md) |
| ANA-003 | Component inventory and role hypotheses | Before section decisions, report time-aligned visual content, text/marks, speech, music/sound, creative-beat hypotheses and source-integrity cues; distinguish shots from reusable sections; show per-signal status, provenance and uncertainty; never infer identity or auto-exclude. | `analysis` | Product requirement specified in [coverage contract](video_analysis_signal_strategy.md#required-analysis-coverage-contract); currently only shot boundaries are implemented in Python CLI, so the result is explicitly partial. Mobile analysis and providers remain unimplemented/decision-gated. |
| SREV-001 | Review and correct spans | Preview-linked section cards; time ranges, durations, thumbnails, role/uncertainty, detected/manual provenance; trim, split, merge, reorder, rename, undo/redo. | `section-review` | Specified: [workflow section 4.3](video_template_workflow_spec.md#43-review-proposed-boundaries-and-form-sections) |
| SEC-002 | Edit / Keep / Exclude | Every section requires an explicit decision; meaning is explained; excluded spans never enter recipe/render; retained reference footage is shown and requires confirmation. | `section-review`, `recipe-editor` | Specified: [workflow section 4.4](video_template_workflow_spec.md#44-decide-what-each-section-means-for-the-template) |
| REP-001 | Replacement guidance | Give an actionable capture/use prompt, timing/framing, rationale, source type and provenance; user may accept, edit, skip, or request another; no auto-application. | `recipe-editor` | Specified: [workflow section 4.5](video_template_workflow_spec.md#45-suggest-replacements-and-creative-alternatives) |
| REP-002 | Content families | Support distinct patterns for song/beat, cinematic, action, comedy, story/dialogue, tutorial, and product; do not force beat timing on non-beat formats. | `recipe-editor`, `analysis` | Specified; validated family set depends on sample and creator study. |
| TXT-001 | Text and captions | Edit/rewrite text and captions, style and time; preview in selected language/aspect profile; no reuse claim for source wording/lyrics without rights. | `recipe-editor` | Specified; supported typography/render capability is renderer-gated. |
| AUD-001 | Audio editing | Separate source audio, replacement track, narration, effects; mute/replace/volume/time controls and mix preview; show asset provenance and applicable license information. | `recipe-editor`, `render-preview` | Specified; licensed catalog/provider not chosen. |
| VIS-001 | Visual replacement | Whole-section replacement with user media is baseline; crop/reframe supported; background/subject operations only when quality-tested, reversible, and explicitly labeled. | `recipe-editor`, renderer | Base specified; background/person generation decision-gated or deferred. |
| PRE-001 | Recipe preview | Clearly distinguish Reference / Template structure / Your version; summarize included/excluded sections, placeholders, retained media, timing, layers, profile, unsupported operations. | `render-preview` | Specified: [workflow section 4.7](video_template_workflow_spec.md#47-recipe-preview-and-save) |
| SAV-001 | Save and reuse template | Private editable template, schema version, stable IDs, duplicate/rename/reopen/delete; save decisions separately from analysis; preserve drafts through interruption. | `template-library`, `project-drafts` | Recipes persist through `RecipeRepository`; one unfinished project autosaves section edits through `ProjectDraftRepository` and can be resumed after source reselection. Cross-device recovery and production migration evidence remain required. [ADR 0001](../architecture/decisions/0001-local-recipe-storage.md) |
| FILL-001 | Fill template slots | Add/replace user media; required/optional, expected duration/framing, trim/crop; preserve the original recipe and create a new edit/version. | `recipe-editor` | Specified: [workflow section 4.8](video_template_workflow_spec.md#48-reuse-render-and-download) |
| EXP-001 | Preview and output checks | Validate missing slots, runtime, excluded material, unsupported effects, crop/text collisions, audio and provenance before render. | `render-preview`, `export` | Specified; exact output profiles and tolerances are decision-gated. |
| EXP-002 | MP4 render and handoff | Render immutable snapshot; show progress/cancel/retry; validate output can be reopened; save locally and offer system share sheet; no direct posting promise. | `export` | Specified; renderer and output settings are decision-gated. |

## 3. Cross-cutting product and release coverage

| ID | Domain | Required coverage | Owner | State / source |
|---|---|---|---|---|
| UX-001 | Screen states | Loading, empty, offline, error, permission-denied, unsupported, dirty-exit, saved, and retry states for every network/media operation. | Owning feature | Specified: [UI states](../design/mobile_frontend_design_spec.md#7-interaction-and-state-requirements); detailed per-screen implementation checklist still required. |
| UX-002 | Resumption and recovery | Preserve draft across app backgrounding, picker handoff, low-memory termination where possible, analysis/render cancellation and failure; never overwrite user's edits. | `project-drafts`, job owners | Local manual-section draft persists through process restart; source must be selected again. Background/low-memory/device recovery validation and analysis/render job recovery remain pending. |
| ACC-001 | Accessibility | VoiceOver/TalkBack labels and focus, scalable text, contrast, non-color state, large touch targets, captions, mute, reduced motion, no gesture-only path; actual-device evaluation. | App shell + every feature | Specified: [UI accessibility](../design/mobile_frontend_design_spec.md#9-accessibility-and-inclusive-use) |
| LOC-001 | Localization and RTL | Externalizable strings; text expansion, right-to-left layout, translated captions and title preview; language list chosen for launch. | App shell, recipe/text | Requirements specified; first languages and QA vendors/plan decision-gated. |
| SOC-001 | Output profiles | Separate app layout from output canvas/profile; aspect, crop, safe areas, duration guidance, resolution/frame rate/audio; profile versioning and updates. | `render-preview`, `export` | Specified; initial supported profiles/specs require release-time verification. |
| PRIV-001 | Media lifecycle | Source, extracted frames, analysis payload, replacement assets, recipes, caches, and exports have explicit storage/retention/delete behavior. | `import`, storage, settings | Specified; local/cloud architecture decision-gated. [Data lifecycle plan](media_privacy_security_and_data_lifecycle.md) |
| SEC-001 | Application security | Threat model; secure credential store; TLS; authorization on every server object/job; short-lived asset access; validation; redacted logs/analytics; deletion and session revocation. | `account`, backend, settings | Baseline specified; detailed threat/lifecycle controls documented; security review before cloud pilot. [Data lifecycle plan](media_privacy_security_and_data_lifecycle.md), [security research](../research/account_security_monetization_and_editor_scope.md#5-security-and-privacy-baseline) |
| ACCNT-001 | Sign-up/login | Guest-first where feasible; account needed only for named benefit; email/provider options, verification/recovery, rate limits, neutral anti-enumeration responses, sign-out/session management/account deletion. | `account` | Specified; provider and whether MVP requires cloud identity unresolved. [Account research](../research/account_security_monetization_and_editor_scope.md#2-account-and-profile-requirements) |
| ACCNT-002 | Guest-to-account migration | Explain local/cloud boundaries; attach local projects only with user action; detect duplicates/conflicts; never overwrite silently. | `account`, `template-library` | Specified for future account path; only build if account/sync selected. |
| PROF-001 | Creator profile | Optional public-facing name/avatar/brand preferences separate from identity; no social-profile requirement for creation/export. | `settings-privacy` | Specified; optional MVP detail. |
| SET-001 | Settings | Group creator profile, account/security, creation defaults, notification controls, privacy/media, plan, accessibility, help/legal; show current permission/processing state. | `settings-privacy` | Specified: [account and settings research](../research/account_security_monetization_and_editor_scope.md#3-settings-information-architecture) |
| NOTIF-001 | Notifications | Never request at first launch; context and benefit before OS prompt; local renders use in-app state; remote completion only with opt-in; low-volume and privacy-safe text. | `notifications` | Specified; push deferred unless remote long jobs need it. [Notification policy](../research/account_security_monetization_and_editor_scope.md#4-notification-policy-and-ux) |
| BILL-001 | Subscription/payments | No launch paywall; validate return use and variable costs first; if later sold, show exact price/period/trial/renewal/cancel/restore and recheck store/region rules. | `billing` | Deferred; release review required if activated. [Monetization research](../research/account_security_monetization_and_editor_scope.md#6-subscription-and-purchase-strategy) |
| LEG-001 | Rights/provenance | Separate source analysis from publishing permission; user declarations, asset origin/license/destination/expiry, attribution and lineage; no rights-safe claims from edits; public marketplace requires moderation/takedown process. | `recipe-editor`, `settings-privacy` | Specified; target jurisdiction and asset provider need legal review. [Rights requirements](copyright_rights_and_asset_provenance.md) |
| AI-001 | AI transparency and safety | Separate detected/suggested/user-selected/applied; show uncertainty; explain generated/material alteration; user approval/undo; avoid unsupported identity/likeness transformation promises. | `analysis`, `recipe-editor` | Specified; individual providers/models and policy controls not selected. |
| DATA-001 | Analytics/telemetry | Define minimal product events and retention; no source frames, raw media, transcript or sensitive titles in logs/analytics by default; opt-in/notice according to target market. | Cross-cutting | Privacy goal specified; analytics vendor, consent/legal basis and retention decision-gated. |
| HELP-001 | Help and support | Explain input failures, rights, processing, export, contact/report problem, policy/legal links; support request must not silently attach media. | `settings-privacy` | Information architecture specified; support channel/SLA deferred. |
| MON-001 | Reliability and operations | Track analysis/render success, duration, cancellation, storage/error classes and version; redact media-derived data; define alerting and recovery ownership if cloud is used. | Backend, `analysis`, `export` | Requirements implied/specifiable; SLOs and ops provider decision-gated. |
| COMP-001 | Compatibility and upgrades | Version all saved recipe/proposal/profile/job contracts; deterministic migrations preserve user decisions/provenance; unknown future data remains intact; rollback and change record. | Contracts + feature owners | Specified: [change-safety plan](../research/software_evolution_and_ai_change_safety.md#4-upgrade-and-compatibility-strategy) |
| REL-001 | Build/release/distribution | Reproducible development builds; dependency/license inventory; signing/secrets, staged release, crash reporting privacy, store disclosures/review and rollback. | Release engineering | Research incomplete until stack/markets selected. |
| MONET-001 | Cost controls | Measure upload/storage/analysis/model/music/render costs, quotas and abuse limits before subscriptions or unlimited cloud use. | Product + backend | Required research; no prices/quotas set. |

## 4. Explicitly deferred functionality

These requirements are recorded so they are not mistaken for implementation omissions in MVP. Reopen only with product evidence and a scoped decision record.

| ID | Deferred area | Reopen trigger | Source |
|---|---|---|---|
| DEF-001 | Public user template publishing / marketplace / profiles | Core private create-reuse loop, rights, provenance, moderation, reporting and takedown are validated and supported. | [Blueprint roadmap](mvp_product_blueprint.md#9-phased-roadmap) |
| DEF-002 | Full professional multi-track editor / arbitrary pre/post clips | Creator research shows material harm from external editor handoff; a bounded scope and parity proof is accepted. | [Editor scope research](../research/account_security_monetization_and_editor_scope.md#7-professional-editor-feasibility-and-scope) |
| DEF-003 | Direct posting to social platforms | Platform API, permissions, policy, reliability, and user demand are established; export/share sheet remains MVP. | [Workflow spec](video_template_workflow_spec.md#48-reuse-render-and-download) |
| DEF-004 | Generative person/character replacement and arbitrary object inpainting | Quality, temporal consistency, likeness consent, moderation, cost and safety pass separate gates. | [Technology research](../research/mvp_technology_and_design_research.md#6-analysis-and-ai-capability-feasibility) |
| DEF-005 | Push engagement reminders/social graph | A product need is supported by research, user opts in, and notification controls/operations exist. | [Account research](../research/account_security_monetization_and_editor_scope.md#4-notification-policy-and-ux) |
| DEF-006 | Paid subscription, creator payouts, paid catalog | Repeat value and cost data support an offer; storefront/region requirements are reviewed. | [Account research](../research/account_security_monetization_and_editor_scope.md#6-subscription-and-purchase-strategy) |

## 5. Decision and evidence register

Do not treat these as accidental gaps or solve them implicitly during UI implementation. Each decision needs a short record containing context, alternatives, evidence, decision, tradeoffs, owner, date, and revisit trigger.

| Decision ID | Question still open | Evidence required before decision | Blocks |
|---|---|---|---|
| DEC-001 | Which market, launch age policy, languages, data-residency regions? | Target-user/market choice, qualified privacy and store-policy review. | Accounts, consent copy, data hosting, localization, launch. |
| DEC-002 | Analysis on device, server, or staged hybrid? | Representative annotated clips; accuracy/correction time; privacy, latency, low-end device, battery, cost comparison. | Production analysis implementation and consent UX. |
| DEC-003 | Which boundary detector and supported input codecs/device floor? | Current PySceneDetect AdaptiveDetector implementation is a baseline only. Compare it on the same permissioned corpus with TransNet V2; add AutoShot only after inference, weights, data/model terms, and packaging are verified. Evaluate per-family boundary metrics, correction burden, VFR/corruption, performance and malformed-file handling. | Production analysis integration and validation limits. |
| DEC-004 | Which providers and processing paths will deliver each required analysis signal in the first release? | Per-language/family accuracy, correction cost, performance, privacy, platform availability, and user-value evidence. The component categories and per-signal reporting contract are set; provider and staged rollout remain open. See [signal strategy](video_analysis_signal_strategy.md). | Analysis adapters/models, permission disclosures, processing-location decision. |
| DEC-005 | Which iOS/Android render architecture and feature subset? | Complete [rendering capability and quality gate](rendering_capability_and_quality_gate.md): same-plan preview/export parity, codec/HDR/VFR matrix, device/resource/recovery measures, and iOS evidence. | Real export, development-build requirements, supported effects. |
| DEC-006 | Production persistence, recipe format, and media retention policy? | Current Expo candidate uses local SQLite behind `RecipeRepository`; production decision still needs iOS/Android migration, backup, recovery/delete evidence and privacy review. See [ADR 0001](../architecture/decisions/0001-local-recipe-storage.md). | Durable production library/reopen flow and media policy. |
| DEC-007 | Which licensed audio/visual asset provider and rights fields? | Provider terms, markets, attribution/export restrictions, cost. | Stock suggestions/catalog and related export behavior. |
| DEC-008 | Are background/person visual edits in MVP? | Diverse consented media quality study, cross-platform parity, safety and compute evaluation. | Any user-facing transformation claim. |
| DEC-009 | Initial social output profiles and safe zones? | Organic-use requirements checked against primary platform guidance on release date; crop/text collision usability. | Output profile presets and UI overlays. |
| DEC-010 | Backend, auth provider, database, storage, observability? | DEC-001/002/005, threat model, cost and ownership. | Any cloud processing, identity, sync, remote render. |
| DEC-011 | Analytics/events and consent model? | Product metric plan, data-minimization review, target-market privacy review. | Production telemetry and experiments. |
| DEC-012 | Is monetization needed and which model? | Repeat usage, creator willingness-to-pay, measured variable cost, release-time app-store policy review. | Billing implementation; explicitly does not block free MVP. |
| DEC-013 | Is a finishing editor needed? | Observe where users continue editing after export; frequency and task analysis. | Any added timeline beyond template slots. |
| DEC-014 | What are quantitative release thresholds? | Baseline results per content family and device tier, agreed product risk appetite. | Accuracy, latency, export, usability SLOs. |
| DEC-015 | Local encryption, file protection, and backup inclusion policy? | Data classification, iOS/Android file-protection and backup behavior, restore/delete evidence, draft recovery needs. | Persistent media and project storage. |
| DEC-016 | What cloud retention and deletion TTLs can be guaranteed? | Selected provider, backup expiry, deletion API behavior, legal/market review, operational retry and orphan cleanup evidence. | Cloud processing, account deletion, consent notices. |
| DEC-017 | What retained-source use will the product permit in MVP? | Market-specific legal review of import, local analysis/storage, transformation, and export; validate the proposed replacement-only default and structure-only path. | Retained reference media in recipes or output. |
| DEC-018 | What rights complaint/takedown process is needed for app-owned content? | Launch catalog scope, contact route, response owner/time, evidence retention and market review. | Curated inspiration and future public content. |
| DEC-019 | What rights evidence is required for curated examples? | Per-asset owner/source, license grant, allowed uses, territories, term, attribution, edits and export rights. | Shipped inspiration assets and demo media. |

## 6. End-to-end release scenarios

Every scenario must be exercised on target iOS and Android devices or emulators appropriate to the capability. These examples check integration across features; feature-local acceptance checks are also required.

| Scenario ID | Happy path / edge case | Required result |
|---|---|---|
| E2E-001 | Import valid 20-sec, no-audio vertical clip; no detected cuts. | User can manually add sections, make decisions, save, reopen, fill a slot, export. |
| E2E-002 | Clip is over 30 sec. | Rejected before analysis; explicit trim path if supported; no silent truncation. |
| E2E-003 | Partial clip begins mid-sentence and has an attached outro. | Warnings are suggestions; user corrects boundaries, excludes outro; no claims about clip completeness. |
| E2E-004 | Fast song montage has many cuts and flashes. | Cuts may be proposed; user can group cuts into creative sections; beat alignment remains optional and editable. |
| E2E-005 | Action clip has camera movement and strobe/impact frames. | False cut is correctable; no auto-removal; visual edits unsupported unless validated. |
| E2E-006 | Comedy dialogue with setup, pause and payoff but no shot change. | User can create/group story sections even without boundary detector support; pause timing can be preserved. |
| E2E-007 | Analysis provider fails or user cancels / goes offline. | Draft and prior user decisions remain; retry/manual flow exists; no ghost job or fake result. |
| E2E-008 | User excludes a middle section, reorders two remaining sections, and saves. | Preview/output reflect order and omission; source-time references remain correct; excluded material never renders. |
| E2E-009 | User adds replacement clip shorter/longer/different aspect ratio. | Clear trim/fit choices; no silent stretch; timing/profile preview updates before save/export. |
| E2E-010 | Source soundtrack is muted and new audio added. | Mix preview and output sync; source rights are still disclosed; no copyright-safe promise. |
| E2E-011 | User background-switches or operating system terminates app during work. | Draft reopens at recoverable state; no uncommitted choice is reported as saved. |
| E2E-012 | Export runs out of storage, is cancelled, or encoder fails. | Error is actionable; recipe survives; partial file is not shown as complete; retry is possible. |
| E2E-013 | User deletes source/project, or deletes account if accounts exist. | UI states which local/cloud copies, derived frames, jobs and exports are deleted and reports completion/failure honestly. |
| E2E-016 | Imported reference has unknown rights; user removes original audio and edits captions. | App does not claim the video is cleared; user can create a structure-only recipe, and export blocks or clearly requests replacement/removal of unconfirmed source layers. |
| E2E-017 | User saves a template, closes/reopens the app, renames/duplicates it, and deletes one copy. | Recipes survive restart; each copy has independent identity; delete affects only the selected copy; no source-video URI or bytes are stored in the recipe database. |
| E2E-014 | Saved recipe uses a future schema or unsupported renderer effect. | Data is preserved; migration/unsupported message is explicit; no destructive downgrade/drop. |
| E2E-015 | Screen reader, large text, RTL, muted preview, reduced motion. | All core decisions and export remain accessible without relying on color, sound, or precision gesture alone. |

## 7. Implementation traceability rules

For each code change that touches product behavior:

- Reference the requirement IDs in the implementation task/PR/commit notes.
- Update the matching feature row/status; link to the implementation location after code exists.
- Identify dependencies and shared contracts touched.
- Add acceptance checks for visible behavior and relevant error/recovery state; use integration scenarios when cross-feature behavior changes.
- For persisted schema changes, include old-version fixtures, migration outcome, rollback/recovery, and compatibility evidence.
- For platform behavior, record results for both iOS and Android, naming any deliberate supported-feature difference.
- For unresolved decisions, add/update an ADR before choosing a production dependency/provider/policy.
- In release notes, state new permissions, upload/storage behavior, supported media/effects, migrations, and removed/changed behavior.

Before calling MVP complete, create a coverage report with each in-scope ID marked **implemented and evidenced**, **not implemented**, or **accepted limitation with owner/reason**. No "TBD" may be silently treated as complete. A deliberate MVP exclusion must reference a `DEF-*` row; an open choice must reference a `DEC-*` row.

## 8. Research boundary and ongoing discovery

No static research document can guarantee that no requirement will ever be missed. This map reduces omissions by recording current scope, linking detail, naming unresolved choices, and requiring traceability through implementation/release. Continue discovery for:

- New user groups, countries, languages, age requirements, devices, codecs, accessibility needs, and platform policy changes.
- Real creator task observations and usability findings that contradict the current assumptions.
- New media/render API changes, licensing terms, dependency vulnerabilities, and supported OS changes.
- Abuse, privacy, rights, moderation, support, and reliability issues revealed in prototype or pilot use.
- Operational needs if cloud analysis, accounts, asset hosting, notifications, payments, or public publishing are enabled.

Update this document when scope changes, and date the evidence. Recheck web-source policy/technical claims immediately before decisions and release because platform APIs and rules change.
