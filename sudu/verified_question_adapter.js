/* Strict, side-effect-free adapter for future QA-approved questions.
 * Never changes Demo questions, device codes or localStorage on import.
 */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.SUDU_QUESTION_ADMISSION = api;
})(typeof window !== 'undefined' ? window : null, function() {
  'use strict';
  const PAPERS = Object.freeze({
    '國文':'00-C','英文':'00-E','數學 B':'00-MB','數學B':'00-MB',
    '商業概論':'09-1','數位科技':'09-1','會計學':'09-2','經濟學':'09-2'
  });
  const DEMO = Object.freeze({
    '國文':[1,2,3,7,9], '英文':[1,2,3,4,5], '數學 B':[7,9,10,11,12],
    '商業概論':[1,3,5,6,7], '數位科技':[26,27,28,32,34],
    '會計學':[2,3,4,5,6], '經濟學':[25,26,27,28,29]
  });
  function canonical(year, subject, number) {
    const paper=PAPERS[subject], n=Number(number);
    if (Number(year)!==115 || !paper || !Number.isInteger(n) || n<1 || n>50)
      return null;
    return '115-'+paper+'-'+String(n).padStart(2,'0');
  }
  function demoLegacyKeys() {
    const out={};
    Object.entries(DEMO).forEach(([subject, ids])=>ids.forEach(id=>{
      out[subject+'|'+id]=canonical(115,subject,id);
    }));
    return out;
  }
  const isLetter=v=>typeof v==='string' && /^[ABCD]$/.test(v.trim().toUpperCase());
  function review(q, evidence) {
    const e=evidence||{};
    const ai=e.aiAnswer, official=q&&q.officialFinalAnswer;
    const independent=e.solvedWithoutOfficialAnswer===true &&
      typeof e.solvedAt==='string' && e.solvedAt.length>0 &&
      typeof e.questionRevision==='string' &&
      e.questionRevision===q.questionRevision && isLetter(ai);
    const officialConfirmed=e.officialCorrectionChecked===true &&
      e.answerVerified===true && isLetter(official);
    let comparison='not_checked';
    if(independent && officialConfirmed)
      comparison=ai.trim().toUpperCase()===official.trim().toUpperCase()?'matched':'mismatch';
    const dataReady=e.imageQa===true && e.textQa===true &&
      e.dbQa===true && officialConfirmed && e.sourceQa===true;
    const studentReady=dataReady && comparison==='matched' &&
      e.teachingQa===true && e.uiQa===true && e.studentReleaseApproved===true;
    const warning=comparison==='mismatch' ?
      '警示：AI 解答與題庫官方解答不一致，本題待核對。 AI 答案：'+
      ai.trim().toUpperCase()+'；官方答案：'+official.trim().toUpperCase() : '';
    return Object.freeze({comparison,dataReady,studentReady,warning,
      actionAllowed:studentReady});
  }
  function renderBlockingNotice(questionCard, buttons, state) {
    if (!questionCard || !state) throw Error('Missing question card or admission state');
    const doc=questionCard.ownerDocument;
    const previous=questionCard.querySelector('[data-sudu-admission-notice]');
    if(previous)previous.remove();
    if(state.warning) {
      const warning=doc.createElement('div');
      warning.setAttribute('data-sudu-admission-notice','');
      warning.setAttribute('role','alert');
      warning.style.cssText='font-size:clamp(20px,4vw,28px);font-weight:900;background:#7f1025;color:white;padding:18px;border:4px solid #ffcc00;border-radius:12px;line-height:1.5;margin-bottom:16px';
      warning.textContent=state.warning;
      questionCard.prepend(warning);
    }
    for(const button of buttons||[])button.disabled=!state.actionAllowed;
  }
  return Object.freeze({canonical,demoLegacyKeys,review,renderBlockingNotice});
});
