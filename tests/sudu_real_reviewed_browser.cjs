/* Real 115 Math B audited source data, not hand-authored fixtures.
 * Only CI substitutes temporary PASS UI evidence; no branch source mutated. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright');
const source=JSON.parse(fs.readFileSync('sudu/data/approved/115.json','utf8'));
const IDs=['115-00-MB-02','115-00-MB-03','115-00-MB-04','115-00-MB-09'];
assert.deepEqual(source.questions.map(q=>q.canonicalId).sort(), [...IDs].sort());
assert.equal(source.approvedCount,4);
const answers=['A','A','C','A'];
const sizes=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
(async()=>{
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  try{
    for(const [width,height] of sizes){
      const page=await browser.newPage({viewport:{width,height}});
      try{
        await page.goto('http://127.0.0.1:8765/sudu/v4-115-multisubject-review-demo.html?year=115');
        await page.locator('#verifiedStatus').waitFor({timeout:20000});
        assert.match(await page.locator('#verifiedStatus').innerText(),/已通過全部驗收並開放 4 題/);
        assert.equal(await page.locator('#subjectSel option').count(),1);
        for(let i=0;i<4;i++){
          const expected=source.questions[i];
          assert.equal(expected.canonicalId,IDs[i]);
          assert.equal(expected.answer,answers[i]);
          const number=await page.locator('#questionCard .qnum').innerText();
          assert.equal(Number(number),expected.id);
          assert.equal(await page.locator('#studyView .opt').count(),4);
          const img=page.locator('#questionCard img').first();
          const src=await img.getAttribute('src');
          assert.equal(src,expected.image);
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
          assert.match(await correct.innerText(),/考題計算式/);
          assert.equal(await page.locator('#memoryWrap.show').count(),1);
          assert.equal(await page.locator('#nextBtn').isDisabled(),i===3);
          if(i<3)await page.locator('#nextBtn').click();
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
    console.log('PASS: FOUR actual QA audited questions x 8 responsive viewports, correct answer, full steps, wrong state, 4 options, 2 levels and original WebP decode');
  }finally{await browser.close()}
})().catch(error=>{console.error(error.stack||error);process.exitCode=1});
