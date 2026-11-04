'use strict';
/* Role D exact-publisher 115 Math B REAL already-approved five E2E UI.
 * NO interception, NO fixture, NO change to published status, NO NEW READY.
 * This test relies on the actual existing sudu/data/approved/115.json and
 * actual original WebP files served by scripts/build.py after publisher check.
 */
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs');
const path=require('node:path');
const cp=require('node:child_process');
const {URL:NativeURL}=require('node:url');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const SITE=process.env.SUDU_D_REAL_BASE_URL||'http://127.0.0.1:8765/sudu/';
const OUT=path.resolve(process.env.SUDU_D_REAL_OUT||'test-results/role-d-114-115-current-main');
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const IDS=['115-00-MB-02','115-00-MB-03','115-00-MB-04','115-00-MB-05','115-00-MB-09'];
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
const gitBlob=b=>crypto.createHash('sha1').update(Buffer.concat([
 Buffer.from('blob '+b.length),Buffer.from([0]),b])).digest('hex');
const abs=p=>path.join(ROOT,p);
const file=p=>fs.readFileSync(abs(p));
const hash=p=>SHA(file(p));
const sha=cp.execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim();
if(process.env.SUDU_D_EXPECT_SHA)assert.equal(sha,process.env.SUDU_D_EXPECT_SHA,'exact-head CI or source changed');
const raw=file('sudu/data/approved/115.json');
const ORIGINAL_APPROVED_BLOB='51e7b4e73e2d46b4c8b1672c6af20477cc90d44e';
assert.equal(gitBlob(raw),ORIGINAL_APPROVED_BLOB,'the five original 115 published rows changed; redo admission/evidence');
// Actual CURRENT main admission boundary: 114 has zero playable questions.
const raw114=file('sudu/data/approved/114.json');
const APPROVED_114_BLOB='874e47c72134b79778741d0c28a4f5c638e7626d';
assert.equal(gitBlob(raw114),APPROVED_114_BLOB,'114 approved source changed: stop, re-audit admission');
const approved114=JSON.parse(raw114.toString('utf8'));
assert.equal(approved114.year,114);
assert.equal(approved114.approvedCount,0,'114 not authorized for graded practice');
assert.deepEqual(approved114.questions,[],'114 now has new admissions: requires fresh E/D proof');
const preview114=JSON.parse(file('sudu/data/approved/preview/114.json').toString('utf8'));
assert.equal(preview114.year,114);
assert.equal(preview114.imagePreviewCount,9);
assert.equal(preview114.questions.length,9);
const payload=JSON.parse(raw.toString('utf8'));
assert.equal(payload.year,115);
assert.equal(payload.approvedCount,5);
assert.equal(payload.questions.length,5);
assert.equal(payload.sourceSha,'16d04a0d642fb433de289417a22c3050aa3e52b6');
assert.deepEqual(payload.questions.map(q=>q.canonicalId),IDS,
  'original five historical published QIDs modified');
