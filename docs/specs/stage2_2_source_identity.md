# STAGE 2.2 — Contract #1: Source Identity

**Stage:** 2 | **Sub-section:** 2.2 | **Contract:** #1 `SourceDescription`
**Status:** SPECIFICATION CLOSED ✅ — seven-consumer freeze test passed 7/7 (§F.3.5); blocker G8 closed by §2.1 amendment v1.2 (§2.1.15). Implementation and tests remain NOT STARTED (2.15)
**Governs:** §2.1 discipline applies in full (tiers, states, stability, naming, codes)

> Source identity answers "which exact bytes did we read, and where did we get them" —
> nothing about what the bytes *mean*. It is the only part of Contract #1 that is allowed to
> be content-addressed, and it is the anchor for caching, deduplication, lineage, and storage.

---

# PROJECT STATE — Stage 2 progression

> **2.1 is CLOSED v1.2** (two controlled amendments: §2.1.14 code set → v1.1; §2.1.15 envelope
> vocabulary → v1.2). The discipline below is frozen at v1.2: do not re-derive it, do not re-argue it.

```text
Stage 2.1  ── CLOSED ✅ v1.2  (REJ_* set is v1.1; envelope vocabulary is v1.2 — §2.1.15)

Stage 2.2  ── SPECIFICATION CLOSED ✅  (seven-consumer freeze test passed 7/7 — §F.3.5)
  Specification ── CLOSED — every consumer consumes the frozen contract without inventing a rule
  Contract      ── CLOSED as specification (§2.2.1–§2.2.5); the JSON Schema ships with 2.15 per §2.2.5
  Implementation ── NOT STARTED — register rows 1–12 + 24 are the 2.15 migration list; no src/ change
  Tests          ── NOT STARTED — existing 25 tests green; §E identity/version tests not yet written

  G1 ── RE-HOMED (fd://<n> canonical form → §2.16; no consumer blocked)
  G2 ── CLOSED AS DECISION (deletion scoped §2.2A.4; model change at 2.15)
  G3 ── SPEC-SIDE CLOSED ✅ (ladder §2.2B + trace §F.3.1)
  G4 ── SPEC-SIDE CLOSED ✅ (matrix §2.2A + freeze audit §F.3.2; fd form + spool quota → §2.16)
  G5 ── CLOSED ✅
  G6 ── CLOSED ✅ (integrity §2.2.2; failure-map half is normative in §2.2B)
  G7 ── MIGRATION-MAPPED ✅ (per-kind map §2.2A.3; lands at 2.15)
  G8 ── CLOSED ✅ via §2.1 controlled amendment v1.2 (§2.1.15) — 2.2 invented no version carrier

Stage 2.3 ── UNBLOCKED — may begin, constrained by frozen source_kind + §2.2A.4 allow/deny lists
```

Order of work: **2.2's specification is closed; 2.3 may begin.** What is deferred is *not* a 2.2 gap:
register rows 1–12 + 24 are the 2.15 migration, rows 21–22 are §2.16's, row 23 is Stage 4's. Still
binding on 2.3: no `source_identity` implementation, and **no Container probe designed as though the
input is necessarily a local filesystem path** (§2.2A.4).

> **Chain format for every amendment (mandatory).** Each amendment below is recorded as:
> Decision → Affected contract field → Affected producer → Affected consumer → Affected
> invariant → Affected failure code → Affected test → Downstream stages affected.
> A prose fix without this chain is incomplete: an old assumption will otherwise survive in
> the implementation or in a later contract.

---

## 2.2.1 The `source_identity` block (normative)

```yaml
source_identity:
  source_kind: local_file                     # REQUIRED, T1, stable
  hash_sha256: "e3b0c44…64 hex chars…8fa2"   # REQUIRED, T1, stable
  size_bytes: 8123456                        # REQUIRED, T1, stable
  original_filename: "clip_04.mp4"           # REQUIRED (local_file/object_uri) or null (stream_handle), T1, stable
  source_path: "/data/uploads/clip_04.mp4"   # REQUIRED, T1, stable-per-run
```

The name is **`source_identity`** — never `source` (see §2.1.7: `source` is the reserved §6
envelope key, already shipped inside every field group).

| Field | Type | Tier | Allowed states | Stability | Requirement | Producer | Consumers |
|---|---|---|---|---|---|---|---|
| `source_kind` | enum: `local_file \| object_uri \| stream_handle` | T1 | extracted | stable | REQUIRED | ingestion (input classifier) | identity semantics, cache policy, Decoder open-path, Stages 15/16 |
| `hash_sha256` | string, 64 lowercase hex | T1 | extracted (unavailable → §2.1.5 step 3) | stable | REQUIRED | filesystem + hasher | cache, storage, lineage, debugging, dedup |
| `size_bytes` | integer, bytes, ≥ 0 | T1 | extracted | stable | REQUIRED | `os.stat` (deprecated at container level — see §2.2.7 G2) | ingestion gate, storage, cache |
| `original_filename` | string (verbatim) \| null | T1 | extracted (null only per 2.2.3 r1) | stable | REQUIRED for `local_file`/`object_uri`; null (OPTIONAL, "not applicable — no name exists") for `stream_handle` | upload/API layer | UX, audit, debugging |
| `source_path` | string, absolute path \| object URI \| `fd://<n>` | T1 | extracted | stable **per run** | REQUIRED | ingestion | Decode (locate bytes), storage linkage |

`source_path` is stable only within a single deployment's storage layout — it must **never** be
used as a cache or dedup key. The hash is the only cross-machine identity.

> **CLOSED G5 — fidelity.** The `source_identity` block is `fidelity: preserved`. Byte-exact
> content and verbatim naming must survive unchanged from ingestion into every downstream
> contract that references the source. Chain: Decision (2.1.4 fidelity axis applies to identity)
> → field: whole `source_identity` block → producer: ingestion hasher/stat/classifier →
> consumer: Stages 13 (DNA assembly) and 15 (storage lineage), cache keys, Decoder input locator
> → invariant: `preserved` means content-addressed bytes are never rewritten downstream →
> failure: silent rewrite surfaces as `REJ_SOURCE_CORRUPT` on lineage re-verification →
> test: §E-1 golden-hash + §E-2 cross-path equality → downstream: all 12 contracts' lineage refs.

## 2.2.2 Hashing rules (normative)

> **CLOSED G6 (integrity half).** Hashing and parsing the same path are **one pipeline
> transaction**: after the hash pass, the file MUST be re-statted immediately before the parse
> pass, and any size/mtime disagreement aborts to `REJ_SOURCE_CORRUPT` with a partial contract.
> This extends the existing size-agreement rule (r3) across the hash→parse handoff. The hash
> therefore attests to *exactly the bytes the parser then reads* — a correctness boundary,
> not a security enhancement. Remaining half (failure-code mapping: `os.stat` errors →
> `REJ_FILE_UNREADABLE`, never an unhandled exception; re-hash-before-reuse of rejected identities)
> is a §2.16 producer rule, tracked as an §E test item, not a new code path yet.

1. **Algorithm:** SHA-256 over the *entire byte stream* of the file as read at ingestion time.
2. **Streaming:** hash in 1 MiB chunks while reading; never load the whole file into memory.
   (hashlib/sha256 appear **nowhere** in the current code — this is new work, §2.1.9.)
3. **Size agreement:** the byte count consumed while hashing must equal `os.stat` size.
   Mismatch (file changed mid-read) → `REJ_SOURCE_CORRUPT` with a partial contract.
4. **Identity-first:** the hash is computed at §2.1.5 evaluation step 1. Even a source later
   rejected for duration or codec **still carries its full identity** — a 60-second rejected
   file is still hashable, and that hash is what lets a later, higher-limit pipeline or a new
   decoder version find it again.
5. **Unreadable bytes:** if hashing itself fails after the file passed step 1 (disk error,
   permissions revoked mid-read) → `REJ_FILE_UNREADABLE`. This is the one place where
   `state: unavailable` is legitimate at the *group* level for `hash_sha256`.

## 2.2.3 Filename policy

1. `original_filename` is stored **verbatim** — it is an audit fact, not a filesystem operation.
   It is REQUIRED for `source_kind ∈ {local_file, object_uri}` and `null` for `stream_handle`
   (OPTIONAL, "not applicable — no name exists"). The old empty-string carve-out is deleted:
   an empty string is a failed name, not a kind of name, and `""` never satisfies REQUIRED.
2. Sanitisation, collision handling, quarantine, and storage layout are **API/storage concerns**
   (Stages 15/16), not identity concerns. Contract #1 records; it does not sanitise.
3. The filename must **never** be used for format detection (§17, §30). `"clip.mp4"` tells the
   Builder nothing until the container probe speaks. A `.mp4` extension on a WebM container is
   expected behaviour for this field (faithfully recorded) and a `WARN_CONTAINER_VARIANT` at
   the container step (2.3).

## 2.2.4 Identity and caching

Per §37 and §2.1.4 Dimension C:

- `source_identity` (hash + size) is the **cache key** for a persisted `SourceDescription`.
- Stable facts may be served from cache indefinitely for an immutable hash.
- `estimate` fields (FPS, CFR/VFR verdict, presentation duration, heuristics) are valid cache
  hits **only if** the cached record's producer versions match the current runtime. The carrier is
  **`provenance[].tool_version`** (plus **`.model_version`** where a model produced the value), and
  the comparison is **exact equality with no `unknown` hit**, per §2.1.15 R5 — v1.2 of §2.1 named
  these fields; before that this rule had no referent (finding G8). Mismatch → recompute the
  estimates, keep the stable facts.
