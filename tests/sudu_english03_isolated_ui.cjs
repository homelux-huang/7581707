'use strict';
// QA only: exact E03 text and current main HTML, candidate adapter intercepted locally.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),{chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),main=path.resolve(process.env.SUDU_QA_MAIN_CHECKOUT||'current-main');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8777/sudu/';
assert(process.env.SUDU_PREVIEW_ONLY==='1'&&new URL(base).hostname==='127.0.0.1');
const folder=path.join(root,'sudu/teaching-drafts/preview-128-20261023');
const q=JSON.parse(fs.readFileSync(path.join(folder,'115-00-E-03.json'),'utf8')),t=q.teaching,e=t.english;
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
assert.equal(hash(fs.readFileSync(path.join(main,'sudu',q.image))),q.imageSha256);
assert.equal(q.studentReleaseApproved,false);assert.equal(q.deploy,false);
const levels=o=>Object.entries(o).map(([k,v])=>k+'：'+v.join('、')).join('\n');
const fixture={year:115,canonicalId:q.questionId,id:3,subject:'英文',topic:'同等對待',
 question:'The teacher treats all her students ________, giving every student the same opportunity to succeed.',
 options:['carelessly','equally','instantly','silently'],answer:'B',image:q.image,imageSha256:q.imageSha256,
 memory:t.memory,concept:t.concept,extension:t.extension,formula:'',teacherSummary:t.teacherSummary,
 elementarySummary:t.elementarySummary,optionExplanations:t.optionExplanations,highlights:t.highlightTerms,
 sourceText:'彰化高商適用英文教材版本、單元、章節、頁數：待核對',
 extra:{'中文翻譯':e.sentenceTranslationZh,'發音':e.pronunciationIPA,
 '同意相關單字':levels(e.synonyms),'反意相關單字':levels(e.antonyms),
 '新聞時事例句':e.newsExampleKind+'\n英文：'+e.newsExampleEnglish+'\n中文：'+e.newsExampleChinese+'\n來源：'+e.newsExampleSourceOrganization+'｜'+e.newsExampleSourceDate+'\n'+e.newsExampleSourceUrl},
 examCalculation:{hasExamCalculation:false,lines:[]}};
const out=path.resolve(process.env.SUDU_TEST_OUTPUT||'test-results/english03-ui');fs.mkdirSync(out,{recursive:true});
const canonical=o=>Array.isArray(o)?o.map(canonical):o&&typeof o==='object'?Object.fromEntries(Object.keys(o).sort().map(k=>[k,canonical(o[k])])):o;
const report={kind:'ISOLATED_E03_MAIN_HTML_CANDIDATE_ADAPTER',questionId:q.questionId,
 imageSha256:q.imageSha256,teachingDigestSha256:hash(JSON.stringify(canonical(t))),
 actualReleaseApproved:false,fullTeachingReview:false,observations:[],errors:[]};
