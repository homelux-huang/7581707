"""Final AI admission: real exact-five bytes positive; no source-self-PASS authority."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from scripts import sudu_verified_publish as publisher
from scripts import sudu_independent_review_gate as gate

ROOT=Path(__file__).resolve().parents[1]

class FinalAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source=Path(self.tmp.name)
        self.policy=json.loads((ROOT/'sudu/release-governance/independent-review-policy.json').read_text())
        self.records=json.loads((ROOT/'tests/fixtures/loop-historical-five-original-blobs.json').read_text())['records']

    def fixture(self,qid):
        raw=self.records[qid]['rawUtf8'].encode()
        self.assertEqual(gate.blob_oid(raw),self.records[qid]['gitBlobSha'])
        doc=json.loads(raw)
        pin=self.policy['legacyAlreadyPublished'][qid]
        q={'questionId':qid,'year':115,'teaching':copy.deepcopy(doc['content'])}
        item={'sha256':pin['webpSha256']}
        def write(name,raw):
            rel='sudu/data/processed/115/review-evidence/'+qid+'-'+name+'.json'
            p=self.source/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            return {'evidencePath':rel,'evidenceSha256':publisher.digest(raw)}
        q['teachingQaEvidence']=write('teaching',raw)
        q['uiQaEvidence']=write('ui',json.dumps({'testedQuestionRevision':pin['questionRevision']}).encode())
        return q,item,pin['questionRevision']

    def authorize(self,q,item,revision):
        return publisher.final_review_authorized(self.source,q,item,None,revision)

    def test_real_original_five_exact_raw_teaching_bytes_are_preserved(self):
        for qid in sorted(self.records):
            q,item,rev=self.fixture(qid)
            self.assertEqual(self.authorize(q,item,rev),(True,'exact_five_historical_students_preserved'),qid)

    def test_source_teaching_change_is_not_authorized_by_original_blob(self):
        q,item,rev=self.fixture('115-00-MB-02')
        q['teaching']['memory']='unreviewed source override'
        self.assertFalse(self.authorize(q,item,rev)[0])

    def test_raw_blob_resealing_cannot_keep_legacy_exception(self):
        q,item,rev=self.fixture('115-00-MB-02')
        ev=q['teachingQaEvidence'];p=self.source/ev['evidencePath']
        raw=p.read_bytes()+b' ';p.write_bytes(raw);ev['evidenceSha256']=publisher.digest(raw)
        self.assertFalse(self.authorize(q,item,rev)[0])

    def test_changed_webp_or_revision_or_sixth_id_is_rejected(self):
        for field in ['webp','revision','sixth']:
            q,item,rev=self.fixture('115-00-MB-02')
            if field=='webp':item['sha256']='0'*64
            if field=='revision':rev='0'*64
            if field=='sixth':q['questionId']='115-09-2-27'
            self.assertFalse(self.authorize(q,item,rev)[0],field)

    def test_legacy_stale_ui_digest_and_missing_ui_document_rejected(self):
        q,item,rev=self.fixture('115-00-MB-02')
        ev=q['uiQaEvidence'];p=self.source/ev['evidencePath']
        raw=json.dumps({'testedQuestionRevision':rev,'testedTeachingDigest':'0'*64}).encode()
        p.write_bytes(raw);ev['evidenceSha256']=publisher.digest(raw)
        self.assertFalse(self.authorize(q,item,rev)[0])
        p.unlink()
        self.assertFalse(self.authorize(q,item,rev)[0])

    def test_no_registry_receipt_or_raw_teaching_is_not_authority(self):
        q={'questionId':'115-09-2-27','year':115,
           'questionVerified':True,'studentReleaseApproved':True,
           'teachingQaStatus':'PASS','teaching':{'memory':'source-author-PASS'}}
        self.assertFalse(self.authorize(q,{'sha256':'a'*64},'b'*64)[0])

if __name__=='__main__':unittest.main()
