# MVP Technology and Design Research

**Prepared:** 1 October 2026  
**Purpose:** Make architecture and product-design decisions from evidence before building the mobile application.  
**Scope:** iOS + Android, reference videos up to 30 seconds, editable in-app templates, template-based MP4 export/download. A general-purpose multitrack editor and direct publishing are later phases.  
**Status:** Decision study; stack recommendations remain provisional until the comparative spike is complete.
**Frontend detail:** The screen-by-screen interaction and layout proposal is in the [mobile frontend design specification](../design/mobile_frontend_design_spec.md); it is a testable design direction, not a final visual identity.
**Account/lifecycle detail:** See [account, security, monetization, and editor scope research](account_security_monetization_and_editor_scope.md) for sign-in, settings, privacy, notification, subscription, and editor boundaries.
**Evolution/change-safety detail:** See [software evolution and AI change-safety plan](software_evolution_and_ai_change_safety.md) for modular feature boundaries, compatibility, migrations, and safe AI-assisted upgrades.

## 1. Executive recommendation

Do not commit the product to one framework or renderer based on familiarity alone. Run a short, controlled feasibility spike for the highest-risk paths: analyzing real clips, previewing a recipe, replacing a background, mixing text/audio/effects, and exporting a playable file on both iOS and Android.

The current evidence supports this direction:

1. Use a **cross-platform mobile UI** if the team can keep platform-specific rendering behind a small native adapter. Expo/React Native and Flutter both support this architecture; neither removes the need to validate iOS and Android rendering separately.
2. Keep a **platform-independent, versioned `TemplateRecipe`** as the durable product asset. It represents user-approved edit instructions and placeholders, not a copy of the source video.
3. Decide between **on-device, server, and hybrid analysis/rendering** with measurements of quality, latency, cost, privacy, low-end device performance, and preview/export parity.
4. Design around **versioned output profiles**, not hard-coded assumptions about one platform. Social platforms change duration rules, UI overlays, safe areas, codecs, and publication flows.
5. Make the first visual AI promise narrow and testable. **Background replacement using a tracked person mask** is a different capability from **generating a replacement person/character while preserving the original performance**. The latter is a high-risk research feature and should not be claimed until it is demonstrated on varied motion.
6. Design the user journey as a guided video craft workflow: **inspect sections → edit/keep/exclude → receive optional replacement ideas → preview → confirm/save template → fill its slots → preview/export/download**. Show a detailed timeline only when users need it.

## 2. Product definition to protect during technology decisions

### First release

- User imports a complete or partial reference video up to 30 seconds.
- The app proposes sections with timestamps, thumbnails, labels, and uncertainty.
- For each section, the user selects Edit, Keep, or Exclude and can repair boundaries/order.
- The app suggests shot ideas and optional alternatives for media, text, audio, and visual treatment.
- Users can replace/mute audio, edit text, swap media, and apply supported visual/background edits.
- The user previews the proposed template and confirms it.
- The editable template stays saved in the app. The user fills defined sections, renders and downloads a standard video file, and may continue editing that file in another editor.

### Explicit later release

- Add arbitrary clips outside the template sections in a general timeline.
- Compose longer videos from several templates and new clips.
- Direct social account posting and public community publishing.

Do not let implementation convenience move these capabilities into or out of the MVP without user validation.

## 3. Social-platform flexibility research

### Findings

