"""
Stage 2.3 §V.1 R-2 (G18) — a probe failure is RECORDED ON THE GROUP, not raised away.

These are the acceptance criteria for closing G18. `test_unreadable_is_not_metadata_absent`
is the one that decides it: a migration that merely stopped `ingest()` raising would
satisfy the other checks and still collapse UNREADABLE into METADATA_ABSENT.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

import av  # noqa: E402
import numpy as np  # noqa: E402

from videotemplate.ingestion.ingestor import Ingestor  # noqa: E402
from videotemplate.models.source_description import (  # noqa: E402
    IngestionError, ProbeFailureState,
)
from videotemplate.utils.confidence import ObservationState  # noqa: E402


def _valid_clip(path):
    c = av.open(path, "w")
    st = c.add_stream("libx264", rate=10)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    for i in range(10):
        f = np.zeros((120, 160, 3), dtype=np.uint8)
        f[40:60, i * 8:(i * 8) + 8] = 255
        vf = av.VideoFrame.from_ndarray(f, format="rgb24")
        vf.pts = i
        for p in st.encode(vf):
            c.mux(p)
    for p in st.encode(None):
        c.mux(p)
    c.close()
    return path


def _garbage(path):
    with open(path, "wb") as fh:
        fh.write(b"A" * 128)
    return path


def _audio_only(path):
    c = av.open(path, "w")
    a = c.add_stream("pcm_s16le", rate=48000)
    a.layout = av.AudioLayout("stereo")
    c.start_encoding()
    for i in range(4):
        af = av.AudioFrame(format="s16", layout="stereo", samples=1024)
        af.sample_rate = 48000
        af.pts = i * 1024
        for p in a.encode(af):
            c.mux(p)
    for p in a.encode(None):
        c.mux(p)
    c.close()
    return path


class TestProbeFailureRecordedOnGroup(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        self.ing = Ingestor(max_duration=30.0)

    def test_unreadable_is_not_metadata_absent_on_the_state_axis(self):
        """Acceptance criterion 3 — THE DECIDING TEST.

        Two inputs side by side that a naive migration would make equivalent:
          * a VALID container whose scopes carry no producer declaration -> ABSENT
          * an UNREADABLE container                                     -> UNAVAILABLE
        They must not converge merely because both yield no producer value.
        """
        valid = self.ing.ingest(_valid_clip(str(self.tmp / "ok.mp4"))).container
        broken = self.ing.ingest(_garbage(str(self.tmp / "bad.mp4"))).container
        self.assertIsNone(valid.probe_state,
                          "a successful probe must not report a failure state")
        self.assertEqual(broken.probe_state, ProbeFailureState.UNREADABLE)
        self.assertNotEqual(valid.producer_state, broken.producer_state,
                            "UNREADABLE and 'read, nothing declared' must differ "
                            "on the state axis")

    def test_failure_records_unavailable_never_absent(self):
        """§V.1 R-1: ABSENT is a SUCCESS outcome. A failure must never record it."""
        for name, builder in (("g.mp4", _garbage), ("a.mkv", _audio_only)):
            info = self.ing.ingest(builder(str(self.tmp / name))).container
            with self.subTest(name=name):
                self.assertEqual(info.producer_state,
                                 ObservationState.UNAVAILABLE)
                self.assertNotEqual(info.producer_state, ObservationState.ABSENT)

    def test_groups_never_reached_are_absent_not_null_filled(self):
        """§2.2 F.3.1 rule 2: None means 'this step did not run'."""
        desc = self.ing.ingest(_garbage(str(self.tmp / "g2.mp4")))
        for name in ("video_stream", "fps_actual", "cfr_vfr", "duration",
                     "quality_score"):
            with self.subTest(group=name):
                self.assertIsNone(getattr(desc, name))

    def test_no_sentinel_is_invented_for_an_undetermined_format(self):
        """Recording UNREADABLE must not fabricate format='unknown' — that is the
        exact sentinel class A9 was discharged for removing."""
        info = self.ing.ingest(_garbage(str(self.tmp / "g3.mp4"))).container
        self.assertIsNone(info.format)
        self.assertIsNone(info.format_long)

    def test_successful_probe_still_populates_every_group(self):
        """The migration must not hollow out the success path."""
        desc = self.ing.ingest(_valid_clip(str(self.tmp / "ok2.mp4")))
        for name in ("video_stream", "fps_actual", "cfr_vfr", "duration",
                     "quality_score"):
            with self.subTest(group=name):
                self.assertIsNotNone(getattr(desc, name))
        self.assertIsNone(desc.container.probe_state)

    def test_no_video_stream_is_distinct_from_unreadable(self):
        """Both are failures, but §V.1 gives them different states."""
        novid = self.ing.ingest(_audio_only(str(self.tmp / "a2.mkv"))).container
        unread = self.ing.ingest(_garbage(str(self.tmp / "g4.mp4"))).container
        self.assertEqual(novid.probe_state, ProbeFailureState.NO_VIDEO_STREAM)
        self.assertEqual(unread.probe_state, ProbeFailureState.UNREADABLE)

    def test_probe_detail_is_non_contract_and_not_a_state(self):
        """The detail string must never be mistaken for the semantic state."""
        info = self.ing.ingest(_garbage(str(self.tmp / "g5.mp4"))).container
        self.assertIsInstance(info.probe_state, ProbeFailureState)
        self.assertNotEqual(info.probe_detail, str(info.probe_state))

    def test_pre_probe_conditions_still_raise(self):
        """No probe ran and no group exists, so there is nothing to record on.
        Those are §2.1.5 REJ_FILE_* conditions, not §V.1 probe failures."""
        with self.assertRaises(IngestionError):
            self.ing.ingest(str(self.tmp / "does-not-exist.mp4"))
        empty = self.tmp / "empty.mp4"
        empty.write_bytes(b"")
        with self.assertRaises(IngestionError):
            self.ing.ingest(str(empty))

    def test_no_new_rejection_vocabulary_was_introduced(self):
        """§V.1 R-3: the REJ_* set is CLOSED and 2.3 may not mint a member.
        ProbeFailureState records a CONDITION; it is not a rejection code."""
        import videotemplate.models.source_description as m
        self.assertEqual({s.value for s in ProbeFailureState},
                         {"unreadable", "no_video_stream", "resource_limit",
                          "rejected_by_policy"})
        self.assertFalse([n for n in dir(m) if n.startswith("REJ_")])


if __name__ == "__main__":
    unittest.main()


    def test_unreadable_returns_a_contract_not_an_exception(self):
        """Acceptance criterion 1: ingest() RETURNS. It used to raise."""
        desc = self.ing.ingest(_garbage(str(self.tmp / "garbage.mp4")))
        self.assertIsNotNone(desc)
        self.assertEqual(desc.container.probe_state,
                         ProbeFailureState.UNREADABLE)
        self.assertIsNotNone(desc.container.probe_detail)
