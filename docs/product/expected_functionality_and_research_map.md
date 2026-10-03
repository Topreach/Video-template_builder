# Expected Application Functionality and Research Map

**Purpose:** Put the functionality discussed with the product owner in one reviewable baseline and point each requirement to its detailed research source.
**Status:** Reconciled product baseline, 3 October 2026. This describes intended behavior, not a claim that the current prototype already provides it.
**Related:** [MVP product blueprint](mvp_product_blueprint.md), [video-to-template workflow](video_template_workflow_spec.md), [component analysis signals](video_analysis_signal_strategy.md), [mobile interface specification](../design/mobile_frontend_design_spec.md), [MVP coverage map](mvp_coverage_and_traceability.md), [mobile implementation audit](mobile_mvp_implementation_audit.md).

## 1. Product in one sentence

The user imports a short reference video, sees a time-aligned analysis of its parts, chooses what to edit, keep, or exclude, adapts those parts into a reusable template, previews it, saves it, then fills its slots with their own media and downloads a new short video.

The application is a guided **video-to-reusable-template workshop**. Its main value is understanding and reusing a video's structure. A sample template gallery alone, a cut detector alone, or an unstructured professional editor does not satisfy this objective.

## 2. The expected end-to-end workflow

```text
Create from a reference ─┐
                         ├─> Inspect and validate media (reference <= 30 seconds)
Use a curated app recipe ┘
  -> Explain rights and processing; user confirms or cancels
  -> Analyze the whole clip across the defined component passes
  -> Show the component map, evidence, uncertainty, and per-pass coverage
  -> User corrects findings and groups/marks reusable sections
  -> For each section: Edit / Keep / Exclude
  -> Offer replacement ideas and controls for supported text/audio/visual edits
  -> Preview the proposed template before saving
  -> Save a private, editable recipe and reusable user-created sections
  -> Later reopen the recipe and fill its media slots with the user's own assets
  -> Preview the assembled result and resolve warnings
  -> Render/download an MP4 (<= 30 seconds) and hand off through the system share sheet
```

Analysis, the user's section groupings, the user's decisions, the saved template, and the final rendered video are separate data and workflow states. Rerunning analysis must not overwrite work the user has approved.

## 3. Competitive bar

CapCut already offers replaceable template clips and publishing for eligible creators; Canva and Adobe Express offer searchable, customizable template libraries and brand tools. A gallery and basic clip swap are therefore baseline expectations, not our distinction. The proposed advantage is to explain the source video's structure, expose editable timing and section grouping, guide users toward suitable footage, support meaningful variations, and carry their preferences into a repeatable private recipe. The prevalence of reported template-slot frustrations remains unproven and needs creator usability research. [Product and competitive research](../research/product_strategy_and_competitive_research.md#4-template-design-patterns-and-observed-weaknesses)

## 4. Functional expectations and delivery scope

