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
const source=path.resolve(process.env.SUDU_QA_SOURCE_CHECKOUT||'current-qa-source');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8777/sudu/';
const out=path.resolve(process.env.SUDU_TEST_OUTPUT||'test-results/preflight-128');
const numbers=[19,20,21,22,23,24,25];
const dims=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const folder=path.join(root,'sudu/teaching-drafts/preview-128-20261023');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const canonical=o=>Array.isArray(o)?o.map(canonical):o&&typeof o==='object'?
  Object.fromEntries(Object.keys(o).sort().map(k=>[k,canonical(o[k])])):o;
const shaObject=o=>sha(Buffer.from(JSON.stringify(canonical(o))));

const git=p=>cp.execFileSync('git',['rev-parse','HEAD'],{cwd:p,encoding:'utf8'}).trim();
if(process.env.SUDU_PREVIEW_ONLY!=='1')throw Error('NO RELEASE: SUDU_PREVIEW_ONLY=1 required');
const host=new URL(base);
if(host.protocol!=='http:'||!['localhost','127.0.0.1'].includes(host.hostname)||!host.pathname.endsWith('/sudu/'))
 throw Error('NO RELEASE: loopback /sudu/ is mandatory');
const mainSha=git(main),draftSha=git(root),sourceQaSha=git(source);
const approvedCorrectionCommit='aad909a726a201e2841b86b2c35634e5d5f4afe5';
assert.equal(sourceQaSha,approvedCorrectionCommit,'source text correction evidence must use the pinned audited commit');

