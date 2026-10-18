/* Per-paper completion and source-verified scoring. No estimate masquerades as an official score. */
(function(root){
"use strict";
const MS=1000;
const qkey=(year,paper)=>String(year)+"/"+String(paper);
const iso=()=>new Date().toISOString();
function initial(s){s.examSessions||={};s.examSubmissions||={};return s}
function isGradeable(q){return q&&q.answerVerified===true&&q.questionVerified===true&&Number.isInteger(q.answer)&&q.answer>=0&&q.answer<=3&&Array.isArray(q.options)&&q.options.length===4&&q.options.every(x=>typeof x==="string"&&x.trim().length>0)}
function getPaper(data,year,paper){return data.officialYearReports?.[String(year)]?.papers?.find(x=>String(x.paper)===String(paper))}
function rubric(data,year,paper){
 const rule=data.scoringRules?.rules?.find(x=>String(x.year)===String(year)&&x.paper===paper);
 if(!rule||rule.verified!==true||rule.type!=="per-question"||!/^https:\/\/(?:[^/]+\.)?tcte\.edu\.tw\//.test(rule.sourceUrl||"")||!rule.reviewedBy||!rule.reviewedAt)return null;
 return rule;
}
function paperStatus(data,history,year,paper){
 initial(history);
 const key=qkey(year,paper),items=(data.officialQuestions||[]).filter(q=>String(q.year)===String(year)&&q.paper===paper),p=getPaper(data,year,paper);
 const sub=history.examSubmissions[key]||null;
 const expected=Number(p?.expectedCount||0);
 const answered=items.filter(q=>Array.isArray(history.attempts?.[q.id])&&history.attempts[q.id].length>0).length;
 const ready=expected>0&&items.length===expected&&items.every(isGradeable)&&answered===expected;
 const pendingQuestionAudit=items.some(q=>!isGradeable(q));
 const status=sub?"submitted":ready?"ready":"incomplete";
 const label=sub?"已送出":ready?"已完成，可送出":"未考完（"+answered+"/"+(expected||"待確認")+" 題）";
 const sc=sub?scoreSubmitted(data,year,paper,sub,items):null;
 return {key,year:String(year),paper,expected,available:items.length,answered,ready,submitted:!!sub,
   status,label,unverified:pendingQuestionAudit||!p||items.length!==expected,submittedAt:sub?.submittedAt||null,
   startedAt:history.examSessions[key]?.startedAt||null,elapsedMs:sub?.elapsedMs??null,score:sc,submission:sub};
}
function scoreSubmitted(data,year,paper,sub,items){
 const rule=rubric(data,year,paper);
 const p=getPaper(data,year,paper);
 if(!rule||!p||rule.expectedCount!==p.expectedCount||items.length!==p.expectedCount||items.some(q=>!isGradeable(q)))
  return {value:null,max:null,reason:"正式計分規則或完整原題尚待核實"};
 const weights=rule.points;
 if(!weights||Object.keys(weights).length!==p.expectedCount||items.some(q=>!Number.isFinite(weights[String(q.number)])||weights[String(q.number)]<0))
  return {value:null,max:null,reason:"配分欄位未完整核實"};
 const max=items.reduce((n,q)=>n+weights[String(q.number)],0);
 if(!(max>0)||!Number.isFinite(max)||!Number.isFinite(rule.maxScore)||Math.abs(max-rule.maxScore)>0.001)
  return {value:null,max:null,reason:"配分總和與官方滿分不一致"};
 if(!items.every(q=>Number.isInteger(sub.choices?.[q.id])))return {value:null,max:null,reason:"送出紀錄缺少完整作答"};
 const value=items.reduce((n,q)=>{
   const correct=(Array.isArray(q.acceptedAnswers)&&q.acceptedAnswers.length?q.acceptedAnswers:[q.answer]).includes(sub.choices[q.id]);
   return n+(correct?weights[String(q.number)]:0)
 },0);
 return {value:Math.round(value*100)/100,max,sourceUrl:rule.sourceUrl,reason:null,ruleReviewedAt:rule.reviewedAt};
}
function markFirstAnswer(data,s,year,paper,now){
 initial(s);if(year==="自編")return;
 const key=qkey(year,paper);
 if(!s.examSessions[key])s.examSessions[key]={startedAt:now||iso()};
}
function submit(data,s,year,paper,now){
 const info=paperStatus(data,s,year,paper);
 if(info.submitted)return {ok:false,reason:"這份試卷已送出；原始送出紀錄不會被後續練習覆寫"};
 if(!info.ready)return {ok:false,reason:info.unverified?"正式題庫／答案未完整核實，不能冒充整份試卷完成":"尚有試題未完成，請先完成整份試卷"};
 const when=now||iso(),items=data.officialQuestions.filter(q=>String(q.year)===String(year)&&q.paper===paper);
 const choices=Object.create(null);
 for(const q of items)choices[q.id]=s.attempts[q.id].at(-1).choice;
 if(!items.every(q=>Number.isInteger(choices[q.id])&&choices[q.id]>=0&&choices[q.id]<=3))return {ok:false,reason:"存在無效作答"};
 const key=qkey(year,paper);
 const first=Date.parse(s.examSessions[key]?.startedAt||when);
 const last=Date.parse(when);
 const elapsedMs=Number.isFinite(first)&&Number.isFinite(last)?Math.max(0,last-first):0;
 s.examSubmissions[key]={year:String(year),paper,submittedAt:when,elapsedMs,
  startedAt:s.examSessions[key]?.startedAt||when,choices,questionCount:items.length};
 return {ok:true,status:paperStatus(data,s,year,paper)};
}
function humanTime(ms){if(!Number.isFinite(ms))return "N/A";const sec=Math.floor(ms/MS);return Math.floor(sec/3600)+" 小時 "+Math.floor(sec%3600/60)+" 分 "+sec%60+" 秒（含離開頁面的經過時間）"}
const api={qkey,initial,getPaper,rubric,paperStatus,scoreSubmitted,markFirstAnswer,submit,humanTime,isGradeable};
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.SUDU_SCORING=api;
})(typeof window!=="undefined"?window:globalThis);
