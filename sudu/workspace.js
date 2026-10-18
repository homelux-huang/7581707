
/* Personalized, local-only layout and theme. Works with pointer drag, keyboard buttons and touch menu. */
const SUDU_LAYOUT_KEY="sudu_layout_order_v1";
const SUDU_THEME_KEY="sudu_theme_v1";
let suduLayoutOrder=[];
let suduMenuPinned=false;
function suduReadLayout(){
 try{const x=JSON.parse(localStorage.getItem(SUDU_LAYOUT_KEY)||"[]");if(Array.isArray(x))suduLayoutOrder=[...new Set(x.filter(v=>["question","answer","explanation","extension","source"].includes(v)))];}catch(e){}
}
function suduSaveLayout(){try{localStorage.setItem(SUDU_LAYOUT_KEY,JSON.stringify(suduLayoutOrder))}catch(e){}}
function suduTheme(next){
 const valid=next==="dark"?"dark":"light";
 document.documentElement.dataset.suduTheme=valid;
 try{localStorage.setItem(SUDU_THEME_KEY,valid)}catch(e){}
 const b=document.getElementById("sudu-theme-button");
 if(b){b.innerHTML='<span aria-hidden="true">'+(valid==="dark"?"☀":"☾")+'</span>';b.setAttribute("aria-label",valid==="dark"?"切換淺色主題":"切換深色主題");b.title=b.getAttribute("aria-label");}
 const menuTheme=document.getElementById("sudu-theme-in-menu");if(menuTheme)menuTheme.textContent=valid==="dark"?"☀ 切換淺色主題":"☾ 切換深色主題";
}

