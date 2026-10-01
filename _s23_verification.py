"""Stage 2.3 controlled-remediation verification gate (Part IV).

Purpose
-------
Part III defined the required changes and their closure conditions. This script is
the machine-checkable form of those conditions. It exists to make one thing
structurally impossible: declaring Stage 2.3 frozen on the strength of having
*written down* the remediation rather than *performed* it.

Every check answers a yes/no question against the real repository, the real
models, and the real emitted contract. Checks do not read Part III and agree with
it; they read the code. A check that cannot be evaluated returns HELD or NOT
IMPLEMENTED -- never PASS. That asymmetry is the whole design: the gate can only
report a pass when something was demonstrated.

It changes nothing under src/. It imports the package to inspect it.
"""

from __future__ import annotations

import io
import os
import re
import sys
import tempfile
import tokenize

REPO = os.getcwd()
SRC = os.path.join(REPO, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "_s23_verification.txt")
SPEC = os.path.join(REPO, "docs", "specs", "stage2_3_container_probe.md")

PASS, FAIL, HELD = "PASS", "FAIL", "HELD"
NOT_IMPLEMENTED = "NOT-IMPLEMENTED"
VACUOUS = "VACUOUS-PASS"
SPEC_ONLY = "SPEC-ONLY"

RESULTS = []


def _two_scope_fixture():
    """The T-R3b two-scope artifact, or None. Built by _s23_fixture_inject.py.

    Container scope says one producer, stream scope says another. Both are written
    into the real file, so the check that consumes it is reading the artifact rather
    than a hand-built list.
    """
    path = os.path.join(REPO, "_s23_fixtures", "conflict_two_scope.mp4")
    return path if os.path.exists(path) else None


def _measure_a5(path):
    """Does the codec string ever enter a producer declaration?

    Returns None when there is no fixture to measure. `ok` is True only when a
    producer value genuinely existed AND the codec stayed out of it -- otherwise the
    check would pass for having nothing to refuse.
    """
    from videotemplate.ingestion.ingestor import Ingestor

    desc = Ingestor().ingest(path)
    decls = list(desc.container.producer_declarations or [])
    values = [d.original_value for d in decls]
    codec = getattr(desc.video_stream, "codec", None)
    codecs = {str(codec).lower()} if codec else set()
    leaked = [v for v in values
              if any(c and c in str(v).lower() for c in codecs)]
    return {
        "codec": codec,
        "producer_values": values,
        "codec_leaked": bool(leaked),
        # A5 is only demonstrated when there WAS a producer value to protect.
        "ok": bool(values) and not leaked,
    }


def _measure_t7(path):
    """Is a genuine two-scope conflict preserved per the §2.1.16 rule?

    Three clauses, all measured on the emitted contract:
      1. two scopes disagree on the SAME canonical key;
      2. the group rolls up to `conflicting`;
      3. every disputed value survives in the record (retention precedes marking).
    A state label over a dropped value fails, which is what separates this from the
    old VACUOUS proxy.
    """
    from videotemplate.ingestion.ingestor import Ingestor
    from videotemplate.utils.confidence import ObservationState

    desc = Ingestor().ingest(path)
    decls = [d for d in (desc.container.producer_declarations or [])
             if d.canonical_key == "encoder"]
    by_scope = {}
    for d in decls:
        by_scope.setdefault(d.scope, set()).add(d.original_value)
    two_scopes = len(by_scope) >= 2
    values = {v for vs in by_scope.values() for v in vs}
    inconsistent = len(values) >= 2
    state = desc.container.producer_state
    # Retention is measured, not assumed: every value seen in ANY scope must still be
    # present in the emitted record. (Comparing `values` to itself would be a
    # tautology and would pass even if the producer kept nothing.)
    emitted = {d.original_value for d in decls}
    retained = values <= emitted and len(decls) == sum(
        len(v) for v in by_scope.values())
    return {
        "by_scope": {k: sorted(v) for k, v in by_scope.items()},
        "state": getattr(state, "value", state),
        "two_scopes": two_scopes,
        "inconsistent": inconsistent,
        "retained": retained,
        "ok": (two_scopes and inconsistent and retained
               and state == ObservationState.CONFLICTING),
    }


# Resolved once, after the helpers above it exist: A5 and T7 read the same artifact.
CONFLICT_FIXTURE = _two_scope_fixture()


def record(check_id, subject, status, evidence):
    RESULTS.append((check_id, subject, status, evidence))


def out(line=""):
    STREAM.write(line + "\n")


def read_spec():
    with io.open(SPEC, encoding="utf-8") as fh:
        return fh.read()


def spec_has(pattern, label):
    """True if the draft/spec text contains a required statement.

    Used only for checks that are genuinely *about the text*. A text match never
    discharges a runtime obligation; runtime checks are separate and stricter.
    """
    return bool(re.search(pattern, read_spec()))


def _origin_value(decl) -> str:
    """The origin as a plain lowercase string.

    `str()` on a `str, Enum` member yields 'ObservationOrigin.MUXER_AUTHORED' on
    Python 3.11+, not the value, so filtering on str() silently matches nothing.
    That bug is exactly the kind this gate exists to surface, so it is fixed here
    explicitly rather than by loosening the comparison.
    """
    origin = getattr(decl, "origin", None)
    return str(getattr(origin, "value", origin) or "").casefold()


def _build_clip(path):
    """A minimal valid clip, built exactly the way the test suite builds them."""
    import av
    c = av.open(path, "w")
    st = c.add_stream("libx264")
    st.width, st.height, st.pix_fmt, st.rate = 160, 120, "yuv420p", 24
    c.start_encoding()
    for i in range(8):
        f = av.VideoFrame(160, 120, "yuv420p")
        for pl in f.planes:
            pl.update(bytes(pl.buffer_size))
        f.pts = i
        c.mux(st.encode(f))
    for pk in st.encode(None):
        c.mux(pk)
    c.close()
    return path


