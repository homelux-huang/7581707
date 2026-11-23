'use strict';
// ROLE D single-original 114 E12: QA-ONLY staged V4, never formal approval.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const crypto=require('node:crypto'),cp=require('node:child_process');
const {URL:NativeURL}=require('node:url'),{chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..'),A='_role_a_e12',B='_role_b_e12',ID='114-00-E-12';
const OUT=path.resolve('test-results/role-d-114-e12-exact-v4');
const SITE='http://127.0.0.1:8765/sudu/';
const AS='a25a6e43de1a8f8179d84cc2257998d3c4ad4f58';
const BS='57d969888c57fdcd2b16c933e92c7a2c9eebb3a5';
const REV='0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec';
const W='99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60';
const T='fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4';
const sizes=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const p=x=>path.resolve(ROOT,x),raw=x=>fs.readFileSync(p(x)),read=x=>JSON.parse(raw(x).toString('utf8'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const sort=x=>Array.isArray(x)?x.map(sort):(x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sort(x[k])])):x);
const digest=x=>sha(Buffer.from(JSON.stringify(sort(x)),'utf8'));
const head=x=>cp.execFileSync('git',['rev-parse','HEAD'],{cwd:p(x||'.'),encoding:'utf8'}).trim();
const branchSha=head();
assert.equal(process.env.SUDU_D_QA_ONLY,'1');
if(process.env.SUDU_D_EXPECT_SHA)assert.equal(branchSha,process.env.SUDU_D_EXPECT_SHA);
assert.equal(head(A),AS);assert.equal(head(B),BS);
const approved=read('sudu/data/approved/114.json');
assert.equal(approved.approvedCount,0);assert.deepEqual(approved.questions,[]);
const source=read(A+'/sudu/data/processed/114/questions.json').questions.find(x=>x.questionId===ID);
const manifest=read(A+'/sudu/data/processed/114/webp-manifest.json').items.find(x=>x.questionId===ID);
const official=read(A+'/sudu/data/processed/114/review-evidence/114-00-E-12-official-20261102.json');
const bpath=B+'/sudu/teaching-candidates/114-role-b-20261025-batch02/'+ID+'.json';
const b=read(bpath),batch=read(B+'/sudu/teaching-candidates/114-role-b-20261025-batch02/batch.json');
const breceipt=batch.items.find(x=>x.questionId===ID);
assert(source&&manifest&&official&&b&&breceipt);
assert.equal(source.answer,'C');
assert.equal(source.questionVerified,false);assert.equal(source.answerVerified,false);
assert.equal(official.publishedOfficialAnswer.answer,'C');
assert.equal(official.finalOfficialNoticeScope.q12ListedInOfficialCorrection,false);
assert.equal(official.handoff.ready,false);
assert.equal(manifest.sha256,W);assert.equal(manifest.qaStatus,'PASS');
assert.equal(sha(raw(A+'/'+manifest.output)),W);
assert.equal(b.question,source.question);assert.deepEqual(b.options,source.options);
assert.equal(b.source.questionRevision,REV);assert.equal(b.source.webpSha256,W);
assert.equal(b.composedTeachingSha256,T);assert.equal(breceipt.composedTeachingSha256,T);
assert.equal(breceipt.fileSha256,sha(raw(bpath)));
assert.equal(digest({question:source.question,options:source.options,singleQuestionWebpSha256:W}),REV);
assert.equal(digest({questionId:ID,sourceRevision:REV,webpSha256:W,teaching:b.teaching,enrichment:b.enrichment}),T);
assert.equal(b.teaching.hasExamCalculation,false);assert.equal(b.teaching.examCalculation,null);
assert.equal(b.review.formalReady,false);
const news=b.enrichment.newsExample;
assert(news.english&&news.chinese&&news.highlightActualForm);
assert(news.english.toLowerCase().includes(news.highlightActualForm.toLowerCase()));
const v=b.enrichment.englishVocabulary;
const e={
 '中文翻譯':v.map(x=>x.headword+'：'+x.meaningZh).join('\n'),
 '發音':v.map(x=>x.headword+' '+x.ipa).join('\n'),
 '同意相關單字':v.map(x=>x.headword+'（'+x.level+'）→ '+x.synonyms.join('、')).join('\n'),
 '反意相關單字':v.map(x=>x.headword+'（'+x.level+'）→ '+x.antonyms.join('、')).join('\n'),
 '新聞時事例句':news.english,
 '新聞時事中文翻譯':news.chinese,
 '詞彙用法':v.map(x=>x.usageNote).filter(Boolean).join('\n')
};
const q={id:12,canonicalId:ID,year:114,subject:'英文',topic:b.teaching.topic,
 question:source.question,options:source.options,answer:'C',memory:b.teaching.memory,
 concept:b.teaching.concept,extension:b.teaching.extension,formula:b.teaching.formula||'',
 teacherSummary:b.teaching.teacherSummary,elementarySummary:b.teaching.elementarySummary,
 optionExplanations:b.teaching.optionExplanations,sourceText:b.teaching.source,
 extra:e,highlights:[...new Set([...(b.enrichment.highlights||[]).map(x=>x.text),news.highlightActualForm])],
 examCalculation:null,image:'data/approved/webp/114/'+ID+'.webp',imageSha256:W,
 qaOnlySourceRevision:REV,qaOnlyTeachingDigest:T};
