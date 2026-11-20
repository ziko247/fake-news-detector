import os
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.analysis import analyze_article, load_passages
from app.main import app
from app.storage import connection, initialize


class AnalysisApiTests(unittest.TestCase):
    def setUp(self):
        self.db_path = Path(self.enterContext(tempfile.TemporaryDirectory())) / "test.sqlite3"
        self.enterContext(patch.dict(os.environ, RGPH_DB_PATH=str(self.db_path)))
        passages = load_passages()
        self.analyzer = Mock(
            side_effect=lambda text: analyze_article(text, passages, lambda _: [("P01", 0.99)])
        )
        builder = self.enterContext(patch("app.main.build_article_analyzer", return_value=self.analyzer))
        self.client = self.enterContext(TestClient(app))
        builder.assert_called_once_with()

    def test_returns_typed_sourced_analysis(self):
        text = "Au 1er septembre 2024, le Maroc comptait 36 828 330 habitants."
        response = self.client.post("/analyses", json={"texte": text})
        self.assertEqual(response.status_code, 200)
        result = response.json()["affirmations"][0]
        self.assertEqual(result["affirmation"], text)
        self.assertEqual(result["statut"], "Appuyée par les sources")
        self.assertEqual(result["preuves"][0]["id"], "P01")
        self.assertTrue(result["preuves"][0]["url"].startswith("https://www.hcp.ma/"))

    def test_history_and_feedback_survive_reopening_database(self):
        article = "Au 1er septembre 2024, le Maroc comptait 36 828 330 habitants."
        response = self.client.post("/analyses", json={"texte": article})
        self.assertEqual(response.status_code, 200)
        with connection(self.db_path) as db:
            db.execute("""INSERT INTO feedback(claim_id, user_id, comment)
                          SELECT claims.id, analyses.user_id, 'Source relue'
                          FROM claims JOIN analyses ON analyses.id = claims.analysis_id""")
        initialize(self.db_path)
        with connection(self.db_path) as db:
            name, text, snapshot, comment = db.execute("""
                SELECT users.name, article, snapshot, comment FROM users
                JOIN analyses ON analyses.user_id = users.id
                JOIN claims ON claims.analysis_id = analyses.id
                JOIN feedback ON feedback.claim_id = claims.id AND feedback.user_id = users.id
            """).fetchone()
        self.assertEqual((name, text, comment), ("local", article, "Source relue"))
        self.assertEqual(json.loads(snapshot), response.json()["affirmations"][0])

    def test_failed_claim_insert_rolls_back_article_and_returns_documented_error(self):
        with connection(self.db_path) as db:
            db.execute("""CREATE TRIGGER fail_save BEFORE INSERT ON claims
                          BEGIN SELECT RAISE(ABORT, 'simulation'); END""")
        with self.assertLogs("app.main", level="ERROR"):
            response = self.client.post("/analyses", json={"texte": "Le Maroc compte 36 habitants."})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "L’analyse a échoué."})
        with connection(self.db_path) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM analyses").fetchone(), (0,))

    def test_empty_missing_oversized_and_non_string_inputs_are_rejected(self):
        for payload in ({}, {"texte": ""}, {"texte": " \n\t "}, {"texte": "a" * 12_001}, {"texte": 42}):
            with self.subTest(payload_type=type(payload.get("texte"))):
                response = self.client.post("/analyses", json=payload)
                self.assertEqual(response.status_code, 422)
        self.analyzer.assert_not_called()

    def test_valid_input_without_extracted_claims_returns_empty_list(self):
        response = self.client.post("/analyses", json={"texte": "À mon avis, le texte est intéressant."})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"affirmations": []})

    def test_processing_error_returns_generic_message(self):
        self.analyzer.side_effect = RuntimeError("détails internes")
        with self.assertLogs("app.main", level="ERROR"):
            response = self.client.post("/analyses", json={"texte": "Le Maroc compte 36 habitants."})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "L’analyse a échoué."})

    def test_openapi_documents_request_response_and_errors(self):
        schema = self.client.get("/openapi.json").json()
        endpoint = schema["paths"]["/analyses"]["post"]
        self.assertIn("requestBody", endpoint)
        self.assertEqual(set(endpoint["responses"]), {"200", "422", "500"})
        text_schema = schema["components"]["schemas"]["AnalysisRequest"]["properties"]["texte"]
        self.assertEqual(text_schema["maxLength"], 12_000)
