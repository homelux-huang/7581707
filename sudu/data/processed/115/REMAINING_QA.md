## 2026-10-24 | Math B05 original text and SQLite source repaired; NOT RELEASE READY

- `115-00-MB-05` image SHA: `be5bb1f0e23eddff9e8a0f17e6e116ce2ce4219205f4527d50a710fb76e20dd2`. True pre-key solution was saved in commit `cf6a4efede233b0e447d52498209adf1b721c13e`, then compared with the official recorded answer B. No human audit or fresh PDF reading claimed.
- Original OCR fractions were broken. New text/choices correctly read as A (3/2,-5/2), B (3/2,-7/2), C (5/2,-5/2), D (5/2,-7/2). Earlier raw text, image, answers, historical evidence and all 205 IDs preserved.
- Source correction run [#40082891762](https://github.com/homelux-huang/7581707/actions/runs/40082891762) SUCCESS; corrected JSON, full SQLite roundtrip for 205 rows, checked idempotence. Exact applied QA branch commit `30122c3ca2dba956ff62c0de24d090664689c7dc`. Source review diff: `review-evidence/115-00-MB-05-source-text-applied-20261024.json`.
- An earlier run #40082858255 failed in only the added CI assertion due to unexpected SQLite column `payload_json` instead of `payload`. CI check was corrected to interrogate table schema, preserving all assertions. Do not count the earlier run as success.
- Remaining **concrete** requirements: final correct text_revision binding, five schema-compatible OCR/official/pre-key blind/teaching/UI evidence docs and hashes, real final-export source content V4 browser test on 8 sizes x 2 themes, valid addition to verified-student-batch, publisher stage/check, same-SHA Pages and LIVE. The MathB19–25 placeholder fixture is not usable as a release UI certificate. Do not set studentReleaseApproved/READY before actual proof.
- Formal published baseline: 115 Math B 02,03,04,09; 114 none. Q05 is **NOT DEPLOYED**.

---
# 115 年題庫尚待 QA｜105–115 QA 分支工作清單

> 2026-10-23 基於指定 QA 分支 JSON 的可追溯快照；本清單**不是**新的人工圖片目視驗收、答案查核或放行結果。不修改任何既有 QA 狀態。當來源 JSON 更新時，應重新比對清單與來源，而非把舊快照視為即時狀態。

## 當次可核實的計數

- G1：單題 WebP 目視 PASS 紀錄 **143/205**；待直接目視 QA **62**。僅計入 manifest `qaStatus=PASS` 且 `visualReviewEvidence.reviewedSha256` 與輸出 SHA 相同者；已登錄 PASS 仍須依證據稽核。
- 共用材料：已登錄 PASS **5/20**；待獨立目視驗收 **15**。
- G2：依 inventory 各科 `questionVerified` 總計 **0/205**；全部 OCR／選項、圖表及來源原卷仍須核實，不得把 OCR raw 當 PASS。
- G3：最終官方答案已登錄 `answerVerified=true` **81/205**，尚待 **124**；未核實題目要對官方最終標準答案及疑義／更正公告逐題留證。
- G5：本年隔離 SQLite 已登錄 205 題、SHA mismatches []；但 `inventory.sqlite.reimportCount` 目前未登錄，不得宣稱已完成雙次匯入之 G5 驗收。
- G6：`integrationReady=false`、`releaseAllowed=false`。不得合併 main 或正式部署。

## 優先處理與已知風險

- 115 國文 C16、C17 已有獨立修正版 QA 證據與 PASS 紀錄，不再重作 SHA 相同資產。C18 起仍需逐題對照原卷。
- 處理跨頁題時需核查上一題殘片、共用圖表及原頁裁切座標；`sourcePage`、`crop`、原卷 SHA、WebP SHA、reviewer、reviewedAt 與比對結果必須可回讀。
- 商科 09-1 多題仍缺 G1；英文題組共用文章與其他共享圖表不可因單題 PASS 推定通過。
- 所有候選答案只可標記 `answerMatched`，不能以此代替最終公告和 `answerVerified`。
- 圖片與文字驗收應分開；`questionVerified` 不能從已解碼 WebP 推算。

## G1：62 題 WebP 仍待逐題原卷目視比對

### 00-C（國文，21 筆）

- [ ] `115-00-C-18`
- [ ] `115-00-C-19`
- [ ] `115-00-C-20`
- [ ] `115-00-C-21`
- [ ] `115-00-C-22`
- [ ] `115-00-C-23`
- [ ] `115-00-C-24`
- [ ] `115-00-C-25`
- [ ] `115-00-C-26`
- [ ] `115-00-C-27`
- [ ] `115-00-C-28`
- [ ] `115-00-C-29`
- [ ] `115-00-C-30`
- [ ] `115-00-C-31`
- [ ] `115-00-C-32`
- [ ] `115-00-C-33`
- [ ] `115-00-C-34`
- [ ] `115-00-C-35`
- [ ] `115-00-C-36`
- [ ] `115-00-C-37`
- [ ] `115-00-C-38`

### 09-1（商管專業（一），38 筆）

- [ ] `115-09-1-02`
- [ ] `115-09-1-04`
- [ ] `115-09-1-08`
- [ ] `115-09-1-09`
- [ ] `115-09-1-10`
- [ ] `115-09-1-11`
- [ ] `115-09-1-12`
- [ ] `115-09-1-13`
- [ ] `115-09-1-14`
- [ ] `115-09-1-15`
- [ ] `115-09-1-16`
- [ ] `115-09-1-17`
- [ ] `115-09-1-18`
- [ ] `115-09-1-19`
- [ ] `115-09-1-20`
- [ ] `115-09-1-21`
- [ ] `115-09-1-22`
- [ ] `115-09-1-23`
- [ ] `115-09-1-24`
- [ ] `115-09-1-25`
- [ ] `115-09-1-30`
- [ ] `115-09-1-31`
- [ ] `115-09-1-35`
- [ ] `115-09-1-36`
- [ ] `115-09-1-37`
- [ ] `115-09-1-38`
- [ ] `115-09-1-39`
- [ ] `115-09-1-40`
- [ ] `115-09-1-41`
- [ ] `115-09-1-42`
- [ ] `115-09-1-43`
- [ ] `115-09-1-44`
- [ ] `115-09-1-45`
- [ ] `115-09-1-46`
- [ ] `115-09-1-47`
- [ ] `115-09-1-48`
- [ ] `115-09-1-49`
- [ ] `115-09-1-50`

### 09-2（商管專業（二），3 筆）

- [ ] `115-09-2-22`
- [ ] `115-09-2-49`
- [ ] `115-09-2-50`

## 共用閱讀材料：15 份仍待獨立 G1
- [ ] `115-00-E-SHARED-29-30`：題號 29、30；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-E-SHARED-31-32`：題號 31、32；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-E-SHARED-33-35`：題號 33、34、35；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-E-SHARED-36-38`：題號 36、37、38；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-E-SHARED-39-42`：題號 39、40、41、42；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-09-1-SHARED-18-19`：題號 18、19；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-09-1-SHARED-20-21`：題號 20、21；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-09-1-SHARED-22-23`：題號 22、23；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-09-2-SHARED-23-24`：題號 23、24；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-09-2-SHARED-49-50`：題號 49、50；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-C-SHARED-19-22`：題號 19、20、21、22；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-C-SHARED-23-26`：題號 23、24、25、26；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-C-SHARED-27-30`：題號 27、28、29、30；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-C-SHARED-31-34`：題號 31、32、33、34；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`
- [ ] `115-00-C-SHARED-35-38`：題號 35、36、37、38；現況 `DRAFT_NEEDS_INDIVIDUAL_VISUAL_QA`

## G3：124 題仍待最終官方答案、疑義／更正公告核對

### 00-C（國文，32 筆）

- [ ] `115-00-C-01`
- [ ] `115-00-C-02`
- [ ] `115-00-C-03`
- [ ] `115-00-C-04`
- [ ] `115-00-C-05`
- [ ] `115-00-C-07`
- [ ] `115-00-C-08`
- [ ] `115-00-C-09`
- [ ] `115-00-C-10`
- [ ] `115-00-C-16`
- [ ] `115-00-C-17`
- [ ] `115-00-C-18`
- [ ] `115-00-C-19`
- [ ] `115-00-C-20`
- [ ] `115-00-C-21`
- [ ] `115-00-C-22`
- [ ] `115-00-C-23`
- [ ] `115-00-C-24`
- [ ] `115-00-C-25`
- [ ] `115-00-C-26`
- [ ] `115-00-C-27`
- [ ] `115-00-C-28`
- [ ] `115-00-C-29`
- [ ] `115-00-C-30`
- [ ] `115-00-C-31`
- [ ] `115-00-C-32`
- [ ] `115-00-C-33`
- [ ] `115-00-C-34`
- [ ] `115-00-C-35`
- [ ] `115-00-C-36`
- [ ] `115-00-C-37`
- [ ] `115-00-C-38`

### 00-E（英文，42 筆）

- [ ] `115-00-E-01`
- [ ] `115-00-E-02`
- [ ] `115-00-E-03`
- [ ] `115-00-E-04`
- [ ] `115-00-E-05`
- [ ] `115-00-E-06`
- [ ] `115-00-E-07`
- [ ] `115-00-E-08`
- [ ] `115-00-E-09`
- [ ] `115-00-E-10`
- [ ] `115-00-E-11`
- [ ] `115-00-E-12`
- [ ] `115-00-E-13`
- [ ] `115-00-E-14`
- [ ] `115-00-E-15`
- [ ] `115-00-E-16`
- [ ] `115-00-E-17`
- [ ] `115-00-E-18`
- [ ] `115-00-E-19`
- [ ] `115-00-E-20`
- [ ] `115-00-E-21`
- [ ] `115-00-E-22`
- [ ] `115-00-E-23`
- [ ] `115-00-E-24`
- [ ] `115-00-E-25`
- [ ] `115-00-E-26`
- [ ] `115-00-E-27`
- [ ] `115-00-E-28`
- [ ] `115-00-E-29`
- [ ] `115-00-E-30`
- [ ] `115-00-E-31`
- [ ] `115-00-E-32`
- [ ] `115-00-E-33`
- [ ] `115-00-E-34`
- [ ] `115-00-E-35`
- [ ] `115-00-E-36`
- [ ] `115-00-E-37`
- [ ] `115-00-E-38`
- [ ] `115-00-E-39`
- [ ] `115-00-E-40`
- [ ] `115-00-E-41`
- [ ] `115-00-E-42`

### 09-2（商管專業（二），50 筆）

- [ ] `115-09-2-01`
- [ ] `115-09-2-02`
- [ ] `115-09-2-03`
- [ ] `115-09-2-04`
- [ ] `115-09-2-05`
- [ ] `115-09-2-06`
- [ ] `115-09-2-07`
- [ ] `115-09-2-08`
- [ ] `115-09-2-09`
- [ ] `115-09-2-10`
- [ ] `115-09-2-11`
- [ ] `115-09-2-12`
- [ ] `115-09-2-13`
- [ ] `115-09-2-14`
- [ ] `115-09-2-15`
- [ ] `115-09-2-16`
- [ ] `115-09-2-17`
- [ ] `115-09-2-18`
- [ ] `115-09-2-19`
- [ ] `115-09-2-20`
- [ ] `115-09-2-21`
- [ ] `115-09-2-22`
- [ ] `115-09-2-23`
- [ ] `115-09-2-24`
- [ ] `115-09-2-25`
- [ ] `115-09-2-26`
- [ ] `115-09-2-27`
- [ ] `115-09-2-28`
- [ ] `115-09-2-29`
- [ ] `115-09-2-30`
- [ ] `115-09-2-31`
- [ ] `115-09-2-32`
- [ ] `115-09-2-33`
- [ ] `115-09-2-34`
- [ ] `115-09-2-35`
- [ ] `115-09-2-36`
- [ ] `115-09-2-37`
- [ ] `115-09-2-38`
- [ ] `115-09-2-39`
- [ ] `115-09-2-40`
- [ ] `115-09-2-41`
- [ ] `115-09-2-42`
- [ ] `115-09-2-43`
- [ ] `115-09-2-44`
- [ ] `115-09-2-45`
- [ ] `115-09-2-46`
- [ ] `115-09-2-47`
- [ ] `115-09-2-48`
- [ ] `115-09-2-49`
- [ ] `115-09-2-50`

## 快照來源（Git blob SHA；供比對、非 PDF 內容證明）

- `sudu/data/processed/115/webp-manifest.json`：Git blob `2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b`
- `sudu/data/processed/115/official-answer-evidence.json`：Git blob `ed02ef9cde66720af2142330d79afb5349d0f999`
- `sudu/data/processed/115/inventory.json`：Git blob `0b38841e9d223715750b8b4bbf9be03d4682c391`
- `sudu/data/processed/115/VISUAL_QA.json`：Git blob `7c072fc04bb75f781df462d8c5bc0fd058b4ebc8`
- `sudu/data/processed/115/release-manifest.json`：Git blob `111305afb21cc944f888de4c0fa6cb84cfe94fce`

官方題卷與最終答案來源以 TCTE 原站及對應來源 PDF SHA 為準。任何未通過 G0–G6 的題目均不得設為 `integrationReady=true`。
