# MVP Architecture and Build Plan

**Status:** Provisional planning note. The [technology and design research](../research/mvp_technology_and_design_research.md) is the current decision study; no production stack or renderer is approved.  
**Product scope:** Editable templates created from reference videos; users fill template slots, preview, render, and download a standard video file. Arbitrary extra clip insertion and direct publishing are later capabilities.  
**Related:** [Product blueprint](mvp_product_blueprint.md), [competitive research](../research/product_strategy_and_competitive_research.md), [technology and design research](../research/mvp_technology_and_design_research.md), [software evolution and AI change-safety plan](../research/software_evolution_and_ai_change_safety.md)

## 1. Recommendation

No production stack is selected. Expo/React Native, Flutter, native rendering, and local/server/hybrid processing remain candidates for the comparative study. The durable template recipe should be independent of the UI and renderer; the existing Python package is a prototype, not an assumed production service.

The decision gate is evidence from representative clips and devices: preview/export parity, editing feature coverage, speed, memory, reliability, privacy, operational cost, and the current team's ability to maintain the result. See the technology and design research for the proposed bake-off. Do not scaffold the production app around a presumed stack before that gate is passed.

## 2. Product boundary for version 1

### Included

- Import a local reference video up to 30 seconds.
- Analyze and split it into editable sections; let the user edit, keep, or exclude each section.
- Edit or replace text, sound/audio, visual elements, backgrounds, and supported media slots.
- Offer optional replacement ideas, with source and license information where applicable.
- Preview the proposed template and confirm it.
- Save, reopen, revise, duplicate, and reuse the editable template in the app.
- Fill defined template slots with user-selected footage/images.
- Render and download the resulting video file to the device.

### Deferred

- General-purpose timeline with arbitrary clips before/after a template.
- Direct posting APIs or social account integration.
- Public template marketplace, creator payouts, and community graph.
- Unlimited generative replacement; initial capability is constrained to supported subjects/scenes and must pass quality testing.
- General professional multitrack finishing editor; consider a bounded follow-on only after validating export handoff pain and demand.
- Public profiles, notifications beyond opted-in operational render status, and subscriptions until product value, cost, and policy requirements are validated.

## 3. System view

```text
┌───────────────────────────────────────────────┐
│ Mobile app: React Native + Expo + TypeScript  │
│ Import • section review • recipe editor       │
│ template library • preview • export controls  │
└────────────────┬────────────────────┬─────────┘
                 │                    │
      analysis API (optional)   native render bridge
                 │               ┌────┴────┐
┌────────────────▼─────────────┐ │         │
│ Python analysis service      │ │ Android │ iOS
│ existing PyAV / models       │ │ Media3  │ AVFoundation
│ scene/cut/metadata proposals │ │ export  │ export
└──────────────────────────────┘ └─────────┴─────────┘
                    │
              TemplateRecipe
        versioned, platform-independent
```

The analysis service should return proposals and evidence, not a rendered template. The recipe is the durable product artifact. A platform renderer consumes the same recipe and produces a video file; renderer-specific implementation details must not leak into the saved recipe.

## 4. Major components

### Mobile application

- **Import manager:** local media picker, 30-second validation, metadata probe, orientation/audio checks, clear errors.
- **Analysis/review UI:** progress states, contact sheet/section cards, timestamp corrections, Edit/Keep/Exclude actions, confidence indicators.
- **Recipe editor:** section order/timing, media placeholders, text/audio/visual controls, replacement suggestions, rights/source labels.
- **Template library:** private saved templates, duplicate/rename/delete, version history, starter examples.
- **Preview:** play the recipe with current selections and surface unsupported effects before render.
- **Export manager:** device resources check, progress, cancel/retry, MP4 file save, completion/share-sheet entry point (share sheet only; no platform publishing API in v1).

### Python analysis service

Reuse current ingestion/decoder models as a prototype, but separate analysis from app-facing contracts. Add authenticated job API, upload/temporary storage, schema validation, job status, cleanup/retention, versioned analysis outputs, and explicit 30-second gate. Avoid passing local filesystem paths to mobile clients. The service must never assume a successful probe means the user has rights to republish the video.

### Native renderer

