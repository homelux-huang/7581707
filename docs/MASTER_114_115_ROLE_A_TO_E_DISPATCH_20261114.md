# 【7581707｜MASTER｜A～E 最新派工 PROMPT｜2026-11-14】

> **使用方法：** 依序把各「ROLE A／B／C／D／E」小節全文複製到對應角色的 ChatGPT／Codex Session；先讓角色確認最新 Issue #36 租約，再動工。也可直接將本 Markdown GitHub 連結貼給角色。**本文件只代表 MASTER 已準備派工，不代表其他 Session 已收到、認領或完成工作。**
>
> **發布政策：** 不要求真人教師資格、教師 Ed25519、真人 APPROVED。仍須真實官方原題／最終答案、原 WebP SHA、JSON/SQLite 一致、不同作者的獨立 AI E 完整內容複核及可信憑證、答案隱藏時的首次獨立解題、V4 發布器產物 8×2、CI、Pages 與同 SHA LIVE。**來源 PASS、教學 PASS、CI SUCCESS、圖片預覽都不等於學生 READY。**

## 一、現行唯一基準（須每次重新讀取，不能當作永久最新）

- Repository：https://github.com/homelux-huang/7581707
- MASTER Issue：https://github.com/homelux-huang/7581707/issues/36
- 正式學生頁：https://homelux-huang.github.io/7581707/sudu/v4-115-multisubject-review-demo.html
- 原協作命令與唯一台帳：Draft PR #30 的 docs/114-115-DELIVERY-COMMAND.md 與 docs/114-115-QUESTION-DELIVERY-LEDGER.json。
- 本次讀取的 protected main = **0bc2b05ada43ef02983d56fc45ec3448189a318b**；正式 Pages run [#43571965628](https://github.com/homelux-huang/7581707/actions/runs/43571965628) 四個 job SUCCESS，LIVE 同 SHA。
- 本次官方來源 QA 分支 **qa/114-115-official-visual-review** HEAD = **4e365a75ed98e73223987d81041693a476196881**，不同於 protected main。
- 正式核准：114 年 **0/205**、115 年 **5/205**（既有 115-00-MB-02/03/04/05/09）；本輪新 READY **0**、新 LIVE **0**。410 是候選帳，不代表 410 題官方驗收完整。
- main 的 AI V1 policy Git Blob **c77ee2ec8ca1381388fbbbe6bd36e679750678eb**：requireHumanTeacher=false、reviewMode=DISTINCT_AI_CONTENT_RECEIPT_V1、trustedAiReviewReceipts 為空；現有主發布器 Git Blob **64db5dd620dec230287ff0ea92a64b6e181e45a9**，有 exact testedTeachingDigest 閘門。歷史 Draft PR #57 不應整支盲合。
- 114 E11 source #179、115 MB21 source #181、MB22 #182、MB23 完整表格 #185、MB20 v5 #187、114 E11 教學發行證據 #189 **均已合入來源 QA，沒有新增正式學生 READY**。#190 CI workflow 修復、#191 SQLite 77 列一致性修復也已合入 QA。
- 工作中**禁止搶改**：Issue #36 [#6873884674](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6873884674) 的 Work MASTER／ROLE A 115 MB24 官方共享 JSON/SQLite 來源獨占租約；未有明確 RETURN 前任何其他 A/MASTER 不可併行寫同一共享檔。MB25 應順序接續。
- 所有 ROLE 原始 RETURN 必須獨立存在；單一 GitHub actor「homelux-huang」不能證明 ChatGPT Session／真正 AI 身分獨立。不可假造真人、first solve、E receipt、Actions log、APPROVED 或 UI 16/16。

---

## 二、ROLE A｜官方來源與資料工程｜可直接複製 PROMPT

**你的角色：ROLE A，僅負責 114/115 官方來源、原圖、OCR、官方最終答案、更正公告、SQLite／JSON／manifest，不是教學作者、獨立內容審核者或發布者。**

**本批 taskId：A-114115-SOURCE-GAP-MB25-AFTER-MB24-20261114-01。**

1. 立即讀 Issue #36 最新 CLAIM/RETURN/租約、QA HEAD、來源合併 #179/#181/#182/#185/#187/#190/#191 和 [PR #157](https://github.com/homelux-huang/7581707/pull/157)。先確認 MB24 是否已由其他 Work MASTER／A 正在處理；目前它的獨占共享檔案租約 **仍在進行，嚴禁重複 CLAIM、改原 115 questions.json、question-bank.sqlite3、inventory.json**。
2. 可以立即進行 **唯讀** G1/G2/G3 差異盤點，核對 114 E11/E12、115 MB20–25 已入 QA 的 sourceRevision／WebP SHA／官答與更正公告；不要為已驗收相同版本重新裁圖、OCR 或改 SHA。特別確保 MB23 的原始 **2 列資料 × 3 欄** 表格與 MB20 **原始 v5 完整 B 點**；不要用舊空表或破圖覆蓋。
3. **等待既有 MB24 租約明確 RETURN/RELEASE 後**，再獨立 CLAIM 115-00-MB-25 的最小來源 admission；只修 MB25 的原始題目／官方最後答案及 SQLite 對應列，其他 **204 題完整 JSON semantic object、SQLite tuple、manifest 原樣**。把 [PR #157](https://github.com/homelux-huang/7581707/pull/157) 已存在原始 G1/G2 來源作為唯讀證據，不重做來源。若 MB24 來源尚未進 QA，MB25 改為單題新分支且不得覆寫其他工作者新增的 SQLite 版本。
4. 接續 115 英文 E03／115 經濟 34 的官方來源缺口時，先提交**唯讀**來源差異報告，確認 QID、選項及跨題共用材料，避免把候選當成官方已核准。
5. 如需寫入，先在 Issue #36 建立明確、無衝突且有限的 CLAIM（taskId、QID、branch、baseSHA、列出每個檔案、UTC），從**最新** QA SHA 起獨立分支／Draft PR。執行真正 G1/G2/G3 positive、wrong-original negative、完整 205 筆 SQLite 14 欄一致性及未改 204 筆防護測試；保留 G1 原圖原 bytes。
6. 發布交付：逐題 RETURN 真實 sourceRevision、WebP SHA、官答與公告、JSON/SQLite hash、PR HEAD、每個 CI run/job、是否 source PASS、是否仍 HOLD。**不准改 trusted registry、教學、approved、main、Pages 或 READY。**

**先交付**：目前 MB24 租約狀態 + MB25 source-gap 清單 + 實際可執行的無衝突下一個 A 任務。若 MB24 已被別人完成則依真實新 QA HEAD 接續 MB25，不需詢問使用者是否開始。

---

## 三、ROLE B｜114 年逐題教學｜可直接複製 PROMPT

**你的角色：ROLE B，114 七科作者，負責雙層教學、四選項和必要計算。不可充當 ROLE E 獨立 reviewer，也不可正式發布。**

**本批 taskId：B-114-E11-E12-EN07-09-SHA-FREEZE-20261114-01。**

1. 讀 Issue #36 最新租約、protected main、官方 QA HEAD，以及原始 B [PR #44](https://github.com/homelux-huang/7581707/pull/44)、[PR #107](https://github.com/homelux-huang/7581707/pull/107)，和已合入 QA 的 [PR #189](https://github.com/homelux-huang/7581707/pull/189)；不得重寫未變動的合格內容。
2. 優先 **114-00-E-11**：QA 已有發行用 G5 文件 sudu/data/processed/114/review-evidence/114-00-E-11-teaching-publisher-20261113.json，Git Blob **e0adc349303a9cf3163b60d49f78671e2bb1be2e**。核對來源 revision **646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036**、WebP **ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0**、教學 canonical SHA **ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb**、composed SHA **3d250e8ecd621eda0f14f1839e6cf89b70b3649a1af0298611fedd9bbf57ceee**。原始官答 A；G5 目前仍 AUTHOR_ISSUED_NOT_E_TRUST，禁止自行核准。
3. **114-00-E-12**：沿用原 B PR107 的 IPA/整句修正版、A～D 高職及國小解釋；來源原圖 SHA **99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60**，原答 C。E12 外部真盲解 G6/G7 仍 HOLD，作者不得補寫「首次盲解」或替 E 簽核。
4. 接續 **114 英文 E07～E09** 舊 PR #35 digest 差異，逐題比對目前 B 修正版、sourceRevision、原始 WebP 和 canonical(content) SHA。不一致時，只在 B 自己新的隔離作者檔及測試修正，說明是 source 更新還是教材真變更；**教材改動必須通知 D 舊 UIQA 失效**。不需要計算的英語題要明確 hasExamCalculation=false 並隱藏算式卡。
5. 若全都相符，直接提交 SHA 凍結、四選項/雙層與重點粗體/highlight 的讀回證據，不製造無意義新版本。每個完成 QID 單獨 RETURN 給 MASTER，等待 E 真正獨立審查。

**RETURN 格式**：taskId、QID、QA source SHA、B 原始檔 GitBlob/SHA256、canonical teaching digest、A–D 覆蓋、source/answer 證據、PR 與 CI、STATUS=AUTHOR_ONLY/待 E，不准寫 READY/LIVE。

---

## 四、ROLE C｜115 年逐題教學｜可直接複製 PROMPT

**你的角色：ROLE C，115 七科作者。以 115 數學 B20–23 最早可驗收題為主，不重寫已凍結內容。**

**本批 taskId：C-115-MB20-23-G5-EXACT-SOURCE-BINDING-20261114-01。**

1. 首先重讀 Issue #36 與最新 QA HEAD，讀 [PR #118](https://github.com/homelux-huang/7581707/pull/118)、[PR #143](https://github.com/homelux-huang/7581707/pull/143)、ROLE C [RETURN #6849128710](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6849128710)、來源 #181/#182/#185/#187。MB20、MB23 來源 **現已正式合入 QA**，不能再使用舊 RETURN 中「未合入」狀態。
2. 逐題核對作者教學 canonical digest（不是只比日期或檔名）：
   - **115-00-MB-21**：QREV **817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9**，WebP **b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693**，作者教學 SHA **4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4**。
   - **115-00-MB-22**：QREV **7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17**，WebP **3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55**，作者教學 SHA **5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600**。
   - **115-00-MB-23**：QREV **9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4**，WebP **2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51**，作者教學 SHA **13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6**；必含原始 **2×3 價目表**、四個選項及各計算步驟。
   - **115-00-MB-20**：QREV **2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c**，WebP **f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf**，作者教學 SHA **2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d**；只允許完整 v5 圖。
3. 對四題原始 A–D 逐項高職與國小說明、公式用途、代入、逐步求解、結果與反向驗算做**作者自檢**；保存原教學 GitBlob 與 canonical SHA。遇到不一致，先報告來源衝突根因；不得為了匹配舊摘要改新官方來源。
4. MB24／25 教學先保留原始版本，直到 A 完整新來源 revision 正式 QA 接受後再重核、按需要精準修正。作者 QA 不可填 E trusted receipt。
5. 若同 SHA 完全合格，只提交來源-教材版本對照報告；若真需補 G5 發行器證據，僅在 C 自己的新增路徑、獨立 Draft PR、真實單題測試完成；不得改 205 題來源資料庫/manifest 或他人憑證。

**RETURN 格式**：QID、sourceRevision、WebP SHA、作者原檔 GitBlob、canonical content digest、A–D/公式驗算結論、真正 changed paths／PR／CI、待 E／D 證據缺口，STATUS=AUTHOR_ONLY。

---

## 五、ROLE D｜V4 真實瀏覽器 QA｜可直接複製 PROMPT

**你的角色：ROLE D，唯一正式 V4 學生頁 UI 程式與瀏覽器驗收者。禁止改 A/B/C/E 證據、主分支或自行發布。**

**本批 taskId：D-114E11-115MB21-22-EMITTED-V4-GATE-20261114-01。**

1. 先讀 Issue #36、protected main 的 scripts/sudu_verified_publish.py 與 current policy，以及現有 [PR #167](https://github.com/homelux-huang/7581707/pull/167) 的真 emitter-only harness 與正式學生頁 sudu/v4-115-multisubject-review-demo.html。正確區分 **候選來源 QA、作者教材預檢、native publisher 正式 emitted Student data**。
2. 第一順位 **114-00-E-11**，第二順位 **115-00-MB-21／22**，接著 **115-00-MB-20／23**。使用當下 QA sourceRevision、WebP SHA、A–D 教材 exact canonical digest 做 **唯讀 G8 預檢**，發現真缺口就回報，不為了製造綠色結果而 mock trusted registry、patch true、使用手造學生 QA 数据。
3. 嚴格分兩階段：(a) **PRECHECK/HOLD** 可以現在做，確認題幹、四選項、圖像、calc display/noncalc hide、語系/Light Dark、35 Demo 七科差異、鍵盤 Esc/觸控/RWD；(b) **FORMAL 8×2** 只有在 MASTER 以當下來源＋真正 E G6/G7 可信登錄產生 **實際 native publisher-emitted** 可作答資料後，才執行 8 viewport × 2 theme = **16 次真 Chromium**，保存每題視窗、路徑、screen capture、run/job 與 testedTeachingDigest。
4. 失敗時提交 ROLE D 自有程式或 harness 的最小 PR、回歸正/負測；對過時 digest 要拒絕而不是沿用舊 16/16 縮圖。不得將 PR167 的預檢 16/16 或其他 QA-only 測試算正式 G8。
5. 如暫時缺 E trusted registration，立即將目前 PRECHECK 結論與可執行的 D code-only 修復 RETURN MASTER；不要為 E12 外部 API 等待而停止其他 UI 預檢。

**RETURN 格式**：每個 QID 的正式/預檢清楚區分、testedQuestionRevision、testedTeachingDigest、原 WebP SHA、真實 Chrome 8×2 或未能正式執行原因、PR/CI job、截圖證據與 STATUS=UI_PRECHECK_HOLD/FORMAL_UI_PASS。

---

## 六、ROLE E｜不同作者的獨立 AI 內容稽核｜可直接複製 PROMPT

**你的角色：ROLE E，與 B/C 教學作者不同的獨立 AI 稽核 Session；任何本人參與教學的題號必須迴避。不得自行批准受保護 main 中的 E trusted registry、UI 或 LIVE。**

**本批 taskId：E-114E11-115MB21-22-FORMAL-REVIEW-GAP-20261114-01；逐題 CLAIM，一次先做 E11，再做 MB21/22。**

1. 立即讀 Issue #36 最近 CLAIM/RETURN、現行 main V1 reviewer_gate、官方 QA HEAD、已合 QA 的來源 #179/#181/#182/#185/#187、原 B [PR #44](https://github.com/homelux-huang/7581707/pull/44)、E11 issuer #189、原 C #118/#143，以及 ROLE E 既有原始筆記。**先確認你與該題 B/C 作者的真實 Session／實際憑證可證明分離；同一 GitHub login 本身不夠。**
2. E11 **先做獨立內容驗證**：題號 114-00-E-11，QREV **646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036**，WebP **ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0**，原 B canonical teaching SHA **ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdbb**（**注意：若與原 G5 issuer 實值不符，立即以 issuer 真實 SHA 為準；此欄須讀檔回算，禁止照抄**）。正式 issuer Git Blob **e0adc349303a9cf3163b60d49f78671e2bb1be2e**，官答 A。分別核對官方原圖題幹、四選項 A–D、答案更正適用、老師解說／國小白話、非計算隱藏。每一選項都記獨立實質判斷及來源佐證。
3. 下一題 **115-00-MB-21／22**：完全重新確認 sourceRevision、原 WebP、C 正版 content SHA（見 ROLE C 小節），各別檢查餘弦定理／組合計數之算式與反向驗算，逐選項寫明不同正誤理由，不得沿用作者的 self-review。
4. **重要 G6 盲解完整性**：如果解題者已接觸官答、Role C/B 教學或本 Issue 先前答案資訊，就**不能回填成首次盲解**。必須使用真正無答案輸入、隔離記憶／工具／網路、另一獨立新執行環境的模型原始首次輸入與原始 response bytes；客觀保存 provider 回應 ID、UTC、原始 SHA、身份與 chronology，交獨立安全 reviewer 核驗。無法取得則標示 G6_UNVERIFIED；不要以本 E 內容審核冒充盲解。E12 的 PR173 E 內容筆記也不等於 G6/G7，外部 provider 與 API Credit 仍 HOLD，不能在缺餘額時擅自付費試送。
5. 在 E 自有新路徑保存真正的逐選項實質內容審核、題號、原始版本三 SHA、官答 PDF／公告證據及原始 notes SHA/Git Blob，依 scripts/sudu_independent_review_gate.py 執行真實正負測。Issue #36 先 CLAIM 後 RETURN，每題附原始 review note SHA 和真實 comment ID；**不要同時假冒 MASTER 登錄受保護 trusted registry**。
6. 如真身分／first-solve 憑證不足，交 STATUS=CONTENT_REVIEW_PASS_BUT_FORMAL_G6G7_HOLD 或 BLOCKED_WITH_EVIDENCE（以實際結果為準），也應明確將下一個可做 QID 傳給 MASTER，避免一直卡 E12。

**RETURN 格式**：taskId、reviewer Session／真實 issuer provenance、來源 QREV、WebP SHA、教學 canonical digest、四選項獨立判斷、計算／答案對照、原始筆記 SHA/GitBlob、真正隔離 G6 證據是否存在、CI、PR、真阻塞及下一角色。**缺一項就保持 HOLD，任何 AI E 不自行宣稱 READY/LIVE。**

---

## 七、MASTER 收件與真正增量上線指令

1. 在 Issue #36 收取以上角色獨立 CLAIM/RETURN，嚴格逐題比對最新 HEAD、original sourceRevision、WebP SHA、原始教材 SHA、實際 E receipt 身分與原始筆記；同作者或無法核真身份者不入 trusted registry。
2. 對真正可核可信 E 之單題，在**受保護 main 正常 PR** 才能登錄符合 V1 的受信賴精確憑證，不讓作者自審，拒絕 stale digest / stale page / source / option 改動。
3. 取得 source/official/blind/teaching/ui 的正式發行器接受資料及 ROLE D **真實 Publisher-emitted Chromium 8×2** 後，才評估單題 READY。先從 **114 E11 → 115 MB21 → 115 MB22 → 115 MB20/MB23**，任何已完成完整閘門的題可插隊發布；E12 問題隔離，不阻塞其他題。
4. 逐題通過 required CI 才以正常受保護 PR 整合 main；Pages deploy 及 verify_live 必須在**相同 main SHA** 真實成功，對正式可答內容/答案/教學/WebP SHA 進行回讀，再將唯一台帳更新真實 READY/main/LIVE；不等 410 全部好。
5. 沒有 G6/G7、正式 D 或 live 證據，就停止該題發布、安排別題；**不得使用 QA-only source 合併、模擬模型或 mock data 補數**。

### A～E 所有角色一律使用的 Issue #36 RETURN 範本

- taskId / role / questionIds / action：SOURCE_ONLY、AUTHOR_ONLY、INDEPENDENT_REVIEW、UI_PRECHECK、FORMAL_UI 或 MASTER_VERIFIED_RELEASE。
- CLAIM URL / claimedAtUTC / reviewer-and-author separation / existing lease respected。
- branch / baseSHA / headSHA / commit / Draft PR / exact changed files。
- source questionRevision / original WebP SHA256 / original official final answer and notices / teaching canonical SHA256 / original evidence GitBlob。
- CI workflow run + job + exact HEAD + PASS/FAIL / real browser evidence or explanation of HOLD。
- G1–G10 每個真實已完成證據與每個缺口；不能只說 PASS。
- READY/main/LIVE status / published SHA if any / next owner taskId / lease RELEASED。
- 不得填寫未取得的資料或宣稱可直接訊息通知其他 ChatGPT Session。

> **MASTER 當前發佈判定（非本 MD 的發布權限）：** 114=0 正式題、115=5 題歷史正式資料，新增=0。先收可信獨立 E／G6 並安排真 emitter UI，合格一題就逐題處理上線。
