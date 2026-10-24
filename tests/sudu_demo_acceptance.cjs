/* Isolated acceptance of the existing 35-question demo; never reuses a student profile. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
const output=process.env.SUDU_TEST_OUTPUT||'test-results';
const sizes=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const expected={'國文':[1,2,3,7,9],'英文':[1,2,3,4,5],'數學 B':[7,9,10,11,12],'商業概論':[1,3,5,6,7],'數位科技':[26,27,28,32,34],'會計學':[2,3,4,5,6],'經濟學':[25,26,27,28,29]};
(async()=>{
 fs.mkdirSync(output,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'reduce'});
 const page=await context.newPage(),errors=[],report={images:[],english:[],rwd:[]};
 page.on('pageerror',e=>errors.push(e.message));
 // These mutations exist only in this fresh automated browser context.
 const choose=async(subject,id)=>{
  await page.evaluate(({subject,id})=>{currentSubject=subject;currentIndex=list().findIndex(q=>q.id===id);showStudy();renderAll();closeQuestionNav();window.scrollTo({top:0,behavior:'instant'});},{subject,id});
 };
 const settle=()=>page.waitForTimeout(400);
 const noOverflow=async(label)=>{const layout=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,offenders:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.right>innerWidth+1&&getComputedStyle(e).position!=='fixed'}).slice(0,12).map(e=>({tag:e.tagName,id:e.id,cls:e.className,right:e.getBoundingClientRect().right}))}));assert(layout.scrollWidth<=layout.width+1,label+' '+JSON.stringify(layout));};
 try{
  await page.goto(base+'v4-115-multisubject-review-demo.html');
  assert(await page.locator('#homeView').isVisible(),'home is the initial view');
  assert.equal(await page.locator('#studyView').isVisible(),false,'no question visible on home');
  assert.equal(await page.locator('.home-actions > *').count(),3,'three home actions');
  assert(await page.locator('#homeSubjectSel').isDisabled(),'pick year before subject');
  const clockBefore=await page.locator('#examClock').innerText();
  assert(/天.*時.*分.*秒/.test(clockBefore));
  await page.waitForTimeout(1100);assert.notEqual(await page.locator('#examClock').innerText(),clockBefore,'countdown ticks each second');
  const edges=await page.evaluate(()=>[countdownText(EXAM_DAY_START-1000),countdownText(EXAM_DAY_START),countdownText(EXAM_DAY_END)]);
  assert.deepEqual(edges,['0天 00時 00分 01秒','統測考試期間，加油！','本屆統測已結束']);
  const qs=await page.evaluate(()=>JSON.parse(document.getElementById('demoData').textContent).questions);
  assert.equal(qs.length,35);
  for(const [subject,ids] of Object.entries(expected))assert.deepEqual(qs.filter(q=>q.subject===subject).map(q=>q.id),ids);
  await page.locator('#homeYearSel').selectOption('demo');
  await page.locator('#homeSubjectSel').selectOption({label:'英文'});
  assert(await page.locator('#studyView').isVisible(),'year and subject enter study');
  assert(await page.locator('#explainBtn').isDisabled(),'answer shortcut locked until answering');
  const manifestResponse=await context.request.get(base+'questions/115/crop-manifest.json');
  assert(manifestResponse.ok());const manifest=await manifestResponse.json();
  assert.equal(manifest.generatedCount,30);assert.equal(manifest.items.length,30);
  for(const item of manifest.items){
   assert.equal(item.ocrPerformed,false);
   const response=await context.request.get(new URL(item.output.replace(/^sudu\//,''),base).href);
   assert(response.ok(),item.output);
   assert.equal(crypto.createHash('sha256').update(await response.body()).digest('hex'),item.sha256,item.output+' matches manifest');
  }
  for(const q of qs){
   await choose(q.subject,q.id);
   const img=page.locator('.source-figure img');await img.scrollIntoViewIfNeeded();
   await page.waitForFunction(()=>{const i=document.querySelector('.source-figure img');return i.complete&&i.naturalWidth>0});
   const dimensions=await img.evaluate(i=>({width:i.naturalWidth,height:i.naturalHeight,src:i.getAttribute('src')}));
   if(q.subject!=='會計學')assert(dimensions.src.startsWith('questions/115/'));
   report.images.push({subject:q.subject,question:q.id,width:dimensions.width,height:dimensions.height,decoded:true});
   // On the historical economics 28 stall, sample geometry *during* Playwright
   // actionability checks (post-timeout geometry alone can look stationary).
   const trace=(q.subject==='經濟學'&&q.id===28);
   if(trace)await page.evaluate(()=>{
    window.__suduClickTrace=[];
    window.__suduClickTraceTimer=setInterval(()=>{
     const e=document.querySelector('.opt'),r=e?.getBoundingClientRect();
     window.__suduClickTrace.push({t:Math.round(performance.now()),y:scrollY,
      top:r?.top,left:r?.left,w:r?.width,h:r?.height,
      scroller:document.scrollingElement?.scrollTop,
      body:document.body.className,hover:e?.matches(':hover'),
      transform:e?getComputedStyle(e).transform:null});
    },80);
   });
   try{await page.locator('.opt').first().click();}
   catch(clickError){
    if(trace)report.duringClick=await page.evaluate(()=>window.__suduClickTrace);
    throw clickError;
   }finally{
    if(trace)await page.evaluate(()=>clearInterval(window.__suduClickTraceTimer));
   }
   await settle();
   assert.equal(await page.locator('.option-detail').count(),4);
   assert((await page.locator('#guideCard').innerText()).includes('頁數：待核對'));
  }
  // A fast subject/question switch must cancel an earlier answer's delayed jump.
  // Use real browser interaction and preserve the normal (non-forced) click QA.
  await choose('經濟學',27);
  await page.locator('.opt').first().click();
  await choose('經濟學',28);
  const beforeLateJump=await page.evaluate(()=>window.scrollY);
  await page.waitForTimeout(470);
  const afterLateJump=await page.evaluate(()=>window.scrollY);
  assert(Math.abs(afterLateJump-beforeLateJump)<=2,
    'previous question answer-jump moved the newly selected question: '+JSON.stringify({beforeLateJump,afterLateJump}));
    // Existing guide content wins, while unique source notes remain in the same section.
  await choose('國文',1);
  await page.locator('.opt').first().click();await settle();
  const mergedSource=await page.evaluate(()=>{
   const rows=[...document.querySelectorAll('#guideCard .guide-block')].filter(el=>el.querySelector('h3')?.textContent==='出處');
   return {count:rows.length,text:rows[0]?.innerText||''};
  });
  assert.equal(mergedSource.count,1,'duplicate source headings are merged');
  assert(mergedSource.text.includes('國立彰化高商')&&mergedSource.text.includes('115 年統測國文第 1 題'),
   'guide retains textbook and official question source without duplicate panels');
  const noDuplicate=await page.evaluate(()=>{
   const q=qnow(),old=q.memory;
   q.memory=q.concept;
   const labels=guideEntries(q).map(x=>x[0]);
   q.memory=old;
   return {memo:labels.filter(x=>x==='速記重點').length,source:labels.filter(x=>x==='出處').length};
  });
  assert.deepEqual(noDuplicate,{memo:0,source:1},'duplicated quick memo is omitted');
  // All five English words and their actual inflections in all three required surfaces.
  for(const [id,word] of [[1,'wet'],[2,'joined'],[3,'equally'],[4,'suitable'],[5,'attract']]){
   await choose('英文',id);
   await page.locator('.opt').first().click();await settle();
   assert.equal(await page.locator('#memoryWrap, #memoryCard, .memory-extra').count(),0,'removed duplicate memory UI');
    const oldNote=await page.evaluate(()=>qnow().memory);
    assert((await page.locator('#guideCard').innerText()).includes(oldNote),'unique quick-memory content survives inside the subject guide');
    await page.locator('#questionBtn').click();await settle();
    assert.equal(await page.locator('#guideCard').isVisible(),false,'question button focuses the question');
    await page.locator('#explainBtn').click();await settle();
    assert.equal(await page.locator('#guideCard').isVisible(),true,'explanation button reopens guide');
    const vocab=await page.locator('#guideCard').innerText();
    for(const label of ['初級','中級','高級','中文：'])assert(vocab.includes(label),id+' guide '+label);
    assert(!/\b(low|mid|high)\s*:/i.test(vocab));
    assert.equal((await page.locator('#guideCard .exam-highlight').innerText()).toLowerCase(),word);
    assert.equal(await page.locator('#correctAnswer .option-detail-grid').count(),0,'no English subject metadata repeated in correct option');
    const labels=await page.locator('#guideCard .guide-block h3').allTextContents();
    assert.deepEqual(labels.slice(0,5),['中文翻譯','發音','同意相關單字','反意相關單字','新聞時事例句'],'English vocabulary leads guide');
    assert.equal(labels.filter(x=>x==='新聞時事中文翻譯').length,0,'bilingual example does not copy translation twice');
    // Deliberately choose a wrong option so this isolated profile has a review card.
   const wrong=await page.evaluate(()=>LETTERS.find(x=>x!==qnow().answer));
   await page.locator('.opt[data-a="'+wrong+'"]').click();await settle();
   await page.locator('#navHandle').click();
   await page.locator('#reviewTop').click();
   const card=page.locator('.wrong-card').filter({has:page.locator('[data-key="英文|'+id+'"]')});
   assert.equal((await card.locator('.exam-highlight').innerText()).toLowerCase(),word);
   const text=await card.innerText();
   for(const label of ['初級','中級','高級','中文：'])assert(text.includes(label));
   assert(!/\b(low|mid|high)\s*:/i.test(text));
   report.english.push({question:id,highlight:word,surfaces:3,status:'passed'});
  }
  // Every question in both themes at all requested dimensions, with genuine scroll geometry.
  for(const [width,height] of sizes){
   await page.setViewportSize({width,height});
   for(const theme of ['light','dark']){
    await page.evaluate(t=>{document.documentElement.dataset.theme=t;state.theme=t;},theme);
    for(const q of qs){
     await choose(q.subject,q.id);await page.waitForTimeout(40);
     const img=page.locator('.source-figure img');await img.scrollIntoViewIfNeeded();
     // A lazy-loaded WebP must finish decoding before geometry assertions.
     // Keep the same strict ratio threshold: genuine distortion still fails CI.
     await img.evaluate(async i=>{
      await i.decode();
      if(!i.complete||i.naturalWidth<=0||i.naturalHeight<=0)
       throw Error('WebP was not decoded: '+i.getAttribute('src'));
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
     });
     const imageGeometry=await img.evaluate(i=>{
      const r=i.getBoundingClientRect();
      return {renderedWidth:r.width,renderedHeight:r.height,
       naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,src:i.getAttribute('src')};
     });
     const ratio=Math.abs(imageGeometry.renderedWidth/imageGeometry.renderedHeight-
                          imageGeometry.naturalWidth/imageGeometry.naturalHeight);
     assert(Number.isFinite(ratio)&&ratio<0.03,
      'undistorted decoded image '+q.subject+q.id+' '+JSON.stringify({ratio,imageGeometry}));
     await noOverflow('question overflow '+width+' '+q.subject+q.id);
     const colors=await page.evaluate(()=>['#questionCard','#answerCard'].map(s=>getComputedStyle(document.querySelector(s)).backgroundColor));
     assert.notEqual(colors[0],colors[1]);
     assert.equal(await page.locator('#questionCard .opt').count(),0,'answers are in a separate card');
     assert.equal(await page.locator('#answerCard .opt').count(),4);
     await page.locator('.opt').first().click();await settle();
     const geometry=await page.evaluate(()=>{
       const guide=document.querySelector('#guideCard').getBoundingClientRect(),c=document.querySelector('#correctAnswer').getBoundingClientRect();
       return {gap:guide.top-c.bottom,left:Math.abs(c.left-guide.left),width:Math.abs(c.width-guide.width),answerTop:c.top,viewportHeight:innerHeight,scrollY,maxScroll:document.documentElement.scrollHeight-innerHeight,spacer:document.querySelector('#answerScrollSpace').getBoundingClientRect().height};
      });
      assert(geometry.gap>=8&&geometry.gap<=12,JSON.stringify({width,height,theme,subject:q.subject,id:q.id,geometry}));
      assert(geometry.left<=2&&geometry.width<=3);
      assert(geometry.answerTop>=-1&&geometry.answerTop+44<geometry.viewportHeight,'answer visible in viewport '+JSON.stringify({width,height,subject:q.subject,id:q.id,geometry}));
      assert.equal(await page.locator('#correctAnswer + #guideCard').count(),1,'guide is the only block after the correct option');
      assert.equal(await page.locator('#memoryWrap, #memoryCard').count(),0,'memory block removed at every viewport');
      if(['數學 B','經濟學','會計學'].includes(q.subject)){
      const shouldCalculate=q.subject==='數學 B'||(q.subject==='經濟學'&&[26,27,28].includes(q.id));
      assert.equal(await page.locator('#correctAnswer .calculation-step').count(),0,'calculation steps only in subject guide');
       assert.equal(await page.locator('#guideCard .guide-block h3').first().innerText()==='考題計算式',shouldCalculate,'calculation is first when applicable');
       const count=await page.locator('#guideCard .calculation-step').count();assert(shouldCalculate?count>=3:count===0);
       assert.equal((await page.locator('#guideCard .guide-block h3').allTextContents()).filter(x=>x==='考題計算式').length,shouldCalculate?1:0,'calculation appears exactly once');
      }
      if(q.subject==='國文'){
      const t=await page.locator('#correctAnswer .option-detail').innerText();assert(!/(?:^|[｜／\n])(?:低|中|高)[：:]/.test(t));
     }
     await noOverflow('answer overflow '+width+' '+q.subject+q.id);
    }
    await page.screenshot({path:path.join(output,`demo-${width}x${height}-${theme}.png`)});
    await page.locator('#navHandle').click();await page.locator('#reviewTop').click();await noOverflow('review overflow '+width);
    assert.equal(await page.locator('#progressShell').isVisible(),false,'review never shows study picker');
    assert.equal(await page.locator('#navToggle').isVisible(),false);
    const controls=await page.locator('.review-toolbar > *').evaluateAll(es=>es.map(e=>getComputedStyle(e).backgroundColor));
    assert.equal(new Set(controls).size,3,'three distinct control backgrounds');
    assert.equal(await page.locator('.review-toolbar svg').count(),3);
    const cards=await page.locator('.wrong-card').evaluateAll(es=>es.map(e=>getComputedStyle(e).backgroundColor));
    assert.equal(new Set(cards).size,cards.length,'each wrong question has a distinct light background');
    await page.screenshot({path:path.join(output,`review-${width}x${height}-${theme}.png`)});
    report.rwd.push({width,height,theme,questions:35,status:'passed'});
   }
  }
  // Touch context has no hover effect; grading colors retain precedence under mouse hover.
  const touch=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  const mobile=await touch.newPage();await mobile.goto(base+'v4-115-multisubject-review-demo.html');
  await mobile.locator('#homeYearSel').selectOption('demo');
  await mobile.locator('#homeSubjectSel').selectOption({label:'英文'});
  const before=await mobile.locator('.opt').first().evaluate(e=>getComputedStyle(e).backgroundColor);
  await mobile.locator('.opt').first().hover();await mobile.waitForTimeout(230);
  assert.equal(await mobile.locator('.opt').first().evaluate(e=>getComputedStyle(e).backgroundColor),before);
  await mobile.locator('.opt').first().tap();await mobile.waitForTimeout(400);
  await mobile.locator('#navHandle').click();await mobile.waitForTimeout(300);
  assert.equal(await mobile.locator('#navHandle').getAttribute('aria-expanded'),'true');
  await mobile.locator('.chip').nth(1).click();
  assert.equal(await mobile.locator('#navHandle').getAttribute('aria-expanded'),'false');
  await touch.close();
  await page.setViewportSize({width:1440,height:900});await choose('英文',1);
  await page.locator('.opt[data-a="A"]').click();await settle();
  for(const selector of ['.opt.correct','.opt.wrong']){
   const el=page.locator(selector),color=await el.evaluate(e=>getComputedStyle(e).backgroundColor);
   await el.hover();await page.waitForTimeout(230);assert.equal(await el.evaluate(e=>getComputedStyle(e).backgroundColor),color);
  }
  assert.deepEqual(errors,[]);report.status='passed';report.generatedCount=30;report.ocrPerformed=false;report.errors=errors;
  fs.writeFileSync(path.join(output,'sudu-demo-acceptance.json'),JSON.stringify(report,null,2));
  console.log('PASS: 35 images; 30 hashes; 5 English questions x 4 surfaces; 35 questions x 8 viewports x 2 themes; touch and graded hover');
 }catch(e){
  report.status='failed';report.error=e.stack;
  // Observe genuine click geometry and CSS for a full second on failure.
  // Do not force clicks, disable assertions, or turn failures into PASS.
  report.clickGeometry=[];
  try{
   for(let sample=0;sample<14;sample++){
    report.clickGeometry.push(await page.evaluate(()=>{
     const btn=document.querySelector('.opt'),answer=document.querySelector('#answerCard');
     const rect=btn?.getBoundingClientRect(),ar=answer?.getBoundingClientRect();
     const cs=btn?getComputedStyle(btn):null;
     return {time:Math.round(performance.now()),scrollY:window.scrollY,
      reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,
      scrollBehavior:getComputedStyle(document.documentElement).scrollBehavior,
      option:rect?{top:rect.top,left:rect.left,width:rect.width,height:rect.height}:null,
      answerTop:ar?.top, transform:cs?.transform,animation:cs?.animationName,
      transition:cs?.transitionDuration,htmlHeight:document.documentElement.scrollHeight,
      activeAnimations:document.getAnimations().slice(0,8).map(a=>({playState:a.playState,
       animationName:a.animationName||null}))};
    }));
    await page.waitForTimeout(65);
   }
  }catch(debugError){report.geometryError=String(debugError);}
  fs.writeFileSync(path.join(output,'sudu-demo-acceptance.json'),JSON.stringify(report,null,2));
  await page.screenshot({path:path.join(output,'demo-acceptance-failure.png')});throw e;
 }
 finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1)});
