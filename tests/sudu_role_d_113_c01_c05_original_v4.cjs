'use strict';
/* Role D: real 113 Chinese C01-C05 original A-source + B-author exact SHA.
 * This is an UNPUBLISHABLE playwright-only annual HTTP intercept, NOT approved
 * JSON, NOT a trusted E receipt, NOT READY, NOT LIVE. No placeholder fixture.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const cp=require('node:child_process');
const {URL:NativeURL}=require('node:url');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const SRCROOT=process.env.SUDU_D_SOURCE_CHECKOUT||'_source113';
const BASE=process.env.SUDU_D_BASE_URL||'http://127.0.0.1:8765/sudu/';
const OUT=path.resolve(process.env.SUDU_D_OUT||'test-results/role-d-113-c01-c05-original-v4');
const AUTHOR_HEAD='5e8765ef512e05b551df8c3240b2c8fcfc4db920';
const SOURCE_HEAD='481734d51928c8e47303718034479feafdf7e45e';
const QIDS=['113-00-C-01','113-00-C-02','113-00-C-03','113-00-C-04','113-00-C-05'];
const EXPECT=[
 ['0d979723a0cfd9f689c135ae84a9e198522d66ddc5ab4d1a5e7221310ba9ed47','7530812fb36120a00f1df784da804cb85e8c7cdd03c6eb78fcf886d95625d784','786cd98331c46b07719087522148805975fc32aa199aaf9fdfed80d42afc0c8d','C'],
 ['9f61ff0935d744867ee63ea100e39a8202d63ae540f13a046cbacf68b03c4971','4504646281047509ea1bd88b68271e79ef3c44f89893ea8331cfd7f2e3e6c73a','fb547ce5485ffe8ffeed26548f368e10072336d8f8b04c3606371a52915ffacd','D'],
 ['ecad096df5d194a1a98e78dbd0ca5130bd27fbd47d24b7316d0b0caa79b68261','ef5244f376272eaf43718c33cac84e3585eaa23a3411e11e024fe627536adf79','0fd8672536e756ba9116a0c41c64f313ab3c09b1a7183e73dcc9cf011b71312e','D'],
 ['65819ce90089f3b1113b4182ed213e6286a1c99b51a849beaa16c0ea6bd70e61','f548f0e5cdfbc3c669dd5ea161128ba5b277a83ed58ef0d044d61c64f5e4c13a','a4bbbc6f31c17aa05e06d32eeb17564944f609716657ef6c1378a6aafb90051e','C'],
 ['232ee18447551bd6e8c7b46ad4d4984a9ec766881bf8e224aed2d16ca3ae399f','ff1f548bead9b1850688f99b74e1946e2a2e0f5f1c83b299b5002801a51e9cd3','0ce0363ca2cd1d5b2812afa1e42340bb09db07162d1b75c82b85533cbe60314a','D']
];
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const SHA=b=>crypto.createHash('sha256').update(b).digest('hex');
const gitBlob=b=>crypto.createHash('sha1').update(Buffer.concat([Buffer.from('blob '+b.length),Buffer.from([0]),b])).digest('hex');
const stable=x=>Array.isArray(x)?x.map(stable):x&&typeof x==='object'?
 Object.fromEntries(Object.keys(x).sort().map(k=>[k,stable(x[k])])):x;
const canonical=x=>SHA(Buffer.from(JSON.stringify(stable(x)),'utf8'));
const absolute=p=>path.join(ROOT,p);
const bytes=p=>fs.readFileSync(absolute(p));
const read=p=>JSON.parse(bytes(p));
const fileSHA=p=>SHA(bytes(p));
const gitHead=(dir='.')=>cp.execFileSync('git',['rev-parse','HEAD'],{
 cwd:absolute(dir),encoding:'utf8'}).trim();
const currentHead=gitHead();
if(process.env.SUDU_D_QA_ONLY!=='1')throw Error('QA ONLY flag required; never run as publisher');
if(process.env.SUDU_D_EXPECT_SHA)
 assert.equal(currentHead,process.env.SUDU_D_EXPECT_SHA,'V4 code/test HEAD changed after claim');
assert.equal(gitHead(SRCROOT),AUTHOR_HEAD,'B author exact immutable head moved');
const root113=SRCROOT+'/';
const manifestPath=root113+'sudu/data/processed/113/role-a-c01-05/manifest.json';
const originalJsonPath=root113+'sudu/data/years/113.json';
const visualPath=root113+'sudu/data/processed/113/role-a-c01-05/VISUAL_QA_ASSISTANT_20261025.json';
const teachingRoot=root113+'sudu/teaching-candidates/113-role-b-c01-05-20261025/';
const manifest=read(manifestPath),archive=read(originalJsonPath),visual=read(visualPath);
const batch=read(teachingRoot+'batch.json');
const observedPage=manifest.originalPage,observedAnswer=manifest.answerPage;
assert.equal(manifest.archivedYearJsonGitBlobSha1,gitBlob(bytes(originalJsonPath)));
assert.equal(observedPage.gitBlobSha1,gitBlob(bytes(root113+observedPage.path)));
assert.equal(observedPage.sha256,fileSHA(root113+observedPage.path));
assert.equal(observedAnswer.gitBlobSha1,gitBlob(bytes(root113+observedAnswer.path)));
assert.equal(observedAnswer.sha256,fileSHA(root113+observedAnswer.path));
assert.equal(manifest.answerReviewStatus,'ORIGINAL_ANSWER_IMAGE_OBSERVED_CORRECTION_PDF_SCOPE_PENDING');
assert.equal(manifest.pdfRehashStatus,'UNAVAILABLE_NOT_FRESHLY_DOWNLOADED');
assert.equal(batch.distinctAiEReview,'PENDING');
assert.equal(batch.roleDRealV4_8x2,'PENDING');
assert.equal(batch.masterRelease,'NOT_AUTHORIZED');
assert.equal(archive.year,113);
const originalPaper=archive.papers.find(x=>x.paper==='00-C');
assert(originalPaper);
const originalRecords=originalPaper.questions;
const targetRoot='data/approved/webp/113/';
const mapData=QIDS.map((id,i)=>{
 const [rev,img,digest,answer]=EXPECT[i];
 const m=manifest.questions.find(x=>x.questionId===id);
 const v=visual.questions.find(x=>x.questionId===id);
 const b=read(teachingRoot+id+'.json');
 const row=batch.items.find(x=>x.questionId===id);
 const raw=originalRecords.find(x=>x.id===id);
 assert(m&&v&&b&&row&&raw,'missing REAL original source/B lesson '+id);
 assert.equal(b.questionId,id);
 assert.equal(b.role,'B');
 assert.equal(m.sourceRevisionSha256,rev);
 assert.equal(b.source.sourceRevision,rev);
 assert.equal(row.sourceRevision,rev);
 assert.equal(m.asset.sha256,img);
 assert.equal(v.assetSha256,img);
 assert.equal(b.source.webpSha256,img);
 assert.equal(row.webpSha256,img);
 assert.equal(fileSHA(root113+m.asset.path),img,'original A WebP byte SHA mismatch '+id);
 assert.equal(gitBlob(bytes(root113+m.asset.path)),m.asset.gitBlobSha1);
 assert.equal(v.reviewResult,'PASS_ASSISTANT_DIRECT_ORIGINAL_PIXEL_VISUAL_QA');
 assert.equal(m.individualImageQa,'DRAFT_NEEDS_DIRECT_ASSISTANT_VISUAL_QA',
  'A manifest unexpectedly promoted without formal review '+id);
 assert.equal(m.answerVerified,false);
 assert.equal(m.questionVerified,false);
 assert.equal(m.studentReady,false);
 assert.equal(b.source.originalAnswerVerified,false);
 assert.equal(b.source.finalNoticeScopeVerified,false);
 assert.equal(b.review.status,'BLOCKED');
 assert.equal(b.review.formalReady,false);
 assert.equal(b.review.newLive,false);
 assert.equal(b.review.authorSelfCheckOnly,true);
 assert.equal(b.teaching.hasExamCalculation,false);
 assert.equal(b.teaching.examCalculation,null);
 assert.equal(raw.answerVerified,false);
 assert.equal(raw.questionVerified,false);
 assert.equal(raw.teachingVerified,false);
 assert.equal(b.knownAnswerCandidate,answer);
 assert.equal(m.answerCandidate,answer);
 assert.equal(v.publishedAnswerImageCandidate,answer);
 assert.equal('ABCD'[raw.answer],answer,'archived original published-answer candidate inconsistent');
 assert.equal(raw.question,m.question);
 assert.deepEqual(raw.options,m.options);
 assert.equal(b.question,raw.question);
 assert.deepEqual(b.options,raw.options);
 assert.equal(canonical(b.teaching),b.teachingCanonicalSha256);
 assert.equal(b.teachingCanonicalSha256,row.teachingCanonicalSha256);
 const composed=canonical({
  questionId:id,sourceRevision:rev,webpSha256:img,
  teaching:b.teaching,enrichment:b.enrichment
 });
 assert.equal(composed,digest,'recomputed actual author teaching digest mismatch '+id);
 assert.equal(composed,b.composedTeachingSha256);
 assert.equal(composed,row.composedTeachingSha256);
 assert.equal(fileSHA(teachingRoot+id+'.json'),row.fileSha256,
  'author complete JSON bytes changed but digest was not invalidated');
 const lesson=b.teaching;
 assert(Array.isArray(lesson.solvingSteps)&&lesson.solvingSteps.length>=3);
 const optionExplanations={};
 for(const L of 'ABCD'){
  const x=lesson.optionExplanations?.[L];
  assert(x&&typeof x.teacher==='string'&&x.teacher.length>=12);
  assert(x.elementary?.length>=8&&x.why?.length>=8);
  assert.equal(x.isCorrect,L===answer);
  optionExplanations[L]={
   teacher:x.teacher,elementary:x.elementary,reason:x.why
  };
 }
 const words=b.enrichment.chineseVocabulary;
 assert(words.length>=3);
 for(const w of words)
  assert(['初級','中級','高級'].includes(w.level)&&w.term&&w.meaning);
 const highlights=b.enrichment.highlights.map(x=>x.text);
 assert(highlights.length>=3);
 assert(highlights.every(x=>typeof x==='string'&&x.length>0));
 const extra={'相關字詞':words.map(w=>w.level+'：'+w.term+'（'+w.meaning+'）').join('\n')};
 const publicQuestion={
  id:m.originalQuestionNumber,year:113,canonicalId:id,subject:'國文',
  topic:lesson.topic,question:m.question,options:m.options,answer,
  image:targetRoot+id+'.webp',imageSha256:img,
  sharedMaterialIds:[],sharedImages:[],
  sourceText:raw.source,memory:lesson.memory,concept:lesson.concept,
  extension:lesson.solvingSteps.join('\n'),
  teacherSummary:lesson.teacherSummary,
  elementarySummary:lesson.elementarySummary,
  optionExplanations,highlights,extra,formula:'',
  examCalculation:null,
  qaOnlyOriginalRevision:rev,qaOnlyTeachingDigest:digest,
  qaOnlyOriginalWebPSha256:img,
  qaOnlyAnswerCorrectionScope:'PENDING',
  qaOnlyFormalReview:false
 };
 assert(publicQuestion.sourceText.includes('tcte.edu.tw'),'source URL not original TCTE');
 return {id,original:m,raw,b,rev,img,digest,answer,publicQuestion,words,highlights};
});
const preview={
 schemaVersion:1,year:113,approvedCount:mapData.length,
 questions:mapData.map(x=>x.publicQuestion),
 QA_ONLY_UNPUBLISHABLE:true,studentReleaseApproved:false,
 independentFormalEReceiptRegistered:false,actualPublishedApproved113:0
};
const releasePath=absolute('_site/sudu/data/approved/113.json');
assert(!fs.existsSync(releasePath),'actual approved 113 exists: must re-review, do not intercept it');
const report={
 taskId:'D-113-C01-C05-REAL-SOURCE-V4-PER-QUESTION-20261027-01',
 authorRole:'D',headerSha:currentHead,sourceAHead:SOURCE_HEAD,
 teacherPerspectiveAuthorBHead:AUTHOR_HEAD,
 notReadyReason:'Actual A 113 G1 manifest DRAFT and official final correction scope pending; B/E candidate not registered formal publisher',
 realPublisherPayloadUsed:false,qaOnlyBrowserResponseIntercept:true,
 studentReleaseApproved:false,liveVerified:false,
 v4HtmlSha256:fileSHA('sudu/v4-115-multisubject-review-demo.html'),
 v4RuntimeSha256:fileSHA('sudu/verified-questions-runtime.js'),
 archivedOriginalYearSha256:fileSHA(originalJsonPath),
 originalPageSha256:observedPage.sha256,
 originalAnnouncedAnswerImageSha256:observedAnswer.sha256,
 originalRoleAManifestSha256:fileSHA(manifestPath),
 sourceVisualReceiptSha256:fileSHA(visualPath),
 teachingBatchSha256:fileSHA(teachingRoot+'batch.json'),
 ciRunId:process.env.GITHUB_RUN_ID||null,errors:[],
 individual:mapData.map(x=>({
   questionId:x.id,sourceRevision:x.rev,originalSingleWebPSha256:x.img,
   originalAnswerCandidate:x.answer,
   originalPublishedAnswerPageSha256:observedAnswer.sha256,
   actualAuthorTeachingDigest:x.digest,
   originalManifestG1Status:x.original.individualImageQa,
   finalOfficialCorrectionVerified:false,
   distinctFormalEReceipt:false,
   readiness:'QUARANTINED_NO_RELEASE',
   cases:[],errors:[]
 })),
 status:'RUNNING'
};
function save(){
 fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'per-question-v4-results.json'),JSON.stringify(report,null,2)+'\n');
 for(const q of report.individual)
   fs.writeFileSync(path.join(OUT,q.questionId+'-results.json'),
    JSON.stringify({...q,v4HtmlSha256:report.v4HtmlSha256,
     runtimeSha256:report.v4RuntimeSha256,headSha:report.headerSha,
     ciRunId:report.ciRunId,qaOnly:true,ready:false,live:false},null,2)+'\n');
}
const copied=[];
for(const x of mapData){
 const to=absolute('_site/sudu/'+targetRoot+x.id+'.webp');
 fs.mkdirSync(path.dirname(to),{recursive:true});
 if(fs.existsSync(to))throw Error('unapproved 113 image somehow already in public build: '+to);
 fs.copyFileSync(absolute(root113+x.original.asset.path),to);
 assert.equal(SHA(fs.readFileSync(to)),x.img,'staged image modified');
 copied.push(to);
}
const tap=(locator,touch)=>touch?locator.tap({timeout:15000}):locator.click({timeout:15000});
const norm=s=>String(s).normalize('NFKC').replace(/\s+/g,'').replace(/[：:，,。；;（）()\n]/g,'');
async function checkImage(page,locator,x,label){
 assert.equal(await locator.getAttribute('src'),x.publicQuestion.image,label+' original URL mismatch');
 await locator.scrollIntoViewIfNeeded();
 const rect=await locator.evaluate(async e=>{
  await e.decode();
  const a=e.getBoundingClientRect(),p=e.parentElement.getBoundingClientRect();
  return{width:a.width,height:a.height,parentWidth:p.width,
   naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight};
 });
 assert(rect.naturalWidth>0&&rect.naturalHeight>0);
 assert(rect.width>0&&rect.height>0&&rect.width<=rect.parentWidth+1,
  label+' original picture clipped');
 assert(Math.abs(rect.width/rect.height-rect.naturalWidth/rect.naturalHeight)/
  (rect.naturalWidth/rect.naturalHeight)<0.03,label+' original image ratio distorted');
 const response=await page.request.get(new NativeURL('./'+x.publicQuestion.image,BASE).href);
 assert.equal(response.status(),200,label+' genuine original picture HTTP');
 assert.equal(SHA(await response.body()),x.img,label+' actual picture HTTP bytes do not match original A');
}
async function layout(page,label){
 const shape=await page.evaluate(()=>{
  const clipped=[...document.querySelectorAll('#questionCard h1,#answerCard .opt-text,#guideCard .guide-block')].
    filter(e=>e.offsetWidth>0&&e.scrollWidth>e.clientWidth+3&&
      getComputedStyle(e).overflowX==='hidden')
    .map(e=>({text:e.textContent.slice(0,36),scroll:e.scrollWidth,client:e.clientWidth}));
  return{view:innerWidth,doc:document.documentElement.scrollWidth,clipped};
 });
 assert(shape.doc<=shape.view+1,label+' horizontal overflow '+JSON.stringify(shape));
 assert.deepEqual(shape.clipped,[],label+' clipped actual Chinese source/lesson text');
}
async function glyph(page,label){
 const glyphs=await page.evaluate(async()=>{
  await document.fonts.ready;
  const el=document.getElementById('guideCard');
  const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
  ctx.canvas.width=80;ctx.canvas.height=80;ctx.font='47px '+getComputedStyle(el).fontFamily;
  ctx.textBaseline='top';ctx.fillStyle='#000';
  return ['中','文','摒','屏'].map(c=>{
   ctx.clearRect(0,0,80,80);ctx.fillText(c,5,4);
   const pixels=ctx.getImageData(0,0,80,80).data;
   let n=0,h=2166136261;
   for(let i=3;i<pixels.length;i+=4){if(pixels[i]>32)n++;h=Math.imul(h^pixels[i],16777619)>>>0}
   return{char:c,pixels:n,hash:h.toString(16)};
  });
 });
 assert(glyphs.every(x=>x.pixels>70)&&new Set(glyphs.map(x=>x.hash)).size>=3,
   label+' unreadable CJK tofu '+JSON.stringify(glyphs));
 return glyphs;
}
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
 for(const [width,height] of SIZES)for(const theme of ['light','dark']){
  const touch=width<=430;
  const profile={width,height,theme,actualInput:touch?'touch':'mouse'};
  const ctx=await browser.newContext({viewport:{width,height},hasTouch:touch,locale:'zh-TW',reducedMotion:'reduce'});
  const page=await ctx.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  let current=-1;
  try{
   await page.route('**/sudu/data/approved/113.json',route=>
     route.fulfill({status:200,contentType:'application/json; charset=utf-8',
      body:JSON.stringify(preview)}));
   await page.goto(BASE+'v4-115-multisubject-review-demo.html?year=113',
     {waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='113',null,{timeout:25000});
   await page.addStyleTag({content:
    'body::after{content:"113 SOURCE-EXACT QA ONLY / UNAPPROVED / NOT LIVE";'+
    'position:fixed;bottom:3px;right:3px;background:#971616;color:white;'+
    'font:bold 11px sans-serif;padding:4px 6px;z-index:100000;pointer-events:none}'});
   assert(await page.locator('#homeView').isVisible());
   assert.equal(await page.locator('#homeYearSel').inputValue(),'113');
   const demoOriginal=await page.evaluate(()=>localStorage.getItem('tvet-115-multisubject-demo-v1'));
   await page.locator('#homeSubjectSel').selectOption('國文');
   await page.locator('#studyView').waitFor({state:'visible'});
   if(theme==='dark')await tap(page.locator('#themeBtn'),touch);
   assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
   for(let i=0;i<mapData.length;i++){
    current=i;
    const x=mapData[i],q=x.publicQuestion,label=x.id+' '+width+'x'+height+' '+theme;
    const dom=await page.evaluate(()=>({
     year:pageYear(),id:qnow()?.canonicalId,
     stem:qnow()?.question,options:qnow()?.options,answer:qnow()?.answer,
     source:qnow()?.qaOnlyOriginalRevision,webp:qnow()?.qaOnlyOriginalWebPSha256,
     digest:qnow()?.qaOnlyTeachingDigest,
     lessons:qnow()?.optionExplanations,
     sharedIds:qnow()?.sharedMaterialIds,
     studentRelease:qnow()?.qaOnlyFormalReview
    }));
    assert.equal(dom.year,'113');
    assert.equal(dom.id,x.id);
    assert.equal(dom.stem,q.question);
    assert.deepEqual(dom.options,q.options);
    assert.equal(dom.answer,q.answer);
    assert.equal(dom.source,x.rev);assert.equal(dom.webp,x.img);
    assert.equal(dom.digest,x.digest);
    assert.deepEqual(dom.lessons,q.optionExplanations);
    assert.deepEqual(dom.sharedIds,[]);assert.equal(dom.studentRelease,false);
    assert.equal(await page.locator('#questionCard h1').textContent(),q.question);
    const options=page.locator('#answerCard .opt');
    assert.equal(await options.count(),4);
    for(let k=0;k<4;k++){
     assert.equal(await options.nth(k).getAttribute('data-a'),'ABCD'[k]);
     assert.equal(await options.nth(k).locator('.opt-text').textContent(),q.options[k]);
    }
    const image=page.locator('#questionCard figure[data-single-question-webp="true"] img');
    assert.equal(await image.count(),1,'one actual original single-Q WebP required');
    assert.equal(await page.locator('#questionCard figure[data-shared-material-webp="true"]').count(),0);
    await checkImage(page,image,x,label);
    await layout(page,label+' before answer');
    if(!touch){
     await options.first().scrollIntoViewIfNeeded();
     const before=await options.first().evaluate(e=>getComputedStyle(e).backgroundColor);
     await options.first().hover();await page.waitForTimeout(170);
     const after=await options.first().evaluate(e=>getComputedStyle(e).backgroundColor);
     assert.notEqual(before,after,label+' real mouse hover CSS does not respond');
    }
    const chosen=i%2===0?(x.answer==='A'?'B':'A'):x.answer;
    await tap(page.locator('#answerCard .opt[data-a="'+chosen+'"]'),touch);
    await page.locator('#guideCard.show').waitFor({timeout:15000});
    assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
    assert.equal(await page.locator('#answerCard .opt.wrong').count(),chosen===x.answer?0:1);
    assert.equal(await page.locator('#answerCard .option-detail').count(),4);
    for(const L of 'ABCD'){
     const detail=q.optionExplanations[L];
     const found=norm(await page.locator('#answerCard .opt[data-a="'+L+'"] + .option-detail').innerText());
     for(const field of ['teacher','elementary','reason'])
      assert(found.includes(norm(detail[field].replace(/反向檢查/g,'相反意思'))),
       label+' B authored '+L+'/'+field+' missing from real V4');
    }
    const blocks=page.locator('#guideCard .guide-block h3');
    assert.equal(await blocks.filter({hasText:'考題計算式'}).count(),0);
    assert.equal(await page.locator('#guideCard .calculation-step').count(),0);
    const guide=await page.locator('#guideCard').innerText();
    assert(guide.includes(q.memory)&&guide.includes(q.concept),label+' original pedagogy/mnemonic lost');
    for(const term of x.words)assert(guide.includes(term.term)&&guide.includes(term.level),
      label+' original author graded vocabulary lost '+term.term);
    assert(!guide.includes(q.teacherSummary)&&!guide.includes(q.elementarySummary),
      label+' repeated original answer full teacher/child summary in guide');
    const marks=await page.locator('#answerCard mark.exam-highlight').allInnerTexts();
    assert(marks.length>0,label+' authored source-literal highlights are not visible');
    for(const m of marks)assert(x.highlights.some(t=>t.includes(m)||m.includes(t)),
      label+' highlighted text not present in author source bound terms: '+m);
    await glyph(page,label);
    await layout(page,label+' after answer');
    const screenshot=x.id+'-'+width+'x'+height+'-'+theme+'.png';
    await page.screenshot({path:path.join(OUT,screenshot),fullPage:false,animations:'disabled'});
    report.individual[i].cases.push({
     ...profile,status:'AUTHENTIC_SOURCE_QA_ONLY_COMPONENT_PASS_NOT_RELEASE',
     originalQuestionAndFourOptionsExact:true,
     AWebPHttpBytesExact:true,BTeachingDigestExact:true,
     fourDualLevelReasonsExact:true,correctWrongRealAction:true,
     noCalculationCard:true,highlightRealText:true,CJKnonTofu:true,
     noHorizontalOverflow:true,screenshot
    });
    save();
    if(i<mapData.length-1){
     const next=page.locator('#nextBtn');
     await next.scrollIntoViewIfNeeded();
     await tap(next,touch);
    }
   }
   const handle=page.locator('#navHandle');
   if(await handle.getAttribute('aria-expanded')!=='true')await tap(handle,touch);
   await tap(page.locator('#reviewTop'),touch);
   await page.locator('#reviewView.show').waitFor({timeout:15000});
   assert.equal(await page.locator('#reviewList .wrong-card').count(),3,
    'correct/wrong choice history must have 3 real reviewed mistakes');
   const stored=await page.evaluate(()=>({
    annual:localStorage.getItem('tvet-verified-113-v1'),
    demo:localStorage.getItem('tvet-115-multisubject-demo-v1')
   }));
   assert(stored.annual,'113 QA-only student state key unexpectedly missing');
   assert.equal(stored.demo,demoOriginal,'annual isolated 113 answer changed Demo35 record');
   assert.deepEqual(errors,[],'actual V4 browser JS errors occurred');
  }catch(error){
   const entry={...profile,
    currentQid:current>=0?mapData[current].id:null,
    error:String(error.stack||error),browserErrors:errors};
   report.errors.push(entry);
   if(current>=0)report.individual[current].errors.push(entry);
  }finally{
   await ctx.close();save();
  }
 }
 }finally{
  await browser.close();
  for(const p of copied)try{fs.unlinkSync(p)}catch(e){report.errors.push({cleanup:p,error:String(e)})}
 }
 assert.equal(fs.existsSync(releasePath),false,'testing illegally created a public approved 113 file');
 const counts=report.individual.map(q=>q.cases.length);
 report.status=report.errors.length?'FAIL':'STAGED_REAL_ORIGINAL_5X8X2_QA_ONLY_PASS_NOT_READY';
 save();
 if(report.errors.length)console.error('FIRST_FAILS',JSON.stringify(report.errors.slice(0,5),null,2));
 for(const q of report.individual)
  console.log(q.questionId+': '+q.cases.length+'/16 genuine V4 QA-only cases; source '+q.sourceRevision+
   '; image '+q.originalSingleWebPSha256+'; teaching '+q.actualAuthorTeachingDigest+
   '; officialFinal=PENDING; READY=0; LIVE=0');
 assert.equal(report.errors.length,0,'actual original per-question browser UI failures');
 assert.deepEqual(counts,[16,16,16,16,16],'missing genuine per-question 8x2 receipts');
 console.log('PASS 80/80 exact real source/B lesson 113 Chinese QA ONLY; not authorized published source');
})().catch(error=>{
 report.status='FAIL';report.errors.push({fatal:String(error.stack||error)});
 save();console.error(error.stack||error);process.exitCode=1;
});
