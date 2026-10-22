/* 114/115 automatic admission RWD/zero-ready smoke on the real V4 page. */
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const widths=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
 const page=await browser.newPage();
 try{
  await page.goto(base+'v4-115-multisubject-review-demo.html');
  await page.locator('#verifiedYearNav').waitFor();
  assert.equal(await page.locator('.opt').count(),4);
  assert.equal(await page.evaluate(()=>JSON.parse(document.getElementById('demoData').textContent).questions.length),35);
  const r=await page.request.get(base+'data/approved/progress.json');assert(r.ok());
  const p=await r.json();
  for(const year of ['114','115']){
   const yr=await page.request.get(base+'data/approved/'+year+'.json');assert(yr.ok());
   const data=await yr.json();
   assert.equal(data.year,+year);assert.equal(data.questions.length,data.approvedCount);
   for(const [width,height] of widths){
    await page.setViewportSize({width,height});
    await page.goto(base+'v4-115-multisubject-review-demo.html?year='+year);
    await page.locator('#verifiedStatus').waitFor();
    if(data.approvedCount===0){
     assert.match(await page.locator('#verifiedStatus').innerText(),/沒有通過|暫停/);
     assert.equal(await page.locator('#studyView').isVisible(),false);
    }else{
     const subjects=await page.locator('#subjectSel option').allTextContents();
     assert(subjects.length>0);
     assert.match(await page.locator('#verifiedStatus').innerText(),/已通過全部驗收/);
    }
    for(const theme of ['light','dark']){
     await page.evaluate(mode=>document.documentElement.dataset.theme=mode,theme);
     const dims=await page.evaluate(()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth}));
     assert(dims.scroll<=dims.viewport+1,year+' '+theme+' '+width+' '+JSON.stringify(dims));
    }
   }
  }
  await page.goto(base+'question-bank-progress.html');
  await page.locator('#cards article.card').first().waitFor();
  assert.match(await page.locator('h1').innerText(),/題庫接入平台部署進度表/);
  console.log('PASS: V4 Demo 35 retained, QA-only 114/115 year selector, RWD 8x2, no invalid release');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