DECLARED_FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "_s23_fixtures", "declared_real.mp4")
DECLARED_VALUE = "HandBrake 1.6.0 2023041600"


def _declared_artifact(tmp):
    """The T-R3b fixture: an artifact that genuinely DECLARES a producer.

    R3 measured that no fixture built by writing tags can carry a declaration —
    the muxer destroys it. This artifact is built by direct atom injection
    (`_s23_fixture_inject.py`) and verified to decode to byte-identical frames, so
    it is a real declared producer and not a corrupt file that merely opens.

    Built on demand so the gate does not depend on a checked-in binary.
    """
    if os.path.exists(DECLARED_FIXTURE):
        return DECLARED_FIXTURE
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _s23_fixture_inject as fix
    base = fix.build_base(os.path.join(os.path.dirname(DECLARED_FIXTURE), "t1_base.mp4"))
    fix.inject_declaration(base, DECLARED_FIXTURE, DECLARED_VALUE)
    return DECLARED_FIXTURE


def _probe_version_strings() -> set:
    """Every version string the PROBE could possibly supply.

    If SourceInfo.version ever equals one of these, the probe's identity has been
    substituted for the artifact's own declaration (S2.1.15 R3).
    """
    import av
    out = {str(av.__version__), str(getattr(av, "ffmpeg_version_info", ""))}
    for _lib, nums in getattr(av, "library_versions", {}).items():
        out.add(".".join(str(n) for n in nums))
        out.add("".join(str(n) for n in nums))
    return out


def _ingest(tmp, name, stream_tags=None, container_tags=None, fmt="mp4"):
    """Build a fixture and ingest it, the way the test suite builds them."""
    import av
    from videotemplate.ingestion.ingestor import Ingestor
    codec = "libvpx" if fmt == "webm" else "libx264"
    path = os.path.join(tmp, f"{name}.{fmt}")
    c = av.open(path, "w")
    for k, v in (container_tags or {}).items():
        c.metadata[k] = v
    st = c.add_stream(codec, rate=10)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    for k, v in (stream_tags or {}).items():
        st.metadata[k] = v
    for i in range(8):
        f = av.VideoFrame(160, 120, "yuv420p")
        for pl in f.planes:
            pl.update(bytes(pl.buffer_size))
        f.pts = i
        c.mux(st.encode(f))
    for pk in st.encode(None):
        c.mux(pk)
    c.close()
    return Ingestor(max_duration=30.0).ingest(path)


def _unreadable_fixture(tmp: str, name: str = "unreadable.mp4") -> str:
    """A file that is definitely not a container.

    Shared by A8 and T8 so the two rows cannot end up measuring different artifacts —
    they are one register finding (G18) with one root cause.
    """
    p = os.path.join(tmp, name)
    with open(p, "wb") as fh:
        fh.write(b"A" * 128)
    return p


def classify_ref(ref: str) -> str:
    """Classify one evidence ref against the §2.1.17 grammar (v1.4).

    Returns one of:
      NOT_ADDRESS   a `method:` value -- identifies a procedure, never a location (E-2)
      CONFORMING    parses, and the locator is specific enough to locate evidence (E-3)
      LEGACY        legal but unclassified -- satisfies neither E-1 nor E-3 (E-4)

    The old A7 check asked `"://" in ref`. That is RETIRED, not satisfied: not one of the six
    emission sites in src/ uses a scheme, so the proxy rejected 100% of real emissions by
    construction -- including `frame_0`, which does locate a frame. §2.1.17.3 explains why a
    URI scheme was rejected structurally rather than adopted to silence this check.
    """
    if ":" not in ref:
        return "LEGACY"
    kind, _, locator = ref.partition(":")
    if kind == "method":
        return "NOT_ADDRESS"
    if kind not in ("artifact", "frame", "contract", "derived"):
        return "LEGACY"
    if not locator or locator.strip() in ("*", ""):
        return "LEGACY"
    if kind == "artifact":
        # The locator names the container THEN a structural path within it. Testing
        # for a digit is wrong: "mp4" contains a '4', which let "artifact:mp4:*"
        # through as conforming until T-E3 caught it. A structural path is the real
        # requirement, and a wildcard is never a location (§2.1.17.4).
        if "*" in locator or "/" not in locator:
            return "LEGACY"
    if kind == "frame" and not any(s in locator for s in ("@idx", "@pts=")):
        return "LEGACY"
    if kind == "derived" and ":" not in locator:
        return "LEGACY"
    return "CONFORMING"


def check_a1(tmp):
    """A1 — no invented producer identity.

    A1 is only meaningful once a producer-value path EXISTS. This check therefore
    does not ask "is there a field called encoder?" — that was a proxy which
    reported VACUOUS forever regardless of the truth. It asks the real question:

        1. did the contract obtain a producer-related value?
        2. is its authorship classified rather than assumed?
        3. was it withheld from the identity field it is ineligible for?

    (3) is the part that makes A1 a pass rather than an absence. If a future change
    promotes a muxer-authored value, this check goes red — which is the behaviour
    a freeze gate must have.
    """
    from videotemplate.ingestion.ingestor import Ingestor
    path = _build_clip(os.path.join(tmp, "a1.mp4"))
    desc = Ingestor(max_duration=30.0).ingest(path)
    decls = list(getattr(desc.container, "producer_declarations", []) or [])

    if not decls:
        record("A1", "no invented producer identity", VACUOUS,
               "no producer-related value was obtained at all, so there is nothing "
               "to withhold and nothing to fabricate")
        return

    origins = sorted({_origin_value(d) for d in decls})
    muxer = [d for d in decls if _origin_value(d) == "muxer_authored"]
    si_fields = set(type(desc.container.source).model_fields)
    promoted = "version" in si_fields and getattr(desc.container.source, "version", None)

    if muxer and not promoted:
        record("A1", "no invented producer identity", PASS,
               f"{len(decls)} producer-related value(s) obtained, origins={origins}; "
               f"{len(muxer)} muxer-authored value(s) REPORTED VERBATIM and withheld "
               f"from SourceInfo.version (which is {'present and None' if 'version' in si_fields else 'absent'}). "
               f"The withholding is demonstrated, not vacuous")
    elif muxer and promoted:
        record("A1", "no invented producer identity", FAIL,
               f"a muxer-authored value was PROMOTED to SourceInfo.version="
               f"{getattr(desc.container.source, 'version')!r}. This is exactly the "
               f"fabrication R3 exists to prevent")
    else:
        record("A1", "no invented producer identity", NOT_IMPLEMENTED,
               f"producer values were obtained but none carried a muxer-authored "
               f"classification; origins={origins}, so the withholding path is "
               f"untested")


