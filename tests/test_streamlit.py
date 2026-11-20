import io
import unittest
from http.client import IncompleteRead
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from streamlit.testing.v1 import AppTest


class FormTests(unittest.TestCase):
    def test_demo_loads_actual_article_without_submitting(self):
        root = Path(__file__).resolve().parents[1]
        page = AppTest.from_file(str(root / "frontend/streamlit_app.py")).run()
        with patch("urllib.request.urlopen") as send:
            page.button[0].click().run()
        send.assert_not_called()
        self.assertFalse(page.exception)
        self.assertEqual(page.text_area[0].value, (root / "data/demo-rgph.txt").read_text(encoding="utf-8"))

    def test_submit_then_service_failure_clears_previous_result(self):
        page = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "frontend/streamlit_app.py")).run()
        page.button[1].click().run()
        self.assertTrue(page.warning)
        page.text_area[0].set_value("Un exemple.")
        with patch("urllib.request.urlopen", return_value=io.BytesIO(b'{"affirmations":[]}')) as send:
            page.button[1].click().run()
        self.assertEqual(send.call_args.args[0].data, b'{"texte":"Un exemple."}')
        self.assertTrue(page.info)
        with patch("urllib.request.urlopen", side_effect=URLError("offline")):
            page.button[1].click().run()
        self.assertTrue(page.error)
        self.assertFalse(page.info)
        self.assertFalse(page.exception)
        with patch("urllib.request.urlopen") as send:
            send.return_value.__enter__.return_value.read.side_effect = IncompleteRead(b"")
            page.button[1].click().run()
        self.assertTrue(page.error)
        self.assertFalse(page.exception)
