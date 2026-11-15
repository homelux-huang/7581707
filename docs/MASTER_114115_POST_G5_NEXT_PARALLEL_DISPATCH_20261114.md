# 【7581707｜MASTER｜114/115 下一輪實際上線關鍵路徑與 A/C/E/D 派工｜2026-11-14】

> 使用方法：把以下各 ROLE 的 **完整區塊**直接貼到對應 ChatGPT/Codex Session。指令以本次 GitHub 回讀時間為準；各 ROLE 執行前須重新讀取 Issue #36／PR／租約。**建立本文不代表其他 Session 已自行啟動。** 逐題合格即單題發布，不等 410 題。禁止假造首次盲解、獨立 E 身分、E trust、D formal 16/16、READY／LIVE。

## 0. MASTER 精確基準、當前真進度

- Repository: https://github.com/homelux-huang/7581707
- 唯一 Issue 控制台: https://github.com/homelux-huang/7581707/issues/36
- 正式學生網站: https://homelux-huang.github.io/7581707/sudu/v4-115-multisubject-review-demo.html
- Protected main: `0bc2b05ada43ef02983d56fc45ec3448189a318b`，正式 Pages #43571965628 同 SHA SUCCESS。
- 官方來源 QA：`qa/114-115-official-visual-review` HEAD `f9922959acde5a838f0a9ecbe97aba81e928780e`，由 PR #195 正式合併 115 MB21/22 真正作者 G5。原來源、教學、SQLite 並未改變。
- 115 正式學生 LIVE 目前僅 5 題（MB02/03/04/05/09）；114 仍為 0 題；**本輪新 READY=0、LIVE=0**。410 題只是候選庫，絕非全部來源／學生驗收完成。
- main policy `DISTINCT_AI_CONTENT_RECEIPT_V1`、`requireHumanTeacher=false`、trustedAiReviewReceipts **仍空**；不能用真人教師資格或簽章阻塞，也不能略過不同作者 AI E 複核。
- 原 G5：114 E11 已合併 QA PR #189，115 MB21/22 已合併 QA PR #195，原 C PR118/143 沒被重寫。PR195 六個新增檔案在 QA 新 SHA 的六個 CI 均 SUCCESS，真值屬**作者 G5，不是 E TRUST，不是學生發布**。
- **並行者請勿衝突**：另一 Work MASTER 正在處理 [PR #196](https://github.com/homelux-huang/7581707/pull/196) 的 **MB21/22 兩份原 G5 測試模組整合修正**（Issue #36 #6877710036），不得碰那兩個測試檔／代他合併。另有 Work MASTER／ROLE A [MB24 共用 115 JSON／SQLite 租約 #6873884674](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6873884674)，**直到本人 RETURN+RELEASE，不得另開 MB24/25 共用資料庫寫入任務**。
- B 114 E07/08/09 作者已 [RETURN #6876469175](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6876469175)，教材原 SHA 凍結，但官方 QA 的三題 `questionVerified=false`、`answerVerified=false`，舊 PR35 UIQA 過期，不可拿它們 READY。

---

## ROLE C｜下一批 MB23／MB20 native G5 原作者發行憑證（可直接複製）

**taskId：`C-115-MB23-MB20-NATIVE-G5-ISSUER-20261114-03`，角色 C。**

1. 立即讀 Issue #36 最新租約、現行 QA HEAD、C 既有原作者 PR #118／#143 及 ROLE C 完成的 MB21/22 [PR #195](https://github.com/homelux-huang/7581707/pull/195)。**只需沿用 MB21/22 issuer 結構，不要再次修改它們；不得動另一 MASTER PR #196 的原測試模組。**
2. 現在開始兩個**互不重寫原教學**的原作者 issuer：先 `115-00-MB-23`、再 `115-00-MB-20`，先獨立 CLAIM 限定**新**檔案路徑、分支、baseSHA、QID，建自己的 QA-based Draft PR。
3. MB23 已合 QA 原始完整 2 資料列 × 3 欄價目表。正確 **with-table QREV** `9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4`，絕不能用舊 `sourceTextRevisionWithoutTable=4dc7a376...`。原 WebP SHA `2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51`；原 C GitBlob `eae542565062adf997ab8c8d37d2c3cd4dd71ca1`，教學 canonical SHA `13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6`，官方 B；原公式 `2x−3000=1.8(x+2000)`、x=33000、兩組 63000 元。
4. MB20 已合 QA **v5 完整原圖**，QREV `2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c`，原 WebP SHA `f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf`，原 C GitBlob `c226ee59e24d2136c5882ede894f9f0bb93d16d0`，教學 canonical SHA `2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d`，官方 A；原圖 B 點、圖（四）下緣必完整，原正弦定理驗算不重寫。
5. 完全比照原生 G5：嚴格綁定 sourceRevision、WebP SHA、原 C GitBlob、G2/G3 原始 SHA、真正 author RETURN，`content` 必須是舊教材教學子樹**位元內容等值**；unknown author Session ID 留 null，`independentAiContentReviewed=false`、`studentReleaseApproved=false`。
6. 新原作者 JSON、正/負向實測、isolated workflow `contents:read` 和交接 MD 在**你自己的新路徑**；保護完整 205 SQLite/manifest、不碰 approved/main/E/D/trust。
7. 每完成一題就提供 **實際 final-head Actions/run/job**、原始 SHA、GitBlob、QID、負測 PASS、PR 和 BLOCKERS，在 Issue #36 逐題 RETURN；MASTER 再唯讀審核 QA-only 整合。不得自行稱 READY 或 LIVE。

---

## ROLE A｜114 英文 E07 官方來源 G1/G2/G3（與 MB24 的 115 銀行隔離；可直接複製）

**taskId：`A-114-E07-SOURCE-NATIVE-ADMISSION-20261114-04`，角色 A。**

1. 立即讀 Issue #36 最新租約、官方 114 年 205 source QA HEAD、PR #31 原 B 教學與 [B E07 RETURN #6876440075](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6876440075)。先**確認沒有其他 114 questions.json/SQLite 寫入租約**，才可逐題 CLAIM。
2. 115 MB24 有另一 Work MASTER 的**獨占 115** 共用來源租約，不可改動 115 或 MB25；本輪只接手 **114-00-E-07** 的 114 年 bank／7 欄 SQLite，避免 115 工作受阻就全員停工。
3. E07 既有 WebP SHA `0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc`，來源 QREV 候選 `8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c`，目前 QA `questionVerified=false`／`answerVerified=false`。印刷答案 **候選 A**，先從官方原題頁、官方完整最終答案與公告核對，**不得把候選答案直接當最終官答**。
4. 原 B PR31 E07 作者教材教學 canonical SHA `d40bb97b85de499b63a3eeea1aa4c808f295f8e4ae6515cf597fdf9d40152eaf`，請保護作者 bytes；A 不修改 B 教學。原圖已合格時不要重切 WebP 或改 manifest SHA。
5. 僅真實來源缺口的最小更正，新增 G2/G3 原始 issuer 與正/負向測試；114 SQLite **歷史 schema 7 欄**、完整 205 payload+SHA、其他 204 題不變，來源 notices 必須符合 **114 年**特殊官方公告語意，不硬套 115 年。
6. 完成一題立即 RETURN：QID、修正版 sourceRevision、原始 WebP SHA、官答原始證據/更正公告、205 SQL parity、CI/run/job、PR HEAD、下一題。**E07 真實 RELEASE 後**才安排 E08、E09 依序逐題相同程序。只可來源 QA，不可替 E/D/MASTER 正式發布。

---

## ROLE E｜真獨立內容驗收 / G6 / protected V1（可直接複製）

原 taskId `E-114E11-115MB21-22-FORMAL-REVIEW-GAP-20261114-01`，角色 E；本工作早已由使用者指派，但 GitHub 尚無本輪真實 E 完工 RETURN。先查是否已有真正 CLAIM/RETURN，若有接續而非重做。

優先 114 E11（B PR189 G5 已 QA）、115 MB21/22（C PR195 G5 已 QA）、再 MB23/20。逐題重新核原始 G2/G3、官方最後答案、更正公告、WebP/作者教學 SHA、四選項的獨立內容判斷、真正公式/答案反驗及各自 SHA 來源；避免照抄 B/C 自評。保留 E 原始 notes bytes/git blob、真實角色/執行 Session 的不同身份證據和 GitHub RETURN。

**G6 必須是真正原始 answer-hidden 首次模型解題的 prompt/response 原始 bytes、timestamps、模型/provider 回應 ID 與其執行者 provenance；已知答案的 E 或 MASTER Session 不可倒填、重寫或冒充 G6。** 若無法證明，`G6_UNVERIFIED/G7_UNVERIFIED`，先交完可真做的獨立內容審查而不虛構通過。原始 B/C author Session ID null 不能用同一 GitHub actor 自動補成不同 Session。任何 E 本人不得私自改 protected trust registry，也不能叫 D 將未獲認證的 staged browser 算正式 UIQA。

---

## ROLE D｜先跑可行的 V4 預檢／正式 emitter 階段僅在 E/G6 合格後（可直接複製）

原 taskId `D-114E11-115MB21-22-EMITTED-V4-GATE-20261114-01`，角色 D。檢查 Issue #36 是否已有自己的最新 RETURN；不要重做合格的 35 題原 demo、不得改 A/B/C/E source/teaching/trust。

優先 E11 → MB21 → MB22。先以目前正式 V4 及原題、正式 G5 issuer digest 進行真 browser **PRECHECK**，核 DOM 計算卡（E11 不需計算）及 highlight、四選項、WebP、答題互動、Light/Dark／RWD。**只有在 MASTER 以真正受信任 E、原始 G6，依 native publisher 產生真正可答學生資料後**，才可主張正式 8 個 viewport × Light/Dark 共 16 次真 Chromium 與屏幕/CI/run、`testedTeachingDigest`、QREV；不能 mock E TRUST 或用 QA-only staged artifact 假冒正式 G8。

若 blocked by E/G6，交精準 PRECHECK、功能測試與缺口清單；安全的 UI code-only bug fix 可以用自己新分支/PR 真測試後 RETURN，不能手填 FORMAL_UI_PASS。

---

## MASTER｜真正逐題 LIVE 條件（不能提前偽造）

1. 原始 114/115 source、官答、WebP、JSON/SQLite、最終公告、原作者 G5、真 G6 answer-blind、真不同 Session E 逐題實質複核與 protected V1 exact receipt、D 真 publisher-emitted 8×2、全部 CI 都要通過。
2. **重要新的 native publisher 結構核實**：protected `scripts/sudu_verified_publish.py` 的 `apply_independently_certified_review()` 只有在 QA 的 `verified-student-batch.json` 有真 `STUDENT_QA_APPROVED` 逐題項目，且 OCR／official／blind／teaching／UI **五份 SHA-bound evidence** 全部存在、原圖／source revision／官答／教學與 protected V1 registry 都可信時，才會把原作者 G5 注入學生輸出。現有 115 verified batch 只有歷史 MB02/03/04/05/09；114 verified batch 目前不存在。**禁止在 E/G6/D 真實完成前新增假核准項目或把 G5 issuer 單獨當 LIVE。**
3. 當某一題真的全閘門 PASS，MASTER 才在獨立正常受保護 PR 建單題 verified-student-batch 憑證、受信任 E 保護登錄、完整 CI 與 Pages 同 SHA LIVE 確認；更新 PR30 唯一台帳。保留原有歷史五題。
4. 新 QID 尚缺證據，維持 HOLD，但轉下一個無衝突任務；**本輪新 READY/LIVE 仍 0**。確認並行 MB24 Work owner、PR196 另一 MASTER 工作者的結果，不能搶其檔案或硬合分支。

> 所有角色 RETURN 需精確 taskId、claim link、role、QID、base/head SHA、逐檔 diff、原 source revision／WebP SHA／教學 SHA、證據原 Blob/原 bytes、真 CI run/job、G6/E/D 真實判定、READY/main/LIVE、下一個 owner 與租約 RELEASE。其他 Session 並未由此文件直接啟動。
