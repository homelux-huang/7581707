#!/usr/bin/env python3
"""Non-release source text and independently recomputed arithmetic regression.

These checks validate a pinned AI visual correction against existing six-WebP
hashes and independent math. They do NOT award formal source/teaching/UI QA.
"""
import hashlib
import json
import math
import os
import pathlib
import unittest

WORKSPACE = pathlib.Path.cwd()
SRC = WORKSPACE / os.environ.get("SUDU_QA_SOURCE_CHECKOUT", "current-qa-source")
DRAFT = WORKSPACE / "draft"
BASE = SRC / "sudu/data/processed/115/review-evidence"
M = DRAFT / "sudu/teaching-drafts/preview-128-20261023"


class VerifiedMathBSourceCorrections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((BASE / "MATHB_20_25_IMAGE_TEXT_CORRECTIONS_20261024.json").read_text())
        cls.progress = json.loads((M / "progress.json").read_text())
        cls.record = {q["questionId"]: q for q in cls.progress["items"]}
        cls.entries = {}
        for ref in cls.ledger["items"]:
            cls.entries[ref["qid"]] = json.loads((SRC / ref["entry"]).read_text())

    def test_exact_six_source_artifacts_are_pinned_and_undisclosed(self):
        self.assertEqual(set(self.entries), {f"115-00-MB-{n:02d}" for n in range(20,26)})
        self.assertIs(self.ledger["formalTextQaPass"], False)
        for qid, value in self.entries.items():
            self.assertEqual(value["sourceWebpSha256"], self.record[qid]["imageSha256"])
            self.assertEqual(value["knownOfficialAnswer"], {20:"A",21:"A",22:"B",23:"B",24:"C",25:"C"}[int(qid[-2:])])
            for k in ("studentReleaseApproved","deploy","formalIndependentHumanTextQaPass"):
                self.assertIs(value["status"][k],False)
            opts=value["correctedText"]["options"]
            self.assertEqual(len(opts),4)
            self.assertTrue(all(s.strip() for s in opts))
            self.assertFalse(any("公告試題僅供參考" in s or "以下空白" in s or "\ue000" in s for s in opts))
            binary=SRC / value["sourceWebp"]
            self.assertTrue(binary.is_file())
            self.assertEqual(hashlib.sha256(binary.read_bytes()).hexdigest(),value["sourceWebpSha256"])

    def test_mathematical_answer_and_option_mapping(self):
        source=lambda n:self.entries[f"115-00-MB-{n}"]["correctedText"]
        self.assertEqual(source(20)["options"][0],"50(√3＋1)")
        self.assertAlmostEqual(100*math.sin(math.radians(75))/math.sin(math.radians(45)),
                               50*(math.sqrt(3)+1))
        roots=[3,5]
        self.assertEqual([x for x in roots if x>4],[5])
        self.assertEqual(source(21)["options"][0],"5")
        self.assertEqual(2**5-1,31)
        self.assertEqual(source(22)["options"][1],"31")
        self.assertEqual(source(22)["question"].count("bô"),1)
        self.assertEqual(len(source(23)["table"]["rows"]),2)
        x=33000
        self.assertEqual(2*x-3000,1.8*(x+2000))
        self.assertEqual(source(23)["options"][1],"33000")
        a=110/8
        b=math.log(3)/math.log(1.08)
        self.assertEqual((math.ceil(a),math.ceil(b)),(14,15))
        self.assertEqual(source(24)["options"][2],"D＝C＋1")
        self.assertIn("√2",source(25)["question"])
        self.assertEqual(4+(2-16),-10)
        self.assertEqual(source(25)["options"][2],"－10")

if __name__=="__main__":
    unittest.main()
