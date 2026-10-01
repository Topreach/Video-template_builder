"""
Ingestor — Block 1, Layer 1 (Ingestion).

Produces SourceDescription (Contract #1) from a video file using
source-native metadata only. No analysis models, no decoded pixel processing.

Uses PyAV (Python bindings for FFmpeg libraries) for metadata extraction.
All provenance references track Tool="PyAV".
"""
from __future__ import annotations

import os
import re
import statistics
from typing import Optional

import av
from fractions import Fraction

from ..models.source_description import (
    AudioStreamInfo,
    BitDepth,
    ChromaSubsampling,
    ColorSpace,
    ContainerInfo,
    CfrVfr,
    DurationInfo,
    FpsActual,
    GenerationalEstimate,
    ObservationOrigin,
    ProbeFailureState,
    ProducerDeclaration,
    QualityScore,
    SourceDescription,
    TransferCharacteristic,
    VideoStreamInfo,
    IngestionError,
)
from ..utils.confidence import (
    Confidence,
    ConfidenceType,
    ObservationState,
    ProvenanceEntry,
    SourceInfo,
    SourceLayer,
    producer_identity,
)

MAX_DURATION_SECONDS = 30.0

# ── Stage 2.3 R2 — key normalisation (registered rule set) ─────────────────────────
#
# Key comparison is a case-insensitive ASCII fold. The fold is a LOOKUP convenience
# only: the verbatim original key and value are always retained alongside it, per
# §2.1.15 R7. R2's whole purpose is to close the measured false absence where
# Matroska's 'ENCODER' was invisible to an exact-match lookup on 'encoder' while
# mp4's 'encoder' was found — same value, same provenance, opposite verdict.
#
# A key that matches PRODUCER_KEY_PATTERN but is absent from CANONICAL_KEYS is
# still recorded (unrecognised, rule_id=None). It is never silently dropped, and it
# never degrades to "absent": those are different audit facts.
PRODUCER_KEY_PATTERN = re.compile(
    r"encod|mux|writ|handler|tool|software|creat|title|author|comment", re.IGNORECASE
)
CANONICAL_KEYS: dict[str, str] = {
    "encoder": "r2.casefold.encoder",
    "encoder_version": "r2.casefold.encoder_version",
    "muxing_application": "r2.casefold.muxing_application",
    "writing_application": "r2.casefold.writing_application",
    "handler_name": "r2.casefold.handler_name",
    "creation_time": "r2.casefold.creation_time",
    "title": "r2.casefold.title",
    "author": "r2.casefold.author",
    "comment": "r2.casefold.comment",
}

# ── Stage 2.3 R3 — origin classification ───────────────────────────────────────────
#
# R3 measured the origin of 'Lavf62.12.102': the string is physically present in
# every FFmpeg-muxed artifact, written by the muxer into mp4's '©too' atom or
# Matroska's MuxingApp/WritingApp fields. It is NOT computed at probe time, and it
# is NOT a declaration by the authoring tool — that value is destroyed at write time
# under every write instruction measured.
#
# So the classification is not "is this string a version?" but "is this string the
# writing stack describing ITSELF?". It matches when the value is the muxer/library
# identity of the probe environment. That is a registered, documented rule, not an
# inference about producer semantics: no producer name is ever derived from it.
_MUXER_PREFIXES = ("lavf", "lavc", "lavfi")