const adapter=fs.readFileSync(path.join(root,'sudu/verified-questions-runtime.js'),'utf8');
assert(!adapter.includes('verifiedImagePreview'),'do not restore obsolete preview panel');
(async()=>{const browser=await chromium.launch({headless:true,args:['--no-sandbox']});try{
 for(const [width,height] of [[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]])for(const theme of ['light','dark']){
 const ctx=await browser.newContext({viewport:{width,height},hasTouch:width<1024,isMobile:width<768,reducedMotion:'reduce'});
 const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const activate=el=>width<1024?el.tap({timeout:10000}):el.click({timeout:10000});
 try{
 await ctx.route('**/verified-questions-runtime.js*',r=>r.fulfill({contentType:'text/javascript',body:adapter}));
 await ctx.route('**/data/approved/115.json',r=>r.fulfill({contentType:'application/json',body:JSON.stringify({year:115,approvedCount:1,questions:[fixture]})}));
 await page.goto(base+'v4-115-multisubject-review-demo.html?year=115&subject='+encodeURIComponent('英文'));
 await page.waitForFunction(()=>document.body.dataset.verifiedReadyYear==='115');
 await page.evaluate(theme=>{document.documentElement.dataset.theme=theme;state.theme=theme;},theme);
 assert.equal((await page.locator('#questionCard .qnum').innerText()).trim(),'03');
 const qaImage=page.locator('#questionCard .source-figure img');
 const imageDiagnostic=await qaImage.evaluate(async img=>{
   const source=img.currentSrc||img.src;
   let http=null,size=null,fetchError=null,decodeError=null;
   try{const r=await fetch(source);http=r.status;size=(await r.arrayBuffer()).byteLength;}
   catch(e){fetchError=String(e)}
   try{await img.decode();}catch(e){decodeError=String(e)}
   return {source,rawAttribute:img.getAttribute('src'),http,size,fetchError,decodeError,
     naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight};
 });
 assert(imageDiagnostic.naturalWidth>100&&!imageDiagnostic.decodeError,
   'Image decode in V4: '+JSON.stringify(imageDiagnostic));
 assert.equal(await page.locator('#guideCard.show').count(),0);
 await activate(page.locator('#answerCard .opt[data-a="A"]'));
 await page.locator('#guideCard.show').waitFor();
 assert.equal(await page.locator('.option-detail').count(),4);
 assert.equal(await page.locator('.option-detail p').count(),8,'two distinct levels, no duplicated reason');
 assert((await page.locator('.option-detail.is-correct strong mark').allTextContents()).includes('equally'));
 const guide=await page.locator('#guideCard').innerText();
 for(const word of ['初級','中級','高級',e.newsExampleChinese,e.newsExampleEnglish])assert(guide.includes(word),word);
 assert(!guide.includes('**'));assert(!/\b(low|mid|high)\s*:/i.test(guide));
 assert.equal(await page.locator('#guideCard .calculation-first').count(),0);
 assert((await page.locator('#guideCard mark').allTextContents()).includes('equally'));
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
 await activate(page.locator('#questionBtn'));assert.equal(await page.locator('#guideCard.show').count(),0);
 await activate(page.locator('#explainBtn'));await page.locator('#guideCard.show').waitFor();
 // On mobile the dynamic top bar intentionally collapses after answering.
 // Use the real visible handle to expand it before touching the review entry.
 const navHandle=page.locator('#navHandle');
 await activate(navHandle);
 assert.equal(await navHandle.getAttribute('aria-expanded'),'true','navigation opened by real touch/click');
 await activate(page.locator('#reviewTop'));await page.locator('#reviewView.show').waitFor();
 const review=await page.locator('#reviewList').innerText();
 assert(review.includes(e.newsExampleChinese)&&review.includes('正確答案 B'));
 assert(!review.includes('**'));assert((await page.locator('#reviewList mark').allTextContents()).includes('equally'));
 assert.equal(await page.locator('#studyView').isVisible(),false);
 await activate(page.locator('#reviewList .goto'));
 await activate(page.locator('#answerCard .opt[data-a="B"]'));
 assert.equal(await page.locator('#answerCard .opt.correct').count(),1);
 assert.deepEqual(errors,[]);
 await page.screenshot({path:path.join(out,`${width}x${height}-${theme}.png`),fullPage:true});
 report.observations.push({width,height,theme,input:width<1024?'touch':'mouse',passed:true});
 }catch(e){await page.screenshot({path:path.join(out,`FAIL-${width}-${theme}.png`),fullPage:true});throw e;}finally{await ctx.close();}
 }
 console.log('PASS: E03 exact options, bold/highlight, bilingual news, wrong review and click/touch x 8 sizes x 2 themes');
 }finally{await browser.close();}})().catch(e=>{report.errors.push(String(e.stack||e));process.exitCode=1;console.error(e);}).finally(()=>fs.writeFileSync(path.join(out,'english03-summary.json'),JSON.stringify(report,null,2)));
