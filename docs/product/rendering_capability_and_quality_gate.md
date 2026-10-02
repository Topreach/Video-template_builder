# Mobile Rendering Capability and Quality Gate

**Status:** Technical decision research; no production renderer is selected.
**Updated:** 2 October 2026
**Related:** [Video-to-template workflow](video_template_workflow_spec.md), [coverage/decision map](mvp_coverage_and_traceability.md), [analysis signal strategy](video_analysis_signal_strategy.md), [MVP technology research](../research/mvp_technology_and_design_research.md), [feature map](../architecture/feature-map.md).

## 1. Decision being researched

The app needs to preview and export the same user-approved recipe on iOS and Android. The template model must express edit intent independently of native renderer APIs. A supported operation is not production-ready until it works in preview and export on the target device range, survives interruption/error cases, and produces a file that opens in other mobile editors.

### Current recommendation

Keep the Expo/React Native app as the UI shell and put rendering behind a narrow native-renderer interface. Run a small native proof using Android Media3 Transformer and iOS AVFoundation. Prefer local device rendering for the initial private workflow if the smallest useful effect set passes quality and performance gates. Keep a server-rendering option behind the same `RenderPort` only if device limits or cross-platform mismatch require it and a privacy/cost decision accepts uploading media.

Do not implement a professional timeline, arbitrary keyframes, generative replacements, or a catalog of effects before that proof. Do not describe native API feature lists as proof that all devices can handle a specific recipe.

## 2. Candidate architecture comparison

| Option | Strengths | Risks / costs | Use in MVP research |
|---|---|---|---|
| iOS AVFoundation + Android Media3, local | Source stays on device; no upload/service cost; device lifecycle and share/save flows are native; both platforms expose composition/export APIs. | Two implementations can drift; codec/encoder support varies by device; preview and export use different APIs/stability levels; native bridge and development builds required; test matrix is substantial. | Preferred first spike because it matches accountless/private direction. Do not adopt until output parity and target device floor are measured. |
| One shared native/C++ media engine | Potentially one edit/render implementation and more consistent effect semantics. | Native integration, memory/threading, packaging/codec licensing, hardware acceleration, UI preview integration and app upgrades add risk; actual parity is not automatic. | Consider only if native proofs show unacceptable behavioral divergence and a specific maintained engine is legally/technically viable. |
| Controlled server render | One centrally managed engine/output path; upgrade and rollback centrally; broad codec/effect options. | Upload latency/cost, large data exposure, retention/deletion burden, network dependence, queue/retry/abuse operations, export download failures; accountless use still requires a secure job identity. | Fallback if local renderer cannot meet required quality on supported devices; needs explicit consent and a privacy/security/cost decision. |
| Third-party editor SDK | Can reduce time to complex editing features. | Licensing cost/terms, vendor dependence, recipe model mapping, UI constraints, SDK size, security review and version compatibility; may duplicate the app's intended differentiation. | Research only if a measured need exists that native proof cannot meet economically. |

## 3. Current platform evidence and limits

### Android Media3

