'use strict';
/* Role D: source-exact 114 English E07-E09 annual V4 browser interactions.
 * QA-ONLY INTERCEPT: NOT the published approved bank, NOT full release UIQA.
 * Every question, choice, official answer candidate, WebP byte and teaching
 * explanation comes from existing original source + immutable B author files.
 * This test NEVER writes a release/approval/reviewer flag or Pages artifact.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {URL:NativeURL}=require('node:url');
const cp=require('node:child_process');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const URL=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
const OUT=path.resolve(process.env.SUDU_D_STAGE_OUT||'test-results/role-d-114-english-staged');
const QS=['114-00-E-07','114-00-E-08','114-00-E-09'];
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const EXPECT_SHA=process.env.SUDU_D_EXPECT_SHA||'';
const AUTHOR_SHA='32256dd286bd95ea78ae26938cf8184b4ec72949';
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
const blobSHA=b=>crypto.createHash('sha1').update(Buffer.concat([
  Buffer.from('blob '+b.length),Buffer.from([0]),b])).digest('hex');
const sorted=x=>Array.isArray(x)?x.map(sorted):
 x!==null&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sorted(x[k])])):x;
const canonical=x=>SHA(Buffer.from(JSON.stringify(sorted(x)),'utf8'));
const abs=p=>path.join(ROOT,p);
const read=p=>JSON.parse(fs.readFileSync(abs(p),'utf8'));
const fileSHA=p=>SHA(fs.readFileSync(abs(p)));
const git=dir=>cp.execFileSync('git',['rev-parse','HEAD'],{cwd:abs(dir||'.'),encoding:'utf8'}).trim();
const head=git();
if(process.env.SUDU_D_QA_ONLY!=='1')throw Error('QA_ONLY staging requires explicit CI flag; never use this as publication');
if(EXPECT_SHA)assert.equal(head,EXPECT_SHA,'audited exact-HEAD mismatch');
const roleBRoot=process.env.SUDU_D_AUTHOR_CHECKOUT||'_role_b_current';
assert.equal(git(roleBRoot),AUTHOR_SHA,'Role B authored lesson source HEAD changed');
const sourceRevisionExpected={
 '114-00-E-07':'8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c',
 '114-00-E-08':'09a56002bd224815a9d413ad9a5db3565af0837e16c58ec031bd851f17d69b6c',
 '114-00-E-09':'0346c84990c84812b9705adcfab7bb6d51877dce1e07c7ba4cc3e74797583cdd'
};
const digestExpected={
 '114-00-E-07':'f65c50e011f57025f2ffc9ff7df107f16f4bd6c6e3b1c64c75169bb77c35dd5b',
 '114-00-E-08':'6dd7125dddf83293dc52a0fcbc35b113918f92f9b2fca9e6b0dc0ca06442d5b1',
 '114-00-E-09':'45b33a02da4059fc7efc2cae7d9c7914732d53e967c195d004cc879e212fa584'
};
const source=read('sudu/data/processed/114/questions.json');
const manifest=read('sudu/data/processed/114/webp-manifest.json');
const targetRoot='data/approved/webp/114/';
const buildSource=()=>QS.map(qid=>{
 const q=source.questions.find(v=>v.questionId===qid);
 const m=manifest.items.find(v=>v.questionId===qid);
 const authorFile=roleBRoot+'/sudu/teaching-candidates/114-role-b-20261025/'+qid+'.json';
 const b=read(authorFile);
 const teachFile=b.source?.baseTeachingEvidencePath;
 const previousBytes=fs.readFileSync(abs(teachFile));
 const original=JSON.parse(previousBytes);
 const OCR=read('sudu/data/processed/114/review-evidence/'+qid+'-ocr.json');
 const final=read('sudu/data/processed/114/review-evidence/'+qid+'-official.json');
 assert(q&&m&&b&&original&&OCR&&final,'actual Q/A/B original missing '+qid);
 assert.equal(qid,b.questionId);
 assert.equal(b.kind,'PRESERVE_BASE_AND_ENRICH');
 assert.equal(b.teaching,null,'do not synthesize missing original lessons');
 assert.equal(b.review?.formalReady,false);
 assert.equal(b.review?.studentReleaseApproved,false);
 assert.equal(b.review?.independentAiContentReview?.status,'PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW');
 assert.equal(m.qaStatus,'PASS','historical source image QA is not formal independent teaching QA');
 assert.equal(m.output,b.source.webpPath);
 assert.equal(m.sha256,b.source.webpSha256);
 assert.equal(fileSHA(m.output),m.sha256,'actual raw WebP byte mismatch');
 assert.equal(m.visualReviewEvidence?.reviewedSha256,m.sha256);
 assert.equal(m.sourceSha256,b.source.sourcePageWebpSha256);
 assert.equal(OCR.question,q.question);
 assert.deepEqual(OCR.options,q.options);
 assert.equal(OCR.webpSha256,m.sha256);
 assert.equal(final.finalAnswer,b.answer);
 assert.equal(q.answer,b.answer);
 assert.equal(final.officialPdfSha256,b.source.officialAnswerPdfSha256);
 assert.equal(m.sourcePdfSha256,b.source.questionPdfSha256);
 assert.equal(blobSHA(previousBytes),b.source.baseTeachingGitBlobSha,'original teacher-perspective text git blob changed');
 assert.equal(canonical(original.content),b.source.baseTeachingCanonicalSha256,'original effective teacher+elementary lesson changed');
 assert.equal(original.questionRevision,b.source.questionRevision);
 assert.equal(canonical({question:q.question,options:q.options,singleQuestionWebpSha256:m.sha256}),
  b.source.questionRevision,'official question and four choices revision differs');
 assert.equal(b.source.questionRevision,sourceRevisionExpected[qid]);
 const teach=structuredClone(original.content);
 const overrides=b.optionReasonOverrides||{};
 for(const [L,reason] of Object.entries(overrides)){
   assert('ABCD'.includes(L));
   assert(typeof reason==='string'&&reason.trim().length>20);
   teach.optionExplanations[L].reason=reason;
 }
 for(const L of 'ABCD')for(const field of ['teacher','elementary','reason'])
   assert(teach.optionExplanations?.[L]?.[field]?.trim().length>5,
     'missing REAL authored '+L+' '+field+' for '+qid);
 const effective=canonical({questionId:qid,sourceRevision:b.source.questionRevision,
   webpSha256:m.sha256,teaching:teach,enrichment:b.enrichment});
 assert.equal(effective,b.composedTeachingSha256,'B current teaching digest invalid '+qid);
 assert.equal(effective,digestExpected[qid]);
 const news=b.enrichment.newsExample;
 assert(news.english&&news.chinese&&news.english.toLowerCase().includes(news.highlightActualForm.toLowerCase()));
 assert(news.notAnArticleQuote===true,'news sentence must be labelled author-created');
 const vocab=b.enrichment.englishVocabulary;
 assert(Array.isArray(vocab)&&vocab.length>0);
 for(const term of vocab){
   assert(term.headword&&term.ipa&&/^(初級|中級|高級)$/.test(term.level));
   assert(term.meaningZh&&Array.isArray(term.synonyms)&&Array.isArray(term.antonyms));
 }
 const extra={
   '中文翻譯':vocab.map(x=>x.headword+'：'+x.meaningZh).join('\n'),
   '發音':vocab.map(x=>x.headword+' '+x.ipa).join('\n'),
   // The level belongs to the AUTHORED headword only. Never invent a
   // CEFR grade for the individual synonyms/antonyms.
   '同意相關單字':vocab.map(x=>x.headword+'（'+x.level+'）→ '+x.synonyms.join('、')).join('\n'),
   '反意相關單字':vocab.map(x=>x.headword+'（'+x.level+'）→ '+x.antonyms.join('、')).join('\n'),
   '新聞時事例句':news.english,
   '新聞時事中文翻譯':news.chinese,
   '詞彙用法':vocab.map(x=>x.usageNote).filter(Boolean).join('\n')
 };
 // This projection is a QA-only EXPECTED STUDENT VIEW, NOT the active
 // publisher. MASTER must source-admit independently and then map exactly.
 const publicQuestion={
  id:q.originalQuestionNumber,canonicalId:qid,year:114,subject:'英文',
  topic:teach.topic,question:q.question,options:q.options,answer:b.answer,
  memory:teach.memory,concept:teach.concept,extension:teach.extension,
  formula:teach.formula||'',teacherSummary:teach.teacherSummary,
  elementarySummary:teach.elementarySummary,
  optionExplanations:teach.optionExplanations,sourceText:teach.source,
  extra,highlights:b.enrichment.highlights.map(x=>x.text),
  examCalculation:null,image:targetRoot+qid+'.webp',imageSha256:m.sha256,
  qaOnlySourceRevision:b.source.questionRevision,
  qaOnlyTeachingDigest:effective,qaOnlyAuthorRef:AUTHOR_SHA
 };
 assert(!teach.hasExamCalculation&&teach.examCalculation===null,
  'English no-math should not invent a calculation block');
 return {qid,publicQuestion,rawWebP:m.output,
   sourceRevision:b.source.questionRevision,
   imageSha256:m.sha256,digest:effective,
   english:news.english,chinese:news.chinese,highlight:news.highlightActualForm,
   vocab};
});
const qs=buildSource();
const payload={schemaVersion:1,year:114,approvedCount:qs.length,
  questions:qs.map(x=>x.publicQuestion),
  QA_ONLY_UNPUBLISHABLE:true,studentReleaseApproved:false,
  actualPublishedApproved114Count:0};
const report={
 schemaVersion:1,role:'D',taskId:'D-114-EN07-09-STAGED-REAL-QUIZ-20261025-06',
 purpose:'AUTHENTIC_SOURCE_STAGED_YEARLY_V4_QUIZ_NOT_PUBLISHER_ADMISSION',
 qaOnlyIntercept:true,realApprovedArtifact:false,eligibleForRelease:false,
 headerSha:head,roleBHead:AUTHOR_SHA,
 htmlSHA:fileSHA('sudu/v4-115-multisubject-review-demo.html'),
 runtimeSHA:fileSHA('sudu/verified-questions-runtime.js'),
 sourceJsonSha:fileSHA('sudu/data/processed/114/questions.json'),
 manifestSHA:fileSHA('sudu/data/processed/114/webp-manifest.json'),
 exactSource:qs.map(x=>({qid:x.qid,sourceRevision:x.sourceRevision,
    webpSha256:x.imageSha256,composedTeachingSha256:x.digest})),
 ciRun:process.env.GITHUB_RUN_ID||null,
 cases:[],errors:[],status:'STARTED'
};
function save(){fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'staged-annual-114-English-results.json'),JSON.stringify(report,null,2)+'\n')}
function checkBytes(){
 const staged=[];
 for(const r of qs){
  const dest=abs('_site/sudu/'+targetRoot+r.qid+'.webp');
  fs.mkdirSync(path.dirname(dest),{recursive:true});
  fs.copyFileSync(abs(r.rawWebP),dest);
  assert.equal(SHA(fs.readFileSync(dest)),r.imageSha256,'QA-only staged WebP byte changed');
  staged.push(dest);
 }
 return staged;
}
const temporaryFiles=checkBytes();
const act=(loc,touch)=>touch?loc.tap({timeout:12000}):loc.click({timeout:12000});
async function layout(page,label){
 return await page.evaluate(()=>{
  const w=document.documentElement.scrollWidth;
  const t=[...document.querySelectorAll('#questionCard h1,#answerCard .opt-text,#guideCard .news-zh')].
   filter(e=>e.offsetWidth).filter(e=>e.scrollWidth>e.clientWidth+3&&getComputedStyle(e).overflowX==='hidden').
   map(e=>({text:e.textContent?.slice(0,40),scroll:e.scrollWidth,client:e.clientWidth}));
  return {screen:innerWidth,document:w,clipped:t};
 }).then(g=>{assert(g.document<=g.screen+1,label+' horizontal overflow '+JSON.stringify(g));
  assert.deepEqual(g.clipped,[],label+' clipped student text');return g});
}
async function fontGate(page,qid,label){
 const x=await page.evaluate(()=>{
  const el=document.querySelector('#guideCard .news-zh');
  if(!el)return null;
  const ctx=document.createElement('canvas').getContext('2d',{willReadFrequently:true});
  ctx.canvas.width=80;ctx.canvas.height=80;ctx.fillStyle='#000';
  ctx.font='48px '+getComputedStyle(el).fontFamily;ctx.textBaseline='top';
  const glyphs=['中','文','字','譯'].map(c=>{
   ctx.clearRect(0,0,80,80);ctx.fillText(c,5,4);
   const data=ctx.getImageData(0,0,80,80).data;
   let h=2166136261,n=0;
   for(let i=3;i<data.length;i+=4){const a=data[i];if(a>32)n++;h=Math.imul(h^a,16777619)>>>0}
   return {char:c,pixels:n,hash:h.toString(16)};
  });
  return {family:getComputedStyle(el).fontFamily,glyphs};
 });
 assert(x&&x.glyphs.every(g=>g.pixels>70)&&new Set(x.glyphs.map(g=>g.hash)).size>=3,
   label+' illegible Traditional Chinese fallback '+JSON.stringify(x));
 return x;
}
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of SIZES)for(const theme of ['light','dark']){
    const touch=width<=430;
    const context=await browser.newContext({viewport:{width,height},hasTouch:touch,reducedMotion:'reduce'});
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    try{
     // All THREE are true source originals, but interception bypasses the
     // real publisher. This deliberately NEVER creates a READY certificate.
     await page.route('**/sudu/data/approved/114.json',route=>
      route.fulfill({status:200,contentType:'application/json; charset=utf-8',
        body:JSON.stringify(payload)}));
     await page.goto(URL+'v4-115-multisubject-review-demo.html?year=114',
      {waitUntil:'domcontentloaded'});
     await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='114',
       null,{timeout:30000});
     await page.evaluate(()=>{document.body.dataset.roleDQaOnly='NOT_APPROVED_SOURCE_INTERCEPT'});
     await page.addStyleTag({content:
       'body::after{content:"QA-ONLY / UNAPPROVED / NOT LIVE";position:fixed;bottom:2px;right:2px;'+
       'background:#8b0000;color:white;font:bold 11px sans-serif;padding:3px 6px;'+
       'z-index:100000;pointer-events:none;border-radius:3px}'});
     assert(await page.locator('#homeView').isVisible());
     assert.equal(await page.locator('#studyView').isVisible(),false);
     // The original 35-Demo V4 can seed an unanswered default record at
     // boot even on an annual route. Preserve its ACTUAL baseline byte-for-byte
     // rather than assuming the Demo localStorage key never exists.
     const demoOriginal=await page.evaluate(()=>
       localStorage.getItem('tvet-115-multisubject-demo-v1'));
     await page.locator('#homeSubjectSel').selectOption('英文');
     await page.locator('#studyView').waitFor({state:'visible',timeout:12000});
     if(theme==='dark')await act(page.locator('#themeBtn'),touch);
     assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
     for(let i=0;i<qs.length;i++){
      const r=qs[i],q=r.publicQuestion,label=r.qid+' '+width+'x'+height+' '+theme;
      const expected=await page.evaluate(()=>({
        year:pageYear(),question:qnow()?.question,options:qnow()?.options,
        digest:qnow()?.qaOnlyTeachingDigest,id:qnow()?.canonicalId,
        sourceRevision:qnow()?.qaOnlySourceRevision,
        answer:qnow()?.answer,explanations:qnow()?.optionExplanations
      }));
      assert.equal(expected.year,'114');
      assert.equal(expected.id,r.qid,label+' staged canonical ID misbound');
      assert.equal(expected.question,q.question,label+' real stem differs');
      assert.deepEqual(expected.options,q.options,label+' real four options changed');
      assert.equal(expected.digest,r.digest,label+' actual effective teaching digest not attached');
      assert.equal(expected.sourceRevision,r.sourceRevision);
      assert.equal(expected.answer,q.answer);
      assert.deepEqual(expected.explanations,q.optionExplanations,
        label+' actual B authored four option teaching changed');
      // CSS must preserve actual exam cloze spacing; comparing only a
      // whitespace-normalized DOM string would conceal the real V4 defect.
      const stem=await page.locator('#questionCard h1').evaluate(el=>({
        text:el.textContent,visible:el.innerText,whiteSpace:getComputedStyle(el).whiteSpace
      }));
      assert.equal(stem.text,q.question,label+' original source stem bytes changed');
      assert.equal(stem.whiteSpace,'pre-wrap',label+' meaningful official exam whitespace collapsed');
      if(/ {5,}/.test(q.question))assert(/ {5,}/.test(stem.visible),
        label+' full original cloze blank is no longer visible in Chromium');
      const options=page.locator('#answerCard .opt');
      assert.equal(await options.count(),4);
      for(let k=0;k<4;k++){
       const el=options.nth(k);
       assert.equal(await el.getAttribute('data-a'),'ABCD'[k]);
       assert.equal((await el.locator('.opt-text').innerText()).trim(),q.options[k].trim());
      }
      const image=page.locator('#questionCard img').first();
      assert.equal(await image.getAttribute('src'),q.image);
      await image.scrollIntoViewIfNeeded();
      const decoded=await image.evaluate(async el=>{
       await el.decode();
       const box=el.getBoundingClientRect(),parent=el.parentElement.getBoundingClientRect();
       return {nw:el.naturalWidth,nh:el.naturalHeight,w:box.width,h:box.height,pw:parent.width};
      });
      assert(decoded.nw>0&&decoded.nh>0&&decoded.w<=decoded.pw+1,
        label+' original image missing or overflows');
      assert(Math.abs(decoded.w/decoded.h-decoded.nw/decoded.nh)/(decoded.nw/decoded.nh)<0.025,
        label+' original WebP aspect changed');
      const imageHTTP=await page.request.get(new NativeURL('./'+q.image,URL).href);
      assert(imageHTTP.ok(),label+' WebP HTTP '+imageHTTP.status());
      assert.equal(SHA(await imageHTTP.body()),r.imageSha256);
      await layout(page,label+' before answer');
      if(!touch){
        await options.first().scrollIntoViewIfNeeded();
        const normal=await options.first().evaluate(e=>getComputedStyle(e).backgroundColor);
        await options.first().hover();await page.waitForTimeout(150);
        const hover=await options.first().evaluate(e=>getComputedStyle(e).backgroundColor);
        assert.notEqual(hover,normal,label+' no real mouse-hover effect');
      }
      const wrong=q.answer==='A'?'B':'A';
      await act(page.locator('#answerCard .opt[data-a="'+wrong+'"]'),touch);
      await page.locator('#guideCard.show').waitFor({timeout:12000});
      assert.equal(await page.locator('#answerCard .option-detail').count(),4);
      assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
      assert.equal(await page.locator('#answerCard .opt.wrong').count(),1);
      for(const L of 'ABCD'){
        const detail=q.optionExplanations[L];
        const actual=await page.locator('#answerCard .opt[data-a="'+L+'"] + .option-detail').innerText();
        for(const key of ['teacher','elementary','reason']){
          assert(actual.replace(/\s/g,'').includes(detail[key].replace(/反向檢查/g,'相反意思').replace(/\s/g,'')),
            label+' option '+L+' '+key+' author original content lost');
        }
      }
      assert.equal(await page.locator('#guideCard .calculation-step').count(),0,
        label+' invented calculation on English nonmath');
      const guide=await page.locator('#guideCard').innerText();
      assert(guide.includes(r.chinese),label+' actual B Chinese news missing');
      assert(guide.includes(r.english),label+' actual B English news missing');
      assert(guide.includes(q.memory),label+' source mnemonic missing');
      for(const v of r.vocab){
        assert(guide.includes(v.ipa),label+' original IPA missing '+v.headword);
        assert(guide.includes(v.level),label+' level missing '+v.headword);
        for(const syn of v.synonyms)assert(guide.includes(syn),label+' source synonym lost '+syn);
        for(const ant of v.antonyms)assert(guide.includes(ant),label+' source antonym lost '+ant);
      }
      const actualMarks=await page.locator('#guideCard .news-en mark.exam-highlight').allInnerTexts();
      assert(actualMarks.some(x=>x.toLowerCase()===r.highlight.toLowerCase()),
        label+' authored news highlighted form absent');
      for(const word of actualMarks)assert(r.english.toLowerCase().includes(word.toLowerCase()),
        label+' highlighted words not in actual sentence');
      assert.equal(await page.locator('#guideCard .news-zh').count(),1);
      const font=await fontGate(page,r.qid,label);
      const scroll=await page.locator('#correctAnswer').evaluate(el=>el.getBoundingClientRect().top);
      assert(Number.isFinite(scroll),label+' correct answer anchor broken');
      await layout(page,label+' after answer');
      const img=path.join(OUT,r.qid+'-'+width+'x'+height+'-'+theme+'.png');
      await page.screenshot({path:img,fullPage:false,animations:'disabled'});
      report.cases.push({status:'STAGED_COMPONENT_AND_REAL_QUIZ_FLOW_PASS_NOT_RELEASE',
        qid:r.qid,sourceRevision:r.sourceRevision,imageSha256:r.imageSha256,
        composedTeachingSha256:r.digest,width,height,theme,input:touch?'real_touch':'real_mouse',
        realStemFourOptions:true,originalSourceWebP:true,
        correctWrongColors:true,allFourDualExplanations:true,
        CJKGlyphs:true,fontFamily:font.family,realNewsHighlight:true,
        IPAandVocabulary:true,noCalculation:true,reviewPending:true,
        screenshot:path.relative(OUT,img)});
      if(i<qs.length-1){
        const next=page.locator('#nextBtn');await next.scrollIntoViewIfNeeded();
        await act(next,touch);
      }
     }
     // Exercise genuine 114-year mistake list using all three wrong answers.
     const handle=page.locator('#navHandle');
     if(await handle.getAttribute('aria-expanded')!=='true')await act(handle,touch);
     assert.equal(await handle.getAttribute('aria-expanded'),'true');
     await act(page.locator('#reviewTop'),touch);
     await page.locator('#reviewView.show').waitFor({timeout:12000});
     assert.equal(await page.locator('#reviewList .wrong-card').count(),3,
       'staged 114 annual wrong-answer review lacks actual three mistakes');
     const stored=await page.evaluate(()=>({
       annual:localStorage.getItem('tvet-verified-114-v1'),
       demo:localStorage.getItem('tvet-115-multisubject-demo-v1')
     }));
     assert(stored.annual&&JSON.parse(stored.annual).records,'annual isolated student data missing');
     assert.equal(stored.demo,demoOriginal,
       '114 yearly answering mutated original 35-Demo progress from startup baseline');
     assert.deepEqual(errors,[],'uncaught browser errors');
    }catch(e){
      report.errors.push({width,height,theme,error:String(e.stack||e),browserErrors:errors});
    }finally{
      await context.close();save();
    }
   }
 }finally{
   await browser.close();
   // QA-only staged original WebPs must not survive even this temporary build.
   for(const dest of temporaryFiles)try{fs.unlinkSync(dest)}catch{}
 }
 report.status=report.errors.length?'QA_ONLY_STAGED_FAILED':'QA_ONLY_STAGED_PASS_NEEDS_REAL_PUBLISHER_ADMISSION';
 save();
 if(report.errors.length)console.error('FIRST_STAGED_QA_FAILURES',JSON.stringify(report.errors.slice(0,5),null,2));
 assert.equal(report.errors.length,0,'some original annual-question staged V4 workflows failed');
 assert.equal(report.cases.length,48,'not all real 3 annual questions x 8 viewports x 2 themes tested');
 console.log('PASS QA-ONLY 114 English original question/answer UI 3x8x2; NOT formal publisher, NOT READY/LIVE');
})().catch(error=>{
 report.errors.push({fatal:String(error.stack||error)});
 report.status='QA_ONLY_STAGED_FAILED';save();
 console.error(error.stack||error);process.exitCode=1;
});
