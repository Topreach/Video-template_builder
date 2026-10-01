# Video-to-Template Workflow: Product and Technical Specification

**Status:** Research baseline for the first end-to-end workflow; implementation gates remain open where device measurements or user research are required.
**Updated:** 2 October 2026
**Related:** [MVP product blueprint](mvp_product_blueprint.md), [MVP architecture and build plan](mvp_architecture_and_build_plan.md), [technology and design research](../research/mvp_technology_and_design_research.md), [mobile UI specification](../design/mobile_frontend_design_spec.md), [feature map](../architecture/feature-map.md).

## 1. Purpose and product promise

The core product takes a short video a user is permitted to analyze, proposes an editable sequence of sections, and helps the user turn that sequence into a private reusable template. The template describes the creative structure and replacement slots. It does not grant rights to publish the reference video's footage, music, performances, logos, or text.

The first complete workflow must let a user:

1. Select and inspect a local video of 30 seconds or less.
2. See proposed boundaries and correct them without needing to trust AI labels.
3. Mark every section **Edit**, **Keep**, or **Exclude**.
4. Get optional, explainable replacement ideas for sections marked **Edit**.
5. Change text/audio choices and preview the proposed template sequence.
6. Save a versioned, editable private template.
7. Reopen the template, attach their own replacement media, preview, and export an MP4.

The product must not claim the video is â€œcopyright safeâ€ because the user changed a song, text, person, or background. It must not promise virality or claim a detected section role is a fact.

## 2. Important distinction: a cut is not a story section

Video shot-boundary detection finds visual changes between adjacent frames. It does not reliably infer that a span is a hook, joke setup, punchline, action beat, chorus, tutorial step, or coherent reusable idea. A short social clip can have rapid edits inside one creative section, continuous action across several camera cuts, or no visual cut where the spoken story changes.

Accordingly, the workflow separates:

- **Boundary proposals:** candidate time ranges derived from measurable media cues.
- **Section grouping:** the user's chosen reusable pieces, which can span one or more detected shots.
- **Role labels:** optional interpretations such as hook, setup, reveal, payoff, CTA, lyric/beat, action beat, or explanation. Each is marked as a suggestion and can be changed or left unset.
- **Template decisions:** user-approved Edit / Keep / Exclude choices, distinct from analysis results.

