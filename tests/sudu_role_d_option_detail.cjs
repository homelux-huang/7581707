'use strict';
const assert=require('node:assert/strict');
function visibleOptionFields(detail,letter,answer){
  assert(detail&&typeof detail==='object'&&!Array.isArray(detail),'option explanation object required');
  assert(/^[ABCD]$/.test(letter)&&/^[ABCD]$/.test(answer),'exact A-D option and answer required');
  const fields=['teacher','elementary','reason'];
  for(const name of Object.keys(detail))
    assert(fields.includes(name)||name==='isCorrect','unknown explanation field: '+name);
  for(const name of fields){
    assert.equal(typeof detail[name],'string',name+' must be source text');
    assert(detail[name].trim(),name+' must not be empty');
  }
  if(Object.hasOwn(detail,'isCorrect')){
    assert.equal(typeof detail.isCorrect,'boolean','isCorrect must be boolean, not display text');
    assert.equal(detail.isCorrect,letter===answer,'isCorrect conflicts with source answer');
  }
  return fields.map(name=>[name,detail[name]]);
}
module.exports={visibleOptionFields};
