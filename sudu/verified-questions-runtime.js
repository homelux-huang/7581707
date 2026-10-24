/* A QA-gated 114/115 adapter for the EXISTING V4 practice UI.
 * Loads ONLY data/approved/{year}.json. Demo and its localStorage are unchanged.
 * The published artifact never embeds candidate/unverified OCR or official keys.
 */
(() => {
  'use strict';
  const relative='./v4-115-multisubject-review-demo.html';
  const args=new URLSearchParams(location.search);
  const activeYear=args.get('year');
  const imageModeRequested=args.get('view')==='images';
  // Keep navigation within the EXISTING year selector. Never add the four
  // large Demo/year/progress link buttons to the question reading area.
  const yearSelect=document.getElementById('yearSel');
  if(yearSelect){
    yearSelect.replaceChildren();
    for(const [value,label] of [['demo','35 題 Demo'],['115','115 年'],['114','114 年']]){
      const option=document.createElement('option');
      option.value=value;option.textContent=label;yearSelect.append(option);
    }
    yearSelect.value=['114','115'].includes(activeYear)?activeYear:'demo';
    yearSelect.onchange=()=>{
      location.href=yearSelect.value==='demo'?relative:relative+'?year='+yearSelect.value;
    };
  }
  if(!['114','115'].includes(activeYear))return;
  const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const useful=value=>typeof value==='string'&&value.trim()!==''&&!/^(N\/?A|本題無金額計算)$/i.test(value.trim());
  const storageKey='tvet-verified-'+activeYear+'-v1';
  const highlightStyles=document.createElement('style');
  highlightStyles.textContent='.exam-highlight{background:#ffe86f!important;color:#152037!important;font-weight:900;padding:0 2px;border-radius:3px}';
  document.head.append(highlightStyles);
  const viewStyles=document.createElement('style');
  viewStyles.textContent=[
    'body.verified-year-loading #studyView,body.verified-year-loading #reviewView,body.verified-year-loading #progressShell,body.verified-year-loading .bottom{display:none!important}',
    'body.qa-image-mode #answerCard,body.qa-image-mode #guideCard,body.qa-image-mode #answerScrollSpace,body.qa-image-mode .review-head,body.qa-image-mode #readingShortcuts{display:none!important}',
    'body.qa-image-mode.study-mode #studyView{display:block!important}',
    'body.qa-image-mode .side-arrow{bottom:24px}',
    'body.qa-image-mode #resetBtn,body.qa-image-mode #continueBtn{display:none!important}',
    'body.qa-image-mode #questionCard .source-figure{margin:12px 0 4px}',
    'body.qa-image-mode #questionCard .source-figure img{max-width:100%;height:auto}',
    'body.qa-image-mode #questionCard .qa-caption{margin:8px 0 0;font-size:13px;color:var(--muted);font-weight:750}',
    'body.qa-error-mode #studyView,body.qa-error-mode #reviewView,body.qa-error-mode #progressShell,body.qa-error-mode .bottom,body.qa-error-mode #prevBtn,body.qa-error-mode #nextBtn,body.qa-error-mode #navHandle,body.qa-error-mode #readingShortcuts{display:none!important}'
  ].join('');
  document.head.append(viewStyles);
  document.body.classList.add('verified-year-loading');

  const showError=(message)=>{
    document.body.classList.remove('verified-year-loading','qa-image-mode');
    document.body.classList.add('qa-error-mode');
    let p=document.getElementById('verifiedLoadError');
    if(!p){
      p=document.createElement('p');p.id='verifiedLoadError';
      p.setAttribute('role','alert');
      p.style.cssText='margin:8px 0 16px;color:var(--text);font-weight:750';
      document.querySelector('main')?.prepend(p);
    }
    p.textContent=message;
  };
  const subjectFor=(paper,n)=>{
    if(paper==='00-C')return '國文';
    if(paper==='00-E')return '英文';
    if(paper==='00-MB')return '數學 B';
    if(paper==='09-1')return n<=25?'商業概論':'數位科技';
    if(paper==='09-2')return n<=24?'會計學':'經濟學';
    return null;
  };
  const parsedIdentity=q=>{
    if(typeof q.canonicalId!=='string')return null;
    const m=/^(114|115)-(00-C|00-E|00-MB|09-1|09-2)-([0-9]{2})$/.exec(q.canonicalId);
    if(!m||m[1]!==activeYear||q.year!==Number(activeYear))return null;
    const n=Number(m[3]);
    if(n<1||q.subject!==subjectFor(m[2],n))return null;
    return {n,paper:m[2],id:q.canonicalId};
  };
  const imagePath=id=>'data/approved/webp/'+activeYear+'/'+id+'.webp';
  const shaValid=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);

  // verifiedSingleQuestionWebp: only the SAME canonical question ID may appear
  // immediately below its own question header; never a whole paper or another
  // question's WebP. Source visual QA and asset hashes remain authoritative.
  function verifiedSingleQuestionWebp(q){
    if(q.image!==imagePath(q.canonicalId)||!shaValid(q.imageSha256))
      throw Error('單題 WebP 題號或 SHA 不符：'+q.canonicalId);
    const figure=document.createElement('figure');
    figure.className='source-figure';
    figure.setAttribute('data-single-question-webp','true');
    const img=document.createElement('img');
    img.src='./'+q.image;
    img.alt=q.subject+'第 '+q.questionNumber+' 題，官方原始單題 WebP';
    img.dataset.canonicalId=q.canonicalId;
    img.dataset.sha256=q.imageSha256;
    img.decoding='async';
    img.loading='eager';
    const caption=document.createElement('figcaption');
    caption.textContent='本題原圖｜第 '+q.questionNumber+' 題';
    figure.append(img,caption);
    return figure;
  }
  async function showImageOnlyMode(){
    const response=await fetch('./data/approved/preview/'+activeYear+'.json',{cache:'no-store'});
    if(!response.ok)throw Error('原圖清單 HTTP '+response.status);
    const payload=await response.json();
    if(payload.year!==Number(activeYear)||!Array.isArray(payload.questions)||
       payload.imagePreviewCount!==payload.questions.length)
      throw Error('原圖題庫年度或筆數有誤');
    const seen=new Set();
    const items=payload.questions;
    for(const q of items){
      const id=parsedIdentity(q);
      if(!id||seen.has(id.id)||q.reviewStage!=='image_qa_pass_only'||
         q.questionNumber!==id.n||q.image!==imagePath(id.id)||
         !shaValid(q.imageSha256)||!Array.isArray(q.sharedImages)||
         ['answer','question','options','teaching','memory','independentSolve'].some(k=>Object.hasOwn(q,k))||
         q.sharedImages.some(s=>typeof s.image!=='string'||
           !s.image.startsWith('data/approved/webp/'+activeYear+'/'+activeYear+'-'+id.paper+'-SHARED-')||
           !/SHARED-[0-9]{2}-[0-9]{2}[.]webp$/.test(s.image)||!shaValid(s.sha256)))
        throw Error('題號、科目、WebP 來源或影像 QA 有誤');
      seen.add(id.id);
    }
    if(!items.length)throw Error(activeYear+' 年尚無通過影像 QA 的單題原圖');
    // Keep the existing V4 question area, and clear the demo records from the
    // active quiz model so image-only questions cannot be accidentally graded.
    QUESTIONS.splice(0,QUESTIONS.length);
    SUBJECTS.splice(0,SUBJECTS.length);
    document.getElementById('answerCard').replaceChildren();
    document.getElementById('guideCard').replaceChildren();
    document.getElementById('reviewSubject').innerHTML='<option value="ALL">全部科目</option>';
    const subjects=['全部科目',...new Set(items.map(q=>q.subject))];
    const filter=document.getElementById('subjectSel');
    filter.replaceChildren();
    for(const s of subjects){
      const option=document.createElement('option');
      option.value=s;option.textContent=s;filter.append(option);
    }
    let rows=items,index=0;
    const card=document.getElementById('questionCard');
    const summary=document.getElementById('summary');
    const render=(scroll=false)=>{
      const q=rows[index];
      if(!q)return;
      card.replaceChildren();
      card.dataset.canonicalId=q.canonicalId;
      card.setAttribute('data-qa-preview','read-only');
      const meta=document.createElement('div');
      meta.className='qmeta';
      const prefix=document.createElement('span');
      prefix.textContent='第';
      const number=document.createElement('span');
      number.className='qnum';
      number.textContent=String(q.questionNumber).padStart(2,'0');
      const suffix=document.createElement('span');
      suffix.textContent='題';
      const subj=document.createElement('span');
      subj.className='pill';subj.textContent=q.subject;
      meta.append(prefix,number,suffix,subj);
      card.append(meta,verifiedSingleQuestionWebp(q));
      for(const shared of q.sharedImages){
        const note=document.createElement('p');
        note.className='qa-caption';note.textContent='本題需要的共用文章／圖表';
        const fig=document.createElement('figure');
        fig.className='source-figure';
        const img=document.createElement('img');
        img.src='./'+shared.image;img.decoding='async';img.loading='eager';
        img.alt='第 '+q.questionNumber+' 題需要的官方共用材料';
        img.dataset.canonicalId=q.canonicalId;
        img.dataset.sha256=shared.sha256;
        fig.append(img);
        card.append(note,fig);
      }
      const note=document.createElement('p');
      note.className='qa-caption';
      note.textContent='影像 QA 已通過；答案與詳解待核對，尚未開放作答';
      card.append(note);
      summary.replaceChildren();
      const title=document.createElement('span');
      title.textContent=activeYear+' 年｜原題影像';
      const count=document.createElement('b');
      count.textContent=q.subject+'｜第 '+q.questionNumber+' 題（'+(index+1)+' / '+rows.length+'）';
      summary.append(title,count);
      document.getElementById('prevBtn').disabled=index===0;
      document.getElementById('nextBtn').disabled=index===rows.length-1;
      // Visible single-question IDs are the existing QA-approved image snapshots.
      const chips=document.getElementById('progressChips');
      chips.replaceChildren();
      rows.forEach((entry,i)=>{
        const button=document.createElement('button');
        button.className='chip'+(i===index?' current':'');
        button.textContent=entry.questionNumber;
        button.setAttribute('aria-label',entry.subject+'第 '+entry.questionNumber+' 題唯讀原圖');
        button.onclick=()=>{index=i;render(true);collapseQuestionNav();};
        chips.append(button);
      });
      document.getElementById('progressLabel').textContent='原圖唯讀｜'+(index+1)+' / '+rows.length+' 題';
      syncHeights();
      if(scroll)card.scrollIntoView({behavior:'smooth',block:'start'});
    };
    const changeSubject=()=>{
      rows=filter.value==='全部科目'?items:items.filter(q=>q.subject===filter.value);
      index=0;render(true);
    };
    window.suduOpenImageSubject=subject=>{
      if(!subjects.includes(subject)||subject==='全部科目')return;
      filter.value=subject;
      rows=items.filter(q=>q.subject===subject);
      index=0;
      showStudy();
      render();
      setQuestionNavAutoHide(false);
      window.scrollTo({top:0,behavior:'instant'});
    };
    filter.onchange=changeSubject;
    move=function(delta){
      index=Math.max(0,Math.min(rows.length-1,index+delta));
      render(true);
    };
    document.title='速讀｜'+activeYear+' 年單題 WebP 原圖';
    document.body.classList.remove('verified-year-loading','qa-error-mode');
    document.body.classList.add('qa-image-mode');
    document.body.dataset.verifiedReadyYear=activeYear;
    render();
    refreshHomeSubjects();
    showHome();
  }

  function htmlWithActualHighlights(value,terms) {
    const raw=String(value??'');
    const highlights=(Array.isArray(terms)?terms:[]).filter(t=>typeof t==='string'&&t.trim()&&raw.includes(t));
    if(!highlights.length)return escapeHtml(raw);
    const unique=[...new Set(highlights)].sort((a,b)=>b.length-a.length);
    const chunks=[],indexes=[];
    for(const term of unique){
      let p=0,pos=raw.indexOf(term,p);
      while(pos>=0){
        const before=raw[pos-1]||'', after=raw[pos+term.length]||'';
        const isAsciiWord=c=>/[A-Za-z0-9]/.test(c);
        const brokenWord=(isAsciiWord(term[0])&&isAsciiWord(before))||
          (isAsciiWord(term[term.length-1])&&isAsciiWord(after));
        if(!brokenWord)indexes.push({from:pos,to:pos+term.length});
        p=pos+term.length;pos=raw.indexOf(term,p);
      }
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
  // Escape untrusted text first; only **bold** and actual highlight terms are rendered.
  // This never executes arbitrary HTML from the teaching draft.
  function safeTeachingInlineMarkup(value,terms){
    return String(value??'').replace(/反向檢查/g,'相反意思')
      .split(/(\*\*[^*\n]+\*\*)/g).map(bit=>{
        if(/^\*\*[^*\n]+\*\*$/.test(bit))
          return '<strong>'+htmlWithActualHighlights(bit.slice(2,-2),terms)+'</strong>';
        return htmlWithActualHighlights(bit,terms);
      }).join('');
  }
  function safeCalculationMarkup(value,terms){
    return '<span class="calculation-steps">'+String(value??'').split('\n')
      .map((line,i)=>'<span class="calculation-step"><b>步驟 '+(i+1)+'</b> '+
        safeTeachingInlineMarkup(line,terms)+'</span>').join('')+'</span>';
  }
  fetch('./data/approved/'+activeYear+'.json',{cache:'no-store'}).then(async r=>{
    if(!r.ok)throw Error('資料未發布（HTTP '+r.status+'）');
    return r.json();
  }).then(data=>{
    if(Number(data.year)!==Number(activeYear)||!Array.isArray(data.questions)||data.approvedCount!==data.questions.length)
      throw Error('題庫驗收清單格式不符');
    const verified=data.questions;
    if(!verified.length||imageModeRequested) {
      showImageOnlyMode().catch(e=>{
        console.error('原圖逐題驗證失敗',e);
        showError('單題 WebP 暫不可用：'+e.message);
      });
      return;
    }
    const keyset=new Set();
    const expectedIds=new Set();
    for(const q of verified){
      const id=q.canonicalId;
      const identity=parsedIdentity(q);
      if(!identity||identity.id!==id||q.id!==identity.n||expectedIds.has(id)||
         q.image!==imagePath(id)||!shaValid(q.imageSha256)||
         !Array.isArray(q.options)||q.options.length!==4||!q.options.every(useful)||!/^[ABCD]$/.test(q.answer)||!q.optionExplanations ||
         ['A','B','C','D'].some(k=>!useful(q.optionExplanations[k]?.teacher)||!useful(q.optionExplanations[k]?.elementary)))
        throw Error('題庫驗收欄位異常：'+String(id));
      expectedIds.add(id);keyset.add(q.subject);
    }
    const originalSave=save;
    const originalMove=move;
    const originalProgress=renderProgress;
    const originalDetail=renderOptionDetail;
    const originalStudyFormatter=formatStudyValue;
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
      // The correct answer retains both teaching levels, while extra notes and
      // full worked steps occur exactly once in the subject guide.
      const parts=Object.entries(q.extra||{}).filter(x=>useful(x[1]));
      const calc=q.examCalculation;
      if(calc&&calc.hasExamCalculation===true&&Array.isArray(calc.lines)&&calc.lines.length)
        parts.push(['考題計算式',calc.lines.join('\n')]);
      return parts;
    };
    formatStudyValue=function(q,key,value){
      if(q.year!==Number(activeYear))
        return originalStudyFormatter(q,key,value);
      if(key==='考題計算式')return safeCalculationMarkup(value,q.highlights||[]);
      return safeTeachingInlineMarkup(value,q.highlights||[]);
    };
    renderOptionDetail=function(q,L){
      if(q.year!==Number(activeYear))return originalDetail(q,L);
      const detail=q.optionExplanations?.[L]||{};
      const color=L===q.answer?'is-correct':'is-wrong';
      const keywords=q.highlights||[];
      const header=L===q.answer?'✓ 正確解答':'× 選項檢查';
      const rows=[
        ['高職生理解',detail.teacher],
        ['國小學生也聽得懂',detail.elementary]
      ].filter(x=>useful(x[1]));
      const norm=x=>String(x??'').replace(/\*\*/g,'').replace(/\s+/g,'').trim();
      if(useful(detail.reason)&&!rows.some(x=>norm(x[1])===norm(detail.reason)))
        rows.push(['此選項正確／錯誤原因',detail.reason]);
      // The guide card already displays the teacher summary, memory, vocabulary
      // and calculation. Do not append the same extra sections under the answer.
      let html='<div class="option-detail '+color+'"><b>'+header+'</b>'+
        rows.map(x=>'<p><b>'+escapeHtml(x[0])+'：</b>'+
          safeTeachingInlineMarkup(x[1],keywords)+'</p>').join('');
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
    document.body.dataset.verifiedReadyYear=activeYear;
    document.body.classList.remove('verified-year-loading','qa-image-mode');
    renderSelectors();renderAll();refreshHomeSubjects();showHome();
    const requestedSubject=new URLSearchParams(location.search).get('subject');
    if(requestedSubject&&SUBJECTS.includes(requestedSubject))openSubjectFromHome(requestedSubject);
  }).catch(error=>{
    console.error('正式年度題庫載入失敗',error);
    showError('資料驗證或載入未通過，已暫停本年度正式作答：'+error.message);
  });
})();