/* Three independent menus. A pointer bridge allows immediate 0 ms closure. */
const SUDU_MENU_TYPES=["year","subject","functions"];
let suduMenuActive=null;
let suduSuppressFocusReopen=false;
function suduMenuTriggers(){return [...document.querySelectorAll("[data-sudu-menu-trigger]")];}
function suduPositionMenu(kind){
 const trigger=document.querySelector('[data-sudu-menu-trigger="'+kind+'"]');
 const panel=document.getElementById("sudu-floating-controls");
 if(!trigger||!panel)return;
 const bounds=trigger.getBoundingClientRect();
 const width=kind==="functions"?Math.min(560,window.innerWidth-18):Math.min(410,window.innerWidth-18);
 const centered=bounds.left+bounds.width/2-width/2;
 const x=Math.max(9,Math.min(centered,window.innerWidth-width-9));
 panel.style.setProperty("--sudu-menu-left",x+"px");
 panel.style.setProperty("--sudu-menu-width",width+"px");
 panel.style.setProperty("--sudu-menu-top",Math.max(48,document.querySelector(".header")?.getBoundingClientRect().bottom||56)+"px");
 const bridge=document.getElementById("sudu-menu-bridge");
 if(bridge){
  const top=Math.max(bounds.bottom,document.querySelector(".header")?.getBoundingClientRect().bottom||bounds.bottom);
  const left=Math.min(x,bounds.left),right=Math.max(x+width,bounds.right);
  bridge.style.left=left+"px";bridge.style.top=(bounds.bottom-1)+"px";
  bridge.style.width=(right-left)+"px";bridge.style.height=(top-bounds.bottom+3)+"px";
  bridge.style.clipPath='polygon('+(bounds.left-left)+'px 0,'+(bounds.right-left)+'px 0,'+(x+width-left)+'px 100%,'+(x-left)+'px 100%)';
 }
}
function suduSetMenu(open,kind=suduMenuActive||"year"){
 const panel=document.getElementById("sudu-floating-controls");
 if(!panel)return;
 if(open && !SUDU_MENU_TYPES.includes(kind))return;
 if(open){suduMenuActive=kind;suduPositionMenu(kind);}
 panel.dataset.activeMenu=open?kind:"";
 panel.classList.toggle("open",Boolean(open));
 document.getElementById("sudu-menu-bridge")?.classList.toggle("open",Boolean(open));
 panel.setAttribute("aria-hidden",String(!open));
 panel.inert=!open;
 for(const trigger of suduMenuTriggers()){
  const isActive=Boolean(open)&&trigger.dataset.suduMenuTrigger===kind;
  trigger.setAttribute("aria-expanded",String(isActive));
  trigger.classList.toggle("is-active",isActive);
 }
}
function suduInMenuRegion(node){
 return node instanceof Node&&(document.getElementById("sudu-floating-controls")?.contains(node)||document.getElementById("sudu-menu-bridge")?.contains(node)||suduMenuTriggers().some(trigger=>trigger.contains(node)));
}
function suduScheduleMenuClose(event){
 if(event?.pointerType==="touch"||suduInMenuRegion(event?.relatedTarget))return;
 if(event?.relatedTarget===null&&document.activeElement?.tagName==="SELECT"&&suduInMenuRegion(document.activeElement))return;
 suduMenuPinned=false;suduSetMenu(false);
}
function suduWorkspaceInit(){
 suduReadLayout();
 let theme="light";try{theme=localStorage.getItem(SUDU_THEME_KEY)||"light"}catch(e){}
 const head=document.querySelector(".header .head");
 const filter=document.querySelector(".filters");
 const tabs=document.querySelector(".tabs");
 const wrap=document.querySelector(".wrap");
 if(!head||!filter||!tabs||!wrap)return;
 if(document.getElementById("sudu-floating-controls"))return;
 const actions=document.createElement("div");actions.className="sudu-head-actions";
 actions.innerHTML='<div class="sudu-header-triggers" role="group" aria-label="學習平台導覽">'
  +'<button type="button" class="sudu-controls-trigger" data-sudu-menu-trigger="year" aria-haspopup="true" aria-controls="sudu-floating-controls" aria-expanded="false">年度 <span aria-hidden="true">⌄</span></button>'
  +'<button type="button" class="sudu-controls-trigger" data-sudu-menu-trigger="subject" aria-haspopup="true" aria-controls="sudu-floating-controls" aria-expanded="false">科目 <span aria-hidden="true">⌄</span></button>'
  +'<button type="button" class="sudu-controls-trigger" data-sudu-menu-trigger="functions" aria-haspopup="true" aria-controls="sudu-floating-controls" aria-expanded="false">個人學習 Dashboard <span aria-hidden="true">⌄</span></button>'
  +'</div><div class="sudu-header-tools" role="group" aria-label="紀錄與外觀"><button type="button" id="sudu-theme-button" aria-label="切換深色主題" title="切換深色主題"><span aria-hidden="true">☾</span></button></div>';
 const exportControl=head.querySelector("#export");
 head.append(actions);
 if(exportControl){
  exportControl.innerHTML='<span aria-hidden="true">⇩</span>';exportControl.setAttribute("aria-label","匯出學習紀錄備份");exportControl.title="匯出學習紀錄備份";
  actions.querySelector(".sudu-header-tools").prepend(exportControl);
 }
 const float=document.createElement("nav");
 float.id="sudu-floating-controls";
 float.setAttribute("aria-hidden","true");
 float.setAttribute("aria-label","統測速讀導覽選單");
 float.dataset.closeDelay="0";
 float.inert=true;
 const inner=document.createElement("div");inner.className="floating-inner";
 inner.innerHTML='<div class="sudu-mega-heading"><div><span class="mega-eyebrow">7581707 · STUDY NAVIGATION</span><h2 id="sudu-menu-title">選擇年度</h2></div><button id="sudu-mega-close" class="sudu-mega-close" type="button" aria-label="收起選單">✕</button></div>'
  +'<section class="sudu-menu-section" data-sudu-menu-section="year"><span class="mega-eyebrow">01 / YEAR</span><div class="sudu-year-filters"></div><p class="sudu-menu-help">90～115 學年度；自編練習另行標示。試卷請在「科目」選單挑選。</p></section>'
  +'<section class="sudu-menu-section" data-sudu-menu-section="subject"><span class="mega-eyebrow">02 / PAPER & SUBJECT</span><div class="sudu-subject-filters"></div><p class="sudu-menu-help">試卷與科目依該年度已收錄資料提供，選取後返回逐題學習。</p></section>'
  +'<section class="sudu-menu-section" data-sudu-menu-section="functions"><span class="mega-eyebrow">03 / PERSONAL LEARNING</span><div class="sudu-functions-tabs"></div><div class="sudu-functions-utilities"><button type="button" id="sudu-menu-settings">裝置學習代碼與個人設定</button><button type="button" id="sudu-theme-in-menu">☾ 切換深色主題</button><button type="button" id="sudu-menu-backup">↓ 備份學習紀錄</button><button type="button" id="sudu-menu-restore">↑ 還原學習紀錄</button></div><p class="sudu-menu-help"><span id="sudu-miniprofile"></span><br>學習代碼只辨識此瀏覽器，跨裝置請使用備份或經同意啟用的同步服務。</p></section>';
 float.append(inner);
 const filterin=filter.querySelector(".filterin");
 if(!filterin)throw Error("Course filtering controls are missing");
 const yearLabel=filterin.querySelector('label:has(#year)');
 const paperLabel=filterin.querySelector('label:has(#paper)');
 const subjectLabel=filterin.querySelector('label:has(#subject)');
 const status=filterin.querySelector("#status");
 if(!yearLabel||!paperLabel||!subjectLabel)throw Error("Year, paper, or subject is missing");
 const yearHolder=inner.querySelector(".sudu-year-filters");
 const subjectHolder=inner.querySelector(".sudu-subject-filters");
 yearHolder.append(yearLabel);
 if(status)yearHolder.append(status);
 subjectHolder.append(paperLabel,subjectLabel);
 tabs.querySelectorAll('[data-tab="archive"],[data-tab="source"]').forEach(button=>button.remove());
 if(!tabs.querySelector('[data-tab="mistakes"]')){const b=document.createElement("button");b.type="button";b.dataset.tab="mistakes";tabs.append(b);}
 const tabLabels={learn:"返回逐題學習",dashboard:"我的 Dashboard",clinic:"首次答錯複習",mistakes:"全部曾答錯題目"};
 for(const button of tabs.querySelectorAll("[data-tab]")){button.textContent=tabLabels[button.dataset.tab]||button.textContent;button.onclick=()=>switchTab(button.dataset.tab);}
 inner.querySelector(".sudu-functions-tabs").append(tabs);
 filter.remove();
 head.parentNode.insertAdjacentElement("afterend",float);
 const bridge=document.createElement("div");bridge.id="sudu-menu-bridge";bridge.setAttribute("aria-hidden","true");document.body.append(bridge);
 for(const tab of tabs.querySelectorAll("[data-tab]")){
  tab.dataset.menuNumber=({learn:"01",dashboard:"02",clinic:"03",archive:"04",source:"05"})[tab.dataset.tab]||"";
 }
 const returnButton=document.createElement("button");
 returnButton.id="sudu-return-to-question";
 returnButton.type="button";
 returnButton.setAttribute("aria-label","回到目前題目");
 returnButton.setAttribute("title","回到題目");
 returnButton.innerHTML='<span class="return-icon" aria-hidden="true">↑</span><span class="return-label">回題目</span>';
 returnButton.hidden=true;
 returnButton.addEventListener("click",suduGoToQuestion);
 document.body.append(returnButton);
 window.addEventListener("scroll",suduUpdateReturnButton,{passive:true});
 const workbar=document.createElement("div");workbar.id="sudu-workbar";
 workbar.innerHTML='<span class="work-current" id="sudu-current-selection">學習中</span><button type="button" id="sudu-toggle-drag" title="顯示排序手把">↕ 區塊排序</button><button type="button" id="sudu-reset-drag">恢復預設排序</button>';
 const intro=wrap.querySelector(".intro");if(intro)intro.insertAdjacentElement("afterend",workbar);else wrap.prepend(workbar);
 const triggers=suduMenuTriggers();
 const titles={year:"挑選學年度",subject:"挑選試卷與科目",functions:"個人學習 Dashboard"};
 const enter=kind=>{
  if(suduMenuPinned&&kind!==suduMenuActive)suduMenuPinned=false;
  inner.querySelector("#sudu-menu-title").textContent=titles[kind];
  suduSetMenu(true,kind);
 };
 const immediateClose=()=>{
  suduMenuPinned=false;
  suduSetMenu(false);
 };
 for(const trigger of triggers){
  const kind=trigger.dataset.suduMenuTrigger;
  trigger.addEventListener("pointerenter",e=>{if(e.pointerType!=="touch")enter(kind);});
  trigger.addEventListener("pointerleave",suduScheduleMenuClose);
  trigger.addEventListener("focusin",()=>{if(!suduSuppressFocusReopen)enter(kind);});
  trigger.addEventListener("focusout",e=>{if(!suduInMenuRegion(e.relatedTarget))immediateClose();});
  trigger.addEventListener("keydown",e=>{
   if(e.key==="ArrowDown"||(e.key==="Tab"&&!e.shiftKey&&trigger.getAttribute("aria-expanded")==="true")){
    e.preventDefault();enter(kind);inner.querySelector('[data-sudu-menu-section="'+kind+'"]')?.querySelector('select,button,a[href]')?.focus({preventScroll:true});
   }
  });
  trigger.addEventListener("click",e=>{
   e.stopPropagation();
   if(suduMenuPinned&&suduMenuActive===kind){immediateClose();return;}
   suduMenuPinned=true;enter(kind);
  });
 }
 float.addEventListener("pointerleave",suduScheduleMenuClose);
 bridge.addEventListener("pointerleave",suduScheduleMenuClose);
 float.addEventListener("focusout",e=>{
  if(!suduInMenuRegion(e.relatedTarget))immediateClose();
 });
 float.addEventListener("change",e=>{
  if(["year","paper","subject"].includes(e.target.id)){if(ui.tab!=="learn")switchTab("learn");immediateClose();}
 });
 float.addEventListener("click",e=>{
  if(e.target.closest("[data-tab]"))immediateClose();
 });
 inner.querySelector("#sudu-mega-close").addEventListener("click",immediateClose);
 document.addEventListener("click",e=>{
  if(!float.contains(e.target)&&!triggers.some(b=>b.contains(e.target)))immediateClose();
 });
 document.addEventListener("keydown",e=>{
  if(e.key==="Escape"&&float.classList.contains("open")){
   const current=triggers.find(b=>b.dataset.suduMenuTrigger===suduMenuActive);
   immediateClose();suduSuppressFocusReopen=true;
   current?.focus({preventScroll:true});suduSuppressFocusReopen=false;
  }
 });
 const toggleTheme=()=>suduTheme(document.documentElement.dataset.suduTheme==="dark"?"light":"dark");
 document.getElementById("sudu-theme-button").addEventListener("click",toggleTheme);
 inner.querySelector("#sudu-theme-in-menu").addEventListener("click",toggleTheme);
 inner.querySelector("#sudu-menu-backup").addEventListener("click",()=>document.getElementById("export")?.click());
 inner.querySelector("#sudu-menu-restore").addEventListener("click",()=>{document.getElementById("db-import-file")?.click();immediateClose();});
 inner.querySelector("#sudu-menu-settings").addEventListener("click",()=>{switchTab("dashboard");immediateClose();requestAnimationFrame(()=>{const field=document.getElementById("db-nickname");field?.scrollIntoView({block:"center",behavior:suduScrollBehavior()});field?.focus({preventScroll:true});});});
 document.getElementById("sudu-toggle-drag").addEventListener("click",()=>{
  const yes=document.body.classList.toggle("sudu-layout-edit");
  document.getElementById("sudu-toggle-drag").classList.toggle("active",yes);
  document.getElementById("sudu-toggle-drag").setAttribute("aria-pressed",String(yes));render();
 });
 document.getElementById("sudu-reset-drag").addEventListener("click",()=>{suduLayoutOrder=[];suduSaveLayout();render()});
 suduTheme(theme);
 suduUpdateMini();
 const geometry=()=>{suduUpdateHeaderHeight();suduMeasureDock();if(float.classList.contains("open"))suduPositionMenu(suduMenuActive);};
 window.addEventListener("resize",geometry,{passive:true});window.visualViewport?.addEventListener("resize",geometry,{passive:true});
 if(typeof ResizeObserver!=="undefined"){const observer=new ResizeObserver(geometry);observer.observe(document.querySelector(".header"));}
 geometry();
}
function suduUpdateMini(){
 const t=document.getElementById("sudu-current-selection");
 if(t&&typeof ui!=="undefined")t.textContent=(ui.year==="自編"?"自編練習":ui.year+" 年")+" · "+(ui.subject==="全部科目"?"全部科目":ui.subject)+" · "+(typeof paperText!=="undefined"?(paperText[ui.paper]||ui.paper):ui.paper);
 const name=document.getElementById("sudu-miniprofile");
 if(name&&typeof suduDevice!=="undefined"&&suduDevice)name.textContent=suduDevice.name+" · "+suduDevice.id.slice(-8);
}
function suduWorkspaceApply(){
 suduUpdateMini();
 const learning=typeof ui!=="undefined"&&ui.tab==="learn";
 const workbar=document.getElementById("sudu-workbar");if(workbar)workbar.hidden=!learning;
 const screen=document.getElementById("screen");
 suduBuildQuestionDock(screen);
 suduUpdateReturnButton();
 if(!learning){suduAnswerJumped=false;return;}
 if(!screen||screen.querySelector("#sudu-workspace"))return;
 const current=typeof available==="function"?available()[ui.index]:null;
 if(current?.id!==suduRenderedQuestionId){suduAnswerJumped=false;suduRenderedQuestionId=current?.id||null;}
 const raw=[...screen.children];
 const blue=raw.find(x=>x.classList.contains("blue"));
 const orange=raw.find(x=>x.classList.contains("orange"));
 const green=raw.find(x=>x.classList.contains("green"));
 const source=raw.find(x=>x.classList.contains("sourcebox"));
 if(!blue||!orange||!green||!source)return;
 const answer=orange.querySelector(".resultbox");
 if(answer){
  answer.classList.add("sudu-answer-box");
  orange.removeChild(answer);
 }
 const els={question:blue,answer,explanation:orange,extension:green,source};
 const keys=["question","answer","explanation","extension","source"].filter(x=>els[x]);
 const defaults=["question","answer","explanation","extension","source"];
 const saved=[...suduLayoutOrder.filter(x=>keys.includes(x)),...defaults.filter(x=>keys.includes(x)&&!suduLayoutOrder.includes(x))];
 const priority=Boolean(answer||orange.dataset.answered==="true");
 const fixed=priority?["question","answer","explanation"].filter(x=>keys.includes(x)):[];
 const order=priority?[...fixed,...saved.filter(x=>!fixed.includes(x))]:saved;
 const box=document.createElement("div");box.id="sudu-workspace";
 box.dataset.answerPriority=String(priority);
 let notice=document.getElementById("sudu-layout-notice");
 if(!notice&&workbar){notice=document.createElement("p");notice.id="sudu-layout-notice";notice.textContent="作答後固定先讀題目、正確答案與白話解說；自訂順序仍保存。此時可調整延伸／來源順序，完整排序可在未作答題目設定。";workbar.append(notice);}
 if(notice)notice.hidden=!(priority&&document.body.classList.contains("sudu-layout-edit"));
 screen.insertBefore(box,blue);
 for(const key of order){
  const outer=document.createElement("div");outer.className="study-section";outer.dataset.block=key;outer.draggable=document.body.classList.contains("sudu-layout-edit")&&!fixed.includes(key);
  const tools=document.createElement("div");tools.className="study-dragbar";
  const names={question:"題目",answer:"正確答案",explanation:"白話解說",extension:"延伸觀念",source:"教材出處"};
  tools.innerHTML='<button type="button" class="sudu-move-up" aria-label="將'+names[key]+'上移">↑ 上移</button><button type="button" class="sudu-move-down" aria-label="將'+names[key]+'下移">↓ 下移</button><button type="button" class="sudu-drag-handle" title="按住滑鼠拖拉">⠿ 拖拉</button>';
  if(!document.body.classList.contains("sudu-layout-edit"))tools.hidden=true;
  if(fixed.includes(key))tools.querySelectorAll("button").forEach(button=>{button.disabled=true;button.title="作答後優先顯示，自訂順序仍保存";});
  outer.append(tools,els[key]);box.append(outer);
  tools.querySelector(".sudu-move-up").onclick=()=>suduMoveBlock(key,-1);
  tools.querySelector(".sudu-move-down").onclick=()=>suduMoveBlock(key,1);
  outer.addEventListener("dragstart",e=>{if(!outer.draggable){e.preventDefault();return}e.dataTransfer.setData("text/plain",key);e.dataTransfer.effectAllowed="move";outer.classList.add("sudu-dragging")});
  outer.addEventListener("dragend",()=>{outer.classList.remove("sudu-dragging");box.querySelectorAll(".sudu-drop-target").forEach(y=>y.classList.remove("sudu-drop-target"))});
  outer.addEventListener("dragover",e=>{if(!fixed.includes(key)){e.preventDefault();outer.classList.add("sudu-drop-target");}});
  outer.addEventListener("dragleave",()=>outer.classList.remove("sudu-drop-target"));
  outer.addEventListener("drop",e=>{e.preventDefault();const k=e.dataTransfer.getData("text/plain");if(keys.includes(k)&&k!==key&&!fixed.includes(k)&&!fixed.includes(key)){suduArrange(k,key);suduSaveLayout();render()}});
 }
 suduUpdateReturnButton();
}
function suduMoveBlock(key,delta){
 const all=[...document.querySelectorAll("#sudu-workspace > .study-section")].map(x=>x.dataset.block);
 const i=all.indexOf(key),j=i+delta;if(i<0||j<0||j>=all.length)return;
 const priority=document.getElementById("sudu-workspace")?.dataset.answerPriority==="true";
 if(priority&&[key,all[j]].some(k=>["question","answer","explanation"].includes(k)))return;
 [all[i],all[j]]=[all[j],all[i]];
 if(priority){
  const saved=[...suduLayoutOrder,...["question","answer","explanation","extension","source"].filter(k=>!suduLayoutOrder.includes(k))];
  const tail=all.filter(k=>["extension","source"].includes(k));let n=0;
  suduLayoutOrder=saved.map(k=>["extension","source"].includes(k)?tail[n++]:k);
 }else suduLayoutOrder=all;
 suduSaveLayout();render();
}
function suduArrange(source,target){
 const all=[...suduLayoutOrder,...["question","answer","explanation","extension","source"].filter(k=>!suduLayoutOrder.includes(k))];
 const i=all.indexOf(source),j=all.indexOf(target);if(i<0||j<0)return;
 all.splice(i,1);all.splice(j,0,source);suduLayoutOrder=all;
}