- The hash does not version the *analysis*. Re-running with new models produces a new
  processing lineage under the same source hash (see §2.1.3).

## 2.2.5 JSON Schema fragment

```json
"source_identity": {
  "type": "object",
  "required": ["source_kind", "hash_sha256", "size_bytes", "original_filename", "source_path"],
  "additionalProperties": false,
  "properties": {
    "source_kind":       { "type": "string", "enum": ["local_file", "object_uri", "stream_handle"] },
    "hash_sha256":       { "type": "string", "pattern": "^[0-9a-f]{64}$" },
    "size_bytes":        { "type": "integer", "minimum": 0 },
    "original_filename": { "type": ["string", "null"] },
    "source_path":       { "type": "string", "minLength": 1 }
  }
}
```

The full `SourceDescription` JSON Schema (with `schema: {name: "SourceDescription",
version: "1.0"}` per §46) ships with the complete 2.15 schema. Version policy: a change to any
REQUIRED field or any state vocabulary is a **major** bump; adding an OPTIONAL/ABSENT-ALLOWED
group is a **minor** bump. Migrations stay explicit per Stage 1 D5.

## 2.2.6 Exit criteria

> **Split by the freeze pass (§F.3.3/F.3.5):** every unchecked item below is a
> `IMPLEMENTATION_MIGRATION_REQUIRED` row of the divergence register → it lands with the **2.15**
> schema/migration and does **not** block specification closure. The one item that *did* block
> closure — **G8** (§F.3.4), a §2.1 envelope-vocabulary amendment — is closed at the §2.1 layer by
> **v1.2 / §2.1.15**; 2.2 gained no field from it, which was the test. Code-side items stay
> "→ 2.15 migration" so none reads as silently satisfied.

- [ ] `_compute_identity()` implemented (sha256 streamed, size agreement check, filename capture)
- [x] G5 fidelity — `fidelity: preserved` written into §2.2.1
- [x] G6-integrity — single-transaction hash→parse rule written into §2.2.2
- [ ] `SourceIdentity` model added; `SourceDescription.source_path` relocated into it; G2 applied
- [ ] Hash of the same file is identical across runs/machines; copy has same hash, different path
- [ ] Truncated-while-reading file yields `REJ_SOURCE_CORRUPT` with a partial contract
- [ ] Filename-vs-container mismatch yields `WARN_CONTAINER_VARIANT`, never a rejection
- [ ] G4 input-scheme matrix implemented (`local_file` / `object_uri` / `stream_handle`),
      Decoder accepts `source_identity` — not a raw path (G7)
- [ ] §2.1.12 unaffected: no field added here lacks a producer and a consumer
      (`source_kind` producer: ingestion input classifier; consumer: identity semantics +
      cache policy + Decoder open-path + Stages 15/16)
- [x] G8 consumed, not invented: the version carrier is §2.1.15's (`provenance[].tool_version` /
      `.model_version`, `SourceInfo.version`); §2.2.4 now names those fields and adds none of its own
      — the model change is register row 24 → 2.15

---

## 2.2.7 Completeness gate record