class Ingestor:
    """Ingests a video file and produces a SourceDescription."""

    def __init__(self, max_duration: float = MAX_DURATION_SECONDS):
        self.max_duration = max_duration

    def ingest(self, path: str) -> SourceDescription:
        """
        Main entry point. Validates the file and extracts all metadata.

        Stage 2.3 §V.1 R-2 (G18) — a PROBE FAILURE is recorded ON the affected group,
        not raised away. `ingest()` therefore RETURNS A CONTRACT for every probe-level
        failure; the contract carries `container.probe_state` (a ProbeFailureState) and
        `container.producer_state = unavailable`.

        An exception is still raised for the two PRE-PROBE conditions — the path is not
        a file, or it is empty. Deliberate: no probe was attempted and no group exists,
        so recording `unavailable` on a container group would assert an observation of
        something never observed. Those are §2.1.5 `REJ_FILE_*` conditions and belong to
        the `ingestion_status` migration row (§2.1.9), which is NOT this change.
        """
        if not os.path.isfile(path):
            raise IngestionError(f"File not found: {path}", recoverable=False)

        file_size = os.path.getsize(path)
        if file_size == 0:
            raise IngestionError(f"File is empty: {path}", recoverable=False)

        source_info = SourceInfo(
            layer=SourceLayer.SOURCE_NATIVE,
            tool="PyAV",
        )

        try:
            container = av.open(path, metadata_errors="warn")
        except Exception as exc:
            # R-2: UNREADABLE is recorded on the container group. `format`/`format_long`
            # are left ABSENT rather than set to a sentinel — the format genuinely could
            # not be determined, and "unknown" is a fabrication (A9).
            return self._build_partial_description(
                path=path,
                file_size=file_size,
                source_info=source_info,
                probe_state=ProbeFailureState.UNREADABLE,
                probe_detail=f"{type(exc).__name__}: {exc}",
            )

        try:
            return self._build_source_description(
                container=container,
                path=path,
                file_size=file_size,
                source_info=source_info,
            )
        finally:
            container.close()

    def _build_partial_description(
        self,
        *,
        path: str,
        file_size: int,
        source_info: SourceInfo,
        probe_state: ProbeFailureState,
        probe_detail: str | None = None,
        container_info: ContainerInfo | None = None,
    ) -> SourceDescription:
        """A contract that SURVIVES a probe failure (Stage 2.3 §V.1 R-2, G18).

        The group is RETAINED and carries the failure. It is never replaced by an
        exception, and it is never dressed up as a successful observation.

        Two properties this must preserve, both acceptance criteria for G18:

        1. **`producer_state = UNAVAILABLE`, not `ABSENT`.** These are different facts.
           `ABSENT` means the probe read the scope and found no declaration — a SUCCESS
           outcome (§V.1 R-1). `UNAVAILABLE` means the probe could not determine it. If a
           failure recorded `ABSENT`, it would be indistinguishable from a legitimately
           empty source, which is the exact collapse the acceptance criteria forbid.

        2. **Groups the probe never reached are ABSENT, not null-filled** (§2.2 F.3.1
           rule 2). A `None` here means "this step did not run", and must never be read
           as "this step ran and found nothing".

        `probe_detail` is NON-CONTRACT human text. It exists for operators and may be
        dropped at any time; no consumer may branch on it (§2.2 T7).
        """
        if container_info is None:
            # Nothing was read, so format/format_long stay ABSENT. Writing "unknown"
            # would be a fabrication — precisely the sentinel class A9 forbids.
            container_info = ContainerInfo(
                format=None,
                format_long=None,
                size_bytes=file_size,
                source=source_info,
                producer_state=ObservationState.UNAVAILABLE,
                probe_state=probe_state,
                probe_detail=probe_detail,
            )
        else:
            container_info = container_info.model_copy(update={
                "producer_state": ObservationState.UNAVAILABLE,
                "probe_state": probe_state,
                "probe_detail": probe_detail,
            })

        return SourceDescription(
            source_path=path,
            container=container_info,
            video_stream=None,
            fps_actual=None,
            cfr_vfr=None,
            duration=None,
            quality_score=None,
        )

    def _build_source_description(
        self,
        container: av.container.InputContainer,
        path: str,
        file_size: int,
        source_info: SourceInfo,
    ) -> SourceDescription:
        """Extract all metadata and assemble SourceDescription."""
        # §2.1.15 R9: one introspection point for the builder-side tool identity.
        # R1: `estimate`-stability groups (fps_actual, duration) are produced by this
        # same probe, so their producing entry must carry tool_version or the field
        # is non-conformant. R6 permits stable groups to carry it for triage value,
        # so it is set on every entry this probe emits rather than partitioned.
        identity = producer_identity()
        provenance = [
            ProvenanceEntry(
                layer=SourceLayer.SOURCE_NATIVE,
                evidence_refs=["container_probe"],
                transform_type="none",
                confidence_delta=0.0,
                tool_version=identity["tool_version"],
            )
        ]

        # §2.1.15 R3: SourceInfo.version is the SOURCE-side declaration, and only an
        # artifact_declared origin is eligible to populate it. A muxer-authored
        # self-description is NOT a declaration by the analysed object, and the
        # probe's own version is R3-forbidden substitution. When nothing eligible
        # exists the field is simply absent — never "", never "unknown".
        source_info.version = self._declared_source_version(container)

        # Container info
        container_info = self._extract_container_info(container, file_size, source_info, provenance)

        # Find video stream
        video_stream = self._get_video_stream(container)
        if video_stream is None:
            # R-2: NO_VIDEO_STREAM is recorded on the group. The container WAS read, so
            # this partial contract keeps the real container facts it obtained rather
            # than discarding them — the group survives, which is the whole point.
            return self._build_partial_description(
                path=path, file_size=file_size, source_info=source_info,
                container_info=container_info,
                probe_state=ProbeFailureState.NO_VIDEO_STREAM,
                probe_detail="container parsed; no video stream present",
            )

        # Duration check
        duration_seconds = self._compute_duration(container, video_stream)
        if duration_seconds > self.max_duration:
            # R-2: a policy rejection is also a recorded failure state, not an exception.
            return self._build_partial_description(
                path=path, file_size=file_size, source_info=source_info,
                container_info=container_info,
                probe_state=ProbeFailureState.REJECTED_BY_POLICY,
                probe_detail=(f"Video exceeds {self.max_duration}-second limit "
                              f"(got {duration_seconds:.2f}s)"),
            )

        # Video stream info
        video_info, nb_frames = self._extract_video_stream_info(video_stream, source_info, provenance)

        # Duration info
        duration_info = self._build_duration_info(duration_seconds, container, video_stream, source_info, provenance)

        # Timing evidence is collected ONCE and shared by both analyses.
        # Demuxing the container twice does NOT work: the first pass consumes the packet queue,
        # so a second pass yields no PTS and `cfr_vfr` silently degraded to state="uncertain"
        # (confidence 0.5, variance 0.0) for EVERY source — a wrongly pessimistic contract that
        # would have emitted a spurious sparse-evidence warning on every video.
        pts_times = self._collect_pts_times(container, video_stream, max_packets=5000)

        # FPS / CFR-VFR analysis
        fps_actual = self._analyze_fps(container, video_stream, source_info, provenance, pts_times)
        cfr_vfr = self._analyze_cfr_vfr(container, video_stream, source_info, provenance, pts_times)

        # Audio streams
        audio_streams = self._extract_audio_streams(container, source_info, provenance)

        # OPTIONAL fields
        bit_depth = self._extract_bit_depth(video_stream, source_info, provenance)
        color_space = self._extract_color_space(video_stream, source_info, provenance)
        transfer = self._extract_transfer(video_stream, source_info, provenance)
        chroma = self._extract_chroma(video_stream, source_info, provenance)
        generational_estimate = self._compute_generational_estimate(video_stream, container_info, source_info, provenance)

        # Quality score heuristic
        quality_score = self._compute_quality_score(
            file_size=file_size,
            duration=duration_seconds,
            width=video_stream.width,
            height=video_stream.height,
            codec=video_info.codec,
            source_info=source_info,
        )

        return SourceDescription(
            source_path=path,
            container=container_info,
            video_stream=video_info,
            fps_actual=fps_actual,
            cfr_vfr=cfr_vfr,
            duration=duration_info,
            audio_streams=audio_streams,
            bit_depth=bit_depth,
            color_space=color_space,
            transfer=transfer,
            chroma=chroma,
            generational_estimate=generational_estimate,
            quality_score=quality_score,
        )

    # ── Extraction helpers ──

    def _extract_container_info(
        self,
        container: av.container.InputContainer,
        file_size: int,
        source_info: SourceInfo,
        provenance: list,
    ) -> ContainerInfo:
        fmt_obj = container.format
        if fmt_obj is not None:
            fmt_name = getattr(fmt_obj, "name", None) or str(fmt_obj)
            fmt_long = getattr(fmt_obj, "long_name", None) or fmt_name
        else:
            fmt_name = "unknown"
            fmt_long = "unknown"

        long_names = {
            "mov,mp4,m4a,3gp,3g2,mj2": "MOV MP4 MPEG-4 Raw",
            "matroska": "Matroska/WebM",
            "webm": "WebM",
            "avi": "AVI",
            "mpeg": "MPEG",
            "mpegts": "MPEG Transport Stream",
            "image2": "Image2 image sequence",
        }
        if fmt_name in long_names:
            fmt_long = long_names[fmt_name]

        declarations = self._extract_producer_declarations(container)
        return ContainerInfo(
            format=self._normalize_container_format(fmt_name),
            format_long=fmt_long,
            size_bytes=file_size,
            source=source_info,
            provenance=list(provenance),
            producer_declarations=declarations,
            # §2.1.16: the rollup is computed from the SAME list that is retained, so
            # the state can never describe a different observation than the record.
            producer_state=self._producer_declarations_state(declarations),
        )

    # ── Stage 2.3 R1/R2/R3 — producer declaration observation ──────────────────────

    def _producer_declarations_state(self, declarations) -> ObservationState:
        """The group-level observation state for the retained declarations (§2.1.16 S-2).

        `conflicting` requires ALL of: >= 2 values, mutually inconsistent, each from a
        distinct scope, and ALL retained. Every clause is checked here rather than
        assumed, because a `conflicting` label over a single retained value is exactly
        the false record the state exists to prevent.

        THE ROLLUP IS PER CANONICAL KEY, and this is not a detail. First written across
        the whole declaration list, it immediately reported `conflicting` for a plain
        FFmpeg file: that file has `encoder` at container scope and `handler_name` at
        stream scope, which are two different properties, not two disagreeing claims
        about one. A conflict is a contradiction about THE SAME property — anything
        looser manufactures conflicts out of ordinary multi-key metadata and would make
        the state worthless as an audit signal.

        A single value is `extracted` even when it is muxer-authored: authorship is the
        `origin` axis and is orthogonal to this one.
        """
        by_key: dict[str, set[str]] = {}
        scopes_by_key: dict[str, set[str]] = {}
        for d in declarations:
            if not d.original_value:
                continue
            by_key.setdefault(d.canonical_key, set()).add(d.original_value)
            scopes_by_key.setdefault(d.canonical_key, set()).add(d.scope)

        if any(len(values) >= 2 and len(scopes) >= 2
               for key, values in by_key.items()
               for scopes in [scopes_by_key[key]]):
            return ObservationState.CONFLICTING
        if not declarations:
            return ObservationState.ABSENT
        return ObservationState.EXTRACTED

    def _extract_producer_declarations(
        self,
        container: av.container.InputContainer,
    ) -> list[ProducerDeclaration]:
        """Observe producer-related metadata across scopes, with authorship.

        R1: scope is recorded, never assumed. A container-scope value and a
        stream-scope value are different observations even when the strings match,
        because they are written by different things. Both values are ALWAYS retained
        here — this method never drops or prefers one. The `conflicting` rollup and
        the precedence rule live in `_producer_declarations_state`, which consumes the
        §2.1 v1.3 `ObservationState.CONFLICTING` member (S-3: retention precedes
        marking, so the record is built before the state describes it).

        R2: keys are matched by case-insensitive fold against a registered set; the
        original key and value are always kept verbatim.
        """
        found: list[ProducerDeclaration] = []
        scopes: list[tuple[str, dict]] = [("container", dict(container.metadata or {}))]
        for stream in container.streams:
            if stream.type == "video":
                scopes.append(("video_stream", dict(stream.metadata or {})))
        for scope, metadata in scopes:
            for original_key, original_value in metadata.items():
                if not isinstance(original_value, str):
                    continue
                if not PRODUCER_KEY_PATTERN.search(original_key):
                    continue
                canonical = original_key.casefold()
                found.append(
                    ProducerDeclaration(
                        scope=scope,
                        canonical_key=canonical,
                        original_key=original_key,
                        original_value=original_value,
                        origin=self._classify_producer_origin(canonical, original_value),
                        state=ObservationState.EXTRACTED,
                        rule_id=CANONICAL_KEYS.get(canonical),
                    )
                )
        return found

    def _declared_source_version(self, container) -> Optional[str]:
        """The source-side producer string, or None when the artifact declares none.

        §2.1.15 R3 + Stage 2.3 R3, applied together:

          - only an `artifact_declared` origin is eligible;
          - a `muxer_authored` value is the writing stack describing itself and is
            NOT a declaration by the analysed object;
          - the probe's own version is a R3-forbidden substitution;
          - the value is copied VERBATIM (R7): no splitting into name and version,
            no canonicalising, no release-name derivation;
          - when nothing is eligible, None is returned and the field is omitted.
            Never "" and never "unknown" (R3).

        Scope precedence follows R1: container scope outranks video-stream scope,
        because a container-scope declaration describes the object as a whole.
        """
        best: Optional[tuple[int, str]] = None
        for decl in self._extract_producer_declarations(container):
            if decl.origin is not ObservationOrigin.ARTIFACT_DECLARED:
                continue
            if not decl.original_value.strip():
                continue
            rank = 0 if decl.scope == "container" else 1
            if best is None or rank < best[0]:
                best = (rank, decl.original_value)
        return best[1] if best else None

    def _classify_producer_origin(
        self,
        canonical_key: str,
        value: str,
    ) -> ObservationOrigin:
        """Attribute a producer-related value to an author (R3).

        The only judgement made here is authorship: did the writing stack write this
        about itself? No producer name, release, or application identity is ever
        derived, because deriving one is the inference A9 forbids and §2.3.11 bans.
        """
        if not value:
            return ObservationOrigin.UNAVAILABLE
        folded = value.casefold()
        # The writing stack stamps itself as e.g. 'Lavf62.12.102' (libavformat) or
        # 'Lavc61.3.100' (libavcodec). Matching the observed value against the
        # libraries actually loaded is stricter than matching the 'Lav*' prefix and
        # so cannot mislabel an unrelated tag that merely starts with those letters.
        for lib, prefix in (("libavformat", "lavf"), ("libavcodec", "lavc")):
            version = getattr(av, "library_versions", {}).get(lib)
            if not version:
                continue
            dotted = ".".join(str(n) for n in version)
            squashed = dotted.replace(".", "")
            if folded in (f"{prefix}{dotted}", f"{prefix}{squashed}"):
                return ObservationOrigin.MUXER_AUTHORED
        if canonical_key in ("muxing_application", "writing_application", "encoder"):
            return ObservationOrigin.ARTIFACT_DECLARED
        return ObservationOrigin.PROBE_OBSERVED

    @staticmethod
    def _normalize_container_format(fmt: str) -> str:
        """Normalize container format name to canonical short name."""
        if "mp4" in fmt or "mov" in fmt:
            return "mp4"
        if "matroska" in fmt or "webm" in fmt:
            return fmt
        return fmt.split(",")[0]

    def _get_video_stream(self, container: av.container.InputContainer) -> Optional[av.stream.Stream]:
        """Return the first video stream, or None if no video stream exists."""
        for stream in container.streams.video:
            return stream
        return None

    def _extract_video_stream_info(
        self,
        stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
    ) -> tuple[VideoStreamInfo, int]:
        codec = stream.codec.name or "unknown"
        codec_long = stream.codec.long_name or codec

        frame_rate = self._get_frame_rate(stream)
        avg_frame_rate = self._get_avg_frame_rate(stream)
        time_base = self._format_rational(stream.time_base)

        # Count frames if available
        nb_frames = stream.frames or 0

        coded_w = getattr(stream, "coded_width", 0) or 0
        coded_h = getattr(stream, "coded_height", 0) or 0

        dar = getattr(stream, "display_aspect_ratio", None)
        # Amendment Record v1.2 / S-1: absence is null. The previous fallback="0:1"
        # fabricated a zero aspect ratio for every stream declaring none — a value no
        # consumer could mistake for a measurement, yet emitted as though it were one.
        dar_str = self._format_display_ratio(dar, fallback=None)

        sar = getattr(stream, "sample_aspect_ratio", None)
        # stage2_source_description.md Amendment Record v1.1 / S-1: absence is null.
        # The previous fallback="1:1" fabricated a square ratio for every stream that
        # simply declares none — indistinguishable from a real 1:1 (G10 / A9).
        sar_str = self._format_display_ratio(sar, fallback=None)

        level_val = getattr(stream, "level", None)
        if level_val is not None and not isinstance(level_val, str):
            level_val = str(level_val)

        info = VideoStreamInfo(
            codec=codec,
            codec_long=codec_long,
            profile=stream.profile if stream.profile else None,
            level=level_val,
            width=stream.width,
            height=stream.height,
            coded_width=coded_w if coded_w else stream.width,
            coded_height=coded_h if coded_h else stream.height,
            display_aspect_ratio=dar_str,
            sample_aspect_ratio=sar_str,
            frame_rate=frame_rate,
            avg_frame_rate=avg_frame_rate,
            time_base=time_base,
            nb_frames=nb_frames,
            source=source_info,
            provenance=list(provenance),
        )
        return info, nb_frames

    @staticmethod
    def _get_frame_rate(stream: av.stream.Stream) -> str:
        """Get frame rate as a rational string. Tries base_rate, codec_context.framerate."""
        rate = getattr(stream, "base_rate", None)
        if rate is None:
            cc = getattr(stream, "codec_context", None)
            if cc:
                rate = getattr(cc, "framerate", None)
        if rate is None:
            return "0/0"
        return Ingestor._format_rational(rate)

    @staticmethod
    def _get_avg_frame_rate(stream: av.stream.Stream) -> str:
        """Compute average frame rate from stream duration and frames."""
        if stream.frames and stream.frames > 0:
            duration = getattr(stream, "duration", None)
            if duration and duration > 0:
                tb = stream.time_base
                if tb.denominator != 0:
                    duration_sec = float(duration) * float(tb.numerator) / float(tb.denominator)
                    if duration_sec > 0:
                        avg = stream.frames / duration_sec
                        return f"{avg:.2f}/1"
        rate = getattr(stream, "base_rate", None)
        if rate is not None:
            return Ingestor._format_rational(rate)
        cc = getattr(stream, "codec_context", None)
        if cc:
            fr = getattr(cc, "framerate", None)
            if fr is not None:
                return Ingestor._format_rational(fr)
        return "0/0"

    @staticmethod
    def _format_rational(rat) -> str:
        """Format a PyAV Fraction or tuple as a string rational."""
        if rat is None:
            return "0/0"
        if isinstance(rat, Fraction):
            return f"{rat.numerator}/{rat.denominator}"
        if hasattr(rat, "numerator") and hasattr(rat, "denominator"):
            return f"{rat.numerator}/{rat.denominator}"
        if isinstance(rat, (tuple, list)) and len(rat) == 2:
            return f"{rat[0]}/{rat[1]}"
        if isinstance(rat, (int, float)):
            return f"{rat}/1"
        return str(rat)

    @staticmethod
    def _format_display_ratio(rat, fallback: Optional[str]) -> Optional[str]:
        """
        Format a PyAV aspect-ratio value as "W:H", or return `fallback` when absent.

        PyAV returns `fractions.Fraction` for video_stream.display_aspect_ratio and
        sample_aspect_ratio (see av/video/stream.pyi: `Fraction | None`). A Fraction is
        NOT subscriptable, so indexing it raises TypeError — which previously crashed
        ingestion on any clip carrying SAR/DAR metadata. Accept every shape FFmpeg can
        hand back (Fraction, tuple/list, None) and validate before formatting.

        stage2_source_description.md Amendment Record v1.1: `fallback` is now
        `Optional[str]` and may be None. Callers that pass None get genuine absence
        rather than a fabricated ratio — which was the whole point (G10 / A9).

        KNOWN LIMIT (that record's S-5): the four ways this returns None — source
        absent, unparseable shape, unparseable value, non-positive — are collapsed into
        one result. At T1 granularity they cannot be separated without a per-field
        ObservationState, so None currently means "no usable value", not strictly
        "declares none". That residual is recorded, not fixed here.
        """
        if rat is None:
            return fallback

        num = getattr(rat, "numerator", None)
        den = getattr(rat, "denominator", None)
        if num is None and isinstance(rat, (tuple, list)) and len(rat) == 2:
            num, den = rat[0], rat[1]
        if num is None:
            return fallback

        try:
            num_i, den_i = int(num), int(den)
        except (TypeError, ValueError):
            return fallback

        if num_i <= 0 or den_i <= 0:
            return fallback
        return f"{num_i}:{den_i}"

    def _compute_duration(
        self,
        container: av.container.InputContainer,
        video_stream: av.stream.Stream,
    ) -> float:
        """
        Compute duration in seconds, preferring container-level, then stream-level.
        PyAV container.duration is in microseconds (AV_TIME_BASE = 1000000).
        """
        AV_TIME_BASE = 1_000_000

        if container.duration and container.duration > 0:
            return float(container.duration) / AV_TIME_BASE

        if video_stream.duration and video_stream.duration > 0:
            tb = video_stream.time_base
            if tb.denominator != 0:
                return float(video_stream.duration) * float(tb.numerator) / float(tb.denominator)

        # Fallback: compute from frame count and frame rate
        if video_stream.frames:
            base_rate = getattr(video_stream, "base_rate", None)
            if base_rate is not None and base_rate != 0:
                rate_float = float(base_rate)
                if rate_float > 0:
                    return float(video_stream.frames) / rate_float

        return 0.0

    def _build_duration_info(
        self,
        duration_seconds: float,
        container: av.container.InputContainer,
        video_stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
    ) -> DurationInfo:
        start_time = 0.0
        if video_stream.start_time is not None:
            tb = video_stream.time_base
            start_time = float(video_stream.start_time) * float(tb.numerator) / float(tb.denominator)

        end_time = start_time + duration_seconds

        return DurationInfo(
            value=duration_seconds,
            start_time=start_time,
            end_time=end_time,
            confidence=Confidence(
                value=0.95,
                type=ConfidenceType.MEASURED,
                calibration=0.95,
            ),
            source=source_info,
            provenance=list(provenance),
        )

    def _analyze_fps(
        self,
        container: av.container.InputContainer,
        video_stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
        pts_times: Optional[list[float]] = None,
    ) -> FpsActual:
        """
        Compute actual FPS from r_frame_rate.
        Falls back to avg_frame_rate, then to PTS analysis.
        """
        fps_value = 0.0
        confidence = 0.95
        fps_type = "cfr"

        # Primary: base_rate
        base_rate = getattr(video_stream, "base_rate", None)
        if base_rate is not None and base_rate != 0:
            if hasattr(base_rate, "denominator") and base_rate.denominator != 0:
                fps_value = float(Fraction(base_rate))
            else:
                fps_value = float(base_rate)
            fps_type = "cfr"
        # Fallback: codec_context.framerate
        elif video_stream.codec_context and getattr(video_stream.codec_context, "framerate", None) is not None:
            fr = video_stream.codec_context.framerate
            if hasattr(fr, "denominator") and fr.denominator != 0:
                fps_value = float(Fraction(fr))
            else:
                fps_value = float(fr)
            fps_type = "cfr"
        # Fallback: PTS analysis (expensive but accurate)
        else:
            fps_value, fps_type, confidence = self._compute_fps_from_pts(
                container, video_stream, source_info, provenance, pts_times
            )

        fps_state = "extracted" if fps_value > 0 else "uncertain"

        if fps_value > 0:
            # §2.9 step 5 — refine from CFR/VFR analysis
            cfr_vfr_result = self._analyze_cfr_vfr(
                container, video_stream, source_info, provenance, pts_times
            )
            if fps_type == "cfr" and cfr_vfr_result.is_vfr:
                fps_type = "vfr" if cfr_vfr_result.variance > 0.01 else "mixed"
                confidence = min(confidence, cfr_vfr_result.confidence.value)
            # §2.6 rule 5 / §2.5 — "PTS analysis failure → mark uncertain".
            # The verdict is only trustworthy if the timing analysis itself is extracted.
            if cfr_vfr_result.state != "extracted":
                fps_state = "uncertain"
                confidence = min(confidence, 0.5)

        return FpsActual(
            value=fps_value,
            type=fps_type,
            state=fps_state,
            confidence=Confidence(
                value=confidence,
                type=ConfidenceType.MEASURED,
                calibration=0.95,
            ),
            source=source_info,
            provenance=list(provenance),
        )

    def _compute_fps_from_pts(
        self,
        container: av.container.InputContainer,
        video_stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
        pts_times: Optional[list[float]] = None,
    ) -> tuple[float, str, float]:
        """
        Compute FPS by analyzing PTS timestamps of decoded frames.
        """
        if pts_times is None:
            pts_times = self._collect_pts_times(container, video_stream, max_packets=1000)
        if len(pts_times) < 2:
            return 0.0, "unknown", 0.0

        deltas = [pts_times[i + 1] - pts_times[i] for i in range(len(pts_times) - 1)]
        valid_deltas = [d for d in deltas if d > 0]
        if not valid_deltas:
            return 0.0, "unknown", 0.0

        median_delta = statistics.median(valid_deltas)
        fps = 1.0 / median_delta if median_delta > 0 else 0.0

        delta_std = statistics.pstdev(valid_deltas) if len(valid_deltas) > 1 else 0.0
        variance = delta_std / median_delta if median_delta > 0 else 0.0

        fps_type = "cfr" if variance < 0.01 else ("vfr" if variance > 0.1 else "mixed")
        confidence = max(0.5, 1.0 - variance)

        return fps, fps_type, confidence

    def _analyze_cfr_vfr(
        self,
        container: av.container.InputContainer,
        video_stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
        pts_times: Optional[list[float]] = None,
    ) -> CfrVfr:
        """
        Detect whether the video is CFR (constant frame rate) or VFR.
        Analysis: collect PTS for up to 5000 frames, compute delta variance.

        `pts_times` is supplied by the caller so the packet queue is drained only once —
        a second demux pass on the same container yields nothing.
        """
        if pts_times is None:
            pts_times = self._collect_pts_times(container, video_stream, max_packets=5000)

        if len(pts_times) < 2:
            return CfrVfr(
                is_cfr=True, is_vfr=False, variance=0.0, max_delta=0.0,
                state="uncertain",
                confidence=Confidence(value=0.5, type=ConfidenceType.MEASURED, calibration=0.9),
                source=source_info, provenance=list(provenance),
            )

        # Sort PTS for display-order analysis (B-frames may reorder packets)
        pts_times = sorted(pts_times)
        deltas = [pts_times[i + 1] - pts_times[i] for i in range(len(pts_times) - 1)]
        valid_deltas = [d for d in deltas if d > 0]

        # §2.6 rule 5 — in *display* order, timestamps must strictly advance. A zero or
        # negative gap means duplicate/broken PTS, so the timing verdict cannot be trusted.
        # (Decode order alone is not a violation — B-frames legitimately reorder packets,
        # which is exactly why the sort above happens before this check.)
        has_duplicate_pts = any(d <= 0 for d in deltas)
        if not valid_deltas:
            return CfrVfr(
                is_cfr=True, is_vfr=False, variance=0.0, max_delta=0.0,
                state="uncertain",
                confidence=Confidence(value=0.5, type=ConfidenceType.MEASURED, calibration=0.9),
                source=source_info, provenance=list(provenance),
            )

        # Determine nominal FPS for CFR comparison
        nominal_fps = 0.0
        base_rate = getattr(video_stream, "base_rate", None)
        if base_rate is not None and base_rate != 0:
            if hasattr(base_rate, "denominator") and base_rate.denominator != 0:
                nominal_fps = float(Fraction(base_rate))
            else:
                nominal_fps = float(base_rate)
        if nominal_fps <= 0 and video_stream.codec_context:
            fr = getattr(video_stream.codec_context, "framerate", None)
            if fr is not None:
                if hasattr(fr, "denominator") and fr.denominator != 0:
                    nominal_fps = float(Fraction(fr))
                else:
                    nominal_fps = float(fr)
        if nominal_fps <= 0:
            nominal_fps = float(len(pts_times)) / max(pts_times[-1], 0.001)

        nominal_delta = 1.0 / nominal_fps if nominal_fps > 0 else statistics.median(valid_deltas)
        deltas_from_nominal = [abs(d - nominal_delta) for d in valid_deltas]

        variance = statistics.pstdev(deltas) if len(deltas) > 1 else 0.0
        max_delta = max(deltas_from_nominal)

        is_vfr = max_delta > 0.002 or (len(valid_deltas) > 10 and variance / nominal_delta > 0.005)
        is_cfr = not is_vfr

        confidence_val = 1.0 if is_cfr else max(0.5, 1.0 - (max_delta / nominal_delta * 2))
        if confidence_val < 0.5:
            confidence_val = 0.5

        state = "extracted" if len(pts_times) >= 10 else "uncertain"
        if len(pts_times) < 10:
            confidence_val = min(confidence_val, 0.5)

        # §2.7 — VFR with extreme jitter (max_delta > 0.1s): mark uncertain, continue.
        # NOTE: Stage 1 §3 lists "extreme VFR" under Layer-1 rejection, but Stage 2 §2.7
        # (and the "never crash" principle) mandate UNCERTAIN + continue. Stage 2 wins.
        if is_vfr and max_delta > 0.1:
            state = "uncertain"
            confidence_val = min(confidence_val, 0.5)

        if has_duplicate_pts:
            state = "uncertain"
            confidence_val = min(confidence_val, 0.5)

        return CfrVfr(
            is_cfr=is_cfr,
            is_vfr=is_vfr,
            variance=variance,
            max_delta=max_delta,
            state=state,
            confidence=Confidence(
                value=confidence_val,
                type=ConfidenceType.MEASURED,
                calibration=0.92 if state == "extracted" else 0.5,
            ),
            source=source_info,
            provenance=list(provenance),
        )

    def _collect_pts_times(
        self,
        container: av.container.InputContainer,
        video_stream: av.stream.Stream,
        max_packets: int = 5000,
    ) -> list[float]:
        """
        Collect PTS timestamps from packets using container.demux().
        In PyAV 18, decoded frames may not carry PTS, so we use packet PTS.
        PTS are in decode order (B-frames may reorder); caller sorts if needed.
        """
        pts_times: list[float] = []
        tb = video_stream.time_base
        if tb.denominator == 0:
            return pts_times

        time_base_sec = float(tb.numerator) / float(tb.denominator)

        try:
            for i, packet in enumerate(container.demux(video_stream)):
                if i >= max_packets:
                    break
                if packet.pts is not None:
                    pts_times.append(float(packet.pts) * time_base_sec)
        except Exception:
            pass

        return pts_times

    def _extract_audio_streams(
        self,
        container: av.container.InputContainer,
        source_info: SourceInfo,
        provenance: list,
    ) -> list[AudioStreamInfo]:
        """Extract audio stream info. Empty array if no audio."""
        result = []
        for stream in container.streams.audio:
            codec = stream.codec.name or "unknown"
            codec_long = stream.codec.long_name or codec

            duration = 0.0
            if stream.duration and stream.time_base.denominator != 0:
                duration = float(stream.duration) * float(stream.time_base.numerator) / float(stream.time_base.denominator)

            channel_layout = "unknown"
            layout = getattr(stream, "layout", None)
            if layout is not None:
                channel_layout = str(layout) if not isinstance(layout, str) else layout

            result.append(
                AudioStreamInfo(
                    stream_index=stream.index,
                    codec=codec,
                    codec_long=codec_long,
                    sample_rate=stream.sample_rate or 0,
                    channels=stream.channels or 0,
                    channel_layout=channel_layout,
                    bits_per_sample=getattr(stream, "bits_per_sample", None),
                    duration=duration,
                    bit_rate=getattr(stream, "bit_rate", None),
                    language=stream.metadata.get("language") if stream.metadata else None,
                    title=stream.metadata.get("title") if stream.metadata else None,
                    source=source_info,
                    provenance=list(provenance),
                )
            )
        return result

    def _extract_bit_depth(
        self,
        stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
    ) -> Optional[BitDepth]:
        """Extract bit depth from pixel format. None if not determinable."""
        pix_fmt = stream.pix_fmt if hasattr(stream, "pix_fmt") else None
        if pix_fmt:
            depth = self._bit_depth_from_pix_fmt(pix_fmt)
            if depth:
                return BitDepth(
                    luma=depth,
                    chroma=depth,
                    confidence=Confidence(
                        value=0.85,
                        type=ConfidenceType.MEASURED,
                        calibration=0.90,
                    ),
                    source=source_info,
                    provenance=list(provenance),
                )
        return None

    @staticmethod
    def _bit_depth_from_pix_fmt(pix_fmt: str) -> Optional[int]:
        """Infer bit depth from pixel format string."""
        # PyAV pixel format names
        depth_map = {
            "yuv420p": 8,
            "yuv422p": 8,
            "yuv444p": 8,
            "yuv420p10le": 10,
            "yuv422p10le": 10,
            "yuv444p10le": 10,
            "yuv420p12le": 12,
            "yuv422p12le": 12,
            "yuv444p12le": 12,
            "yuv420p10be": 10,
            "yuv422p10be": 10,
            "yuv444p10be": 10,
            "yuv420p16le": 16,
            "yuv444p16le": 16,
            "nv12": 8,
            "nv21": 8,
            "rgb24": 8,
            "rgb48le": 16,
            "gbrp": 8,
            "gbrp10le": 10,
            "gbrp12le": 12,
            "yuv444p16le": 16,
            "p010le": 10,
            "p012le": 12,
            "p210le": 10,
            "p420le": 12,
            "bgr0": 8,
            "bgra": 8,
            "rgba": 8,
            "gray": 8,
            "gray10le": 10,
            "gray12le": 12,
            "gray16le": 16,
            "yuv420p9": 9,
            "yuv420p9le": 9,
            "yuv422p9le": 9,
            "yuv444p9le": 9,
        }
        return depth_map.get(pix_fmt)

    def _extract_color_space(
        self,
        stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
    ) -> Optional[ColorSpace]:
        """Extract color space info from pixel format."""
        pix_fmt = stream.pix_fmt if hasattr(stream, "pix_fmt") else None
        if pix_fmt:
            color_info = self._color_info_from_pix_fmt(pix_fmt)
            full_name = color_info.get("full_name", f"Pixel format {pix_fmt}")
            # A fallback name means the pixel format was not recognised → looked for,
            # ambiguous (§9.1). Previously the confidence expression was dead code.
            recognized = not full_name.startswith("Pixel format ")
            return ColorSpace(
                value=pix_fmt,
                full_name=full_name,
                state="extracted" if recognized else "uncertain",
                confidence=Confidence(
                    value=0.95 if recognized else 0.5,
                    type=ConfidenceType.MEASURED,
                    calibration=0.95 if recognized else 0.5,
                ),
                source=source_info,
                provenance=list(provenance),
            )
        return None

    @staticmethod
    def _color_info_from_pix_fmt(pix_fmt: str) -> dict:
        """Return color info for a pixel format."""
        if pix_fmt.startswith("yuv"):
            return {"full_name": "YUV color space restrictions"}
        elif pix_fmt.startswith("rgb"):
            return {"full_name": "RGB color space"}
        elif pix_fmt.startswith("gray"):
            return {"full_name": "YUV grayscale"}
        elif pix_fmt.startswith("gbrp"):
            return {"full_name": "RGB planar"}
        return {"full_name": f"Pixel format {pix_fmt}"}

    def _extract_transfer(
        self,
        stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
    ) -> Optional[TransferCharacteristic]:
        """Extract transfer characteristic from color metadata."""
        color_trc = getattr(stream, "color_transfer", None)
        if not color_trc and stream.metadata:
            color_trc = stream.metadata.get("color_trc")

        if color_trc:
            return TransferCharacteristic(
                value=str(color_trc),
                confidence=Confidence(value=0.90, type=ConfidenceType.MEASURED, calibration=0.90),
                source=source_info,
                provenance=list(provenance),
            )
        return None

    def _extract_chroma(
        self,
        stream: av.stream.Stream,
        source_info: SourceInfo,
        provenance: list,
    ) -> Optional[ChromaSubsampling]:
        """Extract chroma subsampling from pixel format."""
        pix_fmt = stream.pix_fmt if hasattr(stream, "pix_fmt") else None
        if pix_fmt:
            subsampling = self._chroma_subsampling_from_pix_fmt(pix_fmt)
            if subsampling:
                return ChromaSubsampling(
                    subsampling=subsampling,
                    confidence=Confidence(
                        value=0.95,
                        type=ConfidenceType.MEASURED,
                        calibration=0.95,
                    ),
                    source=source_info,
                    provenance=list(provenance),
                )
        return None

    @staticmethod
    def _chroma_subsampling_from_pix_fmt(pix_fmt: str) -> Optional[str]:
        """Infer chroma subsampling from pixel format."""
        if "420" in pix_fmt:
            return "4:2:0"
        elif "422" in pix_fmt:
            return "4:2:2"
        elif "444" in pix_fmt:
            return "4:4:4"
        elif "411" in pix_fmt:
            return "4:1:1"
        elif "410" in pix_fmt:
            return "4:1:0"
        elif "nv12" in pix_fmt:
            return "4:2:0"
        elif pix_fmt.startswith("rgb") or pix_fmt.startswith("gbrp") or pix_fmt.startswith("bgr"):
            return None  # No chroma subsampling in pure RGB
        elif "gray" in pix_fmt:
            return None  # No chroma in grayscale
        return None

    def _compute_generational_estimate(
        self,
        stream: av.stream.Stream,
        container_info: ContainerInfo,
        source_info: SourceInfo,
        provenance: list,
    ) -> Optional[GenerationalEstimate]:
        """
        Heuristic estimate of source device generation from metadata.
        """
        factors: list[str] = []
        estimate = "unknown"

        codec = stream.codec.name
        if codec == "hevc" and "10" in (stream.profile or ""):
            factors.append("hevc_main_10_profile")
            estimate = "prosumer_phone"
        elif codec == "hevc":
            factors.append("hevc_codec")
            estimate = "prosumer_phone"
        elif codec == "h264" and "high" in (stream.profile or "").lower():
            factors.append("h264_high_profile")
            estimate = "prosumer_phone"
        elif codec == "h264":
            factors.append("h264_baseline_or_main")
            estimate = "prosumer_phone"
        elif codec in ("proRes", "prores"):
            factors.append("prores_codec")
            estimate = "broadcast"
        elif codec == "dnxhd":
            factors.append("dnxhd_codec")
            estimate = "broadcast"
        elif codec == "ffv1":
            factors.append("ffv1_lossless")
            estimate = "cinema"

        # Container-specific hints
        if container_info.format in ("mov", "mp4", "m4a"):
            factors.append("apple_ecosystem_container")

        # Bitrate hint
        v_bit_rate = getattr(stream, "bit_rate", None)
        if v_bit_rate and v_bit_rate > 50000000:
            factors.append("high_bitrate")
            if estimate == "unknown":
                estimate = "broadcast"

        confidence_val = 0.60 if estimate != "unknown" else 0.30

        return GenerationalEstimate(
            value=estimate,
            # D-2 (Stage 2 §2.1.13) — an estimate; "unknown" means the heuristic could not
            # establish it, which is `unavailable` (never `absent`: absence of generation
            # evidence is not absence of generation).
            state="extracted" if estimate != "unknown" else "unavailable",
            confidence=Confidence(
                value=confidence_val,
                type=ConfidenceType.SEMANTIC_INTERPRETATION,
                calibration=0.85,
            ),
            source=source_info,
            provenance=list(provenance),
        )

    def _compute_quality_score(
        self,
        file_size: int,
        duration: float,
        width: int,
        height: int,
        codec: str,
        source_info: SourceInfo,
    ) -> QualityScore:
        """
        Heuristic quality score based on bitrate, resolution, and codec.
        State: "measured" if calculable, "uncertain" if insufficient data, "absent" if no video.
        """
        if duration <= 0 or file_size <= 0:
            return QualityScore(
                value=None,
                state="absent",
                confidence=Confidence(value=0.0, type=ConfidenceType.MEASURED, calibration=1.0),
                source=source_info,
            )

        # Estimate bitrate (total file, rough proxy)
        total_bitrate = (file_size * 8) / duration

        # Heuristic scoring
        resolution_score = min(1.0, (width * height) / (1920 * 1080))
        codec_score = {"hevc": 0.95, "h264": 0.85, "vp9": 0.90, "av1": 0.95}
        bitrate_score = min(1.0, total_bitrate / 20_000_000)  # 20Mbps = perfect

        score = (resolution_score * 0.3 + codec_score.get(codec, 0.5) * 0.4 + bitrate_score * 0.3)

        # §9.1 UNCERTAIN-ALLOWED + §2.5 "Uncertain if insufficient data".
        # Previously both branches set state="measured", making "uncertain" unreachable.
        if codec not in codec_score or total_bitrate < 500_000:
            state = "uncertain"
            confidence_val = 0.4
        else:
            state = "extracted"
            confidence_val = 0.75

        return QualityScore(
            value=round(score, 4),
            state=state,
            confidence=Confidence(
                value=confidence_val,
                type=ConfidenceType.MEASURED,
                calibration=0.85,
            ),
            source=source_info,
            provenance=[
                ProvenanceEntry(
                    layer=SourceLayer.SOURCE_NATIVE,
                    evidence_refs=["file_size", "duration", "resolution", "codec"],
                    transform_type="heuristic_scoring",
                    confidence_delta=0.0,
                    # §2.1.15 R1: this is an `estimate` (a heuristic), so its producing
                    # entry MUST carry tool_version or the field is non-conformant.
                    # R9: obtained from the one introspection point, never ad hoc.
                    tool_version=producer_identity()["tool_version"],
                )
            ],
        )