const answers=['A','A','C','B','A'];
for(let i=0;i<payload.questions.length;i++){
 const q=payload.questions[i],id=IDS[i];
 assert.equal(q.canonicalId,id);
 assert.equal(q.year,115);
 assert.equal(q.subject,'數學 B');
 assert.equal(q.answer,answers[i],'historical original published answer changed');
 assert(q.question&&q.topic&&q.memory&&q.teacherSummary&&q.elementarySummary&&q.sourceText);
 assert(Array.isArray(q.options)&&q.options.length===4&&q.options.every(x=>typeof x==='string'&&x.trim()));
 assert.deepEqual(Object.keys(q.optionExplanations).sort(),['A','B','C','D']);
 for(const L of 'ABCD')for(const f of ['teacher','elementary','reason'])
  assert(q.optionExplanations[L][f]?.trim().length>5,id+' missing '+L+' '+f);
 assert(q.examCalculation?.hasExamCalculation===true,
  id+' actual original 115 worked maths must be TRUE');
 assert(q.examCalculation.lines?.length>=6&&q.examCalculation.lines.every(x=>typeof x==='string'&&x.trim()),
  id+' full real multi-step math no longer present');
 assert.equal(q.image,'data/approved/webp/115/'+id+'.webp');
 assert(/^[a-f0-9]{64}$/.test(q.imageSha256),'original verified image SHA missing');
}
const report={
 schemaVersion:1,role:'D',
 taskId:'D-114-115-CURRENT-MAIN-APPROVED-REGRESSION-20261103-01',
 classification:'CURRENT_MAIN_LEGACY_FIVE_115_AND_114_IMAGE_ONLY_NO_RELEASE',
 originalApprovedBeforeTest:5,newReady:0,newLive:0,noFixture:true,noResponseInterception:true,
 headSha:sha,ciRun:process.env.GITHUB_RUN_ID||null,
 approved114GitBlob:APPROVED_114_BLOB,approved114SHA256:SHA(raw114),
 approved114Count:0,preview114ImageOnly:preview114.imagePreviewCount,
 approved115GitBlob:ORIGINAL_APPROVED_BLOB,
 legacyQuestionRowsSHA256:SHA(Buffer.from(JSON.stringify(payload.questions),'utf8')),
 approved115SHA256:SHA(raw),officialAlreadyPublishedSourceSha:payload.sourceSha,
 htmlSha256:hash('sudu/v4-115-multisubject-review-demo.html'),
 runtimeSha256:hash('sudu/verified-questions-runtime.js'),
 originalApprovedRows:payload.questions.map(q=>({
  canonicalId:q.canonicalId,answer:q.answer,imageSha256:q.imageSha256,
  workSteps:q.examCalculation.lines.length,legacyContentSha256:SHA(Buffer.from(JSON.stringify(q),'utf8'))
 })),
 cases:[],readOnly114Cases:[],errors:[],status:'STARTED'
};
function save(){
 fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'exact-main-114-115-v4-results.json'),
  JSON.stringify(report,null,2)+'\n');
}
const action=(loc,touch)=>touch?loc.tap({timeout:15000}):loc.click({timeout:15000});
const normalize=s=>String(s).replace(/\s+/g,'');
async function cjkRaster(page,label){
 const result=await page.evaluate(async()=>{
  await document.fonts.ready;
  const e=document.getElementById('guideCard');
  const css=getComputedStyle(e).fontFamily;
  const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
  ctx.canvas.width=80;ctx.canvas.height=80;ctx.font='48px '+css;
  ctx.textBaseline='top';ctx.fillStyle='#000';
  return ['國','文','學','數'].map(c=>{
   ctx.clearRect(0,0,80,80);ctx.fillText(c,3,3);
   const data=ctx.getImageData(0,0,80,80).data;
   let hit=0,h=2166136261;
   for(let i=3;i<data.length;i+=4){
    if(data[i]>32)hit++;
    h=Math.imul(h^data[i],16777619)>>>0;
   }
   return {char:c,pixels:hit,fingerprint:h.toString(16)};
  });
 });
 assert(result.every(x=>x.pixels>70)&&new Set(result.map(x=>x.fingerprint)).size>=3,
   label+' real CJK glyphs are tofu / missing '+JSON.stringify(result));
 return result;
}
async function layout(page,label){
 const r=await page.evaluate(()=>{
  const els=[...document.querySelectorAll('#questionCard h1,#answerCard .opt-text,#guideCard .calculation-step')];
  const clipped=els.filter(e=>e.offsetWidth>0&&e.scrollWidth>e.clientWidth+3&&
    ['hidden','clip'].includes(getComputedStyle(e).overflowX)).
    map(e=>({txt:e.innerText?.slice(0,65),scroll:e.scrollWidth,client:e.clientWidth}));
  return {scroll:document.documentElement.scrollWidth,width:innerWidth,clipped};
 });
 assert(r.scroll<=r.width+1,label+' horizontal page overflow '+JSON.stringify(r));
 assert.deepEqual(r.clipped,[],label+' clipped source math/option/formula');
 return r;
}
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of SIZES)for(const theme of ['light','dark']){
   const touch=width<=430;
   const context=await browser.newContext({
    viewport:{width,height},hasTouch:touch,locale:'zh-TW',reducedMotion:'reduce'
   });
   const page=await context.newPage();
   const browserErrors=[];
   page.on('pageerror',e=>browserErrors.push(e.message));
   try{
    const response=await page.goto(SITE+'v4-115-multisubject-review-demo.html?year=115',
      {waitUntil:'domcontentloaded'});
    assert(response.ok(),'V4 official HTML not available');
    await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='115',
      null,{timeout:30000});
    assert(await page.locator('#homeView').isVisible());
    assert.equal(await page.locator('#studyView').isVisible(),false);
    assert.equal(await page.locator('#homeYearSel').inputValue(),'115');
    const liveHTTP=await page.request.get(new NativeURL('data/approved/115.json',SITE).href);
    assert(liveHTTP.ok());
    assert.equal(SHA(await liveHTTP.body()),SHA(raw),
      'real HTTP published 115 original five rows changed during current V4 CI');
    const demoOriginal=await page.evaluate(()=>localStorage.getItem('tvet-115-multisubject-demo-v1'));
    await page.locator('#homeSubjectSel').selectOption('數學 B');
    await page.locator('#studyView').waitFor({state:'visible',timeout:15000});
    if(theme==='dark')await action(page.locator('#themeBtn'),touch);
    assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
    for(let index=0;index<5;index++){
     const q=payload.questions[index],id=IDS[index],label=id+' '+width+'x'+height+' '+theme;
     const browserData=await page.evaluate(()=>({
      id:qnow()?.canonicalId,question:qnow()?.question,
      options:qnow()?.options,answer:qnow()?.answer,
      formula:qnow()?.formula,calc:qnow()?.examCalculation,
      explain:qnow()?.optionExplanations,image:qnow()?.image
     }));
     assert.equal(browserData.id,id,label+' user current question wrong');
     assert.equal(browserData.question,q.question,label+' changed original math statement');
     assert.deepEqual(browserData.options,q.options);
     assert.equal(browserData.answer,q.answer);
     assert.deepEqual(browserData.calc,q.examCalculation);
     assert.deepEqual(browserData.explain,q.optionExplanations);
     assert.equal((await page.locator('#questionCard h1').textContent()),q.question);
     const opts=page.locator('#answerCard .opt');
     assert.equal(await opts.count(),4);
     for(let k=0;k<4;k++){
      assert.equal(await opts.nth(k).getAttribute('data-a'),'ABCD'[k]);
      assert.equal(normalize(await opts.nth(k).locator('.opt-text').innerText()),
       normalize(q.options[k]),label+' original A-D mismatch');
     }
     const img=page.locator('#questionCard img').first();
     assert.equal(await img.getAttribute('src'),q.image);
     await img.scrollIntoViewIfNeeded();
     const box=await img.evaluate(async el=>{
      await el.decode();const b=el.getBoundingClientRect(),p=el.parentElement.getBoundingClientRect();
      return {w:b.width,h:b.height,nw:el.naturalWidth,nh:el.naturalHeight,parent:p.width};
     });
     assert(box.nw>0&&box.nh>0&&box.w>0&&box.h>0);
     assert(box.w<=box.parent+1,label+' original source single WebP overflows');
     assert(Math.abs(box.w/box.h-box.nw/box.nh)/(box.nw/box.nh)<0.025,
       label+' original WebP distorted');
     const imResp=await page.request.get(new NativeURL('./'+q.image,SITE).href);
     assert(imResp.ok(),label+' HTTP original WebP missing');
     assert.equal(SHA(await imResp.body()),q.imageSha256,
       label+' original verified single-question WebP byte has changed');
     await layout(page,label+' before answer');
     if(!touch){
      await opts.first().scrollIntoViewIfNeeded();
      const c0=await opts.first().evaluate(e=>getComputedStyle(e).backgroundColor);
      await opts.first().hover();await page.waitForTimeout(130);
      const c1=await opts.first().evaluate(e=>getComputedStyle(e).backgroundColor);
      assert.notEqual(c0,c1,label+' real mouse hover no response');
     }
     const wrong=q.answer==='A'?'B':'A';
     await action(page.locator('#answerCard .opt[data-a="'+wrong+'"]'),touch);
     await page.locator('#guideCard.show').waitFor({timeout:15000});
     assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
     assert.equal(await page.locator('#answerCard .opt.wrong').count(),1);
     assert.equal(await page.locator('#answerCard .option-detail').count(),4);
     assert.equal(await page.locator('#answerCard #correctAnswer').count(),1);
     for(const L of 'ABCD'){
      const text=normalize(await page.locator('#answerCard .opt[data-a="'+L+'"] + .option-detail').innerText());
      for(const key of ['teacher','elementary','reason']){
       const authored=normalize(q.optionExplanations[L][key].replace(/反向檢查/g,'相反意思'));
       assert(text.includes(authored),label+' lost actual '+L+' '+key);
      }
     }
     const calcTitle=page.locator('#guideCard .guide-block h3').filter({hasText:'考題計算式'});
     assert.equal(await calcTitle.count(),1,
       label+' expected ONE full exam calculation guide, no duplicate/missing');
     const actualLines=page.locator('#guideCard .calculation-step');
     assert.equal(await actualLines.count(),q.examCalculation.lines.length,
       label+' calculation line count incomplete');
     for(let n=0;n<q.examCalculation.lines.length;n++){
      const line=normalize(await actualLines.nth(n).innerText());
      assert(line.includes(normalize(q.examCalculation.lines[n])),
       label+' lost entire calculation step '+(n+1));
     }
     const steps=await page.locator('#guideCard .calculation-step').allInnerTexts();
     assert(steps.some(x=>x.includes('公式用途'))&&steps.some(x=>x.includes('代入'))&&
       steps.some(x=>x.includes('結果'))&&steps.some(x=>x.includes('對應選項')),
       label+' incomplete meaning/use/substitution/result/check of Maths steps');
     assert((await page.locator('#guideCard').innerText()).includes(q.memory),
       label+' original memory mnemonic missing');
     await layout(page,label+' after answer');
     const font=await cjkRaster(page,label);
     const imageName=id+'-'+width+'x'+height+'-'+theme+'.png';
     await page.screenshot({path:path.join(OUT,imageName),fullPage:false,animations:'disabled'});
     report.cases.push({
      id,width,height,theme,input:touch?'real_touch':'real_mouse',
      originalImageSha256:q.imageSha256,approvedJsonSha256:SHA(raw),
      officialApprovedBefore:5,fullCalculationSteps:q.examCalculation.lines.length,
      completedAllAuthoredSteps:true,realAnswerAndFourDualLevelExplanations:true,
      originalImageHTTPDecoded:true,wrongReviewStorageIsolated:true,
      CJKFontSample:font,screenshot:imageName,
      result:'CURRENT_MAIN_LEGACY_ALREADY_APPROVED_115_8X2_REGRESSION_PASS'
     });
     if(index<4){
      await page.locator('#nextBtn').scrollIntoViewIfNeeded();
      await action(page.locator('#nextBtn'),touch);
     }
    }
    if(await page.locator('#navHandle').getAttribute('aria-expanded')!=='true')
      await action(page.locator('#navHandle'),touch);
    await action(page.locator('#reviewTop'),touch);
    await page.locator('#reviewView.show').waitFor({timeout:15000});
    assert.equal(await page.locator('#reviewList .wrong-card').count(),5,
      'existing original 115 five wrong Math B questions missing in wrong review');
    const history=await page.evaluate(()=>({
      annual:localStorage.getItem('tvet-verified-115-v1'),
      demo:localStorage.getItem('tvet-115-multisubject-demo-v1'),
      demoSeed:!!document.querySelector('#seedDemo')
    }));
    assert(history.annual&&JSON.parse(history.annual).records);
    assert.equal(history.demo,demoOriginal,'actual 115 student math practice mutated 35 Demo history');
    assert.equal(history.demoSeed,false,'true formal approved 115 wrong review shows fake Demo sample');
    // 114 has NO formally approved lessons. Its original image previews must
    // remain read-only at EVERY size/theme, with zero A-D controls or scoring.
    const qa114=await context.newPage();
    try {
      const resp114=await qa114.goto(SITE+'v4-115-multisubject-review-demo.html?year=114',
        {waitUntil:'domcontentloaded'});
      assert(resp114.ok(), '114 original V4 route unavailable');
      await qa114.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='114' &&
        document.body.classList.contains('qa-image-mode'),null,{timeout:30000});
      const live114=await qa114.request.get(new NativeURL('data/approved/114.json',SITE).href);
      assert(live114.ok());
      assert.equal(SHA(await live114.body()),SHA(raw114), '114 approved changed via HTTP');
      assert.equal(await qa114.locator('#homeYearSel').inputValue(),'114');
      assert.equal(await qa114.locator('#homeSubjectSel option[value="國文"]').count(),1);
      await qa114.locator('#homeSubjectSel').selectOption('國文');
      await qa114.locator('#questionCard[data-qa-preview="read-only"]').waitFor({state:'visible',timeout:15000});
      const first=preview114.questions[0];
      assert.equal(await qa114.locator('#questionCard').getAttribute('data-canonical-id'),first.canonicalId);
      assert.equal(await qa114.locator('#answerCard .opt').count(),0);
      assert.equal(await qa114.locator('#answerCard #correctAnswer').count(),0);
      assert.equal(await qa114.locator('#guideCard .calculation-step').count(),0);
      assert.equal(await qa114.locator('#answerCard').isVisible(),false);
      assert.equal(await qa114.locator('#guideCard').isVisible(),false);
      const qaImg=qa114.locator('#questionCard img[data-canonical-id]').first();
      await qaImg.scrollIntoViewIfNeeded();
      await qaImg.evaluate(el=>el.decode());
      assert.equal(await qaImg.getAttribute('data-canonical-id'),first.canonicalId);
      assert.equal(await qaImg.getAttribute('data-sha256'),first.imageSha256);
      const qaImgResp=await qa114.request.get(new NativeURL('./'+first.image,SITE).href);
      assert(qaImgResp.ok());
      assert.equal(SHA(await qaImgResp.body()),first.imageSha256);
      if((await qa114.locator('html').getAttribute('data-theme'))!==theme){
        await action(qa114.locator('#themeBtn'),touch);
      }
      assert.equal(await qa114.locator('html').getAttribute('data-theme'),theme);
      await layout(qa114,'114 read-only '+width+'x'+height+' '+theme);
      assert.equal(await qa114.evaluate(()=>localStorage.getItem('tvet-verified-114-v1')),null,
        '114 image-only visitor accidentally created scored-year student records');
      const png114='114-IMAGE-ONLY-'+width+'x'+height+'-'+theme+'.png';
      await qa114.screenshot({path:path.join(OUT,png114),fullPage:false,animations:'disabled'});
      report.readOnly114Cases.push({year:114,width,height,theme,approvedCount:0,
        previewCanonicalId:first.canonicalId,originalWebpSHA256:first.imageSha256,
        screenshot:png114,result:'READ_ONLY_NO_ANSWER_NO_SCORE_PASS'});
    } finally { await qa114.close() }
    assert.deepEqual(browserErrors,[],'uncaught browser pageerror');
   }catch(e){
    report.errors.push({width,height,theme,error:String(e.stack||e),pageErrors:browserErrors});
   }finally{await context.close();save()}
  }
 }finally{await browser.close()}
 report.status=report.errors.length?'CURRENT_MAIN_114_115_UIQA_FAIL':'CURRENT_MAIN_115_FIVE_8X2_AND_114_READONLY_PASS';
 save();
 if(report.errors.length)console.error('FIRST_PROVEN_REAL_FAILURES',JSON.stringify(report.errors.slice(0,4),null,2));
 assert.equal(report.errors.length,0,'actual already approved 115 real V4 browser regression failed');
 assert.equal(report.cases.length,80,'five original Math B × 8 viewports × 2 themes required');
 assert.equal(report.readOnly114Cases.length,16,'114 read-only original WebP must pass 8x2');
 console.log('PASS 80/80 CURRENT MAIN 115 five real MathB + 16/16 114 no-score preview; NEW READY=0/LIVE=0');
})().catch(e=>{
 report.status='REAL_115_REGRESSION_FAIL';report.errors.push({fatal:String(e.stack||e)});
 save();console.error(e.stack||e);process.exitCode=1;
});
