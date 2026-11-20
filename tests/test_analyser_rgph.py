import unittest

from app.analysis import analyze_article, load_passages
from app.verdict import Status


class ArticleTests(unittest.TestCase):
    def setUp(self):
        self.passages = load_passages()

    def test_article_returns_exact_claims_and_sourced_statuses(self):
        claims = [
            "Au 1er septembre 2024, le Maroc comptait 36 828 330 habitants.",
            "En 2024, le Maroc comptait 10 000 000 ménages.",
            "Au 1er septembre 2023, le Maroc comptait 36 828 330 habitants.",
        ]
        results = analyze_article(
            " ".join(claims) + " À mon avis, ces chiffres sont étonnants.",
            self.passages,
            lambda _: [("P15", 0.95), ("P01", 0.93), ("P03", 0.91)],
        )
        self.assertEqual([item["affirmation"] for item in results], claims)
        self.assertEqual(
            [item["statut"] for item in results],
            [Status.SUPPORTED, Status.CONTRADICTED, Status.INSUFFICIENT],
        )
        self.assertEqual([item["preuves"][0]["id"] for item in results[:2]], ["P01", "P15"])
        self.assertTrue(results[0]["preuves"][0]["url"].startswith("https://www.hcp.ma/"))
        self.assertIn("36 828 330 habitants", results[0]["preuves"][0]["extrait"])
        self.assertEqual(results[2]["preuves"], [])

    def test_one_person_difference_is_contradiction(self):
        results = analyze_article(
            "Au 1er septembre 2024, le Maroc comptait 36 828 331 habitants.",
            self.passages,
            lambda _: [("P01", 0.99)],
        )
        self.assertEqual(results[0]["statut"], Status.CONTRADICTED)

    def test_unsupported_wording_and_wrong_indicator_are_inconclusive(self):
        results = analyze_article(
            "En 2024, le Maroc comptait 62,8 % de citadins. "
            "Le taux d’urbanisation du Maroc était de 62,8 % en 2024.",
            self.passages,
            lambda _: [("P09", 0.99)],
        )
        self.assertEqual([item["statut"] for item in results], [Status.INSUFFICIENT] * 2)

    def test_explicit_urbanization_rate_is_checked_with_source(self):
        result = analyze_article(
            "Le taux d’urbanisation du Maroc était de 62,80 % en 2024.",
            self.passages,
            lambda _: [("P12", 0.99)],
        )[0]
        self.assertEqual(result["statut"], Status.SUPPORTED)
        self.assertEqual(result["preuves"][0]["id"], "P12")
