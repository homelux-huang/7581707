'use strict';
// Role D 104–113 historic YEAR ROUTING and NO-UNVERIFIED-PLAY gate.
// NEVER presents archival candidate OCR/answers/lessons as playable fixtures.
// Actual source year JSONs are read only to prove they are NOT READY.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const cp=require('node:child_process');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const BASE=process.env.SUDU_D_BASE_URL||
  'http://127.0.0.1:8765/sudu/v4-115-multisubject-review-demo.html';
const OUT=path.resolve(process.env.SUDU_D_OUTPUT||
  'test-results/role-d-104-113-year-route');
const YEARS=Array.from({length:10},(_,i)=>String(104+i));
const ALLYEARS=Array.from({length:12},(_,i)=>String(115-i));
const SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],
 [768,1024],[1024,768],[1440,900]];
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
const abs=p=>path.join(ROOT,p);
const hash=p=>SHA(fs.readFileSync(abs(p)));
const head=cp.execFileSync('git',['rev-parse','HEAD'],{
 cwd:ROOT,encoding:'utf8'}).trim();
if(process.env.SUDU_D_EXPECT_SHA){
 assert.equal(head,process.env.SUDU_D_EXPECT_SHA,'exact CI HEAD moved');
}
const HTML=fs.readFileSync(abs('sudu/v4-115-multisubject-review-demo.html'),'utf8');
const match=HTML.match(/<script id="demoData" type="application\/json">([\s\S]*?)<\/script>/);
assert(match,'one original existing V4 Demo35 source');
const demo=JSON.parse(match[1]);
assert.deepEqual(demo.subjects,[
 '國文','英文','數學 B','商業概論','數位科技','會計學','經濟學'
]);
assert.equal(demo.questions.length,35);
for(const subject of demo.subjects)
 assert.equal(demo.questions.filter(q=>q.subject===subject).length,5,
  'original 35 Demo subject layout parity');
for(const year of YEARS){
 const previous=abs('_site/sudu/data/approved/'+year+'.json');
 assert(!fs.existsSync(previous),
  'Historical year has newly published approved data; must independently inspect/retest before QA no-data gate '+year);
}
const archive=[];
for(const year of YEARS){
 const p='sudu/data/years/'+year+'.json';
 const doc=JSON.parse(fs.readFileSync(abs(p),'utf8'));
 assert.equal(doc.year,Number(year));
 assert.equal(doc.papers.length,5);
 assert.deepEqual(doc.papers.map(x=>x.paper),['00-C','00-E','00-MB','09-1','09-2']);
 const qs=doc.papers.flatMap(p=>p.questions);
 assert(qs.length>=200&&qs.length<=205,'unexpected raw legacy source count '+year);
 const readCertified=qs.filter(q=>q.answerVerified===true||
  q.questionVerified===true||q.teachingVerified===true);
 assert.equal(readCertified.length,0,
  'Historic archived QA flags changed; do not use old no-release baseline '+year);
 const explanations=qs.filter(q=>typeof q.explanation==='string'&&q.explanation.trim()).length;
 assert.equal(explanations,0,'found new lesson; separate B/C/E review needed');
 archive.push({
  year,originalGitSourceFile:p,originalJsonSha256:hash(p),
  actualRawCandidates:qs.length,legacyQuestionsFound:doc.questionsFound,
  automaticAnswerMatched:qs.filter(q=>q.answerMatched===true).length,
  independentAnswerQuestionTeachingPass:0,
  officialPerQuestionWebpReady:false,explanationCount:explanations
 });
}
assert.equal(archive.reduce((n,x)=>n+x.actualRawCandidates,0),2043);
assert.equal(archive.reduce((n,x)=>n+x.automaticAnswerMatched,0),1799);
const report={
 taskId:'D-104-113-V4-YEAR-ROUTE-FAILCLOSED-20261025-01',role:'D',
 status:'TESTING',headSha:head,ciRun:process.env.GITHUB_RUN_ID||null,
 officialStudentPage:'sudu/v4-115-multisubject-review-demo.html',
 htmlSha256:hash('sudu/v4-115-multisubject-review-demo.html'),
 runtimeSha256:hash('sudu/verified-questions-runtime.js'),
 demo35SourceSha256:SHA(Buffer.from(match[1],'utf8')),
 demo35Questions:35,archivalRawSourceInventory:archive,
 historicalReady:0,historicalLiveVerified:0,
 label:'EXISTING_V4_HISTORY_ROUTE_ONLY_NOT_OLD_QUESTION_UIQA',
 cases:[],smoke:[],errors:[]
};
function save(){fs.mkdirSync(OUT,{recursive:true});
 fs.writeFileSync(path.join(OUT,'historical-year-gate.json'),
   JSON.stringify(report,null,2)+'\n');}
