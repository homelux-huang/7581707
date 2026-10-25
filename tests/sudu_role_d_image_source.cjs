'use strict';
// Resolve existing image bytes; never generate, replace or waive an image.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {createHash}=require('node:crypto');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
function webp(bytes,label='image'){
  assert(bytes.length>=12,label+' has no WebP header');
  assert.equal(bytes.toString('ascii',0,4),'RIFF',label+' RIFF signature');
  assert.equal(bytes.toString('ascii',8,12),'WEBP',label+' WebP signature');
  assert.equal(bytes.readUInt32LE(4)+8,bytes.length,label+' truncated RIFF length');
  return bytes;
}
function inlineBytes(image){
  const match=/^data:image\/webp;base64,([A-Za-z0-9+/]+={0,2})$/.exec(image);
  assert(match,'only an original base64 WebP data URI is supported');
  const bytes=Buffer.from(match[1],'base64');
  assert.equal(bytes.toString('base64'),match[1],'noncanonical base64 WebP');
  return webp(bytes,'inline original');
}
function resolveOriginal(root,item){
  assert.equal(typeof item.image,'string','original image reference required');
  let bytes,kind;
  if(item.image.startsWith('data:')){
    bytes=inlineBytes(item.image);kind='original-inline-webp';
  }else{
    assert(!/[:\\?#%]/.test(item.image)&&!item.image.startsWith('/')&&
      !item.image.split('/').some(x=>x==='..'||x==='.'||!x),'unsafe original image path');
    const relative='sudu/'+item.image;
    const source=path.join(root,relative),built=path.join(root,'_site',relative);
    if(fs.existsSync(source)){
      assert(!fs.lstatSync(source).isSymbolicLink(),'source image must not be a symlink');
      bytes=webp(fs.readFileSync(source),item.image);kind='original-source-file';
      if(fs.existsSync(built))assert.equal(sha(fs.readFileSync(built)),sha(bytes),
        'built original differs from source bytes');
    }else{
      assert(relative.startsWith('sudu/questions/115/'),'missing actual original image: '+item.image);
      const config=JSON.parse(fs.readFileSync(path.join(root,'sudu/demo-question-crops.json'),'utf8'));
      const manifest=JSON.parse(fs.readFileSync(path.join(root,'_site/sudu/questions/115/crop-manifest.json'),'utf8'));
      const configs=config.crops.filter(x=>x.output===relative);
      const entries=manifest.items.filter(x=>x.output===relative);
      assert.equal(configs.length,1,'missing/duplicate original crop configuration');
      assert.equal(entries.length,1,'missing/duplicate built original crop');
      const c=configs[0],m=entries[0];
      assert.equal(m.source,c.source,'crop source changed');
      assert.deepEqual(m.crop,c.box,'crop bounds changed');
      assert.equal(m.ocrPerformed,false,'original crop must not be OCR-generated');
      if(item.subject)assert.equal(m.subject,item.subject,'crop subject mismatch');
      if(item.id!==undefined)assert.equal(m.question,item.id,'crop question mismatch');
      assert(!path.isAbsolute(c.source)&&!c.source.split(/[\\/]/).includes('..'), 'unsafe crop source');
      assert(fs.existsSync(path.join(root,c.source)),'official original page missing');
      webp(fs.readFileSync(path.join(root,c.source)),'official original page');
      assert(fs.existsSync(built),'built original crop missing');
      bytes=webp(fs.readFileSync(built),item.image);
      assert.equal(sha(bytes),m.sha256,'built crop does not match original manifest SHA');
      kind='existing-official-pixel-crop';
    }
  }
  const digest=sha(bytes);
  if(item.sha256)assert.equal(digest,item.sha256,'original image supplied SHA mismatch');
  return {bytes,sha256:digest,kind};
}
module.exports={resolveOriginal,inlineBytes,webp,sha};
