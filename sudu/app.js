/* Existing 7581707 application. Persistent keys and question IDs are retained. */
const ALL=JSON.parse(document.getElementById('bootstrap').textContent);
const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeURL=value=>{try{const u=new URL(String(value),location.href);return ['https:','http:'].includes(u.protocol)?u.href:'#';}catch{return '#';}};
let ui={year:'自編',paper:'自編',subject:'全部科目',tab:'learn',index:0};
let state={attempts:{},extended:{},reviewAnswers:{},reviewHistory:{},reviewFilter:'all'};
let suduStorageError=null;
// Preferences and learning history are independent. A damaged preference must
// never prevent a valid history from being restored before the first save.
try{ui={...ui,...JSON.parse(localStorage.getItem('sudu_sites_ui')||'{}')};}catch{}
try{state={...state,...JSON.parse(localStorage.getItem('sudu_sites_state')||'{}')};}catch{}
if(!['自編',...ALL.archive.map(x=>String(x.year))].includes(String(ui.year)))ui.year='自編';
for(const key of ['attempts','extended','reviewAnswers','reviewHistory'])if(!state[key]||typeof state[key]!=='object'||Array.isArray(state[key]))state[key]={};
state.dashboard||={year:'全部',subject:'全部科目'};
state.reviewSelection||={year:'全部',paper:'全部',subject:'全部科目'};
// Removed standalone tabs return to the corresponding useful learning view.
if(ui.tab==='archive'||ui.tab==='source')ui.tab='dashboard';
if(!['learn','dashboard','clinic','mistakes'].includes(ui.tab))ui.tab='learn';
const save=()=>{
 let persisted=false;
 try{localStorage.setItem('sudu_sites_state',JSON.stringify(state));localStorage.setItem('sudu_sites_ui',JSON.stringify(ui));suduStorageError=null;persisted=true;}catch(e){suduStorageError='本機儲存失敗；本次選擇仍在頁面記憶體。請使用右上角匯出備份，避免關閉頁面後遺失。';}
 progress();suduMirrorSave();if(persisted&&typeof SUDU_SYNC!=='undefined')SUDU_SYNC.schedule();
 return persisted;
};
const subs=[...new Set(ALL.practice.map(q=>q.subject))];
const paperText={'自編':'各科自編練習','09-1':'專業科目（一）','09-2':'專業科目（二）','BIZ-1':'舊制商業類專一','BIZ-2':'舊制商業類專二','00-C':'國文','00-E':'英文','00-MB':'數學 B','00-M-OLD':'舊制商業類數學'};
const rec=id=>Array.isArray(state.attempts[id])?state.attempts[id]:[];
const allQuestions=()=>ALL.practice.concat(ALL.officialQuestions||[]);
const questionById=id=>allQuestions().find(q=>q.id===id);
const acceptedAnswers=q=>[...new Set((Array.isArray(q.acceptedAnswers)&&q.acceptedAnswers.length?q.acceptedAnswers:[q.answer]).filter(x=>Number.isInteger(x)&&x>=0&&x<4))];
const gradeReady=q=>!q.official?acceptedAnswers(q).length>0:q.answerVerified===true&&q.questionVerified===true&&acceptedAnswers(q).length>0;
const answerLabel=q=>gradeReady(q)?acceptedAnswers(q).map(x=>'ABCD'[x]).join('／'):'待核對';
function questionOptions(q){return [0,1,2,3].map(i=>String(q.options?.[i]||''));}
function isImageQuestion(q){return q.official&&(q.questionVerified!==true||q.issues?.includes('OCR_missing_question'));}
function currentAttempt(q){
 const key=String(q.year)+'/'+(q.paper||ui.paper);
 const session=state.examSessions?.[key];
 if(session?.fresh){const choice=session.choices?.[q.id];return Number.isInteger(choice)?{choice,correct:gradeReady(q)?acceptedAnswers(q).includes(choice):null}:null;}
 return rec(q.id).at(-1)||null;
}
function filters(){
 $('year').innerHTML='<option value="自編">自編練習（'+ALL.practice.length+' 題，非官方）</option>'+ALL.archive.map(x=>'<option value="'+x.year+'">'+x.year+' 學年度</option>').join('');
 $('year').value=ui.year;
 const report=ALL.officialYearReports?.[ui.year];
 const codes=ui.year==='自編'?['自編']:[...new Set((report?.papers||[]).map(p=>p.paper))];
 if(!codes.includes(ui.paper))ui.paper=codes.includes('09-2')?'09-2':codes.includes('BIZ-2')?'BIZ-2':(codes[0]||'');
 $('paper').innerHTML=codes.length?codes.map(c=>'<option value="'+esc(c)+'">'+esc((paperText[c]||c)+((report?.papers?.find(p=>p.paper===c)?.coverSubjects||[]).length?'｜'+report.papers.find(p=>p.paper===c).coverSubjects.join('、'):''))+'</option>').join(''):'<option value="">卷別資料待載入／核對</option>';
 $('paper').value=ui.paper;$('paper').disabled=!codes.length;
 const paper=report?.papers?.find(p=>p.paper===ui.paper);
 const imported=(ALL.officialQuestions||[]).filter(q=>String(q.year)===String(ui.year)&&q.paper===ui.paper).map(q=>q.subject);
 // Use the actual imported historical paper; never inject modern digital subjects.
 const subjectList=ui.year==='自編'?subs:[...imported,...(paper?.subject?[paper.subject]:[])];
 const subjects=['全部科目',...new Set(subjectList.filter(Boolean))];
 if(!subjects.includes(ui.subject))ui.subject='全部科目';
 $('subject').innerHTML=subjects.map(s=>'<option value="'+esc(s)+'">'+esc(s)+'</option>').join('');$('subject').value=ui.subject;
 const qs=(ALL.officialQuestions||[]).filter(q=>String(q.year)===String(ui.year));
 $('status').textContent=ui.year==='自編'?'已收錄 '+ALL.practice.length+' 題自編練習（非正式考題）':report?ui.year+' 年：'+qs.length+' 筆原題紀錄；答案程式配對 '+qs.filter(q=>q.answerMatched).length+'，覆核 '+qs.filter(q=>q.answerVerified).length+'。完整度依逐卷稽核。':ui.year+' 年：正在載入已核對卷別。';
 save();
}
function available(){return (ui.year==='自編'?ALL.practice:(ALL.officialQuestions||[]).filter(q=>String(q.year)===String(ui.year)&&q.paper===ui.paper)).filter(q=>ui.subject==='全部科目'||q.subject===ui.subject);}
function progress(){
 const entries=Object.values(state.attempts).filter(Array.isArray);
 if($('answered'))$('answered').textContent=entries.filter(a=>a.length).length;
 if($('wrong'))$('wrong').textContent=entries.filter(a=>a[0]?.correct===false&&!a.at(-1)?.mastered).length;
 if($('study-identity')&&suduDevice)$('study-identity').textContent=(suduDevice.name||'我的學習空間')+' · 本機學習代碼 '+suduDevice.id.slice(-8);
}
function switchTab(tab){ui.tab=['learn','dashboard','clinic','mistakes'].includes(tab)?tab:'learn';save();render();if(ui.tab!=='learn')suduLoadAllOfficialYears();}
function nav(delta){const a=available();if(!a.length)return;ui.index=Math.max(0,Math.min(a.length-1,ui.index+delta));suduAnswerJumped=false;save();render();suduGoToQuestion();}
function h(icon,title){return '<h2><span aria-hidden="true">'+icon+'</span>'+title+'</h2>';}
// Escaped, curated accounting concept highlights (never inject untrusted HTML).
const accountingConcepts=['企業個體假設','繼續經營假設','權責基礎','現金基礎','先進先出法','先進先出','銷貨淨額','銷貨成本','銷貨毛利','流動資產','流動負債','流動比率','速動比率','營運資金','應收帳款','預收收入','預付費用','未兌現支票','銀行調節表','直線法折舊','折舊','備抵損失','備抵呆帳','應收票據','進項稅額','銷項稅額','股票股利','本益比','每股盈餘','保留盈餘','借方','貸方','資產','負債'];
function keyHtml(value,q){const raw=String(value??'');if(q?.subject!=='會計學')return esc(raw);const terms=[...new Set([q.topic,...accountingConcepts].filter(t=>typeof t==='string'&&t.length>=2))].sort((a,b)=>b.length-a.length);let result='',offset=0;while(offset<raw.length){let found=terms.find(t=>raw.startsWith(t,offset));if(found){result+='<mark class="concept-key">'+esc(found)+'</mark>';offset+=found.length;}else{result+=esc(raw[offset]);offset++;}}return result;}
function sourceHTML(q){
 const book=q.textbook,listed=ALL.books[q.subject];
 const exact=q.textbookVerified===true&&book?.chapter;
 return '<div class="section sourcebox"><h2>📚 本題教材與來源</h2><p class="textline"><b>題目：</b>'+ (q.official?'<a href="'+esc(safeURL(q.source))+'" target="_blank" rel="noopener">'+q.year+' 年 '+esc(paperText[q.paper]||q.paper)+' 原卷第 '+q.number+' 題</a>':esc(q.source||'本站自編練習'))+'</p>'+
 (q.answerSource?'<p class="small"><a href="'+esc(safeURL(q.answerSource))+'" target="_blank" rel="noopener">官方答案來源</a> · '+(q.answerVerified?'答案已覆核':'答案配對尚待覆核')+'</p>':'')+
 (exact?'<p>'+esc([book.publisher,book.title,book.volume,book.chapter,book.pages].filter(Boolean).join('｜'))+'</p>':'<p class="small"><b>精確章節待核實</b>；頁碼 N/A。教材核實與題目解析分開審核。</p>')+
 (listed?'<p class="small">彰商歷史公開書單參照：'+esc(listed.publisher)+'《'+esc(listed.title)+'》；此書單不代表本題或該考試年度的採用版本。</p>':'')+
 '<p class="small"><a href="'+esc(safeURL(ALL.schoolSource))+'" target="_blank" rel="noopener">彰化高商公開書單</a> · <a href="'+esc(safeURL(ALL.catalog))+'" target="_blank" rel="noopener">審定教科書</a> · <a href="'+esc(safeURL(ALL.curriculum))+'" target="_blank" rel="noopener">課綱</a></p></div>';
}
function teachingHTML(q){
 const verified=!q.official||q.teachingVerified===true;
 const accepted=acceptedAnswers(q);
 const reasons=[0,1,2,3].map(i=>{
  const kind=gradeReady(q)?accepted.includes(i)?'正確選項':'其他選項':'待核對';
  let reason=verified?(q.optionReasons?.[i]||q.wrongOptions?.[i]||''):'';
  if(!reason&&verified&&accepted.includes(i))reason=q.correctExplanation||q.explanation||'';
  return '<li><b>'+('ABCD'[i])+'｜'+kind+'</b><p class="textline">'+keyHtml(reason||'N/A／此選項的理由待核實',q)+'</p></li>';
 }).join('');
 return '<div class="subsection">白話解說｜小學生也懂</div><p class="textline">'+keyHtml(verified?(q.explanation||'N/A／白話解說待補'):'N/A／逐題教師解說待原卷、答案與推理覆核',q)+'</p>'+
 (verified?suduAccountingTeacher(q):'')+'<h3>核心原理與推理步驟</h3><p class="textline">'+keyHtml(verified?(q.principle||q.steps||'N/A／步驟待補'):'N/A／待核實',q)+'</p>'+
 (verified&&q.principle&&q.steps?'<p class="textline">'+keyHtml(q.steps,q)+'</p>':'')+'<h3>每個選項為什麼對／錯</h3><ol class="sudu-option-reasons">'+reasons+'</ol>';
}
function extensionHTML(q){
 const verified=!q.official||q.teachingVerified===true,p=verified?q.practice:null;
 return '<p class="textline">'+keyHtml(verified?(q.extension||'N/A／延伸觀念待補'):'N/A／延伸觀念待核實',q)+'</p>'+(p?.question?'<section class="followup"><h3>自編延伸題（非官方考題）</h3><p class="textline">'+esc(p.question)+'</p>'+(Array.isArray(p.options)?p.options.map((o,i)=>'<p>'+('ABCD'[i])+'｜'+esc(o)+'</p>').join(''):'<p class="small">四選項版本待補。</p>')+'<details><summary>查看延伸題答案與白話解說</summary><p class="textline">'+esc(Number.isInteger(p.answer)?('ABCD'[p.answer]+'｜'+(p.options?.[p.answer]||'')):(p.answer||'N/A'))+'</p><p class="textline">'+esc([p.steps,p.explanation].filter(Boolean).join('\n')||'完整步驟／白話詳解待補')+'</p></details></section>':'<p class="small">N/A／完整四選項延伸題待核實。</p>');
}
function questionHTML(q){
 if(isImageQuestion(q))return '<p class="small">請閱讀下方原卷影像。題幹、公式、圖表以原卷為準；文字定位與選項尚待覆核。</p>';
 return '<p class="bodytext" data-hover-text="'+esc(q.id)+'">'+esc(q.question)+'</p>';
}
function imagesHTML(q,answer=false){return q.official&&typeof SUDU_IMAGES!=='undefined'?SUDU_IMAGES.placeholder(q,answer):'';}
function optionsHTML(q,choice,graded,review=false){
 const accepted=acceptedAnswers(q);
 return '<p class="small">點 A～D 按鈕作答；點字詞可閱讀學習卡片。</p><div class="sudu-options">'+questionOptions(q).map((text,i)=>'<div class="sudu-option-row"><div class="option '+(choice===i?'chosen ':'')+(graded&&accepted.includes(i)?'right ':graded&&choice===i?'wrong ':'')+'"><button type="button" class="sudu-option-answer" '+(review?'data-clinic-answer="'+esc(q.id)+'" data-choice="'+i+'"':'data-answer="'+i+'"')+' aria-label="選擇 '+('ABCD'[i])+'" aria-pressed="'+(choice===i)+'">'+('ABCD'[i])+'</button><div class="sudu-option-content" '+(!isImageQuestion(q)?'data-hover-text="'+esc(q.id)+'"':'')+'>'+(isImageQuestion(q)?'原卷選項 '+('ABCD'[i]):esc(text||'請參照原卷選項 '+('ABCD'[i])))+'</div></div></div>').join('')+'</div>';
}
function suduExamPanel(){
 if(ui.year==='自編')return '<p class="small">自編練習不計入官方統測成績。</p>';
 const info=SUDU_SCORING.paperStatus(ALL,state,ui.year,ui.paper);
 const validScore=info.submitted&&Number.isFinite(info.score?.value);
 const score=validScore?'<p><b>正式規則計算成績：'+info.score.value+' / '+info.score.max+' 分</b></p>':'';
 const when=info.submitted?'<p class="small">送出：'+esc(info.submittedAt?new Date(info.submittedAt).toLocaleString('zh-TW',{timeZone:'Asia/Taipei'}):'N/A')+'；經過時間：'+esc(SUDU_SCORING.humanTime(info.elapsedMs))+'（含離開頁面；活躍時間未記錄則 N/A）</p>':'';
 return '<section class="section white sudu-exam-status"><h2>🧾 試卷進度與送出</h2><p><b>'+esc(info.label)+'</b> · 已作答 '+info.answered+'／'+(info.expected||'待核實')+'</p>'+score+(info.score?.reason?'<p class="small">'+esc(info.score.reason)+'</p>':'')+
 (info.ready&&!info.submitted?'<button id="sudu-submit-paper" class="btn" type="button">保存並送出本次試卷</button>':'')+when+
 (info.submitted&&SUDU_SCORING.startNewExam?'<button id="sudu-new-exam" class="btn light" type="button">開始新測驗（保留歷程）</button>':'')+'</section>';
}
function learn(){
 const a=available();ui.index=Math.max(0,Math.min(a.length-1,Number(ui.index)||0));const q=a[ui.index];$('bottom').style.display='none';
 if(!q){const paper=ALL.officialYearReports?.[ui.year]?.papers?.find(p=>p.paper===ui.paper);const documentRecord={id:'paper:'+ui.year+':'+ui.paper,official:true,year:ui.year,paper:ui.paper,source:paper?.questionPdf,number:null};return '<section class="section white"><h2>這個範圍的逐題題庫待補</h2><p>已核對官方卷別；尚未有可靠逐題紀錄。可先閱讀完整原卷，題數與作答進度不會憑空建立。</p>'+imagesHTML(documentRecord)+'<p><a href="'+esc(safeURL(paper?.questionPdf||ALL.official))+'" target="_blank" rel="noopener">官方試卷來源</a></p></section><div id="sudu-exam-panel">'+suduExamPanel()+'</div>';}

 const last=currentAttempt(q),choice=last?.choice,answered=Number.isInteger(choice),graded=answered&&gradeReady(q),accepted=acceptedAnswers(q);
 const correct=graded?accepted.includes(choice):null;
 const notice=answered?'<p class="hint" role="status"><b class="'+(correct===true?'correct':correct===false?'incorrect':'')+'">'+(suduStorageError?'選擇暫存於本頁，尚未保存':graded?(correct?'答對了':'答錯了，紀錄已保存'):'已保存，答案待核對')+'</b>　你選 '+('ABCD'[choice])+(graded?'；'+(q.official?'官方接受答案 ':'自編參考答案 ')+answerLabel(q):'；不列入正誤判分')+'。</p>':'<p class="small">點選後先保存作答，再顯示答案與解說。'+(!gradeReady(q)?'本題尚待覆核，可先記錄選擇。':'')+'</p>';
 const answer=answered?'<div class="section resultbox"><h2>'+(gradeReady(q)?'✅ 正確答案：'+answerLabel(q):'答案待核對')+'</h2><p class="textline">'+(gradeReady(q)?accepted.map(i=>esc(q.options?.[i]||'原卷選項 '+('ABCD'[i]))).join('／'):'目前沒有可確定的逐題答案；可展開官方答案原頁自行對照，其他題答案也可能同頁顯示。')+'</p>'+imagesHTML(q,true)+'</div>'+teachingHTML(q):'<p>先試著作答，解說區會立即接在題目下方。</p>';
 return '<div class="section blue" data-current-question="'+esc(q.id)+'">'+h('✏️','題目｜'+esc(q.subject)+' '+(q.official?'原卷第 '+q.number+' 題':'第 '+(ui.index+1)+' 題'))+'<div class="meta"><span class="pill">'+(q.official?'官方原卷・'+(q.questionVerified?'原題已覆核':'原題待覆核'):'自編練習')+'</span><span class="pill">'+esc(q.topic||paperText[q.paper]||'觀念練習')+'</span><span class="pill">目前篩選 '+(ui.index+1)+' / '+a.length+'</span></div>'+questionHTML(q)+imagesHTML(q)+
 '<div data-question-hover="'+esc(q.id)+'"></div>'+optionsHTML(q,choice,graded)+notice+'</div><div class="section orange">'+h('💡','白話解說｜小學生也懂')+answer+'</div><div class="section green">'+h('📖','延伸觀念與練習')+(answered?extensionHTML(q):'<p class="small">作答後顯示。</p>')+'</div>'+sourceHTML(q)+
 '<nav class="questionnav" aria-label="上一題與下一題"><button id="prev2" type="button" '+(ui.index===0?'disabled':'')+'><span aria-hidden="true">←</span> 上一題</button><strong aria-label="目前題數">'+(ui.index+1)+' / '+a.length+'</strong><button id="next2" type="button" '+(ui.index===a.length-1?'disabled':'')+'>下一題 <span aria-hidden="true">→</span></button></nav><div id="sudu-exam-panel">'+suduExamPanel()+'</div>';
}
function wrongEvents(id){
 const attempts=rec(id),reviews=Array.isArray(state.reviewHistory[id])?state.reviewHistory[id]:[];
 const legacy=!reviews.length&&state.reviewAnswers[id]?[state.reviewAnswers[id]]:[];
 return [...attempts,...reviews,...legacy].filter(x=>x.correct===false);
}
function clinic(){return reviewPage(false);}
function mistakes(){return reviewPage(true);}
function reviewPage(all){
 const ids=[...new Set([...Object.keys(state.attempts),...Object.keys(state.reviewHistory),...Object.keys(state.reviewAnswers)])].filter(id=>all?wrongEvents(id).length>0:rec(id)[0]?.correct===false);
 const selection=state.reviewSelection,filter=state.reviewFilter||'all';
 const metadata=ids.map(id=>({id,q:questionById(id)}));
 const years=['全部',...new Set(metadata.map(x=>String(x.q?.year||'資料待載入')))];
 const subjects=['全部科目',...new Set(metadata.map(x=>x.q?.subject||'資料待载入'))];
 const papers=['全部',...new Set(metadata.map(x=>x.q?.paper||'自編'))];
 const sel=(id,key,values)=>'<label>'+key+'<select id="'+id+'">'+values.map(v=>'<option value="'+esc(v)+'" '+(selection[id.replace('review-','')]===v?'selected':'')+'>'+esc(paperText[v]||v)+'</option>').join('')+'</select></label>';
 const shown=metadata.filter(({id,q})=>(selection.year==='全部'||String(q?.year)===selection.year)&&(selection.subject==='全部科目'||q?.subject===selection.subject)&&(selection.paper==='全部'||(q?.paper||'自編')===selection.paper)&&(filter==='all'||(filter==='mastered')===!!rec(id).at(-1)?.mastered));
 const items=shown.map(({id,q})=>{
  const logs=wrongEvents(id),first=logs[0],test=state.reviewAnswers[id],mastered=!!rec(id).at(-1)?.mastered;
  if(!q)return '<article class="reviewitem"><h3>原題待載入／目前題庫缺漏</h3><p>題目識別：'+esc(id)+'；錯誤事件 '+logs.length+' 次。原始作答紀錄仍保留。</p></article>';
  const tested=Number.isInteger(test?.choice),graded=tested&&gradeReady(q);
  return '<article class="reviewitem" id="review-'+esc(id)+'"><h3>'+esc(q.year+' 年 '+q.subject+'｜'+(q.number?'原卷第 '+q.number+' 題':q.topic))+'</h3><p class="small">首次錯選：'+('ABCD'[first?.choice]||'N/A')+'；首次錯誤日期：'+esc(first?.at||'N/A')+'；累計錯誤事件 '+logs.length+' 次。'+(mastered?'已標記掌握':'待複習')+'，歷史紀錄永久保留。</p>'+questionHTML(q)+imagesHTML(q)+'<div data-question-hover="'+esc(q.id)+'"></div>'+optionsHTML(q,test?.choice,graded,true)+
 (tested?'<p class="hint">本次選 '+('ABCD'[test.choice])+'：'+(graded?(acceptedAnswers(q).includes(test.choice)?'答對':'答錯'):'待核對')+'。<button type="button" class="btn light" data-clinic-reset="'+esc(id)+'">清除本次選擇並重答（保留歷史）</button></p>':'')+
 '<section class="section orange"><h2>正解與白話解說</h2><p><b>'+answerLabel(q)+'</b></p>'+imagesHTML(q,true)+teachingHTML(q)+'</section><section class="section green"><h2>延伸／反向思考</h2>'+extensionHTML(q)+'</section>'+sourceHTML(q)+
 '<div class="actions"><button type="button" class="btn light" data-jump="'+esc(id)+'">回逐題學習</button><button type="button" class="btn light" data-master="'+esc(id)+'">'+(mastered?'恢復待複習':'標記已掌握')+'</button></div></article>';
 }).join('');
 return '<section class="section white"><h2>'+(all?'全部曾答錯的題目':'首次作答即答錯的題目')+'</h2><p class="small">'+(all?'包含逐題作答及複習中所有曾答錯的題目。':'保留第一次作答就答錯的題目；後來答對不移除。')+'累計錯誤事件數與不同錯題數分開計算。</p><p><b>'+ids.length+' 個不同錯題／'+ids.reduce((n,id)=>n+wrongEvents(id).length,0)+' 次錯誤事件</b></p><div class="db-control">'+sel('review-year','年度',years)+sel('review-paper','試卷',papers)+sel('review-subject','科目',subjects)+'</div><div class="clinicfilter">'+[['all','全部'],['pending','待複習'],['mastered','已掌握']].map(([v,label])=>'<button type="button" data-review-filter="'+v+'" class="'+(filter===v?'active':'')+'">'+label+'</button>').join('')+'</div><button type="button" class="btn light" id="clinicOnly">回逐題學習</button>'+(items||'<p class="hint">此篩選目前沒有錯題。</p>')+'</section>';
}
async function jumpToQuestion(id){
 let q=questionById(id);
 if(!q){const year=id.match(/^(\d{2,3})-/)?.[1];if(year)await suduLoadOfficialYear(year);q=questionById(id);}
 if(!q)return;
 ui.year=String(q.year);ui.paper=q.paper||'自編';ui.subject=q.subject;ui.tab='learn';filters();ui.index=Math.max(0,available().findIndex(x=>x.id===id));suduAnswerJumped=false;save();render();suduGoToQuestion();
}
function recordChoice(q,choice,review=false){
 if(!q||!Number.isInteger(choice)||choice<0||choice>3)return;
 const at=new Date().toISOString(),correct=gradeReady(q)?acceptedAnswers(q).includes(choice):null;
 const answer={choice,correct,at,gradingStatus:correct===null?'pending':'graded',questionVersion:q.contentHash||q.sourceVersion||null};
 if(review){state.reviewAnswers[q.id]=answer;(state.reviewHistory[q.id]||=[]).push({...answer});}
 else{
  if(SUDU_SCORING.recordAnswer)SUDU_SCORING.recordAnswer(ALL,state,q,choice,at);
  else SUDU_SCORING.markFirstAnswer(ALL,state,q.year,q.paper||ui.paper,at);
  const rows=rec(q.id).slice();rows.push({...answer,firstChoice:rows.length===0?choice:undefined});state.attempts[q.id]=rows;
 }
 const persisted=save();render();if(!persisted){$('sudu-save-warning')?.focus();return;}if(!review)suduGoToExplanation();
 else requestAnimationFrame(()=>document.getElementById('review-'+q.id)?.scrollIntoView({behavior:suduScrollBehavior(),block:'start'}));
}
function render(){
 document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x.dataset.tab===ui.tab));
 $('screen').innerHTML=({learn,clinic,mistakes,dashboard}[ui.tab]||learn)();$('bottom').style.display='none';progress();
 if(ui.tab==='dashboard')suduWireDashboard();
 suduWorkspaceApply();
 if(suduStorageError){const warning=document.createElement('section');warning.className='section white';warning.id='sudu-save-warning';warning.setAttribute('role','alert');warning.tabIndex=-1;warning.textContent=suduStorageError;$('screen').prepend(warning);}
 if(typeof SUDU_IMAGES!=='undefined')SUDU_IMAGES.mount();
 if(typeof SUDU_HOVER!=='undefined')SUDU_HOVER.mount();
 $('sudu-submit-paper')?.addEventListener('click',()=>{if(!confirm('保存並送出本次作答快照？舊紀錄會保留。'))return;const r=SUDU_SCORING.submit(ALL,state,ui.year,ui.paper);if(!r.ok){alert(r.reason);return;}save();render();});
 $('sudu-new-exam')?.addEventListener('click',()=>{if(!confirm('開始新測驗？既有答案歷史與已送出快照仍會保留。'))return;SUDU_SCORING.startNewExam(ALL,state,ui.year,ui.paper,new Date().toISOString());ui.index=0;save();render();suduGoToQuestion();});
 document.querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>recordChoice(available()[ui.index],Number(b.dataset.answer)));
 document.querySelectorAll('[data-clinic-answer]').forEach(b=>b.onclick=()=>recordChoice(questionById(b.dataset.clinicAnswer),Number(b.dataset.choice),true));
 document.querySelectorAll('[data-clinic-reset]').forEach(b=>b.onclick=()=>{delete state.reviewAnswers[b.dataset.clinicReset];save();render();});
 document.querySelectorAll('[data-review-filter]').forEach(b=>b.onclick=()=>{state.reviewFilter=b.dataset.reviewFilter;save();render();});
 for(const key of ['year','paper','subject'])if($('review-'+key))$('review-'+key).onchange=e=>{state.reviewSelection[key]=e.target.value;save();render();};
 document.querySelectorAll('[data-jump]').forEach(b=>b.onclick=()=>jumpToQuestion(b.dataset.jump));
 document.querySelectorAll('[data-master]').forEach(b=>b.onclick=()=>{const logs=rec(b.dataset.master);if(logs.length){logs.at(-1).mastered=!logs.at(-1).mastered;save();render();}});
 $('prev2')?.addEventListener('click',()=>nav(-1));$('next2')?.addEventListener('click',()=>nav(1));$('clinicOnly')?.addEventListener('click',()=>switchTab('learn'));
}
$('year').onchange=async()=>{ui.year=$('year').value;ui.paper='';ui.subject='全部科目';ui.index=0;ui.tab='learn';filters();save();render();await suduLoadOfficialYear(ui.year);filters();render();};
$('paper').onchange=()=>{ui.paper=$('paper').value;ui.subject='全部科目';ui.index=0;ui.tab='learn';filters();save();render();};
$('subject').onchange=()=>{ui.subject=$('subject').value;ui.index=0;ui.tab='learn';save();render();};
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>switchTab(b.dataset.tab));
$('export').onclick=suduExportBackup;$('quick-dashboard').onclick=()=>switchTab('dashboard');
$('db-import-file').onchange=e=>{suduImportBackup(e.target.files?.[0]);e.target.value='';};
document.addEventListener('keydown',e=>{if(ui.tab!=='learn'||e.altKey||e.ctrlKey||e.metaKey||['INPUT','SELECT','TEXTAREA','BUTTON','SUMMARY'].includes(document.activeElement?.tagName)||document.querySelector('dialog[open]'))return;if(e.key==='ArrowRight'){e.preventDefault();nav(1);}else if(e.key==='ArrowLeft'){e.preventDefault();nav(-1);}});
suduBoot();SUDU_SCORING.initial(state);suduWorkspaceInit();if(typeof SUDU_COUNTDOWN!=='undefined')SUDU_COUNTDOWN.init();filters();render();
suduLoadOfficialIndex().then(()=>fetch('./data/scoring-rules.json',{cache:'no-store'})).then(r=>r.ok?r.json():null).then(data=>{if(data&&Array.isArray(data.rules)){ALL.scoringRules=data;render();}}).catch(()=>{});
suduLoadOfficialYear(ui.year).then(()=>{filters();render();if(ui.tab!=='learn')suduLoadAllOfficialYears();});
