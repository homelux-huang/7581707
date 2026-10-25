/* 114/115 automatic admission RWD/zero-ready smoke on the real V4 page. */
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const widths=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
 const seven=['國文','英文','數學 B','商業概論','數位科技','會計學','經濟學'];
 const page=await browser.newPage();
 try{
  await page.goto(base+'v4-115-multisubject-review-demo.html');
  assert.equal(await page.locator('#verifiedYearNav').count(),0,'no obstructive four-link navigation');
  assert.deepEqual(await page.locator('#yearSel option').evaluateAll(xs=>xs.map(x=>x.value)),['demo','115','114']);
  assert(await page.locator('#homeView').isVisible(),'root loads home');
  assert.equal(await page.locator('#studyView').isVisible(),false,'no questions on home');
  assert.equal(await page.locator('.opt').count(),4);
  assert.equal(await page.evaluate(()=>JSON.parse(document.getElementById('demoData').textContent).questions.length),35);
  const r=await page.request.get(base+'data/approved/progress.json');assert(r.ok());
  const p=await r.json();
  for(const year of ['114','115']){
   const yr=await page.request.get(base+'data/approved/'+year+'.json');assert(yr.ok());
   const data=await yr.json();
   assert.equal(data.year,+year);assert.equal(data.questions.length,data.approvedCount);
   const imagePreview=await page.request.get(base+'data/approved/preview/'+year+'.json');
   assert(imagePreview.ok(),'preview JSON not whitelisted');
   const preview=await imagePreview.json();
   assert.equal(preview.year,+year);
   assert.equal(preview.imagePreviewCount,preview.questions.length);
   for(const item of preview.questions){
     assert.equal(item.reviewStage,'image_qa_pass_only');
     for(const forbidden of ['answer','question','options','teaching','memory'])
       assert.equal(Object.hasOwn(item,forbidden),false,'QA preview must not leak '+forbidden);
   }
   for(const [width,height] of widths){
    await page.setViewportSize({width,height});
    await page.goto(base+'v4-115-multisubject-review-demo.html?year='+year);
    await page.waitForFunction(()=>!document.body.classList.contains('verified-year-loading'));
    assert.equal(await page.locator('#verifiedStatus').count(),0,'no large status card');
    assert.equal(await page.locator('#verifiedImagePreview').count(),0,'no separate preview gallery');
    assert.equal(await page.locator('#verifiedPreviewToggle').count(),0,'no preview toggle bar');
    assert.equal(await page.locator('#verifiedYearNav').count(),0,'no four-link bar');
    assert.equal(await page.locator('#yearSel').inputValue(),year);
    assert(await page.locator('#homeView').isVisible(),year+' starts on home');
    assert.equal(await page.locator('#studyView').isVisible(),false,'year alone cannot expose question');
    assert.equal(await page.locator('#homeYearSel').inputValue(),year);
    assert(await page.locator('#homeSubjectSel').isEnabled(),year+' has subject navigation');
    assert.deepEqual(
      await page.locator('#homeSubjectSel option').evaluateAll(xs=>xs.slice(1).map(x=>x.value)),
      seven,year+' must list seven subjects even when not yet student-approved');
    assert.match(await page.locator('#annualSubjectAvailability').innerText(),/七科沿用 35 題 Demo/);
    const chosenSubject=data.approvedCount?data.questions[0].subject:preview.questions[0].subject;
    await page.locator('#homeSubjectSel').selectOption({label:chosenSubject});
    assert(await page.locator('#studyView').isVisible(),year+' subject begins study');
    if(data.approvedCount===0){
     if(preview.imagePreviewCount){
      await page.locator('body.qa-image-mode #questionCard img').first().waitFor();
      assert.equal(await page.locator('#studyView').isVisible(),true);
      assert.equal(await page.locator('#answerCard').isVisible(),false);
      assert.equal(await page.locator('#studyView .opt').count(),0,'image-only never exposes grading');
      const rows=preview.questions.filter(item=>item.subject===chosenSubject);
      const first=rows[0];
      assert.equal(Number(await page.locator('#questionCard .qnum').innerText()),first.questionNumber);
      assert.equal(await page.locator('#questionCard').getAttribute('data-canonical-id'),first.canonicalId);
      const img=page.locator('#questionCard img').first();
      assert.equal(await img.getAttribute('src'),'./'+first.image);
      assert.equal(await img.getAttribute('data-canonical-id'),first.canonicalId);
      assert(await img.evaluate(async el=>{await el.decode();return el.naturalWidth>0&&el.naturalHeight>0}));
      if(rows.length>1){
       await page.locator('#nextBtn').click();
       const second=rows[1];
       assert.equal(Number(await page.locator('#questionCard .qnum').innerText()),second.questionNumber);
       assert.equal(await page.locator('#questionCard img').first().getAttribute('src'),'./'+second.image);
      }
     }
    }else{
     await page.locator('#questionCard img').first().waitFor();
     assert.equal(await page.locator('#studyView').isVisible(),true);
     assert.equal(await page.locator('#studyView .opt').count(),4);
     const first=data.questions[0];
     assert.equal(Number(await page.locator('#questionCard .qnum').innerText()),first.id);
     assert.equal(await page.locator('#questionCard img').first().getAttribute('src'),first.image);
     assert.equal(await page.locator('#answerCard').isVisible(),true);
    }
    for(const theme of ['light','dark']){
     await page.evaluate(mode=>document.documentElement.dataset.theme=mode,theme);
     const dims=await page.evaluate(()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth}));
     assert(dims.scroll<=dims.viewport+1,year+' '+theme+' '+width+' '+JSON.stringify(dims));
    }
   }
  }
  // 115 student-approved Math B and image-only other six subjects coexist
  // in ONE Demo-style year/subject selector, without leaking answer keys.
  await page.goto(base+'v4-115-multisubject-review-demo.html?year=115');
  await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='115');
  await page.locator('#homeSubjectSel').selectOption('國文');
  await page.waitForFunction(()=>location.search.includes('view=images'));
  await page.locator('body.qa-image-mode #questionCard img').first().waitFor();
  assert.equal(await page.locator('#questionCard .pill').first().innerText(),'國文');
  assert.equal(await page.locator('#studyView .opt').count(),0,'non-approved 115 Chinese cannot be graded');
  assert.equal(await page.locator('#answerCard').isVisible(),false);
  assert.match(await page.locator('#annualSubjectAvailability').innerText(),/原圖 QA/);
  await page.goto(base+'v4-115-multisubject-review-demo.html?year=115&view=images');
  await page.waitForFunction(()=>document.body.classList.contains('qa-image-mode'));
  await page.locator('#homeSubjectSel').selectOption('數學 B');
  await page.waitForFunction(()=>!location.search.includes('view=images'));
  await page.locator('#studyView .opt').first().waitFor();
  assert.equal(await page.locator('#studyView .opt').count(),4,'115 Math B uses approved-grade Demo UI');
  await page.goto(base+'v4-115-multisubject-review-demo.html?year=114');
  await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='114');
  await page.locator('#homeSubjectSel').selectOption('英文');
  assert(await page.locator('#homeView').isVisible(),'unavailable 114 English stays on home');
  assert.equal(await page.locator('#studyView').isVisible(),false,'114 unapproved English never exposes Demo questions');
  assert.match(await page.locator('#annualSubjectAvailability').innerText(),/尚無可顯示的正式題目/);
  await page.locator('#homeSubjectSel').selectOption('國文');
  await page.locator('body.qa-image-mode #questionCard img').first().waitFor();
  assert.equal(await page.locator('#studyView .opt').count(),0);
  // A real annual English example must not silently use same-number 115 Demo
  // examples, which are keyed only by the original question number.
  await page.goto(base+'v4-115-multisubject-review-demo.html');
  const annualNews=await page.evaluate(()=>formatStudyValue({
    canonicalId:'114-00-E-01',id:1,subject:'英文',highlights:['annually']
  },'新聞時事例句','The figures are reviewed annually by teachers.'));
  assert.match(annualNews,/exam-highlight/);
  assert.match(annualNews,/annually/);
  assert.doesNotMatch(annualNews,/After heavy rain|outdoor seats/);
  // 115 original-image audit is available ONLY as a single-question view in
  // the existing question card, without an extra top block or answer leak.
  await page.goto(base+'v4-115-multisubject-review-demo.html?year=115&view=images');
  await page.locator('body.qa-image-mode').waitFor();
  assert(await page.locator('#homeView').isVisible(),'image preview starts from home');
  const snapshot=await (await page.request.get(base+'data/approved/preview/115.json')).json();
  await page.locator('#homeSubjectSel').selectOption({label:snapshot.questions[0].subject});
  await page.locator('body.qa-image-mode #questionCard img').first().waitFor();
  assert.equal(await page.locator('#verifiedYearNav').count(),0);
  assert.equal(await page.locator('#verifiedImagePreview').count(),0);
  assert.equal(await page.locator('#answerCard').isVisible(),false);
  assert.equal(await page.locator('#questionCard img').first().getAttribute('data-canonical-id'),
    (await (await page.request.get(base+'data/approved/preview/115.json')).json()).questions[0].canonicalId);
  await page.goto(base+'question-bank-progress.html');
  await page.locator('#cards article.card').first().waitFor();
  assert.match(await page.locator('h1').innerText(),/題庫接入平台部署進度表/);
  console.log('PASS: V4 Demo 35 retained, QA-only 114/115 year selector, RWD 8x2, no invalid release');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
