'use strict';
/* Role D: source-exact 114 English E11/E13/E14 annual V4 browser interactions.
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
const OUT=path.resolve(process.env.SUDU_D_STAGE_OUT||'test-results/role-d-114-english-e11-e13-e14-staged');
const QS=['114-00-E-11','114-00-E-13','114-00-E-14'];
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const EXPECT_SHA=process.env.SUDU_D_EXPECT_SHA||'';
const AUTHOR_SHA='e0d4532c751127204e73af9cd9d3a95c52449131';
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
const roleBRoot=process.env.SUDU_D_AUTHOR_CHECKOUT||'_role_b_batch02';
const roleARoot=process.env.SUDU_D_IMAGE_CHECKOUT||'_role_a_original';
const SOURCE_A_SHA='47afa7108b92cbd37b81e0f2d9369a4a3c226ab1';
assert.equal(git(roleBRoot),AUTHOR_SHA,'new Role B lesson source HEAD moved');
assert.equal(git(roleARoot),SOURCE_A_SHA,'immutable Role A WebP source HEAD moved');
const EXPECT_SOURCE={
 '114-00-E-11':'646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036',
 '114-00-E-13':'074fb9847eda936d31dfd4503f3a7a12cbde9f89ddc888957d8eba4f17fa746c',
 '114-00-E-14':'6164a310c7d38229aaaf52df678121ee88f6242cf6611310badfb5b1b46714dd'
};
const EXPECT_DIGEST={
 '114-00-E-11':'3d250e8ecd621eda0f14f1839e6cf89b70b3649a1af0298611fedd9bbf57ceee',
 '114-00-E-13':'e62d80dd377d6dcd8872b416f2499dc6c1c6f185f14644b5bdab188ff5a910d1',
 '114-00-E-14':'b9c464e05fcec6969ef298d5744a9599af8e17612fc5cde2615a6a090e3c560e'
};
const EXPECT_IMAGE={
 '114-00-E-11':'ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0',
 '114-00-E-13':'81f4487c4012456b4f1c3449aa388f16d12de19b72cc844ae6b6269be76e9be7',
 '114-00-E-14':'388773561e436315452bdf0c28c792efa0983eb25538e8b3119926cd338f3a94'
};
const source=read('sudu/data/processed/114/questions.json');
const manifest=read('sudu/data/processed/114/webp-manifest.json');
const roleBBatch=read(roleBRoot+'/sudu/teaching-candidates/114-role-b-20261025-batch02/batch.json');
assert.equal(roleBBatch.role,'B');
assert.equal(roleBBatch.newReady,0);
assert.equal(roleBBatch.newLive,0);
const targetRoot='data/approved/webp/114/';
const qaDoc=read(roleARoot+'/sudu/data/processed/114/QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json');
assert.equal(qaDoc.releaseAllowed,false);
const buildSource=()=>QS.map(qid=>{
 assert.notEqual(qid,'114-00-E-12','independent E finding: unresolved US water bottle IPA must be quarantined');
 const q=source.questions.find(v=>v.questionId===qid);
 const m=manifest.items.find(v=>v.questionId===qid);
 const authorFile=roleBRoot+'/sudu/teaching-candidates/114-role-b-20261025-batch02/'+qid+'.json';
 const bBytes=fs.readFileSync(abs(authorFile));
 const b=JSON.parse(bBytes);
 const receipt=roleBBatch.items.find(x=>x.questionId===qid);
 const proof=qaDoc.items.find(x=>x.questionId===qid);
 assert(q&&m&&b&&receipt&&proof,'missing exact source-backed record '+qid);
 assert.equal(qid,b.questionId);
 assert.equal(b.kind,'NEW_AUTHOR_DRAFT');
 assert.equal(b.role,'B');
 assert.equal(b.review?.studentReleaseApproved,false);
 assert.equal(b.review?.formalReady,false);
 assert.equal(b.review?.independentAiContentReview?.status,'PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW');
 assert.equal(m.qaStatus,'PASS');
 assert.equal(m.output,b.source.webpPath);
 assert.equal(m.sha256,EXPECT_IMAGE[qid]);
 assert.equal(m.sha256,b.source.webpSha256);
 assert.equal(receipt.webpSha256,m.sha256);
 assert.equal(receipt.sourceRevision,EXPECT_SOURCE[qid]);
 assert.equal(receipt.composedTeachingSha256,EXPECT_DIGEST[qid]);
 assert.equal(SHA(bBytes),receipt.fileSha256,'B exact raw author file differs from batch receipt');
 assert.equal(fileSHA(roleARoot+'/'+m.output),m.sha256,'real A original WebP byte source SHA mismatch');
 assert.equal(proof.result,'PASS','original pixel individual QA NOT PASS');
 assert.equal(proof.reviewedWebpSha256,m.sha256,'original pixel QA SHA mismatched');
 assert.equal(proof.sourcePageSha256,m.sourceSha256,'original scan source page mismatched');
 assert.deepEqual(proof.cropPixels,m.crop,'real original QA pixel rectangle mismatched');
 assert.equal(proof.sourceOfficialPdfSha256,m.sourcePdfSha256);
 assert.equal(m.visualReviewEvidence?.reviewedSha256,m.sha256);
 assert.equal(m.sourcePdfSha256,b.source.questionPdfSha256);
 assert.equal(q.questionProvenance?.officialPdfSha256,b.source.questionPdfSha256);
 assert.equal(q.answerProvenance?.officialPdfSha256,b.source.answerPdfSha256);
 assert.equal(q.answer,b.knownAnswerCandidate);
 assert.equal(q.question,b.question);
 assert.deepEqual(q.options,b.options);
 assert.equal(canonical({question:q.question,options:q.options,singleQuestionWebpSha256:m.sha256}),
   EXPECT_SOURCE[qid],'source revision not exact authentic text+image');
 assert.equal(b.source.questionRevision,EXPECT_SOURCE[qid]);
 assert.equal(canonical(b.teaching),b.teachingCanonicalSha256,'authored teaching canonical SHA mismatch');
 assert.equal(receipt.teachingCanonicalSha256,b.teachingCanonicalSha256);
 const teach=b.teaching;
 assert.equal(teach.hasExamCalculation,false);
 assert.equal(teach.examCalculation,null);
 assert(teach.solvingSteps.length>=3);
 for(const L of 'ABCD'){
   for(const k of ['teacher','elementary','reason']){
    assert(typeof teach.optionExplanations?.[L]?.[k]==='string'&&
     teach.optionExplanations[L][k].trim().length>=8,'missing real Role B '+L+'/'+k);
   }
   assert.equal(teach.optionExplanations[L].isCorrect,L===q.answer,
     'exact authored correct/incorrect choice not matching source');
 }
 const composed=canonical({questionId:qid,sourceRevision:EXPECT_SOURCE[qid],
   webpSha256:m.sha256,teaching:teach,enrichment:b.enrichment});
 assert.equal(composed,b.composedTeachingSha256,'actual effective teaching SHA changed');
 assert.equal(composed,EXPECT_DIGEST[qid]);
 const news=b.enrichment.newsExample;
 assert.equal(news.notAnArticleQuote,true);
 assert(news.kind==='AUTHOR_COMPOSED_NEWS_CONTEXT_NOT_QUOTE');
 assert(news.english&&news.chinese&&news.highlightActualForm);
 assert(news.english.toLowerCase().includes(news.highlightActualForm.toLowerCase()),
   'author-highlighted form not in actual news example');
 const vocab=b.enrichment.englishVocabulary;
 assert(vocab.length>0);
 for(const v of vocab){
  assert(v.headword&&v.ipa&&v.meaningZh&&/^(初級|中級|高級)$/.test(v.level));
  assert(v.synonyms.length>0&&v.antonyms.length>0);
 }
 const extra={
  '中文翻譯':vocab.map(v=>v.headword+'：'+v.meaningZh).join('\n'),
  '發音':vocab.map(v=>v.headword+' '+v.ipa).join('\n'),
  '同意相關單字':vocab.map(v=>v.headword+'（'+v.level+'）→ '+v.synonyms.join('、')).join('\n'),
  '反意相關單字':vocab.map(v=>v.headword+'（'+v.level+'）→ '+v.antonyms.join('、')).join('\n'),
  '新聞時事例句':news.english,
  '新聞時事中文翻譯':news.chinese,
  '詞彙用法':vocab.map(v=>v.usageNote).filter(Boolean).join('\n')
 };
 // QA-only anticipated projection. MASTER must bind exact admitted source,
 // not silently drop authored news.highlightActualForm as existing publisher does.
 const authoredHighlights=b.enrichment.highlights.map(x=>x.text);
 const highlights=[...new Set([...authoredHighlights,news.highlightActualForm])];
 const publicQuestion={
  id:q.originalQuestionNumber,canonicalId:qid,year:114,subject:'英文',
  topic:teach.topic,question:q.question,options:q.options,answer:q.answer,
  memory:teach.memory,concept:teach.concept,extension:teach.extension,
  formula:teach.formula||'',teacherSummary:teach.teacherSummary,
  elementarySummary:teach.elementarySummary,
  optionExplanations:teach.optionExplanations,sourceText:teach.source,
  extra,highlights,
  examCalculation:null,image:targetRoot+qid+'.webp',imageSha256:m.sha256,
  qaOnlySourceRevision:EXPECT_SOURCE[qid],qaOnlyTeachingDigest:composed,
  qaOnlyAuthorRef:AUTHOR_SHA
 };
 return {qid,publicQuestion,rawWebP:roleARoot+'/'+m.output,
  sourceRevision:EXPECT_SOURCE[qid],imageSha256:m.sha256,digest:composed,
  english:news.english,chinese:news.chinese,highlight:news.highlightActualForm,vocab};
});
const qs=buildSource();
const payload={schemaVersion:1,year:114,approvedCount:qs.length,
  questions:qs.map(x=>x.publicQuestion),
  QA_ONLY_UNPUBLISHABLE:true,studentReleaseApproved:false,
  actualPublishedApproved114Count:0};
const report={
 schemaVersion:1,role:'D',taskId:'D-114-EN11-13-14-REAL-V4-STAGED-20261026-01',
 purpose:'AUTHENTIC_SOURCE_STAGED_YEARLY_V4_QUIZ_NOT_PUBLISHER_ADMISSION',
 qaOnlyIntercept:true,realApprovedArtifact:false,eligibleForRelease:false,
 headerSha:head,roleBHead:AUTHOR_SHA,roleAHead:SOURCE_A_SHA,originalPixelQaDocSha:fileSHA(roleARoot+'/sudu/data/processed/114/QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json'),
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
 fs.writeFileSync(path.join(OUT,'staged-annual-114-English-E11-E13-E14-results.json'),JSON.stringify(report,null,2)+'\n')}
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
     // All THREE selected real source originals (E12 independently quarantined), but interception bypasses the
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
