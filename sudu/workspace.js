
/* Personalized, local-only layout and theme. Works with pointer drag, keyboard buttons and touch menu. */
const SUDU_LAYOUT_KEY="sudu_layout_order_v1";
const SUDU_THEME_KEY="sudu_theme_v1";
let suduLayoutOrder=[];
let suduMenuPinned=false;
function suduReadLayout(){
 try{const x=JSON.parse(localStorage.getItem(SUDU_LAYOUT_KEY)||"[]");if(Array.isArray(x))suduLayoutOrder=x.filter(v=>["question","answer","explanation","extension","source"].includes(v));}catch(e){}
}
function suduSaveLayout(){try{localStorage.setItem(SUDU_LAYOUT_KEY,JSON.stringify(suduLayoutOrder))}catch(e){}}
function suduTheme(next){
 const valid=next==="dark"?"dark":"light";
 document.documentElement.dataset.suduTheme=valid;
 try{localStorage.setItem(SUDU_THEME_KEY,valid)}catch(e){}
 const b=document.getElementById("sudu-theme-button");
 if(b){b.textContent=valid==="dark"?"☀ 淺色":"☾ 深色";b.setAttribute("aria-label",valid==="dark"?"切換淺色主題":"切換深色主題");}
 const menuTheme=document.getElementById("sudu-theme-in-menu");if(menuTheme)menuTheme.textContent=valid==="dark"?"☀ 切換淺色主題":"☾ 切換深色主題";
}

