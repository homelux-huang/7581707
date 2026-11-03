'use strict';
/* ROLE D 115 MB21/22 original source + authentic C teaching exact-SHA V4 8x2.
 * QA-ONLY browser-local HTTP interception; NOT a publisher emission, E, READY, or LIVE.
 */
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs');
const path=require('node:path');
const cp=require('node:child_process');
const {URL:NativeURL}=require('node:url');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const SITE=process.env.SUDU_D_SITE||'http://127.0.0.1:8765/sudu/';
const OUT=path.resolve(process.env.SUDU_D_OUT||'test-results/role-d-115-mb21-mb22-staged');
const A=process.env.SUDU_D_A_DIR||'_role_a_115_mb21_mb22';
const C=process.env.SUDU_D_C_DIR||'_role_c_115_mb21_mb22';
const AHEAD='fbd7756b995e3d27dc31a99ecc54fe66af4d82c6';
const CHEAD='e50198cad6821a5252008bd474d8240510832f85';
const IDS=['115-00-MB-21','115-00-MB-22'];
const SIZE=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const SHAS={
 '115-00-MB-21':{image:'b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693',revision:'817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9',teaching:'4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4',answer:'A'},
 '115-00-MB-22':{image:'3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55',revision:'7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17',teaching:'5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600',answer:'B'}
};
const abs=p=>path.join(ROOT,p);
const raw=p=>fs.readFileSync(abs(p));
const read=p=>JSON.parse(raw(p).toString('utf8'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const blob=x=>crypto.createHash('sha1').update(Buffer.concat([Buffer.from('blob '+x.length),Buffer.from([0]),x])).digest('hex');
const git=dir=>cp.execFileSync('git',['rev-parse','HEAD'],{cwd:abs(dir||'.'),encoding:'utf8'}).trim();
const sort=x=>Array.isArray(x)?x.map(sort):(x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sort(x[k])])):x);
const canonical=x=>sha(Buffer.from(JSON.stringify(sort(x)),'utf8'));
const normalize=x=>String(x||'').replace(/\s+/g,'');
const head=git();
assert.equal(process.env.SUDU_D_QA_ONLY,'1','QA-only must be explicitly enabled; never emit release data');
if(process.env.SUDU_D_EXPECT_SHA)assert.equal(head,process.env.SUDU_D_EXPECT_SHA,'D head different from run SHA');
assert.equal(git(A),AHEAD,'official source A Git head changed');
assert.equal(git(C),CHEAD,'independent author C Git head changed');
const main115raw=raw('sudu/data/approved/115.json');
assert.equal(blob(main115raw),'51e7b4e73e2d46b4c8b1672c6af20477cc90d44e',
 'actual five formal 115 approved rows changed; stop and re-evaluate');
