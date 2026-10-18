const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1260,height:850}});
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/sudu/',{waitUntil:'domcontentloaded'});
 const trigger=kind=>page.locator('[data-sudu-menu-trigger="'+kind+'"]');
 const menu=page.locator('#sudu-floating-controls');
 await trigger('year').waitFor();
 assert.equal(await page.locator('[data-sudu-menu-trigger]').count(),3,'three independent buttons');
 assert.equal(await menu.getAttribute('aria-hidden'),'true');
 // All three menus open independently on desktop mouse hover.
 for(const kind of ['year','subject','functions']){
   await trigger(kind).hover();
   assert.equal(await menu.getAttribute('aria-hidden'),'false','hover must open '+kind);
   assert.equal(await menu.getAttribute('data-active-menu'),kind,'correct menu for '+kind);
   assert.equal(await page.locator('[data-sudu-menu-section="'+kind+'"]').isVisible(),true);
 }
 const bg=await menu.locator('.floating-inner').evaluate(x=>getComputedStyle(x).backgroundColor);
 assert.equal(bg,'rgb(16, 17, 19)','Apple-style near-black menu');
 const yearTitle=await trigger('year').innerText(),subjectTitle=await trigger('subject').innerText(),functionTitle=await trigger('functions').innerText();
 for(const word of ['年度','科目','功能'])assert([yearTitle,subjectTitle,functionTitle].some(x=>x.includes(word)),word);
 // Hover-out delay of 1000ms; re-entry should cancel it.
 await trigger('year').hover();
 await page.mouse.move(2,500);
 await page.waitForTimeout(450);
 assert.equal(await menu.getAttribute('aria-hidden'),'false','450ms should remain open');
 await page.waitForTimeout(850);
 assert.equal(await menu.getAttribute('aria-hidden'),'true','should close after one second');
 await trigger('subject').hover();
 await page.mouse.move(2,500);
 await page.waitForTimeout(350);
 await trigger('subject').hover();
 await page.waitForTimeout(850);
 assert.equal(await menu.getAttribute('aria-hidden'),'false','re-entering should cancel close');
 await page.keyboard.press('Escape');
 assert.equal(await menu.getAttribute('aria-hidden'),'true','Escape must close active menu');
 // Function list may switch to Dashboard, then back to Learning.
 await trigger('functions').hover();
 await menu.locator('[data-tab="dashboard"]').click();
 assert.equal(await menu.getAttribute('aria-hidden'),'true');
 assert.equal(await page.locator('.db-pane').count()>0,true,'dashboard must render');
 await trigger('functions').hover();
 await menu.locator('[data-tab="learn"]').click();
 await page.locator('.option[data-answer]').first().click();
 await page.locator('.accounting-teacher').waitFor();
 assert(await page.locator('.accounting-teacher').innerText().then(t=>t.includes('高職會計老師')&&t.includes('小學生白話')));
 assert(await page.locator('.accounting-teacher .concept-key').count()>0);
 await page.waitForTimeout(900);
 const answerTop=await page.locator('#sudu-workspace [data-block="answer"]').evaluate(x=>x.getBoundingClientRect().top);
 assert(answerTop>=0&&answerTop<250,'clicking a choice should scroll to its answer; actual='+answerTop);
 assert.equal(await page.locator('#sudu-return-to-question').isVisible(),true);
 await page.locator('#sudu-return-to-question').click();
 await page.waitForTimeout(900);
 const questionTop=await page.locator('#sudu-workspace [data-block="question"]').evaluate(x=>x.getBoundingClientRect().top);
 assert(questionTop>=0&&questionTop<240,'return to question; actual='+questionTop);
 // Dark is truly black/charcoal and readable.
 await page.locator('#sudu-theme-button').click();
 assert.equal(await page.locator('html').getAttribute('data-sudu-theme'),'dark');
 const darkColors=await page.evaluate(()=>{
  const body=getComputedStyle(document.body).backgroundColor;
  const section=getComputedStyle(document.querySelector('#screen .section')).backgroundColor;
  const text=getComputedStyle(document.querySelector('#screen .section h2')).color;
  const button=getComputedStyle(document.querySelector('.option')).color;
  return {body,section,text,button};
 });
 assert.equal(darkColors.body,'rgb(5, 5, 5)','dark background must be black');
 assert.equal(darkColors.section,'rgb(20, 20, 20)','dark cards charcoal');
 assert.equal(darkColors.text,'rgb(242, 242, 242)','dark headings white');
 assert.equal(darkColors.button,'rgb(246, 246, 246)','dark answer text white');
 await page.locator('#sudu-theme-button').click();
 assert.equal(await page.locator('html').getAttribute('data-sudu-theme'),'light');
 // User custom block order is saved and restored after reload.
 await page.locator('#sudu-toggle-drag').click();
 const blocks=page.locator('#sudu-workspace > .study-section');
 const before=await blocks.evaluateAll(xs=>xs.map(x=>x.dataset.block));
 assert(before.includes('question')&&before.includes('explanation')&&before.includes('source'));
 await page.locator('#sudu-workspace [data-block="source"] .sudu-move-up').click();
 const after=await blocks.evaluateAll(xs=>xs.map(x=>x.dataset.block));
 assert.notDeepEqual(after,before);
 await page.reload({waitUntil:'domcontentloaded'});
 await page.locator('#sudu-toggle-drag').click();
 const restored=await page.locator('#sudu-workspace > .study-section').evaluateAll(xs=>xs.map(x=>x.dataset.block));
 assert.deepEqual(restored,after);
 assert.equal(errors.length,0,'browser JS errors: '+errors.join('; '));
 // Touch + RWD: each page stays within viewport, and menus can be tapped.
 const mobile=await browser.newPage({viewport:{width:375,height:780},isMobile:true,hasTouch:true});
 mobile.on('pageerror',e=>errors.push(e.message));
 await mobile.goto('http://127.0.0.1:8765/sudu/',{waitUntil:'domcontentloaded'});
 const mobileMenu=mobile.locator('#sudu-floating-controls');
 for(const kind of ['year','subject','functions']){
  await mobile.locator('[data-sudu-menu-trigger="'+kind+'"]').tap();
  assert.equal(await mobileMenu.getAttribute('data-active-menu'),kind);
  assert.equal(await mobileMenu.getAttribute('aria-hidden'),'false');
  await mobile.locator('#sudu-mega-close').tap();
  assert.equal(await mobileMenu.getAttribute('aria-hidden'),'true');
 }
 async function checkOverflow(name){
  const values=await mobile.evaluate(()=>({w:document.documentElement.scrollWidth,viewport:window.innerWidth}));
  assert(values.w<=values.viewport+3,name+' horizontal overflow '+JSON.stringify(values));
 }
 await checkOverflow('learning');
 for(const tab of ['dashboard','clinic','archive','source','learn']){
  await mobile.locator('[data-sudu-menu-trigger="functions"]').tap();
  await mobileMenu.locator('[data-tab="'+tab+'"]').tap();
  await checkOverflow(tab);
 }
 await mobile.locator('[data-sudu-menu-trigger="functions"]').tap();
 await mobileMenu.locator('#sudu-theme-in-menu').tap();
 assert.equal(await mobile.locator('html').getAttribute('data-sudu-theme'),'dark');
 await checkOverflow('mobile dark');
 assert.equal(errors.length,0,'browser JS errors: '+errors.join('; '));
 // Root URL always enters learning platform.
 await page.goto('http://127.0.0.1:8765/',{waitUntil:'domcontentloaded'});
 await page.waitForURL('**/sudu/');
 console.log('PASS: split Year Subject Functions menus, hover delay, mobile, black theme, answer jump, all tabs RWD, persistence');
 await browser.close();
})().catch(e=>{console.error(e.stack);process.exit(1)});
