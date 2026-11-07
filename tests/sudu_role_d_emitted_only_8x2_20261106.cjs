'use strict';
/*
 * ROLE D, 2026-11-06: actual protected publisher output only.
 * NO page.route, NO synthetic approved JSON, NO local approval mutation.
 * PRECHECK => HOLD when upstream A/E/Master formal admission is absent.
 * FORMAL => fail closed unless an exact SHA-pinned independent evidence
 * bundle matches the approved emitted row and 8x2 real Chromium results.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const cp=require('node:child_process');
const ROOT=path.resolve(__dirname,'..');
const OUT=path.join(ROOT,'test-results/role-d-emitted-only-20261106');
const SITE=process.env.SUDU_D_SITE||'http://127.0.0.1:8765/sudu/';
const MODE=process.env.SUDU_D_MODE||'precheck';
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const IDS=[
 '114-00-E-12','114-00-E-11','115-00-MB-21','115-00-MB-22','115-00-MB-23'
];
const SHA=/^[0-9a-f]{64}$/;
const HEX40=/^[0-9a-f]{40}$/;
const GIT=(...args)=>cp.execFileSync('git',args,{cwd:ROOT,encoding:'utf8'}).trim();
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const sort=x=>Array.isArray(x)?x.map(sort):(x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sort(x[k])])):x);
const teachingSha=x=>hash(Buffer.from(JSON.stringify(sort(x)),'utf8'));
const load=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const head=cp.execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim();
const pins={
 '114-00-E-12':{image:'99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60',revision:'0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec',teaching:'c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a',composedTeaching:'fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4',officialEvidence:'63056df18120597440feea7489522b6f6f9ba7b039a9b5748795f8b5081f8f12',answer:'C'},
 '114-00-E-11':{image:'ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0',revision:'646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036',teaching:'ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb',composedTeaching:'3d250e8ecd621eda0f14f1839e6cf89b70b3649a1af0298611fedd9bbf57ceee',answer:'A'},
 '115-00-MB-21':{image:'b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693',revision:'817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9',teaching:'4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4',answer:'A'},
 '115-00-MB-22':{image:'3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55',revision:'7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17',teaching:'5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600',answer:'B'},
 '115-00-MB-23':{image:'2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51',revision:'9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4',teaching:'13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6',answer:'B'}
};
const report={role:'D',mode:MODE,headSHA:head,qaOnly:false,
 noInterception:true,formalEvidenceRequired:true,
 cases:[],errors:[],status:'STARTED',outcomes:{},runId:process.env.GITHUB_RUN_ID||null};
function save(){fs.mkdirSync(OUT,{recursive:true});fs.writeFileSync(path.join(OUT,'formal-uiqa-report.json'),JSON.stringify(report,null,2)+'\n');}
function fail(msg){report.errors.push(msg);report.status='FAIL';save();throw Error(msg);}
function check(cond,msg){if(!cond)fail(msg);}
function qidYear(id){return Number(id.slice(0,3));}
function trustedReceiptProblems(id,entry){
 const problems=[],year=qidYear(id),pin=pins[id];
 if(!entry||typeof entry!=='object'||Array.isArray(entry)){
  return ['no structured protected trustedAiReviewReceipts QID'];
 }
 const validText=v=>typeof v==='string'&&v.trim().length>=6&&
  !/^(unverified|unknown|null|none|placeholder|synthetic|fake|test|pending)/i.test(v.trim());
 const pathPrefix='sudu/data/processed/'+year+'/review-evidence/';
 if(typeof entry.evidencePath!=='string'||!entry.evidencePath.startsWith(pathPrefix)||
    !entry.evidencePath.endsWith('.json')||entry.evidencePath.split('/').includes('..'))
  problems.push('trusted E receipt evidencePath invalid');
 for(const field of ['evidenceGitBlobSha','sourceCommit']){
  if(!HEX40.test(entry[field]))problems.push('trusted E receipt '+field+' missing/invalid');
 }
 if(!SHA.test(entry.reviewNotesSha256))problems.push('trusted E reviewer notes SHA missing');
 if(!String(entry.reviewTaskId||'').startsWith('E-'))
  problems.push('trusted E actual E-role reviewTaskId invalid');
 if(!validText(entry.sourceAuthorSessionId)||!validText(entry.reviewerSessionId)||
    entry.sourceAuthorSessionId?.toLowerCase()===entry.reviewerSessionId?.toLowerCase())
  problems.push('trusted E source author/reviewer distinct-session provenance invalid');
 if(!Number.isInteger(entry.reviewIssueCommentId)||entry.reviewIssueCommentId<=0)
  problems.push('trusted E actual Issue36 RETURN ID missing');
 if(!Number.isInteger(entry.reviewerGithubUserId)||entry.reviewerGithubUserId<=0||
    typeof entry.reviewerGithubLogin!=='string'||!entry.reviewerGithubLogin.trim())
  problems.push('trusted E authenticated GitHub reviewer identity missing');
 if(entry.questionRevision!==pin.revision)problems.push('trusted E questionRevision mismatch');
 if(entry.webpSha256!==pin.image)problems.push('trusted E original WebP SHA mismatch');
 if(entry.teachingDigest!==pin.teaching)problems.push('trusted E canonical teaching SHA mismatch');
 if(pin.officialEvidence&&entry.officialEvidenceSha256!==pin.officialEvidence)
  problems.push('trusted E formal G3 official evidence SHA mismatch');
 if(!SHA.test(entry.officialEvidenceSha256))
  problems.push('trusted E G3 official evidence SHA missing');
 return problems;
}
function verifyProtectedMainPolicyRoot(){
 // The source/PR branch MUST NOT self-assert a trusted registry. The trusted
 // policy Git blob must equal remote protected main, fetched at this CI run.
 if(MODE!=='formal'&&process.env.SUDU_D_REQUIRE_PROTECTED_ROOT!=='1')return;
 if(process.env.GITHUB_ACTIONS==='true')
  check(process.env.GITHUB_REPOSITORY==='homelux-huang/7581707','wrong GitHub Actions repository');
 let remoteHead,remoteBlob,localBlob;
 try {
  remoteHead=GIT('rev-parse','refs/remotes/origin/main');
  remoteBlob=GIT('rev-parse','refs/remotes/origin/main:sudu/release-governance/independent-review-policy.json');
  localBlob=GIT('hash-object','sudu/release-governance/independent-review-policy.json');
 }catch(err){fail('protected main Git remote policy unavailable: '+String(err));}
 check(HEX40.test(remoteHead)&&HEX40.test(remoteBlob),'unverifiable protected main SHA/blob');
 check(remoteBlob===localBlob,'PR/source branch policy differs from protected main trust root');
 if(MODE==='formal')
  check(process.env.SUDU_D_PROTECTED_MAIN_SHA===remoteHead,
    'formal tested protected main commit pin missing or stale');
 report.protectedMainSHA=remoteHead;
 report.protectedPolicyGitBlob=remoteBlob;
}
function prepare(){
 verifyProtectedMainPolicyRoot();
 check(['precheck','formal'].includes(MODE),'unknown mode: '+MODE);
 const policy=load('sudu/release-governance/independent-review-policy.json');
 check(policy.reviewMode==='DISTINCT_AI_CONTENT_RECEIPT_V1'&&policy.requireHumanTeacher===false,
  'protected distinct AI independent policy unavailable');
 const trust=policy.trustedAiReviewReceipts||{};
 check(typeof trust==='object'&&!Array.isArray(trust),'trusted receipt registry invalid');
 const approved={114:load('sudu/data/approved/114.json'),115:load('sudu/data/approved/115.json')};
 for(const year of [114,115]){
  const data=approved[year];
  check(data.year===year&&data.expected===205&&data.approvedCount===data.questions.length,
   'real publisher approved year parity invalid: '+year);
  const seen=new Set();
  for(const q of data.questions){
   check(!seen.has(q.canonicalId),'duplicate approved QID '+q.canonicalId);
   seen.add(q.canonicalId);
  }
 }
 const ready={};
 for(const id of IDS){
  const year=qidYear(id);
  const q=approved[year].questions.find(x=>x.canonicalId===id);
  const missing=[];
  if(!q)missing.push('actual protected approved/'+year+'.json has no QID');
  missing.push(...trustedReceiptProblems(id,trust[id]));
  if(q){
   if(q.image!=='data/approved/webp/'+year+'/'+id+'.webp')missing.push('emitted WebP identity mismatch');
   if(q.imageSha256!==pins[id].image)missing.push('original source WebP SHA mismatch');
   if(q.answer!==pins[id].answer)missing.push('published official answer mismatch');
   if(!Array.isArray(q.options)||q.options.length!==4)missing.push('four options missing');
   if(!q.optionExplanations||'ABCD'.split('').some(k=>!q.optionExplanations[k]?.teacher||!q.optionExplanations[k]?.elementary))
    missing.push('four choice teacher/elementary explanation incomplete');
  }
  ready[id]={q,missing};
  report.outcomes[id]={status:missing.length?'HOLD':'ADMITTED_PREFLIGHT_ONLY',
   sourceRevision:pins[id].revision,expectedTeachingDigest:pins[id].teaching,
   historicalComposedTeachingDigest:pins[id].composedTeaching||null,
   originalWebpSHA256:pins[id].image,missing};
 }
 return {ready,trust};
}
async function formal(){
 const id=process.env.SUDU_D_QID;
 check(IDS.includes(id),'formal mode requires exact allowlisted SUDU_D_QID');
 check(process.env.SUDU_D_EXPECT_SHA===head,'formal mode requires exact tested Git head');
 check(process.env.SUDU_D_QA_ONLY!=='1','QA-only runner cannot be formal');
 const {ready}=prepare();
 const record=ready[id];check(record.missing.length===0,'HOLD upstream admission: '+record.missing.join('; '));
 const q=record.q,expected=pins[id],year=qidYear(id);
 const trusted=load('sudu/release-governance/independent-review-policy.json').trustedAiReviewReceipts[id];
 // The independent upstream evidence bundle is mandatory, never reconstructed
 // from author-controlled QA flags or from the visible approved row.
 const rel=process.env.SUDU_D_FORMAL_EVIDENCE_PATH||'';
 const expectedFileSha=process.env.SUDU_D_FORMAL_EVIDENCE_SHA256||'';
 check(rel.startsWith('sudu/')&&!rel.includes('..')&&rel.endsWith('.json')&&SHA.test(expectedFileSha),
  'missing SHA-pinned current formal source/teaching/reviewer evidence bundle');
 const fp=path.resolve(ROOT,rel);
 check(fp.startsWith(ROOT+path.sep),'unsafe formal evidence path');
 const bytes=fs.readFileSync(fp);
 check(hash(bytes)===expectedFileSha,'formal evidence byte SHA mismatch');
 const proof=JSON.parse(bytes.toString('utf8'));
 for(const [field,value] of Object.entries({
  questionId:id,year,sourceRevision:expected.revision,
  webpSha256:expected.image,teachingDigest:expected.teaching,officialAnswer:expected.answer
 }))check(proof[field]===value,'formal evidence '+field+' mismatch');
 check(proof.sourceCanonicalAdmission===true&&proof.independentContentReceiptAccepted===true&&proof.publisherEmissionVerified===true,
  'formal upstream admission evidence incomplete');
 check(proof.authorSessionId===trusted.sourceAuthorSessionId&&
       proof.reviewerSessionId===trusted.reviewerSessionId&&
       proof.authorSessionId!==proof.reviewerSessionId,
  'formal bundle author/reviewer sessions are not the protected E receipt');
 check(proof.reviewTaskId===trusted.reviewTaskId&&
       proof.officialEvidenceSha256===trusted.officialEvidenceSha256&&
       proof.evidenceGitBlobSha===trusted.evidenceGitBlobSha,
  'formal bundle E task/evidence does not match the protected receipt');
 check(proof.testedTeachingDigest===expected.teaching,'evidence testedTeachingDigest differs from current content');
 check(proof.teaching&&typeof proof.teaching==='object',
  'actual authored teaching object missing');
 check(teachingSha(proof.teaching)===expected.teaching,
  'actual canonical teaching content SHA256 mismatch');
 // 114 PR107 additionally recorded a composed digest over source+enrichment.
 // This is NOT the UI emitter's testedTeachingDigest (which is canonical teaching).
 if(expected.composedTeaching&&proof.composedCanonicalPayload){
  const composed=proof.composedCanonicalPayload;
  check(proof.composedTeachingDigest===expected.composedTeaching&&
        composed.questionId===id&&composed.sourceRevision===expected.revision&&
        composed.webpSha256===expected.image&&
        JSON.stringify(composed.teaching)===JSON.stringify(proof.teaching)&&
        composed.enrichment&&typeof composed.enrichment==='object'&&
        teachingSha(composed)===expected.composedTeaching,
    'optional historical 114 composed teaching/enrichment SHA mismatches actual PR107 evidence');
 }
 // Historical composed/enrichment receipt is independently verified against
 // immutable PR107 by the separate CI negative test; the production publisher
 // itself MUST bind testedTeachingDigest to canonical teach.content instead.
 // Validate every emitted teaching-facing field against the original
 // SHA-pinned authored object; public publisher intentionally omits QA metadata.
 const t=proof.teaching;
 for(const k of ['concept','extension','teacherSummary','elementarySummary','optionExplanations'])
  check(JSON.stringify(q[k])===JSON.stringify(t[k]),'emitted teaching content mismatch: '+k);
 check(q.memory===String(t.memory||'').replace(/\*\*(.*?)\*\*/g,'$1'),
  'emitted memory differs from canonical authored lesson');
 check(JSON.stringify(q.highlights)===JSON.stringify(t.highlights||[]),
  'emitted highlights differ from canonical authored lesson');
 check(q.sourceText===t.source,'emitted source text mismatch');
 check(q.formula===(t.formula||''),'emitted formula mismatch');
 check(q.question===proof.question&&JSON.stringify(q.options)===JSON.stringify(proof.options),
  'emitted official text/options differ from source');
 check(q.imageSha256===expected.image,'emitted original image SHA mismatch');
 if(id==='115-00-MB-23'){
  const table=proof.officialOriginalTable;
  check(table&&table.title==='表（二）'&&Array.isArray(table.columns)&&table.columns.length===3
    &&Array.isArray(table.rows)&&table.rows.length===2,
   'MB23 exact original 2-row x 3-column table evidence missing');
  check(JSON.stringify(table.columns).includes('行程')&&JSON.stringify(table.columns).includes('原價')
    &&JSON.stringify(table.columns).includes('優惠'),
   'MB23 official header/columns missing');
  check(JSON.stringify(table.rows).includes('3000')&&JSON.stringify(table.rows).includes('2000'),
   'MB23 official original discount and original price formula missing');
 }
 const {chromium}=require('playwright');
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const url=SITE+'v4-115-multisubject-review-demo.html?year='+year;
 try{
  for(const [width,height] of SIZES)for(const theme of ['light','dark']){
   const ctx=await browser.newContext({viewport:{width,height},hasTouch:width<=430,reducedMotion:'reduce'});
   const page=await ctx.newPage(),errs=[],label=id+'-'+width+'x'+height+'-'+theme;
   page.on('pageerror',x=>errs.push('JS '+x.message));
   page.on('response',x=>{if(x.status()>=400&&x.url().includes('/sudu/'))errs.push('HTTP '+x.status()+' '+x.url());});
   try{
    const resp=await page.goto(url,{waitUntil:'domcontentloaded'});
    assert(resp&&resp.ok(),'V4 route failed');
    await page.waitForFunction(y=>document.body.dataset.verifiedReadyYear===String(y),year,{timeout:25000});
    const website=await page.request.get(SITE+'data/approved/'+year+'.json');
    assert(website.ok(),'emitted JSON HTTP failure');
    const raw=await website.json();
    assert.deepEqual(raw,load('sudu/data/approved/'+year+'.json'),'HTTP emitted approved JSON not exact local publisher artifact');
    const homeSubject=q.subject;
    await page.locator('#homeSubjectSel').selectOption(homeSubject);
    await page.locator('#studyView').waitFor({state:'visible'});
    const found=await page.evaluate(want=>{
     const all=QUESTIONS.filter(x=>x.canonicalId===want);
     if(all.length!==1)return null;
     currentSubject=all[0].subject;
     currentIndex=list().findIndex(x=>x.canonicalId===want);
     renderAll();
     return qnow()?.canonicalId;
    },id);
    assert.equal(found,id,'current student V4 question selection');
    if((await page.locator('html').getAttribute('data-theme'))!==theme)
     await page.locator('#themeBtn').click();
    assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
    const img=page.locator('#questionCard img').first();
    await img.scrollIntoViewIfNeeded();
    await img.evaluate(async el=>el.decode());
    assert.equal(await img.getAttribute('src'),q.image);
    const wb=await page.request.get(SITE+q.image);
    assert(wb.ok(),'official original WebP HTTP missing');
    assert.equal(hash(await wb.body()),expected.image,'WebP byte SHA');
    assert.equal(await page.locator('#answerCard .opt').count(),4);
    assert.equal((await page.locator('#questionCard h1').innerText()).trim(),q.question.trim(),
     'emitted question text mismatch');
    for(let i=0;i<4;i++){
     const el=page.locator('#answerCard .opt').nth(i);
     assert.equal(await el.getAttribute('data-a'),'ABCD'[i]);
     const txt=await el.locator('.opt-text').innerText();
     assert.equal(txt.replace(/\s+/g,''),q.options[i].replace(/\s+/g,''),
      'emitted option text mismatch at '+i);
    }
    for(const L of 'ABCD')assert.equal(await page.locator('#answerCard .opt[data-a="'+L+'"]').count(),1);
    await page.locator('#answerCard .opt[data-a="'+(q.answer==='A'?'B':'A')+'"]').click();
    await page.locator('#guideCard.show').waitFor();
    assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
    assert.equal(await page.locator('#answerCard .option-detail').count(),4);
    const calc=await page.locator('#guideCard .calculation-step').count();
    if(t.hasExamCalculation===false){
     assert.equal(calc,0,'non-calculation question must hide calculation card');
     assert.equal(await page.locator('#guideCard .calculation-first').count(),0);
    } else {
     assert(calc>0,'real calculation steps missing');
     assert(t.examCalculation&&t.examCalculation.steps?.length,'calculation steps unbound');
    }
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
    assert.equal(overflow,false,'horizontal layout overflow');
    assert.deepEqual(errs,[],'JS/image/API failures');
    const screenshot=label+'.png';
    await page.screenshot({path:path.join(OUT,screenshot),animations:'disabled'});
    const screenshotSha256=hash(fs.readFileSync(path.join(OUT,screenshot)));
    report.cases.push({qid:id,width,height,theme,screenshot,screenshotSha256,sourceRevision:expected.revision,
     testedTeachingDigest:expected.teaching,imageSha256:expected.image,result:'PASS'});
   }catch(err){
    report.errors.push({qid:id,width,height,theme,error:String(err.stack||err),browserErrors:errs});
    try{await page.screenshot({path:path.join(OUT,label+'-FAIL.png')});}catch{}
   }finally{await ctx.close();save();}
  }
 }finally{await browser.close();}
 if(report.errors.length||report.cases.length!==16)fail('FORMAL_UIQA_FAIL; review screenshots and exact SHA report');
 report.outcomes[id].status='FORMAL_EMITTER_CHROMIUM_16_OF_16_PASS';
 report.status='FORMAL_EMITTER_CHROMIUM_16_OF_16_PASS';
 save();
 console.log('PASS 16/16 actual emitted V4 '+id+' exact source/image/canonical teaching SHA. MASTER decides READY.');
}
async function main(){
 fs.mkdirSync(OUT,{recursive:true});
 if(MODE==='precheck'){
  const {ready}=prepare();
  report.status=IDS.every(id=>ready[id].missing.length===0)?'ADMISSION_CANDIDATES_PRESENT_NOT_UIQA':'HOLD_UPSTREAM_ADMISSION';
  save();
  console.log(JSON.stringify({status:report.status,headSHA:head,outcomes:report.outcomes}));
  return;
 }
 await formal();
}
module.exports={trustedReceiptProblems,teachingSha,pins};
if(require.main===module)main().catch(err=>{
 report.status='FAIL';report.errors.push(String(err.stack||err));save();
 console.error(err.stack||err);process.exitCode=1;
});
