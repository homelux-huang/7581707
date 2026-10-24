# 2026-10-24｜逐題第一候選 E03 真實原題與教學來源修復（維持隔離直到完整證書）

- 最新實質內容 commit `3399a3abd90bedac8ebad14c9bdb8368a6608afa`；E03 新 teaching canonical SHA256 `c7bce2469356f95e929b19d5275cd3ca1a4ff8f2c9f89cd858b61e5c8cdc3316`，原圖 SHA256 `16c8e37d3f169f0488398844030bf4922c4f4639633ee7a4d9a9af83466d8ebd`。
- 舊候選 UI 最新完整綠燈 [Actions #40048104080](https://github.com/homelux-huang/7581707/actions/runs/40048104080)：E03 真點擊／觸控／錯題復習、8×2、單題原圖與解說成功。由於本批後續修訂教學來源與 IPA，**不能沿用舊 SHA 作新教學版本正式 UI 驗收**。
- 最新 `tests/sudu_english03_isolated_ui.cjs` 改用真正 `sudu/data/years/115.json` 題幹與四個選項，不再手填練習題。E03 四選項語義、新聞原始出處、Cambridge 發音查核詳 `E03_PEDAGOGY_SOURCE_QA_20261024.md`；已修正原無法取回的新聞網址及 IPA、補同義詞不能任意替換的教學提醒。
- **真正的學生發布阻塞**：`qa/114-115-official-visual-review` 分支 student-certified 現僅數學B02/03/04/09，E03 尚缺符合 `scripts/sudu_verified_publish.py` 的 source OCR text QA、事前獨立解題證據、正式獨立教學證據及 UI 覆核憑證。不得追認已知答案後審查成盲解，亦不得因 8×2 隔離 UI 綠燈改 releaseApproved。先完成各層真實查證才可交由原部署 Session 依 same-SHA gate 增量發布。
- 統計：既有 main 四道數學B仍單獨核准；本批新正式教學 READY=0、新部署=0。教學草稿 E03 已改善；工作應繼續其他非爭議題，不能讓此題來源認證拖住後續。
- 無跨 Session 通訊 API 已確認，此交接文字與 manifest 是可供原部署 Session 直接取用的持久通知，**未宣稱已直接送達其他對話**。

---

# 2026-10-24｜逐題增量發布工作：E03 UI 阻塞實修與解碼診斷（未放行）

- 使用者已授權逐題完成即可增量發布；仍須各題實際 QA 與正式 same-SHA Pages 部署。正式 main SHA 最後檢查為 `5415a30452cdf9020242aca16fe0ff2b6814ab4b`；主開發 Session 統一合併。
- E03 對應原圖 `sudu/data/approved/webp/115/115-00-E-03.webp`；GitHub main 與 draft blob 皆 `f511b6b5447c38f4cb91ec14572adef56f79991f`，直接目視內容完整：題3原句、A carelessly/B equally/C instantly/D silently，官答 B。這不是正式的所有 UI 核准。
- **真實修正1：** `tests/sudu_english03_isolated_ui.cjs` 依正式 V4 的「答後收合」導覽，改以真實 pointer/touch 操作 `#navHandle` 展開，再用 `#reviewTop` 進錯題復習，不以 force click 掩蓋。提交 `a98c9fa98dec69636e9fb6d3671524e6a8ebbb61`。
- [CI #40047884759](https://github.com/homelux-huang/7581707/actions/runs/40047884759) 數學B7題×8尺寸×2主題預檢 PASS，但英文E03在原圖 decode 時失敗（`EncodingError: The source image cannot be decoded`），故**整體workflow FAIL，絕不可將E03記成 UI PASS**。不是另一個確認導覽失敗的證據，因該次先在圖像載入中止。
- **真實修正2：** 再補 `img.currentSrc`、HTTP status、回應位元組、decodeError、原始src等診斷，提交 `d56eaaf48956bfd607fa0538f0069501ea02d4d2`；[CI #40048048087](https://github.com/homelux-huang/7581707/actions/runs/40048048087) 正在驗證，完成前不記PASS。需讀 CI log 判斷是圖片網路/路徑/404或媒體本身解碼問題，修復後再跑所有真實 E03 8×2 測項。
- 來源分支 `qa/114-115-official-visual-review` 僅有四個 Math B `STUDENT_QA_APPROVED` 紀錄，E03 沒有 `verified-student-batch.json` 的獨立先行解答、OCR文字/正式答案與教學/UI同來源SHA認證。不能因草稿128答案核對與隔離fixture測試便擅自偽造 `solvedWithoutOfficialAnswer=true`、降低 admission gate 或將 E03 放入正式 main；須補真正可追溯的驗收或隔離此題改驗下一題。
- 本回合新增READY=0；新進度系統要分開計算舊正式Math B 4題及新草稿128題。資料工程原圖、OCR、SQLite及學生紀錄未修改。
- 給部署 Session：只可接入拿到完整原圖/官方/教學/UI同SHA憑證的題，先隔離測試後依正式 `scripts/sudu_verified_publish.py`、`pages.yml` 驗證及 LIVE SHA 核對。**目前不得直接合併或宣稱E03上線。**

---

# 2026-10-24｜接入修復與E03真實內容UI測試

發現教學分支轉接器基底落後main，已在草稿中保留main最新首頁／逐題原圖架構並移入markup修正。新增E03無選項佔位文字的8×2隔離V4測試。詳見 `E03_INTEGRATION_QA_20261024.md`；UI結果待實際CI，READY仍0，main未動。

# 2026-10-24｜後續接手：既有正式 V4 年度轉接器文字與 highlight 修復（尚未發布）

- **最新內容提交**：`cd99e681850f835daf0ff57e1fd15008ccad144d`；這批不更動 main、正式 approved、128 題 QA 與學生作答紀錄。
- 修正 `sudu/verified-questions-runtime.js`：對經過HTML escape的教學資料，安全渲染 `**粗體**`、對真實出現詞形建立 mark，不執行草稿 HTML；四選項如果老師文字與 reason 重複則只呈現一次。答後重點/計算留在 guide，不在正解重複整排。修復 join 不可只高亮 joined 一部分的英文詞界限錯誤。
- 新增 `tests/sudu_verified_teaching_markup_test.cjs`，read-only QA workflow 納入測試。
- 初次新測試 [run #40046604901](https://github.com/homelux-huang/7581707/actions/runs/40046604901) **FAIL**：抓出 join 會誤被標在 joined 字首。已依真正 log 修復，必須以修復提交的新 CI 為準；不可把失敗標 PASS。
- 來源盤點新檔：`ALL_YEARS_SOURCE_INVENTORY_20261024.json` 已逐年讀取 104–115 `sudu/data/years/*.json` 現存原始紀錄，12 年總計 2453 筆，內含未完成來源與佔位，不能算全部完整題目QA；保留固定128題原manifest作第一優先，再擴大114/115，隨後113到104。
- **新 READY=0、正式 main 合併=0、此次新增部署=0**。先確認此次測試通過，隨後針對非爭議英文 E03 及其他題目的真實 V4 8x2 操作進行完整隔離QA，不能沿用含佔位文字的 MathB19–25 預檢當正式憑證。
- 當前無跨 Session 發送工具：請原部署 Session 以本 handoff、精確教學分支 HEAD 與 source inventory 繼續處理。本輪沒有聲稱已直接通知。

---

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