PySceneDetect documents content/adaptive detectors as cut-finding methods based on differences in adjacent frames; its adaptive method aims to reduce false detections during fast camera motion. These methods are useful candidates for shot boundaries, not story understanding. [PySceneDetect detector documentation](https://www.scenedetect.com/docs/latest/api/detectors.html), [algorithm guide](https://www.scenedetect.com/docs/latest/cli.html#detect-adaptive).

## 3. Workflow map and durable states

```text
New
  -> MediaSelected
  -> MediaValidated
  -> AnalysisConsentRecorded
  -> AnalysisQueued -> Analyzing -> ProposalReady
       |                 |              |
       |                 |              +-> ProposalNeedsManualReview
       |                 +-> AnalysisFailed (retry or manual sections)
       +-> UnsupportedMedia (choose another file or manual path)
  -> ReviewingSections
  -> AdaptingSections
  -> PreviewingRecipe
  -> TemplateSaved (versioned, private, editable)
  -> FillingSlots
  -> PreviewingOutput
  -> Rendering -> ExportReady
                  |-> RenderFailed (retry / remove unsupported edit)
```

All transitions must be resumable after the app is backgrounded or closed. Save the latest user-confirmed state before starting a long operation. Analysis is recomputable; user decisions and edits are durable and must never be overwritten by a rerun. A rerun creates a new proposal revision and asks whether to compare/apply it; it does not silently rewrite the saved recipe.

## 4. Detailed user journey

### 4.1 Select and validate a reference

**Screen goal:** establish what file is being used, whether it is supported, what will happen to it, and whether the user wants analysis.

Show a local thumbnail/player and these inspectable facts when available: duration, dimensions, orientation, frame rate, audio presence, file type, and file size. Explain whether analysis is performed on-device or sent to a service before requesting consent. Ask the user to confirm they have the right to submit the clip for analysis. This confirmation is not represented as a license to publish its contents.

Validation rules:

- Accept at most 30 seconds for MVP. Enforce this before expensive analysis and again at the analysis boundary.
- Reject files that cannot be decoded, have no usable video frames, have invalid/unknown duration, exceed configured byte/dimension limits, or use an unsupported codec. Give a human-readable reason and a route to select another file or create sections manually.
- Do not auto-trim a long file without user selection. Offer an explicit trim-to-30-seconds action only if supported and show the exact retained range.
- A valid but incomplete-looking clip remains valid. A partial file is not proof that it is incomplete or unauthorized.
- Detect obvious technical quality warnings (truncated decode, large blank/black spans, freeze/repeated frames, abrupt audio edges) as warnings, never as automatic proof that an attached or unwanted clip is present.

**User control:** cancel and return to media selection without leaving a background upload/analysis running. If cloud processing is selected, consent must describe purpose, processing location, retention/deletion behavior, and whether model providers receive media.

### 4.2 Analyze and report honestly

Progress shows named work stages such as `Checking file`, `Finding possible cuts`, `Preparing section previews`, and `Ready to review`. Show indeterminate progress unless the selected operation can calculate reliable completion. Provide Cancel and Keep draft actions. On cancellation, stop new work, discard temporary upload data where possible, and retain only the user's local draft and explicitly saved decisions.

Analysis proposal content for the first workflow:

- Exact source duration and media facts.
- Candidate shot boundaries with time, cue type, detector/version, and confidence or uncertainty band.
- Suggested thumbnails at meaningful points in each candidate range.
- Optional technical warnings for blank/frozen/abrupt edges and missing/unclear audio.
- Optional OCR/transcript/audio-beat findings only when the chosen capability is reliable and consented; each result carries timestamp, language/status, source method, and uncertainty.
- Optional role suggestions with a short explanation. No role is required to proceed.

Initial boundary proposal should combine a fast, interpretable cut detector with review, rather than require a generative model. Candidate implementation: run PySceneDetect's adaptive/content detectors over a normalized decode path, then apply configurable minimum-distance suppression and thumbnail extraction. Compare its results with the current PyAV inspection pipeline and an annotated sample set before selecting thresholds. Rapid music cuts, flashes, camera motion, fades, picture-in-picture, and montage effects are explicit adversarial cases; no default threshold should be called universal.

If analysis fails or times out, keep the selected local asset and allow **Create sections manually**. Never create fabricated sample boundaries and label them as analysis.

### 4.3 Review proposed boundaries and form sections

Use a vertical preview with a scrubber and an ordered list of cards. Each card shows a frame, start/end timecode, duration, boundary source (detected/manual), optional role suggestion, and decision state. Tapping a card seeks the preview to that range.

Required operations:

- Move a start/end boundary with a magnified time readout; allow frame-level adjustment where source frame timing supports it.
- Split a span at the playhead.
- Merge adjacent spans.
- Reorder sections; ordering is separate from original source order and shows a changed-order indicator.
- Rename/set an optional role; unset is a valid value.
- Undo and redo each boundary or ordering change.
- Mark Edit, Keep, or Exclude. Exactly one state per included candidate section; default is **undecided** so the app cannot silently keep reference footage in output.
- Restore an excluded section before confirming the recipe.

The cards should be the default interface. A compact timeline is a precision aid, not a mandatory navigation mode. Use redundant text/icon/state cues, accessible names, and touch targets suitable for the platform. Low-confidence areas should say what is uncertain and offer correction; do not use color alone.

**Attached or mismatched content:** there is no reliable universal detector for â€œan attached videoâ€ versus intentional transitions, reaction overlays, split screens, or montages. The app can flag evidence such as an abrupt splice, incompatible audio, black lead-in/out, or a duplicated/frozen span. The user decides whether to keep, edit, or exclude it. Ask a lightweight optional question if useful: â€œDoes this clip include parts you donâ€™t want in the template?â€ Do not make users classify their file before seeing the analysis.

### 4.4 Decide what each section means for the template

Define the actions precisely:

- **Edit:** include this time span as a replaceable slot. The reference provides structure/inspiration; exported outputs use a user-selected asset or an explicit user-approved retained source asset if the product supports that rights path.
- **Keep:** include the section's timing and treatment as fixed template material. During template authoring, make clear that this keeps the reference material in the private recipe/preview. Do not include it in a public or final export by default unless the user explicitly confirms ownership/permission and the output screen shows it remains.
- **Exclude:** leave this span out of the recipe and all downstream renders. Preserve it only in the source analysis until the user deletes the source/project.

Because reuse should default to the user's own footage, final creation should make **Edit** slots easy to fill and clearly identify any retained reference media. Before final save, show a retained-reference-content count and require explicit acknowledgment when any source media remains. Provide **Replace all reference media** as a guided shortcut.

### 4.5 Suggest replacements and creative alternatives

Suggestions should be concrete and explain their fit. Each suggestion includes:

- A capture/use prompt (subject, action, framing, approximate duration, optional movement).
- Which template role/visual cue it responds to.
- Why it may fit (e.g. â€œkeeps the fast close-up reveal in this sectionâ€).
- Source type: prompt only, user's library, licensed library, or generated media.
- Rights/attribution information when an actual asset is supplied.
- Actions: Use, Edit prompt, Save for later, Skip, Try another.

MVP must still be useful without generative video or paid stock: generate structured shot prompts from user-selected category/role and let users select/capture their own footage. Library matching and generative assets are separate optional providers. Never apply an asset or alter footage automatically.

Support distinct patterns without forcing one beat grid on everything:

| Format family | Useful cues | Replacement idea example | Timing default |
|---|---|---|---|
| Song / beat edit | beat markers, repeated chorus, lyric/caption timing | â€œFilm three quick detail shots, one per beatâ€ | beat-aligned, user-adjustable |
| Film / cinematic | shot scale, atmosphere, movement, reveal | â€œUse a wide establishing shot, then a close detailâ€ | hold timing or choose target duration |
| Action | motion direction, impact moments, camera movement | â€œCapture the same action from a safe, stable angleâ€ | preserve action interval; avoid forced beat cuts |
| Comedy / funny | setup, pause, reaction, punchline | â€œShow the reaction after a short pause; write a new punchlineâ€ | preserve pause and payoff relation |
| Story / dialogue | speech turns, claims, evidence, resolution | â€œReplace the personal anecdote with your own exampleâ€ | speech-led; allow subtitle timing edits |
| Tutorial / product | steps, demonstration, result, CTA | â€œShow the result first, then one close-up of the processâ€ | step order; allow optional sections |

Role/category detection is a draft label, not a fact. User edits must be possible even if OCR/transcription fails or the clip has no sound.

### 4.6 Edit text, voice, music, and sound

Represent source audio, replacement music, narration, effects, captions, and titles as separate optional recipe layers. MVP controls: replace/mute source audio, select supplied licensed or user-owned audio, edit title/caption text, set timing and volume, and preview the mix. Tone suggestions (e.g. playful, calm, tense, energetic) are optional and never applied without acceptance.

Track the provenance of an actual media asset, license/permission notes, attribution, permitted destinations, and expiry where applicable. A prompt is not an audio license. Rewording lyrics or captions, changing pitch, muting a track, or selecting a different song does not clear rights to footage, performances, compositions, sound recordings, likenesses, or trademarks. Copyright Office materials distinguish musical compositions from sound recordings; obtain jurisdiction-specific legal review before launch claims or public remix features. [U.S. Copyright Office, Copyright and the Music Marketplace](https://www.copyright.gov/engage/docs/recording.pdf), [fair-use FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html).

### 4.7 Recipe preview and save

Preview must be built from the actual current user decisions. It must not use demo/sample sections in a real project. Show:

- Ordered included sections and total duration.
- Excluded sections and confirmation that they do not appear downstream.
- Replaceable slots, remaining placeholders, and retained reference footage/audio.
- Audio/text changes, output aspect ratio, crop warnings, and unsupported operations.
- A clear distinction between **Reference**, **Template structure**, and **Your version**.

When slots are empty, show labeled placeholders or a structure preview; do not pass an unchanged reference video off as a finished new output. When the user previews with their replacements, preview the same recipe snapshot intended for save/export. Confirming creates a private versioned recipe with a new ID or version; it does not flatten away editability.

### 4.8 Reuse, render, and download

On reopen, each Edit slot gives the prompt, accepted media type, target duration/framing, trim/crop controls, and optionality. On adding media, show fit/crop and duration decisions and allow changes before render. If beat timing must adapt, ask whether to preserve beat positions, total runtime, or replacement clip length; never choose destructive retiming silently.

Before export, validate:

- No required slots are empty.
- Final runtime is <=30 seconds for initial MVP.
- Excluded source spans are absent.
- Unsupported effects are removed or clearly disabled.
- Crop, aspect ratio, audio mix, text clipping, and rights/provenance summary are visible.
- The chosen output profile states dimensions, frame rate policy, audio policy, and file type.

Export MP4 to app-managed temporary storage, verify that the output can be reopened/decoded, then offer save-to-device/share-sheet actions. Preserve the editable recipe separately. On low storage, cancellation, interrupted app lifecycle, or encode error, keep the recipe and render inputs so the user can retry; never report completion before output validation.

## 5. MVP feature boundary

### Required for a trustworthy vertical slice

- Local import, <=30-second gate, metadata/decode validation, preview.
- Candidate cut boundaries plus manual create/split/merge/trim/reorder.
- Explicit Edit / Keep / Exclude decision state.
- Honest suggestion cards, initially prompt-based and user-owned-media-first.
- Text and source-audio replace/mute controls when renderer proof passes.
- Recipe preview, private local persistence, reopen/duplicate/version behavior.
- Attach replacement clips, basic crop/trim, render MP4, reopen/validate exported output.
- Recoverable errors and deletion controls; disclose processing location.

### Do not make a general MVP promise for

- Correctly identifying every semantic section or attachment.
- Automatic replacement of a real person/character while preserving their performance.
- Photorealistic background replacement on arbitrary action/motion footage.
- Copyright clearance from editing or changing audio/text.
- Unlimited generative asset creation, public community templates, or automatic social publishing.
- A full multitrack editor, direct platform posting, or guaranteed virality.

Person masks are not person replacement. Apple Vision documents a person-segmentation matte that can be used for compositing, not generation of a different person; use it only as a separately validated optional effect. [Apple Vision person-segmentation matte guidance](https://developer.apple.com/documentation/vision/applying-matte-effects-to-people-in-images-and-video).

## 6. Proposed versioned contracts

Keep these as separate objects and persist explicit schema and producer versions. Do not freeze the current Python `TemplateRecipe` model until these ownership and time semantics are mapped to it.

```ts
type TimeRange = { startMs: number; endMs: number }; // half-open [start,end)

type AnalysisProposal = {
  id: string;
  sourceId: string;
  schemaVersion: number;
  producer: { name: string; version: string };
  status: 'ready' | 'partial' | 'failed';
  mediaFacts: { durationMs: number; width?: number; height?: number; hasAudio?: boolean };
  boundaries: Array<{
    atMs: number;
    origin: 'detector' | 'user';
    cue: 'visual-cut' | 'fade' | 'audio-change' | 'manual' | 'other';
    confidence?: number;
  }>;
  warnings: Array<{ code: string; range?: TimeRange; messageKey: string }>;
};

type RecipeSection = {
  id: string;
  sourceRange?: TimeRange;       // points into reference; absent for newly inserted material
  order: number;
  role?: string;
  roleOrigin?: 'user' | 'suggestion';
  decision: 'edit-slot' | 'keep-fixed' | 'exclude';
  optional: boolean;
  targetDurationMs?: number;
  replacementPrompt?: string;
  mediaSlotId?: string;
};

type TemplateRecipe = {
  id: string;
  version: number;
  schemaVersion: number;
  parentVersionId?: string;
  sourceId: string;
  sections: RecipeSection[];
  layers: Array<{ id: string; kind: 'title' | 'caption' | 'source-audio' | 'music' | 'voice' | 'effect'; assetId?: string; editable: boolean }>;
  outputProfileId: string;
  rightsAcknowledgements: Array<{ scope: string; acknowledgedAt: string }>;
  createdAt: string;
};
```

Contract rules:

- Timestamps are integer milliseconds relative to source media and use a documented half-open interval. UI may display frame/timecode precision but must round-trip a valid source time.
- Source time and template output time are separate. Exclusion/reordering changes output placement, not original source references.
- `AnalysisProposal` is immutable once displayed; corrections create a user-edited view or new proposal revision.
- `TemplateRecipe` contains only user-approved choices; analyzer output does not become recipe data by implicit default.
- `exclude` can never reach a renderer input plan.
- Source asset references are indirect IDs/URIs with retention state, not video bytes embedded in recipe JSON.
- Schema migrations are explicit and tested against saved fixtures before release. Unknown optional fields must be tolerated; unsupported required renderer features must produce a clear compatibility message.

## 7. Architecture recommendation and unresolved decisions

### Stable boundaries to implement now

The mobile screens should call feature-owned interfaces rather than import Python internals:

- `MediaImportPort`: pick, inspect, retain/delete local media.
- `AnalysisPort`: `analyze(sourceRef, options) -> AnalysisProposal`; cancellation and partial results are explicit.
- `RecipeRepository`: save/load/version/duplicate/delete recipes and user decisions.
- `SuggestionPort`: return typed suggestion cards with rationale and source type; no automatic application.
- `PreviewPort`: render/seek a recipe preview and surface unsupported capabilities.
- `RenderPort`: render immutable recipe + filled-slot snapshot to a local MP4 and return validation metadata.

Each interface lives with its owning feature or a small shared contract package. Adapters are swappable and individually documented. Keep sample adapters labelled as sample and avoid mixing sample data with a real source project.

### Decision: Expo remains a reversible UI choice

The current app is Expo/React Native. This can remain the interface layer while media work is behind native/service ports. Expo documents local native modules in Swift/Kotlin and development builds for capabilities that need native code; that permits adding a measured media adapter without moving every screen to another framework. [Expo custom native code](https://docs.expo.dev/workflow/customizing/), [development builds](https://docs.expo.dev/develop/development-builds/introduction/).

### Analysis location: prototype both before choosing

No final local-vs-server selection is justified by current evidence. Use a thin `AnalysisPort` and compare:

1. **Local native sampling/cut detection:** stronger media privacy and offline use; requires Swift/Kotlin media decode and parity work, possible custom Expo module, device-floor/performance evidence.
2. **Ephemeral server analysis using Python/PyAV + PySceneDetect:** reuses current Python work and enables faster detector iteration; adds upload consent, secure transport/storage, service cost/latency, deletion and breach obligations, plus connectivity dependency.

For the first technical spike, use consented/synthetic fixture clips, record transfer and end-to-end latency, and delete test uploads. If server analysis wins initial feasibility, require explicit opt-in per source, bounded upload size, short-lived encrypted storage, deletion on success/cancel/expiry, no use for model training, and a documented incident/deletion process. Provide manual local section editing when network analysis is unavailable. Do not silently upload media.

PySceneDetect is a plausible experimental component: it offers several cut detectors and the project's license is BSD-3-Clause. Verify dependency/transitive codec licensing and packaging before shipping; BSD licensing for the detector does not determine the license obligations of FFmpeg or other bundled codecs. [PySceneDetect methods](https://www.scenedetect.com/docs/latest/api/detectors.html), [PySceneDetect license](https://github.com/Breakthrough/PySceneDetect/blob/main/LICENSE).

### Rendering: defer framework lock until parity spike

Android Media3 `Composition` can represent multiple video/audio/image sequences and is shared by preview/export, but current docs list video/audio crossfades as unsupported; `CompositionPlayer` is marked early preview. [Media3 Composition](https://developer.android.com/media/media3/transformer/composition), [CompositionPlayer preview](https://developer.android.com/media/media3/transformer/compositionplayer).

Apple AVFoundation supports mutable compositions and export sessions with video composition instructions. [AVMutableComposition](https://developer.apple.com/documentation/avfoundation/avmutablecomposition), [AVAssetExportSession](https://developer.apple.com/documentation/avfoundation/avassetexportsession).

Before enabling a feature on both platforms, render the same recipe and compare: selected section in/out points, concatenation order, crop, text overlay, source-audio mute/replacement, audio sync, output rotation, color/HDR handling, interruption/cancel/retry, and decoded export versus preview. Until the bake-off is complete, restrict transitions to cuts and simple fades only if both implementations pass; do not promise visual parity based solely on API availability.

## 8. Research and validation plan

### Dataset

Assemble a permissioned evaluation set of short videos with no public redistribution requirement. Include song/beat edits, film/cinematic montage, action, comedy, dialogue/story, tutorial/product, and clips with attached or split-screen content. Vary complete/partial starts and endings, portrait/landscape/square, 24/30/60fps, low/high compression, low light, flashes, camera motion, subtitles, no-audio, speech, music, and overlap. Keep source identity and consent metadata separate from annotations.

Have at least two annotators mark shot boundaries, useful reusable sections, role tags (including â€œunknownâ€), unwanted spans, and replacement prompts; adjudicate disagreements. Measure inter-annotator agreement before treating a role as an objective ground truth.

### Detector and experience measures

- Boundary precision/recall/F1 within predeclared time tolerances and per-content-family results.
- Merge/split correction count and correction time per clip.
- Fraction of users who understand/Edit/Keep/Exclude correctly without coaching.
- Time to a saved usable recipe, abandonment point, and manual fallback rate.
- Suggestion acceptance/edit/skip rate and user's explanation of why an idea fits.
- Analysis failure, cancel, timeout, upload size, memory, battery, and render/preview divergence.
- Whether users understand retained source content and rights statements after task completion.

Do not choose detector thresholds or publish accuracy claims from a handful of demo videos. First gather a baseline, then set release limits per clip family and device tier. Automatically exclude nothing. Where confidence is uncalibrated, display an uncertainty label, not a percentage.

### Usability tasks

1. Import a 25-second funny video with an unwanted intro, fix one wrong boundary, exclude intro, rewrite the punchline, preview and save.
2. Import a beat edit with 8 quick cuts; merge or group cuts into 3 reusable slots and select beat-preserving timing.
3. Import an action clip with camera movement; correct an over-detected flash/cut and replace the section with user footage.
4. Import a partial dialogue clip; accept that context is missing, create a manual section, use a new caption/audio, and identify any reference material remaining.
5. Interrupt analysis/rendering, reopen the draft, and verify user decisions persist.

Test novice creators and experienced short-form editors; include large text scaling, screen reader navigation, reduced motion, and RTL layout. The key usability measure is whether the user can understand and correct the recipe, not whether an AI label looks convincing.

## 9. Release gates

### Gate 1 â€” Workflow truthfulness

Demo data is separated from real projects; source, analysis proposal, user decision, and final recipe have visibly distinct states; an analysis failure can be completed manually.

### Gate 2 â€” Section editing

On representative devices, users can trim/split/merge/reorder and mark Edit/Keep/Exclude with undo. Tests confirm excluded spans never enter the output plan, and rerunning analysis never overwrites user edits.

### Gate 3 â€” Replacement and rights comprehension

Users can tell prompt ideas from supplied assets, can choose their own media, and do not interpret audio/text changes as a rights guarantee. Any retained reference media is explicit before save/export.

### Gate 4 â€” Preview/export parity

Supported effects preview and export consistently on iOS and Android within agreed frame/audio tolerances. Unsupported effects are rejected or removed with explanation before render; exports reopen and validate as MP4.

### Gate 5 â€” Privacy and recovery

Processing location and retention are disclosed. Cancel, deletion, low storage, app interruption, network failure, and render failure preserve the recipe and user's explicit decisions and do not leave undeclared source copies.

## 10. Decisions for the next implementation increment

1. Build a real project-state model and interfaces around current screens; leave the visible workflow intact.
2. Add explicit manual section creation and the Edit/Keep/Exclude persisted decision model before integrating analysis.
3. Create a small consented clip evaluation set and compare PySceneDetect-based cut proposals with manual annotations; include no-audio and motion-heavy cases.
4. Implement local import metadata and local draft persistence; do not require accounts for the first private workflow.
5. Run the local-vs-ephemeral-server analysis and iOS-vs-Android renderer spikes before committing to those execution models.
6. Add replacement prompts as transparent, user-approved cards. Defer generated people/backgrounds and any public marketplace.

This sequence produces a useful, testable product even if automatic semantic interpretation or advanced generative replacement is not ready.

## 11. Sources checked for this specification

Official or project-maintained technical documentation checked 2 October 2026:

- PySceneDetect [detector API](https://www.scenedetect.com/docs/latest/api/detectors.html), [CLI guidance](https://www.scenedetect.com/docs/latest/cli.html), [BSD-3-Clause license](https://github.com/Breakthrough/PySceneDetect/blob/main/LICENSE).
- Expo [custom native code](https://docs.expo.dev/workflow/customizing/), [development builds](https://docs.expo.dev/develop/development-builds/introduction/).
- Android [Media3 Composition](https://developer.android.com/media/media3/transformer/composition), [CompositionPlayer](https://developer.android.com/media/media3/transformer/compositionplayer).
- Apple [AVMutableComposition](https://developer.apple.com/documentation/avfoundation/avmutablecomposition), [AVAssetExportSession](https://developer.apple.com/documentation/avfoundation/avassetexportsession), [Vision person mattes](https://developer.apple.com/documentation/vision/applying-matte-effects-to-people-in-images-and-video).
- U.S. Copyright Office [music rights overview](https://www.copyright.gov/engage/docs/recording.pdf), [fair-use FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html).
