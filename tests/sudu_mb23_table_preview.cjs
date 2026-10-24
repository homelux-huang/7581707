'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const payload=JSON.parse(fs.readFileSync(path.join(ROOT,'mb23-qa-only/115.json'),'utf8'));
const meta=JSON.parse(fs.readFileSync(path.join(ROOT,'mb23-qa-only/meta.json'),'utf8'));
assert(payload.QA_ONLY_UNPUBLISHABLE===true&&payload.studentReleaseApproved===false);
const q=payload.questions[0];assert.equal(q.canonicalId,'115-00-MB-23');
const base='http://127.0.0.1:8777/sudu/';
const widths=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const results=[];
(async()=>{
 const b=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
 for(const [width,height] of widths)for(const theme of ['light','dark']){
  const ctx=await b.newContext({viewport:{width,height},hasTouch:width<1024,isMobile:width<768,reducedMotion:'reduce'});
  const page=await ctx.newPage(),err=[];
  page.on('pageerror',e=>err.push(e.message));
  const tap=loc=>width<1024?loc.tap({timeout:15000}):loc.click({timeout:15000});
  try{
   await page.route('**/data/approved/115.json',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(payload)}));
   await page.goto(base+'v4-115-multisubject-review-demo.html?year=115&subject='+encodeURIComponent('數學 B'),
           {waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='115',{timeout:30000});
   await page.evaluate(theme=>{document.documentElement.dataset.theme=theme;state.theme=theme;},theme);
   assert((await page.locator('#questionCard').innerText()).includes('如表（二）'));
   assert.equal(await page.locator('#questionCard .source-figure img').count(),1);
   const img=await page.locator('#questionCard .source-figure img').evaluate(async e=>{
      await e.decode();return {src:e.getAttribute('src'),w:e.naturalWidth,h:e.naturalHeight};});
   assert(img.src.endsWith('115-00-MB-23.webp')&&img.w>100&&img.h>30);
   const t=page.locator('#questionCard details.official-source-table');
   assert.equal(await t.count(),1,'table accessibility must appear next to original WebP');
   await tap(t.locator('summary'));
   assert.equal(await t.locator('thead th').count(),3);
   assert.equal(await t.locator('tbody tr').count(),2);
   assert.equal(await t.locator('tbody td').count(),6);
   const words=await t.innerText();
   for(const s of ['行程Ⅰ','行程Ⅱ','3000','八折'])assert(words.includes(s),'missing table '+s);
   assert.equal(await page.locator('#answerCard .opt').count(),4);
   await tap(page.locator('#answerCard .opt[data-a="A"]'));
   await page.locator('#guideCard.show').waitFor();
   assert.equal(await page.locator('#guideCard .guide-block.calculation-first').count(),1);
   assert((await page.locator('#guideCard').innerText()).includes('33000'));
   await tap(page.locator('#reviewTop'));
   await page.locator('#reviewView.show').waitFor();
   assert((await page.locator('#reviewList').innerText()).includes('正確答案 B'));
   assert.deepEqual(err,[],'Javascript exceptions');
   const widths=await page.evaluate(()=>({inner:innerWidth,scroll:document.documentElement.scrollWidth}));
   assert(widths.scroll<=widths.inner+1,'horizontal overflow');
   results.push({width,height,theme,passed:true,webpSha256:meta.originalWebpSha256,
      tableRevisionSha256:meta.tableBoundQuestionRevision,originalWebp:true,rows:2,cols:3,workedMath:true});
  }finally{await ctx.close()}
 }
 console.log('PASS MB23 original source table and WebP, real V4 8x2, wrong answer + worked math, ONLY isolated QA, NO RELEASE');
 }finally{await b.close()}
})().catch(e=>{console.error(e.stack||e);process.exitCode=1}).finally(()=>{
 fs.mkdirSync(path.join(ROOT,'mb23-qa-only'),{recursive:true});
 fs.writeFileSync(path.join(ROOT,'mb23-qa-only/ui-results.json'),JSON.stringify({qid:'115-00-MB-23',sourceApproved:false,tests:results},null,2));
});
