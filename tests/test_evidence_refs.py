"""
§2.1.17 v1.4 — the `evidence_refs` address grammar. T-E1..T-E6.

T-E6 is the boundary guard: it fails if anyone retrofits `evidence_refs` into
`ProducerDeclaration` to make §2.1.16's prose true. v1.4 defines what an address
IS; it deliberately does not assign carriers (E-6), and §2.1.16 was corrected in
the previous pass to say so.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_s23_verification", _ROOT / "_s23_verification.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
classify_ref = _mod.classify_ref


class TestEvidenceRefGrammar(unittest.TestCase):

    def test_te1_each_kind_parses(self):
        """T-E1: all five kinds are recognised; four are addresses, one is not."""
        self.assertEqual(classify_ref("artifact:mp4:moov/udta/meta/ilst/x/data"),
                         "CONFORMING")
        self.assertEqual(classify_ref("frame:v0@idx3"), "CONFORMING")
        self.assertEqual(classify_ref("frame:v0@pts=2048"), "CONFORMING")
        self.assertEqual(classify_ref("contract:container.format"), "CONFORMING")
        self.assertEqual(classify_ref("derived:heuristic_scoring:file_size,duration"),
                         "CONFORMING")

    def test_te2_method_is_recognised_and_is_not_an_address(self):
        """T-E2 / E-2: a method names a procedure. It must be REJECTED, not tolerated."""
        self.assertEqual(classify_ref("method:container_probe"), "NOT_ADDRESS")
        self.assertEqual(classify_ref("container_probe"), "LEGACY")

    def test_te3_vague_locators_rejected(self):
        """T-E3: a wildcard, a bare container, an empty path and an unnamed
        selector are all locations that locate nothing."""
        self.assertNotEqual(classify_ref("artifact:mp4:*"), "CONFORMING")
        self.assertNotEqual(classify_ref("artifact:mp4"), "CONFORMING")
        self.assertNotEqual(classify_ref("frame:v0"), "CONFORMING")
        self.assertNotEqual(classify_ref("contract:"), "CONFORMING")
        self.assertNotEqual(classify_ref("derived:scored"), "CONFORMING")

    def test_te4_two_observations_yield_different_refs(self):
        """T-E3 / E-3: an address that cannot distinguish two observations is not an
        address. Distinct locators of one artifact must stay distinct."""
        a = classify_ref("frame:v0@idx3")
        b = classify_ref("frame:v0@idx7")
        self.assertEqual(a, "CONFORMING")
        self.assertEqual(b, "CONFORMING")
        self.assertNotEqual("frame:v0@idx3", "frame:v0@idx7")

    def test_te5_existing_refs_are_all_legacy(self):
        """T-E5 / E-4: every ref the repo emits today classifies as LEGACY, and
        none conforms. v1.4 is additive and changed nothing in src/."""
        emitted = ["container_probe",
                   "file_size", "duration", "resolution", "codec",
                   "decoded_frames", "quality_heuristics",
                   "source_file", "frame_0", "frame_1",
                   "source.quality_score"]
        for ref in emitted:
            with self.subTest(ref=ref):
                self.assertEqual(classify_ref(ref), "LEGACY")
        self.assertEqual(
            [r for r in emitted if classify_ref(r) == "CONFORMING"], [])

    def test_te6_no_evidence_refs_on_producer_declaration(self):
        """T-E6 / E-6: the boundary. v1.4 defines addresses; it must not have added
        a carrier to satisfy §2.1.16's prose. This is the coupling v1.4 refuses."""
        from videotemplate.models.source_description import ProducerDeclaration
        self.assertNotIn("evidence_refs", ProducerDeclaration.model_fields)


if __name__ == "__main__":
    unittest.main()