const interact=async(loc,touch)=>{
 if(touch)await loc.tap({timeout:15000});
 else await loc.click({timeout:15000});
};
const choose=async(loc,value,touch)=>{
 await interact(loc,touch);
 await loc.selectOption(value,{timeout:15000});
};
async function cjkLegible(page){
 const result=await page.evaluate(async()=>{
  await document.fonts.ready;
  const item=document.getElementById('verifiedLoadError');
  if(!item)return null;
  const font=getComputedStyle(item).fontFamily;
  const letters=['中','文','未','審'];
  const values=letters.map(letter=>{
   const canvas=document.createElement('canvas');
   canvas.width=88;canvas.height=88;
   const g=canvas.getContext('2d',{willReadFrequently:true});
   g.font='49px '+font;g.fillStyle='#000';g.textBaseline='top';
   g.fillText(letter,4,3);
   const pixels=g.getImageData(0,0,88,88).data;
   let count=0,h=2166136261;
   for(let i=3;i<pixels.length;i+=4){
    const alpha=pixels[i];if(alpha>32)count++;
    h=Math.imul(h^alpha,16777619)>>>0;
   }
   return {char:letter,pixels:count,fingerprint:h.toString(16)};
  });
  return {font,glyphs:values};
 });
 assert(result&&result.glyphs.every(x=>x.pixels>70)&&
   new Set(result.glyphs.map(x=>x.fingerprint)).size>=3,
   'real CJK rendering unresolved (tofu) '+JSON.stringify(result));
 return result;
}
async function loadErrorGate(page,year,baseline,profile){
 await page.waitForURL(url=>new URL(url).searchParams.get('year')===year,
   {timeout:15000});
 await page.locator('#verifiedLoadError').waitFor({state:'visible',timeout:15000});
 await page.waitForFunction(()=>
  document.body.classList.contains('qa-error-mode'),null,{timeout:15000});
 const observed=await page.evaluate(()=>{
  const years=id=>[...document.getElementById(id).options]
   .map(o=>o.value).filter(v=>/^\d{3}$/.test(v));
  return{
   urlYear:new URLSearchParams(location.search).get('year'),
   appYear:pageYear(),homeYear:document.getElementById('homeYearSel').value,
   navYear:document.getElementById('yearSel').value,
   annualState:document.body.dataset.verifiedReadyYear||null,
   cssTheme:document.documentElement.dataset.theme,
   yearsHome:years('homeYearSel'),yearsNav:years('yearSel'),
   homeVisible:!document.getElementById('homeView').hidden,
   homeSubjectDisabled:document.getElementById('homeSubjectSel').disabled,
   homeSubjectText:document.getElementById('homeSubjectSel').selectedOptions[0]?.textContent,
   wrongReviewDisabled:document.getElementById('homeReviewBtn').disabled,
   renderedOptionCount:document.querySelectorAll('#answerCard .opt').length,
   allQuestionCardsText:document.getElementById('questionCard').textContent,
   guideText:document.getElementById('guideCard').textContent,
   firstQuestionButtonVisible:[...document.querySelectorAll('#progressChips button')].some(e=>e.offsetParent!==null),
   docWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth,
   errorText:document.getElementById('verifiedLoadError').textContent,
   oldStudentStorage:localStorage.getItem('tvet-verified-'+
       new URLSearchParams(location.search).get('year')+'-v1'),
   demoStudentStorage:localStorage.getItem('tvet-115-multisubject-demo-v1'),
   questionViewVisible:!!document.getElementById('studyView').offsetParent,
   errorVisible:!!document.getElementById('verifiedLoadError').offsetParent
  };
 });
 assert.equal(observed.urlYear,year);
 assert.equal(observed.appYear,year,'104-113 route silently aliasing original 35-Demo');
 assert.equal(observed.homeYear,year);
 assert.equal(observed.navYear,year);
 assert.deepEqual(observed.yearsHome,ALLYEARS);
 assert.deepEqual(observed.yearsNav,ALLYEARS);
 assert.equal(observed.annualState,null);
 assert.equal(observed.cssTheme,profile.theme);
 assert.equal(observed.homeVisible,true);
 assert.equal(observed.homeSubjectDisabled,true);
 assert.match(observed.homeSubjectText||'',/尚無已核准題庫/);
 assert.equal(observed.wrongReviewDisabled,true);
 assert.equal(observed.renderedOptionCount,0);
 assert.equal(observed.allQuestionCardsText,'');
 assert.equal(observed.guideText,'');
 assert.equal(observed.firstQuestionButtonVisible,false);
 assert.equal(observed.oldStudentStorage,null);
 assert.equal(observed.demoStudentStorage,baseline,
  'historic 104–113 route changed existing 35-Demo student record bytes');
 assert.equal(observed.questionViewVisible,false);
 assert.equal(observed.errorVisible,true);
 assert(observed.docWidth<=observed.viewportWidth+1,
  'historic no-release homepage horizontal overflow '+JSON.stringify(observed));
 assert(observed.errorText.includes(year+' 年官方候選尚未完成逐題原圖'),
  'error concealed old-year 0 QA status: '+observed.errorText);
 assert(/未通過|未完成|尚未/.test(observed.errorText));
 const font=await cjkLegible(page);
 // Negative security probe only (NOT a historic question fixture or QA pass):
 // a direct old-year call to Demo wrong-sample seed must be a no-op, and
 // old-year review must NOT offer an action to generate fake wrong answers.
 const seeded=await page.evaluate(()=>{
  renderReview();
  const demoSeedExists=!!document.querySelector('#seedDemo');
  const before=localStorage.getItem('tvet-115-multisubject-demo-v1');
  seedDemo();
  return {demoSeedExists,before,after:localStorage.getItem('tvet-115-multisubject-demo-v1')};
 });
 assert.equal(seeded.demoSeedExists,false,
  'unverified old-year review exposes Demo sample wrong-answer generator');
 assert.equal(seeded.after,seeded.before,
  'direct Demo sample callback mutated the real Demo history on an old-year route');
 // Screenshots explicitly remain QA ONLY, never original old exam UIQA.
 await page.addStyleTag({content:
  'body::after{content:"D QA-ONLY / OLD YEAR NOT READY / NOT LIVE";'+
  'position:fixed;bottom:3px;right:3px;background:#821c1c;color:#fff;'+
  'font:bold 11px sans-serif;padding:3px 5px;border-radius:3px;'+
  'z-index:99999;pointer-events:none}'});
 const name='year-'+year+'-'+profile.width+'x'+profile.height+'-'+profile.theme+'.png';
 await page.screenshot({path:path.join(OUT,name),fullPage:false,animations:'disabled'});
 report.cases.push({
  ...profile,year,sourceSha256:archive.find(x=>x.year===year).originalJsonSha256,
  classification:'HISTORICAL_YEAR_ROUTE_FAILCLOSED_NOT_QUESTION_UIQA',
  realOldYearDisplayed:true,oldYearAvailableQuestionCount:0,
  archivedAnswerVerifiedCount:0,noAutomaticAnswerPromotion:true,
  noDemoQuestionFallback:true,noAnswerOptionsExposed:true,
  demoStudentStateByteIdentical:true,viewportOverflow:false,
  cjkRasterFont:font.font,cjkRasterSample:font.glyphs,screenshot:name
 });
}
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const [width,height] of SIZES)for(const theme of ['light','dark']){
   const profile={width,height,theme,input:width<=430?'real_touch':'real_mouse'};
   const context=await browser.newContext({
    viewport:{width,height},hasTouch:width<=430,locale:'zh-TW',reducedMotion:'reduce'
   });
   const page=await context.newPage();
   const errors=[];const responses=new Map();
   page.on('pageerror',e=>errors.push(e.message));
   page.on('response',r=>{
    const match=r.url().match(/\/sudu\/data\/approved\/(10[4-9]|11[0-3])\.json/);
    if(match)responses.set(match[1],r.status());
   });
   try{
    await page.goto(BASE,{waitUntil:'domcontentloaded'});
    await page.locator('#homeView').waitFor({state:'visible'});
    // Real existing 35-Demo navigation; dark is changed by actual UI button,
    // never by injecting test theme or overriding the student CSS.
    await choose(page.locator('#homeYearSel'),'demo',width<=430);
    // Positive real Demo control: the old example button must remain
    // accessible ONLY in authentic Demo review and never annual 104–115.
    await interact(page.locator('#homeReviewBtn'),width<=430);
    await page.locator('#reviewView.show').waitFor({state:'visible'});
    assert.equal(await page.locator('#seedDemo').count(),1,
      'original 35-Demo review sample intentionally removed');
    await interact(page.locator('#backStudy'),width<=430);
    await page.locator('#homeView').waitFor({state:'visible'});
    if(theme==='dark'){
     await choose(page.locator('#homeSubjectSel'),'英文',width<=430);
     await page.locator('#studyView').waitFor({state:'visible'});
     await interact(page.locator('#themeBtn'),width<=430);
     assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
     await interact(page.locator('#navHomeBtn'),width<=430);
     await page.locator('#homeView').waitFor({state:'visible'});
    }
    const baseline=await page.evaluate(()=>localStorage.getItem(
      'tvet-115-multisubject-demo-v1'));
    for(const year of YEARS){
     await choose(page.locator('#homeYearSel'),year,width<=430);
     await loadErrorGate(page,year,baseline,profile);
     assert.equal(responses.get(year),404,
      'unexpected actual historical approved artifact HTTP '+year+' '+responses.get(year));
    }
    assert.deepEqual(errors,[],'unexpected browser JS runtime exception');
   }catch(error){
    report.errors.push({...profile,error:String(error.stack||error),pageErrors:errors});
   }finally{
    await context.close();
    save();
   }
  }
  // Real grandfathered 115 routes and 114 image-preview path must retain
  // their historic behavior; this is only a smoke, never new UIQA/READY.
  for(const year of ['114','115']){
   const context=await browser.newContext({viewport:{width:390,height:844},locale:'zh-TW'});
   const page=await context.newPage();const errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   try{
    await page.goto(BASE+'?year='+year,{waitUntil:'domcontentloaded'});
    await page.waitForFunction((y)=>
      document.body.classList.contains('qa-error-mode')||
      document.body.dataset.verifiedReadyYear===y,year,{timeout:25000});
    const info=await page.evaluate(()=>({
     requested:new URLSearchParams(location.search).get('year'),
     parsed:pageYear(),verifiedYear:document.body.dataset.verifiedReadyYear||null,
     preview:document.body.classList.contains('qa-image-mode'),
     denied:document.body.classList.contains('qa-error-mode'),
     allYearOptions:[...document.getElementById('homeYearSel').options]
        .map(x=>x.value).filter(x=>/^\d{3}$/.test(x))
    }));
    assert.equal(info.requested,year);
    assert.equal(info.parsed,year);
    assert.deepEqual(info.allYearOptions,ALLYEARS);
    if(year==='115'){
      assert.equal(info.verifiedYear,'115',
       'previous five original 115 approved Math B questions lost on new route');
      assert.equal(info.denied,false);
      await page.locator('#homeSubjectSel').selectOption('數學 B');
      await page.locator('#studyView').waitFor({state:'visible'});
      assert.equal(await page.locator('#answerCard .opt').count(),4,
        'existing approved real 115 Math B A-D altered');
      const canonicalId=await page.evaluate(()=>qnow()?.canonicalId);
      assert(/^115-00-MB-/.test(canonicalId));
      info.realPriorApprovedMathB=canonicalId;
      // The old implementation would seed fabricated wrong-answer records
      // into the 115 student session despite being a Demo-only helper.
      // Call directly as a negative guard test, NEVER as student evidence.
      const annualSeedGate=await page.evaluate(()=>{
        const before=localStorage.getItem('tvet-verified-115-v1');
        renderReview();const demoSeedExists=!!document.getElementById('seedDemo');
        seedDemo();
        return {before,after:localStorage.getItem('tvet-verified-115-v1'),demoSeedExists};
      });
      assert.equal(annualSeedGate.demoSeedExists,false,
        'real approved 115 incorrectly offers Demo seed inside wrong-review');
      assert.equal(annualSeedGate.after,annualSeedGate.before,
        'Demo seed mutated existing approved 115 student history');
    }else{
      assert.equal(info.preview||info.denied,true,
        'unapproved 114 must not alias to original 35-demo answering');
    }
    assert.deepEqual(errors,[],'114/115 smoke uncaught browser exception');
    report.smoke.push({year,classification:'114_115_HISTORIC_REGRESSION_ONLY',
     ...info,accepted:true});
   }catch(error){report.errors.push({smokeYear:year,error:String(error.stack||error),
     pageErrors:errors});}
   finally{await context.close();save();}
  }
 }finally{await browser.close();}
 report.status=report.errors.length?'FAIL':'YEAR_ROUTE_FAILCLOSED_PASS_NOT_OLD_UIQA';
 save();
 if(report.errors.length)console.error('FIRST_ERR',JSON.stringify(report.errors.slice(0,3),null,2));
 assert.equal(report.errors.length,0,'old year route/browser regression failure');
 assert.equal(report.cases.length,160,
  'require 10 authentic old years x 8 screen sizes x two themes');
 assert.equal(report.smoke.length,2);
 console.log('PASS 160/160 104-113 existing V4 no-release year selector; archived candidate READY 0, LIVE 0');
})().catch(error=>{
 report.status='FAIL';report.errors.push({fatal:String(error.stack||error)});
 save();console.error(error.stack||error);process.exitCode=1;
});
