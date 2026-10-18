/* Real Chromium P0 acceptance; counts and answer choices come from repository data. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
const output=process.env.SUDU_TEST_OUTPUT||'/tmp/sudu-workspace-test';
const widths=[320,375,390,430,768,1024,1280,1440];
const results=[];
const record=(name,detail={})=>results.push({name,status:'passed',...detail});
(async()=>{
 fs.mkdirSync(output,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox'],...(process.env.SUDU_BROWSER_EXECUTABLE?{executablePath:process.env.SUDU_BROWSER_EXECUTABLE}:{})});
 const context=await browser.newContext({viewport:{width:1280,height:900},reducedMotion:'reduce'});
 const page=await context.newPage(),errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 try{
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await page.locator('#sudu-question-dock .questionnav').waitFor();
  const source=await page.evaluate(()=>({count:available().length,q:available()[0],code:localStorage.getItem('sudu_device_profile_v1')}));
  assert(source.count>1,'fixture must have multiple real questions');
  assert.equal(await page.locator('.sudu-question-ball').count(),source.count);
  assert.equal(await page.locator('.sudu-head-actions #export').count(),1);
  assert.equal(await page.locator('.sudu-head-actions #sudu-theme-button').count(),1);
  assert.equal((await page.locator('[data-sudu-menu-trigger="functions"]').innerText()).replace(/\s+/g,' ').trim(),'個人學習 Dashboard ⌄');
  assert.equal(await page.locator('[data-sudu-menu-section="year"] #paper').count(),0);
  assert.equal(await page.locator('[data-sudu-menu-section="subject"] #paper').count(),1);
  assert.equal(await page.locator('[data-sudu-menu-section="subject"] #subject').count(),1);
  assert.equal(await page.locator('#sudu-floating-controls [data-tab="archive"],#sudu-floating-controls [data-tab="source"]').count(),0);
  record('three independent menus and original header controls');

  const menu=page.locator('#sudu-floating-controls'),trigger=page.locator('[data-sudu-menu-trigger="year"]');
  await trigger.hover();assert.equal(await menu.getAttribute('aria-hidden'),'false');
  const rect=await trigger.boundingBox(),panel=await menu.boundingBox();
  await page.mouse.move(rect.x+rect.width/2,rect.y+rect.height-1);
  await page.mouse.move(rect.x+rect.width/2,panel.y+35,{steps:8});
  assert.equal(await menu.getAttribute('aria-hidden'),'false','pointer can cross trigger/panel bridge');
  await page.mouse.move(1,850);
  assert.equal(await menu.getAttribute('aria-hidden'),'true','no delay when pointer leaves interaction region');
  await trigger.focus();await page.keyboard.press('ArrowDown');
  assert.equal(await page.evaluate(()=>document.activeElement.id),'year');
  await page.keyboard.press('Escape');assert.equal(await menu.getAttribute('aria-hidden'),'true');
  assert.equal(await trigger.evaluate(node=>node===document.activeElement),true);
  record('desktop hover bridge, immediate close, keyboard and Escape');

  const q=source.q,accepted=q.acceptedAnswers?.length?q.acceptedAnswers:[q.answer];
  const wrong=q.options.findIndex((_,i)=>!accepted.includes(i));
  assert(wrong>=0&&Number.isInteger(accepted[0]));
  await page.locator('[data-answer="'+wrong+'"]').click();
  assert.equal(await page.locator('.sudu-question-ball').first().getAttribute('data-status'),'incorrect');
  let saved=await page.evaluate(id=>JSON.parse(localStorage.getItem('sudu_sites_state')).attempts[id],q.id);
  assert.equal(saved[0].choice,wrong);assert.equal(saved[0].correct,false);
  await page.waitForFunction(()=>{const a=document.querySelector('#sudu-workspace [data-block="answer"]')?.getBoundingClientRect();const h=document.querySelector('.header').getBoundingClientRect();return a&&a.top>=h.bottom-2&&a.top<h.bottom+100;});
  const answerPosition=await page.evaluate(()=>{
   const answer=document.querySelector('#sudu-workspace [data-block="answer"]').getBoundingClientRect();
   const header=document.querySelector('.header').getBoundingClientRect(),dock=document.querySelector('#sudu-question-dock').getBoundingClientRect();
   return {top:answer.top,bottom:answer.bottom,header:header.bottom,dock:dock.top};
  });
  assert(answerPosition.top>=answerPosition.header-2&&answerPosition.top<answerPosition.dock,'answer begins between sticky header and dock');
  await page.locator('#sudu-return-to-question').click();
  await page.locator('[data-answer="'+accepted[0]+'"]').click();
  assert.equal(await page.locator('.sudu-question-ball').first().getAttribute('data-status'),'correct');
  saved=await page.evaluate(id=>JSON.parse(localStorage.getItem('sudu_sites_state')).attempts[id],q.id);
  assert.equal(saved[0].correct,false,'first mistake stays immutable');assert.equal(saved.at(-1).correct,true);
  record('save before explanation scroll, recent grade balls and original first error');

  await page.locator('#next2').click();
  assert.equal(await page.locator('#sudu-question-dock strong').innerText(),'2 / '+source.count);
  await page.locator('.sudu-question-ball').last().click();assert.equal(await page.locator('#next2').isDisabled(),true);
  await page.locator('.sudu-question-ball').first().click();assert.equal(await page.locator('#prev2').isDisabled(),true);
  await page.reload({waitUntil:'domcontentloaded'});await page.locator('.sudu-question-ball').first().waitFor();
  assert.equal(await page.locator('.sudu-question-ball').first().getAttribute('data-status'),'correct');
  assert.equal(await page.evaluate(()=>localStorage.getItem('sudu_device_profile_v1')),source.code,'student code is unchanged');
  record('next/previous boundaries, all balls, jumping, refresh and identity preservation',{questionCount:source.count});

  const custom=['source','extension','question','explanation','answer'];
  await page.evaluate(order=>{localStorage.setItem('sudu_layout_order_v1',JSON.stringify(order));suduReadLayout();render();},custom);
  assert.deepEqual(await page.locator('#sudu-workspace > .study-section').evaluateAll(nodes=>nodes.slice(0,3).map(node=>node.dataset.block)),['question','answer','explanation']);
  assert.deepEqual(await page.evaluate(()=>JSON.parse(localStorage.getItem('sudu_layout_order_v1'))),custom);
  await page.evaluate(()=>{suduLayoutOrder=[];suduSaveLayout();render();});
  record('answer-first reading keeps stored custom order');

  for(const width of widths){
   await page.setViewportSize({width,height:900});
   for(const theme of ['light','dark']){
    await page.evaluate(theme=>suduTheme(theme),theme);
    await page.locator('.sudu-question-ball').first().click();
    await page.waitForTimeout(30);
    const geometry=await page.evaluate(()=>{
     const dock=document.getElementById('sudu-question-dock'),r=dock.getBoundingClientRect();
     const balls=[...dock.querySelectorAll('.sudu-question-ball')];
     const tools=['export','sudu-theme-button'].map(id=>document.getElementById(id).getBoundingClientRect());
     const ballOK=balls.every(b=>{const range=document.createRange();range.selectNodeContents(b);const text=range.getBoundingClientRect(),circle=b.getBoundingClientRect();return b.offsetWidth===b.offsetHeight&&text.left>=circle.left&&text.right<=circle.right&&text.top>=circle.top&&text.bottom<=circle.bottom;});
     return {width:innerWidth,doc:document.documentElement.scrollWidth,position:getComputedStyle(dock).position,center:(r.left+r.right)/2,bottom:r.bottom,height:r.height,padding:parseFloat(getComputedStyle(document.querySelector('.wrap')).paddingBottom),ballOK,tools:tools.every(b=>b.left>=0&&b.right<=innerWidth&&b.width>=32),count:balls.length};
    });
    assert(geometry.doc<=width+1,theme+' '+width+' horizontal overflow: '+geometry.doc);
    assert.equal(geometry.position,'fixed');assert(Math.abs(geometry.center-width/2)<1);assert.equal(geometry.bottom,900);
    assert(geometry.padding>=geometry.height+15,'dynamic bottom space');assert(geometry.ballOK,'circle numbers stay within equal-sized circles');assert(geometry.tools);assert.equal(geometry.count,source.count);
    const colors=await page.evaluate(()=>{
     const selectors=['body','#screen .section','#screen .section h2','#screen .textline','#screen .small','#screen .warning','#screen .option','#sudu-question-dock .questionnav button'];
     const rgb=s=>(s.match(/[\d.]+/g)||[]).map(Number),l=c=>{const v=c.slice(0,3).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*v[0]+.7152*v[1]+.0722*v[2];};
     const result=[];
     for(const selector of selectors)for(const el of document.querySelectorAll(selector)){
      if(!el.getClientRects().length)continue;
      let node=el,bg;
      while(node){bg=rgb(getComputedStyle(node).backgroundColor);if(bg.length===3||bg[3]===1)break;node=node.parentElement;}
      if(!node)bg=[255,255,255];
      const color=rgb(getComputedStyle(el).color),a=l(color),b=l(bg);result.push({selector,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05),color,bg});
     }return result;
    });
    for(const value of colors)assert(value.ratio>=4.5,theme+' '+width+' contrast '+JSON.stringify(value));
    record('responsive theme geometry and contrast',{width,theme,minimumContrast:Math.min(...colors.map(value=>value.ratio))});
    if([320,1280].includes(width))await page.screenshot({path:path.join(output,'workspace-'+width+'-'+theme+'.png')});
   }
  }
  await page.setViewportSize({width:320,height:480});
  await page.locator('.sudu-question-ball').last().evaluate(button=>button.scrollIntoView({block:'nearest'}));
  const short=await page.evaluate(()=>{const dock=document.querySelector('#sudu-question-dock').getBoundingClientRect(),nav=document.querySelector('#sudu-question-dock .questionnav').getBoundingClientRect(),last=[...document.querySelectorAll('.sudu-question-ball')].at(-1).getBoundingClientRect();return {dock:{top:dock.top,bottom:dock.bottom},nav:{top:nav.top,bottom:nav.bottom},last:{top:last.top,bottom:last.bottom}};});
  assert(short.nav.top>=short.dock.top-2&&short.nav.bottom<=short.dock.bottom,'short viewport keeps primary navigator visible while balls scroll');
  assert(short.last.top>=short.nav.bottom&&short.last.bottom<=short.dock.bottom,'last ball is accessible in short viewport');
  record('short viewport keeps primary controls and last question accessible',{width:320,height:480});
  await page.setViewportSize({width:1280,height:900});
  for(const tab of ['dashboard','mistakes'])for(const theme of ['light','dark']){
   await page.evaluate(({tab,theme})=>{switchTab(tab);suduTheme(theme);},{tab,theme});
   assert.equal(await page.locator('#sudu-question-dock').count(),0,'no inactive navigator on '+tab);
   const contrast=await page.evaluate(()=>{
    const selector='.db-welcome h2,.db-welcome p,.db-pane h3,.db-pane p,.db-device,.db-control label,.db-control button,.db-metric b,.db-metric span,.db-device-panel code,.db-year-row button,.reviewitem p,.reviewitem h3,.reviewitem .section h2';
    const rgb=s=>(s.match(/[\d.]+/g)||[]).map(Number),lum=c=>{const v=c.slice(0,3).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*v[0]+.7152*v[1]+.0722*v[2];};
    return [...document.querySelectorAll(selector)].filter(el=>el.getClientRects().length).map(el=>{let n=el,bg;while(n){bg=rgb(getComputedStyle(n).backgroundColor);if(bg.length===3||bg[3]===1)break;n=n.parentElement;}if(!n)bg=[255,255,255];const a=lum(rgb(getComputedStyle(el).color)),b=lum(bg);return {tag:el.tagName,cls:el.className,text:el.textContent.slice(0,60),ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};});
   });
   assert(contrast.length>0,'rendered text exists on '+tab);
   for(const row of contrast)assert(row.ratio>=4.5,tab+' '+theme+' low contrast '+JSON.stringify(row));
   record('nonlearning nested contrast and no inactive dock',{tab,theme,minimumContrast:Math.min(...contrast.map(row=>row.ratio))});
  }

  await page.evaluate(async()=>{
   await suduLoadOfficialYear('114');const official=(ALL.officialQuestions||[]).find(item=>String(item.year)==='114');
   if(!official)throw Error('114 corpus unavailable');
   ui.year='114';ui.paper=official.paper;ui.subject=official.subject;ui.index=0;ui.tab='learn';filters();save();render();
  });
  const mapping=await page.evaluate(()=>({expected:available().map(q=>({id:q.id,number:String(q.number)})),actual:[...document.querySelectorAll('.sudu-question-ball')].map(node=>({id:node.dataset.questionId,number:node.dataset.originalNumber})),first:available()[0]}));
  assert(mapping.expected.length>0);assert.deepEqual(mapping.actual,mapping.expected);
  await page.locator('.sudu-question-ball').last().click();
  assert.equal(await page.evaluate(()=>available()[ui.index].id),mapping.expected.at(-1).id);
  if(!mapping.first.questionVerified||!mapping.first.answerVerified){
   await page.locator('.sudu-question-ball').first().click();await page.locator('[data-answer]').first().click();
   assert.equal(await page.locator('.sudu-question-ball').first().getAttribute('data-status'),'pending');
  }
  record('official paper numbers map to filtered array and unverified answers stay pending',{questionCount:mapping.expected.length});

  const touch=await browser.newContext({viewport:{width:375,height:812},isMobile:true,hasTouch:true,reducedMotion:'reduce'}),phone=await touch.newPage();
  await phone.goto(base,{waitUntil:'domcontentloaded'});await phone.locator('[data-sudu-menu-trigger="functions"]').tap();
  assert.equal(await phone.locator('#sudu-floating-controls').getAttribute('aria-hidden'),'false');
  await phone.locator('#sudu-mega-close').tap();assert.equal(await phone.locator('#sudu-floating-controls').getAttribute('aria-hidden'),'true');
  await phone.locator('#sudu-theme-button').tap();assert.equal(await phone.locator('html').getAttribute('data-sudu-theme'),'dark');
  await touch.close();record('touch open, close and theme icon');
  assert.deepEqual(errors,[],'no browser page errors');
  fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({base,results,pageErrors:errors},null,2));
  console.log(JSON.stringify({status:'passed',checks:results.length,widths,themes:['light','dark'],results:output}));
 }catch(error){
  fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({base,results,error:String(error.stack||error),pageErrors:errors},null,2));
  await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});throw error;
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
