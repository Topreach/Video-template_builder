# STAGE 2 — SourceDescription Contract Specification

> **Subordinate to `stage2_1_contract_boundary.md` (Stage 2.1).**
> §2.1 fixes the contract's responsibility, boundary, four field dimensions (tier / state /
> stability / requirement), the `ingestion_status` gate, and the naming rules. This document
> provides the field-level detail for §2.2–§2.15 and **must not contradict §2.1**. Where it
> currently does, §2.1 wins and the change list in §2.1.9 applies.

**Stage:** 2 | **Contract #1** | **Layer:** Ingestion (Layer 1)  
**Derived from:** Stage 1 Architecture (Section 8, Contract #1)  
**Status:** SPECIFY FIELD-LEVEL SCHEMA

---

## 2.1 Purpose

The `SourceDescription` is the **first interface contract** produced by the Ingestion layer. It captures the structural identity of the input video file using only source-native metadata — no analysis models, no decoded pixel processing.

**Producers:** Ingestion module (Layer 1) — exclusively via FFprobe/mediainfo-style container/codec interrogation.

**Consumers:** Decode (Layer 2), Quality (Layer 3), and all downstream evidence layers via `DecodedVideo` (Contract #2).

---

## 2.2 Canonical YAML Schema

```yaml
SourceDescription:
  id: string               # uuid4
  source_path: string      # absolute filesystem path or object-storage URI

  container:               # REQUIRED — measured
    format: string         # e.g. "mov", "mp4", "webm", "mkv"
    format_long: string    # human-readable, e.g. "QuickTime MOV"
    size_bytes: integer    # file size

  video_stream:            # REQUIRED — measured
    codec: string          # e.g. "h264", "hevc", "vp9", "av1"
    codec_long: string     # human-readable, e.g. "H.264 / AVC / MPEG-4 AVC"
    profile: string?       # OPTIONAL
    level: string?         # OPTIONAL
    width: integer         # pixel width (REQUIRED)
    height: integer        # pixel height (REQUIRED)
    coded_width: integer   # storage dimensions (may differ from display via crop)
    coded_height: integer
    display_aspect_ratio: string?  # e.g. "16:9"; OPTIONAL — `null` means the source declares none
                                  # (amended v1.2 — see Amendment Record v1.2; was non-optional `string`)
    sample_aspect_ratio: string?  # e.g. "1:1"; OPTIONAL — `null` means the source declares none
                                 # (amended v1.1 — see Amendment Record v1.1; was non-optional `string`)
    frame_rate: string     # rational, e.g. "30000/1001" (=29.97)
    avg_frame_rate: string # average over entire stream
    time_base: string      # e.g. "1/30000"
    nb_frames: integer     # total decoded frame count

  fps_actual:              # REQUIRED — measured
    value: float           # e.g. 29.97
    type: string           # "cfr" | "vfr" | "mixed"
    confidence: float      # 0.0–1.0 (FFprobe timing reliability)
    provenance:            # [§6 provenance]
      tool: string         # e.g. "ffprobe"
      raw_rational: string # e.g. "30000/1001"

  cfr_vfr:                 # REQUIRED — measured
    is_cfr: boolean        # constant frame rate flag
    is_vfr: boolean        # variable frame rate flag
    variance: float        # 0.0 = constant, >0 = variable magnitude
    max_delta: float       # max PTS gap in seconds from nominal
    confidence: float
    provenance:
      tool: string         # e.g. "ffprobe", "ffmpeg-vfr-analysis"
      method: string       # "packet_pts_analysis"
      samples_checked: integer

  duration:                # REQUIRED — measured
    value: float           # seconds (wall-clock)
    start_time: float      # earliest PTS in seconds
    end_time: float
    confidence: float
    provenance:
      tool: string
      method: string       # "format_duration" | "stream_duration"

  audio_streams:           # REQUIRED — array (may be empty)
    - stream_index: integer
      codec: string        # e.g. "aac", "opus", "mp3"
      codec_long: string
      sample_rate: integer
      channels: integer
      channel_layout: string
      bits_per_sample: integer?
      duration: float
      bit_rate: integer?
      language: string?    # from metadata
      title: string?       # from metadata

  # ── OPTIONAL / ABSENT-ALLOWED FIELDS (Stage 1 §9.1) ──
  # Each group carries the full §6 envelope. `state` is what lets downstream distinguish
  #   measured  = looked for and found
  #   uncertain = looked for, ambiguous
  #   absent    = looked for and not found
  # A `null` group means "not applicable to this video type / not analyzed yet".
  # ABSENT (state: absent) and OPTIONAL (null) are DIFFERENT and must not be conflated.

  bit_depth:               # OPTIONAL — measured
    luma: integer          # e.g. 8
    chroma: integer        # e.g. 8
    state: string          # "measured" | "uncertain" | "absent"
    confidence: {value: float, type: string, calibration: float?}
    source: {layer: string, model: string?, tool: string?}
    provenance: [ {layer, evidence_refs[], transform_type, confidence_delta} ]
    fidelity: {type: string, tolerance: string?}
    validation: {status: string, rules_passed[], rules_failed[]}

  color_space:             # OPTIONAL — measured (state=uncertain if pix_fmt unrecognised)
    value: string          # e.g. "yuv420p"
    full_name: string      # e.g. "YUV color space restrictions"
    state: string
    confidence / source / provenance / fidelity / validation   # §6 envelope

  transfer:                # OPTIONAL — measured (absent when container has no color_trc tag)
    value: string          # e.g. "bt709"
    state: string
    confidence / source / provenance / fidelity / validation   # §6 envelope

  chroma:                  # OPTIONAL — measured
    subsampling: string    # e.g. "4:2:0"
    state: string
    confidence / source / provenance / fidelity / validation   # §6 envelope

  generational_estimate:   # OPTIONAL — measured (state=absent when value == "unknown")
    value: string          # "prosumer_phone" | "dslr" | "broadcast" | "cinema" | "unknown"
    state: string
    confidence: {value: float, type: semantic_interpretation, calibration: float?}
    source / provenance / fidelity / validation                # §6 envelope

  # ── UNCERTAIN-ALLOWED ──

  quality_score:           # UNCERTAIN-ALLOWED
    value: float | null    # 0.0–1.0, null if cannot measure
    state: string          # "measured" | "uncertain" | "absent"
    confidence: {value: float, type: measured, calibration: float?}
    source / provenance                                        # §6 envelope
```

---

## 2.3 Field Categorization (Per §9.1)

### REQUIRED (always present — contract invalid if missing)

| Field | Type | Produced By | Failure Mode |
|---|---|---|---|
| `container.format` | string | ffprobe `format.format_name` | File unreadable → Ingestion rejects |
| `container.size_bytes` | integer | OS stat | Same |
| `video_stream.codec` | string | ffprobe `stream.codec_name` | No video stream → reject |
| `video_stream.width` | integer | ffprobe `stream.width` | Invalid dimensions → reject |
| `video_stream.height` | integer | ffprobe `stream.height` | Invalid dimensions → reject |
| `frame_rate` | string | ffprobe `stream.r_frame_rate` | Missing → default to derived from avg |
| `fps_actual.value` | float | computed from `frame_rate` rational | PTS analysis failure → mark `uncertain` |
| `fps_actual.type` | string | ffprobe PTS variance analysis | — |
| `cfr_vfr.is_cfr` | boolean | ffprobe PTS delta analysis | — |
| `cfr_vfr.is_vfr` | boolean | ffprobe PTS delta analysis | — |
| `duration.value` | float | ffprobe `format.duration` | Stream shorter than format → use max |
| `duration.start_time` | float | ffprobe `stream.start_time` | — |
| `audio_streams` | array | ffprobe (filter audio streams) | Empty array if no audio |

### OPTIONAL (absence = not applicable, not error)

| Field | Condition for Presence | Confidence Type |
|---|---|---|
| `video_stream.profile` | Codec defines profiles (e.g. H.264: baseline/main/high) | measured |
| `video_stream.level` | Codec defines levels | measured |
| `bit_depth` | Codec exposes pixel format (e.g. yuv420p → 8-bit) | measured |
| `color_space` | Container metadata provides color info | measured |
| `transfer` | Transfer characteristic tag present | measured |
| `chroma` | Chroma subsampling tag present | measured |
| `generational_estimate` | Heuristic model applied to metadata | semantic_interpretation |

### UNCERTAIN-ALLOWED (schema supports explicit uncertainty)

| Field | When Uncertain | Cap Confidence |
|---|---|---|
| `fps_actual` | PTS timestamps inconsistent across packets | 0.5 |
| `cfr_vfr` | Sparse or corrupted PTS data | 0.5 |
| `quality_score` | Could not measure bitrate stability | 0.0 |

---

## 2.4 Confidence + Provenance Envelopes (Per §6)

**NORMATIVE KEY NAMES.** This envelope is Stage 1 §6 and is implemented 1:1 by
`src/videotemplate/utils/confidence.py` (`Confidence`, `SourceInfo`, `ProvenanceEntry`,
`Fidelity`, `ValidationInfo`). Earlier drafts of this section used `evidence_ref`
(singular), `transform`, and `source.method` — none of those names exist in the code base.
Do not reintroduce them.

Every field that can carry confidence MUST use the following envelope:

```json
{
  "value": "<field_value>",
  "confidence": {
    "value": 0.95,
    "type": "measured",
    "calibration": 0.98
  },
  "source": {
    "layer": "source_native",
    "model": null,
    "tool": "PyAV"
  },
  "provenance": [
    {
      "layer": "source_native",
      "evidence_refs": ["container_probe"],
      "transform_type": "none",
      "confidence_delta": 0.0
    }
  ],
  "fidelity": {
    "type": "preserved",
    "tolerance": "exact"
  },
  "validation": {
    "status": "validated",
    "rules_passed": [],
    "rules_failed": []
  }
}
```

Notes:

- `confidence.type` ∈ `measured | detection | tracking | identity_persistence | semantic_interpretation | inferred | fusion`.
- `source.layer` ∈ `source_native | analysis_normalized | evidence | semantic | template_dna`.
- `fidelity.type` ∈ `preserved | structural | regenerable`.
- `validation.status` ∈ `validated | conflict | uncertain`.

### §6.1 Boundary Crossing Rules (for SourceDescription)

| Transform | Confidence Delta |
|---|---|
| SOURCE-NATIVE → ANALYSIS-NORMALIZED | 0.0 (lossless — metadata extraction is deterministic) |
| SOURCE-NATIVE → EVIDENCE | 0.0 (no model inference applied) |

**Rule:** SourceDescription crosses into DecodedVideo at the Decode boundary (Layer 2). The confidence delta is 0.0 per §6.1 Rule 5 — source-native metadata is lossless until pixel-level decoding occurs.

---

## 2.5 Field-Level Production Matrix

| Field | FFprobe Command / Probe Path | Confidence | Notes |
|---|---|---|---|
| `container.format` | `format.format_name` | 1.0 | e.g. "mov,mp4,m4a,3gp,3g2,mj2" → normalized to "mp4" or "mov" |
| `container.size_bytes` | `format.size` | 1.0 | From filesystem stat |
| `video_stream.codec` | `stream.codec_name` | 1.0 | e.g. "h264" |
| `video_stream.codec_long` | `stream.codec_name + "/" + stream.profile` | 0.95 | Profile may be missing |
| `video_stream.width` | `stream.width` | 1.0 | Coded display width |
| `video_stream.height` | `stream.height` | 1.0 | Coded display height |
| `coded_width/coded_height` | `stream.coded_width/coded_height` | 0.95 | May equal display dims |
| `frame_rate` | `stream.r_frame_rate` | 0.95 | May be "0/0" for some formats → fallback to `avg_frame_rate` |
| `avg_frame_rate` | `stream.avg_frame_rate` | 0.90 | Calculated; less precise than r_frame_rate |
| `time_base` | `stream.time_base` | 1.0 | Fundamental PTS unit |
| `nb_frames` | `stream.nb_frames` or packet count | 0.85 | Not always present; may require counting |
| `fps_actual.value` | `eval(r_frame_rate)` | 0.95 | Rational → float conversion |
| `fps_actual.type` | PTS delta histogram | 0.90 | Computed by analyzing PTS spacing |
| `cfr_vfr.is_cfr` | PTS variance < epsilon | 0.90 | Threshold: max_delta < 0.5ms |
| `cfr_vfr.variance` | `stddev(pts_deltas)` | 0.90 | In seconds |
| `duration.value` | `format.duration` or `stream.duration` | 0.95 | Prefer longest of format/stream |
| `duration.start_time` | `stream.start_time` | 0.95 | May be negative |
| `audio_streams[].codec` | `stream.codec_name` (audio filter) | 1.0 | Empty array if none |
| `audio_streams[].sample_rate` | `stream.sample_rate` | 1.0 | Integer Hz |
| `audio_streams[].channels` | `stream.channels` | 1.0 | Integer |
| `bit_depth.luma` | `stream.bits_per_raw_sample` or pix_fmt | 0.85 | Heuristic from pix_fmt for some codecs |
| `color_space.value` | `stream.pix_fmt` | 0.95 | e.g. "yuv420p" |
| `transfer.value` | `stream.transfer` | 0.90 | Not always present |
| `generational_estimate` | metadata heuristics v1 | 0.60 | Low confidence — heuristic model |
| `quality_score` | bitrate / resolution / codec model | 0.70 | Uncertain if insufficient data |

---

## 2.6 Validation Rules (For Contract #1)

1. **Duration Check:** `duration.value` must be ≤ 30.0 seconds. Exceeds 30 → Ingestion rejects with actionable message: `Video exceeds 30-second limit (got {X}s)`.
2. **Video Stream Presence:** At least one video stream exists. No video → reject: `No video stream found`.
3. **Readable Container:** FFprobe must successfully parse container. Parse failure → reject: `Unreadable container format: {reason}`.
4. **Frame Count Consistency:** If `nb_frames` present, must match sum of packets. Discrepancy → mark `confidence=0.7` on `nb_frames`.
   - **⚠️ OPEN — not implemented.** `video_stream.nb_frames` is currently a bare `integer` (§2.2), so there is nowhere to attach a confidence value. Implementing this rule requires promoting `nb_frames` to an enveloped group like `fps_actual`. Decide before Stage 2 is locked.
5. **PTS Monotonicity:** PTS must be non-decreasing across packets. Violations → mark `fps_actual.state="uncertain"`.
   - **✅ Implemented.** Restated precisely: monotonicity is checked in **display order** (after sorting by PTS), because B-frames legitimately reorder packets in decode order — checking raw decode order would false-positive on nearly every normal clip. A zero or negative gap in display order means duplicate/broken PTS → `fps_actual.state="uncertain"` and `cfr_vfr.state="uncertain"`, confidence capped at 0.5. See `Ingestor._analyze_cfr_vfr` / `Ingestor._analyze_fps`.

---

## 2.7 Failure Modes & Recovery (Layer 1)

| Failure | Behavior | Confidence |
|---|---|---|
| File unreadable (permissions/corrupt) | Ingestion returns error, no SourceDescription | 0.0 |
| Duration > 30s | Reject with message, suggest trimming | 0.0 |
| No video stream | Reject | 0.0 |
| VFR with extreme jitter (max_delta > 0.1s) | Mark `cfr_vfr.state="uncertain"`, confidence=0.5, continue | 0.5 |
| FFprobe version incompatible | Fallback to mediainfo, mark provenance accordingly | 0.9 |
| Container is image sequence | Accept if duration ≤ 30s, `container.format="image2"`, set `fps_actual.type="cfr"` | 0.95 |

> **Resolution of audit item D1 — "extreme VFR":** Stage 1 §3 lists "extreme VFR" among the
> Layer 1 **rejection** triggers, which contradicts the row above. This row wins. The
> governing principle is "never crash, degrade confidence instead": ingestion marks
> `cfr_vfr.state="uncertain"` with confidence capped at 0.5, sets `fps_actual.state="uncertain"`,
> and **continues** to Decode. Implementing rejection here would discard usable evidence and
> break the "always produce a report" contract that Layers 2-3 rely on. Stage 1 §3 should be
> corrected to read "flag extreme VFR", not "reject".
>
> **Implemented:** `Ingestor._analyze_cfr_vfr` (`is_vfr and max_delta > 0.1`).

---

## 2.8 Example SourceDescription (MP4 from iPhone)

```yaml
SourceDescription:
  id: "src_2f4a1b8e-c3d2-4e1f-9a5b-7c8d9e0f1a2b"
  source_path: "/videos/iphone_15_pro_dolby_001.mp4"

  container:
    format: "mp4"
    format_long: "MOV MP4 MPEG-4 Raw"
    size_bytes: 14789234

  video_stream:
    codec: "hevc"
    codec_long: "H.265 / HEVC / MPEG-H Part 2"
    profile: "main 10"
    level: "5.1"
    width: 1920
    height: 1080
    coded_width: 1920
    coded_height: 1088          # internal encoding padding
    display_aspect_ratio: "16:9"
    sample_aspect_ratio: "1:1"
    frame_rate: "6000/1001"     # 59.94
    avg_frame_rate: "6000/1001"
    time_base: "1/60000"
    nb_frames: 1798

  fps_actual:
    value: 59.94
    type: "cfr"
    confidence: 0.95
    provenance:
      tool: "ffprobe-6.1"
      raw_rational: "6000/1001"

  cfr_vfr:
    is_cfr: true
    is_vfr: false
    variance: 0.0
    max_delta: 0.001
    confidence: 0.98
    provenance:
      tool: "ffprobe-6.1"
      method: "packet_pts_analysis"
      samples_checked: 1798

  duration:
    value: 30.0
    start_time: 0.0
    end_time: 30.0
    confidence: 0.99
    provenance:
      tool: "ffprobe-6.1"
      method: "format_duration"

  audio_streams:
    - stream_index: 1
      codec: "aac"
      codec_long: "AAC (Advanced Audio Coding)"
      sample_rate: 48000
      channels: 2
      channel_layout: "stereo"
      bit_rate: 256000
      language: "und"
      title: null

  bit_depth:
    luma: 10
    chroma: 10
    confidence: 0.90
    provenance:
      tool: "ffprobe-6.1"
      method: "stream_profile_analysis"

  color_space:
    value: "yuv420p10le"
    full_name: "YUV color system with 10-bit components, little-endian"
    confidence: 0.95
    provenance:
      tool: "ffprobe-6.1"

  transfer:
    value: "bt2020"
    confidence: 0.90
    provenance:
      tool: "ffprobe-6.1"

  chroma:
    subsampling: "4:2:0"
    confidence: 0.95
    provenance:
      tool: "ffprobe-6.1"

  generational_estimate:
    value: "prosumer_phone"
    confidence: 0.75
    provenance:
      tool: "metadata_heuristic_v1"
      factors: ["hevc_profile_main_10", "10bit_depth", "iphone_isp_characteristics"]

  quality_score:
    value: 0.87
    state: "measured"
    confidence: 0.85
    provenance:
      tool: "ffprobe-6.1"
      method: "bitrate_resolution_model"
```

---

## 2.9 Implementation Notes

### FFprobe Command Pattern

```bash
ffprobe \
  -v quiet \
  -print_format json \
  -show_format \
  -show_streams \
  -count_frames \
  -select_streams v:0 \
  <input>
```

For VFR analysis, a separate pass with packet-level PTS extraction:

```bash
ffprobe \
  -v quiet \
  -select_streams v:0 \
  -show_entries packet=pts_time,flags \
  -of csv=p=0 \
  <input>
```

### Validation Order

1. Parse file → if fail, reject
2. Check duration ≤ 30s → if fail, reject with message
3. Extract video_stream fields → validate presence
4. Extract audio_streams → array (may be empty)
5. VFR analysis → compute `fps_actual` and `cfr_vfr`
6. OPTIONAL extraction (bit_depth, color_space, etc.) → mark confidence per field
7. Apply validation rules → produce quality flags
8. Emit `SourceDescription`

---

## 2.10 Test Corpus Plan (See §10.2.1)

SourceDescription must be tested against at least 20 videos of varying containers:

| Category | Container | Codec | Count |
|---|---|---|---|
| iPhone (recent) | mp4 | hevc + aac | 3 |
| iPhone (older) | mp4 | h264 + aac | 2 |
| Android | mp4/mov | hevc/h264 + aac | 3 |
| DSLR/mirrorless | mp4/mov | h264/h265 + pcm/aac | 3 |
| Screen recording | mp4/mov | h264 + aac/opus | 2 |
| Web video | webm | vp9/av1 + opus | 2 |
| Broadcast | mp4 | h264 + aac | 2 |
| Variable Frame Rate | mp4 | h264 + aac | 2 |
| Silent video | mp4 | h264 | 1 |
| Image sequence | image2 | png sequence | 1 |
| MKV container | mkv | h264 + aac | 1 |

Each test verifies:
- All REQUIRED fields populated
- Duration check enforced
- CFR/VFR correctly classified
- Audio streams correctly enumerated or empty array

---

## 2.11 Stage 2 Success Criterion

Stage 2 succeeds when:

1. ✅ `SourceDescription` schema is fully specified with every field typed, categorized (REQUIRED/OPTIONAL/UNCERTAIN-ALLOWED), and confidence-assigned.
2. ✅ Production matrix maps every field to its FFprobe probe path and confidence value.
3. ✅ Validation rules (duration, readability, stream presence) are defined with actionable rejection messages.
4. ✅ Failure modes and recovery paths are enumerated.
5. ✅ A testable spec exists with ≥20 video corpus plan covering all container/format combinations.
6. ✅ Provenance + confidence envelope format is defined for all fields crossing the SOURCE-NATIVE → ANALYSIS-NORMALIZED boundary.

**Stage 2 is complete and ready for Stage 3 (Decode + Representation).**

---

## 2.12 Stage 1 Conformance Gate — Audit Reconciliation

Before Stage 2 was locked, Contract #1 and the Block 1 code were audited against the Stage 1
architecture document. Outcome and resolutions:

### Contract #1 extensions (schema changed by this audit)

| Change | Reason |
|---|---|
| `state` added to `bit_depth`, `color_space`, `transfer`, `chroma`, `generational_estimate` | Stage 1 §9.1 requires ABSENT-ALLOWED groups to expose `state: absent` so downstream can distinguish "looked for and not found" from "not applicable (null)". Without it the requirement was unsatisfiable. |
| `state = "uncertain"` now reachable on `quality_score` | §2.5 says "Uncertain if insufficient data", but both branches of the heuristic set `measured`, making `uncertain` dead. Now set when the codec is not in the scoring table or total bitrate < 500 kbps. |
| `color_space.state = "uncertain"` (confidence 0.5) for unrecognised pixel formats | The previous confidence expression was unreachable dead code — every pixel format took the fallback branch at 0.95 confidence. |
| `state = "absent"` on `generational_estimate` when no metadata factor matched (`value == "unknown"`) | "Looked for, not found" per §9.1. |

### Bulletins — contradictions resolved

1. **D1 "Extreme VFR": reject vs continue** → resolved in favour of **flag + continue** (see §2.7 note). Stage 1 §3's wording must be corrected.
2. **D2 Envelope key drift** → resolved in favour of **Stage 1 §6** (`evidence_refs[]`, `transform_type`, `source{layer, model, tool}`, plus `validation`). §2.4 is now normative and matches `utils/confidence.py`. Any downstream doc using `evidence_ref` / `transform` / `source.method` is wrong.

### Contract #2 / #3 extensions (§6 envelope completion)

Stage 1 §6 requires every important field to carry `VALUE + SOURCE LAYER + PROVENANCE[] +
CONFIDENCE + FIDELITY + VALIDATION`. Contracts #2 and #3 previously carried **none** of it —
the Decoder and QualityAnalyzer both built confidence/provenance objects and then discarded
them, silently dropping the boundary-crossing record that §4 depends on.

| Contract | Added | Notes |
|---|---|---|
| #2 `DecodedVideo` | `confidence`, `provenance[]`, `state`, `uncertain_frames[]` | `state="uncertain"` + the failing frame indices implement §3 Layer 2 "partial decode → mark segments UNCERTAIN, continue". A partial decode no longer rewrites the source-native `cfr_vfr` verdict (§4 — nothing may leak upward). |
| #3 `QualityReport` | `source`, `provenance[]` | Tagged `layer=evidence`, `tool=numpy`. `confidence_delta = -0.05` per §6.1 Rule 5. `extraction_status` now agrees with `state` (`uncertain` when no frames were sampled). |
| Jobs (`workspace/jobs/*.json`) | `schema_version: 1` | §9 Decision 5. `recover_job()` warns rather than silently misreading state written by a newer schema. |

### Open items carried into Stage 3+

| Ref | Item | Owner |
|---|---|---|
| R1 | §2.6 Rule 4 (nb_frames confidence 0.7) needs `nb_frames` promoted to an enveloped group | Stage 2/3 schema decision |
| R2 | `container.format` normalises any QuickTime file to `"mp4"`; FFmpeg reports `mov` and `mp4` under one identical format name, so distinguishing them requires the file extension, not the probe | Stage 2 |
| R3 | The §2.10 corpus plan (11 categories, ≥20 videos) has no real fixtures — all current tests use one synthetic 160x120 clip generated in-process. This is why the anamorphic SAR/DAR defect (§2.2 `sample_aspect_ratio`) went unnoticed | Stage 18 harness, corpus needed earlier |
| R4 | §1 "Receives: … optional user config `{expected_type, focus}`" has no entry point anywhere in the API | Stage 11+ |

---

# Amendment Record — v1.0 → v1.1 (`sample_aspect_ratio` may express absence)

> **Register row G10, Stage 2.3 row A9. Owner: this document** (the field's owning contract).
> Triggered by §2.1's controlled amendment discipline; §2.1 v1.3 and v1.4 both explicitly
> *declined* to make this change, because it is not theirs to make.
> **Scope: this one field's type. Nothing else in this document is amended.**

## 1. What changed, and the before/after

```text
BEFORE  stage2_source_description.md:47   sample_aspect_ratio: string    # REQUIRED
        models/source_description.py:124  sample_aspect_ratio: str
        ingestion/ingestor.py:447         _format_display_ratio(sar, fallback="1:1")

AFTER   sample_aspect_ratio: string?       # OPTIONAL; null == the source declares none
        sample_aspect_ratio: Optional[str]
        _format_display_ratio(sar, fallback=None)
```

## 2. The finding (evidence, not preference)

`sample_aspect_ratio` is a **T1 flat field with no per-field `ObservationState`**. Under §2.1.4
Dimension B, absence must be expressed as a *state*, never as a fabricated value. A T1 field cannot
carry a state, so the repo solved the problem by **inventing a value**: when PyAV reported
`sample_aspect_ratio = None` (measured — the stream declares none), the ingestor wrote the string
`"1:1"`.

**The string is indistinguishable from a genuinely declared 1:1.** A consumer reading
`sample_aspect_ratio = "1:1"` cannot tell "this is square" from "this container told us nothing and
2.3 guessed square on its behalf". That is exactly the failure A9 names: *technical plausibility
becoming declared metadata*.

**The sentinel is forced by the type, not chosen in error.** `fallback=None` was not representable
before this amendment: Pydantic would reject `None` against `str`. So the defect could not be fixed at
the call site — it had to be fixed **here**, in the contract that declares the type. That is why this
is an amendment to this document rather than a 2.15 patch.

## 3. Normative rules

| # | Rule |
|---|---|
| **S-1** | `sample_aspect_ratio` is `Optional[str]`. When the source declares none, the value is `null`. **Never** `"1:1"`, `"unknown"`, `"N/A"`, `"none"`, or any other substitution. |
| **S-2** | The key remains **REQUIRED** in the group. `null` means *"checked; the source declares none"* — not "not applicable". Omitting the key would conflate absence with non-applicability (§2.1.4-B reserves `null` for the latter, and this field **is** applicable). |
| **S-3** | A **present** value must be a reduced `N:M` with `N > 0` and `M > 0`. A non-positive or unparseable source value yields `null`, never a fallback ratio. |
| **S-4** | **`display_aspect_ratio` is NOT amended by this record.** It has the identical sentinel (`fallback="0:1"`, `ingestor.py:444`) and is listed in §5 as a separate open item. Bundling it would repeat the v1.1→v1.2 mistake, and its own check gap must be recorded before it is changed. |
| **S-5** | **Residual, stated not hidden.** `_format_display_ratio` collapses four distinct conditions into one `fallback`: `None` (absent), an unparseable shape, an unparseable value, and `num <= 0` (invalid). At T1 granularity these cannot be separated, so `null` will mean *"no usable value"* rather than strictly *"declares none"*. This amendment removes the **fabricated value**; it does not create the per-field state that would separate `absent` from `unavailable`. Closing that is a Dimension B question for §2.1, not a typing fix. |

## 4. What this does not do

```text
  does NOT  change display_aspect_ratio          (S-4; separate item, see §5)
  does NOT  add a per-field ObservationState     (S-5; that is Dimension B work, §2.1's)
  does NOT  modify the Stage 2.3 contract        (no stage accommodates another to absorb its own cost)
  does NOT  touch G18 / R-2 / 2.15               (separate owner, separate pass)
  does NOT  change the group tier                (still T1)
```

## 5. Open item raised by this record

| Ref | Item | Owner |
|---|---|---|
| **A9-DAR** | `display_aspect_ratio` carries the same defect via `fallback="0:1"` (`ingestor.py:444`), and **the Stage 2.3 A9 check cannot see it**: its sentinel tuple is `("unknown", "1:1", "N/A", "none")` and contains no `"0:1"`. Until both are addressed, an A9 `PASS` would be reporting the absence of a *detectable* sentinel, not the absence of sentinels. | §2.1 / this document — **separate amendment** |

## 6. Execution

Type changed here; the mechanical call-site change (`fallback=None`, and widening
`_format_display_ratio`'s own `fallback` parameter to `Optional[str]`) is **2.15's** and was applied in
the same pass, because leaving the contract and the code disagreeing would recreate exactly the
"spec says X, code says Y" state this record exists to prevent. **Whether A9 closes is the gate's
decision, not this record's** — and §5 must be read first.


---

# Amendment Record — v1.1 → v1.2 (`display_aspect_ratio` may express absence)

> **Standalone by construction.** v1.1 §5 raised `A9-DAR` as a separate open item and
> explicitly *declined* to fold this into the same record. This is that separate record.
> Register row **G10**, Stage 2.3 row **A9**. Scope: this one field's type.

## 1. Why this is a separate amendment rather than a continuation of v1.1

v1.1 fixed `sample_aspect_ratio`. It found `display_aspect_ratio` carrying the **identical** defect
and left it alone under S-4, recording the reason. Two findings were therefore in play and only one
was discharged.

The delay was not incidental — it exposed something v1.1 could not have predicted:

> **Stage 2.3's A9 check went green while this sentinel was still being emitted.**

Its sentinel tuple was `("unknown", "1:1", "N/A", "none")` and contained no `"0:1"`, so it reported
`sentinel-valued fields=none` while `display_aspect_ratio='0:1'` was present in the same contract.
**A green row that did not cover its own invariant is worse than a red one**, because it is consumed
as a discharge.

## 2. What changed

```text
BEFORE  stage2_source_description.md:46   display_aspect_ratio: string    # REQUIRED
        models/source_description.py:123  display_aspect_ratio: str
        ingestion/ingestor.py:444         _format_display_ratio(dar, fallback="0:1")

AFTER   display_aspect_ratio: string?      # OPTIONAL; null == the source declares none
        display_aspect_ratio: Optional[str]
        _format_display_ratio(dar, fallback=None)
```

`"0:1"` was worse than `"1:1"` as a fabrication: a **zero** aspect ratio is not a displayable shape, so
no consumer could mistake it for a measured value — yet it was being emitted as though it were one.

## 3. Normative rules (v1.2)

| # | Rule |
|---|---|
| **S-1** | `display_aspect_ratio` is `Optional[str]`. When the source declares none, the value is `null`. **Never** `"0:1"`, `"1:1"`, or any other substitution. |
| **S-2** | The key stays **REQUIRED**. `null` means *"checked; the source declares none"* — not "not applicable" (§2.1.4-B reserves `null` for the latter, and this field **is** applicable). |
| **S-3** | A present value must be `N:M` with `N > 0` and `M > 0`. Non-positive or unparseable yields `null`. |
| **S-4** | **v1.1's S-5 residual is unchanged and is NOT addressed here.** `fallback=None` means four conditions still collapse into one result (absent / unparseable shape / unparseable value / non-positive). That is an **observation-state** question at T1 granularity, owned by §2.1 Dimension B — not a typing fix, and not fixable by any change to this field's type. Recording it again here would imply v1.2 solved it. It did not. |
| **S-5** | **Both** ratio fields now follow one rule. Any future field that formats an absent measurement through `_format_display_ratio` inherits `null`, and MUST NOT reintroduce a string fallback. |

## 4. What v1.2 does not do

```text
  does NOT  solve the absent-vs-unavailable distinction      (S-4; v1.1 S-5, unchanged; Dimension B's)
  does NOT  add a per-field ObservationState                (S-4; §2.1's, not this document's)
  does NOT  reopen the Stage 2.3 contract                   (the check was corrected instead; see §5)
  does NOT  touch G18 / R-2 / 2.15, or G17 / §2.16
  does NOT  reopen §2.1 v1.3 or v1.4
```

## 5. The verification check was corrected BEFORE this change, not after

This mirrors the A8 precedent exactly. Order of events:

```text
  1. add "0:1" to the A9 sentinel set
  2. re-run the gate  ->  A9 FAIL, naming display_aspect_ratio='0:1'
                          (proof the corrected check actually SEES the defect)
  3. amend THIS document, then implement  (this record)
  4. re-run the gate  ->  A9 decides
```

The A9 check additionally now **verifies its own completeness**: it reads every `fallback=` used in
`ingestion/ingestor.py` and fails if src/ fabricates a default the sentinel set cannot recognise. So a
future `fallback="2:1"` produces *"the check cannot see a fallback src/ is actually using"* rather
than a silent green.

## 6. Execution (v1.2)

Type changed here; the mechanical call-site change (`fallback=None`) was applied in the same pass so
the contract and the code never disagree. **Whether A9 closes is the gate's decision, not this
record's.**

| R5 | `fidelity` + `validation` envelopes are only populated on the five optional Contract #1 groups; Container/VideoStream/AudioStream/FpsActual/CfrVfr/DurationInfo/QualityScore are not wrapped | Stage 13 (DNA assembly) |
