/* Real formal G8 only after the Python bridge verifies actual G1-G7 trust.
 * No route interception, fixture trust, synthetic candidate, or direct promotion.
 */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const {spawn,spawnSync}=require('child_process');
const ROOT=path.resolve(__dirname,'..'),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const requireEnv=k=>{assert(process.env[k],`missing ${k}`);return process.env[k];};
async function main(){
 const source=path.resolve(requireEnv('SUDU_G8_SOURCE')),stage=path.resolve(requireEnv('SUDU_G8_STAGE'));
 const privateEvidence=path.resolve(requireEnv('SUDU_G8_PRIVATE_EVIDENCE')),out=path.resolve(requireEnv('SUDU_G8_OUTPUT'));
 const verify=()=>{
  const r=spawnSync('python',['-m','scripts.sudu_g8_release_bridge','verify-stage','--source',source,'--stage',stage,'--private-evidence',privateEvidence],{cwd:ROOT,encoding:'utf8'});
  assert.equal(r.status,0,'native G1-G7/authorized staging required: '+r.stderr);return JSON.parse(r.stdout);
 };
 const verified=verify();
 assert.equal(process.env.GITHUB_ACTIONS,'true','formal promotion requires an actual Actions execution');
 const runId=Number(requireEnv('GITHUB_RUN_ID'));assert(Number.isSafeInteger(runId)&&runId>0);
 const m=JSON.parse(fs.readFileSync(path.join(stage,'stage.json'))),q=JSON.parse(fs.readFileSync(path.join(stage,'row.json')));
 assert.equal(hash(fs.readFileSync(path.join(stage,'stage.json'))),verified.stageManifestSha256);
 const payload=fs.readFileSync(path.join(stage,'site',m.payloadPath));assert.equal(hash(payload),m.payloadSha256);
 for(const [rel,blob] of Object.entries(m.codeBindings)){
  const b=fs.readFileSync(path.join(ROOT,rel));const h=crypto.createHash('sha1').update(Buffer.from(`blob ${b.length}\0`)).update(b).digest('hex');assert.equal(h,blob,'code changed '+rel);
 }
 assert.equal(process.env.GITHUB_SHA,m.codeCommit,'actual formal job must run the staging code commit');
 assert(!fs.existsSync(out),'never overwrite formal evidence');fs.mkdirSync(out,{recursive:true,mode:0o700});
 const report={schema:m.schema,status:'FORMAL_G8_FAILED',stageManifest:fs.readFileSync(path.join(stage,'stage.json'),'utf8'),stageManifestSha256:verified.stageManifestSha256,payloadSha256:m.payloadSha256,codeCommit:m.codeCommit,codeBindings:m.codeBindings,runId,cases:[],errors:[]};
 const save=()=>fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n',{mode:0o600});save();
 // New server binds ONLY loopback and serves the immutable private staging tree.
 const server=spawn('python',['-u','-c',`import http.server,sys,functools\nh=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=sys.argv[1]))\nprint(h.server_address[1],flush=True)\nh.serve_forever()`,path.join(stage,'site')],{stdio:['ignore','pipe','pipe']});
 let serverErrors='';server.stderr.on('data',b=>{serverErrors+=b.toString();});
 const port=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('loopback server startup timeout')),15000);server.stdout.once('data',b=>{clearTimeout(timer);const n=Number(b.toString().trim());if(!Number.isInteger(n))reject(Error('invalid server port'));else resolve(n);});server.once('error',reject);server.once('exit',code=>reject(Error('server exited '+code)));});
 const SITE=`http://127.0.0.1:${port}/sudu/`,SIZES=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
 const {chromium}=require('playwright');let browser;
 const norm=s=>String(s).replace(/\*\*/g,'').replace(/反向檢查/g,'相反意思').replace(/\s+/g,'');
 try{
  browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  for(const [width,height] of SIZES)for(const theme of ['light','dark']){
   const ctx=await browser.newContext({viewport:{width,height},hasTouch:width<=430,reducedMotion:'reduce'}),page=await ctx.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&r.url().startsWith(SITE))errors.push('HTTP '+r.status()+' '+r.url());});
   try{
    const response=await page.goto(SITE+'v4-115-multisubject-review-demo.html?year='+m.year,{waitUntil:'domcontentloaded'});assert(response&&response.ok());
    await page.waitForFunction(y=>document.body.dataset.verifiedReadyYear===String(y),m.year,{timeout:25000});
    const http=await page.request.get(SITE+'data/approved/'+m.year+'.json');assert(http.ok());assert.equal(hash(await http.body()),m.payloadSha256,'HTTP payload differs');
    await page.locator('#homeSubjectSel').selectOption(q.subject);await page.locator('#studyView').waitFor({state:'visible'});
    const selected=await page.evaluate(id=>{const a=QUESTIONS.filter(x=>x.canonicalId===id);if(a.length!==1)return null;currentSubject=a[0].subject;currentIndex=list().findIndex(x=>x.canonicalId===id);renderAll();return qnow()?.canonicalId;},m.qid);assert.equal(selected,m.qid);
    if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#themeBtn').click();assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
    const img=page.locator('#questionCard img').first();await img.scrollIntoViewIfNeeded();await img.evaluate(el=>el.decode());assert.equal(await img.getAttribute('src'),q.image);
    const wb=await page.request.get(SITE+q.image);assert(wb.ok());assert.equal(hash(await wb.body()),m.webpSha256);
    assert.equal(norm(await page.locator('#questionCard h1').innerText()),norm(q.question));assert.equal(await page.locator('#answerCard .opt').count(),4);
    for(let i=0;i<4;i++){const el=page.locator('#answerCard .opt').nth(i);assert.equal(await el.getAttribute('data-a'),'ABCD'[i]);assert.equal(norm(await el.locator('.opt-text').innerText()),norm(q.options[i]));}
    const choose=async L=>{const button=page.locator('#answerCard .opt[data-a="'+L+'"]');if(width<=430)await button.tap();else await button.click();};
    await choose(q.answer==='A'?'B':'A');await page.locator('#guideCard.show').waitFor();
    assert.equal(await page.evaluate(()=>record(qnow()).status),'bad','wrong-answer interaction did not register');
    assert.equal(await page.locator('#answerCard .opt.wrong').count(),1);
    await choose(q.answer);
    assert.equal(await page.evaluate(()=>record(qnow()).status),'ok','positive answer interaction did not register');
    assert.equal(await page.locator('#answerCard .opt.wrong').count(),0);
    assert.equal(await page.locator('#answerCard .opt.correct').count(),1);assert.equal(await page.locator('#answerCard .opt.correct').getAttribute('data-a'),q.answer);assert.equal(await page.locator('#answerCard .option-detail').count(),4);
    if(q.highlights?.length)assert(await page.locator('#studyView .exam-highlight, #studyView mark, #studyView strong, #studyView b').count()>0,'highlight/strong missing');
    const details=norm(await page.locator('#answerCard').innerText());for(const L of 'ABCD')for(const field of ['teacher','elementary'])assert(details.includes(norm(q.optionExplanations[L][field])),'missing '+L+' '+field+' explanation');
    if(q.examCalculation){assert(await page.locator('#guideCard .calculation-step').count()>0,'calculation steps missing');const text=norm(await page.locator('#guideCard').innerText());for(const line of q.examCalculation.lines)assert(text.includes(norm(line)),'calculation line absent');}
    else{assert.equal(await page.locator('#guideCard .calculation-step').count(),0);assert.equal(await page.locator('#guideCard .calculation-first').count(),0);}
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,'horizontal overflow');assert.deepEqual(errors,[]);
    const screenshot=`${m.qid}-${width}x${height}-${theme}.png`;await page.screenshot({path:path.join(out,screenshot),animations:'disabled'});
    report.cases.push({width,height,theme,result:'PASS',interaction:width<=430?'real-touch-tap':'mouse-click',wrongAndCorrectAnswerVerified:true,screenshot,screenshotSha256:hash(fs.readFileSync(path.join(out,screenshot))),stageManifestSha256:verified.stageManifestSha256,payloadSha256:m.payloadSha256});
   }catch(e){report.errors.push({width,height,theme,message:String(e.stack||e),browserErrors:errors});}
   finally{await ctx.close();save();}
  }
  verify();assert.equal(hash(fs.readFileSync(path.join(stage,'site',m.payloadPath))),m.payloadSha256);assert.equal(report.cases.length,16);assert.deepEqual(report.errors,[]);report.status='FORMAL_G8';report.completedAt=new Date().toISOString();save();
  console.log('FORMAL_G8 16/16 exact authenticated staged bytes; promotion requires separate protected owner receipt');
 }finally{if(browser)await browser.close();server.kill();}
}
main().catch(e=>{console.error(String(e.stack||e));process.exitCode=1;});
