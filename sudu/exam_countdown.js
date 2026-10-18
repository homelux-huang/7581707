/* Calendar-day countdown until an officially verified start time is available. */
const SUDU_COUNTDOWN=(()=>{
 function state(data,now=new Date()){
  if(!data?.dateVerified||!/^\d{4}-\d{2}-\d{2}$/.test(data.startDate||''))return {label:'考試日期待官方確認',status:'unconfirmed'};
  const today=new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit'}).format(now);
  if(today>data.endDate)return {label:'本次統測已結束 · 下一場日期待確認',status:'ended'};
  if(today>=data.startDate)return {label:data.year+' 統測考試期間 · 請依准考證時間',status:'exam-days'};
  if(data.timeVerified&&data.targetTime&&Number.isFinite(Date.parse(data.targetTime))){const seconds=Math.max(0,Math.floor((Date.parse(data.targetTime)-now.getTime())/1000));return {label:data.year+' 統測 '+Math.floor(seconds/86400)+'天 '+Math.floor(seconds%86400/3600)+'時 '+Math.floor(seconds%3600/60)+'分 '+seconds%60+'秒',status:seconds?'countdown':'exam-days'};}
  const days=Math.round((Date.parse(data.startDate+'T00:00:00+08:00')-Date.parse(today+'T00:00:00+08:00'))/86400000);
  return {label:data.year+' 統測倒數 '+days+' 天',status:'date-countdown'};
 }
 async function init(){
  const head=document.querySelector('.header .head');if(!head)return;const el=document.createElement('a');el.id='sudu-exam-countdown';el.textContent='考試日期待官方確認';el.target='_blank';el.rel='noopener';head.append(el);
  try{const r=await fetch('./data/exam-schedule.json');if(!r.ok)throw Error();const data=await r.json();el.href=data.sourceUrl;el.title=data.startDate+'～'+data.endDate+'（Asia/Taipei）｜'+data.note;const update=()=>{const s=state(data);el.textContent=s.label;el.dataset.status=s.status;};update();setInterval(update,data.timeVerified?1000:60000);}catch{el.removeAttribute('href');}
 }
 return {state,init};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=SUDU_COUNTDOWN;
