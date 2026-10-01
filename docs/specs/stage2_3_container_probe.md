# STAGE 2.3 — TECHNICAL / CONTAINER PROBING, SOURCE METADATA, ENCODER IDENTITY & ARTIFACT-DECLARED VERSIONING

**Stage:** 2 | **Sub-section:** 2.3 | **Contract:** #1 `SourceDescription`
**Status:** SPECIFICATION **DRAFT — FREEZE AUDIT EXECUTED, NOT CLOSED**. Part I is the authored draft
as received. Part II is the freeze audit (§F): 12 findings (G9–G20), **10 blocking spec-side**, 2
re-homed to §2.16. Two findings point back into closed Stage 2.1 as candidate amendment **v1.3**
(§V.6) — proposed, **not executed**. Parts III–IV add controlled remediation (R1–R6) and an **executable
freeze gate**; three remediation cycles have run, moving the gate from 18 outstanding to **6**.

> ### Current status of record
> *(superseded twice: by §H.9's ownership audit, and by Part V's amendment pass)*
>
> ```text
> Stage 2.3 — SPECIFICATION: CLOSED at v2.3-a1   (Part V; 9 clauses restated, 4 constructs deleted)
>             STAGE:          NOT CLOSED
>
> **One blocking finding remains.** Its ownership and dependencies are recorded in the
> G-register (§F.6) and restated item by item in §V.7 — that table is authoritative,
> NOT any summary count. G17 remains HELD under §2.16.
> ```
>
> **No ownership is asserted here by category or by tally.** Two routing errors in this
> audit (§H.8.1, §H.9.2) came from exactly that, and both were corrected against the
> register row rather than against the surrounding prose. A count of "§2.1 ×3" is a
> summary of §V.7, never a substitute for it.
>
> Gate: **1 blocking** (1 fail) + 5 held. This is **1, down from 6**:
> **A5** and **T7** after §2.1.16 established `conflicting` (§V.7.1); **A9** after
> `stage2_source_description`'s Amendment Records v1.1/v1.2 (§V.7.3); **A8** and **T8**
> after 2.15 implemented §V.1 R-2 (§V.7.4). Every one was **re-measured by a re-run
> gate, not declared** — and A9's first `PASS` and T8's first `PASS` were each rejected
> because the check was not yet measuring its own invariant.
>
> **A7's remaining obligation is an EMISSION obligation, not a specification one.** §2.1.17
> (v1.4) defines the address grammar; what is missing is the probe's ability to produce a
> conforming `artifact:` locator. The G13 investigation closed with **exactly one proven
> eligible mechanism** — MP4 container-scope `moov/udta/meta/ilst/<key>` — and the closure
> language for A7 is **bound in §V.7.15.1** so a future pass cannot widen it. **Track-scope
> producer addressability is not claimed**, and G13-F records that this toolchain cannot
> currently construct a track-scope producer declaration at all.
**Governs:** nothing yet — this stage holds no normative field, no code set, and no vocabulary of its own.
**Consumes, never redefines:** §2.1 envelope vocabulary + §2.1.15 R1–R9 · §2.1.4 Dimensions A–D ·
§2.1.5 `REJ_*` (closed set, v1.1) / `WARN_*` (open, additive) · §2.2 identity rules · §2.2A matrix +
§2.2A.4 allow/deny lists · §2.2B failure ladder · the frozen `source_kind` vocabulary.
**Supersedes:** nothing. Subordinate to Stage 1 and §2.1. Records divergence from
`stage2_source_description.md` §2.9 (which describes an ffprobe/mediainfo probe the repo does not run).

```
Freeze-audit dashboard (this pass)
  Part I draft        ── retained verbatim; annotated *(audit: Gxx)*, never rewritten
  §F.1 Scope check    ── FAIL: 14 of 24 claimed scope items belong to 2.4–2.9 / 2.11 / 2.14 (G9)
  §F.2 Findings       ── G9–G20 raised; every finding has evidence, class, owner, blocking flag
  §F.3 Probe reality  ── MEASURED on this machine: PyAV 18.1.0 / libavformat 62.12.102 /
                          libavcodec 62.28.102. The draft's ffprobe premise is not the repo's probe.
  §F.4 Invariants     ── A1–A12: 4 enforceable today, 5 blocked by a G-row, 3 need §2.16 (A10/A11)
  §F.5 Closure tests  ── T1–T12: 2 executable now, 6 blocked by G-rows, 4 deferred to §2.16
  §F.6 Register       ── G9–G20 classified; zero unexplained "gaps"
  §F.6 Verdict        ── NOT CLOSED. 2.3 may not be implemented, and no migration may be accepted,
                          while G10/G12/G13/G16/G18/G20 remain open — each is a place where two
                          correct-looking implementations would emit different contracts.
  Part III            ── controlled remediation R1–R6, specified against the measurements
  Part IV             ── executable freeze gate + three remediation cycles (18 -> 6 outstanding)
  Part V              ── controlled amendment v2.3-a1: 9 clauses restated, Part I left verbatim
  §V.7.1              ── A5 + T7 re-measured to PASS after §2.1.16; gate 6 -> 4 blocking
  src/                ── CHANGED in cycles 1-3, deliberately: 53/53 green. Unchanged in Part V
                          (a document-only pass). CHANGED for §2.1.16's consumer side
                          (`conflicting` rollup): 70/70 green. Ownership per item: §F.6 / §V.7.
  §2.1                ── v1.3 OPENED AND CLOSED at §2.1.16 (`conflicting`). The §2.1.15
                          version carriers and the §2.1.16 conflict member are separate
                          amendments; 2.3 adopted the former in v1.2 and the latter in v1.3.
  §2.2                ── UNCHANGED.
```

> **Reading rule.** Part I is the draft's own words. Where the audit contradicts the draft, the
> contradiction is recorded in Part II with a section reference — the draft is not silently corrected,
> because a stage closes by amending its own text against findings, not by having them absorbed invisibly.

---
---

# PART I — THE AUTHORED DRAFT (§2.3.0 – §2.3.22)

## 2.3.0 — Stage Purpose

Stage 2.3 defines how the system **observes, extracts, records, and preserves technical metadata about
digital video artifacts and their containers** without manufacturing provenance that the artifact does
not actually declare. It operates downstream of the Stage 2.1 provenance contract and Stage 2.2
reproducibility/consumption contract.

The central rule is:

> **A probe may observe technical facts. It may record explicitly declared producer identity. It must
> not infer, fabricate, back-fill, or substitute producer identity when the artifact does not provide it.**

Stage 2.3 therefore concerns **technical observation**, not semantic interpretation and not
model-generated estimation.

## 2.3.1 — Scope

Stage 2.3 covers technical inspection of video artifacts, including: container identification; media
stream identification; codec identification; encoder identification; encoder-tag/version extraction;
container metadata; stream metadata; dimensions; frame rate; duration; bitrate; time base; pixel
format; color metadata; audio-stream metadata where present; declared creation/tool metadata; technical
timestamps where explicitly available; technical probing through approved probe mechanisms; source
metadata normalization; representation of unavailable metadata; provenance of probe-produced
observations; artifact-declared producer identity; technical evidence references.

Stage 2.3 does **not** authorize: guessing missing metadata; reconstructing producer identity from
indirect clues; treating codec identity as encoder identity; treating container identity as producer
identity; treating the probe's own software version as the artifact's encoder version; treating file
extension as authoritative codec identity; treating filename patterns as producer evidence; semantic
interpretation of video content; quality scoring; model-generated estimates; silent correction of
contradictory artifact metadata. Those belong to other stages or require explicit contracts elsewhere.

*(audit: **G9** — §2.1.2's frozen ownership table assigns 14 of the 24 scope items above to 2.4–2.9,
2.11 and 2.14. **G20** — no consumer is named for the producer-identity items, which §2.1.2's anti-dump
rule requires.)*

## 2.3.2 — Relationship to Earlier Stages

**From §2.1** — the provenance vocabulary established by §2.1.15 v1.2 is authoritative. Where a technical
observation is emitted as an `estimate`, its applicable producer identity must use the existing provenance
carrier `provenance[].tool_version` / `provenance[].model_version` as applicable. The Stage 2.3 probe must
not create a competing version field.

**From §2.2** — Stage 2.3 must consume, rather than redefine, `provenance[].tool_version` /
`provenance[].model_version`, and must preserve the Stage 2.2 reproducibility/cache semantics. Stage 2.3
must not create a second provenance carrier.

**From §2.2A** — the frozen `source_kind` vocabulary remains authoritative. Stage 2.3 may attach technical
observations to an existing source representation but may not silently introduce a new source
classification merely because a particular probing mechanism was used.

**From R3** — the established rule remains binding: **absence of an encoder tag must not be filled in.**
The correct result is omission/unavailability rather than inference.

*(audit: "as applicable" and "wherever required" are this draft's two unfalsifiable escape hatches —
**G17** resolves both against the frozen Dimension C stability table instead of leaving them open.)*

## 2.3.3 — Core Design Principle: Observation ≠ Inference

The technical probe operates under three distinct states.

| State | Meaning | Permitted output |
|---|---|---|
| **Declared** | Artifact explicitly contains the metadata | Record the declared value |
| **Unavailable** | Metadata was not present or could not be obtained | Record absence/unavailability per schema |
| **Observed indirectly** | A value could theoretically be inferred from other evidence | **Do not manufacture the value** |

For example `container = MP4`, `codec = H.264`, `encoder_tag = absent` must **not** become
`encoder = x264`, even if H.264 encoding makes x264 plausible. Likewise
`encoder_tag = "Lavc61.3.100"` may be recorded because the artifact explicitly declares it.

The distinction is fundamental: **technical plausibility is not artifact-declared identity.**

*(audit: **G10** — this table is a third availability vocabulary; §2.1.4 Dimension B already owns the
concept and 2.3 may not re-cut it. **G18** — §F.3 measures a fixture where the tag is genuinely declared
yet authored by the muxer: "declared" is necessary but not sufficient to license an encoder attribution.)*

## 2.3.4 — Container Identity

The probe may identify the technical container from authoritative container-level probing. Examples:
`MP4`, `MOV`, `Matroska`, `WebM`, `AVI`, `MPEG-TS`. The resulting value represents **container format**,
not producer identity. Therefore `container = MP4` does not imply `producer = Apple / FFmpeg /
HandBrake`, and `container = Matroska` does not imply `producer = mkvmerge`. Container identification and
producer identification remain separate fields/concepts.

*(audit: **G16** — the six example values are not what the approved probe observes; measured demuxer names
are `"mov,mp4,m4a,3gp,3g2,mj2"` and `"matroska,webm"`. `ingestor.py:892` already converts container
identity into an `apple_ecosystem_container` inference — precisely the inference forbidden here, one
module away from the probe.)*

## 2.3.5 — Codec Identity

The probe may identify the codec associated with a media stream (e.g. `video_codec = h264`,
`audio_codec = aac`). Codec identity describes the encoding format. It does **not** establish which
software produced the stream. Therefore `video_codec = h264` does not authorize `encoder = x264` or
`encoder = NVENC` unless that identity is explicitly declared by the artifact or otherwise directly
evidenced under an approved contract.

*(audit: **G18** — "directly evidenced under an approved contract" names no contract, and §F.3 shows the
only evidence available in practice: the stream-level tag is absent while a container-level tag named
`encoder` is present.)*

## 2.3.6 — Encoder Identity

Encoder identity is treated as a separate technical property. The probe may record an encoder when an
authoritative artifact-level field explicitly declares it (example: `encoder = Lavc61.3.100`). If the
artifact exposes `encoder_tag = Lavc61.3.100`, the value may be carried into the Stage 2.3 technical
metadata representation. However `encoder_tag = absent` means `encoder = unavailable` or omission,
according to the envelope/schema rule. It does **not** mean `encoder = unknown_x264`,
`encoder = inferred_from_codec`, or `encoder = probe_default`.

*(audit: **G10** — `encoder = unavailable` is a sentinel *value*; the frozen representation is a state, not
a string inside the observed field, and at T1 granularity no per-field state exists at all. **G18** —
"authoritative artifact-level field" must name tag identity, tag scope and tag case or the rule cannot be
implemented twice with the same result.)*

## 2.3.7 — Encoder Version

Encoder version is subject to the Stage 2.1.15 R3 rule. Two fundamentally different possibilities.

**Case A — the artifact declares the encoder version** (`encoder = Lavc`,
`encoder_version = 61.3.100`): the artifact-declared value may populate `SourceInfo.version`, where
`SourceInfo` is the appropriate source-side carrier.

**Case B — the artifact does not declare the encoder version**: the probe must **not** inspect its own
installed FFmpeg/libavcodec version and place that value into `SourceInfo.version`; that would describe
the **probe**, not the artifact producer. `Artifact: encoder_version = 61.3.100` and
`Probe: ffprobe_version = 8.x` are different facts and must never be conflated.

*(audit: **G14** — Case A's two-field split requires parsing one opaque tag string, which §2.1.15 R7
forbids for version strings; real tags are `Lavf62.12.102` (a muxer string) and
`x264 - core 164 r3106 3136fe9` (a build string with no single "the version"). **G12** — `SourceInfo` has
no place for the producer's *name* or *kind*. **G15** — the probe's own `libavformat` version formats to
exactly `Lavf62.12.102`: the fabrication path is one dictionary lookup away and its output would pass a
naively written T3 assertion.)*

## 2.3.8 — Builder/Probe Version vs Artifact Version

Stage 2.3 formally recognizes three potentially different identities.

| Identity | Describes | Carrier |
|---|---|---|
| Artifact producer | Software declared by artifact | `SourceInfo.version` where applicable |
| Builder/probe tool | Tool that generated the observation | `ProvenanceEntry.tool_version` |
| Model/heuristic | Model that generated an estimate | `ProvenanceEntry.model_version` |

Example — artifact declares `encoder = Lavc`, `encoder_version = 61.3.100`; probe is `ffprobe = 8.0`;
observation records `encoder = Lavc`. The resulting provenance must not collapse these into one version.
Conceptually `SourceInfo.version` → artifact-declared producer; `ProvenanceEntry.tool_version` →
probe/build tool; `ProvenanceEntry.model_version` → model/heuristic, if applicable.
**This separation is mandatory.**

*(audit: the table is correct and is the strongest part of the draft; it is also exactly what **G15**
breaks in practice, because a PyAV probe has two legitimate builder-side versions at once —
`av.__version__ = 18.1.0` and `libavformat = 62.12.102` — and the draft's carrier model assumes the probe
is a single binary with one banner.)*

## 2.3.9 — Technical Metadata Categories

Stage 2.3 should distinguish metadata by origin. **(A) Container-declared:** format name; format long
name; container-level duration; container bitrate; creation metadata; container tags. **(B)
Stream-declared:** codec; profile; level; dimensions; pixel format; frame rate; stream bitrate; time
base; channel count; sample rate. **(C) Producer-declared:** encoder name; encoder version; writing
application; muxing application; creation tool. **(D) Probe-generated:** normalized representation;
parsed technical values; probe diagnostics; extraction status.

Probe-generated information must not be represented as if it were artifact-declared information.

*(audit: **G11** — categories A–D re-invent what `SourceLayer` already encodes; a second origin carrier is
prohibited by §2.3.2's own rule. **G18** — category C is unusable until a tag→concept table freezes which
tag names may feed which concept. §F.3/§F.6 show category-D material today being emitted as
`layer: source_native` with `state: extracted`, which is the violation this sentence forbids.)*

## 2.3.10 — Source Metadata Rule

For every technical metadata value, Stage 2.3 should be able to answer: (1) What value was observed?
(2) Where was it found? (3) Was it explicitly declared? (4) Which probe extracted it? (5) Which probe
version performed the extraction? (6) Was any transformation applied? This establishes an auditable
chain: Artifact → Container/Stream metadata → Probe extraction → Normalized technical observation →
Evidence reference → Provenance.

*(audit: questions 4–6 are precisely the G15/G13/G14 gap — (4) needs an approved mechanism list, (5) needs
the probe-version tuple defined, (6) needs `transform_type` values registered rather than improvised.)*

## 2.3.11 — No Silent Normalization of Identity

Normalization may change representation but must not change identity. `"AVC"`, `"h264"`, `"H.264"` may
potentially be normalized into a canonical codec representation **if the canonicalization rule is
explicitly defined**. But `"h264"` must never be normalized into `"x264"`, because those represent
different concepts. Likewise `"FFmpeg"` must not automatically become `"FFmpeg 7.0"` when no version is
declared.

*(audit: **G16** — the repo already violates the first sentence at the container layer:
`_normalize_container_format` (`ingestor.py:208-215`) rewrites the observed
`"mov,mp4,m4a,3gp,3g2,mj2"` to `"mp4"`, which changes identity, while the Matroska family is left
unnormalised. Canonical codec naming belongs to 2.4/2.5 (G9), and no canonicalization rule is defined
anywhere today.)*

## 2.3.12 — Missing Metadata Semantics

Stage 2.3 distinguishes **Present** (the artifact provides the value: `encoder: "Lavc61.3.100"`),
**Absent** (the artifact does not contain the field: `encoder: omitted`), **Unavailable** (the field may
exist conceptually, but the probe cannot retrieve it: `encoder: unavailable`), and **Invalid** (the
artifact contains a value that cannot be parsed according to the defined representation:
`encoder: invalid`). These states must not silently collapse into one another. In particular:
**Absent is not unknown producer identity, and unavailable is not permission to infer.**