const payload={year:114,schemaVersion:1,approvedCount:1,questions:[q],
 QA_ONLY_UNPUBLISHABLE:true,realApproved114Count:0};
const report={role:'D',headSHA:branchSha,roleA:AS,roleB:BS,qid:ID,
 realApproved114Count:0,originalWebPSHA256:W,sourceRevision:REV,qaOnlyTeachingDigest:T,
 htmlSHA256:sha(raw('sudu/v4-115-multisubject-review-demo.html')),
 ciRun:process.env.GITHUB_RUN_ID||null,qaOnly:true,newReady:0,newLive:0,
 cases:[],errors:[],status:'STARTED'};
function save(){fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'114-E12-report.json'),JSON.stringify(report,null,2)+'\n');}
const originalDest=p('_site/sudu/'+q.image);
const norm=s=>String(s||'').replace(/\s+/g,'');
const act=(x,t)=>t?x.tap({timeout:15000}):x.click({timeout:15000});
(async()=>{
 fs.mkdirSync(path.dirname(originalDest),{recursive:true});
 fs.copyFileSync(p(A+'/'+manifest.output),originalDest);
 assert.equal(sha(fs.readFileSync(originalDest)),W);
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try {
  for(const [width,height] of sizes)for(const theme of ['light','dark']){
   const touch=width<=430,ctx=await browser.newContext({viewport:{width,height},hasTouch:touch,reducedMotion:'reduce'});
   const page=await ctx.newPage(),errors=[];page.on('pageerror',x=>errors.push(x.message));
   const label=ID+' '+width+'x'+height+' '+theme;
   try {
    await page.route('**/sudu/data/approved/114.json',route=>route.fulfill({
      status:200,contentType:'application/json; charset=utf-8',body:JSON.stringify(payload)}));
    await page.goto(SITE+'v4-115-multisubject-review-demo.html?year=114',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='114' &&
      !document.body.classList.contains('qa-image-mode'),null,{timeout:30000});
    await page.addStyleTag({content:'body::after{content:"QA ONLY NOT LIVE";position:fixed;bottom:0;right:0;z-index:99999;background:black;color:white;padding:4px;pointer-events:none}'});
    await page.locator('#homeSubjectSel').selectOption('英文');
    await page.locator('#studyView').waitFor({state:'visible'});
    if((await page.locator('html').getAttribute('data-theme'))!==theme)
      await act(page.locator('#themeBtn'),touch);
    assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
    assert.equal(await page.evaluate(()=>qnow()?.canonicalId),ID);
    assert.equal(await page.locator('#questionCard h1').textContent(),q.question);
    const opts=page.locator('#answerCard .opt');assert.equal(await opts.count(),4);
    for(let i=0;i<4;i++){
      assert.equal(await opts.nth(i).getAttribute('data-a'),'ABCD'[i]);
      assert.equal(norm(await opts.nth(i).locator('.opt-text').innerText()),norm(q.options[i]));
    }
    const image=page.locator('#questionCard img').first();
    await image.scrollIntoViewIfNeeded();
    await image.evaluate(async el=>el.decode());
    assert.equal(await image.getAttribute('src'),q.image);
    const webp=await page.request.get(new NativeURL('./'+q.image,SITE).href);
    assert(webp.ok());assert.equal(sha(await webp.body()),W);
    if(!touch){const before=await opts.first().evaluate(el=>getComputedStyle(el).backgroundColor);
      await opts.first().hover();await page.waitForTimeout(120);
      assert.notEqual(await opts.first().evaluate(el=>getComputedStyle(el).backgroundColor),before);}
    await act(page.locator('#answerCard .opt[data-a="A"]'),touch);
    await page.locator('#guideCard.show').waitFor({timeout:15000});
    assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
    assert.equal(await page.locator('#answerCard .opt.wrong').count(),1);
    assert.equal(await page.locator('#answerCard .option-detail').count(),4);
    assert.equal(await page.locator('#guideCard .calculation-step').count(),0);
    for(const L of 'ABCD'){
      const detail=norm(await page.locator('#answerCard .opt[data-a="'+L+'"] + .option-detail').innerText());
      for(const k of ['teacher','elementary','reason'])
       assert(detail.includes(norm(b.teaching.optionExplanations[L][k].replace(/反向檢查/g,'相反意思'))));
    }
    assert((await page.locator('#guideCard').innerText()).includes(b.teaching.memory));
    const box=await page.evaluate(()=>({width:innerWidth,doc:document.documentElement.scrollWidth}));
    assert(box.doc<=box.width+1,label+' horizontal overflow');
    const png=ID+'-'+width+'x'+height+'-'+theme+'.png';
    await page.screenshot({path:path.join(OUT,png),fullPage:false,animations:'disabled'});
    const zh=page.locator('#guideCard .news-zh');
    assert.equal(await zh.count(),1,label+' author Chinese news missing');
    assert((await zh.innerText()).includes(news.chinese),label+' news Chinese lost');
    const en=page.locator('#guideCard .news-en');
    assert.equal(await en.count(),1,label+' author English news missing');
    assert((await en.innerText()).includes(news.english),label+' news English overwritten');
    assert((await en.locator('mark.exam-highlight').allInnerTexts()).some(x=>x.toLowerCase()===news.highlightActualForm.toLowerCase()),
      label+' keyword highlight missing');
    assert.deepEqual(errors,[]);
    report.cases.push({width,height,theme,qid:ID,sourceRevision:REV,webpSha256:W,
      qaOnlyTeachingDigest:T,screenshot:png,result:'EXACT_AUTHOR_SOURCE_STAGED_QA_ONLY_PASS'});
   }catch(err){report.errors.push({width,height,theme,error:String(err.stack||err),browserErrors:errors});
     try{await page.screenshot({path:path.join(OUT,ID+'-'+width+'x'+height+'-'+theme+'-FAIL.png')});}catch{}
   }finally{await ctx.close();save();}
  }
 }finally{await browser.close();try{fs.unlinkSync(originalDest)}catch{}}
 report.status=report.errors.length?'E12_V4_QA_ONLY_FAIL':'E12_V4_QA_ONLY_16_OF_16_PASS';save();
 if(report.errors.length)console.error('E12_UIQA_DEFECT',JSON.stringify(report.errors.slice(0,3),null,2));
 assert.equal(report.errors.length,0,'E12 exact-source V4 QA-only has real UI defects');
 assert.equal(report.cases.length,16,'8 widths x light/dark mandatory');
 console.log('PASS 16/16 E12 QA-ONLY, NOT REAL PUBLISHER READY/LIVE');
})().catch(err=>{report.status='E12_V4_QA_ONLY_FAIL';report.errors.push({fatal:String(err.stack||err)});
 save();console.error(err.stack||err);process.exitCode=1;});
