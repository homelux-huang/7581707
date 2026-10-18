
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
}
function suduSetMenu(open){
 const panel=document.getElementById("sudu-floating-controls"),trigger=document.getElementById("sudu-controls-button");
 if(!panel||!trigger)return;
 panel.classList.toggle("open",Boolean(open));
 trigger.setAttribute("aria-expanded",String(Boolean(open)));
 panel.setAttribute("aria-hidden",String(!open));
}
function suduWorkspaceInit(){
 suduReadLayout();
 let theme="light";try{theme=localStorage.getItem(SUDU_THEME_KEY)||"light"}catch(e){}
 const head=document.querySelector(".header .head");
 const filter=document.querySelector(".filters");
 const tabs=document.querySelector(".tabs");
 const wrap=document.querySelector(".wrap");
 if(!head||!filter||!tabs||!wrap)return;
 const old=document.getElementById("sudu-floating-controls");
 if(old)return;
 const actions=document.createElement("div");actions.className="sudu-head-actions";
 actions.innerHTML='<span id="sudu-miniprofile">進入後自動恢復學習紀錄</span><button type="button" id="sudu-theme-button" aria-label="切換主題">☾ 深色</button><button type="button" class="sudu-controls-trigger" id="sudu-controls-button" aria-haspopup="true" aria-controls="sudu-floating-controls" aria-expanded="false">☰ 年度・科目・功能 ▾</button>';
 head.append(actions);
 const float=document.createElement("div");float.id="sudu-floating-controls";float.setAttribute("aria-hidden","true");
 const inner=document.createElement("div");inner.className="floating-inner";
 float.append(inner);
 inner.append(filter,tabs);
 head.parentNode.insertAdjacentElement("afterend",float);
 const workbar=document.createElement("div");workbar.id="sudu-workbar";
 workbar.innerHTML='<span class="work-current" id="sudu-current-selection">學習中</span><button type="button" id="sudu-toggle-drag" title="顯示排序手把">↕ 區塊排序</button><button type="button" id="sudu-reset-drag">恢復預設排序</button>';
 const intro=wrap.querySelector(".intro");if(intro)intro.insertAdjacentElement("afterend",workbar);else wrap.prepend(workbar);
 const trigger=document.getElementById("sudu-controls-button");
 trigger.addEventListener("click",e=>{e.stopPropagation();suduMenuPinned=!suduMenuPinned;suduSetMenu(suduMenuPinned)});
 trigger.addEventListener("mouseenter",()=>suduSetMenu(true));
 float.addEventListener("mouseenter",()=>suduSetMenu(true));
 const close=()=>{if(!suduMenuPinned)suduSetMenu(false)};
 trigger.addEventListener("mouseleave",e=>{if(!float.contains(e.relatedTarget))close()});
 float.addEventListener("mouseleave",e=>{if(e.relatedTarget!==trigger)close()});
 document.addEventListener("click",e=>{if(!float.contains(e.target)&&!trigger.contains(e.target)){suduMenuPinned=false;suduSetMenu(false)}});
 document.addEventListener("keydown",e=>{if(e.key==="Escape"){suduMenuPinned=false;suduSetMenu(false);trigger.focus()}});
 float.addEventListener("change",e=>{if(["year","paper","subject"].includes(e.target.id)){suduMenuPinned=false;suduSetMenu(false)}});
 float.addEventListener("click",e=>{if(e.target.closest("[data-tab]")){suduMenuPinned=false;suduSetMenu(false)}});
 document.getElementById("sudu-theme-button").addEventListener("click",()=>suduTheme(document.documentElement.dataset.suduTheme==="dark"?"light":"dark"));
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