**Gate verdict: 2.2 was OPEN — now CLOSED for specification, still do not implement.** *(Final
freeze pass: the single blocker, **G8**, was classified `SPECIFICATION_CHANGE_REQUIRED` (§F.3.3 row
13), routed to the layer that owned the rule, and closed by §2.1 controlled amendment **v1.2**
(§2.1.15). The freeze test re-ran 7/7 PASS (§F.3.5). The "~85% complete" estimate below is
superseded by that classified register; the §F.1 ledger supersedes the "G1–G6 amended" shorthand in
§C. Implementation (#3) and verification (#4) remain absent **by decision** — they are the 2.15
migration, not a 2.2 gap.)*
 The specification is internally
coherent and ~85% complete, but the audit below finds **6 required amendments** (one is a
genuine spec contradiction), 2 integrity/security items that must be resolved before any
implementation, and a set of explicitly-tracked open items. Implementation completeness (#3)
and verification completeness (#4) are both absent: there is no hashing code, no
`SourceIdentity` model, and no identity tests in the repository.

Evidence basis: `sha256|hashlib|blake2` → 0 hits repo-wide; `MIN_DURATION|min_duration` → 0
hits; `unavailable` → 1 hit (a decoder comment only). `size_bytes` lives in
`models/source_description.py:32` and `ingestion/ingestor.py:203` (inside `container`);
`source_path` flows `ingestor.py:156 → models/source_description.py:181 → decode/decoder.py:45`
(which opens it blindly) and `tests/test_pipeline.py:79`. `original_filename` exists in **no**
implementation file — docs only.

### A. Dimension verdicts (29/29 checked)

> **Amendment pass applied:** G5 closed in §2.2.1 (fidelity note) and G6-integrity closed in
> §2.2.2 (single-transaction rule). Dimension rows 12 and 25 below retain their audit-time
> verdicts for the record; the fixes are the quoted amendments.

| # | Dimension | Verdict | Note |

| # | Dimension | Verdict | Note |
|---|---|---|---|
| 1 | Purpose | ✅ pass | "which exact bytes, and where" — nothing about meaning |
| 2 | Boundary | ✅ pass | D-5 respected; Stages 15/16 owned items named |
| 3 | Inputs | ⚠️ gap | file/URI/fd named, but per-scheme producers undefined → **G4** |
| 4 | Outputs | ✅ pass | 4 fields + schema fragment |
| 5 | Field semantics | ✅ pass | table + filename/hash/size policies |
| 6 | Type | ⚠️ gap | filename charset + path canonicalisation undefined → **O1**, **G4** |
| 7 | Requirement | ❌ fail | `original_filename` REQUIRED contradicts the empty-string carve-out and the §2.1.4 orthogonality table → **G1** |
| 8 | Observation state | ⚠️ gap | group-level semantics for `hash_sha256: unavailable` unclear → **G3** |
| 9 | Stability | ✅ pass | + cache policy in §2.2.4 |
| 10 | Confidence | ✅ pass | T1 inherits group-level; nothing to compute |
| 11 | Provenance | ✅ pass | producers listed per field |
| 12 | Fidelity | ❌ fail | no fidelity label on the block; identity must be `preserved` → **G5** |
| 13 | Ownership | ✅ pass | consumers listed per field |
| 14 | Dependencies | ✅ pass | Decode/Storage/cache/lineage named; Job surfacing → **O8** |
| 15 | Failure modes | ⚠️ gap | TOCTOU hash-then-parse window; `os.stat` failure mapping → **G6** |
| 16 | Rejection rules | ✅ pass | maps cleanly onto §2.1.5 codes |
| 17 | Warning rules | ✅ pass | `WARN_CONTAINER_VARIANT` named |
| 18 | Ambiguity | ✅ pass | same-hash/different-name expected; copies defined |
| 19 | Missing information | ⚠️ gap | empty-name carve-out vs REQUIRED; hash-unavailable path → **G1**, **G3** |
| 20 | Normalisation | ⚠️ gap | filename encoding + path canonicalisation → **O1**, **G4** |
| 21 | Units | ✅ pass | bytes; 64-hex; no geometry in this section |
| 22 | Versioning | ⚠️ open | schema block deferred to 2.15 (tracked); hash-agility → **O6** |
| 23 | Caching | ✅ pass | key/estimate-invalidation rules present; negative caching → **O7** |
| 24 | Reproducibility | ⚠️ gap | cross-machine equality claimed but no golden-hash fixture defined → test gaps |
| 25 | Security/integrity | ❌ fail | TOCTOU; blind path open in Decoder; display-escaping ownership → **G6**, **G7**, **O1** |
| 26 | Performance | ✅ pass-with-note | full-file hash acknowledged as deliberate identity-first cost; single-pass optimisation deferred to §2.16 |
| 27 | Testing | ❌ fail | zero identity tests exist; gap list in §E below |
| 28 | Downstream impact | ✅ pass | ledger in §C below |
| 29 | Acceptance criteria | ⚠️ gap | §2.2.6 exists; must absorb the new test gaps + amendments before sign-off |

### B. Cross-stage consistency ledger

| Pair | Verdict |
|---|---|
| 2.2 ↔ Stage 1 §6/§9.1 (via §2.1) | ✅ conforms — vocabulary, `source`-is-reserved, envelope inheritance all respected |
| 2.2 ↔ §2.1.3 (three identities) | ✅ conforms — hash/size filed under source identity |
| 2.2 ↔ §2.1.5 (codes/order) | ✅ conforms — step-1 hashing; `REJ_FILE_UNREADABLE`/`REJ_SOURCE_CORRUPT` mapped |
| 2.2 ↔ §2.1.7 (naming) | ✅ conforms — `source_identity` used, `source` untouched |
| 2.2 ↔ §2.1.9 (migration) | ✅ conforms — `source_path` relocation already listed |
| 2.2 ↔ old `stage2_source_description.md` | ⚠️ **G2**: `container.size_bytes` (model:32, ingestor:203) will duplicate `source_identity.size_bytes` after migration — single source of truth required before 2.3 |
| 2.2 ↔ Decoder (`decoder.py:45`) | ⚠️ **G7**: opens the path string blindly; must migrate to `source_identity.source_path` + scheme allowlist |
| 2.2 ↔ Pipeline recovery | ⚠️ **O8**: lineage joins need the hash surfaced (currently only `input_path` on `Job`) |
| 2.2 ↔ Generator (future) | 🔒 locked now: `original_filename`/`source_path` must never enter Generator inputs; lineage by hash only (**O5** resolved as rule) |
| 2.2 ↔ §2.15 (schema) | tracked — full schema + `schema.version` policy stated in §2.2.5 |
| 2.2 ↔ Stages 15/16 (storage/API) | sanitisation, layout, dedup-store, redaction explicitly theirs, not silent |


### C. Required amendments — status after this pass

| ID | Status | Record |
|---|---|---|
| **G5** | ✅ **CLOSED** | fidelity: `preserved` notes added to §2.2.1 table area and planned for the §2.2.5 fragment body (fragment gains a `"fidelity": "preserved"` sibling in §2.15; fragment shown here is unchanged pending the full-schema assembly, per the "subordinate doc" rule) |
| **G6-integrity** | ✅ **CLOSED** | single-transaction hash→parse rule written into §2.2.2 (extends r3) |
| **G6-failure-map** | ⬜ OPEN, re-homed | `os.stat`/I/O mapping → §2.16 producer rule + §E test; no code path exists to change yet |
| **G1** | ⬜ OPEN, amendment drafted | `source_kind` added to §2.2.1 table + YAML + JSON fragment; filename nullability rewritten in §2.2.3 r1; empty-string carve-out deleted. Remaining: G4's `fd://<n>` form definition and the §2.1.4 nuance (REQUIRED-field-with-nullable-name) to be stated in the 2.15 field inventory, since G4 owns the handle semantics |
| **G2** | ⬜ OPEN, scoped | deletion of `container.size_bytes` recorded; code untouched until the 2.15 migration (deliberate — avoids a half-migrated contract) |
| **G3** | ⬜ OPEN | §2.2.2 r5 procedure stands; needs the "terminal-diagnostic only" clause elevated into §2.1.5 rejection semantics on the next pass |
| **G4** | ⬜ OPEN (blocks 2.3) | full per-scheme table deferred to §2.16, but `source_kind` + `fd://<n>` placeholder are now normative so 2.3 cannot assume a filesystem path |
| **G7** | ⬜ OPEN / downstream | exit criteria now require the Decoder migration; `decoder.py:45` blind open unchanged until the model lands |

### D. Superseded amendment prose (kept one turn for diff review — delete on next pass)

> The G1–G6 paragraphs below are superseded by §C and by the amended §2.2.1–§2.2.5.
> The live definitions are the amended sections, not these paragraphs.

**G1 — resolve the filename contradiction.** `original_filename` is declared REQUIRED while §2.2.3
permits an empty string for fd-like sources. Under §2.1.4 this is incoherent: a REQUIRED field
may only be `extracted`. Resolution: introduce `source_kind: local_file | object_uri |
stream_handle` (REQUIRED, T1, stable) on the block. For `local_file`/`object_uri` the name
policy is unchanged; for `stream_handle`, `original_filename` becomes `null` (OPTIONAL, "not
applicable — no name exists") and `source_path` uses `fd://<n>` form, defined in G4. Delete the
empty-string carve-out.

**G2 — single source of truth for size.** `container.size_bytes` (`models/source_description.py:32`,
`ingestion/ingestor.py:203`, `tests/test_pipeline.py:81`) must be **removed** when
`source_identity.size_bytes` lands; size is identity evidence, not container metadata. Recorded
for the 2.15 migration; no code touched yet.

**G3 — define `hash_sha256: unavailable`.** Amend §2.2.2 rule 5: (a) hash even when later steps
will reject — identity-first (§2.2.2 r4) applies to every step-1-passed path; (b) `unavailable`
is emitted *only* when the read itself fails after step-1 checks passed → `REJ_FILE_UNREADABLE`,
partial contract, identity group present with `size_bytes` from the pre-read `os.stat`;
(c) post-rejection, identity is terminal-diagnostic only.

**G4 — input-scheme matrix.** §2.2.1 names three producers without defining them. Required table
(local_file / object_uri incl. query-string and percent-encoding policy: canonicalise or byte-hash
the raw bytes as received, stated once / stream_handle incl. one-shot-stream rule: hash consumed
bytes during a mandatory local spool, never twice, stated in §2.16) with columns: producer, name
source, path/canonical form, `size_bytes` meaning (unknown-until-EOF allowed as `unavailable`
mid-stream), hash domain, state rules.

**G5 — fidelity label.** Add to §2.2.1 and the §2.2.5 fragment: the `source_identity` block is
`fidelity: preserved`. Exact bytes and names must survive into every downstream contract that
references the source.

**G6 — integrity/security rules.** (a) TOCTOU: hashing then parsing the same path is one pipeline
transaction — re-stat before parse, mismatch → `REJ_SOURCE_CORRUPT` (extends §2.2.2 r3);
(b) `os.stat` failures map to `REJ_FILE_UNREADABLE`, never an unhandled exception;
(c) rejected identities may linger for diagnostics but must be re-hashed before reuse.

### D1. Live open items ("not yet determined" — must stay visible)

| ID | Item | Owner |
|---|---|---|
| O1 | Filename/scheme string policy: UTF-8 normalisation form, max-length guard, control-character handling; display-escaping stays Stages 15/16-owned | **RESOLVED by §2.2.3 ✅** — the identity layer stores **verbatim**: no normalisation form is chosen, no truncation, no escaping, no control-character rewriting (an audit fact, not a filesystem operation). Consequences that are *not* identity concerns re-homed: length/column limits, sanitisation, quarantine, display-escaping → **Stages 15/16** (tested there, §E.3) |
| O2 | `REJ_FILE_UNREADABLE` vs `REJ_SOURCE_CORRUPT`: §2.1.5 must state the discriminator (I/O layer error vs content/parse failure after step 1) | **CLOSED ✅** — discriminator is the detection layer, stated in §2.2B.2 and frozen by §2.1 v1.1's non-overlap table (§2.1.14) |
| O3 | Object-storage integrity: server-side ETag/hash compare when offered; divergence → `REJ_SOURCE_CORRUPT` | 2.3+ |
| O4 | Upper size bound / spill policy for very large single-pass hashes | §2.16 pipeline design |
| O5 | Generator boundary: RESOLVED as rule — `original_filename`/`source_path` never enter Generator inputs; lineage by `hash_sha256` only | locked (§B) |
| O6 | Hash agility: algorithm name must be schema-carried in 2.15; no second hash field now | 2.15 |
| O7 | Negative caching: recommended to cache the *decision* keyed by hash+schema version with TTL, not the contract | Stages 15/16 |
| O8 | Surface `source_identity.hash_sha256` on pipeline/job recovery views (`Job` carries only `input_path` today) | Stages 16/19 |

### E. Verification gaps (→ re-homed: the 2.15 identity test set, not a 2.2 spec blocker)

Identity currently has **zero tests** — these must all exist. Originally worded "before 2.2
sign-off"; under the closure rule agreed for this stage (implementation lag does not block
specification closure, §F.3.5) these become the **acceptance set for the 2.15 implementation**, and
they join §2.1.15 §7's version tests 1–8 as one list. Recorded here so nothing is dropped:

1. Golden-hash: a fixed fixture file asserts the exact expected SHA-256 (encoding/read-order regression tripwire; also the reproducibility proof for dimension 24).
2. Cross-machine equality: same bytes at a different path → equal hash, different path/filename.
3. Adversarial filenames: `../../etc/passwd`, absolute paths, UNC paths, 400-char names,
   emoji/CJK — recorded verbatim, Builder never touches the filesystem with them
   (sanitiser lives in Stages 15/16, tested there).
4. Missing-file and empty-file contracts: `REJ_FILE_NOT_FOUND` / `REJ_FILE_EMPTY` partial
   contracts whose identity group contains no hash.
5. Read-write open mode: no mode that truncates or mutates the source is ever opened by ingestion.
6. Symlink chain: resolve-or-refuse per the recorded policy; hashed bytes = read bytes either way.
7. 29.999 / 30.000 / 30.001 and 0.999 / 1.000 / 1.001 duration boundaries — identities intact on
   the rejected boundary cases (ties the gate to §2.13 early).
8. Concurrent dual ingestion of the same file: two independent contracts, identical hash.

### G. Gate closure criteria for §2.2 — disposition at closure

> *Label note: this subsection is deliberately lettered **G**, not F. In this document **§F** means
> the cross-stage freeze appendix (F.1–F.3), and one label must not carry two meanings — that is how
> silent divergences start.*

1. ✅ G1–G8 amended into §2.2.1–§2.2.5 / §2.2A / §2.2B, or re-homed with an owner — ledger in §F.1.
   This section does not survive into implementation unchanged, as predicted.
2. ✅ O1–O8: O1 resolved by §2.2.3, O2 closed (§2.2B.2 + §2.1 v1.1), O5 locked (§B); O3 → 2.3+,
   O4 → §2.16, O6 → 2.15, O7 → Stages 15/16, O8 → Stages 16/19. **None silently dropped.**
3. ⏳ → **2.15 acceptance set.** §E tests 1–8 + §2.1.15 §7 tests 1–8 are *implementation* gates;
   they cannot pass before code exists, and under the closure rule they do not block the
   specification. Register row 18 tracks them so the deferral is visible, not assumed.
4. ✅ §2.2.6 updated: spec-side items checked, code-side items explicitly marked "→ 2.15
   migration" by the note at its head; the golden fixture and adversarial-filename cases now live
   in §E's re-homed acceptance list.
5. ✅ §2.1.12 re-checked: `source_kind` has a named producer (ingestion input classifier) and named
   consumers (identity semantics, cache policy, Decoder open-path, Stages 15/16); no orphan fields,
   and 2.2 still adds no field without a consumer — G8 was closed in **§2.1**, not by growing #1.

**Disposition: criteria 1, 2, 4, 5 hold; criterion 3 is re-homed to 2.15 with its tests enumerated.
On that recorded basis §2.2's SPECIFICATION is CLOSED and its implementation remains explicitly out of
scope until 2.15** — which is the same conclusion §F.3.5 reaches by the consumer route, from the
other direction.

---

## 2.2A Input-scheme matrix (normative — closes the G4 core; the cross-stage audit §F.3.2 passed 7/7)

> `source_kind` is not an enum label. It is a **behavioral contract**: each kind fixes what
> identity acquisition can rely on, who owns the byte lifecycle, when `size_bytes` is knowable,
> and what every downstream stage may assume. Anything a stage invents beyond its column below
> is a spec violation, not an implementation detail.

| Axis | `local_file` | `object_uri` | `stream_handle` |
|---|---|---|---|
| **Input representation** | absolute filesystem path, verified regular file | object URI as received (`scheme://authority/path[?query]`); hash the received bytes, do not normalise | open handle / fd-like object; no path semantics (`fd://<n>` in `source_path`) |
| **Identity acquisition** | `os.stat` → size; sha256 streamed from fd; filename = basename | size from manifest/HEAD when offered, else unknown-until-EOF (`unavailable` mid-stream); sha256 streamed from body; filename = last path segment, verbatim | size unknown-until-EOF; **mandatory local spool first** (§2.16): hash the spooled bytes once, then treat *the spool* as `local_file` for every later stage |
| **Hash acquisition** | full byte stream at step 1 | full response body at step 1; the hash covers **the bytes received**, period | hash covers the **spooled bytes**; the handle itself is never hashed twice and never re-read |
| **Size acquisition** | `os.stat` before hashing; used in the size-agreement check | manifest when trustworthy, else counted during the body read; manifest/body disagreement → `REJ_SOURCE_CORRUPT` | counted during spooling when the handle has no length API; spool truncation (`ENOSPC`, quota) → `REJ_FILE_UNREADABLE` |
| **Filename availability** | REQUIRED, verbatim basename | REQUIRED, verbatim last-segment (empty segment allowed → `null` + `WARN_CONTAINER_VARIANT`) | none: `null`, OPTIONAL ("not applicable — no name exists") |
| **Random / sequential access** | random-capable (seek, re-stat per G6) | sequential-only for hashing; single transaction | one-shot: **consumable exactly once**; after spooling, random access happens *on the spool*, never on the handle |
| **Spooling requirement** | none | none mandated (streaming read); local spool optional per Stages 15/16 policy | **mandatory local spool before any parsing**; the spool file IS the source for steps 2–13 of §2.1.5 |
| **Container probing** | direct probe of the file | probe the streamed body (buffered windows allowed) | probe **the spool only** — §2.3 must never describe a probe that consumes handle bytes directly |
| **Capability probe + decoding** | as-is | as-is (scrubbed) | run against the spool; Decode opens the spool path recorded in `source_path` |
| **Lifecycle owner** | OS filesystem; Builder holds no locks beyond the read | HTTP/object client owned by the API/storage layer; Builder cancels on abort | **provider owns the handle until the spool completes**; Builder owns the spool from completion |
| **Premature termination** | mid-read I/O error → `REJ_FILE_UNREADABLE` | truncated body vs manifest → `REJ_SOURCE_CORRUPT`; transport error → `REJ_FILE_UNREADABLE` | handle EOF before declared length → `REJ_SOURCE_CORRUPT`; handle error → `REJ_FILE_UNREADABLE`; spool itself corrupt → `REJ_SOURCE_CORRUPT` on the spool path |

### 2.2A.1 Stream-handle answers (the eight questions, settled)

1. **Can it be replayed?** No — consumable exactly once (§2.2A row 6).
2. **Is it seekable?** Not assumed; treated as non-seekable always.
3. **Can its complete byte sequence be hashed before parsing?** Yes — *after* the mandatory spool; the hash covers the spool.
4. **Does it require local spooling?** Yes, mandatory, before §2.1.5 step 2.
5. **Who owns the lifecycle?** Provider until spool completion; Builder owns the spool after.
6. **When is `size_bytes` known?** At spool completion (counted); `unavailable` only mid-spool.
7. **Premature termination?** EOF-before-length → `REJ_SOURCE_CORRUPT`; transport/handle error → `REJ_FILE_UNREADABLE` (see 2.2B chain D2).
8. **Can Container probe it without consuming Decode's bytes?** Yes — *only because* the probe and Decode both read the spool, never the handle. This is the exact failure 2.3 was at risk of designing into itself.

### 2.2A.2 Fidelity + caching consequences per kind

- `fidelity: preserved` (G5) applies to the **post-acquisition bytes**: file bytes, received body bytes, spooled bytes. The spool is a byte-exact copy; its hash equals the source hash by construction.
- Cache key remains `(hash_sha256, size_bytes)` for all kinds; for `stream_handle` the cached record additionally carries `spool_path` as a *run-local* locator only (never a cross-machine key).
- Estimate invalidation is kind-independent: producer-version match still governs (§2.2.4).

### 2.2A.3 Decoder migration map (G7, per kind)

| Kind | What changes in `decode/decoder.py:45` |
|---|---|
| `local_file` | open the recorded path; scheme allowlist denies `..`/UNC/control chars before open |
| `object_uri` | never opened directly by Decode — the ingestion spool/snapshot path recorded in `source_path` is opened instead |
| `stream_handle` | Decode opens the spool path; the original handle is closed and never referenced beyond identity |

### 2.2A.4 What 2.3 must assume (the unblocking contract)

§2.3 may assume: bytes are re-readable (file or spool), size is known or declarable-unavailable,
hash was attested at step 1. §2.3 must **not** assume: a filesystem path exists, the input is
seekable, or the filename is meaningful. Any 2.3 probe description that touches handle bytes
directly is non-conformant by construction.

---

## 2.2B Terminal-diagnostic contract (normative — closes the G3 core; producers traced in §F.3.1, code application → 2.15)

> A low-level exception must **never** become the public contract by accident. Every failure
> observable during ingestion travels exactly one canonical path: raw cause → diagnostic class
> → status decision → machine code → contract state. The runtime, library, or OS underneath may
> change; the contract surface must not.

### 2.2B.1 The canonical ladder (exactly five rungs, no skipping)

```text
low-level failure (OSError, av.error, HTTPError, …)
        ↓ classify (single choke point: classify_failure)
diagnostic class: NOT_FOUND | EMPTY | UNREADABLE | UNRECOGNIZED | UNSUPPORTED |
                  UNDECODABLE | CORRUPT | TOO_LONG | TOO_SHORT | TIMING_BROKEN
        ↓ decide (§2.1.5 evaluation order, first failure wins)
status: rejected | accepted | accepted_with_warnings
        ↓ encode (closed REJ_* set / additive WARN_*)
code: REJ_* | WARN_* (+ null reason only when not rejected)
        ↓ emit (always a contract — partial when rejected)
SourceDescription: populated groups + per-field state + ingestion_status
```

### 2.2B.2 Classification table (normative)

| Low-level signal (examples) | Diagnostic class | Status | Code | Contract state |
|---|---|---|---|---|
| `ENOENT`, 404, handle open fails | NOT_FOUND | rejected | `REJ_FILE_NOT_FOUND` | identity: hash group absent; `source_path`/`source_kind` recorded |
| zero-length read / size 0 | EMPTY | rejected | `REJ_FILE_EMPTY` | identity present without hash |
| `EACCES`/`EPERM`, mid-read I/O error, `os.stat` failure, spool `ENOSPC`, transport error | UNREADABLE | rejected | `REJ_FILE_UNREADABLE` | partial contract to last extracted group; hash `unavailable` only if the read itself failed |
| parse raises with bytes present | UNRECOGNIZED | rejected | `REJ_CONTAINER_PARSE_FAILED` | identity + whatever `container` fields parsed |
| container parses, format unknown | UNRECOGNIZED | rejected | `REJ_CONTAINER_UNRECOGNIZED` | identity + `container` |
| no video stream | UNSUPPORTED | rejected | `REJ_NO_VIDEO_STREAM` | identity + `container` |
| unknown codec id | UNSUPPORTED | rejected | `REJ_UNSUPPORTED_VIDEO_CODEC` | identity + `container` + `video.codec` |
| known codec, unsupported profile/level/pix_fmt | UNSUPPORTED | rejected | `REJ_DECODER_UNAVAILABLE` | identity + `container` + video params |
| decoder opens, no usable frame in probe window | UNDECODABLE | rejected | `REJ_NO_DECODABLE_FRAMES` | identity + `container` + video params |
| size/agreement mismatch, hash↔parse re-stat mismatch, truncated body | CORRUPT | rejected | `REJ_SOURCE_CORRUPT` | identity + everything parsed so far |
| authoritative duration > MAX | TOO_LONG | rejected | `REJ_DURATION_EXCEEDS_MAX` | full technical description, Decode never reached |
| authoritative duration < MIN | TOO_SHORT | rejected | `REJ_DURATION_BELOW_MIN` | full technical description |
| no presentation and no declared timing | TIMING_BROKEN | rejected | `REJ_TIMING_UNUSABLE` | identity + `container` + `video` |
| sparse PTS, duplicate PTS, jitter | TIMING_* (degraded) | accepted_with_warnings | `WARN_TIMING_EVIDENCE_SPARSE` / `WARN_TIMING_ANOMALY` / `WARN_EXTREME_VFR_JITTER` | timing groups `uncertain`, confidence capped |
| Builder-internal fault (bug, mid-write I/O failure, OOM) | INTERNAL | **raise, never emit** | n/a (triage, not a code) | no contract obligation — this is the *only* case that may throw |

**Discriminator O2 — resolved here:** `REJ_FILE_UNREADABLE` means *the byte channel failed*
(transport, permissions, disk, spool space). `REJ_SOURCE_CORRUPT` means *bytes arrived but do
not cohere* (parse failure, size disagreement, truncation, hash↔parse mismatch). The
distinguisher is the layer at which the failure is detected, never the exception class name.

### 2.2B.3 `unavailable` emission rule (closes G3's group-level question)

`state: unavailable` is emitted **only** for a group whose acquisition step was reached but
whose producer failed *after* the step-1 checks passed — currently the canonical case is
`hash_sha256` on a mid-read failure. It is never emitted for steps never reached (those groups
are simply absent from the partial contract), and never for REQUIRED fields on an accepted
contract (§2.1.4 step 1 → that path is REJECT, not a state).

### 2.2B.4 What the current implementation leaks today (evidence, not a change order)

- `ingestor.py:58-63`: `os.path.isfile` → `IngestionError("File not found")`; `os.path.getsize` →
  `IngestionError("File is empty")`. Two distinct low-level conditions become one exception type
  with free-text messages: exactly the accident 2.2B forbids.
- `ingestor.py:71-73`: **any** `av.open` failure — missing file, permissions, corrupt bytes,
  unknown format — becomes one `IngestionError("Unreadable container format: …")`. Three
  diagnostic classes (NOT_FOUND/UNREADABLE/CORRUPT/UNRECOGNIZED) collapsed into one string.
- `pipeline/__init__.py:157-159` → `job.error = f"Ingestion error: {exc}"`: the public
  contract surface (job error) is today's exception `str()`. This is the consumer that the
  ladder must eventually feed — reason codes, not messages.
- `tests/test_pipeline.py:96-105`: asserts on message substrings (`"exceeds"`, `"not found"`)
  — substring assertions are the test-suite form of the same leak and must become code
  assertions on `reason` in the 2.15 migration.

Nothing above changes in this pass. It is recorded so the 2.15 migration cannot claim the
ladder without rewiring the producers.

---

## F.3.1 G3 Application Audit — producer-by-producer trace (normative, spec-only)

> **Scope rule for this pass:** `src/` and `tests/` stay byte-identical. This section traces
> every failure-producing path cited in §2.2B.4 through the §2.2B.1 ladder and records, per path,
> the mandated future behavior. Implementation and test rewrites happen only in the 2.15
> migration, against this trace.

### Trace key (read every row the same way)

`actual condition → raw signal → diagnostic class → status → code → contract state → CLI/job-visible result`

### T1 — `ingestor.py:58-63` (two conditions, one exception type)

| Path | Actual condition | Raw signal | Diagnostic class | Status | Code | Contract state | CLI / job result |
|---|---|---|---|---|---|---|---|
| T1a | path names nothing (`ENOENT`, dangling symlink, non-file) | `os.path.isfile` → `False` → `IngestionError("File not found")` | NOT_FOUND | rejected | `REJ_FILE_NOT_FOUND` | identity records `source_kind` + `source_path`; `hash_sha256` absent (no bytes ever existed); all other groups absent | ingest prints partial contract, exit 2; job FAILED with `reason`, never the message string (replaces `tests/test_pipeline.py:100-105` substring assert) |
| T1b | path names a zero-byte file | `os.path.getsize` → `0` → `IngestionError("File is empty")` | EMPTY | rejected | `REJ_FILE_EMPTY` | identity present **without** hash (no bytes to attest); all other groups absent | same CLI/job shape as T1a with the EMPTY code |

Both rows exist precisely so the two conditions cannot share a result: T1a has nothing to hash,
T1b has an identity shell with no attestable bytes.

### T2 — `ingestor.py:71-73` (three collapsed conditions, by detection layer)

The current code maps **every** `av.open` failure to one message. The mandated split keys on
*what evidence the detector had*, never the exception class name:

| Path | Actual condition | Evidence the detector must use | Diagnostic class → Code |
|---|---|---|---|
| T2a | open fails *before* any byte is parsed (`EACCES`, `ENOENT` raced in, fd invalid) | step 1 stat/open outcome, not the `av` error string | UNREADABLE → `REJ_FILE_UNREADABLE` |
| T2b | bytes present but the container parser rejects them | container parse probe outcome (bytes were readable) | UNRECOGNIZED → `REJ_CONTAINER_PARSE_FAILED` |
| T2c | bytes parse, format id unknown to the runtime | post-parse format table lookup | UNRECOGNIZED → `REJ_CONTAINER_UNRECOGNIZED` |

Partial-contract floor per row follows §2.2B.2 (identity always; `container` only where parsing
actually produced fields). The `2.2B.4` evidence stands: today's three-into-one collapse is the
accident being removed.

### T3 — spooling failures, with ENOSPC isolated

| Path | Actual condition | Diagnostic class → Code | Why this column, not the neighbour |
|---|---|---|---|
| T3a | spool write fails `ENOSPC` / quota | **RESOURCE** → `REJ_SPOOL_EXHAUSTED` (§2.1 v1.1 — amended under §2.1.14, no longer a placeholder) | bytes were never shown to be malformed — the channel ran out of room. Classifying it CORRUPT would frame an infrastructure limit as a source defect and poison dedup/lineage caches keyed by hash. |
| T3b | spooled bytes fail agreement/hash checks | CORRUPT → `REJ_SOURCE_CORRUPT` | bytes *arrived* but do not cohere — the discriminator from §2.2B.2, applied to the spool path |
| T3c | provider aborts mid-spool | UNREADABLE → `REJ_FILE_UNREADABLE` | byte channel failed before coherence could be judged |

T3a is the ENOSPC path called out for special attention. The evidence test: after the failure,
`stat -f` (or the object-store equivalent) shows exhaustion while source bytes are unremarkable
→ RESOURCE. Flipping that test must flip the code; any implementation that maps "could not
finish reading" straight to CORRUPT is non-conformant by construction.

### T4 — premature stream termination (EOF-vs-error, applied)

Uses §2.2A row 11, enforced at the acquisition step, not reinterpreted downstream:

| Path | Actual condition | Diagnostic class → Code | `unavailable` check |
|---|---|---|---|
| T4a | handle EOF before declared length; body shorter than manifest | CORRUPT → `REJ_SOURCE_CORRUPT` | no group is marked `unavailable` — the read completed, the bytes failed coherence |
| T4b | transport/handle error mid-stream | UNREADABLE → `REJ_FILE_UNREADABLE` | `hash_sha256` is the *only* group that may be `unavailable`, and only because its acquisition step was reached and its producer failed (2.2B.3) |
| T4c | clean EOF at/after declared length | not a failure — normal end, identity computed | n/a |

### T5 — partial-contract shape guarantees

A partial contract **must not be confusable with success**:

1. `ingestion_status` is REQUIRED on every emitted contract and is the *only* success predicate
   downstream may read (`status == "accepted"` / `"accepted_with_warnings"`).
2. Groups for steps never reached are **absent from the contract**, never `null`-filled and
   never `unavailable` (2.2B.3). A rejected-at-step-1 contract carries `schema` + `source_identity`
   (possibly hash-less) + `ingestion_status`, and nothing else.
3. `size_bytes`/`hash_sha256` present without step-1 attestation is a contract violation, caught
   by the §E-4 missing/empty-file tests.

### T6 — `pipeline/__init__.py:157-159` (job surface migration)

| Today | Mandated future |
|---|---|
| `job.error = f"Ingestion error: {exc}"` — durable API surface is an exception string, and two different conditions can produce indistinguishable errors (`T1a` vs `T1b` today differ only by wording) | `job.error` becomes a structured payload: `{reason: REJ_*, status, identity: {hash_sha256?, source_kind}}`; human text moves to a non-contract `detail` field. Recovery (`O8`) joins lineage on `hash_sha256`, replays from the partial contract. No consumer may branch on `detail`. |

### T7 — `tests/test_pipeline.py:96-105` and the CLI contract

| Today | Mandated future |
|---|---|
| `pytest.raises(IngestionError)` + `"exceeds"` / `"not found"` substring asserts; `cmd_ingest` prints `ERROR: {exc}` + exit 1 | rejection returns a contract: `ingestion_status.status == "rejected"` + exact `reason in {REJ_DURATION_EXCEEDS_MAX, REJ_FILE_NOT_FOUND, …}`; CLI prints the contract and exits non-zero *keyed off the status field*; `cmd_run` refuses to advance on rejected (never reaches Decode); duration tests assert boundary codes from §E-7 |

### F.3.2 Seven-consumer freeze audit (normative — the 2.2 closure test)

> Each row uses the mandated chain: consumer → input contract consumed → fields relied upon →
> invariant relied upon → failure/status semantics → current implementation assumption →
> conflict? → required migration → test required → downstream impact.
> **"Yes, with our own reading" is a NO.** A row passes only if the consumer can operate from
> the frozen 2.2A/2.2B decisions with zero invented interpretation.

#### C1 — 2.3 Container Information

| Link | Content |
|---|---|
| Input contract | re-readable bytes + size known-or-`unavailable` + step-1 hash attestation (§2.2A.4) |
| Fields relied upon | `source_identity.{source_kind, source_path (run-local locator), size_bytes}`, `hash_sha256` attestation; §2.2A.4 allow/deny lists |
| Invariant | never touches handle bytes; never uses filename for detection; parse windows are buffered and non-consuming |
| Failure/status semantics | probe failure travels 2.2B (T2b/T2c); partial container groups per §2.2B.2 floor |
| Current implementation assumption | none — 2.3 has no probe description yet; the risk was *future* assumption, now fenced by §2.2A.4 |
| Conflict? | **No live conflict.** Residual risk only: a 2.3 author writing direct-handle probing language |
| Required migration | §2.2A.4 holds verbatim in the 2.3 probe description (sign-off item, not code) |
| Test required | per-kind probe fixtures (file/URI/spool); same-container-three-filenames → identical `container` group; stream_handle probe reads spool bytes only |
| Downstream impact | 2.4 inherits probed bytes + size; Decode inherits the spool-vs-file resolution |

#### C2 — 2.4 Stream Information

| Link | Content |
|---|---|
| Input contract | §2.2A.4 + probed container handle + size |
| Fields relied upon | `source_kind` (inherited, never re-derived); `container` group; `size_bytes` |
| Invariant | stream selection must not depend on kind; ambiguity emits `WARN_MULTIPLE_VIDEO_STREAMS`, never a private heuristic |
| Failure/status semantics | selection failure is a contract outcome (`REJ_*`/warning), never an exception |
| Current implementation assumption | no kind-aware selection exists; no multi-stream selection rule exists at all — the gap is absence, not contradiction |
| Conflict? | **No.** But 2.4 must cite §2.2A.4 in its selection rule or it re-opens G4 by omission |
| Required migration | 2.4 stream-selection rule referencing the matrix (spec work, not code) |
| Test required | multi-video-stream fixture per kind; ambiguity → warning code, not silent first-pick |
| Downstream impact | Temporal/Entity track selection inherits the chosen stream index |

#### C3 — Decode

| Link | Content |
|---|---|
| Input contract | `source_identity.source_path` (run-local locator) *after* scheme allowlist; never the original handle, never a consumer-invented path |
| Fields relied upon | `source_path`, `source_kind`, attested `hash_sha256` |
| Invariant | `object_uri`/`stream_handle` resolve to the recorded spool path (§2.2A.3); spool-path reuse across Decode runs within a run is permitted, cross-run reuse forbidden |
| Failure/status semantics | decode-stage failures stay in Decode's contract (`DecodeError` today, 2.2B chain D2 applies at migration); spool missing/rotated → `REJ_SOURCE_CORRUPT` on re-verification, not a silent re-read |
| Current implementation assumption | `decode/decoder.py:45` — `path = source.source_path` opened blindly, no allowlist, no kind distinction, no attestation check |
| Conflict? | **Yes — live divergence, migration-mapped.** Not invented interpretation: the map in §2.2A.3 names the exact change per kind |
| Required migration | scheme allowlist + spool-path resolution + `REJ_SOURCE_CORRUPT` on re-verification mismatch (2.15 migration) |
| Test required | traversal/UNC/control-char paths denied pre-open; URI/handle jobs decode via spool; spool rotated mid-job → corrupt, not re-read |
| Downstream impact | DecodedVideo lineage; Quality frames provenance; every frame's bytes traceable to the attested hash |

#### C4 — Quality

| Link | Content |
|---|---|
| Input contract | `DecodedVideo` frames + Contract #1 envelope (provenance carrying `source_kind`); **never re-opens the source** |
| Fields relied upon | frame bytes; `quality_score` hint record; `generational_estimate` (sealed, §2.1.13) |
| Invariant | analyzer inputs unchanged; no source-path parameters added; hint is evidence, never an input (D-2 lock enforced in code: `hint_recorded_not_chained`, `analyzer.py:82-90`) |
| Failure/status semantics | analyzer never raises for source conditions; empty frames → `uncertain` report (current `state="extracted" if frames else "uncertain"`) — consistent with, not duplicative of, ingestion status |
| Current implementation assumption | `analyzer.py:32-90` verified line-by-line: takes `(decoded, source)`, no path opens, no reinterpretation of ingestion failure; `source_kind` currently unused (provenance-only consumption, as permitted) |
| Conflict? | **No.** This is the one consumer already consuming the frozen contract correctly |
| Required migration | none. Stage 4 owns the hint-admission decision (§2.1.13 open item) |
| Test required | hint-present vs hint-absent reports differ only in provenance, never in score (D-2 regression) |
| Downstream impact | all Evidence layers inherit frame-scoped quality, never source-scoped reinterpretation |

#### C5 — Caching

| Link | Content |
|---|---|
| Input contract | `(hash_sha256, size_bytes)` as the *only* cross-machine key; `spool_path` run-local only; estimates gated on producer-version match (§2.2.4) |
| Fields relied upon | `hash_sha256`, `size_bytes`, per-field `provenance.tool_version` (+ `.model_version` where model-backed) — named by §2.1.15 |
| Invariant | no surrogate keys, no path keys, no version-blind estimate hits |
| Failure/status semantics | cache miss → recompute (not a rejection); negative decisions cached by `(hash, schema_version)` with TTL per O7, never as surrogate contracts |
| Current implementation assumption | **no cache exists in `src/`** (search: only pytest-cache hits) — absence, not contradiction |
| Conflict? | **Resolved — was the freeze blocker (G8).** The gate this row specifies had no field to compare; §2.1 v1.2 (§2.1.15) supplies `tool_version` and fixes the comparison as exact equality with `"unknown"` never hitting (R5). The residual freeze risk is a *future* cache keyed on path or job id, which this row forbids in advance |
| Required migration | cache-key definition in Stages 15/16 referencing exactly these fields + §2.1.15 R5 (register rows 24, and the register's row-13 residual) |
| Test required | same bytes/different path → hit; same path/rewritten bytes → miss; stale producer version → estimate recompute, stable facts kept; `"unknown"` on either side → **no hit** |
| Downstream impact | every later stage's "already processed?" check; dedup store identity |

#### C6 — Reproducibility

| Link | Content |
|---|---|
| Input contract | attested `hash_sha256` + per-field `provenance` (producer versions) + §E-1 golden fixture |
| Fields relied upon | full identity block; `provenance[].{tool, tool_version, model, model_version}` on every estimate — names fixed by §2.1.15 |
| Invariant | same bytes + same producer versions → same contract; same bytes + newer producers → same stable facts, recomputed estimates |
| Failure/status semantics | non-reproducible output without a producer-version change is a defect, not drift; version change without recompute is a cache defect |
| Current implementation assumption | unchanged — provenance carries `tool` (`"numpy"`, `analyzer.py:39`) and still **no version field**; the vocabulary now exists in spec (§2.1.15) while the model does not. Golden fixture §E-1 still does not exist → register rows 24 and 18 |
| Conflict? | **RESOLVED — was G8, the sole blocking omission.** §2.2.4's invalidation rule referenced fields that could not exist; §2.1 controlled amendment v1.2 (§2.1.15) creates them, fixes their distinct meanings, and forbids 2.2 from inventing its own carrier |
| Required migration | 2.15 schema: `ProvenanceEntry.tool_version` / `.model_version`, `SourceInfo.version`, written via one `producer_identity()` helper (§2.1.15 R9); §E-1 golden-hash fixture lands with the identity tests and records the exact version tuple that produced it (§2.1.15 §7.7) |
| Test required | golden fixture reproduces across machines; bump a producer version in test → estimates recompute, stable facts identical |
| Downstream impact | every stage's "why did this output change?" triage; audit/debug lineage |

#### C7 — Failure recovery

| Link | Content |
|---|---|
| Input contract | partial contracts + `REJ_*` reason + `hash_sha256` surfaced on recovery views (O8) |
| Fields relied upon | `ingestion_status.{status, reason}`; `source_identity.{hash_sha256, source_kind}`; persisted job state |
| Invariant | recovery joins lineage on hash, never on message text; every `REJ_*` is replayable from its partial contract; `detail` text is never branched on |
| Failure/status semantics | source/resource/unreadable/internal distinguished by code per 2.2B (T6); INTERNAL raises, everything else emits |
| Current implementation assumption | `recover_job` (`pipeline/__init__.py:208-240`) restores `{id, input_path, status, timestamps, error}` + full `source_description`/`quality_report` blobs — but no `reason` field, no identity surfacing, and `error` is a free-text string |
| Conflict? | **Yes — live divergence, migration-mapped.** Recovery works structurally today; it cannot yet satisfy the lineage/distinguishability invariant |
| Required migration | structured `job.error = {reason, status, identity}` per T6; `recover_job` exposes reason + hash; CLI `recover`/`status` print codes |
| Test required | each `REJ_*` recovered and replayed from its partial contract; message-text-only recovery rejected by test |
| Downstream impact | Stages 16/19 operator views; retry-vs-abort policy (retryable: UNREADABLE/RESOURCE; non-retryable: CORRUPT/UNSUPPORTED — policy lives in 16/19, codes come from here) |

- [x] T1 two-condition split with distinct codes and distinct contract shapes
- [x] T2 three-condition split keyed on detection layer/evidence, not exception type
- [x] T3 ENOSPC isolated as RESOURCE with new closed-set code `REJ_SPOOL_EXHAUSTED` (evidence test stated)
- [x] T4 EOF-vs-error with the `unavailable`-only-where-reached check
- [x] T5 partial-contract non-confusion rules
- [x] T6 job-surface migration shape (reason+identity, text demoted to `detail`)
- [x] T7 test/CLI migration targets (code assertions, status-keyed exit)
- [x] 2.3/2.4/Decode/Quality/Caching/Reproducibility/Recovery row-by-row audit against §2.2A.4 +
      this trace — **done in §F.3.2 (C1–C7)**, divergence guard in §F.3.3, verdict in §F.3.5.
      `Stage 2.3 BLOCKED` still stands, now for exactly one reason: **G8** (§F.3.4).

---

## F. Cross-stage closure audit — the freeze test (normative)

> **Before 2.2 closes, every consumer below must be able to consume the frozen 2.2A/2.2B
> decisions without inventing its own interpretation.** A "yes, with our own reading" is a NO.
> Each row must name the consumer's contract obligation or the item stays open.
>
> **Result of this audit: 5/7 passed on the first run; C5 and C6 failed on one root cause (G8), which
> was closed at the §2.1 layer as controlled amendment v1.2 (§2.1.15). Re-run: 7/7 PASS — Stage 2.2
> specification is CLOSED (§F.3.5).**

| Consumer | Frozen-decision consumption | Pass condition | Blocker if NO |
|---|---|---|---|
| **2.3 Container probe** | accepts only re-readable bytes + known-or-unavailable size; never touches handle bytes; never uses filename for detection | §2.2A.4 holds verbatim in the 2.3 probe description | any direct-handle probing language |
| **2.4 Stream info** | inherits `source_kind`; stream selection ambiguity emits `WARN_MULTIPLE_VIDEO_STREAMS` (not a private heuristic) | stream-selection rule references the matrix | kind-dependent selection logic |
| **Decode** | opens only `source_identity.source_path` after scheme allowlist; `object_uri`/`stream_handle` resolve to the recorded spool path (§2.2A.3) | migration map implemented; `decoder.py:45` blind open removed | raw-path or handle opens surviving |
| **Quality** | consumes `source_kind` for provenance only; never re-opens the source (frames only) | analyzer inputs unchanged; no source-path parameters added | new source-opening parameters |
| **Caching** | key `(hash_sha256, size_bytes)`; `stream_handle` cache rows carry run-local `spool_path` never as key; estimates gated on producer-version match | cache-key definition references exactly these fields | surrogate keys, path keys, version-blind hits |
| **Reproducibility** | golden-hash fixture (§E-1) reproduces across machines; `decoder` version recorded in provenance | fixture + version fields present | machine-local hashes, unversioned producers |
| **Failure recovery** | recovery views join lineage on `hash_sha256` (surfaced per O8); every `REJ_*` replayable from its partial contract | `recover_job` exposes reason + identity | message-string recovery, hash-less jobs |

### F.1 Verdict ledger (updated by this pass)

| Item | Status |
|---|---|
| G1 | OPEN — `source_kind` normative; only the `fd://<n>` canonical form remains, owned by §2.16 (register row 21). **No F.3.2 consumer depends on it** — C1 needs re-readable bytes, not a handle spelling |
| G2 | OPEN, SCOPED — deletion recorded (register row 8); code untouched until 2.15. Does not block closure: consumers read the frozen allow/deny lists, not the model |
| G3 | **SPEC-SIDE CLOSED** — ladder (2.2B) + producer trace (F.3.1) + consumer rows (F.3.2) + register rows 1–6. What remains is *implementation* (2.15), per §F.3.5 |
| G4 | **SPEC-SIDE CLOSED** — matrix + lifecycle (2.2A) + seven-consumer freeze audit (F.3.2) + verdicts (F.3.5). Residuals: `fd://<n>` (row 21) and spool quota policy (row 22), both owned by §2.16 |
| G5 | CLOSED ✅ |
| G6 | PARTIALLY CLOSED (integrity ✅; failure-map folded into 2.2B) |
| G7 | OPEN / downstream (per-kind migration map in §2.2A.3; register row 17 — DOWNSTREAM_DEPENDENCY, lands at 2.15 gated on G1+G4) |
| O2 | **CLOSED ✅** — discriminator stated in §2.2B.2 (channel failure vs incoherent bytes) |
| O5 | CLOSED ✅ (unchanged) |
| T3a | **RESOLVED ✅** — `REJ_SPOOL_EXHAUSTED` is now §2.1 v1.1, not a 2.2 placeholder |
| **G8** | **CLOSED ✅ — §2.1 controlled amendment v1.2 (§2.1.15).** Producer-version identity is now expressible in the envelope: `ProvenanceEntry.tool_version` / `.model_version`, `SourceInfo.version` (source-side meaning), rules R1–R9, tests 1–8, non-overlap against v1.1, Stage 2.1 re-closed. 2.2 defines **no** version field. Residual = register row 24 (implementation, 2.15) |
| **Freeze verdict** | **Stage 2.2 SPECIFICATION → CLOSED** — 7/7 consumers consume the frozen contract without inventing a rule (§F.3.5). Implementation/tests NOT STARTED (register rows 1–12 + 24 → 2.15); re-homed items: rows 21–22 → §2.16, row 23 → Stage 4 |


### F.2 What §2.2.6/§2.2.7 gain from this pass (no silent divergence)

- §2.2.6 exit criteria must absorb: scheme-matrix producer/consumer coverage, ladder tables as code-review checklists, and the §F freeze-test rows as sign-off items.
- §2.2.7 gate record: replace "G1–G6 amended" vagueness with this ledger; the D-section "not yet determined" set shrinks by O2.

### F.3 Remaining work before 2.2 can close (explicit, ordered — status after the freeze pass)

> Structural note: the child audits **F.3.1** (producer trace) and **F.3.2** (seven-consumer freeze)
> physically sit above this parent heading, and **F.3.3–F.3.5** (divergence guard, G8, verdict) sit
> below it. Reflow into one contiguous §F.3 block on the next touch; the numbering is authoritative,
> the ordering is an editing artifact.

1. ~~Apply 2.2B to the six evidence-cited producers~~ → **DONE as specification** in F.3.1 (T1–T7).
   The *code* application (`ingestor.py:58-63,71-73`, `pipeline/__init__.py:157-159`,
   `tests/test_pipeline.py:96-105`, `cli.py` exit paths) is now **register rows 1–6**, owned by 2.15.
2. Write the G4 full per-scheme table into §2.16 — spool paths, quota policy (row 22), and the
   `fd://<n>` canonical form (row 21). Both are §2.16-owned and neither blocks a consumer today.
3. ~~Run the §F freeze test row-by-row at close-out~~ → **DONE**: F.3.2 (C1–C7) + F.3.5 verdict.
   Two consumers could not consume the frozen contract without inventing meaning: C5, C6.
4. ✅ **CLOSED:** G8 resolved as §2.1 controlled amendment **v1.2** (§2.1.15) — chain in F.3.4.
   Nothing now blocks 2.2's specification; the stage is CLOSED (§F.3.5).
5. Delete the §D superseded-prose block (still held for diff review) once its content is confirmed
   subsumed by §C.
6. Keep `Stage 2.3 BLOCKED` until F.1 shows no OPEN rows except explicitly re-homed ones — today the
   only genuine blocker is G8, plus the re-homed §2.16 items (rows 21–22) and Stage 4 (row 23).

### F.3.3 Divergence guard — every spec ↔ repo difference, classified exactly once

> Classes: `CONFORMING` · `SPECIFICATION_CHANGE_REQUIRED` · `IMPLEMENTATION_MIGRATION_REQUIRED`
> · `OPEN_DECISION` · `DOWNSTREAM_DEPENDENCY`. Nothing may remain an unexplained "gap".
> Evidence collected across the F.3.1/F.3.2 passes; repo state = 25/25 green, `src/` unchanged.

| # | Divergence (spec ↔ repo) | Class | Owner / when |
|---|---|---|---|
| 1 | `ingestion_status {status, reason, warnings[]}` does not exist; rejection is an `IngestionError` | IMR | 2.15 |
| 2 | `ingestor.py:58-63` two conditions, one exception path (T1) | IMR | 2.15 |
| 3 | `ingestor.py:71-73` three-way collapse keyed on exception type (T2) | IMR | 2.15 |
| 4 | `pipeline/__init__.py:157-159` durable job error = exception string (T6) | IMR | 2.15 |
| 5 | `tests/test_pipeline.py:96-105` substring asserts (T7) | IMR | lands with #1–4 |
| 6 | `cli.py` exit keyed on `ERROR: {exc}` text (T7) | IMR | lands with #1 |
| 7 | `source_identity` block absent (`hashlib`/`sha256` → 0 repo hits) | IMR | 2.15 |
| 8 | `container.size_bytes` (`source_description.py:32`, `ingestor.py:203`) vs §2.2A.4 byte-identity rule (G2) | IMR | 2.15 (deletion already scoped) |
| 9 | Single `duration` group vs locked `presentation`/`declared` authority split (§38/§40) | IMR | 2.15 |
| 10 | `MIN_DURATION` gate not enforced (`MAX_DURATION_SECONDS` only, `ingestor.py:43`) | IMR | 2.15 |
| 11 | `schema: {name, version}` block absent from the model (§46) | IMR | 2.15 |
| 12 | Capability probe §2.1.5.1 + `WARN_SOFTWARE_DECODE_ONLY` / `WARN_DURATION_NEAR_BOUNDARY` unemitted | IMR | post-2.15 (explicitly deferred) |
| 13 | **`ProvenanceEntry`/`SourceInfo` carried no producer-version field**, while §2.1's stability rule makes an estimate without one *non-conformant* and §2.2.4 gates cache hits on it (C5/C6) | **SCR (G8) → RESOLVED** by §2.1 controlled amendment v1.2 (§2.1.15) — the vocabulary now exists; residual moved to row 24 | closed this pass; §2.1 re-closed v1.2 |
| 14 | §2.1.4-D `state: unavailable`; `ObservationState.UNAVAILABLE` exists and is emitted where reached | CONFORMING | — |
| 15 | D-1 vocabulary applied in code (`extracted`, not `measured`) | CONFORMING | — |
| 16 | D-2 sealed hints un-chained in code (`hint_recorded_not_chained`, `analyzer.py:82-90`) | CONFORMING | — |
| 17 | `decoder.py:45` blind `open(source_path)` (G7) — per-kind map exists (§2.2A.3) | DD | 2.15, gated on G1+G4 landing |
| 18 | §E-1 golden-hash fixture + all §E identity tests absent (verification track not started) | DD | 2.15 + §E |
| 19 | Multi-video-stream selection rule absent (code `WARN_MULTIPLE_VIDEO_STREAMS` already in the closed set) | DD | 2.4 (must cite §2.2A.4) |
| 20 | Numeric `MIN_DURATION` value not locked (only the *code* `REJ_DURATION_BELOW_MIN` is) | **OPEN_DECISION** | §2.16 / product owner |
| 21 | `fd://<n>` canonical form for `stream_handle` unspecified (G1 residual) | **OPEN_DECISION** | §2.16 (G4 full table) |
| 22 | Spool quota / retention / cleanup policy unspecified (§2.2A.2 states run-locality, not policy) | **OPEN_DECISION** | §2.16 |
| 23 | Contract #3 `extraction_status` retained (D-3 removed it from #1 only) | **OPEN_DECISION** | Stage 4 |
| 24 | Residual of resolved row 13: `ProvenanceEntry` gains `tool_version` / `model_version`, `SourceInfo` gains `version`, and producers capture versions through one `producer_identity()` helper (§2.1.15 R1–R9) | IMR | 2.15 (+ §2.1.15 §7 tests 1–8) |

**Tally after §2.1 v1.2:** CONFORMING 3 (rows 14–16) · SPECIFICATION_CHANGE_REQUIRED **1, resolved**
(row 13 → §2.1.15) · IMPLEMENTATION_MIGRATION_REQUIRED **13** (rows 1–12, 24) · OPEN_DECISION 4
(rows 20–23) · DOWNSTREAM_DEPENDENCY 3 (rows 17–19). **Zero open specification-change rows**; every
row has a named owner; none is left as a "gap".

### F.3.4 G8 — the one blocking item, in the mandated chain

```
Decision    producer-version identity must be expressible in the envelope the spec already
            mandates (§2.1:164 "must record producer version in provenance"; §2.1:169 "an
            estimate whose provenance does not identify the producer version is
            non-conformant"; §2.2.4 cache gating; §2.2A.2 kind-independent invalidation)
Field       envelope vocabulary §2.1.4-B — ProvenanceEntry (and SourceInfo); NOT a 2.2 field
Producer    every estimate producer (timing analyzer, heuristics, later model-backed fields)
Consumer    Caching (C5), Reproducibility (C6), recovery triage, Stages 15/16 cache keys
Invariant   a version-blind cache hit becomes impossible; "why did this output change?" is
            answerable from the contract alone
Code        NONE now — utils/confidence.py gains the field at the 2.15 schema migration
Test        §E: bump a producer version in a fixture → estimates recompute, stable facts
            identical; a version-blind hit fails
Downstream  every estimate field from 2.3 onward; 2.15 schema; 15/16 caching; 18 reproducibility
```

**Why this is not a 2.2 prose fix:** the rule creating the obligation lives in §2.1's closed
dimension table. Per the §2.1.14 procedure just used for `REJ_SPOOL_EXHAUSTED`, closing G8 meant a
**controlled §2.1 amendment (v1.2)** to the envelope vocabulary — not a re-home, and not quietly
adding the field from the 2.2 side.

> **RESOLVED ✅ — G8 is closed by §2.1.15 (Stage 2.1 v1.2).** Re-decided on the route question:
> because §2.1 *already* makes producer-version provenance normative, the gap was a
> contract-vocabulary defect, and re-homing it to §2.15 would have changed the meaning of a rule to
> dodge a reopening. v1.2 adds `ProvenanceEntry.tool_version` / `.model_version` and
> `SourceInfo.version` (source-side meaning, fixed by §2.1.15 §3), with requirement/state rules
> R1–R9, ownership, tests, non-overlap and cross-stage impact all recorded there. 2.2 invents **no**
> field: C5 and C6 now consume the envelope. `src/` untouched, as with v1.1.

### F.3.5 Stage 2.2 closure decision — **CLOSED** (freeze test re-run after §2.1 v1.2)

Re-run of the same seven rows, after G8 was closed by §2.1.15. No row's *input contract* was changed
to obtain this result; only the vocabulary question that blocked C5/C6 was answered, in §2.1.

| Consumer | Verdict before v1.2 | Verdict after v1.2 | Blocking? |
|---|---|---|---|
| C1 2.3 Container probe | **PASS** — fenced by §2.2A.4 allow/deny lists | **PASS** | no |
| C2 2.4 Stream info | **PASS** — selection rule is 2.4's own work; code already in the closed set | **PASS** | no |
| C3 Decode | **PASS with migration** — register row 17 | **PASS with migration** | no |
| C4 Quality | **CONFORMING today** | **CONFORMING today** | no |
| C5 Caching | **CONDITIONAL** — gate depended on G8 | **PASS with migration** — gate is now `tool_version` exact-equality (§2.1.15 R5); residual is register row 24 | no |
| C6 Reproducibility | **FAIL** — spec referenced envelope fields that could not exist | **PASS with migration** — `{tool, tool_version, model, model_version}` + §E-1 tuple rule (§2.1.15 §7.7) | no |
| C7 Recovery | **PASS with migration** — register rows 4/5/6 | **PASS with migration** | no |

**Freeze-test question — "can every relevant failure path be interpreted deterministically by every
consumer without inventing meaning?" → YES, 7/7.** The one root cause that made C5 and C6 invent
where producer versions live is resolved at the layer that owned the rule (§2.1), and 2.2 gained no
field of its own in the process — which was the point of the test.

Nothing remains as an unexplained gap: 13 `IMPLEMENTATION_MIGRATION_REQUIRED` rows are owned by 2.15
(spec-lagging-code is expected and does not block specification closure), 4 `OPEN_DECISION` rows have
named owners outside 2.2 (§2.16 ×3, Stage 4 ×1), 3 `DOWNSTREAM_DEPENDENCY` rows have named landing
points, and 3 rows are conforming today.

**Closure gate — all three conditions executed:**
1. ✅ G8 resolved as a §2.1 controlled amendment **v1.2** with the full chain recorded in §2.1.15
   (evidence → proposal → record → impact/conformance audit → versioned re-close; §2.1 re-closed).
2. ✅ F.1 ledger flipped: no G row remains open except explicitly re-homed items (G1 → §2.16;
   register rows 21–22 → §2.16, row 23 → Stage 4).
3. ✅ §2.2.6 exit criteria labelled: spec-side items checked; code-side items marked "→ 2.15
   migration" by the note at the head of that section, so nothing reads as silently satisfied.

> **Decision: Stage 2.2 SPECIFICATION → CLOSED.** Implementation remains **NOT STARTED** and is
> governed by register rows 1–12 + 24 (2.15) and the §E verification gaps. **Stage 2.3 → UNBLOCKED**:
> C1 already passes, and 2.3 carries no dependency on rows 20–22 beyond the §2.2A.4 allow/deny lists
> frozen in this stage. 2.3 additionally inherits one producer duty: it emits `SourceInfo.version`
> only when the artifact itself declares a producer version (§2.1.15 R3 — never a Builder version).