| Area | Expected functionality | MVP boundary / release condition | Detailed source |
|---|---|---|---|
| Video import | Select a local short reference video, play/inspect it, and show duration, dimensions, orientation, frame rate/audio when available. Accept complete and partial clips; fail safely on corrupt/unsupported input. | Reference is limited to 30 seconds. No automatic trimming; no scraping/downloading from social platforms. User chooses the source file. | [Workflow: import](video_template_workflow_spec.md#41-select-and-validate-a-reference), [media lifecycle](media_privacy_security_and_data_lifecycle.md) |
| Analysis before editing | Finish configured analysis passes and show results/coverage before asking what the user wants to edit. A cut is a visual shot boundary, not automatically a creative/story section. Several shots may make one reusable section; one shot may contain several beats. | The required component inventory is a product requirement. “Ready” means every required pass completed or was genuinely unsupported by the source; it does not claim perfect detection. Failed/not-run/partial passes stay visibly partial and expose manual review. | [Signal coverage contract](video_analysis_signal_strategy.md#required-analysis-coverage-contract), [workflow: analysis](video_template_workflow_spec.md#42-analyze-and-report-honestly) |
| Component map | Report timestamps, evidence, provider/version, processing location, and uncertainty for technical facts; shot boundaries; people/subjects; objects/actions; setting/background; camera motion/layout/split-screen/overlays; on-screen text/marks; speech; music/effects/silence/beats; creative roles; and source-integrity cues. | No identity recognition or sensitive-trait inference. Subject continuity IDs are anonymous and local to one clip. Region/mask data is only returned if a capable, quality-evaluated provider produced it. | [Signal inventory](video_analysis_signal_strategy.md#2-signal-inventory-and-mvp-order), [proposal contract](video_template_workflow_spec.md#6-proposed-versioned-contracts) |
| Video families | Understand that song/beat edits, film/cinematic, action, comedy/funny, dialogue/story, tutorial, and product clips need different structures and timing. | Do not force all formats onto beat timing. Roles are editable hypotheses (including `unknown`), not objective claims or virality scores. | [Template families](video_template_workflow_spec.md#45-suggest-replacements-and-creative-alternatives), [signal strategy](video_analysis_signal_strategy.md) |
| Section review | Show ordered, preview-linked sections. Let the user create/split/trim/merge/group/reorder/rename sections, correct timing/roles, undo, and choose **Edit**, **Keep**, or **Exclude**. | No section is automatically removed or assumed safe to keep. Excluded source intervals cannot enter the recipe or render. Incomplete clips remain usable with manual correction. | [Workflow: review](video_template_workflow_spec.md#43-review-proposed-boundaries-and-form-sections), [coverage](mvp_coverage_and_traceability.md) |
| Replacement ideas | Offer practical, format/role-aware prompts for what to record or select, with timing/framing and why it fits; allow edit, skip, or another suggestion. | Prompts are distinguishable from actual supplied media and never auto-applied. No claim that a template predicts reach or virality. | [Signal/recommendation strategy](video_analysis_signal_strategy.md#34-semantic-analysis-and-replacement-recommendations), [workflow](video_template_workflow_spec.md#45-suggest-replacements-and-creative-alternatives) |
| Reuse and visual edits | Let users replace section media with their own videos/images; retain timing/framing guidance. Support section-scoped crop/reframe. The user also wants to change backgrounds and people/characters so outputs look different from the reference. | Whole-section replacement is the dependable baseline. Background replacement is conditional on quality/performance evidence. Replacing a person with a different/generated character while preserving action is a higher-risk research capability, not a universal v1 promise. Keep this requested outcome on the roadmap and expose supported operations honestly. | [Visual replacement research](../research/mvp_technology_and_design_research.md#personbackground-replacement), [quality gates](rendering_capability_and_quality_gate.md), [blueprint visual requirements](mvp_product_blueprint.md#4-mvp-scope) |
| Text and audio | Edit/replace captions and titles; change music, speech/voiceover, sound effects, tone, volume, and timing; preview the mix. | Text/audio tracks remain separate and user-editable. Show provenance and actual usage scope. Changing a song, tone, or words does not by itself clear rights in the remaining source video or other assets. | [Signal strategy](video_analysis_signal_strategy.md#31-ocr-sampled-frames-not-a-claim-about-every-caption), [rights and provenance](copyright_rights_and_asset_provenance.md), [workflow](video_template_workflow_spec.md#46-edit-text-audio-and-visual-layers) |
| Preview and save | Compare reference, template structure, and user's proposed version. Preview before confirming; save a private editable template with stable IDs/versioning. Let the user reopen, duplicate, revise, and reuse it. | Template recipe stores the structure/instructions and user-approved choices, not an unapproved public copy of reference media. Keep analysis findings separate from the recipe. | [Workflow: preview/save](video_template_workflow_spec.md#47-recipe-preview-and-save), [data contracts](video_template_workflow_spec.md#6-proposed-versioned-contracts) |
| Personal reusable sections | Let a user save a section/format they created from their own project and use it again. | Private and reusable in the user's library. This is distinct from publishing it publicly or selling it. Preserve origin/rights and version information. | [Blueprint MVP scope](mvp_product_blueprint.md#4-mvp-scope), [recipe and provenance](../research/mvp_technology_and_design_research.md#5-template-recipe-requirements) |
| App-owned inspiration hub | The app owner supplies categorized starter templates for inspiration and application (e.g. song, cinematic, action, comedy, tutorial, product). Each entry explains purpose, runtime, slots, required media, output profile, and source/rights. | Include a small, high-quality curated starter catalog in the MVP. Expand it after the core create/reuse path works. Do not require a public marketplace or user publishing to provide owner-curated examples. | [Product strategy](../research/product_strategy_and_competitive_research.md), [UI spec](../design/mobile_frontend_design_spec.md#4-screen-by-screen-specification), [rights requirements](copyright_rights_and_asset_provenance.md) |
| Public creator marketplace | Users submit/publish templates, browse public creator profiles, follow/comment, or earn payouts. | Later phase. Requires creator submission tools, review/moderation, rights checks, reporting/takedown, attribution, versioning, privacy, and operations. Not needed for private personal reuse or the app-owned starter catalog. | [Blueprint roadmap](mvp_product_blueprint.md#9-phased-roadmap), [account/community scope](../research/account_security_monetization_and_editor_scope.md#8-updated-roadmap-boundary) |
| Render/download/social handoff | Apply the saved recipe to selected media, preview, export a standard playable video, save/download it, and offer the platform share sheet. | MP4, at most 30 seconds, initially. User may continue editing/posting in TikTok, Facebook, or another editor. Direct posting/API integration is not part of the MVP. | [Rendering gates](rendering_capability_and_quality_gate.md), [account/editor scope](../research/account_security_monetization_and_editor_scope.md#7-professional-editor-feasibility-and-scope) |
| Full finishing editor | Import extra arbitrary clips/audio after applying a template, then make general timeline edits. | Future, separately validated Finishing Studio; do not expand the MVP into a CapCut-scale editor. | [Editor scope research](../research/account_security_monetization_and_editor_scope.md#7-professional-editor-feasibility-and-scope) |
| Profile and settings | Creator profile/preferences, creation defaults, accessibility, privacy/media retention, help/legal. Keep creator presentation distinct from login identity. | Essential local settings exist in product design. Logo/colors/tone are optional profile preferences; no profile should block local creation. | [Account/settings research](../research/account_security_monetization_and_editor_scope.md#2-account-and-profile-requirements), [UI spec](../design/mobile_frontend_design_spec.md) |
| Login and security | Optional guest/local path; email or supported identity login when sync/cloud needs it; verification/recovery, sessions, sign-out, deletion, secure token handling, server authorization if services are added. | Do not force signup for local creation. Account provider/backend and cloud sync remain unselected. Do not store credentials or source media in ordinary settings/logs. | [Account/security research](../research/account_security_monetization_and_editor_scope.md#2-account-and-profile-requirements), [privacy lifecycle](media_privacy_security_and_data_lifecycle.md) |
| Notifications | In-app status by default; contextual opt-in for long remote jobs; user category/OS controls. | Core workflow works without push permission. No sensitive video details in lock-screen messages. | [Notification policy](../research/account_security_monetization_and_editor_scope.md#4-notification-policy-and-ux) |
| Subscription/billing | Plan status, entitlements, restore/cancel and purchase support if/when a paid product exists. | No subscription paywall at launch. First measure repeat creation, reuse, costs, and willingness to pay; recheck store rules at release. | [Monetization research](../research/account_security_monetization_and_editor_scope.md#6-subscription-and-purchase-strategy) |
| Platform/design quality | iOS and Android mobile UX, vertical social preview, accessible controls, adjustable output profile/safe areas, responsive text/crops, interruption recovery. | Cross-platform parity is a release gate for supported edit/render operations; no parity claim from API docs alone. Keep interfaces/contracts modular and saved-data migrations explicit. | [UI specification](../design/mobile_frontend_design_spec.md), [rendering gate](rendering_capability_and_quality_gate.md), [change-safety plan](../research/software_evolution_and_ai_change_safety.md) |

## 5. Important boundaries that protect the product

- “Viral” describes the source inspiration/content category, not an outcome the app can predict or guarantee.
- Uploading a clip for private analysis is separate from permission to publish, distribute, or reuse the clip's footage, music, text, performance, or likeness.
- Do not scrape/download videos from social platforms or treat platform availability as permission.
- Replacing sound or wording alone is not a copyright clearance mechanism. Prefer user-owned/licensed replacement assets and retain provenance.
- Do not interpret an abrupt join or a partial clip as proof of an unauthorized/attached video. Show evidence and let the user decide.
- A public user-template marketplace is different from (a) an app-owned curated catalog and (b) a user's private reusable sections; keep these separate in navigation, permissions, data, and roadmap.
- “All components” means all defined categories have an explicit analysis/reporting pass and coverage state. It cannot honestly mean perfect recognition of every object, action, word, sound, or intent.

## 6. Current prototype versus expected product

The mobile prototype currently supports local video picking/playback, the 30-second gate, manual time seeking/splitting, selected-moment previews, Edit/Keep/Exclude choices, metadata recipe persistence, and one recoverable local draft. Discovery and replacement screens are sample content. The Python CLI detects candidate visual cuts and explicitly returns a partial proposal. It is not connected to the mobile app.

The central product loop is therefore not complete yet: comprehensive component detection, analysis-to-mobile integration, automatic suggestions, persistent slot filling with personal footage, real text/audio/visual edits, actual template preview, MP4 rendering/download, and functional account/settings services remain incomplete or unbuilt. See the [source-level implementation audit](mobile_mvp_implementation_audit.md) for the detailed screen-by-screen status.

## 7. Decisions still open before production commitments

1. Which evaluated detector/provider handles each required component pass, for which languages and media families?
2. Which passes run locally, which (if any) run through a disclosed service, and what are their retention/resource limits?
3. What measured precision, recall, temporal stability, correction burden, and device performance are required for each component before it can be marked complete?
4. Which background/subject replacement operations pass visual-quality and iOS/Android preview/export parity gates?
5. What are the first supported launch markets, languages, media limits, and social output profiles?
6. What lightweight editorial workflow maintains the app-owned curated starter catalog? A public creator CMS/marketplace is not assumed.
7. Which account/backend provider is selected if cross-device sync or cloud processing is introduced?
8. Is there measured recurring value/cost evidence for a later paid tier?

These are provider/operations decisions. They do not change the agreed user workflow above.
