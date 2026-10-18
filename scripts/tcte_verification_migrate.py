#!/usr/bin/env python3
"""One-way, idempotent metadata migration: automatic answer pairing is not review.

Does not change question IDs, stems, options, answers, accepted answers or student
storage. Previous flags and immutable git source/JSON SHA are retained as evidence.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from check_tcte_corpus import COVER, review_evidence
from tcte_preserve_teaching import stable_key
ROOT=Path(__file__).resolve().parents[1]
MIGRATION='separate-answer-match-v1'

def migrate(root=ROOT,write=False,backup=None):
    stamp=datetime.now(timezone.utc).isoformat()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    images=json.loads((root/'sudu/data/original/index.json').read_text())
    answers=json.loads((root/'sudu/data/original/answers.json').read_text())
    changed=matched=cover=0
    for file in sorted((root/'sudu/data/years').glob('*.json')):
        original=file.read_bytes();doc=json.loads(original);touched=False;local_matched=local_cover=0
        for paper in doc.get('papers',[]):
            key=f"{doc['year']}/{paper['paper']}";qsha=images['papers'].get(key,{}).get('pdfSha256');asha=answers['papers'].get(key,{}).get('pdfSha256')
            for q in paper.get('questions',[]):
                if q.get('answerVerified') is True and not review_evidence(q,'answer'):
                    q['answerVerificationLegacy']={'migrationId':MIGRATION,'answerVerified':True,'migratedAt':stamp,
                        'sourceCommit':revision,'reason':'automatic_pairing_without_independent_review'}
                    q['answerMatched']=True;q['answerVerified']=False;touched=True;local_matched+=1
                if 'sourceVersion' not in q:
                    q['sourceVersion']={'questionPdfSha256':qsha,'answerPdfSha256':asha}
                    q['sourceVersion']['contentSha256']=stable_key(q);touched=True
                if COVER.search(q.get('question','').strip()):
                    if q.get('questionPresentation')!='original_image_required':
                        q['questionPresentation']='original_image_required'
                        if 'cover_instruction_extraction_suspected' not in q.setdefault('issues',[]):q['issues'].append('cover_instruction_extraction_suspected')
                        touched=True;local_cover+=1
                    mapping=images['papers'].get(key,{}).get('questions',{}).get(q['id'])
                    if mapping and mapping.get('page') is not None:
                        mapping['previousMapping']={k:mapping[k] for k in ('page','mapping','questionVerified') if k in mapping}
                        mapping['page']=None;mapping['mapping']='cover_instruction_mapping_rejected_use_whole_paper'
                        mapping['questionVerified']=False;mapping['reason']='cover_instruction_extraction_suspected'
        if touched:
            if write:
                if backup:
                    target=backup/revision/file.name;target.parent.mkdir(parents=True,exist_ok=True)
                    if not target.exists():target.write_bytes(original)
                doc.setdefault('verificationMigrations',[]).append({'id':MIGRATION,'at':stamp,'sourceCommit':revision,
                    'sourceJsonSha256':hashlib.sha256(original).hexdigest(),'answerFlagsSeparated':local_matched,'coverTextFlagged':local_cover})
                file.write_text(json.dumps(doc,ensure_ascii=False,separators=(',',':')),'utf-8')
            changed+=1;matched+=local_matched;cover+=local_cover
    if write and changed:
        images.setdefault('indexHistory',[]).append({'reason':MIGRATION,'at':stamp,'sourceCommit':revision,
            'note':'Rejected cover-instruction page mappings. Image bytes unchanged; previousMapping retained per question.'})
        (root/'sudu/data/original/index.json').write_text(json.dumps(images,ensure_ascii=False,separators=(',',':')),'utf-8')
    result={'write':write,'yearsChanged':changed,'answerFlagsSeparated':matched,'coverTextFlagged':cover,'migration':MIGRATION}
    print(json.dumps(result));return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--backup',type=Path);p.add_argument('--root',type=Path,default=ROOT)
    a=p.parse_args();migrate(a.root.resolve(),a.write,a.backup)
if __name__=='__main__':main()