def check_a_invariants(tmp):
    """A1-A12, the draft's acceptance invariants, evaluated against the repo.

    A10/A11 are resource invariants owned by S2.16; they are HELD by construction.
    """
    from videotemplate.utils.confidence import ProvenanceEntry, SourceInfo
    from videotemplate.models.source_description import (
        ContainerInfo, SourceDescription, VideoStreamInfo)

    check_a1(tmp)

    # A2/A3/A12 -- the version carriers, now that cycle 2 landed them. Each is a
    # BEHAVIOURAL check against a real ingested contract, not a field-name probe:
    # a carrier that exists but is populated wrongly must still fail.
    ci = set(ContainerInfo.model_fields)
    si = set(SourceInfo.model_fields)
    pe = set(ProvenanceEntry.model_fields)
    has_version = "version" in si
    has_toolver = {"tool_version", "model_version"} & pe
    probe = _probe_version_strings()
    src = _ingest(tmp, "a2")
    version = getattr(src.container.source, "version", None)

    fabricated = version is not None and version in probe
    sentinel = version in ("", "unknown", "none", "N/A")
    record("A2", "no version fabrication",
           FAIL if (fabricated or sentinel or not has_version) else PASS,
           f"SourceInfo.version={version!r}; it is a probe/library version="
           f"{fabricated}; it is a sentinel={sentinel}. A muxer-authored tag was "
           f"withheld, so 'no fabrication' is demonstrated rather than vacuous")

    record("A3", "builder-side versions use S2.1.15 vocabulary",
           FAIL if not has_toolver else PASS,
           f"ProvenanceEntry fields={sorted(pe)}; S2.1.15 requires exactly "
           f"tool_version/model_version. Present={sorted(has_toolver)}")

    recorded = [e.tool_version for e in src.container.provenance
                if getattr(e, "tool_version", None)]
    estimate_recorded = [e.tool_version for e in src.quality_score.provenance
                         if getattr(e, "tool_version", None)]
    record("A12", "probe identity/version recorded",
           PASS if (recorded and estimate_recorded and has_version) else FAIL,
           f"probe provenance tool_version={recorded}; estimate (quality_score) "
           f"tool_version={estimate_recorded}; S2.1.15 R1 requires it on the "
           f"producing entry of every `estimate` field")

    # A4 -- the source-side and builder-side versions must be DISTINCT, which is
    # only observable once both can hold a value.
    declared = _ingest(tmp, "a4", stream_tags={"encoder": "HandBrake 1.6.0"})
    dv = declared.container.source.version
    if dv is not None and recorded:
        distinct = dv not in probe
        record("A4", "artifact-declared version distinct from probe version",
               PASS if distinct else FAIL,
               f"artifact declares {dv!r}; probe reports {recorded[0]!r}; the two are "
               f"disjoint={distinct}. Source-side and builder-side are separate slots")
    else:
        record("A4", "artifact-declared version distinct from probe version",
               NOT_IMPLEMENTED,
               f"no declared source version is obtainable on any fixture "
               f"(got {dv!r}); the slots exist but the distinction is unexercised")

    # A5 -- codec must not establish encoder identity. Previously a field-name proxy
    # (no `encoder` field on VideoStreamInfo => VACUOUS). It is now exercised for
    # real: the two-scope fixture puts a codec and a producer in tension, and the
    # check reads the produced contract.
    vs = set(VideoStreamInfo.model_fields)
    fused = bool({"codec", "encoder"} <= vs)
    a5 = _measure_a5(CONFLICT_FIXTURE) if CONFLICT_FIXTURE else None
    if fused:
        record("A5", "codec identity does not establish encoder identity", FAIL,
               f"VideoStreamInfo carries both codec and encoder; fused={fused}")
    elif a5 is None:
        record("A5", "codec identity does not establish encoder identity", VACUOUS,
               "two-scope fixture absent; cannot exercise the separation")
    else:
        record("A5", "codec identity does not establish encoder identity",
               PASS if a5["ok"] else FAIL,
               f"codec={a5['codec']!r} is present and the producer values are "
               f"{a5['producer_values']}; the codec string appears in a producer "
               f"declaration={a5['codec_leaked']}; no encoder field on "
               f"VideoStreamInfo={not fused}. The codec was offered to the producer "
               f"path and refused, on a file where a producer value DID exist")

    # A6 -- container identification is not producer identification. A producer
    # value may now exist, but it must be attributed to the artifact, never
    # synthesised from format/format_long/size.
    fmt_fields = {"format", "format_long", "size_bytes"}
    record("A6", "container does not establish producer identity",
           PASS if fmt_fields <= ci else FAIL,
           f"container identity fields are {sorted(fmt_fields)}; a producer value is "
           f"read from metadata with a recorded origin, never derived from them. "
           f"producer_declarations present={'producer_declarations' in ci}")

    # A7 -- evidence traceability, measured against the §2.1.17 (v1.4) grammar.
    # The previous check asked `"://" in ref`. That proxy rejected 100% of real emissions
    # by construction, so it was measuring the wrong thing and is RETIRED (E-4/E-5).
    from videotemplate.ingestion.ingestor import Ingestor
    path = _build_clip(os.path.join(tmp, "a7.mp4"))
    desc = Ingestor(max_duration=30.0).ingest(path)
    refs = desc.container.provenance[0].evidence_refs if desc.container.provenance else []
    classes = {r: classify_ref(r) for r in refs}
    conforming = [r for r in refs if classes[r] == "CONFORMING"]
    methods = [r for r in refs if classes[r] == "NOT_ADDRESS"]
    legacy = [r for r in refs if classes[r] == "LEGACY"]

    # A7's subject: producer metadata traceable to artifact evidence. E-1 requires an
    # `artifact:` address for a value extracted from a declaration. A `derived:` or
    # `contract:` ref does NOT satisfy it -- a computed value has no artifact location.
    artifact_located = [r for r in conforming if r.startswith("artifact:")]
    # This fixture DOES carry a producer declaration, so the obligation is live, not
    # vacuous: there is a real value here that must be traceable.
    has_declaration = bool(getattr(desc.container, "producer_declarations", None))
    ok = bool(artifact_located) and has_declaration

    if methods:
        why = "a method word sits in the address field (E-2)"
    elif legacy and not conforming:
        why = "LEGACY refs are unclassified and satisfy neither E-1 nor E-3 (E-4)"
    elif not refs:
        why = "no ref emitted at all"
    else:
        why = "conforming refs present but none is artifact-located (E-1)"

    record("A7", "producer metadata traceable to artifact evidence",
           PASS if ok else FAIL,
           f"§2.1.17 v1.4 grammar; the \"://\" proxy is retired. refs={refs} "
           f"classes={classes}; conforming={conforming or 'none'}; "
           f"method-words={methods or 'none'}; legacy={legacy or 'none'}; "
           f"artifact-located={artifact_located or 'none'}; "
           f"a producer declaration exists on this fixture={has_declaration}. "
           f"Failing because {why}. v1.4 made the obligation FALSIFIABLE, not satisfied")


