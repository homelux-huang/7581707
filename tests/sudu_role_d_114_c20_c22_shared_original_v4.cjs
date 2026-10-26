'use strict';
/* Role D: authentic archived original 114 Chinese C20-C22 single WebP PLUS
 * complete original shared source article rendered in EXISTING seven-subject
 * V4, not another website. QA_ONLY Playwright intercept; NO READY/RELEASE.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const cp=require('node:child_process');
const {URL:NativeURL}=require('node:url');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const BASE=process.env.SUDU_D_BASE_URL||'http://127.0.0.1:8765/sudu/';
const OUT=path.resolve(process.env.SUDU_D_OUT||'test-results/role-d-114-c20-22-shared-v4');
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const QIDS=['114-00-C-20','114-00-C-21','114-00-C-22'];
const SHARED_ID='114-00-C-SHARED-20-23';
const AUTHOR_SHA='4e8b3065d7f1b0e71eba0928a6f5fe002ea25852';
const SOURCE_SHA='9944759e339ef2d3c002042798f7fe696d861d96';
const sharedSHA='7b7f592f01378a6fa9ece08d87291810420479c9529f2d5233f10ad458c47f8a';
const expectRevision=[
 'c31503c4314d5d1ad6686edeb45991ae602275013e6cae4555b65f4d3c1edc09',
 '79b10bd19d9ccbd74994844610babf6ffc1a5f6212cf923391f09710026bce9e',
 'b78a3e7f300621fa64217d420476c195fa6a3f44050a344dbf2eb20292c1aea1'
];
const expectImages=[
 '13ceb4e57baa428cfa09a59e381b84d7f3bf114d6ff60fe1df20f0fe527ae19c',
 '290d7b3a11395cbe05e2fb1f86fa47986b3c03fc1dde44d97b0baef7e405e975',
 'b795e87aabd5b3d3ea07b32afc7ebc51a983afaa72351fe1eebaace49772482b'
];
const expectDigests=[
 'd28e20c96d6156b67560cdf4379cc3479bd0f880fc60c71154b2610d02a64d62',
 'fe12bead7cfa8eb701504980b7393b7b9e71d1f77b54e0ee0657e718117384aa',
 '8ab9eeb1b8d522111a67cf52d952d1d2a505233de1ca498d0222b42096d554d6'
];
const SHA=b=>crypto.createHash('sha256').update(b).digest('hex');
const BLOB=b=>crypto.createHash('sha1').update(Buffer.concat([
 Buffer.from('blob '+b.length),Buffer.from([0]),b])).digest('hex');
const ordered=x=>Array.isArray(x)?x.map(ordered):
 x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,ordered(x[k])])):x;
const canonical=x=>SHA(Buffer.from(JSON.stringify(ordered(x)),'utf8'));
const abs=p=>path.join(ROOT,p);
const bytes=p=>fs.readFileSync(abs(p));
const read=p=>JSON.parse(bytes(p).toString('utf8'));
const fileSHA=p=>SHA(bytes(p));
const HEAD=cp.execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim();
const git=dir=>cp.execFileSync('git',['-C',abs(dir),'rev-parse','HEAD'],{encoding:'utf8'}).trim();
assert.equal(process.env.SUDU_D_QA_ONLY,'1','original reading stage NEVER becomes publisher approval');
if(process.env.SUDU_D_EXPECT_SHA)assert.equal(HEAD,process.env.SUDU_D_EXPECT_SHA);
const BR=process.env.SUDU_D_B_CHECKOUT||'_role_b_chinese20';
const AR=process.env.SUDU_D_A_CHECKOUT||'_role_a_chineseoriginal';
assert.equal(git(BR),AUTHOR_SHA,'Role B original C20–22 real SHA moved');
assert.equal(git(AR),SOURCE_SHA,'Role A original C20–22 real SHA moved');
const source=read('sudu/data/processed/114/questions.json');
const manifest=read('sudu/data/processed/114/webp-manifest.json');
const batch=read(BR+'/sudu/teaching-candidates/114-role-b-20261025-batch05/batch.json');
const qa=read(AR+'/sudu/data/processed/114/qa-drafts/DIRECT_VISUAL_114_C19_23_SHARED_20261023.json');
assert.equal(source.questions.length,205);
assert.equal(batch.itemCount,3);
assert.equal(batch.newReady,0);
assert.equal(batch.newMain,0);
assert.equal(batch.newLive,0);
assert.deepEqual(batch.items.map(x=>x.questionId),QIDS);
assert(batch.excludedQuarantinedIds.includes('114-00-C-23'));
assert.equal(qa.releaseAllowed,false);
const shared=source.sharedMaterials.find(x=>x.sharedMaterialId===SHARED_ID);
assert(shared,'original shared 20–23 not present');
assert.equal(shared.qaStatus,'PASS');
assert.equal(shared.sha256,sharedSHA);
assert.equal(batch.sharedMaterialWebpSha256,sharedSHA);
assert.equal(fileSHA(AR+'/'+shared.output),sharedSHA,'actual original article bytes changed');
assert.equal(BLOB(bytes(AR+'/'+shared.output)),batch.sharedArticleOriginalGitBlob);
assert.equal(fileSHA(AR+'/'+shared.source),shared.sourceSha256,'original paper page 7 bytes mismatch');
assert.equal(shared.sourceSha256,qa.sharedMaterial.sourcePageWebpSha256);
assert.equal(qa.sharedMaterial.outputSha256,sharedSHA);
assert.equal(qa.sharedMaterial.result,'PASS_DIRECT_ORIGINAL_PAGE_SHARED_ARTICLE_VISUAL');
assert.deepEqual(qa.sharedMaterial.questionIds,QIDS.concat('114-00-C-23'));
assert.equal(qa.sharedMaterial.integrationReady,false);
const destRoot='data/approved/webp/114/';
const sharedUrl=destRoot+SHARED_ID+'.webp';
const real=QIDS.map((id,i)=>{
 const q=source.questions.find(x=>x.questionId===id);
 const m=manifest.items.find(x=>x.questionId===id);
 const row=batch.items.find(x=>x.questionId===id);
 const bpath=BR+'/sudu/teaching-candidates/114-role-b-20261025-batch05/'+id+'.json';
 const raw=bytes(bpath),b=JSON.parse(raw);
 const proof=qa.items.find(x=>x.questionId===id);
 assert(q&&m&&row&&b&&proof,'missing actual source/img/QA/B author '+id);
 assert.equal(BLOB(bytes(AR+'/'+m.output)).length,40);
 assert.equal(SHA(raw),row.fileSha256);
 assert.equal(m.qaStatus,'PASS');
 assert.equal(m.sha256,expectImages[i]);
 assert.equal(m.sha256,q.questionProvenance.webpSha256);
 assert.equal(m.sha256,proof.reviewedWebpSha256);
 assert.equal(proof.result,'PASS_DIRECT_ORIGINAL_PAGE_IMAGE');
 assert.deepEqual(proof.cropSourcePixelBounds,m.crop);
 assert.equal(proof.sourcePageWebpSha256,m.sourceSha256);
 assert.deepEqual(q.sharedMaterialIds,[SHARED_ID]);
 assert.equal(fileSHA(AR+'/'+m.output),expectImages[i],'original single question image changed');
 assert.equal(b.questionId,id);assert.equal(b.kind,'NEW_AUTHOR_DRAFT');
 assert.equal(b.review?.formalReady,false);
 assert.equal(b.review?.studentReleaseApproved,false);
 assert.equal(q.answerVerified,false);
 assert.equal(q.questionVerified,false);
 assert.equal(q.answer,b.knownAnswerCandidate);
 assert.equal(row.answerCandidate,q.answer);
 assert.equal(q.question,b.question);
 assert.deepEqual(q.options,b.options);
 const rev=canonical({question:q.question,options:q.options,singleQuestionWebpSha256:m.sha256});
 assert.equal(rev,expectRevision[i]);
 assert.equal(rev,b.source.questionRevision);
 assert.equal(rev,row.sourceRevision);
 assert.equal(m.sourcePdfSha256,b.source.originalQuestionPdfSha256);
 assert.equal(m.sha256,b.source.webpSha256);
 assert.equal(b.source.sharedMaterialId,SHARED_ID);
 assert.equal(b.source.sharedMaterialWebpSha256,sharedSHA);
 assert.equal(b.enrichment.sharedReading.webpSha256,sharedSHA);
 const t=b.teaching;
 assert.equal(t.hasExamCalculation,false,'no fictional formula on Chinese literary reading');
 assert.equal(t.examCalculation,null);
 assert(t.solvingSteps.length>=3);
 assert(t.teacherSummary&&t.elementarySummary&&t.memory&&t.concept);
 for(const L of 'ABCD'){
  const r=t.optionExplanations[L];
  assert(r?.teacher?.trim()&&r?.elementary?.trim()&&r?.reason?.trim());
  assert.equal(r.isCorrect,L===q.answer);
 }
 assert.equal(canonical(t),row.teachingCanonicalSha256);
 const digest=canonical({questionId:id,sourceRevision:rev,webpSha256:m.sha256,teaching:t,enrichment:b.enrichment});
 assert.equal(digest,expectDigests[i]);
 assert.equal(digest,b.composedTeachingSha256);
 assert.equal(digest,row.composedTeachingSha256);
 const entries=(b.enrichment.chineseVocabulary||[]).map(x=>x.term+'（'+x.level+'）：'+x.meaning+' '+(x.usageNote||''));
 const extra={'國文重點詞語':entries.join('\n'),'原文閱讀線索':(b.enrichment.readingFacts||[]).join('\n')};
 // QA-only projection of exact A+B original files: NOT an actual approved file.
 const publicQuestion={
  id:q.originalQuestionNumber,canonicalId:id,year:114,subject:'國文',
  question:q.question,options:q.options,answer:q.answer,topic:t.topic,
  teacherSummary:t.teacherSummary,elementarySummary:t.elementarySummary,
  memory:t.memory,concept:t.concept,extension:t.extension,sourceText:t.source,
  optionExplanations:t.optionExplanations,formula:'',
  examCalculation:null,highlights:b.enrichment.highlights.map(x=>x.text),
  extra,image:destRoot+id+'.webp',imageSha256:m.sha256,
  sharedImages:[{sharedMaterialId:SHARED_ID,image:sharedUrl,sha256:sharedSHA}],
  qaOnlySourceRevision:rev,qaOnlyComposedTeachingSha256:digest
 };
 return {id,q,m,b,t,digest,revision:rev,publicQuestion,originalPath:AR+'/'+m.output};
});
const payload={schemaVersion:1,year:114,approvedCount:3,
 questions:real.map(x=>x.publicQuestion),QA_ONLY_UNPUBLISHABLE:true,
 studentReleaseApproved:false,actualApproved114:0};
const report={
 taskId:'D-114-C20-22-SHARED-ORIGINAL-V4-20261026-04',role:'D',
 reportClass:'SOURCE_ORIGINAL_SHARED_YEARLY_V4_RENDERER_QA_ONLY_NOT_ADMITTED',
 gitHead:HEAD,authorHead:AUTHOR_SHA,originalSourceHead:SOURCE_SHA,
 sourceBankGitBlob:'074bff8cbb9ca7bbc0aefd8580454892d21f7d6b',
 manifestGitBlob:'249a41d5a64558ccaa3084b21f915922a55c6a1b',
 sourceBankSHA:fileSHA('sudu/data/processed/114/questions.json'),
 manifestSHA:fileSHA('sudu/data/processed/114/webp-manifest.json'),
 sourcePixelQASha:fileSHA(AR+'/sudu/data/processed/114/qa-drafts/DIRECT_VISUAL_114_C19_23_SHARED_20261023.json'),
 HTML_SHA:fileSHA('sudu/v4-115-multisubject-review-demo.html'),
 runtime_SHA:fileSHA('sudu/verified-questions-runtime.js'),
 actualSharedOriginalSha:sharedSHA,
 individualRealSources:real.map(x=>({
  id:x.id,questionRevision:x.revision,WebPSha256:x.m.sha256,
  sharedMaterialId:SHARED_ID,sharedWebPSha256:sharedSHA,
  authorComposedTeachingSha256:x.digest,answerCandidate:x.q.answer,
  officialAnswerVerified:false,questionVerified:false
 })),
 ciRun:process.env.GITHUB_RUN_ID||null,
 noResponseAdmittedPublisher:true,unpublished114QAOnly:true,newReady:0,newLive:0,
 cases:[],negatives:[],errors:[],status:'STARTED'
};
function save(){
 fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'114-chinese20-22-shared-V4.json'),
  JSON.stringify(report,null,2)+'\n');
}
const created=[];
function stage(src,out){
 const dest=abs('_site/sudu/'+out);
 fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.copyFileSync(abs(src),dest);
 assert.equal(fileSHA('_site/sudu/'+out),fileSHA(src));
 created.push(dest);
}
for(const x of real)stage(x.originalPath,x.publicQuestion.image);
stage(AR+'/'+shared.output,sharedUrl);
const act=(loc,touch)=>touch?loc.tap({timeout:13000}):loc.click({timeout:13000});
const noWhitespace=x=>String(x).replace(/\s+/g,'');
async function layout(page,id){
 const k=await page.evaluate(()=>{
  const overflow=[...document.querySelectorAll('#questionCard h1,#questionCard img,#answerCard .opt-text,#guideCard .guide-block p')].
   filter(e=>e.offsetWidth>0&&e.scrollWidth>e.clientWidth+3&&['hidden','clip'].includes(getComputedStyle(e).overflowX)).
   map(e=>({text:e.textContent?.slice(0,50),scroll:e.scrollWidth,client:e.clientWidth}));
  return {width:innerWidth,docWidth:document.documentElement.scrollWidth,overflow};
 });
 assert(k.docWidth<=k.width+1,id+' horizontal overflow '+JSON.stringify(k));
 assert.deepEqual(k.overflow,[],id+' clipped original story/choices');
}
async function fontRaster(page,id){
 const r=await page.evaluate(async()=>{
  await document.fonts.ready;
  const el=document.querySelector('#guideCard');
  const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
  ctx.canvas.width=80;ctx.canvas.height=80;
  ctx.fillStyle='#000';ctx.textBaseline='top';ctx.font='48px '+getComputedStyle(el).fontFamily;
  return ['虎','貓','擒','讀'].map(letter=>{
   ctx.clearRect(0,0,80,80);ctx.fillText(letter,4,4);
   const arr=ctx.getImageData(0,0,80,80).data;
   let n=0,v=2166136261;
   for(let i=3;i<arr.length;i+=4){if(arr[i]>32)n++;v=Math.imul(v^arr[i],16777619)>>>0}
   return {letter,pixels:n,hash:v.toString(16)};
  });
 });
 assert(r.every(x=>x.pixels>75)&&new Set(r.map(x=>x.hash)).size>=3,
  id+' CJK missing/tofu glyph '+JSON.stringify(r));
 return r;
}
async function assertImage(page,locator,expectedSha,expectedSrc,label){
 assert.equal(await locator.getAttribute('src'),expectedSrc,label+' wrong original asset routing');
 await locator.scrollIntoViewIfNeeded();
 const shape=await locator.evaluate(async el=>{
  await el.decode();const a=el.getBoundingClientRect(),p=el.parentElement.getBoundingClientRect();
  return{naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,width:a.width,height:a.height,parent:p.width};
 });
 assert(shape.naturalWidth>0&&shape.naturalHeight>0&&shape.width>0&&shape.height>0);
 assert(shape.width<=shape.parent+1,label+' image clipped or too wide');
 assert(Math.abs(shape.width/shape.height-shape.naturalWidth/shape.naturalHeight)/(shape.naturalWidth/shape.naturalHeight)<0.03,
  label+' original pixel image aspect altered');
 const response=await page.request.get(new NativeURL('./'+expectedSrc,BASE).href);
 assert(response.ok(),label+' image HTTP '+response.status());
 assert.equal(SHA(await response.body()),expectedSha,label+' original SHA incorrect');
}
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of SIZES)for(const theme of ['light','dark']){
   const touch=width<=430;
   const context=await browser.newContext({viewport:{width,height},hasTouch:touch,reducedMotion:'reduce',locale:'zh-TW'});
   const page=await context.newPage();
   const jsErrors=[];page.on('pageerror',e=>jsErrors.push(e.message));
   try{
    await page.route('**/sudu/data/approved/114.json',route=>
      route.fulfill({status:200,contentType:'application/json; charset=utf-8',body:JSON.stringify(payload)}));
    await page.goto(BASE+'v4-115-multisubject-review-demo.html?year=114',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='114',null,{timeout:30000});
    await page.addStyleTag({content:
      'body::after{content:"ROLE D QA-ONLY / NOT OFFICIAL ADMISSION / NOT LIVE";position:fixed;bottom:3px;right:3px;'+
      'background:#861f19;color:#fff;font:bold 10px sans-serif;padding:3px 5px;z-index:100000;pointer-events:none}'});
    const demoOriginal=await page.evaluate(()=>localStorage.getItem('tvet-115-multisubject-demo-v1'));
    await page.locator('#homeSubjectSel').selectOption('國文');
    await page.locator('#studyView').waitFor({state:'visible'});
    if(theme==='dark')await act(page.locator('#themeBtn'),touch);
    assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
    for(let i=0;i<real.length;i++){
     const x=real[i],q=x.publicQuestion,label=x.id+' '+width+'x'+height+' '+theme;
     const dom=await page.evaluate(()=>({
      id:qnow()?.canonicalId,question:qnow()?.question,options:qnow()?.options,
      shared:qnow()?.sharedImages,sourceRev:qnow()?.qaOnlySourceRevision,
      digest:qnow()?.qaOnlyComposedTeachingSha256,answer:qnow()?.answer
     }));
     assert.equal(dom.id,x.id);
     assert.equal(dom.question,q.question);
     assert.deepEqual(dom.options,q.options);
     assert.equal(dom.answer,q.answer);
     assert.deepEqual(dom.shared,q.sharedImages);
     assert.equal(dom.sourceRev,x.revision);
     assert.equal(dom.digest,x.digest);
     assert.equal(await page.locator('#questionCard h1').textContent(),q.question);
     const choices=page.locator('#answerCard .opt');
     assert.equal(await choices.count(),4);
     for(let k=0;k<4;k++){
      assert.equal(await choices.nth(k).getAttribute('data-a'),'ABCD'[k]);
      assert.equal(noWhitespace(await choices.nth(k).locator('.opt-text').innerText()),noWhitespace(q.options[k]));
     }
     // The official single Q WebP and its real unredrawn shared ARTICLE are
     // two distinct correct images beneath the SAME official question.
     const single=page.locator('#questionCard figure[data-single-question-webp="true"] img');
     const figures=page.locator('#questionCard figure[data-shared-material-webp="true"]');
     assert.equal(await single.count(),1,label+' missing single question original');
     assert.equal(await figures.count(),1,label+' shared article omitted or duplicated');
     assert.equal(await figures.getAttribute('data-shared-material-id'),SHARED_ID);
     assert.equal(await figures.getAttribute('data-image-sha256'),sharedSHA);
     assert((await figures.innerText()).includes(SHARED_ID));
     assert.equal(await page.locator('#answerCard img').count(),0,'shared original inserted among answer buttons');
     await assertImage(page,single,x.m.sha256,q.image,label+' single');
     await assertImage(page,figures.locator('img'),sharedSHA,sharedUrl,label+' shared');
     await layout(page,label+' before answer');
     if(!touch){
      await choices.first().scrollIntoViewIfNeeded();
      const before=await choices.first().evaluate(e=>getComputedStyle(e).backgroundColor);
      await choices.first().hover();await page.waitForTimeout(150);
      const after=await choices.first().evaluate(e=>getComputedStyle(e).backgroundColor);
      assert.notEqual(before,after,label+' hover not working');
     }
     const wrong=q.answer==='A'?'B':'A';
     await act(page.locator('#answerCard .opt[data-a="'+wrong+'"]'),touch);
     await page.locator('#guideCard.show').waitFor({timeout:15000});
     assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
     assert.equal(await page.locator('#answerCard .opt.wrong').count(),1);
     assert.equal(await page.locator('#answerCard .option-detail').count(),4);
     for(const L of 'ABCD'){
      const actual=noWhitespace(await page.locator('#answerCard .opt[data-a="'+L+'"] + .option-detail').innerText());
      for(const key of ['teacher','elementary','reason']){
       const authored=noWhitespace(q.optionExplanations[L][key].replace(/反向檢查/g,'相反意思'));
       assert(actual.includes(authored),label+' missing Chinese authored '+L+'/'+key);
      }
     }
     assert.equal(await page.locator('#guideCard .calculation-step').count(),0,
       label+' original Chinese reading must not have numeric calculation');
     assert.equal(await page.locator('#guideCard .guide-block h3').filter({hasText:'考題計算式'}).count(),0);
     const guide=await page.locator('#guideCard').innerText();
     // Authoritative V4 guideEntries keeps high-school/elementary A-D under
     // the four answer explanations, never duplicates those paragraphs in
     // the singular subject guide. Check the SAME full education content
     // in its actual intended location, not a deprecated duplicate card.
     assert(guide.includes(q.memory)&&guide.includes(q.concept),
       label+' original Chinese mnemonic/concept guide lost');
     assert(!guide.includes(q.teacherSummary)&&!guide.includes(q.elementarySummary),
       label+' duplicate full high-school/child summaries were reintroduced into guide');
     const optionDetails=await page.locator('#answerCard .option-detail').allInnerTexts();
     assert.equal(optionDetails.length,4);
     for(const detailText of optionDetails){
       assert(detailText.includes('高職生理解')&&detailText.includes('國小學生也聽得懂'),
         label+' original four-option two-level educational explanation labels lost');
     }
     const font=await fontRaster(page,label);
     await layout(page,label+' after answer');
     const filename=x.id+'-'+width+'x'+height+'-'+theme+'.png';
     await page.screenshot({path:path.join(OUT,filename),fullPage:false,animations:'disabled'});
     report.cases.push({qid:x.id,width,height,theme,input:touch?'touch':'mouse',imageSHA:x.m.sha256,
      sharedOriginalWebpSHA:sharedSHA,composedTeachingSHA:x.digest,actualQuestionRevision:x.revision,
      exactTwoOriginalImagesDecodedAndHTTPVerified:true,allRealFourOptionExplanations:true,
      noCalculation:true,cjk:font,screenshot:filename,status:'QA_ONLY_SHARED_ARTICLE_REAL_V4_PASS_NOT_RELEASE'});
     if(i<real.length-1)await act(page.locator('#nextBtn'),touch);
    }
    if(await page.locator('#navHandle').getAttribute('aria-expanded')!=='true')
      await act(page.locator('#navHandle'),touch);
    await act(page.locator('#reviewTop'),touch);
    await page.locator('#reviewView.show').waitFor({timeout:15000});
    assert.equal(await page.locator('#reviewList .wrong-card').count(),3);
    const history=await page.evaluate(()=>({
      annual:localStorage.getItem('tvet-verified-114-v1'),
      demo:localStorage.getItem('tvet-115-multisubject-demo-v1'),
      demoSeed:!!document.getElementById('seedDemo')
    }));
    assert(history.annual&&JSON.parse(history.annual).records);
    assert.equal(history.demo,demoOriginal,'cross-year student history corrupted');
    assert.equal(history.demoSeed,false,'formal annual Chinese review must never seed artificial Demo mistakes');
    assert.deepEqual(jsErrors,[],'real Chrome exception');
   }catch(e){
    report.errors.push({width,height,theme,error:String(e.stack||e),pageErrors:jsErrors});
   }finally{await context.close();save();}
  }
  // Negative route tampering is NOT a fixture for a release PASS.
  for(const [tag,bad] of [
   ['foreign_year',{...payload.questions[0].sharedImages[0],image:'data/approved/webp/115/'+SHARED_ID+'.webp'}],
   ['foreign_range',{...payload.questions[0].sharedImages[0],sharedMaterialId:'114-00-C-SHARED-21-22',image:destRoot+'114-00-C-SHARED-21-22.webp'}],
   ['malformed_sha',{...payload.questions[0].sharedImages[0],sha256:'0'}],
   ['missing_material_id',{...payload.questions[0].sharedImages[0],sharedMaterialId:null}]
  ]){
    const tampered=structuredClone(payload);tampered.questions[0].sharedImages=[bad];
    const ctx=await browser.newContext({viewport:{width:390,height:844},locale:'zh-TW'});
    const page=await ctx.newPage();
    try{
     await page.route('**/sudu/data/approved/114.json',r=>r.fulfill({status:200,contentType:'application/json',body:JSON.stringify(tampered)}));
     await page.goto(BASE+'v4-115-multisubject-review-demo.html?year=114',{waitUntil:'domcontentloaded'});
     await page.waitForFunction(()=>document.body.classList.contains('qa-error-mode'),null,{timeout:15000});
     assert.equal(await page.locator('#answerCard .opt').count(),0,
       tag+' untrusted neighboring shared material became playable');
     assert.equal(await page.locator('#studyView').isVisible(),false);
     report.negatives.push({case:tag,rejected:true,classification:'ONLY_NEGATIVE_MALFORMED_SOURCE_INTERCEPT_NO_UIQA'});
    }catch(e){report.errors.push({negative:tag,error:String(e.stack||e)});}
    finally{await ctx.close();}
  }
 }finally{
  await browser.close();
  for(const dest of created)try{fs.unlinkSync(dest)}catch{}
 }
 report.status=report.errors.length?'FAIL_ORIGINAL_SHARED_V4':'QA_ONLY_SHARED_ORIGINAL_V4_PASS_NOT_READY';
 save();
 if(report.errors.length)console.error('ORIGINAL_SHARED_REAL_BROWSER_FAILURE',JSON.stringify(report.errors.slice(0,6),null,2));
 assert.equal(report.errors.length,0,'original source shared article/4 answers V4 browser gate failed');
 assert.equal(report.cases.length,48,'must test 3 real Chinese questions x 8 viewports x 2 themes');
 assert.equal(report.negatives.length,4,'negative annual shared guards not tested');
 console.log('PASS ROLE D QA-ONLY 114 C20/C21/C22 original article single+shared real V4 48/48 + 4 negative; NOT READY/LIVE');
})().catch(error=>{
 report.status='FAIL_ORIGINAL_SHARED_V4';report.errors.push({fatal:String(error.stack||error)});
 save();console.error(error.stack||error);process.exitCode=1;
});
