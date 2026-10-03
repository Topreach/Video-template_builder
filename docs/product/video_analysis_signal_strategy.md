# Video Analysis Signals and Recommendation Strategy

**Status:** Research and implementation baseline; providers/models and launch-language coverage remain decision-gated.
**Updated:** 2 October 2026
**Parent:** [Video-to-template workflow](video_template_workflow_spec.md)  |  [coverage and decision register](mvp_coverage_and_traceability.md)  |  [technology research](../research/mvp_technology_and_design_research.md).

## 1. Purpose

Specify what the analyzer may observe, how each observation can help a user, what it cannot establish, and what consent/device evidence is required. "Analyze the video" is not one model call. It is a collection of signals with different accuracy, platform, privacy, and processing constraints. A comprehensive, time-aligned component inventory is a core product outcome: the user sees what was found (and what could not be analyzed) before deciding which parts to reuse, replace, or exclude.

### Required analysis coverage contract

Every analysis proposal reports each required pass independently: media facts; shot boundaries; people/subjects; objects/actions; setting/background; camera motion/layout (including split-screen and overlays); on-screen text/marks; speech; music/sound (effects, silence and beat candidates); creative beats/role hypotheses; and source integrity (abrupt edges, black/freeze spans and decode problems). Findings use overlapping, timestamped tracks: a camera cut is not automatically a reusable story section, and one creative section may span several shots. Creative roles such as hook, context, setup, tutorial step, demonstration, action, reaction, reveal, payoff, call-to-action, lyric/beat and transition are hypotheses with an `unknown` option, never asserted facts.

Each signal must report `completed`, `partial`, `not-run`, `unsupported` or `failed`, with provider/version and processing location when it ran. A missing, failed, or partial signal keeps the whole inventory visibly partial and offers manual review; unsupported is acceptable only when the source/platform genuinely lacks that modality (for example, no audio). A “complete coverage” state means all defined analysis passes ran; it does not mean every object, word, sound, or creative intent was detected. Findings require evidence/time ranges, honest uncertainty, and user correction. No finding may automatically delete source material or authorize reuse. Person findings must not identify a person or infer sensitive traits.

### Current implementation checkpoint

The Python package now has an experimental local PySceneDetect Adaptive baseline and versioned shot-span proposal output. It is available through the developer CLI only, is not connected to the mobile app, has no calibrated confidence, and does not physically split source media. See [ADR 0003](../architecture/decisions/0003-experimental-local-shot-analysis.md). The processing-location decision and annotated-corpus evaluation remain open.

### Core rule

Signals describe evidence in the selected media. They do not by themselves establish story meaning, ownership, consent, identity, safety, or permission to publish. An analyzer may propose; the user reviews and decides.

## 2. Signal inventory and MVP order

| Signal | MVP order | What it can contribute | What it cannot guarantee | Recommended first treatment |
|---|---|---|---|---|
| Media/container facts | Required | Duration, dimensions, rotation, frame timing, audio/video tracks, codec/probe/decode warnings. | The creative intent, clip completeness, rights, or whether a fragment is "attached." | Local metadata probe; block unsupported/corrupt input with recoverable errors. |
| Shot-boundary score | Required proposal capability | Candidate hard/gradual visual transitions and useful contact-sheet spans. | Creative/story section, semantic event, unwanted content, or accurate boundary on every style. | Compare classical adaptive/content detection against learned short-video detector; user can regroup/correct. |
| Black/freeze/abrupt edges | Useful warning | Possible gap, stalled frame, abrupt splice/edge, decode loss. | Defect, partial download, attached material, or intent. | Display a warning with source time; no automatic removal. |
| OCR/on-screen text | Required analysis pass; provider may be unsupported | Possible overlay/caption/lyric text, timing/location and text-heavy areas. | Correct transcription, language, authorship, or whether text should remain. | Report coverage; run an evaluated OCR provider where supported, otherwise mark unavailable. Show evidence and let user correct/delete; save only approved replacement text in the recipe. |
| Speech transcription | Required analysis pass; opt-in/availability may limit it | Candidate speech spans/text/timing for dialogue, storytime, tutorial and captions. | Correct words, speaker identity, emotion, safe attribution, or all-language support. | Always report status. Transcribe only with disclosed supported processing and consent; if off/unavailable, mark not-run/unsupported and offer manual continuation. |
| Audio activity/beat grid | Required analysis pass when audio exists | Speech/music/effects/silence spans and beat candidates for rhythm editing. | Exact meter/downbeat, song rights, or that a template should follow a beat. | Report status; offer editable beat candidates. Do not force beat snapping on comedy/dialogue/action. |
| Visual/motion cues | Required analysis pass | People (anonymous), objects, actions, setting/background, camera motion and layout cues for replacement planning. | Identity, sensitive traits, safe action, intended emotion, or stable tracking in every clip. | Report per-category coverage and uncertainty; use only evaluated cues, never high-level assertions from generic classifiers. |
| Semantic section/role classification | Required hypothesis pass, user-reviewed | Candidate hook/context/setup/reveal/payoff/CTA/tutorial/action/reaction/lyric-beat/transition labels. | Objective ground truth or cross-cultural meaning. | Include suggestions and `unknown`; evaluate separately on creator categories; never block manual correction or claim factual story understanding. |
| Personalized replacement matching | Later | Find candidate user-owned clips based on duration, orientation, subject/motion/framing or user tags. | That a match has rights, is semantically appropriate, or should be inserted. | Start with user-directed browsing and shot prompts; add local/private matching only after consent, indexing and quality evidence. |

