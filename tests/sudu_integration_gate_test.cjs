const assert=require('node:assert/strict');
const gate=require('../sudu/verified_question_adapter.js');
const expected={'國文':[1,2,3,7,9],'英文':[1,2,3,4,5],'數學 B':[7,9,10,11,12],
  '商業概論':[1,3,5,6,7],'數位科技':[26,27,28,32,34],'會計學':[2,3,4,5,6],
  '經濟學':[25,26,27,28,29]};
const keys=gate.demoLegacyKeys();assert.equal(Object.keys(keys).length,35);
for(const [name,ids] of Object.entries(expected))
 for(const n of ids)assert.equal(keys[name+'|'+n],gate.canonical(115,name,n));
assert.equal(gate.canonical(114,'國文',1),null);
const q={questionRevision:'source-hash-1',officialFinalAnswer:'B'};
const ev={solvedWithoutOfficialAnswer:true,solvedAt:'2026-10-22T10:00:00+08:00',
  questionRevision:'source-hash-1',aiAnswer:'C',
  imageQa:true,textQa:true,dbQa:true,sourceQa:true,
  officialCorrectionChecked:true,answerVerified:true,
  teachingQa:true,uiQa:true,studentReleaseApproved:true};
let mismatch=gate.review(q,ev);
assert.equal(mismatch.comparison,'mismatch');
assert.equal(mismatch.studentReady,false);
assert.match(mismatch.warning,/警示：AI 解答與題庫官方解答不一致，本題待核對。/);
assert.match(mismatch.warning,/AI 答案：C；官方答案：B/);
assert.equal(gate.review(q,{...ev,solvedWithoutOfficialAnswer:false}).comparison,'not_checked');
assert.equal(gate.review(q,{...ev,questionRevision:'old-source'}).comparison,'not_checked');
assert.equal(gate.review(q,{...ev,officialCorrectionChecked:false}).comparison,'not_checked');
assert.equal(gate.review(q,{...ev,aiAnswer:'B',imageQa:false}).studentReady,false);
assert.equal(gate.review(q,{...ev,aiAnswer:'B',teachingQa:false}).studentReady,false);
assert.equal(gate.review(q,{...ev,aiAnswer:'B'}).studentReady,true);
let notice,disabled=false;const button={set disabled(value){disabled=value;}};
const card={
 ownerDocument:{createElement(){return {
   setAttribute(){},style:{},set textContent(x){notice=x}
 }}},
 querySelector(){return null;},
 prepend(){}};
gate.renderBlockingNotice(card,[button],mismatch);
assert.equal(disabled,true);assert.match(notice,/AI 答案：C/);
gate.renderBlockingNotice(card,[button],gate.review(q,{...ev,aiAnswer:'B'}));
assert.equal(disabled,false);
console.log('PASS: 35 historical IDs remain mapped; pending, mismatch, source change and student blocking enforced');
