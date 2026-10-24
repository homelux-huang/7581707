/* A-style animated exam feedback for the existing 115 V4 five-question demo.
 * Grade only the demo subset here; real 114/115 exam scoring stays in
 * exam_scoring.js and requires an audited year/paper rubric and source QA.
 * Never subtract a mark on a wrong answer: TCTE objective questions have
 * no negative marking. This file does not touch student history or answers.
 */
(function (root) {
  'use strict';

  const POINTS_115 = Object.freeze({
    '國文': 2, '英文': 2, '數學 B': 4,
    '商業概論': 2, '數位科技': 2,
    '會計學': 2, '經濟學': 2
  });
  const LETTERS = new Set(['A','B','C','D']);
  // These 2 Demo questions have official keys, but teaching reasoning is still in dispute.
  // Withhold their points and explicitly label the pending portion of the practice total.
  const TEACHING_HOLDS = Object.freeze({
    '商業概論|7': '特別股與財務槓桿的教學定義待核',
    '經濟學|28': '未給預算的 MU/P 教學歧義待核'
  });
  const teachingHold = (q,year) => year === 'demo' && q
    ? TEACHING_HOLDS[key(q)] || null : null;
  const validRound = value => Number.isSafeInteger(value) && value > 0 ? value : 1;
  const key = q => q.subject + '|' + q.id;

  function questionPoints(q, year) {
    if (year !== 'demo' || !q || !Object.hasOwn(POINTS_115, q.subject)) return null;
    // These are practice points from the 115 paper's objective-question weights.
    // A single subject within 09-1/09-2 is NOT an independent official paper.
    return POINTS_115[q.subject];
  }

  function countedAnswer(q, record, round) {
    if (!record || !['ok','bad'].includes(record.status)) return null;
    if (record.scoreRound === round) {
      return typeof record.scoreCorrect === 'boolean'
        ? { correct: record.scoreCorrect, legacy: false } : null;
    }
    // Preserve historic live-demo answers made before this feature was added.
    // The demo "seed wrong answer" button never records an actual attempt.
    if (record.scoreRound == null && round === 1 && Number(record.attempts) > 0) {
      return { correct: record.status === 'ok', legacy: true };
    }
    return null;
  }

  function lockFirstAnswer(q, record, selected, round, year) {
    const points = questionPoints(q, year);
    if (points == null || !LETTERS.has(selected) || !record ||
        !q || !LETTERS.has(q.answer)) {
      return { eligible: false, first: false, points: 0, earned: 0 };
    }
    const hold = teachingHold(q,year);
    if (hold) return {eligible:true,blocked:true,reason:hold,first:false,
      points:0,earned:0};
    round = validRound(round);
    const previous = countedAnswer(q, record, round);
    if (previous) {
      if (previous.legacy) {
        record.scoreRound = round;
        record.scoreCorrect = previous.correct;
        record.scoreChoice = record.selected || null;
      }
      return {eligible:true,first:false,points,earned:0,correct:previous.correct};
    }
    const correct = selected === q.answer;
    record.scoreRound = round;
    record.scoreCorrect = correct;
    record.scoreChoice = selected;
    return {eligible:true,first:true,correct,points,earned:correct ? points : 0};
  }

  function totalFor(questions, subject, records, round, year) {
    if (year !== 'demo' || !Array.isArray(questions) ||
        questions.length !== 5 || questions.some(q => q.subject !== subject ||
        !LETTERS.has(q.answer) || questionPoints(q, year) == null)) {
      return { eligible: false, reason: '不是五題練習可計分範圍' };
    }
    round = validRound(round);
    let earned = 0, max = 0, answered = 0, correct = 0, wrong = 0;
    let missed = 0, pendingAnswered = 0, pendingTotal = 0;
    for (const q of questions) {
      const points = questionPoints(q, year);
      const entry = countedAnswer(q, (records || {})[key(q)], round);
      if (teachingHold(q,year)) {
        pendingTotal++;
        if (entry) { answered++; pendingAnswered++; }
        continue;
      }
      max += points;
      if (!entry) continue;
      answered++;
      if (entry.correct) { correct++; earned += points; }
      else { wrong++; missed += points; }
    }
    return {eligible:true,subject,round,answered,total:questions.length,
      correct,wrong,earned,max,missed,pendingAnswered,pendingTotal,
      percent:max>0?Math.round(earned/max*100):null,
      complete:answered===questions.length,
      fullyVerified:pendingTotal===0};
  }

  function ensureUI() {
    if (typeof document === 'undefined') return null;
    let hud = document.getElementById('scoreHud');
    if (hud) return hud;
    const study = document.getElementById('studyView');
    const question = document.getElementById('questionCard');
    const answer = document.getElementById('answerCard');
    if (!study || !question || !answer) return null;
    hud = document.createElement('section');
    hud.id = 'scoreHud';
    hud.className = 'score-hud';
    hud.setAttribute('aria-label','五題統測題型練習計分');
    hud.innerHTML = [
      '<div class="score-hud-left">',
      '<span class="score-eyebrow">★ 活力練習計分｜<span id="scoreSubject"></span></span>',
      '<div class="score-value-row"><strong id="scoreEarned">0</strong>',
      '<span class="score-divider">/ <span id="scoreMaximum">10</span> 分</span>',
      '<span class="score-percent" id="scoreRate">0%</span></div>',
      '</div>',
      '<div class="score-hud-right">',
      '<div class="score-hud-count"><span id="scoreAnswered">0 / 5 題</span>',
      '<span id="scoreStatus">未考完</span></div>',
      '<div class="score-meter" role="progressbar" aria-label="練習得分率"',
      ' aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">',
      '<span id="scoreMeterFill"></span></div>',
      '<small id="scoreNotice">五題練習小計｜答錯不倒扣</small>',
      '</div>'
    ].join('');
    study.insertBefore(hud,question);
    const summary = document.createElement('section');
    summary.id = 'scoreSummary';
    summary.className = 'score-summary';
    summary.hidden = true;
    summary.setAttribute('role','status');
    summary.innerHTML = [
      '<div class="score-summary-head"><span aria-hidden="true">🏆</span>',
      '<div><strong id="scoreSummaryHeading">本次科目練習完成！</strong>',
      '<span id="scoreSummarySubject"></span></div></div>',
      '<div class="score-summary-grid">',
      '<div class="score-summary-major"><span>練習小計</span>',
      '<strong id="scoreSummaryValue">0 / 10 分</strong></div>',
      '<div><span>練習得分率</span><strong id="scoreSummaryRate">0%</strong></div>',
      '<div><span>答對 / 答錯</span><strong id="scoreSummaryCounts">0 / 0 題</strong></div>',
      '</div>',
      '<p id="scoreSummaryNotice">依115學年度選擇題每題配分計算；',
      '非整張統測試卷的正式分數，答錯不倒扣。</p>'
    ].join('');
    answer.insertAdjacentElement('afterend',summary);
    const toast = document.createElement('div');
    toast.id = 'scoreToast';
    toast.className = 'score-toast';
    toast.setAttribute('role','status');
    toast.setAttribute('aria-live','polite');
    toast.setAttribute('aria-atomic','true');
    toast.innerHTML = [
      '<span class="score-stars" aria-hidden="true">',
      '<i>✦</i><i>✦</i><i>★</i><i>✦</i><i>★</i><i>✦</i><i>✦</i><i>★</i>',
      '</span>',
      '<span id="scoreToastTitle" class="score-pop-title"></span>',
      '<strong id="scoreToastDelta" class="score-pop-delta"></strong>',
      '<span id="scoreToastTotal" class="score-pop-total"></span>'
    ].join('');
    document.body.appendChild(toast);
    return hud;
  }

  function render({questions,subject,records,round,year}) {
    const result = totalFor(questions,subject,records,round,year);
    const hud = ensureUI();
    if (!hud) return result;
    const hidden = !result.eligible ||
      document.body.classList.contains('qa-image-mode') ||
      document.body.classList.contains('qa-error-mode') ||
      year!=='demo';
    hud.hidden = hidden;
    const panel = document.getElementById('scoreSummary');
    panel.hidden = hidden || !result.complete;
    if (hidden) return result;
    const set = (id,value)=>{const node=document.getElementById(id);
      if(node)node.textContent=String(value);};
    set('scoreSubject',subject);
    set('scoreEarned',result.earned);
    set('scoreMaximum',result.max);
    set('scoreRate',result.percent===null?'待核':result.percent+'%');
    set('scoreAnswered',result.answered+' / '+result.total+' 題');
    set('scoreStatus',result.complete ? (result.fullyVerified?'已完成':'已答完・待核'):'未考完');
    set('scoreNotice',result.pendingTotal
      ? '本組有 '+result.pendingTotal+' 題教學爭議，暫不計分；其餘題小計'
      : '五題練習小計｜答錯不倒扣');
    const meter=document.querySelector('#scoreHud .score-meter');
    const fill=document.getElementById('scoreMeterFill');
    if (meter) meter.setAttribute('aria-valuenow',String(result.percent||0));
    if (fill) fill.style.width=(result.percent||0)+'%';
    hud.classList.toggle('is-complete',result.complete);
    if(result.complete) {
      set('scoreSummaryHeading',result.fullyVerified
        ? '本次科目練習完成！':'五題已答完｜教學疑義待核');
      set('scoreSummarySubject','115 '+subject+'｜五題練習');
      set('scoreSummaryValue',result.earned+' / '+result.max+' 分');
      set('scoreSummaryRate',result.percent+'%');
      set('scoreSummaryCounts',result.correct+' / '+result.wrong+' 題');
      set('scoreSummaryNotice',result.fullyVerified
        ? '依115年選擇題原卷配分計算的五題練習小計，不是整張統測試卷正式成績。答錯不倒扣。'
        : '尚有 '+result.pendingTotal+' 題教學爭議，已排除在小計之外；此為其餘題目得分率，不是五題正式完整成績。');
    }
    return result;
  }

  let activeTimer = null;
  function announce({score,result}) {
    if(!score || !score.eligible || typeof document==='undefined' ||
       document.body.classList.contains('qa-image-mode'))return;
    ensureUI();
    const toast=document.getElementById('scoreToast');
    if(!toast)return;
    if(activeTimer!==null)clearTimeout(activeTimer);
    const good=Boolean(score.correct);
    toast.className='score-toast';
    const first=Boolean(score.first);
    toast.classList.add(score.blocked?'score-pending':
      first?(good?'score-win':'score-lose'):'score-repeat');
    const write=(id,text)=>{const node=document.getElementById(id);if(node)node.textContent=text;};
    if(score.blocked){
      write('scoreToastTitle','本題教學疑義待核');
      write('scoreToastDelta','暫不列入計分');
      write('scoreToastTotal',score.reason||'官方正解與教學說明須另行驗收');
    }else if(first){
      write('scoreToastTitle',good?'🎉 答對了！':'✕ 答錯了');
      write('scoreToastDelta',good?'+'+score.points+' 分':'本題 0 分');
      write('scoreToastTotal',good
        ? ('累計 '+result.earned+' / '+result.max+' 分')
        : ('少拿 '+score.points+' 分｜統測不倒扣'));
    }else{
      write('scoreToastTitle','這題已作答');
      write('scoreToastDelta','不重複計分');
      write('scoreToastTotal','本輪得分採第一次作答，保留錯題練習紀錄');
    }
    const study=document.getElementById('studyView');
    study?.classList.remove('score-shake');
    if(first&&!good&&!score.blocked&&study){
      void study.offsetWidth;study.classList.add('score-shake');
    }
    toast.classList.remove('is-visible');
    void toast.offsetWidth;
    toast.classList.add('is-visible');
    activeTimer=setTimeout(()=>{
      toast.classList.remove('is-visible');
      study?.classList.remove('score-shake');
    },1600);
    if(result?.complete){
      const panel=document.getElementById('scoreSummary');
      if(panel)panel.classList.add('score-finish');
      // The native V4 answer-jump remains intact. The score HUD and result
      // panel stay available without an auto-redirect hiding explanations.
    }
  }

  root.SUDU_SCORE_FEEDBACK = {
    questionPoints, countedAnswer, lockFirstAnswer, totalFor, render, announce, teachingHold
  };
  if (typeof module !== 'undefined' && module.exports)
    module.exports = root.SUDU_SCORE_FEEDBACK;
})(typeof window !== 'undefined' ? window : globalThis);
