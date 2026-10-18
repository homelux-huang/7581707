/* Teacher-curated explanations for original practice accounting questions.
   These are general accounting teaching notes, NOT verified textbook chapters.
   Official TCTE questions must not inherit them without checking the original text and answer. */
const SUDU_ACCOUNTING_TEACHER={
  "practice-會計學-01": {
    "concept": "企業個體假設",
    "principle": "企業與業主在會計紀錄上視為不同個體。老闆的私人財物，不會因為老闆擁有商店就自動成為商店資產。",
    "analogy": "把老闆與商店想成兩個各自上鎖的存錢筒。腳踏車放在老闆的筒裡，沒正式投入公司，就不能算商店設備。",
    "pitfall": "「老闆的東西就是公司的」是錯的。真正要看財物是否屬於企業、是否投入供企業使用。",
    "key": "企業個體假設"
  },
  "practice-會計學-02": {
    "concept": "銷貨毛利與銷貨成本",
    "principle": "銷貨毛利＝銷貨淨額－銷貨成本；毛利還要再扣營業費用等，才可能得到最終的淨利。",
    "analogy": "一個玩具賣 500 元，進貨花 300 元。先把買玩具的錢還回去，剩下的 200 元叫毛利，還不是整家店最後賺到的錢。",
    "pitfall": "不要把銷貨收入和銷貨成本相加，也不要把毛利當作淨利。",
    "key": "銷貨毛利"
  },
  "practice-會計學-03": {
    "concept": "借貸法則",
    "principle": "資產增加記借方，資產減少記貸方；現金買設備屬於資產間的交換，資產總額不因這筆交易增加。",
    "analogy": "拿出 2,000 元現金換回一張 2,000 元的桌子：口袋錢少了，店裡設備多了，只是資產換了樣子。",
    "pitfall": "會計的借方和貸方是記帳方向，不是日常說的借錢與還錢。",
    "key": "借貸法則"
  },
  "practice-會計學-04": {
    "concept": "流動比率",
    "principle": "流動比率＝流動資產÷流動負債，常用來觀察企業應付短期債務的能力；比率高並不保證一定有現金。",
    "analogy": "你短期需要付 100 元，手上短期可變現的資源約有 200 元，兩者相比是 2 倍。",
    "pitfall": "先看分子是流動資產，分母是流動負債。不要除反，也不能只憑一個比率斷定公司完全沒風險。",
    "key": "流動比率"
  },
  "practice-會計學-05": {
    "concept": "先進先出法",
    "principle": "先進先出法（FIFO）把最早購入的存貨成本優先列為銷貨成本，是成本流動假設，未必等於貨物實際出庫順序。",
    "analogy": "兩批筆記本像排隊，計算成本時先用前面那一批的價格。最早每本 10 元，賣 1 本先算成本 10 元。",
    "pitfall": "不是把所有成本平均，也不是拿最新一批的 20 元直接算。",
    "key": "先進先出法"
  },
  "practice-會計學-06": {
    "concept": "權責基礎與預收收入",
    "principle": "權責基礎重視收入何時賺得。企業先收錢、還未提供服務時，通常先列預收款項的負債，履約後才認列收入。",
    "analogy": "你先拿到下個月補習費，但還沒開始上課，就像先收下同學的錢卻還欠他上課服務；不是今天已全部賺到。",
    "pitfall": "收到現金不一定代表收入已實現；也不能把預收學費當成購置設備。",
    "key": "預收收入"
  },
  "practice-會計學-07": {
    "concept": "直線法折舊",
    "principle": "直線法每年折舊＝（成本－估計殘值）÷估計耐用年限。折舊是把設備可折舊成本合理分攤到使用年度。",
    "analogy": "一台機器可用 4 年，好比把它可分攤的價值平均切成 4 塊，每年分攤 1 塊，不是每年又花錢買一台。",
    "pitfall": "不能忽略殘值；折舊不是設備當年實際付出的現金。",
    "key": "直線法折舊"
  },
  "practice-會計學-08": {
    "concept": "銀行調節表與未兌現支票",
    "principle": "未兌現支票是公司已記錄支出、銀行尚未扣帳的支票。編銀行存款調節表時，通常從銀行對帳單餘額扣除。",
    "analogy": "你已把支付的支票交出去，但對方還沒拿去銀行換錢，銀行的帳就暫時看起來比較多，所以銀行那邊要扣掉。",
    "pitfall": "不要把未兌現支票當成銀行已扣除的錢，也不要在銀行端加回。",
    "key": "未兌現支票"
  }
};
function suduAccountingTeacher(q){
 if(!q||q.subject!=='會計學')return '';
 const note=q.official?null:SUDU_ACCOUNTING_TEACHER[q.id];
 if(!note){
  if(q.official&&!q.teachingVerified)
   return '<div class="accounting-teacher pending"><h3>👩‍🏫 高職會計老師｜待核實的觀念</h3><p>本正式題的原卷、標準答案與教材章節尚未全數核對，暫不寫出推測的老師詳解。</p></div>';
  const principle=q.principle||'';
  return principle?'<div class="accounting-teacher"><h3>👩‍🏫 高職會計老師｜核心原理</h3><p>'+keyHtml(principle,q)+'</p></div>':'';
 }
 return '<div class="accounting-teacher"><h3>👩‍🏫 高職會計老師｜重要觀念</h3>'
   +'<p><strong>考試關鍵字：</strong><mark class="concept-key">'+esc(note.key)+'</mark></p>'
   +'<p><strong>老師教原理：</strong>'+keyHtml(note.principle,q)+'</p>'
   +'<p><strong>小學生白話：</strong>'+keyHtml(note.analogy,q)+'</p>'
   +'<p><strong>常見答錯原因：</strong>'+keyHtml(note.pitfall,q)+'</p>'
   +'<p class="teacher-attribution">來源：本站自編會計學基礎觀念教學整理。與彰化高商實際教科書的精確章節、頁碼尚未核實；並非官方統測原題解析。</p></div>';
}
