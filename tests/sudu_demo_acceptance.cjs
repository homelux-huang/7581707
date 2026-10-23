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
  await page.evaluate(({subject,id})=>{currentSubject=subject;currentIndex=list().findIndex(q=>q.id===id);showStudy();renderAll();closeQuestionNav();window.scrollTo(0,0);},{subject,id});
 };
 const settle=()=>page.waitForTimeout(400);
 const noOverflow=async(label)=>{const layout=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,offenders:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.right>innerWidth+1&&getComputedStyle(e).position!=='fixed'}).slice(0,12).map(e=>({tag:e.tagName,id:e.id,cls:e.className,right:e.getBoundingClientRect().right}))}));assert(layout.scrollWidth<=layout.width+1,label+' '+JSON.stringify(layout));};
 try{
  await page.goto(base+'v4-115-multisubject-review-demo.html');
  const clockBefore=await page.locator('#examClock').innerText();
  assert(/天.*時.*分.*秒/.test(clockBefore));
  await page.waitForTimeout(1100);assert.notEqual(await page.locator('#examClock').innerText(),clockBefore,'countdown ticks each second');
  const edges=await page.evaluate(()=>[countdownText(EXAM_DAY_START-1000),countdownText(EXAM_DAY_START),countdownText(EXAM_DAY_END)]);
  assert.deepEqual(edges,['0天 00時 00分 01秒','統測考試期間，加油！','本屆統測已結束']);
  const qs=await page.evaluate(()=>JSON.parse(document.getElementById('demoData').textContent).questions);
  assert.equal(qs.length,35);
  for(const [subject,ids] of Object.entries(expected))assert.deepEqual(qs.filter(q=>q.subject===subject).map(q=>q.id),ids);
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
   await page.locator('.opt').first().click();await settle();
   assert.equal(await page.locator('.option-detail').count(),4);
   assert((await page.locator('#guideCard').innerText()).includes('頁數：待核對'));
  }
  // All five English words and their actual inflections in all four required surfaces.
  for(const [id,word] of [[1,'wet'],[2,'joined'],[3,'equally'],[4,'suitable'],[5,'attract']]){
   await choose('英文',id);
   await page.locator('.opt').first().click();await settle();
   await page.locator('.memory-extra summary').scrollIntoViewIfNeeded();
   const beforeExpand=await page.evaluate(()=>scrollY);
   await page.locator('.memory-extra summary').click();
   await page.waitForTimeout(100);
   assert(Math.abs(await page.evaluate(()=>scrollY)-beforeExpand)<3,'extension expands in place');
   await page.locator('.memory-close').click();
   assert.equal(await page.locator('#memoryWrap').isVisible(),false);
   await page.locator('#explainBtn').click();await settle();
   assert.equal(await page.locator('#memoryWrap').isVisible(),true);
   await page.locator('#questionBtn').click();await settle();
   assert.equal(await page.locator('#memoryWrap').isVisible(),false);
   await page.locator('#explainBtn').click();await settle();

   for(const selector of ['#correctAnswer .option-detail','#guideCard','#memoryCard']){
    const text=await page.locator(selector).innerText();
    for(const label of ['初級','中級','高級','中文：'])assert(text.includes(label),id+' '+selector+' '+label);
    assert(!/\b(low|mid|high)\s*:/i.test(text));
    assert.equal((await page.locator(selector+' .exam-highlight').innerText()).toLowerCase(),word);
   }
   // Deliberately choose a wrong option so this isolated profile has a review card.
   const wrong=await page.evaluate(()=>LETTERS.find(x=>x!==qnow().answer));
   await page.locator('.opt[data-a="'+wrong+'"]').click();await settle();
   await page.locator('#reviewTop').click();
   const card=page.locator('.wrong-card').filter({has:page.locator('[data-key="英文|'+id+'"]')});
   assert.equal((await card.locator('.exam-highlight').innerText()).toLowerCase(),word);
   const text=await card.innerText();
   for(const label of ['初級','中級','高級','中文：'])assert(text.includes(label));
   assert(!/\b(low|mid|high)\s*:/i.test(text));
   report.english.push({question:id,highlight:word,surfaces:4,status:'passed'});
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
      const m=document.querySelector('#memoryCard').getBoundingClientRect(),c=document.querySelector('#correctAnswer').getBoundingClientRect(),b=document.querySelector('.bottom').getBoundingClientRect();
      return {gap:m.top-c.bottom,left:Math.abs(c.left-m.left),width:Math.abs(c.width-m.width),memoryTop:m.top,memoryBottom:m.bottom,answerTop:c.top,bottomTop:b.top,scrollY,maxScroll:document.documentElement.scrollHeight-innerHeight,spacer:document.querySelector('#answerScrollSpace').getBoundingClientRect().height};
     });
     assert(geometry.gap>=8&&geometry.gap<=12,JSON.stringify({width,height,theme,subject:q.subject,id:q.id,geometry}));
     assert(geometry.left<=2&&geometry.width<=3);
     assert(geometry.answerTop>=-1&&geometry.answerTop+44<geometry.bottomTop,'answer visible above bottom bar '+JSON.stringify({width,height,subject:q.subject,id:q.id,geometry}));
     const joined=await page.evaluate(()=>{const m=document.querySelector('#memoryCard'),g=document.querySelector('#guideCard'),a=m.getBoundingClientRect(),b=g.getBoundingClientRect();return {adjacent:m.nextElementSibling===g,gap:b.top-a.bottom,left:Math.abs(a.left-b.left),width:Math.abs(a.width-b.width)};});
     assert(joined.adjacent&&Math.abs(joined.gap)<=1&&joined.left<=1&&joined.width<=1,'memory directly joins explanation '+JSON.stringify(joined));
     if(['數學 B','經濟學','會計學'].includes(q.subject)){
      const shouldCalculate=q.subject==='數學 B'||(q.subject==='經濟學'&&[26,27,28].includes(q.id));
      assert.equal((await page.locator('#correctAnswer .option-detail').innerText()).includes('考題計算式'),shouldCalculate);
      const count=await page.locator('#correctAnswer .calculation-step').count();assert(shouldCalculate?count>=3:count===0);
      if(!shouldCalculate){assert.equal(await page.locator('#memoryCard .calculation-step').count(),0);assert.equal(await page.locator('#guideCard .calculation-step').count(),0);}

     }
     if(q.subject==='國文'){
      const t=await page.locator('#correctAnswer .option-detail').innerText();assert(!/(?:^|[｜／\n])(?:低|中|高)[：:]/.test(t));
     }
     await noOverflow('answer overflow '+width+' '+q.subject+q.id);
    }
    await page.screenshot({path:path.join(output,`demo-${width}x${height}-${theme}.png`)});
    await page.locator('#reviewTop').click();await noOverflow('review overflow '+width);
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
  const before=await mobile.locator('.opt').first().evaluate(e=>getComputedStyle(e).backgroundColor);
  await mobile.locator('.opt').first().hover();await mobile.waitForTimeout(230);
  assert.equal(await mobile.locator('.opt').first().evaluate(e=>getComputedStyle(e).backgroundColor),before);
  await mobile.locator('.opt').first().tap();await mobile.waitForTimeout(400);
  await mobile.locator('#navToggle').click();await mobile.waitForTimeout(300);
  assert.equal(await mobile.locator('#navToggle').getAttribute('aria-expanded'),'true');
  await mobile.locator('.chip').nth(1).click();
  assert.equal(await mobile.locator('#navToggle').getAttribute('aria-expanded'),'false');
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
 }catch(e){report.status='failed';report.error=e.stack;fs.writeFileSync(path.join(output,'sudu-demo-acceptance.json'),JSON.stringify(report,null,2));await page.screenshot({path:path.join(output,'demo-acceptance-failure.png')});throw e;}
 finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1)});
