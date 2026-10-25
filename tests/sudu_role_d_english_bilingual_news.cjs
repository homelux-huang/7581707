'use strict';
/* Role D annual-English news renderer regression using the actual three
 * 114 candidate records. This is COMPONENT ONLY: no teacher review,
 * no admission, no approved mutation and no full-question UIQA certificate.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const cp=require('node:child_process');
const {chromium}=require('playwright');

const ROOT=path.resolve(__dirname,'..');
const OUT=path.resolve(process.env.SUDU_D_NEWS_OUTPUT||'test-results/role-d-english-news');
const URL=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
const EXPECT_SHA=process.env.SUDU_D_NEWS_EXPECT_SHA;
const mainSHA=process.env.SUDU_D_NEWS_MAIN_SHA||null;
const sizes=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const candidateIds=['114-00-E-07','114-00-E-08','114-00-E-09'];
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const hashFile=p=>sha(fs.readFileSync(path.join(ROOT,p)));
const realSHA=cp.execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim();
if(EXPECT_SHA)assert.equal(realSHA,EXPECT_SHA,'workflow did not checkout exact audited HEAD');

function assertSourceRecords(){
  const records=[];
  for(const id of candidateIds){
    const folder='sudu/teaching-candidates/114-role-b-20261025/';
    const file=folder+id+'.json';
    const c=read(file);
    const ocr=read('sudu/data/processed/114/review-evidence/'+id+'-ocr.json');
    const prior=read('sudu/data/processed/114/review-evidence/'+id+'-teaching.json');
    const n=c.enrichment?.newsExample,source=c.source;
    assert.equal(c.questionId,id);
    assert.equal(c.year,114);
    assert.equal(c.subject,'英文');
    assert.equal(c.review?.humanTeacherVerified,false,'not a human-reviewed teaching record');
    assert.equal(c.review?.formalReady,false);
    assert.equal(c.review?.studentReleaseApproved,false);
    assert.equal(prior.questionRevision,source.questionRevision);
    assert.equal(ocr.questionRevision,source.questionRevision);
    assert.equal(ocr.webpSha256,source.webpSha256);
    assert.equal(prior.webpSha256,source.webpSha256);
    assert.equal(source.webpPath,ocr.originalWebpPath);
    assert(Array.isArray(ocr.options)&&ocr.options.length===4&&ocr.options.every(x=>x.trim()),
      'original official paper four choices incomplete');
    assert(ocr.question.trim()&&n.english.trim()&&n.chinese.trim()&&n.highlightActualForm.trim(),
      'real English question/news/translation missing');
    assert(n.english.toLowerCase().includes(n.highlightActualForm.toLowerCase()),
      'the declared highlight does not occur in real candidate English text');
    assert(/^[0-9a-f]{64}$/.test(c.composedTeachingSha256||''),'missing exact authored digest');
    const absolute=path.join(ROOT,source.webpPath);
    assert(fs.existsSync(absolute),'actual original question WebP missing '+source.webpPath);
    assert.equal(hashFile(source.webpPath),source.webpSha256,
      'the original local WebP SHA differs from source record');
    const highlights=(c.enrichment.highlights||[]).map(x=>x.text);
    assert(highlights.includes(n.highlightActualForm),
      'news highlight must be a declared original candidate word form');
    records.push({
      id,question:ocr.question,options:ocr.options,answer:c.answer,sourceRevision:source.questionRevision,
      imageSha256:source.webpSha256,imagePath:source.webpPath,sourcePDFSha256:source.questionPdfSha256,
      composedTeachingSha256:c.composedTeachingSha256,sourceFileSha256:hashFile(file),
      candidate:{canonicalId:id,subject:'英文',id:Number(id.slice(-2)),question:ocr.question,
        options:ocr.options,answer:c.answer,highlights,
        extra:{'新聞時事例句':n.english,'新聞時事中文翻譯':n.chinese}},
      expectedEnglish:n.english,expectedChinese:n.chinese,expectedHighlight:n.highlightActualForm
    });
  }
  return records;
}

const source=assertSourceRecords();
const report={
 schemaVersion:1,role:'D',taskId:'D-ENGLISH-BILINGUAL-V4-20261025-01',
 purpose:'CANDIDATE_BILINGUAL_COMPONENT_REGRESSION_NOT_FULL_QUESTION_UIQA',
 release:'NO_RELEASE',eligibleForReady:false,teacherApprovalClaimed:false,
 checkoutSha:realSHA,mainBaseSha:mainSHA,
 htmlSha256:hashFile('sudu/v4-115-multisubject-review-demo.html'),
 runtimeSha256:hashFile('sudu/verified-questions-runtime.js'),
 sourceEvidence:source.map(({id,sourceRevision,imageSha256,composedTeachingSha256,
   sourcePDFSha256,sourceFileSha256})=>({
   id,sourceRevision,imageSha256,composedTeachingSha256,sourcePDFSha256,sourceFileSha256
 })),
 ciRunId:process.env.GITHUB_RUN_ID||null,viewports:sizes,themes:['light','dark'],
 checks:[],errors:[],status:'IN_PROGRESS'
};
function save(){
 fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'results.json'),JSON.stringify(report,null,2)+'\n');
}
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of sizes){
   for(const theme of ['light','dark']){
    const touch=width<=430;
    const context=await browser.newContext({viewport:{width,height},hasTouch:touch,reducedMotion:'reduce'});
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    try{
     await page.goto(URL+'v4-115-multisubject-review-demo.html',{waitUntil:'domcontentloaded'});
     assert(await page.locator('#homeView').isVisible(),'real 35 Demo home disappeared');
     assert.equal(await page.locator('#studyView').isVisible(),false);
     await page.locator('#homeYearSel').selectOption('demo');
     await page.locator('#homeSubjectSel').selectOption('英文');
     await page.locator('#studyView').waitFor({state:'visible'});
     if(theme==='dark'){
       if(touch)await page.locator('#themeBtn').tap();
       else await page.locator('#themeBtn').click();
     }
     assert.equal(await page.locator('html').getAttribute('data-theme'),theme,
       'real dark/light UI control mismatch');
     assert.equal(await page.locator('#answerCard .opt').count(),4,
       'original English Demo A-D choices changed');

     const demoNews=await page.evaluate(()=>{
       const q=QUESTIONS.find(q=>q.subject==='英文');
       const en=q.extra?.['新聞時事例句'];
       return en?formatStudyValue(q,'新聞時事例句',en):'';
     });
     if(demoNews)assert(demoNews.includes('AI 學習示例'),
       'uncanonicalized original Demo news should retain Demo-specific annotation');

     for(const r of source){
       const value=await page.evaluate(q=>{
         const ordered=guideEntries(q);
         const entry=ordered.find(([name])=>name==='新聞時事例句');
         if(!entry)throw Error('actual candidate annual English guide omitted news');
         const container=document.getElementById('guideCard');
         // Display solely inside this isolated browser context, NEVER update
         // QUESTIONS, approved JSON, Page storage or public student release.
         container.classList.add('show');
         container.innerHTML='<h2>英文解說重點｜未核准候選元件測試</h2>'+
           '<div class="guide-grid"><section class="guide-block"><h3>新聞時事例句</h3><p>'+
           formatStudyValue(q,'新聞時事例句',entry[1])+'</p></section></div>';
         const el=container.querySelector('.guide-block');
         const english=el.querySelector('.news-en');
         const chinese=el.querySelector('.news-zh');
         const marks=[...el.querySelectorAll('mark.exam-highlight')].map(m=>m.textContent);
         const html=el.innerHTML;
         const strip={...q,extra:{...q.extra}};
         delete strip.extra['新聞時事中文翻譯'];
         const noChinese=formatStudyValue(strip,'新聞時事例句',q.extra['新聞時事例句']);
         return {
           english:english?.textContent,chinese:chinese?.textContent,marks,html,
           noChinese,newsHeadings:ordered.filter(([key])=>key==='新聞時事例句').length,
           duplicateChineseHeading:ordered.some(([key])=>key==='新聞時事中文翻譯')
         };
       },r.candidate);
       assert.equal(value.english,r.expectedEnglish,r.id+' candidate English altered');
       assert.equal(value.chinese,'中文：'+r.expectedChinese,r.id+' Chinese translation missing/modified');
       assert(value.marks.some(m=>m.toLowerCase()===r.expectedHighlight.toLowerCase()),
         r.id+' actual highlighted term missing');
       for(const term of value.marks)assert(r.expectedEnglish.includes(term),
         r.id+' generated highlight not in actual news English');
       assert.equal(value.newsHeadings,1);
       assert.equal(value.duplicateChineseHeading,false,
         'English and Chinese news should share one original guide block');
       assert(!value.noChinese.includes('news-zh')&&!value.noChinese.includes(r.expectedChinese),
         'annual English must not invent/fall back to Demo news translation when absent');
       assert(!value.html.includes('After heavy rain')&&!value.html.includes('outdoor seats'),
         'Demo text was illegally copied to a formal-year candidate');

       const block=page.locator('#guideCard .guide-block');
       await block.scrollIntoViewIfNeeded();
       const geometry=await page.evaluate(()=>{
         const e=document.querySelector('#guideCard .guide-block');
         const eng=e.querySelector('.news-en'),z=e.querySelector('.news-zh');
         const style=getComputedStyle(e);
         return {innerWidth,scrollWidth:document.documentElement.scrollWidth,
          blockWidth:e.clientWidth,blockScrollWidth:e.scrollWidth,
          englishWidth:eng.scrollWidth,englishClientWidth:eng.clientWidth,
          chineseWidth:z.scrollWidth,chineseClientWidth:z.clientWidth,
          fontSize:style.fontSize};
       });
       assert(geometry.scrollWidth<=geometry.innerWidth+1,
         r.id+' '+width+'px '+theme+' horizontal overflow '+JSON.stringify(geometry));
       assert(geometry.blockScrollWidth<=geometry.blockWidth+3,
         r.id+' '+width+'px '+theme+' overflow inside the news guide');
       assert(geometry.englishWidth<=geometry.englishClientWidth+3,
         r.id+' '+width+'px '+theme+' clipped English sentence');
       assert(geometry.chineseWidth<=geometry.chineseClientWidth+3,
         r.id+' '+width+'px '+theme+' clipped Chinese sentence');
       const screenshot=path.join(OUT,r.id+'-'+width+'x'+height+'-'+theme+'.png');
       await block.screenshot({path:screenshot,animations:'disabled'});
       report.checks.push({questionId:r.id,width,height,theme,
         event:touch?'real_touch_theme':'real_mouse_theme',
         bilingualTranslation:true,exactEnglish:true,actualHighlightedString:true,
         noDemoNewsFallback:true,noLayoutOverflow:true,
         imageSha256:r.imageSha256,sourceRevision:r.sourceRevision,
         composedTeachingSha256:r.composedTeachingSha256,
         screenshot:path.relative(OUT,screenshot),
         status:'COMPONENT_PASS_NOT_FULL_UIQA'});
     }
     assert.deepEqual(errors,[],'unexpected browser JS errors');
    }catch(e){
     report.errors.push({width,height,theme,error:String(e?.stack||e),browserErrors:errors});
    }finally{
     await context.close();
     save();
    }
   }
  }
 }finally{await browser.close()}
 report.status=report.errors.length?'COMPONENT_FAILED':'COMPONENT_PASS_NOT_FULL_UIQA';
 save();
 assert.equal(report.errors.length,0,'candidate news renderer regressions failed; see '+OUT);
 assert.equal(report.checks.length,3*8*2,'not all three exact-source candidates x8x2 were exercised');
 console.log('Role D SOURCE-BOUND English news component 3 actual candidates x8x2: PASS; NEW READY=0, UIQA(full)=NOT_VERIFIED, LIVE=0');
})().catch(e=>{
 report.status='COMPONENT_FAILED';
 report.errors.push({fatal:String(e?.stack||e)});
 save();
 console.error(e.stack||e);
 process.exitCode=1;
});