- TikTok for Business recommends vertical 9:16 creative, high-resolution assets, and keeping key content in the safe zone. Its official guidance also ties safe-zone geometry to creative format and UI overlays. These are advertising references; organic surfaces can differ. [TikTok Creative Codes](https://ads.tiktok.com/business/en-US/creative-codes), [TikTok ad safe-zone specs](https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads).
- Meta’s Reels advertising guidance similarly recommends vertical 9:16 video, audio, and safe-zone placement for key messages. It provides a Reels safe-zone checker for ad creative. This is ad guidance, not a guarantee of identical organic UI in every app version. [Meta Reels ads guidance](https://www.facebook.com/business/ads/facebook-instagram-reels-ads).
- YouTube classifies square or vertical uploads up to three minutes as Shorts for standard channels, subject to policy and music-claim caveats. The product’s 30-second limit is therefore a chosen product constraint, not the current maximum for every destination. [YouTube Shorts eligibility](https://support.google.com/youtube/answer/15424877?hl=en-EN).
- TikTok and Meta feature distinct UI overlays and placement formats; safe areas can change with captions, buttons, device geometry, and format. One universal safe-zone rectangle will age badly.

### Design requirements

- Separate **reference import limit**, **template target duration**, and **destination profile limits**. They are different constraints.
- Store output profiles as versioned data: platform/surface, aspect ratio, resolution, frame rate, codec/container, duration guidance, safe-area overlays, and date/source checked.
- Offer a neutral “vertical social” profile plus explicit TikTok, Instagram/Facebook Reels, and YouTube Shorts previews. Always label a profile as guidance and let the user see/correct cropping.
- Let users preview important text and subjects under simulated interface chrome. Use the correct regional layout when known (for example, TikTok documents distinct Arabic RTL advertising safe-zone files).
- Keep profile rules updateable without migrating each saved template. The recipe describes content and composition; the profile describes how to frame/export it now.
- Export a compatible video file and leave upload/posting to the destination app in v1.

### Design implication

The template itself should be aspect-ratio-aware but not platform-locked. Render preview and export from the same profile definition. Crop should have a focal point/subject anchor and a reviewable fallback; do not stretch source footage.

## 4. Technology options and selection method

### Mobile UI framework

| Option | Strengths for this product | Risks / costs | Evidence and decision |
|---|---|---|---|
| React Native + Expo + TypeScript | Shared iOS/Android UI; fast iteration; camera/media libraries; existing workstation has Node; Expo supports local Swift/Kotlin modules and development builds. | Expo Go cannot exercise arbitrary custom native modules; video engine still needs platform code; native module/toolchain upgrades can disrupt builds. | Strong candidate for rapid guided UI, not automatically the renderer choice. [Expo native code](https://docs.expo.dev/workflow/customizing/), [Expo development builds](https://docs.expo.dev/develop/development-builds/introduction/). |
| Flutter | Shared UI with consistent custom-rendered controls; supports Kotlin/Swift platform channels and Pigeon typed bridges. | Dart is a separate implementation language; video timeline/preview still requires native integration; some platform plugins may not expose needed export behavior. | Viable alternative; prove bridge complexity and team ability in the same spike. [Flutter platform channels](https://docs.flutter.dev/platform-integration/platform-channels). |
| Native Swift + Kotlin | Direct access to platform media APIs and best control over platform-specific behavior. | Two app UIs, duplicated product logic/design implementation, higher initial delivery and ongoing maintenance cost. | Consider only if shared framework blocks preview/export quality or a confirmed platform-specific capability is essential. |

### Weighted decision process (proposed, scores assigned after spike)

Compare options against these criteria, with weights agreed before scoring:

| Criterion | Suggested weight | Why it matters |
|---|---:|---|
| Preview-to-export fidelity on both OSes | 25% | User must trust that saved output matches preview. |
| Native video/audio APIs and effect feasibility | 20% | Rendering is a core product capability, not an add-on. |
| Development speed and maintainability for current team | 15% | Needed for constrained MVP and repeated iteration. |
| Device range, render time, memory, battery | 15% | Short video export can still stress low/mid devices. |
| Privacy/offline behavior and media retention | 10% | User footage and reference clips can be sensitive. |
| UI accessibility and adaptive layout quality | 5% | Mobile-first must work across device settings and abilities. |
| Build/release friction from the current Windows workstation | 5% | iOS testing has a Mac/cloud dependency. |
| Ecosystem/licensing/supply-chain risk | 5% | Impacts long-term maintenance, costs, and distribution. |

Score each criterion with evidence (prototype, official API support, measured output, or team capability), not preference. A critical failure in fidelity, privacy, or export reliability is a veto even if the weighted score is high.

### Provisional framework direction

Expo/React Native is a reasonable starting candidate because a shared TypeScript UI and custom Swift/Kotlin modules are supported. But commit only if the prototype confirms the native bridge can preview and export the required subset reliably. Flutter should remain in the bake-off until the team and product constraints are known. The app framework and renderer are separate decisions.

## 5. Rendering and media-processing architectures

| Architecture | Benefits | Risks | Best fit / investigation |
|---|---|---|---|
| Fully on-device | Keeps media local; works offline after templates/assets are available; no per-render server cost; immediate local file access. | Device codec variability, heat/memory, longer renders, two native implementations, cross-platform output differences. | Strong privacy and download UX. Test low/mid devices and preview/export parity. |
| Fully server-side | One render implementation/output profile; easier to run large models; consistent logs and rollback. | Upload wait/bandwidth, infra cost, retention/security obligations, failures under poor connectivity, local camera-roll output still needs download. | Useful for heavy generative transformations if costs and privacy can be controlled. |
| Hybrid | Run metadata/cuts and ordinary editing locally; send only opted-in frames/clips for heavier AI; or render locally and use remote analysis. | More states and contracts, transfer/consent complexity, version skew between local/native and backend tools. | Likely practical if each operation is explicitly classified and user sees where processing happens. |

### Native render evidence

- Android Media3 Transformer supports editing, trimming, crop, effects, overlay, audio processing and MP4 export. Its multi-asset `Composition` can combine video/image/audio. However, Android’s current documentation says crossfading video/audio tracks is not supported in `Composition`; `CompositionPlayer` is marked early preview and lists multi-asset preview as under active development. These limits could directly affect music/cinematic template families. [Transformer](https://developer.android.com/media/media3/transformer), [composition limits](https://developer.android.com/media/media3/transformer/composition), [preview status](https://developer.android.com/media/media3/transformer/compositionplayer).
- Apple AVFoundation supports composition and export of media tracks, transitions, audio mixes, and video composition instructions. Its surface differs from Android’s APIs, so equivalent recipe behavior must be tested rather than assumed. [AVFoundation video](https://developer.apple.com/documentation/technologyoverviews/video), [AVVideoComposition](https://developer.apple.com/documentation/avfoundation/avvideocomposition).
- Expo MediaLibrary/Video support media access/playback/save, but those packages are not a complete edit graph/export engine. Custom native modules are an expected route for platform-specific editing. [Expo MediaLibrary](https://docs.expo.dev/versions/latest/sdk/media-library/), [Expo native modules](https://docs.expo.dev/workflow/customizing/).

### Render decision gate

Do not commit to native rendering merely because both OS vendors expose editing APIs. Before committing, run one renderer proof on both platforms for:

1. cut/trim/concatenate selected sections;
2. animated text/caption overlay;
3. replace/mute source audio and mix a licensed music or voice track;
4. beat marker timing with stable sync;
5. crop/reframe a landscape clip to vertical with safe-area text;
6. preview the exact same recipe and compare frame samples/audio timing against exported MP4;
7. cancel/recover render on constrained hardware.

If platform parity is poor, consider a controlled server renderer or restrict v1 features. Do not silently give iOS and Android different template behavior.

## 6. Analysis and AI capability feasibility

### Video segmentation and section roles

Existing code extracts technical metadata and decodes frames; it does not provide a validated scene/story segmentation model. Candidate section proposals should combine cut detection, sampled visual/audio cues, and user correction. A model can propose “hook,” “setup,” “payoff,” “punchline,” or “CTA,” but these labels are interpretations and must be editable.

**Research action:** create an authorized sample set across song/beat edit, film/cinematic, action, comedy/funny, story/dialogue, and tutorial. Have people manually annotate cuts and section roles. Compare methods for boundary F1, role agreement, confidence calibration, processing time, and correction minutes per clip.

### Person/background replacement

- Apple Vision can produce person segmentation masks frame by frame and sample code demonstrates compositing a replacement background. Current documented person segmentation is a mask operation, not realistic new-person generation. [Apple person segmentation for video](https://developer.apple.com/documentation/vision/applying-matte-effects-to-people-in-images-and-video).
- MediaPipe Image Segmenter exposes image, video, and live-stream modes and returns category/confidence masks; iOS samples accept video frames. It requires choosing and packaging compatible model assets. [MediaPipe Image Segmenter](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/ImageSegmenterOptions), [iOS segmentation guide](https://ai.google.dev/edge/mediapipe/solutions/vision/image_segmenter/ios).
- A segmentation mask can support background replacement, cutout-style overlays, and selective effects. It does not by itself synthesize a photorealistic replacement character or preserve identity, clothing, shadows, reflections, motion, and occlusion.
- Replacing a real person with a different person/character through generation is a separate and substantially higher-risk capability: temporal flicker, identity/likeness consent, misrepresentation, compute cost, and moderation must be researched independently.

### Capability staging recommendation

| Tier | User capability | MVP disposition |
|---|---|---|
| 1 | Replace a whole section with user-owned image/video; crop and trim. | Core template capability. |
| 2 | Change background behind a clearly detected person; apply stylized overlays/effects. | Candidate for MVP only after quality/performance bake-off on both OSes. Make unsupported shots fail gracefully. |
| 3 | Replace selected person/character while preserving the original performance; semantic object removal/inpainting across video. | Research/roadmap item, not a general MVP guarantee. Prototype on consented media and publish quality limits. |

### Audio/text suggestions

Template recipes need distinct editable tracks for original source sound, replacement music, voiceover, effects, captions, and titles. Preserve text's creative function (e.g. setup or punchline) while generating new wording; let the user control tone, language, voice, and timing. Music rights, sound recording/composition rights, and destination permissions are independent fields; changing audio/text does not clear rights in remaining video. A reviewed source/rights workflow is required.

## 7. Design direction: accessible, flexible, creator-first

### Interaction principles

1. **Progressive disclosure:** section cards and simple decisions first; optional detailed timeline afterward.
2. **Show, then edit:** each section card includes thumbnail, time range, length, role, confidence/uncertainty, and actions Edit / Keep / Exclude.
3. **Explain recommendations:** replacement suggestion says what to film/use and why it matches the section; it is never automatically applied.
4. **Preview before commitment:** preview selected sections and proposed text/sound/visual edits before confirming the template; later preview the generated file before download.
5. **Reversible changes:** undo/restore and template versions protect experimentation.
6. **Separate template from rendered video:** template is editable in-app; exported MP4 is a flattened output the user may continue editing elsewhere.
7. **Format-aware, not format-forced:** music edits use beat timing; jokes need setup and payoff timing; action may need impact/speed timing; stories/tutorials may need speech-led sections. Let a template use multiple tags.
8. **Honest AI:** mark uncertain boundaries/masks, explain limitations, and provide a manual path.

### Screen model

1. **Start:** Create from a reference / Browse curated ideas / My templates.
2. **Import:** duration and basic media facts; explain analysis/rights; reject >30 seconds before full processing.
3. **Analyze:** honest stage progress and recoverable error state.
4. **Review sections:** preview plus scrollable section cards; combine/split/trim/reorder; choose Edit, Keep, Exclude.
5. **Adapt:** replacement ideas, media selection, text rewrite, audio replacement/tone, background/visual edit when supported.
6. **Template preview:** source visual vs proposed output, included sequence, runtime, placeholders, rights/source summary; confirm/save.
7. **Template library:** reopen, edit, duplicate, manage versions.
8. **Create video:** fill section slots with user's own media, preview fit, adjust text/sound, generate output.
9. **Export:** downloadable MP4, destination profile preview, progress/cancel, output issue warnings.

### Social preview should be flexible

- Simulate platform chrome as overlays that can be updated or disabled.
- Make the user-visible safe area a profile property, not an immutable rectangle.
- Show both 9:16 output and crop previews for other selected aspect ratios.
- Allow subject focal point repositioning and text repositioning when the export profile changes.
- Do not insert platform branding/watermarks or claim direct integration when exporting a file.

### Accessibility and comfort

- Meet platform-native screen-reader semantics, clear text contrast, caption controls, and non-audio cues.
- Use large touch targets. Android guidance recommends at least 48dp for interactive Compose elements; WCAG 2.2 AA target-size criterion is 24×24 CSS px with exceptions, and Apple recommends platform-comfortable controls. [Android touch targets](https://developer.android.com/develop/ui/compose/accessibility/api-defaults), [WCAG target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum), [Apple accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility).
- Do not autoplay sound without clear controls; allow pause/mute and reduced motion where effects flash or move rapidly. [Apple video HIG](https://developer.apple.com/design/human-interface-guidelines/playing-video).
- Avoid relying on color alone to show section states; combine label, icon, and state text.

## 8. Data, contracts, and migration strategy

Separate these durable objects:

- `ReferenceVideo`: source identity, duration/probe result, storage locator, rights acknowledgment, retention/deletion status.
- `AnalysisProposal`: sections, timestamps, transcript/OCR/audio cues, model/tool versions, confidence, warnings. Recomputable and never mistaken for a user decision.
- `TemplateRecipe`: user-confirmed structure, sections, layers, replacement guidance, output profiles, source lineage, schema version.
- `TemplateVersion`: immutable snapshot/change history after confirmation.
- `EditSession`: a user filling a recipe with personal assets and overrides.
- `RenderJob`: renderer/version, recipe/edit snapshot, output profile, progress/cancel/error/output file reference.
- `AssetLicense`: origin, allowed use, attribution, platform/territory/expiry limits, and proof or confirmation.

Keep source video reference intervals and final template timeline positions separate. Excluded sections remain in analysis evidence but not the user-approved recipe. Never infer “user approved” from a model confidence score.

The recently added Python `TemplateRecipe` model is a **first contract prototype**, not a frozen schema. Research gaps before final freeze: timestamps after section retiming, layer overlap and transition semantics, audio rights representation, multi-language text, regional platform profiles, generated asset lineage, asset retention and external object storage, recipe migrations, renderer capability negotiation, and template versus render version IDs.

## 9. Privacy, legal, and trust research

- Changing music or wording alone does not guarantee clearance. The U.S. Copyright Office distinguishes musical works from sound recordings; rights are commonly separately owned. Its fair-use FAQ also states there is no universal amount of change that automatically authorizes a derivative use. Rules depend on jurisdiction and context; obtain qualified legal review for product rules. [Copyright Office music guide](https://www.copyright.gov/engage/docs/recording.pdf), [Fair Use FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html).
- Platform rules and music catalogs vary. Build the product around user-owned/licensed assets and explicit permissions, not downloading platform videos or reusing embedded tracks by default.
- Default templates and projects to private. Make upload purpose, server/on-device processing, retention, delete behavior, and AI usage visible.
- Before public sharing: moderation, reporting, takedown, likeness/deepfake rules, provenance, attribution, and license checks are required.
- Avoid product claims that outputs are copyright-safe or guaranteed viral. Explain the user's responsibility and the available asset license information.

## 10. Validation plan and decision gates

### Research before stack lock

1. Interview 12–20 creators across song edits, comedy, action, film/cinematic, story/dialogue, and tutorial/product categories. Ask them to demonstrate how they recreate a video and where they get stuck.
2. Usability-test section triage and replacement suggestions with novice and experienced editors.
3. Test three UI approaches: simple section cards, card + compact timeline, and detailed timeline. Select by task completion and correction burden, not aesthetic preference alone.
4. Get consented/sample videos from multiple devices, orientations, frame rates, compression levels, and lighting conditions.

### Technical bake-off

1. Choose the same recipe and media for Expo/native modules and Flutter/native channels, or justify a smaller comparison based on team expertise.
2. Render the same five required edits on Android and iOS; compare preview and export.
3. Benchmark local and server processing separately for first run and repeat run, on low/mid/high devices and poor network conditions.
4. Benchmark background masks and track stability; use a human quality rubric for edges, flicker, occlusion, exposure, and temporal consistency.
5. Produce a weighted decision record with implementation notes, cost estimate, known risks, and a reversible decision boundary.

### Gates

- **Gate A — User need:** users understand the section decisions and find replacement suggestions useful.
- **Gate B — Recipe clarity:** users can distinguish source analysis, confirmed template, and exported video.
- **Gate C — Renderer:** preview/export parity and file reliability meet target thresholds on both OSes.
- **Gate D — Visual AI:** only claim transformations that pass diverse clips and user review.
- **Gate E — Product/operations:** rights, privacy, storage, delete, and support procedures are ready for the chosen pilot.

Set numerical thresholds after baseline testing; avoid arbitrary accuracy promises beforehand.

## 11. Recommendations and unresolved decisions

### Recommend now

- Keep the 30-second source limit for the initial product but treat it as product scope, not universal social platform limit.
- Keep user-approved, editable section decisions and preview-before-confirm as core.
- Save the template in-app and export a rendered file; defer full timeline and direct posting.
- Keep the Python code as a video-analysis prototype, not yet the assumed production backend.
- Use a versioned platform-independent recipe and versioned destination profiles.
- Build no large public hub until creation and reuse have been validated with a small curated set.

### Do not decide without evidence

- Expo versus Flutter versus fully native.
- Local versus server render/analysis.
- Whether person/background replacement belongs in initial v1 or the first update.
- Which AI models/providers will be used and whether processing is on-device.
- Target device floor, max file size, resolution/bitrate, render-time target, and service costs.
- Which languages/markets launch first; this affects text length, RTL layout, captions, and licensed media.

## 12. Source notes

Current platform and API details were checked on 1 October 2026. Platform ad specifications are not assumed to be identical to organic requirements. Official sources:

- [Expo custom native code](https://docs.expo.dev/workflow/customizing/), [Expo development builds](https://docs.expo.dev/develop/development-builds/introduction/)
- [Flutter platform channels](https://docs.flutter.dev/platform-integration/platform-channels)
- [Android Media3 Transformer](https://developer.android.com/media/media3/transformer), [composition](https://developer.android.com/media/media3/transformer/composition), [CompositionPlayer](https://developer.android.com/media/media3/transformer/compositionplayer)
- [Apple AVFoundation video editing](https://developer.apple.com/documentation/technologyoverviews/video), [AVVideoComposition](https://developer.apple.com/documentation/avfoundation/avvideocomposition), [Vision person segmentation](https://developer.apple.com/documentation/vision/applying-matte-effects-to-people-in-images-and-video)
- [MediaPipe Image Segmenter options](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/ImageSegmenterOptions), [iOS guide](https://ai.google.dev/edge/mediapipe/solutions/vision/image_segmenter/ios)
- [TikTok Creative Codes](https://ads.tiktok.com/business/en-US/creative-codes), [TikTok safe-zone ad specs](https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads)
- [Meta Reels ads](https://www.facebook.com/business/ads/facebook-instagram-reels-ads)
- [YouTube Shorts rules](https://support.google.com/youtube/answer/15424877?hl=en-EN)
- [W3C WCAG 2.2 target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum), [Android Compose touch target](https://developer.android.com/develop/ui/compose/accessibility/api-defaults), [Apple accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [U.S. Copyright Office music guide](https://www.copyright.gov/engage/docs/recording.pdf), [fair use FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html)
- [CapCut documented mobile template workflow](https://www.capcut.com/help/use-and-export-templates-in-capcut), [Canva mobile video template features](https://www.canva.com/video-editor/mobile-app/)
- [Apple accessibility guidance](https://developer.apple.com/design/human-interface-guidelines/accessibility), [Android Compose touch-target guidance](https://developer.android.com/develop/ui/compose/accessibility/api-defaults)
