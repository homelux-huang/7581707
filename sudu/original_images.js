/* Original official WebP pages. Never OCR, crop by guess, or reveal answer sheets on load. */
const SUDU_IMAGES=(()=>{
 let original=null,answers=null,pending=null,dialog=null,returnFocus=null;
 const refs=new Map();
 function placeholder(q,answer=false){refs.set(q.id,q);return '<div class="sudu-original" data-source-images="'+esc(q.id)+'" data-image-role="'+(answer?'answer':'question')+'"><p class="small">正在載入'+(answer?'答案':'原卷')+'影像索引…</p></div>';}
 async function load(){
  if(!pending)pending=Promise.allSettled(['index.json','answers.json'].map(async file=>{const r=await fetch('./data/original/'+file);if(!r.ok)throw Error(String(r.status));const d=await r.json();if(!d.papers||typeof d.papers!=='object')throw Error('index');return d;})).then(r=>{original=r[0].status==='fulfilled'?r[0].value:{papers:{},failed:true};answers=r[1].status==='fulfilled'?r[1].value:{papers:{},failed:true};});
  return pending;
 }
 function validPage(p){return p&&/^data\/original\/[\d]{2,3}\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\.webp$/.test(p.src)&&Number.isInteger(p.page)&&p.page>0&&p.width>0&&p.height>0;}
 function figure(page,label){
  return '<figure class="sudu-original-page"><button type="button" class="sudu-image-open" data-image-src="'+esc(page.src)+'" data-image-label="'+esc(label)+'" aria-label="放大'+esc(label)+'"><img loading="lazy" decoding="async" src="./'+esc(page.src)+'" width="'+Number(page.width)+'" height="'+Number(page.height)+'" alt="'+esc(label)+'；點按可放大"></button><figcaption>'+esc(label)+' · '+Number(page.width)+'×'+Number(page.height)+' · '+Math.round(page.bytes/1024)+' KB</figcaption><p class="sudu-image-error" hidden role="status">影像載入失敗。請檢查網路後 <button type="button" data-image-retry>重試</button>。</p></figure>';
 }
 function content(q,answer){
  const index=answer?answers:original,key=String(q.year)+'/'+q.paper,entry=index?.papers?.[key];
  const pages=(entry?.pages||[]).filter(validPage);
  if(!pages.length)return '<p class="warning">'+(answer?'官方答案':'原卷')+' WebP '+(index?.failed?'索引載入失敗':'尚未收錄')+'；'+(answer?'本題答案仍待核對。':'此題原圖待補，不以缺字提示代替正式題幹。')+'</p><button type="button" class="btn light" data-index-retry>重新載入影像索引</button>';
  const label=(answer?'官方答案卷':'官方原卷')+'｜'+q.year+' 年 '+(paperText[q.paper]||q.paper);
  const source='<p class="small"><a href="'+esc(safeURL(entry.source))+'" target="_blank" rel="noopener">官方來源</a> · 原頁 WebP；無 OCR、無重畫。</p>';
  if(answer)return '<details class="sudu-answer-images"><summary>展開官方答案卷原頁（會看到同頁其他題答案）</summary>'+source+pages.map(p=>figure(p,label+' 第 '+p.page+' 頁')).join('')+'</details>';
  const mapping=entry.questions?.[q.id],anchor=pages.find(p=>p.page===mapping?.page)||pages[0];
  const other=pages.filter(p=>p!==anchor);
  return '<div class="sudu-original-heading"><b>原始試卷影像</b><span class="small">'+(Number.isInteger(q.number)?'原卷第 '+q.number+' 題；':'完整試卷；')+(mapping?.questionVerified?'頁碼已覆核':'頁碼定位待覆核')+'</span></div>'+figure(anchor,label+' 第 '+anchor.page+' 頁')+
  (other.length?'<details class="sudu-full-paper"><summary>查看完整原卷（'+pages.length+' 頁，含跨頁題組／共用圖表）</summary><p class="small">上方預覽只供對照；若題目跨頁或引用共用題組，請閱讀以下完整原頁。沒有推測裁切。</p>'+other.map(p=>figure(p,label+' 第 '+p.page+' 頁')).join('')+'</details>':'')+source;
 }
 async function mount(){
  await load();
  document.querySelectorAll('[data-source-images]').forEach(el=>{const q=refs.get(el.dataset.sourceImages);if(q)el.innerHTML=content(q,el.dataset.imageRole==='answer');});
  document.querySelectorAll('.sudu-original img').forEach(img=>{img.addEventListener('error',()=>{img.closest('figure').querySelector('.sudu-image-error').hidden=false;});});
 }
 function ensureDialog(){
  if(dialog)return dialog;
  dialog=document.createElement('dialog');dialog.id='sudu-image-dialog';dialog.setAttribute('aria-labelledby','sudu-image-dialog-title');
  dialog.innerHTML='<div class="sudu-image-dialog-bar"><strong id="sudu-image-dialog-title"></strong><button type="button" data-image-zoom>切換原尺寸</button><button type="button" data-image-close aria-label="關閉原卷放大">關閉 ✕</button></div><div class="sudu-image-dialog-body"><img alt=""></div>';
  document.body.append(dialog);dialog.querySelector('[data-image-close]').onclick=()=>dialog.close();dialog.querySelector('[data-image-zoom]').onclick=()=>dialog.classList.toggle('actual-size');
  dialog.addEventListener('close',()=>returnFocus?.isConnected&&returnFocus.focus({preventScroll:true}));dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});return dialog;
 }
 document.addEventListener('click',e=>{
  const open=e.target.closest('[data-image-src]');if(open){e.preventDefault();const d=ensureDialog();returnFocus=open;d.classList.remove('actual-size');d.querySelector('img').src='./'+open.dataset.imageSrc;d.querySelector('img').alt=open.dataset.imageLabel;d.querySelector('strong').textContent=open.dataset.imageLabel;d.showModal();d.querySelector('[data-image-close]').focus();}
  const retry=e.target.closest('[data-image-retry]');if(retry){const fig=retry.closest('figure'),img=fig.querySelector('img');fig.querySelector('.sudu-image-error').hidden=true;const old=img.src;img.removeAttribute('src');img.src=old;}
  if(e.target.closest('[data-index-retry]')){pending=null;mount();}
 });
 return {placeholder,mount};
})();
