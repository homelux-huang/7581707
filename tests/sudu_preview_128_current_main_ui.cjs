/* QA-ONLY: test current MAIN V4 with fixed-128 draft data in local Chromium.
 * This bypasses approved/115.json only within a browser route fixture. NEVER
 * release fixture data or treat this preflight as a real teaching UI certificate.
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const cp=require('node:child_process');
const crypto=require('node:crypto');
const {chromium}=require('playwright');

const root=path.resolve(__dirname,'..');
const main=path.resolve(process.env.SUDU_QA_MAIN_CHECKOUT||'current-main');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8777/sudu/';
const out=path.resolve(process.env.SUDU_TEST_OUTPUT||'test-results/preflight-128');
const numbers=[19,20,21,22,23,24,25];
const dims=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const folder=path.join(root,'sudu/teaching-drafts/preview-128-20261023');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const git=p=>cp.execFileSync('git',['rev-parse','HEAD'],{cwd:p,encoding:'utf8'}).trim();
if(process.env.SUDU_PREVIEW_ONLY!=='1')throw Error('NO RELEASE: SUDU_PREVIEW_ONLY=1 required');
const host=new URL(base);
if(host.protocol!=='http:'||!['localhost','127.0.0.1'].includes(host.hostname)||!host.pathname.endsWith('/sudu/'))
 throw Error('NO RELEASE: loopback /sudu/ is mandatory');
const mainSha=git(main),draftSha=git(root);
assert(mainSha!==draftSha,'same checkout is not a cross-branch QA');
const progress=read(path.join(folder,'progress.json'));
const official=read(path.join(folder,'official-final-evidence-20261023.json')).questions;
const legacy=read(path.join(root,'sudu/data/years/115.json')).papers.find(p=>p.paper==='00-MB');
assert(progress.scopeTotal===128&&progress.fullyAccepted===0&&progress.deployed===0);
const fixtures=numbers.map(n=>{
 const id='115-00-MB-'+String(n).padStart(2,'0');
 const record=read(path.join(folder,id+'.json')),t=record.teaching,calc=t.examCalculation;
 assert(record.questionId===id&&record.studentReleaseApproved===false&&record.deploy===false,id+' isolated');
 assert(record.qa.independentTeachingReview==='PENDING'&&record.qa.uiReview==='PENDING',id+' not formally QA');
 assert(record.answerComparison.officialAnswer===official[id].officialAnswer,id+' official key');
 for(const repoRoot of [main,root]){
  const image=path.join(repoRoot,'sudu',record.image);
  assert(fs.existsSync(image),id+' WebP exists');
  assert.equal(sha(fs.readFileSync(image)),record.imageSha256,id+' original WebP SHA');
 }
 assert(calc&&calc.substitutionAndSteps.length>0,id+' calculation exists');
 const candidate=legacy.questions.find(q=>q.id===id);
 assert(candidate&&candidate.options?.length===4);
 // Known legacy OCR/diagram contamination. Never inject these candidate fields
 // as correct student display; use clearly labeled placeholders in QA only.
 const options=[20,21,22,25].includes(n)?
  ['對照下方 WebP 的原始選項 A','對照下方 WebP 的原始選項 B','對照下方 WebP 的原始選項 C','對照下方 WebP 的原始選項 D']:
  candidate.options;
 const calculationLines=[
  ...calc.givenConditions.map(s=>'已知條件：'+s),
  '公式用途：'+calc.formulaPurpose,
  '公式：'+calc.formula,
  ...calc.substitutionAndSteps.map(s=>s.formula+'；理由：'+s.why),
  '結果：'+calc.result+'；單位：'+calc.unit+'；正確選項：'+calc.matchingOption
 ];
 return {year:115,canonicalId:id,id:n,subject:'數學 B',topic:'QA Only：數學 B',
  question:record.solution.questionAsReadFromOriginalImage||'題幹以既有 WebP 為準',
  image:record.image,imageSha256:record.imageSha256,options,
  answer:official[id].officialAnswer,memory:t.memory,concept:t.concept,
  extension:t.extension,formula:calc.formula,teacherSummary:t.teacherSummary,
  elementarySummary:t.elementarySummary,optionExplanations:t.optionExplanations,
  highlights:t.highlightTerms||[],
  extra:{'高職老師原理解說':t.teacherSummary,'國小學生白話解說':t.elementarySummary},
  examCalculation:{hasExamCalculation:true,lines:calculationLines},
  sourceText:'官方答案已核；實際彰化高商課本版本、章節、頁碼待核對'};
});
const dataset={schemaVersion:1,year:115,approvedCount:fixtures.length,questions:fixtures,
  QA_ONLY_UNPUBLISHABLE_FIXTURE:true,sourceDraftSha:draftSha};
const report={kind:'CROSS_BRANCH_MAIN_V4_DRAFT_PREFLIGHT_ONLY_NO_RELEASE',
 mainSha,draftSha,pinnedImagesChecked:7,questionIds:fixtures.map(f=>f.canonicalId),
 actualReleaseApproved:false,formalContentUiQaGranted:false,
 browserOnlyApprovedJsonInterception:true,
 browserInputModality:'REAL_TOUCH_UNDER_1024_AND_MOUSE_CLICK',
 mousePointerClickStability:'SEE_PER_CASE_RESULTS',
 touchActionability:'SEE_PER_CASE_RESULTS',

 legacyTextReplacementsOnlyInQaFixture:[20,21,22,25],
 expectedViewportThemeCases:16,observations:[],errors:[]};
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of dims){
   for(const theme of ['light','dark']){
    const ctx=await browser.newContext({viewport:{width,height},hasTouch:width<1024,isMobile:width<768,reducedMotion:'reduce'});
    try{
     await ctx.route('**/data/approved/115.json',route=>{
      if(!route.request().url().startsWith(base))throw Error('off-host fixture denied');
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(dataset),
       headers:{'Cache-Control':'no-store','X-Internal-Preview':'NO-RELEASE'}});
     });
     const page=await ctx.newPage(),pageErrors=[];
     const activate=async locator=>width<1024?locator.tap({timeout:10000}):locator.click({timeout:10000});
     page.on('pageerror',err=>pageErrors.push(err.message));
     await page.goto(base+'v4-115-multisubject-review-demo.html?year=115&subject='+encodeURIComponent('數學 B'),
       {waitUntil:'domcontentloaded',timeout:30000});
     await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='115',{timeout:30000});
     await page.evaluate(t=>{document.documentElement.dataset.theme=t;state.theme=t;},theme);
     const successes=[];
     for(const n of numbers){
      const fixture=fixtures.find(q=>q.id===n);
      await page.evaluate(num=>{
       currentSubject='數學 B';currentIndex=listFor(currentSubject).findIndex(q=>q.id===num);
       if(currentIndex<0)throw Error('missing math QA '+num);
       showStudy();renderAll();scrollTo(0,0);
      },n);
      assert.equal(Number((await page.locator('#questionCard .qnum').innerText()).trim()),n,'question ID');
      const img=page.locator('#questionCard .source-figure img');
      await img.waitFor({state:'visible'});
      const info=await img.evaluate(async el=>{await el.decode();return {src:el.getAttribute('src'),w:el.naturalWidth,h:el.naturalHeight}});
      assert(info.src.endsWith(fixture.canonicalId+'.webp')&&info.w>100&&info.h>40,'original WebP decoded');
      assert.equal(await page.locator('#answerCard .opt').count(),4,'4 options');
      assert.equal(await page.locator('#guideCard.show').count(),0,'hidden explanation before answer');
      const selected=n===19?'A':fixture.answer;
      // Actual pointer/touch input; never force or dispatch a synthetic DOM click.
      const answerButton=page.locator('#answerCard .opt[data-a="'+selected+'"]');
      await activate(answerButton);
      await page.locator('#correctAnswer').waitFor({state:'visible'});
      await page.locator('#guideCard.show').waitFor({state:'visible'});
      assert.equal(await page.locator('#guideCard .guide-block.calculation-first').count(),1,'exactly one math computation');
      assert.equal(await page.locator('.option-detail').count(),4,'explanation for 4 options');
      assert.equal(await page.locator('.option-detail.is-correct').count(),1,'one correct explanation');
      const reason=await page.locator('.option-detail.is-correct').innerText();
      assert(reason.includes('高職生理解')&&reason.includes('國小學生也聽得懂'),'two levels');
      const guide=await page.locator('#guideCard').innerText();
      assert(guide.includes('高職老師原理解說')&&guide.includes('國小學生白話解說'),'guide summaries');
      const widthCheck=await page.evaluate(()=>({client:innerWidth,scroll:document.documentElement.scrollWidth}));
      assert(widthCheck.scroll<=widthCheck.client+1,'no horizontal overflow '+JSON.stringify(widthCheck));
      if(n===19){
       assert.equal(await page.locator('#answerCard .opt.wrong').count(),1,'wrong answer shown');
       await activate(page.locator('#questionBtn'));
       assert.equal(await page.locator('#guideCard.show').count(),0,'hide explanation');
       await activate(page.locator('#explainBtn'));
       assert.equal(await page.locator('#guideCard.show').count(),1,'restore explanation');
      }
      successes.push({questionId:fixture.canonicalId,decoded:true,optionsExplained:4,mathStepsShown:true,
        noHorizontalOverflow:true,inputModality:width<1024?'touch':'mouse'});
     }
     await page.evaluate(()=>showReview());
     assert.equal(await page.locator('#reviewView.show').count(),1,'review UI');
     assert.equal(await page.locator('#studyView').isVisible(),false,'study selection hidden');
     assert((await page.locator('#reviewList').innerText()).includes('19'),'wrong question in review');
     assert.deepEqual(pageErrors,[],'page JavaScript errors');
     await page.screenshot({path:path.join(out,'current-main-'+width+'x'+height+'-'+theme+'.png')});
     report.observations.push({width,height,theme,questions:successes,reviewRendered:true,passed:true});
    }finally{await ctx.close();}
   }
  }
  fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(report,null,2));
  console.log('PASS: 7 current-main V4 Math B draft fixture questions x 8 viewport sizes x 2 themes (NO RELEASE)');
  console.log('MAIN='+mainSha+' DRAFT='+draftSha);
 }finally{await browser.close();}
})().catch(e=>{
 report.errors.push(String(e?.stack||e));
 fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(report,null,2));
 console.error('FAILED MAIN-V4 PREFLIGHT, no approvals granted',e);
 process.exitCode=1;
});
