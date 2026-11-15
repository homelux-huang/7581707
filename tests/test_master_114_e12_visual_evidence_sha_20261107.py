"""E12 only: real archived visual QA SHA and no changes to other 204 images."""
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"scripts/master_114_e12_visual_evidence_sha_20261107.py"
spec=importlib.util.spec_from_file_location("e12_sha_manifest",SOURCE)
e12=importlib.util.module_from_spec(spec)
spec.loader.exec_module(e12)

class E12VisualSha(unittest.TestCase):
    def test_actual_qa_document_bytes_and_manifest_are_bound(self):
        expected=e12.sha((ROOT/e12.EVIDENCE_REL).read_bytes())
        manifest=json.loads((ROOT/e12.MANIFEST_REL).read_text(encoding="utf-8"))
        item=next(x for x in manifest["items"] if x["questionId"]==e12.QID)
        self.assertEqual(item["visualReviewEvidence"]["referenceSha256"],expected)
        self.assertEqual(e12.main(False),expected)
        self.assertTrue(len(expected)==64)

    def test_exactly_one_manifest_question_changed(self):
        raw=subprocess.check_output([
            "git","show",e12.BASE_SHA+":"+e12.MANIFEST_REL],cwd=ROOT)
        before=json.loads(raw)["items"]
        after=json.loads((ROOT/e12.MANIFEST_REL).read_text())["items"]
        self.assertEqual(len(before),len(after))
        self.assertEqual(len(after),205)
        self.assertEqual([x for x in before if x["questionId"]!=e12.QID],
                         [x for x in after if x["questionId"]!=e12.QID])
        a=next(x for x in before if x["questionId"]==e12.QID)
        b=next(x for x in after if x["questionId"]==e12.QID)
        ev=b["visualReviewEvidence"].copy()
        self.assertEqual(ev.pop("referenceSha256"),e12.sha((ROOT/e12.EVIDENCE_REL).read_bytes()))
        self.assertEqual(a["visualReviewEvidence"],ev)
        self.assertEqual({k:v for k,v in a.items() if k!="visualReviewEvidence"},
                         {k:v for k,v in b.items() if k!="visualReviewEvidence"})

    def test_tampered_source_qa_and_webp_are_rejected(self):
        source=e12.ROOT
        for target,variant in [(e12.EVIDENCE_REL,"qa"),(e12.WEBP_REL,"image")]:
            with self.subTest(variant=variant),tempfile.TemporaryDirectory() as td:
                root=Path(td)
                for rel in [e12.EVIDENCE_REL,e12.WEBP_REL,e12.MANIFEST_REL]:
                    file=root/rel
                    file.parent.mkdir(parents=True,exist_ok=True)
                    file.write_bytes((source/rel).read_bytes())
                altered=root/target
                altered.write_bytes(altered.read_bytes()+b"\ninvalid-tamper")
                e12.ROOT=root
                try:
                    with self.assertRaisesRegex(RuntimeError,"E12_VISUAL_HOLD"):
                        e12.main(False)
                finally:
                    e12.ROOT=source

if __name__=="__main__":
    unittest.main()
