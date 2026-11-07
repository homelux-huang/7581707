'use strict';
/*
 * ROLE D: negative trust-shape and source-vs-composed teaching SHA regression.
 * This test uses synthetic *in-memory invalid receipts* ONLY to reject them.
 * It never touches real approved/policy source files or Chromium UIQA status.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {trustedReceiptProblems,teachingSha,pins}=
 require('./sudu_role_d_emitted_only_8x2_20261106.cjs');
const ID='114-00-E-12',p=pins[ID];
assert.equal(p.teaching,'c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a');
assert.equal(p.composedTeaching,'fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4');
assert.notEqual(p.teaching,p.composedTeaching,'composed SHA must not be testedTeachingDigest');
assert.equal(p.officialEvidence,'63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12');
const authorPath=path.resolve(__dirname,'../_role_b_e12/sudu/teaching-candidates/114-role-b-20261025-batch02/114-00-E-12.json');
assert(fs.existsSync(authorPath),'original real PR107 author source checkout required');
const a=JSON.parse(fs.readFileSync(authorPath,'utf8'));
assert.equal(a.questionId,ID);
assert.equal(a.composedTeachingSha256,p.composedTeaching);
assert.equal(a.source.questionRevision,p.revision);
assert.equal(a.source.webpSha256,p.image);
assert.equal(teachingSha(a.teaching),p.teaching,'official publisher must bind actual canonical teaching SHA');
assert.equal(teachingSha({
 questionId:ID,sourceRevision:p.revision,webpSha256:p.image,
 teaching:a.teaching,enrichment:a.enrichment
}),p.composedTeaching,'historical 114 enriched/composed SHA must remain separately auditable');
const incomplete=[undefined,false,true,'trusted',{},[],null,123];
for(const entry of incomplete)
 assert(trustedReceiptProblems(ID,entry).length>0,'non-object/truthy/fake E registry was incorrectly trusted');
const shape={
 evidencePath:'sudu/data/processed/114/review-evidence/role-e-114-e12-20261107/independent-ai-review.json',
 evidenceGitBlobSha:'a'.repeat(40),sourceCommit:'b'.repeat(40),
 reviewNotesSha256:'c'.repeat(64),reviewTaskId:'E-114-E12-REAL-TRUSTED-RECEIPT-20261107-01',
 sourceAuthorSessionId:'test-B-source-session',reviewerSessionId:'test-E-review-session',
 reviewIssueCommentId:6710069163,reviewerGithubUserId:268841848,reviewerGithubLogin:'homelux-huang',
 questionRevision:p.revision,webpSha256:p.image,teachingDigest:p.teaching,
 officialEvidenceSha256:p.officialEvidence
};
// Do not assert a fabricated positive trust receipt. All tests below must fail.
const reject=(name,changes)=>{
 const problems=trustedReceiptProblems(ID,{...shape,...changes});
 assert(problems.length>0,name+' must be rejected by current D preflight');
 return problems;
};
const checks=[
 ['wrong source revision',{questionRevision:'0'.repeat(64)}],
 ['wrong official E12 image',{webpSha256:'1'.repeat(64)}],
 ['OLD composed instead of actual canonical teaching SHA',{teachingDigest:p.composedTeaching}],
 ['wrong official G3 document SHA',{officialEvidenceSha256:'2'.repeat(64)}],
 ['fake empty E content document',{evidencePath:'not-a-safe-e-review.json'}],
 ['malicious relative E document',{evidencePath:'sudu/data/processed/114/review-evidence/../wrong.json'}],
 ['unverified distinct E author session',{sourceAuthorSessionId:'UNVERIFIED'}],
 ['unverified E reviewer session',{reviewerSessionId:'UNVERIFIED'}],
 ['author self-review',{reviewerSessionId:shape.sourceAuthorSessionId}],
 ['missing actual issue36 E RETURN',{reviewIssueCommentId:0}],
 ['missing actual review source commit',{sourceCommit:'wrong'}],
 ['missing review original markdown SHA',{reviewNotesSha256:null}],
 ['no authenticated GitHub actor',{reviewerGithubUserId:0}],
 ['no authenticated GitHub login',{reviewerGithubLogin:''}],
 ['not ROLE E task',{reviewTaskId:'B-FAKE'}],
 ['not SHA-pinned E evidence blob',{evidenceGitBlobSha:'bad'}]
];
for(const [name,changes] of checks)reject(name,changes);
console.log('PASS ROLE D E12 trusted E fail-closed negatives: '+(incomplete.length+checks.length)+
 ' invalid receipt shapes rejected; actual canonical vs composed author SHA verified. FORMAL E12 UIQA STILL HOLD.');
