/* Chromium integration checks using real data plus explicitly synthetic edge fixtures. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
const output=process.env.SUDU_TEST_OUTPUT||'test-results';
(async()=>{
 fs.mkdirSync(output,{recursive:true});const results=[];
 const browser=await chromium.launch({headless:true,args:['--no-sandbox'],...(process.env.SUDU_BROWSER_EXECUTABLE?{executablePath:process.env.SUDU_BROWSER_EXECUTABLE}:{})});
 const context=await browser.newContext({viewport:{width:1280,height:900},reducedMotion:'reduce'});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const passed=(name,detail={})=>{results.push({name,status:'passed',...detail});console.log('PASS: '+name);};
 const loadedImage=async locator=>{await locator.scrollIntoViewIfNeeded();await page.waitForFunction(img=>img.complete&&img.naturalWidth>0,await locator.elementHandle(),{timeout:15000});};
 try{
  await page.goto(base,{waitUntil:'domcontentloaded'});await page.locator('#sudu-question-dock').waitFor();
  const first=await page.evaluate(()=>available()[0]);
  await page.locator('[data-answer="'+first.answer+'"]').click();
  assert.equal(await page.locator('.sudu-option-reasons > li').count(),first.options.length);
  assert.equal(await page.locator('#sudu-workspace [data-block="answer"]').count(),1);
  assert.equal(await page.evaluate(id=>state.attempts[id].at(-1).correct,first.id),true);
  passed('answer saved and all option reasons rendered');

  await page.evaluate(()=>{ui.subject='英文';ui.index=0;filters();render();});
  const english=await page.evaluate(()=>available()[0]);
  const englishTerm=page.locator('.sudu-option-content .sudu-hover-term').first();await englishTerm.waitFor();await englishTerm.click();
  assert.equal(await page.locator('#sudu-hover-card').isVisible(),true);
  assert.equal(await page.evaluate(id=>(state.attempts[id]||[]).length,english.id),0,'word click must not submit an answer');
  assert((await page.locator('#sudu-hover-card').innerText()).includes('N/A'));
  await page.keyboard.press('Escape');assert.equal(await page.locator('#sudu-hover-card').isVisible(),false);
  await page.evaluate(()=>{ui.subject='國文';ui.index=0;filters();render();});
  const chinese=await page.evaluate(()=>available()[0]);await page.locator('.sudu-option-content .sudu-hover-term').first().click();
  assert.equal(await page.evaluate(id=>(state.attempts[id]||[]).length,chinese.id),0);
  await page.locator('[data-hover-close]').click();
  passed('Chinese and English option vocabulary is separate from answering; N/A and Escape work');

  for(const width of [320,375,390,430,768,1024,1280,1440]){
   await page.setViewportSize({width,height:900});
   for(const theme of ['light','dark']){
    await page.evaluate(t=>{suduTheme(t);ui.subject='英文';ui.index=0;filters();render();},theme);
    await page.locator('.sudu-option-content .sudu-hover-term').first().click();
    const card=await page.locator('#sudu-hover-card').boundingBox();
    assert(card.x>=0&&card.y>=0&&card.x+card.width<=width+1&&card.y+card.height<=901,'hover card stays inside '+width+' '+theme);
    await page.locator('[data-hover-close]').click();
    assert.equal(await page.evaluate(id=>(state.attempts[id]||[]).length,english.id),0);
   }
  }
  await page.setViewportSize({width:1280,height:900});await page.evaluate(()=>suduTheme('light'));
  passed('hover cards fit all eight widths and both themes without intercepting answer choices');

  await page.evaluate(async()=>{await suduLoadOfficialYear('115');ui.year='115';ui.paper='00-C';ui.subject='國文';ui.index=0;ui.tab='learn';filters();render();});
  const original=page.locator('[data-image-role="question"] .sudu-image-open img').first();await original.waitFor();
  await loadedImage(original);
  const mapping=await original.evaluate(img=>({width:img.naturalWidth,src:img.getAttribute('src'),filter:getComputedStyle(img).filter}));assert(mapping.width>0&&mapping.src.endsWith('.webp'));assert.equal(mapping.filter,'none');
  assert.equal(await page.locator('[data-image-role="answer"] img').count(),0,'answer sheet is absent before answer');
  await page.locator('[data-image-role="question"] .sudu-image-open').first().click();assert.equal(await page.locator('#sudu-image-dialog').isVisible(),true);await page.keyboard.press('Escape');
  await page.locator('[data-answer="0"]').click();
  await page.locator('.sudu-answer-images').waitFor();assert.equal(await page.locator('.sudu-answer-images').getAttribute('open'),null);
  assert.equal(await page.locator('.sudu-question-ball').first().getAttribute('data-status'),'pending');
  await page.locator('.sudu-answer-images summary').click();const answerImage=page.locator('[data-image-role="answer"] img').first();await loadedImage(answerImage);
  passed('real original and answer WebP, no inversion, zoom, pre-answer privacy and pending grade',mapping);
  await page.setViewportSize({width:375,height:812});await page.locator('[data-image-role="question"] .sudu-image-open').first().click();
  const modal=await page.locator('#sudu-image-dialog').boundingBox();assert(modal.x>=0&&modal.x+modal.width<=376&&modal.y>=0&&modal.y+modal.height<=813);
  await page.locator('[data-image-zoom]').click();await page.locator('[data-image-close]').click();await page.setViewportSize({width:1280,height:900});
  passed('mobile original WebP zoom and close fit the viewport');

  await page.evaluate(()=>switchTab('dashboard'));await page.waitForFunction(()=>Object.keys(ALL.officialYearReports).length>=26);
  const resume=page.locator('[data-resume-year="115"][data-resume-paper="00-C"]');await resume.first().click();
  assert.equal(await page.evaluate(()=>ui.index),1,'resume goes to first unanswered real question');
  const code=await page.evaluate(()=>localStorage.getItem('sudu_device_profile_v1'));
  await page.evaluate(()=>switchTab('dashboard'));await page.locator('[data-resume-year="115"][data-resume-paper="00-C"]').nth(1).click();assert.equal(await page.evaluate(()=>ui.index),1);
  assert.equal(await page.evaluate(()=>localStorage.getItem('sudu_device_profile_v1')),code);
  passed('both annual paper name and progress status resume without erasing identity or answers');

  const caseData=await page.evaluate(()=>{
   const q=ALL.practice[0],answer=q.answer,wrong=q.options.findIndex((_,i)=>i!==answer);state.attempts[q.id]=[{choice:answer,correct:true,at:'2026-10-01T00:00:00Z'},{choice:wrong,correct:false,at:'2026-10-02T00:00:00Z'}];state.reviewHistory[q.id]=[{choice:wrong,correct:false,at:'2026-10-03T00:00:00Z'},{choice:answer,correct:true,at:'2026-10-04T00:00:00Z'}];state.dashboard={year:'全部',subject:'全部科目'};save();switchTab('dashboard');return {id:q.id,wrong};
  });
  await page.locator('#db-all-mistakes').click();assert.equal(await page.evaluate(()=>ui.tab),'mistakes');assert.equal(await page.locator('#review-'+caseData.id).count(),1);assert((await page.locator('#review-'+caseData.id).innerText()).includes('累計錯誤事件 2 次'));
  await page.evaluate(()=>switchTab('clinic'));assert.equal(await page.locator('#review-'+caseData.id).count(),0,'first-attempt-wrong set is distinct');
  await page.evaluate(()=>switchTab('mistakes'));await page.locator('#review-'+caseData.id+' [data-clinic-answer]').first().click();assert.equal(await page.evaluate(id=>state.attempts[id][0].correct,caseData.id),true);
  passed('all-ever-wrong differs from initial-attempt-wrong; review history appends');

  await page.evaluate(()=>{
   const q={...ALL.practice[0],id:'fixture-multiple-accepted',year:'自編',official:false,acceptedAnswers:[0,1],answer:0,options:['測試接受A','測試接受B','測試錯C','測試錯D'],question:'僅在隔離測試頁使用的多個接受答案 fixture'};ALL.practice.push(q);ui.year='自編';ui.paper='自編';ui.subject=q.subject;filters();ui.index=available().findIndex(x=>x.id===q.id);ui.tab='learn';render();
  });
  await page.locator('[data-answer="1"]').click();assert.equal(await page.evaluate(()=>state.attempts['fixture-multiple-accepted'].at(-1).correct),true);assert((await page.locator('#sudu-workspace [data-block="answer"]').innerText()).includes('A／B'));assert.equal(await page.locator('.option.right').count(),2);
  passed('multiple officially accepted choices never mark an accepted alternative wrong (synthetic fixture)');

  await page.route('**/data/original/**/*.webp',route=>route.abort());
  await page.evaluate(()=>{ui.year='115';ui.paper='00-MB';ui.subject='全部科目';ui.index=0;filters();render();});
  await page.locator('[data-image-role="question"] .sudu-image-error:not([hidden])').first().waitFor();
  assert(await page.locator('[data-image-retry]').first().isEnabled());await page.unroute('**/data/original/**/*.webp');
  passed('offline image failure exposes clear retry instead of fabricated question');

  await page.evaluate(()=>{ui.year='自編';ui.paper='自編';ui.subject='全部科目';ui.index=0;filters();render();window.suduTestOriginalSetItem=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new DOMException('synthetic quota failure','QuotaExceededError');};});
  await page.locator('[data-answer="0"]').click();assert.equal(await page.locator('#sudu-save-warning').isVisible(),true);assert((await page.locator('#sudu-save-warning').innerText()).includes('本機儲存失敗'));
  await page.evaluate(()=>{Storage.prototype.setItem=window.suduTestOriginalSetItem;delete window.suduTestOriginalSetItem;save();render();});assert.equal(await page.locator('#sudu-save-warning').count(),0);
  passed('storage failure is explicit and in-memory answers can be saved again without clearing history');

  // A corrupt UI preference must never prevent valid student state from loading.
  // Seed a separate browser profile so the main integration scenario stays intact.
  const paperSeed=await page.evaluate(()=>{
   const qs=ALL.officialQuestions.filter(q=>String(q.year)==='115'&&q.paper==='00-C');
   return {choices:Object.fromEntries(qs.map(q=>[q.id,0])),versions:Object.fromEntries(qs.map(q=>[q.id,SUDU_SCORING.fingerprint(q)]))};
  });
  const protectedProfile={id:'SUDU-0123456789ABCDEF01234567',created:'2025-01-01T00:00:00.000Z',name:'隔離回歸測試學習者'};
  const protectedSubmission={id:'fixture-preserved-submission',year:'115',paper:'00-C',startedAt:'2026-10-01T00:00:00.000Z',submittedAt:'2026-10-01T00:10:00.000Z',elapsedMs:600000,activeMs:null,choices:paperSeed.choices,questionVersions:paperSeed.versions,questionCount:Object.keys(paperSeed.choices).length,ruleVersion:null};
  const protectedState={attempts:{[first.id]:[{choice:first.options.findIndex((_,i)=>i!==first.answer),correct:false,at:'2026-10-01T00:00:00.000Z'},{choice:first.answer,correct:true,at:'2026-10-02T00:00:00.000Z'}]},reviewAnswers:{},reviewHistory:{},extended:{},examSubmissions:{'115/00-C':protectedSubmission},examSubmissionHistory:{'115/00-C':[{...protectedSubmission,id:'fixture-preserved-retake',submittedAt:'2026-10-03T00:10:00.000Z'}]}};
  const damagedContext=await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce',storageState:{cookies:[],origins:[{origin:new URL(base).origin,localStorage:[{name:'sudu_sites_ui',value:'{broken'},{name:'sudu_sites_state',value:JSON.stringify(protectedState)},{name:'sudu_device_profile_v1',value:JSON.stringify(protectedProfile)}]}]}});
  try{
   const damagedPage=await damagedContext.newPage(),damagedErrors=[];damagedPage.on('pageerror',e=>damagedErrors.push(e.message));
   await damagedPage.goto(base,{waitUntil:'domcontentloaded'});await damagedPage.locator('#sudu-question-dock').waitFor();await damagedPage.waitForFunction(()=>suduMirrorReady===true);
   const inspect=()=>damagedPage.evaluate(()=>({memory:{attempts:state.attempts,examSubmissions:state.examSubmissions,examSubmissionHistory:state.examSubmissionHistory},saved:JSON.parse(localStorage.getItem('sudu_sites_state')),profile:JSON.parse(localStorage.getItem('sudu_device_profile_v1'))}));
   for(let load=0;load<2;load++){
    const kept=await inspect();
    for(const key of ['attempts','examSubmissions','examSubmissionHistory']){
     assert.deepEqual(kept.memory[key],protectedState[key],'corrupt UI must preserve in-memory '+key);
     assert.deepEqual(kept.saved[key],protectedState[key],'corrupt UI must preserve persisted '+key);
    }
    assert.deepEqual(kept.profile,protectedProfile,'corrupt UI must not replace the original browser identity');
    if(load===0){await damagedPage.reload({waitUntil:'domcontentloaded'});await damagedPage.locator('#sudu-question-dock').waitFor();await damagedPage.waitForFunction(()=>suduMirrorReady===true);}
   }
   assert.deepEqual(damagedErrors,[]);
  }finally{await damagedContext.close();}
  passed('corrupt UI JSON preserves first error, all submitted snapshots and device identity across reload in an isolated profile');

  const root=new URL('../',base).href;
  await page.goto(root,{waitUntil:'domcontentloaded'});
  await page.waitForURL('**/sudu/v4-115-multisubject-review-demo.html');
  assert((await page.title()).includes('115 全科'));
  assert.equal(await page.locator('#subjectSel option').count(),7);
  assert(await page.locator('#reviewTop').isVisible());
  assert.equal(await page.locator('.header-actions #reviewTop').count(),1,'wrong-review entry must live in header');
  assert.equal(await page.locator('.progress-actions #reviewTop').count(),0,'wrong-review entry must not remain in question picker');
  assert.equal(await page.locator('.chip').first().evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(255, 255, 255)','unanswered question chip is white');

  const cropManifest=await page.evaluate(async()=>{const r=await fetch('questions/115/crop-manifest.json');if(!r.ok)throw new Error('crop manifest '+r.status);return r.json()});
  assert.equal(cropManifest.generatedCount,30,'30 non-accounting demo questions have generated single-question WebPs');
  assert(cropManifest.items.every(x=>x.ocrPerformed===false),'question WebP generation must not perform OCR');
  assert(cropManifest.items.every(x=>x.outputSize[0]>x.outputSize[1]),'generated crops must be single-question strips rather than portrait full pages');
  const imageAudit=await page.evaluate(async()=>{
   const qs=JSON.parse(document.getElementById('demoData').textContent).questions;
   const rows=[];
   for(const q of qs){
    const row=await new Promise(resolve=>{
     const img=new Image();
     img.onload=()=>resolve({subject:q.subject,id:q.id,src:q.image||'',w:img.naturalWidth,h:img.naturalHeight,ok:true});
     img.onerror=()=>resolve({subject:q.subject,id:q.id,src:q.image||'',w:0,h:0,ok:false});
     img.src=q.image||'';
    });
    rows.push(row);
   }
   return rows;
  });
  assert.equal(imageAudit.length,35,'35 demo questions audited for single-question WebP');
  assert(imageAudit.every(x=>x.ok&&x.w>0&&x.h>0),'every demo question image decodes');
  assert(imageAudit.every(x=>x.w>x.h),'every displayed question image is a cropped question strip, not a full portrait exam page');
  assert(imageAudit.filter(x=>x.subject!=='會計學').every(x=>!x.src.includes('/data/original/')),'non-accounting questions never point the UI at a full original page');

  await page.locator('#subjectSel').selectOption({label:'英文'});
  const questionBg=await page.locator('#questionCard').evaluate(el=>getComputedStyle(el).backgroundColor);
  const firstOption=page.locator('.opt').first();
  const optionBg=await firstOption.evaluate(el=>getComputedStyle(el).backgroundColor);
  assert.notEqual(questionBg,optionBg,'question block and answer option blocks use different backgrounds');
  const hoverBefore=optionBg;
  await firstOption.hover();await page.waitForTimeout(230);
  const hoverAfter=await firstOption.evaluate(el=>getComputedStyle(el).backgroundColor);
  assert.notEqual(hoverBefore,hoverAfter,'answer option hover animates to a different background');
  const figureBox=await page.locator('.source-figure').boundingBox();
  const optionsBox=await page.locator('.options').boundingBox();
  assert(figureBox&&optionsBox&&figureBox.y<optionsBox.y,'single-question WebP appears below the question text and before answer options');

  await page.locator('.opt[data-a="A"]').click();
  await page.waitForTimeout(340);
  assert.equal(await page.locator('#memoryWrap').isVisible(),true,'memory card appears automatically after answering');
  assert.equal(await page.locator('.memory-actions button').count(),4,'memory card has four learning actions');
  assert.equal(await page.locator('.memory-actions [data-go="出處"]').count(),1,'memory card includes source action');
  const iconColors=await page.locator('.memory-action-icon').evaluateAll(nodes=>nodes.map(n=>getComputedStyle(n).backgroundColor));
  assert.equal(new Set(iconColors).size,4,'four memory mini-diagrams use distinct high-contrast colors');
  assert((await page.locator('#correctAnswer .option-detail').innerText()).includes('正確解答'),'correct option is labeled 正確解答');
  const englishCorrectText=await page.locator('#correctAnswer .option-detail').innerText();
  assert(englishCorrectText.includes('初級')&&englishCorrectText.includes('中級')&&englishCorrectText.includes('高級'),'English synonym/antonym levels use 初級／中級／高級');
  assert(!/\blow\s*:|\bmid\s*:|\bhigh\s*:/i.test(englishCorrectText),'English detail no longer exposes low/mid/high labels');
  assert(englishCorrectText.includes('中文：'),'English current-affairs example includes Chinese translation');
  assert.equal(await page.locator('#correctAnswer .exam-highlight').count(),1,'tested English word is highlighted in the news example');
  await page.waitForTimeout(80);
  const memoryBox=await page.locator('#memoryCard').boundingBox();
  const correctBox=await page.locator('#correctAnswer').boundingBox();
  assert(Math.abs(memoryBox.x-correctBox.x)<=2,'memory and correct answer left edges align');
  assert(Math.abs(memoryBox.width-correctBox.width)<=3,'memory and correct answer widths align');
  const answerGap=correctBox.y-(memoryBox.y+memoryBox.height);
  assert(answerGap>=8&&answerGap<=12,'memory bottom and correct-answer top keep a safe 8-12px aligned gap; actual '+answerGap);
  assert.equal(await page.evaluate(()=>document.body.classList.contains('nav-auto')),true,'question picker auto-hides after answering starts');
  assert.equal(await page.locator('.chip.bad').first().evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(197, 44, 73)','wrong chip is red');
  let navBox=await page.locator('#progressShell').boundingBox();assert(navBox.y<0,'auto-hidden picker slides above viewport');
  await page.mouse.move(640,5);await page.waitForTimeout(340);
  assert.equal(await page.evaluate(()=>document.body.classList.contains('nav-peek')),true,'desktop top hover reveals question picker');
  navBox=await page.locator('#progressShell').boundingBox();assert(navBox.y>=-1,'hovered picker slides into view');
  await page.mouse.move(640,500);await page.waitForTimeout(1050);

  await page.locator('#subjectSel').selectOption({label:'國文'});
  await page.locator('.opt[data-a="C"]').click();
  assert.equal(await page.locator('.chip.ok').first().evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(19, 121, 91)','correct chip is green');


  await page.locator('#subjectSel').selectOption({label:'商業概論'});
  await page.locator('.chip').filter({hasText:'3'}).first().click();
  await page.locator('.opt').first().click();
  const businessMemory=await page.locator('#memoryCard').innerText();
  const businessGuide=await page.locator('#guideCard').innerText();
  assert(!/\bN\/A\b/i.test(businessMemory),'memory block must hide N/A subject-extension entries');
  assert(!/\bN\/A\b/i.test(businessGuide),'guide block must hide N/A entries');
  assert.equal(await page.locator('.memory-actions [data-go="公式／分錄"]').count(),0,'N/A formula icon is hidden from memory block');
  assert.equal(await page.locator('.memory-extra-grid').getByText('法規',{exact:true}).count(),0,'N/A business law entry is hidden from subject extension');
  assert.equal(await page.locator('#guideCard .guide-block').filter({hasText:'法規'}).count(),0,'N/A law block is hidden from guide');
  const extraStyle=await page.locator('.memory-extra').evaluate(el=>({background:getComputedStyle(el).backgroundColor,color:getComputedStyle(el).color,textAlign:getComputedStyle(el).textAlign}));
  assert.equal(extraStyle.background,'rgb(255, 255, 255)','subject extension uses white background');
  assert.equal(extraStyle.color,'rgb(17, 17, 17)','subject extension uses black text');
  assert.equal(extraStyle.textAlign,'center','subject extension text is centered');
  const sourceText=await page.locator('#guideCard .guide-block').filter({hasText:'出處'}).innerText();
  assert(!sourceText.includes('待核對')&&!sourceText.includes('N/A'),'unverified/missing source fields are hidden');
  const missingSource=await page.evaluate(()=>{
   const C=window.DEMO_LEARNING_CONFIG,book=C.bookProfile['商業概論'],chapter=C.chapterMap['商業概論|3'];
   delete C.bookProfile['商業概論'];delete C.chapterMap['商業概論|3'];renderAll();
   const state={action:document.querySelectorAll('.memory-actions [data-go="出處"]').length,block:[...document.querySelectorAll('#guideCard .guide-block h3')].some(x=>x.textContent==='出處')};
   C.bookProfile['商業概論']=book;C.chapterMap['商業概論|3']=chapter;renderAll();return state;
  });
  assert.equal(missingSource.action,0,'source icon is hidden when no valid source information exists');
  assert.equal(missingSource.block,false,'source guide block is hidden when no valid source information exists');

  await page.locator('#subjectSel').selectOption({label:'數位科技'});
  await page.locator('.chip').filter({hasText:'27'}).first().click();
  await page.locator('.opt').first().click();
  assert.equal(await page.locator('.memory-extra').count(),0,'subject extension is hidden when subject-specific data is unavailable');

  const demoSubjects=['國文','英文','數學 B','商業概論','數位科技','會計學','經濟學'];
  for(const subject of demoSubjects){
   await page.locator('#subjectSel').selectOption({label:subject});
   await page.locator('.opt').first().click();
   assert((await page.locator('#guideCard').innerText()).includes('出處'),subject+' should show source');
   assert((await page.locator('#guideCard').innerText()).includes('國立彰化高商'),subject+' source should prefer CHSC');
   assert(await page.locator('.option-detail').count()===4,subject+' should extend all four options after grading');
   if(subject!=='數位科技')assert(await page.locator('.memory-extra').count()===1,subject+' should show subject extension inside memory card');
  }

  await page.setViewportSize({width:390,height:844});
  assert(await page.locator('#navToggle').isVisible(),'mobile question-number trigger is visible');
  await page.locator('#navToggle').click();await page.waitForTimeout(300);
  assert.equal(await page.evaluate(()=>document.body.classList.contains('nav-open')),true,'mobile trigger opens question picker');
  navBox=await page.locator('#progressShell').boundingBox();assert(navBox.y>=-1,'mobile opened picker is visible');
  await page.locator('.chip').nth(1).click();await page.waitForTimeout(80);
  assert.equal(await page.evaluate(()=>document.body.classList.contains('nav-open')),false,'selecting a question closes mobile picker');

  await page.locator('#reviewTop').click();
  assert(await page.locator('.wrong-card').count()>=1);
  assert((await page.locator('.wrong-card').first().innerText()).includes('出處'));
  const sizes=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
  for(const [width,height] of sizes){
   await page.setViewportSize({width,height});
   await page.waitForTimeout(30);
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1);
   assert.equal(overflow,false,`horizontal overflow at ${width}x${height}`);
  }
  await page.goto(root+'?tools=1',{waitUntil:'domcontentloaded'});
  assert(new URL(page.url()).searchParams.get('tools')==='1');
  assert((await page.title()).length>0);
  passed('35-question demo: N/A and unknown learning items are hidden; valid subject extensions are white/black/centered; distinct question/answer blocks, animated hover, 35/35 single-question WebPs, bilingual highlighted English, memory alignment and eight widths pass');
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'sudu-browser-results.json'),JSON.stringify({status:'passed',results,errors},null,2));console.log(JSON.stringify({status:'passed',checks:results.length,results},null,2));
 }catch(e){fs.writeFileSync(path.join(output,'sudu-browser-results.json'),JSON.stringify({status:'failed',results,error:e.stack,errors},null,2));await page.screenshot({path:path.join(output,'sudu-browser-failure.png'),fullPage:false});throw e;}
 finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1);});
