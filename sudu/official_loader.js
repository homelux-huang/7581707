/* Official TCTE question JSON reader. Read-only client, no student-side PDF uploading. */
function suduEnsureOfficialData(){
  ALL.officialQuestions ||= [];
  ALL.officialYearReports ||= Object.create(null);
  ALL.officialYearLoaded ||= Object.create(null);
}
async function suduLoadOfficialYear(year){
  suduEnsureOfficialData();
  if(year==='自編'||year==='全部')return;
  const key=String(year);
  if(ALL.officialYearLoaded[key])return;
  const statusEl=document.getElementById('status');
  if(statusEl)statusEl.textContent=key+' 年：正在載入雲端官方題庫……';
  try{
    const res=await fetch('./data/years/'+encodeURIComponent(key)+'.json',{cache:'no-store'});
    if(!res.ok)throw Error('題庫檔尚未發布 ('+res.status+')');
    const data=await res.json();
    if(String(data.year)!==key||!Array.isArray(data.papers))throw Error('題庫格式不符合要求');
    const found=[];
    for(const paper of data.papers){
      if(!Array.isArray(paper.questions))continue;
      for(const q of paper.questions){
        if(!q||typeof q.question!=='string'||!Number.isInteger(q.number)||String(q.year)!==key)continue;
        const options=Array.isArray(q.options)?q.options.map(x=>String(x)):[],ans=q.answer;
        const check=options.length===4&&options.every(x=>x.trim().length>0);
        found.push({...q,
          options,
          official:true,
          answer: Number.isInteger(ans)&&ans>=0&&ans<=3&&q.answerVerified?ans:null,
          answerVerified:check&&q.answerVerified===true,
          teachingVerified:q.teachingVerified===true,
          readable:check,
          subject:q.subject||paper.subject||paper.paper,
          year:Number(key),
          paper:q.paper||paper.paper,
          issues:q.issues||[],
          source:q.source||paper.questionPdf
        });
      }
    }
    ALL.officialQuestions=ALL.officialQuestions.filter(q=>String(q.year)!==key).concat(found);
    ALL.officialYearReports[key]=data;
    ALL.officialYearLoaded[key]=true;
    if(statusEl)statusEl.textContent=key+' 年已載入 '+found.length+' 題（其中 '+found.filter(q=>q.answerVerified).length+' 題有配對官方答案）；未核實題會保留原卷查閱。';
  }catch(e){
    ALL.officialYearReports[key]={year:Number(key),papers:[],errors:[String(e.message||e)],questionsFound:0};
    ALL.officialYearLoaded[key]=true;
    if(statusEl)statusEl.textContent=key+' 年題庫尚未完成雲端匯入。請稍後重試。';
  }
}
function suduPaperStats(year,paper){
  const qs=(ALL.officialQuestions||[]).filter(q=>String(q.year)===String(year)&&q.paper===paper);
  return {count:qs.length,withAnswers:qs.filter(q=>q.answerVerified).length,withTeaching:qs.filter(q=>q.teachingVerified).length};
}