const main115=JSON.parse(main115raw.toString('utf8'));
assert.equal(main115.approvedCount,5,'no new MB21/22 formal emission permitted by this test');
assert(!main115.questions.some(q=>IDS.includes(q.canonicalId)),'MB21/22 already formally emitted: QA-only test is obsolete');
const bank=read(A+'/sudu/data/processed/115/questions.json');
const manifest=read(A+'/sudu/data/processed/115/webp-manifest.json');
const official=read(A+'/sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json');
const batch=read(C+'/sudu/teaching-candidates/114-115-20261025/batch.json');
assert.equal(bank.questions.length,205,'115 original canonical bank count changed');
assert.equal(official.itemCount,25,'original official Math B answer source 25-row scope changed');
const source=[...IDS].map(id=>{
 const q=bank.questions.find(x=>x.questionId===id);
 const m=manifest.items.find(x=>x.questionId===id);
 const r=official.records.find(x=>x.questionId===id);
 const tpath=C+'/sudu/teaching-candidates/114-115-20261025/'+id+'.json';
 const t=read(tpath),receipt=batch.items.find(x=>x.questionId===id),expected=SHAS[id];
 assert(q&&m&&r&&t&&receipt,id+' source/manifest/official/author/batch missing');
 assert.equal(t.questionId,id);assert.equal(t.year,115);assert.equal(t.sourceCommit,AHEAD);
 assert.equal(t.studentReleaseApproved,false);assert.equal(t.deploy,false);
 assert.equal(t.review.externalIndependentReview,'PENDING','must not fabricate review receipt');
 assert.equal(t.sourceTextRevisionWithoutTable,expected.revision);
 assert.equal(t.imageSha256,expected.image);
 assert.equal(t.teachingCanonicalSha256,expected.teaching);
 assert.equal(canonical(t.teaching),expected.teaching,'actual author teaching content digest differs');
 assert.equal(receipt.teachingSha256,expected.teaching);
 assert.equal(sha(raw(tpath)),receipt.fileSha256,'author raw file or batch changed');
 assert.equal(t.image,m.output);
 assert.equal(m.sha256,expected.image);
 assert.equal(m.qaStatus,'PASS','historical pixel G1 must be PASS; does not imply G2/READY');
 assert.equal(m.visualReviewEvidence.reviewedSha256,expected.image);
 assert.equal(m.sourcePdfSha256,'e82e34d9cda67c8d28f556d7eb0cd8486b66ccfbe4423d7a40857d7289082');
 assert.equal(sha(raw(A+'/'+m.output)),expected.image,'actual original one-question WebP bytes differ');
 assert.equal(q.question,t.question,'source original stem vs author teaching mismatch');
 assert.deepEqual(q.options,t.options,'source original A-D options vs C author mismatch');
 assert.equal(q.answer,expected.answer,'original A bank letter vs actual final published image');
 assert.equal(r.officialFinalAnswerReadDirectlyFromPublishedImage,expected.answer);
 assert.equal(r.answerVerified,true,'historic printed official answer not verified');
 assert.equal(r.questionVerified,false,'do not silently certify G2 OCR from old answer record');
 assert.equal(r.officialCorrectionChecked,true);
 assert.equal(r.integrationReady,false,'cannot claim source admitted');
 assert.equal(t.teaching.hasExamCalculation,true);
 assert.equal(t.teaching.calculationReviewed,true);
 assert.equal(t.teaching.examCalculation.option,expected.answer);
 assert(t.teaching.examCalculation.steps.length>=4,'authored full calculation steps missing');
 assert(t.teaching.examCalculation.steps.some(x=>/核對|代回|合計|驗算/.test(x)),id+' independent reverse check missing');
 assert.deepEqual(Object.keys(t.teaching.optionExplanations).sort(),['A','B','C','D']);
 for(const L of 'ABCD')for(const k of ['teacher','elementary','reason']){
  assert(t.teaching.optionExplanations[L][k]?.trim().length>4,id+' '+L+' missing C '+k);
 }
 const e=t.teaching.examCalculation;
 const lines=[...e.given.map(x=>'已知條件：'+x),
  '公式用途：'+e.formulaUse,...e.substitution.map(x=>'代入：'+x),
  ...e.steps,'結果：'+e.result,'對應選項：'+expected.answer];
 const publicQuestion={
  id:Number(id.slice(-2)),canonicalId:id,year:115,subject:'數學 B',
  topic:t.teaching.concept,question:t.question,options:t.options,answer:expected.answer,
  memory:t.teaching.memory,concept:t.teaching.concept,extension:t.teaching.extension,
  formula:t.teaching.formula,teacherSummary:t.teaching.teacherSummary,
  elementarySummary:t.teaching.elementarySummary,
  optionExplanations:t.teaching.optionExplanations,sourceText:t.teaching.source,
  highlights:t.teaching.highlights,extra:{},
  examCalculation:{hasExamCalculation:true,lines},
  image:'data/approved/webp/115/'+id+'.webp',imageSha256:expected.image,
  qaOnlySourceRevision:expected.revision,qaOnlyTeachingDigest:expected.teaching
 };
 return {id,author:t,source:q,manifest:m,record:r,expected,lines,
  publicQuestion,rawWebpPath:A+'/'+m.output};
});
const staging={schemaVersion:1,year:115,approvedCount:2,questions:source.map(x=>x.publicQuestion),
 QA_ONLY_UNPUBLISHABLE:true,studentReleaseApproved:false,actualFormalApprovedCount:5};
