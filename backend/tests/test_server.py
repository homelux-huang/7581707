import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

p=Path(__file__).resolve().parents[1]/"server.py"
spec=importlib.util.spec_from_file_location("sudu_private_server",p)
server=importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

class TestPrivateAdmin(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        server.DB=Path(self.tmp.name)/"test.sqlite3"
        server.DEV=True
        server.BOOTSTRAP=""
        server.initialize()
    def tearDown(self):
        self.tmp.cleanup()
    def test_admin_default_requires_password_change(self):
        with server.connect() as db:
            account=db.execute("SELECT * FROM admins WHERE username='admin'").fetchone()
        self.assertTrue(server.verify("admin",account["password"]))
        self.assertEqual(account["must_change"],1)
        self.assertFalse(server.verify("wrong",account["password"]))
        self.assertNotIn("admin",account["password"])
    def test_clean_state_and_unknown_fields_not_synced(self):
        given={"attempts":{"q1":[{"choice":1,"correct":True,"at":"2026-10-18"}]},
               "examSubmissions":{"114/09-2":{"year":114,"paper":"09-2","submittedAt":"2026","elapsedMs":5000}},
               "password":"leak"}
        result=server.clean_state(given)
        self.assertNotIn("password",result)
        self.assertEqual(result["attempts"]["q1"][0]["choice"],1)
        self.assertEqual(result["examSubmissions"]["114/09-2"]["elapsedMs"],5000)
    def test_official_score_requires_verified_rules(self):
        self.assertIsNone(server.official_score("114/09-2",{"choices":{}}))
    def test_tokens_not_stored_in_plaintext(self):
        self.assertNotEqual(server.digest("temporary-token"),"temporary-token")
        self.assertNotEqual(server.digest("token-a"),server.digest("token-b"))
    def test_short_production_password_rejected(self):
        server.DEV=False;server.BOOTSTRAP="admin"
        with self.assertRaises(RuntimeError):server.initialize()

if __name__=="__main__":
    unittest.main()