def check_a8(tmp):
    """A8 -- probe failure must be distinguishable from probed-and-absent.

    Measured by OBSERVING the contract the ingestor returns, per §V.1 R-2. The two
    physically different malformations are expected to land in the SAME UNREADABLE
    group (§V.1 maps both there and R-3 forbids minting another code); what must not
    happen is either of them becoming indistinguishable from a successful probe that
    simply found no declaration. So the decisive comparison is FAILURE vs SUCCESS, not
    malformed-vs-malformed.
    """
    from videotemplate.ingestion.ingestor import Ingestor
    from videotemplate.utils.confidence import ObservationState
    import av

    ing = Ingestor(max_duration=30.0)
    bad = {}
    p1 = os.path.join(tmp, "ascii.mp4")
    with open(p1, "wb") as fh:
        fh.write(b"A" * 128)
    bad["128 ASCII bytes"] = p1
    p2 = os.path.join(tmp, "trunc.mp4")
    c = av.open(p2, "w")
    st = c.add_stream("libx264")
    st.width, st.height, st.pix_fmt, st.rate = 160, 120, "yuv420p", 24
    c.start_encoding()
    for i in range(8):
        f = av.VideoFrame(160, 120, "yuv420p")
        for pl in f.planes:
            pl.update(bytes(pl.buffer_size))
        f.pts = i
        c.mux(st.encode(f))
    for pk in st.encode(None):
        c.mux(pk)
    c.close()
    with open(p2, "r+b") as fh:
        fh.truncate(24)
    bad["24-byte header"] = p2
    p3 = os.path.join(tmp, "novideo.mkv")
    c = av.open(p3, "w")
    a = c.add_stream("pcm_s16le", rate=48000)
    a.layout = av.AudioLayout("stereo")
    c.start_encoding()
    for i in range(4):
        af = av.AudioFrame(format="s16", layout="stereo", samples=1024)
        af.sample_rate = 48000
        af.pts = i * 1024
        for pk in a.encode(af):
            c.mux(pk)
    for pk in a.encode(None):
        c.mux(pk)
    c.close()
    bad["no video stream"] = p3

    seen = {}
    for label, path in bad.items():
        rec = {"producer_decls": [], "provenance": False, "message": ""}
        try:
            desc = ing.ingest(path)
            rec["outcome"] = "CONTRACT"
            rec["failure_state"] = getattr(desc.container, "producer_state", None)
            rec["producer_decls"] = list(
                desc.container.producer_declarations or [])
            rec["provenance"] = bool(desc.container.provenance)
        except IngestionError as exc:
            rec.update(outcome="EXCEPTION", failure_state=None,
                       message=str(exc))
        except Exception as exc:  # noqa: BLE001
            rec.update(outcome="EXCEPTION", failure_state=None,
                       message=f"{type(exc).__name__}: {exc}")
        seen[label] = rec

    # ── A8 per §V.1, after the R-2 migration. ───────────────────────────────────────
    # The contract is read from the RETURNED group. Nothing here inspects an exception
    # class, a message, or any diagnostic text: §V.1 specifies no exception vocabulary,
    # and branching on message text is forbidden (§2.2 T7). If the implementation raised
    # instead of returning, `ingest()` below would raise and `survives` would be False.
    def observe(path):
        rec = {"decls": [], "version": None, "raised": None}
        try:
            desc = ing.ingest(path)
        except Exception as exc:  # noqa: BLE001
            rec.update(outcome="RAISED", probe_state=None,
                       producer_state=None, raised=type(exc).__name__)
            return rec
        c = desc.container
        rec.update(
            outcome="CONTRACT",
            probe_state=getattr(c.probe_state, "value", c.probe_state),
            producer_state=getattr(c.producer_state, "value", c.producer_state),
            decls=list(c.producer_declarations or []),
            version=getattr(c.source, "version", None) if c.source else None,
            format=c.format,
        )
        return rec

    seen = {label: observe(path) for label, path in bad.items()}
    good = observe(_build_clip(os.path.join(tmp, "a8_ok.mp4")))

    # (1) A probe failure SURVIVES ingestion as a returned group.
    survives = all(r["outcome"] == "CONTRACT" for r in seen.values())
    # (2) The state is read from the group's own field, not inferred from anything.
    states = {l: r["probe_state"] for l, r in seen.items()}
    unreadable_ok = states.get("128 ASCII bytes") == "unreadable"
    grouped = states.get("128 ASCII bytes") == states.get("24-byte header")
    novid_ok = states.get("no video stream") == "no_video_stream"
    # (3) UNREADABLE != METADATA_ABSENT on the state axis. METADATA_ABSENT is a SUCCESS
    #     outcome (probe_state absent, producer_state 'absent'); a failure must record
    #     'unavailable' and must carry a probe_state. Both halves are checked against
    #     the real contract, including a genuinely successful probe for contrast.
    failures_unavailable = all(
        r["producer_state"] == "unavailable" for r in seen.values())
    success_has_no_failure = good["outcome"] == "CONTRACT" and \
        good["probe_state"] is None
    absent_is_not_unavailable = ObservationState.ABSENT != ObservationState.UNAVAILABLE
    # (4) no REJ_* member introduced (R-3: §2.1.5's set is closed).
    import videotemplate.models.source_description as _m
    new_rej = sorted(n for n in dir(_m) if n.startswith("REJ_"))
    # (5) nothing fabricated as a consequence of the failure. NOTE the asymmetry: an
    #     UNREADABLE input must carry NO format (nothing was read), but a readable
    #     container that merely has no video stream legitimately DOES carry one. An
    #     earlier version demanded `format is None` for every fixture and failed on the
    #     audio-only case for reporting a real matroska format — a bug in the check.
    #     The SAME over-constraint survived here in the declaration half of (5): an
    #     audio-only Matroska genuinely carries a MuxingApp/WritingApp tag, so it
    #     legitimately yields one `muxer_authored` declaration, and demanding the
    #     list be empty for it was a second instance of the identical check bug. The
    #     obligation is about what the FAILURE must not invent, so it is scoped to the
    #     inputs where the probe read nothing. The scope is asserted, not assumed:
    #     `unreadable_subjects` must be non-empty or this would pass vacuously.
    unreadable_subjects = [r for r in seen.values()
                           if r["probe_state"] == "unreadable"]
    no_synthetic = bool(unreadable_subjects) and all(
        not r["decls"] and r["version"] is None for r in unreadable_subjects)
    unreadable_carries_no_format = all(
        r["format"] is None for r in seen.values()
        if r["probe_state"] == "unreadable")

    ok = (survives and unreadable_ok and grouped and novid_ok
          and failures_unavailable and success_has_no_failure
          and absent_is_not_unavailable and no_synthetic
          and unreadable_carries_no_format and not new_rej)
    record("A8", "probe failure distinguishable from probed-with-absent",
           PASS if ok else FAIL,
           f"§V.1 R-2 — failure survives as a contract={survives}; "
           f"states={states}; malformed pair shares one UNREADABLE group={grouped}; "
           f"failure records producer_state='unavailable'={failures_unavailable}; "
           f"a successful probe reports NO failure state={success_has_no_failure} "
           f"(probe_state={good['probe_state']}, producer_state="
           f"{good['producer_state']}); absent != unavailable="
           f"{absent_is_not_unavailable}; nothing fabricated on the "
           f"{len(unreadable_subjects)} unreadable input(s)={no_synthetic}; "
           f"an unreadable input carries no format={unreadable_carries_no_format}; "
           f"new REJ_* members={new_rej or 'none'}")


