import unittest
from unittest.mock import patch

from web_app import app


class WebAppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("web_app.get_session")
    def test_index_loads_with_v21_ui_controls(self, get_session):
        get_session.return_value = (
            "test",
            {"model": "gemini-3.5-flash-lite", "history": [], "chat": object()},
        )
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Coding Chatbot", response.data)
        self.assertIn(b"New chat", response.data)
        self.assertIn(b"prompt-suggestions", response.data)
        self.assertIn(b"Saved conversations", response.data)

    @patch("web_app.get_session")
    def test_empty_message_rejected(self, get_session):
        get_session.return_value = (
            "test",
            {"model": "gemini-3.5-flash-lite", "history": [], "chat": object()},
        )
        response = self.client.post("/api/chat", json={"message": " "})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["ok"])

    def test_models(self):
        response = self.client.get("/api/models")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["models"])

    def test_ui_assets_are_served(self):
        css = self.client.get("/static/style.css")
        js = self.client.get("/static/app.js")
        self.assertEqual(css.status_code, 200)
        self.assertIn(b".message.user", css.data)
        self.assertEqual(js.status_code, 200)
        self.assertIn(b"formatMessage", js.data)
        self.assertIn(b"confirm(", js.data)


if __name__ == "__main__":
    unittest.main()
