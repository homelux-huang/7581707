/* Live private-API UI test. Its database and tokens exist only in an isolated temp directory. */
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const {spawn}=require('node:child_process');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'sudu-admin-browser-'));
const port=18500+(process.pid%900),base='http://127.0.0.1:'+port;
const child=spawn('python3',['backend/server.py'],{cwd:root,env:{...process.env,PORT:String(port),SUDU_DB_PATH:path.join(tmp,'private.sqlite3'),SUDU_DEV_ALLOW_ADMIN_ADMIN:'1',SUDU_ADMIN_INITIAL_PASSWORD:'',SUDU_ADMIN_PUBLIC_URL:''},stdio:'ignore'});
const pause=ms=>new Promise(r=>setTimeout(r,ms));
function luminance(rgb){const c=rgb.match(/[\d.]+/g).slice(0,3).map(Number).map(x=>{x/=255;return x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4)});return .2126*c[0]+.7152*c[1]+.0722*c[2]}
async function checkLayout(page,width,theme){await page.setViewportSize({width,height:900});await page.evaluate(theme=>window.theme(theme),theme);await pause(35);const colors=await page.evaluate(()=>{const body=getComputedStyle(document.body),button=getComputedStyle(document.querySelector('#theme'));return {overflow:document.documentElement.scrollWidth>innerWidth+1,bodyText:body.color,bodyBg:body.backgroundColor,buttonText:button.color,buttonBg:button.backgroundColor}});assert.equal(colors.overflow,false,`admin/share overflow ${width} ${theme}`);for(const pair of [[colors.bodyText,colors.bodyBg],[colors.buttonText,colors.buttonBg]]){const a=luminance(pair[0]),b=luminance(pair[1]);assert((Math.max(a,b)+.05)/(Math.min(a,b)+.05)>=4.5,`contrast ${width} ${theme}`)}}
(async()=>{
 let browser;
 try{
  let ready=false;for(let i=0;i<80;i++){try{const r=await fetch(base+'/health');if(r.ok){ready=true;break}}catch{}await pause(100)}assert(ready,'temporary private API must actually start');
  browser=await chromium.launch({headless:true,...(process.env.SUDU_BROWSER_EXECUTABLE?{executablePath:process.env.SUDU_BROWSER_EXECUTABLE}:{})});
  const context=await browser.newContext(),page=await context.newPage();
  await page.goto(base+'/admin');await page.locator('#login').waitFor({state:'visible'});
  await page.locator('[name=password]').fill('admin');await page.locator('#login-form button').click();
  await page.locator('#change').waitFor({state:'visible'});
  await page.locator('[name=oldPassword]').fill('admin');await page.locator('[name=newPassword]').fill('browser-private-test-password');await page.locator('#change-form button').click();
  await page.locator('#dashboard').waitFor({state:'visible'});
  const enrollment=await context.request.post(base+'/api/students/enroll',{data:{nickname:'Browser synthetic test learner'}});assert.equal(enrollment.status(),201);const student=await enrollment.json();
  const year=JSON.parse(fs.readFileSync(path.join(root,'sudu/data/years/115.json'),'utf8'));
  const paper=year.papers.find(p=>p.expectedCount>0&&p.questions.length===p.expectedCount);assert(paper,'real corpus fixture with complete record count exists');
  const first=paper.questions[0],key='115/'+paper.paper,at=new Date(),started=new Date(at.getTime()-60000);
  const submission={id:'browser-test-only',year:'115',paper:paper.paper,startedAt:started.toISOString(),submittedAt:at.toISOString(),elapsedMs:60000,questionCount:paper.questions.length,choices:Object.fromEntries(paper.questions.map((q,i)=>[q.id,i%4]))};
  const sync=await context.request.post(base+'/api/students/sync',{headers:{Authorization:'Bearer '+student.accessToken},data:{state:{attempts:{[first.id]:[{choice:0,correct:false,at:started.toISOString()}]},examSubmissions:{[key]:submission}}}});assert.equal(sync.status(),200);
  await page.locator('#refresh').click();await page.getByRole('button',{name:'查看進度與題目'}).click();await page.locator('#student-report').waitFor({state:'visible'});
  assert((await page.locator('#scores').innerText()).includes('待核實'),'real corpus cannot produce fabricated official grade');
  await page.locator('[name=score]').fill('5');await page.locator('[name=reason]').fill('瀏覽器測試人工調整理由');await page.locator('[name=source]').fill(paper.questionPdf);await page.locator('#adjust-form button').click();
  await page.locator('#adjust-history').filter({hasText:'瀏覽器測試人工調整理由'}).waitFor({state:'visible'});
  await page.locator('#share-paper').fill(key);await page.locator('#create-share').click();await page.locator('#share-out a').waitFor();
  const shareUrl=await page.locator('#share-out a').getAttribute('href'),share=await context.newPage();await share.goto(shareUrl);await share.locator('#report').filter({hasText:'分享範圍'}).waitFor({state:'visible'});
  assert(!(await share.locator('#report').innerText()).includes('Browser synthetic test learner'),'shared report omits personal nickname');
  for(const width of [320,375,390,430,768,1024,1280,1440])for(const theme of ['light','dark']){await checkLayout(page,width,theme);await checkLayout(share,width,theme)}
  const output=process.env.SUDU_TEST_OUTPUT;if(output){fs.mkdirSync(output,{recursive:true});await page.setViewportSize({width:390,height:900});await page.evaluate(()=>window.theme('dark'));await page.bringToFront();await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'admin-dark-390.png'),animations:'disabled',timeout:15000});await share.bringToFront();await share.evaluate(()=>window.scrollTo(0,0));await share.screenshot({path:path.join(output,'share-dark-1440.png'),animations:'disabled',timeout:15000})}
  await page.getByRole('button',{name:'撤銷此分享'}).click();await page.locator('#share-list button').waitFor({state:'detached'});await share.reload();await share.locator('#report').filter({hasText:'已撤銷'}).waitFor({state:'visible'});
  await page.locator('#logout').click();await page.locator('#login').waitFor({state:'visible'});const denied=await context.request.get(base+'/api/admin/students');assert.equal(denied.status(),401);
  console.log('PASS: private API browser login/change-password/sync/adjustment/share/revoke/logout; 8 widths × 2 themes × admin/share; text and button contrast >= 4.5');
 }finally{if(browser)await browser.close();child.kill('SIGTERM');await new Promise(resolve=>{if(child.exitCode!==null)return resolve();child.once('exit',resolve)});fs.rmSync(tmp,{recursive:true,force:true})}
})().catch(e=>{console.error(e);process.exitCode=1});
