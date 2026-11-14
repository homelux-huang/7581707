'use strict';
/*
 * ROLE D 114 E12 actual V4 NEGATIVE/HOLD Chromium regression.
 *
 * No page.route interception, no synthetic approved row, no session override.
 * This confirms the currently unapproved E12 remains absent from the student
 * answer UI. 8x2 screenshots are HOLD evidence, NOT formal UIQA 16/16.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const cp=require('node:child_process');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const OUT=path.join(ROOT,'test-results/role-d-114-e12-actual-v4-hold-20261107');
const SITE=process.env.SUDU_D_SITE||'http://127.0.0.1:8765/sudu/';
const ID='114-00-E-12';
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const current=cp.execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim();
const approved=JSON.parse(fs.readFileSync(path.join(ROOT,'sudu/data/approved/114.json'),'utf8'));
const policy=JSON.parse(fs.readFileSync(path.join(ROOT,'sudu/release-governance/independent-review-policy.json'),'utf8'));
assert.equal(process.env.SUDU_D_MODE,'hold-browser','explicit HOLD-only mode required');
assert.equal(approved.year,114);
assert.equal(approved.approvedCount,0,'an actual E12 release changes test intent; use formal 8x2 runner instead');
assert.equal(approved.questions.length,0);
assert.equal((policy.trustedAiReviewReceipts||{})[ID],undefined,
 'E12 now has protected trusted review; re-evaluate instead of classifying as historical hold');
const report={test:'114-E12 actual student V4 unreleased negative',role:'D',qid:ID,
 headSHA:current,expectedHead:process.env.SUDU_D_EXPECT_SHA||null,
 mode:'REAL_BROWSER_NEGATIVE_ONLY',qaOnly:false,formalUiqaPassed:false,
 studentReady:false,studentLive:false,interception:false,
 screenshots:[],errors:[],status:'STARTED',runId:process.env.GITHUB_RUN_ID||null};
function save(){fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'114-E12-actual-HOLD-report.json'),JSON.stringify(report,null,2)+'\n');}
(async()=>{
 assert.equal(current,process.env.SUDU_D_EXPECT_SHA,'exact GitHub HEAD mismatch');
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of SIZES)for(const theme of ['light','dark']){
   const ctx=await browser.newContext({viewport:{width,height},hasTouch:width<=430,
     reducedMotion:'reduce',colorScheme:theme});
   const page=await ctx.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   page.on('response',r=>{
     if(r.url().includes('/sudu/')&&r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url());
   });
   const label=ID+'-'+width+'x'+height+'-'+theme;
   try{
    const response=await page.goto(SITE+'v4-115-multisubject-review-demo.html?year=114',
      {waitUntil:'domcontentloaded'});
    assert(response?.ok(),'V4 page route must load');
    await page.waitForFunction(()=>
      document.body.dataset.verifiedReadyYear==='114'
      &&document.body.classList.contains('qa-image-mode'),null,{timeout:20000});
    const r=await page.request.get(SITE+'data/approved/114.json',{failOnStatusCode:true});
    const served=await r.json();
    assert.deepEqual(served,approved,'HTTP served actual approved differs from checked published artifact');
    assert(!served.questions.some(q=>q.canonicalId===ID),'unapproved E12 leaked into actual approved');
    assert.equal(await page.evaluate(()=>QUESTIONS.length),0,'demo answer bank leaked to year 114');
    assert.equal(await page.locator('#homeYearSel').inputValue(),'114');
    await page.locator('#homeSubjectSel').selectOption('國文');
    await page.locator('#studyView').waitFor({state:'visible'});
    const isTheme=await page.locator('html').getAttribute('data-theme');
    if(isTheme!==theme){
      await page.locator('#themeBtn').click({timeout:8000});
    }
    assert.equal(await page.locator('html').getAttribute('data-theme'),theme,'theme toggle did not take effect');
    assert.equal(await page.locator('#answerCard').isVisible(),false,'answers visible in HOLD mode');
    assert.equal(await page.locator('#guideCard').isVisible(),false,'teaching visible in HOLD mode');
    assert.equal(await page.locator('#answerCard .opt').count(),0,'answers inserted from demo');
    assert.equal(await page.locator('#guideCard .calculation-step').count(),0,'calculation inserted from demo');
    assert.equal(await page.locator('#questionCard [data-single-question-webp]').count(),1);
    assert.equal(await page.locator('#questionCard[data-qa-preview="read-only"]').count(),1);
    const holding=await page.locator('#questionCard').innerText();
    assert(holding.includes('尚未開放作答'),'image-only HOLD warning missing');
    assert(!holding.includes('114-00-E-12'),'E12 must not be fabricated in student preview');
    const img=page.locator('#questionCard img').first();
    await img.scrollIntoViewIfNeeded();
    await img.evaluate(async img=>img.decode());
    const imageID=await img.getAttribute('data-canonical-id');
    const cardID=await page.locator('#questionCard').getAttribute('data-canonical-id');
    assert.equal(imageID,cardID,'visible preview has mismatched QID WebP');
    assert.notEqual(cardID,ID,'unapproved E12 was displayed as released');
    const bounds=await page.evaluate(()=>({
      viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth
    }));
    assert(bounds.scrollWidth<=bounds.viewport+1,'mobile horizontal overflow '+JSON.stringify(bounds));
    assert.deepEqual(errors,[],'real Chromium JS/HTTP errors');
    const filename=label+'-HOLD-NOT-UIQA.png';
    const dest=path.join(OUT,filename);
    await page.screenshot({path:dest,animations:'disabled'});
    report.screenshots.push({qid:ID,width,height,theme,file:filename,
      screenshotSha256:sha(fs.readFileSync(dest)),displayedPreviewQid:cardID,
      actualApproved114:0,status:'PASS_NEGATIVE_HOLD_ONLY'});
   }catch(error){
     report.errors.push({width,height,theme,error:String(error.stack||error),browserErrors:errors});
     try{await page.screenshot({path:path.join(OUT,label+'-FAIL.png'),animations:'disabled'});}catch{}
   }finally{await ctx.close();save();}
  }
 }finally{await browser.close();}
 report.status=report.errors.length?'HOLD_NEGATIVE_CHROMIUM_FAIL':'HOLD_NEGATIVE_CHROMIUM_16_OF_16_PASS_NOT_UIQA';
 save();
 if(report.errors.length){console.error(JSON.stringify(report.errors.slice(0,3),null,2));process.exitCode=1;return;}
 assert.equal(report.screenshots.length,16,'8 viewports times 2 themes');
 console.log('SUCCESS: 16/16 actual Chromium HOLD/NO-LEAK negatives; FORMAL E12 UIQA not run.');
})().catch(e=>{report.status='HOLD_NEGATIVE_CHROMIUM_FAIL';
 report.errors.push({fatal:String(e.stack||e)});save();console.error(e.stack||e);process.exitCode=1;});
