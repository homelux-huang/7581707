'use strict';
const assert=require('node:assert/strict');
const {createHash}=require('node:crypto');
function assertReadableGlyphs(records){
  const samples=records.filter(x=>x.kind==='cjk');
  const missing=new Set(records.filter(x=>x.kind==='missing').map(x=>x.signature));
  assert(samples.length>=8,'representative Traditional Chinese glyphs required');
  assert(missing.size>0,'missing-glyph control required');
  assert.equal(new Set(samples.map(x=>x.character)).size,samples.length,'duplicate sample characters');
  assert.equal(new Set(samples.map(x=>x.signature)).size,samples.length,
    'Chinese characters collapse to identical missing-glyph boxes');
  for(const sample of samples){
    assert(sample.inkPixels>30,'Chinese glyph is blank: '+sample.character);
    assert(!missing.has(sample.signature),'Chinese glyph matches missing-glyph control: '+sample.character);
  }
}
async function verifyCjkReadability(page){
  const raster=await page.evaluate(async()=>{
    await document.fonts.ready;
    const family=getComputedStyle(document.body).fontFamily;
    const samples=[...'繁體中文數學會計經濟題解'];
    const canvas=document.createElement('canvas');canvas.width=96;canvas.height=96;
    const ctx=canvas.getContext('2d',{willReadFrequently:true});
    const records=[...samples.map(character=>({kind:'cjk',character})),
      {kind:'missing',character:'\u{10ffff}'},{kind:'missing',character:'\ufffd'}].map(sample=>{
      ctx.clearRect(0,0,96,96);ctx.font='48px '+family;ctx.textBaseline='top';
      ctx.fillStyle='#000';ctx.fillText(sample.character,8,8);
      const pixels=[...ctx.getImageData(0,0,96,96).data];
      return {...sample,pixels,inkPixels:pixels.filter((v,i)=>i%4===3&&v>0).length};
    });
    return {family,records};
  });
  const records=raster.records.map(({pixels,...item})=>({...item,
    signature:createHash('sha256').update(Buffer.from(pixels)).digest('hex')}));
  assertReadableGlyphs(records);
  return {fontFamily:raster.family,method:'REAL_BODY_FONT_CANVAS_GLYPHS_VS_MISSING_CONTROLS',
    representativeGlyphs:records,meaning:'CJK_GLYPH_PRESENCE_NOT_INDEPENDENT_SCREENSHOT_ACCEPTANCE'};
}
module.exports={verifyCjkReadability,assertReadableGlyphs};