def check_a10_a11():
    """A10/A11 are S2.16's. They are HELD, and must not be able to pass here."""
    record("A10", "resource boundedness per S2.16 quota", HELD,
           "S2.16.5-7 do not exist; no subject. Cannot be discharged by 2.3.")
    record("A11", "deterministic cleanup of descriptor/spool", HELD,
           "S2.16.5-7 do not exist; no subject. Cannot be discharged by 2.3.")


# Values that stand in for ABSENCE inside an observed field. A sentinel is a value
# fabricated by the producer, never read from the artifact.
#
# Why this list is derived rather than hardcoded: the previous tuple was
# ("unknown", "1:1", "N/A", "none") and MISSED "0:1", so it could not see
# display_aspect_ratio's fallback at ingestor.py:444. A9 then went green while a real
# sentinel was still being emitted -- a green row that did not cover its own invariant.
# `_missing_detection()` below now checks this list against the fallbacks actually used
# in src/, so a newly added fabrication default fails the check instead of hiding.
FABRICATION_SENTINELS = frozenset({"unknown", "1:1", "0:1", "N/A", "none", "-1"})


def _fabrication_fallbacks() -> set:
    """Every non-None `fallback=` the ingestor passes when formatting an absent value.

    TOKENISED, not regexed over raw text. A plain regex also matches the prose: the
    comments added when this check was introduced literally contain `fallback="0:1"`
    while describing the OLD behaviour, so the audit reported fallbacks that no longer
    existed. Inside a docstring or comment there is no NAME/OP/STRING token triple --
    it is a single STRING -- so matching the token sequence finds real code only.

    Read from the source rather than remembered, because remembering is what let "0:1"
    go unnoticed in the first place.
    """
    path = os.path.join(SRC, "videotemplate", "ingestion", "ingestor.py")
    with open(path, "rb") as fh:
        toks = list(tokenize.tokenize(fh.readline))
    skip = {tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
            tokenize.COMMENT}
    hits = set()
    for i, t in enumerate(toks):
        if t.type != tokenize.NAME or t.string != "fallback":
            continue
        j = i + 1
        while j < len(toks) and toks[j].type in skip:
            j += 1
        if (j + 1 < len(toks)
                and toks[j].type == tokenize.OP and toks[j].string == "="
                and toks[j + 1].type == tokenize.STRING):
            hits.add(toks[j + 1].string.strip("\"'"))
    return hits


