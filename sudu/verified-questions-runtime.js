/* A QA-gated 114/115 adapter for the EXISTING V4 practice UI.
 * Loads ONLY data/approved/{year}.json. Demo and its localStorage are unchanged.
 * The published artifact never embeds candidate/unverified OCR or official keys.
 */
(() => {
  'use strict';
  const relative='./v4-115-multisubject-review-demo.html';
  const args=new URLSearchParams(location.search);
  const activeYear=args.get('year');
  // 104–113 have archived candidates, NOT independently verified releases.
  // Whitelisting a year must not promote auto-paired historic answers to QA.
  const allYears=Array.from({length:12},(_,i)=>String(115-i));
  const imageModeRequested=args.get('view')==='images';
  // Keep navigation within the EXISTING year selector. Never add the four
  // large Demo/year/progress link buttons to the question reading area.
  const yearSelect=document.getElementById('yearSel');
  if(yearSelect){
    yearSelect.replaceChildren();
    for(const [value,label] of [['demo','35 題 Demo'],...allYears.map(year=>[year,year+' 年'])]){
      const option=document.createElement('option');
      option.value=value;option.textContent=label;yearSelect.append(option);
    }
    yearSelect.value=allYears.includes(activeYear)?activeYear:'demo';
    yearSelect.onchange=()=>{
      location.href=yearSelect.value==='demo'?relative:relative+'?year='+yearSelect.value;
    };
  }
  if(!allYears.includes(activeYear))return;
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
    document.body.dataset.verifiedReadyYear='';
    // The original V4 initializes Demo questions before the verified adapter.
    // Never leave those Demo cards/chips reachable on a missing annual route.
    QUESTIONS.splice(0,QUESTIONS.length);
    SUBJECTS.splice(0,SUBJECTS.length);
    for(const id of ['questionCard','answerCard','guideCard','progressChips'])
      document.getElementById(id)?.replaceChildren();
    const homeReview=document.getElementById('homeReviewBtn');
    if(homeReview)homeReview.disabled=true;
    let p=document.getElementById('verifiedLoadError');
    if(!p){
      p=document.createElement('p');p.id='verifiedLoadError';
      p.setAttribute('role','alert');
      p.style.cssText='margin:8px 0 16px;color:var(--text);font-weight:750';
      document.querySelector('main')?.prepend(p);
    }
    p.textContent=message;
    // Error state is stable, not an endless spinner and not a Demo fallback.
    refreshHomeSubjects();
  };
  const subjectFor=(paper,n,year)=>{
    // Professional 09-1/09-2 sections may differ by historical year.
    // Refuse unreviewed inferred cutoffs until A's exact official mapping
    // and MASTER's admission contract are both integrated.
    if(year<114&&(paper==='09-1'||paper==='09-2'))return null;
    if(paper==='00-C')return '國文';
    if(paper==='00-E')return '英文';
    if(paper==='00-MB')return '數學 B';
    if(paper==='09-1')return n<=25?'商業概論':'數位科技';
    if(paper==='09-2')return n<=24?'會計學':'經濟學';
    return null;
  };
  const parsedIdentity=q=>{
    if(typeof q.canonicalId!=='string')return null;
    const m=/^(10[4-9]|11[0-5])-(00-C|00-E|00-MB|09-1|09-2)-([0-9]{2})$/.exec(q.canonicalId);
    if(!m||m[1]!==activeYear||q.year!==Number(activeYear))return null;
    const n=Number(m[3]);
    if(n<1||q.subject!==subjectFor(m[2],n,Number(m[1])))return null;
    return {n,paper:m[2],id:q.canonicalId};
  };
  const imagePath=id=>'data/approved/webp/'+activeYear+'/'+id+'.webp';
  const shaValid=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
  // Original shared materials in approved-year questions must match this
  // paper/year and cover the current original question number.
  const approvedSharedImagesValid=(q,identity)=>{
    // If the canonical approved source declares required original materials,
    // accepting an absent/empty sharedImages array would hide essential
    // reading/table context from the student. Publisher MUST carry this field.
    if(q.sharedMaterialIds!==undefined){
      if(!Array.isArray(q.sharedMaterialIds)||q.sharedMaterialIds.length>8||
         q.sharedMaterialIds.some(id=>typeof id!=='string')||
         new Set(q.sharedMaterialIds).size!==q.sharedMaterialIds.length)return false;
      // An explicit empty declaration must also fail closed: no extra images.
      // Preserve absent legacy metadata compatibility, but enforce a bijection
      // whenever the publisher provides the canonical material ID list.
      const images=q.sharedImages===undefined?[]:q.sharedImages;
      if(!Array.isArray(images)||images.length!==q.sharedMaterialIds.length||
         !q.sharedMaterialIds.every(id=>images.some(v=>v&&v.sharedMaterialId===id))||
         images.some(v=>!q.sharedMaterialIds.includes(v?.sharedMaterialId)))return false;
    }
    if(q.sharedImages===undefined)return true;
    if(!Array.isArray(q.sharedImages)||q.sharedImages.length>8)return false;
    const prefix='data/approved/webp/'+activeYear+'/'+activeYear+'-'+identity.paper+'-SHARED-';
    const seen=new Set();
    return q.sharedImages.every(v=>{
      if(!v||typeof v.image!=='string'||!v.image.startsWith(prefix)||!shaValid(v.sha256))return false;
      const range=/^([0-9]{2})-([0-9]{2})[.]webp$/.exec(v.image.slice(prefix.length));
      if(!range)return false;
      const first=Number(range[1]),last=Number(range[2]);
      if(first<1||first>identity.n||identity.n>last||last>99)return false;
      const expectedId=activeYear+'-'+identity.paper+'-SHARED-'+range[1]+'-'+range[2];
      if(v.sharedMaterialId!==expectedId||seen.has(v.image))return false;
      seen.add(v.image);return true;
    });
  };


  // All seven commerce-group subjects use the SAME V4 UI as the 35-question
  // Demo. The annual subject menu reflects course coverage, not permission
  // to answer unpublished questions.
  const annualSubjects=['國文','英文','數學 B','商業概論','數位科技','會計學','經濟學'];
  let approvedCounts=new Map(),previewCounts=new Map();
  function annualNote(message){
    const target=document.getElementById('homeSubjectSel')?.closest('.home-choice-content');
    if(!target)return;
    let note=document.getElementById('annualSubjectAvailability');
    if(!note){
      note=document.createElement('small');
      note.id='annualSubjectAvailability';
      note.setAttribute('role','status');
      note.setAttribute('aria-live','polite');
      note.style.cssText='display:block;font-size:12px;line-height:1.5;color:var(--muted);margin-top:4px';
      target.appendChild(note);
    }
    note.textContent=message;
  }
  function syncAnnualStickySubjects(){
    const nav=document.getElementById('subjectSel');
    if(!nav)return;
    const selected=nav.value;
    nav.replaceChildren();
    for(const name of annualSubjects){
      const option=document.createElement('option');
      option.value=name;option.textContent=name;nav.appendChild(option);
    }
    nav.value=annualSubjects.includes(selected)?selected:currentSubject;
  }
  function subjectStatus(subject){
    const count=approvedCounts.get(subject)||0;
    const images=previewCounts.get(subject)||0;
    if(count)return subject+'：'+count+' 題已完成正式審查，可作答並查看逐選項雙層解說；其他題目仍待 QA。';
    if(images)return subject+'：'+images+' 題僅通過原圖 QA，可唯讀原圖；答案及教學未獲核准，不開放作答。';
    return subject+'：目前尚無可顯示的正式題目或通過影像 QA 的原圖；請選其他科目。';
  }
  function publishAnnualMenu(){
    window.suduAnnualSubjects=annualSubjects.slice();
    refreshHomeSubjects();
    annualNote(activeYear+' 年｜沿用原 35 題 Demo 各科 V4；僅經逐題正式核准者開放作答。');
  }
  function subjectUrl(subject,images){
    const url=new URL(relative,location.href);
    url.searchParams.set('year',activeYear);
    url.searchParams.set('subject',subject);
    if(images)url.searchParams.set('view','images');
    else url.searchParams.delete('view');
    return url.pathname+url.search;
  }
  async function loadPreviewSubjectCounts(){
    // Untrusted QA-only data must never supply answers or teaching to the
    // playable QUESTIONS array. Use it only for validated preview counts.
    try{
      const res=await fetch('./data/approved/preview/'+activeYear+'.json',{cache:'no-store'});
      if(!res.ok)return new Map();
      const data=await res.json();
      if(data.year!==Number(activeYear)||!Array.isArray(data.questions)||
         data.imagePreviewCount!==data.questions.length)throw Error('preview index metadata mismatch');
      const counts=new Map(),seen=new Set();
      for(const q of data.questions){
        const identity=parsedIdentity(q);
        if(!identity||seen.has(identity.id)||q.reviewStage!=='image_qa_pass_only'||
           q.image!==imagePath(identity.id)||q.questionNumber!==identity.n||
           !shaValid(q.imageSha256)||!Array.isArray(q.sharedImages)||
           ['answer','question','options','teaching','memory','independentSolve'].some(k=>Object.hasOwn(q,k))||
           q.sharedImages.some(v=>typeof v.image!=='string'||
             !v.image.startsWith('data/approved/webp/'+activeYear+'/'+activeYear+'-'+identity.paper+'-SHARED-')||
             !/SHARED-[0-9]{2}-[0-9]{2}[.]webp$/.test(v.image)||!shaValid(v.sha256)))
          throw Error('preview subject/question content not authorized');
        seen.add(identity.id);
        counts.set(q.subject,(counts.get(q.subject)||0)+1);
      }
      return counts;
    }catch(error){
      console.warn('唯讀原圖索引不可用；不將來源候選加入正式作答',error);
      return new Map();
    }
  }

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
  async function showImageOnlyMode(approved=[]){
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
    approvedCounts=new Map();
    for(const q of approved)approvedCounts.set(q.subject,(approvedCounts.get(q.subject)||0)+1);
    previewCounts=new Map();
    for(const q of items)previewCounts.set(q.subject,(previewCounts.get(q.subject)||0)+1);
    // Keep the existing V4 question area, and clear the demo records from the
    // active quiz model so image-only questions cannot be accidentally graded.
    QUESTIONS.splice(0,QUESTIONS.length);
    SUBJECTS.splice(0,SUBJECTS.length);
    document.getElementById('answerCard').replaceChildren();
    document.getElementById('guideCard').replaceChildren();
    document.getElementById('reviewSubject').innerHTML='<option value="ALL">全部科目</option>';
    const subjects=['全部科目',...annualSubjects];
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
      if(filter.value==='全部科目'){
        rows=items;index=0;showStudy();render(true);return;
      }
      window.suduOpenYearSubject(filter.value);
    };
    window.suduOpenYearSubject=subject=>{
      if(!annualSubjects.includes(subject))return;
      if(approvedCounts.get(subject)){
        location.href=subjectUrl(subject,false);
        return;
      }
      const nextRows=items.filter(q=>q.subject===subject);
      if(!nextRows.length){
        showHome();
        annualNote(subjectStatus(subject));
        return;
      }
      filter.value=subject;
      rows=nextRows;
      index=0;
      showStudy();
      render();
      annualNote(subjectStatus(subject));
      setQuestionNavAutoHide(false);
      window.scrollTo({top:0,behavior:'instant'});
    };
    window.suduOpenImageSubject=window.suduOpenYearSubject;
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
    publishAnnualMenu();
    showHome();
    const requestedSubject=args.get('subject');
    if(requestedSubject&&annualSubjects.includes(requestedSubject))
      window.suduOpenYearSubject(requestedSubject);
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
  }).then(async data=>{
    if(Number(data.year)!==Number(activeYear)||!Array.isArray(data.questions)||data.approvedCount!==data.questions.length)
      throw Error('題庫驗收清單格式不符');
    const verified=data.questions;
    if(!verified.length||imageModeRequested) {
      showImageOnlyMode(verified).catch(e=>{
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
      const calc=q.examCalculation;
      if(!identity||identity.id!==id||q.id!==identity.n||expectedIds.has(id)||
         q.image!==imagePath(id)||!shaValid(q.imageSha256)||!approvedSharedImagesValid(q,identity)||
         !useful(q.question)||!useful(q.topic)||!useful(q.teacherSummary)||
         !useful(q.elementarySummary)||!useful(q.memory)||!useful(q.sourceText)||
         !Array.isArray(q.options)||q.options.length!==4||!q.options.every(useful)||!/^[ABCD]$/.test(q.answer)||!q.optionExplanations ||
         ['A','B','C','D'].some(k=>!useful(q.optionExplanations[k]?.teacher)||
           !useful(q.optionExplanations[k]?.elementary)||!useful(q.optionExplanations[k]?.reason))||
         (calc?.hasExamCalculation===true&&(!Array.isArray(calc.lines)||
           calc.lines.length<2||!calc.lines.every(useful))))
        throw Error('年度題目未具備與35題Demo相同的雙層教學、四選項或必要解題步驟：'+String(id));
      expectedIds.add(id);keyset.add(q.subject);
    }
    approvedCounts=new Map();
    for(const q of verified)approvedCounts.set(q.subject,(approvedCounts.get(q.subject)||0)+1);
    previewCounts=await loadPreviewSubjectCounts();
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
    sourceText=function(q){
      // Demo textbook profiles are not verified for another exam year.
      return useful(q.sourceText)?q.sourceText:
        activeYear+' 年正式原題 '+q.canonicalId+'｜教材來源待核對';
    };
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
        rows.map(x=>'<p><b>'+escapeHtml(x[0])+'：</b>'+htmlWithActualHighlights(String(x[1]).replace(/反向檢查/g,'相反意思'),keywords)+'</p>').join('');
      // Unique subject metadata and calculations belong in the guide only.
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
    window.suduOpenYearSubject=subject=>{
      if(!annualSubjects.includes(subject))return;
      if(!approvedCounts.get(subject)){
        if(previewCounts.get(subject))location.href=subjectUrl(subject,true);
        else{
          showHome();
          annualNote(subjectStatus(subject));
        }
        return;
      }
      currentSubject=subject;
      const firstOpen=listFor(subject).findIndex(q=>!record(q).status);
      currentIndex=Math.max(0,firstOpen);
      const top=document.getElementById('subjectSel');
      if(top&&[...top.options].some(o=>o.value===subject))top.value=subject;
      showStudy();renderAll();
      annualNote(subjectStatus(subject));
      window.scrollTo({top:0,behavior:'instant'});
    };
    document.title='速讀｜'+activeYear+' 正式題庫｜教學解說';
    document.body.dataset.verifiedReadyYear=activeYear;
    document.body.classList.remove('verified-year-loading','qa-image-mode');
    renderSelectors();syncAnnualStickySubjects();renderAll();publishAnnualMenu();showHome();
    const requestedSubject=args.get('subject');
    if(requestedSubject&&annualSubjects.includes(requestedSubject))
      window.suduOpenYearSubject(requestedSubject);
  }).catch(error=>{
    console.error('正式年度題庫載入失敗',error);
    showError((Number(activeYear)<114?activeYear+' 年官方候選尚未完成逐題原圖、官答、解說及獨立 AI QA；':'')+
      '資料驗證或載入未通過，已暫停本年度正式作答：'+error.message);
  });
})();
