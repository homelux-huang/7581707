
/* 7581707 Study Dashboard — local browser-profile identity, not biometric/device fingerprinting */
const SUDU_DEVICE_KEY='sudu_device_profile_v1';
let suduDevice=null;
let suduDb=null;
let suduMirrorReady=false;
let suduHadSavedState=false;
let suduHadDevice=false;

function suduNewCode(){
  let arr=new Uint8Array(12);
  if(typeof crypto!=='undefined' && crypto.getRandomValues) crypto.getRandomValues(arr);
  else throw new Error('瀏覽器無法產生安全的隨機學習代碼');
  return 'SUDU-'+Array.from(arr,x=>x.toString(16).padStart(2,'0')).join('').toUpperCase();
}
function suduSetDevice(profile){
  suduDevice={id:profile.id,created:profile.created||new Date().toISOString(),name:String(profile.name||'我的學習空間').slice(0,40)};
  try{localStorage.setItem(SUDU_DEVICE_KEY,JSON.stringify(suduDevice));}catch(e){}
}
function suduBoot(){
  suduHadSavedState=!!localStorage.getItem('sudu_sites_state');
  suduHadDevice=!!localStorage.getItem(SUDU_DEVICE_KEY);
  try{
    const x=JSON.parse(localStorage.getItem(SUDU_DEVICE_KEY)||'null');
    if(x && /^SUDU-[A-F0-9]{24}$/.test(x.id))suduSetDevice(x);
  }catch(e){}
  if(!suduDevice)suduSetDevice({id:suduNewCode(),created:new Date().toISOString(),name:'我的學習空間'});
  state.visitCount=(Number(state.visitCount)||0)+1;
  state.lastVisit=new Date().toISOString();
  state.recentVisits=Array.isArray(state.recentVisits)?state.recentVisits:[];
  state.recentVisits.unshift(state.lastVisit);
  state.recentVisits=state.recentVisits.slice(0,60);
  state.dashboard=state.dashboard||{year:'全部',subject:'全部科目'};
  suduTryOpenMirror();
}
function suduTryOpenMirror(){
  if(typeof indexedDB==='undefined'){suduMirrorReady=true;return;}
  try{
    const req=indexedDB.open('7581707-sudu-profile-backup',1);
    req.onupgradeneeded=()=>{if(!req.result.objectStoreNames.contains('snapshots'))req.result.createObjectStore('snapshots');};
    req.onerror=()=>{suduMirrorReady=true;};
    req.onsuccess=()=>{
      suduDb=req.result;
      try{
        const t=suduDb.transaction('snapshots','readonly').objectStore('snapshots').get('latest');
        t.onsuccess=()=>{
          const old=t.result;
          if(!suduHadDevice && old?.profile?.id && /^SUDU-[A-F0-9]{24}$/.test(old.profile.id))suduSetDevice(old.profile);
          if(!suduHadSavedState && old?.state?.attempts && Object.keys(state.attempts||{}).length===0){
            const visitCount=state.visitCount,lastVisit=state.lastVisit;
            state={...state,...old.state,visitCount:(Number(old.state.visitCount)||0)+1,lastVisit: lastVisit};
            state.recentVisits=[lastVisit,...(old.state.recentVisits||[])].slice(0,60);
            state.attempts=state.attempts||{};
            state.reviewAnswers=state.reviewAnswers||{};
            state.reviewHistory=state.reviewHistory||{};
            state.extended=state.extended||{};
            state.dashboard=state.dashboard||{year:'全部',subject:'全部科目'};
            save();render();
          }
          suduMirrorReady=true;suduMirrorSave();
        };
        t.onerror=()=>{suduMirrorReady=true;suduMirrorSave();};
      }catch(e){suduMirrorReady=true;}
    };
  }catch(e){suduMirrorReady=true;}
}
function suduMirrorSave(){
  if(!suduMirrorReady||!suduDb)return;
  try{
    const tx=suduDb.transaction('snapshots','readwrite');
    tx.objectStore('snapshots').put({profile:suduDevice,state:JSON.parse(JSON.stringify(state)),savedAt:new Date().toISOString()},'latest');
  }catch(e){}
}
function suduSaveName(){
  const el=document.getElementById('db-nickname');
  if(!el)return;
  suduSetDevice({...suduDevice,name:el.value.trim().slice(0,40)||'我的學習空間'});
  suduMirrorSave();render();
}
function suduStudyQuestions(){
  const official=(ALL.officialQuestions||[]).filter(q=>q&&typeof q.id==='string'&&Number.isInteger(q.number));
  return ALL.practice.concat(official);
}
function suduQueryQuestions(year,subject){
  return suduStudyQuestions().filter(q=>(year==='全部'||String(q.year)===String(year))&&(subject==='全部科目'||q.subject===subject));
}
function suduWrongCount(q){
  const initial=(state.attempts?.[q.id]||[]).filter(a=>a.correct===false).length;
  const history=Array.isArray(state.reviewHistory?.[q.id])?state.reviewHistory[q.id]:[];
  const reviews=history.filter(a=>a.correct===false).length;
  const legacy=history.length?0:(state.reviewAnswers?.[q.id]?.correct===false?1:0);
  return initial+reviews+legacy;
}
function suduStats(year,subject){
  const qs=suduQueryQuestions(year,subject),done=qs.filter(q=>(state.attempts?.[q.id]||[]).length>0).length;
  return {total:qs.length,done,remaining:qs.length-done,completed:qs.length?Math.round(done*100/qs.length):null,unfinished:qs.length?Math.round((qs.length-done)*100/qs.length):null};
}
function suduRate(x){return x===null?'—':String(x)+'%';}
function suduBar(n){
  return '<div class="db-progress-track"><div class="db-progress-fill" style="width:'+Math.max(0,Math.min(100,n||0))+'%"></div></div>';
}
function suduSourceInfo(q){
  const chapter=q.textbook?.chapter;
  if(chapter&&q.textbookVerified===true)return esc((q.textbook.publisher||'')+'《'+(q.textbook.title||'課本')+'》 '+chapter);
  const b=ALL.books[q.subject];
  return b?'彰商曾採用 '+esc(b.publisher)+'《'+esc(b.title)+'》；本題章節與頁碼尚未核實':'本題尚未核實課本章節，僅提供觀念及題目來源';
}
function suduYearRows(subject){
  const years=['自編',...ALL.archive.map(a=>String(a.year)).sort((a,b)=>Number(b)-Number(a))];
  function row(year){
    const st=suduStats(year,subject),label=year==='自編'?'自編學習題':year+' 年';
    return '<div class="db-year-row"><strong>'+esc(label)+'</strong><div>'+(
      st.total?suduBar(st.completed)+'<span class="small">已完成 '+st.done+'/'+st.total+' 題（'+st.completed+'%），未完成 '+st.unfinished+'%</span>':
      '<span class="db-empty-state">尚未收錄可導覽题目，無法計算完成率</span>')+
      '</div><em>'+(st.total?suduRate(st.completed):'未建置')+'</em></div>';
  }
  const g=[
    {title:'自編練習（目前可作答）',items:years.filter(x=>x==='自編'),open:true},
    {title:'110～115 年',items:years.filter(x=>Number(x)>=110),open:true},
    {title:'100～109 年',items:years.filter(x=>Number(x)>=100&&Number(x)<110),open:false},
    {title:'90～99 年',items:years.filter(x=>Number(x)>=90&&Number(x)<100),open:false}
  ];
  return g.map(x=>'<details class="db-year-group" '+(x.open?'open':'')+'><summary>'+x.title+'</summary>'+x.items.map(row).join('')+'</details>').join('');
}
function suduLeaderRows(year,subject){
  const list=suduQueryQuestions(year,subject).map(q=>({q,n:suduWrongCount(q)})).filter(x=>x.n>0).sort((a,b)=>b.n-a.n||a.q.id.localeCompare(b.q.id)).slice(0,12);
  if(!list.length)return '<p class="db-empty-state">目前沒有這個範圍的答錯紀錄。答題後會依實際答錯次數自動排序。</p>';
  return list.map(({q,n},i)=>'<article class="db-leader"><div class="db-leader-header"><strong>第 '+(i+1)+' 名｜'+esc(q.subject)+'・'+esc(q.topic||'正式卷題目')+'</strong><span class="db-count">答錯 '+n+' 次</span></div>'+
    '<p>'+esc(q.question)+'</p>'+
    '<p class="db-concept"><b>關鍵觀念：</b>'+keyHtml(q.explanation,q)+'</p>'+
    '<p class="db-source"><b>出處：</b>'+suduSourceInfo(q)+'；題目：'+esc(q.source||'來源待確認')+'</p>'+
    '<button class="db-simple-btn" data-jump="'+esc(q.id)+'">再練這一題 →</button></article>').join('');
}
function suduSubjectReview(year,subject){
  const subjects=[...new Set(suduStudyQuestions().map(q=>q.subject))];
  const visible=subject==='全部科目'?subjects:subjects.filter(s=>s===subject);
  return visible.map((sub,i)=>{
    const qs=suduQueryQuestions(year,sub),w=qs.filter(q=>suduWrongCount(q)>0);
    const top=w.sort((a,b)=>suduWrongCount(b)-suduWrongCount(a));
    let content=top.length?top.map(q=>
      '<div class="db-topic"><b>'+esc(q.topic)+'</b> <span class="db-tag">錯 '+suduWrongCount(q)+' 次</span>'+
      '<p><b>觀念：</b>'+keyHtml(q.explanation,q)+'</p>'+
      '<p><b>計算／原理：</b>'+keyHtml(q.steps||'此題無步驟資料',q)+'</p>'+
      '<p><b>教材：</b>'+suduSourceInfo(q)+'</p>'+
      '<p><b>延伸：</b>'+keyHtml(q.extension||'延伸觀念待補',q)+'</p>'+
      '<button class="db-simple-btn" data-jump="'+esc(q.id)+'">複習原題與延伸考題</button></div>').join('') :
      '<p class="db-empty-state">目前沒有這一科的答錯題目。已收錄可作答 '+qs.length+' 題。</p>';
    return '<details class="db-subject" '+((subject!=='全部科目'||i===0)?'open':'')+'><summary>'+esc(sub)+'｜'+w.length+' 題曾答錯</summary><div class="db-subject-inner">'+content+'</div></details>';
  }).join('');
}
function suduScoreDashboard(){
 if(typeof SUDU_SCORING==='undefined')return '';
 const years=Object.keys(ALL.officialYearReports||{}).sort((a,b)=>Number(b)-Number(a)),cards=[];
 for(const year of years){for(const paper of ALL.officialYearReports[year].papers||[]){
  const info=SUDU_SCORING.paperStatus(ALL,state,year,paper.paper);
  const name=year+' 年 '+(typeof paperText!=='undefined'?paperText[paper.paper]||paper.paper:paper.paper);
  const attrs=' data-resume-year="'+esc(year)+'" data-resume-paper="'+esc(paper.paper)+'"';
  const validScore=info.submitted&&Number.isFinite(info.score?.value);
  const result=validScore?info.score.value+' / '+info.score.max+' 分':info.label;
  const time=info.submitted?'<p class="small">送出：'+esc(info.submittedAt?new Date(info.submittedAt).toLocaleString('zh-TW',{timeZone:'Asia/Taipei'}):'N/A')+'｜經過時間：'+esc(SUDU_SCORING.humanTime(info.elapsedMs))+'</p>':'';
  cards.push('<div class="db-year-row"><button type="button" class="db-resume-link"'+attrs+'>'+esc(name)+'</button><div><button type="button" class="db-resume-link"'+attrs+'>'+esc(result||'未考完')+' → '+(info.submitted?'檢視／複習':'繼續作答')+'</button><p class="small">已作答 '+info.answered+'／'+(info.expected||'待核實')+' 題</p>'+time+(info.score?.reason?'<p class="small">'+esc(info.score.reason)+'</p>':'')+'</div></div>');
 }}
 return '<section class="db-pane"><h3>🧾 我的學習空間｜年度試卷與續答</h3><p class="small">點試卷名稱或進度狀態，續答第一個未回答的題目。完成時進入檢視；數字成績只來自有效送出快照及核實配分。</p>'+(cards.join('')||'<p class="db-empty-state">正在載入年度卷別。</p>')+'</section>';
}
async function suduResumePaper(year,paper){
 await suduLoadOfficialYear(year);
 ui.year=String(year);ui.paper=paper;ui.subject='全部科目';ui.tab='learn';filters();
 const qs=available();const index=qs.findIndex(q=>!Number.isInteger(typeof currentAttempt==='function'?currentAttempt(q)?.choice:(state.attempts?.[q.id]||[]).at(-1)?.choice));
 ui.index=index>=0?index:0;save();render();if(typeof suduGoToQuestion==='function')suduGoToQuestion();
}
function dashboard(){
  const d=state.dashboard||{year:'全部',subject:'全部科目'};
  const years=['全部','自編',...ALL.archive.map(x=>String(x.year)).sort((a,b)=>Number(b)-Number(a))];
  const subjects=['全部科目',...new Set(suduStudyQuestions().map(q=>q.subject))];
  if(!years.includes(String(d.year)))d.year='全部';
  if(!subjects.includes(d.subject))d.subject='全部科目';
  const stats=suduStats(d.year,d.subject);
  const mistakes=suduQueryQuestions(d.year,d.subject).filter(q=>suduWrongCount(q)>0);
  const totalWrong=mistakes.reduce((n,q)=>n+suduWrongCount(q),0);
  const identity=suduDevice?.id||'學習代碼建立中';
  let selYears=years.map(y=>'<option value="'+esc(y)+'" '+(String(d.year)===String(y)?'selected':'')+'>'+(y==='全部'?'全部年度':y==='自編'?'自編練習':y+' 年')+'</option>').join('');
  let selSubjects=subjects.map(y=>'<option value="'+esc(y)+'" '+(d.subject===y?'selected':'')+'>'+esc(y)+'</option>').join('');
  const top='<section class="db-welcome"><div class="db-top"><div><h2>你好，'+esc(suduDevice?.name||'同學')+' 👋</h2><p>歡迎回到你的個人學習 Dashboard。這個瀏覽器會自動找回之前的作答與錯題。</p></div><span class="db-badge">✓ 本機學習代碼已辨識</span></div>'+
    '<div class="db-device"><span>本瀏覽器固定學習代碼： <strong>'+esc(identity)+'</strong></span></div>'+
    '<div class="db-control"><label>年度範圍<select id="db-year">'+selYears+'</select></label><label>科目篩選<select id="db-subject">'+selSubjects+'</select></label></div></section>';
  const n='<div class="db-summary"><div class="db-metric"><b>'+stats.done+'/'+stats.total+'</b><span>已完成／目前可作答題數</span></div>'+
    '<div class="db-metric"><b>'+suduRate(stats.completed)+'</b><span>已完成比例</span></div>'+
    '<div class="db-metric"><b>'+suduRate(stats.unfinished)+'</b><span>未完成比例</span></div>'+
    '<button type="button" class="db-metric" id="db-all-mistakes"><b>'+totalWrong+'</b><span>累計錯誤次數（'+mistakes.length+' 個不同錯題） · 查看全部 →</span></button></div>';
  const msg=stats.total===0?
    '<div class="db-empty">目前這個年度／科目還沒有可導覽的正式題庫，所以無法計算完成率。這不代表你沒有考試，也不會將缺題的年度算成 0% 或 100%。</div>':
    '<p class="small">只以「目前已收錄且可作答」的題目計算完成率；尚未取得的正式歷年題目不會列入分母。</p>';
  const yearCard='<section class="db-pane"><h3>📅 每一年考試完成度</h3>'+msg+suduYearRows(d.subject)+'</section>';
  const mistakesCard='<section class="db-pane"><h3>🎯 答錯最多次的題目 TOP 12</h3>'+suduLeaderRows(d.year,d.subject)+'</section>';
  const sourceCard='<section class="db-pane"><h3>📖 各科錯誤觀念複習（點開科目）</h3><p class="small">依你實際答錯的觀念整理；用黑底白字標示會計關鍵字。出處未核實時會誠實顯示，不會編造課本頁數。</p>'+suduSubjectReview(d.year,d.subject)+'</section>';
  const device='<section class="db-pane"><h3>🔐 裝置與學習紀錄</h3><div class="db-device-panel"><p class="small">目前辨識的是 <b>此瀏覽器使用者設定檔</b>，不是手機型號、IP 或真正的身分驗證。同一瀏覽器重開會保留；不同瀏覽器／無痕模式是不同學習空間。</p>'+
    '<p class="small"><b>固定學習代碼：</b><code>'+esc(identity)+'</code></p>'+
    '<p class="small"><b>此瀏覽器已啟用次數：</b>'+Number(state.visitCount||0)+'　 <b>最近進入：</b>'+esc(state.lastVisit?new Date(state.lastVisit).toLocaleString('zh-TW'):'尚無')+'</p>'+
    '<div class="db-control"><label>本機暱稱<input class="db-name" id="db-nickname" maxlength="40" value="'+esc(suduDevice?.name||'')+'" placeholder="例如：商一甲學生"></label><button id="db-save-name">儲存暱稱</button><button id="db-copy-code">複製學習代碼</button><button id="db-download">備份紀錄</button><button id="db-restore">還原備份</button><button id="db-persist">加強本機保留</button></div></div>'+
    '<div class="db-device-panel"><h3>選用：自願同步至私人管理後台</h3><p class="small">預設關閉。只有管理伺服器完成安全部署，且學生主動同意後，才會同步答題歷史、送出與作答時間。</p><div class="db-control"><label>管理 API HTTPS 網址<input type="url" id="sudu-sync-endpoint" placeholder="https://你的私人後台.onrender.com"></label><button type="button" id="sudu-sync-enable">同意並啟用同步</button><button type="button" id="sudu-sync-stop">停止同步</button></div><p id="sudu-sync-status" class="small" role="status"></p></div>'+'<p class="db-footer-note">作答紀錄儲存在瀏覽器本機，也同步嘗試儲存至瀏覽器資料庫。正常關閉瀏覽器不會登出；但清除網站資料、裝置損壞、使用無痕模式時仍可能遺失。若要永久跨裝置保存，需另外建立有登入驗證的雲端帳號與資料庫。請定期下載備份，尤其在更換手機／電腦前。</p></section>';
  return '<div class="db-page">'+top+n+suduScoreDashboard()+'<div class="db-two">'+yearCard+mistakesCard+'</div>'+sourceCard+device+'</div>';
}
function suduWireDashboard(){
  document.querySelectorAll('[data-resume-year]').forEach(b=>b.onclick=()=>suduResumePaper(b.dataset.resumeYear,b.dataset.resumePaper));
  const allWrong=document.getElementById('db-all-mistakes');if(allWrong)allWrong.onclick=()=>{state.reviewSelection={year:state.dashboard?.year||'全部',subject:state.dashboard?.subject||'全部科目',paper:'全部'};switchTab('mistakes');};
 if(typeof SUDU_SYNC!=='undefined')SUDU_SYNC.controls();
  const y=document.getElementById('db-year'),sb=document.getElementById('db-subject');
  if(y)y.onchange=()=>{state.dashboard=state.dashboard||{};state.dashboard.year=y.value;save();render();};
  if(sb)sb.onchange=()=>{state.dashboard=state.dashboard||{};state.dashboard.subject=sb.value;save();render();};
  const nm=document.getElementById('db-save-name');if(nm)nm.onclick=suduSaveName;
  const cp=document.getElementById('db-copy-code');if(cp)cp.onclick=async()=>{
    try{await navigator.clipboard.writeText(suduDevice.id);cp.textContent='已複製';}
    catch(e){window.prompt('請複製學習代碼（不是登入密碼）',suduDevice.id);}
  };
  const bk=document.getElementById('db-download');if(bk)bk.onclick=suduExportBackup;
  const rst=document.getElementById('db-restore');if(rst)rst.onclick=()=>document.getElementById('db-import-file')?.click();
  const pst=document.getElementById('db-persist');if(pst)pst.onclick=async()=>{
    if(!navigator.storage?.persist){window.alert('此瀏覽器不支援額外的本機資料保留要求，請改用備份功能。');return;}
    const ok=await navigator.storage.persist();
    window.alert(ok?'瀏覽器已同意盡量保留此網站資料。仍建議定期備份。':'瀏覽器未允許額外保留；現有本機學習紀錄不受影響。');
  };
}
function suduExportBackup(){
  const data={format:'sudu-backup-1',schemaVersion:2,platform:'7581707統測速讀平台',savedAt:new Date().toISOString(),originalBrowserCode:suduDevice?.id||null,nickname:suduDevice?.name||'',ui:typeof ui!=='undefined'?ui:null,layout:localStorage.getItem('sudu_layout_order_v1'),theme:localStorage.getItem('sudu_theme_v1'),state};
  const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download='7581707速讀學習紀錄備份.json';a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1200);
}
function suduMergeBackupState(current,imported){
 const output={...current};
 const safeKey=k=>typeof k==='string'&&!['__proto__','constructor','prototype'].includes(k)&&k.length<=200;
 const clean=a=>a&&Number.isInteger(a.choice)&&a.choice>=0&&a.choice<=3&&(typeof a.correct==='boolean'||a.correct===null);
 const eventKey=a=>JSON.stringify([a?.at??null,a?.choice,a?.correct]);
 // Preserve repeated legacy events with unknown dates. Re-importing the same
 // backup keeps the maximum multiplicity in either history, not their sum.
 const mergeEvents=(before,rows)=>{
  const available=new Map();
  for(const a of before){const key=eventKey(a);available.set(key,(available.get(key)||0)+1);}
  const additions=[];
  for(const a of rows.filter(clean)){
   const key=eventKey(a),count=available.get(key)||0;
   if(count)available.set(key,count-1);else additions.push({...a});
  }
  return before.concat(additions);
 };
 output.attempts={...(current.attempts||{})};
 for(const [id,rows] of Object.entries(imported.attempts||{})){
  if(!safeKey(id)||!Array.isArray(rows))continue;
  output.attempts[id]=mergeEvents(Array.isArray(output.attempts[id])?output.attempts[id]:[],rows);
 }
 const reviews=(data,id)=>{
  const history=Array.isArray(data.reviewHistory?.[id])?data.reviewHistory[id]:[];
  const legacy=data.reviewAnswers?.[id];
  // reviewAnswers is the latest-answer view. Its legacy event belongs in the
  // permanent history unless the same event is already represented there.
  return clean(legacy)&&!history.some(a=>eventKey(a)===eventKey(legacy))?history.concat({...legacy}):history;
 };
 output.reviewHistory={...(current.reviewHistory||{})};
 const reviewIds=new Set([...Object.keys(current.reviewHistory||{}),...Object.keys(imported.reviewHistory||{}),...Object.keys(current.reviewAnswers||{}),...Object.keys(imported.reviewAnswers||{})]);
 for(const id of reviewIds){
  if(safeKey(id))output.reviewHistory[id]=mergeEvents(reviews(current,id),reviews(imported,id));
 }
 for(const field of ['reviewAnswers','extended','examSessions','firstWrong']){
  output[field]={...(current[field]||{})};
  for(const [id,value] of Object.entries(imported[field]||{}))if(safeKey(id)&&!(id in output[field]))output[field][id]=value;
 }
 output.examSubmissions={...(current.examSubmissions||{})};
 output.examSubmissionHistory={...(current.examSubmissionHistory||{})};
 const isSnapshot=item=>item&&typeof item==='object'&&!Array.isArray(item);
 const snapshotKey=item=>item?.id?'id:'+item.id:'legacy:'+JSON.stringify(item);
 const papers=new Set([...Object.keys(imported.examSubmissions||{}),...Object.keys(imported.examSubmissionHistory||{})]);
 for(const paper of papers){
  if(!safeKey(paper))continue;
  const before=Array.isArray(output.examSubmissionHistory[paper])?output.examSubmissionHistory[paper]:[];
  const seen=new Set(before.filter(isSnapshot).map(snapshotKey));
  if(isSnapshot(output.examSubmissions[paper]))seen.add(snapshotKey(output.examSubmissions[paper]));
  const history=Array.isArray(imported.examSubmissionHistory?.[paper])?imported.examSubmissionHistory[paper]:[];
  const additions=[];
  for(const item of [imported.examSubmissions?.[paper],...history]){
   if(!isSnapshot(item))continue;
   const key=snapshotKey(item);if(seen.has(key))continue;seen.add(key);
   if(!isSnapshot(output.examSubmissions[paper]))output.examSubmissions[paper]=item;
   else additions.push(item);
  }
  output.examSubmissionHistory[paper]=before.concat(additions);
 }
 return output;
}
async function suduImportBackup(file){
 if(!file)return;if(file.size>25*1024*1024){window.alert('備份超過 25 MB，請確認檔案。');return;}
 let data;try{data=JSON.parse(await file.text());}catch{window.alert('無法讀取 JSON 備份。');return;}
 const imported=data?.state;
 if(!imported?.attempts||typeof imported.attempts!=='object'||Array.isArray(imported.attempts)||Object.keys(imported.attempts).length>20000){window.alert('不是受支援的學習紀錄備份。');return;}
 if(!window.confirm('將備份合併至目前紀錄？會先保存現況，既有首次作答、測驗快照與裝置代碼都保留。'))return;
 const snapshot={savedAt:new Date().toISOString(),state,profile:suduDevice};
 try{localStorage.setItem('sudu_backup_before_restore_v1',JSON.stringify(snapshot));}catch{window.alert('無法先備份目前紀錄；還原已取消，請先匯出備份並釋出空間。');return;}
 if(suduDb)try{suduDb.transaction('snapshots','readwrite').objectStore('snapshots').put(snapshot,'before-restore-'+Date.now());}catch{}
 state=suduMergeBackupState(state,imported);
 if(typeof SUDU_SCORING!=='undefined')SUDU_SCORING.initial(state);
 save();ui.tab='dashboard';save();render();window.alert('已合併學習紀錄。既有歷史與此瀏覽器的學習代碼保持不變。');
}
