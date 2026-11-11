"""Synthetic-only contract tests: NEVER evidence of a real G6 model solve."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import master_e12_openai_first_solver_20261111 as h


class FakeHttp:
    def __init__(self, body, ctype="application/json", status=200):
        self._body = body
        self.status = status
        self.headers = {
            "content-type": ctype,
            "date": "Wed, 11 Nov 2026 00:00:00 GMT",
            "x-request-id": "req_SYNTHETIC_TEST_ONLY_NOT_PROVIDER",
            "openai-processing-ms": "5",
        }

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


class ContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.oldout = h.OUT
        h.OUT = Path(self.temp.name)

    def tearDown(self):
        h.OUT = self.oldout
        self.temp.cleanup()

    def read(self, filename):
        return json.loads((h.OUT / filename).read_bytes())

    def test_answer_free_g2_is_exact_immutable_source_and_has_no_key(self):
        original = h.verified_g2()
        self.assertEqual(h.blob(original), h.G2_BLOB)
        self.assertEqual(h.sha(original), h.G2_SHA256)
        doc = json.loads(h.request_bytes(original))
        self.assertEqual(doc["input"], original.decode())
        self.assertEqual(doc["store"], True)
        self.assertEqual(doc["stream"], False)
        self.assertNotIn("previous_response_id", doc)
        self.assertNotIn("tools", doc)
        self.assertNotIn("officialAnswer", doc)
        self.assertNotIn("finalAnswer", doc)
        self.assertNotIn("official", doc["input"].lower())

    def test_preflight_never_sends_model_request(self):
        with patch.object(h.urllib.request, "urlopen", side_effect=AssertionError("network forbidden")):
            h.preflight()
        self.assertEqual(list(h.OUT.iterdir()), [])

    def test_missing_secret_never_calls_provider_and_cannot_forge_g6(self):
        with patch.dict(os.environ, {"E12_G6_OPENAI_API_KEY": ""}):
            with patch.object(h.urllib.request, "urlopen", side_effect=AssertionError("network forbidden")):
                with self.assertRaisesRegex(RuntimeError, "MISSING_PROVIDER_SECRET"):
                    h.first()
        receipt = self.read("provider_error.json")
        self.assertEqual(receipt["g6"], "UNVERIFIED")
        self.assertEqual(receipt["g7"], "UNVERIFIED")
        self.assertFalse((h.OUT / "provider_first_response.body").exists())

    def test_one_synthetic_model_post_preserves_bytes_but_never_approves(self):
        fake = {
            "id": "resp_SYNTHETIC_TEST_ONLY_NOT_PROVIDER",
            "model": h.MODEL,
            "created_at": 1794355200,
            "output": [{
                "type": "message", "role": "assistant",
                "content": [{"type": "output_text",
                             "text": "First answer: C\nA: wrong for example.\n"
                                     "B: wrong for example.\nC: correct for example.\n"
                                     "D: wrong for example.\nConfidence: high."}]
            }],
        }
        original_bytes = json.dumps(fake, ensure_ascii=False).encode("utf-8")
        calls = []
        def mock_urlopen(request, timeout=0):
            calls.append((request.full_url, request.data, timeout))
            return FakeHttp(original_bytes)
        with patch.dict(os.environ, {"E12_G6_OPENAI_API_KEY": "KEY_SYNTHETIC_TEST_DO_NOT_USE", "GITHUB_RUN_ID": "SYNTHETIC"}, clear=False):
            with patch.object(h.urllib.request, "urlopen", side_effect=mock_urlopen):
                h.first()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], h.API)
        self.assertEqual(calls[0][1], (h.OUT / "provider_first_request.body").read_bytes())
        self.assertEqual(original_bytes, (h.OUT / "provider_first_response.body").read_bytes())
        evidence = self.read("first_exchange_frozen.json")
        self.assertTrue(evidence["firstAnswerAllFourOptionLabelsPresent"])
        self.assertEqual(evidence["originalFirstHttpResponse"]["sha256"], h.sha(original_bytes))
        self.assertFalse(evidence["qualifiedG6"])
        self.assertFalse(evidence["qualifiedG7"])
        self.assertFalse(evidence["blindPass"])
        self.assertFalse(evidence["ready"])
        self.assertFalse(evidence["live"])
        self.assertFalse(evidence["providerServerRecordIndependentlyRetrieved"])
        self.assertFalse((h.OUT / "official_g3_retrieved_only_after_first.body").exists())
        for p in h.OUT.iterdir():
            self.assertNotIn(b"KEY_SYNTHETIC_TEST_DO_NOT_USE", p.read_bytes())

    def test_retired_service_plain_ok_body_is_rejected_not_g6_pass(self):
        with patch.dict(os.environ, {"E12_G6_OPENAI_API_KEY": "KEY_SYNTHETIC_TEST_DO_NOT_USE"}, clear=False):
            with patch.object(h.urllib.request, "urlopen", return_value=FakeHttp(b"OK\r\n", ctype="text/plain")):
                with self.assertRaisesRegex(RuntimeError, "INVALID_FIRST_MODEL_REPLY"):
                    h.first()
        self.assertEqual((h.OUT / "provider_first_response.body").read_bytes(), b"OK\r\n")
        evidence = self.read("first_exchange_frozen.json")
        self.assertFalse(evidence["jsonValid"])
        self.assertFalse(evidence["firstAnswerAllFourOptionLabelsPresent"])
        self.assertFalse(evidence["qualifiedG6"])
        self.assertFalse(evidence["trustedV1Receipt"])

    def test_no_response_prevents_official_key_fetch(self):
        with patch.object(h.urllib.request, "urlopen", side_effect=AssertionError("must not fetch G3")):
            with self.assertRaisesRegex(RuntimeError, "NO_FROZEN_FIRST_REPLY"):
                h.reveal_after()


if __name__ == "__main__":
    unittest.main()
