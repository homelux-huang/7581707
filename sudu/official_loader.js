/* Read-only official corpus loader. Does not alter student history. */
function suduEnsureOfficialData(){ALL.officialQuestions||=[];ALL.officialYearReports||=Object.create(null);ALL.officialYearLoaded||=Object.create(null);}
const suduYearRequests=new Map();
let suduCatalogPromise=null;
function suduLoadOfficialCatalog(){
 if(!suduCatalogPromise)suduCatalogPromise=fetch('./data/official-paper-catalog.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(String(r.status));return r.json();}).then(data=>{ALL.officialCatalog=data;return data;}).catch(()=>null);
 return suduCatalogPromise;
}
async function suduLoadOfficialYear(year){
 suduEnsureOfficialData();if(year==='自編'||year==='全部')return;
 const key=String(year);if(!/^\d{2,3}$/.test(key)||Number(key)<90||Number(key)>115)return;
 if(ALL.officialYearLoaded[key])return;if(suduYearRequests.has(key))return suduYearRequests.get(key);
 const task=(async()=>{
  try{
   await suduLoadOfficialCatalog();
   const response=await fetch('./data/years/'+key+'.json',{cache:'no-store'});if(!response.ok)throw Error('題庫尚未發布（'+response.status+'）');
   const data=await response.json();if(String(data.year)!==key||!Array.isArray(data.papers))throw Error('年度題庫格式不正確');
   // Official source indexes: 90-91 commerce=14, 92-97 commerce=13, 98+ commerce=09.
   const catalogue=ALL.officialCatalog?.years?.[key];
   data.papers=data.papers.filter(p=>catalogue?catalogue.allowedPaperCodes.includes(p.paper):String(p.paper||'').startsWith('00-')||p.paper==='BIZ-1'||p.paper==='BIZ-2'||Number(key)>=98&&['09-1','09-2'].includes(p.paper));
   for(const entry of catalogue?.papers||[]){
    const p=data.papers.find(p=>p.paper===entry.paper);
    if(p){p.coverSubjects=entry.subjects;p.subjectStatus=entry.subjectStatus;}
    else data.papers.push({paper:entry.paper,subject:entry.subjects?.length===1?entry.subjects[0]:entry.paper,coverSubjects:entry.subjects,subjectStatus:entry.subjectStatus,questionPdf:entry.questionSource,answerPdf:entry.answerSource,questions:[],status:'source_only',expectedCount:null});
   }
   const found=[],seen=new Set();
   for(const paper of data.papers){
    for(const raw of Array.isArray(paper.questions)?paper.questions:[]){
     if(!raw||typeof raw.id!=='string'||seen.has(raw.id)||!Number.isInteger(raw.number)||raw.number<1||String(raw.year)!==key)continue;
     seen.add(raw.id);const options=Array.isArray(raw.options)?raw.options.map(String):[];
     const proof=raw.verification?.answer||raw.answerReview||raw.answerVerification;
     const answerReviewed=raw.answerVerified===true&&(raw.answerMatched===true||Boolean(proof));
     const q={...raw,options,official:true,question:String(raw.question||''),year:Number(key),paper:raw.paper||paper.paper,subject:raw.subject||paper.subject||paper.paper,
      answerMatched:raw.answerMatched===true||raw.answerVerified===true||Boolean(raw.officialAnswerCandidate),
      answerVerified:answerReviewed,questionVerified:raw.questionVerified===true,
      teachingVerified:raw.teachingVerified===true,textbookVerified:raw.textbookVerified===true,
      readable:options.length===4&&options.every(x=>x.trim())&&raw.questionVerified===true,
      issues:Array.isArray(raw.issues)?raw.issues:[],source:raw.source||paper.questionPdf,answerSource:raw.answerSource||paper.answerPdf};
     found.push(q);
    }
   }
   ALL.officialQuestions=ALL.officialQuestions.filter(q=>String(q.year)!==key).concat(found);
   ALL.officialYearReports[key]=data;ALL.officialYearLoaded[key]=true;
  }catch(error){ALL.officialYearReports[key]={year:Number(key),papers:[],errors:[String(error.message||error)],loadFailed:true};}
  finally{suduYearRequests.delete(key);}
 })();suduYearRequests.set(key,task);return task;
}
function suduPaperStats(year,paper){const qs=(ALL.officialQuestions||[]).filter(q=>String(q.year)===String(year)&&q.paper===paper);return {count:qs.length,withAnswers:qs.filter(q=>q.answerMatched).length,answersVerified:qs.filter(q=>q.answerVerified).length,withTeaching:qs.filter(q=>q.teachingVerified).length};}
async function suduLoadOfficialIndex(){
 suduEnsureOfficialData();if(ALL.officialIndex)return ALL.officialIndex;
 try{const r=await fetch('./data/index.json',{cache:'no-store'});if(!r.ok)throw Error(String(r.status));ALL.officialIndex=await r.json();}
 catch(e){ALL.officialIndex={years:[],warning:String(e)};}return ALL.officialIndex;
}
let suduAllYearsPromise=null;
function suduLoadAllOfficialYears(){
 if(suduAllYearsPromise)return suduAllYearsPromise;
 suduAllYearsPromise=(async()=>{await suduLoadOfficialIndex();const years=ALL.archive.map(x=>String(x.year));for(let i=0;i<years.length;i+=4)await Promise.all(years.slice(i,i+4).map(suduLoadOfficialYear));if(['dashboard','clinic','mistakes'].includes(ui.tab))render();})();return suduAllYearsPromise;
}
