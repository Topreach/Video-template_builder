# STAGE 2.1 — Contract #1: Responsibility & Boundary

**Stage:** 2 | **Sub-section:** 2.1 | **Contract:** #1 `SourceDescription`
**Status:** CLOSED v1.2 — amended twice under controlled procedure (§2.1.14 code set → v1.1; §2.1.15 envelope vocabulary → v1.2); was CLOSED v1, CLOSED v1.1
**Governs:** the field-level work of 2.2–2.15
**Supersedes:** nothing. Subordinate to Stage 1 (CLOSED). Extends `stage2_source_description.md`.

> This section fixes the *discipline* of Contract #1 — what it is responsible for, what it
> must never touch, how a field is described, and how the ingestion gate is expressed.
> Once §2.1.10 is closed, 2.2–2.15 may add fields freely **without reopening anything here**.

---

## 2.1.1 The One Question This Contract Answers

> **"What is this source, technically — and may the Builder safely hand it to Decode?"**

Two halves, both mandatory, in this order:

1. **Description** — technical identity and structure of the source file.
2. **Gate** — `ingestion_status`, the decision variable that authorises or forbids Decode.

The contract answers *neither* "what happens in the video" (Evidence/Semantic) *nor*
"how good is the signal" (QualityReport).

### Explicit non-questions

| Question | Owner | Why not Contract #1 |
|---|---|---|
| Is the frame blurry / noisy / banded / compressed? | `QualityReport` | signal reliability, Stage 1 §3 Layer 3 |
| Two 16:9 sources from the same source bytes, same `SourceDescription`? | — | not a description concern |
| Is there a person? a face? text? | Spatial/Text Evidence | bypasses Stage 1 §4 boundary |
| Is the camera panning? | MotionEvidence | semantic-adjacent, Layer 7 |
| Will generation reproduce the video? | Generator | Builder/Generator split, Stage 1 §1 |

---

## 2.1.2 Responsibility Scope (normative)

### In scope

| Area | Sub-section |
|---|---|
| Source identity (hash, size, filename policy) | 2.2 |
| Container identity (actual container, not file extension) | 2.3 |
| Video stream identity (codec, profile, level, dimensions) | 2.4–2.5 |
| Timing authority (nominal vs actual, PTS, frame count, duration) | 2.6 |
| Pixel representation (pix_fmt, bit depth, chroma) — *descriptive, not judgemental* | 2.7 |
| Color metadata — **declared** vs **inferred**, kept distinguishable | 2.8 |
| Audio at stream-description level only | 2.9 |
| Geometry/orientation canonicalisation before Decode | 2.10 |
| Metadata preserve/normalize/ignore policy | 2.11 |
| Validation + `ingestion_status` gate | 2.12–2.13 |
| Missing/uncertain/unavailable representation | 2.14 |
| Schema, JSON Schema, versioning | 2.15 |

### Out of scope (hard boundaries)

| Must never appear in Contract #1 | True owner |
|---|---|
| blur / noise / blocking / banding severity, overall quality score | `QualityReport` §3 L3 |
| generational estimate as a *reliability* judgement | see §2.1.13 (D-2 lock) |
| character / object counts, detections, masks | Spatial (+Entity) |
| shot, scene, cut, beat | Temporal |
| camera motion, optical flow, pose | Motion |
| speech, music, speaker, emotion | AudioEvidence / Semantic |
| OCR strings | TextEvidence |
| actions, roles, relationships, story beats | SemanticStructure |
| analysis-normalized pixels (e.g. 1024×576 tensors) | ANALYSIS-NORMALIZED (§4) |
| any Template DNA field | DNA Assembly |

**Rule:** a field may only enter Contract #1 with a named producer (§2.1.4) *and* a named
downstream consumer or ingestion-purpose. "The tool happened to return it" is not a reason.
This is the anti-`ffprobe`-dump rule: the adapter produces a controlled vocabulary, not a mirror.

---

## 2.1.3 Three Identities — Which One Lives in Contract #1

```
sha256(source bytes)        processing_run_id            dna_version
        │                          │                          │
        ▼                          ▼                          ▼
  SOURCE IDENTITY           PROCESSING IDENTITY         DNA IDENTITY
  ← Contract #1 owns →      ← Job/pipeline owns →       ← Contract #11 owns →
```

| Identity | Field | Lives in | Notes |
|---|---|---|---|
| Source | `source_identity.hash_sha256` | **Contract #1** | immutable, content-addressed, stable |
| Source | `source_identity.size_bytes` | **Contract #1** | stable |
| Processing | `job.id` | pipeline (`workspace/jobs/<id>.json`) | already implemented, `job_<hex16>` |
| DNA | `version`, `schema_version` | Contract #11 | Stage 13/15 |

**Rules**

- The same source hash may map to **many** processing runs and **many** DNA versions. Never
  treat the hash as a job id or a DNA id.
- Identical bytes do **not** imply identical downstream results once models/tools change.
  Tool/model/pipeline/schema versions are recorded as *provenance on estimates* (§2.1.4
  Stability), never folded into the hash.

---

## 2.1.4 The Four Field Dimensions (normative — inherited by Contracts #2–#12)

A field is never described by its value alone. Every field in Contract #1 declares four
independent dimensions. They are orthogonal: knowing one tells you nothing about another.

### Dimension A — Representation Tier

| Tier | Shape | Obligation | Examples |
|---|---|---|---|
| **T1** | bare scalar/enum | no per-field envelope. Traceability is inherited from the parent group's single `source` + `provenance`. | `codec: h264`, `width: 1920`, `size_bytes: 8123456` |
| **T2** | `{value, state, confidence}` | measurement that can be wrong. Confidence **required**. | `fps_actual`, `duration.presentation`, `nb_frames` |
| **T3** | `{value, state, confidence, source, provenance[], fidelity?, validation?}` | inferred / multi-evidence / heuristic. Full Stage 1 §6 envelope. | `generational_estimate`, any field derived from more than one evidence source |

**Tier assignment rules (mechanical, no judgement calls):**

1. Value is returned by a single structural probe → **T1**.
2. Value is *computed* from probes (arithmetic/rational conversion) but not inferred → **T2**.
3. Value depends on a heuristic, a threshold, a statistical characterisation, or ≥2 evidence
   sources → **T3**.
4. Any value derived from *decoded frames* is at least **T2** (never T1).

This satisfies Stage 1 §6 proportionately: "every important field" gets the envelope, while a
directly-observed scalar keeps the cheap representation. A T1 group still carries `source` +
`provenance` at the group level, so traceability is never lost.

### Dimension B — Observation State

```
EXTRACTED      the Builder obtained the value
ABSENT         the Builder checked; the property does not exist in this source
UNCERTAIN      evidence exists; the Builder cannot establish the value confidently
UNAVAILABLE    the Builder could not determine the value (probe failed / no evidence)
```

**State decision procedure — ordered, first match wins, fully deterministic:**

| Step | Test | Result |
|---|---|---|
| 1 | Property is contractually **REQUIRED** and cannot be obtained | **REJECT** (§2.1.5) — never `null`, never `unavailable` |
| 2 | Property is structurally impossible for this source (e.g. audio stream in a video-only file) | `absent` + (usually) group emitted, not `null` |
| 3 | Property is expected, but the probe returned nothing or raised | `unavailable` |
| 4 | A value was obtained, but evidence conflicts, or measurement falls below the field's floor | `uncertain` + confidence ≤ 0.65 (§6.1 Rule 4) |
| 5 | Otherwise | `extracted` (+ confidence for T2/T3) |

**Hard rules**

- `absent` is a **positive assertion** ("I looked; it is not there"). `unavailable` is a
  **capability statement** ("I could not establish it"). They are never interchangeable.
- A `null` group means *not applicable to this video type / not analysed yet*. It is **never**
  used to mean "looked for and not found" — that is `state: absent`. (This closes audit C1
  permanently, for all twelve contracts.)
- `uncertain` and `unavailable` propagate downward: consumers must cap their own confidence at
  the weakest required input (§6.1 Rule 3/4) rather than recomputing from scratch.

### Dimension C — Stability

| Stability | Meaning | Cache policy |
|---|---|---|
| `stable` | identical for identical source bytes, across tools/versions | cacheable indefinitely, keyed by `source_identity.hash_sha256` |
| `estimate` | may change with decoder/tool/heuristic/model version | must record producer version in `provenance`; invalidate on producer version change |

Stable: hash, size, container identity, codec, width, height, declared pix_fmt.
Estimate: actual FPS, CFR/VFR classification, presentation duration, any heuristic inference.

**Rule:** an `estimate` field whose `provenance` does not identify the producer version is
non-conformant. This is the hook where decoder/tool/model versioning attaches (§36) — it is
deliberately *not* overloaded into the source hash. *(v1.2: the vocabulary that carries it is
`provenance[].tool_version` and, for model-backed values, `provenance[].model_version` — semantics,
state rules and cache-gating in **§2.1.15**. Until v1.2 this rule had no referent; that gap was
finding G8, and it is the reason the record exists.)*

### Dimension D — Contract Requirement

```
REQUIRED            must be present, else the contract is invalid → REJECT
OPTIONAL            present only if the analysis succeeded; `null` otherwise
ABSENT-ALLOWED      schema supports an explicit "checked, not there"
UNCERTAIN-ALLOWED   schema supports explicit ambiguity + low confidence
UNAVAILABLE-ALLOWED schema supports explicit "could not determine"
```

### Orthogonality — legal Requirement × State combinations

| Requirement \ State | extracted | absent | uncertain | unavailable | `null` group |
|---|---|---|---|---|---|
| REQUIRED | ✅ only legal outcome | ❌ reject | ❌ reject | ❌ reject | ❌ reject |
| OPTIONAL | ✅ | ✅ | ✅ | ✅ | ✅ |
| ABSENT-ALLOWED | ✅ | ✅ | ✅ | ✅ | ✅ |
| UNCERTAIN-ALLOWED | ✅ | ⚠️ allowed, warn | ✅ | ✅ | ✅ |
| UNAVAILABLE-ALLOWED | ✅ | ✅ | ✅ | ✅ | ✅ |

