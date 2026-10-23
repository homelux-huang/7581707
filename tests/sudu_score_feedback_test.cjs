/* Pure A-mode practice scoreboard checks. No QA release flags or histories touched. */
const assert = require('node:assert/strict');
const S = require('../sudu/v4-score-feedback.js');
let tests=0;
function check(name,fn){fn();tests++;console.log('PASS A SCORE: '+name)}
const mk=(subject='數學 B')=>Array.from({length:5},(_,i)=>({subject,id:i+1,answer:'B'}));
const entries={};
const score=(q,correct,round=1,subject=q.subject)=>{const r=entries[subject+'|'+q.id]||{attempts:0,wrongCount:0};
  entries[subject+'|'+q.id]=r;
  const outcome=S.lockFirstAnswer(q,r,correct?'B':'C',round,'demo');
  r.status=correct?'ok':'bad';r.selected=correct?'B':'C';r.attempts++;
  return outcome;};
check('115 source-covered 5-question practice weights and no negative marking',()=>{
  const points=[['數學 B',4],['國文',2],['英文',2],['商業概論',2],
    ['數位科技',2],['會計學',2],['經濟學',2]];
  const rules=require('../sudu/data/scoring-rules.json').rules.filter(r=>r.year===115);
  const paper={'數學 B':'00-MB','國文':'00-C','英文':'00-E',
    '商業概論':'09-1','數位科技':'09-1','會計學':'09-2','經濟學':'09-2'};
  for(const [subject,weight] of points){
    const rule=rules.find(r=>r.paper===paper[subject]);
    assert.equal(rule.basePointsVerified,true);
    assert.equal(rule.incorrectPenalty,0);
    assert(Object.values(rule.points).every(x=>x===weight));
    assert.equal(S.questionPoints({subject,id:1,answer:'B'},'demo'),weight);
    assert.equal(S.questionPoints({subject,id:1,answer:'B'},'115'),null,
      'formal papers require the separate verified scoring engine');
  }
});
check('first correct +4, first wrong +0, score rate uses real max',()=>{
  const qs=mk();
  assert.equal(score(qs[0],true).earned,4);
  assert.equal(score(qs[1],false).earned,0);
  let s=S.totalFor(qs,'數學 B',entries,1,'demo');
  assert.equal(s.earned,4);assert.equal(s.max,20);
  assert.equal(s.missed,4);assert.equal(s.percent,20);
  assert.equal(s.answered,2);assert.equal(s.complete,false);
});
check('re-answer never adds marks or changes first answer snapshot',()=>{
  const q=mk()[0],r=entries['數學 B|1'];let old={...r};
  let repeat=score(q,false);
  assert.equal(repeat.first,false);assert.equal(repeat.earned,0);
  assert.equal(r.scoreCorrect,old.scoreCorrect);
  assert.equal(S.totalFor(mk(),'數學 B',entries,1,'demo').earned,4);
});
check('five answers produce a real 16/20 or 80-percent practice subtotal',()=>{
  const qs=mk();
  score(qs[2],true);score(qs[3],true);score(qs[4],true);
  let s=S.totalFor(qs,'數學 B',entries,1,'demo');
  assert.equal(s.earned,16);assert.equal(s.max,20);
  assert.equal(s.percent,80);assert.equal(s.missed,4);
  assert.equal(s.correct,4);assert.equal(s.wrong,1);assert.equal(s.complete,true);
  assert.equal(s.pendingTotal,0);
});
check('reset/new round cannot reuse prior round points; old history remains',()=>{
  const qs=mk();
  const before=JSON.stringify(entries);
  let s=S.totalFor(qs,'數學 B',entries,2,'demo');
  assert.equal(s.earned,0);assert.equal(s.answered,0);
  score(qs[0],false,2);
  s=S.totalFor(qs,'數學 B',entries,2,'demo');
  assert.equal(s.earned,0);assert.equal(s.missed,4);
  assert.notEqual(JSON.stringify(entries),before);
});
check('older localStorage practice status remains readable without record rewrite',()=>{
  const qs=mk('英文'),legacy={};
  legacy['英文|1']={attempts:2,status:'ok',selected:'B'};
  assert.equal(S.totalFor(qs,'英文',legacy,1,'demo').earned,2);
  assert.equal(S.totalFor(qs,'英文',legacy,2,'demo').earned,0);
  assert.equal(legacy['英文|1'].scoreRound,undefined);
});
check('seed records with no attempts are not misgraded',()=>{
  const qs=mk('英文'),fake={};
  fake['英文|1']={attempts:0,status:'bad',wrongCount:3};
  assert.equal(S.totalFor(qs,'英文',fake,1,'demo').answered,0);
});
check('two disputed demo questions are blocked, not approved by a score widget',()=>{
  for(const [subject,id] of [['商業概論',7],['經濟學',28]]){
    const qs=mk(subject);qs[4].id=id;
    const rec={attempts:0,status:null};
    const pending=S.lockFirstAnswer(qs[4],rec,'B',1,'demo');
    assert.equal(pending.blocked,true);
    assert.equal(rec.scoreRound,undefined,'no approval flag or earned mark');
    const records={[subject+'|'+id]:{attempts:1,status:'bad'}};
    const s=S.totalFor(qs,subject,records,1,'demo');
    assert.equal(s.max,8);assert.equal(s.earned,0);
    assert.equal(s.pendingTotal,1);
    assert.equal(s.answered,1);assert.equal(s.fullyVerified,false);
  }
});
check('5-question scope and official-year release are always isolated',()=>{
  assert.equal(S.totalFor(mk().slice(0,4),'數學 B',{},1,'demo').eligible,false);
  assert.equal(S.totalFor(mk(),'數學 B',{},1,'115').eligible,false);
  assert.equal(S.lockFirstAnswer(mk()[0],{status:null},'B',1,'115').eligible,false);
});
console.log('PASS: '+tests+' A-style scoring, history and QA-gate scenarios');