let suduAnswerJumped=false;
/* Scroll to the explanation immediately after a submitted, validated answer. */
function suduScrollBehavior(){
 return window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth";
}
function suduExplanationTarget(){
 return document.querySelector('#sudu-workspace > [data-block="answer"]')
     || document.querySelector('#sudu-workspace > [data-block="explanation"]')
     || document.querySelector('#screen .section.orange');
}
function suduGoToExplanation(){
 if(typeof ui!=="undefined"&&ui.tab!=="learn")return;
 suduAnswerJumped=true;
 requestAnimationFrame(()=>{
  const target=suduExplanationTarget();
  if(!target)return;
  suduScrollReadingTarget(target);
  suduUpdateReturnButton();
 });
}
function suduGoToQuestion(){
 if(typeof ui!=="undefined"&&ui.tab!=="learn")return;
 suduAnswerJumped=false;
 suduUpdateReturnButton();
 const target=document.querySelector('#sudu-workspace > [data-block="question"]')
   || document.querySelector('#screen .section.blue');
 if(!target)return;
 suduScrollReadingTarget(target);
}
function suduUpdateReturnButton(){
 const button=document.getElementById("sudu-return-to-question");
 if(!button)return;
 const target=document.querySelector('#sudu-workspace > [data-block="question"]')
   || document.querySelector('#screen .section.blue');
 const inStudy=typeof ui!=="undefined"&&ui.tab==="learn";
 const pastQuestion=target&&target.getBoundingClientRect().bottom<(document.querySelector(".header")?.getBoundingClientRect().height||0)+35;
 button.hidden=!(inStudy&&(pastQuestion||suduAnswerJumped));
}

