import unittest

from app.analysis import analyze_article, load_passages
from app.verdict import Status


class EconomyAnalysisTests(unittest.TestCase):
    def test_annual_claims_match_indicator_population_and_year(self):
        passages = load_passages("corpus-economie.md")
        text = (
            "Le taux de chômage au Maroc était de 13,3 % en 2024. "
            "En 2024, le taux de chômage en milieu rural au Maroc était de 16,9 %. "
            "L'inflation annuelle au Maroc était de 0.8% en 2025. "
            "En 2023, l’inflation annuelle au Maroc était de 0,8 %. "
            "Au premier trimestre, le taux de chômage au Maroc était de 13,3 % en 2024."
        )
        ranking = [(pid, 0.0) for pid in passages]
        results = analyze_article(text, passages, lambda _: ranking)
        self.assertEqual([item["statut"] for item in results], [
            Status.SUPPORTED, Status.CONTRADICTED, Status.SUPPORTED,
            Status.INSUFFICIENT, Status.INSUFFICIENT,
        ])
        self.assertEqual([[p["id"] for p in item["preuves"]] for item in results], [
            ["P18"], ["P21"], ["P23"], [], [],
        ])
