/* Real 115 Math B audited source data, not hand-authored fixtures.
 * Only CI substitutes temporary PASS UI evidence; no branch source mutated. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {createHash}=require('node:crypto');
const {chromium}=require('playwright');
const source=JSON.parse(fs.readFileSync('sudu/data/approved/115.json','utf8'));
const IDs=['115-00-MB-02','115-00-MB-03','115-00-MB-04','115-00-MB-05','115-00-MB-09'];
assert.deepEqual(source.questions.map(q=>q.canonicalId).sort(), [...IDs].sort());
assert.equal(source.approvedCount,IDs.length);
const answers=['A','A','C','B','A'];
const sizes=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
(async()=>{
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  try{
    for(const [width,height] of sizes){
      const page=await browser.newPage({viewport:{width,height}});
      try{
        await page.goto('http://127.0.0.1:8765/sudu/v4-115-multisubject-review-demo.html?year=115');
        await page.waitForFunction(()=>!document.body.classList.contains('verified-year-loading'),{timeout:20000});
        assert(await page.locator('#homeView').isVisible(),'real approved year opens home');
        await page.locator('#homeSubjectSel').selectOption({label:'數學 B'});
        assert(await page.locator('#studyView').isVisible(),'real subject selection opens quiz');
        await page.locator('#questionCard .qnum').waitFor();
        assert.equal(await page.locator('#verifiedStatus').count(),0);
        assert.equal(await page.locator('#verifiedImagePreview').count(),0);
        assert.equal(await page.locator('#verifiedYearNav').count(),0);
        assert.equal(await page.locator('#verifiedPreviewToggle').count(),0);
        assert.equal(await page.locator('#subjectSel option').count(),1);
        for(let i=0;i<IDs.length;i++){
          const expected=source.questions[i];
          assert.equal(expected.canonicalId,IDs[i]);
          assert.equal(expected.answer,answers[i]);
          const number=await page.locator('#questionCard .qnum').innerText();
          assert.equal(Number(number),expected.id);
          assert.equal(await page.locator('#studyView .opt').count(),4);
          const img=page.locator('#questionCard img').first();
          const src=await img.getAttribute('src');
          assert.equal(src,expected.image);
          const expectedUrl=new URL(expected.image,page.url()).href;
          assert.equal(await img.evaluate(el=>el.src),expectedUrl);
          const response=await page.request.get(expectedUrl);
          assert.equal(response.status(),200,'Original image HTTP status '+expected.canonicalId);
          assert.equal(response.url(),expectedUrl,'Original image must not redirect');
          assert.match(response.headers()['content-type']||'',/^image\/webp(?:;|$)/i);
          const bytes=await response.body();
          assert(bytes.length>=12,'Original image WebP header');
          assert.equal(bytes.toString('ascii',0,4),'RIFF');
          assert.equal(bytes.toString('ascii',8,12),'WEBP');
          assert.equal(createHash('sha256').update(bytes).digest('hex'),expected.imageSha256,
            'Original image SHA256 '+expected.canonicalId);
          await img.scrollIntoViewIfNeeded();
          await page.waitForFunction(url=>{
            const el=document.querySelector('#questionCard img');
            return el&&el.src===url&&el.complete&&el.naturalWidth>0&&el.naturalHeight>0;
          },expectedUrl);
          assert(await img.evaluate(async el=>{await el.decode();return el.naturalWidth>0&&el.naturalHeight>0}),
            'WebP image must decode '+expected.canonicalId);
          for(let idx=0;idx<4;idx++){
            assert((await page.locator('#studyView .opt .opt-text').nth(idx).innerText()).length>0);
          }
          const wrong=expected.answer==='A'?'B':'A';
          await page.locator('#studyView .opt[data-a="'+wrong+'"]').click();
          await page.locator('#studyView .option-detail').first().waitFor();
          assert.equal(await page.locator('#studyView .option-detail').count(),4,
            'All A/B/C/D options need explanation '+expected.canonicalId);
          assert.equal(await page.locator('#studyView .opt.wrong').count(),1);
          const correct=page.locator('#studyView .option-detail.is-correct');
          assert.equal(await correct.count(),1);
          assert.match(await correct.innerText(),/高職生理解/);
          assert.match(await correct.innerText(),/國小學生也聽得懂/);
          await page.locator('#guideCard.show').waitFor();
          assert.equal(await page.locator('#guideCard .guide-block h3').first().innerText(),'考題計算式','every real math calculation leads the guide');
          assert(await page.locator('#guideCard .calculation-step').count()>=5,'all original worked steps remain');
          assert.equal(await correct.locator('.calculation-step').count(),0,'steps not duplicated inside correct option');
          assert.equal(await correct.locator('.option-detail-grid').count(),0,'real approved correct answer has no duplicated guide metadata');
          assert.equal(await page.locator('#memoryWrap, #memoryCard').count(),0,'no duplicate memory card');
          assert.equal(await page.locator('#nextBtn').isDisabled(),i===IDs.length-1);
          if(i<IDs.length-1)await page.locator('#nextBtn').click();
        }
        for(const theme of ['light','dark']){
          await page.evaluate(t=>{
            document.documentElement.dataset.theme=t;
            document.body.dataset.theme=t;
          },theme);
          const dimensions=await page.evaluate(()=>({
            innerWidth,scrollWidth:document.documentElement.scrollWidth,
            scrollBody:document.body.scrollWidth,
          }));
          assert(dimensions.scrollWidth<=dimensions.innerWidth+1 &&
                 dimensions.scrollBody<=dimensions.innerWidth+1,
            'Horizontal overflow '+width+' '+theme+' '+JSON.stringify(dimensions));
        }
        console.log('PASS: real 115 math original answer/images/explanations, '+width+'x'+height);
      }finally{await page.close()}
    }
    console.log('PASS: FIVE actual QA audited questions x 8 responsive viewports, correct answer, full steps, wrong state, 4 options, 2 levels and original WebP decode');
  }finally{await browser.close()}
})().catch(error=>{console.error(error.stack||error);process.exitCode=1});