## 3. Signal-specific technical research

### 3.1 OCR: sampled frames, not a claim about every caption

Apple Vision's `VNRecognizeTextRequest` recognizes text in an image and returns observations with candidate text, location and confidence. Google ML Kit Text Recognition v2 provides text blocks/lines/words and supports image/video inputs, but the documented v2 scripts are Latin, Chinese, Devanagari, Japanese and Korean. The Android guide offers bundled or downloaded model choices with different startup/app-size tradeoffs. [Apple Vision OCR](https://developer.apple.com/documentation/vision/vnrecognizetextrequest), [ML Kit overview](https://developers.google.com/ml-kit/vision/text-recognition/v2), [ML Kit script coverage](https://developers.google.com/ml-kit/vision/text-recognition/v2/languages), [Android packaging/performance](https://developers.google.com/ml-kit/vision/text-recognition/v2/android).

This is not enough to promise equal OCR on iOS and Android, especially for every launch language, stylized text, curved/moving overlays, compression, lyrics, or mixed Arabic/Latin text. Before using OCR in the product:

1. Confirm the actual framework's supported recognition languages/revisions at runtime and its per-OS model/package size.
2. Benchmark on device frames with burned-in captions, interface overlays, watermarks, emoji, low-contrast text, fast motion, RTL text, Arabic diacritics, mixed scripts, and repeated frames.
3. Sample frames adaptively: shot midpoints, likely text changes, and user-requested intervals. Deduplicate repeated text observations over adjacent frames into a time span. Sampling rate is a measured quality/cost choice, not a fixed product claim.
4. Return text only as a candidate with timestamp range, normalized bounding box, language if known, confidence/uncertainty and engine/version. Keep OCR observations out of logs and analytics.
5. Show a thumbnail with the recognized string and allow Edit, Remove, Ignore, or "keep as editable overlay" decisions. OCR output must never automatically overwrite text, remove a watermark, or become recipe text.

### 3.2 Speech: platform APIs do not create a parity guarantee

