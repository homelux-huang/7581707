'use strict';
/* 113 Chinese original Q07/08: A source exact + B lesson true SHA and
 * genuine existing V4 browser. QA-only browser interception, NOT publisher
 * approval, not an E credential, not main/Pages or student-ready content.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const cp=require('node:child_process');
const {URL:NativeURL}=require('node:url');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..'),SRC='_source113_next';
const BASE=process.env.SUDU_D_URL||'http://127.0.0.1:8765/sudu/';
const OUT=path.resolve(process.env.SUDU_D_OUT||'test-results/role-d-113-c07-c08');
const AUTHOR='08cb5a503b6f53be0e7e4de285d1cb2e0a8beaf3';
const A_SOURCE='1f76d702dd00ff2bcfef7bccf7afa33b3dbc7ad5';
const ITEMS=[
 {id:'113-00-C-07',answer:'A',revision:'ff4d5109a27db1bff06d28df802051167915a627ac116e75ce5c456df21dfc26',
  webp:'dc654891d368033b5b422cf01181231aefc62e9a31452ad1e64aaca478291b4a',
  digest:'1e04c8e4d7e72aa5ecb16fe49bc22c3dc9e049c713a28da8fefa0f9182a31020'},
 {id:'113-00-C-08',answer:'D',revision:'052e45e52d7f966f0f4e249522a63dfb1813124b93c2a09239b7848c1a0298d5',
  webp:'4ea59fb90d9bbec2f255944b0a5fc6be4f9a25257e3f74caa7aa3b5e10e88e49',
  digest:'2d7cb668a1c12edf79e19fcc234968325b669eb38327eff38c24d9678d95fd82'}
];
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const full=p=>path.join(ROOT,p),buf=p=>fs.readFileSync(full(p));
const SHA=b=>crypto.createHash('sha256').update(b).digest('hex');
const gitBlob=b=>crypto.createHash('sha1').update(Buffer.concat([Buffer.from('blob '+b.length),Buffer.from([0]),b])).digest('hex');
const stable=x=>Array.isArray(x)?x.map(stable):x&&typeof x==='object'?
 Object.fromEntries(Object.keys(x).sort().map(k=>[k,stable(x[k])])):x;
const digest=x=>SHA(Buffer.from(JSON.stringify(stable(x)),'utf8'));
const json=p=>JSON.parse(buf(p));
const git=dir=>cp.execFileSync('git',['rev-parse','HEAD'],{cwd:full(dir||'.'),encoding:'utf8'}).trim();
const head=git();
if(process.env.SUDU_D_QA_ONLY!=='1')throw Error('Role D real source QA-only requires explicit NO RELEASE marker');
if(process.env.SUDU_D_HEAD)assert.equal(head,process.env.SUDU_D_HEAD,'branch moved after audited head');
assert.equal(git(SRC),AUTHOR,'B authored source head changed');
const source=SRC+'/';
const manifest=json(source+'sudu/data/processed/113/role-a-c07-10/manifest.json');
const visual=json(source+'sudu/data/processed/113/role-a-c07-10/VISUAL_QA_ASSISTANT_20261025.json');
const year=json(source+'sudu/data/years/113.json');
const authored=json(source+'sudu/teaching-candidates/113-role-b-c06-10-20261026/batch.json');
const originalPage=manifest.originalPage;
const answerPage=manifest.originalAnswerPage;
assert.equal(year.year,113);
assert.equal(manifest.officialFinalAmendmentCheckedForNumbers,false);
assert.equal(manifest.newAnswerVerified,0);
assert.equal(manifest.newReady,0);
assert.equal(manifest.originalPdfsFreshlyDownloadedAndHashed,false);
assert.equal(SHA(buf(source+originalPage.path)),originalPage.sha256);
assert.equal(SHA(buf(source+answerPage.path)),answerPage.sha256);
assert.equal(gitBlob(buf(source+answerPage.path)),answerPage.gitBlobSha1);
assert.equal(authored.sourceA78Head,A_SOURCE);
assert.equal(authored.distinctEApproval,'PENDING');
const archive=year.papers.find(p=>p.paper==='00-C').questions;
const webpRoot='data/approved/webp/113/';
const reals=ITEMS.map(item=>{
 const m=manifest.questions.find(x=>x.questionId===item.id);
 const v=visual.questionResults.find(x=>x.questionId===item.id);
 const b=json(source+'sudu/teaching-candidates/113-role-b-c06-10-20261026/'+item.id+'.json');
 const batch=authored.items.find(x=>x.questionId===item.id);
 const raw=archive.find(x=>x.id===item.id);
 assert(m&&v&&b&&batch&&raw,'missing authentic source+authored lesson '+item.id);
 assert.equal(m.sourceRevisionSha256,item.revision);
 assert.equal(b.source.sourceRevision,item.revision);
 assert.equal(batch.sourceRevision,item.revision);
 assert.equal(m.asset.sha256,item.webp);
 assert.equal(v.asset.sha256,item.webp);
 assert.equal(batch.webpSha256,item.webp);
 assert.equal(b.source.webpSha256,item.webp);
 assert.equal(b.source.originalSourceCommit,A_SOURCE);
 assert.equal(b.source.manifestGitBlobSha,'ca3e7839f9811b6cae7ae92a229e9c8709e887bb');
 assert.equal(SHA(buf(source+m.asset.path)),item.webp);
 assert.equal(gitBlob(buf(source+m.asset.path)),m.asset.gitBlobSha1);
 assert.equal(m.visualQaStatus,'DRAFT_NEEDS_INDIVIDUAL_SOURCE_PIXEL_IMAGE_QA');
 assert.equal(m.originalQuestionTextQa,'PENDING_FINAL_PAGE_VISUAL_TEXT_QA');
 assert.equal(v.visualSourceResult,'PASS_ROLE_A_SOURCE_IMAGE_ONLY');
 assert.equal(v.answerVerified,false);
 assert.equal(v.questionVerified,false);
 assert.equal(m.answerVerified,false);
 assert.equal(m.studentReady,false);
 assert.equal(b.source.officialYearCorrectionNoticeVerified,false);
 assert.equal(b.review.formalReady,false);
 assert.equal(b.review.studentReleaseApproved,false);
 assert.equal(b.review.independentEContent,'PENDING');
 assert.equal(raw.answerVerified,false);
 assert.equal(raw.questionVerified,false);
 assert.equal(raw.teachingVerified,false);
 assert.equal(raw.question,m.question,'archived original question differs from A manifest');
 assert.deepEqual(raw.options,m.options,'archived original A-D differs from original A manifest');
 assert.deepEqual(m.originalRawOptions,m.options,'this Q no OCR change allowed');
 assert.equal(b.question,m.question);
 assert.deepEqual(b.options,m.options);
 assert.equal(b.knownAnswerCandidate,item.answer);
 assert.equal(m.answerCandidate,item.answer);
 assert.equal(v.originalPublishedAnswerCandidate,item.answer);
 assert.equal('ABCD'[raw.answer],item.answer);
 assert.equal(digest(b.teaching),b.teachingCanonicalSha256);
 assert.equal(b.teachingCanonicalSha256,batch.teachingCanonicalSha256);
 const composed=digest({questionId:item.id,sourceRevision:item.revision,webpSha256:item.webp,teaching:b.teaching,enrichment:b.enrichment});
 assert.equal(composed,item.digest);
 assert.equal(composed,b.composedTeachingSha256);
 assert.equal(composed,batch.composedTeachingSha256);
 assert.equal(SHA(buf(source+batch.path)),batch.fileSha256);
 assert.equal(b.teaching.hasExamCalculation,false);
 assert.equal(b.teaching.examCalculation,null);
 const opts={};
 for(const L of 'ABCD'){
  const op=b.teaching.optionExplanations?.[L];
  assert(op&&op.teacher?.length>10&&op.elementary?.length>6&&op.reason?.length>6);
  assert.equal(op.isCorrect,L===item.answer);
  opts[L]={teacher:op.teacher,elementary:op.elementary,reason:op.reason};
 }
 const words=b.enrichment.chineseVocabulary;
 assert(words.length>=3&&words.every(x=>['初級','中級','高級'].includes(x.level)&&x.term&&x.meaning));
 const highlights=b.enrichment.highlights.map(x=>x.text);
 assert(highlights.length>0);
 const q={
  id:m.originalQuestionNumber,canonicalId:item.id,year:113,subject:'國文',
  topic:b.teaching.topic,question:m.question,options:m.options,answer:item.answer,
  image:webpRoot+item.id+'.webp',imageSha256:item.webp,
  sharedMaterialIds:[],sharedImages:[],
  memory:b.teaching.memory,concept:b.teaching.concept,
  extension:b.teaching.solvingSteps.join('\n'),
  sourceText:raw.source,teacherSummary:b.teaching.teacherSummary,
  elementarySummary:b.teaching.elementarySummary,optionExplanations:opts,
  extra:{'相關字詞':words.map(w=>w.level+'：'+w.term+'（'+w.meaning+'）').join('\n')},
  highlights,formula:'',examCalculation:null,
  qaOnlyRevision:item.revision,qaOnlyDigest:item.digest,
  qaOnlyOriginalWebp:item.webp,qaOnlyApproved:false
 };
 return {...item,raw,m,b,words,highlights,q};
});
const temporaryApproved=full('_site/sudu/data/approved/113.json');
assert(!fs.existsSync(temporaryApproved),'unexpected real approved 113; do not stage over publisher output');
const payload={schemaVersion:1,year:113,approvedCount:2,questions:reals.map(x=>x.q),
 QA_ONLY_UNPUBLISHABLE:true,studentReleaseApproved:false,independentEReviewRegistered:false};
const report={
 taskId:'D-113-C07-C08-AUTHENTIC-V4-8X2-20261027-03',
 purpose:'TWO_REAL_113_CHINESE_QA_ONLY_ANNUAL_SOURCE_AND_LESSON_BROWSER_NOT_PUBLISHER',
 role:'D',sourceAHead:A_SOURCE,lessonBHead:AUTHOR,headSha:head,
 ciRunId:process.env.GITHUB_RUN_ID||null,
 htmlSha256:SHA(buf('sudu/v4-115-multisubject-review-demo.html')),
 runtimeSha256:SHA(buf('sudu/verified-questions-runtime.js')),
 manifestGitBlob:'ca3e7839f9811b6cae7ae92a229e9c8709e887bb',
 originalArchiveSha256:SHA(buf(source+'sudu/data/years/113.json')),
 originalPublishedAnswerPageSha256:answerPage.sha256,
 exactOriginalSource:true,interceptedPlaywrightOnly:true,
 actualPublisherApproval:false,ready:0,live:0,
 items:reals.map(x=>({qid:x.id,sourceRevision:x.revision,webpSha256:x.webp,
  teachingDigest:x.digest,announcedAnswerCandidate:x.answer,officialCorrectionVerified:false,
  EFormalReviewRegistered:false,G1ImageQa:'DRAFT_NEEDS_INDIVIDUAL_SOURCE_PIXEL_IMAGE_QA',
  status:'PENDING_ISOLATED_QA_NOT_READY',cases:[],errors:[]})),
 errors:[],status:'RUNNING'
};
function save(){
 fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'two-question-results.json'),JSON.stringify(report,null,2)+'\n');
 for(const q of report.items)fs.writeFileSync(path.join(OUT,q.qid+'-results.json'),
  JSON.stringify({role:'D',ciRunId:report.ciRunId,exactHead:head,
   htmlSHA:report.htmlSha256,runtimeSHA:report.runtimeSha256,
   qaOnly:true,ready:false,live:false,...q},null,2)+'\n');
}
const staged=[];
for(const x of reals){
 const dest=full('_site/sudu/'+x.q.image);
 fs.mkdirSync(path.dirname(dest),{recursive:true});
 assert(!fs.existsSync(dest),'publisher unexpectedly placed old source WebP');
 fs.copyFileSync(full(source+x.m.asset.path),dest);
 assert.equal(SHA(fs.readFileSync(dest)),x.webp);
 staged.push(dest);
}
const act=(loc,touch)=>touch?loc.tap({timeout:12000}):loc.click({timeout:12000});
const compact=s=>String(s).normalize('NFKC').replace(/\s+/g,'').replace(/[，。：；（）]/g,'');
async function imageCheck(page,img,x,label){
 assert.equal(await img.getAttribute('src'),x.q.image);
 await img.scrollIntoViewIfNeeded();
 const shape=await img.evaluate(async el=>{
  await el.decode();let a=el.getBoundingClientRect(),b=el.parentElement.getBoundingClientRect();
  return{nw:el.naturalWidth,nh:el.naturalHeight,w:a.width,h:a.height,pw:b.width};
 });
 assert(shape.nw>0&&shape.nh>0&&shape.w>0&&shape.w<=shape.pw+1,label+' cropped original WebP');
 assert(Math.abs(shape.w/shape.h-shape.nw/shape.nh)/(shape.nw/shape.nh)<0.03,label+' image aspect ratio distorted');
 const resp=await page.request.get(new NativeURL('./'+x.q.image,BASE).href);
 assert.equal(resp.status(),200);assert.equal(SHA(await resp.body()),x.webp);
}
async function layout(page,label){
 const data=await page.evaluate(()=>({viewport:innerWidth,doc:document.documentElement.scrollWidth,
  clipped:[...document.querySelectorAll('#questionCard h1,#answerCard .opt-text,#guideCard .guide-block')]
    .filter(x=>x.offsetWidth&&x.scrollWidth>x.clientWidth+3&&getComputedStyle(x).overflowX==='hidden')
    .map(x=>x.textContent.slice(0,35))}));
 assert(data.doc<=data.viewport+1,label+' horizontal overflow '+JSON.stringify(data));
 assert.deepEqual(data.clipped,[],label+' cropped original lesson/option');
}
async function glyphs(page,label){
 const result=await page.evaluate(async()=>{
  await document.fonts.ready;const c=document.createElement('canvas'),ctx=c.getContext('2d',{willReadFrequently:true});
  c.width=84;c.height=84;ctx.fillStyle='#000';ctx.textBaseline='top';
  ctx.font='47px '+getComputedStyle(document.getElementById('guideCard')).fontFamily;
  return ['中','文','序','轉'].map(v=>{
   ctx.clearRect(0,0,84,84);ctx.fillText(v,4,3);
   let raw=ctx.getImageData(0,0,84,84).data,n=0,h=2166136261;
   for(let i=3;i<raw.length;i+=4){if(raw[i]>32)n++;h=Math.imul(h^raw[i],16777619)>>>0}
   return {glyph:v,pixels:n,hash:h.toString(16)};
  });
 });
 assert(result.every(x=>x.pixels>70)&&new Set(result.map(x=>x.hash)).size>=3,
  label+' Chinese tofu '+JSON.stringify(result));
}
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
 for(const [width,height] of SIZES)for(const theme of ['light','dark']){
  const touch=width<=430,context=await browser.newContext({
   viewport:{width,height},hasTouch:touch,locale:'zh-TW',reducedMotion:'reduce'});
  const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  let i=-1;
  try{
   await page.route('**/sudu/data/approved/113.json',r=>
     r.fulfill({status:200,contentType:'application/json; charset=utf-8',body:JSON.stringify(payload)}));
   await page.goto(BASE+'v4-115-multisubject-review-demo.html?year=113',{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='113',null,{timeout:25000});
   await page.addStyleTag({content:
    'body::after{content:"QA-ONLY / 113 C07-C08 NOT PUBLISHER ADMITTED OR LIVE";position:fixed;'+
    'right:3px;bottom:3px;background:#871919;color:white;z-index:100000;padding:4px 5px;'+
    'font:bold 10px sans-serif;pointer-events:none}'});
   assert.equal(await page.locator('#homeYearSel').inputValue(),'113');
   const demoBefore=await page.evaluate(()=>localStorage.getItem('tvet-115-multisubject-demo-v1'));
   await page.locator('#homeSubjectSel').selectOption('國文');
   await page.locator('#studyView').waitFor({state:'visible'});
   if(theme==='dark')await act(page.locator('#themeBtn'),touch);
   assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
   for(i=0;i<reals.length;i++){
    const x=reals[i],q=x.q,label=x.id+' '+width+'x'+height+' '+theme;
    const dom=await page.evaluate(()=>({
     id:qnow()?.canonicalId,question:qnow()?.question,options:qnow()?.options,
     rev:qnow()?.qaOnlyRevision,sha:qnow()?.qaOnlyOriginalWebp,
     digest:qnow()?.qaOnlyDigest,answer:qnow()?.answer,lessons:qnow()?.optionExplanations
    }));
    assert.equal(dom.id,x.id);assert.equal(dom.question,q.question);
    assert.deepEqual(dom.options,q.options);
    assert.equal(dom.rev,x.revision);assert.equal(dom.sha,x.webp);
    assert.equal(dom.digest,x.digest);assert.equal(dom.answer,x.answer);
    assert.deepEqual(dom.lessons,q.optionExplanations);
    assert.equal(await page.locator('#questionCard h1').textContent(),q.question);
    const options=page.locator('#answerCard .opt');
    assert.equal(await options.count(),4);
    for(let k=0;k<4;k++){
     assert.equal(await options.nth(k).getAttribute('data-a'),'ABCD'[k]);
     assert.equal(await options.nth(k).locator('.opt-text').textContent(),q.options[k]);
    }
    const img=page.locator('#questionCard figure[data-single-question-webp="true"] img');
    assert.equal(await img.count(),1);
    assert.equal(await page.locator('#questionCard figure[data-shared-material-webp="true"]').count(),0);
    await imageCheck(page,img,x,label);await layout(page,label+' before answer');
    if(!touch){
     await options.first().scrollIntoViewIfNeeded();
     const normal=await options.first().evaluate(e=>getComputedStyle(e).backgroundColor);
     await options.first().hover();await page.waitForTimeout(160);
     assert.notEqual(await options.first().evaluate(e=>getComputedStyle(e).backgroundColor),normal,label+' hover effect');
    }
    const selected=i===0?(x.answer==='A'?'B':'A'):x.answer;
    await act(page.locator('#answerCard .opt[data-a="'+selected+'"]'),touch);
    await page.locator('#guideCard.show').waitFor({timeout:12000});
    assert.equal(await page.locator('#answerCard .option-detail').count(),4);
    assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
    assert.equal(await page.locator('#answerCard .opt.wrong').count(),selected===x.answer?0:1);
    for(const L of 'ABCD'){
     const actual=compact(await page.locator('#answerCard .opt[data-a="'+L+'"] + .option-detail').innerText());
     for(const field of ['teacher','elementary','reason'])
      assert(actual.includes(compact(q.optionExplanations[L][field].replace(/反向檢查/g,'相反意思'))),
       label+' original author B missing '+L+' '+field);
    }
    assert.equal(await page.locator('#guideCard .guide-block h3').filter({hasText:'考題計算式'}).count(),0);
    assert.equal(await page.locator('#guideCard .calculation-step').count(),0);
    const guide=await page.locator('#guideCard').innerText();
    assert(guide.includes(q.memory)&&guide.includes(q.concept),label+' original source teaching guide lost');
    for(const w of x.words)assert(guide.includes(w.term)&&guide.includes(w.level),
      label+' B graded vocabulary missing '+w.term);
    assert(!guide.includes(q.teacherSummary)&&!guide.includes(q.elementarySummary),
      label+' duplicate full original teacher/child summary in guide');
    const marks=await page.locator('#answerCard mark.exam-highlight').allInnerTexts();
    assert(marks.length>0,label+' no authored literal source highlight');
    assert(marks.every(w=>x.highlights.some(t=>t.includes(w)||w.includes(t))),
      label+' highlighted text unrelated to true original author terms');
    await glyphs(page,label);await layout(page,label+' after answer');
    const screenshot=x.id+'-'+width+'x'+height+'-'+theme+'.png';
    await page.screenshot({path:path.join(OUT,screenshot),fullPage:false,animations:'disabled'});
    report.items[i].cases.push({width,height,theme,
     input:touch?'real_touch':'real_mouse',sourceRevision:x.revision,webpSHA:x.webp,
     authoredDigest:x.digest,exactSource:true,originalImageHTTPHash:true,
     teacherAndElementaryABCD:true,actualHighlight:true,
     noFormulaCard:true,realWrongCorrectColor:true,rtl:false,
     noOverflow:true,CJKnotTofu:true,screenshot,
     status:'QA_ONLY_REAL_ORIGINAL_V4_PASS_NOT_READY'});
    save();
    if(i<reals.length-1){
     const next=page.locator('#nextBtn');await next.scrollIntoViewIfNeeded();await act(next,touch);
    }
   }
   const handle=page.locator('#navHandle');
   if(await handle.getAttribute('aria-expanded')!=='true')await act(handle,touch);
   await act(page.locator('#reviewTop'),touch);
   await page.locator('#reviewView.show').waitFor({timeout:12000});
   assert.equal(await page.locator('#reviewList .wrong-card').count(),1,
    'one real Q07 wrong answer must enter 113 wrong review');
   const saved=await page.evaluate(()=>({
    student:localStorage.getItem('tvet-verified-113-v1'),
    demo:localStorage.getItem('tvet-115-multisubject-demo-v1')}));
   assert(saved.student,'113 isolated original practice record absent');
   assert.equal(saved.demo,demoBefore,'113 year practice mutated original 35-Demo student record');
   assert.deepEqual(errors,[], 'uncaught V4 browser runtime errors');
  }catch(e){
   const failure={width,height,theme,qid:i>=0?reals[i].id:null,error:String(e.stack||e),browserErrors:errors};
   report.errors.push(failure);if(i>=0)report.items[i].errors.push(failure);
  }finally{await context.close();save()}
 }
 }finally{
  await browser.close();
  for(const p of staged)try{fs.unlinkSync(p)}catch(e){report.errors.push({cleanup:p,error:String(e)})}
 }
 assert.equal(fs.existsSync(temporaryApproved),false,'test illegally wrote approved/113.json');
 report.status=report.errors.length?'FAIL':'QA_ONLY_AUTHENTIC_TWO_113_CHINESE_PASS_NOT_READY';save();
 if(report.errors.length)console.error('FIRST_ACTUAL_FAILS',JSON.stringify(report.errors.slice(0,5),null,2));
 for(const q of report.items)console.log(q.qid+' '+q.cases.length+'/16 real original SHA-bound V4 QA-only; officialNotice=PENDING; newREADY=0; newLIVE=0');
 assert.equal(report.errors.length,0,'real original browser year 113 source/teaching mismatch');
 assert.deepEqual(report.items.map(q=>q.cases.length),[16,16],
   'both original questions need 8 widths by 2 themes');
 console.log('PASS real 113 C07/C08 32/32 isolated original UIQA; NEVER RELEASE READY');
})().catch(error=>{report.status='FAIL';report.errors.push({fatal:String(error.stack||error)});
 save();console.error(error.stack||error);process.exitCode=1});
