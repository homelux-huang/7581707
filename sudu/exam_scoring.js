/* One scoring engine for the study screen and Dashboard. Existing histories are never erased. */
(function(root){
"use strict";
const qkey=(year,paper)=>String(year)+"/"+String(paper);
const iso=()=>new Date().toISOString();
const copy=value=>JSON.parse(JSON.stringify(value));
function initial(s){s.examSessions||={};s.examSubmissions||={};s.examSubmissionHistory||={};return s}
function validChoice(choice){return Number.isInteger(choice)&&choice>=0&&choice<=3}
function accepted(q){return Array.isArray(q?.acceptedAnswers)&&q.acceptedAnswers.length?q.acceptedAnswers.filter(validChoice):validChoice(q?.answer)?[q.answer]:[]}
function canAnswer(q){return !!q&&(Array.isArray(q.options)&&q.options.length===4&&q.options.every(x=>typeof x==="string"&&x.trim())||q.official===true&&/^https:\/\/(?:[^/]+\.)?tcte\.edu\.tw\//.test(q.source||""))}
function incompletePresentation(q){return q.questionPresentation==="original_image_required"||(q.issues||[]).includes("cover_instruction_extraction_suspected")}
function isGradeable(q){return canAnswer(q)&&!incompletePresentation(q)&&q.answerVerified===true&&q.questionVerified===true&&accepted(q).length>0}
function getPaper(data,year,paper){return data.officialYearReports?.[String(year)]?.papers?.find(x=>String(x.paper)===String(paper))}
function paperItems(data,year,paper){return (data.officialQuestions||[]).filter(q=>String(q.year)===String(year)&&q.paper===paper)}
function rubric(data,year,paper){
 const rules=(data.scoringRules?.rules||[]).filter(x=>String(x.year)===String(year)&&x.paper===paper);
 const rule=rules.at(-1);
 if(!rule||rule.verified!==true||rule.type!=="per-question"||!/^https:\/\/(?:[^/]+\.)?tcte\.edu\.tw\//.test(rule.sourceUrl||"")||!rule.reviewedBy||!rule.reviewedAt)return null;
 return rule;
}
function fingerprint(q){
 // Change detector only; the server independently reads official data and never trusts this hash.
 const text=JSON.stringify([q.id,q.number,q.source,q.question,q.options,q.answer,q.acceptedAnswers,q.questionVerified,q.answerVerified,q.sourceRevision,q.sourceChangePending,q.questionPresentation]);
 let n=2166136261;for(let i=0;i<text.length;i++){n^=text.charCodeAt(i);n=Math.imul(n,16777619)}return (n>>>0).toString(16);
}
function submissions(s,year,paper){
 initial(s);const key=qkey(year,paper),list=[];
 if(s.examSubmissions[key])list.push(s.examSubmissions[key]);
 for(const entry of s.examSubmissionHistory[key]||[])if(!list.some(x=>x.id&&entry.id?x.id===entry.id:x.submittedAt===entry.submittedAt))list.push(entry);
 return list.sort((a,b)=>(Date.parse(a.submittedAt)||0)-(Date.parse(b.submittedAt)||0));
}
function latestSubmission(s,year,paper){return submissions(s,year,paper).at(-1)||null}
function currentChoices(s,year,paper,items){
 const session=s.examSessions[qkey(year,paper)];
 if(session?.fresh)return session.choices||{};
 return Object.fromEntries(items.map(q=>[q.id,(s.attempts?.[q.id]||[]).at(-1)?.choice]));
}
function choiceIsValid(q,choice){
 return q.questionType==="multiple-choice"?Array.isArray(choice)&&choice.length>0&&choice.every(validChoice)&&new Set(choice).size===choice.length:validChoice(choice);
}
function scoreSubmitted(data,year,paper,sub,items=paperItems(data,year,paper)){
 const pending=(reason,extra={})=>({value:null,max:null,reason,status:"pending-verification",...extra});
 const rule=rubric(data,year,paper),p=getPaper(data,year,paper);
 if(!sub||!Number.isFinite(Date.parse(sub.submittedAt)))return pending("缺少有效送出日期，不是完整送出快照");
 if(!rule||!p||rule.expectedCount!==p.expectedCount||items.length!==p.expectedCount||items.some(q=>!isGradeable(q)))return pending("正式計分規則或完整原題尚待核實");
 if(new Set(items.map(q=>q.id)).size!==items.length||new Set(items.map(q=>q.number)).size!==items.length)return pending("試題 ID 或原卷題號重複，不能計分");
 if(sub.ruleVersion&&sub.ruleVersion!==(rule.version||rule.reviewedAt))return pending("官方配分版本已變更，歷史成績須重新覆核");
 if(!sub.questionVersions||items.some(q=>sub.questionVersions[q.id]!==fingerprint(q)))return pending("原題／答案版本已變更或舊快照無版本證據，需重新覆核；原始作答仍保留");
 const weights=rule.points;
 if(!weights||Object.keys(weights).length!==p.expectedCount||items.some(q=>!Number.isFinite(weights[String(q.number)])||weights[String(q.number)]<0))return pending("配分欄位未完整核實");
 const objectiveMax=items.reduce((n,q)=>n+weights[String(q.number)],0),manual=rule.manualSections||[];
 if(!Array.isArray(manual)||manual.some(x=>!Number.isFinite(x.maxScore)||x.maxScore<0||!x.id))return pending("非選擇題配分未完整核實");
 const manualMax=manual.reduce((n,x)=>n+x.maxScore,0),max=objectiveMax+manualMax;
 if(!(max>0)||!Number.isFinite(max)||!Number.isFinite(rule.maxScore)||Math.abs(max-rule.maxScore)>0.001)return pending("配分總和與官方滿分不一致");
 if(!items.every(q=>choiceIsValid(q,sub.choices?.[q.id]))||Object.keys(sub.choices||{}).length!==items.length)return pending("送出紀錄缺少完整作答或含其他試卷答案");
 let value=0;
 for(const q of items){
  const choice=sub.choices[q.id],weight=weights[String(q.number)],item=rule.itemRules?.[String(q.number)]||{};
  if(item.fullCredit===true){value+=weight;continue}
  if(q.questionType==="multiple-choice"){
   if(item.method==="official-subsets"&&item.subsetPoints){
    const points=item.subsetPoints[[...choice].sort().join(",")];
    if(!Number.isFinite(points)||points<0||points>weight)return pending("多選題缺少對應的官方部分給分規則");
    value+=points;
   }else if(item.method==="all-or-nothing"){
    if(JSON.stringify([...choice].sort())===JSON.stringify([...accepted(q)].sort()))value+=weight;
   }else return pending("多選題配分方式待核實");
  }else if(accepted(q).includes(choice))value+=weight;
 }
 const details={max,sourceUrl:rule.sourceUrl,ruleVersion:rule.version||rule.reviewedAt,ruleReviewedAt:rule.reviewedAt,objectiveValue:Math.round(value*100)/100,objectiveMax};
 if(manual.length||rule.scope==="objective-section")return pending("選擇題小計不等於整卷總分；非選擇題須授權人工閱卷",{...details,status:"pending-marking",pendingManualSections:manual.map(x=>x.id)});
 return {...details,value:Math.round(value*100)/100,reason:null,status:"scored"};
}
function paperStatus(data,history,year,paper){
 initial(history);
 const key=qkey(year,paper),items=paperItems(data,year,paper),p=getPaper(data,year,paper),session=history.examSessions[key];
 const previous=latestSubmission(history,year,paper),sub=session?.fresh&&!session.submittedAt?null:previous;
 const expected=Number.isInteger(p?.expectedCount)&&p.expectedCount>0?p.expectedCount:0;
 const choices=currentChoices(history,year,paper,items),answerable=items.filter(canAnswer),answered=items.filter(q=>choiceIsValid(q,choices[q.id])).length;
 const corpusComplete=expected>0&&items.length===expected&&answerable.length===expected&&!items.some(incompletePresentation)&&new Set(items.map(q=>q.id)).size===expected&&new Set(items.map(q=>q.number)).size===expected;
 const ready=corpusComplete&&answered===expected&&!sub;
 const unverified=!corpusComplete||items.some(q=>!isGradeable(q));
 const sc=sub?scoreSubmitted(data,year,paper,sub,items):null;
 let status="incomplete",label="未考完（"+answered+"/"+(expected||"待確認")+" 題）";
 if(sub){status=sc.status;label=status==="scored"?"可顯示成績":status==="pending-marking"?"已送出待閱卷":"已送出待核實"}
 else if(!corpusComplete&&answered>=answerable.length){status="corpus-pending";label="題庫待補／原卷題數待核實（已答完目前可作答的 "+answerable.length+" 題）"}
 else if(ready){status="ready";label="已作答待送出"}
 return {key,year:String(year),paper,expected,available:items.length,answerable:answerable.length,answered,ready,submitted:!!sub,status,label,unverified,
  submittedAt:sub?.submittedAt||null,startedAt:sub?.startedAt||session?.startedAt||null,elapsedMs:Number.isFinite(sub?.elapsedMs)?sub.elapsedMs:null,
  activeMs:Number.isFinite(sub?.activeMs)?sub.activeMs:null,score:sc,submission:sub,previousSubmission:previous,submissionCount:submissions(history,year,paper).length};
}
function markFirstAnswer(data,s,year,paper,now){
 initial(s);if(String(year)==="自編")return;
 const key=qkey(year,paper);if(!s.examSessions[key])s.examSessions[key]={startedAt:now||iso()};
}
function recordAnswer(data,s,q,choice,now){
 if(!q||!choiceIsValid(q,choice))return false;
 markFirstAnswer(data,s,q.year,q.paper,now);
 const session=s.examSessions[qkey(q.year,q.paper)];
 if(session?.fresh&&!session.submittedAt){session.choices||={};session.choices[q.id]=copy(choice);session.answerEvents||=[];session.answerEvents.push({id:q.id,choice:copy(choice),at:now||iso()})}
 return true;
}
function startNewExam(data,s,year,paper,now){
 initial(s);const key=qkey(year,paper);
 if(s.examSessions[key]?.fresh&&!s.examSessions[key].submittedAt)return {ok:false,reason:"本次測驗尚未送出，請先續答"};
 const startedAt=now||iso();if(!Number.isFinite(Date.parse(startedAt)))return {ok:false,reason:"無效開始日期"};
 s.examSessions[key]={id:"exam-"+Date.parse(startedAt)+"-"+Math.random().toString(36).slice(2,10),startedAt,fresh:true,choices:{},answerEvents:[]};
 return {ok:true,id:s.examSessions[key].id};
}
function submit(data,s,year,paper,now){
 const info=paperStatus(data,s,year,paper);
 if(info.submitted)return {ok:false,reason:"這份試卷已送出；請明確開始新測驗，原始送出紀錄不會被重練覆寫"};
 if(!info.ready)return {ok:false,reason:info.status==="corpus-pending"?"題庫待補，已答完目前收錄題目不代表全卷完成":"尚有可作答試題未完成，請先完成整份試卷"};
 const when=now||iso(),items=paperItems(data,year,paper),key=qkey(year,paper),session=s.examSessions[key];
 if(!Number.isFinite(Date.parse(when)))return {ok:false,reason:"無效送出日期"};
 const choices=currentChoices(s,year,paper,items);
 if(!items.every(q=>choiceIsValid(q,choices[q.id])))return {ok:false,reason:"存在無效作答"};
 const first=Date.parse(session?.startedAt),last=Date.parse(when),elapsedMs=Number.isFinite(first)&&last>=first?last-first:null;
 const entry={id:session?.id||"submission-"+last,year:String(year),paper,submittedAt:when,elapsedMs,activeMs:null,
  timingBasis:elapsedMs===null?"unknown":"elapsed-including-away",startedAt:Number.isFinite(first)?session.startedAt:null,choices:copy(choices),
  questionCount:items.length,questionVersions:Object.fromEntries(items.map(q=>[q.id,fingerprint(q)])),ruleVersion:rubric(data,year,paper)?.version||null,
  answerEvents:session?.answerEvents?copy(session.answerEvents):items.flatMap(q=>(s.attempts?.[q.id]||[]).map(a=>({id:q.id,choice:a.choice,at:a.at||null})))};
 if(!s.examSubmissions[key])s.examSubmissions[key]=entry;
 else{(s.examSubmissionHistory[key]||=[]).push(entry)}
 if(session)session.submittedAt=when;
 return {ok:true,status:paperStatus(data,s,year,paper)};
}
function humanTime(ms){if(!Number.isFinite(ms)||ms<0)return "N/A";const sec=Math.floor(ms/1000);return Math.floor(sec/3600)+" 小時 "+Math.floor(sec%3600/60)+" 分 "+sec%60+" 秒（含離開頁面的經過時間；活躍時間 N/A）"}
const api={qkey,initial,getPaper,rubric,paperStatus,scoreSubmitted,markFirstAnswer,recordAnswer,startNewExam,submissions,submit,humanTime,isGradeable,canAnswer,accepted,fingerprint};
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.SUDU_SCORING=api;
})(typeof window!=="undefined"?window:globalThis);
