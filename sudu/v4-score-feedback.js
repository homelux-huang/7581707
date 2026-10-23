/* C-style exam dashboard for the existing 115 V4 five-question demo.
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
    round = validRound(round);
    const previous = countedAnswer(q, record, round);
    if (previous) {
      if (previous.legacy) {
        record.scoreRound = round;
        record.scoreCorrect = previous.correct;
        record.scoreChoice = record.selected || null;
      }
      return { eligible: true, first: false, points, earned: 0,
        correct: previous.correct };
    }
    const correct = selected === q.answer;
    record.scoreRound = round;
    record.scoreCorrect = correct;
    record.scoreChoice = selected;
    return { eligible: true, first: true, correct, points,
      earned: correct ? points : 0 };
  }

  function totalFor(questions, subject, records, round, year) {
    if (year !== 'demo' || !Array.isArray(questions) ||
        questions.length !== 5 || questions.some(q => q.subject !== subject ||
        !LETTERS.has(q.answer) || questionPoints(q, year) == null)) {
      return { eligible: false, reason: '非已核實的五題練習計分範圍' };
    }
    round = validRound(round);
    let earned = 0, max = 0, answered = 0, correct = 0, wrong = 0;
    for (const q of questions) {
      const points = questionPoints(q, year);
      max += points;
      const previous = countedAnswer(q, (records || {})[key(q)], round);
      if (!previous) continue;
      answered++;
      if (previous.correct) { correct++; earned += points; }
      else wrong++;
    }
    return { eligible: true, subject, round, answered, total: questions.length,
      correct, wrong, earned, max, missed: answered ? max - earned -
      questions.filter(q => !countedAnswer(q, (records || {})[key(q)], round))
        .reduce((sum, q) => sum + questionPoints(q, year), 0) : 0,
      percent: max > 0 ? Math.round(earned / max * 100) : 0,
      complete: answered === questions.length };
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
    hud.setAttribute('aria-label', '115統測題型五題練習計分儀表');
    hud.innerHTML = [
      '<div class="score-hud-left">',
        '<span class="score-eyebrow"><span class="score-status-dot" aria-hidden="true"></span>',
          '統測練習計分｜<span id="scoreSubject"></span></span>',
        '<div class="score-value-row"><strong id="scoreEarned">0</strong>',
          '<span class="score-divider">/ <span id="scoreMaximum">10</span> 分</span>',
          '<span class="score-percent" id="scoreRate">0%</span></div>',
      '</div>',
      '<div class="score-hud-right">',
        '<div class="score-hud-count"><span id="scoreAnswered">0 / 5 題</span>',
          '<span id="scoreStatus">未考完</span></div>',
        '<div class="score-meter" role="progressbar" aria-label="已得分占練習滿分的比例" ',
          'aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">',
          '<span id="scoreMeterFill"></span></div>',
        '<small>練習得分率｜答錯不倒扣</small>',
      '</div>'
    ].join('');
    study.insertBefore(hud, question);
    const summary = document.createElement('section');
    summary.id = 'scoreSummary';
    summary.className = 'score-summary';
    summary.hidden = true;
    summary.setAttribute('role','status');
    summary.innerHTML = [
      '<div class="score-summary-head"><span aria-hidden="true">🏁</span>',
       '<div><strong>本次科目練習完成！</strong>',
       '<span id="scoreSummarySubject"></span></div></div>',
      '<div class="score-summary-grid">',
        '<div class="score-summary-major"><span>本次練習小計</span>',
          '<strong id="scoreSummaryValue">0 / 10 分</strong></div>',
        '<div><span>練習得分率</span><strong id="scoreSummaryRate">0%</strong></div>',
        '<div><span>答對 / 答錯</span><strong id="scoreSummaryCounts">0 / 0 題</strong></div>',
      '</div>',
      '<p>依115學年度選擇題配分計算；不是整份統測正式成績。',
       '國文、英文的非選擇題及商管專業科目合卷總分，不包含在這五題小計中。</p>'
    ].join('');
    answer.insertAdjacentElement('afterend', summary);
    const toast = document.createElement('div');
    toast.id = 'scoreToast';
    toast.className = 'score-toast';
    toast.setAttribute('role','status');
    toast.setAttribute('aria-live','polite');
    toast.setAttribute('aria-atomic','true');
    document.body.appendChild(toast);
    return hud;
  }

  function render({ questions, subject, records, round, year }) {
    const result = totalFor(questions, subject, records, round, year);
    const hud = ensureUI();
    if (!hud) return result;
    const hidden = !result.eligible ||
      document.body.classList.contains('qa-image-mode') ||
      document.body.classList.contains('qa-error-mode');
    hud.hidden = hidden;
    const panel = document.getElementById('scoreSummary');
    panel.hidden = hidden || !result.complete;
    if (hidden) return result;
    const set = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = String(value);
    };
    set('scoreSubject', subject);
    set('scoreEarned', result.earned);
    set('scoreMaximum', result.max);
    set('scoreRate', result.percent + '%');
    set('scoreAnswered', result.answered + ' / ' + result.total + ' 題');
    set('scoreStatus', result.complete ? '已完成' : '未考完');
    const bar = document.querySelector('#scoreHud .score-meter');
    const fill = document.getElementById('scoreMeterFill');
    if (bar) bar.setAttribute('aria-valuenow', String(result.percent));
    if (fill) fill.style.width = result.percent + '%';
    hud.classList.toggle('is-complete', result.complete);
    if (result.complete) {
      set('scoreSummarySubject', '115 ' + subject + '｜五題練習');
      set('scoreSummaryValue', result.earned + ' / ' + result.max + ' 分');
      set('scoreSummaryRate', result.percent + '%');
      set('scoreSummaryCounts', result.correct + ' / ' + result.wrong + ' 題');
    }
    return result;
  }

  let activeTimer = null;
  function announce({ score, result }) {
    if (!score || !score.eligible || typeof document === 'undefined' ||
        document.body.classList.contains('qa-image-mode')) return;
    ensureUI();
    const toast = document.getElementById('scoreToast');
    if (!toast) return;
    if (activeTimer != null) clearTimeout(activeTimer);
    const correct = !!score.correct;
    const first = !!score.first;
    toast.className = 'score-toast';
    toast.classList.add(first ? (correct ? 'score-win' : 'score-lose') : 'score-repeat');
    if (first) {
      toast.textContent = (correct ? '✓ 答對　+' + score.points + ' 分' :
        '✕ 答錯　本題 0 分，少拿 ' + score.points + ' 分') +
        (result && result.eligible ? '｜累計 ' + result.earned + ' / ' + result.max + ' 分' : '');
    } else {
      toast.textContent = '此題已計分｜重答不重複加分';
    }
    const study = document.getElementById('studyView');
    if (study) {
      study.classList.remove('score-shake');
      // Restart the effect without modifying the surrounding document geometry.
      if (first && !correct) {
        void study.offsetWidth;
        study.classList.add('score-shake');
      }
    }
    const hud = document.getElementById('scoreHud');
    if (hud) {
      hud.classList.remove('score-pulse');
      if (first && correct) {
        void hud.offsetWidth;
        hud.classList.add('score-pulse');
      }
    }
    toast.classList.add('is-visible');
    activeTimer = setTimeout(() => {
      toast.classList.remove('is-visible');
      if (study) study.classList.remove('score-shake');
      if (hud) hud.classList.remove('score-pulse');
    }, 1500);
  }

  root.SUDU_SCORE_FEEDBACK = {
    questionPoints, countedAnswer, lockFirstAnswer, totalFor, render, announce
  };
  if (typeof module !== 'undefined' && module.exports)
    module.exports = root.SUDU_SCORE_FEEDBACK;
})(typeof window !== 'undefined' ? window : globalThis);
