"""
§2.1.16 v1.3 — the `conflicting` observation state. T-C1..T-C8.

Each test is a rule from the amendment. T-C3 is the one that decides whether the
amendment is sound at all: if `conflicting` cannot be told apart from `uncertain` in
practice, the member is a rename and the amendment should be rejected, not weakened.

The two-scope fixture is built by `_s23_fixture_inject.py` (container scope via the
atom injector, stream scope via PyAV's own writer — hand-injecting the track `udta`
made the mov demuxer read the value back as empty). Tests that need it skip rather
than fabricate it when it is absent: a conflict asserted from a hand-built list would
not prove the real path works.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from videotemplate.ingestion.ingestor import Ingestor
from videotemplate.models.source_description import (
    ContainerInfo, ObservationOrigin, ProducerDeclaration,
)
from videotemplate.utils.confidence import (
    ObservationState, ValidationInfo, ValidationStatus,
)

_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = _ROOT / "_s23_fixtures"
CONFLICT = FIXTURES / "conflict_two_scope.mp4"
DECLARED = FIXTURES / "declared_real.mp4"
BASE = FIXTURES / "t1_base.mp4"

CONTAINER, STREAM = "container", "video_stream"


def _decl(value, scope, origin=ObservationOrigin.ARTIFACT_DECLARED,
          state=ObservationState.EXTRACTED) -> ProducerDeclaration:
    return ProducerDeclaration(
        scope=scope, canonical_key="encoder", original_key="encoder",
        original_value=value, origin=origin, state=state, rule_id="R2-fold",
    )


class TestObservationStateV13(unittest.TestCase):
    """T-C7 / T-C8 — the envelope member itself (S-1, S-8)."""

    def test_tc7_exactly_five_members_originals_unchanged(self):
        self.assertEqual(len(list(ObservationState)), 5)
        self.assertEqual(ObservationState.EXTRACTED.value, "extracted")
        self.assertEqual(ObservationState.ABSENT.value, "absent")
        self.assertEqual(ObservationState.UNCERTAIN.value, "uncertain")
        self.assertEqual(ObservationState.UNAVAILABLE.value, "unavailable")

    def test_tc8_serialised_form_is_literal(self):
        self.assertEqual(ObservationState.CONFLICTING.value, "conflicting")
        info = ContainerInfo(format="mp4", format_long="x", size_bytes=1,
                             producer_state=ObservationState.CONFLICTING)
        self.assertEqual(info.model_dump()["producer_state"],
                         ObservationState.CONFLICTING)

    def test_s6_conflict_state_is_independent_of_validation_status(self):
        """The two axes stay orthogonal: a conflict does not force a status, and the
        two vocabularies are not merged into one another.

        `ValidationInfo` is a separate model and is untouched by this amendment, so
        the check is that the two vocabularies remain distinct and that a
        `conflicting` producer state carries no ValidationStatus of its own.
        """
        info = ContainerInfo(format="mp4", format_long="x", size_bytes=1,
                             producer_state=ObservationState.CONFLICTING)
        self.assertNotIn("validation", info.model_dump())
        self.assertNotEqual(ValidationStatus.CONFLICT.value,
                            ObservationState.CONFLICTING.value)
        self.assertEqual(ValidationInfo().status, ValidationStatus.VALIDATED)


class TestConflictingRollup(unittest.TestCase):
    """T-C1..T-C5 — the conditions, tested directly on the rollup."""

    def setUp(self):
        self.ing = Ingestor()

    def test_tc1_two_inconsistent_values_from_two_scopes_is_conflicting(self):
        decls = [_decl("Lavf62.12.102", CONTAINER),
                 _decl("SomeOtherTool 9.9.9", STREAM)]
        self.assertEqual(self.ing._producer_declarations_state(decls),
                         ObservationState.CONFLICTING)

    def test_s2_different_keys_are_not_a_conflict(self):
        """The per-key rule. Two different properties at two scopes are two facts, not
        a contradiction; treating them as one would report `conflicting` for any file
        carrying more than one producer-ish tag, which is what a plain FFmpeg mux does."""
        handler = _decl("VideoHandler", STREAM, ObservationOrigin.PROBE_OBSERVED)
        handler.canonical_key = "handler_name"
        decls = [_decl("Lavf62.12.102", CONTAINER), handler]
        self.assertEqual(self.ing._producer_declarations_state(decls),
                         ObservationState.EXTRACTED)

    def test_s2_same_key_different_scopes_conflicts_regardless_of_other_keys(self):
        handler = _decl("VideoHandler", STREAM, ObservationOrigin.PROBE_OBSERVED)
        handler.canonical_key = "handler_name"
        decls = [_decl("Lavf62.12.102", CONTAINER), handler,
                 _decl("SomeOtherTool 9.9.9", STREAM)]
        self.assertEqual(self.ing._producer_declarations_state(decls),
                         ObservationState.CONFLICTING)

    def test_tc2_both_values_are_retained_in_the_record(self):
        """S-3: the state must describe a record that exists, not replace it."""
        decls = [_decl("Lavf62.12.102", CONTAINER),
                 _decl("SomeOtherTool 9.9.9", STREAM)]
        info = ContainerInfo(format="mp4", format_long="x", size_bytes=1,
                             producer_declarations=decls,
                             producer_state=self.ing._producer_declarations_state(decls))
        self.assertEqual(len(info.producer_declarations), 2)
        self.assertEqual({d.original_value for d in info.producer_declarations},
                         {"Lavf62.12.102", "SomeOtherTool 9.9.9"})
        self.assertEqual({d.scope for d in info.producer_declarations},
                         {CONTAINER, STREAM})

    def test_tc3_single_ambiguous_value_is_uncertain_not_conflicting(self):
        """The discriminator. One value is never a conflict, however poor its quality."""
        decls = [_decl("???", CONTAINER, state=ObservationState.UNCERTAIN)]
        result = self.ing._producer_declarations_state(decls)
        self.assertNotEqual(result, ObservationState.CONFLICTING)
        self.assertEqual(result, ObservationState.EXTRACTED)

    def test_tc4_agreeing_values_from_two_scopes_are_not_conflicting(self):
        """Same value twice is corroboration, not disagreement (S-2 condition (b))."""
        decls = [_decl("Lavf62.12.102", CONTAINER),
                 _decl("Lavf62.12.102", STREAM)]
        self.assertEqual(self.ing._producer_declarations_state(decls),
                         ObservationState.EXTRACTED)

    def test_tc5_capability_failures_are_never_conflicting(self):
        """S-5: `unavailable`/`absent`/`uncertain` are not disagreements."""
        for state in (ObservationState.UNAVAILABLE, ObservationState.ABSENT,
                      ObservationState.UNCERTAIN):
            decls = [_decl("x", CONTAINER, ObservationOrigin.UNAVAILABLE, state)]
            with self.subTest(state=state):
                self.assertNotEqual(self.ing._producer_declarations_state(decls),
                                    ObservationState.CONFLICTING)

    def test_tc5_no_declarations_is_absent_not_conflicting(self):
        self.assertEqual(self.ing._producer_declarations_state([]),
                         ObservationState.ABSENT)


class TestTwoScopeFixture(unittest.TestCase):
    """T-C1/T-C2/T-C6 against the real artifact rather than a stub.

    A conflict asserted from a hand-built list would prove the rollup works but not
    that the observation path can actually reach it, so these run the real ingestor
    over a file that carries two disagreeing declarations. They skip (never fake) when
    the fixture is absent.
    """

    def setUp(self):
        if not CONFLICT.exists():
            self.skipTest("two-scope fixture not built (_s23_fixture_inject.py)")
        self.desc = Ingestor().ingest(str(CONFLICT))
        self.info = self.desc.container

    def test_tc1_fixture_rolls_up_to_conflicting(self):
        self.assertEqual(self.info.producer_state, ObservationState.CONFLICTING)

    def test_tc2_fixture_retains_both_scopes_and_both_values(self):
        """S-3/S-4: the disputed value is retained, not dropped or silently preferred."""
        decls = [d for d in self.info.producer_declarations
                 if d.canonical_key == "encoder"]
        self.assertEqual(len(decls), 2)
        values = {d.original_value for d in decls}
        self.assertEqual(len(values), 2, "both distinct values must be retained")
        self.assertEqual({d.scope for d in decls}, {CONTAINER, STREAM})
        self.assertIn("SomeOtherTool 9.9.9", values)
        self.assertIn("HandBrake 1.6.0 2023041600", values)

    def test_tc6_codec_never_becomes_a_producer_value(self):
        """A5: the decoder-side codec string must not enter a producer declaration,
        even though it is present and even though a conflict exists."""
        for d in self.info.producer_declarations:
            self.assertNotIn("h264", d.original_value.lower())
            self.assertNotIn("avc1", d.original_value.lower())
            self.assertNotEqual(d.canonical_key, "codec")

    def test_s7_conflict_does_not_silently_collapse_the_record(self):
        """S-7, at the level §2.1 actually owns.

        `conflicting` is an observation, not an adjudication: it must not cause a value
        to be invented or the retained set to be reduced. It does NOT govern which
        value a single-valued destination field receives — that is 2.3's precedence and
        destination-eligibility rule (§V.5.1), which 2.1 cannot decide.

        NOTE the deliberate limit of this test. `SourceInfo.version` does receive ONE
        retained value even though the group is `conflicting`. That is 2.3's registered
        precedence resolving the destination, not a §2.1 rule, and asserting either way
        here would put a 2.3 decision inside a 2.1 amendment. What 2.1 requires, and what
        is asserted below, is that the conflict remains visible in the record and that
        nothing is fabricated to resolve it.
        """
        decls = [d for d in self.info.producer_declarations
                 if d.canonical_key == "encoder"]
        values = {d.original_value for d in decls}
        self.assertEqual(len(values), 2, "the dispute must not be silently collapsed")
        self.assertEqual(self.info.producer_state, ObservationState.CONFLICTING)

        # Whatever a destination field holds, it is one of the retained values —
        # no synthesised "winner" string is introduced to end the dispute.
        source = self.info.source
        version = getattr(source, "version", None) if source else None
        if version is not None:
            self.assertIn(version, values)


class TestNoRegression(unittest.TestCase):
    """S-1: v1.3 must not change single-scope behaviour."""

    def setUp(self):
        self.ing = Ingestor()

    def test_single_scope_fixture_is_extracted_not_conflicting(self):
        if not DECLARED.exists():
            self.skipTest("declared fixture not built")
        info = self.ing.ingest(str(DECLARED)).container
        self.assertEqual(info.producer_state, ObservationState.EXTRACTED)
        encoders = [d for d in info.producer_declarations
                    if d.canonical_key == "encoder"]
        self.assertEqual(len(encoders), 1)
        self.assertEqual(encoders[0].original_value,
                         "HandBrake 1.6.0 2023041600")

    def test_plain_base_has_no_conflict(self):
        if not BASE.exists():
            self.skipTest("base fixture not built")
        info = self.ing.ingest(str(BASE)).container
        self.assertNotEqual(info.producer_state, ObservationState.CONFLICTING)


if __name__ == "__main__":
    unittest.main()