/* ROLE D: exact-source V4 browser matrix, never a publisher/admission test.
 * Inputs come ONLY from the checked-out real Demo and approved/preview artifacts.
 * No synthetic teacher approval, placeholder question or answer fixture is used.
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const cp=require('node:child_process');
const {chromium}=require('playwright');

const ROOT=process.cwd();
const BASE=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
const YEAR=process.env.SUDU_D_YEAR;
const SUBJECT=process.env.SUDU_D_SUBJECT;
const SUBJECTS=['國文','英文','數學 B','商業概論','數位科技','會計學','經濟學'];
const VIEWPORTS=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
const SUBJECT_SLUG={'國文':'C','英文':'E','數學 B':'MB','商業概論':'BC','數位科技':'IT','會計學':'ACC','經濟學':'ECON'};
const OUTPUT=path.resolve(process.env.SUDU_D_OUTPUT||'test-results/role-d');
const sourcePath=p=>path.join(ROOT,'sudu',p);
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const fileHash=p=>hash(fs.readFileSync(path.join(ROOT,p)));
const git=()=>{try{return cp.execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim()}catch{return null}};
const readJson=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
const expect=process.env.SUDU_D_EXPECT_SHA||'';
const check=(value,message)=>assert(value,message);
if(!['demo','114','115'].includes(YEAR)||!SUBJECTS.includes(SUBJECT))
  throw Error('Specify an exact SUDU_D_YEAR=demo|114|115 and SUDU_D_SUBJECT (one of seven)');
if(expect)assert.equal(git(),expect,'checkout SHA differs from audited workflow HEAD');
const demoHTML=fs.readFileSync('sudu/v4-115-multisubject-review-demo.html','utf8');
const match=demoHTML.match(/<script id="demoData" type="application\/json">([\s\S]*?)<\/script>/);
check(match,'original 35-question V4 script not found');
const demoData=JSON.parse(match[1]);
assert.equal(demoData.questions.length,35,'Demo baseline question count changed');
assert.deepEqual(demoData.subjects,SUBJECTS,'Demo subject-specific seven-course structure changed');
const baseline=readJson('docs/ROLE_D_V4_DEMO_35_BASELINE_20261025.json');
const expectedDemoIDs=baseline.subjects[SUBJECT].questionIds;
assert.deepEqual(demoData.questions.filter(q=>q.subject===SUBJECT).map(q=>q.id),
  expectedDemoIDs,'subject-specific Demo original question IDs changed');
const approved=YEAR==='demo'?null:readJson('sudu/data/approved/'+YEAR+'.json');
const preview=YEAR==='demo'?null:readJson('sudu/data/approved/preview/'+YEAR+'.json');
const report={
  schemaVersion:1,role:'D',purpose:'ISOLATED_UI_QA_NOT_RELEASE',
  year:YEAR,subject:SUBJECT,sourceMode:'ACTUAL_GITHUB_CHECKOUT_NOT_FIXTURE',
  actualCommitSha:git(),expectedCommitSha:expect||null,
  mainBaseSha:process.env.SUDU_D_MAIN_SHA||null,
  commandDocRef:'PR30:27f13aef46588e0eacd9c50edddae90f982e0d86',
  ciRunId:process.env.GITHUB_RUN_ID||null,
  ciRunUrl:process.env.GITHUB_RUN_ID?
    'https://github.com/homelux-huang/7581707/actions/runs/'+process.env.GITHUB_RUN_ID:null,
  htmlSha256:fileHash('sudu/v4-115-multisubject-review-demo.html'),
  runtimeSha256:fileHash('sudu/verified-questions-runtime.js'),
  demoLearningSha256:fileHash('sudu/demo-subject-learning.js'),
  baselineSha256:fileHash('docs/ROLE_D_V4_DEMO_35_BASELINE_20261025.json'),
  approvedJsonSha256:YEAR==='demo'?null:fileHash('sudu/data/approved/'+YEAR+'.json'),
  previewJsonSha256:YEAR==='demo'?null:fileHash('sudu/data/approved/preview/'+YEAR+'.json'),
  approvedSourceRevision:approved?.sourceSha||null,
  previewSourceRevision:preview?.sourceSha||null,
  viewports:VIEWPORTS,themes:['light','dark'],
  cases:[],missing:[],summary:null
};
const selectedDemo=demoData.questions.filter(q=>q.subject===SUBJECT);
const approvedRows=approved?approved.questions.filter(q=>q.subject===SUBJECT):[];
const previewRows=preview?preview.questions.filter(q=>q.subject===SUBJECT):[];
const modes=YEAR==='demo'?[{mode:'demo',rows:selectedDemo}]:
  [{mode:'approved',rows:approvedRows},{mode:'image-preview-only',rows:previewRows}];
function lessonFields(q){
  return {
    canonicalId:q.canonicalId,question:q.question,options:q.options,answer:q.answer,
    topic:q.topic,concept:q.concept,teacherSummary:q.teacherSummary,
    elementarySummary:q.elementarySummary,optionExplanations:q.optionExplanations,
    memory:q.memory,examCalculation:q.examCalculation,extra:q.extra,
    highlights:q.highlights,sourceText:q.sourceText,
    sourceTable:q.sourceTable??null
  };
}
function demoFields(q){
  return {subject:q.subject,id:q.id,topic:q.topic,question:q.question,options:q.options,
    answer:q.answer,memory:q.memory,concept:q.concept,extension:q.extension,
    formula:q.formula,extra:q.extra,image:q.image};
}
function localImageDigest(item){
  const full=sourcePath(item.image);
  check(fs.existsSync(full),'missing actual original image: '+item.image);
  const actual=fileHash(path.join('sudu',item.image));
  if(item.sha256)assert.equal(actual,item.sha256,'image bytes fail supplied SHA: '+item.image);
  return actual;
}
function sourceAudit(){
  if(YEAR==='demo'){
    assert.equal(selectedDemo.length,5,'original subject is not five Demo questions');
    for(const q of selectedDemo){check(q.image&&q.question&&q.options.length===4&&q.answer,
      'incomplete actual Demo content');localImageDigest(q)}
    return;
  }
  assert.equal(approved.approvedCount,approved.questions.length);
  assert.equal(preview.imagePreviewCount,preview.questions.length);
  for(const q of approvedRows){
    assert.match(q.canonicalId,new RegExp('^'+YEAR+'-'));
    check(q.options?.length===4&&q.imageSha256&&q.optionExplanations,'incomplete admitted real lesson');
    localImageDigest({image:q.image,sha256:q.imageSha256});
  }
  for(const q of previewRows){
    assert.equal(q.reviewStage,'image_qa_pass_only');
    assert.equal(q.year,Number(YEAR));
    for(const illegal of ['answer','question','options','teaching','memory','independentSolve'])
      check(!Object.hasOwn(q,illegal),'unapproved content leaked into image index: '+illegal);
    localImageDigest({image:q.image,sha256:q.imageSha256});
    for(const shared of q.sharedImages||[])localImageDigest(shared);
  }
}
function assertOriginalQuestionNumber(q,mode){
  if(mode==='demo')return q.id;
  if(mode==='approved')return q.id;
  return q.questionNumber;
}
async function act(locator,touch){
  if(touch)await locator.tap({timeout:15000});
  else await locator.click({timeout:15000});
}
async function layoutQA(page,label){
  const geometry=await page.evaluate(()=>{
    const ids=['#questionCard h1','#questionCard img','.opt-text','#guideCard .calculation-step'];
    const clipping=[];
    for(const sel of ids)for(const node of document.querySelectorAll(sel)){
      const style=getComputedStyle(node);
      if(style.display==='none'||!node.getClientRects().length)continue;
      if(node.scrollWidth>node.clientWidth+3&&style.overflowX!=='auto'&&style.overflowX!=='scroll')
        clipping.push({sel,text:(node.textContent||'').slice(0,60),scrollWidth:node.scrollWidth,clientWidth:node.clientWidth});
    }
    const imgs=[...document.querySelectorAll('#questionCard img')].map(el=>{
      const box=el.getBoundingClientRect();
      return {src:el.getAttribute('src'),width:box.width,height:box.height,
        naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,
        containerWidth:el.parentElement.getBoundingClientRect().width};
    });
    return {viewport:innerWidth,document:document.documentElement.scrollWidth,
      body:document.body.scrollWidth,clipping,imgs};
  });
  check(geometry.document<=geometry.viewport+1&&geometry.body<=geometry.viewport+1,
    label+' horizontal overflow '+JSON.stringify(geometry));
  assert.deepEqual(geometry.clipping,[],label+' text clipped');
  for(const i of geometry.imgs){
    check(i.naturalWidth>0&&i.naturalHeight>0,label+' WebP not decoded '+i.src);
    check(i.width<=i.containerWidth+2,label+' WebP overflows original figure');
    const rendered=i.width/i.height,original=i.naturalWidth/i.naturalHeight;
    check(Math.abs(rendered-original)/original<0.025,label+' original WebP aspect ratio changed');
  }
  return geometry;
}
async function verifyImageOverHTTP(page,p,expectedSha){
  const res=await page.request.get(new URL(p,BASE).href);
  check(res.ok(),'original WebP HTTP failure '+p+': '+res.status());
  const actual=hash(await res.body());
  if(expectedSha)assert.equal(actual,expectedSha,'staged original WebP SHA mismatch '+p);
  return actual;
}
async function verifyImagePreview(page,q,geometry){
  const card=page.locator('#questionCard');
  assert.equal(await card.getAttribute('data-canonical-id'),q.canonicalId);
  assert.equal(await card.getAttribute('data-qa-preview'),'read-only');
  assert.equal(Number(await card.locator('.qnum').innerText()),q.questionNumber);
  check(await page.locator('#answerCard').isHidden(),'image preview illegally exposes answer choices');
  check(await page.locator('#guideCard').isHidden(),'image preview illegally exposes explanations');
  assert.equal(await page.locator('#studyView .opt').count(),0,'QA-only must never be gradeable');
  check(await page.locator('#explainBtn').isDisabled(),'QA-only answer shortcut must be disabled');
  const imgs=card.locator('img');
  assert.equal(await imgs.count(),1+(q.sharedImages||[]).length,'missing original shared material');
  const all=[{image:q.image,sha256:q.imageSha256},...(q.sharedImages||[])];
  for(let i=0;i<all.length;i++){
    const el=imgs.nth(i),a=all[i];
    assert.equal(await el.getAttribute('src'),'./'+a.image,'wrong raw question/shared image');
    assert.equal(await el.getAttribute('data-canonical-id'),q.canonicalId);
    assert.equal(await el.getAttribute('data-sha256'),a.sha256);
    await el.evaluate(el=>el.decode());
    await verifyImageOverHTTP(page,a.image,a.sha256);
  }
  assert.equal(geometry.imgs.length,all.length,'wrong rendered image count');
  return {questionRevision:q.revision||q.sourceRevision||null,
    teachingDigest:null,imageSha256:q.imageSha256,sharedImageSHA:all.slice(1).map(x=>x.sha256)};
}
async function verifyActiveQuestion(page,q,mode,touch,geometry){
  assert.equal(Number(await page.locator('#questionCard .qnum').innerText()),
    assertOriginalQuestionNumber(q,mode),'rendered question number differs');
  assert.equal((await page.locator('#questionCard h1').innerText()).trim(),q.question.trim(),'rendered stem changed');
  const option=page.locator('#answerCard .opt');
  assert.equal(await option.count(),4,'A/B/C/D missing');
  for(let i=0;i<4;i++){
    assert.equal(await option.nth(i).getAttribute('data-a'),'ABCD'[i],'option index mismatch');
    assert.equal((await option.nth(i).locator('.opt-text').innerText()).trim(),
      String(q.options[i]).trim(),'actual option text not displayed');
  }
  const img=page.locator('#questionCard .source-figure img').first();
  assert.equal(await img.getAttribute('src'),q.image,'question mismatch: source WebP');
  await img.evaluate(i=>i.decode());
  const imageSha256=await verifyImageOverHTTP(page,q.image,q.imageSha256);
  check(geometry.imgs.length>=1,'original single-question WebP missing from question card');
  const draft=mode==='approved'?lessonFields(q):demoFields(q);
  const expectedDigest=hash(Buffer.from(JSON.stringify(draft),'utf8'));
  const actualSource=await page.evaluate(({id,mode})=>{
    const q=QUESTIONS.find(item=>mode==='approved'?item.canonicalId===id:
      item.subject===id.subject&&item.id===id.id);
    if(!q)return null;
    if(mode==='approved')return JSON.stringify({
      canonicalId:q.canonicalId,question:q.question,options:q.options,answer:q.answer,
      topic:q.topic,concept:q.concept,teacherSummary:q.teacherSummary,
      elementarySummary:q.elementarySummary,optionExplanations:q.optionExplanations,
      memory:q.memory,examCalculation:q.examCalculation,extra:q.extra,
      highlights:q.highlights,sourceText:q.sourceText,sourceTable:q.sourceTable??null
    });
    return JSON.stringify({subject:q.subject,id:q.id,topic:q.topic,question:q.question,options:q.options,
      answer:q.answer,memory:q.memory,concept:q.concept,extension:q.extension,
      formula:q.formula,extra:q.extra,image:q.image});
  },{id:mode==='approved'?q.canonicalId:{subject:q.subject,id:q.id},mode});
  check(actualSource,'student runtime did not load exact source question');
  assert.equal(hash(Buffer.from(actualSource,'utf8')),expectedDigest,
    'exact approved lesson digest differs from browser runtime');
  if(!touch){
    const btn=option.first();
    const original=await btn.evaluate(el=>getComputedStyle(el).backgroundColor);
    await btn.hover();
    await page.waitForTimeout(180);
    const hovered=await btn.evaluate(el=>getComputedStyle(el).backgroundColor);
    assert.notEqual(hovered,original,'desktop option hover has no visual color response');
  }
  const wrong=q.answer==='A'?'B':'A';
  await act(option.locator('[data-a="'+wrong+'"]').first().count()?option.locator('[data-a="'+wrong+'"]').first():
    page.locator('#answerCard .opt[data-a="'+wrong+'"]'),touch);
  await page.locator('#answerCard .option-detail').first().waitFor({timeout:15000});
  assert.equal(await page.locator('#answerCard .option-detail').count(),4,
    'all four true answer explanations must appear');
  assert.equal(await page.locator('#answerCard .opt.correct').count(),1,'correct style lost');
  assert.equal(await page.locator('#answerCard .opt.wrong').count(),1,'wrong style lost');
  const colored=await page.evaluate(()=>({
    correct:getComputedStyle(document.querySelector('#answerCard .opt.correct')).backgroundColor,
    wrong:getComputedStyle(document.querySelector('#answerCard .opt.wrong')).backgroundColor
  }));
  assert.notEqual(colored.correct,colored.wrong,'red/green correctness colors collapsed');
  if(mode==='approved'){
    for(const letter of 'ABCD'){
      const detail=q.optionExplanations[letter];
      const x=page.locator('#answerCard .opt[data-a="'+letter+'"] + .option-detail');
      check(await x.count()===1,'missing separate option detail '+letter);
      const actual=(await x.innerText()).replace(/\s+/g,'');
      for(const [name,value] of Object.entries(detail)){
        check(actual.includes(String(value).replace(/反向檢查/g,'相反意思').replace(/\s+/g,'')),
          letter+' '+name+' exact teaching text differs from source');
      }
    }
    await page.locator('#guideCard.show').waitFor();
    const lines=q.examCalculation?.hasExamCalculation?q.examCalculation.lines:[];
    const calc=page.locator('#guideCard .calculation-step');
    assert.equal(await calc.count(),lines.length,
      'full calculation lines missing or unwanted calculation shown');
    for(let i=0;i<lines.length;i++)
      check((await calc.nth(i).innerText()).includes(lines[i]),'calculation step lost '+i);
    assert.equal(await page.locator('#answerCard .calculation-step').count(),0,
      'duplicate calculation in answer and guide');
    const headings=await page.locator('#guideCard .guide-block h3').allInnerTexts();
    assert.equal(new Set(headings).size,headings.length,'duplicate explanation guide fields');
    if(q.sourceTable){
      const table=page.locator('#questionCard [data-source-table-id="'+q.canonicalId+'"]');
      assert.equal(await table.count(),1,'exact original semantic table missing');
      assert.deepEqual(await table.locator('thead th').allInnerTexts(),q.sourceTable.heading);
      assert.equal(await table.locator('tbody tr').count(),q.sourceTable.rows.length);
    }
    const displayed=await page.locator('#answerCard .option-detail').allInnerTexts();
    const hits=(q.highlights||[]).filter(term=>displayed.join('').includes(term));
    if(hits.length)check(await page.locator('#answerCard mark.exam-highlight').count()>0,
      'highlight terms available, but no real text was highlighted');
    const marks=await page.locator('#answerCard mark.exam-highlight').allInnerTexts();
    for(const mark of marks)check(displayed.join('').includes(mark)&&mark.trim(),
      'highlight uses content absent from rendered lesson');
  }else{
    const section=await page.locator('#guideCard').innerText();
    check(section.includes(q.memory),'35-Demo memory lost');
    if(SUBJECT==='英文'){
      const headers=await page.locator('#guideCard .guide-block h3').allInnerTexts();
      const top=['中文翻譯','發音','同意相關單字','反意相關單字','新聞時事例句'];
      const actual=headers.filter(x=>top.includes(x));
      assert.deepEqual(actual,[...actual].sort((a,b)=>top.indexOf(a)-top.indexOf(b)),
        'Demo English-specific guide priority reversed');
    }
  }
  assert.equal(await page.locator('#memoryWrap, #memoryCard').count(),0,
    'cancelled duplicate memory block reappeared');
  return {questionRevision:q.revision||q.sourceRevision||null,
    teachingDigest:expectedDigest,imageSha256,sharedImageSHA:[]};
}
async function screenshot(page,year,subject,mode,q,width,height,theme){
  const slug=SUBJECT_SLUG[subject];
  const id=q.canonicalId||'demo-'+slug+'-'+String(q.id).padStart(2,'0');
  const rel=path.join(year,slug,mode,
    id+'-'+width+'x'+height+'-'+theme+'.jpg');
  const absolute=path.join(OUTPUT,rel);
  fs.mkdirSync(path.dirname(absolute),{recursive:true});
  await page.screenshot({path:absolute,type:'jpeg',quality:67,fullPage:false,
    animations:'disabled'});
  return rel;
}
function dump(){
  const passed=report.cases.filter(x=>x.status==='PASS').length;
  const failed=report.cases.filter(x=>x.status==='FAIL').length;
  report.summary={passed,failed,missing:report.missing.length,
    eligibleQuestionCount:modes.reduce((s,m)=>s+m.rows.length,0),
    casesExpected:16*modes.reduce((s,m)=>s+m.rows.length,0),
    screenshotCount:report.cases.filter(x=>x.screenshot).length,
    meaning:failed?'UI_QA_FAILED':report.summary?.meaning||'ISOLATED_UI_QA_ONLY_NOT_LIVE'};
  fs.mkdirSync(OUTPUT,{recursive:true});
  fs.writeFileSync(path.join(OUTPUT,YEAR+'-'+SUBJECT_SLUG[SUBJECT]+'.json'),
    JSON.stringify(report,null,2)+'\n');
}
(async()=>{
  fs.mkdirSync(OUTPUT,{recursive:true});
  sourceAudit();
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  try{
    for(const modeEntry of modes){
      const mode=modeEntry.mode,rows=modeEntry.rows;
      if(!rows.length){
        report.missing.push({mode,subject:SUBJECT,year:YEAR,
          status:'NOT_TESTABLE_NO_QUALIFIED_SOURCE',notPass:true});
        continue;
      }
      for(const [width,height] of VIEWPORTS)for(const theme of ['light','dark']){
        const touch=width<=430;
        const context=await browser.newContext({
          viewport:{width,height},hasTouch:touch,reducedMotion:'reduce'
        });
        const page=await context.newPage();
        const errors=[];
        page.on('pageerror',e=>errors.push(e.message));
        let q=null;
        try{
          const query='?year='+YEAR+(mode==='image-preview-only'?'&view=images':'');
          await page.goto(BASE+'v4-115-multisubject-review-demo.html'+query,{waitUntil:'domcontentloaded'});
          if(YEAR!=='demo')await page.waitForFunction(
            ()=>document.body.dataset.verifiedReadyYear===new URLSearchParams(location.search).get('year'),
            null,{timeout:30000});
          check(await page.locator('#homeView').isVisible(),'home YEAR/SUBJECT/REVIEW/COUNTDOWN missing');
          check(await page.locator('#studyView').isHidden(),'home reveals question before subject');
          assert.deepEqual(
            await page.locator('#homeSubjectSel option').evaluateAll(xs=>xs.slice(1).map(x=>x.value)),
            SUBJECTS,'different 35-Demo courses replaced by generic UI');
          await page.locator('#homeSubjectSel').selectOption({label:SUBJECT});
          await page.locator('#studyView').waitFor({state:'visible',timeout:15000});
          if(theme==='dark')await act(page.locator('#themeBtn'),touch);
          assert.equal(await page.locator('html').getAttribute('data-theme'),theme,
            'visible real theme control failed');
          for(let index=0;index<rows.length;index++){
            q=rows[index];
            const label=YEAR+' '+SUBJECT+' '+mode+' '+(q.canonicalId||q.id)+' '+width+'x'+height+' '+theme;
            const geometry=await layoutQA(page,label+' (pre-answer)');
            const evidence=mode==='image-preview-only'?
              await verifyImagePreview(page,q,geometry):
              await verifyActiveQuestion(page,q,mode,touch,geometry);
            await layoutQA(page,label+' (post-action)');
            if(errors.length)throw Error(label+' browser JS exception: '+errors.join(' | '));
            const screenshotFile=await screenshot(page,YEAR,SUBJECT,mode,q,width,height,theme);
            report.cases.push({status:'PASS',canonicalId:q.canonicalId||null,
              questionId:q.canonicalId||SUBJECT+'|'+q.id,
              questionNumber:assertOriginalQuestionNumber(q,mode),mode,
              viewport:{width,height},theme,input:touch?'real_touch_tap':'real_mouse_click',
              checks:{noHorizontalOverflow:true,textUnclipped:true,webpAspect:true,
                originalWebpBytes:true,digestBound:mode!=='image-preview-only',
                fourOptions:mode!=='image-preview-only',dualLevel:mode==='approved',
                readOnly:mode==='image-preview-only',realQuestionData:true},
              ...evidence,screenshot:screenshotFile});
            if(index<rows.length-1){
              await act(page.locator('#nextBtn'),touch);
            }
          }
          if(mode!=='image-preview-only'){
            await act(page.locator('#navHandle'),touch);
            await act(page.locator('#navHomeBtn'),touch);
            await act(page.locator('#homeReviewBtn'),touch);
            await page.locator('#reviewList .wrong-card').first().waitFor({timeout:15000});
            assert.equal(await page.locator('#reviewList .wrong-card').count(),rows.length,
              'answered mistake count not preserved in review');
            const value=YEAR==='demo'?'tvet-115-multisubject-demo-v1':
              'tvet-verified-'+YEAR+'-v1';
            check(await page.evaluate(k=>!!localStorage.getItem(k),value),
              'actual student history not stored in expected isolated namespace');
          }
        }catch(e){
          const name=(q?.canonicalId||q?.id||'ENTRY');
          report.cases.push({status:'FAIL',year:YEAR,subject:SUBJECT,mode,
            questionId:name,viewport:{width,height},theme,
            error:String(e?.stack||e),browserErrors:errors,
            notApprovedForRelease:true});
          const faildir=path.join(OUTPUT,YEAR,SUBJECT_SLUG[SUBJECT],mode);
          fs.mkdirSync(faildir,{recursive:true});
          try{await page.screenshot({path:path.join(faildir,'FAIL-'+width+'x'+height+'-'+theme+'.jpg'),
            type:'jpeg',quality:67,fullPage:false})}catch{}
        }finally{
          await context.close();
          dump();
        }
      }
    }
  }finally{await browser.close()}
  dump();
  check(report.summary.failed===0,
    'Role D V4 exact-source browser matrix failures: '+report.summary.failed+
    ' (see test-results/role-d JSON and screenshots)');
  check(report.cases.filter(x=>x.status==='PASS').length===report.summary.casesExpected,
    'some actual question x 8 viewport x 2 theme cases were not independently exercised');
  console.log(JSON.stringify({role:'D',year:YEAR,subject:SUBJECT,summary:report.summary,
    htmlSha256:report.htmlSha256,runtimeSha256:report.runtimeSha256,actualCommitSha:report.actualCommitSha}));
})().catch(error=>{
  report.fatal=String(error.stack||error);
  dump();
  console.error(error.stack||error);
  process.exitCode=1;
});