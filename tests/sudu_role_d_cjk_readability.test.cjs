'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {assertReadableGlyphs}=require('./sudu_role_d_cjk_readability.cjs');
const records=()=>[...[...'繁體中文數學會計'].map((character,i)=>({kind:'cjk',character,
  signature:'distinct-'+i,inkPixels:500})),{kind:'missing',character:'\ufffd',signature:'tofu',inkPixels:500}];
test('glyph contract accepts distinct nonblank samples with missing-glyph control',()=>{
  assert.doesNotThrow(()=>assertReadableGlyphs(records()));
});
test('repeated tofu, missing control, blank and replacement glyphs fail closed',()=>{
  const tofu=records().map(x=>x.kind==='cjk'?{...x,signature:'tofu'}:x);
  assert.throws(()=>assertReadableGlyphs(tofu),/missing-glyph boxes/);
  assert.throws(()=>assertReadableGlyphs(records().filter(x=>x.kind!=='missing')),/control required/);
  const blank=records();blank[0].inkPixels=0;
  assert.throws(()=>assertReadableGlyphs(blank),/blank/);
  const replacement=records();replacement[0].signature='tofu';
  assert.throws(()=>assertReadableGlyphs(replacement),/matches missing/);
});
