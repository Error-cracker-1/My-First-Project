import tempfile, unittest
from pathlib import Path
from conversation_store import ConversationStore, ConversationStoreError

class ConversationStoreTests(unittest.TestCase):
    def make_store(self):
        d=tempfile.TemporaryDirectory(); self.addCleanup(d.cleanup); return ConversationStore(Path(d.name))
    def test_save_load_order_and_model(self):
        s=self.make_store(); h=[("First","Answer 1"),("Second","Answer 2")]
        p=s.save("My Chat","gemini-3.5-flash-lite",h); x=s.load("My Chat")
        self.assertEqual(p.name,"My Chat.json"); self.assertEqual(x["model"],"gemini-3.5-flash-lite"); self.assertEqual(x["history"],h)
    def test_empty_history(self):
        s=self.make_store(); s.save("Empty","gemini-3.5-flash-lite",[]); self.assertEqual(s.load("Empty")["history"],[])
    def test_missing(self):
        with self.assertRaises(ConversationStoreError): self.make_store().load("missing")
    def test_corrupt(self):
        s=self.make_store(); (s.root/"Broken.json").write_text("{bad",encoding="utf-8")
        with self.assertRaises(ConversationStoreError): s.load("Broken")
    def test_invalid_history(self):
        with self.assertRaises(ConversationStoreError): self.make_store().save("Broken","gemini-3.5-flash-lite",[("only",)])
    def test_safe_name(self):
        s=self.make_store(); s.save("project/notes","gemini-3.5-flash-lite",[]); self.assertEqual(s.list_names(),["project_notes"])
if __name__=="__main__": unittest.main()