*(audit: **G10** — four names, three of them renamed duplicates of the frozen §2.1.4 Dimension B
vocabulary, one of them (`invalid`) nonexistent in it, and the frozen `uncertain` — which is exactly the
home of §2.3.13's conflict — is missing. Blocking: yes.)*

## 2.3.13 — Conflicting Technical Metadata

If multiple technical sources inside the artifact provide conflicting values, Stage 2.3 must preserve the
conflict rather than silently select a preferred producer identity. For example a container tag
`encoder = Tool-A` against a stream tag `encoder = Tool-B`: the system must not silently conclude
`encoder = Tool-A` or `encoder = Tool-B` unless an explicit precedence rule exists. The conflict itself
becomes an auditable technical observation.

*(audit: the precedence rule the draft asks for already exists — §2.1.4 Dimension B step 4 ("evidence
conflicts" → `uncertain`, confidence ≤ 0.65), plus `ValidationStatus.CONFLICT` and
`ValidationInfo{rules_passed, rules_failed}`, both already in `utils/confidence.py`. 2.3 must adopt them
rather than describe a new conflict object — **G10/G11**.)*

## 2.3.14 — Probe Failure

A technical probe may fail because: artifact is malformed; container cannot be parsed; stream cannot be
decoded; metadata field is unsupported; probe process fails; resource limits are exceeded; artifact access
fails; metadata is unavailable. Probe failure must not result in fabricated metadata: `probe_failed` must
not become `encoder = unknown` unless the schema explicitly defines that representation and its semantics.
The failure itself should remain distinguishable from a successfully completed probe that found no encoder
declaration.

*(audit: **G17** — bullet 8 ("metadata is unavailable") contradicts both §2.3.12 and A8 and must be
deleted; bullet 3 ("stream cannot be decoded") belongs to the §2.1.5.1 bounded capability probe; bullets 6
and 7 are owned by §2.16 and §2.2B. The `REJ_*` set is CLOSED at v1.1, so 2.3 may not mint
`REJ_PROBE_FAILED` — it must map onto existing codes, and any genuinely new signal may only be an additive
`WARN_*`.)*

## 2.3.15 — Evidence Reference

Every technical observation that requires auditability should retain a reference to its evidence source.
Conceptually:

```text
technical_observation
    ├── value
    ├── metadata_origin
    ├── evidence_ref
    └── extraction_status
```

The evidence reference should allow an auditor to determine where the observation originated without
requiring the system to preserve arbitrary raw metadata indefinitely. This is especially important for
producer identity, because `encoder identity` must be traceable to the artifact declaration rather than to
an inference made by the system.

*(audit: **G11** — `evidence_ref` (singular) is the exact key drift the CLOSED D2 bulletin ruled wrong
("any downstream doc using `evidence_ref` / `transform` / `source.method` is wrong"); `metadata_origin`
duplicates `SourceLayer`; `extraction_status` revives the field D-3 removed from Contract #1 (§2.2
register row 23, owner Stage 4). **G13** — the frozen `evidence_refs[]` has no address grammar anywhere, so
A7 is unfalsifiable as written.)*

## 2.3.16 — `fd://<n>` and Spool Boundary

The technical probing subsystem may require controlled file-descriptor or spool-backed access to artifacts.
The `fd://<n>` mechanism therefore belongs to the technical transport layer rather than the
producer-identity layer. The contract must separately define: artifact acquisition → descriptor/spool
allocation → probe execution → metadata extraction → descriptor/spool cleanup. The descriptor itself does
**not** constitute provenance. Likewise `fd://7` does not identify the producer, the encoder, the
container, or the probe version. It is an access mechanism only.

*(audit: correct and already frozen — the `fd://<n>` canonical form is a §2.16-owned `OPEN_DECISION` (§2.2
register rows 21–22). 2.3's wording should read "§2.16 will define", not "the contract must define", or it
reads as 2.3 claiming ownership — **G19**.)*

## 2.3.17 — Spool Quota

The Stage 2.16 contract must define the limits governing temporary artifact storage. At minimum: maximum
artifact size; per-artifact quota; aggregate quota; lifetime; cleanup; overflow behaviour; observable
failure semantics; and which quota events are audited. The quota system must not silently truncate an
artifact and allow the technical probe to treat the truncated artifact as complete.

*(audit: **G19** — all eight parameters are §2.16-owned (register row 22, `OPEN_DECISION`). The last
sentence is 2.3's own legitimate requirement and must stay. What must change is 2.3's acceptance list:
A10/A11 and T9/T10/T11 cannot be *satisfied* by 2.3 before §2.16 exists — see §F.5.)*

## 2.3.18 — Security Boundary

Technical probing must treat the input artifact as untrusted data. The probe must not assume metadata is
truthful, metadata is well formed, filenames are trustworthy, embedded strings are safe, or container
declarations are internally consistent. Technical probing must therefore remain isolated from arbitrary
execution implied by artifact content. Metadata extraction is an observation operation, not an
authorization mechanism.

*(audit: the last sentence is frozen-quality writing. "Remain isolated from arbitrary execution" is, as
written, **unachievable by the mechanism actually in use** — PyAV runs FFmpeg demuxers inside the Builder
process; only a subprocess boundary would isolate anything. Restated as a resource/protocol-bounded rule
in **G15**.)*

## 2.3.19 — Stage 2.3 Non-Goals

Stage 2.3 does not determine whether a video is good or bad; whether compression is visually acceptable;
whether the content is authentic; whether a video is AI-generated; whether an encoder is trustworthy;
whether a producer is legitimate; whether metadata is truthful beyond its declared presence; semantic
content; scene classification; quality assessment; or model predictions. It reports technical evidence. It
does not convert technical metadata into conclusions outside its contract.

*(audit: sound — and contradicted by today's module: `_compute_generational_estimate`
(`ingestor.py:892`) derives `apple_ecosystem_container` from container identity and
`_compute_quality_score` (`ingestor.py:919-976`) scores bitrate/resolution/codec inside ingestion. Both
are §2.1.13 D-2 fields, not 2.3 fields, but they live in the file 2.3 will extend — register 2.3-R9/R10.)*

## 2.3.20 — Acceptance Invariants

| # | Invariant |
|---|---|
| A1 | No invented producer identity — missing encoder identity remains missing/unavailable |
| A2 | No version fabrication — a missing artifact-declared producer version is never generated from the probe's own version |
| A3 | Carrier consistency — builder-side versions use the Stage 2.1.15 provenance vocabulary |
| A4 | Source-side distinction — artifact-declared version remains distinct from builder/probe version |
| A5 | Codec ≠ encoder — codec identification cannot establish encoder identity by itself |
| A6 | Container ≠ producer — container identification cannot establish producer identity |
| A7 | Evidence traceability — producer metadata can be traced back to its artifact evidence |
| A8 | Failure distinction — probe failure is distinguishable from successful probing with absent metadata |
| A9 | No hidden inference — technical plausibility cannot silently become declared metadata |
| A10 | Resource boundedness — spool and descriptor use obey the §2.16 quota contract |
| A11 | Cleanup — temporary descriptor/spool resources have deterministic cleanup behaviour |
| A12 | Reproducibility — probe identity/version is recorded according to the existing provenance contract wherever required |

## 2.3.21 — Stage 2.3 Closure Test

| Test | Input condition | Expected result |
|---|---|---|
| T1 | Encoder explicitly declared | Encoder recorded |
| T2 | Encoder absent | Encoder omitted/unavailable |
| T3 | Encoder version declared | `SourceInfo.version` carries declared version |
| T4 | Encoder version absent | No fabricated version |
| T5 | Codec known, encoder absent | Codec recorded; encoder remains absent |
| T6 | Probe has its own version | Probe version remains builder provenance |
| T7 | Conflicting metadata | Conflict preserved according to defined rule |
| T8 | Malformed container | Probe failure recorded |
| T9 | Spool quota exceeded | Controlled failure |
| T10 | Descriptor released | No leaked descriptor |
| T11 | Temporary spool cleanup | Artifact removed according to retention rule |
| T12 | Repeated probe | Same artifact + same probe contract produces reproducible technical representation |

## 2.3.22 — Stage Boundary

> **Stage 2.3 observes technical metadata and preserves its declared origin. It does not manufacture
> producer identity, infer missing encoder information, or reinterpret technical observations as semantic
> conclusions.**

```text
2.1 Provenance Vocabulary → 2.2 Reproducibility / Consumption → 2.3 Technical / Container Observation → 2.4 …
```

The most important invariant carried forward:

```text
DECLARED   ↓  RECORD
ABSENT     ↓  OMIT / UNAVAILABLE
INFERABLE  ↓  DO NOT INVENT
```

*(audit: the boundary statement is adopted unchanged into §F.6 as the one thing in this draft that is
already closure-grade. Everything else in Part I is either a restatement of a frozen rule, a scope claim
over another stage's fields, or a rule with no vocabulary to express it in.)*

---
---

# PART II — STAGE 2.3 FREEZE AUDIT (§F)

> **The freeze question, same as §2.2's:** can every relevant path be interpreted deterministically by
> every consumer **without inventing meaning?** For 2.3 the test is sharper than it was for 2.2, because
> 2.3's subject matter is a field nobody has ever written: a producer identity that may or may not exist
> inside the artifact. Ambiguity here does not produce a crash; it produces a *confident, plausible,
> false provenance record* — which is the failure the whole Stage 2 exercise exists to prevent.

## F.0 — Method

Five classes of defect were searched for, in this order, against `stage2_1_contract_boundary.md` (CLOSED
v1.2), `stage2_2_source_identity.md` (SPECIFICATION CLOSED), `stage2_source_description.md`,
`src/videotemplate/**` and `tests/**`:

1. **Ambiguous field** — a draft term with two defensible readings, or a name that already means something
   else in the frozen vocabulary.
2. **Ownership overlap** — a draft rule over a field, code set, or policy another stage owns (§2.1.2).
3. **Missing contract** — a rule that cannot be evaluated because no frozen rule defines its vocabulary,
   its thresholds, or its representation.
4. **Cross-reference dependency** — a draft statement that is true only if a rule of §2.1/§2.2/§2.16 keeps
   a promise that is still `OPEN_DECISION`.
5. **Implementation ↔ specification gap** — what the probe actually does today versus what Part I says it
   does. Evidence was *measured*, not inferred: a PyAV probe run against mp4/mkv/webm fixtures built the
   same way `tests/test_pipeline.py` builds them (§F.4).

Every finding is classified with §2.2's closed taxonomy: `CONFORMING` · `SPECIFICATION_CHANGE_REQUIRED` ·
`IMPLEMENTATION_MIGRATION_REQUIRED` · `OPEN_DECISION` · `DOWNSTREAM_DEPENDENCY`. Nothing is left as a bare
"gap". Numbering continues §2.2's G-series (last was G8) so a finding can be cited unambiguously across
stages: **G9–G20**.

## F.1 — Scope reconciliation (G9): what §2.1 already gave 2.3, and what the draft claimed

§2.1.2 line 45 is the only frozen scope grant 2.3 holds: *"Container identity (actual container, not file
extension) → 2.3"*. Part I §2.3.1 claims 24 items. Mapped against the frozen table:

| Claimed in §2.3.1 | Frozen owner (§2.1.2 / §2.1) | Verdict |
|---|---|---|
| container identification | **2.3** | ✅ the grant |
| technical probing via approved mechanisms | **2.3** (implicit in the grant: "actual container, not extension" *requires* a probe) | ✅ admitted as the grant's instrument, not an extra field |
| media stream identification; codec; dimensions | 2.4–2.5 | ❌ overlap |
| frame rate; duration; bitrate; time base | 2.6 | ❌ overlap (and `bitrate` has no field anywhere — see 2.3-R7) |
| pixel format | 2.7 | ❌ overlap |
| color metadata (declared vs inferred) | 2.8 | ❌ overlap — 2.8's whole purpose is the distinction 2.3 would erase by capturing it flat |
| audio-stream metadata | 2.9 | ❌ overlap |
| stream metadata (as a category) | 2.4–2.9 per field | ❌ overlap |
| source metadata normalization | **2.11** (preserve / normalize / ignore policy) | ❌ overlap — §2.3.11's "if the rule is explicitly defined" concedes the point |
| representation of unavailable metadata | **2.14** | ❌ overlap — this is G10's root |
| provenance of probe-produced observations | §2.1 envelope (consume) | ⚠️ restate as consumption |
| technical evidence references | §2.1 envelope (`evidence_refs[]`) | ⚠️ consume — blocked by G13 (no grammar) |
| artifact-declared producer identity; encoder + tag/version extraction; declared creation/tool metadata; technical timestamps | **no owner in §2.1.2** | ⚠️ genuinely new — admissible only with a named consumer (§2.1.2 anti-dump rule, lines 72–74) → **G9's M4, and G20 for the missing harness** |
| container metadata; container-level duration; container bitrate | 2.3 captures, 2.6/2.11 own meaning | ⚠️ split verdict — capture ≠ authority |

**Count: 4 items are 2.3's, 10 belong to 2.4–2.9, 2 belong to 2.11/2.14, 3 are §2.1 consumption, 5 are new
and currently consumer-less.** (The dashboard's "14 of 24 outside 2.3" = the 10 + 2 + 2 §2.1-owned rows.)

**G9 — Class `SPECIFICATION_CHANGE_REQUIRED` (owned by 2.3's own text, no closed stage touched). Blocking: YES.**

Resolution to adopt when 2.3 is rewritten — a two-column scope law instead of a list:

```text
2.3 OWNS (capture + mechanism + fidelity of the declaration)
  M1 the probe mechanism list and its identity (§2.1.2's grant cannot be honoured without it)
  M2 container identity as OBSERVED (demuxer identity + declared brand, verbatim) — §2.1.2's grant
  M3 declared-metadata CAPTURE: for each observed item, the value verbatim, its scope, its tag address,
     its state — and nothing else
  M4 artifact-declared producer identity (name/kind/version verbatim), subject to G12/G14/G20
  M5 the observation discipline: declared vs unavailable vs indirect, expressed ONLY through
     §2.1.4 Dimensions A–D
  M6 probe-failure mapping ONTO the frozen §2.1.5 codes (never a new code — G18)

2.3 FEEDS, NEVER OWNS (it may not type, canonicalise, judge, or resolve these)
  codec/profile/level/dimensions → 2.4–2.5 · timing authority incl. container-declared duration → 2.6
  pix_fmt/bit depth/chroma → 2.7 · color declared-vs-inferred → 2.8 · audio → 2.9
  preserve/normalize/ignore policy incl. any canonicalisation rule → 2.11
  missing/uncertain/unavailable representation → 2.14 · gate order/codes → 2.1.5 / §2.2B
  envelope vocabulary incl. evidence-ref grammar → §2.1
```

The law that makes the overlap non-competitive: **2.3 may capture a declared item, but a captured item is
an input to its owner stage, never a verdict about it.** "The container declares `encoder=Lavf62.12.102`"
is 2.3's sentence; "the video was encoded by FFmpeg" is nobody's.

## F.2 — Findings G9–G20

### G10 — §2.3.12 / §2.3.3 invent a third availability vocabulary *(blocking)*

**Locus:** §2.3.3 (Declared / Unavailable / Observed-indirectly), §2.3.6 (`encoder = unavailable`),
§2.3.12 (Present / Absent / Unavailable / Invalid).

The frozen vocabulary is `ObservationState` = `extracted | absent | uncertain | unavailable` (§2.1.4
Dimension B, implemented `utils/confidence.py:32-48`, carrying a **five-step ordered decision procedure**,
not merely names). Mapping the draft onto it:

| Draft state | Frozen equivalent | Problem |
|---|---|---|
| Present | `extracted` | Rename only. Two names for one state in one spec set = the D-1 drift §2.2 register row 15 exists to prevent. |
| Absent | `absent` | Same referent, weaker definition: Dimension B's `absent` is a **positive assertion** ("I looked; it is not there") — exactly the commitment A1 needs, which "does not contain the field" does not make. |
| Unavailable | `unavailable` | Rename only — and then mis-used as a value (below). |
| — | `uncertain` | **Dropped**, although Dimension B step 4 routes conflicting evidence there. §2.3.13 therefore has no home in the draft's own vocabulary. |
| Invalid | *(none)* | A fifth state. Keeping it amends a CLOSED §2.1 vocabulary (§V.2), and steps 3/4 already split what it lumps: probe raised → `unavailable`; value obtained but unusable/conflicting → `uncertain` + confidence ≤ 0.65. |

Three further defects inside the same sections:

1. **Sentinel values.** `encoder: unavailable` and `encoder: invalid` put a state *inside the observed
   value*. That is the pattern §2.1.15 R4 forbids for versions and Dimension B's `null` rule exists to
   prevent for observations. The repo already exhibits it: `fmt_name = "unknown"` (`ingestor.py:185-186`),
   `codec = stream.codec.name or "unknown"` (`ingestor.py:229`), `avg_frame_rate = "0/0"`, and SAR falling
   back to `"1:1"` (`ingestor.py:246`) — that last asserts square pixels for a clip that declares none
   (measured: `sar=None` on fixture A, `_s23_out.txt` line 24), which is A1/A9 material today.
2. **T1-granularity gap (a genuine §2.1 defect that 2.3 surfaces).** Dimension A rule 1 assigns "value
   returned by a single structural probe → **T1**", and a T1 field has **no per-field `state`** — only the
   parent group's. A container-level tag captured as T1 therefore cannot express `absent`: the only
   representations available are a group-level `null` (reserved by Dimension B for "not applicable") or a
   forbidden sentinel string. **A1 is unrepresentable for any T1 producer field**, so producer identity is
   necessarily ≥ T2 — or §2.1's tier rule needs an explicit exception.
3. **R8 boundary.** §2.1.15 R8: version fields "never carry an `ObservationState`". §2.3.12's table is
   titled by `encoder`, mixing the *name* (a source observation → state-bearing) with the *version*
   (`SourceInfo.version` → never state-bearing, omission-only per R3). As written, obeying A2 and obeying
   R8 pull in opposite directions.

**And `invalid` has no reachable producer at all.** The approved mechanism is opened with
`metadata_errors="warn"` (`ingestor.py:71`, `decoder.py:65`), so a container that *opens* but carries
undecodable metadata raises a Python warning and still returns `succeeded` — and no consumer of `warnings`
exists in `src/`. Conversely, the inputs that do fail, fail **before** any metadata is read: measured
fixtures E (a 200-byte prefix of a valid mp4) and F (128 bytes of ASCII named `.mp4`) both raise
`av.error.InvalidDataError [Errno 1094995529] Invalid data found when processing input` from inside
`av.open` (`_s23_out.txt` lines 60 and 63) and are converted by `ingestor.py:66-77` into
`IngestionError("Unreadable container format: …")` with `recoverable=False`. So `invalid` is a state with
zero inputs in this stage: byte-damage → probe raise, metadata damage → warning + `succeeded`. The draft
must either register the defect rule that produces `invalid` (with its observable trigger and its test) or
drop it; and because the two measured failures are **identical in exception type, message prefix and
recoverability**, a non-video file and a damaged video are today indistinguishable at the contract layer —
which is A8 failing before Stage 2.3 even exists.

**Class:** `SPECIFICATION_CHANGE_REQUIRED`, split: (a) in-stage rewrite to consume Dimension B;
(b) `invalid`, if kept, becomes a §2.1 v1.3 candidate (§V.2); (c) the T1-granularity gap is a §2.1
ambiguity (§V.2). **Owner:** 2.3 (a,b) / §2.1 (c). **Blocking: YES.**

### G11 — §2.3.15 revives keys and carriers already closed *(blocking, cheap)*

| Draft key | Frozen status |
|---|---|
| `evidence_ref` | The CLOSED D2 bulletin (`stage2_source_description.md` §2.12 item 2) resolved envelope drift in favour of Stage 1 §6: `evidence_refs[]`, `transform_type`, `source{layer, model, tool}`, `validation`. Its ruling is verbatim: *"Any downstream doc using `evidence_ref` / `transform` / `source.method` is wrong."* The draft's block is wrong on the first line. |
| `metadata_origin` | A second origin carrier. `SourceLayer` (`source_native / analysis_normalized / evidence / semantic / template_dna`) already separates §2.3.9's categories A/B/C from D, and §2.3.2 itself forbids a second provenance carrier. |
| `extraction_status` | Contract-level `extraction_status` was **removed from Contract #1** by D-3 (recorded `models/source_description.py:201-204`): it is a Contract #11 rollup, and its Contract #3 survival is `OPEN_DECISION` (§2.2 register row 23, owner Stage 4). Per-observation reintroduction inside Contract #1 reopens a decision 2.3 does not own. |

**Required restatement (adopt verbatim):** a technical observation is
`{value, state, source, provenance[]}` where `provenance[].evidence_refs[]` locates the declaration,
`source.layer` distinguishes artifact-declared from probe-generated, and `transform_type` names any
transformation. **Class:** `SPECIFICATION_CHANGE_REQUIRED`, owner 2.3. **Blocking: YES** — cheap to fix, but
leaving it puts 2.3 in direct conflict with a closed bulletin.

### G12 — `SourceInfo` cannot express artifact-declared producer identity *(blocking; §2.1 v1.3 candidate)*

§2.1.15 §3 fixed the *meaning* of `SourceInfo.version` (source-side, artifact-declared, never a Builder
version). It did not give the carrier enough structure to be used:

```text
SourceInfo { layer, model, tool, version }      utils/confidence.py:77-81 (post-v1.2 projection)
  tool    = "PyAV"     ← Builder-side, written for EVERY group (ingestor.py:65-68)
  version = ?          ← source-side, artifact-declared (v1.2)
```

One `source` object therefore holds a Builder tool name beside an artifact-declared version, and nothing
records **which kind** of artifact producer the version came from — encoder, muxer, writing application, or
creation tool. §F.3 shows the omission is not academic: the measured mp4 declares
`encoder = "Lavf62.12.102"` at **container** scope while the x264-encoded video stream declares **no**
producer tag at all. Copying that container tag into `VideoStreamInfo.source.version` would present a
**muxer** string as the video stream's encoder — an A1/A5 violation *licensed by the vocabulary itself*,
invisible on review because every field name used is legal and every rule obeyed.

| Option | Shape | Cost |
|---|---|---|
| **P1 (recommended)** | New Contract #1 group `producer_declared: [{kind, value_verbatim, scope, state, evidence_refs[]}]`, `kind ∈ {encoder, muxer, writing_app, creation_tool}` (frozen, additive), plus population rule: "`SourceInfo.version` of a group is set only from a declaration whose scope covers that group" | One new group at 2.15 + a §2.1.9 inventory row; `SourceInfo.version` and R3 untouched |
| P2 | Add `producer_kind` to `SourceInfo` | Amends the v1.2 carrier two revisions after closure; `SourceInfo` becomes the union of two meanings |
| P3 | Cram the name into `SourceInfo.tool` | Rejected — `tool` is Builder-side in every existing emission and in §2.1.15 §3's table; a silent meaning change, exactly what §2.1.15 §5's non-overlap test exists to catch |

**Class:** `SPECIFICATION_CHANGE_REQUIRED` against closed §2.1 vocabulary → §V.3.2. **Owner:** §2.1 (v1.3)
+ 2.3 (population rule) + 2.15 (model). **Blocking: YES** — A1, A4, A7 and T1/T3/T5 all resolve through it.

### G13 — `evidence_refs[]` has no address grammar, so A7 is unfalsifiable *(blocking)*

A7 demands that producer metadata "can be traced back to its artifact evidence"; T7 and §2.3.15 depend on
the same claim. Nowhere in §2.1, §2.2 or `stage2_source_description.md` is the *shape* of an evidence
reference defined — no scheme, no authority, no way to address a value inside an artifact. `evidence_refs`
is a free-form `list[str]` (`utils/confidence.py`), and what the two existing producers actually put in it
are unrelated conventions:

```text
ingestor.py:96    evidence_refs = ["container_probe"]          a bare mechanism word, measured
§2.1 line 521     evidence_refs = ["source.quality_score"]     a dotted contract-field path, spec example
```

Measured run (`_s23_probe_experiment.py` → `_s23_out.txt` §"WHAT THE CONTRACT LAYER RECORDS"): for every
group of the emitted Contract #1 the only ref present is `['container_probe']`. An auditor holding
`encoder = "Lavf62.12.102"` (a tag that **is** present in the fixture — see §F.4) cannot answer "where was
it found?" (§2.3.10 question 2) from `container_probe`: it names a *method class*, not a location, and it
is identical for every group and every artifact, so it cannot fail any test. **Blocking** because A7/T7 are
unfalsifiable as written.

**Concrete proposal for §2.1 v1.3 (§V.6.1)** — a bounded grammar, additive; existing free-form values
stay legal but become a declared `legacy` form:

```text
artifact://<artifact_id>/container/tags/<key>          container-scope declaration
artifact://<artifact_id>/stream/<i>/tags/<key>         stream-scope declaration
artifact://<artifact_id>/container/<box-path>          structural / box-scope observation
file://<abs-path>                                       artifact locator (the bytes)
probe://<tool>@<tool_version>                           mechanism locator (identity, not method word)
```

Rule: a value whose state is `extracted` **from an artifact declaration** must carry at least one
`artifact://…/tags/…` ref; a group-level `probe://` ref proves the *mechanism*, never the *provenance of a
value*. Under this rule, `container_probe` would be legal only as a mechanism ref, never as the sole
justification for a producer value.

### G14 — encoder name/version: verbatim capture vs structured split *(blocking on the boundary only)*

§2.1.15 **R7** freezes declared versions as **verbatim, never normalised**; §2.3.7 wants *name* and
*version* as separate fields; §2.3.11 forbids identity-changing normalisation. The measured fixtures defeat
the split:

```text
"Lavf62.12.102"      fused name+version, ONE token, and it names the MUXER   (measured, container scope)
"Lavc61.3.100"       fused, encoder-library versioning, ffmpeg-internal     (measured, stream scope, fixture D)
"HandBrake 1.6.0 2023041600"   name + release + nightly build id — and see the suppression result below
"isomiso2avc1mp41"   compatible_brands: a brand list that looks like producer identity but is not
```

Measured suppression: fixture D asked the writer to declare
`container.metadata["encoder"] = "HandBrake 1.6.0 2023041600"`; the file on disk reports
`encoder = 'Lavf62.12.102'`. **The muxer overwrote the producer declaration.** A declared producer identity
is therefore not merely absent-or-present — it can be present at authoring time and *gone* at probe time,
with no trace.
> ⚠️ **Sharpened by Part III (§G.2.3).** "Overwrote" understates it. The declared string is **absent from the
> artifact's bytes entirely** under five different write instructions, including an empty string and an
> explicit value — so this is destruction at write time, not in-place replacement, and no write-side option
> suppresses it (`_s23_r3_out.txt:36-55`). The consequence for this finding is unchanged and, if anything,
> stronger: a real `artifact_declared` producer identity is **unbuildable in this environment**, so T1–T4
> cannot be satisfied by writing tags and must construct fixtures at the byte level (§G.2.5, T-R3b).

Any "encoder name + version" split must be additive to the verbatim string, tagged
`transform_type = "structured_parse"`, with a **registered parse-rule id**; where no registered rule parses
the string, the only lawful emission is the verbatim string. Deriving `Lavf62.12.102 → "FFmpeg n8.1"`
additionally requires a library-version→release lookup table owned by nobody and frozen nowhere; without it
that derivation is exactly the inference §2.3.4/A9 forbid, and with it the table becomes a *maintained
dependency whose staleness silently yields false producer identity*. Recommended: **no release-name
derivation in 2.3**; store verbatim + optional registered parse; defer any lookup table to the first stage
that needs a human-readable producer name.

---

## F.3 — Findings continued: G15–G20

### G15 — codec identity and encoder identity are fused in one field *(blocking; A5/T5)*

**Locus:** §2.3.7's `encoder` row, §2.3.13's inference row, §2.3.15's `container.codec`/`encoder_tag`.
§2.3.5 and A5 forbid codec→encoder, and §2.3.1's exclusion list repeats it — but §2.3.7 defines **one**
field with four different meanings (codec identification, encoder identity, encoder metadata, encoder tag,
encoder version), and §2.3.13's `codec string patterns → FFmpeg version` row *is* a codec→encoder
inference expressed as a procedure. The measured artifacts show the two are different kinds of thing at
different scopes: the codec is reported by the **decoder** (`h264`, long name
`H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10`, `_s23_out.txt:21`), while a producer declaration is a **tag**
(`encoder='Lavc61.3.100'` on the stream, `_s23_out.txt:55`). `Lavc…` and `h264` agree only because FFmpeg
made both.

**Class:** `SPECIFICATION_CHANGE_REQUIRED` — the principle is right, the structure is wrong. **Fix:** two
groups, never merged: `codec_observation` (mechanism = decoder, scope = stream, tier T1) and
`producer_declaration` (mechanism = tag reader, scope = container **and** stream, tier T2, verbatim per R7).
§2.3.13's codec-pattern row is deleted, not gated. **Blocking: YES** — A5/T5 have no field to bind to.

### G16 — normalisation destroys the observation it is supposed to preserve *(blocking; A6/§2.3.11)*

**Locus:** §2.3.11 "normalisation must not change identity", §2.3.7, and the repo's own approved mechanism.
Measured on fixture A: the probe reports `format.name = 'mov,mp4,m4a,3gp,3g2,mj2'` and
`format.long_name = 'QuickTime / MOV'`; the contract emits `format='mp4'` and
`format_long='MOV MP4 MPEG-4 Raw'` (`_s23_out.txt:16,20,66`). The first substitution picks one member of a
demuxer family list; the second **discards a probe-observed value and replaces it with a string hardcoded in
the repo** (`ingestor.py:188-198`). Measured asymmetry: `_normalize_container_format` reduces the mp4 family
list to `'mp4'` but returns `'matroska,webm'` **unchanged** (`ingestor.py:213-214`), and the `long_names`
lookup key `"matroska"` can never match a family list, so Matroska artifacts keep the probe's own long name
while mp4 artifacts lose theirs. Both are identity-changing normalisations of exactly the kind §2.3.11
forbids, and they already sit inside the stage that §2.3.2 designates as the authority on container identity.

**Class:** `SPECIFICATION_CHANGE_REQUIRED`. **Fix:** §2.3.7's table gains four columns — `scope`,
`mechanism`, `normalisation`, `state` — and one rule: *normalisation is a transformation; the verbatim value
is always retained alongside the normalised value, with the rule id recorded in `transform_type`.* Family
lists are kept verbatim (they are probe output), never reduced to a guess. **Owner:** 2.3, with the
repo-side normalisation table registered as an R9 method id. **Blocking: YES.**

### G17 — the resource half of the stage points at contracts that do not exist *(closure-blocking; A10/A11/T9–T11)*

**Locus:** §2.3.14's spool path, §2.3.20 **A10** ("§2.16 quota contract"), **A11** (cleanup), **T9/T10/T11**.
As Part I's table row D-5 already recorded, §2.16.5–2.16.7 are not defined things yet, and the §2.16
register records them as *deferred to first use with no named owner*. Three of §2.3's twelve closure tests
therefore test rules that no document owns, while §2.3 is itself the *first consumer* that would make them
"first use". Today the mechanism opens and seeks the artifact in place (`ingestor.py:71`); no spool,
descriptor or quota is touched anywhere, so T9–T11 have no subject.

**Class:** `DOWNSTREAM_DEPENDENCY` — **not** a reason to re-open §2.16, and **not** a reason to invent a
spool here. **Fix:** §2.3 keeps its §2.3.14 *outcome* taxonomy (including "input resource limit exceeded"
as an outcome name) and explicitly marks the *mechanism* as `pending 2.16`, moving the three tests to a
"blocked-by" list rather than the closure list; §2.3.20 then states which invariants close today (A1–A9,
A12) and which are held (A10–A11) — the §2.2A precedent. **Owner:** 2.3 (wording) / 2.16 (mechanism).
**Blocking for A10/A11: yes; for the rest of 2.3: no.**

### G18 — probe failure, unreadable input and "probed, nothing declared" are one state today *(blocking; A8/T8)*

Measured: fixture E (a valid mp4 truncated to its first 200 bytes) and fixture F (128 bytes of ASCII text
named `.mp4`) both raise `av.error.InvalidDataError [Errno 1094995529] Invalid data found when processing
input` from `av.open`, and `ingestor.py:66-77` converts both into
`IngestionError("Unreadable container format: …", recoverable=False)`
(`_s23_out.txt:60,63,72,73`). Three distinct §2.3.14 outcomes — damaged artifact, wrong artifact, and
successful probe with nothing declared — are indistinguishable by exception type, by message prefix and by
recoverability. §2.3.12's warning that "probe raised → metadata fabricated as default" understates the
present condition: the repo cannot tell a damaged video from a text file, and §2.3.11's reclassification of
byte-damage to `unreadable` has nowhere to be recorded, because the `container` group has no failure field
and §2.1.5 has no registered code for it.

**Class:** `SPECIFICATION_CHANGE_REQUIRED` plus a repo-side defect (§F.6). **Fix:** each §2.3.14 outcome gets
one §2.1.5 code registered by 2.3; a probe raise records `state=unavailable` **on the group** plus a failure
entry instead of raising away the distinction; "wrong artifact" (non-video) is separated from "damaged
artifact" (video, incomplete). **Blocking: YES.**

> ⚠️ **Extended by Part III (§G.5.1).** An eleven-input census adds two facts to this finding. First, the
> collapse is *wider* than three outcomes: "no video stream" and "path does not exist" are **also** distinct
> physical conditions that the code happens to distinguish today (`IngestionError('No video stream found')` vs
> `'File not found'`), while three genuinely different malformations (24-byte header, truncated mid-stream,
> 128 ASCII bytes) collapse into one branch. Second, and more consequentially, **three of the draft's
> proposed states have no reachable producer at all** — `UNSUPPORTED`, a distinct `INVALID`, and a distinct
> `PROBE_FAILURE` — because `except Exception` at `ingestor.py:70-73` catches every `av` error and the only
> signal available is a single errno. So the fix is not merely "split the branch": §2.3.14's state list
> needs a reachability column, and the two `METADATA_*` states need reclassifying as *success-with-state*
> rather than failure (§G.5.2).

### G19 — probe identity is never recorded, so T12 is not a property of the system *(blocking; A12/T12)*

Measured: `SourceInfo.version` exists in the model but is `None` for **every** group of the emitted
Contract #1 (`_s23_out.txt:66,69`), while the values that would fill it are trivially available
(`av.ffmpeg_version_info='8.1.2'`, `libavformat=62.12.102`; `_s23_out.txt:7,11`). Consequences: (i) A12 is
vacuously satisfied — `None` is not a record; (ii) T12 ("same artifact + same probe contract → reproducible
representation") cannot be evaluated, because the emitted representation never names the contract that
produced it; (iii) §2.2's cache key cannot carry the probe identity it requires (Part I row 14). And the
probe's answer is container-dependent in ways a build bump can silently change: the same producer declaration
is keyed `encoder` on mp4 and `ENCODER` on Matroska (`_s23_out.txt:19,30`), so a case-sensitive lookup
returns *present* for one artifact and *absent* for another of identical provenance.

> ⚠️ **Corrected by Part III (§G.6.1).** The premise "exists in the model but is `None`" is wrong in a way
> that strengthens the finding: `SourceInfo` has **no `version` field at all** — its fields are exactly
> `['layer', 'model', 'tool']`, and `ProvenanceEntry`'s are `['confidence_delta', 'evidence_refs', 'layer',
> 'transform_type']`, with no version anywhere (`_s23_r3_out.txt:178-180`). The gap is therefore total, not
> partial, and T12 fails for want of a *field*, not for want of a value. §2.1.15 v1.2 already specifies both
> fields; 2.3's job is to consume them, not to define them.

**Class:** `SPECIFICATION_CHANGE_REQUIRED` (one population rule, plus a §2.1-adjacent clarification) +
`IMPLEMENTATION_MIGRATION_REQUIRED` (`SourceInfo.version` must actually be written). **Fix:** a rule — *"a group's
`SourceInfo.version` is set only from a declaration whose scope covers that group; the mechanism's own
identity is recorded once at artifact level as `probe://<tool>@<version>` (§G13 grammar) and enters the §2.2
cache key"* — and an explicit statement that tag lookup is either registered case-insensitive or verbatim
exact, never implicit. **Blocking: YES** (T12 unexecutable, A12 unfalsifiable).

### G20 — no producer-declaration test exists, and the draft's fixture is unbuildable *(blocking; A1/A5/T1–T4)*

**Nothing in the repo asserts anything about producer declarations, in either direction.** The complete set
of container/metadata assertions in the suite is: `result.container.format == "mp4"` and
`size_bytes > 0` (`test_pipeline.py:80-81`), `video_stream.codec in ("h264", "libx264", "mpeg4")` (`:82`),
and three non-emptiness checks on `provenance` (`:148-150`). Line 82 is A5's exact blind spot — a codec
allow-list recorded and never disclaimed as *not* encoder identity — and `:148-150` are satisfied forever by
the single constant ref `['container_probe']` (§G13), so "provenance exists" is unfalsifiable too. There is
**no** `encoder`-absent test, and the draft's fixture concept is not merely uncovered but unbuildable as
described: `create_simple_video` (`test_pipeline.py:23-58`) has **no tag-writing parameter at all**, so
§2.3.12's row "no container tags | `mkv_no_tags` fixture (`write_tags=False`)" cites a fixture and a flag
that do not exist in the repo — and even a file that helper writes with zero metadata still reports
`encoder='Lavf62.12.102'` (mp4, `_s23_out.txt:19`) or `ENCODER='Lavf62.12.102'` (Matroska, `:30`) plus a
stream `DURATION` tag (`:33`), because the muxer declares a producer whether or not the test asks it to. A
"no container tags" artifact is therefore a *deliberate suppression*, not an absence — which is exactly what
fixture D of §F.4 measures. Until that distinction exists in the harness, T1–T4 cannot tell a compliant
implementation from one that invents `encoder="FFmpeg"`.

**Class:** `SPECIFICATION_CHANGE_REQUIRED` (T1–T4 must be specified as contract tests) +
`IMPLEMENTATION_MIGRATION_REQUIRED` (the repo has no such test, and `create_simple_video` cannot produce the
fixtures they need). **Blocking: YES.**

---

## F.4 — The measurement: what the approved mechanism can actually see

**Method (reproducible).** `_s23_probe_experiment.py` builds six fixtures with the same construction the
test suite uses (`create_simple_video`, `test_pipeline.py:23-58`: 160×120, yuv420p, 10 fps, 1 s, libx264 or
libvpx), then asks the repo's **only** approved probe mechanism — `av.open(..., metadata_errors="warn")`,
`ingestor.py:71` — what it can see, and finally runs the real `_extract_container_info` to show what the
contract records. Reproduce with `python _s23_probe_experiment.py > _s23_out.txt 2>&1`; every number below is
a line of `_s23_out.txt`. `tests/test_pipeline.py::test_full_pipeline_success` passes on the same
interpreter, so the environment is the repo's own.

**Probe identity as measured** (`_s23_out.txt:2-11`) — this is what §2.3 must record and does not:

```text
PyAV 18.1.0        av.ffmpeg_version_info = '8.1.2'
libavformat 62.12.102   libavcodec 62.28.102   libavutil 60.26.102
libavdevice 62.3.102    libavfilter 11.14.102  libswscale 9.5.102   libswresample 6.3.102
```

**Fixtures and what the probe reported.** "Tag" = a string the artifact itself declares; scope matters, and
today's code reads only the container scope.

| # | Artifact | Container tags observed | Stream tags observed | Contract records |
|---|---|---|---|---|
| A | mp4, no tags written by the test | `encoder='Lavf62.12.102'`, `major_brand='isom'`, `compatible_brands='isomiso2avc1mp41'`, `minor_version='512'` | `language='und'`, `handler_name='VideoHandler'` — **no producer declaration** | `format='mp4'`, `format_long='MOV MP4 MPEG-4 Raw'`, `size_bytes`, provenance ref `'container_probe'` — **no tag at all** |
| B | mkv, no tags written | `ENCODER='Lavf62.12.102'` — **uppercase key** | `DURATION='00:00:00.109000000'` | `format='matroska,webm'` **verbatim family list** (measured: `_normalize_container_format('matroska,webm') == 'matroska,webm'`), and `format_long` stays the probe's `'Matroska / WebM'` because the repo's lookup key `matroska` (`ingestor.py:190`) can never match a family list (`:197`) |
| C | webm via libvpx | `ENCODER='Lavf62.12.102'`; demuxer `matroska,webm` — **one demuxer for both families** | `DURATION=…`; codec `vp8`, `profile=None` | as A |
| D | mp4, producer declared at container **and** stream scope | `encoder='Lavf62.12.102'` — the declared `HandBrake 1.6.0 2023041600` was **overwritten by the muxer** ⚠️ *amended by §G.2.3: the declared value is **not in the bytes at all**; it is destroyed at write time, and the stream-scope value below was written by the fixture builder, not preserved* | `encoder='Lavc61.3.100'` — **survived**, at a scope nothing reads ⚠️ *amended by §G.2.3: this value was authored by the fixture itself (`_s23_probe_experiment.py:108`); it did not "survive" a declaration* | byte-identical to A: same 5 fields, `has encoder anywhere? False` |
| E | A truncated to its first 200 bytes | — | — | `IngestionError("Unreadable container format: …")`, `recoverable=False` |
| F | 128 bytes of ASCII named `.mp4` | — | — | **the identical** exception, message prefix and recoverability as E |

**The collision, stated once.** A declares `encoder = "Lavf62.12.102"`. The probe's own libavformat is
`62.12.102`. The artifact's declaration of its producer and the mechanism's own identity are the **same
string**, because FFmpeg stamps the version of the library performing the mux. §2.3.14's prohibition
("probe version must not become artifact encoder version") is therefore not a hypothetical to be guarded by
an `if` — it is the *default outcome* of reading the one tag that FFmpeg-muxed files carry.

> ⚠️ **Refined by Part III (§G.2.2).** The collision is real, but the mechanism is more specific than
> "FFmpeg stamps the library version": the string is **physically written into the file** by the muxer — in
> mp4's `©too` atom, in Matroska's `MuxingApp`/`WritingApp` EBML fields (`_s23_r3_out.txt:16-18`). The probe
> reads it faithfully; nothing is computed at probe time. What makes it a hazard is therefore not
> fabrication but authorship: it is the *writing stack describing itself*, which is why Part III introduces
> the `muxer_authored` origin class (§G.2.4) instead of a blanket "reject generated values" rule.

**Geometry and timing the probe declines to assert** (`_s23_out.txt:23-24,34,45`): on fixture A
`sample_aspect_ratio` is `None` (repo emits `"1:1"` — G10), `average_rate` is `10000/109` against
`guessed_rate 1000/1`, container `duration=109000` with `bit_rate=161541`, stream `time_base=1/16000`
`duration=1744`; on B and C the stream reports `duration=None` and `bit_rate=None`, with the duration living only in a `DURATION` **tag**. So "duration" and "bitrate" have three different
sources with three different statuses, and §2.3.7's single-row-per-field table cannot express which source
produced the value.

**What the contract layer emitted for those same files** (`_s23_out.txt:66-71`, produced by the real
`_extract_container_info`):

```text
ContainerInfo fields = ['format', 'format_long', 'provenance', 'size_bytes', 'source']
source     = {layer: source_native, model: None, tool: 'PyAV', version: None}
           ⚠️ amended by §G.6.1: `version` is not a field that is None — it does not
             exist. SourceInfo's fields are exactly ['layer', 'model', 'tool'].
provenance = [{layer: source_native, evidence_refs: ['container_probe'],
               transform_type: 'none', confidence_delta: 0.0}]
has encoder anywhere? False        # for A — and also for D, which declares one at two scopes
```

Five fields survive from a probe that reported a demuxer family list, a long name, four container tags,
codec name and long name, a codec profile, a time base, a stream duration, a container duration, two
bit-rates, a pixel format and a frame rate. Nothing in the emitted object states *which* of those the probe
looked at, at what scope, with which build, or with what confidence — and there is no field in
`ContainerInfo` that could hold an `ObservationState`.

### F.5 — Invariant and closure-test map, measured

| Invariant | Status in the system today | Measured basis |
|---|---|---|
| A1 no invented producer identity | **Held by accident, unfalsifiable** — the code never reads any tag, so it cannot invent one; no test could catch it if it did | `has encoder anywhere? False`; §G20 |
| A2 no version fabrication | **Held, unfalsifiable** — `SourceInfo.version` is `None` everywhere; the only value that *could* be fabricated (`Lavf62.12.102`) is present on disk and unreachable | `_s23_out.txt:66,69`; §G12, §G19 |
| A3 carrier consistency | Held (single carrier `SourceInfo`), vacuously — never populated | `utils/confidence.py` |
| A4 source-side vs builder-side distinction | **Unrepresentable**: one `version` field must carry both, and the strings collide | §G12, collision block above |
| A5 codec ≠ encoder | **Unenforceable**: only `StreamInfo.codec` exists; `test_pipeline.py:82` asserts the codec allow-list with no disclaimer | §G15, §G20 |
| A6 container ≠ producer | Held today; **will break** on the first commit that reads `encoder` | A-vs-D identity |
| A7 evidence traceability | **Failed**: the only ref is a constant word naming a method class | `['container_probe']`; §G13 |
| A8 probe failure ≠ absent metadata | **Failed**: damaged video and non-video are the same object; success-with-no-metadata is an exception, not a state | E vs F; §G18 |
| A9 no hidden inference | **Failed today** at neighbouring scope: SAR `None → "1:1"`, `fmt_name="unknown"`, `codec or "unknown"` | `_s23_out.txt:24`; §G10.1 |
| A10 resource boundedness | **No subject**: mechanism opens the file in place; §2.16.5–7 undefined | §G17 |
| A11 cleanup | Same | §G17 |
| A12 probe identity recorded | **Failed**: field exists, value is `None`, identity is available and discarded | `_s23_out.txt:7,11,66` |

| Test | Executable today? | Why / why not |
|---|---|---|
| T1 declared encoder recorded | **No** | no field to record it in; muxer suppression (D) must be modelled |
| T2 encoder absent → omitted | **No** | "absent" is indistinguishable from "suppressed by muxer" and from "not read" |
| T3 declared version in `SourceInfo.version` | **No** | population rule missing (§G12) |
| T4 no fabricated version | Unfalsifiable | nothing writes the field |
| T5 codec recorded, encoder absent | **No** | one field serves both (§G15) |
| T6 probe version stays builder provenance | **No** | builder identity is never recorded (§G19) |
| T7 conflicting metadata preserved | **No** | no conflict rule, no scope model, no ref grammar (§G11/G13) |
| T8 malformed container → probe failure recorded | Partly | failure raises out of the stage; nothing is *recorded* (§G18) |
| T9–T11 spool/quota/cleanup | **No subject** | §G17, `pending 2.16` |
| T12 reproducible representation | **No** | representation does not name its producer (§G19) |

Two of twelve closure tests are executable in the current system; neither of them tests the stage's subject
matter.

---

## F.6 — Register, repo-side defects, verdict

### The register (continues the §2.1/§2.2/§2.2A/§2.16 register conventions)

| # | Title | Class | Owner | Blocking |
|---|---|---|---|---|
| G9 | §2.3.1 claims 24 scope items; 4 are 2.3's, 12 belong to 2.4–2.14, 5 are new and consumer-less | `SPECIFICATION_CHANGE_REQUIRED` | 2.3 | yes |
| G10 | Five-state encoder taxonomy vs frozen `ObservationState`; sentinel values; T1-granularity gap; R8 tension | `SPECIFICATION_CHANGE_REQUIRED` (part `OPEN_DECISION` on `invalid`) | 2.3 / §2.1 | yes |
| G11 | §2.3.15 revives keys and carriers already closed (`container.tags`, `encoder_tag`, `producer_software`) | `SPECIFICATION_CHANGE_REQUIRED` | 2.3 | yes (cheap) |
| G12 | `SourceInfo` cannot express artifact-declared producer identity; one `version` slot, two owners; muxer collision is the default | `SPECIFICATION_CHANGE_REQUIRED` (§2.1 v1.3 candidate) | §2.1 + 2.3 | yes |
| G13 | `evidence_refs[]` has no address grammar → A7/T7 unfalsifiable | `SPECIFICATION_CHANGE_REQUIRED` | §2.1 | yes |
| G14 | Verbatim-R7 vs name/version split; a declared producer can be overwritten by the muxer | `SPECIFICATION_CHANGE_REQUIRED` (narrowly) | 2.3 | yes |
| G15 | Codec identity fused with encoder identity in one field; §2.3.13's codec-pattern row is the forbidden inference | `SPECIFICATION_CHANGE_REQUIRED` | 2.3 | yes |
| G16 | Normalisation destroys the observation (family-list reduction, hardcoded long names, dead lookup key) | `SPECIFICATION_CHANGE_REQUIRED` + `DOWNSTREAM_DEPENDENCY` (2.11 owns the policy) | 2.3 | yes |
| G17 | A10/A11/T9–T11 bind to §2.16.5–7, which do not exist; mechanism must be marked `pending 2.16` | `DOWNSTREAM_DEPENDENCY` | 2.16 | closure-only |
| G18 | Probe failure / wrong artifact / success-with-nothing-declared collapse into one exception | `SPECIFICATION_CHANGE_REQUIRED` + `IMPLEMENTATION_MIGRATION_REQUIRED` (`ingestor.py:66-77`) | 2.3 | yes |
| G19 | Probe identity never recorded → A12 vacuous, T12 not a property of the system | `SPECIFICATION_CHANGE_REQUIRED` (population rule) + `IMPLEMENTATION_MIGRATION_REQUIRED` | 2.3 (+§2.1 rule) | yes |
| G20 | No producer-declaration test exists; the draft's `mkv_no_tags` / `write_tags=False` fixture is unbuildable as described | `SPECIFICATION_CHANGE_REQUIRED` + `IMPLEMENTATION_MIGRATION_REQUIRED` | 2.3 | yes |

Eleven of the twelve findings block the freeze; one (G17) blocks only the two invariants that depend on
§2.16. Every finding is classified exactly once, per §2.2's divergence-guard rule — nothing is left as a
bare "gap". The pattern is the one §2.2 and §2.16 already recorded: **a stage written as a self-contained
design document, downstream of contracts it never cites.**

### Repo-side defects (evidence for the findings, not the findings themselves)

| Where | Behaviour | Finding |
|---|---|---|
| `ingestor.py:185-186, 229` | `"unknown"` sentinels emitted instead of absence | G10 |
| `ingestor.py:246` | SAR `None` → `"1:1"` asserts square pixels (measured `_s23_out.txt:24`) | G10 / A9 |
| `ingestor.py:188-198, 209-215` | probe long name overwritten by a repo table; mp4 family reduced, Matroska family passed through raw; lookup key `matroska` unreachable | G16 |
| `ingestor.py:66-77` | every probe raise becomes `IngestionError("Unreadable container format")`, `recoverable=False` | G18 |
| `ingestor.py:96` | `evidence_refs=["container_probe"]` is the only ref for every emitted group | G13 |
| `ingestor.py:71`, `decoder.py:65` | `metadata_errors="warn"`; no consumer of warnings anywhere in `src/` | G10 |
| `source_description.py` `ContainerInfo` | five fields; no `ObservationState`, no declaration slot | G15/G18/G19 |
| `test_pipeline.py:80-82, 148-150` | the only metadata assertions; codec allow-list never disclaimed as non-encoder | G15/G20 |

### Verdict

**Stage 2.3 as drafted is not freezable.** Not because its ethics are wrong — §2.3.3, §2.3.4, §2.3.5 and R3
are the correct moral core, and should be carried verbatim into whatever replaces §2.3.7 — but because the
draft defines its central object (`encoder`) with four meanings, in a vocabulary that is not the frozen one,
on a carrier that cannot express absence, with an evidence notion that has no address, against a mechanism
whose *measured* behaviour produces the very failure (§2.3.14's prohibition) the draft says it prevents.

**Minimum set to reach freeze:**

1. Cite §2.1.15 and adopt `ObservationState` / `SourceInfo` verbatim; drop Present/Absent/Invalid and the
   sentinel values (G1, G10).
2. Replace §2.3.7's table with a field register carrying `scope | mechanism | normalisation | state | tier`,
   and split `codec_observation` from `producer_declaration` (G5, G15, G16).
3. Settle the two owners of `version`: adopt one of the three §G12 options — **P1 recommended** (one additive
   `producer_declared[]` group at the §2.1.9 inventory, `SourceInfo.version` and R3 untouched).
4. Take the §G13 reference grammar from §2.1 v1.3, or mark A7/T7 `deferred` with a named owner — do not leave
   an unfalsifiable acceptance invariant in a frozen list.
5. Mark the §2.3.14 mechanism `pending 2.16` and move T9–T11 to a blocked-by list; §2.3.20 then states which
   invariants close today (A1–A9, A12 as reworded) and which are held (A10, A11) — the §2.2A precedent (G17).
6. Specify T1–T4 as contract tests over the §F.4 fixture matrix, asserting on emitted groups, replacing the
   `write_tags=False` fiction (G20).

What §2.3 must not do, stated in its own terms and now backed by measurement: **the tag that looks like
producer identity is usually the muxer's signature; the scope at which a real declaration survives is the one
nothing reads; and the state that looks like "absent" is most often "not read".** A stage that cannot
distinguish those three will, on its first useful commit, publish the probe as the producer — which is
precisely the failure R3 and A1 exist to forbid.

### Reproducibility

```text
_s23_probe_experiment.py   builds the six fixtures, probes them, then runs the real _extract_container_info
_s23_out.txt               73 lines of raw probe + contract output; every citation above is a line number
_s23_fixtures/             clip.mp4  clip.mkv  clip.webm  declared.mp4  truncated.mp4  fake.mp4
environment                PyAV 18.1.0 · FFmpeg 8.1.2 · libavformat 62.12.102 (as recorded in _s23_out.txt)
control                    python -m pytest -q → 25 passed in 2.36s on the same interpreter (src/ untouched)
```

These three artifacts are working files for the audit, not part of the contract set; delete them once the
findings are transcribed into the §2.3 revision, or promote the fixture builder into `tests/` when T1–T4 are
actually written (G20) — at which point it stops being evidence and starts being a regression net.


---

# PART III — STAGE 2.3 CONTROLLED REMEDIATION

> **Status: 2.3 remains OPEN.** The freeze audit (Part II) is complete; it returned a non-freezable verdict.
> Part III converts each finding into a resolution record. It changes **no** acceptance criterion, and it
> triggers **no** implementation work. Nothing under `src/` is touched in this pass.
>
> Every class below is one of §2.2's five frozen classes — `CONFORMING` · `SPECIFICATION_CHANGE_REQUIRED` ·
> `IMPLEMENTATION_MIGRATION_REQUIRED` · `OPEN_DECISION` · `DOWNSTREAM_DEPENDENCY`
> (`stage2_2_source_identity.md:778-779`). Nothing is left as a bare "gap".

## G.0 — State of record

```text
STAGE 2.3
    │
    ├── Specification draft ............ OPEN
    ├── Freeze audit .................. COMPLETE
    ├── Findings ...................... G9–G20
    ├── Blocking findings ............. 11
    ├── Non-blocking / held ........... G17  (blocked by §2.16)
    ├── Implementation migration ...... NOT YET
    ├── src/ changes .................. NONE
    └── Next phase .................... CONTROLLED REMEDIATION (this part)
```

### G.0.1 What Part III is, and what it is not

| It is | It is not |
|---|---|
| A per-finding resolution record: class, owner, required change, test, closure condition | A code change. Every "fix" below is a **specification instruction** or a **deferred migration** |
| A place to record what the second measurement pass changed about our own conclusions | A weakened acceptance criterion. No A-invariant or T-test is relaxed, narrowed, or re-scoped to pass |
| A place to hold G17 open against §2.16 | An absorption of §2.16's scope into 2.3 |

The load-bearing sentence of this part, and the reason remediation is ordered the way it is:

> **A probe failing to expose a declaration is not equivalent to the artifact not containing the
> declaration.**

## G.1 — Why remediation is ordered R3 → R1 → R2 → R4 → R5

The order is forced by measurement, not chosen for readability. The R3 experiment
(`_s23_r3_probe.py` → `_s23_r3_out.txt`, 183 lines) settled the question Part II had to leave open, and its
answer invalidates the premise two of the remediation items were going to be written against:

```text
ORDER  ITEM  SETTLES                          WHY IT CANNOT COME LATER
───────────────────────────────────────────────────────────────────────────────────────────────
1      R3    what a producer tag IS           until a value's origin is fixed, "absent" has no
                                               meaning, so R1/R2 have no object to govern
2      R1    which scopes are authoritative    scopes are meaningless before origin is classified
3      R2    how keys are compared            normalisation must preserve a known-good original
4      R4    what a failure means              states must not imply distinctions the stack cannot make
5      R5    where an identity may be written  a destination rule needs a trustworthy source
6      R6    §2.16 stays held                 never a 2.3 action at all
```

## G.2 — R3: the origin of `Lavf62.12.102` *(the finding that reorders the work)*

### G.2.1 The question, and why the draft could not answer it

R3 as posed: is the value the probe reports (a) physically in the artifact, (b) inserted by the muxer at
write time, (c) computed by PyAV/libavformat at probe time, or (d) something else? The draft §2.3.14 asserts
the prohibition on probe-generated values without establishing which of the four applies, so the assertion had
no subject.

### G.2.2 Measured answer: **(a) and (b) — present in the bytes, written by the muxer**

The string is physically present in every fixture, and it is *not* produced by the probe. The mp4 form sits
in the iTunes `©too` atom, the standard "encoder" field of the `moov/udta` box (`_s23_r3_out.txt:16`):

```text
b'\xa9too\x00\x00\x00\x1ddata\x00\x00\x00\x01\x00\x00\x00\x00Lavf62.12.102'
```

The Matroska/WebM form sits in the two EBML header fields `MuxingApp` and `WritingApp`
(`_s23_r3_out.txt:17-18`) — two occurrences per file, plus a third `Lavf` at a CRC-adjacent offset:

```text
b'...\x80\x8dLavf62.12.102WA\x8dLavf62.12.102...'     # MuxingApp, WritingApp
```

**Answer: (a) + (b).** The value is in the bytes, written by the muxer at write time. PyAV reports it
faithfully. The probe fabricates nothing.

### G.2.3 The correction this forces on Part II — a declared value is *destroyed*, not overwritten

Part II recorded, from fixture D, that the muxer "overwrote" the declared `encoder` tag. **That wording
understated the measurement, and the correction matters.** Re-running the write with the declaration isolated
(`_s23_r3_out.txt:36-55`) shows the declared value does not appear in the artifact **at all**:

| Write instruction | `HandBrake` in bytes? | Bytes contain | Re-read `container.metadata` |
|---|---|---|---|
| default | **False** | `Lavf62.12.102` @ 2409 | `encoder='Lavf62.12.102'` |
| `movflags=+faststart` | **False** | `Lavf62.12.102` @ 917 | `encoder='Lavf62.12.102'` |
| `encoder=''` (empty) | **False** | `Lavf62.12.102` @ 2409 | `encoder='Lavf62.12.102'` |
| `encoder='HandBrake 1.6.0'` | **False** | `Lavf62.12.102` @ 2409 | `encoder='Lavf62.12.102'` |
| `creation_time` only | **False** | `Lavf62.12.102` @ 2409 | `encoder='Lavf62.12.102'` |

Three consequences, each stronger than the Part II claim:

1. **A declared producer identity is unrepresentable in the output.** The value is discarded at write time.
   No artifact in this environment carries a HandBrake declaration, so no test can assert one.
2. **No write-side suppression exists.** Empty string, an explicit value, and no value at all all produce the
   identical artifact. §2.3.14's "reject or suppress" has nothing to suppress with — no flag, no option, no
   key changes the outcome. For Matroska, `MUXING_APPLICATION` and `WRITING_APPLICATION` *can* be set by the
   writer (`_s23_r3_out.txt:67-74`), but setting them does not remove the separate `ENCODER` key, which the
   muxer always writes.
3. **Part II's "false absence" on fixture D is explained.** Part II reported that D's stream-scope
   `encoder='Lavc61.3.100'` was a "surviving declaration". It was not surviving: it was a value the *fixture
   builder* wrote at authoring time (`_s23_probe_experiment.py:108`), and it survived only because stream-scope
   tags are not subject to the container-scope overwrite. The genuinely declared value — the container one —
   was destroyed. Recorded as an amendment to §F.4, not as a new finding.



### G.2.4 The classification R3 was asked to produce

The value is a **muxer-authored container default**. It is neither artifact-declared producer identity nor
probe-generated. The draft's binary (declared vs generated) has no slot for it — which is the shared root
cause of G12, G14 and G15.

> **Adopted classification (four-way), superseding the draft's binary.** This set differs from the
> earlier Part III draft (`artifact_declared` / `muxer_authored` / `decoder_reported` / `probe_generated`)
> in two ways that matter, both corrections rather than restatements:
>
> - **`unavailable` joins the origin set.** The earlier set had no way to say *"the mechanism did not obtain
>   a value at all"*, which forced that fact into the `state` axis and left a gap: a scope the probe could not
>   read then looked like an author-attribution question. `unavailable` makes it an origin-level fact, so
>   origin and state stop disagreeing about the same observation.
> - **`decoder_reported` and `probe_generated` are merged into `probe_observed`.** R3 measured that the probe
>   fabricates nothing, so a separate "probe-generated" origin describes a case with no measured instance. The
>   prohibition §2.3.14 intends does not disappear — it moves to where it actually binds, the **eligibility
>   rule** below, which is testable where a provenance label would not have been.

```text
ORIGIN CLASS         EXAMPLE                        IS IT ARTIFACT-DECLARED?
───────────────────────────────────────────────────────────────────────────────────
ARTIFACT_DECLARED    a real HandBrake 'encoder'      YES — but unbuildable in this environment
MUXER_AUTHORED       'Lavf62.12.102'  (mp4 ©too)     NO — the writing stack describing itself
MUXER_AUTHORED       'ENCODER'        (mkv header)    NO — same fact, different key name
PROBE_OBSERVED       codec 'h264' + long name        NO — reported by the decoder
UNAVAILABLE          scope the mechanism could not    NO — no value obtained, so no author
                     read                            can be attributed at all
```

Note what `UNAVAILABLE` prevents: it is the origin that pairs with `state=unavailable`, and it is distinct from
an *absent* declaration. A read that succeeded and found nothing is `ARTIFACT_DECLARED`-eligible-but-absent; a
read that could not happen is `UNAVAILABLE`. Collapsing them is precisely the false-absence defect of §G.4.1
in its other form.

**Resolution R3.** Stage 2.3 adopts the four-way origin classification above, with `MUXER_AUTHORED` added to
the draft's vocabulary as a first-class, non-inferable origin. §2.3.14's blanket prohibition is **replaced**,
not merely re-emphasised, because a rule saying "never report a probe-generated value" is silent about a value
that is neither declared nor probe-generated:

> A technical observation carries an `origin` ∈ {`artifact_declared`, `muxer_authored`, `probe_observed`,
> `unavailable`}. `SourceInfo.version` may be populated **only** from an `artifact_declared` origin.
> `muxer_authored` values are reported verbatim, attributed to the muxer, and never used to satisfy any
> `SourceInfo` field. `unavailable` means no value was obtained, so no author is attributable and the
> observation pairs with `state=unavailable`.
>
> The prohibition the draft intended is preserved as an **eligibility rule on the destination**, not as a
> label on the source. That relocation is the substance of R3:

```text
DANGEROUS CHAIN — what R3 forbids, and why origin breaks it
────────────────────────────────────────────────────────────────────────────────────────────────
  bytes contain "Lavf62.12.102"
        ↓  ✗ presence in bytes is NOT authorship
  therefore producer declared FFmpeg
        ↓  ✗ no declaration ever existed
  therefore SourceInfo.version = 62.12.102      ← the fabrication R3 makes unreachable

CORRECTED CHAIN
────────────────────────────────────────────────────────────────────────────────────────────────
  bytes contain producer-related metadata
        ↓  identify its origin
  origin = muxer_authored
        ↓  ✗ ineligible for SourceInfo.version
  → reported verbatim, attributed to the muxer, never promoted
```

This also answers the standing question in G12: the muxer collision is not an edge case §2.3.14 defends
against — it is the **only** producer-identity outcome this environment can produce for mp4 and Matroska. Any
test asserting a declared producer must construct that fixture by byte-level atom injection, not by writing
tags. That is a test-infrastructure decision, recorded in G.2.5 as T-R3b.

### G.2.5 R3 record

| Field | Value |
|---|---|
| **Findings closed** | G12 (origin half), G14 (the "overwrite" claim, now precisely stated), G15 (mechanism) |
| **Class** | `SPECIFICATION_CHANGE_REQUIRED` — origin vocabulary and the §2.3.14 rule both change |
| **Owner** | 2.3 (vocabulary + rule) · §2.1 (whether `origin` is an envelope-level attribute) |
| **Affected contract** | §2.3.4 (A9), §2.3.5, §2.3.7 (`encoder` row), §2.3.11, §2.3.13, §2.3.14; §2.1.4/§2.1.15 on the population rule |
| **Required change** | Add `muxer_authored` to the origin set; restate §2.3.14 as a rule about *eligibility for `SourceInfo.version`*, not a blanket ban; keep Part II's ban on name/version derivation |
| **Test** | **T-R3**: for each of mp4 / mkv / webm, assert `origin == muxer_authored` and that `SourceInfo.version` stays `None` **while the contract still reports the value verbatim** — the value is attributed, not suppressed. **T-R3b**: a hand-built fixture carrying a real `©too` atom, asserting `origin == artifact_declared` |
| **Closure condition** | §2.3.4 / §2.3.7 / §2.3.14 text restated; T-R3 + T-R3b specified; **no** implementation until 2.15 |
| **Blocking** | YES for the freeze |
| **Status** | RESOLVED as a specification change. Not yet applied to the §2.3 draft text — that edit is the first deliverable of the 2.3 revision pass. |


## G.3 — R1: which metadata scopes are authoritative

### G.3.1 Measured scope census

Per-fixture inventory of every key that could carry producer information, across all scopes PyAV exposes
(`_s23_r3_out.txt:84-102`):

| Fixture | Container scope | Video stream scope | Distinct keys |
|---|---|---|---|
| A mp4 (no tags set) | `encoder`, `major_brand`, `minor_version`, `compatible_brands` | `handler_name`, `language` | 6 |
| B mkv (no tags set) | `ENCODER` | `DURATION` | 2 |
| C webm (no tags set) | `ENCODER` | `DURATION` | 2 |
| D declared (tags set) | `encoder`, `major_brand`, … | `encoder`, `handler_name`, `language` | 6 |

Three facts the draft does not account for:

1. **No audio scope exists in these fixtures.** The test helper writes video only. Any scope table in §2.3.7
   that assigns authority to an audio scope is, today, unreachable by the repo's own fixtures. It may still be
   specified — but it must be marked as untested rather than presented as measured.
2. **Matroska exposes the same fact under a different key** (`ENCODER` vs `encoder`), and mp4 exposes *two*
   producer-bearing keys at container scope (`encoder`, `compatible_brands`) of which only the first is
   self-description. `compatible_brands='isomiso2avc1mp41'` is a brand list that *looks* like producer identity
   and is not.
3. **Matroska stream scope carries no producer information at all** (`DURATION` only). The stream-scope fallback
   that Part II's Fixture D appeared to demonstrate exists **only in mp4, and only because the builder wrote
   the value itself.**

### G.3.2 The rule R1 requires

Scope must be paired with origin, not chosen independently. The resolution:

> Every metadata observation is recorded with a `(scope, origin)` pair. `scope` ∈ {`container`, `video_stream`,
> `audio_stream`, `other`}, from the closed set the probe mechanism actually exposes. `origin` is per G.2.4.
> Authority is resolved by a **single precedence order**, and no scope is authoritative by virtue of existing:
>
> ```text
> 1. artifact_declared  beats   2. muxer_authored
> 3. probe_observed    is never a producer identity, whatever the scope
> 4. unavailable      attributes no author and populates no identity field
> ```
>
> A producer identity is populated only from a `container`- or `video_stream`-scoped `artifact_declared` value.
> `audio_stream` and `other` scopes are **recorded but never authoritative** for a container-level group.
> When two scopes disagree, the record keeps **both**, marks the group `state=conflicting`, and raises a
> warning code — it does not silently prefer one. Silent preference is the inference A9 forbids.

**Resolution R1** supersedes the draft's implicit "container scope only" with the scope table above plus an
explicit precedence and a conflict rule. `state=conflicting` is the new element; §2.1.4's frozen
`ObservationState` has no such value, so this is a §2.1 v1.3 candidate — routed to §2.1, owned by 2.3's
consumption of it.

### G.3.3 R1 record

| Field | Value |
|---|---|
| **Findings closed** | G14 (scope half), G15 (scope separation), G12 (scope half) |
| **Class** | `SPECIFICATION_CHANGE_REQUIRED` (precedence + conflict rule) + `OPEN_DECISION` (`state=conflicting` in the frozen `ObservationState`) |
| **Owner** | 2.3 (rule) · §2.1 (v1.3 candidate for `conflicting`) |
| **Affected contract** | §2.3.7 (scope column), §2.3.9, §2.3.11, §2.3.13; §2.1.4 for the state value |
| **Required change** | Add the scope table, the precedence order, and the "keep both, mark conflicting" rule. Mark audio/other scopes explicitly as **unreachable by current fixtures** |
| **Test** | **T-R1**: T-R3b fixture (declared at both scopes, disagreeing) → `state=conflicting`, both values retained, one warning code. **T-R1b**: for each of the six audit fixtures, assert the recorded `(scope, origin)` pair matches §G.3.1 |
| **Closure condition** | §2.3.7 amended; `conflicting` routed to §2.1 v1.3; T-R1/T-R1b specified |
| **Blocking** | YES for the freeze (a precedence rule is not optional) |
| **Status** | RESOLVED as a specification change, with one dependency on §2.1 recorded rather than absorbed |

## G.4 — R2: metadata-key normalisation, and why absence cannot be asserted before it

### G.4.1 Measured false absence

The exact-match lookup `metadata['encoder']` against each fixture (`_s23_r3_out.txt:104-111`):

| Fixture | `exact-match 'encoder'` | Case-only match, **invisible** to the lookup |
|---|---|---|
| A mp4 | `[('container', 'Lavf62.12.102')]` | — |
| B mkv | **ABSENT** | `scope=container key='ENCODER' value='Lavf62.12.102'` |
| C webm | **ABSENT** | `scope=container key='ENCODER' value='Lavf62.12.102'` |
| D declared | `[('container', 'Lavf62.12.102'), ('stream:0', 'Lavc61.3.100')]` | — |

Two artifacts of identical provenance report `present` and `absent` under the current rule, purely because
Matroska upper-cases its tag names. This is the G10 sentinel defect in its sharpest form: `"unknown"` and
`"1:1"` are false *values*, while this is a false *absence* — and a false absence is the one that A9 and the
§2.1.15 population rule cannot detect, because the emitted contract simply has no field.

### G.4.2 Measured normalisation dead end (G16 confirmation)

The codec long-name census (`_s23_r3_out.txt:113-118`) shows the `LONGS` map in `ingestor.py` covers only 2 of
the 4 observed `(name, long_name)` pairs, and the miss is silent:

```text
A mp4    video name='h264' long='H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10'  in_LONGS_map=True
B mkv    video name='h264' long='H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10'  in_LONGS_map=True
C webm   video name='vp8'  long='On2 VP8'                                    in_LONGS_map=False   ← silent miss
D decl.  video name='h264' long='H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10'  in_LONGS_map=True
```

A missing entry produces no state, no warning, and no difference in output — the value simply falls through.
Any normalisation rule that cannot report its own misses will produce exactly the confident-but-wrong record
§2.3's preamble warns about.

### G.4.3 The rule R2 requires

> Key comparison is **case-insensitive ASCII fold** against a registered canonical key set. The fold is a
> *lookup* convenience only:
>
> 1. The **verbatim original key and value are always retained** in the record, alongside the canonical key.
> 2. The fold rule is recorded as a `transform_type` with a rule id, per R7's verbatim rule.
> 3. A key that folds to a canonical key but is **not** in the registered set is `state=unrecognised` — never
>   silently dropped.
> 4. A canonical key with no registered entry is a **normalisation miss** and is reported as such. A miss may
>   never degrade silently to "absent".
>
> The distinction R2 exists to protect: **`absent` means "the mechanism read the scope and found no matching
> key."** A miss in the canonical set, an unreadable scope, or a case-fold collision all mean something else,
> and each has its own state.

**Resolution R2** adds a case-insensitive comparison layer that preserves the original and reports its own
misses. It does not add a codec-family inference: the VP8 miss stays a miss until §2.11 (which owns the
family policy) decides otherwise. This is deliberately narrower than the draft's §2.3.11, and it closes the
false-absence path that R1 alone cannot.

### G.4.4 R2 record

| Field | Value |
|---|---|
| **Findings closed** | G10 (sentinel/`"unknown"` half), G16 (lookup-key half) |
| **Class** | `SPECIFICATION_CHANGE_REQUIRED` |
| **Owner** | 2.3 (fold + retention) · 2.11 (family policy, for the codec half only) |
| **Affected contract** | §2.3.7 (key column), §2.3.11 (normalisation column), §2.3.13 (inference rows) |
| **Required change** | Case-insensitive canonical key set; verbatim retention; `unrecognised` state; normalisation-miss reporting; no codec-family inference in 2.3 |
| **Test** | **T-R2**: for each of mkv and webm, assert the `ENCODER` value is **found** and `origin == muxer_authored` — i.e. the false absence of §G.4.1 is closed. **T-R2b**: assert a key outside the canonical set yields `unrecognised`, not silent drop. **T-R2c**: assert the VP8 fixture's family is `state=unresolved` rather than silently defaulted |
| **Closure condition** | §2.3.7 + §2.3.11 amended; T-R2/T-R2b/T-R2c specified |
| **Blocking** | YES for the freeze (a false-absence path is a correctness defect, not a style issue) |
| **Status** | RESOLVED as a specification change |

## G.5 — R4: failure-state semantics, derived from reachable states

### G.5.1 Measured census — the current code produces six distinct outcomes, not the five the draft names

Eleven inputs, run through both libavformat directly and `Ingestor.ingest()`
(`_s23_r3_out.txt:120-172`):

| Input | libavformat says | `ingest()` returns |
|---|---|---|
| zero-byte file | `InvalidDataError` | `IngestionError('File is empty: …', recoverable=False)` |
| 24 bytes (header only) | `InvalidDataError` | `IngestionError('Unreadable container format: …Invalid data found…')` |
| truncated mid-stream | `InvalidDataError` | **same message as above** |
| 128 ASCII bytes | `InvalidDataError` | **same message as above** |
| valid container, no video stream | `av.open OK, video=0` | `IngestionError('No video stream found', recoverable=False)` |
| path does not exist | `FileNotFoundError` | `IngestionError('File not found: …', recoverable=False)` |
| valid file / mkv / no extra tags / ~25s long | OK | **success** |

Six distinct terminal outcomes. Three of the draft's proposed states — `UNSUPPORTED`, `PROBE_FAILURE`,
`INVALID` as distinct from `UNREADABLE` — have **no reachable producer in this environment**:

- `UNSUPPORTED` is unreachable: no input in the census produced a *recognised-but-unhandled* condition. Every
  malformed input failed at the *recognition* step, not at a dispatch step, so nothing distinguishes "we know
  this format and cannot handle it" from "we cannot read this at all."
- `PROBE_FAILURE` is unreachable as distinct from `INVALID`: `except Exception` at `ingestor.py:72` catches
  every `av` error, so a genuine library fault and a genuinely corrupt file are one branch.
- `INVALID` vs `UNREADABLE` is not separable: the three malformed cases produce the *same* `InvalidDataError`
  (errno `1094995529`) and the same message. Nothing in the current signal distinguishes "bytes are
  incoherent" from "bytes are a valid container of a format we mishandle."

### G.5.2 The state list, corrected against evidence

Per the R4 requirement that reachable states be determined by implementation evidence rather than enumeration,
two of the five proposed states are recorded as **unreachable today** and one is added:

| Proposed state | Reachable? | Evidence / what it would need |
|---|---|---|
| `UNREADABLE` | **YES** | 3 inputs, collapsed to one branch today (`ingestor.py:70-73`) |
| `INVALID` | **NO** (as distinct from `UNREADABLE`) | needs a discriminator that does not exist; §2.2B.2's channel-vs-coherence test is the model |
| `UNSUPPORTED` | **NO** | needs a recognised-format + undispatchable-codec path; none observed |
| `PROBE_FAILURE` | **NO** (as distinct from `INVALID`) | needs `except Exception` split by exception type; errno is the only signal available |
| `METADATA_ABSENT` | **YES** — but not as a *failure* | it is a **success** outcome with no declaration (§G.2: `Lavf` present but not declared). Not a probe failure |
| `METADATA_UNAVAILABLE` | **YES** — but not as a *failure* | a scope the mechanism could not read; also a success-with-caveat outcome |
| *(added)* `METADATA_ABSENT` **vs** `DECLARED_AND_MUXER_OVERWRITTEN` | **YES** — newly required | the R3 result: a declaration can exist at authoring time and be absent at probe time. This is neither "absent" nor "unavailable"; it is **destroyed** |

**Resolution R4** (a) keeps the six-state vocabulary but marks `INVALID`, `UNSUPPORTED` and `PROBE_FAILURE`
as *specified-but-unreachable*, each with the discriminator it would need; (b) reclassifies
`METADATA_ABSENT` / `METADATA_UNAVAILABLE` as **success-with-state**, not failure — they describe a completed
probe, and calling them failures would make every metadata-less artifact a rejected job; (c) adds the
R3-derived `DECLARED_AND_MUXER_OVERWRITTEN` state so that R3's destruction result is representable rather
than silently reported as absence.

The last point is the substantive one. Without (c), a destroyed declaration and a never-made declaration are
indistinguishable in the emitted contract — which is precisely the inference A9 forbids, arriving through the
state vocabulary rather than through §2.3.13's inference table.

### G.5.3 R4 record

| Field | Value |
|---|---|
| **Findings closed** | G18 (state collapse), G10 (`invalid` half) |
| **Class** | `SPECIFICATION_CHANGE_REQUIRED` (vocabulary + reachability) + `IMPLEMENTATION_MIGRATION_REQUIRED` (`ingestor.py:70-73` is one branch) |
| **Owner** | 2.3 (states + reachability notes) · 2.15 (the branch split) |
| **Affected contract** | §2.3.14, §2.3.9; §2.1.5 code set (one `REJ_*` per failure state) |
| **Required change** | Adopt the corrected table; add `DECLARED_AND_MUXER_OVERWRITTEN`; reclassify the two METADATA_* states as success-with-state; register a `REJ_*` code per *failure* state only |
| **Test** | **T-R4**: each of the 11 census inputs maps to exactly one expected state, and the 3 malformed inputs are asserted **distinct** from one another once 2.15 splits the branch. **T-R4b**: the T-R3b fixture asserts `DECLARED_AND_MUXER_OVERWRITTEN` is *not* reported for an artifact that simply never declared anything |
| **Closure condition** | §2.3.14 amended with reachability column; `REJ_*` codes registered; T-R4/T-R4b specified |
| **Blocking** | YES for the freeze — A8 fails today, and it fails because the vocabulary is wrong, not because the code is unlucky |
| **Status** | RESOLVED as a specification change; the code-side split is explicitly **deferred to 2.15** and is not a prerequisite for specification closure |

## G.6 — R5: probe identity — three distinct identities, one slot

### G.6.1 Measured: nothing is recorded, and the slot does not exist

The contract's identity carriers, as emitted (`_s23_r3_out.txt:174-183`):

```text
SourceDescription.source?        False          (no contract-level source at all)
container.source = SourceInfo(layer=SOURCE_NATIVE, model=None, tool='PyAV')
video_stream.source = SourceInfo(layer=SOURCE_NATIVE, model=None, tool='PyAV')
SourceInfo fields     = ['layer', 'model', 'tool']
ProvenanceEntry[0]    = ProvenanceEntry(layer=SOURCE_NATIVE, evidence_refs=['container_probe'],
                                         transform_type='none', confidence_delta=0.0)
ProvenanceEntry fields = ['confidence_delta', 'evidence_refs', 'layer', 'transform_type']
av.ffmpeg_version_info = '8.1.2'
av.library_versions['libavformat'] = '62.12.102'
-> no version of anything is recorded anywhere in the contract.
```

Three identities exist in this process and the contract has room for none of them:

| Identity | Value in this run | Belongs in | Status |
|---|---|---|---|
| **artifact producer version** | *nothing recoverable* — see R3 | `SourceInfo.version` | the field **does not exist** |
| **probe library version** | `libavformat 62.12.102` | `ProvenanceEntry.tool_version` | field does not exist |
| **probe executable version** | `8.1.2` (`av.ffmpeg_version_info`) | `ProvenanceEntry.tool_version` | field does not exist |

Part II's phrasing — "`SourceInfo.version` is always `None`" — was imprecise and is corrected here: the
attribute is not present on the model at all. `SourceInfo` has exactly three fields (`layer`, `model`,
`tool`), and `tool='PyAV'` is a *name*, which §2.1.11.8's anti-dump rule and §2.1.15 §2 both forbid carrying a
version string in.

### G.6.2 The rule R5 requires, and the constraint R3 imposes on it

> `artifact producer version`, `probe library version` and `probe executable version` are **three distinct
> facts** and occupy three distinct slots:
>
> - `SourceInfo.version` — the version declared **by the artifact's own producer**, from an
>   `artifact_declared` origin only. Populated from nothing else, ever.
> - `ProvenanceEntry.tool_version` — the **probe** side: the library version that performed the read, and the
>   executable version it reports. Both are builder-side facts about *how the value was obtained*, and both
>   belong here because they determine when the reading is reproducible.
>
> **R3 prohibits the obvious shortcut.** `av.ffmpeg_version_info` and `libavformat` describe *this probe*, not
> the artifact's producer. Writing either into `SourceInfo.version` would produce exactly the confident-but-
> false provenance record §2.3's preamble exists to prevent — and it would do so *silently*, because the value
> is always present and always well-formed. This is the most likely implementation error in the whole
> remediation, so it gets its own test.

**Resolution R5.** `SourceInfo.version` is populated only under the R3 origin rule, and a T-R5 assertion makes
the prohibition testable rather than advisory: for all six audit fixtures, `SourceInfo.version is None` **and**
`ProvenanceEntry.tool_version == '62.12.102'` — i.e. the probe version is recorded, and the artifact version
is not invented from it.

### G.6.3 R5 record

| Field | Value |
|---|---|
| **Findings closed** | G19 (identity), G12 (destination half) |
| **Class** | `SPECIFICATION_CHANGE_REQUIRED` (three-slot rule) + `IMPLEMENTATION_MIGRATION_REQUIRED` (`SourceInfo.version`, `ProvenanceEntry.tool_version`) |
| **Owner** | §2.1 (the fields — v1.2 §2.1.15 already specifies them) · 2.3 (population rule) · 2.15 (writing them) |
| **Affected contract** | §2.3.2, §2.3.9, §2.3.15; §2.1.15 R1–R9; §2.2 register row 24 (the existing `IMR` residual) |
| **Required change** | Adopt the three-slot rule; make "never fill artifact version from probe version" an explicit prohibition; bind population to `origin` |
| **Test** | **T-R5**: as §G.6.2 — all six fixtures, `SourceInfo.version is None` while `tool_version == '62.12.102'`. **T-R5b**: T-R3b fixture asserts `SourceInfo.version` is populated from the `©too` atom and **differs** from `62.12.102`, so the two paths are not the same code |
| **Closure condition** | §2.3.2/§2.3.15 amended; T-R5/T-R5b specified. Note §2.1 already closed these fields at v1.2 — **2.3's job is to consume them, not to redefine them** |
| **Blocking** | YES for the freeze (A12 is vacuous and T12 has no subject while this is unresolved) |
| **Status** | RESOLVED as a specification change; the field-addition work is already owned by §2.1.15 / §2.2 row 24 and is **not** re-opened here |

## G.7 — R6: §2.16 stays held, separately

### G.7.1 The decision

**§2.3.16, §2.3.17 and the resource half of §2.3.18 remain unimplementable, and this part does not change
that.** The draft binds A10, A11 and T9–T11 to `fd://<n>` and to a spool quota that §2.16 has not yet defined
(§2.16.5–7 do not exist). The measured environment offers no evidence either way — the census never reached a
file descriptor or a spool, because every failure it produced was a *read* failure.

So the resolution is deliberately the least interesting one available, and that is the point:

> §2.3 retains its §2.3.14 **outcome** name "input resource limit exceeded" as a vocabulary item, marks its
> **mechanism** as `pending 2.16`, and moves T9–T11 to a §2.3.22 closure sub-list that reads *held*, not *pass*.
> A10/A11 remain **open invariants with no current subject**. They are not deleted, not weakened, and not
> re-pointed at a mechanism 2.3 does not own.

### G.7.2 What is explicitly not done

- §2.16 is **not** re-opened. It owns the `fd://<n>` grammar, the quota, and the retention policy.
- §2.3 does **not** define a spool, a file-descriptor form, or a quota. Inventing one here would create a
  second, incompatible contract — the exact failure §2.2's `fd://<n>` `OPEN_DECISION` (register row 21) is
  already carrying.
- G17 is **not** absorbed into any other finding, and it does not block the eleven others.

### G.7.3 R6 record

| Field | Value |
|---|---|
| **Findings closed** | G17 — **held, not closed** |
| **Class** | `DOWNSTREAM_DEPENDENCY` |
| **Owner** | §2.16 (unchanged) |
| **Affected contract** | §2.3.16, §2.3.17, §2.3.18 (resource half), §2.3.20 (A10/A11), §2.3.21 (T9–T11) |
| **Required change** | Mark the mechanism `pending 2.16`; move T9–T11 to a *held* sub-list; leave A10/A11 open with no subject |
| **Test** | None possible in this environment — recorded as **held**, not as passing. When §2.16 lands, T9–T11 are written there and executed against it |
| **Closure condition** | §2.16.5–7 exist, and 2.3's held tests are re-pointed at them |
| **Blocking** | Closure-only. It does not block the other eleven findings |
| **Status** | HELD against §2.16. Explicitly **not** resolved by this part |

## G.8 — The chain, and the audit distinction that generates it

The six resolutions exist to make one distinction enforceable in the emitted contract:

> **A probe failing to expose a declaration is not equivalent to the artifact not containing the
> declaration.**

Part II asserted this as a principle. The measurements make it structural, because each link in the chain is
now backed by an observation rather than an intention:

```text
RAW ARTIFACT
     │   Q1: the bytes are the ground truth. 'Lavf62.12.102' is physically present
     │       in all six fixtures (_s23_r3_out.txt:10-13)
     ▼
CONTAINER / STREAM METADATA
     │   G.3.1: scopes differ per container. mp4 → container 'encoder' + 3 brand keys;
     │       mkv/webm → container 'ENCODER' only, stream 'DURATION' only
     │   ├── scope            ∈ {container, video_stream, audio_stream, other}
     │   ├── original key     'encoder' | 'ENCODER' | 'handler_name' | 'compatible_brands' …
     │   ├── original value   retained verbatim, never overwritten by a fold
     │   └── extraction status  read | unreadable | not_attempted
     ▼
NORMALIZATION
     │   G.4.1: exact-match 'encoder' returns ABSENT for mkv and webm — a false
     │       absence caused solely by case (_s23_r3_out.txt:107-110)
     ├── canonical key     case-insensitive fold, registered set only
     ├── preserved original   mandatory; a miss is reported, never a silent drop
     └── origin            ∈ {artifact_declared, muxer_authored,
     │                         probe_observed, unavailable}          ← G.2.4, the new link
     ▼
SOURCE METADATA
     │   G.6.1: SourceInfo has three fields and NO version. tool='PyAV' is a name.
     │       av.ffmpeg_version_info='8.1.2' sits unused beside it.
     └── SourceInfo.version   populated ONLY from origin=artifact_declared.
                               Never from av.ffmpeg_version_info, never from libavformat.
     ▼
TECHNICAL OBSERVATION
         provenance.evidence_refs  → a location, per G.13's grammar (still OPEN_DECISION)
         provenance.tool_version   → the probe side: 62.12.102 / 8.1.2
         state                     → extracted | absent | unrecognised | conflicting |
                                     unresolved | declared_and_muxer_overwritten
```

The `origin` link is the one the draft did not have, and R3 is what forced it. Without it, the chain collapses
at the normalisation step: `Lavf62.12.102` and a genuine `HandBrake 1.6.0` are both "an encoder tag at
container scope", and the only available distinction — *who wrote it* — is destroyed before the probe ever
sees the file. The audit distinction above is therefore not a principle the chain *enforces*; it is a property
the `origin` link *creates*.


## G.9 — Consolidated remediation register (G9–G20)

Continues the §2.1/§2.2/§2.2A/§2.16 register conventions. Class is one of §2.2's five frozen classes. "Held"
means resolved-as-pending against another stage; "Open" means the required change is specified but **not yet
applied to the §2.3 draft text** — which is the next pass, and is not this part's work.

| # | Title | Class | Owner | Blocking | Part III status |
|---|---|---|---|---|---|
| G9 | §2.3.1 claims 24 scope items; 4 are 2.3's, 12 belong to 2.4–2.14, 5 are new and consumer-less | `SPECIFICATION_CHANGE_REQUIRED` | 2.3 | yes | Open — §F.1 (M1–M6) not yet applied |
| G10 | Encoder taxonomy vs frozen `ObservationState`; sentinels; false absence; T1 granularity | `SPECIFICATION_CHANGE_REQUIRED` (+ `OPEN_DECISION` on `invalid`) | 2.3 / §2.1 | yes | **R2 + R4** — §G.4.3, §G.5.2 |
| G11 | §2.3.15 revives keys/carriers closed in §2.2 | `SPECIFICATION_CHANGE_REQUIRED` | 2.3 | yes | Open (cheap) |
| G12 | `SourceInfo` cannot express artifact-declared producer identity; muxer collision is the default | `SPECIFICATION_CHANGE_REQUIRED` (§2.1 v1.3 candidate) | §2.1 + 2.3 | yes | **R3 + R1 + R5** — §G.2.4, §G.3.2, §G.6.2 |
| G13 | `evidence_refs[]` has no address grammar → A7/T7 unfalsifiable | `SPECIFICATION_CHANGE_REQUIRED` | §2.1 | yes | Open — shown in the §G.8 chain, not resolved here |
| G14 | Verbatim-R7 vs name/version split; a declared producer is **destroyed**, not overwritten | `SPECIFICATION_CHANGE_REQUIRED` | 2.3 | yes | **R3 + R1** — §G.2.3, §G.3.2 |
| G15 | Codec identity fused with encoder identity; §2.3.13's codec-pattern row is the forbidden inference | `SPECIFICATION_CHANGE_REQUIRED` | 2.3 | yes | **R3 + R1** — §G.2.4 origin, §G.3.2 scope |
| G16 | Normalisation destroys the observation (family lists, hardcoded long names, dead lookup key) | `SPECIFICATION_CHANGE_REQUIRED` (+ `DOWNSTREAM_DEPENDENCY` → 2.11) | 2.3 | yes | **R2** — §G.4.2, §G.4.3 |
| G17 | A10/A11/T9–T11 bind to §2.16.5–7, which do not exist | `DOWNSTREAM_DEPENDENCY` | §2.16 | closure-only | **HELD** — §G.7.1; not absorbed |
| G18 | Probe failure / wrong artifact / nothing-declared collapse into one exception | `SPECIFICATION_CHANGE_REQUIRED` + `IMPLEMENTATION_MIGRATION_REQUIRED` | 2.3 / 2.15 | yes | **R4** — §G.5.1, §G.5.2 |
| G19 | Probe identity never recorded → A12 vacuous, T12 not a property of the system | `SPECIFICATION_CHANGE_REQUIRED` + `IMPLEMENTATION_MIGRATION_REQUIRED` | 2.3 / §2.1.15 | yes | **R5** — §G.6.1, §G.6.2 |
| G20 | No producer-declaration test exists; the draft's fixture is unbuildable as described | `SPECIFICATION_CHANGE_REQUIRED` + `IMPLEMENTATION_MIGRATION_REQUIRED` | 2.3 | yes | **R3** — T-R3b, §G.2.5; the real fixture needs byte-level atom injection |

Eleven blocking, one held. Eight rows are now resolved *as specification changes*; the remaining three
(G9, G11, G13) carry no measurement dependency and are ordinary draft edits for the revision pass.

### G.9.1 Two amendments to Part II, recorded rather than silently applied

| Part II said | Correction | Basis |
|---|---|---|
| "the muxer **overwrote** the declared `encoder` at container scope" (§F.4) | The declared value is **not in the file at all** — destroyed at write time, not overwritten in place. The `Lavc61.3.100` read at stream scope on fixture D is a value the *fixture builder* wrote (`_s23_probe_experiment.py:108`), not a surviving declaration | `_s23_r3_out.txt:36-55` — `HandBrake` absent under five different write instructions |
| "`SourceInfo.version` is always `None`" (G19) | The attribute **does not exist**. `SourceInfo` has exactly `layer`, `model`, `tool`; `ProvenanceEntry` has no version field either | `_s23_r3_out.txt:178-180` — `model_fields` enumerated |

Neither correction weakens a finding. Both make it more precise, and the second is the reason T12 has no
subject rather than merely a wrong value.

## G.10 — What Part III deliberately does not do

1. **No acceptance criterion is weakened.** A1–A12 and T1–T12 stand exactly as Part II measured them. The
   measured failures (A8 collapses, A12 vacuous, T12 untestable) are the freeze audit doing its job; the
   response is to fix the specification, not the measurements.
2. **No implementation.** Every row in §G.9 marked `IMPLEMENTATION_MIGRATION_REQUIRED` is a *2.15* item. `src/`
   is untouched in this pass; `python -m pytest -q` remains 25/25.
3. **No §2.16 re-opening** (§G.7.2).
4. **No family-policy decision.** G16's codec half stays with §2.11; 2.3 records the miss and stops.
5. **No lookup table for `Lavf62.12.102 → "FFmpeg n8.1"`.** Part II's recommendation stands, and R3 strengthens
   it: the value names the *muxer*, and deriving a producer name from it is the inference A9 forbids.
6. **The draft §2.3 text is not yet edited.** Part III specifies what the edit must say. Applying it is the
   revision pass, which is gated on the three still-open rows above.

### G.10.1 Next pass, in order

```text
1  Apply §G.9 rows G9, G11, G13 to the draft text        (no measurement needed)
2  Apply R3, R1, R2, R4, R5 to §2.3.4/.7/.9/.11/.13/.14    (origin link + scope + fold)
3  Route two items to §2.1: state=conflicting, evidence_refs grammar
4  Leave G17 held; do not touch §2.16
5  Re-run the freeze audit; 2.3 is freezable only when A8 and A12 hold on measured
   evidence — not when the text merely asserts them
```

### G.10.2 Reproducibility of Part III

```text
script                _s23_r3_probe.py
evidence              _s23_r3_out.txt   (183 lines; R3, R1, R2, R4)
command               python _s23_r3_probe.py > _s23_r3_run.log 2>&1
environment           PyAV 18.1.0 · libavformat 62.12.102 · ffmpeg_version_info='8.1.2'
inputs                the six Part II fixtures (unmodified) + 11 R4 cases in a temp dir
limitations           (a) no audio stream in any fixture, so audio-scope rules are
                      specified but untested; (b) T-R3b (a real ©too atom) is a
                      *design* for a fixture that does not exist yet; (c) §2.16 items
                      are untestable here by construction; (d) a packet-copy remux was
                      attempted and abandoned — PyAV 18 dropped add_stream(template=),
                      and Q1+Q5 answer its question without it
control               python -m pytest -q → 25 passed (src/ untouched)
```

These artifacts are audit evidence, not part of the contract set. Delete them once the findings are
transcribed into the §2.3 revision, or promote the fixture builder into `tests/` when T1–T4 and T-R1–T-R5 are
actually written (G20) — at which point they stop being evidence and start being a regression net.



---

# PART V — CONTROLLED AMENDMENT RECORD (draft → v2.3-a1)

> **This is the Stage 2.3 specification-closure pass.** It rewrites the draft's *wording* to match the
> verified contract. It changes no acceptance criterion, weakens nothing, and touches no external
> contract. Part I is **not** edited — it remains the audited baseline exactly as received, and every
> restatement below names the clause it supersedes so the delta is legible.
>
> The governing rule, applied throughout:
>
> > **Revise the specification to reflect the verified contract. Do not change implementation merely to
> > make the old wording pass.**
>
> Each restatement carries: what changes, the measurement that forces it, the register row, and what
> remains external. Nothing here is marked complete on the strength of having been written.

## V.0 — Order of application, and the four buckets

| Priority | Clause | Forced by | Register row | External? |
|---|---|---|---|---|
| **1** | **§2.3.14** — probe failure, reachability | R4 | G18 (`2.3`) | **no** — 2.3's own |
| 2 | §2.3.12 — metadata states | R4 | G10 (`2.3 / §2.1`) | partly |
| 3 | §2.3.7 + §2.3.4/5/6 — origin, scope, codec≠producer | R1, R3 | G12/G14/G15 (`2.3`) | no |
| 4 | §2.3.11 — normalisation | R2 | G16 (`2.3` + 2.11) | partly (2.11) |
| 5 | §2.3.13 — conflict | R1 | G10 | §2.1 (`conflicting`) |
| 6 | §2.3.9 — categories | R1 | G11 (`2.3`) | no |
| 7 | §2.3.2 + §2.3.8 — version carriers | R5 | G19 (`2.3 / §2.1.15`) | no — consume |
| 8 | §2.3.1 — scope | G9 | G9 (`2.3`) | no |
| 9 | §2.3.15 — evidence reference | — | G13 (**§2.1**) | **yes** — cannot land |

`§2.3.15` is the one clause this pass **cannot** close: its address grammar is `§2.1`'s to write. It is
restated here as a stated dependency, not as a proposed grammar 2.3 may adopt.

---

## V.1 — §2.3.14 Probe Failure *(supersedes the clause at line 279; priority 1)*

### V.1.1 What the draft said, and why it fails

The draft enumerates eight causes and then asserts the right principle:

> "The failure itself should remain distinguishable from a successfully completed probe that found no
> encoder declaration."

The principle is correct. The **enumeration is what fails A8 and T8**, for two independent reasons
measured in §G.5.1:

1. **Three of the eight are owned elsewhere.** "stream cannot be decoded" belongs to §2.1.5.1's bounded
   capability probe; the resource limits belong to §2.16 (G17); "metadata is unavailable" contradicts
   §2.3.12 and A8 directly.
2. **The list is not reachable.** An eleven-input census produced six distinct outcomes, and three
   proposed states — `UNSUPPORTED`, a distinct `INVALID`, and a distinct `PROBE_FAILURE` — have **no
   reachable producer** in this environment. `ingestor.py:70-73` catches every `av` error in one
   `except Exception`, so the only available signal is a single errno.

### V.1.2 The restated clause

```text
§2.3.14 — Probe failure: reachable states and their reachability

A probe outcome is recorded as one of:

  FAILURE STATES (the probe did not complete; one REJ_* code applies)
    UNREADABLE            the artifact could not be read
    NO_VIDEO_STREAM       a readable container carries no video stream
    RESOURCE_LIMIT        input resource limit exceeded        [mechanism: pending §2.16]
    REJECTED_BY_POLICY    a §2.1.5/§2.2B rule rejected the artifact before 2.3

  SUCCESS STATES (the probe completed; the artifact is described)
    METADATA_ABSENT       the mechanism read the scope and found no matching declaration
    METADATA_UNAVAILABLE  a scope or field the mechanism could not read
    METADATA_DECLARED_AND_MUXER_OVERWRITTEN
                          a declaration existed at authoring time and was replaced at write time

RULES
  R-1  METADATA_ABSENT and METADATA_UNAVAILABLE are SUCCESS outcomes. They describe a completed
       probe and must never be reported as a rejection.
  R-2  A failure state is recorded ON THE GROUP, not raised away. A probe failure records
       state=unavailable on the affected group plus the failure entry; it does not replace
       the group with an exception.
  R-3  Each FAILURE state maps onto exactly one code from the §2.1.5 CLOSED REJ_* set.
       2.3 may NOT mint REJ_PROBE_FAILED. A genuinely new signal may only be an additive WARN_*.
  R-4  Declared-and-overwritten is a SUCCESS state and is NOT absent. The distinction is
       reported, not inferred, and is only recorded when the authoring side can attest it —
       a probe reading an artifact alone CANNOT observe it (the declaration is gone).
```

**On R-4 — a correction this amendment makes to Part III.** Part III (§G.5.2) listed
`DECLARED_AND_MUXER_OVERWRITTEN` as a state to populate. That is wrong in one respect, and the
implementation follows the corrected form: **a probe cannot detect it.** The declaration is destroyed
before the file exists (§G.2.3), so from the artifact alone, "never declared" and "declared then
destroyed" are byte-identical. The state is therefore *reserved* for an authoring-side witness. A probe
that inferred it would be doing exactly the inference A9 forbids — and would be reporting a history it
cannot see.

### V.1.3 What this closes and what it does not

| | |
|---|---|
| **Closes** | The 2.3-owned *specification* half of G18. The draft can now be read without contradiction by §2.3.12, and the "resource limits" bullet is correctly marked `pending §2.16` |
| **Does not close** | A8/T8 themselves. The code still raises one `IngestionError` for three malformations. That is `ingestor.py:70-73` — an `IMPLEMENTATION_MIGRATION_REQUIRED` row, owned by **2.15** |
| **Explicitly not** | No spool, descriptor, or quota behaviour is specified here. `RESOURCE_LIMIT` names an *outcome*; its mechanism is `§2.16`'s, exactly as §G.7.1 requires |

---

# PART IV — CONTROLLED REMEDIATION: IMPLEMENTATION & VERIFICATION

> **Stage 2.3 is NOT frozen.** Part III completed the *definition* of the remediation. Part IV exists
> because a definition is not a discharge: it is the phase in which each closure condition is either
> **demonstrated** or **explicitly not discharged**. Nothing in `src/` was changed to produce it.
>
> The organising rule of this part, and the reason it is a part rather than a closing section:
>
> > **Writing the remediation down does not discharge it. Demonstrating it does.**

## H.0 — State of record

```text
STAGE 2.3
    │
    ├── Part I  -- authored draft .................... COMPLETE  (audited baseline; not edited)
    ├── Part II -- freeze audit ...................... COMPLETE  (G9–G20, 11 blocking)
    ├── Part III -- controlled remediation ........... COMPLETE  (R1–R6 specified)
    ├── Part IV -- implementation & verification .... THIS PART
    │
    ├── Empirical verification ...................... COMPLETE  (R3/R1/R2/R4 measured)
    ├── Repo test suite ............................ 25/25 PASS
    ├── Verification gate ........................... BUILT, and it reports BLOCKED
    │
    ├── Specification acceptance ................... NOT SATISFIED  (18 checks outstanding)
    ├── Implementation migration .................... NOT STARTED
    ├── src/ changes ................................ NONE
    └── Next ........................................ DISCHARGE the gate, item by item
```

### H.0.1 The one thing this part must not do

The failure mode Part IV is built to prevent is a **paper freeze**: a stage that acquires a tidy
"remediation complete" checklist and a passing-looking status, while the system it describes still cannot do
what the checklist says. Part III produced exactly the material such a freeze could be constructed from —
twelve findings, each with a class, a required change, a test and a closure condition. Completing that
document is not progress toward a freeze; it is the *precondition* for one, and the two are easily confused.

So the freeze is not gated on the document. It is gated on the executable.

## H.1 — The verification gate, and why it is a program rather than a section

A "verification" written as prose has the same failure mode as the paper freeze: it reports what someone
concluded rather than what the system did. The gate is therefore executable
(`_s23_verification.py` → `_s23_verification.txt`), and it is built so that **the most likely way to get a
wrong answer is to get no answer at all**.

### H.1.1 The asymmetry that makes it trustworthy

```text
STATUS              MEANING                                          CAN IT OPEN THE GATE?
─────────────────────────────────────────────────────────────────────────────────────────────────
PASS                ran; expectation met on real evidence             yes
FAIL                ran; expectation not met                          no  (blocking)
NOT-IMPLEMENTED     specified, but no fixture or carrier exists        no  (blocking)
VACUOUS-PASS        'passed' only because nothing could violate it     no  (blocking)
HELD                no subject; another stage owns it                 no, and excluded by design
```

Three consequences worth stating plainly, because each closes a specific way this audit could have
deceived itself:

1. **Absence of evidence is never PASS.** The naive implementation reports "no `SourceInfo.version`
   fabrication detected" when the field does not exist. That is not a pass; it is an unexercised
   obligation. Hence `NOT-IMPLEMENTED` and `VACUOUS-PASS` as first-class statuses, and both are blocking.
2. **A check that cannot run is a blocking result, not a skipped one.** T9–T11 return `HELD` — visibly
   undischarged — rather than being dropped from the run so the denominator looks better.
3. **The gate reads the repository, never the audit.** `_s23_verification.py` imports the models and runs
   the real `Ingestor`. It does not read Part III and agree with it. The `SPEC-*` rows are the *only*
   text-matching checks, they are labelled as such, and they exist solely to distinguish "the fix is
   written down" from "the fix is in the system" — a distinction no other check can make.

### H.1.2 First run — the honest result

```text
TALLY
  PASS               8
  VACUOUS-PASS       3      A1, A5, T5
  FAIL               6      A3, A7, A8, A9, A12, T8
  NOT-IMPLEMENTED    9      A2, A4, T1, T2, T3, T4, T6, T7, T12
  HELD               5      A10, A11, T9, T10, T11

GATE: BLOCKED — 18 check(s) not satisfied. Stage 2.3 is NOT freezable.
```

The three `VACUOUS-PASS` rows deserve attention, because they are the subtlest result in the whole audit
and they were produced *by the gate catching its own false passes*:

| Check | Naive reading | What the gate says |
|---|---|---|
| **A1** no invented producer identity | "PASS — no producer field, so nothing invented" | **VACUOUS.** There is no field to fabricate into. A1 becomes real only when an origin-bearing field exists **and is observed withholding** a `muxer_authored` value |
| **A5** codec ≠ encoder | "PASS — no encoder field to fuse with codec" | **VACUOUS.** The separation is unexercised, not demonstrated |
| **T5** codec recorded, encoder absent | "PASS — codec present, encoder absent" | **VACUOUS.** The encoder half is satisfied by the *absence of a subject* |

This is the same defect the audit found everywhere else, arriving through the verification apparatus instead
of through the contract: **a property that is trivially true because the thing it constrains does not exist
is not a property of the system.** A1 is the most alarming of the three, because "we never invent producer
identity" is the stage's headline claim and the current system satisfies it only by never having the
opportunity.

## H.2 — Discharge map: what each blocking check actually requires

Ordered by dependency, not by severity. The gate cannot be worked from the bottom up — A1 and T1 are both
blocked on the same missing capability, and T-R3b exists to unblock both.

| Check | Blocks on | Owner | Discharge requires | Part III ref |
|---|---|---|---|---|
| **T1**, **A1** (real pass) | an artifact carrying a genuine declaration | 2.3 (fixture) | Byte-level `©too` injection — R3 proved writing tags cannot produce one | §G.2.5 T-R3b |
| **T2**, **T4** | an `origin` attribute on the observation | 2.3 + §2.1 | The R3/R1 scope+origin model, applied to the draft | §G.2.4, §G.3.2 |
| **A2**, **A4**, **T3**, **T6**, **A12** | `SourceInfo.version` + `ProvenanceEntry.tool_version` | §2.1.15 → 2.15 | The carriers, which §2.1 v1.2 already specifies and no code implements | §G.6.2 |
| **A5**, **T5** (real pass) | an encoder field to separate from codec | 2.3 | Two distinct groups, per the R1/R3 split | §G.2.4, §G.3.3 |
| **A7** | an `evidence_refs` address grammar | §2.1 | The bounded grammar of §F.2-G13; free-form refs are not locations | §G.8 chain |
| **A8**, **T8** | failure states the stack can actually distinguish | 2.3 (vocabulary) + 2.15 (branch) | R4's state table with its reachability column; then the branch split | §G.5.2 |
| **A9** | absence of sentinel values | 2.3 + 2.15 | `"1:1"`, `"unknown"` retired for the frozen `ObservationState` | §G.4.3 |
| **A3** | `tool_version`/`model_version` on `ProvenanceEntry` | §2.1 → 2.15 | Same carriers as the A12 row | §G.6.3 |
| **T7** | a two-scope disagreeing fixture + conflict rule | 2.3 + §2.1 | `state=conflicting`, a §2.1 v1.3 candidate | §G.3.3 |
| **A10**, **A11**, **T9**–**T11** | §2.16.5–7 | **§2.16** | Nothing in 2.3. Held by design | §G.7.3 |

## H.3 — G17: held behind §2.16, and *not* implementable by stealth

**G17 must not be closed as part of 2.3, by any route.** The failure this part is guarding against is
specific and plausible: with 18 checks outstanding, the fastest-looking way to reduce the number is to
"implement" a spool or a file-descriptor path so that T9–T11 stop returning `HELD`. That would be worse
than doing nothing, for three reasons that the gate makes concrete:

1. **The mechanism does not exist to implement against.** §2.16.5–7 are unwritten. Any descriptor form or
   quota 2.3 invents is a *second* contract, incompatible with whatever §2.16 later freezes — the precise
   failure already carried as an `OPEN_DECISION` in §2.2's register (row 21, the `fd://<n>` form).
2. **`HELD` is the honest status, and the gate already excludes it from the blocking tally** so that §2.16's
   absence does not masquerade as 2.3's failure — *and* so that 2.3 cannot claim credit by simulating it.
   A `HELD` row that someone quietly converted to `PASS` would corrupt the tally in the direction of a
   premature freeze.
3. **Discharge must come from §2.16, not from 2.3's test suite.** When §2.16 lands, T9–T11 are written
   there against the real mechanism, and the gate's `HELD` rows become `PASS` because the subject appeared —
   not because 2.3 asserted it.

```text
CORRECT                                          FORBIDDEN
───────────────────────────────────────────────────────────────────────────────────────────────
A10/A11/T9–T11  =  HELD  (no subject)      vs.   2.3 "implements" a spool to make them pass
§2.16.5–7 land → tests written there       vs.   2.3 pre-empting §2.16's grammar
gate tally excludes HELD                    vs.   HELD silently reclassified as PASS
```

**Recorded invariant for this stage:** no commit touching spool, descriptor, or quota behaviour may be
attributed to Stage 2.3. If such a change appears in a 2.3 change set, it is out of scope by this rule.

## H.4 — The freeze gate, stated as a contract

Stage 2.3 becomes freezable when, and only when:

```text
GATE OPENS  ⟺  every check in _s23_verification.py reports PASS
              AND the 5 HELD rows have been discharged by §2.16, not by 2.3
              AND no VACUOUS-PASS or NOT-IMPLEMENTED remains
              AND python -m pytest -q is green
```

Each clause is load-bearing, and the third is the one that a paper freeze would fail:

| Clause | Prevents |
|---|---|
| every check PASS | declaring success on a subset ("9 of 12 tests pass") |
| HELD discharged by §2.16 | 2.3 closing §2.16's scope by simulation |
| no VACUOUS / NOT-IMPLEMENTED | the trivial-truth passes of §H.1.2 being counted as real |
| suite green | trading a working system for a satisfying document |

### H.4.1 Current verdict

```text
GATE: BLOCKED — 18 checks outstanding.
Stage 2.3 is NOT freezable. Part IV establishes the gate; it does not open it.
```

That is the correct and expected outcome of this phase. A gate that opened on its first run, immediately
after the pass that built it, would not be a gate.

## H.5 — What Part IV changed, and what it deliberately did not

| | |
|---|---|
| **Changed** | Added Part IV; adopted the four-way `origin` classification (`unavailable` added, `decoder_reported`/`probe_generated` merged into `probe_observed`) and rewrote the eligibility rule as a chain; built the executable verification gate and ran it; classified three previously-unnoticed false passes as `VACUOUS-PASS` |
| **Not changed** | `src/` — untouched, 25/25 green. No acceptance criterion. No §2.1 or §2.16 contract. Part I's audited baseline. G17 |
| **New finding** | The gate caught three `VACUOUS-PASS` results (A1, A5, T5) that Parts II–III had scored as satisfied. A1 is material: "no invented producer identity" currently holds because no producer field exists, not because the system withholds one |
| **Not claimed** | That the remediation is implemented. It is specified, and the gate that will judge it is built and currently refuses to open |

### H.5.1 Reproducibility

```text
script      _s23_verification.py        the executable freeze gate
evidence    _s23_verification.txt      first run: BLOCKED, 18 outstanding
command     python _s23_verification.py > _s23_v_run.log 2>&1
control     python -m pytest -q  ->  25 passed   (src/ untouched)
env         PyAV 18.1.0 | libavformat 62.12.102 | ffmpeg_version_info='8.1.2'

prior artifacts (Parts II–III evidence, unchanged):
  _s23_probe_experiment.py  -> _s23_out.txt        (73 lines)  freeze audit
  _s23_r3_probe.py         -> _s23_r3_out.txt     (183 lines) R3/R1/R2/R4 measurements
  _s23_fixtures/           (6 artifacts)

limitations of the gate itself, stated so it is not over-trusted:
  (a) it checks the properties 2.3 owns, not the whole contract;
  (b) SPEC-* rows are text matches and prove only that wording is present,
      never that behaviour follows — which is why they are labelled and why
      every behavioural check is independent of them;
  (c) A9 is approximated by a sentinel-value scan; a subtler inference that
      produces a well-formed non-sentinel value would not be caught;
  (d) T12's reproducibility check is currently vacuous by construction, and is
      marked NOT-IMPLEMENTED rather than PASS for that reason.
```

The gate is the deliverable. When §2.16 and §2.15 land, re-running it is the whole of the freeze
procedure, and its verdict — not this document's completeness — decides Stage 2.3.

## H.6 — Remediation cycle 1: the producer-value path

> **Status: executed. One finding discharged, and only the parts it actually discharges.**
> The gate remains `BLOCKED`. This cycle demonstrates that the procedure works; it is not evidence of
> progress toward a freeze.

### H.6.1 What was changed, and what was deliberately not

| Changed | Not changed |
|---|---|
| `ContainerInfo.producer_declarations` — new optional field (additive, minor bump) | `SourceInfo` — **untouched**. `version` is a §2.1.15 carrier owned by 2.15 |
| `ObservationOrigin` + `ProducerDeclaration` models | `ProvenanceEntry` — **untouched**. `tool_version`/`model_version` likewise |
| `Ingestor._extract_producer_declarations()` — R1 scopes, R2 fold, R3 origin | `ingest()` signature, pipeline, decoder, analyzer |
| 9 behavioural tests in `tests/test_producer_declaration.py` | `ObservationState` — still the frozen four members |

The single sentence governing the scope: **give the contract a producer-value path that classifies
authorship instead of silently dropping the value.** Everything else was out of scope.

### H.6.2 What the cycle did *not* claim

It did not touch `SourceInfo.version`, so **A2, A3, A4, T3, T4, T6, T12 remain exactly where they
were** — `NOT-IMPLEMENTED` or `FAIL`. It is tempting to read "the version carrier is now populated by
the right rule" as discharging them. It does not: with no carrier the eligibility rule has nothing to
bind to, and a rule that constrains nothing has not been demonstrated.

### H.6.3 Gate movement — and the two defects found on the way

```text
                  before        after        delta
  PASS                8            11          +3
  VACUOUS-PASS        3             1          -2
  FAIL                6             6           0
  NOT-IMPLEMENTED     9             8          -1
  HELD                5             5           0    (G17 untouched)
  ────────────────────────────────────────────────────
  BLOCKING           18            15          -3
```

**A1 moved `VACUOUS-PASS → PASS`, demonstrated:**

```text
2 producer-related value(s) obtained, origins=['muxer_authored', 'probe_observed'];
1 muxer-authored value(s) REPORTED VERBATIM and withheld from SourceInfo.version
(which is absent). The withholding is demonstrated, not vacuous
```

That is the discharge the earlier parts specified: *no attack surface ≠ demonstrated protection*. There is
now an attack surface — a real `Lavf62.12.102`, present in the bytes and visible to the contract — and the
implementation reports it verbatim, attributes it to the muxer, and refuses to promote it. T2 (`PASS`) and
T5 (`PASS`, rewritten from a vacuity check into a real separation check) moved with it.

**Defect 1 — the gate's own A1 check was a stale proxy.** It asked "is there a field named `encoder`?",
which returns VACUOUS forever regardless of the truth. Left alone, the cycle would have produced no
movement and the tally would have been *misleading rather than merely unhelpful*. The check was rewritten
to ask the real question, and — critically — it now goes **red** if a muxer-authored value is ever
promoted:

```python
elif muxer and promoted:
    record("A1", ..., FAIL, "a muxer-authored value was PROMOTED to SourceInfo.version")
```

A check that cannot go red on the failure it exists to catch is not a check.

**Defect 2 — an enum `str()` bug that silently matched nothing.** The rewritten check first reported A1
as `NOT-IMPLEMENTED` while its own evidence listed `muxer_authored`. Cause: on Python 3.11+, `str()` on a
`str, Enum` member yields `ObservationOrigin.MUXER_AUTHORED`, not `muxer_authored`, so
`str(d.origin).endswith("muxer_authored")` was always false. Recorded because it is the same failure shape
the audit is about — a lookup that finds nothing and reports it as an absence — and it was found only
because the gate was **run** rather than reasoned about. Fixed by comparing `origin.value` explicitly
(`_origin_value()`).

**Also surfaced by the tests:** Matroska's `TITLE` reaches this code already lower-cased, because the
*demuxer* folds it before this layer runs, while `ENCODER` arrives upper-cased. So R7's "verbatim" means
*verbatim as the mechanism reported it*, not as the authoring tool spelled it. The test now states that
rather than asserting a guarantee the approved mechanism cannot make.

### H.6.4 The next cycle, and what it must not assume

| Next target | Blocks on | Note |
|---|---|---|
| **A5** | — | **Discharged** by §2.1.16 + a re-measured check (§V.7.1). Was `VACUOUS-PASS`: the check was a field-name proxy |
| **A7** | the `artifact:` locator cannot be produced | **2.3.** Grammar exists (§2.1.17); route is the R-a/R-b decision record (§V.7.6) |
| **A8 / T8** | R-2 on-group failure recording | **Discharged** — 2.15 implemented it; see §V.7.4 |
| **A9** | the `"1:1"` / `"0:1"` sentinels | **Discharged** — `stage2_source_description` v1.1 + v1.2; see §V.7.3 |
| **A2 / A3 / A4 / T3 / T4 / T6 / T12** | `SourceInfo.version` + `ProvenanceEntry.tool_version` | **2.15.** Seven checks, one carrier decision — the largest single win available, and entirely outside 2.3 |

Two things the next cycle must not do:

1. **Do not upgrade A5 by loosening its check.** Under-claiming is safe; over-claiming is the failure
   this apparatus exists to prevent. A5 stays `VACUOUS` until the conflict fixture exists, even though the
   structural separation cycle 1 introduced would make a sloppier check pass today.
2. **Do not let G17's `HELD` rows move.** They are excluded from the tally, and converting one to `PASS`
   to shrink the number would fabricate a §2.16 discharge. The tally arithmetic is fixed in code precisely
   so this cannot be done by hand.

### H.6.5 Cycle 1 reproducibility

```text
change    src/videotemplate/models/source_description.py
            + ObservationOrigin, ProducerDeclaration, ContainerInfo.producer_declarations
          src/videotemplate/ingestion/ingestor.py
            + R2 canonical-key rule table, R3 muxer prefixes,
              _extract_producer_declarations(), _classify_producer_origin()
          tests/test_producer_declaration.py
            new file, 9 behavioural tests (no pre-existing test modified)

gate      python _s23_verification.py  ->  _s23_verification.txt
tests     python -m pytest -q  ->  34 passed  (25 pre-existing + 9 new)
verdict   GATE: BLOCKED -- 15 outstanding  (was 18)
held      A10, A11, T9, T10, T11  -- unchanged, still §2.16's
unchanged SourceInfo, ProvenanceEntry, ObservationState, pipeline, decoder, analyzer
```

### H.6.6 Standing instruction carried into cycle 2

A smaller blocking count is not progress. **15 outstanding is not "better than 18" in any sense the
freeze cares about** — three checks changed status because something was demonstrated, not because the
document grew. If cycle 2 reaches zero outstanding by loosening checks rather than discharging them, the
gate has been defeated and the correct action is to discard cycle 2, not to accept it.




## H.7 — Remediation cycle 2: the version carriers (§2.1.15 v1.2, owned by 2.15)

> **Status: executed. The gate moved 15 → 8 blocking. Stage 2.3 remains `BLOCKED`, and the
> remaining 8 are not 2.3's to close.**

### H.7.1 A correction to the cycle brief, made because the owning contract disagreed

The cycle-2 brief specified, at step 5, *"Test missing artifact-declared version → `"unknown"`
behavior where the owning contract requires it."* Reading §2.1.15 before implementing
(`stage2_1_contract_boundary.md:690-698`) shows the owning contract requires the **opposite**:

> **R3:** "`SourceInfo.version` is **OPTIONAL / UNAVAILABLE-ALLOWED** … Omission then means 'the
> object declares none'. **Never `""`, never `"unknown"`**, never a Builder version substituted
> for a missing source tag — that is fabrication, and it is the failure mode this field's naming
> must not invite."

`"unknown"` is permitted on `tool_version` only (**R4**), and only when introspection is genuinely
impossible. So the implementation **omits** the key. The qualifier *"where the owning contract
requires it"* is what makes this unambiguous: the contract does not require it here, and where a
proposed step and the owning contract disagree, the contract wins. This is recorded rather than
silently reconciled because it is the first time a remediation instruction was corrected by the
specification it was meant to implement — and it is exactly the class of drift this audit exists
to catch, aimed at the remediation process itself rather than only at the draft.

### H.7.2 What was changed

| Changed | Not changed |
|---|---|
| `SourceInfo.version` (§2.1.15 R3, `exclude_if` so absence omits the key rather than emitting `null`) | `ObservationState` — still four frozen members |
| `ProvenanceEntry.tool_version` / `.model_version` (R1/R2/R4, same omission rule) | The pipeline, decoder, analyzer, `ingest()` signature |
| `producer_identity()` — the single introspection point **R9 requires** | Any producer's ad-hoc introspection: there is now exactly one |
| `tool_version` on both provenance entries the ingestor emits | `ProvenanceEntry.tool` — see H.7.5 |
| `Ingestor._declared_source_version()` — the R3 eligibility rule, bound to `origin` | Any new carrier, name, or sentinel value |
| 13 tests in `tests/test_version_carriers.py` (R1–R9, each independently failable) | The 25 pre-existing tests |

The eligibility rule, in code and in one line:

```python
if decl.origin is not ObservationOrigin.ARTIFACT_DECLARED:
    continue          # muxer self-description and probe-observed are ineligible
...
return best[1] if best else None   # None => key omitted, never "" / "unknown"
```

### H.7.3 Gate movement

```text
                  cycle 1      cycle 2      delta
  PASS                11           18          +7
  VACUOUS-PASS         1            1           0
  SPEC-ONLY            0            0           0
  FAIL                 6            4          -2
  NOT-IMPLEMENTED      8            3          -5
  HELD                 5            5           0    (G17 untouched)
  ────────────────────────────────────────────────────
  BLOCKING            15            8          -7
```

Each of the seven is a behavioural demonstration, not a presence check:

| Check | Evidence now recorded |
|---|---|
| **A2** no version fabrication | `SourceInfo.version=None`, not a probe/library version, not a sentinel — and a value *was* available, so this is a withholding, not an absence |
| **A3** §2.1.15 vocabulary | `ProvenanceEntry` carries exactly `tool_version`/`model_version` |
| **A12** probe identity recorded | probe provenance `tool_version='18.1.0'`; **and** the `estimate` field's (`quality_score`) entry carries it, satisfying R1 |
| **A4** source vs builder distinct | artifact declares `'HandBrake 1.6.0'`; probe reports `'18.1.0'`; disjoint |
| **T4** no fabricated version | the key is **omitted from the dump** — a value was available and deliberately not written |
| **T6** probe version stays builder-side | `tool_version='18.1.0'` on provenance, and that string does **not** appear on `SourceInfo.version` |
| **T12** reproducibility | stable across runs **and** the producing build is recorded, so the contract is keyable |

A4 and T4 are worth pausing on. Both were previously "cannot be evaluated: neither carrier exists".
A4 now uses a genuine declaration (`'HandBrake 1.6.0'` at stream scope — the only route R3 leaves
open) to show the two slots are genuinely disjoint, which is the property the three-way version
confusion of G12/G19 was about.

### H.7.4 Three gate/test defects found, and one self-correction

**Defect 3 — `SPEC-ONLY` was not in the blocking set.** After cycle 2 landed the carriers, four checks
(A2, A3, A12, T6) reported `SPEC-ONLY` — and `SPEC-ONLY` was *excluded* from the tally. They were
silently not counting. That is precisely the escape hatch this gate exists to close, and it was in the
gate itself. `SPEC-ONLY` is now blocking: presence is not proof. It currently reports zero rows,
because every check that used it was rewritten into a real behavioural test — but the hole is closed
rather than left for the next cycle to use.

**Defect 4 — T12's verdict contradicted its own evidence.** The first re-run printed `T12 PASS` above
the text *"stability is not reproducibility: no probe identity is recorded"* — a stale message
asserting the opposite of the verdict it was attached to. A gate whose prose can contradict its own
status is untrustworthy at any tally. The check now requires **both** stability *and* a recorded
producing identity, and its message is generated from the same values the verdict is computed from, so
the two cannot disagree again.

**Defect 5 — my own R5 test asserted the wrong rule.** The cycle-2 cache-gate test initially
implemented matching as plain equality. §2.1.15 R5 says an `"unknown"` on either side is a
**non-match** forcing recompute. The test was wrong, not the contract. It now implements the rule, and
states plainly that no cache component exists in the repository — so it records the rule without
pretending to discharge a cache conformance obligation.

The common shape of all three: **each was found by running the thing, not by reasoning about it.**
Defects 3 and 4 existed only in the measurement apparatus, and they were both biased in the direction
of *overstating* how close the stage was to a freeze.

### H.7.5 Recorded, not fixed: `ProvenanceEntry.tool`

§2.1.15's field tree lists `tool` under `ProvenanceEntry` as *"(existing — name only, anti-dump rule)"*
(`stage2_1_contract_boundary.md:662`). **It does not exist in the code.** The v1.2 migration table
(`:714-715`) scopes the amendment to `tool_version`/`model_version`/`version` only, so `tool` was
neither added nor dropped by the amendment — the spec and the repo simply disagree about what is
"existing". Cycle 2 did **not** add it: that is outside the amendment's scope, and adding a field
because a document implies it already exists is precisely the drift this audit exists to prevent.
Logged as a repo/spec discrepancy for §2.1 to resolve, not silently reconciled here.

### H.7.6 What cycle 2 did not mark, and why

| Not marked | Reason |
|---|---|
| **A5** still `VACUOUS-PASS` | Unchanged and deliberately so. Its check is still a field-name proxy, and cycle 2 did not build the codec-vs-producer conflict fixture A5 actually requires |
| **T3** still `NOT-IMPLEMENTED` | The carrier and the rule both work, but no artifact can be given a surviving container-scope declaration. T3 is blocked on **T1's byte-level fixture**, not on code — and the gate says exactly that rather than blaming the carrier |
| **A7, A8, A9, T8** still `FAIL` | Untouched. A successful carrier change is not a reason to reconsider a failure that contradicts the contract |
| **G17 / A10 / A11 / T9–T11** still `HELD` | Unchanged. Excluded from the tally by design, in code |
| Any `HELD` → `PASS` conversion | Would fabricate a §2.16 discharge. Not done, and not available to do by hand |

The dependency chain now stands as the architecture intended:

```text
Stage 2.3          establishes   observation · scope · origin · eligibility
Stage 2.15/§2.1.15 provides     SourceInfo.version · ProvenanceEntry.*_version
downstream         consumes      caching · reproducibility · provenance consumers
```

Stage 2.3 did not create a competing carrier, and it did not reach across into §2.16.


## H.8 — Remediation cycle 3: the T-R3b fixture, and a correction to my own report

> **Status: executed. 8 → 6 blocking. Stage 2.3 remains `BLOCKED`.**

### H.8.1 Correction: my "nothing is 2.3-closable" claim was wrong

§H.7.7 ended with *"not one of the eight is closable by Stage 2.3 alone."* **That was an
overstatement, and it was mine.** The register it drew on (`§F.6`) assigns **G20 to 2.3**
(`SPECIFICATION_CHANGE_REQUIRED` + `IMPLEMENTATION_MIGRATION_REQUIRED`), and T-R3b to 2.3 as a fixture.
So the fixture was 2.3's own deliverable all along, and T1/T3 were waiting on work sitting in 2.3's own
column. I mis-classified a fixture gap as an external dependency — the exact category error this method
exists to prevent, committed by the auditor rather than by the system under audit.

The honest statement is narrower: of the eight, **two were 2.3's**; the other six were not.

### H.8.2 What was built

`_s23_fixture_inject.py` — an mp4 `moov/udta/meta/ilst/©too` atom injector, plus six tests
(`tests/test_fixture_inject.py`). The payload layout was **read from the real muxer output**, not assumed:

```text
base payload   b'\x00\x00\x00\x1d' b'data' b'\x00\x00\x00\x01' b'\x00\x00\x00\x00' b'Lavf62.12.102'
               size=29            'data'   type=UTF-8      locale=0          the value
```

For a longer value (+13 bytes) the build repairs the `©too`/`ilst`/`meta`/`udta`/`moov` size chain and
every `stco`/`co64` entry pointing past the end of `moov`.

```text
  base too atom   depth=4 size_field=37 atom_size=37
  delta           13 bytes
  chunk offsets   0 patched        (mdat precedes moov here, so none needed shifting)
  container meta  {..., 'encoder': 'HandBrake 1.6.0 2023041600'}
  frames decode   10 base / 10 injected
  frames identical True
  VERDICT         OK
```

### H.8.3 Three bugs found in the builder — and the fourth failure that is really the story

Every one produced a file that **opened successfully** and reported *plausible* metadata:

1. **Wrong payload field order.** Emitted `[type][size][data][value]` and omitted the locale. Result: no `encoder` key at all.
2. **`box_start = pos - header`.** The size field lives at `pos`; this patched eight bytes early and corrupted the enclosing atom.
3. **Only the leaf was resized.** The ancestor chain was never recorded, so `moov` was left shorter than its contents.

Bug 3 caused the persistent symptom; 1 and 2 masked it. But the one worth recording is not any of the
three — it is a fourth shape, and it is the shape this whole audit is about:

> The first working-looking version spliced the replacement payload over `buf[pos:pos+size]` — the whole
> atom **including its 8-byte header**. That deleted the size field and the `©too` type. The result was
> **a file that opens, whose brand keys read correctly, and whose encoder tag has silently vanished.**

A loss that leaves behind a plausible-looking record — reproduced accidentally inside the very tool
written to repair it. It was caught only because `verify()` asserts the declaration reads back
**verbatim** rather than asserting the file merely opens. Had the test been "the file opens", the
fixture would have shipped broken and T1/T3 would have read `NOT-IMPLEMENTED` for ever with no clue why.

### H.8.4 The integrity check that metadata cannot provide

A wrong chunk-offset repair yields a file that opens, reports the right tags, and decodes to garbage.
So this fixture's correctness is a claim about **decoded picture data**, and is tested that way:

```text
  frames decode   10 base / 10 injected
  frames identical True
```

`test_injected_file_is_not_corrupt` decodes both files fully and compares plane data. No metadata
assertion could have distinguished the correct fixture from the broken one.

One test is written to **retire** the injector rather than protect it:
`test_no_declaration_survives_by_being_written_as_a_tag` asserts R3's finding still holds, and its
failure message says the injector is obsolete and should be replaced. A test that can only ever pass is
not a regression test; this one encodes a falsification condition.

### H.8.5 Gate movement

```text
                  cycle 2      cycle 3      delta
  PASS                18           20          +2
  VACUOUS-PASS         1            1           0
  FAIL                 4            4           0
  NOT-IMPLEMENTED      3            1          -2
  HELD                 5            5           0
  ────────────────────────────────────────────────────
  BLOCKING             8            6          -2
```

| Check | Evidence |
|---|---|
| **T1** `PASS` | *"an artifact declaring 'HandBrake 1.6.0 2023041600' was read back verbatim as `encoder='HandBrake 1.6.0 2023041600'` with `origin=artifact_declared` at `scope=container`. This is the first fixture in the project on which a producer declaration demonstrably survives to probe time."* |
| **T3** `PASS` | *"carried verbatim (R7): not split into name/version, no release derivation, and it differs from the probe's '18.1.0'"* |

T1 and T3 are now **positive demonstrations on a real declared artifact** — the first time any
producer-identity check in this project has had one to run against.

### H.8.6 The six that remain, and the one forward-looking result

| Still blocking | Owner | Why cycle 3 could not move it |
|---|---|---|
| **A5** | §2.1 (v1.3) + fixture | The injector *can* now build a two-scope conflicting fixture, but `state=conflicting` does not exist in the frozen `ObservationState`, so the check would still be unevaluable |
| **A7** | §2.1 | `evidence_refs` address grammar — §2.1's to write |
| **A8, T8** | 2.3 spec + 2.15 code | R4's reachability table, then the branch split. Still real failures |
| **A9** | 2.3 + 2.15 | retiring the `"1:1"` sentinel |
| **T7** | §2.1 | as A5 — now blocked on the state, not the fixture |
| **G17** | §2.16 | unchanged, `HELD` |

One vacuous (A5), four failing (A7, A8, A9, T8), one not-implemented (T7) — and **not one of the six is
closable by Stage 2.3 implementation alone.** That claim is now made with the register behind it rather
than by assertion, and it is true.

**The forward-looking result is T7.** Its fixture blocker is gone; the same injector produces a
two-scope disagreeing artifact in one call. The moment §2.1 v1.3 adds `conflicting`, T7 and A5 are
fixture-ready and their remaining cost is the state value alone.

### H.8.7 Cycle 3 reproducibility

```text
change    _s23_fixture_inject.py            new: the T-R3b atom injector
          tests/test_fixture_inject.py      new, 6 tests (incl. a retirement condition)
          _s23_verification.py              T1/T3 now run against the real fixture; an `av`
                                            UnboundLocalError was fixed by hoisting the import
                                            to the top of the function (T3 and T6 both need it)
          _s23_fixtures/declared_real.mp4  generated, frame-verified

gate      python _s23_verification.py  ->  6 outstanding (was 8)
tests     python -m pytest -q  ->  53 passed  (25 pre-existing + 9 + 13 + 6)
verdict   GATE: BLOCKED -- 6 check(s) not satisfied
```

### H.8.8 Standing instruction, unchanged

**6 outstanding is not a number to optimise.** Three cycles have now run, and in each the tally fell
only where something was demonstrated; in every cycle, checks that were stale were rewritten to be
**stricter** and then allowed to pass on evidence. Cycle 3 additionally corrected the auditor's own
ownership claim rather than letting a convenient version stand. If a later cycle reaches zero by
loosening, the gate has been defeated and that cycle is discarded.



### H.7.7 Cycle 2 reproducibility

```text
change    src/videotemplate/utils/confidence.py
            + producer_identity()          (R9, the single introspection point)
            + SourceInfo.version           (R3, omitted when absent)
            + ProvenanceEntry.tool_version / .model_version   (R1/R2/R4)
          src/videotemplate/ingestion/ingestor.py
            + _declared_source_version()    (R3 eligibility, bound to origin)
            + tool_version on both provenance entries
          tests/test_version_carriers.py     new file, 13 tests (R1–R9)
          tests/test_producer_declaration.py one test EXTENDED, per its own standing
                                             instruction to assert the rule rather
                                             than the carrier's absence

gate      python _s23_verification.py  ->  8 outstanding (was 15)
tests     python -m pytest -q  ->  47 passed  (25 pre-existing + 9 + 13; none broken)
verdict   GATE: BLOCKED -- 8 check(s) not satisfied
```

The eight that remain are: **A5** (vacuous), **A7**, **A8**, **A9**, **T8** (fail), **T1**, **T3**,
**T7** (not implemented) — plus the five held.

> ⚠️ **Corrected in cycle 3 (§H.8.1).** The sentence that followed here originally read *"Not one of the
> eight is closable by 2.3 alone."* **That was an overstatement.** Two of the eight — **T1 and T3** — were
> blocked on **G20's fixture, which §F.6 assigns to 2.3**. They were closed in cycle 3. The accurate
> statement is: six were external, and two were the stage's own.

### H.7.8 Standing instruction carried into cycle 3

Unchanged, and now better supported: **8 outstanding is not a number to optimise.** The cycle-2 tally
fell because capabilities were demonstrated, not because any check was relaxed — and where checks *were*
stale (A1, A2, A3, A4, A6, T2, T5, T6, T12) they were rewritten to be **stricter** and were then
allowed to pass on evidence. Had they been left alone, the gate would have *understated* progress; had
they been loosened, it would have overstated it. Neither happened.

If cycle 3 reaches zero by loosening rather than discharging, the gate has been defeated and cycle 3
is discarded.

## H.9 — Final ownership / closure audit (no new implementation)

> Purpose: verify every remaining item against the **register**, not against the narrative that has
> accumulated around it. Cycle 3 already produced one routing error by reasoning from prose (§H.8.1),
> so this pass re-derives each owner from `§F.6` and from the code. It changes no implementation and
> adds no architecture.

### H.9.1 The audit table — owners read from `§F.6`, not inferred

| Item | State | Register row | **Recorded owner** | External dependency | 2.3 action |
|---|---|---|---|---|---|
| **A5** | `VACUOUS-PASS` | G10 (`2.3 / §2.1`) + G15 (`2.3`) | **multi-owner** | §2.1 v1.3 `state=conflicting` | **Hold.** Fixture capability now exists; the state value does not |
| **T7** | `NOT-IMPLEMENTED` | G13 (`§2.1`) | **§2.1** | `conflicting` state value | **Hold.** Its fixture blocker is gone; the state is all that remains |
| **A7** | `FAIL` | G13 (`§2.1`) | **§2.1** | `evidence_refs` address grammar | **Consume only.** 2.3 writes nothing here |
| **A8** | `FAIL` | **G18 (`2.3`)** | **2.3** | none | ⚠️ **2.3-OWNED AND NOT DONE** — §H.9.2 |
| **T8** | `FAIL` | **G18 (`2.3`)** | **2.3** | none | ⚠️ **2.3-OWNED AND NOT DONE** — §H.9.2 |
| **A9** | `FAIL` | G10 (`2.3 / §2.1`) | **multi-owner** | §2.1 contract typing — §H.9.3 | **Hold** on the type change; the call-site half is mechanical |
| **G17** | `HELD` | G17 (`§2.16`) | **§2.16** | spool / descriptor / quota | **Hold.** Unchanged; excluded from the tally in code |

### H.9.2 Routing correction #1 — A8 and T8 are **2.3's**, and remain open

My last report routed A8/T8 as *"2.3 spec + 2.15 code"* and then listed them among the six 2.3 cannot
touch. **The register does not say that.** `§F.6` row G18 records:

> owner **2.3** · class `SPECIFICATION_CHANGE_REQUIRED` + `IMPLEMENTATION_MIGRATION_REQUIRED` (`ingestor.py:66-77`)

So the finding is 2.3's, and its specification half — replacing §2.3.14's enumerated outcome list with
R4's reachability table (`§G.5.2`) — **has not been applied to the draft text.** That is a
**2.3-owned deliverable still outstanding**, and the largest one.

This is the same category of error as the T1/T3 mistake in cycle 3, in the opposite direction: there I
called 2.3's work external; here I called it external *after* listing it as multi-owner. Both came from
reading the surrounding prose instead of the register row.

### H.9.3 Routing correction #2 — A9 is blocked by a **type**, not by a value

I had described A9 as "retiring the `"1:1"` sentinel". The code says otherwise, and the difference
changes the owner:

```text
src/videotemplate/ingestion/ingestor.py:408
    sar_str = self._format_display_ratio(sar, fallback="1:1")
                             ^^^^^^^^^^^^^^^^^^^^^
    `_format_display_ratio` ALREADY takes an explicit fallback parameter, and
    tests/test_pipeline.py:181-185 exercises it with fallback="0:1".

src/videotemplate/models/source_description.py:114
    sample_aspect_ratio: str            ← REQUIRED, non-optional

docs/specs/stage2_source_description.md:47
    sample_aspect_ratio: string         ← the contract says string, not optional
```

**The sentinel exists because the type demands a string.** Passing `fallback=None` is not representable
— Pydantic would reject it. So A9 is not a one-line call-site change; it requires relaxing
`sample_aspect_ratio` to `Optional[str]`, a **contract-boundary change** in a document subordinate to
§2.1, therefore §2.1's to make and 2.15's to execute. My "2.3 + 2.15" routing was directionally right and
materially incomplete: it named the wrong blocker.

The generalisation worth keeping: **a sentinel value is usually a symptom of a type that cannot express
absence.** Retiring the value without retiring the type produces a different false absence.

### H.9.4 The premise behind the freeze recommendation does not hold as stated

Freezing on the basis of *"no unresolved 2.3-owned implementation work"* is accurate about
**implementation** and inaccurate about **specification**. Outstanding and owned by 2.3:

| Outstanding 2.3-owned work | Recorded at | Status |
|---|---|---|
| Apply R4's reachability table to §2.3.14 | `§G.5.2`, G18 | **not applied** |
| Apply R3 origin + eligibility to §2.3.4/.7/.9/.11/.13 | `§G.2.4`, G12/G14/G15 | **not applied** |
| Apply R1 scope + precedence to §2.3.7 | `§G.3.2` | **not applied** |
| Apply R2 fold + miss-reporting to §2.3.7/.11 | `§G.4.3` | **not applied** |
| Apply R5 three-slot rule to §2.3.2/.15 | `§G.6.2` | **not applied** |
| Close G9 and G11 | `§F.1`, register | **not applied** |

This is the work `§G.10.1` itself sequenced as "next pass, steps 1–2" and then explicitly deferred.
**It is why Stage 2.3 is not ready to be frozen as a document**, independent of every external
dependency. Freezing now would freeze a draft whose own remediation is unwritten — precisely the
paper-freeze failure mode `§H.0.1` was written to prevent.

So the correct status is **not** "blocked by external contracts". It is:

> **Stage 2.3 — BLOCKED BY EXTERNAL DEPENDENCIES (§2.1 ×3, §2.16 ×1) *AND* BY 2.3'S OWN UNFINISHED
> SPECIFICATION REVISION (§2.3.2/.4/.7/.9/.11/.13/.14/.15).**

> ⚠️ **First half DISCHARGED by Part V.** The specification revision named above was completed in the
> §V amendment pass: all nine clauses restated, G9 and G11 closed. **The second half — the dependency
> clause — was never discharged and is not 2.3's to discharge.** The statement is retained rather than
> deleted because the split it records is the finding: 2.3 owed the specification work and has now paid
> it; the dependency work was never 2.3's. The current status of record is at the head of this document.

The external dependencies cannot be cleared by 2.3. The specification revision can, and must, before the
document is frozen. The gate stays `BLOCKED` either way — and must not be forced to `PASS`.

### H.9.5 What this audit does not change

| Unchanged | Why |
|---|---|
| **A5 = `VACUOUS-PASS`** | `conflicting` does not exist. The fixture capability now exists and is deliberately **not** rebuilt |
| **`conflicting` not added in 2.3** | `ObservationState` is §2.1's frozen vocabulary; adding a member for 2.3's convenience would edit a closed contract. It must arrive as a §2.1 v1.3 controlled amendment |
| **The four-origin model** | `artifact_declared` · `muxer_authored` · `probe_observed` · `unavailable` — unchanged; the destination eligibility rule stays separate from `origin` |
| **The omission rule** | Declared → `SourceInfo.version` verbatim; undeclared → **key omitted**. Never `null` / `""` / `"unknown"` / builder version. Carried by 13 R1–R9 tests and the gate's T4 |
| **The fixture injector** | Retained. `test_no_declaration_survives_by_being_written_as_a_tag` is the recorded retirement test and **has not** fired — the finding that justified the injector still holds, so retiring it now would discard a permanent regression net |
| **G17 `HELD`** | Unchanged, fenced, excluded from the tally in code |
| **`src/`** | Untouched in this pass; 53/53 green |

### H.9.6 Audit verdict

```text
6 gate-blocking items
  ├── 3 are §2.1-owned, and two of them (A5, T7) collapse into ONE v1.3 amendment
  │     A5 · T7 · A7
  ├── 1 is multi-owner, blocked on a §2.1 TYPE change rather than a value change
  │     A9
  ├── 2 are 2.3-OWNED and NOT DONE
  │     A8 · T8  — the §2.3.14 reachability table is not yet in the draft
  └── G17 is §2.16's and HELD

plus 5 further 2.3-owned specification edits outstanding from §G.10.1
```

**No new implementation cycle is warranted.** The two items 2.3 owns outright (A8, T8) are
*specification* work — the same kind as the five `§G.10.1` edits, under the same register. The other four
genuinely belong elsewhere, and two of them collapse into a single §2.1 v1.3 amendment that is cheap to
write and unblocks two checks at once.

The registered prerequisite for the next move is therefore **§2.1 v1.3** — and, in parallel and under
2.3's own ownership, the draft-text revision. Both are specification passes. Neither requires a further
implementation cycle, and neither should be started before the other is written down.








---

## V.2 — §2.3.12 Metadata States *(supersedes the clause at line 253; priority 2)*

The draft defines four states — Present, Absent, Unavailable, Invalid. Three of those are renamed
duplicates of the frozen §2.1.4 Dimension B vocabulary, and `invalid` does not exist in it. The frozen
`uncertain` — the exact home of §2.3.13's conflict — is missing. 2.3 may not re-cut §2.1.4.

```text
§2.3.12 — Metadata states

Observation states are EXACTLY the frozen §2.1.4 Dimension B set:
    extracted | absent | uncertain | unavailable
2.3 defines no additional state member. `invalid` is DELETED: no reachable producer
distinguishes it from `unavailable` (V.1.1), and a value that cannot be parsed is
`uncertain`, not a new state.

    absent       the Builder checked; the property does not exist in this source
    unavailable  the Builder could not determine the value
    uncertain    evidence exists; the Builder cannot establish the value confidently

R-S1  absent is a positive assertion; unavailable is a capability statement. They are
      never interchangeable, and neither is ever a substitute for a null group.
R-S2  Neither is ever a sentinel VALUE. A field whose type cannot represent absence
      must have its type corrected by its owning contract, not papered over with a
      string — see V.6 (the A9 type boundary).
```

**R-S2 is the amendment that changes §2.3.10's fate.** The draft's "these states must not silently
collapse into one another" is correct, and it is now backed by the type rule that makes it enforceable.

---

## V.3 — §2.3.4/.5/.6/.7 Container, Codec, Encoder, Version *(priorities 3)*

### V.3.1 What changes

| Clause | Draft's defect | Restated rule |
|---|---|---|
| **§2.3.4** Container | treats `container = MP4` as a clean fact; the probe actually reports the family list `"mov,mp4,m4a,3gp,3g2,mj2"` and `"matroska,webm"` | Container identity is recorded **verbatim as the mechanism reports it**, with the demuxer's family list retained. A family list is never reduced to a guess. Reduction to a short name belongs to the stage that owns container naming, and is a registered method id, not an inline table |
| **§2.3.5** Codec | "or otherwise directly evidenced under an approved contract" — names no contract | That phrase is **deleted**. Codec identity never establishes encoder identity. There is no "otherwise" path |
| **§2.3.6** Encoder | one field, four meanings; `encoder_tag` is a second carrier | Split into two groups that are never merged: **`codec_observation`** (mechanism = decoder, scope = stream) and **`producer_declaration`** (mechanism = tag reader, scope = container **and** stream). `encoder_tag` is **deleted** — it is a second carrier, which §2.3.2 forbids |
| **§2.3.7** Version | "Case A / Case B" with a two-field name+version split | Restated as the origin + eligibility rule below |

### V.3.2 The origin rule (supersedes §2.3.7's two cases)

```text
§2.3.7 — Producer declarations: origin, scope, and eligibility

Every producer-related observation carries (scope, origin):

  scope   ∈ { container, video_stream, audio_stream, other }
          audio_stream and other are RECORDED but never authoritative for a
          container-level group.

  origin  ∈ { artifact_declared,   a declaration by the artefact's producing tool
             muxer_authored,      the writing stack describing ITSELF
             probe_observed,      reported by the probe mechanism (e.g. a codec name)
             unavailable }        no value was obtained; no author can be attributed

ELIGIBILITY (destination rule, deliberately separate from origin)
  SourceInfo.version is populated ONLY from origin = artifact_declared.
  muxer_authored values are reported verbatim, attributed to the muxer, and are
  never promoted. probe_observed never populates a producer field. unavailable
  populates nothing.

AUTHORSHIP IS NOT PRESENCE
  A value physically present in the artefact is not a declaration. Measured: the
  mp4 '©too' atom and Matroska's MuxingApp/WritingApp contain 'Lavf62.12.102' in
  EVERY FFmpeg-muxed file, including files whose authoring tool declared something
  else — and the authoring tool's value is DESTROYED at write time, not overwritten.
  The string names the MUXER. Classifying it as a declaration would fabricate a
  producer identity, which is the failure this stage exists to prevent.
```

**§2.3.7's Case A/B split is deleted, not amended.** A name+version split requires parsing one opaque
tag string, which §2.1.15 R7 forbids: real values are `Lavf62.12.102` (muxer), `HandBrake 1.6.0 2023041600`
(name + release + nightly build), `x264 - core 164 r3106` (a build string with no single "the version").
The declared string is carried **verbatim**; any structured parse is optional, additive, and requires a
**registered** rule id. No release-name derivation: `Lavf62.12.102 → "FFmpeg n8.1"` would need a

---

## V.4 — §2.3.11 Normalisation and §2.3.9 Categories *(priorities 4, 6)*

### V.4.1 §2.3.11 restated — normalisation may not destroy the observation

The draft's principle ("may change representation but must not change identity") is kept. What is added
is the mechanism that makes it enforceable, plus a **reachability** requirement the draft lacks.

```text
§2.3.11 — Normalisation rules

R-N1  Key comparison is a case-insensitive ASCII fold against a REGISTERED canonical
      key set. The fold is a lookup convenience only.
R-N2  The verbatim original key and value are ALWAYS retained alongside the folded key,
      with the rule id recorded in transform_type (§2.1.15 R7).
R-N3  A key matching the producer pattern but absent from the canonical set is recorded
      as unrecognised. It is NEVER silently dropped.
R-N4  A normalisation MISS is reported. A miss may never degrade into "absent".
R-N5  Normalisation must be REACHABLE for every value the mechanism can produce. A
      canonicalisation that cannot map an observed value is a defect, not a fallback.

  Measured, and the reason R-N5 exists: the repo's long-name table covers 3 of the 4
  (name, long_name) pairs its own fixtures produce. 'On2 VP8' misses, and the miss is
  silent — no state, no warning, no difference in output.
```

R-N5 is the amendment's sharpest addition. The draft says "if the canonicalization rule is explicitly
defined" — which a lookup table is not. A rule that silently fails to apply produces the
confident-but-wrong record §2.3.0 warns about, and no acceptance criterion currently catches it.


---

## V.5 — §2.3.13 Conflict, §2.3.2/.8 Version Carriers, §2.3.1 Scope *(priorities 5, 7, 8)*

### V.5.1 §2.3.13 — adopt the existing conflict mechanism, do not invent one

The draft asks for "an explicit precedence rule" without providing one. **One already exists**, and 2.3
must adopt it rather than describe a new conflict object:

```text
§2.3.13 — Conflicting technical metadata

  On disagreement the conflict is preserved, never resolved by preference. 2.3 adopts
  §2.1.4 Dimension B step 4 ("evidence conflicts" -> uncertain, confidence <= 0.65),
  together with ValidationStatus.CONFLICT and ValidationInfo{rules_passed, rules_failed},
  all of which already exist in utils/confidence.py.

  Scope precedence for producer declarations (R1):
     1. artifact_declared   beats   2. muxer_authored
     3. probe_observed      is never a producer identity, whatever the scope
     4. unavailable         attributes no author and populates no identity field
  On disagreement BOTH values are retained and the group is marked; neither is silently
  preferred. Silent preference is the inference A9 forbids.

  DEPENDENCY (RESOLVED 2026-09-30): a dedicated `conflicting` state member was a §2.1 v1.3
  candidate. §2.1.16 has now established it as an additive Dimension B member, so 2.3
  marks the conflict through `ObservationState.CONFLICTING` and does NOT add a member to a
  frozen vocabulary. The interim rule below is SUPERSEDED and is retained only to show what
  was specified before the dependency existed:

    SUPERSEDED INTERIM (never implemented, now obsolete): 2.3 marks the conflict through the
    EXISTING `uncertain` state and ValidationStatus.CONFLICT.
```

**This is the boundary the register cares about, and it held.** `conflicting` was not pre-created by
2.3; §2.1.16 created it under §2.1's own authority. A5 and T7 moved to `PASS` only after that
happened **and** the checks were re-measured against the two-scope artifact (§V.7.1). The
`uncertain`-based interim route was never implemented, so there is no code to migrate.

### V.5.2 §2.3.2 / §2.3.8 — three version slots, no escape hatches

| Slot | Carries | Never |
|---|---|---|
| `SourceInfo.version` | The **source-side** producer string the artefact itself declares, from `origin=artifact_declared` only | a Builder version; the probe's own version; `""`; `"unknown"` |
| `ProvenanceEntry.tool_version` | The Builder-side software that produced the evidence | the source's encoder; the schema version |
| `ProvenanceEntry.model_version` | The Builder-side model behind an estimate, when one exists | the heuristic's name (that is `transform_type`) |

The draft's two escape hatches — *"as applicable"* and *"wherever required"* — are **deleted**:
`tool_version` is present on the producing provenance entry of **every** `estimate` field (§2.1.15 R1);
`model_version` only when a model produced the value (R2); `SourceInfo.version` only when the artefact
declares one, and is **omitted** otherwise (R3).

**The omission rule, stated as a freeze invariant:**

```text
  artefact declares a version   ->  SourceInfo.version = the declared string, VERBATIM
  artefact declares none        ->  the key is OMITTED from the serialised form

  Never: null · "" · "unknown" · a Builder version · the probe's own version
```

### V.5.3 §2.3.1 — scope restated to what 2.3 actually owns

The draft claims 24 scope items; §2.1.2's frozen ownership table assigns 14 of them to 2.4–2.9, 2.11 and
2.14. Restated scope, in 2.3's own words only:

```text
§2.3.1 — Scope (restated)

  IN SCOPE      container and stream technical observation; codec identification;
                producer-related tag observation with (scope, origin) classification;
                normalisation with verbatim retention; the metadata-state and
                probe-failure vocabularies as restated in V.1 and V.2; evidence-reference
                CONSUMPTION (the grammar itself is §2.1's).

  NOT IN SCOPE  canonical codec naming (2.4/2.5) · colour semantics (2.8) · geometry
                canonicalisation (2.10) · codec families (2.11) · duration authority
                (2.6) · quality scoring · any semantic interpretation.

  The draft's non-goals list is ADOPTED UNCHANGED. It was already correct; §2.3.22's
  boundary statement is the one clause in Part I that needed no amendment.
```

---

## V.6 — Two dependencies this pass records but cannot close

### V.6.1 §2.3.15 — evidence references: `§2.1`'s to write, not 2.3's

**Register row G13, owner `§2.1`.** 2.3 may consume the grammar and may not author it. The draft's
current exemplar is not an address at all — the only value the repo emits is `['container_probe']`, a
method word, identical for every group and every artefact, so it cannot fail any test.

```text
§2.3.15 — Evidence reference (restated as a stated dependency)

  2.3 REQUIRES, and does not define, an address grammar for evidence_refs. Owner: §2.1.
  Until it exists:
    - A7 and T7 are unevaluable, not passing;
    - existing free-form values remain legal and are classed `legacy`;
    - 2.3 emits no ref it cannot justify by an address.

  REQUIRED PROPERTIES (stated here so §2.1 inherits the constraint, not the work):
    R-E1 a value extracted from an artefact declaration carries at least one
         artefact-located ref;
    R-E2 a mechanism ref proves the METHOD, never the provenance of a value;
    R-E3 a ref is falsifiable: two different observations of the same artefact must be
         able to produce different refs.
```

**2.3 does not propose a grammar here.** Part II sketched one; it is recorded in §F.2-G13 as an
*illustrative* proposal, and it is explicitly **not adopted**, because adopting it would be 2.3 writing
§2.1's contract.

### V.6.2 A9 — a cross-boundary **type** dependency, not a value dependency

**Register row G10, owner `2.3 / §2.1`.** A9 was long described as "retiring the `"1:1"` sentinel", which
names the wrong blocker. The measured chain:

```text
  stage2_source_description.md:47   sample_aspect_ratio: string      <- the CONTRACT says string
  source_description.py:114         sample_aspect_ratio: str          <- REQUIRED, non-optional
  ingestor.py:408                   _format_display_ratio(sar, fallback="1:1")

  The helper ALREADY takes an explicit fallback parameter, and
  tests/test_pipeline.py:181-185 exercises it with fallback="0:1".

  => passing fallback=None is NOT representable: the field cannot hold absence.
  => the sentinel is not a value chosen in error; it is forced by a type that
     cannot express absence.
```

```text
  REQUIRED CHAIN (owned by §2.1 / stage2_source_description, executed by 2.15)
    sample_aspect_ratio  ->  must be able to represent absence
                         ->  Optional[str] (+ the §2.1.4 state that says 'absent')
                         ->  no fabricated fallback at the call site

  2.3 does NOT modify the owning document opportunistically. A9 stays FAIL until the
  owning contract accepts the representation, at which point the gate determines the
  result.
```

**The generalisation this dependency encodes, recorded because it will recur:** *a sentinel value is
usually a symptom of a type that cannot express absence.* Retiring the value without retiring the type
produces a different false absence — the field stops lying about geometry and starts lying about whether
geometry was ever observed.

---

## V.7 — Ownership re-statement, with the register as the only authority

The four external dependencies are named by their **recorded owner**, not by category. This corrects the
loose phrase "external dependencies" used in earlier parts, and it is applied because two routing errors
already came from exactly that broad categorisation (§H.8.1, §H.9.2).

| Item | State | **Recorded owner** | Class | 2.3 action |
|---|---|---|---|---|
| A5 | **`PASS`** — re-measured | §2.1 (§2.1.16 `conflicting`, now established) + 2.3 (precedence) | `DISCHARGED` | None. Gate evidence `_s23_verification.txt`: codec `h264` present, three producer values retained, codec string in a producer declaration = `False` |
| T7 | **`PASS`** — re-measured | §2.1 (§2.1.16 `conflicting`, now established) | `DISCHARGED` | None. Two-scope fixture: `{container: ['HandBrake 1.6.0 2023041600'], video_stream: ['SomeOtherTool 9.9.9']}`, `producer_state='conflicting'`, both values retained |
| A7 | `FAIL` | **§2.1** (G13, address grammar) | `SPECIFICATION_CHANGE_REQUIRED` | Consume only |
| A9 | **`PASS`** — re-measured | **§2.1 / `stage2_source_description`** (type, discharged by its Amendment Records v1.1 + v1.2) | `DISCHARGED` | None. Both ratio fields now express absence as `null`; zero string fallbacks remain in `src/` |
| A8 | **`PASS`** — re-measured | 2.3 spec (§V.1) · implementation 2.15 | `DISCHARGED` | None. R-2 implemented; see §V.7.4 |
| T8 | **`PASS`** — re-measured | as A8 | `DISCHARGED` | None. Same finding (G18), shared fixture |
| G17 | `HELD` | **§2.16** | `DOWNSTREAM_DEPENDENCY` | Hold. Fenced |

### V.7.1 A5 and T7 discharged by §2.1.16 — what actually changed, and what it did not

A5 and T7 moved because **§2.1 v1.3 established `conflicting`** (`stage2_1_contract_boundary.md` §2.1.16)
**and** because 2.3 then consumed it against a real two-scope artifact. Both conditions were required:

```text
A5   VACUOUS-PASS -> PASS    §2.1.16 supplied the state, AND the check stopped being a
                             field-name proxy. The old check could only prove "no
                             `encoder` field exists on VideoStreamInfo", which is an
                             unexercised obligation. It now runs the ingestor over a file
                             that HAS producer values and confirms `h264` does not enter
                             any of them.

T7   NOT-IMPLEMENTED -> PASS  §2.1.16 supplied the state, AND a two-scope fixture existed.
                             The check asserts all three clauses on the emitted contract:
                             two scopes disagree on the SAME canonical key, the group rolls
                             up to `conflicting`, and every disputed value survives.
```

Three things this discharge explicitly does **not** claim:

1. **It is not a §2.1 amendment closing a §2.1 item.** A5 and T7 are 2.3 gate rows; §2.1 owned the
   *vocabulary* they needed, not the rows themselves. §2.1.16 changed no 2.3 rule.
2. **The two-scope fixture is stream-scope-via-writer plus container-scope-via-injector.** A
   hand-injected `©too` in the track `udta` was tried first and read back as `encoder: ''` — a silent
   loss that would have produced a false conflict. Recorded because the broken route produced a
   *plausible-looking* empty value rather than an error.
3. **`SourceInfo.version` still receives ONE value under a conflict.** That is 2.3's registered
   destination precedence (§V.5.1) resolving the destination, not §2.1 adjudicating the conflict. T7
   asserts the conflict is *preserved in the record*; it does not assert the destination is
   multi-valued, and no test may move that decision into §2.1.

**Blocking count is now 4** (A7, A8, A9, T8) + 5 held. It was 6. The gate re-ran and produced
`_s23_verification.txt`; no row was edited to match the prose.

### V.7.2 A8 and T8 — the gate corrected against §V.1, before any 2.15 migration

**A8's previous `FAIL` was partly the check's fault, not the code's.** The old check required the two
malformed inputs ("128 ASCII bytes", "24-byte header") to produce *different* states. §V.1 deliberately
maps **both** to `UNREADABLE`, provides no state that separates them, and **R-3 forbids minting a new
`REJ_*` code**. Satisfying the old check would therefore have required violating the very contract it
was written to test — and it compared exception *message strings*, which §2.2 T7 forbids.

**Decision: correct the check, do not amend §V.1.** §V.1 is the closed contract; the apparatus was wrong.

The check now tests only what §V.1 specifies:

| Clause | Source | Status |
|---|---|---|
| No malformed input surfaces as a completed description | R-1 | **satisfied** |
| The failure is recorded **on the group**, not raised away | **R-2** | **FAILS — not implemented** |
| Nothing fabricated for an undescribable file | R-1 | satisfied |
| No new `REJ_*` code invented | R-3 | satisfied (no `REJ_*` exists in `src/` at all) |
| Both malformations share one `UNREADABLE` group | §V.1 | **not checkable yet** — reported `None`, never asserted on `None == None` |

**The tally did not move, and that is the honest result.** `PASS 22 · FAIL 4 · HELD 5`, `BLOCKED -- 4`.
Correcting the gate changed *why* A8 and T8 fail, not *whether*:

```text
  A8  before   FAIL  "malformed pair collapsed=True"      <- required a distinction §V.1
                                                          does not provide
  A8  after    FAIL  "failure recorded on the group per R-2=False"   <- the real defect
  T8  before   FAIL  hardcoded prose string
  T8  after    FAIL  measured: ingest() raised instead of recording UNREADABLE
```

**This is the whole point of correcting the check first.** Had 2.15 been routed against the old check, it
would have implemented an unobservable split between two malformed inputs — code satisfying a
specification that does not exist. Instead it now receives a single, contract-backed instruction:
*record the failure on the group.*

**Two obligations recorded for 2.15 before it starts** (not after, or they will be missed):

1. R-2 on-group recording. `ingestion_status` does not exist — `source_description.py:280` marks it
   "to be added in 2.15". No `REJ_*` code exists in `src/`. The whole ladder is 2.15's.
2. **The failure/success distinction must move to the STATE axis.** Today it holds only *accidentally*,
   because a failure raises and a success returns a contract. Once R-2 lands, both return contracts, and
   unless the state axis carries the distinction, `UNREADABLE` becomes confusable with
   `METADATA_ABSENT` — violating R-1, which holds both to be SUCCESS-with-different-meaning. Nothing in
   the current code preserves this.

**G18 remains ONE register finding** with two layers: specification half discharged by §V.1, implementation
half owned by 2.15 — after this correction. A8 and T8 are two check rows of that single finding and must
never be routed to two different owners.

### V.7.3 A9 — discharged, and the false green it briefly produced

**A9 went `PASS` at one point with a live sentinel still in the contract.** That result was not
discharged, and the row was re-blocked rather than banked. The sequence, in full:

```text
  1. stage2_source_description.md Amendment Record v1.1   sample_aspect_ratio -> Optional[str]
                                                        call site fallback=None
     gate  ->  A9 PASS                      <-- NOT TRUSTED. See (3).

  2. inspection found display_aspect_ratio='0:1' still emitted, and that the A9
     sentinel tuple ("unknown","1:1","N/A","none") contained no "0:1".
     => the row was green because it COULD NOT SEE the defect, not because the
        defect was absent.

  3. DECISION: correct the check, do not amend 2.3 (the A8 precedent, applied again)
     add "0:1";  re-run  ->  A9 FAIL, naming display_aspect_ratio='0:1' exactly
     **the FAIL is the evidence the corrected check actually SEES the defect**

  4. stage2_source_description.md Amendment Record v1.2   display_aspect_ratio -> Optional[str]
                                                        call site fallback=None
     gate  ->  A9 PASS   with zero string fallbacks remaining in src/
```

**The intermediate `FAIL` is the point.** A green row obtained while the check was blind proves
nothing; a red row from a strengthened check proves the check now covers its invariant.

**The check now audits its own completeness.** It tokenises `ingestion/ingestor.py` and reports every
string `fallback=` actually used in code, failing if one is outside its detectable set. So a future
`fallback="2:1"` produces *"the check cannot see a fallback src/ is actually using"* rather than
another silent green. **Tokenised, not regexed** — a plain regex also matched the comments documenting
this change, because the prose literally contains `fallback="0:1"` while describing the old behaviour.
A test caught that, in both the check and itself.

**Two things this discharge explicitly does not claim:**

1. **The absent-vs-unavailable distinction is still unresolved.** `_format_display_ratio` collapses
   *absent*, *unparseable shape*, *unparseable value* and *non-positive* into one `null`. At T1
   granularity there is no per-field `ObservationState`, so `null` means *"no usable value"*, not
   strictly *"declares none"*. Recorded as S-5 in v1.1 and carried forward unchanged by v1.2. **This
   is an observation-state question for §2.1 Dimension B, not a typing fix**, and it is deliberately
   not bundled here.
2. **A9 was not discharged by a document change.** It was discharged by two contract amendments plus
   two call-site edits, and the verdict came from a re-run gate each time.

### V.7.4 G18 discharged — R-2 implemented, and the evidence for it

G18 had two halves. §V.1 closed the **specification**; 2.15 has now implemented the **code**. Both A8 and
T8 are `PASS`. The evidence, taken from the contracts themselves (`_s23_dbg.txt`, not from a summary row):

| Input | `probe_state` | `producer_state` | `format` | decls | `src.version` |
|---|---|---|---|---|---|
| valid clip | *(absent)* | `extracted` | `mp4` | 2 | `None` |
| 128 ASCII bytes | `unreadable` | `unavailable` | *(absent)* | 0 | `None` |
| truncated mp4 | `unreadable` | `unavailable` | *(absent)* | 0 | `None` |
| audio-only mkv | `no_video_stream` | `unavailable` | `matroska,webm` | 1 | `None` |
| duration overrun | `rejected_by_policy` | `unavailable` | `mp4` | 2 | `None` |

**The acceptance criterion that mattered.** `UNREADABLE` and `METADATA_ABSENT` are separated on the state
axis by **two independent facts**, not one: a failure carries `probe_state`, and it records
`producer_state=unavailable` rather than `absent`. A successful probe carrying no declaration carries
*neither*. So a consumer cannot confuse them even by reading only `producer_state`.

**Both malformations share ONE `unreadable` group**, which is what §V.1 specifies and what R-3 requires
(no new `REJ_*` was invented — the check verifies no `REJ_*` symbol exists in the models).

**Partial contracts retain what was genuinely read.** The audio-only case keeps its real
`matroska,webm` format and its one real declaration; the policy rejection keeps `mp4` and both
declarations. The group survives with the facts it actually obtained, rather than being flattened.

**Groups never reached are ABSENT, not null-filled** (§2.2 F.3.1 rule 2) — `video_stream`, `fps_actual`,
`cfr_vfr`, `duration`, `quality_score` are all `None` on every partial.

#### Two things this does NOT claim

1. **`ingestion_status` is still not implemented.** §2.1.5's contract-level gate
   (`status: accepted|accepted_with_warnings|rejected`, `reason: REJ_*`) is a **separate migration row**
   (§2.1.9 line 409). R-2 records the failure on the group; it does not build the §2.1.5 gate, and
   nothing here maps a `ProbeFailureState` to a `REJ_*` code. `test_ingest_rejects_too_long` was migrated
   to the R-2 representation and its docstring says it will be *replaced*, not deleted, when that row
   lands. The two pre-probe conditions (missing file, empty file) still raise, because no group exists
   to record on and they are `REJ_FILE_*` conditions.
2. **A residual tension for §V.1 review, recorded not hidden.** On `no_video_stream` and
   `rejected_by_policy` the contract reports `producer_state=unavailable` *while retaining* real producer
   declarations (1 and 2 respectively). R-2 says "a probe failure records `state=unavailable` on the
   affected group", and this implements that literally. But the container *was* read, so
   "could not determine" is arguably too strong for the producer group specifically — the declarations
   were genuinely observed. **This was not silently "fixed"**, because deviating from R-2's wording is
   §V.1's call, not 2.15's. Raised as an open item below.

| Ref | Item | Owner |
|---|---|---|
| **G18-R** | Should `producer_state` be `unavailable` on a partial where container metadata *was* read (`no_video_stream`, `rejected_by_policy`), or should it carry the real rollup while only `probe_state` marks the failure? R-2's wording says `unavailable`; the evidence says the declarations were observed. | **2.3** (§V.1) — normative wording |

### V.7.5 A7 carrier decision — and the blocker it exposed

A7's specification is closed (§2.1.17 / v1.4 defines the grammar). What remains is **emission**, and
v1.4 E-6 deliberately refused to say which object should carry an address. That question is **2.3's**,
because `ProducerDeclaration` is 2.3's own model. It was decided from a trace, not from preference
(`_s23_evidence_trace.py` → `_s23_trace.txt`).

#### The trace

| Layer | Finding |
|---|---|
| **Emission** | 6 sites, all in `src/`: `decoder.py:53,148` · `ingestor.py:225,1278` · `analyzer.py:72,86`. All writes; all free-form strings. |
| **Model** | One declaration only: `ProvenanceEntry.evidence_refs: list[str]`, default `[]`. Plain pydantic field. |
| **Serialization** | Verbatim through `model_dump()`. **No custom serializer exists**, so nothing can reinterpret or normalise the value on the way out. |
| **Consumers** | **ZERO.** No module under `src/` reads `evidence_refs`. The only reader in the repository is the Stage 2.3 gate. |

The consumer count is the decisive fact: **moving a ref from one carrier to another breaks nothing.** The
cost of this decision is therefore entirely in choosing the *semantically* right home, not in blast radius.

#### Decision: the carrier is `ProducerDeclaration`

§2.1.17 E-1 reads *"A value extracted from an artifact declaration MUST carry at least one `artifact:`
address."* The subject is **the value**, and `ProducerDeclaration` is this repository's model of exactly
that. `ProvenanceEntry` cannot serve: one entry covers an entire **group**, so it cannot name *which*
declaration an address belongs to — which is precisely why every current value is identical for every
group and every artifact, and therefore why `container_probe` cannot fail any test.

| # | Reason |
|---|---|
| 1 | **E-1's own wording.** The value carries the address; `ProducerDeclaration` *is* the value. |
| 2 | **Granularity.** `ProducerDeclaration` is per-observation and already carries `scope`, so a declaration's address is addressable per declaration rather than per group. |
| 3 | **No new carrier invented.** `ProducerDeclaration` already exists and already models the observation; adding a field is not introducing a new object. |
| 4 | **No consumer breakage.** Proven by the trace: zero readers. |

**This deliberately changes a v1.4 boundary guard, and says so.** `test_evidence_refs.py::test_te6_no_evidence_refs_on_producer_declaration` asserted that `ProducerDeclaration` has *no* `evidence_refs`. That guard encoded v1.4's *then-current* scope (the grammar assigns no carrier), and answering the carrier question supersedes it. The guard is rewritten as **T-E7** below rather than deleted.

#### The blocker: the locator cannot be honestly produced today

**Measured, not assumed.** PyAV exposes the probe a `{key: value}` dict and **no positional
information whatsoever** — the only container attributes resembling a location are `metadata`,
`metadata_encoding` and `metadata_errors`; there is no offset, atom path, or index.

Therefore `artifact:mp4:moov/udta/meta/ilst/©too/data` cannot be *derived* — it would have to be
**guessed**, and the demuxer cannot even tell the probe whether the tag lives at `moov/udta/<x>` or
`moov/meta/ilst/<x>/data`. **A guessed path is the same class of fabrication as `format="unknown"` or
`sample_aspect_ratio="1:1"`** — precisely what A9 was just discharged for removing. It is not written.

| # | Route to a real `artifact:` address | Cost | Owner |
|---|---|---|---|
| **R-a** | A registered **tag → atom-path table** per container family | Specification content: which mp4 atom holds a given logical tag, which Matroska EBML element. §2.1.17 can define the grammar but cannot know container internals | **2.3** |
| **R-b** | **Byte-level location** — the probe scans the container to find where a tag physically lives, as `_s23_fixture_inject.py` already does for the injector | Factual and table-free, but a real cost in a "probe", and a scope decision | **2.3** |
| **R-c** | Emit a *weaker* address such as `artifact:mp4:metadata/encoder` | **Rejected.** That is changing the grammar to accommodate what the probe can produce — the exact move §2.1.17 exists to prevent, in mirror image | — |

**Partial compliance is available and must not be reported as discharge.** For **Matroska** the mapping
is deterministic by spec — container tags are `segment/info/<TAG>`, stream tags
`segment/tracks/<n>/tags/<TAG>` — so route R-a could honestly cover mkv immediately. For **mp4** it
cannot, because iTunes-style `meta/ilst` and plain `udta` `©` tags coexist at different depths with no
demuxer signal. **An mkv-only address is not A7 closing**; it is the first measurable step, and the row
stays `FAIL` until the mp4 route is settled.

#### Current state of A7 — unchanged, and honestly

`A7 FAIL`. The gate still reports `refs=['container_probe']`, classified `LEGACY`, with zero
artifact-located refs. **Nothing in the implementation was changed for this step**, deliberately: adding
an `evidence_refs` field to `ProducerDeclaration` that is always empty would make the model *look*
closer to compliance while A7 still failed — the same appearance-of-progress that made A1 vacuous.

| Ref | Item | Owner |
|---|---|---|
| **G13-L** | The `artifact:` locator is not derivable from what PyAV exposes. Requires R-a (tag→path table) or R-b (byte-level scan). | **2.3** — container/probe knowledge, not §2.1's |

Four check rows, **three register findings**. They are deliberately not bundled:

| Row(s) | Register | Owning contract | Missing work | Smallest next action |
|---|---|---|---|---|
| **A7** | G13 | **2.3** (implementation obligation) | grammar EXISTS (§2.1.17); no `artifact:` locator can be produced | the R-a/R-b decision record, **§V.7.6** |
| **A9** | **DISCHARGED** | G10 | `stage2_source_description` v1.1 (SAR) + v1.2 (DAR) | **None** — see §V.7.3 |
| **A8 + T8** | **DISCHARGED** | G18 | R-2 implemented | **None** — see §V.7.4 |
| **G17** | G17 | **§2.16** | §2.16.5–7 do not exist | **fenced; nothing belongs here** |
### V.7.6 R-a vs R-b — technical decision record for A7/G13

> **FROZEN — ROUTING BASELINE for A7/G13.** Frozen 2026-09-30. This record scopes the
> implementation obligation; it changed no rule and no code, and it is **not** grounds to
> reopen §2.1.17. Three decisions are deliberately left **OPEN** (G13-M, G13-R, G13-T) and
> must be resolved before any code is written. Superseding this record requires new
> measurement, not preference.

> **Governing invariant.** No artifact address may be emitted unless the implementation can
> establish that the address identifies the actual declaration being reported. This is the
> same anti-fabrication principle that drove the SAR/DAR correction and the retirement of the
> `"://"` proxy.

**Implementation sequence.** Frozen with the record; steps 1–3 are decisions, 4–7 are code, 8 is the verdict.

| # | Step | Kind |
|---|---|---|
| 1 | Resolve **G13-M** — locator scope, and `not located` as an explicit outcome | decision |
| 2 | Resolve **G13-R** — one address or two when a key is physically present twice | decision |
| 3 | Empirically resolve **G13-T** — is `<n>` the stream index or the track number | **measurement**, not assumption |
| 4 | Define the smallest locator mechanism consistent with 1–3 | design |
| 5 | **Only then** add `ProducerDeclaration.evidence_refs` | code |
| 6 | Emit real `artifact:` references from the probe | code |
| 7 | Make the A7 gate validate the **structure and identity** of the locator, not merely the `artifact:` prefix | code |
| 8 | Re-run from a clean state; the gate decides | verdict |

**Step 5 is not optional to reorder.** Adding the field before a locator exists would leave it
permanently empty — the appearance of compliance that made A1 vacuous.

This is a decision record, not code. It answers the three questions from measured bytes
(`_s23_feasibility.py` → `_s23_feas.txt`), not from plausibility.

## The three questions

### Q1 — Can a deterministic mapping be established, per family, from what the probe possesses?

| Family | Answer | Evidence |
|---|---|---|
| **Matroska / WebM** | **YES** | `Tags` element `0x1254C367` occurs exactly **2×** (Info + TrackEntry), `Info` `0x1549A966` present, and PyAV surfaces exactly those keys. The Matroska spec admits Tags **only** under `Segment>Info` or a `TrackEntry`, so a global tag has exactly **one** legal home. The location is derived *by specification*, not by a muxer implementation detail. |
| **mp4** | **NO** | Measured: PyAV writes the container `encoder` tag to **`/moov/udta/meta/ilst/©too`** — iTunes-style. The format *also* permits plain `/moov/udta/©too`. The demuxer merges both into one `{key: value}` dict with no positional signal, so the probe cannot tell which it saw. |

**The decisive detail, and the reason this is not a footnote:** the "obvious" table entry
`encoder → moov/udta/©too` is **wrong for this repository's own files**. PyAV writes
`meta/ilst/©too`. A table written from intuition would have emitted a false address on the very
fixtures this audit already uses. **That is exactly "pretending an unverified mapping is an observed
byte location", so R-a is rejected for mp4.**

*Caveat recorded:* `ffmpeg` is not on PATH, so a second mp4 atom layout could not be *synthesised*
and observed. The mp4 claim rests on the **format** permitting several paths for one key, plus the
measured fact that this repo's writer uses a non-obvious one. It is not resting on two observed files.

### Q2 — Can byte-level location be obtained without turning 2.3 into a container parser?

| Question | Answer | Evidence |
|---|---|---|
| Does the probe already parse bytes? | **No** | `ingestor.py` contains **0** `struct.unpack` calls and **27** `av.` references. Structure comes entirely from PyAV; an atom walk does not exist in `src/`. |
| Would R-b need a general parser? | **No — if bounded to the question** | Locating *one* tag needed a **~25-line** recursive descent over a known set of container boxes, with one special case (`meta` carries a 4-byte version/flags header). That is a bounded locator, not a general ISO-BMFF parser. |

So R-b is **feasible and small *when scoped to locating a tag***. It would be large, and out of
character for a probe, if implemented as a general container parser. That boundary is the scope
decision this record exists to make.

### Q3 — Coverage

| Question | Answer | Evidence |
|---|---|---|
| What family does the A7 gate measure on? | **mp4** | `check_a_invariants` builds its A7 fixture via `_build_clip(… "a7.mp4")`. |
| What families exist in the repo's fixtures? | **mp4 only** | `declared_real.mp4`, `conflict_two_scope.mp4`, `t1_base.mp4`. |

**This is the finding that changes the plan.** The mkv route looked like "the first measurable step",
but **it covers 0 % of what the gate measures**. An mkv-only implementation leaves A7 `FAIL`, and
proposing it as progress would be a category error.

## Decision

**Neither route discharges A7 alone. A hybrid is selected, and mp4 is the mandatory half.**

### V.7.7 G13-M + G13-R (combined) — physical declaration identity in mp4

Framed on **physical identity, not metadata semantics**: given a canonical producer key, what
physically exists in the artifact? The declaration model then records the *verified* relationship.
Framing it the other way round would let `ProducerDeclaration` semantics drive the locator backwards.

Evidence: `_s23_duplicate.py` → `_s23_dup.txt`, `_s23_control.py` → `_s23_ctrl.txt`,
`_s23_emptycheck.py` → `_s23_empty.txt`.

#### What is ESTABLISHED (measured, replicated three times)

| Observation | Evidence |
|---|---|
| The same logical mp4 key **can physically exist at more than one path** | 2 `©too` atoms at `/moov/udta/meta/ilst/©too` **and** `/moov/udta/©too`, in one artifact |
| The demuxer does **not merge** them | `PyAV container.metadata` reports a single `encoder` |
| It **destroys the value**: `encoder == ''` | reproduced in 3 independent runs |
| **Value agreement does not prevent it** | the identical-values control also returns `''` |
| Spurious suffixed keys appear | `encoder-rus`, `encoder-smi`, `encoder-por` — locale read as empty |

**The collision blanks the value; it does not select one.** That is a stronger and more damaging
finding than "the demuxer merges", and it is why the demuxed dict cannot be the locator's source of
truth for multiplicity.

#### What is NOT established — and must not be cited

| Case | Status |
|---|---|
| **1** — plain `moov/udta/<key>` alone, writer's atom stripped | **INVALID.** The strip/inject helper corrupted the artifact; the scanner and the demuxer both found nothing. Three helper bugs were fixed to get this far (immutable `bytes`, stale offsets after deletion, and shrinking non-ancestor containers). **Whether the plain form is readable in isolation is still unknown.** |
| **4** — one malformed sibling | **INVALID.** The malformed atom was not reachable; the file and the scan disagree. Establishes nothing. |

Cases 2 and 3 are valid: same known-good base, differing only in the injected value.

#### The seven questions

| # | Question | Answer |
|---|---|---|
| 1 | Candidate mp4 paths in scope | `/moov/<key>` · `/moov/udta/<key>` · `/moov/udta/meta/ilst/<key>/data` · `/moov/meta/ilst/<key>/data`, plus the `trak`-scope equivalents. **Format-derived**; only the `meta/ilst` one has been *observed* |
| 2 | Can each actually contain the key? | `meta/ilst/<key>` — **observed**. `/moov/udta/<key>` — **injected and present in the bytes**, but never observed *alone* (Case 1 invalid). `moov/<key>` — unverified |
| 3 | Same vs distinct physical declaration | **Distinct.** Two atoms at two paths are two physical declarations *even when their values are identical*. Case 2 proves identical values do not make them one declaration |
| 4 | Zero locations found | **`not located`** — an explicit outcome. Never a synthesized path, never a default |
| 5 | Exactly one location found | Emit its verified `artifact:` address — **but only if the observed value is non-empty.** An empty observed value is not a declaration (see G13-E) |
| 6 | Two locations found | **Neither can be selected, and neither can be attributed.** The observed value is empty, so no address may be paired with a value. Precedence is **not available here** — there is no value to prefer |
| 7 | One declaration with several refs, or several declarations? | **One declaration, several refs.** Multiplicity is *physical*; the observation is *singular and degraded*. A second `ProducerDeclaration` would assert a second value that was never observed — which would be fabrication |

**Q6 and Q7 are the load-bearing answers.** G13-R is not "retain all vs apply precedence". Given the
measured behaviour, precedence is **moot**: the probe has no value to prefer. The record is therefore
*two verified locations + one degraded observation*, and no silent selection.

#### A NEW defect this exposed — G13-E, and it is live

Feeding the duplicate artifact through the **real ingestor**:

```text
declarations recorded: 3
   scope=container    key=encoder      value=''
   scope=container    key=encoder-rus  value=''
   scope=video_stream key=handler_name value='VideoHandler'
producer_state: ObservationState.EXTRACTED
```

**The current contract asserts two producer declarations whose values are empty strings, and reports
`producer_state=EXTRACTED`.** That is the same fabrication class as the `"1:1"` and `"0:1"` sentinels:
it claims an observation that was never made, and `EXTRACTED` claims metadata was obtained when nothing
was. **This is independent of A7** and was not visible before, because no fixture produced an
empty-valued tag.

Recorded, **not fixed**: the frozen sequence says no code before the decisions are resolved, and fixing
this would move A1/A2 results. It warrants its own gate row and an owner decision.

| Ref | Item | Owner |
|---|---|---|
| **G13-P** | ~~is the plain `moov/udta/<key>` form readable in isolation?~~ | **ANSWERED: NO** — §V.7.7.1. `_s23_g13p.py` → `_s23_g13p.txt` |
| **G13-M** | Locator scope: which candidate mp4 paths are searched, and `not located` as an explicit outcome | **2.3** — now constrained by G13-P, which excludes `/moov/udta/<key>` |
| **G13-R** | Two-location case: one declaration, several verified refs, no precedence, observation flagged degraded | **2.3** — ratify, and apply the G13-P refinement in §V.7.7.1 |
| **G13-T** | Matroska `<n>`: stream index or track number | **2.3** — measurement |
| **G13-E** | An empty-valued producer tag is recorded as a declaration and drives `producer_state=EXTRACTED`. Empty is not a declaration | **2.3** — separate row, not an A7 subtask |

**No code, no carrier change, no §2.1.17 amendment in this pass.** A7 remains `FAIL`.

#### V.7.7.1 G13-P resolved — and it REFINES the duplicate finding

Constructed with a **per-step verifier**: each artifact is re-opened and its box chain re-walked after
every operation, and the run aborts if a step does not do what it claims. All three steps passed with
the chain **intact**, so the empty value below is a real demuxer behaviour, not a corrupt fixture.

```text
[base]                    (c)too: /moov/udta/meta/ilst/©too   encoder='Lavf62.12.102'  chain OK
[stripped]                (c)too: (none)                      encoder=None              chain OK
[plain udta ONLY]         (c)too: /moov/udta/©too             encoder=''                chain OK
```

> **G13-P: NO.** `/moov/udta/<key>`, as the only physical declaration, yields an **empty** value.

**Therefore G13-M must EXCLUDE `/moov/udta/<key>`.** Finding bytes there does **not** establish that
the probe would observe that declaration, so an address for it would describe a declaration the
contract never reported — a direct breach of the frozen invariant.

**This also corrects the causal model behind the duplicate result.** The earlier reading was "two valid
declarations collide". It is not:

| Physical set | `encoder` |
|---|---|
| `meta/ilst/<key>` **alone** | the real value |
| `udta/<key>` **alone** | `''` |
| **both present** | `''` |

The plain-`udta` atom is **unreadable but destructive**: its mere presence blanks the shared key and
destroys the *il*st value that was perfectly readable on its own. So the duplicate case is
**one readable declaration plus one unreadable sibling that corrupts it** — not an ambiguity between two
competing values.

Two consequences for G13-R:

1. **"Precedence" was the wrong frame.** There is no value contest to arbitrate; the readable value is
   simply destroyed before the probe can see it.
2. **A locator alone would not recover it.** It can establish *where* the declarations are, but the
   observed value is gone. Recovering it would require reading the value out of the bytes — a
   **different mechanism** from locating one, and one that must be decided explicitly rather than
   assumed to follow from a locator.



### V.7.8 G13-E — decision: an empty producer value is never reportable

A decision record, not code. It answers the six questions. Evidence:
`_s23_g13e.py` → `_s23_g13e.txt`.

#### The measurement that settles it

Three artifacts were authored and read three times each:

| Case | `encoder` | sibling key |
|---|---|---|
| **A** — a **genuine** `©too` whose value string is `""` | `''` | `encoder-mlt` |
| **B** — the **degradation** (unreadable plain-`udta` sibling, per G13-P) | `''` | `encoder-iri` |
| **C** — control, readable `meta/ilst` | `'Lavf62.12.102'` | *(none)* |

> **A and B are INDISTINGUISHABLE at the contract surface.** Both present `encoder = ''`.

The sibling suffix differs (`mlt` vs `iri`) but is **not a signal**: it is stable *within* an artifact
and varies *across* artifacts, because it reflects adjacent bytes, not the semantic condition. A consumer
cannot use it, and building a rule on it would be exactly the "plausible structural interpretation is not
evidence" error this audit has rejected three times already.

#### The six answers

| # | Question | Decision |
|---|---|---|
| **1** | What constitutes a genuine observed producer value? | A **non-empty string**, read from an **observable** mechanism (one the probe actually surfaces). Both halves are required. |
| **2** | Can `""` ever be a legitimate producer declaration value? | **NO — not in this contract.** Not "not usually": never. A consumer cannot distinguish a genuine empty from a degradation, so `""` is untrustworthy *as a class*, including when genuine. |
| **3** | How is degradation told from a genuine empty? | **It isn't, and no rule may try.** Therefore the answer to Q2 is unconditional rather than detection-based. This is the finding that removes the temptation to sniff for degradation. |
| **4** | What applies when the key is exposed but its value is not usable? | The **declaration is not created**. An empty value yields no `ProducerDeclaration` at all. |
| **5** | Which `ObservationState`? | **`UNAVAILABLE`** — already authorised, no new member. Not `absent`: the property *physically exists* (G13-P located it). Not `uncertain`: there is no single garbled value to interpret, there is nothing usable. Not `extracted`: nothing was obtained. |
| **6** | Is the physical sibling recorded anywhere? | **No.** It creates no declaration and is not an evidence target. G13-M excludes `/moov/udta/<key>` as unobservable, so the sibling is out of locator scope entirely — this is a consequence of Q1, not a second rule. |

#### Consequences

1. **`""` is rejected at extraction, unconditionally.** Not "when a sibling is detected" — detection is
   impossible per Q3. The current code, which records `encoder=''` and `encoder-rus=''` as declarations and
   reports `producer_state=EXTRACTED`, is **non-conformant with this decision**. That is the live defect.
2. **§2.1.17 E-1 does not engage in the degraded case.** E-1 requires an `artifact:` address for a value
   "extracted from an artifact declaration". If no declaration is created, there is no extracted value, so
   there is nothing for A7 to address. A7 is *not* closeable by emitting an address for `""`.
3. **`UNAVAILABLE` is the honest state for the group** — the probe could not determine the producer
   identity, which is precisely its meaning, and it is distinct from `ABSENT` (read, nothing declared).
4. **G13-R can be retired.** There is no arbitration between two observed values: one was readable and
   was destroyed by an unreadable sibling. Retaining a precedence rule for a contest that does not occur
   would be inventing specification for a non-case. **Residual, if one is ever needed:** an unreadable
   physical sibling neither creates a declaration nor becomes an evidence target — which Q6 already
   states.
### V.7.9 G13-M — decision: locator scope is limited to PROVEN observable mechanisms

A decision record, not code. Evidence: `_s23_g13m.py` → `_s23_g13m.txt`,
`_s23_locate.py` → `_s23_loc.txt`.

#### The eligibility rule (from G13-E)

> A structure is **ELIGIBLE** as an evidence source **iff** the probe can obtain a **non-empty** value
> from it **and** that value can legitimately become a `ProducerDeclaration`.

**Physical presence is not eligibility.** G13-P already disqualified `/moov/udta/<key>` on exactly
this basis.

> **Decision: eligibility is PROVEN, never assumed. Anything unproven is INELIGIBLE.**

This is the single rule that makes the scope decidable. It is also why the list below is short.

#### Measured results

| # | Structure | Observed? | Eligible? | Basis |
|---|---|---|---|---|
| 1 | mp4 `/moov/udta/meta/ilst/<key>/data` — **container** | yes, non-empty | **ELIGIBLE** | located at `/moov/udta/meta/ilst` [2201..2259); the file's **only** `©too` box (at 2209); probe reads the value verbatim |
| 2 | mp4 `/moov/udta/<key>` | **no** — yields `''` | **INELIGIBLE** | G13-P, verified per-step |
| 3 | mp4 **track scope** | yes (probe reads `SomeOtherTool 9.9.9`) | **INELIGIBLE — see §V.7.14** | **refined:** the observed mechanism is `stsd`→`compressorname`, which A5-W excluded as unauthorised. An authorised track-scope metadata mechanism **does** exist (`trak/udta/name`), but no producer key can be written there and read back non-empty with the current tooling (`G13-F`) |
| 4 | mp4 `/moov/meta/ilst/<key>/data` | untested | **INELIGIBLE** | not proven |
| 5 | mp4 `/moov/<key>` | untested | **INELIGIBLE** | not proven |
| 6 | mkv **track** `Tags` | yes, non-empty | **CORRECTED — see §V.7.11** | a proper EBML parse shows **no `Tags` inside any `TrackEntry`**; PyAV writes both stream tags into one **global** `Tags`, so `tracks/<n>/tags/<TAG>` does not exist here. **Downgraded to UNLOCATED** |
| 7 | mkv **global** `Info/Tags` | **no** | **INELIGIBLE** | see below |

#### Two corrections this pass forces on itself

**Row 3 — the mp4 track-scope location is WITHDRAWN.** A first pass attributed the stream tag to
`/moov/trak/mdia/minf`. A targeted re-check (`_s23_locate.py`) showed the literal sits at offset 1840,
inside `/moov/trak/mdia/minf/stbl/stsd` — the **sample-description** box, which holds codec
configuration, not metadata. That attribution is an **artifact of an incomplete walker**: `stsd` is a
FullBox carrying a version/flags header and an entry count, and each sample entry has its own 78-byte
header, neither of which this walker parses. The box-walk through `stsd` is therefore unreliable.

The claim is withdrawn, not recorded. **Row 3 stands as UNLOCATED**, and an unlocated structure is
ineligible under the rule above. Locating it properly needs a walker that understands sample entries —
which is Step 4's problem, not this decision's.

**Row 7 — a Matroska container tag is overwritten by the muxer.** Setting `metadata["ENCODER"] =
"ContainerWriter 1.0"` and re-reading returns **`'Lavf62.12.102'`** — the muxer's own value. This is
the Matroska counterpart of the R3 finding already recorded for mp4, and it means the observed global
`ENCODER` is **muxer-authored, not declared**. It is therefore not an eligible evidence source *for a
producer declaration*; a locator that addressed it would be addressing a self-description.

#### `not located`

> **If no qualifying observable declaration can be established at an in-scope location, the locator
> returns `not located`. It never supplies a conventional or default path.**

`not located` is a distinct outcome from `absent` (the scope was read and held nothing) and from
`unavailable` (the value could not be determined — G13-E). It is **not** an error: a key with no proven
mechanism is a legitimate result, and the address stays absent rather than invented.

#### Coverage consequence — stated, not smoothed

| Consumer | Covered? |
|---|---|
| **A7 gate** — measures a **container-scope mp4** declaration (`a7.mp4`) | **YES** — row 1 is eligible |
| **A7/T7 conflict** — involves the **stream-scope** tag of the two-scope fixture | **NO** — row 3 unlocated |
| Matroska global producer identity | **NO** — row 7 is muxer-authored |

**So A7 could be discharged for the case the gate measures while remaining unlocatable for stream-scope
mp4 and for Matroska global tags.** That must be recorded as a coverage limit rather than presented as
general success: "A7 `PASS`" would mean *one container-scope mp4 path is addressable*, not *producer
metadata is addressable everywhere it is observed*.

#### The `not located` rule bounds A7 honestly

Per G13-E, A7 addresses values that legitimately survive the observation layer; it does not provide
evidence for values the observation layer is prohibited from producing. Combined with this record:

```text
  key observed, non-empty, mechanism proven   -> emit the verified artifact: address
  key observed but mechanism UNPROVEN         -> not located     (no address, no default)
  key observed but value empty (G13-E)       -> no declaration; group = unavailable
### V.7.10 G13-M2 — answered NO, and it exposed a producer value inside a CODEC field

Measurement, not code. Evidence: `_s23_g13m2.py` → `_s23_g13m2.txt`,
`_s23_cname.py` → `_s23_cname.txt`.

#### What G13-M2 did

`stsd` was parsed the way the format defines it — FullBox version/flags + entry count, then
`VisualSampleEntry` with its 78-byte header — and the literal located, rather than searched for with a
generic recursive walker. No general sample-entry parser was written; only what the fixtures contain
was read.

**Result: the stream-scope string is not in any metadata box.** It lies at offset 1840, inside
`stsd` [1773..1948) → `avc1` [1789..1948), and in **no** child box of that entry.

#### Decoding the field settles it

`VisualSampleEntry.compressorname` is a 32-byte Pascal string (length byte + text). Decoding it:

| Fixture | `compressorname` |
|---|---|
| **`conflict_two_scope.mp4`** | **`SomeOtherTool 9.9.9`** (length 19, well-formed) |
| `t1_base.mp4` *(control)* | empty — all zeros |
| `declared_real.mp4` *(control)* | empty — all zeros |

The two controls are byte-identical in that field, and only the fixture built with a stream-scope
`encoder` tag carries producer text there.

> **PyAV's mov muxer wrote the stream metadata tag into the sample description's
> `compressorname` field — a CODEC configuration field, not a metadata box.**

Decoding did not break (frames were verified identical), but a codec-configuration field carrying a
producer string is a structural anomaly in its own right.

#### Answers

| # | Question | Answer |
|---|---|---|
| 1 | Sample-entry types present in the fixtures | exactly one: **`avc1`** |
| 2 | `stsd` structure and entry boundaries | established: FullBox + entry_count(1) + `avc1` entry, size 159 |
| 3 | Is a producer-metadata mechanism present there? | **NO** |
| 4 | Define an artifact address for it? | **NO — nothing to define** |
| 5 | Scope retained | **`UNLOCATED`** |

**G13-M2 is CLOSED.** Per the rule in §V.7.9, an unproven mechanism is ineligible, so mp4 track scope stays
ineligible and no locator spec is expanded on a hypothetical structure. `not located` is the correct
result, and it is **not** a claim that track scope has no metadata — only that no mechanism was proven.

#### The consequence that reaches back into A5 — recorded, not acted on

**The stream-scope leg of the A7/T7 conflict fixture is not a metadata declaration.** Its value was
sourced from the **codec sample description**, and the probe surfaces it as `stream.encoder`.

That is, structurally, what A5 exists to prevent: **encoder identity being established from codec
identity.** A5 currently reports `PASS`, because its check asks whether a codec *string* (`h264`,
`avc1`) leaked into a producer declaration — and `SomeOtherTool 9.9.9` contains neither. But the value
arrived *from the codec box*, which its check does not test for.

**A5's verdict is NOT changed here.** The gate was not altered, and no check was rewritten to pass.
This is recorded as a finding against the **check's coverage**, exactly as A9's incomplete sentinel
tuple was handled — the row may be green while the invariant is only partly measured.

### V.7.11 G13-T — answered, and it CORRECTS G13-M row 6

Measurement, not code. Evidence: `_s23_g13t.py` → `_s23_g13t.txt`.

#### G13-T: `<n>` is the POSITION, not the TrackNumber

Two tracks were written, each with a **distinct** tag, then read back:

| Position | TrackNumber | TrackType | tags inside the entry |
|---|---|---|---|
| **0** | **1** | 1 (video) | *(none)* |
| **1** | **2** | 2 (audio) | *(none)* |

> `TrackNumber` is **1-based**; the physical position is **0-based**. **They differ.**
> `segment/tracks/<n>/tags/<TAG>` therefore resolves **only** with `<n>` = **POSITION**.
> Writing `TrackNumber` there addresses the wrong track — or nothing — whenever they diverge.

#### The correction this forces on G13-M row 6

G13-M row 6 claimed **mkv track `Tags` is ELIGIBLE**, on the basis that the value was "physically
inside a `Tags` element". That was established with a **crude byte-offset heuristic** (any `Tags` within
a few KB of `Info` was attributed to `Info`), and it is **wrong**.

A proper EBML parse shows:

```text
  Tags elements INSIDE a TrackEntry : 0
  TAG_ON_VIDEO_TRACK  at 601  -> inside Segment child  Tags [527..742)
  TAG_ON_AUDIO_TRACK  at 688  -> inside Segment child  Tags [527..742)
```

**PyAV's mkv muxer wrote both stream tags into ONE global `Tags` element**, not into per-track
`TrackEntry/Tags`. So there is no `tracks/<n>/tags/<TAG>` structure in these artifacts for a locator to
address — **row 6 is DOWNGRADED to UNLOCATED.**

Note the oddity this leaves: PyAV reads the two values back as *stream-scoped* metadata, correctly
separated, even though both live in one global element. Whatever mechanism it uses to disambiguate is
not a physical location, and therefore cannot be addressed.

This is the **second time in this audit that a plausible offset-based attribution turned out wrong**
(after G13-M's `stsd` claim). Both were caught only by a parser built to the format rather than to the
hypothesis.

#### Eligibility after G13-T — the scope is now a single path

| # | Structure | Eligible? | Basis |
|---|---|---|---|
| 1 | mp4 `/moov/udta/meta/ilst/<key>` — container | **YES** | located, observed non-empty |
| 2 | mp4 `/moov/udta/<key>` | no | unreadable (G13-P) |
| 3 | mp4 track scope | no | `UNLOCATED` (§V.7.10) |
| 4–5 | mp4 `/moov/meta/ilst/<key>`, `/moov/<key>` | no | not proven |
| **6** | **mkv `tracks/<n>/tags/<TAG>`** | **no — DOWNGRADED** | **no per-track Tags is written; the value is in a global `Tags`** |
| 7 | mkv global `Info/Tags` | no | muxer overwrites the global `ENCODER` |

**Exactly one eligible structure remains**, and it is the one the A7 gate measures (container-scope
mp4). "A7 `PASS`" must therefore be reported as *this one path is addressable* — never as *producer
metadata is addressable generally*.

| Ref | Status |
|---|---|
| **G13-T** | **CLOSED** — `<n>` is the position |
| **G13-M** | CLOSED, **row 6 corrected** above |
| **G13-M2 / G13-P** | CLOSED |
| **G13-R** | RETIRED |
| **G13-E** | DECIDED · 2.15 deferred |

### V.7.12 A5-W — OPENED, scope deliberately bounded

Opened **before** any A7 implementation, because it governs *which observations may enter the
producer-declaration population at all* — upstream of addressing them.

> **Scope, fixed:** whether a **codec / sample-description field**, specifically
> `VisualSampleEntry.compressorname`, is an **authorised producer-declaration mechanism**.
> **Nothing else is in scope.** This is not an audit of every possible metadata mechanism.

#### The layered model this audit has converged on

```text
  physical bytes
        ↓
  technical / container mechanism
        ↓
  probe-observable value                G13-P: presence ≠ observability
        ↓                                  G13-E: observable ≠ usable
  AUTHORISED producer-declaration       A5-W: observable ≠ ELIGIBLE  ← the open question
        ↓
  ProducerDeclaration
        ↓
### V.7.13 A5-W — DECIDED: `compressorname` is NOT an authorised producer-declaration mechanism

A decision record, not code. Evidence: `_s23_a5w.py` → `_s23_a5w.txt`,
`_s23_cname.py` → `_s23_cname.txt`.

#### The ruling

> **NO.** A codec sample-entry field is not an authorised producer-declaration mechanism.

| # | Ground | Basis |
|---|---|---|
| 1 | **Field semantics** | `VisualSampleEntry.compressorname` is defined in ISO/IEC 14496-12 as a 32-byte Pascal string naming the **compression algorithm**. Its declared subject is the codec, not the authoring tool. |
| 2 | **Indistinguishability** | Nothing in the artifact distinguishes a codec name from a producer tag placed there by a mis-writing muxer. This is the *same* argument that made `""` rejectable under **G13-E**, applied one layer up: an unprovable claim cannot be admitted. |
| 3 | **Address category** | Admitting it would make `artifact:` addresses point **into codec sample descriptions**. §2.1.17 addresses *declarations*; a sample entry is not one. |

#### The consequence chain

```text
  stsd / avc1 / compressorname
        ↓
  codec configuration            (ground 1)
        ↓
  NOT a producer declaration
        ↓
  no ProducerDeclaration
        ↓
  NO A7 evidence obligation
```

**Cleaner than teaching a locator to address something that should never have entered the model** —
which is why A5-W precedes the carrier.

#### New evidence that bounds the ruling's cost

Three track-scope keys were written with this toolchain, and each landed in a **different** box:

| Key written | Demuxer surfaces | Physically at | Mechanism |
|---|---|---|---|
| `encoder` | yes | `/moov/trak/mdia/minf` → `stsd` → `compressorname` | **codec field** |
| `handler_name` | yes | `/moov/trak/mdia/hdlr` | **handler box** — structural |
| `title` | yes, as `name` | **`/moov/trak/udta/name`** | **metadata atom** |

> **`trak/udta/name` exists, is written, and is read back.**

So an **authorised mp4 track-scope metadata mechanism does exist** — the producer key simply is not
exercised through it by this muxer. Two consequences:

1. **The ruling is not a dead end.** A two-scope conflict **can** be rebuilt on an authorised mechanism,
   by placing a declaration at a track-scope metadata atom (the T-R3b injector already writes atoms at
   arbitrary paths).
### V.7.14 T7 rebuild — ATTEMPTED and BLOCKED by measurement

Rebuilding T7 on an authorised track-scope mechanism was authorised as the next fixture step. It was
attempted first and **failed**. Recording the failure rather than forcing a fixture.
Evidence: `_s23_rebuild.py` → `_s23_rb.txt`.

#### What was tried

| Route | Mechanism written | Stream `encoder` read back |
|---|---|---|
| **R1** — PyAV writes `st.metadata['©too']` | `©too` | **no effect** |
| **R2** — inject `trak/udta/©too`, iTunes `data` payload, locale 0 / 1 / 1033 | `©too` | `Lavf62.12.102` + `encoder-chi: ''` |
| **R3** — inject `trak/udta/encoder` (the shape `title` used) | `encoder` | `Lavf62.12.102` |

**In every route the value that survives as `stream.encoder` is `Lavf62.12.102`** — the *muxer's own*
value, which A5-W established lives in `compressorname`. The injected atom never becomes the
declaration; in R2 it surfaces only as a **locale-suffixed, empty** key.

> **A track-scope PRODUCER declaration cannot be constructed with the available tooling.**

#### Why — and it is not a fixture bug

| Mechanism | Status |
|---|---|
| `trak/udta/name` (title) | **works** — written, readable, **non-empty**, authorised |
| `trak/udta/©too` (producer identity) | **unreadable** — the iTunes `data` payload is not what the plain-`udta` reader expects, so the value comes back `''` |
| `stsd/.../compressorname` | readable, but **unauthorised** (A5-W) |

The plain `udta` reader and the iTunes `ilst` reader use different payload conventions; the injector
models the latter (which is why container-scope injection worked). The track-scope equivalent is a
**different payload format that has not been established here**.

#### The knock-on that matters most

A two-scope conflict requires **the same canonical key at two scopes** — §2.1.16's per-key rule.
Producing that with an authorised mechanism runs into a second obstacle:

- track-scope `title` works and **is** matched by `PRODUCER_KEY_PATTERN` (`…|title|author|comment|…`);
- but a container-`encoder` vs stream-`title` pair is **two different canonical keys** — that is not a
  conflict, it is two unrelated declarations;
- and a `title` vs `title` conflict *is* a same-key conflict, but over a **title**, which would change
  what T7 demonstrates (it currently demonstrates two disagreeing producer *identities*).

#### Consequences, stated plainly

| Ref | Status |
|---|---|
| **T7 rebuild** | **BLOCKED.** Not attempted further; no fixture was altered. The existing `conflict_two_scope.mp4` is untouched and T7's recorded `PASS` stands unchanged. |
| **T7 provenance** | **Questionable and now unreproducible.** Its stream leg rests on `compressorname`, which A5-W excluded, and no authorised substitute is constructible with the current tooling. |
| **T7 verdict** | **NOT reversed.** The recorded `PASS` is a fact about the gate run that happened. What is now open is whether T7 is *supportable by a conforming fixture*, which is a different question. |
| **G13-F** | OPEN — a track-scope producer declaration needs either a track-`udta` payload format that this demuxer accepts, or a writer that emits one. 2.3's to determine. |
| **A5-H** | **PARKED** as directed (`mdia/hdlr`), out of scope. |

**A7's coverage is unchanged by this**: the one eligible path — container-scope
`moov/udta/meta/ilst/<key>` — is unaffected, and it is what the A7 gate measures.

### V.7.15 Freeze — the controlled state at the close of the G13 investigation

This section freezes every decision reached while investigating A7/G13. It is a **status record**, not
a new decision. Nothing here changes a gate row, a model, or a specification.

#### Routing, as frozen

| Ref | Status |
|---|---|
| **A5-W** | **CLOSED — NO.** `compressorname` is not an authorised producer-declaration mechanism |
| **A5-H** | **PARKED.** `handler_name → mdia/hdlr` is a fourth mechanism class, outside the bounded A5-W ruling |
| **A5-C** | **OPEN** — A5's assertion cannot see the *provenance* of a value, only codec strings in it |
| **G13-P** | **CLOSED** — `/moov/udta/<key>` unreadable; excluded |
| **G13-M** | **CLOSED, refined** — eligibility is evidence-based; row 3 refined per §V.7.14 |
| **G13-M2** | **CLOSED** — no producer mechanism inside `stsd` |
| **G13-T** | **CLOSED** — `<n>` is the position, not the TrackNumber |
| **G13-R** | **RETIRED** — no arbitration rule is warranted |
| **G13-E** | **DECIDED** — `""` is never a valid declaration; implementation deferred to 2.15 |
| **G13-F** | **OPEN — TOOLCHAIN CAPABILITY BOUNDARY.** Track-scope producer-declaration construction is unproven with the current writer/demuxer. **This is a stopping condition, not an invitation to try more byte layouts.** |
| **G13-E impl** | 2.15, deferred until the A7 decision sequence reaches implementation |
| **A7/G13** | **ACTIVE** — remains the sole non-held gate blocker |

#### T7 — two separate audit facts, kept separate

| Dimension | Status |
|---|---|
| **Historical T7 execution** | **`PASS`** — a fact about the gate run that happened |
| **T7 fixture mechanism under current specification** | **NON-CONFORMING / unsupported** — the stream leg arrived via `compressorname`, which A5-W excluded |
| **Authorised replacement demonstrated** | **NO** |
| **T7 rebuild** | **BLOCKED** (§V.7.14) |
| **Need to falsify the historical PASS** | **NO** |

**The historical `PASS` is preserved and is not reversed.** What is open is whether T7 is *supportable
by a conforming fixture* — a different question, and the reason the two rows above must not be merged.

**No `title/title` fixture is to be created.** It would exercise the conflict machinery over a
*different population*, and substituting it for the `encoder`/`encoder` scenario would silently change
what the test demonstrates. If T7's purpose cannot be preserved as stated, the correct route is an
explicit controlled **test-spec decision** to retire or re-scope it — not a fixture workaround.

#### §2.1.17 is NOT amended

> **The specification describes the required evidence contract. It is not weakened to accommodate a
> fixture or toolchain limitation.**

The absence of a constructible second authorised mechanism is a fact about *this environment*, not about
the contract. §2.1.17 stays as frozen.

#### V.7.15.1 Mandatory closure language for A7 — binding when A7 is discharged

A7 may be discharged **only** with this wording. It is recorded here so that a later pass cannot widen
it by accident:

> **A7 `PASS` — all producer declarations in the **tested eligible population** are traceable to an
> artifact-located reference. The demonstrated eligible population is currently **limited to the MP4
> container-scope `moov/udta/meta/ilst/<key>` mechanism**. **Track-scope producer-declaration
> addressability is not claimed.****

**The prohibited rewrite** — and it is the specific failure this audit has already caught twice, in A9's
sentinel tuple and in A8's per-input distinction:

| Do **not** write | Write instead |
|---|---|
| "Producer metadata is addressable" | "…in the tested eligible population" |
| "All producer declarations are traceable" | "…in the tested eligible population" |
| "A7 passes" | the full sentence above, with the limitation attached |

**A7 is independently dischargeable** and does not require universal addressability. It requires that
the declarations which actually enter the authorised population are traceable per §2.1.17. The next A7
work is therefore **discharging the demonstrated eligible container mechanism** — *not* expanding the
---

## V.8 — A7 research log (R1: evidence-object identity)

Empirical research on what an `artifact:` reference *identifies*. **No implementation, no model change,
no gate change, no §2.1.17 amendment** — this log is measurement and record only.

### V.8.1 R1.1 — OBJECT IDENTITY: **MEASURED** (was BLOCKED by a malformed fixture)

Measured on the genuine fixture `declared_real.mp4`
(`_s23_r1_1.py` → `_s23_r11.txt`, `_s23_fixture_check.py` → `_s23_fxchk.txt`).

#### What the walk found before it stopped

```text
/moov                          CONTAINER        offset 1364
/moov/udta                     CONTAINER        offset 2148
/moov/udta/meta                FULL-BOX container  header 12   ← 4 extra version/flags bytes
/moov/udta/meta/ilst           CONTAINER        offset 2201
/moov/udta/meta/ilst/<BROKEN>  LEAF, header=0   offset 2209   ← walk terminated
```

The walk terminated because the `©too` item's **declared size overruns its parent**.

#### The fixture is structurally invalid — the BASE is not

| Artifact | `©too` declared | expected | verdict |
|---|---|---|---|
| `t1_base.mp4` *(muxer-written)* | 37 | 37 | **CONSISTENT** |
| `declared_real.mp4` *(T-R3b injected)* | **63** | **50** | **DISCREPANCY 13** |

`13` is exactly the value-length delta (26 − 13). The injector's `inject_declaration` computes the
replacement box's size as *old size + new value length* rather than adjusting by the difference, so it
**double-counts**. Ancestors were grown correctly (`udta` 98→111, `meta` 90→103, `ilst` 45→58,
`moov` 882→895, each +13) — the item box alone is wrong.

> **The artifact every A7/T7 measurement rests on is malformed.**

#### Why this was never noticed — and the lesson

FFmpeg tolerates the overrun: it reads the value correctly and the frames decode identically. **Both were
verified.** So the fixture passed every check that had been written for it, because every one of them
tested *decodability*, and **not one tested structure**.

> A fixture verified only by decoding is not verified. A byte-resolving address cannot be researched
> against a box chain that does not close.

#### Which prior measurements are affected, and which are not

| Measurement | Injector path | Status |
|---|---|---|
| **G13-P**, **G13-E**, **G13-M2**, **A5-W**, **G13-T** | `add_plain_too` / `strip_too` / own writers — each **chain-verified** at every step | **UNAFFECTED** |
| **A7 row 1** (mp4 container `meta/ilst` *eligible*) | `inject_declaration` — **malformed** | **Must be re-demonstrated on a well-formed artifact** |

The G13 series used different code paths and each carried its own structural verification, so its results
stand. The damage is confined to the T-R3b fixtures, and therefore to the *demonstration* of A7's one
eligible mechanism.

> **Status of the last row, at the time of writing: resolved.** A7 row 1 *was* re-demonstrated on a
> well-formed artifact and **still FAILS — on the grammar, not on the fixture.** See *Sub-questions —
> before and after remediation* below. The table above is the record at discovery and is retained
> unaltered; it must not be read as a statement of outstanding work.

#### Sub-questions — before and after remediation

The statuses below were recorded **at discovery**, while the walk terminated early, and they are
retained as the historical record rather than overwritten. They are superseded by the measurement
repeated on the repaired artifact (`_s23_r1_1.py` → `_s23_r11.txt`):

| # | Sub-question | At discovery | After remediation |
|---|---|---|---|
| R1.1(a) | Is the *item box* the declaration object, with `data` inside it? | unmeasured — chain did not close | **measured — YES.** `©too` at offset 2209 size 50 contains exactly one `data` child at 2217 size 42; the path resolves UNIQUELY |
| R1.1(b) | Is the `data` body the observed value, or is there a prefix? | unmeasured | **measured — there IS a prefix.** The body is 34 bytes = 4 well-known-type + 4 locale + 26 value; the value starts at body offset 8, absolute byte 2233, cross-checked against a raw byte scan |
| R1.1(c) | Does the path hide structure? | **measured — YES** | unchanged. `meta` is a FullBox (header 12, `version/flags = 0x00000000`); a plain path cannot express those 4 bytes, and a reader that does not know `meta` is a FullBox is wrong by 4 at every level beneath it |

#### Transition — pre-repair to post-repair

> The pre-repair state identified the malformed fixture and held R1.1. The fixture was subsequently
> repaired, structural validation was added, the observer was corrected, and the measurements were
> repeated. **The resulting A7 failure was unchanged.**

The `©too` item box, the `data` payload box inside it, and a recoverable location are three distinct
objects and are **not** interchangeable. R1.1(a) shows the item is the declaration object; R1.1(b)
shows the address locates a *carrier* whose value begins at an offset the address does not itself
record. Identity of the *reported* declaration is therefore not established by the path alone — value
identity (R1.3) and encoding (R1.6) must carry part of it, and the address grammar must decide whether
the **item box** or the **data box** is the addressed object.

#### Remediation performed

| # | Defect | Repair |
|---|---|---|
| 1 | `_grow_sizes` added `delta` to the `©too` box whose size `inject_declaration` had **already** written exactly — the leaf was counted twice, writing a 50-byte box as 63 | grow **ancestors only** |
| 2 | `inject_declaration` passed the **pre-growth** `moov_end` to `_shift_chunk_offsets`, unlike all six other call sites, leaving any chunk offset in that `delta`-wide window unpatched (inert here: 0 patched, mdat precedes moov) | pass `moov_end + delta` |
| 3 | `_s23_r1_1.py::walk` treated `©too` as a **leaf** and never descended, so `data` was invisible and R1.1 reported "0 child box(es), resolves AMBIGUOUSLY". The ambiguity was **manufactured by the observer**, not a property of the format | `is_item()` descent into `ilst` items |
| 4 | every fixture check to date tested *decodability*; none tested *structure*, which is why the double-count survived an entire cycle | `assert_box_chain()`; the builder now **fails** on a chain that does not close |

#### Verification of the repair

```text
  declared box    50 bytes (was 63)          discrepancy 0
  box chain       t1_base OK · declared_real OK · conflict_base OK · conflict OK
  ancestors       moov 882→895 · udta 98→111 · meta 90→103 · ilst 45→58   (each +13)
  metadata        container 'HandBrake 1.6.0 2023041600' / stream 'VideoHandler'   intact
  frames          10 base / 10 injected, byte-identical
  tests           92 passed, 26 subtests          (unchanged)
  G13-P/E/M2      verdicts byte-identical to the recorded baseline
  gate            25 PASS · 1 FAIL · 5 HELD — BLOCKED    (unchanged)
```

#### Outcome

```text
  R1.1        COMPLETE     — measured on a structurally valid artifact
  G13-FI      CLOSED       — injector size arithmetic repaired; the box chain is now
                             asserted at fixture-construction time, not inferred afterwards
  R1.2        NOT STARTED  — no longer BLOCKED on R1.1, but also not DEFINED:
                             no question, population, evidence requirement or
                             falsification condition is recorded for it anywhere in
                             this repository. "Unblocked" is not "ready to run" — the
                             prerequisite is an explicit falsifiable question.
```

**A7 row 1 was re-demonstrated on the repaired artifact and still FAILS — on the grammar, not on the
fixture:**

```text
  refs        ['container_probe']
  classes     {'container_probe': 'LEGACY'}
  conforming  none
```

A sound fixture and a sound observer did not rescue the row. That is the intended reading: the
obligation is falsifiable and remains unsatisfied.

**The gate remains `PASS 25 · FAIL 1 · HELD 5` — BLOCKED.** No row moved, because no row was edited.
The remediation changed the **reliability of the evidence**, not the substantive outcome.

**No code, no gate change, no carrier change, no §2.1.17 amendment.** The gate remains
**`PASS 25 · FAIL 1 · HELD 5` — BLOCKED**, with A7/G13 the sole active non-held blocker. T7 was
neither re-labelled nor propped up with a substitute population to rescue it.

> **Pre-existing documentation defect — not introduced by the R1.1 remediation pass.** This paragraph
> previously carried an orphan fragment, `population to rescue T7.`, whose antecedent sentence had been
> lost in an earlier edit, and the same *"No code, no gate change…"* statement appeared **twice** with
> divergent tails. The duplicate has been removed in favour of the more complete wording, and the
> fragment folded into the sentence above. That folding is a **reconstruction of evident intent, not a
> recovered original** — the lost antecedent is not recoverable from the file, and no meaning beyond
> what the fragment itself carries has been supplied.

2. **G13-M row 3 is refined, not merely left open.** mp4 track scope is not categorically `UNLOCATED`;
   it is *unlocated for the `encoder` key specifically*, because this muxer routes that key to a codec
   field. The mechanism is available; the key does not use it.

#### Adjacent observation — explicitly OUT OF A5-W's SCOPE

`handler_name` is presently recorded as a producer declaration (`PRODUCER_KEY_PATTERN` matches
`handler`), and its value lands in the **handler box**, which names the media handler type. That is a
**fourth distinct case** — neither metadata nor codec — and it is **not decided here**. Flagged, not
ruled, to keep A5-W bounded to the newly demonstrated boundary as instructed.

#### A5 is NOT reinterpreted

> **A5 remains `PASS` under its currently frozen assertion, with A5-C / A5-W documenting incomplete
> coverage.**

A5's check asks whether a codec **string** (`h264`, `avc1`) leaked into a producer declaration. It does
**not** ask whether a value was **sourced from** codec configuration — which is exactly the case here.
After A5-W, the A5 gate may be amended to measure the real invariant and re-run; that is the correct
order, and doing it now would change the gate's meaning retroactively.

| Ref | Status |
|---|---|
| **A5-W** | **DECIDED — NO** (this section) |
| **A5-C** | OPEN — coverage gap; A5 cannot see provenance of a value |
| **A5-H** | OPEN, out of scope here — `handler_name` → `mdia/hdlr` is a fourth mechanism class |
| **G13-P / M / M2 / T** | CLOSED |
| **G13-R** | RETIRED |
| **G13-E** | DECIDED · 2.15 deferred |
| **T7** | **At risk** — its stream leg rests on `compressorname`, which A5-W disqualifies. Rebuildable on `trak/udta`; **not rebuilt here** |
| **A7/G13** | `FAIL` — awaiting implementation after the population is settled |

**No code, no gate change, no carrier change, no §2.1.17 amendment.** The gate remains
**`PASS 25 · FAIL 1 · HELD 5` — BLOCKED**.

  artifact evidence reference           A7 operates ONLY here
```

**Each layer has already falsified the one above it.** That is why A7 cannot be settled first: it
operates on the last layer, and the population reaching that layer is not yet fixed.

#### The evidence, narrowly stated

```text
  stsd / avc1
      ↓
  compressorname  =  'SomeOtherTool 9.9.9'   (Pascal string, length 19, well-formed)
      ↓
  PyAV surfaces it as  stream.metadata['encoder']
      ↓
  ProducerDeclaration(scope='video_stream', key='encoder', value='SomeOtherTool 9.9.9')
```

Controls `t1_base.mp4` and `declared_real.mp4` are **all zeros** in that field, so this is not ordinary
codec configuration.

#### The question, and its consequence either way

> **Does a codec sample-entry field qualify as an authorised producer-declaration mechanism?**

| Answer | Consequence |
|---|---|
| **NO** | **Upstream suppression.** `compressorname` → observable codec configuration → **not** a producer declaration → no `ProducerDeclaration` → **no A7 evidence obligation.** Conceptually cleaner than teaching a locator to address something that should never have entered the model. |
| **YES** | The value stands, and A7 must address it — at an address inside a **codec** structure, which would make `artifact:` cover sample-description fields. |

**No code, no gate change, no carrier change, no §2.1.17 amendment.** A5's `PASS` stands **unchanged
and provisional** — its check tests for codec *strings* in declarations, not for values **sourced from**
codec configuration (**A5-C**). Re-deriving A5 after A5-W settles is the correct order; changing it now
would alter the meaning of the gate after the fact.

The gate remains **`PASS 25 · FAIL 1 · HELD 5` — BLOCKED**, with A7/G13 still the sole blocker.

| Ref | Item | Owner |
|---|---|---|
| **G13-M2** | **CLOSED** — no mechanism in `stsd`; track scope `UNLOCATED` | **2.3** |
| **A5-C** | A5's check tests for codec *strings*, not for values **sourced from** codec configuration. The stream leg of the T7 fixture is sourced from `stsd` → `compressorname`, and A5 cannot see that. **Recorded; the row's `PASS` is qualified, not overturned** | **2.3** — gate coverage |
| **A5-W** | Whether a `compressorname`-sourced value may be recorded as a producer declaration at all. This is A5's normative question, and G13-E's "non-empty string from an observable mechanism" does **not** settle it — the mechanism is observable, but it is not a *declaration* mechanism | **2.3** |
| **G13-M** | **CLOSED** (§V.7.9) | **2.3** |
| **G13-T** | Matroska `<n>`: stream index or track number — still **OPEN**, independent of this | **2.3** |
| **G13-E** | **DECIDED** (§V.7.8); 2.15 implementation deferred | **2.15** |
| **G13-R** | **RETIRED** (§V.7.8) | — |

**No code, no gate change, no carrier change, no §2.1.17 amendment.** The gate remains
**`PASS 25 · FAIL 1 · HELD 5` — BLOCKED**, with A7/G13 still the sole blocker.

  no key observed                            -> absent
```

| Ref | Item | Owner |
|---|---|---|
| **G13-M** | **Decided above** | **2.3** |
| **G13-M2** | mp4 track-scope structure — needs a walker that understands `stsd` entries before row 3 can be proven | **2.3** — Step 4 |
| **G13-E** | **Decided** (§V.7.8); implementation is 2.15, deferred | **2.15** |
| **G13-R** | **Retired** (§V.7.8) | — |
| **G13-T** | Matroska `<n>`: stream index or track number | **2.3** — measurement |

**No code, no carrier change, no §2.1.17 amendment.** A7 remains `FAIL`; the gate remains
**`PASS 25 · FAIL 1 · HELD 5` — BLOCKED**.


#### Ordering consequence

G13-E is a **semantic prerequisite** for G13-M, as suspected: without it, G13-M could correctly say "only
locate observable declarations" while the extraction layer kept manufacturing declarations out of a
degradation. G13-M may now define:

> "These are the artifact locations corresponding to values the probe is **actually allowed to report**."

with "allowed to report" resolved by this record rather than by guesswork.

#### Recovery stays explicitly out of scope

A7 requires evidence **addressing**; it does **not** authorise **byte-level value recovery**. A locator
that finds `/moov/udta/meta/ilst/<key>` cannot recover the value the demuxer destroyed, because the
destruction happened in the demuxer, not in the bytes — the bytes still hold it. Reconstructing it would
be a **new, separately scoped technical decision** (read the value out of the artifact rather than
trusting the demuxer). It is **not** folded into the locator, and it is not implied by it.

| Ref | Item | Owner |
|---|---|---|
| **G13-E** | **Decided above.** Implementation of Q1–Q6 is 2.15 work once the carrier exists; it does **not** wait for A7 | **2.3** |
| **G13-R** | **Retired** — no arbitration rule is warranted | **2.3** |
| **G13-M** | Locator scope, now constrained by G13-P (exclude `/moov/udta/<key>`) and G13-E (only reportable values) | **2.3** |
| **G13-T** | Matroska `<n>`: stream index or track number | **2.3** — measurement |

**No code, no carrier change, no §2.1.17 amendment.** A7 remains `FAIL`; the gate remains
**`PASS 25 · FAIL 1 · HELD 5` — BLOCKED**.

| Family | Route | Status |
|---|---|---|
| Matroska / WebM | **R-a** — spec-pinned mapping, verified once by fixture | Cheap; may proceed |
| **mp4** | **R-b** — bounded tag locator, because no unverified table is truthful | **Mandatory**: it is the family the gate measures |

**Rationale.** R-a is not "less correct" — on Matroska it is fully correct, because the format pins the
location. But on mp4 the format does not pin it, so the only way to produce a truthful `artifact:`
address is to **verify** where the value actually lives. Verification *is* byte inspection; R-a and
R-b are not alternatives on mp4, they are a mapping plus the check that the mapping is true.

**Explicitly still rejected:**

* **R-c** — weakening `artifact:` into whatever PyAV exposes would let the implementation limitation
  redefine the specification. Same error as satisfying the old A9 check with a `"://"` proxy.
* **Adding `ProducerDeclaration.evidence_refs` now** — the field stays absent until a locator exists.
  An always-empty field would make the model *look* compliant while A7 still failed.

**Consequence for A7: unchanged, `FAIL`.** §V.1 and §2.1.17 are untouched. This record changes no
rule; it scopes the implementation obligation that 2.3 owns.

## What still has to be decided (2.3, not this record)

| Ref | Item |
|---|---|
| **G13-M** | Scope the bounded mp4 locator: which container boxes are descended, and what is done when a key is absent from all of them (must be "not located", never a default path). |
| **G13-R** | Whether a key found under **both** `udta/<key>` and `meta/ilst/<key>` (legal, and FFmpeg merges them) records one address or two. This is the same duplicate-precedence question v1.4's §3 step 4 left open for conflicts. |
| **G13-T** | mkv stream-scope tags address as `segment/tracks/<n>/tags/<TAG>` — `<n>` must be the **stream index**, not the track number, or the address will not resolve. Unverified; flagged rather than assumed. |

**A7 and A9 must NOT be merged into one §2.1 amendment**, for a reason now concrete rather than
stylistic: they are owned by **different documents** — the §2.1 envelope (`utils/confidence.py`) versus the
`stage2_source_description.md` field schema (`stage2_source_description.md:47`). The v1.1→v1.2 split is
what this project already paid for once.

**A7 carries a dependency note.** `stage2_1_contract_boundary.md` §2.1.16 was corrected in this pass: its
consumer table had required "a retained value without an addressable ref violates S-3", which imposed an
obligation resting on a grammar that does not exist. §2.1.16 now records that
`ProducerDeclaration` carries no `evidence_refs` at all and does not require one. **The boundary is the
point:** v1.3 says conflicts must stay observable; v1.4 defines what an addressable evidence reference
*is*. No field was invented to make prose true.

**G17 is fenced and remains so.** Nothing in this amendment specifies a spool, a descriptor, a quota or an
`fd://<n>` form. `RESOURCE_LIMIT` in V.1 names an **outcome**; its mechanism is `pending §2.16`. No commit
in a 2.3 change set may touch those behaviours, and the gate's `HELD` rows remain excluded from the tally
in code.

---

## V.8 — Closure audit of this amendment

Each line is checkable against the text above. **None of them is a claim that a gate check passed** — the
gate's verdict is computed independently in §V.9 and nothing here can move it.

| # | Check | Result |
|---|---|---|
| 1 | **Zero stale R3/R1/R2/R4/R5 wording** in the operative text | **PASS.** §2.3.14 → V.1; §2.3.12 → V.2; §2.3.4/5/6/7 → V.3; §2.3.11 → V.4.1; §2.3.13 → V.5.1; §2.3.2/§2.3.8 → V.5.2. The draft's Case A/B split, the A–D categories, the four-state vocabulary, and `encoder_tag` are each **deleted by name**, not silently left |
| 2 | **R4's reachability model is in §2.3.14** | **PASS.** V.1.2 states failure vs success states, the three ownership corrections, and the `REJ_*` closed-set rule |
| 3 | **Four-origin model intact** | **PASS.** `artifact_declared` · `muxer_authored` · `probe_observed` · `unavailable`, in V.3.2 and in the implementation |
| 4 | **`SourceInfo.version` omission rule intact** | **PASS.** V.5.2 states it as a freeze invariant; enforced by 13 R1–R9 tests and the gate's T4 |
| 5 | **No Builder version promoted to source version** | **PASS.** V.3.2's eligibility rule; the gate's A2/T6 test it on a real declared artefact |
| 6 | **A9 routed as a type dependency** | **PASS.** V.6.2, with the measured chain and the owning document named |
| 7 | **Fixture retirement condition has not fired** | **PASS.** `test_no_declaration_survives_by_being_written_as_a_tag` passes — R3's finding holds, so the injector stays |
| 8 | **G17 remains `HELD`** | **PASS.** V.1.2 marks the mechanism `pending §2.16`; V.7 restates the fence |
| 9 | **All cross-references resolve** | verified mechanically in §V.9 |
| 10 | **No acceptance criterion weakened** | **PASS.** A1–A12 and T1–T12 are untouched. Every restatement makes an obligation *stricter*; none relaxes one |
| 11 | **Implementation and specification ownership agree** | **PARTIALLY — and this is the finding, not a pass.** A8/T8's *specification* half is now written, but the code half (`ingestor.py:70-73`) is unchanged and `IMPLEMENTATION_MIGRATION_REQUIRED`. The two halves disagree until 2.15 runs |

Line 11 is the honest result of this pass: **the amendment moved the specification forward and the
implementation did not follow, because the implementation is 2.15's.** That is the correct division, and
it is why the gate's A8/T8 stay `FAIL` rather than turning green because the prose improved.

### V.8.1 What this pass did *not* do

- It did **not** touch `src/`. 53/53 before and after.
- It did **not** add `conflicting` to `ObservationState`.
- It did **not** adopt an `evidence_refs` grammar.
- It did **not** relax, defer, or re-scope any acceptance criterion.
- It did **not** convert a single `HELD` row.

## V.9 — Post-amendment evidence

> **This block records the Part V pass as it stood at the time, and is left unedited as history.**
> The tally below was correct for the Part V document-only amendment. A **later** pass — §2.1.16's
> `conflicting` member plus the A5/T7 re-measurement — moved it to `PASS 22 · FAIL 4 · HELD 5`,
> `BLOCKED -- 4`. See **§V.7.1** for that change and **§V.9.2** below for the current figures. The
> "expected UNCHANGED" reading is the correct one *for Part V* and is deliberately not retrofitted.

```text
specification   docs/specs/stage2_3_container_probe.md
                Part V added; Part I retained verbatim as the audited baseline
                9 clauses restated, 4 named constructs deleted, 2 dependencies recorded

tests           python -m pytest -q  ->  53 passed   (25 pre-existing + 9 + 13 + 6; src/ untouched)

gate            python _s23_verification.py
                TALLY  PASS 20 · VACUOUS 1 · FAIL 4 · NOT-IMPLEMENTED 1 · HELD 5
                GATE: BLOCKED -- 6 check(s) not satisfied. Stage 2.3 is NOT freezable.

expected        UNCHANGED, and that is the point: the gate measures the SYSTEM, and
                this pass changed only the DOCUMENT. A specification amendment that
                moved the tally would itself be evidence that a check had been
                satisfied by prose rather than by demonstration.
```

### V.9.2 Current evidence (supersedes the block above, which stays as history)

```text
specification   §2.1 CLOSED at v1.3 (stage2_1_contract_boundary.md §2.1.16)
                2.3 specification UNCHANGED by that amendment

tests           python -m pytest -q  ->  92 passed, 26 subtests  (53 pre-existing + 39 new)

fixtures        python _s23_fixture_inject.py
                two-scope conflict artifact rebuilt from scratch and frame-verified
                container 'HandBrake 1.6.0 2023041600' vs stream 'SomeOtherTool 9.9.9'

gate            python _s23_verification.py
                TALLY  PASS 25 · FAIL 1 · HELD 5
                GATE: BLOCKED -- 1 check(s) not satisfied. Stage 2.3 is NOT freezable.
                moved:  A5  VACUOUS-PASS  -> PASS   (S2.1.16 conflicting)
                        T7  NOT-IMPLEMENTED -> PASS  (two-scope fixture)
                        A9  FAIL -> PASS (re-blocked once, then PASS)  (v1.1 + v1.2)
                        A8  FAIL -> PASS (re-blocked once, then PASS)  (S V.1 R-2)
                        T8  FAIL -> PASS                                   (S V.1 R-2)
                still:  A7 FAIL · G17 HELD

the last blocker
                A7 alone. Its SPECIFICATION is closed -- S2.1.17 (v1.4) defines the
                address grammar. What remains is EMISSION: no artifact:-located ref
                is produced. That obligation is the probe's, not the grammar's, and
                S2.1.17 E-6 deliberately did not assign it to a carrier.

checks that were rejected before acceptance
                A9  reached PASS with display_aspect_ratio='0:1' still emitted, because
                    the sentinel tuple could not see "0:1". Rejected; check corrected
                    FIRST; corrected check then FAILed naming the field.
                T8  reached "raised" through a bare `except` that was swallowing a
                    NameError in the check itself -- a false negative blaming the
                    implementation. Rejected; fixed to report the real exception.
                Both were green-or-failing for reasons other than the truth. See V.7.3.

evidence        python _s23_dbg.py   (prints the real contracts for all five paths)
                SUCCESS          probe_state=<absent>     producer_state=extracted
                UNREADABLE x2    probe_state=unreadable    producer_state=unavailable
                NO_VIDEO_STREAM  probe_state=no_video_stream producer_state=unavailable
                REJECTED_BY_POLICY probe_state=rejected_by_policy producer_state=unavailable

still open      G18-R  partial contracts that DID read container metadata report
                producer_state=unavailable while retaining real declarations. R-2's
                wording says unavailable; the evidence says they were observed. R2.3
                (S V.1) owns the wording. NOT silently changed. See V.7.4.
                ingestion_status (S2.1.5 gate, S2.1.9 row 409) is a SEPARATE row and
                is still not implemented. R-2 records on the group; it does not build
                the S2.1.5 gate.
```

### V.9.1 The closure decision

Per the stated criterion — *if any 2.3-owned item remains open, do not freeze*:

| Question | Answer |
|---|---|
| Is any 2.3-owned **specification** work open? | **No.** All nine restatements are written; G9 and G11 are closed by V.4.2 and V.5.3 |
| Is any 2.3-owned **implementation** work open? | **No.** Nothing in `src/` is owed to 2.3; the remaining code work is `IMPLEMENTATION_MIGRATION_REQUIRED`, owned by 2.15 |
| Who owns the 6 gate blockers? | **See §V.7 — item by item, from the G-register.** Not summarised here by category, and not by tally. Several are multi-owner or cross-boundary, which is exactly the classification that produced two routing errors earlier (§H.8.1, §H.9.2) |

**Stage 2.3 is therefore freezable as a SPECIFICATION, and must not be frozen as a CLOSED STAGE.** The
distinction is recorded rather than collapsed:

```text
Stage 2.3 — SPECIFICATION: CLOSED at v2.3-a1   (Part V; 9 clauses restated, 4 constructs deleted)
            STAGE:          NOT CLOSED

Six blocking findings remain, with their ownership and dependencies recorded in §F.6
and restated in §V.7. G17 remains HELD under §2.16.

Freezing the specification is the honest act available. Declaring the stage closed
would require the gate to PASS, and it does not — and it must not be made to.
```

**The closure statement above deliberately carries no ownership tally.** A count such as "§2.1 ×3" is a
*summary of §V.7*, and a summary is what drifted from the register twice in this audit. §V.7 is the
authority; if it and any summary disagree, §V.7 is right.

**§2.1 v1.3 was the next owner, and it has now run** — §2.1.16 established `conflicting`, and A5 and T7
were re-measured to `PASS` rather than declared closed (§V.7.1). Remaining blockers keep their recorded
owners: **A7** and **A9** are §2.1's, **A8/T8** are 2.15's, **G17** stays under §2.16. In parallel and under
2.15, the A8/T8 branch split and the A9 type change. **Not Stage 2.4** — §2.4's inputs are keyed to §2.1.4
Dimension A/C rules that 2.3's restatement now consumes but does not yet own.

### V.4.2 §2.3.9 restated — categories are deleted, origin + scope replace them

The draft's categories (A) Container-declared, (B) Stream-declared, (C) Producer-declared, (D)
Probe-generated **re-invent what `SourceLayer` already encodes**, and a second origin carrier is
prohibited by §2.3.2's own rule. They are replaced, not reworded:

```text
§2.3.9 — Technical metadata classification

Category labels (A)-(D) are DELETED. In their place, every producer-related
observation carries the (scope, origin) pair defined in §2.3.7.

  SourceLayer        the §2.1 vocabulary, unchanged. 2.3 consumes it.
  (scope, origin)    the §2.3.7 addition, for producer-related values only.

  Measured non-conformance this replaces: category-D material was being emitted as
  `layer: source_native` with `state: extracted` — material the probe generated,
  labelled source-native and marked extracted. That is exactly what the draft's closing
  sentence forbids, and the labels are what made it invisible.
```

version→release table owned by nobody, and a stale table silently yields false producer identity.