**Rule:** a `rejected` `ingestion_status` must name a code from §2.1.5, and the reason must be
traceable to a REQUIRED field per the table above.

---

## 2.1.5 `ingestion_status` — The Contract-Level Gate

```yaml
ingestion_status:
  status: accepted | accepted_with_warnings | rejected
  reason: null | REJ_*          # exactly one code when rejected, else null
  warnings: [ WARN_* ]          # zero or more, in evaluation order
```

**What the gate answers:** *may Decode operate on this source?*
**What it does NOT answer:** *is this source good?* (QualityReport), *will analysis succeed?*
(later layers), *is the content interesting?* (Semantic).

### Rejection is a contract outcome, not an exception

**A rejected source still produces a `SourceDescription`.** The Builder retains everything it
legitimately learned, so the result stays diagnosable, testable, user-explainable, and reusable
when decoder support expands.

| Source that… | Contract must still carry |
|---|---|
| cannot be opened as a container | `schema`, `source_identity` (may be hash+size only), `ingestion_status` |
| has no video stream | + `container` |
| has an undecodable video codec | + `container`, `video.codec`, profile/level/pix_fmt |
| exceeds 30 s | the full technical description (Decode is simply never reached) |

An exception escaping ingestion is reserved for **Builder-internal faults** (bug, I/O failure
mid-write, OOM) — never for a source condition. This differs from the shipped implementation,
which raises `IngestionError` (§2.1.9).

### Rejection codes (closed set, v1.1 — see §2.1.14 for the version record)

| Code | Condition | Needs probe |
|---|---|---|
| `REJ_FILE_NOT_FOUND` | path missing / not a regular file | — |
| `REJ_FILE_EMPTY` | size 0 | — |
| `REJ_FILE_UNREADABLE` | I/O error while reading | — |
| `REJ_CONTAINER_PARSE_FAILED` | bytes present, cannot be parsed | ✔ |
| `REJ_CONTAINER_UNRECOGNIZED` | parsed, format unknown to the runtime | ✔ |
| `REJ_NO_VIDEO_STREAM` | container has no video stream | — |
| `REJ_UNSUPPORTED_VIDEO_CODEC` | codec id unknown to the runtime | ✔ |
| `REJ_DECODER_UNAVAILABLE` | codec known, but profile/level/bit depth/pix_fmt unsupported | ✔ |
| `REJ_NO_DECODABLE_FRAMES` | decoder opens, yields no usable frame in the probe window | ✔ |
| `REJ_SOURCE_CORRUPT` | corruption prevents safe parsing/decoding | ✔ |
| `REJ_SPOOL_EXHAUSTED` **(v1.1)** | mandatory spool write fails — storage exhaustion or quota (`ENOSPC`) | stream spool |
| `REJ_DURATION_EXCEEDS_MAX` | authoritative duration > `MAX_DURATION` | timing |
| `REJ_DURATION_BELOW_MIN` | authoritative duration < `MIN_DURATION` | timing |
| `REJ_TIMING_UNUSABLE` | neither presentation nor declared timing can be established | timing |

### Warning codes (open set — additive only)

| Code | Meaning |
|---|---|
| `WARN_VFR_DETECTED` | variable frame rate; timing needs downstream awareness |
| `WARN_EXTREME_VFR_JITTER` | VFR with `max_delta > 0.1 s`; classification `uncertain` |
| `WARN_TIMING_ANOMALY` | duplicate / non-advancing PTS in display order |
| `WARN_TIMING_EVIDENCE_SPARSE` | too few PTS samples to classify confidently |
| `WARN_COLOR_METADATA_UNAVAILABLE` | color tags not declared by the container |
| `WARN_UNUSUAL_ASPECT_RATIO` | SAR/DAR outside the common set |
| `WARN_ORIENTATION_NORMALIZATION_REQUIRED` | rotation/flip metadata present |
| `WARN_UNUSUAL_AUDIO_CODEC` | decodable but uncommon |
| `WARN_MULTIPLE_VIDEO_STREAMS` | stream selection was ambiguous; first selected |
| `WARN_SOFTWARE_DECODE_ONLY` | no hardware acceleration for this source |
| `WARN_CONTAINER_VARIANT` | uncommon variant of a known container |
| `WARN_DURATION_NEAR_BOUNDARY` | within 1 % of `MAX_DURATION` or `MIN_DURATION` |

**Rule:** a warning is **not** a quality score. `WARN_VFR_DETECTED` does not mean "bad video"; it
means "timing requires downstream awareness". Warnings must never be aggregated into a score
inside Contract #1.

### Evaluation order (deterministic; first failure wins, all warnings collected)

```
1  file exists / regular / non-empty / readable           → source_identity
   (stream_handle: the mandatory spool completes inside step 1;
    spool-write failure → REJ_SPOOL_EXHAUSTED — v1.1, see §2.1.14)
2  container parse + recognition                          → container
3  video stream presence                                  → video
4  video stream parameters (codec/profile/level/dims/pix_fmt)
5  decoder capability probe (bounded — §2.1.5.1)           → REJ_UNSUPPORTED_*/DECODER_*/CORRUPT
6  timing evidence collection (declared + PTS)
7  timing usability                                        → REJ_TIMING_UNUSABLE
8  duration bounds on the AUTHORITATIVE duration           → REJ_DURATION_EXCEEDS_MAX / BELOW_MIN
9  audio stream description
10 optional groups (bit depth, chroma, color, transfer, geometry)
11 state assignment per field (§2.1.4 B)
12 warnings collected and ordered
13 ingestion_status emitted
```

**Note (resolves audit R6):** video-stream presence (step 3) is evaluated **before** duration
(step 8); the old spec §2.9 ordering did the reverse. Structural gates are cheaper and more
fundamental, and a 60-second file with no video stream now reports the more actionable
`REJ_NO_VIDEO_STREAM`. This supersedes §2.9's ordering.

### 2.1.5.1 Capability probe — the Ingestion ↔ Decode boundary

Probe-requiring codes involve attempting to decode, which otherwise belongs to Layer 2.

- Ingestion may run a **bounded decoder capability probe**: open the decoder, decode **at most
  N ≤ 3 frames** into a scratch buffer, discard them.
- The probe **must not** produce `DecodedVideo`, write frames to disk, or normalize pixels, and
  its work **must not** be reused by Layer 2.
- Its only outputs are: `decodable: bool` + one rejection code + the codec parameters.
- Rationale: `accepted` must distinguish "codec identified" from "codec actually decodable"
  (§41). Identifying a codec is insufficient — profile, level, bit depth and pix_fmt must all
  be supported too.

This keeps the representation boundary intact: the probe touches SOURCE-NATIVE only to confirm
liveness, and produces no representation.

---

## 2.1.6 Boundaries

### With Decode (Layer 2)

**Decode may rely on these invariants** — no re-validation needed:

1. `ingestion_status.status ∈ {accepted, accepted_with_warnings}`.
2. `video.codec`, `width`, `height`, `pix_fmt` are non-null and the decoder is capable of them.
3. At least one frame is decodable (capability probe passed).
4. Geometry has a canonical interpretation (2.10): `display_*` are the presentation dimensions
   after rotation; `coded_*` are storage dimensions.
5. Timing is honest: `duration.presentation.state` and `cfr_vfr.state` tell Decode exactly how
   much to trust them.

**Decode must not rely on:** colour metadata being present, audio existing, `nb_frames` being
exact, or `cfr_vfr` being anything other than an estimate.

### With Quality (Layer 3)

Contract #1 supplies **availability facts**, not judgements. It may state "bitrate is X,
resolution is Y, codec is Z"; it may not conclude "therefore quality is 0.87". The one contested
field group is `quality_score` / `generational_estimate` — see **D-2**. Under either resolution:

- `QualityReport` remains the **authoritative** signal-reliability contract (Stage 1 §3 L3).
- Contract #1 must not grow blur / noise / blocking / banding metrics.

### With Stage 1 (conformance map)

| Stage 1 clause | Status after §2.1 |
|---|---|
| §1 "Receives: video file ≤30 s" | conforms; `MIN_DURATION` is an explicit Builder product rule, not a media rule |
| §3 L1 "Reject >30 s, unreadable, extreme VFR" | **amendment required** — rejection is now `ingestion_status`; extreme VFR is a *warning* |
| §3 L1 "Never crash. Actionable error message." | strengthened: never throws for a source condition; always emits a typed contract + machine code |
| §4 representation boundaries | conforms; capability probe explicitly bounded (§2.1.5.1) |
| §6 confidence + provenance envelope | conforms via tiering — T1 inherits group-level `source`/`provenance` |
| §8 Contract #1 is the only L1→L2 crossing | conforms |
| §9.1 requirement categories | **amendment required** — add `UNAVAILABLE-ALLOWED`; rename `measured` → `extracted` (D-1) |
| §9 D5 versioned schema | now extends to the contract itself via `schema.version` (2.15) |

---

## 2.1.7 Naming & Namespace Rules (frozen)

| Rule | Detail |
|---|---|
| **`source` is reserved** | `source` is the §6 envelope key (`{layer, model, tool}`), used inside every group. The identity block is therefore named **`source_identity`** — never `source`. |
| Top level | `schema`, `source_identity`, `container`, `video`, `timing`, `audio_streams`, `ingestion_status` (+ the optional groups and the D-2 verdict) |
| Envelope keys (frozen) | `value`, `state`, `confidence`, `source`, `provenance`, `fidelity`, `validation` — exactly the keys of `utils/confidence.py` |
| State literals (frozen) | `extracted`, `absent`, `uncertain`, `unavailable` — lowercase in serialized form |
| Code literals | `REJ_*` / `WARN_*`, SCREAMING_SNAKE, closed for REJ, additive for WARN |
| Renames required | `state: "measured"` → `"extracted"`; `fps_actual` stays (it is the *actual* rate, distinct from nominal); `duration` becomes a group with `presentation` + `declared` |

