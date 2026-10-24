/* REAL 114 English source text+WebP+teaching shown in formal main V4 Chromium.
 * All data here are official source records staged ephemerally in CI.
 * NO synthetic question, no permanent approval and NO deployment.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const {chromium}=require('playwright');
const questions=JSON.parse(fs.readFileSync('../sudu/data/processed/114/questions.json','utf8')).questions;
const source=new Map(questions.map(q=>[q.questionId,q]));
const manifest=JSON.parse(fs.readFileSync('../sudu/data/processed/114/webp-manifest.json','utf8'));
const crops=new Map(manifest.items.map(q=>[q.questionId,q]));
const snapshot=JSON.parse(fs.readFileSync('sudu/data/approved/114.json','utf8'));
const ids=['114-00-E-07','114-00-E-08','114-00-E-09'];
const widthHeight=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const normalize=s=>s.replace(/\s+/g,' ').trim();
const sha=buffer=>crypto.createHash('sha256').update(buffer).digest('hex');
assert(snapshot._temporaryCiUiPreflight===true && snapshot._notForPagesRelease===true,
       'test must never point to permanent approved source');
assert(snapshot.approvedCount===3 && snapshot.year===114);
assert.deepEqual(snapshot.questions.map(x=>x.canonicalId),ids);
for(const pub of snapshot.questions){
  const q=source.get(pub.canonicalId),crop=crops.get(pub.canonicalId);
  assert.deepEqual(pub.options,q.options,'original A-D source not copied exactly');
  assert.equal(pub.question,q.question);
  assert.equal(pub.answer,q.answer);
  assert.equal(pub.imageSha256,crop.sha256);
  assert.equal(sha(fs.readFileSync('sudu/'+pub.image)),crop.sha256);
  assert.equal(pub.examCalculation,null,'English no arithmetic block');
  assert.deepEqual(Object.keys(pub.optionExplanations).sort(),['A','B','C','D']);
}
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const report=[];
 try{
  for(const [width,height] of widthHeight){
   const page=await browser.newPage({viewport:{width,height}});
   try{
    await page.goto('http://127.0.0.1:8765/sudu/v4-115-multisubject-review-demo.html?year=114');
    await page.waitForFunction(()=>!document.body.classList.contains('verified-year-loading'),{timeout:20000});
    assert(await page.locator('#homeView').isVisible(),'student arrives home, not answer');
    assert.equal(await page.locator('#studyView').isVisible(),false,'no question before selecting year/subject');
    await page.locator('#homeSubjectSel').selectOption({label:'英文'});
    assert(await page.locator('#studyView').isVisible(),'real English subject enters study');
    assert.equal(await page.locator('#subjectSel option').count(),1,'only one verified subject');
    for(let i=0;i<ids.length;i++){
      const expected=snapshot.questions[i],qid=ids[i];
      const num=Number(await page.locator('#questionCard .qnum').innerText());
      assert.equal(num,expected.id,'Q number mismatch '+qid);
      // Formal student mode binds the canonical ID through original question number
      // and exact WebP src/SHA; data-canonical-id is only added in image-only QA mode.
      const optionalCanonical=await page.locator('#questionCard').getAttribute('data-canonical-id');
      if(optionalCanonical!==null)assert.equal(optionalCanonical,qid);
      assert.equal(await page.locator('#studyView .opt').count(),4);
      for(let n=0;n<4;n++){
        const displayed=normalize(await page.locator('#studyView .opt .opt-text').nth(n).innerText());
        assert.equal(displayed,normalize(expected.options[n]),'Option '+String.fromCharCode(65+n)+' differs from original '+qid);
      }
      const img=page.locator('#questionCard img').first();
      assert.equal(await img.getAttribute('src'),expected.image);
      assert(await img.evaluate(async im=>{await im.decode();return im.naturalWidth>200&&im.naturalHeight>50}),qid+' invalid original crop');
      const wrong=expected.answer==='A'?'B':'A';
      await page.locator('#studyView .opt[data-a="'+wrong+'"]').click();
      await page.locator('#studyView .option-detail').first().waitFor();
      assert.equal(await page.locator('#studyView .option-detail').count(),4,qid+' missing 4 explanations');
      assert.equal(await page.locator('#studyView .opt.wrong').count(),1,'not red for wrong '+qid);
      const correct=page.locator('#studyView .option-detail.is-correct');
      assert.equal(await correct.count(),1,qid+' wrong correct answer');
      assert.match(await correct.innerText(),/高職生理解/);
      assert.match(await correct.innerText(),/國小學生也聽得懂/);
      await page.locator('#guideCard.show').waitFor();
      assert.equal(await page.locator('#guideCard .calculation-step').count(),0,'English cannot show irrelevant calculation');
      assert.equal((await page.locator('#guideCard .guide-block h3').allTextContents()).includes('考題計算式'),false);
      assert.equal(await correct.locator('.option-detail-grid').count(),0,'correct option explanation duplicated');
      assert.equal(await page.locator('#memoryWrap, #memoryCard').count(),0,'extra memory card overlays question');
      assert.equal(await page.locator('#nextBtn').isDisabled(),i===ids.length-1);
      for(const theme of ['light','dark']){
        await page.evaluate(mode=>{document.documentElement.dataset.theme=mode;document.body.dataset.theme=mode;},theme);
        const dims=await page.evaluate(()=>({innerWidth,scrollWidth:document.documentElement.scrollWidth,
                                               scrollBody:document.body.scrollWidth}));
        assert(dims.scrollWidth<=dims.innerWidth+1 && dims.scrollBody<=dims.innerWidth+1,
               qid+' overflow '+width+' '+theme+' '+JSON.stringify(dims));
        report.push({qid,viewport:width+'x'+height,theme,originalWebpDecode:true,
                     optionsAllFour:true,twoLevelTeaching:true,noCalc:true,noOverflow:true});
        if(width===390 && (i===0 || i===2)){
          fs.mkdirSync('test-results',{recursive:true});
          await page.screenshot({path:'test-results/qa114-'+qid+'-'+theme+'-390.png',fullPage:true});
        }
      }
      if(i<ids.length-1)await page.locator('#nextBtn').click();
    }
    console.log('PASS original 114 English Q07-09 on formal V4 main: '+width+'x'+height);
   }finally{await page.close();}
  }
  assert.equal(report.length,3*8*2);
  fs.mkdirSync('test-results',{recursive:true});
  fs.writeFileSync('test-results/qa114-formal-real-source-8x2.json',JSON.stringify({
      schemaVersion:1,year:114,studentReleaseApproved:false,formalUiQA:true,
      actualQuestionIds:ids,actualSourceImages:true,viewportThemeChecks:report.length,rows:report},null,2)+'\n');
  console.log('PASS: THREE SHA-matched original 114 questions and two-level teaching x 8 viewports x 2 themes = 48 independent UI checks');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
