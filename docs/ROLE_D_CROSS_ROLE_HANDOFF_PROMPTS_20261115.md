# 7581707｜ROLE D 跨角色阻塞回報與可貼上 PROMPT｜2026-11-15

本檔由 ROLE D 整理，**不是**其他角色已接單或已執行的證明；依角色貼到其現有 Session。每個角色首先必須重新讀 GitHub 最新 HEAD、Issue #36 的 CLAIM／RETURN／租約，避免使用此快照當作永遠最新。不要另建網站、不要 Sites。

- Repo：https://github.com/homelux-huang/7581707
- MASTER：https://github.com/homelux-huang/7581707/issues/36
- V4：https://homelux-huang.github.io/7581707/sudu/v4-115-multisubject-review-demo.html
- 本次核實 protected main：`ceda0a0248cb7dc99941758e9e16582e463516ca`
- 本次核實官方 QA：`fec4ff58fbe63170fb42b4c47ad76c08848e8ece`
- main publisher Git Blob `d410b10ff75ff7bfbb465098b0c2e5dd5b104978`
- V4 HTML Blob `3021bcb7846c80f74090b3c3c358c734c5a374f8`；runtime Blob `6e83938eb4bc4f23e1417742f87a3fc6681e0616`
- 受保護 E V1 policy Blob `c77ee2ec8ca1381388fbbbe6bd36e679750678eb`，`trustedAiReviewReceipts={}`
- PR203 已合併，Pages run https://github.com/homelux-huang/7581707/actions/runs/43672475148 同 SHA LIVE VERIFIED；現有 114=0，115=5（既有 MB02/03/04/05/09）；新題目正式 LIVE=0
- ROLE D 新增 [PR205](https://github.com/homelux-huang/7581707/pull/205) Draft HEAD `11f58d67c4a4a74df45fc787cec6abb2b0277290`，實際 [Actions43673921029](https://github.com/homelux-huang/7581707/actions/runs/43673921029) **COMPLETED SUCCESS，兩個 jobs 都成功**（protected-six-QID HOLD；E12 16x Chromium unpublished-negative）。**非正式 G8**
- PR167 原 D harness Draft；PR199 已合併進 PR167 分支（不是 main）。
- 原 PR202 私有技術預檢仍非正式 staging/G8；MASTER 最新 Issue36 RETURN #6888851647 已另建當前 main 基準之 [PR210](https://github.com/homelux-huang/7581707/pull/210)，取代舊 PR202；PR210 也**僅為 TECHNICAL_PRECHECK_ONLY**，不是正式 G8。請先讀最新 PR210/Issue36，不要重複修同一段。
- E #206 的 E11/MB21/MB22 與 E #208 的 MB20/23/24/25 實質來源／內容審查有新證據，但真實作者與 reviewer ChatGPT Session 身分、獨立 G6/G7/受保護 V1 trust 尚未完成。不能把內容 PASS 當成正式可信憑證。
- ROLE A 已 CLAIM 乾淨無答案 G6 輸入包 #6888818246；G6 操作員 #6888802647 明確尚未執行首次盲解。不可重複製作或假設已執行。
- ROLE B E07 G5 Draft PR207 已有作者-only RETURN #6888829698；ROLE E MB20/23/24/25 PR208 已有內容 QA RETURN #6888824745。不要重做。
- 使用者優先新 QID：`114-00-E-11`、`115-00-MB-21`、`115-00-MB-22`，後續 MB20/23/24/25；E12 保持 G6/G7 HOLD。

## PROMPT 1｜交 MASTER：正式 staging 契約與跨角色排程（P0）

你是 7581707 唯一 MASTER，這是既有平台接續；先讀上列 Repo／Issue #36 最新 HEAD 與相關 RETURN，不需要 Sites、不重建網站。

ROLE D 已確認 PR203 的 MB23 2×3 表格 publisher 修復正式部署且不新增學生題。**P0 唯一程式契約阻塞：** `scripts/sudu_verified_publish.py` 仍要求 UI certificate、`uiQaStatus=PASS` 與五文件 `STUDENT_QA_APPROVED` 才輸出可作答資料；但正式 D G8 又必須測試真正 native publisher-emitted staging bytes。這是相互等待的循環。

任務：
1. 優先讀目前 PR210（已代替過時 PR202），不得將 `TECHNICAL_PRECHECK_ONLY` 提升為正式 G8，也不重做其既有修正。
2. 獨立開有上限的 MASTER-own publisher contract PR，建立**可信 G1–G7＋V1 protected E receipt 後**、正式 promotion 前的 authenticated *staging emission* 及不可公開用途限定。將 `PRE_G8_ONLY`／技術預檢、真正 publisher staging、D `FORMAL_G8_16/16`、最終 promotion 四種狀態用強型別與 SHA 證據區分。
3. staging 僅用既有生產 serializer／renderer、原始來源題幹 A-D/共用表格及 WebP bytes；不修改受保護 trust、approved、原始來源、學生 Pages。不以假 `uiQaStatus=PASS`、手工 `STUDENT_QA_APPROVED`、route 攔截或 mock receipt 解循環。
4. 加入負向 gate：缺 E/G6、身份不明、sourceRevision/teachingDigest/image/hash 過時、HTML/runtime/publisher 變版、原批次被替換、先 promotion 才做 D G8 全部拒絕；仍保留原有 35 Demo 和歷史五題。
5. 準備每題正式 staging 真實 artifact 路徑、raw JSON SHA256、sourceCommit、QREV、WebP SHA、teachingDigest、publisher/HTML/runtime Blob、實際 GitHub Actions run/job；獨立提供 ROLE D，而不是宣稱已替 D 做了16次。
6. 只有 D 的同一份 bytes 真 Chromium 16／16 合格、MASTER 再次查核後，才允許受保護 PR promotion、Pages 同 SHA 部署與 verify_live。任一關變動撤銷舊 G8。
7. 跟進 D [PR205](https://github.com/homelux-huang/7581707/pull/205) 已真 CI SUCCESS，但只針對 ROLE D 測試邏輯，正式前置仍 HOLD。MASTER 不要把它當新題正式 G8。
8. 接收各角色下一個 RETURN、派工不重疊租約。無法驗證一律 HOLD，依 E11→MB21→MB22 順序，但單題卡住不要停其他題。

交付：taskId、CLAIM、branch/baseSHA/HEAD、僅 MASTER 擁有的 changed paths、實際正負 CI run/job、staging 內容及 SHA、信任缺口、D 交接輸入、是否 RELEASED、下一步。不自行宣稱新題 LIVE。

## PROMPT 2｜交 ROLE E：真實 E V1 內容憑證與作者身分缺口（P0）

你是獨立 ROLE E，不是 B/C 作者或 MASTER。先刷新 Issue #36 目前 E #206/#208 RETURN 及其實際 QA / CI；已有實質內容與數學核算不要重寫，且**不可**以 GitHub actor、role 標籤、自造 UUID 或後來的 Session 冒充原作者或真獨立 reviewer。

任務：
1. 優先 114 E11、115 MB21、MB22。原始 WebP、G2/G3/G5 canonical SHA、官方更正適用、逐選項 A-D、高職／國小雙層教學及數學反算已在 PR206／208 類型內容證據出現；重新讀原始 bytes、精確綁 GIT Blob 和實際 CI 後引用，避免反覆新寫相同筆記。
2. 核實原始 B/C 作者 Session／execution ID 與 E Session 是實際平台簽發、不同可驗身份，且內容未在同 Session 自審。現有「UNVERIFIED」不能倒填。
3. 取得精確 SHA 綁定的 reviewer notes、official evidence、author content、Issue36 實際 RETURN comment ID，產生符合 `scripts/sudu_independent_review_gate.py` V1 結構的可核查憑證候選；由 MASTER 自行檢查後決定是否登錄 protected main。E 自己不可改 trust registry。
4. G6 另需真正隔離、首次只看去答案題幹與圖片的原始模型 response，原始 prompt/response bytes、provider response ID／UTC／SHA，不得把已接觸正解的對話冒充盲解。未具備就 G6_UNVERIFIED，另派 G6，不在 E 對話直接模擬。
5. 回交每題 STATUS：CONTENT_ONLY_PASS／FORMAL_V1_HOLD 或實際可證的 FORMAL_REVIEW_READY，缺少獨立身分或 G6 即明確 HOLD。

交付：CLAIM／RETURN、QID、sourceCommit、QREV、WebP SHA、teachingDigest、official G3 SHA、原始 E notes SHA/GitBlob、真實作者/E principal、G6/G7 判定、PR/CI、nextOwner。不得寫 READY/LIVE。

## PROMPT 3｜交 G6 獨立操作員及 ROLE A：來源包交接，不可假首次盲解（P0）

請由 MASTER 決定首題 QID／sourceCommit／G2 SHA／WebP SHA，先讀 ROLE A 的獨占乾淨輸入包 CLAIM [#6888818246](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6888818246) 和操作員準備 RETURN [#6888802647](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6888802647)；不要另一角色競爭重寫 A 官方包。

ROLE A 只提供原始官方題幹、A-D、必要原圖／共用材料，輸入包不含官答、G3、教材、Issue、前次解題及 reviewer notes，保留 exact sourceCommit/G2/WebP 原 SHA 與「去答案包」原始 bytes SHA。

G6 操作員只能在**確定全新無記憶、無既有解題內容的獨立解題環境**，取得真實第一次模型請求＋第一次完整回應 bytes；固定首答、A-D 判斷、信心／歧義，不允許事後重寫或從既有答案猜造。保存 provider 原始回應 ID、模型、UTC、prompt/response SHA，交 G7 獨立驗證。若無可用合法 API 配額／分離環境，立刻 HOLD 並報實際原因；不要自行付款、ARM 或發起未授權推理。

交付：原始來源定位、去答案包與 SHA、凍結版本、真正首次 response bytes/provenance 或 UNVERIFIED、操作流程、G7 nextOwner；不得改 E trust／學生資料或 READY。

## PROMPT 4｜交 ROLE D／Work：下一次正式 Chromium 16 次執行契約（取得前置後才做）

你是 ROLE D，先讀 [Draft PR205](https://github.com/homelux-huang/7581707/pull/205) （HEAD `11f58d67c4a4a74df45fc787cec6abb2b0277290`，Actions43673921029兩 jobs SUCCESS），以及 [Draft PR167](https://github.com/homelux-huang/7581707/pull/167) current HEAD，確保 D runner 合併與新版 main 兼容。此 PR 只擴增**未來正式 G8**的 SHA／raw HTTP byte 檢查，既有 Actions 的 E12 16張僅是 unpublished HOLD 截圖，絕非正式 G8。

取得 MASTER 交付並通過真實 G1–G7／E V1／G6/G7、authenticated native **正式** publisher-staging 後，對 `114-00-E-11`、`115-00-MB-21`、`115-00-MB-22` 各別執行：
- clone/checkout MASTER 指定 exact source+code SHA，安裝 Node22／Playwright Chromium、Noto CJK 與 Python；用 `python scripts/build.py` 建置既有 Pages，不重建網站。
- 使用與 MASTER native staging 完全相同 raw `sudu/data/approved/{year}.json` bytes／WebP，在本機 isolated HTTP 伺服器提供，不用 page.route、mock JSON、不改 approved 手工資料。
- `python -m http.server 8765 --bind 127.0.0.1 --directory _site`。以真正存在的 `SUDU_D_QID`、`SUDU_D_EXPECT_SHA`、`SUDU_D_PROTECTED_MAIN_SHA`、`SUDU_D_SOURCE_COMMIT`、`SUDU_D_EMITTED_SHA256`、`SUDU_D_FORMAL_EVIDENCE_PATH`、`SUDU_D_FORMAL_EVIDENCE_SHA256` 設定環境，執行 `SUDU_D_MODE=formal node tests/sudu_role_d_emitted_only_8x2_20261106.cjs`。若任一輸入不存在，必須 fail closed，不可以臨時填 PASS。
- 瀏覽器 360×800、375×812、390×844、412×915、430×932、768×1024、1024×768、1440×900，各 Light/Dark，共16次。驗 QID/原始 WebP SHA、表格共用材料、A-D 題幹/雙層解析、粗體與 highlight、正誤回饋、數學算式/代入/單位/反算、英文非計算卡隱藏、行動裝置觸控、overflow、圖片、JS/HTTP錯誤、35 Demo+既有五題不回歸。
- 保存 16 張真實截圖 SHA256、完整 matrix、run/job/artifact、sourceCommit/QREV/WebP/G5 digest、HTML/runtime/publisher GitBlob、native raw output SHA、誤差與修復前後比較；SHA 變更即舊 G8 全面失效。
- MASTER 未核准真正式 staging 前，僅執行 PRECHECK/HOLD 的真實 Actions，不得把 PR202/210 private TECHNICAL_PRECHECK 當 FORMAL_UI_PASS，也不得先 promotion。

RETURN：QID／checkout SHA／sourceRevision／WebP SHA／teachingDigest／publisher/runtime/HTML Blob／staging raw SHA／16case matrix／16 screenshot hashes／CI run/job/artifacts／errors／正式G8或HOLD／nextOwner。正式 PASS 只交 MASTER，由 MASTER promotion/verify_live，ROLE D 不直接改 approved/main/Pages。

## 派工順序與不重複原則

- **立即交 MASTER：PROMPT 1**，真正需其 owns 的是「兩階段正式發佈契約」；PR210 私有預檢已有人處理，請勿重複分支。
- **並行交 E：PROMPT 2**，已有 E#206/#208 的內容證據，缺的是可信真身分與正式 trust。
- **MASTER 指定首 QID 後交 A／G6：PROMPT 3**；A 正在製作乾淨來源包，G6 目前仍準備中。
- **正式 staging 到位才交 D/Work：PROMPT 4**；目前只許驗真實 HOLD，不可以把 E12 的16張負測當正式通過。

**本文件及所有 PROMPT 是協調資料，不具備安全憑證、學生 READY 或正式 LIVE 效力。**
