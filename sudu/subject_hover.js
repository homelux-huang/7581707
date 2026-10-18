/* Curated cards; unknown values remain N/A. No OCR or automatic audio. */
const SUDU_HOVER=(()=>{
 let data={english:{},chinese:{}},loaded=false,promise=null,card=null,trigger=null,closeTimer=null,suppress=false;
 const na=value=>value===null||value===undefined||value===''?'N/A':String(value);
 function field(title,value){return '<div class="sudu-hover-field"><dt>'+esc(title)+'</dt><dd>'+esc(na(value))+'</dd></div>';}
 function groups(value){return ['低','中','高'].map((label,i)=>label+'：'+(value?.[['low','medium','high'][i]]?.join('、')||'N/A')).join('\n');}
 function ensure(){
  if(card)return card;card=document.createElement('aside');card.id='sudu-hover-card';card.hidden=true;card.setAttribute('role','dialog');card.setAttribute('aria-label','學習卡片');
  document.body.append(card);
  card.addEventListener('pointerenter',()=>clearTimeout(closeTimer));card.addEventListener('pointerleave',e=>{if(!trigger?.contains(e.relatedTarget))scheduleClose();});
  card.addEventListener('focusin',()=>clearTimeout(closeTimer));card.addEventListener('focusout',e=>{if(!card.contains(e.relatedTarget)&&e.relatedTarget!==trigger)close();});
  return card;
 }
 function place(){
  if(!trigger||!card||card.hidden)return;
  const r=trigger.getBoundingClientRect(),gap=8,margin=10,vw=window.innerWidth,vh=window.innerHeight;
  const preferred=Math.min(380,vw-margin*2),right=vw-r.right-gap-margin,left=r.left-gap-margin;
  let width=preferred,top,leftEdge,limit;
  // A tall card must never move over the word that opened it while the pointer
  // is completing a click. Prefer a side; on narrow screens scroll above/below.
  if(Math.max(right,left)>=260){
   const onRight=right>=left;width=Math.min(preferred,onRight?right:left);
   limit=vh-margin*2;leftEdge=onRight?r.right+gap:r.left-gap-width;
   card.style.width=width+'px';card.style.maxHeight=limit+'px';
   top=Math.max(margin,Math.min(r.top,vh-Math.min(card.scrollHeight,limit)-margin));
  }else{
   const below=Math.max(0,vh-r.bottom-gap-margin),above=Math.max(0,r.top-gap-margin),useBelow=below>=above;
   limit=Math.max(64,useBelow?below:above);leftEdge=Math.max(margin,Math.min(r.left,vw-width-margin));
   card.style.width=width+'px';card.style.maxHeight=limit+'px';
   const height=Math.min(card.scrollHeight,limit);top=useBelow?r.bottom+gap:r.top-gap-height;
  }
  card.style.left=leftEdge+'px';card.style.top=top+'px';
 }
 function open(button,focus=false){
  if(suppress)return;clearTimeout(closeTimer);if(trigger&&trigger!==button)trigger.setAttribute('aria-expanded','false');trigger=button;const box=ensure(),q=questionById(button.dataset.hoverQid),term=button.dataset.hoverTerm||q?.topic||q?.subject||'題目';if(!q)return;
  const language=q.subject==='英文'?'english':q.subject==='國文'?'chinese':null;
  const item=language?data[language]?.[term.toLowerCase()]||data[language]?.[term]:null;
  let body='';
  if(language==='english')body=field('中文翻譯（已核對語境）',item?.translation)+field('IPA／發音',item?.ipa)+field('同義字（本站教學難度）',groups(item?.synonyms))+field('相關字（本站教學難度）',groups(item?.related))+field('反義字（本站教學難度）',groups(item?.antonyms))+field('新聞原句／來源／日期',item?.news?.quote?item.news.quote+'\n'+item.news.date+'\n'+item.news.explanation:'N/A')+field('例句（自編）',item?.example);
  else if(language==='chinese')body=field('讀音',item?.pronunciation)+field('本題語境釋義',item?.meaning)+field('同義字／詞',item?.synonyms?.join('、'))+field('出處',item?.origin)+field('相關字詞（本站教學難度）',groups(item?.related))+field('反義字詞（本站教學難度）',groups(item?.antonyms))+field('例句（自編）',item?.example);
  else{
   const trusted=!q.official||q.teachingVerified===true;
   const labels=q.subject.includes('數學')?['公式','用法','簡易範例','日常用法']:q.subject==='會計學'?['法規（適用年度）','會計科目','會計原理','算法','簡易範例','日常時事']:q.subject==='經濟學'||q.subject==='商業概論'?['原理','法規（適用年度）','算法','簡易範例','日常時事']:['運作方式','工作原理','算法','簡易範例','日常時事'];
   body=labels.map(label=>field(label,/原理|用法|工作原理/.test(label)&&trusted?(q.principle||q.explanation):/公式|算法/.test(label)&&trusted?q.steps:label==='簡易範例'&&trusted?q.practice?.question:null)).join('');
  }
  const sources=item?.sources||[];
  box.innerHTML='<div class="sudu-hover-top"><h2>'+esc(term)+'</h2><button type="button" data-hover-close aria-label="關閉學習卡片">✕</button></div><p class="small">'+(item?'來源已查閱；例句與難度分組為本站教學標記。':language?'此詞尚未有可靠語境資料；缺漏欄位保留 N/A。':'題目級觀念卡；不計為逐題教師詳解核實。')+'</p><dl>'+body+'</dl>'+
  (language?'<p class="small">低：日常常用；中：一般閱讀；高：抽象或專門用語。本分組不是 IELTS／TOEFL 官方級別。</p>':'')+
  sources.map(s=>'<p class="small"><a href="'+esc(safeURL(s.url))+'" target="_blank" rel="noopener">'+esc(s.title)+'</a> · 查閱 '+esc(s.checkedAt||'N/A')+'</p>').join('')+
  (language==='english'?'<button type="button" class="btn light" data-hover-speak>點按播放裝置語音</button><p class="small">裝置合成語音；並非辭典原音。未查得 IPA 時仍顯示 N/A。</p>':'');
  box.hidden=false;button.setAttribute('aria-expanded','true');place();
  box.querySelector('[data-hover-close]').onclick=()=>close(true);
  box.querySelector('[data-hover-speak]')?.addEventListener('click',()=>{if(!('speechSynthesis' in window)){alert('此裝置無語音功能。');return;}const audio=new SpeechSynthesisUtterance(term);audio.lang='en-US';speechSynthesis.cancel();speechSynthesis.speak(audio);});
  if(focus)box.querySelector('[data-hover-close]').focus({preventScroll:true});
 }
 function close(focus=false){clearTimeout(closeTimer);if(card)card.hidden=true;if(trigger)trigger.setAttribute('aria-expanded','false');if(focus&&trigger?.isConnected){suppress=true;trigger.focus({preventScroll:true});suppress=false;}}
 function scheduleClose(){clearTimeout(closeTimer);closeTimer=setTimeout(()=>{if(card?.contains(document.activeElement))return;close();},180);}
 function button(term,q){const b=document.createElement('button');b.type='button';b.className='sudu-hover-term';b.dataset.hoverQid=q.id;b.dataset.hoverTerm=term;b.textContent=term;b.setAttribute('aria-label',term+'：開啟學習卡片');b.setAttribute('aria-haspopup','dialog');b.setAttribute('aria-expanded','false');b.addEventListener('pointerenter',e=>{if(e.pointerType!=='touch')open(b);});b.addEventListener('pointerleave',e=>{if(!card?.contains(e.relatedTarget))scheduleClose();});b.addEventListener('focus',()=>open(b));b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();open(b,true);});b.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();close(true);}});return b;}
 function tokenize(el,q){
  if(el.dataset.hoverReady)return;el.dataset.hoverReady='true';const text=el.textContent;el.replaceChildren();
  let segments=[];
  if(q.subject==='英文')segments=text.match(/[A-Za-z]+(?:['’][A-Za-z]+)*|[^A-Za-z]+/g)||[];
  else if(typeof Intl.Segmenter==='function')segments=[...new Intl.Segmenter('zh-TW',{granularity:'word'}).segment(text)].map(s=>s.segment);
  else segments=text.match(/[\u3400-\u9fff]+|[^\u3400-\u9fff]+/g)||[];
  // Keep known idioms intact even if the platform segmenter splits them.
  if(q.subject==='國文'){
   const terms=Object.keys(data.chinese).sort((a,b)=>b.length-a.length);let i=0;segments=[];
   const segmenter=typeof Intl.Segmenter==='function'?new Intl.Segmenter('zh-TW',{granularity:'word'}):null;
   while(i<text.length){const known=terms.find(t=>text.startsWith(t,i));if(known){segments.push(known);i+=known.length;}else{const part=(segmenter?[...segmenter.segment(text.slice(i))][0]?.segment:null)||text[i];segments.push(part);i+=part.length;}}
  }
  for(const part of segments)el.append(/[A-Za-z\u3400-\u9fff]/.test(part)?button(part,q):document.createTextNode(part));
 }
 async function load(){if(!promise)promise=fetch('./data/hover-cards.json').then(r=>{if(!r.ok)throw Error();return r.json();}).then(d=>{data=d;loaded=true;}).catch(()=>{loaded=true;});return promise;}
 async function mount(){
  close();await load();
  document.querySelectorAll('[data-hover-text]').forEach(el=>{const q=questionById(el.dataset.hoverText);if(q&&['英文','國文'].includes(q.subject)&&!isImageQuestion(q))tokenize(el,q);});
  document.querySelectorAll('[data-question-hover]').forEach(el=>{const q=questionById(el.dataset.questionHover);if(!q)return;if(!['英文','國文'].includes(q.subject)||isImageQuestion(q)){const b=button(q.topic||q.subject+'題目級卡片',q);b.classList.add('sudu-question-card-trigger');b.textContent=isImageQuestion(q)?'題目級學習卡片（原圖無逐字定位）':'查看本題觀念卡';el.replaceChildren(b);}});
 }
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&card&&!card.hidden){e.preventDefault();close(true);}});
 document.addEventListener('click',e=>{if(card&&!card.contains(e.target)&&!e.target.closest('.sudu-hover-term'))close();});
 window.addEventListener('resize',place,{passive:true});window.addEventListener('scroll',()=>{if(card&&!card.hidden)place();},{passive:true});
 return {mount};
})();
