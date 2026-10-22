/* A QA-gated 114/115 adapter for the EXISTING V4 practice UI.
 * Loads ONLY data/approved/{year}.json. Demo and its localStorage are unchanged.
 * The published artifact never embeds candidate/unverified OCR or official keys.
 */
(() => {
  'use strict';
  const relative = './v4-115-multisubject-review-demo.html';
  const args = new URLSearchParams(location.search);
  const activeYear = args.get('year');
  const nav = document.createElement('nav');
  nav.id='verifiedYearNav';
  nav.setAttribute('aria-label','正式題庫與進度');
  nav.style.cssText='max-width:980px;margin:0 auto 10px;padding:0 14px;display:flex;flex-wrap:wrap;gap:7px;align-items:center';
  const links=[
    ['./v4-115-multisubject-review-demo.html','35 題 UI Demo'],
    [relative+'?year=115','115 年正式驗收題庫'],
    [relative+'?year=114','114 年正式驗收題庫'],
    ['./question-bank-progress.html','題庫接入／部署進度']
  ];
  for(const [href,label] of links){
    const a=document.createElement('a');
    a.href=href;a.textContent=label;
    a.style.cssText='border:1px solid var(--line);border-radius:12px;padding:9px 12px;min-height:44px;display:inline-flex;align-items:center;text-decoration:none;font-weight:800;font-size:14px;color:var(--text);background:var(--card)';
    if((activeYear==='114'&&label.includes('114 年'))||(activeYear==='115'&&label.includes('115 年')))
      a.style.boxShadow='inset 0 0 0 2px #4675e8';
    nav.append(a);
  }
  const control=document.querySelector('.control-row');
  if(control)control.after(nav);
  if(!['114','115'].includes(activeYear)) return;
  const storageKey='tvet-verified-'+activeYear+'-v1';
  const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const useful=value=>typeof value==='string'&&value.trim()!==''&&!/^(N\/?A|本題無金額計算)$/i.test(value.trim());
  const status=(message)=>{
    const existing=document.getElementById('verifiedStatus');
    if(existing)existing.remove();
    const panel=document.createElement('section');
    panel.id='verifiedStatus';panel.className='card';
    panel.style.cssText='max-width:900px;margin:15px auto;line-height:1.7';
    const h=document.createElement('h2');h.textContent=activeYear+' 年正式題庫驗收';
    const p=document.createElement('p');p.textContent=message;
    const a=document.createElement('a');a.textContent='檢視年度驗收與部署進度';a.href='./question-bank-progress.html';
    a.style.cssText='display:inline-flex;min-height:44px;align-items:center;color:var(--blue);font-weight:900';
    panel.append(h,p,a);
    document.querySelector('main')?.prepend(panel);
    return panel;
  };
  const empty=(message)=>{
    status(message);
    ['studyView','reviewView','progressShell','prevBtn','nextBtn'].forEach(id=>{
      const el=document.getElementById(id);if(el)el.style.display='none';
    });
    const bottom=document.querySelector('.bottom');if(bottom)bottom.style.display='none';
    const select=document.getElementById('subjectSel');if(select)select.disabled=true;
    const summary=document.getElementById('summary');
    if(summary)summary.innerHTML='<b>'+activeYear+' 年：正式可用 0 題</b>';
  };
  function htmlWithActualHighlights(value,terms) {
    const raw=String(value??'');
    const highlights=(Array.isArray(terms)?terms:[]).filter(t=>typeof t==='string'&&t.trim()&&raw.includes(t));
    if(!highlights.length)return escapeHtml(raw);
    const unique=[...new Set(highlights)].sort((a,b)=>b.length-a.length);
    const chunks=[],indexes=[];
    for(const term of unique){
      let p=0,pos=raw.indexOf(term,p);
      while(pos>=0){indexes.push({from:pos,to:pos+term.length});p=pos+term.length;pos=raw.indexOf(term,p)}
    }
    indexes.sort((a,b)=>a.from-b.from||b.to-a.to);
    let at=0;
    for(const item of indexes){
      if(item.from<at)continue;
      chunks.push(escapeHtml(raw.slice(at,item.from)),'<mark class="exam-highlight">',escapeHtml(raw.slice(item.from,item.to)),'</mark>');
      at=item.to;
    }
    chunks.push(escapeHtml(raw.slice(at)));
    return chunks.join('');
  }
  fetch('./data/approved/'+activeYear+'.json',{cache:'no-store'}).then(async r=>{
    if(!r.ok)throw Error('資料未發布（HTTP '+r.status+'）');
    return r.json();
  }).then(data=>{
    if(Number(data.year)!==Number(activeYear)||!Array.isArray(data.questions)||data.approvedCount!==data.questions.length)
      throw Error('題庫驗收清單格式不符');
    const verified=data.questions;
    if(!verified.length) {
      empty('目前沒有通過「單題圖片、OCR、最終官方答案、獨立解題、四選項教學及計算式」全部驗收的題目。候選題不會提前供學生作答。');
      return;
    }
    const keyset=new Set();
    const expectedIds=new Set();
    for(const q of verified){
      const id=q.canonicalId;
      if(q.year!==Number(activeYear)||typeof id!=='string'||expectedIds.has(id)||q.image!==('data/approved/webp/'+activeYear+'/'+id+'.webp')||
         !Array.isArray(q.options)||q.options.length!==4||!q.options.every(useful)||!/[ABCD]/.test(q.answer)||!q.optionExplanations ||
         ['A','B','C','D'].some(k=>!useful(q.optionExplanations[k]?.teacher)||!useful(q.optionExplanations[k]?.elementary)))
        throw Error('題庫驗收欄位異常：'+String(id));
      expectedIds.add(id);keyset.add(q.subject);
    }
    const originalSave=save;
    const originalMove=move;
    const originalProgress=renderProgress;
    const originalDetail=renderOptionDetail;
    const originalSource=sourceText;
    const originalSubjectEntries=subjectEntries;
    const stored=(()=>{try{return JSON.parse(localStorage.getItem(storageKey)||'null')}catch{return null}})();
    state.records=stored&&stored.records&&typeof stored.records==='object'?stored.records:{};
    state.rounds=stored&&stored.rounds&&typeof stored.rounds==='object'?stored.rounds:{};
    state.ui=stored&&stored.ui||{};
    // Separate formal-year history key: never overwrite old 35-demo history.
    save=function(){
      state.ui={subject:currentSubject,index:currentIndex};
      try{localStorage.setItem(storageKey,JSON.stringify({records:state.records,rounds:state.rounds,ui:state.ui,theme:state.theme}))}
      catch(e){console.warn('正式年度學習紀錄儲存失敗',e)}
    };
    QUESTIONS.splice(0,QUESTIONS.length,...verified);
    SUBJECTS.splice(0,SUBJECTS.length,...keyset);
    currentSubject=SUBJECTS.includes(state.ui.subject)?state.ui.subject:SUBJECTS[0];
    currentIndex=Math.max(0,Math.min((listFor(currentSubject).length||1)-1,Number(state.ui.index)||0));
    sourceText=function(q){return q.sourceText||originalSource(q)};
    subjectEntries=function(q){
      if(q.year!==Number(activeYear))return originalSubjectEntries(q);
      const parts=[
        ['高職老師解題',q.teacherSummary],['國小學生白話',q.elementarySummary],
        ...Object.entries(q.extra||{})
      ].filter(x=>useful(x[1]));
      const calc=q.examCalculation;
      if(calc&&calc.hasExamCalculation===true&&Array.isArray(calc.lines)&&calc.lines.length)
        parts.push(['考題計算式',calc.lines.join('\n')]);
      return parts;
    };
    renderOptionDetail=function(q,L){
      if(q.year!==Number(activeYear))return originalDetail(q,L);
      const detail=q.optionExplanations?.[L]||{};
      const color=L===q.answer?'is-correct':'is-wrong';
      const keywords=q.highlights||[];
      const header=L===q.answer?'✓ 正確解答':'× 選項檢查';
      const rows=[
        ['高職生理解',detail.teacher],
        ['國小學生也聽得懂',detail.elementary],
        ['此選項正確／錯誤原因',detail.reason]
      ].filter(x=>useful(x[1]));
      let html='<div class="option-detail '+color+'"><b>'+header+'</b>'+
        rows.map(x=>'<p><b>'+escapeHtml(x[0])+'：</b>'+htmlWithActualHighlights(x[1],keywords)+'</p>').join('');
      if(L===q.answer){
        const extra=subjectEntries(q);
        if(extra.length)html+='<div class="option-detail-grid">'+extra.map(x=>
          '<span><em>'+escapeHtml(x[0])+'</em>'+formatStudyValue(q,x[0],x[1])+'</span>').join('')+'</div>';
      }
      return html+'</div>';
    };
    renderProgress=function(){
      originalProgress();
      const rows=list(), done=rows.filter(q=>record(q).status).length;
      $('progressLabel').innerHTML='已答 '+done+'/'+rows.length+' 題 <span class="round">第 '+(state.rounds[currentSubject]||1)+' 輪</span>';
      $('summary').innerHTML='正式題庫（逐題驗收）<b>'+activeYear+' 年 '+escapeHtml(currentSubject)+'｜'+rows.length+' 題</b>';
    };
    move=function(delta){
      currentIndex=Math.max(0,Math.min(listFor(currentSubject).length-1,currentIndex+delta));
      showStudy();renderAll();window.scrollTo({top:0,behavior:'smooth'});
    };
    document.title='速讀｜'+activeYear+' 正式題庫｜教學解說';
    renderSelectors();showStudy();renderAll();
    status('已通過全部驗收並開放 '+verified.length+' 題。老師會先說高職的解法，再用國小學生聽得懂的白話說明；需要計算的題目會列完整步驟，非計算題自動隱藏。');
    const statusCard=document.getElementById('verifiedStatus');
    if(statusCard)statusCard.style.marginBottom='14px';
  }).catch(error=>{
    console.error('正式年度題庫載入失敗',error);
    empty('資料驗證或載入未通過，已暫停本年度正式作答：'+error.message);
  });
})();