Android Media3 Transformer documents trim, transcode/transmux, track removal, scale/rotate, custom video effects, static image inputs, audio processors, and MP4 output. It relies on platform `MediaCodec` for encoding and documents HDR behavior/device requirements. [Transformations](https://developer.android.com/media/media3/transformer/transformations), [supported formats](https://developer.android.com/media/media3/transformer/supported-formats).

Media3 `Composition` represents video/image/audio sequences for preview and export, but its current documented composition limitation includes unsupported video/audio track crossfades. `CompositionPlayer` can preview a composition, but Android marks it early preview/experimental. [Composition](https://developer.android.com/media/media3/transformer/composition), [CompositionPlayer](https://developer.android.com/media/media3/transformer/compositionplayer).

Transformer offers progress state, callbacks, errors and cancel. Its cancellation documentation warns that an output file may remain; interrupted-file cleanup/validation must be owned by our adapter. Resume has specific composition constraints, so the product should promise retry, not universal continuation from the exact interrupted frame. [Transformer API](https://developer.android.com/reference/androidx/media3/transformer/Transformer), [listener API](https://developer.android.com/reference/androidx/media3/transformer/Transformer.Listener).

### iOS AVFoundation

AVFoundation supports time-based compositions, video composition instructions for render size/frame duration, spatial transforms/crop/opacity ramps, Core Animation integration, audio mix parameters/volume ramps, and export sessions. Export compatibility/output type should be queried for the actual asset/preset rather than assumed. [AVMutableVideoComposition](https://developer.apple.com/documentation/avfoundation/avmutablevideocomposition), [debugging compositions/audio mixes](https://developer.apple.com/documentation/avfoundation/debugging-avfoundation-audio-mixes-compositions-and-video-compositions), [export compatibility](https://developer.apple.com/documentation/avfoundation/avassetexportsession).

Newer AVFoundation export APIs report progress states and support async task cancellation; older APIs are deprecated. Confirm deployment target and API availability before choosing the wrapper. [Export API](https://developer.apple.com/documentation/avfoundation/avassetexportsession/export%28to%3Aas%3Aisolation%3A%29), [export state](https://developer.apple.com/documentation/avfoundation/avassetexportsession/state/exporting%28progress%3A%29).

### What this evidence does not decide

API support does not settle visual equivalence, hardware encode/decode support, font rasterization, audio drift, heat, memory, variable-frame-rate timestamps, HDR tone mapping, output rotation, filesystem access, user-perceived latency, or compatibility with each target social app. Those are measured against our recipes and device floor.

## 4. First supported render contract to prove

Use one versioned platform-neutral `RenderPlan` derived from an immutable user-approved recipe and filled-slot snapshot. The render plan carries intent; platform adapters validate/compile it to their own graph.

### Minimal candidate profile

- Container: `.mp4`.
- Video: H.264/AVC baseline candidate; dimensions/aspect are output-profile data, not hard-coded renderer logic.
- Audio: AAC candidate when audio is included; explicit no-audio output is allowed.
- Primary composition: up to 30 seconds; sequential selected video/image sections, cuts between sections, trim, rotate from metadata, crop/fit/fill, text/title overlay, remove/mute source audio, and add one replacement music or narration track if the mix proof passes.
- Profile starting point: a vertical 9:16 preset for the first social workflow, plus an editable source-ratio option only if user testing and implementation scope support it. Final resolution/frame-rate/bitrate limits remain open pending low/mid/high device tests and destination-platform review.
- Color/HDR: define an explicit policy per profile (preserve supported HDR or tone-map to SDR). Never silently produce washed-out, clipped, or rotated output; unsupported HDR receives a clear route to an SDR profile or an actionable error.
- Unsupported at first proof: overlapping video layers/PIP, video/audio crossfades, speed ramps, advanced keyframes, chroma key, masks, auto person/background replacement, arbitrary effect plugins.

This is a candidate minimal proof, not a final compatibility promise. If title overlays or a replacement-audio mix cannot match across platforms on supported devices, reduce v1 behavior or move the same contract to a centrally controlled renderer after the separate server/privacy decision.

### Output metadata to record

`RenderResult` should include job/snapshot/recipe version, engine and engine version, output URI, container, video/audio codec, dimensions, frame rate policy/observed rate, duration, orientation/rotation metadata, color/HDR policy, file size, validation result, and warnings. Do not infer success from "encoder callback completed" alone: reopen/probe/decode the output and confirm duration/streams before offering Save or Share.

## 5. Preview parity: what "same result" means

The preview and renderer consume the same immutable `RenderPlan` and capability validation. The UI must distinguish:

- **Accurate composition preview:** output sequence, timing, crop, overlays, and audio are represented by the same render semantics.
- **Proxy/approximate preview:** a reduced-resolution or simplified preview is labeled and each known difference is surfaced.
- **Structure preview:** placeholders show recipe arrangement but are not represented as an exported output.

Do not say "what you see is what you get" until representative output samples meet a measured tolerance. For exact edit cuts, compare source/output time mapping and transition frame intervals. For title/crop, compare rendered test frames using geometry and human review. For audio, measure sync offset and listen across section joins and beginning/end. Include tests with VFR, source rotation metadata, variable audio sample rates, no source audio, replacement track shorter/longer than video, and mixed clip dimensions.

## 6. Native proof matrix

Build the same recipe fixture and expected behavior on both platforms. Include low-, mid-, and high-tier supported devices; use physical devices for encoders/thermal behavior and simulators only for UI/contract portions that they can faithfully represent.

| Proof ID | Capability | Pass evidence |
|---|---|---|
| RND-001 | Select/trim/concatenate included sections | Exact section order; cut points correspond to chosen timestamps within agreed frame tolerance; excluded ranges never appear. |
| RND-002 | Rotate/crop/reframe to vertical output | No stretched image; visible subject and title safe-area fit; rotation metadata normalized; crop controls have matching preview/export. |
| RND-003 | Static image replacement slot | Holds exactly chosen duration, frames consistently, crops predictably, and uses documented frame-rate behavior. |
| RND-004 | Text/title layer | Font size, line wrapping, baseline, color, timing and safe position agree in preview and output across platforms/locales/font scaling; no clipped glyphs. |
| RND-005 | Source audio remove/mute | No source track or audible source residue when muted; output stream metadata matches selected policy. |
| RND-006 | Add replacement audio | Correct trim/loop/volume/start/end; no drift or unintended source overlap; mixed playback checked on phone speakers/headphones. |
| RND-007 | MP4 output profile | File opens in platform player and a second independent editor; codec/container/duration/dimensions/profile validated; file naming/save/share is correct. |
| RND-008 | Long/variable or unsupported codec input within source limits | Preflight gives accurate supported/unsupported result; no hang; user can retry or use manual editing/re-import path. |
| RND-009 | Cancel/fail/low storage/app interruption | No false success; temporary partial file is not offered; draft/recipe survives; retry produces a valid output. |
| RND-010 | HDR/rotation/VFR/corruption | Defined profile policy; timestamps remain ordered; no silent color/rotation regression; unsupported file gives actionable explanation. |
| RND-011 | Resource/thermal floor | Record elapsed render time, peak memory, battery, thermal throttling, background behavior, and success rate for each device tier; set release thresholds from baseline. |
| RND-012 | Preview/output equivalence | Compare encoded output against the composition preview with timestamp/frame/audio checks and human review; record accepted tolerances and any disclosed approximation. |

## 7. Error, storage and lifecycle requirements

- Render from a snapshot. Editing the recipe after rendering begins creates another snapshot; it cannot mutate the running job.
- Reserve/check temporary storage before rendering when file size can be estimated; still handle estimate error and OS storage failure.
- Write to a temporary app-owned path; only move/rename to the user's visible export location after validation.
- On cancel, delete partial output when safe and report if cleanup failed. On crash/relaunch, identify orphan temporary outputs and offer cleanup without deleting saved exports.
- Keep the source, recipe and replacements available for retry according to user retention settings; do not duplicate source media unnecessarily.
- Don't promise background completion until iOS/Android background execution behavior is tested. If the app is backgrounded, report whether render continues, pauses, or must restart.
- A render error must include a stable error class for support/telemetry (unsupported media, decoder, encoder, no space, permission, cancellation, muxer, internal) without exposing file paths or media content.
- Share-sheet completion means the system accepted a share action, not that a social platform posted successfully.

## 8. Decisions and next experiment

### Decision still open (`DEC-005`)

Use the `RenderPort` interface now; select local native vs service only after the proof matrix. Keep one capability registry so UI controls are unavailable or clearly marked when that renderer build cannot realize them. Record platform support by operation and minimum OS/device range.

### Spike order

1. Produce a standalone native proof with two video clips, an image slot, crop/rotation, title overlay, source mute, replacement audio, MP4 save and validation.
2. Use one platform-neutral JSON plan for both implementations; do not code product screens into the proof.
3. Run the same fixed media/plan on Android and iOS; include VFR, HEVC/HDR, rotated, damaged, no-audio, and mixed-orientation inputs.
4. Capture preview/export frame comparison, audio sync, run time, resource usage, cancellation/recovery, and failure categories.
5. Implement only operations passing both platforms on the agreed device floor. Record unsupported recipe operations as explicit capabilities/errors.
6. If the current environment cannot build/test iOS natively, keep the decision open until access to macOS/Xcode or an equivalent trusted device-build service is available; do not treat Android-only results as parity evidence.

## 9. Sources checked 2 October 2026

- Android [Media3 Transformations](https://developer.android.com/media/media3/transformer/transformations), [supported formats](https://developer.android.com/media/media3/transformer/supported-formats), [Composition](https://developer.android.com/media/media3/transformer/composition), [CompositionPlayer](https://developer.android.com/media/media3/transformer/compositionplayer), [Transformer API](https://developer.android.com/reference/androidx/media3/transformer/Transformer), [export listener](https://developer.android.com/reference/androidx/media3/transformer/Transformer.Listener).
- Apple [AVMutableVideoComposition](https://developer.apple.com/documentation/avfoundation/avmutablevideocomposition), [composition/audio mix debugging](https://developer.apple.com/documentation/avfoundation/debugging-avfoundation-audio-mixes-compositions-and-video-compositions), [AVAssetExportSession](https://developer.apple.com/documentation/avfoundation/avassetexportsession), [async export](https://developer.apple.com/documentation/avfoundation/avassetexportsession/export%28to%3Aas%3Aisolation%3A%29), [export progress state](https://developer.apple.com/documentation/avfoundation/avassetexportsession/state/exporting%28progress%3A%29).