Apple's Speech framework can transcribe recorded audio, but language availability varies; the recognizer reports whether it is available and whether it supports on-device recognition. Apple documents asking permission for speech recognition and notes that server processing can send voice data to Apple. Android's `SpeechRecognizer` requires `RECORD_AUDIO`, may stream to remote servers, and exposes a separate on-device recognizer only where system support is available; its offline preference may be ignored by an implementation. [Apple recognizer availability](https://developer.apple.com/documentation/speech/sfspeechrecognizer), [Apple on-device support](https://developer.apple.com/documentation/speech/sfspeechrecognizer/supportsondevicerecognition), [Apple speech authorization](https://developer.apple.com/documentation/speech/asking-permission-to-use-speech-recognition), [Android SpeechRecognizer](https://developer.android.com/reference/kotlin/android/speech/SpeechRecognizer), [Android offline preference limitations](https://developer.android.com/reference/android/speech/RecognizerIntent#EXTRA_PREFER_OFFLINE).

This creates important requirements:

- The user is analyzing an existing media file, not necessarily recording new audio. Do not request microphone permission simply because the project can contain speech. If a platform recognizer needs microphone access or treats the content as live capture, assess the API path before using it.
- On iOS, an existing audio-file URL has an API path, but the actual processing location must be set/verified. Require on-device recognition where supported if privacy mode promises local processing; otherwise ask for clear additional consent before any service transmission.
- On Android, system speech recognition behavior and model availability vary by device/service. Do not claim consistent offline transcription based only on the API's existence.
- A production cross-platform transcript needs a provider abstraction and a per-language/per-platform support table. The MVP can omit speech transcription and remain functional through manual role/text controls.
- If transcript is enabled: user can preview/edit/delete it; store only approved text/timing according to the retention choice; provide a transcript-off path; avoid showing transcripts in notifications, crash logs, or analytics.

### 3.3 Beats and audio structure

Beat tracking commonly estimates onset strength, estimates tempo from onset correlation, then selects peaks consistent with that tempo. `librosa.beat.beat_track` documents this dynamic-programming approach. It returns an estimate, not the song's legal rights, intended edit points, or a guaranteed musical downbeat. [librosa beat tracker](https://librosa.org/doc/0.11.0/generated/librosa.beat.beat_track.html).

For beat-oriented templates, use the signal to offer editable beat markers and alignment choices such as preserve detected beats, preserve total duration, or preserve clip length. Always allow a user to move/remove markers and preview changes. Validate audio resampling, channel layout, variable bit rate, silence, crowd noise, speech over music, tempo changes, half/double-time ambiguity, sync offsets, and the first/last partial beat. For comedy, dialogue, story and many action clips, beat markers stay optional and off by default. Beat analysis must not save a copy of a commercial song to a public template or imply rights to reuse it.

### 3.4 Semantic analysis and replacement recommendations

Roles and recommendations should be treated as two separate outputs:

1. **Role hypothesis:** e.g. `hook`, `setup`, `demonstration`, `reveal`, `reaction`, `payoff`, `CTA`, `lyric/beat`, `dialogue`, or `unknown`.
2. **Replacement prompt:** a practical suggestion explaining what the user could capture/use to preserve or change the section's function.

Published datasets show why this must remain a proposal rather than a promise. VidSitu provides dense event/role annotations over 29,000 ten-second movie clips, which is useful research but does not by itself establish coverage for songs, memes, tutorials, screen recordings, action edits, or mixed short-form clips ([VidSitu paper](https://arxiv.org/abs/2104.00990)). TemporalBench reports substantial difficulty even for strong video models on fine-grained temporal questions; one paper-reported GPT-4o score is 38.5% on its benchmark ([TemporalBench paper](https://arxiv.org/abs/2410.10818)). These are research benchmarks, not expected product accuracy. They support evidence-grounded, timestamped hypotheses and user correction, not a generic “understands every video” claim.

An initial recommendation engine does not need a generative model. A controllable rule/template engine can combine:

- user-selected creative format;
- role hypothesis confirmed/corrected by the user, or an explicit `unknown` value;
- section duration and order;
- visible composition cues the user can see (wide/close, subject position, motion direction) when those cues pass a precision review;
- user topic/brand brief; and
- chosen variation goal (preserve structure, change mood, change story, change pace).

Generate prompt cards from reviewed prompt patterns, not hidden claims about emotion, identity, protected traits, or virality. Example: "Keep the reveal timing. Film a close-up of your own product moving into frame." Each card shows the inputs used, why it fits, a way to edit/skip, and whether it is a prompt or an actual media asset. A language model may later rephrase or diversify prompts, but the output remains user-reviewed and bounded to this structure.

Never train on a user's uploads or use them to improve a hosted model unless a separate, specific, revocable research consent and data policy exists. Do not use face/voice identity or sensitive-trait inference to rank suggestions.

### 3.5 Person, pose, and background signals

Pose APIs return landmarks/coordinates, not actions with trustworthy narrative labels. Google's ML Kit Pose Detection documentation marks the API beta and notes device/app-size/performance tradeoffs. Person masks likewise enable a cutout/composite effect, not generation of a replacement character. [ML Kit Pose Detection](https://developers.google.com/ml-kit/vision/pose-detection/android), [Apple person segmentation guidance](https://developer.apple.com/documentation/vision/applying-matte-effects-to-people-in-images-and-video).

The inventory may report candidate people/pose/background cues only when a provider is supported and evaluated; otherwise it must show that coverage as unavailable. Keep automatic person/background generation and identity-preserving replacement out of core template creation until a separate use case and quality study justify them. Any later framing or visual-edit operation needs temporal-stability, occlusion/crowd/low-light evidence, explicit before/after, per-section scope, undo/restore and user approval. Do not infer identity, age, ethnicity, attractiveness, disability, or other sensitive characteristics.

## 4. Cross-platform provider rule

Define signal results as versioned neutral records, not Apple's or Google's native objects:

```ts
type SignalFinding = {
  id: string;
  kind: 'shot-boundary' | 'ocr' | 'speech' | 'beat' | 'audio-activity' | 'visual-cue' | 'role';
  sourceRangeMs?: { startMs: number; endMs: number };
  pointMs?: number;
  value?: string | number | Record<string, unknown>;
  confidence?: number; // only if the provider's value is calibrated and documented
  uncertainty?: 'low' | 'medium' | 'high' | 'unknown';
  provenance: { provider: string; version: string; processing: 'device' | 'server' | 'unknown' };
  reviewState: 'unreviewed' | 'accepted' | 'edited' | 'ignored';
};
```

Do not persist uncalibrated numeric scores as if they were comparable between providers. Keep processing location explicit per finding/job. Keep raw media/frame crops outside the recipe and give them their own retention/deletion behavior.

## 5. MVP signal selection recommendation

### Ship in the first useful workflow

- Technical metadata and decode errors.
- Candidate hard/gradual cut boundaries only after the same-corpus bake-off and manual editing fallback.
- Clearly labeled blank/freeze/abrupt-edge coverage and findings after false-warning review; no automatic removal.
- Creative format controls plus evaluated, editable role hypotheses and an `unknown` option.
- Prompt-based replacements using user-confirmed context; no semantic model required.

### Add only after a bounded evaluation

- OCR if the selected launch script/platform combination passes quality and app-size/privacy checks. Keep OCR text as an editable draft.
- Beat markers for opt-in music-edit templates if the benchmark shows timing benefit and users can easily correct them.
- Speech transcription only after the privacy model, permission UX, launch languages, availability matrix, retention, and cross-platform behavior are decided.

### Keep these operations deferred until separately justified

- Role hypotheses presented as facts; role suggestions remain user-reviewed and correction-first.
- General user-library semantic matching or cloud embeddings.
- Person/character replacement, identity preservation, inferred emotion or sensitive traits.
- Automatic removal of logos/watermarks/captions/source audio.

## 6. Signal validation matrix

For each candidate signal and launch language, collect consented representative samples with adjudicated annotations and test both operating systems. Report availability, precision/recall or task-specific quality, correction time, time/memory/battery/app-size/network impact, failure behavior, and whether user decisions improve. Use a held-out split. Include the types most likely to break the feature, not only clean examples.

| Signal | Required failure cases | User-observable acceptance condition |
|---|---|---|
| OCR | Small/stylized text, motion blur, shadow/outline, emojis, lyric overlays, multi-column/split screen, RTL/mixed script, compression, text appearing for only a few frames. | User can tell OCR is a suggestion, inspect where it came from, correct/delete it, and finish without OCR. |
| Speech | Music underneath speech, multiple/overlapping speakers, accents/dialects, code-switching, names, clipped starts/ends, silence/no speech, noisy or sped-up audio, unsupported language/offline service. | No transcript is shown as authoritative; source audio/processing is disclosed; user can opt out and continue manually. |
| Beat | Half/double tempo, syncopation, tempo change, speech over music, no music, silence, VBR timing, first downbeat off-screen, device codec differences. | Markers are editable/optional; the preview reflects exact changes; non-beat formats are not forced onto them. |
| Visual/motion | Camera pan, zoom, whip pan, flash, strobe, sports/action motion, screen capture, game animation, multiple subjects, occlusion, low light. | App labels only validated cue types; uncertainty and correction/skip are available. |
| Replacement prompt | User changes category/role/topic, no transcript/OCR, offensive or sensitive content, insufficient source context, actual asset vs prompt confusion. | Prompt has visible rationale and source type, is editable/skippable, and is never auto-applied or called a virality predictor. |

## 7. Decision register additions

This document elaborates `DEC-004` in the [coverage map](mvp_coverage_and_traceability.md#5-decision-and-evidence-register):

- **OCR:** decide launch scripts and per-platform engine after runtime language support, visual-text corpus and app-size testing.
- **Speech:** decide whether to omit from MVP or use a common on-device/hosted provider after consent, transmission, languages, permission and retention are documented.
- **Beats:** decide after annotation/user tests establish beat alignment improves completion for music templates without harming other formats.
- **Semantic roles:** role hypotheses and an `unknown` state are required in the product contract; decide the provider/quality thresholds after cross-family evaluation and user research.
- **Suggestions:** start with deterministic prompt patterns; assess hosted language model value and cost separately, with no media upload required for a prompt if the user can describe the section.

## 8. Official sources checked 2 October 2026

- Apple [Vision text recognition](https://developer.apple.com/documentation/vision/vnrecognizetextrequest), [Speech recognizer](https://developer.apple.com/documentation/speech/sfspeechrecognizer), [on-device recognition support](https://developer.apple.com/documentation/speech/sfspeechrecognizer/supportsondevicerecognition), [speech permission](https://developer.apple.com/documentation/speech/asking-permission-to-use-speech-recognition).
- Google [ML Kit Text Recognition v2](https://developers.google.com/ml-kit/vision/text-recognition/v2), [supported scripts/languages](https://developers.google.com/ml-kit/vision/text-recognition/v2/languages), [Android configuration](https://developers.google.com/ml-kit/vision/text-recognition/v2/android), [Language Identification](https://developers.google.com/ml-kit/language/identification/android), [SpeechRecognizer](https://developer.android.com/reference/kotlin/android/speech/SpeechRecognizer), [RecognizerIntent offline note](https://developer.android.com/reference/android/speech/RecognizerIntent#EXTRA_PREFER_OFFLINE), [Pose Detection](https://developers.google.com/ml-kit/vision/pose-detection/android).
- librosa [beat tracking algorithm](https://librosa.org/doc/0.11.0/generated/librosa.beat.beat_track.html).
