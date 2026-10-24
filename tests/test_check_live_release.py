"""P1: unchanged counts must NEVER hide stale answer/preview/shared/source/lesson."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import check_live_release as live

SHA="f"*40
BASE="https://homelux-huang.github.io/7581707/"
def sha(x): return hashlib.sha256(x).hexdigest()
def stable(x): return live.canonical_digest(x)

class FullLiveCoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.store={}
        def write(route,content):
            b=content if isinstance(content,bytes) else json.dumps(content,ensure_ascii=False,sort_keys=True,indent=2).encode()
            self.store[route]=b
            if route.startswith("sudu/data/approved/") or route=="sudu/verified-questions-runtime.js":
                f=self.root/route
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes(b)
        self.write=write
        runtime=b'const verifiedSingleQuestionWebp=true, p="data/approved";'
        write("sudu/verified-questions-runtime.js",runtime)
        rev=sha(runtime)[:12]
        write("sudu/release.json",{"commit":SHA,"testsRequired":True})
        write("sudu/v4-115-multisubject-review-demo.html",
              f'<script id="demoData"></script><script src="verified-questions-runtime.js?v={rev}"></script>'.encode())
        write("sudu/question-bank-progress.html","題庫接入平台部署進度表".encode())
        source="a"*40
        progress={"provenance":{"commit":source},
                  "years":{"114":{"approvedCount":0,"imagePreviewCount":0,"expected":205},
                           "115":{"approvedCount":1,"imagePreviewCount":3,"expected":205}}}
        write("sudu/data/approved/progress.json",progress)
        write("sudu/data/approved/114.json",{"year":114,"expected":205,"sourceSha":source,"approvedCount":0,"questions":[]})
        write("sudu/data/approved/preview/114.json",{"year":114,"expected":205,"imagePreviewCount":0,"questions":[]})
        write("sudu/data/approved/integrity/114.json",{"schemaVersion":1,"year":114,"sourceSha":source,"approvedCount":0,"questions":[]})
        def image(name):
            rel="data/approved/webp/115/"+name+".webp"
            raw=b"RIFF"+(20).to_bytes(4,"little")+b"WEBP"+name.encode()
            write("sudu/"+rel,raw)
            return {"image":rel,"sha256":sha(raw)}
        self.img=image("115-00-MB-05")
        self.pre=[image("115-00-MB-01"),image("115-00-MB-03"),image("115-00-MB-04")]
        self.shared=[image("115-00-MB-SHARED-03-04"),image("115-00-MB-SHARED-08-09")]
        previews=[{"canonicalId":f"115-00-MB-{i:02d}","year":115,
                  "reviewStage":"image_qa_pass_only","image":x["image"],
                  "imageSha256":x["sha256"],
                  "sharedImages":copy.deepcopy(self.shared) if i==1 else []}
                  for i,x in enumerate(self.pre,start=1)]
        write("sudu/data/approved/preview/115.json",{"year":115,"expected":205,
              "imagePreviewCount":3,"questions":previews})
        self.question={"canonicalId":"115-00-MB-05","year":115,"answer":"B",
                       "question":"real question","options":["a","b","c","d"],
                       "teacherSummary":"professional insight","elementarySummary":"child explanation",
                       "image":self.img["image"],"imageSha256":self.img["sha256"]}
        write("sudu/data/approved/115.json",{"year":115,"expected":205,"sourceSha":source,
              "approvedCount":1,"questions":[self.question]})
        self.proof={"canonicalId":self.question["canonicalId"],"year":115,
                    "sourceQuestionRevision":"b"*64,"teachingCanonicalSha256":"c"*64,
                    "approvedContentSha256":stable(self.question),"officialAnswer":"B",
                    "image":self.img["image"],"imageSha256":self.img["sha256"],"sharedImages":[]}
        write("sudu/data/approved/integrity/115.json",{"schemaVersion":1,"year":115,"sourceSha":source,
             "approvedCount":1,"questions":[self.proof]})
        self.fetcher=lambda base,route,sha:self.store[route]
    def run_checker(self):
        with patch.object(live,"fetch",side_effect=self.fetcher):
            return live.inspect_live(BASE,SHA,root=self.root)
    def mutate_json(self,route,patcher,also_local=False):
        data=json.loads(self.store[route])
        patcher(data)
        raw=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2).encode()
        self.store[route]=raw
        if also_local:(self.root/route).write_bytes(raw)
    def test_every_preview_and_all_shared_and_original_are_checked(self):
        out=self.run_checker()
        self.assertEqual(out["live"],"VERIFIED_ALL_PUBLISHED_BYTES")
        self.assertEqual(out["years"]["115"]["approved"],1)
        self.assertGreaterEqual(out["allDistinctAssetsChecked"],6)
    def test_same_count_changed_last_approved_answer_fails(self):
        self.mutate_json("sudu/data/approved/115.json",lambda j:j["questions"][0].update(answer="A"))
        with self.assertRaises(ValueError):self.run_checker()
    def test_third_preview_image_wrong_sha_fails(self):
        image=self.pre[2]["image"]
        self.store["sudu/"+image]=b"RIFF"+b"fake wrong webp"
        with self.assertRaises(ValueError):self.run_checker()
    def test_second_shared_image_wrong_sha_fails(self):
        image=self.shared[1]["image"]
        self.store["sudu/"+image]=b"RIFF"+b"bad shared"
        with self.assertRaises(ValueError):self.run_checker()
    def test_old_teaching_digest_or_source_revision_denied(self):
        url="sudu/data/approved/integrity/115.json"
        self.mutate_json(url,lambda j:j["questions"][0].update(teachingCanonicalSha256="d"*64),also_local=True)
        self.assertEqual(self.run_checker()["live"],"VERIFIED_ALL_PUBLISHED_BYTES")
        # The trusted local expected artifact has been replaced by the caller:
        # this simulates a NEW signed main code commit, not a stale LIVE mutation.
        self.mutate_json(url,lambda j:j["questions"][0].update(sourceQuestionRevision="e"*64))
        with self.assertRaises(ValueError):self.run_checker()
    def test_tampered_published_content_without_new_integrity_sha_denied(self):
        url="sudu/data/approved/115.json"
        self.mutate_json(url,lambda j:j["questions"][0].update(question="silently modified"),
                         also_local=True)
        with self.assertRaises(ValueError):self.run_checker()
    def test_missing_integrity_manifest_denied(self):
        del self.store["sudu/data/approved/integrity/115.json"]
        with self.assertRaises(KeyError):self.run_checker()
    def test_bogus_same_count_preview_leak_denied(self):
        url="sudu/data/approved/preview/115.json"
        self.mutate_json(url,lambda j:j["questions"][2].update(answer="D"),also_local=True)
        with self.assertRaises(ValueError):self.run_checker()

if __name__=="__main__":
    unittest.main()
