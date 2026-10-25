'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {visibleOptionFields}=require('./sudu_role_d_option_detail.cjs');
const legacyIds=['115-00-MB-02','115-00-MB-03','115-00-MB-04','115-00-MB-05','115-00-MB-09'];
const questions=JSON.parse(fs.readFileSync('sudu/data/approved/115.json','utf8')).questions
  .filter(q=>legacyIds.includes(q.canonicalId));
const sample=questions.find(q=>q.canonicalId==='115-00-MB-05');
test('all five real historical questions preserve exact A-D display texts',()=>{
  assert.equal(questions.length,5);
  assert.deepEqual(questions.map(q=>q.canonicalId).sort(),[...legacyIds].sort());
  for(const q of questions)for(const letter of 'ABCD'){
    const entries=visibleOptionFields(q.optionExplanations[letter],letter,q.answer);
    assert.deepEqual(entries.map(x=>x[0]),['teacher','elementary','reason']);
    for(const [key,text] of entries)assert.equal(text,q.optionExplanations[letter][key]);
  }
});
test('MB05 boolean metadata stays typed and tied to the actual source answer',()=>{
  assert.equal(sample.answer,'B');
  for(const letter of 'ABCD'){
    assert.equal(sample.optionExplanations[letter].isCorrect,letter===sample.answer);
    assert.equal(visibleOptionFields(sample.optionExplanations[letter],letter,sample.answer).length,3);
  }
});
test('string true/false, numeric and null correctness metadata are rejected',()=>{
  for(const isCorrect of ['true','false',0,1,null])
    assert.throws(()=>visibleOptionFields({...sample.optionExplanations.A,isCorrect},'A','B'),/must be boolean/);
});
test('wrong actual boolean cannot bypass the source answer',()=>{
  assert.throws(()=>visibleOptionFields({...sample.optionExplanations.A,isCorrect:true},'A','B'),/conflicts/);
  assert.throws(()=>visibleOptionFields({...sample.optionExplanations.B,isCorrect:false},'B','B'),/conflicts/);
});
test('missing or empty explanation and unknown metadata cannot silently pass',()=>{
  for(const name of ['teacher','elementary','reason']){
    const detail={...sample.optionExplanations.A};delete detail[name];
    assert.throws(()=>visibleOptionFields(detail,'A','B'),/source text/);
    assert.throws(()=>visibleOptionFields({...sample.optionExplanations.A,[name]:''},'A','B'),/must not be empty/);
  }
  assert.throws(()=>visibleOptionFields({...sample.optionExplanations.A,approved:true},'A','B'),/unknown/);
});
