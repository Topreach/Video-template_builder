"""
Decoder — Block 1, Layer 2 (Decode).

Produces correctly ordered DecodedVideo (Contract #2) from SourceDescription (Contract #1).
Handles PTS normalization, colorspace conversion, and frame ordering.

Per Stage 1 §3: Partial decode → mark segments UNCERTAIN, continue.
Never crash; always produces a DecodedVideo with whatever was decoded.
"""
from __future__ import annotations

import os
import tempfile
from typing import Optional

import av
import numpy as np

from ..models.source_description import SourceDescription
from ..models.decoded_video import DecodedVideo
from ..utils.confidence import Confidence, ConfidenceType, ProvenanceEntry, SourceLayer


class DecodeError(Exception):
    """Raised on unrecoverable decode failure."""
    pass


class Decoder:
    """Decodes a video file into a frame sequence with normalized PTS."""

    def __init__(self, output_dir: Optional[str] = None):
        if output_dir:
            self._temp_dir = output_dir
            self._owned_temp = False
        else:
            self._temp_dir = tempfile.mkdtemp(prefix="tvb_decode_")
            self._owned_temp = True

    def decode(self, source: SourceDescription) -> DecodedVideo:
        """
        Decode video file into frames stored as PNG in a temp directory.
        Returns DecodedVideo with PTS array.
        """
        path = source.source_path

        frames_dir = os.path.join(self._temp_dir, source.id)
        os.makedirs(frames_dir, exist_ok=True)

        source_provenance = [
            ProvenanceEntry(
                layer=SourceLayer.SOURCE_NATIVE,
                evidence_refs=["source_file"],
                transform_type="decode_init",
                confidence_delta=0.0,
            )
        ]

        pts_times: list[float] = []
        frame_count = 0
        decoded_ok = True
        decode_errors: list[int] = []

        try:
            container = av.open(path, metadata_errors="warn")
        except Exception as exc:
            raise DecodeError(f"Cannot open for decoding: {exc}")

        video_stream = None
        for stream in container.streams.video:
            video_stream = stream
            break

        if video_stream is None:
            raise DecodeError("No video stream for decoding")

        time_base = video_stream.time_base
        if time_base.denominator == 0:
            time_base_sec = 1.0 / 30.0
        else:
            time_base_sec = float(time_base.numerator) / float(time_base.denominator)

        # NOTE: no pixel-format pre-selection here. Conversion to the analysis-normalized
        # representation happens in `frame.to_ndarray(format="rgb24")` below; the previous
        # `src_pix_fmt` computation was dead code.
        try:
            for frame in container.decode(video_stream):
                if frame.pts is not None:
                    pts_sec = float(frame.pts) * time_base_sec
                else:
                    # If PTS unavailable, estimate from frame index and fps
                    fps = source.fps_actual.value
                    if fps > 0:
                        pts_sec = frame_count / fps
                    else:
                        pts_sec = frame_count / 30.0

                pts_times.append(pts_sec)

                # Convert frame to RGB numpy array and save
                try:
                    np_frame = frame.to_ndarray(format="rgb24")
                    self._save_frame(np_frame, frames_dir, frame_count)
                except Exception:
                    # If we can't convert/save a frame, still record PTS
                    # Mark as decode error
                    decode_errors.append(frame_count)
                    # Create a black placeholder
                    np_frame = np.zeros((source.video_stream.height, source.video_stream.width, 3), dtype=np.uint8)
                    self._save_frame(np_frame, frames_dir, frame_count)

                frame_count += 1

        except Exception as exc:
            if frame_count == 0:
                raise DecodeError(f"Failed to decode any frames: {exc}")
            decoded_ok = False
        finally:
            container.close()

        if frame_count == 0:
            raise DecodeError("No frames decoded")

        # Normalize PTS ordering (should already be sorted, but verify)
        if len(pts_times) > 1:
            is_monotonic = all(pts_times[i] <= pts_times[i + 1] for i in range(len(pts_times) - 1))
            if not is_monotonic:
                pts_times = sorted(pts_times)

        # CFR/VFR verdict is SOURCE-NATIVE (§4: lower representations must never leak
        # upward) — a partial decode does not make the source variable-frame-rate.
        # Decode-level uncertainty is reported separately via `state` below.
        cfr_vfr_type = source.fps_actual.type

        # §6 envelope — decode confidence (previously computed and then discarded)
        confidence_val = 0.95 if decoded_ok else 0.6
        if decode_errors:
            confidence_val = 0.6
        if source.video_stream.nb_frames > 0 and frame_count < source.video_stream.nb_frames * 0.5:
            confidence_val = 0.4

        # §3 Layer 2 — partial decode: mark the affected segments UNCERTAIN, continue.
        decode_state = "measured" if (decoded_ok and not decode_errors) else "uncertain"

        provenance = source_provenance + [
            ProvenanceEntry(
                layer=SourceLayer.ANALYSIS_NORMALIZED,
                evidence_refs=[f"frame_{i}" for i in range(min(frame_count, 10))],
                transform_type="pts_normalization",
                confidence_delta=-0.0 if decoded_ok else -0.35,
            )
        ]

        return DecodedVideo(
            frames_ref=frames_dir,
            pts=pts_times,
            duration=pts_times[-1] if pts_times else 0.0,
            width=source.video_stream.width,
            height=source.video_stream.height,
            fps=source.fps_actual.value,
            cfr_vfr=cfr_vfr_type,
            frame_count=frame_count,
            codec=source.video_stream.codec,
            color_space=source.color_space.value if source.color_space else None,
            confidence=Confidence(
                value=confidence_val,
                type=ConfidenceType.MEASURED,
                calibration=0.90,
            ),
            provenance=provenance,
            state=decode_state,
            uncertain_frames=list(decode_errors),
        )

    def _save_frame(self, np_frame: np.ndarray, frames_dir: str, index: int) -> str:
        """Save a numpy array frame as PNG. Returns file path."""
        import imageio.v3 as iio
        path = os.path.join(frames_dir, f"frame_{index:06d}.png")
        iio.imwrite(path, np_frame, extension=".png")
        return path

    def cleanup(self):
        """Remove temporary frames directory."""
        if self._owned_temp:
            import shutil
            if os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir, ignore_errors=True)