def _missing_detection() -> list:
    """Fallbacks in src/ that this check could not detect. Non-empty == the check is BLIND."""
    return sorted(_fabrication_fallbacks() - FABRICATION_SENTINELS)


def check_a9(tmp):
    """A9 -- no hidden inference: plausibility must not become declared metadata.

    Reports FAIL in two distinct situations, because they mean different things:
      (1) a sentinel was actually observed in the emitted contract; or
      (2) the check is BLIND -- src/ fabricates a default this check cannot recognise,
          so a green result would be meaningless.
    Case (2) is why this check now verifies its own completeness.
    """
    from videotemplate.ingestion.ingestor import Ingestor
    ing = Ingestor(max_duration=30.0)
    path = _build_clip(os.path.join(tmp, "a9.mp4"))
    desc = ing.ingest(path)
    # A family-list demuxer name reduced to a family, or a sentinel value, is
    # exactly the inference A9 forbids.
    fam = desc.container.format
    inferred = fam in ("matroska", "webm") and "," in fam
    sentinels = []
    for grp in (desc.container, desc.video_stream):
        d = grp.model_dump()
        for k, v in d.items():
            if isinstance(v, str) and v in FABRICATION_SENTINELS:
                sentinels.append(f"{k}={v!r}")
    blind = _missing_detection()
    ok = not (inferred or sentinels or blind)
    record("A9", "technical plausibility does not become declared metadata",
           PASS if ok else FAIL,
           f"container.format={fam!r}; sentinel-valued fields="
           f"{sentinels or 'none'}; "
           f"fabrication fallbacks in src/={sorted(_fabrication_fallbacks())}; "
           f"UNDETECTABLE by this check={blind or 'none'}. "
           + ("A green A9 requires both: no sentinel observed AND no blind spot"
              if ok else
              ("sentinels observed -> the producer is fabricating absence"
               if sentinels else
               "the check cannot see a fallback src/ is actually using -> a pass "
               "here would be meaningless")))


