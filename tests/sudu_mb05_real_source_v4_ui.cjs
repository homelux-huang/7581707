'use strict';
// NO RELEASE. Test actual MB05 source and formal-publisher mapped teaching on main V4.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),{chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),workspace=path.resolve(root,'..');
const main=path.join(workspace,'current-main'),qa=path.join(workspace,'current-qa-source');
const payload=JSON.parse(fs.readFileSync(path.join(workspace,'mb05-stage/115.json'),'utf8'));
const note=JSON.parse(fs.readFileSync(path.join(workspace,'mb05-stage/input-digests.json'),'utf8'));
const source=JSON.parse(fs.readFileSync(path.join(qa,'sudu/data/processed/115/questions.json'),'utf8')).questions
 .find(x=>x.questionId==='115-00-MB-05');
const question=payload.questions[0];
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
assert(process.env.SUDU_PREVIEW_ONLY==='1','NO RELEASE expected');
assert(payload.QA_ONLY_UNPUBLISHABLE===true&&payload.approvedCount===1);
assert(note.sourceAdmissionYetApproved===false&&note.teachingStudentReleaseApproved===false);
assert.deepEqual(question.options,source.options,'exact canonical options, no test substitutes');
assert.equal(question.question,source.question,'exact canonical question, no test substitutes');
assert.equal(question.answer,source.answer);
assert.equal(question.imageSha256,note.originalWebpSha256);
assert.equal(hash(fs.readFileSync(path.join(main,'sudu',question.image))),note.originalWebpSha256);
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8777/sudu/';
const parsed=new URL(base);
assert(['127.0.0.1','localhost'].includes(parsed.hostname)&&parsed.pathname.endsWith('/sudu/'));
const dest=path.resolve(process.env.SUDU_TEST_OUTPUT||path.join(workspace,'mb05-ui-test-results'));
fs.mkdirSync(dest,{recursive:true});
const sizes=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const report={kind:'MB05_REAL_CANONICAL_SOURCE_MAIN_V4_UI_PREFLIGHT_NOT_RELEASE',
 source:note,questionId:question.canonicalId,actualMainAdapterUnmodified:true,
 expectedRwdCases:16,observations:[],errors:[],approvalGranted:false,deployed:false};
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of sizes)for(const theme of ['light','dark']){
   const ctx=await browser.newContext({viewport:{width,height},hasTouch:width<1024,isMobile:width<768,reducedMotion:'reduce'});
   const page=await ctx.newPage();const errors=[];
   const touch=width<1024;
   const activate=loc=>touch?loc.tap({timeout:15000}):loc.click({timeout:15000});
   page.on('pageerror',err=>errors.push(err.message));
   try{
    await ctx.route('**/data/approved/115.json',r=>{
      if(!r.request().url().startsWith(base))throw Error('unexpected host');
      return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify(payload),
       headers:{'Cache-Control':'no-store','X-Internal-QA-Only':'TRUE'}});
    });
    await page.goto(base+'v4-115-multisubject-review-demo.html?year=115&subject='+encodeURIComponent('數學 B'),
      {waitUntil:'domcontentloaded',timeout:30000});
    await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='115',{timeout:30000});
    await page.evaluate(t=>{document.documentElement.dataset.theme=t;state.theme=t;},theme);
    const found=await page.locator('#questionCard .qnum').innerText();
    assert.equal(found.trim().padStart(2,'0'),'05','actual question 05');
    const original=await page.locator('#questionCard').innerText();
    assert(original.includes('平行四邊形')&&original.includes('中點坐標'),'original text render');
    const img=page.locator('#questionCard .source-figure img');
    const dims=await img.evaluate(async e=>{await e.decode();return {w:e.naturalWidth,h:e.naturalHeight,src:e.getAttribute('src')}});
    assert(dims.src.endsWith('115-00-MB-05.webp')&&dims.w>100&&dims.h>40,'exact source WebP');
    assert.equal(await page.locator('#answerCard .opt').count(),4);
    for(const [ix,letter] of ['A','B','C','D'].entries()){
      const shown=await page.locator('#answerCard .opt[data-a="'+letter+'"]').innerText();
      assert(shown.includes(question.options[ix]),'actual option '+letter);
    }
    assert.equal(await page.locator('#guideCard.show').count(),0,'guide hidden until answering');
    await activate(page.locator('#answerCard .opt[data-a="A"]'));
    await page.locator('#guideCard.show').waitFor();
    assert.equal(await page.locator('#answerCard .opt.wrong').count(),1,'wrong answer recorded');
    assert.equal(await page.locator('.option-detail').count(),4);
    assert.equal(await page.locator('.option-detail.is-correct').count(),1);
    assert.equal(await page.locator('#guideCard .guide-block.calculation-first').count(),1,'worked steps once');
    const correctDetail=await page.locator('.option-detail.is-correct').innerText();
    assert(correctDetail.includes('高職生理解')&&correctDetail.includes('國小學生也聽得懂'),
      'dual-level explanations must be visible in the actual main correct-answer component');
    const guide=await page.locator('#guideCard').innerText();
    assert(guide.includes('3/2')&&guide.includes('7/2'),'actual computation');
    assert(!guide.includes('**'),'no raw markdown leak');
    await activate(page.locator('#questionBtn'));
    assert.equal(await page.locator('#guideCard.show').count(),0,'guide dismiss');
    await activate(page.locator('#explainBtn'));
    await page.locator('#guideCard.show').waitFor();
    await activate(page.locator('#navHandle'));
    assert.equal(await page.locator('#navHandle').getAttribute('aria-expanded'),'true');
    await activate(page.locator('#reviewTop'));
    await page.locator('#reviewView.show').waitFor();
    assert((await page.locator('#reviewList').innerText()).includes('正確答案 B'),'wrong question review');
    assert.equal(await page.locator('#studyView').isVisible(),false);
    await activate(page.locator('#reviewList .goto'));
    await activate(page.locator('#answerCard .opt[data-a="B"]'));
    assert.equal(await page.locator('#answerCard .opt.correct').count(),1,'correct retry');
    const overflow=await page.evaluate(()=>({inner:innerWidth,scroll:document.documentElement.scrollWidth}));
    assert(overflow.scroll<=overflow.inner+1,'RWD overflow '+JSON.stringify(overflow));
    assert.deepEqual(errors,[],'script exceptions');
    await page.screenshot({path:path.join(dest,width+'x'+height+'-'+theme+'.png'),fullPage:true});
    report.observations.push({width,height,theme,passed:true,input:touch?'touch':'mouse',
      singleWebpDecoded:true,realAnswerOptions:4,wrongReview:true,correctRetry:true,
      workedMathVisibleOnce:true,teachingDigestSha256:note.teachingSha256,
      canonicalSourceRevisionSha256:note.canonicalSourceRevisionSha256});
   }catch(e){
    report.errors.push(String(e.stack||e));
    await page.screenshot({path:path.join(dest,'FAIL-'+width+'-'+theme+'.png'),fullPage:true});
    throw e;
   }finally{await ctx.close()}
  }
  console.log('PASS: real MB05 canonical question + publisher-mapped teaching on unmodified main adapter, 8x2 RWD and touch/click, WRONG_REVIEW and CORRECT_RETRY, NO RELEASE');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>{
 fs.writeFileSync(path.join(dest,'mb05-ui-results.json'),JSON.stringify(report,null,2));
});
