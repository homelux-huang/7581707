'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),{chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..'),WORK=path.resolve(ROOT,'..'),MAIN=path.join(WORK,'current-main');
const source=JSON.parse(fs.readFileSync(path.join(ROOT,'sudu/data/processed/115/questions.json'),'utf8')).questions
 .find(x=>x.questionId==='115-09-2-34');
const payload=JSON.parse(fs.readFileSync(path.join(WORK,'econ34-stage/115.json'),'utf8'));
const info=JSON.parse(fs.readFileSync(path.join(WORK,'econ34-stage/input-digests.json'),'utf8'));
const q=payload.questions[0];const sum=b=>crypto.createHash('sha256').update(b).digest('hex');
assert(process.env.SUDU_PREVIEW_ONLY==='1'&&payload.QA_ONLY_UNPUBLISHABLE===true);
assert.equal(q.canonicalId,'115-09-2-34');assert.equal(q.answer,'A');
assert.equal(q.question,source.question);assert.deepEqual(q.options,source.options);
assert(q.question.includes('寡占市場中僅存在兩間廠商'));
assert.equal(q.imageSha256,info.originalWebpSha256);
assert.equal(sum(fs.readFileSync(path.join(MAIN,'sudu',q.image))),info.originalWebpSha256);
assert.equal(q.examCalculation,null,'noncomputational Econ34 MUST hide calculation');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8777/sudu/';
const url=new URL(base);assert(['127.0.0.1','localhost'].includes(url.hostname)&&url.pathname.endsWith('/sudu/'));
const dest=path.resolve(process.env.SUDU_TEST_OUTPUT||path.join(WORK,'econ34-ui-results'));
fs.mkdirSync(dest,{recursive:true});
const viewports=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const output={kind:'ECON34_CANONICAL_ORIGINAL_AND_TEACHING_ON_UNMODIFIED_MAIN_8x2',
 mainSha:info.mainV4Commit,sourceQaSha:info.sourceQaCommit,
 questionId:q.canonicalId,teachingSha256:info.teachingSha256,
 originalWebpSha256:q.imageSha256,expectedCases:16,cases:[],errors:[],
 studentApprovalGranted:false,productionDeployed:false};
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of viewports)for(const theme of ['light','dark']){
   const touch=width<1024;
   const ctx=await browser.newContext({viewport:{width,height},hasTouch:touch,
    isMobile:width<768,reducedMotion:'reduce'});
   const page=await ctx.newPage(),errors=[];
   page.on('pageerror',err=>errors.push(err.message));
   const activate=l=>touch?l.tap({timeout:15000}):l.click({timeout:15000});
   try{
    await page.route('**/data/approved/115.json',route=>{
     if(!route.request().url().startsWith(base))throw Error('unexpected fixture route');
     return route.fulfill({status:200,contentType:'application/json',
      body:JSON.stringify(payload),headers:{'X-QA-ONLY':'TRUE','Cache-Control':'no-store'}});
    });
    await page.goto(base+'v4-115-multisubject-review-demo.html?year=115&subject='+encodeURIComponent('經濟學'),
     {waitUntil:'domcontentloaded',timeout:30000});
    await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='115',{timeout:30000});
    await page.evaluate(t=>{document.documentElement.dataset.theme=t;state.theme=t;},theme);
    const card=await page.locator('#questionCard').innerText();
    assert(card.includes('人工智慧')&&card.includes('寡占市場'),'real question rendered');
    assert.equal((await page.locator('#questionCard .qnum').innerText()).trim().padStart(2,'0'),'34');
    const image=page.locator('#questionCard .source-figure img');
    const dims=await image.evaluate(async e=>{await e.decode();return {w:e.naturalWidth,h:e.naturalHeight,
      src:e.getAttribute('src')}});
    assert(dims.w>=100&&dims.h>=50&&dims.src.endsWith('115-09-2-34.webp'),'real WebP');
    assert.equal(await page.locator('#answerCard .opt').count(),4);
    for(const [n,k] of ['A','B','C','D'].entries()){
     const actual=await page.locator('#answerCard .opt[data-a="'+k+'"]').innerText();
     assert(actual.includes(q.options[n]),'exact original option '+k);
    }
    assert.equal(await page.locator('#guideCard.show').count(),0,'answer-only release');
    await activate(page.locator('#answerCard .opt[data-a="B"]'));
    await page.locator('#guideCard.show').waitFor();
    assert.equal(await page.locator('#answerCard .opt.wrong').count(),1);
    assert.equal(await page.locator('.option-detail').count(),4);
    assert.equal(await page.locator('.option-detail.is-correct').count(),1);
    const correct=await page.locator('.option-detail.is-correct').innerText();
    assert(correct.includes('高職生理解')&&correct.includes('國小學生也聽得懂'));
    for(const choice of ['A','B','C','D']){
      const t=await page.locator('.option-detail').nth(choice.charCodeAt(0)-65).innerText();
      assert(t.includes('此選項正確／錯誤原因'),'all 4 why explanations '+choice);
    }
    assert.equal(await page.locator('#guideCard .guide-block.calculation-first').count(),0,
     'Econ conceptual question must not invent exam calculation');
    const guide=await page.locator('#guideCard').innerText();
    assert(!guide.includes('考題計算式')&&guide.includes('解題判斷步驟'),'nonmath reasoning not fake math');
    assert(!guide.includes('**'),'no leaked raw markdown');
    await activate(page.locator('#questionBtn'));
    assert.equal(await page.locator('#guideCard.show').count(),0);
    await activate(page.locator('#explainBtn'));
    await page.locator('#guideCard.show').waitFor();
    await activate(page.locator('#navHandle'));
    assert.equal(await page.locator('#navHandle').getAttribute('aria-expanded'),'true');
    await activate(page.locator('#reviewTop'));
    await page.locator('#reviewView.show').waitFor();
    assert((await page.locator('#reviewList').innerText()).includes('正確答案 A'),'wrong answer review');
    await activate(page.locator('#reviewList .goto'));
    await activate(page.locator('#answerCard .opt[data-a="A"]'));
    assert.equal(await page.locator('#answerCard .opt.correct').count(),1,'correct retry');
    const overflow=await page.evaluate(()=>({inner:innerWidth,scroll:document.documentElement.scrollWidth}));
    assert(overflow.scroll<=overflow.inner+1,'no viewport overflow '+JSON.stringify(overflow));
    assert.deepEqual(errors,[],'no JS exceptions');
    await page.screenshot({path:path.join(dest,width+'x'+height+'-'+theme+'.png'),fullPage:true});
    output.cases.push({width,height,theme,input:touch?'touch':'mouse',passed:true,
      originalImage:true,fourRealOptions:true,workedConcept:true,calculationHidden:true,
      wrongReviewCorrectRetry:true,teachingSha256:info.teachingSha256});
   }catch(e){
    output.errors.push(e.stack||String(e));
    await page.screenshot({path:path.join(dest,'FAILED-'+width+'-'+theme+'.png'),fullPage:true});
    throw e;
   }finally{await ctx.close()}
  }
  assert.equal(output.cases.length,16);
  console.log('PASS ECON34: authentic original WebP and question, 4 explained options, nonmath calculation hidden, conceptual steps, wrong review, correct retry, 8x2, no approval or deployment');
 }finally{await browser.close()}
})().catch(err=>{console.error(err);process.exitCode=1}).finally(()=>{
 fs.writeFileSync(path.join(dest,'econ34-ui-results.json'),JSON.stringify(output,null,2));
});