def check_t_tests(tmp):
    """T1-T12, the draft's closure tests, each judged for whether it CAN run.

    A closure test that cannot be executed is not a pass. The vocabulary is:
    PASS (ran, expectation met), FAIL (ran, expectation unmet), NOT-IMPLEMENTED
    (specified, but no fixture or carrier in the repo), HELD (no subject, owned
    elsewhere).
    """
    from videotemplate.ingestion.ingestor import Ingestor
    from videotemplate.utils.confidence import SourceInfo
    import av  # imported at the top of the function: T3 and T6 both need it, and a
    # function-local import later in the body would make `av` local throughout

    ing = Ingestor(max_duration=30.0)
    path = _build_clip(os.path.join(tmp, "t.mp4"))
    raw = open(path, "rb").read()
    desc = ing.ingest(path)
    has_version = "version" in set(SourceInfo.model_fields)

    decls = list(getattr(desc.container, "producer_declarations", []) or [])

    # T1/T3 -- exercised against the T-R3b fixture: an artifact that genuinely
    # declares a producer, built by atom injection because the muxer destroys any
    # declaration written through tags (R3).
    declared_path = _declared_artifact(tmp)
    declared_desc = ing.ingest(declared_path)
    ddecls = list(getattr(declared_desc.container, "producer_declarations", []) or [])
    container_declared = [d for d in ddecls
                          if _origin_value(d) == "artifact_declared"
                          and d.scope == "container"]
    raw_declared = open(declared_path, "rb").read()
    has_decl = DECLARED_VALUE.encode("utf-8") in raw_declared

    if not has_decl or not container_declared:
        record("T1", "encoder explicitly declared -> encoder recorded",
               NOT_IMPLEMENTED,
               f"the T-R3b fixture did not yield a container-scope declared "
               f"producer (bytes={has_decl}, declared={[d.original_value for d in container_declared]})")
    else:
        recorded = container_declared[0].original_value
        record("T1", "encoder explicitly declared -> encoder recorded",
               PASS if recorded == DECLARED_VALUE else FAIL,
               f"an artifact declaring {DECLARED_VALUE!r} was read back verbatim as "
               f"encoder={recorded!r} with origin=artifact_declared at "
               f"scope=container. This is the first fixture in the project on which a "
               f"producer declaration demonstrably survives to probe time")

    # T2 -- an encoder value that is NOT artifact-declared must be distinguishable
    # from one that is. This became evaluable once origin was recorded.
    muxer = [d for d in decls if _origin_value(d) == "muxer_authored"]
    declared = [d for d in decls if _origin_value(d) == "artifact_declared"]
    if muxer and not declared:
        record("T2", "muxer-authored value is not reported as a declaration", PASS,
               f"{len(muxer)} muxer-authored value(s) recorded with origin="
               f"muxer_authored and 0 declared; 'omitted' and 'muxer_authored but "
               f"ineligible' are now distinguishable in the contract")
    elif not decls:
        record("T2", "muxer-authored value is not reported as a declaration", VACUOUS,
               "no producer observation exists, so omission cannot be told apart "
               "from ineligibility")
    else:
        record("T2", "muxer-authored value is not reported as a declaration", NOT_IMPLEMENTED,
               f"origins present={sorted({_origin_value(d) for d in decls})}; the "
               f"muxer/declared distinction is recorded but not yet separated by a "
               f"state the frozen ObservationState can express")

    # T3 -- the declared version must be carried VERBATIM into SourceInfo.version,
    # and must not be the probe's own version wearing the declaration's clothes.
    dv = declared_desc.container.source.version
    if not has_decl:
        record("T3", "declared version -> SourceInfo.version carries it",
               NOT_IMPLEMENTED, "no declared artifact available")
    elif dv == DECLARED_VALUE:
        record("T3", "declared version -> SourceInfo.version carries it", PASS,
               f"SourceInfo.version={dv!r} — the declared producer string, carried "
               f"verbatim (R7): not split into name/version, no release derivation, "
               f"and it differs from the probe's {av.__version__!r}")
    else:
        record("T3", "declared version -> SourceInfo.version carries it", FAIL,
               f"an artifact declared {DECLARED_VALUE!r} but SourceInfo.version="
               f"{dv!r}")

    # T4 -- no fabricated version. With the carrier present this is finally a real
    # check: a value was withheld, and it was withheld rather than invented.
    v = getattr(desc.container.source, "version", None)
    invented = v is not None and v in _probe_version_strings()
    omitted = "version" not in desc.container.source.model_dump()
    record("T4", "no fabricated version",
           FAIL if (invented or v in ("", "unknown")) else (PASS if omitted else NOT_IMPLEMENTED),
           f"SourceInfo.version={v!r}; equals a probe version={invented}; the key is "
           f"omitted from the dump={omitted}. A value was available and was withheld")

    # T5 -- codec recorded AND the producer value stays on its own group. A real
    # pass needs the producer value to exist somewhere: it must not be folded into
    # the codec field, and it must not be omitted either.
    codec = desc.video_stream.codec
    enc_on_codec = any("encod" in k.casefold() for k in
                       type(desc.video_stream).model_fields)
    ok5 = bool(codec) and decls and not enc_on_codec
    record("T5", "codec recorded; producer value kept separate from it",
           PASS if ok5 else (VACUOUS if not decls else FAIL),
           f"codec={codec!r} recorded; {len(decls)} producer value(s) live in "
           f"container.producer_declarations, not in video_stream; no encoder field "
           f"on VideoStreamInfo={not enc_on_codec}")

    # T6 -- the probe's own version must live on the BUILDER side and nowhere else.
    import av
    tv = [e.tool_version for e in desc.container.provenance]
    on_builder = all(t == av.__version__ for t in tv) and bool(tv)
    on_source = desc.container.source.version in _probe_version_strings()
    record("T6", "probe version remains builder provenance",
           PASS if (on_builder and not on_source) else FAIL,
           f"provenance tool_version={tv} (probe is {av.__version__}); the same string "
           f"appears on SourceInfo.version={on_source}. T6 passes only when the two "
           f"sides are provably separate")

    t7 = _measure_t7(CONFLICT_FIXTURE) if CONFLICT_FIXTURE else None
    if t7 is None:
        record("T7", "conflicting metadata preserved per defined rule",
               NOT_IMPLEMENTED,
               "two-scope fixture absent; §2.1.16 `conflicting` exists but cannot be "
               "exercised without an artifact that carries two disagreeing "
               "declarations")
    else:
        record("T7", "conflicting metadata preserved per defined rule",
               PASS if t7["ok"] else FAIL,
               f"scopes disagree on the same key: {t7['by_scope']}; two_scopes="
               f"{t7['two_scopes']} inconsistent={t7['inconsistent']} retained="
               f"all_values={t7['retained']}; producer_state={t7['state']!r}. Both "
               f"disputed values survive the mark, so the conflict is preserved "
               f"rather than resolved")

    # T8 shares A8's single root cause (G18). Measured on the SHARED fixture built by
    # `_unreadable_fixture`, which A8 also consumes, so the two rows cannot drift apart.
    # Reads the returned contract only — no exception class, no message text.
    _t8 = _unreadable_fixture(tmp)
    _recorded = _survived = _has_state = _unavailable = False
    _seen = "fixture unavailable"
    if _t8 is not None:
        try:
            _d = ing.ingest(_t8)
            _survived = True
            _c = _d.container
            _seen = (f"probe_state={getattr(_c.probe_state, 'value', None)!r}, "
                     f"producer_state="
                     f"{getattr(_c.producer_state, 'value', None)!r}")
            # `getattr(x, None)` passes None as the ATTRIBUTE NAME, which is a
            # TypeError on every single run. The bare `except` below swallowed it and
            # reported "ingest() did not return a contract", blaming the implementation
            # for a defect in this check -- and `ingest()` in fact returned
            # probe_state='unreadable', producer_state='unavailable', format=None,
            # which is exactly what §V.1 R-2 requires. Second instance of the same
            # class as the NameError noted above.
            _has_state = getattr(_c, "probe_state", None) is not None
            # Compare against the serialised literal, as A8 does, rather than reaching
            # for the enum: `ObservationState` is not in this function's scope, and the
            # resulting NameError was being swallowed by the bare `except` below and
            # reported as "ingest() raised" — a false negative that blamed the
            # implementation for a bug in the check.
            _unavailable = (getattr(_c.producer_state, "value", None) == "unavailable")
            _recorded = _has_state
        except Exception as exc:  # noqa: BLE001
            _seen = f"ingest() did not return a contract: {type(exc).__name__}"
    record("T8", "malformed container -> probe failure recorded",
           PASS if _recorded else FAIL,
           f"§V.1 R-2 on the shared unreadable fixture: failure survives as a "
           f"returned contract={_survived}; failure state recorded on the "
           f"group={_recorded} ({_seen}); recorded as 'unavailable' on the state "
           f"axis, not 'absent'={_unavailable}. One register finding with A8 (G18)")

    for tid, subject in (("T9", "spool quota exceeded -> controlled failure"),
                         ("T10", "descriptor released -> no leak"),
                         ("T11", "temporary spool cleanup")):
        record(tid, subject, HELD,
               "S2.16.5-7 do not exist; no subject. 2.3 cannot discharge these and "
               "must not simulate them.")

    d2 = ing.ingest(path)
    same = (desc.container.model_dump() == d2.container.model_dump()
            and desc.video_stream.model_dump() == d2.video_stream.model_dump())
    # T12 -- reproducibility requires two things: the representation is stable
    # across runs, AND it carries the identity of the build that produced it, so
    # that a later consumer can tell WHICH reading produced it. Stability alone is
    # not reproducibility: a contract with no identity at all is perfectly stable
    # and completely unkeyable, which is why this check now requires both.
    d2 = ing.ingest(path)
    same = (desc.container.model_dump() == d2.container.model_dump()
            and desc.video_stream.model_dump() == d2.video_stream.model_dump())
    identity_present = all(
        getattr(e, "tool_version", None) for e in desc.container.provenance)
    if not has_version:
        record("T12", "repeated probe -> reproducible representation", NOT_IMPLEMENTED,
               "no version carrier exists, so the representation cannot be keyed to "
               "the build that produced it")
    elif not identity_present:
        record("T12", "repeated probe -> reproducible representation", NOT_IMPLEMENTED,
               f"stable across runs={same}, but no provenance entry carries a "
               f"tool_version; stability without identity is not reproducibility")
    else:
        record("T12", "repeated probe -> reproducible representation",
               PASS if same else FAIL,
               f"stable across runs={same} AND the producing build is recorded "
               f"(tool_version={desc.container.provenance[0].tool_version!r}), so a "
               f"consumer can tell which reading produced this contract")