---

## 2.1.8 Required Stage 1 Amendments (exact deltas)

These are **not** reopenings — they are corrections forced by the Stage 2 framework, recorded so
the Stage 1 document stays the single authority.

| ID | Stage 1 location | Current text | Required text |
|---|---|---|---|
| **A-1** | §9.1 | states are `extracted \| absent \| uncertain`; category list is REQUIRED / OPTIONAL / ABSENT-ALLOWED / UNCERTAIN-ALLOWED | add **`unavailable`** as a state; add **`UNAVAILABLE-ALLOWED`** as a requirement category; replace the `measured` literal everywhere (the 3 shipped models use `measured`). Applies to **all twelve** contracts, not just #1. |
| **A-2** | §3 Layer 1 failure mode | "Reject >30s, unreadable, **extreme VFR**. Never crash." | "Reject via `ingestion_status` (Stage 2 §2.1.5). **Flag** extreme VFR as `WARN_EXTREME_VFR_JITTER`. Never crash." |
| **A-3** | §3 Layer 1 failure mode | "Actionable error message" | "emits a typed `SourceDescription` carrying `ingestion_status.reason` (a `REJ_*` code) — including for rejected sources (partial contract)" |
| **A-4** | §8 / §9.1 structure | `§9.1` heading is nested under `## 8. TWELVE INTERFACE CONTRACTS` | nest under `## 9.` (editorial) |
| **A-5** | §9.1 closing sentence | "`extraction_status` in DNA reflects this: `extracted \| absent \| uncertain` per group" | keep for DNA (Contract #11); note explicitly that `extraction_status` is **not** a Contract #1 field (see D-3) |

---

## 2.1.9 Code Migration Impact (evidence-based)

Verified against the working tree on this branch. Nothing here is speculative.

### New in Contract #1 (must be added)

| Addition | Rule |
|---|---|
| `schema: {name: "SourceDescription", version: "1.0"}` | §46 |
| `source_identity: {hash_sha256, size_bytes, original_filename, source_path}` | §16 — `hashlib`/`sha256` appear **nowhere** in the repo today |
| `ingestion_status: {status, reason, warnings[]}` | §9–13 — no such field exists today; rejection is currently an exception |
| `timing.duration.presentation` + `timing.duration.declared` | §38/§40 — today there is a single `duration` group |
| `MIN_DURATION` gate | §39 — `min_duration` appears **nowhere** today; only `MAX_DURATION_SECONDS = 30.0` (`ingestor.py:43`) |
| `state: unavailable` | §6 — today only `measured \| uncertain \| absent` |
| producer-version identity in provenance | **v1.2 (§2.1.15)** — `ProvenanceEntry.tool_version` / `.model_version`, `SourceInfo.version`; none exist today (`utils/confidence.py:77-92`) |
| canonical `display_*` geometry | §24 |

### Must change (breaking)

| Location | Change |
|---|---|
| `models/source_description.py:188` | remove `extraction_status` from Contract #1 (D-3) |
| `models/source_description.py` (all `state` fields) | `"measured"` → `"extracted"` |
| `models/source_description.py:164` (`source_path`) | moves into `source_identity` |
| `models/quality_report.py:46`, `analyzer.py:96` | state vocabulary migration (A-1) — QualityReport uses `measured` today |
| `ingestion/ingestor.py:59, 63, 73, 108, 112-116` | replace 5 `raise IngestionError(...)` paths with `ingestion_status` emission + partial contract; add `REJ_*` constants |
| `ingestion/ingestor.py` | add `_compute_identity()` (sha256 + size + filename), `_build_ingestion_status()`, `_probe_decoder_capability()`, duration-authority split, min-duration gate |
| `pipeline/__init__.py:127-131` | gate on `ingestion_status.status == rejected` → `JobStatus.FAILED` with the reason code (instead of relying on `IngestionError`) |
| `cli.py:cmd_ingest` | always print the contract (even rejected); non-zero exit only on rejected |
| `tests/test_pipeline.py:74-84` | two tests assert `pytest.raises(IngestionError)` — must become `ingestion_status.status == "rejected"` + expected `REJ_*` code |
| `tests/test_pipeline.py:89, 122, 200, 296` | assert `"measured"` — must become `"extracted"` |
| `docs/specs/stage2_source_description.md` §2.2/§2.4/§2.6/§2.9 | add `ingestion_status`, `source_identity`, `schema`; vocabulary migration; superseded evaluation order; remove the `quality_score` question per D-2 |

### Unchanged by §2.1

- The VFR/PTS algorithms just implemented (C7/C8) — they now *feed* `WARN_EXTREME_VFR_JITTER` and
  `WARN_TIMING_ANOMALY` instead of only setting `state: uncertain`.
- The `Fraction`-safe aspect-ratio formatting (audit B2) — unchanged.
- Contract #2 / #3 envelope additions (audit C2/C3/C4) — unchanged.

---

## 2.1.10 Decisions — RESOLVED

**All five decisions are CLOSED.** The options table below is retained as the decision record.

| ID | Resolution | Consequence |
|---|---|---|
| **D-1** ✅ | Adopt `extracted / absent / uncertain / unavailable` **globally**, across all twelve contracts; amend Stage 1 §9.1 (A-1) | `ObservationState` added to `utils/confidence.py` (explicitly distinguished from `ConfidenceType.MEASURED`); `state` literals migrated in Contracts #1/#2/#3 + tests. **APPLIED** |
| **D-2** ✅ | **Keep** `quality_score` + `generational_estimate` in Contract #1 as *sealed ingestion-time source-native hints*; `QualityReport` remains the authoritative quality owner; Stage 2 §15 is amended to mean severity/reliability metrics only | See **§2.1.13**. The analyzer no longer mathematically chains the hint (was `0.6*frames + 0.4*hint`); the hint is recorded as prior evidence instead. **APPLIED** |
| **D-3** ✅ | Remove contract-level `extraction_status` from Contract #1; the rollup belongs to DNA (Contract #11) | Field deleted from `models/source_description.py`; `QualityReport.extraction_status` (Contract #3) is carried into Stage 4 for its own decision. **APPLIED** |
| **D-4** ✅ | Allow a bounded decoder capability probe at ingestion (N ≤ 3 frames, scratch buffer only) | §2.1.5.1 is normative. **Implementation deferred** to the Stage 2 implementation phase (framework §49), after 2.15 |
| **D-5** ✅ | Identity block is named `source_identity`; the §6 envelope key `source` stays reserved | §2.1.7 frozen. **APPLIED** in the naming rules |

### Options considered (decision record)

| ID | Decision | Options | Recommendation | Status |
|---|---|---|---|---|
| **D-1** | State vocabulary & Stage 1 §9.1 amendment | (a) adopt `extracted/absent/uncertain/unavailable` globally + amend §9.1 for all 12 contracts (b) adopt for Contract #1 only, keep `measured` in Quality/Decode with a mapping table (c) keep `measured`, map `extracted`→`measured` and add `unavailable` only | **(a)** — one vocabulary for the whole system, enforced by `utils/confidence.py`. Requires A-1 and the code/test migration in §2.1.9. Choosing (b)/(c) creates two dialects that every future contract must translate. | ⬜ open |
| **D-2** | Ownership of `quality_score` / `generational_estimate` | (a) keep both in Contract #1 as sealed source-native hints; clarify that Stage 2 §15 means *severity/reliability* metrics (b) move both out of Contract #1 into `QualityReport` only (amend Stage 1 §9.1 + spec + tests) (c) split: keep `generational_estimate` (metadata-derived), move `quality_score` | **(a)** — Stage 1 §9.1 (CLOSED) explicitly lists them under Contract #1, `QualityReport.generational_estimate_ref` already exists as the cross-reference, and the Stage 2 §15 list is about *severity* metrics. Zero code churn; one clarifying sentence in §15. | ⬜ open |
| **D-3** | Contract-level `extraction_status` | (a) delete from Contract #1 (it is a DNA-level rollup per §9.1) (b) keep as a contract-level rollup alongside per-group `state` + `ingestion_status` | **(a)** — three overlapping mechanisms for the same question is exactly the ambiguity §2.1 exists to remove. | ⬜ open |
| **D-4** | Bounded capability probe at ingestion (§2.1.5.1) | (a) allow N ≤ 3 scratch-frame probe (b) no decoding at all in ingestion; `REJ_*` decodability codes are emitted only by Layer 2 | **(a)** — required to satisfy §41 and to make `accepted` meaningful; bounded so §4 is not violated. | ⬜ open |
| **D-5** | Top-level identity block name | (a) `source_identity` (b) rename the §6 envelope key instead (c) `source_file` | **(a)** — the envelope key `source` is frozen by Stage 1 §6 and already shipped in 3 models; renaming the envelope would be a far larger, cross-contract break. | ⬜ open |

---

## 2.1.11 The Pattern Contracts #2–#12 Inherit

1. **One question** per contract (§2.1.1), stated as description + gate where applicable.
2. **Four dimensions** on every field: tier, state, stability, requirement (§2.1.4).
3. **States are orthogonal** to requirements; `absent` ≠ `unavailable` ≠ `null`.
4. **Failure is a contract outcome**, not an exception — contracts are emitted even when rejected.
5. **Deterministic evaluation order** with machine-readable codes.
6. **Frozen envelope keys** and a reserved-word list.
7. **Producer + consumer** declared for every field; no orphan fields.
8. **Anti-dump adapter rule** — controlled vocabulary, never a tool mirror.
9. **Schema version on the contract itself** (§46 / Stage 1 D5).
10. **Stability drives caching and invalidation**, and producer version lives in provenance
    (v1.2: `provenance[].tool_version` / `.model_version`, gated by exact equality — §2.1.15 R5).

---

## 2.1.12 Exit Criteria for §2.1

- [ ] D-1 … D-5 closed and recorded in this section
- [ ] Stage 1 amendments A-1 … A-5 applied to the Stage 1 document
- [ ] The top-level field inventory enumerated (§2.1.7) and agreed
- [ ] `utils/confidence.py` extended with the state literal set + a `min` helper for §6.1 Rule 3/4
- [ ] `docs/specs/stage2_source_description.md` marked as subordinate to this section, with the
      §2.1.9 change list applied
- [ ] Migration plan for `IngestionError` → `ingestion_status` agreed (tests included)

**Then, and only then, 2.2 (Source Identity) proceeds field-by-field.**

---

## 2.1.13 D-2 Semantics Lock — Quality Fields in Contract #1

D-2 kept two fields in Contract #1. This section fixes their meaning so the Contract #1 ↔
Contract #3 boundary can never drift back into ambiguity.

### Two levels of quality information

| Field | Owner | Purpose | Authority |
|---|---|---|---|
| `SourceDescription.quality_score` | **Contract #1** | preliminary ingestion-time technical source signal | **hint only** |
| `SourceDescription.generational_estimate` | **Contract #1** | metadata-derived generation-depth **estimate** | **hint only** |
| `QualityReport.score` | **Contract #3** | comprehensive quality assessment over decoded frames | **authoritative** |

They are **not interchangeable**. `QualityReport` remains the authoritative owner of
compression severity, blur, noise, blocking, banding, generational judgement, and all
tracking/OCR/semantic *reliability* implications.

### Sealed-hint rules (normative)

1. `quality_score` is a **preliminary ingestion-time** signal, not a statement about the video's
   quality. `value: 0.72` must never be surfaced as "the video is 72% good".
2. `quality_score` is computed from **source-native metadata only** (file size, duration,
   resolution, codec) — never from decoded frames, which ingest does not have.
3. `quality_score` MUST NOT be mathematically chained into `QualityReport.score`. Re-admitting it
   as an *explicit, declared* input is a **Stage 4 decision**, never an implicit one.
4. `QualityReport` may legitimately produce a different number, because it has decoded media and
   broader evidence. Divergence between the two is expected, not a bug.
5. `generational_estimate` is an **estimate**, never a measured fact. Tier is T2/T3 (T3 if it
   combines ≥2 evidence sources) — to be finalised in the field inventory (2.15), not assumed.
   Stability is `estimate`.
6. `generational_estimate` states are `extracted | uncertain | unavailable`. **`absent` is not
   allowed**: the Builder cannot assert that a source has no generation history. A heuristic
   that matches no factor returns `value: "unknown"` with `state: "unavailable"`.
7. Any heuristic producing either field must record its producer version in `provenance`
   (§2.1.4 Dimension C; field names fixed by §2.1.15 — `tool_version`, plus `model_version` where a
   model is involved), because both are invalidated by tool/model changes.

### Applied to the code

- `quality/analyzer.py` — the blend `overall_score = 0.6*frames + 0.4*source_hint` is removed.
  The authoritative score is computed from decoded frames only; when a hint exists it is
  appended to `QualityReport.provenance` as
  `{layer: source_native, evidence_refs: ["source.quality_score"], transform_type: "hint_recorded_not_chained"}`.
- `models/source_description.py` — `QualityScore` and `GenerationalEstimate` docstrings now state
  the sealed-hint meaning; `generational_estimate` can no longer emit `state="absent"`.

### Stage 4 open item

Stage 4 (Quality) must explicitly decide whether `SourceDescription.quality_score` is admitted as
a declared input to the authoritative score. Until then, it is evidence only.

---

## 2.1.14 Controlled Amendment Record — v1 → v1.1 (`REJ_SPOOL_EXHAUSTED`)

> This is **not** a correction of an error in v1. Stage 2.1 v1 was closed against the failure
> domain known at closure. Stage 2.2's §F.3.1 G3 application audit then exposed a previously
> unspecified resource-exhaustion condition (mandatory spool → `ENOSPC`) that the closed
> taxonomy could not classify without contaminating `REJ_SOURCE_CORRUPT` semantics. The set is
> therefore amended under controlled procedure — and **remains closed after amendment**.

### Decision

Add `REJ_SPOOL_EXHAUSTED` (mandatory spool write fails — storage exhaustion or quota) to the
closed `REJ_*` set. Taxonomy version: **v1 → v1.1**.

### Affected contract field

`SourceDescription.ingestion_status.reason` — new admissible value (2.15 field inventory).

### Affected producer

Mandatory `stream_handle` spool operation (§2.2A). Local-file and object-URI paths are
unchanged; they can never emit this code.

### Affected consumers

`ingestion_status` handling, job recovery lineage, CLI exit paths, persisted job records.

### Affected invariant

Resource exhaustion must not be classified as source corruption: bytes never shown to be
malformed must not be framed as a source defect, and must not poison hash-keyed dedup/lineage
caches. (The lineage-cache contamination argument is the evidence that forced the split.)

### Code impact

§2.1.5 rejection-code table (this section); the future ingestion implementation records the
failure at the spool-write step. **No `src/` changes in this pass** — implementation belongs
to the 2.15 migration, against this record.

### Tests

`ENOSPC → REJ_SPOOL_EXHAUSTED`, and it must NOT → `REJ_SOURCE_CORRUPT`. Both assertions join
the 2.15 migration test set; neither exists yet.

### Downstream affected

2.2 G3/G4 application rows, Decode (spool-path contract), recovery lineage, caching/lineage
dedup policy.

### Non-overlap verification (required before re-close)

| Condition | Code | Evidence test |
|---|---|---|
| Source bytes demonstrably malformed | `REJ_SOURCE_CORRUPT` | parse/agreement checks fail on complete bytes |
| Source unreadable | `REJ_FILE_UNREADABLE` | byte channel failed (transport, permissions, disk) |
| Spool resource exhausted | `REJ_SPOOL_EXHAUSTED` **(new)** | exhaustion evidenced post-failure (`stat -f` / store equivalent) while source bytes unremarkable |
| Internal invariant violated | INTERNAL / raise-only | Builder fault, no contract emitted |

Exactly one canonical interpretation per row; the discriminator is the layer at which the
failure is detected, never the exception class name (§2.2B.2).

### Set status after amendment

```text
Before: REJ_* = closed canonical set (v1)
Action: REJ_SPOOL_EXHAUSTED added through controlled architectural change (this record)
After:  REJ_* = closed canonical set (v1.1)
```

Future additions follow this same procedure: evidence → proposed amendment → amendment record
→ impact/conformance audit → versioned re-close. No stage may extend the set unilaterally.

### Conformance impact check

- §2.1.5 table, step-1 annotation, and status header updated in this pass (marked **v1.1**).
- §2.2's §2.2A row 11 (spool truncation) and §2.2B.2 classification table now have a code to
  point at instead of a "closed-set addition, recorded here" placeholder.
- No other §2.1 section references the code set by count, so no further 2.1 edits are required.
- 2.2 §F.1 ledger gains one resolved row: the T3a placeholder is now a versioned reference.

**Stage 2.1 is re-closed at v1.1 by this section.**

---

## 2.1.15 Controlled Amendment Record — v1.1 → v1.2 (producer-version identity in the envelope vocabulary)

> Not a correction of an error in v1.1. Stage 2.1 was closed holding a **requirement** — §2.1.4-D:
> "must record producer version in `provenance`; invalidate on producer version change", plus
> "**an `estimate` field whose `provenance` does not identify the producer version is
> non-conformant**" — without the **vocabulary** needed to satisfy it. Stage 2.2's §F.3.2
> seven-consumer freeze audit (rows C5/Caching and C6/Reproducibility) proved the gap: the rule is
> enforceable in words, and the fields cannot exist. This is a contract-vocabulary defect — the
> single `SPECIFICATION_CHANGE_REQUIRED` finding of that audit (§F.3.3 register row 13) — and it is
> closed here rather than re-homed forward. Moving a requirement to a later stage in order to avoid
> reopening a closed one would silently change its meaning, which is exactly what controlled
> amendment exists to prevent.
>
> **Scope discipline.** The `REJ_*` / `WARN_*` sets are **not** touched: they remain v1.1, and
> §2.1.14's non-overlap table stands. v1.2 amends the **envelope vocabulary** only. **No `src/`
> changes in this pass** — the same discipline that held for v1.1; the model change belongs to the
> 2.15 migration, executed against this record.

### 1. The finding (evidence, not preference)

| Item | Content |
|---|---|
| Requirement already in force | §2.1.4 Dimension C (stability → cache policy) + its closing rule; §2.1.13 rule 7 (heuristics must record producer version); §2.2.4 (estimate cache hits gated on producer-version match) |
| Consumers proven to exist | 2.2 §F.3.2 **C5** ("no version-blind estimate hits"), **C6** ("same bytes + same producer versions → same contract"), plus recovery triage ("why did this output change?") and Stages 15/16/18 |
| Vocabulary today | `ProvenanceEntry {layer, evidence_refs, transform_type, confidence_delta}` and `SourceInfo {layer, model, tool}` — **no version of any kind** (`utils/confidence.py:77-92`; `tool` appears as a bare name such as `"numpy"`, `quality/analyzer.py:39`) |
| Consequence if not fixed | C5 and C6 each invent where versions live and reach different answers; §2.1.4-D's rule stays unfalsifiable; §E-1's golden fixture cannot define "same producers" |

### 2. Why the existing vocabulary cannot absorb it

- `SourceInfo.model` / `SourceInfo.tool` and `ProvenanceEntry.tool` are **name** fields under the
  anti-dump rule (§2.1.11.8 — controlled vocabulary, never a tool mirror). Overloading a name with a
  version string destroys the "same tool, different version" comparison the cache must make.
- `SourceInfo.layer` is a representation boundary (Stage 1 §4), not producer identity.
- The source hash cannot carry it by design: §2.1.4-D says versioning is "deliberately *not*
  overloaded into the source hash". That sentence is precisely why v1.2 lands in provenance and
  nowhere else.
- Deferring to 2.15 does not resolve it: 2.15 builds the schema **out of** this vocabulary, so an
  unrepresentable requirement propagates into all twelve contracts instead of being fixed once.

### 3. The amended vocabulary (normative)

```text
ProvenanceEntry                              per-field evidence lineage
├── layer                (existing)
├── evidence_refs        (existing)
├── transform_type       (existing)
├── confidence_delta     (existing)
├── tool                 (existing — name only, anti-dump rule)
├── tool_version         (v1.2) version of the software that produced the evidence
└── model_version        (v1.2) version of the inference/model behind the value, where applicable

SourceInfo                                   where a value came from
├── layer                (existing)
├── model                (existing — name only)
├── tool                 (existing — name only)
└── version              (v1.2) version of the SOURCE-SIDE artifact being described — the producer
                                string the analysed object itself declares; never a Builder version
```

**Three distinct concepts, frozen here so `"version": "1.4"` can never be ambiguous:**

| Field | Refers to | Supplied by | Must never mean |
|---|---|---|---|
| `tool_version` | Builder-side software that produced the evidence (imageio / ffmpeg / numpy / …). **This is the value cache invalidation compares.** | runtime introspection at emit time | the source's encoder; the contract schema version |
| `model_version` | Builder-side inference model behind the value, where a model produced it | model registry / heuristic id at emit time | the heuristic's name (that is `transform_type`); `tool_version` |
| `SourceInfo.version` | The **source-side** producer version declared by the analysed artifact (e.g. an encoder tag read from the container) | the probe reading the source | any Builder component's version |

`SourceInfo.version` is deliberately spelled `version` to stay inside the existing `SourceInfo`
pattern; its meaning is fixed by this table, and any future naming collision is resolved by renaming
the *newcomer*, never this field.

### 4. Requirement, state, and provenance rules (normative)

| # | Rule |
|---|---|
| R1 | On a field whose stability is `estimate`, `tool_version` is **required on the producing provenance entry**. Its absence makes that *field* non-conformant — exactly the sentence §2.1.4-D already wrote; v1.2 gives that sentence a referent. |
| R2 | `model_version` is **OPTIONAL** (Dimension D): present only when a model/heuristic produced the value. Omit the key; never emit `null` to mean "not applicable" (§2.1.4-B `null` rule). |
| R3 | `SourceInfo.version` is **OPTIONAL / UNAVAILABLE-ALLOWED**: many artifacts declare no producer version. Omission then means "the object declares none". Never `""`, never `"unknown"`, never a Builder version substituted for a missing source tag — that is fabrication, and it is the failure mode this field's naming must not invite. |
| R4 | Builder-side version genuinely undeterminable → `tool_version: "unknown"` is the only permitted sentinel, and only when introspection is impossible. `"0"`, `"latest"`, `"dev"`, and the package's own placeholder are forbidden. |
| R5 | **Cache gate is exact equality** on the version tuple relevant to the field. A `"unknown"` (R4) on either side is a **non-match** → recompute. This is what turns C5's "no version-blind estimate hits" from an aspiration into a mechanically testable rule. |
| R6 | `stable` fields may record the version fields for triage value; their absence never makes a stable field non-conformant, and they never gate a stable cache hit (the hash already does that work). |
| R7 | Values are recorded **verbatim as the producer reports them** (`importlib.metadata` / `__version__` / tool banner). The Builder does not parse, normalise, canonicalise, or order them; comparison is equality only. No version-range logic may be inferred from these strings. |
| R8 | These are **producer identity, not observed properties of the source**: they never carry an `ObservationState`, never feed the field's `state` or `confidence`, and never appear in `SourceDescription.source_identity`. |
| R9 | Provenance entries are written by **one** helper (`producer_identity()`, single introspection point, 2.15). Per-producer ad-hoc introspection is forbidden — it is how `"1.26.4"` and `"2.31.0"` end up in the same cache. |

### 5. Producer and consumer ownership (§2.1.11.7 — no orphan fields)

| Role | Owner |
|---|---|
| Producer of `tool_version` | every estimate producer: timing analyzer (actual FPS, CFR/VFR verdict, presentation duration), `quality/analyzer.py` source-hint fields, `generational_estimate` heuristics (§2.1.13), and every model-backed field from Stage 8 on |
| Producer of `model_version` | the same set, restricted to model/heuristic-backed values |
| Producer of `SourceInfo.version` | the container/technical probe (2.3), only when the artifact declares one |
| Consumer | **C5/Caching** (hit/miss gate, §2.2.4 + R5), **C6/Reproducibility** (reconstruction key, §E-1 golden fixture), recovery triage (2.2 §F.3.2 C7), Stages 15/16 (cache + job lineage), Stage 18 (reproducibility suite) |
| Enforcement point | §2.1.4-D conformance check + the tests in §7; **not** JSON-Schema `required` (see §6) |

### 6. Migration impact (spec-only in this pass)

| Location | Change | When |
|---|---|---|
| `utils/confidence.py:83-92` | `ProvenanceEntry` gains `tool_version: Optional[str] = None`, `model_version: Optional[str] = None` | 2.15 schema migration |
| `utils/confidence.py:77-80` | `SourceInfo` gains `version: Optional[str] = None` | 2.15 |
| every estimate producer | capture versions at emit time through `producer_identity()` (R9) | 2.15 |
| `SourceDescription` schema | three **optional** additions = **minor** bump under the §2.2.5 version policy; estimate-conditional requiredness stays a *rule enforced by the conformance check + tests*, not by schema `required` | 2.15 |
| 2.2 §F.3.3 register | row 13 (`SPECIFICATION_CHANGE_REQUIRED`) resolved by this record; residual becomes **IMPLEMENTATION_MIGRATION_REQUIRED** as new row 24 | this pass (spec) / 2.15 (code) |

Why the split in the row above matters: marking the fields schema-`required` would invalidate every
contract stored before v1.2 without a migration step, contradicting Stage 1 D5 (explicit migrations).
Optionality preserves old records; R1 + tests preserve the requirement. Records predating v1.2 are
read as "`tool_version` unknown", hence **never** cache hits under R5 — a pre-amendment record can be
parsed but not trusted as fresh, which is the conservative direction.

### 7. Required tests (join the 2.15 migration set; none exists today)

1. An `estimate` field whose provenance entry lacks `tool_version` → conformance check fails (R1).
2. Bump `tool_version` in a fixture → estimates recompute, `stable` fields byte-identical (C5/C6).
3. `tool_version: "unknown"` on either side of a cache comparison → **no hit** (R5).
4. A `stable` field with no version fields → still conforms; still a hash-keyed hit (R6).
5. `SourceInfo.version` absent → parses and round-trips; present → round-trips verbatim, unnormalised (R7).
6. A pre-v1.2 stored contract (no version fields) → parses, but yields no estimate cache hit (D5 + R5).
7. §E-1 golden fixture records the exact version tuple that produced it; a run whose tuple differs
   may not claim the fixture (C6's "same producers" defined).
8. Regression guard for the concept collision: in every fixture, `SourceInfo.version` never equals a
   Builder package version, and `model_version` never equals `tool_version` unless the model *is*
   the tool.

### 8. Non-overlap verification (required before re-close)

| Question | v1.1 changed | v1.2 changes | Overlap? |
|---|---|---|---|
| `REJ_*` / `WARN_*` membership | added `REJ_SPOOL_EXHAUSTED` | nothing | none — v1.1's record is untouched |
| Observation-state vocabulary | unchanged | unchanged | none |
| Tier / fidelity / requirement dimensions | unchanged | §2.1.4-D gains a referent; its text and meaning unchanged | none |
| Meaning of an existing field | none | none — `tool` / `model` stay name-only | none |
| New field invented by a consuming stage | no | no — 2.2 defines **no** version field; it consumes the envelope | none |

### 9. Cross-stage impact

| Stage / document | Effect |
|---|---|
| §2.1.4-D, §2.1.11.10, §2.1.13 rule 7 | annotated to name the fields; no behaviour change |
| §2.1.9 "New in Contract #1" | one addition row; 2.15's field inventory grows by three optional fields |
| **2.2** | §F.3.2 C5 and C6 → **PASS with migration**; §F.3.3 row 13 resolved (residual = row 24, IMR); §F.3.5 verdict becomes CLOSED; **Stage 2.3 unblocked** |
| **2.3** | the container probe is the producer of `SourceInfo.version` when the artifact declares one; it must not invent a Builder-side version there (R3) |
| **2.4 → 2.14** | inherit the pattern (§2.1.11.2/2.1.11.10): every `estimate` field carries the same two version fields; no stage may invent its own version carrier |
| **2.15** | model + schema + `producer_identity()`; pre-v1.2 records parse and are treated as unknown (R5) |
| **15 / 16 / 18** | cache gate, job lineage, reproducibility suite all read the same tuple |
| **Stage 1** | unaffected — no Stage 1 clause is contradicted; §6 provenance is extended within its own allowance, and Stage 1 D5's explicit-migration rule is honoured by keeping the fields optional |

### 10. Vocabulary status after amendment, and the re-close procedure

```text
Before: envelope vocabulary (v1.1) cannot express producer-version identity, though §2.1.4-D
        requires it — a requirement without a referent
Action: tool_version + model_version (ProvenanceEntry) and version (SourceInfo) added through
        controlled architectural change — this record — with semantics, state rules, ownership,
        tests and cross-stage impact fixed here and nowhere else
After:  envelope vocabulary (v1.2) — CLOSED, extensions only, and only via this procedure:
        evidence → proposed amendment → amendment record → impact/conformance audit →
        versioned re-close.  No stage may extend the envelope unilaterally (§2.1.14 precedent).
```

Re-closure checklist executed in this pass: (a) evidence cited with file:line; (b) the two
freeze-audit rows that surfaced it re-checked against the new vocabulary; (c) non-overlap table
above (§8) proves no collision with v1.1's code-set amendment; (d) `src/` deliberately untouched —
`python -m pytest -q` stays green at 25/25 and the register keeps row 24 as the honest
`IMPLEMENTATION_MIGRATION_REQUIRED` residual; (e) consuming documents updated in the same pass so no
"spec says X, code says Y, nobody wrote it down" state survives this turn.

**Stage 2.1 is re-closed at v1.2 by this section.** (Code-set taxonomy remains v1.1; the envelope
vocabulary is now v1.2. A citation to "§2.1 v1.1" for a code and "§2.1 v1.2" for a vocabulary item is
correct usage, not an inconsistency.)

## 2.1.16 Controlled Amendment Record — v1.2 → v1.3 (`conflicting` — multi-source disagreement)

> **Scope of this amendment: the `conflicting` observation state, and nothing else.** It does not
> address the `sample_aspect_ratio` typing question (see §2.1.16.10), does not touch the code-set
> taxonomy (still v1.1), and does not extend the version carriers fixed at v1.2. §2.1's precedent is that a
> controlled amendment carries **one** change; bundling a second finding into v1.3 would repeat the exact
> move that produced the v1.1/v1.2 split.

### 2.1.16.1 The finding (evidence, not preference)
> Numbering note: this amendment's sub-sections are numbered `2.1.16.n`, deliberately repeating the
> 1–10 shape used by §2.1.15. Unqualified "§3" inside this block means §2.1.16.3; a cross-reference that
> means the v1.2 section writes §2.1.15.3. The prefixes exist so a bare section number is never
> ambiguous when both amendments are cited in the same argument.

Evidence from the Stage 2.3 freeze audit (`docs/specs/stage2_3_container_probe.md`):

- **§F.2 G10** — the draft's four-state list omitted `uncertain` while §2.3.13's conflict rule needed a
  home; the frozen set could not express a conflict as anything other than a renamed duplicate.
- **§F.2 G11** — a second origin/category carrier is prohibited, so the conflict had nowhere to live.
- **§G.4.1** (measured) — an exact-match lookup on `encoder` returns `ABSENT` for Matroska while returning a
  value for mp4, from the same string written by the same muxer. Absence was being asserted where the truth
  was disagreement about *where to look*.
- **§G.8 / §V.5.1** — Stage 2.3 specified (but could not implement) the correct behaviour: retain **both**
  disputed values with their scopes and origins, and mark the group.

**Why this is §2.1's and not 2.3's.** `ObservationState` is the envelope vocabulary declared at §2.1.4
Dimension B and inherited by Contracts #2–#12. 2.3 is a *consumer*; §2.1.10 forbids any stage extending the
envelope unilaterally. The State 2.3 specification (§V.5.1) therefore correctly blocked on this amendment
rather than adding the member itself.

### 2.1.16.2 Why the existing vocabulary cannot absorb it

Dimension B's four members, verbatim: `extracted` (the Builder obtained the value) · `absent` (checked;
does not exist) · `uncertain` (evidence exists; the Builder cannot establish the value confidently) ·
`unavailable` (could not determine the value).

Two questions must be answered and none of the four can answer both:

```text
  Q1  Did the Builder obtain a value?              -> yes, two of them
  Q2  Which one is authoritative?                   -> unresolved, and the resolution is
                                                        an EVIDENCE question, not a capability one
```

- `extracted` is false: it asserts a single value was obtained and would license a consumer to read one.
- `absent` is false and is the *measured* failure: it is what the mechanism reported when its key lookup
  missed (`ENCODER` vs `encoder`).
- `unavailable` is false: the Builder could read both scopes successfully. It is a **capability** statement.
- `uncertain` is the closest, and is where §2.1.4 step 4 sends "evidence conflicts" today with
  confidence ≤ 0.65.

**The `uncertain` overlap is real and is stated rather than hidden.** §2.1.4 step 4 already routes conflicts
to `uncertain`. If v1.3 is judged to duplicate it, the correct outcome is to reject the member and strengthen
step 4's rule instead — which is why §3 below states an explicit discriminator and §7 requires a test that

### 2.1.16.3 The amended vocabulary (normative)

```text
ObservationState  (Dimension B, envelope vocabulary v1.3)

    EXTRACTED   the Builder obtained the value
    ABSENT      the Builder checked; the property does not exist in this source
    UNCERTAIN   evidence exists; the Builder cannot establish THE value confidently
    UNAVAILABLE the Builder could not determine the value (probe failed / no evidence)
    CONFLICTING NEW in v1.3 — two or more MUTUALLY INCONSISTENT values were obtained
                from DISTINCT evidence sources, and ALL of them are retained

DISCRIMINATOR (normative; the member is not a rename)
    UNCERTAIN    the difficulty is in INTERPRETING one value.
                 e.g. an unparseable string, a value whose meaning is unclear,
                 a value below a resolution threshold.
    CONFLICTING  the difficulty is in CHOOSING between two or more values that each
                 parsed cleanly and each came from a different, addressable source.
                 Both are retained. Neither is discarded, and no precedence is
                 applied unless a registered rule says so.

CONFLICTING requires ALL of:
    (a) >= 2 values were obtained;
    (b) they are mutually inconsistent (no value equals another);
    (c) each has its own addressable evidence source;
    (d) every value is RETAINED in the contract, with its evidence ref.
```

### 4. State rules (normative)

| # | Rule |
|---|---|
| **S-1** | `conflicting` is an **additive** Dimension B member. It does not alter the meaning of the four existing members, and no existing producer's output changes. |
| **S-2** | `conflicting` is emitted **only** when a group carries ≥ 2 inconsistent values from distinct sources. A single ambiguous value is `uncertain`, never `conflicting`. |
| **S-3** | **Retention is mandatory and precedes marking.** A `conflicting` group with any value discarded is non-conformant, regardless of what the state says. The state is a *consequence* of retention, not a substitute for it. |
| **S-4** | **No silent preference.** A producer MUST NOT select one retained value and emit the other as absent. A registered precedence rule may be applied *and its id recorded*; absent such a rule, all values stand. |
| **S-5** | `conflicting` is **not** a capability statement. A probe that could not read a scope emits `unavailable` (condition (a) fails: fewer than 2 values). A probe that read a scope and found nothing emits `absent`. The three are never interchangeable. |
| **S-6** | `conflicting` **does not** change `Confidence` by itself. `Confidence` and `ObservationState` remain orthogonal axes (§2.1.4). A producer MAY additionally set `ValidationStatus.CONFLICT`; the two are independent. |
| **S-7** | `conflicting` **never** implies a value was invented, and **never** licenses inference from the conflict itself. "Two producers disagree" is an observation; "the true producer is X" is not licensed by it. |
| **S-8** | Serialised form is the literal string `"conflicting"`. Additive change: a v1.2 consumer matching an exhaustive state enum must add the member or handle unknown values. |

### 5. Precedence and consumers (normative)

**Precedence is opt-in, never implicit.** A producer holding a registered rule may order retained values
(e.g. by scope), and MUST record that rule's id. Absent a registered rule, no ordering is applied. Stage
2.3 has registered such a rule for producer declarations
(`stage2_3_container_probe.md` §V.5.1: `artifact_declared` beats `muxer_authored`; `probe_observed` is never
a producer identity) and **consumes** the state rather than defining it.

**Consumer obligations** — the part that makes a fifth member worth adding rather than a rename:

| Consumer class | Required behaviour on encountering `conflicting` |
|---|---|
| **Cache** (§2.2) | MUST NOT serve a single retained value as authoritative. Version gating still applies (v1.2 R5); a conflicting group is a cache miss or an explicit conflict result — never a silent hit on one value. |
| **Downstream analysis** (2.5+) | MUST read the group as multi-valued. MAY adjudicate only via a registered rule; MUST NOT pick by convenience, first-seen order, or scope heuristic. |
| **Provenance / evidence** | MUST retain every value together with the `scope` it was observed at. That is the whole retained record today: `ProducerDeclaration` carries `scope`, `canonical_key`, `original_key`, `original_value`, `origin`, `state` and `rule_id`. **An addressable `evidence_refs` entry per declaration does not exist and is NOT required by this amendment.** The grammar for one is G13 (2.3 row A7), owned by §2.1 and deferred to v1.4. Inventing the field here to make prose true would be v1.3 pre-creating vocabulary it has not been authorised to add. |
| **UI / report** | SHOULD surface both values with their sources. Silently collapsing to one is the S-4 violation. |
| **Regression gate** | Emitting `conflicting` while retaining < 2 values FAILS. Dropping a conflicting value FAILS. |

### 6. Migration impact

| # | Item | Change |
|---|---|---|
| 1 | `ObservationState` (`utils/confidence.py`) | **+1 additive enum member.** No existing member's meaning, name, or serialised value changes |
| 2 | Existing producers | **No output change required.** A producer that never sees inconsistent values never emits the member |
| 3 | `ValidationStatus.CONFLICT` | **Unchanged.** Coexists per S-6; this amendment does **not** fold it into `conflicting` |
| 4 | Consumers | **S-8 is breaking for naive consumers.** A v1.2 consumer matching an exhaustive enum must add the member or handle unknown values. Recorded, not hidden — it is the cost of the amendment |
| 5 | §2.1.4 Dimension B | Amended by §2.1.16.3; the four original members are unchanged |

### 2.1.16.7 Required tests (each must fail independently if its rule is broken)

| # | Test | Proves |
|---|---|---|
| **T-C1** | Two scopes disagreeing → group state is `conflicting` | S-2 |
| **T-C2** | The same group retains **both** values, each with its own `scope` | S-3 |
| **T-C3** | A single unparseable value → `uncertain`, **not** `conflicting` | the §2.1.16.3 discriminator |
| **T-C4** | An unreadable scope → `unavailable`, **not** `conflicting` | S-5 |
| **T-C5** | A readable scope with no matching key → `absent`, **not** `conflicting` | S-5 |
| **T-C6** | A codec value never becomes a producer value, even when the two conflict | Stage 2.3 A5 |
| **T-C7** | `ObservationState` has exactly 5 members; the 4 originals keep their values | S-1 |
| **T-C8** | Serialised form is the literal `"conflicting"` | S-8 |

**T-C3 is the test that decides whether this amendment is sound.** If `conflicting` and `uncertain` cannot
be made separable in practice, the member is a rename of `uncertain` and this amendment should be
**rejected** rather than weakened.

### 2.1.16.8 Non-overlap verification (required before re-close)

| Against | Overlap risk | Verdict |
|---|---|---|
| **§2.1.4 step 4** ("evidence conflicts" → `uncertain`, conf ≤ 0.65) | **Real and unresolved by design.** Both route a conflict to a state. | Step 4 is **not modified** — it remains valid for the `uncertain` case (one unparseable value). `conflicting` is additive and claims only the ≥ 2 distinct-sources case. T-C3 is the guard on the seam. **If a reviewer decides the seam is too thin, the correct remedy is to reject this amendment, not to blur it.** |
| **§2.1.15 (v1.2) version carriers** | Both add enum members to `utils/confidence.py` | **No overlap.** v1.2 added `tool_version`/`model_version`/`version`; v1.3 adds one `ObservationState` member. No field, rule, or test is shared. |
| **§2.1.14 (v1.1) `REJ_SPOOL_EXHAUSTED`** | Both amend the envelope | **No overlap.** v1.1 touched the `REJ_*` code set; v1.3 touches `ObservationState`. The code-set taxonomy stays v1.1. |
| **`ValidationStatus.CONFLICT`** (existing) | Same concept, different axis | **Kept separate, deliberately (S-6).** Folding one into the other would break the §2.1.4 orthogonality guarantee. |
| **Stage 2.3 §V.5.1** (consumer) | 2.3 needed this member | **2.3 changed nothing in its own text.** §2.1.16 exists precisely because 2.3 was forbidden to do this itself. |

### 2.1.16.9 Cross-stage impact

| Stage | Effect |
|---|---|
| **2.3** | **Consumes** `conflicting`; gate rows A5 and T7 re-measured to `PASS` (`stage2_3_container_probe.md` §V.7.1). Its specification is unchanged. |
| **2.15** | Must migrate the consumers listed in §6 row 4 — the S-8 breaking change is real and lands with the migration set. |
| **2.4 / 2.5** | Inherit Dimension B. No action until they branch on `state`. |
| **2.16** | **None.** No spool, descriptor, quota, or `fd://<n>` behaviour is touched, specified, or simulated. |

### 2.1.16.10 Vocabulary status after amendment, and the re-close procedure

```text
Before: envelope vocabulary (v1.2) cannot express multi-source disagreement. §2.1.4 step 4
        sends it to `uncertain`, which asserts nothing about how many sources were read.
Action: `conflicting` added through controlled architectural change — this record — with
        semantics (S-1..S-8), the §3 discriminator, precedence and consumer obligations,
        migration impact, and eight required tests fixed here and nowhere else
After:  envelope vocabulary (v1.3) — extensions only, and only via this procedure:
        evidence → proposed amendment → amendment record → impact/conformance audit →
        versioned re-close.  No stage may extend the envelope unilaterally (§2.1.14 precedent).
```

Re-closure checklist executed in this pass:

| # | Item | Result |
|---|---|---|
| (a) | Evidence cited with source | 2.3 §F.2 G10/G11, §G.4.1 (measured `ENCODER` vs `encoder`), §G.8, §V.5.1 |
| (b) | The freeze-audit rows that surfaced it re-checked | A5, T7 — re-run, not asserted (§V.7.1) |
| (c) | Non-overlap table (§2.1.16.8) | Done, including the `uncertain` seam, which is stated as a risk rather than hidden |
| (d) | Code impact real and tested | `ObservationState` +1 member; rollup consumer in `ingestor.py`; `tests/test_conflicting_state.py` T-C1…T-C8 |
| (e) | Suite green | **70/70** (53 pre-existing + 17 new), 3 subtests |
| (f) | Consuming documents updated same pass | `stage2_3_container_probe.md` §V.7, §V.7.1, §V.5.1, header, dashboard |
| (g) | Boundaries respected | 2.3 spec text, §2.16, A8/T8, and the `sample_aspect_ratio` type chain **all untouched** |

**§2.1 is re-closed at v1.3 by this section.** (Code-set taxonomy remains v1.1; the envelope vocabulary is
now v1.3. As with v1.2, citing "§2.1 v1.1" for a code and "§2.1 v1.3" for a vocabulary item is correct
usage, not an inconsistency.)

**What v1.3 did NOT do, stated so the next reader does not assume it:** the `sample_aspect_ratio` typing
question (2.3 A9) is **not** resolved here — it needs `Optional[str]` in its owning contract and was left
alone deliberately. The `evidence_refs` address grammar (2.3 A7) is **not** resolved here — it remains a
§2.1 item for a future amendment. Neither was bundled in, because bundling is what produced the v1.1/v1.2

---

## 2.1.17 Controlled Amendment Record — v1.3 → v1.4 (the `evidence_refs` address grammar)

> **Scope: G13 only** — what counts as a valid evidence reference. It does **not** decide which field
> must carry one, does **not** add `evidence_refs` to `ProducerDeclaration`, does not touch the
> `sample_aspect_ratio` typing question (A9), and does not touch G18 or 2.15. Those are separate
> amendments to separate owners.

### 2.1.17.1 The finding (evidence, not preference)

Every `evidence_refs` emission in `src/` today, in full:

| Site | `evidence_refs` | `transform_type` |
|---|---|---|
| `ingestion/ingestor.py:147` | `["container_probe"]` | `"none"` |
| `ingestion/ingestor.py:1172` | `["file_size", "duration", "resolution", "codec"]` | `"heuristic_scoring"` |
| `decode/decoder.py:53` | `["source_file"]` | `"decode_init"` |
| `decode/decoder.py:148` | `["frame_0" … "frame_9"]` | `"pts_normalization"` |
| `quality/analyzer.py:72` | `["decoded_frames", "quality_heuristics"]` | `"quality_analysis"` |
| `quality/analyzer.py:86` | `["source.quality_score"]` | `"hint_recorded_not_chained"` |

**Not one of these six sites uses a URI scheme.** Zero occurrences of `://` in any emitted ref. That fact
matters more than it looks: the Stage 2.3 gate has been testing A7 with `"://" in ref`, so it rejects
**100 % of real emissions by construction** — including `frame_0`, which genuinely locates a frame, and
`source_file`, which names the artifact. A check that rejects every conforming value cannot inform a
grammar. **This amendment defines the grammar from evidence, and the `"://"` proxy is retired, not
satisfied.**

Three distinct defects are visible in that table, and they are three different problems:

1. **A method word sits in the address field.** `container_probe` names a *procedure*. Worse, the
   `transform_type` beside it is `"none"` — so the method slot was left empty while the method leaked
   into the address slot. One value, two wrong places.
2. **Property names sit in the address field.** `file_size`, `duration`, `codec` name *what was
   measured*, not *where the evidence is*. Closer to valid, still locate nothing.
3. **Genuinely locatable values already exist and are unrecognised.** `frame_<i>` indexes the decoded

### 2.1.17.3 The grammar (normative)

An **address** is a string that a consumer can resolve to a specific piece of evidence. The grammar is
kind-tagged, because "locate the evidence" means different things for different evidence — and because
the single most common violation in the repo (a method word) must be *recognisable* in order to be
rejected rather than silently tolerated.

```text
address     ::= kind ":" locator

kind        ::= "artifact"    a location INSIDE the analysed artifact
              | "frame"       a location inside the decoded frame sequence
              | "contract"    a path within the emitted contract
              | "derived"     a computed value from a REGISTERED rule
              | "method"      NOT AN ADDRESS -- see E-2

locator     ::= the kind's own syntax (2.1.17.4); must be non-empty and non-"*"

EXEMPLARS (illustrative, from real measurements in 2.1.17.1 -- NOT additional normative text)
  artifact:mp4:moov/udta/meta/ilst/<©too>/data      the injected T-R3b atom
  artifact:matroska:segment/info/ENCODER             the container-scope tag
  artifact:mp4:trak[video=0]/udta/encoder            the stream-scope tag
  frame:v0@idx3                                     a decoded frame by index
  frame:v0@pts=2048                                 a decoded frame by timestamp
  contract:source.quality_score                      the dotted path already emitted
  derived:heuristic_scoring:file_size,duration       a computed value, inputs named
```

**Why a kind tag and not a URI scheme.** The obvious design — require `scheme://authority/path` — was
rejected because the evidence here has **no network layer**. There is no authority to name: a local
file's evidence is addressed by *container structure* (`moov/udta/...`) or by *index* (`frame:v0@idx3`),
not by a host. Bolting a `://` onto the grammar would have satisfied the existing gate check while
describing nothing. That is precisely the failure mode this amendment exists to prevent, and it is why
the `"://"` proxy is retired here rather than written into the standard.

### 2.1.17.4 Locator syntax by kind (normative)

| Kind | Locator must | Well-formed example | Rejected example |
|---|---|---|---|
| `artifact` | name the container, then a structural path within it | `mp4:moov/udta/meta/ilst/©too/data` | `mp4:*` (wildcard — cannot locate) |
| `frame` | name the stream, then a **selector**: `idx<n>` or `pts=<n>` | `frame:v0@pts=2048` | `frame:v0` (no selector) |
| `contract` | a dotted path into the emitted contract | `contract:container.format` | `contract:` (empty) |
| `derived` | name a registered rule id, then its inputs | `derived:heuristic_scoring:file_size,duration` | `derived:scored` (no inputs) |
| `method` | — | — | **`method:*` is never an address (E-2)** |

### 2.1.17.6 Classification of every ref currently in `src/` (measured)

**Two distinct kinds of classification, and conflating them would be a new error.** A *validator* can
determine only what is **mechanically decidable** from the string. An *analyst* can additionally
diagnose **why** a ref fails. §2.1.17.6.1 is the validator's view and is what a consumer may rely on;
§2.1.17.6.2 is the analyst's and is authored, not derived. E-7 forbids re-deriving it.

#### 2.1.17.6.1 Validator-computable class (normative)

| Emitted value(s) | Class | Decidable because |
|---|---|---|
| `container_probe` | **`LEGACY`** | carries no kind tag → parses as no address |
| `file_size`, `duration`, `resolution`, `codec` | **`LEGACY`** | no kind tag |
| `quality_heuristics` | **`LEGACY`** | no kind tag |
| `decoded_frames` | **`LEGACY`** | no kind tag |
| `source_file` | **`LEGACY`** | no kind tag |
| `frame_0` … `frame_9` | **`LEGACY`** | no kind tag |
| `source.quality_score` | **`LEGACY`** | no kind tag |

**Every ref in the repository is `LEGACY`, and the count of conforming refs is zero.** v1.4 changes none
of them — E-5 forbids it. What changes is that the target is *defined* and the obligation is now
**falsifiable**: a consumer can prove the absence of an address, where before it could only notice that
its own guess went unsatisfied.

#### 2.1.17.6.2 Analyst diagnosis (authored, NOT mechanically derivable)

| Emitted value(s) | Diagnosis | Rule engaged | Correct home |
|---|---|---|---|
| `container_probe` | a **method word** in the address field | **E-2** | `transform_type` — currently `"none"` |
| `quality_heuristics` | a method word in the address field | **E-2** | `transform_type` |
| `file_size`, `duration`, `resolution`, `codec` | property names — *what* was measured, not *where* | E-4 | `derived:` + registered rule and inputs |
| `decoded_frames` | a region with no selector | E-3 | `frame:v0@idx<first>-<last>` |
| `source_file` | names the artifact as a whole, not a location in it | E-4 | `artifact:<container>:<path>` |
| `frame_0` … `frame_9` | **near-conforming** — indexes frames, lacks kind + stream | E-3 | `frame:v0@idx<n>` |
| `source.quality_score` | **near-conforming** — a genuine dotted path, lacks a kind | E-4 | `contract:source.quality_score` |

**`container_probe` is doubly misplaced**: it names a method *and* sits beside a `transform_type` of
`"none"`, so the method was lost from its own slot while leaking into the address slot. Correcting the
emission is 2.3's implementation work and is explicitly **out of scope** here (§2.1.17.9).

**Note on the gate.** The A7 check classifies `container_probe` as `LEGACY`, not as `NOT_ADDRESS`,
because a validator cannot know that a bare word names a method — it can only see the absence of a kind
tag. That is correct and deliberate: attributing method-ness would require a frozen registry of method
names, which is a new vocabulary that no owner has authorised.


### 2.1.17.7 Required tests

| # | Test | Proves |
|---|---|---|
| **T-E1** | Each of the five kinds parses; `method:` parses but is classed `NOT_ADDRESS` | §2.1.17.3 |
| **T-E2** | A `method:` ref in `evidence_refs` is rejected as an address | E-2 |
| **T-E3** | `mp4:*`, `frame:v0`, `contract:`, `derived:scored` are all rejected | §2.1.17.4 |
| **T-E4** | Two observations of the same artifact MUST be able to produce different locators; a conforming ref that cannot is rejected | E-3 |
| **T-E5** | Every ref in `src/` classifies as `LEGACY`; the count of conforming refs is 0 | E-4, E-5 |
| **T-E6** | `ProducerDeclaration` has **no** `evidence_refs` field and v1.4 adds none | E-6 (the boundary) |

**T-E6 is the boundary guard.** It fails if anyone retrofits the field into `ProducerDeclaration` to make
§2.1.16's prose true, which is exactly the coupling this amendment refuses to create.


### 2.1.17.8 Ownership and non-overlap

| Against | Overlap | Verdict |
|---|---|---|
| **§2.1.16 (v1.3) `conflicting`** | Both concern observability | **No overlap.** v1.3 defines a *state*; v1.4 defines an *address*. v1.16 §5 was corrected in this pass to state that `ProducerDeclaration` carries no `evidence_refs` and needs none. **v1.4 does not reverse that correction** — E-6 holds the boundary. |
| **§2.1.15 (v1.2) version carriers** | Both edit `utils/confidence.py` | **No overlap.** v1.2 added version fields; v1.4 adds no field at all. |
| **`ProvenanceEntry.transform_type`** | Method-vs-address confusion | **v1.4 corrects the *classification*** (E-2: methods belong here). It does not change the field's type, its `list`/`str` shape, or any value emitted. |
| **§V.6.1 R-E1/R-E2/R-E3** (2.3's stated constraints) | Same three constraints | **Promoted from 2.3's *statement* to §2.1's *normative* rules** (E-1/E-2/E-3). 2.3 stated them as constraints for §2.1 to inherit; §2.1 has now inherited them. 2.3's text is unchanged. |
| **Stage 2.3 A9 / G10** | Both §2.1-adjacent | **Deliberately excluded.** Different owning document (`stage2_source_description.md:47`). |
| **Stage 2.3 A8/T8 / G18** | — | **Deliberately excluded.** 2.15's, and the gate was already corrected in the previous pass (§V.7.2). |

### 2.1.17.9 What v1.4 deliberately does NOT do

```text
  does NOT  add evidence_refs to ProducerDeclaration          (E-6; boundary with §2.1.16)
  does NOT  migrate any of the six emission sites             (E-5 additive)
  does NOT  retire `container_probe` from the codebase        (that is 2.3's implementation)
  does NOT  change ProvenanceEntry's type                     (classification only)
  does NOT  author the sample_aspect_ratio type               (A9 / G10 -- different document)
  does NOT  touch G18, R-2, or anything under 2.15
```

**G13 is NOT closed by this amendment.** v1.4 removes the *undefinability*; it does not make the code
conform. A7 measures the code, and A7 measures the code unchanged. It will therefore still report
`FAIL` — and that is the correct, honest result: the obligation is now *stated* and *falsifiable*
instead of *vague*, which is progress, not discharge.

### 2.1.17.10 Vocabulary status

```text
Before: evidence_refs is list[str] and unenforced. A method word, a property name and a real address
        are indistinguishable. 2.3's A7 tests with "://" and therefore rejects 100% of emissions.
Action: a kind-tagged address grammar (artifact | frame | contract | derived | method), seven
        normative rules E-1..E-7, a measured classification of every ref in src/, and six tests.
        The "://" proxy is RETIRED -- not satisfied, because conforming it would have meant writing
        a URI scheme onto evidence that has no network layer.
After:  envelope grammar (v1.4). Carriers unchanged, emissions unchanged, six sites LEGACY, and
        A7 falsifiable for the first time.
```

Re-closure checklist: (a) evidence measured from all six `src/` sites, not assumed; (b) every one
classified; (c) non-overlap checked against v1.1, v1.2, v1.3, G10 and G18; (d) the `"://"` proxy's
retirement justified structurally, not by preference; (e) `src/` untouched — **no model gained a
field**; (f) suite green.

**§2.1 is re-closed at v1.4 by this section.** (Code-set taxonomy v1.1; envelope vocabulary v1.4.)


A locator naming a **wildcard, a bare container, or an empty path** is not an address. `mp4` is not an
address; it is a format.

### 2.1.17.5 Normative rules

| # | Rule |
|---|---|
| **E-1** | **Artifact-located.** A value extracted from an artifact declaration MUST carry at least one `artifact:` address. `derived:` does **not** satisfy this: a computed value has no artifact location by construction. |
| **E-2** | **Method-distinct.** A `method:` value identifies a *procedure*. It MUST NOT appear in `evidence_refs`; it belongs in `ProvenanceEntry.transform_type`. A method proves how, never where — so it can never satisfy E-1. |
| **E-3** | **Falsifiable.** For a fixed artifact and a fixed kind, distinct observations MUST yield distinct locators. An address that cannot distinguish two observations of the same artifact is not an address. |
| **E-4** | **Classification, not silence.** Every ref is `CONFORMING` or `LEGACY`. `LEGACY` means *unclassified* — legal to emit, but it MUST NOT be counted as satisfying E-1 or E-3, and no consumer may infer provenance from it. |
| **E-5** | **Additive.** All six existing emission sites are `LEGACY` today. v1.4 changes no emitted value and no existing consumer; it defines a target and retires one bad proxy. |
| **E-6** | **This grammar does not assign carriers.** Which field must hold an address, if any, is a separate question. v1.4 adds no field and imposes no obligation on `ProducerDeclaration` or any other model. |
| **E-7** | **A consumer MAY validate against this grammar.** Validation classifies a ref; it never rewrites one and never treats `LEGACY` as `CONFORMING`. |

   sequence; `source.quality_score` is a dotted path into the contract. Nothing in §2.1 calls these
   addresses, so nothing can require them to be.

### 2.1.17.2 What the vocabulary cannot absorb (G13)

`evidence_refs: list[str]` is typed, frozen, and unenforced. It accepts a method word, a property name,
and an address identically. §2.1.4-D requires evidence, but nothing states what evidence *is*, so the
obligation is unfalsifiable — which is 2.3's A7 (`stage2_3_container_probe.md` §V.6.1). The gap is
**not** a missing field. It is a missing definition.

split in the first place.






