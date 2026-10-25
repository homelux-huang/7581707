'use strict';
// Resolver regression tests. Temporary copies never certify a lesson or release.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {resolveOriginal,inlineBytes,sha}=require('./sudu_role_d_image_source.cjs');
const root=process.cwd();
const html=fs.readFileSync(path.join(root,'sudu/v4-115-multisubject-review-demo.html'),'utf8');
const demo=JSON.parse(html.match(/<script id="demoData" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const inline=demo.questions.find(q=>q.image.startsWith('data:'));
const bytes=inlineBytes(inline.image);
const write=(r,p,v)=>{const f=path.join(r,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,v)};
function fixture(run){
  const r=fs.mkdtempSync(path.join(os.tmpdir(),'sudu-image-resolver-'));
  try{
    const output='sudu/questions/115/chinese/q01.webp',source='sudu/data/original/test.webp';
    const c={output,source,box:[0,0,20,10],subject:'國文',question:1};
    const m={output,source,crop:c.box,subject:c.subject,question:1,ocrPerformed:false,sha256:sha(bytes)};
    write(r,source,bytes);write(r,'_site/'+output,bytes);
    write(r,'sudu/demo-question-crops.json',JSON.stringify({crops:[c]}));
    write(r,'_site/sudu/questions/115/crop-manifest.json',JSON.stringify({items:[m]}));
    run(r,m,{image:'questions/115/chinese/q01.webp',subject:'國文',id:1});
  }finally{
    assert.equal(path.dirname(path.resolve(r)),path.resolve(os.tmpdir()),'temporary cleanup boundary');
    assert(path.basename(r).startsWith('sudu-image-resolver-'),'temporary cleanup prefix');
    fs.rmSync(r,{recursive:true,force:true});
  }
}
test('all 35 actual Demo references resolve from exact original bytes after public build',()=>{
  const counts={};
  for(const q of demo.questions){
    const result=resolveOriginal(root,q);
    assert.equal(result.sha256,sha(result.bytes));
    counts[result.kind]=(counts[result.kind]||0)+1;
  }
  assert.deepEqual(counts,{'existing-official-pixel-crop':30,'original-inline-webp':5});
});
test('inline original is hashed from decoded WebP bytes',()=>{
  assert.equal(resolveOriginal(root,{image:inline.image,sha256:sha(bytes)}).sha256,sha(bytes));
});
test('wrong inline hash, unsupported data media and malformed base64 fail closed',()=>{
  assert.throws(()=>resolveOriginal(root,{image:inline.image,sha256:'0'.repeat(64)}),/SHA mismatch/);
  assert.throws(()=>inlineBytes(inline.image.replace('image/webp','image/png')),/supported/);
  assert.throws(()=>inlineBytes('data:image/webp;base64,%%'),/supported/);
  assert.throws(()=>inlineBytes('data:image/webp;base64,YQ=='),/header/);
});
test('generated path requires original crop configuration, manifest and original page',()=>fixture((r,m,q)=>{
  assert.equal(resolveOriginal(r,q).sha256,m.sha256);
  fs.unlinkSync(path.join(r,m.source));
  assert.throws(()=>resolveOriginal(r,q),/official original page missing/);
}));
test('changed manifest hash, crop bounds and question association are rejected',()=>fixture((r,m,q)=>{
  const manifest='_site/sudu/questions/115/crop-manifest.json';
  write(r,manifest,JSON.stringify({items:[{...m,sha256:'0'.repeat(64)}]}));
  assert.throws(()=>resolveOriginal(r,q),/manifest SHA/);
  write(r,manifest,JSON.stringify({items:[{...m,crop:[0,0,21,10]}]}));
  assert.throws(()=>resolveOriginal(r,q),/crop bounds/);
  write(r,manifest,JSON.stringify({items:[m]}));
  assert.throws(()=>resolveOriginal(r,{...q,id:2}),/question mismatch/);
}));
test('source and built bytes must remain identical',()=>fixture((r,m,q)=>{
  write(r,'sudu/direct.webp',bytes);write(r,'_site/sudu/direct.webp',Buffer.from('corrupt'));
  assert.throws(()=>resolveOriginal(r,{image:'direct.webp'}),/differs from source/);
}));
test('missing assets, escape paths and off-origin references cannot be substituted',()=>{
  for(const image of ['../secret.webp','/secret.webp','https://example.org/a.webp','a%2fb.webp','a\\b.webp'])
    assert.throws(()=>resolveOriginal(root,{image}),/unsafe/);
  assert.throws(()=>resolveOriginal(root,{image:'missing.webp'}),/missing actual original/);
});
