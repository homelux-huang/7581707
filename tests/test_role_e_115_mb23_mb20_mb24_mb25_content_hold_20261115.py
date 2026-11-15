"""ROLE E 115 Math B20/23/24/25 exact originals, fail-closed no-release QA."""
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"sudu/data/processed/115"
NOTE=BASE/"review-evidence/role-e-20261115/MB23-MB20-MB24-MB25-SOURCE-CONTENT-EXACT-AUDIT.md"
NOTE_SHA="f9f69d8c979de11e53214afa19003c97b1f4df5ab4364f43b5290d390b5ce3de"
CASE={
"23":("webp-v2","20261110","2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51","9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4","13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6","B","64fa11a8a40ff221a9b6cbc34a45ae8da14c9c5fa0a04d5b36f2a4012df7cde7","a9c4b2f7e56f8ddb69aca1462af3e762029c5c2e78c6b92d473122b5ba943238","21dad9fb33aa14673c7c7d61900e7536ad9f48c067eb8b5f0ca4dfc8b7cbdad4"),
"20":("webp-v5","20261110","f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf","2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c","2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d","A","c6f33db05c38e9fdb3abc682d27cf8f21550dbd638c84adafd396a2bf3f491e2","67b554b4b1f5543d40ca0e455a209554a94792816916415002ee46d4fe59202c","b5418e24534e9683ff8e9bfd105cee6b2fcbfea6597884d6b85a245a935bd9c3"),
"24":("webp-v2","20261114","c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb","9357c0f8f30ab131f8450c8a9b45d34942fdd8207c6aac688f4f3847a55e8267","317fe1d731f29e9634ec17f0fc1dc5c308b804de5759991a005f94f81bbffd06","C","1caa3da4d5d6ce523f371709f944edaaacc2e5e2abf1240a545a385bfe1743ba","73ec23f02bd01ca625aca64b25641a4e46d224018d34ae6040d62eeaa2225ea4","aed936a25b1fec92831fb90dd24e078cdc3db3148cdf98415d6278af2aa3f41b"),
"25":("webp-v2","20261114","92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896","8b29dffa0c37abd1b37989878a9f8d34392ba71a04017ca1591d6fa45ec9cb6f","a860b08a6f5b76fe1331dc4204a46a3135e511449d9b6004cc4f99be020e4d32","C","eca8ece0babeae6886297dca98bd58ace45018cb289f925f44f3d9c44766a464","2179203705d3a089a1d43e3b4e8beb73eb3dffff6ce0a43e3c16149cf6e5a125","cb2fcc0bb9d8a19082c77a581a402d0f61a839bd5c4f1400dfe280bb7bfd4b48"),
}
def h(raw): return hashlib.sha256(raw).hexdigest()
def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def doc(path): return json.loads(path.read_bytes())

class RoleEOriginalContentHold(unittest.TestCase):
    def test_sha256_and_note(self):
        self.assertEqual(h(b"abc"),"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(h(NOTE.read_bytes()),NOTE_SHA)

    def test_actual_g1_to_g5_same_bytes_and_no_trust(self):
        for n,info in CASE.items():
            im,date,webp_sha,rev,teaching_sha,ans,g2sha,g3sha,g5sha=info
            qid="115-00-MB-"+n
            with self.subTest(qid=qid):
                wp=BASE/im/"00-MB"/(qid+".webp")
                self.assertEqual(h(wp.read_bytes()),webp_sha)
                ev=BASE/"review-evidence"
                files=[ev/(qid+"-ocr-publisher-"+date+".json"),ev/(qid+"-official-publisher-"+date+".json"),ev/(qid+"-teaching-publisher-20261114.json")]
                for f,sha in zip(files,[g2sha,g3sha,g5sha]): self.assertEqual(h(f.read_bytes()),sha)
                g2,g3,g5=map(doc,files)
                if n=="23":
                    table=doc(ev/"115-00-MB-23-table-source-20261103.json")["originalTextAndTable"]
                    self.assertEqual(len(table["sourceTable"]["columns"]),3)
                    self.assertEqual(len(table["sourceTable"]["rows"]),2)
                    self.assertEqual(g2["sourceTables"],[{"heading":table["sourceTable"]["columns"],"rows":table["sourceTable"]["rows"]}])
                    text_seed={"question":g2["question"],"options":g2["options"],"table":table["sourceTable"]}
                    text_sha=h(json.dumps(text_seed,ensure_ascii=False,separators=(",",":")).encode())
                    self.assertEqual(text_sha,table["correctedTextSourceSha256"])
                    seed="ROLE_A_115_MB23_TABLE_G2_G3_SOURCE_EVIDENCE_V1\n"+text_sha+"\n"+webp_sha+"\n"+"d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95"
                    self.assertEqual(seed,table["sourceRevisionSeed"])
                    actual=h(seed.encode())
                else:
                    actual=h(canonical({"question":g2["question"],"options":g2["options"],"singleQuestionWebpSha256":webp_sha}))
                self.assertEqual(actual,rev)
                self.assertEqual(g2["questionRevision"],rev)
                self.assertEqual(g3["finalAnswer"],ans)
                self.assertTrue(g3["correctionNoticeReviewed"])
                self.assertEqual(g5["questionRevision"],rev)
                self.assertEqual(g5["webpSha256"],webp_sha)
                self.assertEqual(g5["canonicalTeachingSha256"],teaching_sha)
                self.assertEqual(h(canonical(g5["content"])),teaching_sha)
                self.assertIsNone(g5["sourceAuthorSessionId"])
                self.assertFalse(g5["independentAiContentReviewed"])
                self.assertFalse(g5["studentReleaseApproved"])

    def test_independent_arithmetic(self):
        self.assertEqual(2*33000-3000,round(1.8*(33000+2000)))
        self.assertAlmostEqual(100*math.sin(math.radians(75))/math.sin(math.radians(45)),50*(math.sqrt(3)+1),places=9)
        self.assertEqual(math.ceil(110/8),14)
        self.assertEqual(math.ceil(math.log(3)/math.log(1.08)),15)
        self.assertEqual(4+(2-16),-10)

if __name__=="__main__": unittest.main()