- **Android:** Media3 Transformer supports trimming, cropping, effects, overlays, audio processing, previewing edits, and MP4 export. Multi-asset composition is supported, but current composition limitations include lack of crossfading tracks; validate needed transitions before adopting a recipe feature that depends on them. [Transformer](https://developer.android.com/media/media3/transformer), [editing app guide](https://developer.android.com/media/implement/editing-app), [composition guide and limitations](https://developer.android.com/media/media3/transformer/composition).
- **iOS:** AVFoundation provides time-based composition from audio/video tracks, video compositing, transitions, audio mixing, and export. [Apple video overview](https://developer.apple.com/documentation/technologyoverviews/video), [video composition](https://developer.apple.com/documentation/avfoundation/avvideocomposition).
- Keep the native bridge small: create preview/export from a validated recipe, report progress/errors, cancel export, save output. Keep product logic and template schema in TypeScript/Python, not duplicated across Swift and Kotlin.

### Analysis and rendering boundary

Use analysis output for section suggestions: timestamps, labels, evidence references, and confidence. The user's reviewed choices become the recipe. Rendering must use the recipe plus user-approved assets; it must not silently include source segments the user excluded or apply unapproved generated suggestions.

## 5. Template recipe requirements

Every saved recipe needs:

- Schema version and stable template ID.
- Creative format tags: music/beat edit, cinematic/film, action, comedy/funny, dialogue/story, tutorial, product showcase, and extensible tags.
- Section order and role; target/min/max duration; optional/excluded status.
- Media slot prompt, accepted asset types, crop/framing behavior, and required status.
- Text layers with content, style, timing, editable/locked state, and localization-ready fields.
- Audio layers with source, timing, trim/loop/volume/fade, voiceover/effect roles, license/usage scope, and editable state.
- Visual layers and supported transformation instructions, temporal range, preview/export fallback, and confidence if AI-proposed.
- Beat markers where the format relies on music synchronization; no mandatory beat grid for dialogue, comedy, action, or story formats.
- Output profile: max duration, aspect ratio, resolution, frame rate, safe areas, audio mix target, and renderer capabilities.
- Provenance and lineage: reference asset identifier, analysis version, user-confirmed edits, chosen assets, generation metadata, and rights declarations.

Do not store the reference video itself inside a public template by default. Store edit instructions and placeholders. For private user projects, preserve original media only under an explicit retention policy.

## 6. Privacy, rights, and safety baseline

- Make the user affirm they have permission to submit the reference and any replacement assets.
- Distinguish analysis/inspiration from permission to republish media.
- Default templates to private; user must explicitly choose any future sharing.
- Keep asset provenance and license limits available at edit and export time.
- Provide delete source, delete project, and retention controls.
- Do not imply that changing a song, tone, text, character, or background clears rights to remaining footage or underlying works.
- Before enabling public templates, add moderation, reporting, takedown, attribution, and creator-permission workflows.

## 7. First technical spike: prove render quality and portability

Build a throwaway end-to-end rendering prototype before a large UI implementation. Use a small set of synthetic or user-authorized media samples representing:

1. A beat-synced montage with text overlays and replacement clips.
2. A dialogue/story clip with original audio muted and a licensed music bed or voiceover.
3. A comedy/action clip with variable timing and a transition.
4. A background or person replacement on a supported shot, including a difficult motion example.

For each, define the recipe once and compare iOS/Android preview and output. Measure:

- Preview-to-export visual consistency.
- Export success across low-, mid-, and high-tier devices.
- Render time, memory use, thermal behavior, file size, and battery impact.
- Audio/video synchronization and crop/orientation correctness.
- Text and overlay positioning across aspect ratios.
- Results for slow/fast motion, occlusion, hair, low light, and camera cuts in visual replacement.
- Whether native APIs support the transitions/effects needed by the first template set.

If either platform cannot meet minimum visual parity or export reliability, reduce supported effects for v1 or move rendering to a controlled server pipeline after privacy and cost review. Do not make cross-platform parity a promise before measuring it.

## 8. Suggested build sequence

### Phase A — Research and decision gate

- Validate the creator workflow and establish launch market, language, device floor, and target export constraints.
- Prepare representative, consented samples and manually annotated expected sections for the selected formats.
- Keep the existing `TemplateRecipe` as a draft contract; do not freeze its schema until timing, layers, rights, and renderer capability questions are resolved.
- Decide data retention, rights acknowledgment, max upload size, and whether any footage may leave the device.

### Phase B — Comparative technology spike

- Compare viable UI/framework and renderer paths against the agreed weighted criteria.
- Implement the smallest end-to-end recipe-to-preview/export proof on iOS and Android.
- Validate downloads, permissions, export cancellation, device performance, privacy, and preview/export parity.
- Record the chosen stack, rejected options, evidence, and reversible decision boundary before production scaffolding.

### Phase C — Contract and interaction prototype

- Finalize versioned recipe and analysis contracts based on spike results.
- Prototype section cards, compact timeline, and detailed timeline with target creators.
- Confirm the smallest supported template families and visual transformation set.

### Phase D — Mobile vertical slice

- Implement import, analysis job status, section review, Edit/Keep/Exclude, replacement ideas, editable audio/text/visual controls, preview, save template, fill slots, export/download.
- Keep the app's first library private and small.
- Run moderated usability sessions and analyze correction burden.

### Phase E — Limited pilot

- Pilot with a small creator cohort and supported device range.
- Track first export completion, time to first export, second-use rate, render failure rate, rights confusion, and visual-edit artifact reports.
- Expand template families only when the renderer and template workflow remain understandable.

### Phase F — Later editor capabilities

- Evaluate a bounded finishing editor only if creator research shows material pain after MP4 handoff; scope its first clip/audio/text capabilities separately from a professional editor.
- Add richer multitrack editing, direct social integration where available, and public template publishing only after demand and moderation/legal readiness.

## 9. Quality bar

Do not call the MVP ready because the app launches. For each supported recipe family:

- A first-time user can complete the core flow without help.
- The app explains what it found and lets the user correct it.
- The preview matches the downloaded output closely.
- Excluded sections and unapproved assets do not enter the render.
- Audio stays synchronized and the output opens in major mobile editors.
- Failed exports recover cleanly without losing the template.
- Unsupported media/effects fail with an actionable message.
- User data and media can be removed according to the documented retention behavior.

## 10. Open decisions before a production commitment

1. Confirm the first target market, initial languages, and creator segment.
2. Set device floor, output resolutions, max import file size, and quality/latency targets.
3. Decide on-device vs server analysis after a privacy, accuracy, and cost spike.
4. Decide what visual replacement means for v1: non-generative mask/compositing, licensed/generated asset substitution, or a limited generative workflow.
5. Choose licensed audio source and define platform-specific usage rights.
6. Choose whether render assets remain fully local or temporary upload is allowed for AI operations.
7. Determine whether the Python package becomes the API service or stays as an offline analysis prototype.
8. Decide whether local accountless creation is feasible, what cloud features require sign-in, and which identity provider/security controls to adopt.
9. Validate recurring user value and AI/storage costs before selecting monetization or subscription tiers.
10. Measure post-export editing behavior before planning an in-app finishing editor.
11. Select framework-appropriate feature boundaries, schema migration tooling, and automated change checks while preserving the required modular-monolith and scoped-change principles.

## 11. Current workstation readiness

Environment inspection on 1 October 2026 found:

- Windows machine with Node.js 24.14.0 and npm 11.12.1. Expo's current project guide requires Node.js LTS; this Node version is suitable if it remains on the LTS line.
- Android Studio is installed, with its bundled OpenJDK 21.
- Android SDK platforms 34, 35, 36, and 36.1, build tools, platform tools, emulator, and Pixel 9 Pro / QuantBot_Test virtual devices are present.
- Android SDK Command-Line Tools (`cmdline-tools`) were not found. Android Studio can manage SDK packages through SDK Manager; install **Android SDK Command-line Tools (latest)** there only if the build tooling requires it.
- `python` resolves to the Windows Store execution alias and did not launch. The existing backend requires Python 3.11 or later. Install or repair Python 3.11+ before running the Python analysis service locally; mobile UI work can proceed before that.
- This workstation is Windows, so it cannot compile iOS natively with Xcode. iOS development builds can be produced with Expo Application Services from Windows, or locally on a Mac. Testing native iOS rendering needs access to an iOS device/build or a Mac with Xcode; publishing later requires the relevant Apple developer setup.
- ADB reported a `.android` directory permission/configuration error during environment inspection. Android SDK and emulators exist, but check/fix the ADB user-home configuration if device installation fails.

**Manual install summary:** no new Android Studio or Node installation is needed. The only prerequisite to run the current Python analysis locally is a working Python 3.11+ installation. Android command-line tools are a conditional SDK Manager install, and iOS requires cloud build access or a Mac for native testing.

## 12. Sources

- Expo supports custom native code and local Swift/Kotlin modules in development builds: [Custom native code](https://docs.expo.dev/workflow/customizing/), [Expo Modules API](https://docs.expo.dev/modules/module-api/).
- Expo provides media library access and saving assets, but media playback/library APIs do not themselves implement the product's editing/render graph: [Expo MediaLibrary](https://docs.expo.dev/versions/latest/sdk/media-library/), [Expo Video](https://docs.expo.dev/versions/latest/sdk/video/).
- Android native export and effect pipeline: [Media3 Transformer](https://developer.android.com/media/media3/transformer), [build a basic editing app](https://developer.android.com/media/implement/editing-app), [composition and limitations](https://developer.android.com/media/media3/transformer/composition).
- Apple's native composition/export APIs: [AVFoundation video overview](https://developer.apple.com/documentation/technologyoverviews/video), [AVVideoComposition](https://developer.apple.com/documentation/avfoundation/avvideocomposition).
- Flutter can also bridge to native Kotlin/Swift through platform channels: [Flutter platform channels](https://docs.flutter.dev/platform-integration/platform-channels). It remains a viable alternative; the recommendation favors Expo/React Native to share a TypeScript interface with the existing Python service boundary, not because Flutter lacks native access.
