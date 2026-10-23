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
  const highlightStyles=document.createElement('style');
  highlightStyles.textContent='.exam-highlight{background:#ffe86f!important;color:#152037!important;font-weight:900;padding:0 2px;border-radius:3px}';
  document.head.append(highlightStyles);
  const storageKey='tvet-verified-'+activeYear+'-v1';
  const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const useful=value=>typeof value==='string'&&value.trim()!==''&&!/^(N\/?A|本題無金額計算)$/i.test(value.trim());
  /* Image-QA-only questions use the same one-question flow, never a giant
   * preview gallery and never answer buttons before full student release. */
  const viewStyle=document.createElement('style');
  viewStyle.textContent=[
    'body.verified-year-loading .control-row,body.verified-year-loading #studyView,body.verified-year-loading #reviewView,body.verified-year-loading #progressShell,body.verified-year-loading .bottom{display:none!important}',
    'body.qa-image-mode .control-row,body.qa-image-mode #studyView,body.qa-image-mode #reviewView,body.qa-image-mode #progressShell,body.qa-image-mode .bottom,body.qa-image-mode .review-head,body.qa-image-mode .nav-toggle{display:none!important}',
    '#verifiedImagePreview[hidden]{display:none!important}',
    '#verifiedImagePreview{max-width:900px;margin:0 auto 24px}',
    '#verifiedImagePreview .preview-toolbar{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px}',
    '#verifiedImagePreview .preview-toolbar select,#verifiedImagePreview .preview-toolbar button{min-height:44px;max-width:100%;min-width:0;padding:9px 12px;border:1px solid var(--line);border-radius:12px;background:var(--card);color:var(--text);font-weight:800}',
    '#verifiedImagePreview .preview-toolbar button{cursor:pointer;background:var(--blue-soft);color:var(--blue)}',
    '#verifiedImagePreview .preview-toolbar button:disabled{opacity:.45;cursor:default}',
    '#verifiedImagePreview .preview-position{font-size:13px;font-weight:800;color:var(--muted)}',
    '#previewQuestionCard{background:var(--question-bg);border-color:color-mix(in srgb,var(--blue) 32%,var(--line));padding:18px}',
    '#previewQuestionCard .source-figure{margin:12px 0 0}',
    '#previewQuestionCard .qmeta{margin-bottom:8px}',
    '#previewQuestionCard .preview-stage{color:var(--muted);font-size:13px;font-weight:750;margin:8px 0 0}',
    '#verifiedPreviewToggle[aria-pressed="true"]{box-shadow:inset 0 0 0 2px var(--blue)}',
    '@media(max-width:620px){#verifiedImagePreview .preview-toolbar select{flex:1 1 calc(50% - 8px)}#verifiedImagePreview .preview-toolbar button{flex:1 1 calc(50% - 8px)}#verifiedImagePreview .preview-position{width:100%;text-align:center}}'
  ].join('');
  document.head.append(viewStyle);
  document.body.classList.add('verified-year-loading');
  const showError=(message)=>{
    document.body.classList.remove('verified-year-loading');
    document.body.classList.add('qa-image-mode');
    let alert=document.getElementById('verifiedLoadError');
    if(!alert){
      alert=document.createElement('p');
      alert.id='verifiedLoadError';
      alert.setAttribute('role','alert');
      alert.style.cssText='padding:12px 3px;color:var(--text);font-weight:750';
      document.querySelector('main')?.prepend(alert);
    }
    alert.textContent=message;
  };

  async function showImagePreview(approvedIds=new Set(),openInitially=false){
    const response=await fetch('./data/approved/preview/'+activeYear+'.json',{cache:'no-store'});
    if(!response.ok)throw Error('原圖清單 HTTP '+response.status);
    const data=await response.json();
    if(data.year!==Number(activeYear)||!Array.isArray(data.questions)||
       data.imagePreviewCount!==data.questions.length)
      throw Error('原圖清單與年度或筆數不相符');
    const idPattern=new RegExp('^'+activeYear+'-(00-C|00-E|00-MB|09-1|09-2)-([0-9]{2})$');
    const subjects=(paper,n)=>{
      if(paper==='00-C')return '國文';
      if(paper==='00-E')return '英文';
      if(paper==='00-MB')return '數學 B';
      if(paper==='09-1')return n<=25?'商業概論':'數位科技';
      return n<=24?'會計學':'經濟學';
    };
    const seen=new Set(),available=[];
    for(const item of data.questions){
      const match=typeof item.canonicalId==='string'?idPattern.exec(item.canonicalId):null;
      if(!match||seen.has(item.canonicalId)||item.reviewStage!=='image_qa_pass_only'||
         item.year!==Number(activeYear)||item.questionNumber!==Number(match[2])||
         item.subject!==subjects(match[1],Number(match[2]))||
         item.image!=='data/approved/webp/'+activeYear+'/'+item.canonicalId+'.webp'||
         !/^[a-f0-9]{64}$/.test(item.imageSha256)||!Array.isArray(item.sharedImages)||
         Object.keys(item).some(k=>['answer','question','options','memory','teaching','independentSolve'].includes(k))||
         item.sharedImages.some(s=>
           typeof s.image!=='string'||!s.image.startsWith('data/approved/webp/'+activeYear+'/'+activeYear+'-'+match[1]+'-SHARED-')||
           !/SHARED-[0-9]{2}-[0-9]{2}[.]webp$/.test(s.image)||
           !/^[a-f0-9]{64}$/.test(s.sha256)))
        throw Error('原圖題號、科目、檔名或 QA 證據有誤');
      seen.add(item.canonicalId);
      if(!approvedIds.has(item.canonicalId))available.push(item);
    }
    if(!available.length){
      if(openInitially)showError(activeYear+' 年尚無可顯示的單題原圖或正式驗收題。');
      return;
    }
    const host=document.querySelector('main');
    const study=document.getElementById('studyView');
    if(!host||!study)throw Error('原有 V4 題目區不存在');
    document.getElementById('verifiedImagePreview')?.remove();
    const section=document.createElement('section');
    section.id='verifiedImagePreview';
    section.setAttribute('aria-label','逐題 WebP 原圖唯讀檢視');
    section.setAttribute('data-qa-preview','read-only');
    section.hidden=true;
    const toolbar=document.createElement('div');
    toolbar.className='preview-toolbar';
    const subjectSel=document.createElement('select');
    subjectSel.id='previewSubjectSel';
    subjectSel.setAttribute('aria-label','原圖科目');
    for(const name of ['全部科目',...new Set(available.map(q=>q.subject))]){
      const option=document.createElement('option');
      option.textContent=name;option.value=name;
      subjectSel.append(option);
    }
    const questionSel=document.createElement('select');
    questionSel.id='previewQuestionSel';
    questionSel.setAttribute('aria-label','原圖題號');
    const prev=document.createElement('button');
    prev.id='previewPrevBtn';prev.type='button';prev.textContent='← 上一題';
    const next=document.createElement('button');
    next.id='previewNextBtn';next.type='button';next.textContent='下一題 →';
    const position=document.createElement('span');
    position.className='preview-position';
    position.setAttribute('aria-live','polite');
    toolbar.append(subjectSel,questionSel,prev,next,position);
    const card=document.createElement('article');
    card.className='card';
    card.id='previewQuestionCard';
    section.append(toolbar,card);
    host.insertBefore(section,study);
    let rows=available,index=0,previewMode=false;
    const selectRows=()=>{
      rows=subjectSel.value==='全部科目'?available:available.filter(q=>q.subject===subjectSel.value);
      questionSel.replaceChildren();
      rows.forEach((q,i)=>{
        const option=document.createElement('option');
        option.value=String(i);
        option.textContent=q.subject+'｜第 '+q.questionNumber+' 題';
        questionSel.append(option);
      });
      index=0;
    };
    const image=(src,alt,qid)=>{
      const figure=document.createElement('figure');
      figure.className='source-figure';
      figure.setAttribute('data-single-question-webp','true');
      const img=document.createElement('img');
      img.src='./'+src;
      img.alt=alt;
      img.decoding='async';
      img.loading='eager';
      img.dataset.canonicalId=qid;
      const caption=document.createElement('figcaption');
      caption.textContent='本題原圖｜'+qid+'｜只通過圖片 QA，尚未核准作答';
      figure.append(img,caption);
      return figure;
    };
    const render=(scroll=false)=>{
      if(!rows.length)return;
      const q=rows[index];
      const meta=document.createElement('div');
      meta.className='qmeta';
      const text=document.createElement('span');
      text.textContent='第';
      const num=document.createElement('span');
      num.className='qnum';
      num.id='previewQuestionNumber';
      num.textContent=String(q.questionNumber).padStart(2,'0');
      const word=document.createElement('span');
      word.textContent='題';
      const subject=document.createElement('span');
      subject.className='pill';
      subject.textContent=q.subject;
      meta.append(text,num,word,subject);
      const stage=document.createElement('p');
      stage.className='preview-stage';
      stage.textContent='原題影像已核對｜答案與解說尚未核准（唯讀）';
      card.replaceChildren(meta,image(q.image,q.subject+' 第 '+q.questionNumber+' 題官方單題原圖',q.canonicalId));
      for(const s of q.sharedImages){
        const note=document.createElement('p');
        note.className='preview-stage';
        note.textContent='本題共用文章／圖表';
        card.append(note,image(s.image,'本題共用文章或圖表',q.canonicalId));
      }
      card.append(stage);
      questionSel.value=String(index);
      position.textContent=(index+1)+' / '+rows.length+' 題（原圖唯讀）';
      prev.disabled=index===0;
      next.disabled=index===rows.length-1;
      if(scroll)card.scrollIntoView({behavior:'smooth',block:'start'});
    };
    selectRows();
    render();
    const toggle=document.createElement('button');
    toggle.id='verifiedPreviewToggle';
    toggle.type='button';
    toggle.style.cssText='border:1px solid var(--line);border-radius:12px;padding:9px 12px;min-height:44px;background:var(--card);color:var(--text);font-size:14px;font-weight:800;cursor:pointer';
    toggle.textContent='待詳解原圖 '+available.length+' 題';
    toggle.setAttribute('aria-pressed','false');
    nav.append(toggle);
    const openPreview=()=>{
      previewMode=true;
      section.hidden=false;
      document.body.classList.remove('verified-year-loading');
      document.body.classList.add('qa-image-mode');
      toggle.setAttribute('aria-pressed','true');
      toggle.textContent=approvedIds.size?'返回正式作答':'原圖唯讀 · '+available.length+' 題';
      render();
    };
    const closePreview=()=>{
      if(!approvedIds.size)return;
      previewMode=false;
      section.hidden=true;
      document.body.classList.remove('qa-image-mode','verified-year-loading');
      toggle.setAttribute('aria-pressed','false');
      toggle.textContent='待詳解原圖 '+available.length+' 題';
      showStudy();
      renderAll();
    };
    toggle.onclick=()=>previewMode?closePreview():openPreview();
    subjectSel.onchange=()=>{selectRows();render(true)};
    questionSel.onchange=()=>{index=Number(questionSel.value);render(true)};
    prev.onclick=()=>{if(index>0){index--;render(true)}};
    next.onclick=()=>{if(index<rows.length-1){index++;render(true)}};
    if(openInitially)openPreview();
  }

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
      showImagePreview(new Set(),true).catch(e=>{
        console.error('唯讀原圖載入失敗',e);
        showError('原圖暫不可用：'+e.message);
      });
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
    document.body.classList.remove('verified-year-loading','qa-image-mode');
    showImagePreview(expectedIds).catch(e=>console.error('原圖唯讀模式暫不可用',e));
  }).catch(error=>{
    console.error('正式年度題庫載入失敗',error);
    showError('資料驗證或載入未通過，已暫停本年度正式作答：'+error.message);
  });
})();