assert(mainSha!==draftSha,'same checkout is not a cross-branch QA');
const progress=read(path.join(folder,'progress.json'));
const official=read(path.join(folder,'official-final-evidence-20261023.json')).questions;
const legacy=read(path.join(root,'sudu/data/years/115.json')).papers.find(p=>p.paper==='00-MB');
const correctionRoot=path.join(source,'sudu/data/processed/115/review-evidence');
const corrections=read(path.join(correctionRoot,'MATHB_20_25_IMAGE_TEXT_CORRECTIONS_20261024.json'));
assert.equal(corrections.items.length,6,'exact six text-corrected sources');
assert.equal(corrections.formalTextQaPass,false,'do not confuse AI visual transcription with admission');
const correctedById=new Map(corrections.items.map(item=>{
 const d=read(path.join(source,item.entry));
 assert.equal(d.questionId,item.qid);
 assert.equal(d.sourceWebpSha256,item.sourceWebpSha256);
 assert.equal(d.status.formalIndependentHumanTextQaPass,false,'not formally approved yet');
 assert.equal(d.status.studentReleaseApproved,false,'no extra student approvals');
 assert.equal(d.correctedText.options.length,4);
 return [item.qid,d];
}));
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
 // Never pass old OCR contamination or placeholder options to the browser.
 // Use the original-WebP-corrected question and A-D recorded on pinned QA branch.
 const correction=correctedById.get(id);
 const options=correction?correction.correctedText.options:candidate.options;
 assert.equal(correction?.sourceWebpSha256||record.imageSha256,record.imageSha256,id+' image SHA');
 const correctedQuestion=correction?.correctedText.question||candidate.question;
 if(correction){
  assert(!options.some(s=>/對照下方 WebP|【以下空白】|公告試題僅供參考|第8 頁/.test(s)),
    id+' must not re-introduce known OCR footer or placeholders');
  assert(!/[\ue000-\uf8ff]/.test(correctedQuestion+options.join('')),id+' has private-use PDF glyphs');
  assert.equal(correction.knownOfficialAnswer,official[id].officialAnswer,id+' official mapping');
 }
 const originalTable=correction?.correctedText.table;
 const question=originalTable?
  correctedQuestion+'\n表（二）\n'+originalTable.rows.map(row=>row.join('｜')).join('\n'):
  correctedQuestion;
 const calculationLines=[
  ...calc.givenConditions.map(s=>'已知條件：'+s),
  '公式用途：'+calc.formulaPurpose,
  '公式：'+calc.formula,
  ...calc.substitutionAndSteps.map(s=>s.formula+'；理由：'+s.why),
  '結果：'+calc.result+'；單位：'+calc.unit+'；正確選項：'+calc.matchingOption
 ];
 return {year:115,canonicalId:id,id:n,subject:'數學 B',topic:'QA Only：數學 B',
  question,
  image:record.image,imageSha256:record.imageSha256,options,
  _qaSourceSha256:shaObject({question,options,imageSha256:record.imageSha256}),
  _qaTeachingSha256:shaObject(t),
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
 mainSha,draftSha,sourceQaSha,sourceTextEvidenceCommit:approvedCorrectionCommit,
 pinnedImagesChecked:7,questionIds:fixtures.map(f=>f.canonicalId),
 actualReleaseApproved:false,formalContentUiQaGranted:false,
 browserOnlyApprovedJsonInterception:true,
 candidateAdapterSha256:sha(fs.readFileSync(path.join(root,'sudu/verified-questions-runtime.js'))),
 candidateAdapterInterception:true,
 browserInputModality:'REAL_TOUCH_UNDER_1024_AND_MOUSE_CLICK',
 mousePointerClickStability:'SEE_PER_CASE_RESULTS',
 touchActionability:'SEE_PER_CASE_RESULTS',

 originalImageCorrectedTextUsedInQAFor:[20,21,22,23,24,25],
 legacyCandidateNeverUsedForThoseSix:true,
 perQuestionSourceTeachingHashes:Object.fromEntries(fixtures.map(q=>[q.canonicalId,{sourceTextSha256:q._qaSourceSha256,teachingSha256:q._qaTeachingSha256,imageSha256:q.imageSha256}])),
 expectedViewportThemeCases:16,observations:[],errors:[]};
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of dims){
   for(const theme of ['light','dark']){
    const ctx=await browser.newContext({viewport:{width,height},hasTouch:width<1024,isMobile:width<768,reducedMotion:'reduce'});
    try{
     await ctx.route('**/verified-questions-runtime.js*',route=>route.fulfill({contentType:'text/javascript',body:fs.readFileSync(path.join(root,'sudu/verified-questions-runtime.js'),'utf8')}));
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
      assert((await page.locator('#questionCard').innerText()).includes(fixture.question.slice(0,12)),n+' actual corrected question displayed');
      for(const letter of 'ABCD'){
       const shown=await page.locator('#answerCard .opt[data-a="'+letter+'"]').innerText();
       assert(shown.includes(fixture.options[letter.charCodeAt(0)-65]),n+' actual source option '+letter+' displayed');
      }
      if(n===25)assert((await page.locator('#questionCard').innerText()).includes('√2'),'original sqrt(2) retained');
      if(n===23)assert((await page.locator('#questionCard').innerText()).includes('其中一人打八折'),'original table retained');
      if(n===22)assert((await page.locator('#questionCard').innerText()).includes('bô'),'Taiwanese source diacritic retained');
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
      if(n===25){
       const calculation=page.locator('#guideCard .guide-block.calculation-first');
       assert((await calculation.locator('mark.exam-highlight').count())>0,'real MB25 calculation highlights');
       assert(!(await calculation.innerText()).includes('**'),'no leaked calculation markup');
      }
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
        noHorizontalOverflow:true,inputModality:width<1024?'touch':'mouse',
        sourceTextSha256:fixture._qaSourceSha256,teachingSha256:fixture._qaTeachingSha256,
        originalWebpSha256:fixture.imageSha256,actualSourceText:true});
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
  console.log('PASS: 7 main V4 Math B actual source-text draft QA fixtures x 8 sizes x 2 themes (NO RELEASE)');
  console.log('MAIN='+mainSha+' DRAFT='+draftSha);
 }finally{await browser.close();}
})().catch(e=>{
 report.errors.push(String(e?.stack||e));
 fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(report,null,2));
 console.error('FAILED MAIN-V4 PREFLIGHT, no approvals granted',e);
 process.exitCode=1;
});
