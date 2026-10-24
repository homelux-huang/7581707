# 2026-10-24｜部署 Session 接續複核

已完成10題SHA與隔離狀態測試、數學B20/25圖文與計算複核；修正25選項A具體反證；將隔離V4預檢從鍵盤改為真實click/tap。詳見 `DEPLOY_QA_FOLLOWUP_20261024.md`。UI結果待CI，不授予正式憑證，READY仍0。

# 2026-10-24｜第1批10題原圖及教學內容修復交付（尚非READY_FOR_DEPLOYMENT）

- **教學分支 commit：`3ecb617f83da87f25ad9e7be645c355d68cc7459`**；base `ee74cbaad51740577b24a341559b17a2be5290ba`；未變更 main `5415a30452cdf9020242aca16fe0ff2b6814ab4b`。
- 本批逐題教學修正：`115-09-1-07`、`115-09-1-33`、`115-09-2-28`、`115-09-2-13`、`115-09-2-18`、`115-00-MB-20`、`115-00-MB-25`、`115-00-E-01`、`115-00-E-02`、`115-00-E-03`。
- 本輪實際打開10張既有原圖，重新計算**WebP原始位元組SHA256 10/10相符**；有實質內容修訂10題，三道爭議仍隔離。既存128/128初稿及官方答案來源核實未改。
- 修改內容：上述10個單題JSON、`solution-steps-128.js`、`progress.json`、`content-review-delivery-20261024.json`（含10題來源圖SHA256與教學canonical SHA256）、`BATCH_10_PEDAGOGY_QA_20261024.md`、`tests/test_preview_128_oct24_content.py`、read-only QA workflow（共16檔）。
- 工程／內容證據：[第一批提交](https://github.com/homelux-huang/7581707/commit/3ecb617f83da87f25ad9e7be645c355d68cc7459)；[逐題圖文重核報告](https://github.com/homelux-huang/7581707/blob/draft/preview-128-explanations-20261023/sudu/teaching-drafts/preview-128-20261023/BATCH_10_PEDAGOGY_QA_20261024.md)；[機器可讀manifest](https://github.com/homelux-huang/7581707/blob/draft/preview-128-explanations-20261023/sudu/teaching-drafts/preview-128-20261023/content-review-delivery-20261024.json)。
- 觸發的同SHA workflow： [readiness #40043821023](https://github.com/homelux-huang/7581707/actions/runs/40043821023)、[draft QA #40043821158](https://github.com/homelux-huang/7581707/actions/runs/40043821158)、[latest-main UI preflight #40043821026](https://github.com/homelux-huang/7581707/actions/runs/40043821026)。在確認completed/success前**不得記錄PASS**。
- 真正剩餘阻塞：**128題完整獨立教學QA仍未PASS；128題正式V4對應教學內容之8 RWD×2主題、click/touch與highlight完整獨立UI QA未取得PASS；3題官方/AI概念爭議保持醒目警示；數學B20–25舊OCR文字風險隔離；當屆彰化高商實際採用教材頁碼未核。** 所有資料`studentReleaseApproved=false`、`deploy=false`。
- 交付統計：初稿128、原圖SHA既有128且本次新增再驗10、官方最終答案原有128、本批部分教學內容修訂10、**完整教學QA=0、UI QA=0、READY_FOR_DEPLOYMENT=0、新增正式部署=0**。既有main四題另計。

**部署Session請依序**：讀上述commit＋manifest；核對十題的圖像SHA和教學SHA及A-D；針對實際已改文字進行獨立教學審核（非單靠此Session自行複核）；在最新main V4隔離注入資料做8尺寸×2主題逐題真實mouse-click、手機touch、錯題複習與highlights；各題有真實審核憑證後才逐題打開READY_FOR_DEPLOYMENT，依法遵守正式QA gate。**本批沒有可安全發布的題，勿提前接入main或approved**。

**給原部署Session可貼訊息（本Session沒有跨對話主動傳訊能力，未聲稱已送）：**
> 7581707教學第1批10題修正已存GitHub `draft/preview-128-explanations-20261023` commit `3ecb617f83da87f25ad9e7be645c355d68cc7459`。請讀`DEPLOY_SESSION_HANDOFF_128.md`和`content-review-delivery-20261024.json`；10張原圖SHA已再驗；3道爭議仍隔離，未完成獨立教學及V4 UI實測，READY=0，本批不可部署。CI run 40043821023/40043821158/40043821026須另查結果。

---

## 2026-10-23｜商概及數科固定12題原圖SHA全部到齊、會計增加3題（非完整教學QA）
- 數科32、34與會計01、02、04共5題，實際WebP位元組SHA和逐題目視PASS；部分解說觀念複核。至此商概5／數科7共12題均完成原WebP本週期再驗，非完整答案教學QA。證據`BIZ_TECH_ACCOUNTING_5_20261023.md`。
- 固定128題原圖與SHA去重67/128，封存公告答案影像對照49/128；官方最終更正查證0/128，獨立教學全項QA0、部署0；原BLOCKED持續保留。

## 2026-10-23｜數學B25題本輪全部原WebP及計算子項複驗完成（非完整教學QA）
- 最後4題數學B22～25圖像SHA實算及目視、附圖/選項QA均PASS，重算五卡片補集、雙行程費用、複利估年、圓與直線相切；詳見 `MATHB_22_25_IMAGE_FORMULA_QA_20261023.md`。
- 加上此前 01～21，**數學B25/25張**本週期完成原WebP再次SHA256及目視並有算式推演局部複核，不冒充完整教學QA。固定128題原圖去重57/128、存檔公告答表影像對照39/128；官方最終更正0/128、獨立教學完整QA0、正式發布0。原三道概念BLOCKED與首次解答差異仍保留。

## 2026-10-23｜官方公告答案封存影像三批15題交叉核實完成（非最終更正QA）
- 115年商管專一5、商管專二9、數學B1題：三份舊官方標準答案PDF轉出的GitHub封存WebP，重新取得二進位驗SHA全部匹配 `sudu/data/original/answers.json`，目視15題的表格選項皆與草稿候選一致。三份批次紀錄 `ARCHIVED_ANSWER_IMAGE_09-1_5_20261023.md`、`ARCHIVED_ANSWER_IMAGE_09-2_A_5_20261023.md`、`ARCHIVED_ANSWER_IMAGE_LAST_5_20261023.md`。
- 原PDF bytes本輪未重新取回、疑義確認說明PDF尚未回讀，官方最終更正核實=0/128、完整教學QA=0/128、發布合格0、正式部署0；已有原圖獨立SHA複核33/128。
- 三個BLOCKED不因舊答案影像相符而解除，原始AI判讀差異不改，原題 WebP、OCR、main、approved、學生紀錄均未動。

## 2026-10-23 checkpoint｜10題重新WebP/SHA256複核：新增加7題（不發布）
- 從 GitHub 原圖原位元組開圖10張、SHA256皆一致；其中三個BLOCKED題已在先前21張內，本次不重複計數。新增商概03/05、數學B07、經濟25/26/27/29共7張；本週期去重共33/128，剩95張。
- 數學B07 a=-134°、b=245°，第二象限；經濟26每家90×10=900；經濟27兩條通過原點的供給直線彈性皆1，圖示完整在單題圖內；其餘兩道經濟題均已重看情境。三個原BLOCKED及商概03/05語義歧義未因本次放行。詳細見 `ORIGINAL_RECHECK_10_20261023.md`。
- 官網115/114公布頁可讀，正式PDF下載器無法讀取，官方最終核實0/128、完整教學QA0/128、正式合格0、部署0；不改main、approved、Pages、學生學習紀錄。

## 2026-10-23 checkpoint｜新增5題真實WebP／SHA256與部分會計、商概複核（未發布）
- 本輪使用GitHub原WebP位元組逐張重新SHA256並開圖：115-09-2-03、06、12、15與115-09-1-01全部一致，且sharedImages為空。**本週期累計26/128**，剩餘102張未重驗，歷史128/128與本輪不可混淆。
- 會計03原圖「供出售」；12「原始對帳單≠調節後餘額」；15重算存貨10500、盤虧1000、依題型成本13500，列報政策仍待教材；06前期備抵結轉邏輯；商概01的④文字過度推論待審。完整證據見 `POST_CANDIDATE_RECHECK_5_20261023.md`，獨立首次判讀差異照舊保留。
- 官方115最終PDF下載器仍無法從本工具回讀（官網只可見公告與欄位），正式官方逐題核實仍0/128、完整獨立教學QA0/128、正式發布合格0/128、部署0。本次未動main、approved、正式UI、Pages或學生紀錄。

# 7581707｜固定128題解說草稿→正式平台 Session 交接（非發布核准）
更新：2026-10-23。交接來源：`homelux-huang/7581707` 分支 `draft/preview-128-explanations-20261023`。正式平台整合應由另一個Session執行；本批草稿仍禁止部署。

## 1. 接手時先做
1. 使用 GitHub Git Ref API 重新讀取本分支**最新 HEAD**，不得回到首次交接commit。
2. 讀 `sudu/teaching-drafts/preview-128-20261023/progress.json`、`HANDOFF.md`、`STRUCTURAL_QA_128_20261023.md`、`STEP_BY_STEP_QA.md` 及各獨立題目JSON。另一Session已修改的檔案必須採最新內容，不可覆寫。
3. **唯一凍結範圍是 progress.json.items 的128題**：114國文9；115國文9、英文28、數學B25、商業概論5、數位科技7、會計學21、經濟學24。題號、每題單圖SHA256、sharedImages仍以該清單為準；不可多算或混入其他年份的新題。

## 2. 可直接供介面「草稿預覽」讀取的解說資料（不等於可公開）
- 每題 `teaching.teacherSummary`：高職生理解的原理；`elementarySummary`：國小口語說明；`optionExplanations.A/B/C/D`：四個選項各有teacher與elementary雙層正誤理由。
- 每題 `teaching.concept`：核心觀念；`memory`：「一眼記住」既有內容；`extension`：反向思考；`highlightTerms`：可高亮重點詞。
- **國文18題專屬補強已寫齊**：各題 `teaching.keyPointBullets` 恰3段解題重點、專屬extension與 `chineseEnrichment` 初級/中級/高級相關詞草稿。教育部詞典核實來源包括揩／搴、愀然／默然、橫槊賦詩。其餘讀音、詞彙分級、實際課本版次章節頁碼仍需獨立核對。
- 既有 `teaching.stepByStep`（82題，含有逐步演算或多階段理由）與 `solution-steps-128.js` 同題索引；國文18、英文28共46題無相應算式步驟，自動隱藏「解題步驟」空框。若更新stepByStep，記得同步其索引。
- 需要數學、會計或經濟計算時，`teaching.examCalculation`保存已知條件、公式／理由、代入、各步算式、結果與單位；有時`stepByStep`與舊計算框涵蓋相同內容，整合UI時只能顯示一次，不得重複或杜撰數字。
- 最新另一Session UI要求：保留「解說重點」，獨立「一眼記住」框取消，`memory`併進「解說重點」而不重複；計算題的「考題計算式」置於「解說重點」最上面，沒算式的題自動隱藏。本交接只描述資料與映射，**沒有修改正式UI**。

## 3. 驗收證據與嚴重阻塞（請勿跳過）
- 結構QA歷史紀錄：128份JSON已可解析且有四選項雙層說明；原圖目視歷史紀錄128／128。**本次重新從GitHub取得實際WebP位元組、親自開圖、核對SHA256的是21／128張**：全部國文18張＋三個答案爭議題的單圖，且這21題sharedImages皆空。剩餘107題本次未重驗，歷史紀錄不等於最新再次QA。
- **官方最終答案及更正確認PDF逐題核實仍是0／128**，完整獨立教學QA **0／128**，本批部署**0**。不能將草稿數128／128當成官方核准；官方公告頁並不等於已下載讀完最終標準答案PDF。
- 官方答案入口：https://web1.tcte.edu.tw/EXAM/115_4y/（測驗中心公告2026-05-08 17:00確認最終答案），114頁：https://web1.tcte.edu.tw/EXAM/114_4y/。仍須逐卷下載最終PDF及疑義答覆，確認考科、題號、公告版本、是否更正。
- 次級交叉參考（**非官方最終核實**）：https://tck.com.tw/sites/exam/114_4g/c/tck-114-4y-00-c.pdf ，114國文第2～10題C/D/D/B/C/C/B/A/B與既有草稿候選相符。絕不可把第三方參考答案標為官方核實。
- 三個硬阻塞仍維持BLOCKED：`115-09-1-07`特別股財務槓桿定義、`115-09-1-33`雜湊/數位簽章與加解密差異、`115-09-2-28`無總預算而AI得D／候選A的歧義。不能暗中套候選答案或解除醒目警示。
- 優先獨立複核首次判讀分歧：`115-09-2-03`、`115-09-2-06`、`115-09-2-12`、`115-09-2-15`；商概`115-09-1-01`、`115-09-1-03`、`115-09-1-05`的教材措辭或分類也需查證。其餘128題仍須完整計算與教材教學QA。
- 靜態 `STEP_BY_STEP_QA.md` 並非真實瀏覽器測試；手機/RWD/高亮/深淺主題/解答跳轉/正解警示仍需實測。

## 4. 給另一個正式平台Session的具體工作順序
1. 固定128題ID、原圖SHA及sharedImages；逐卷建立最終官方答案表（含原始PDF連結、版本、公告、更正、逐題比對、簽核證據）。
2. 逐題獨立核實兩層四選項、公式分錄、A-D錯因、重點、反向題，已見候選者誠實標示，難題維持BLOCKED。教材版次／章節／頁碼未查證就維持待核對。
3. 實際在獨立測試環境接入已核對資料，依最新UI需求排列「解說重點」與計算步驟；確保原圖只含單題、共享文章完整、highlight和手機操作通過。
4. 執行JS與GitHub Actions檢查、Playwright瀏覽器驗收、UI對比/可及性及答案不一致警告測試；先作QA報告再按**另一Session明確正式發布授權與放行流程**決定是否公開。**不能把本草稿直接全量合併main或將128題標 approved。**

## 5. 不得破壞的邊界
- 本批絕對不部署GitHub Pages、不合併`main`、不更動`sudu/data/approved`、不動學生學習紀錄、不設定 `studentReleaseApproved=true`，不呼叫任何正式workflow_dispatch。
- 本文件是交接，不是release approval。當用戶在另一Session另行發布時，仍必須完成可核實QA與官方答案門檻，不以本文件代替。
- 目前數字：解說初稿128/128；本次新增原圖SHA實證21/128；國文重點18/18；82題有stepByStep、46題隱藏；官方最終核實0/128；完整教學QA0/128；本批部署0。