let suduDockObserver=null;
let suduRenderedQuestionId=null;
function suduUpdateHeaderHeight(){document.documentElement.style.setProperty("--sudu-header-height",Math.ceil(document.querySelector(".header")?.getBoundingClientRect().height||0)+"px");}
function suduScrollReadingTarget(target){
 if(!target)return;suduUpdateHeaderHeight();suduMeasureDock();
 const top=target.getBoundingClientRect().top+window.scrollY-(document.querySelector(".header")?.getBoundingClientRect().height||0)-12;
 window.scrollTo({top:Math.max(0,top),behavior:suduScrollBehavior()});
}
function suduQuestionStatus(question){
 const events=[...(Array.isArray(state.attempts?.[question.id])?state.attempts[question.id]:[]),...(Array.isArray(state.reviewHistory?.[question.id])?state.reviewHistory[question.id]:[])];
 if(state.reviewAnswers?.[question.id])events.push(state.reviewAnswers[question.id]);
 const answered=events.filter(item=>Number.isInteger(item?.choice)&&item.choice>=0);
 if(!answered.length)return {key:"unanswered",label:"未答"};
 if(question.official&&(question.answerVerified!==true||question.questionVerified!==true))return {key:"pending",label:"已作答，答案待核對"};
 const graded=answered.filter(item=>typeof item.correct==="boolean").map((item,index)=>({item,index,time:Date.parse(item.at)||0}));
 graded.sort((a,b)=>a.time-b.time||a.index-b.index);const last=graded.at(-1)?.item;
 if(!last)return {key:"pending",label:"已作答，判分待核對"};
 return last.correct?{key:"correct",label:"最近有效判分答對"}:{key:"incorrect",label:"最近有效判分答錯"};
}
function suduMeasureDock(){
 const dock=document.getElementById("sudu-question-dock");
 document.documentElement.style.setProperty("--sudu-dock-height",Math.ceil(dock&&!dock.hidden?dock.getBoundingClientRect().height:0)+"px");
}
function suduBuildQuestionDock(screen){
 // Leave the existing dock alone on a second apply without render().
 if(screen?.querySelector("#sudu-workspace")&&ui.tab==="learn"){suduMeasureDock();return;}
 suduDockObserver?.disconnect();document.getElementById("sudu-question-dock")?.remove();
 const items=typeof available==="function"?available():[],navigation=screen?.querySelector(".questionnav");
 const active=typeof ui!=="undefined"&&ui.tab==="learn"&&items.length>0&&navigation;
 document.body.classList.toggle("sudu-has-question-dock",Boolean(active));
 if(!active){suduMeasureDock();return;}
 const dock=document.createElement("aside");dock.id="sudu-question-dock";dock.setAttribute("aria-label","逐題學習導覽");
 navigation.classList.add("sudu-floating-questionnav");navigation.classList.remove("sudu-inline-questionnav");dock.append(navigation);
 const legend=document.createElement("p");legend.className="sudu-question-legend";legend.textContent="題號可跳題 · ✓ 答對 · × 答錯 · ? 待核對 · 白色未答";dock.append(legend);
 const grid=document.createElement("div");grid.className="sudu-question-grid";grid.setAttribute("role","group");grid.setAttribute("aria-label","本次科目篩選的全部題號");
 items.forEach((question,index)=>{
  const button=document.createElement("button"),status=suduQuestionStatus(question);
  const originalKnown=question.official&&Number.isInteger(Number(question.number))&&Number(question.number)>0;
  const number=originalKnown?String(question.number):String(index+1);
  button.type="button";button.className="sudu-question-ball";button.dataset.questionId=question.id;button.dataset.filteredIndex=String(index);button.dataset.status=status.key;button.textContent=number;
  if(question.official)button.dataset.originalNumber=String(question.number??"");
  const prefix=originalKnown?"原卷第 "+number+" 題；":question.official?"原卷題號待核對；":"自編第 "+number+" 題；";
  const label=prefix+"篩選後第 "+(index+1)+"／"+items.length+" 題；"+(question.subject||"")+"；"+status.label+(index===ui.index?"；目前題目":"");
  button.setAttribute("aria-label",label);button.title=label;if(index===ui.index)button.setAttribute("aria-current","step");
  button.addEventListener("click",()=>{
   const resolved=available().findIndex(item=>item.id===question.id);if(resolved<0)return;
   ui.index=resolved;save();render();document.querySelector('.sudu-question-ball[data-filtered-index="'+resolved+'"]')?.focus({preventScroll:true});suduGoToQuestion();
  });grid.append(button);
 });
 dock.append(grid);document.body.append(dock);
 if(typeof ResizeObserver!=="undefined"){suduDockObserver=new ResizeObserver(suduMeasureDock);suduDockObserver.observe(dock);}
 suduMeasureDock();
}
