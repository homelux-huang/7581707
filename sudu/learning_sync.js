/* Student-controlled opt-in sync. No student data leaves the browser without consent. */
(function(root){
"use strict";
const KEY="sudu_student_sync_optin_v1";let timer=null;
function read(){try{return JSON.parse(localStorage.getItem(KEY)||"null")}catch{return null}}
function store(data){localStorage.setItem(KEY,JSON.stringify(data))}
function base(raw){
 const u=new URL(raw),loopback=["localhost","127.0.0.1","[::1]"].includes(u.hostname);
 if(u.username||u.password)throw Error("API 網址不可含帳密");
 if(u.protocol!=="https:"&&!(u.protocol==="http:"&&loopback))throw Error("正式服務必須使用 HTTPS");
 if(u.search||u.hash||!["","/"].includes(u.pathname))throw Error("請填後台 API 的根網址");
 return u.origin;
}
async function call(url,path,payload,token){
 const h={"Content-Type":"application/json"};if(token)h.Authorization="Bearer "+token;
 const r=await fetch(url+path,{method:"POST",mode:"cors",credentials:"omit",cache:"no-store",headers:h,body:JSON.stringify(payload)});
 let data;try{data=await r.json()}catch{throw Error("後台未回傳有效 JSON")}
 if(!r.ok)throw Error(data.error||"同步失敗");return data;
}
async function upload(){
 const c=read();if(!c?.enabled||!c.token||typeof state==="undefined")return;
 return call(c.url,"/api/students/sync",{nickname:typeof suduDevice!=="undefined"?suduDevice.name||"學習者":"學習者",state:{
  attempts:state.attempts||{},reviewHistory:state.reviewHistory||{},examSubmissions:state.examSubmissions||{},examSubmissionHistory:state.examSubmissionHistory||{}
 }},c.token);
}
function schedule(){if(!read()?.enabled)return;clearTimeout(timer);timer=setTimeout(()=>upload().catch(e=>console.warn("自願同步失敗:",e.message)),3000)}
function controls(){
 const inp=document.getElementById("sudu-sync-endpoint"),on=document.getElementById("sudu-sync-enable"),off=document.getElementById("sudu-sync-stop"),label=document.getElementById("sudu-sync-status");
 if(!inp||!on||!off||!label)return;
 const current=read();inp.value=current?.url||"";
 label.textContent=current?.enabled?"已同意同步至 "+current.url:"未啟用：紀錄仍只保存在此瀏覽器";
 on.onclick=async()=>{
  try{
   const url=base(inp.value.trim());
   if(!confirm("自願將學習暱稱、答題選項與日期、重答紀錄、歷次試卷快照上傳至此私人後台？你可停止同步、撤銷權杖或刪除伺服器紀錄。"))return;
   const previous=read();let token=previous?.url===url?previous.token:null,id=previous?.url===url?previous.studentId:null;
   if(!token){const n=await call(url,"/api/students/enroll",{nickname:typeof suduDevice!=="undefined"?suduDevice.name||"學習者":"學習者"});token=n.accessToken;id=n.studentId}
   store({enabled:true,url,token,studentId:id,consentedAt:new Date().toISOString()});await upload();
   label.textContent="同步成功，私人後台識別碼："+id;
  }catch(e){label.textContent="同步失敗："+e.message}
 };
 off.onclick=()=>{clearTimeout(timer);const c=read();if(c){c.enabled=false;store(c)}label.textContent="後續同步已停止。已上傳紀錄仍保留；可另按下方按鈕撤銷權杖或刪除伺服器紀錄。"};
 for(const [id,title,path,confirmation] of [
  ["sudu-sync-revoke","撤銷同步權杖與分享","/api/students/revoke","撤銷目前同步權杖與所有此學生的分享連結？伺服器既有紀錄仍保留，本機學習歷史不變。"],
  ["sudu-sync-delete","刪除伺服器紀錄","/api/students/delete","永久刪除這個私人後台上的學習紀錄、改分及分享，並撤銷權杖？本機作答與備份不會刪除。"]
 ]){
  let button=document.getElementById(id);
  if(!button){button=document.createElement("button");button.id=id;button.type="button";button.className=off.className;button.textContent=title;off.parentElement.append(button)}
  button.onclick=async()=>{
   const c=read();if(!c?.token){label.textContent="沒有可用的同步權杖。已撤銷權杖的既有資料刪除需聯絡私人後台管理員。";return}
   if(!confirm(confirmation))return;
   clearTimeout(timer);store({...c,enabled:false});
   try{await call(c.url,path,{},c.token);store({...c,enabled:false,token:null});label.textContent=path.endsWith("delete")?"伺服器紀錄已刪除；本機學習歷史保留。":"同步權杖及分享已撤銷；本機學習歷史保留。"}
   catch(e){label.textContent="後續同步已停止；伺服器操作失敗："+e.message}
  };
 }
}
root.SUDU_SYNC={controls,schedule,upload};
})(window);