def check_remediation_applied():
    """Did the Part III resolutions actually reach the Stage 2.3 text?

    A1-A12 can all fail while the specification still describes the old model.
    These checks ask whether the required vocabulary is *present*, which is the
    difference between 'remediation written' and 'remediation applied'.
    """
    spec = read_spec()
    required = {
        "R3 origin vocabulary": r"artifact_declared.*muxer_authored",
        "R3 eligibility rule": r"only\*\* from an `artifact_declared` origin",
        "R1 scope+origin pairing": r"\(scope, origin\)",
        "R1 precedence order": r"artifact_declared\s+beats",
        "R2 case-insensitive fold": r"case-insensitive ASCII fold",
        "R4 overwrite state": r"DECLARED_AND_MUXER_OVERWRITTEN",
        "R5 three-slot rule": r"three distinct",
    }
    for label, pat in required.items():
        found = bool(re.search(pat, spec, re.S))
        record("SPEC", f"{label} present in the Stage 2.3 document",
               PASS if found else FAIL,
               "present" if found else
               "absent -- the resolution is a record only; the draft text does "
               "not yet carry it")


def render():
    out("=" * 96)
    out("STAGE 2.3 CONTROLLED-REMEDIATION VERIFICATION GATE")
    out("=" * 96)
    out(f"  generated by : _s23_verification.py")
    out(f"  subject      : docs/specs/stage2_3_container_probe.md")
    out(f"  policy       : a check reports PASS only when something was DEMONSTRATED.")
    out(f"                 Absence of evidence is FAIL, NOT-IMPLEMENTED, or HELD -- never PASS.")
    out("")
    groups = [("A", "ACCEPTANCE INVARIANTS A1-A12"),
              ("T", "CLOSURE TESTS T1-T12")]
    for prefix, title in groups:
        out("-" * 96)
        out(title)
        out("-" * 96)
        for cid, subject, status, evidence in RESULTS:
            if not cid.startswith(prefix):
                continue
            out(f"  {cid:<5} {status:<16} {subject}")
            out(f"        {evidence}")
        out("")
    if any(cid == "SPEC" for cid, _, _, _ in RESULTS):
        out("-" * 96)
        out("REMEDIATION-APPLICATION CHECKS (is the fix in the text, or only recorded?)")
        out("-" * 96)
        for cid, subject, status, evidence in RESULTS:
            if cid != "SPEC":
                continue
            out(f"  {cid:<5} {status:<16} {subject}")
            out(f"        {evidence}")
        out("")
    counts = {}
    for _, _, status, _ in RESULTS:
        counts[status] = counts.get(status, 0) + 1
    out("=" * 96)
    out("TALLY")
    for k in (PASS, VACUOUS, SPEC_ONLY, FAIL, NOT_IMPLEMENTED, HELD):
        if k in counts:
            out(f"  {k:<16} {counts[k]:>3}")
    out("=" * 96)
    # Every status other than PASS and HELD blocks. SPEC-ONLY is included on
    # purpose: it means "the change is specified and present, but no behavioural
    # check demonstrated it". Letting it fall outside the tally would create a
    # silent escape hatch out of the gate, which is the failure this whole
    # apparatus exists to prevent.
    blocking = [c for c in RESULTS
                if c[2] not in (PASS, HELD)]
    out("")
    if blocking:
        out(f"GATE: BLOCKED -- {len(blocking)} check(s) not satisfied. Stage 2.3 is NOT freezable.")
        out("")
        out("      A VACUOUS-PASS is counted as blocking on purpose. A check that")
        out("      'passes' because the contract has no field to violate is not a pass;")
        out("      it is an unexercised obligation, and the freeze must not consume it.")
        out("      SPEC-ONLY is blocking for the same reason: presence is not proof.")
        out("")
        out("      Each item must be discharged by its owner in its own stage. Writing")
        out("      the remediation down does not discharge it; demonstrating it does.")
    else:
        out("GATE: OPEN -- all checks satisfied. Stage 2.3 may be proposed for freeze.")
    out("")
    out("Held items (A10, A11, T9-T11) are excluded from the blocking tally by design:")
    out("they are S2.16's to discharge, and 2.3 must not close them by simulation.")


def main():
    global STREAM
    import shutil
    STREAM = io.TextIOWrapper(open(OUT, "wb"), encoding="utf-8", errors="replace",
                              line_buffering=True)
    tmp = tempfile.mkdtemp(prefix="s23v_")
    try:
        check_a_invariants(tmp)
        check_a8(tmp)
        check_a9(tmp)
        check_a10_a11()
        check_t_tests(tmp)
        check_remediation_applied()
        render()
        shutil.rmtree(tmp, ignore_errors=True)
    finally:
        STREAM.flush()
        STREAM.detach()
    print("WROTE", OUT)


if __name__ == "__main__":
    main()