const report={
 schemaVersion:1,role:'D',taskId:'D-115-MB21-MB22-REAL-SOURCE-STAGED-8X2-20261103-05',
 headSHA:head,roleASourceHEAD:AHEAD,roleCAuthorHEAD:CHEAD,
 originalBankGitBlob:blob(raw(A+'/sudu/data/processed/115/questions.json')),
 originalManifestGitBlob:blob(raw(A+'/sudu/data/processed/115/webp-manifest.json')),
 originalOfficialFinalAnswerEvidenceSHA256:sha(raw(A+'/sudu/data/processed/115/QA_115_MATH_B_Q01_25_OFFICIAL_FINAL_ANSWERS_20261023.json')),
 htmlSHA256:sha(raw('sudu/v4-115-multisubject-review-demo.html')),
 runtimeSHA256:sha(raw('sudu/verified-questions-runtime.js')),
 formalApproved115GitBlob:blob(main115raw),formalApproved115Count:5,
 fixedCandidateRows:source.map(x=>({id:x.id,questionRevision:x.expected.revision,
  originalSingleWebPSHA256:x.expected.image,exactAuthorTeachingDigest:x.expected.teaching,
  authorFileSHA256:sha(raw(C+'/sudu/teaching-candidates/114-115-20261025/'+x.id+'.json')),
  officialPublishedAnswer:x.expected.answer,originalFinalAnswerChecked:true,
  sourceG2FormallyAdmitted:false,formalEReceipt:false})),
 CIrun:process.env.GITHUB_RUN_ID||null,QA_ONLY:true,actualPublisherEmission:false,
 READY:0,newLIVE:0,cases:[],errors:[],status:'STARTED'
};
function save(){fs.mkdirSync(OUT,{recursive:true});fs.writeFileSync(path.join(OUT,'115-MB21-MB22-QA-ONLY.json'),JSON.stringify(report,null,2)+'\n');}
const targetFiles=[];
for(const r of source){
 const t=abs('_site/sudu/'+r.publicQuestion.image);fs.mkdirSync(path.dirname(t),{recursive:true});
 fs.copyFileSync(abs(r.rawWebpPath),t);assert.equal(sha(fs.readFileSync(t)),r.expected.image);
 targetFiles.push(t);
}
const action=(x,touch)=>touch?x.tap({timeout:15000}):x.click({timeout:15000});
async function layout(page,label){
 const r=await page.evaluate(()=>{
  const clipped=[...document.querySelectorAll('#questionCard h1,#answerCard .opt-text,#guideCard .calculation-step')]
    .filter(x=>x.offsetWidth>0&&x.scrollWidth>x.clientWidth+3&&['hidden','clip'].includes(getComputedStyle(x).overflowX))
    .map(x=>x.innerText?.slice(0,90));
  return {document:document.documentElement.scrollWidth,viewport:innerWidth,clipped};
 });
 assert(r.document<=r.viewport+1,label+' horizontal overflow '+JSON.stringify(r));
 assert.deepEqual(r.clipped,[],label+' clipped formula / options / title');
}
async function fontGate(page,label){
 const a=await page.evaluate(async()=>{
  await document.fonts.ready;
  const el=document.getElementById('guideCard'),ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
  ctx.canvas.width=80;ctx.canvas.height=80;ctx.font='48px '+getComputedStyle(el).fontFamily;
  ctx.fillStyle='#000';ctx.textBaseline='top';
  return ['數','學','題','步'].map(ch=>{
    ctx.clearRect(0,0,80,80);ctx.fillText(ch,2,2);
    const bytes=ctx.getImageData(0,0,80,80).data;
    let pixels=0,hash=2166136261;
    for(let n=3;n<bytes.length;n+=4){if(bytes[n]>32)pixels++;hash=Math.imul(hash^bytes[n],16777619)>>>0;}
    return {ch,pixels,hash};
  });
 });
 assert(a.every(x=>x.pixels>70)&&new Set(a.map(x=>x.hash)).size>=3,label+' CJK tofu glyph');
 return a;
}
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of SIZE)for(const theme of ['light','dark']){
   const touch=width<=430;
   const ctx=await browser.newContext({viewport:{width,height},locale:'zh-TW',hasTouch:touch,reducedMotion:'reduce'});
   const page=await ctx.newPage(),pageErrors=[];
   page.on('pageerror',x=>pageErrors.push(x.message));
   try{
    // Local Chromium-only temporary HTTP intercept, never GitHub Pages or actual approved JSON.
    await page.route('**/sudu/data/approved/115.json',r=>r.fulfill({
     status:200,contentType:'application/json; charset=utf-8',body:JSON.stringify(staging)
    }));
    const resp=await page.goto(SITE+'v4-115-multisubject-review-demo.html?year=115',{waitUntil:'domcontentloaded'});
    assert(resp?.ok(),'V4 student page not loaded');
    await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='115' &&
      !document.body.classList.contains('qa-image-mode'),null,{timeout:30000});
    await page.evaluate(()=>{document.body.dataset.roleDQaOnly='STAGED_SOURCE_UNPUBLISHED_115_MB21_22'});
    await page.addStyleTag({content:'body::after{content:"QA-ONLY / NOT APPROVED OR LIVE";position:fixed;bottom:1px;right:1px;background:#900;color:#fff;padding:5px 7px;border-radius:4px;font:700 11px sans-serif;z-index:999999;pointer-events:none}'});
    assert(await page.locator('#homeView').isVisible());
    const demoBefore=await page.evaluate(()=>localStorage.getItem('tvet-115-multisubject-demo-v1'));
    await page.locator('#homeSubjectSel').selectOption('數學 B');
    await page.locator('#studyView').waitFor({state:'visible',timeout:15000});
    if(theme==='dark')await action(page.locator('#themeBtn'),touch);
    assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
    for(let i=0;i<source.length;i++){
     const q=source[i],p=q.publicQuestion,label=q.id+' '+width+'x'+height+' '+theme;
     const inBrowser=await page.evaluate(()=>({
      id:qnow()?.canonicalId,stem:qnow()?.question,answers:qnow()?.options,
      correct:qnow()?.answer,calculation:qnow()?.examCalculation,
      revision:qnow()?.qaOnlySourceRevision,digest:qnow()?.qaOnlyTeachingDigest
     }));
     assert.equal(inBrowser.id,q.id,label+' question ID mismatch');
     assert.equal(inBrowser.stem,p.question);
     assert.deepEqual(inBrowser.answers,p.options);
     assert.equal(inBrowser.correct,q.expected.answer);
     assert.equal(inBrowser.revision,q.expected.revision);
     assert.equal(inBrowser.digest,q.expected.teaching);
     assert.deepEqual(inBrowser.calculation,p.examCalculation,'all actual author formula lines changed');
     assert.equal(await page.locator('#questionCard h1').textContent(),p.question);
     const opts=page.locator('#answerCard .opt');
     assert.equal(await opts.count(),4);
     for(let n=0;n<4;n++){
      assert.equal(await opts.nth(n).getAttribute('data-a'),'ABCD'[n]);
      assert.equal(normalize(await opts.nth(n).locator('.opt-text').innerText()),
        normalize(p.options[n]),label+' official answer option changed');
     }
     const image=page.locator('#questionCard img').first();
     assert.equal(await image.getAttribute('src'),p.image);
     await image.scrollIntoViewIfNeeded();
     const dims=await image.evaluate(async el=>{
      await el.decode();const a=el.getBoundingClientRect(),b=el.parentElement.getBoundingClientRect();
      return {w:a.width,h:a.height,nw:el.naturalWidth,nh:el.naturalHeight,parent:b.width};
     });
     assert(dims.nw>0&&dims.nh>0&&dims.w<=dims.parent+1);
     assert(Math.abs(dims.w/dims.h-dims.nw/dims.nh)/(dims.nw/dims.nh)<0.03);
     const imageHTTP=await page.request.get(new NativeURL('./'+p.image,SITE).href);
     assert(imageHTTP.ok(),label+' original image missing');
     assert.equal(sha(await imageHTTP.body()),q.expected.image,'source-true WebP SHA mismatch');
     await layout(page,label+' before answer');
     if(!touch){
      const b=await opts.first().evaluate(e=>getComputedStyle(e).backgroundColor);
      await opts.first().hover();await page.waitForTimeout(145);
      assert.notEqual(await opts.first().evaluate(e=>getComputedStyle(e).backgroundColor),b,label+' mouse hover absent');
     }
     const wrong=q.expected.answer==='A'?'B':'A';
     await action(page.locator('#answerCard .opt[data-a="'+wrong+'"]'),touch);
     await page.locator('#guideCard.show').waitFor({timeout:15000});
     assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
     assert.equal(await page.locator('#answerCard .opt.wrong').count(),1);
     assert.equal(await page.locator('#answerCard .option-detail').count(),4);
     for(const L of 'ABCD'){
      const actual=normalize(await page.locator('#answerCard .opt[data-a="'+L+'"] + .option-detail').innerText());
      for(const k of ['teacher','elementary','reason']){
       const expected=normalize(q.author.teaching.optionExplanations[L][k].replace(/反向檢查/g,'相反意思'));
       assert(actual.includes(expected),label+' lost author '+L+' '+k);
      }
     }
     const titles=page.locator('#guideCard .guide-block h3').filter({hasText:'考題計算式'});
     assert.equal(await titles.count(),1,label+' calculation card missing or duplicated');
     const rows=page.locator('#guideCard .calculation-step');
     assert.equal(await rows.count(),q.lines.length,label+' incomplete full calculation');
     for(let n=0;n<q.lines.length;n++){
      const actual=normalize(await rows.nth(n).innerText());
      assert(actual.includes(normalize(q.lines[n])),label+' dropped formula/verification line '+(n+1));
     }
     const guide=await page.locator('#guideCard').innerText();
     assert(guide.includes(q.author.teaching.memory),label+' memory missing');
     await layout(page,label+' after answer');
     const raster=await fontGate(page,label);
     const screenshot=q.id+'-'+width+'x'+height+'-'+theme+'.png';
     await page.screenshot({path:path.join(OUT,screenshot),fullPage:false,animations:'disabled'});
     report.cases.push({qid:q.id,width,height,theme,input:touch?'touch':'mouse',
       originalWebPSHA256:q.expected.image,questionRevision:q.expected.revision,
       exactAuthorTeachingDigest:q.expected.teaching,calcLines:q.lines.length,
       officialPublishedAnswer:q.expected.answer,screenshot,font:raster,
       result:'SOURCE_TRUE_STAGED_115_MATHB_V4_TECHNICAL_PASS_NOT_RELEASE'});
     if(i<source.length-1){
      await page.locator('#nextBtn').scrollIntoViewIfNeeded();await action(page.locator('#nextBtn'),touch);
     }
    }
    if(await page.locator('#navHandle').getAttribute('aria-expanded')!=='true')
      await action(page.locator('#navHandle'),touch);
    await action(page.locator('#reviewTop'),touch);
    await page.locator('#reviewView.show').waitFor({timeout:12000});
    assert.equal(await page.locator('#reviewList .wrong-card').count(),2,
     'two staged wrong questions missing from review');
    const local=await page.evaluate(()=>({
     annual:localStorage.getItem('tvet-verified-115-v1'),
     demo:localStorage.getItem('tvet-115-multisubject-demo-v1')
    }));
    assert(local.annual&&JSON.parse(local.annual).records);
    assert.equal(local.demo,demoBefore,'actual 35-Demo student state corrupted');
    assert.deepEqual(pageErrors,[],'uncaught browser JS failure');
   }catch(e){
    report.errors.push({width,height,theme,error:String(e.stack||e),pageErrors});
    try{await page.screenshot({path:path.join(OUT,'ERROR-'+width+'x'+height+'-'+theme+'.png')});}catch{}
   }finally{await ctx.close();save();}
  }
 }finally{await browser.close();for(const file of targetFiles)try{fs.unlinkSync(file)}catch{}}
 report.status=report.errors.length?'QA_ONLY_115_MB21_MB22_FAIL':'QA_ONLY_115_MB21_MB22_32_OF_32_PASS';save();
 if(report.errors.length)console.error('REAL_STAGED_MATHB_ERRORS',JSON.stringify(report.errors.slice(0,4),null,2));
 assert.equal(report.errors.length,0,'115 Math B21/22 staged source+author V4 UIQA errors remain');
 assert.equal(report.cases.length,32,'two authentic source MB21/22 × 8 viewports × 2 themes required');
 console.log('PASS 32/32 TRUE ORIGINAL 115 MB21/MB22 V4 TECHNICAL QA-ONLY; ACTUAL APPROVED=5, NEW READY/LIVE=0');
})().catch(e=>{report.status='QA_ONLY_115_MB21_MB22_FAIL';report.errors.push({fatal:String(e.stack||e)});
 save();console.error(e.stack||e);process.exitCode=1;});
