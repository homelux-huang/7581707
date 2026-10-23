/* Positive 114/115 student-mode regression. Synthetic, intercepted fixture ONLY.
   Real QA file releases remain empty until all independent gates succeed. */
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const base=process.env.SUDU_TEST_URL||'http://127.0.0.1:8765/sudu/';
const explanation=Object.fromEntries('ABCD'.split('').map(letter=>[letter,{
 teacher:letter==='A'?'代入直線求正確截距與平行斜率':'另個選項有錯誤截距或斜率',
 elementary:letter==='A'?'這條線往右下降、碰到x軸在2':'這個交點或斜坡方向不正確',
 reason:letter==='A'?'符合兩個條件':'至少一個條件不符',
}]));
const reviewQ={
 id:3,canonicalId:'115-00-MB-03',year:115,subject:'數學 B',
 topic:'直線的斜率與截距',
 question:'已知直線 L₁：2x+3y=4 與直線 L₂ 相互平行。若 L₁ 的 x 截距為 a，L₂ 的斜率為 m，則 (a,m)＝？',
 options:['(2, −2/3)','(2, 2/3)','(4/3, −2/3)','(4/3, 2/3)'],
 answer:'A',memory:'x截距令 y=0；平行斜率相同',concept:'y=−2x/3+4/3',
 extension:'垂直線斜率是3/2',formula:'y=mx+b',sourceText:'官方統測；高職數學(B)，教材頁數待核對',
 teacherSummary:'先找x截距再比較斜率',elementarySummary:'比較坡道碰到地面的位置和方向',
 optionExplanations:explanation,
 examCalculation:{hasExamCalculation:true,lines:['已知條件：2x+3y=4','公式用途：斜率和平行','代入：y=0',
   '步驟：2x=4，所以 x=2','步驟：y=−2x/3+4/3','結果：(a,m)=(2,−2/3)','對應選項：A']},
 image:'data/approved/webp/115/115-00-MB-03.webp'
};
const conceptual={...reviewQ,id:4,canonicalId:'115-00-MB-04',topic:'二次不等式',
 question:'下列關於二次不等式的觀念，何者正確？',
 options:['超過根外','永遠無解','兩根之間','不必計算'],
 answer:'C',examCalculation:null,image:'data/approved/webp/115/115-00-MB-04.webp',
 optionExplanations:Object.fromEntries('ABCD'.split('').map(k=>[k,{
  teacher:k==='C'?'開口向上，負值區在兩根間':'其他選項不符合條件',
  elementary:k==='C'?'U形碗的底部在兩根之間':'這個方向不符合形狀',
  reason:k==='C'?'觀念正確':'觀念不成立'
 }]))
};
const snapshot={schemaVersion:1,year:115,expected:205,approvedCount:2,questions:[reviewQ,conceptual]};
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage();
 try{
  await page.route('**/data/approved/115.json*',route=>route.fulfill({
   status:200,contentType:'application/json',body:JSON.stringify(snapshot)}));
  const sizes=[[360,800],[375,812],[390,844],[412,915],[430,932],[768,1024],[1024,768],[1440,900]];
  for(const [width,height] of sizes){
   await page.setViewportSize({width,height});
   await page.goto(base+'v4-115-multisubject-review-demo.html?year=115');
   await page.locator('#questionCard .qnum').waitFor();
   await page.waitForFunction(()=>!document.body.classList.contains('verified-year-loading'));
   assert.equal(await page.locator('#verifiedStatus').count(),0);
   assert.equal(await page.locator('#verifiedImagePreview').count(),0);
   assert.equal(await page.locator('#verifiedYearNav').count(),0);
   assert.equal(await page.locator('#verifiedPreviewToggle').count(),0);
   assert.equal(await page.locator('#studyView .opt').count(),4);
   const img=page.locator('#questionCard img[data-mock-asset], #questionCard img').first();
   assert(await img.evaluate(async el=>{await el.decode();return el.naturalWidth>0}));
   assert(await page.locator('#prevBtn').isDisabled());
   assert(await page.locator('#nextBtn').isEnabled());
   await page.locator('#studyView .opt[data-a="B"]').click();
   await page.locator('#studyView .option-detail').first().waitFor();
   assert.match(await page.locator('#answerCard').innerText(),/國小學生也聽得懂/);
   assert.match(await page.locator('#answerCard').innerText(),/考題計算式/);
   const wrong=await page.locator('#studyView .opt.wrong').count();
   assert(wrong>=1,'selected wrong answer should be styled red');
   await page.locator('#nextBtn').click();
   assert.match(await page.locator('#questionCard .qnum').innerText(),/04/);
   assert(await page.locator('#nextBtn').isDisabled());
   await page.locator('#studyView .opt[data-a="C"]').click();
   await page.locator('#studyView .option-detail').first().waitFor();
   assert(!/考題計算式/.test(await page.locator('#answerCard').innerText()),
      'Non-calculating question must not render empty calculation block');
   for(const theme of ['light','dark']){
    await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
    const d=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
    assert(d.scroll<=d.width+1,'Positive student QA mode overflow: '+width+' '+theme+' '+JSON.stringify(d));
   }
   await page.locator('#prevBtn').click();
   assert.match(await page.locator('#questionCard .qnum').innerText(),/03/);
   assert(await page.locator('#nextBtn').isEnabled());
  }
  console.log('PASS: 2 verified-student fixtures; answer/color, both explanation levels, worked math, hidden no-calc, image decode, 8x2 RWD');
 }finally{await browser.close()}
})().catch(err=>{console.error(err.stack||String(err));process.exitCode=1});