/* Three independent Apple-inspired popout menus: 年度、科目、功能. */
const SUDU_MENU_TYPES=["year","subject","functions"];
let suduMenuCloseTimer=null;
let suduMenuActive=null;
let suduSuppressFocusReopen=false;
function suduCancelMenuClose(){
 if(suduMenuCloseTimer!==null){clearTimeout(suduMenuCloseTimer);suduMenuCloseTimer=null;}
}
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
}
function suduSetMenu(open,kind=suduMenuActive||"year"){
 const panel=document.getElementById("sudu-floating-controls");
 if(!panel)return;
 if(open && !SUDU_MENU_TYPES.includes(kind))return;
 if(open){suduCancelMenuClose();suduMenuActive=kind;suduPositionMenu(kind);}
 panel.dataset.activeMenu=open?kind:"";
 panel.classList.toggle("open",Boolean(open));
 panel.setAttribute("aria-hidden",String(!open));
 panel.inert=!open;
 for(const trigger of suduMenuTriggers()){
  const isActive=Boolean(open)&&trigger.dataset.suduMenuTrigger===kind;
  trigger.setAttribute("aria-expanded",String(isActive));
  trigger.classList.toggle("is-active",isActive);
 }
}
function suduScheduleMenuClose(){
 suduCancelMenuClose();
 if(suduMenuPinned)return;
 suduMenuCloseTimer=setTimeout(()=>{
  suduMenuCloseTimer=null;
  if(!suduMenuPinned)suduSetMenu(false);
 },1000);
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
 actions.innerHTML='<span id="sudu-miniprofile">自動恢復學習紀錄</span>'
  +'<button type="button" id="sudu-theme-button" aria-label="切換主題">☾ 深色</button>'
  +'<div class="sudu-header-triggers" role="group" aria-label="學習平台導覽">'
  +'<button type="button" class="sudu-controls-trigger" data-sudu-menu-trigger="year" aria-haspopup="true" aria-controls="sudu-floating-controls" aria-expanded="false">年度 <span aria-hidden="true">⌄</span></button>'
  +'<button type="button" class="sudu-controls-trigger" data-sudu-menu-trigger="subject" aria-haspopup="true" aria-controls="sudu-floating-controls" aria-expanded="false">科目 <span aria-hidden="true">⌄</span></button>'
  +'<button type="button" class="sudu-controls-trigger" data-sudu-menu-trigger="functions" aria-haspopup="true" aria-controls="sudu-floating-controls" aria-expanded="false">功能 <span aria-hidden="true">⌄</span></button>'
  +'</div>';
 head.append(actions);
 const float=document.createElement("nav");
 float.id="sudu-floating-controls";
 float.setAttribute("aria-hidden","true");
 float.setAttribute("aria-label","統測速讀導覽選單");
 float.inert=true;
 const inner=document.createElement("div");inner.className="floating-inner";
 inner.innerHTML='<div class="sudu-mega-heading"><div><span class="mega-eyebrow">7581707 · STUDY NAVIGATION</span><h2 id="sudu-menu-title">選擇年度</h2></div><button id="sudu-mega-close" class="sudu-mega-close" type="button" aria-label="收起選單">✕</button></div>'
  +'<section class="sudu-menu-section" data-sudu-menu-section="year"><span class="mega-eyebrow">01 / YEAR & EXAM</span><div class="sudu-year-filters"></div><p class="sudu-menu-help">選擇年份與試卷後自動切換考題。</p></section>'
  +'<section class="sudu-menu-section" data-sudu-menu-section="subject"><span class="mega-eyebrow">02 / SUBJECT</span><div class="sudu-subject-filters"></div><p class="sudu-menu-help">依試卷挑選會計學、經濟學或其他科目。</p></section>'
  +'<section class="sudu-menu-section" data-sudu-menu-section="functions"><span class="mega-eyebrow">03 / LEARNING TOOLS</span><div class="sudu-functions-tabs"></div><div class="sudu-functions-utilities"><button type="button" id="sudu-theme-in-menu">☾ 切換深色主題</button><button type="button" id="sudu-menu-backup">↓ 備份學習紀錄</button></div><p class="sudu-menu-help">選擇學習頁面、查看錯題，或備份作答紀錄。</p></section>';
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
 yearHolder.append(yearLabel,paperLabel);
 if(status)yearHolder.append(status);
 subjectHolder.append(subjectLabel);
 inner.querySelector(".sudu-functions-tabs").append(tabs);
 filter.remove();
 head.parentNode.insertAdjacentElement("afterend",float);
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
 const titles={year:"挑選學年度",subject:"挑選考試科目",functions:"學習功能"};
 const enter=kind=>{
  if(suduMenuPinned&&kind!==suduMenuActive)suduMenuPinned=false;
  inner.querySelector("#sudu-menu-title").textContent=titles[kind];
  suduSetMenu(true,kind);
 };
 const immediateClose=()=>{
  suduMenuPinned=false;
  suduCancelMenuClose();
  suduSetMenu(false);
 };
 for(const trigger of triggers){
  const kind=trigger.dataset.suduMenuTrigger;
  trigger.addEventListener("mouseenter",()=>enter(kind));
  trigger.addEventListener("mouseleave",suduScheduleMenuClose);
  trigger.addEventListener("focusin",()=>{if(!suduSuppressFocusReopen)enter(kind);});
  trigger.addEventListener("click",e=>{
   e.stopPropagation();
   if(suduMenuPinned&&suduMenuActive===kind){immediateClose();return;}
   suduMenuPinned=true;enter(kind);
  });
 }
 float.addEventListener("mouseenter",suduCancelMenuClose);
 float.addEventListener("mouseleave",suduScheduleMenuClose);
 float.addEventListener("focusin",suduCancelMenuClose);
 float.addEventListener("focusout",e=>{
  if(!float.contains(e.relatedTarget)&&!triggers.includes(e.relatedTarget))suduScheduleMenuClose();
 });
 float.addEventListener("change",e=>{
  if(["year","paper","subject"].includes(e.target.id))immediateClose();
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
 window.addEventListener("resize",()=>{
  if(float.classList.contains("open"))suduPositionMenu(suduMenuActive);
 },{passive:true});
 const toggleTheme=()=>suduTheme(document.documentElement.dataset.suduTheme==="dark"?"light":"dark");
 document.getElementById("sudu-theme-button").addEventListener("click",toggleTheme);
 inner.querySelector("#sudu-theme-in-menu").addEventListener("click",toggleTheme);
 inner.querySelector("#sudu-menu-backup").addEventListener("click",()=>document.getElementById("export")?.click());
 document.getElementById("sudu-toggle-drag").addEventListener("click",()=>{
  const yes=document.body.classList.toggle("sudu-layout-edit");
  document.getElementById("sudu-toggle-drag").classList.toggle("active",yes);
  suduWorkspaceApply();
 });
 document.getElementById("sudu-reset-drag").addEventListener("click",()=>{suduLayoutOrder=[];suduSaveLayout();render()});
 suduTheme(theme);
 suduUpdateMini();
}
function suduUpdateMini(){
 const t=document.getElementById("sudu-current-selection");
 if(t&&typeof ui!=="undefined")t.textContent=(ui.year==="自編"?"自編練習":ui.year+" 年")+" · "+(ui.subject==="全部科目"?"全部科目":ui.subject)+" · "+(typeof paperText!=="undefined"?(paperText[ui.paper]||ui.paper):ui.paper);
 const name=document.getElementById("sudu-miniprofile");
 if(name&&typeof suduDevice!=="undefined"&&suduDevice)name.textContent=suduDevice.name+" · "+suduDevice.id.slice(-8);
}
function suduWorkspaceApply(){
 suduUpdateMini();
 suduUpdateReturnButton();
 if(typeof ui==="undefined"||ui.tab!=="learn")return;
 const screen=document.getElementById("screen");if(!screen)return;
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
  const h=answer.querySelector("h2");if(h)h.textContent="✅ 正確答案";
 }
 const els={question:blue,answer,explanation:orange,extension:green,source};
 const keys=["question","answer","explanation","extension","source"].filter(x=>els[x]);
 const defaults=["question","answer","explanation","extension","source"];
 const order=[...suduLayoutOrder.filter(x=>keys.includes(x)),...defaults.filter(x=>keys.includes(x)&&!suduLayoutOrder.includes(x))];
 const box=document.createElement("div");box.id="sudu-workspace";
 screen.insertBefore(box,blue);
 for(const key of order){
  const outer=document.createElement("div");outer.className="study-section";outer.dataset.block=key;outer.draggable=document.body.classList.contains("sudu-layout-edit");
  const tools=document.createElement("div");tools.className="study-dragbar";
  const names={question:"題目",answer:"正確答案",explanation:"白話解說",extension:"延伸觀念",source:"教材出處"};
  tools.innerHTML='<button type="button" class="sudu-move-up" aria-label="將'+names[key]+'上移">↑ 上移</button><button type="button" class="sudu-move-down" aria-label="將'+names[key]+'下移">↓ 下移</button><button type="button" class="sudu-drag-handle" title="按住滑鼠拖拉">⠿ 拖拉</button>';
  if(!document.body.classList.contains("sudu-layout-edit"))tools.hidden=true;
  outer.append(tools,els[key]);box.append(outer);
  tools.querySelector(".sudu-move-up").onclick=()=>suduMoveBlock(key,-1);
  tools.querySelector(".sudu-move-down").onclick=()=>suduMoveBlock(key,1);
  outer.addEventListener("dragstart",e=>{if(!document.body.classList.contains("sudu-layout-edit")){e.preventDefault();return}e.dataTransfer.setData("text/plain",key);e.dataTransfer.effectAllowed="move";outer.classList.add("sudu-dragging")});
  outer.addEventListener("dragend",()=>{outer.classList.remove("sudu-dragging");box.querySelectorAll(".sudu-drop-target").forEach(y=>y.classList.remove("sudu-drop-target"))});
  outer.addEventListener("dragover",e=>{e.preventDefault();outer.classList.add("sudu-drop-target")});
  outer.addEventListener("dragleave",()=>outer.classList.remove("sudu-drop-target"));
  outer.addEventListener("drop",e=>{e.preventDefault();const k=e.dataTransfer.getData("text/plain");if(k&&k!==key){suduArrange(k,key);suduSaveLayout();render()}});
 }
 suduUpdateReturnButton();
}
function suduMoveBlock(key,delta){
 const all=[...document.querySelectorAll("#sudu-workspace > .study-section")].map(x=>x.dataset.block);
 const i=all.indexOf(key),j=i+delta;if(i<0||j<0||j>=all.length)return;
 [all[i],all[j]]=[all[j],all[i]];
 suduLayoutOrder=all;suduSaveLayout();render();
}
function suduArrange(source,target){
 const all=[...document.querySelectorAll("#sudu-workspace > .study-section")].map(x=>x.dataset.block);
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
  target.scrollIntoView({behavior:suduScrollBehavior(),block:"start"});
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
 target.scrollIntoView({behavior:suduScrollBehavior(),block:"start"});
}
function suduUpdateReturnButton(){
 const button=document.getElementById("sudu-return-to-question");
 if(!button)return;
 const target=document.querySelector('#sudu-workspace > [data-block="question"]')
   || document.querySelector('#screen .section.blue');
 const inStudy=typeof ui!=="undefined"&&ui.tab==="learn";
 const pastQuestion=target&&target.getBoundingClientRect().bottom<Math.max(95,window.innerHeight*.22);
 button.hidden=!(inStudy&&(pastQuestion||suduAnswerJumped));
}
