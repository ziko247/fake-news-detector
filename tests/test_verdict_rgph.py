import unittest

from experiments.verdict_rgph import EvidenceAssessment, Relation, Status, decide_status


class VerdictTests(unittest.TestCase):
    def test_pending_or_interrupted_verification(self):
        support = EvidenceAssessment(Relation.SUPPORTS, same_scope=True, sufficient=True)
        self.assertEqual(decide_status(False, [support]).status, Status.UNVERIFIED)

    def test_completed_search_without_evidence(self):
        self.assertEqual(decide_status(True, []).status, Status.INSUFFICIENT)

    def test_completed_search_with_neutral_passage(self):
        neutral = EvidenceAssessment(Relation.NEUTRAL, same_scope=True, sufficient=False)
        self.assertEqual(decide_status(True, [neutral]).status, Status.INSUFFICIENT)

    def test_partial_support_cannot_confirm_whole_claim(self):
        partial = EvidenceAssessment(Relation.SUPPORTS, same_scope=True, sufficient=False)
        self.assertEqual(decide_status(True, [partial]).status, Status.INSUFFICIENT)

    def test_passage_from_another_year_is_excluded(self):
        other_year = EvidenceAssessment(Relation.CONTRADICTS, same_scope=False, sufficient=True)
        self.assertEqual(decide_status(True, [other_year]).status, Status.INSUFFICIENT)

    def test_verified_support(self):
        support = EvidenceAssessment(Relation.SUPPORTS, same_scope=True, sufficient=True)
        self.assertEqual(decide_status(True, [support]).status, Status.SUPPORTED)

    def test_verified_numeric_contradiction(self):
        unconfirmed_support = EvidenceAssessment(Relation.SUPPORTS, same_scope=True, sufficient=False)
        contradiction = EvidenceAssessment(Relation.CONTRADICTS, same_scope=True, sufficient=True)
        decision = decide_status(True, [unconfirmed_support, contradiction])
        self.assertEqual(decision.status, Status.CONTRADICTED)

    def test_conflicting_sources_trigger_abstention(self):
        support = EvidenceAssessment(Relation.SUPPORTS, same_scope=True, sufficient=True)
        contradiction = EvidenceAssessment(Relation.CONTRADICTS, same_scope=True, sufficient=True)
        for evidence in ([support, contradiction], [contradiction, support]):
            with self.subTest(evidence=evidence):
                decision = decide_status(True, evidence)
                self.assertEqual(decision.status, Status.INSUFFICIENT)
                self.assertIn("divergent", decision.reason)
