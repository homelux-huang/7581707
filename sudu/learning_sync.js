/* Student-controlled opt-in learning sync. No server receives data by default. */
(function(root){"use strict";
const KEY="sudu_student_sync_optin_v1";let timer=null;
function read(){try{return JSON.parse(localStorage.getItem(KEY)||"null")}catch{return null}}
function store(data){localStorage.setItem(KEY,JSON.stringify(data))}
function base(raw){
 const u=new URL(raw);if(u.username||u.password)throw Error("API 網址不可含密碼");
 if(u.protocol!=="https:"&&!["localhost","127.0.0.1"].includes(u.hostname))throw Error("必須使用 HTTPS");
 return u.origin;
}
async function call(url,path,payload,token){
 const h={"Content-Type":"application/json"};if(token)h.Authorization="Bearer "+token;
 const r=await fetch(url+path,{method:"POST",mode:"cors",headers:h,body:JSON.stringify(payload)});
 const data=await r.json();if(!r.ok)throw Error(data.error||"同步失敗");return data;
}
async function upload(){
 const c=read();if(!c?.enabled||!c.token||typeof state==="undefined")return;
 return call(c.url,"/api/students/sync",{nickname:suduDevice?.name||"學習者",state:{attempts:state.attempts||{},examSubmissions:state.examSubmissions||{}}},c.token);
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
   if(!confirm("自願將學習暱稱、答題紀錄、試卷送出時間上傳至指定私人後台？"))return;
   const previous=read();let token=previous?.url===url?previous.token:null,id=previous?.url===url?previous.studentId:null;
   if(!token){const n=await call(url,"/api/students/enroll",{nickname:suduDevice?.name||"學習者"});token=n.accessToken;id=n.studentId}
   store({enabled:true,url,token,studentId:id});await upload();
   label.textContent="同步成功，識別碼："+id;
  }catch(e){label.textContent="同步失敗："+e.message}
 };
 off.onclick=()=>{const c=read();if(c){c.enabled=false;store(c)}label.textContent="未來同步已停止；既有伺服器資料需另向管理員要求刪除。"};
}
root.SUDU_SYNC={controls,schedule,upload};
})(window);
