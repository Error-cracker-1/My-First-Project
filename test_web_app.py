import unittest
from unittest.mock import patch
from web_app import app

class WebAppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"]=True
        self.client=app.test_client()
    @patch("web_app.get_session")
    def test_index_loads(self,get_session):
        get_session.return_value=("test",{"model":"gemini-3.5-flash-lite","history":[],"chat":object()})
        r=self.client.get("/")
        self.assertEqual(r.status_code,200)
        self.assertIn(b"AI Coding Chatbot",r.data)
    @patch("web_app.get_session")
    def test_empty_message_rejected(self,get_session):
        get_session.return_value=("test",{"model":"gemini-3.5-flash-lite","history":[],"chat":object()})
        r=self.client.post("/api/chat",json={"message":" "})
        self.assertEqual(r.status_code,400)
        self.assertFalse(r.get_json()["ok"])
    def test_models(self):
        r=self.client.get("/api/models")
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.get_json()["models"])
if __name__=="__main__": unittest.main()
