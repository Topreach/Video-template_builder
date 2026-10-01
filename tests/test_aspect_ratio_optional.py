"""
stage2_source_description.md Amendment Record v1.1 (G10 / Stage 2.3 A9) —
`sample_aspect_ratio` may express absence.

The point of the amendment is that ABSENCE IS NOW REPRESENTABLE. A test that only
checked "the field is Optional" would pass while the producer still fabricated `"1:1"`,
which is the actual defect. So these assert the emitted CONTRACT on a real file.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

import io  # noqa: E402
import re  # noqa: E402
from fractions import Fraction  # noqa: E402

import av  # noqa: E402
import numpy as np  # noqa: E402

from videotemplate.ingestion.ingestor import Ingestor  # noqa: E402
from videotemplate.models.source_description import VideoStreamInfo  # noqa: E402

SENTINELS = {"1:1", "unknown", "N/A", "none", "0:1"}


def _clip(path, sar=None):
    c = av.open(path, "w")
    st = c.add_stream("libx264", rate=10)
    st.width, st.height, st.pix_fmt = 160, 120, "yuv420p"
    if sar is not None:
        # PyAV requires a Fraction here, not a "W:H" string (AttributeError otherwise).
        st.sample_aspect_ratio = sar
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


class TestSampleAspectRatioOptional(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()

    def test_type_is_optional(self):
        """The contract change itself (S-1)."""
        ann = VideoStreamInfo.model_fields["sample_aspect_ratio"].annotation
        self.assertIn("None", str(ann) + "Optional")

    def test_absent_source_yields_null_not_a_sentinel(self):
        """The defect itself: an ordinary square-pixel clip declares no SAR, and the
        ingestor must say so rather than assert '1:1'."""
        p = _clip(str(Path(self.tmp) / "plain.mp4"))
        sar = Ingestor(max_duration=30.0).ingest(p).video_stream.sample_aspect_ratio
        self.assertIsNone(sar, f"absence must be null; got {sar!r}")
        self.assertNotIn(sar, SENTINELS)

    def test_declared_value_is_still_carried_verbatim(self):
        """S-1 must not degrade the present case: a declared 4:3 must survive."""
        p = _clip(str(Path(self.tmp) / "anamorphic.mp4"), sar=Fraction(4, 3))
        sar = Ingestor(max_duration=30.0).ingest(p).video_stream.sample_aspect_ratio
        self.assertIsNotNone(sar)
        num, den = (int(x) for x in sar.split(":"))
        self.assertAlmostEqual(num / den, 4 / 3, places=2)

    def test_key_stays_required_so_absence_is_not_non_applicability(self):
        """S-2: the key must be emitted, because null means 'checked, declares none',
        which is different from omitting the key ('not applicable')."""
        p = _clip(str(Path(self.tmp) / "plain2.mp4"))
        dumped = Ingestor(max_duration=30.0).ingest(p).video_stream.model_dump()
        self.assertIn("sample_aspect_ratio", dumped)
        self.assertIsNone(dumped["sample_aspect_ratio"])

    def test_no_group_field_carries_any_sentinel(self):
        """S-1 (v1.1) and S-1 (v1.2) across the whole emitted group.

        This test previously ASSERTED that `display_aspect_ratio='0:1'` was still
        present, so the A9-DAR residual could not be forgotten. v1.2 has now removed
        it, so the assertion inverts: no ratio field may carry a fabrication sentinel.
        """
        p = _clip(str(Path(self.tmp) / "plain3.mp4"))
        desc = Ingestor(max_duration=30.0).ingest(p)
        found = []
        for grp in (desc.container, desc.video_stream):
            for k, v in grp.model_dump().items():
                if isinstance(v, str) and v in SENTINELS:
                    found.append(f"{k}={v!r}")
        self.assertEqual(found, [], f"fabrication sentinels still emitted: {found}")

    def test_both_ratio_fields_express_absence(self):
        """v1.2 S-5: both ratio fields follow one rule, and any field formatted through
        _format_display_ratio inherits null rather than a string fallback."""
        p = _clip(str(Path(self.tmp) / "plain4.mp4"))
        vs = Ingestor(max_duration=30.0).ingest(p).video_stream
        self.assertIsNone(vs.sample_aspect_ratio)
        self.assertIsNone(vs.display_aspect_ratio)

    def test_ingestor_no_longer_fabricates_any_ratio_fallback(self):
        """The completeness guard: no string `fallback=` may remain in the SOURCE CODE.

        This is the test-level twin of the A9 check's own blind-spot audit, and it
        deliberately imports the check's own tokenised rule rather than re-implementing
        it. A regex over raw text was tried first and FAILED, because the comments
        documenting this change contain `fallback="0:1"` in prose describing the old
        behaviour. Tokenising finds only real NAME/OP/STRING sequences.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_s23_verification", _ROOT / "_s23_verification.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(sorted(mod._fabrication_fallbacks()), [],
                         "a string fallback re-fabricates absence (v1.1/v1.2 S-1)")


if __name__ == "__main__":
    unittest.main()
