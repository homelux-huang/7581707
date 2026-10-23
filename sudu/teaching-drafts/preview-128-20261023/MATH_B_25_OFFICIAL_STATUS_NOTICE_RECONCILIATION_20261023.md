# 7581707｜數學B 25題官方證據與現行說明同步（非重新驗證官方、非發布）

日期：2026-10-23；起始HEAD：`79b1baaa26a146c1b242b4f57d49a5571cfae7b0`。

## 問題

數學B草稿 `solution.officialFinalStatus=PENDING_DIRECT_OFFICIAL_PDF_AND_CORRECTIONS` 是**早期首次解題時的歷史快照**；但此後已有 `official-final-evidence-20261023.json` 逐題核對全部25題的最終標準答案與確認說明。部分 `answerComparison.notice`、`teaching.source.officialIssueExplanation` 仍使用『目前尚未回讀官方』字眼，易讓介面錯誤顯示已解決的官方來源阻塞。

## 本次修復

- 115數學B第01～25題的**目前狀態文案**均與已存證的官方答案一致，清楚區分『官方最終答案來源已核實』與『完整教學／教材版本與頁碼／V4 UI 驗收未完成』。
- 其中2、3、4、9題已於前次 `mathContentRecheck20261023` 先行同步並保存舊文字。其餘21題本輪以 `qa.officialFinalNoticeSync20261023` 保存原 `answerComparison.notice`、`teaching.source.officialIssueExplanation` 與先前歷史狀態，然後修正目前顯示文字。
- **刻意保留 `solution.officialFinalStatus` 原值**作為當年首次解題的歷史，避免竄改『當時尚未查官方』的解題來源紀錄；下游顯示目前官方狀態應讀 `qa.officialFinalEvidence` 或 `answerComparison.officialFinalCorrectionVerified`，不可拿歷史 first-pass 欄位冒充最新狀態。
- **未重新下載官方PDF**；引用的是現存有 URL、SHA256、公開更正公告的官方來源登錄。沒有改官方正解、數學式、原圖 WebP、OCR、題庫準確數或學生紀錄。
- 避免衝突使用 GitHub 最新HEAD安全前推提交，沒有覆蓋其他Session修改；最新正式main不動。

## 發布防線與測試

- `tests/test_preview_128_math_b_partial.py` 新增檢查全部25題當前說明與官方證據一致、保留舊告警、每題仍未放行，並由草稿只讀 CI 執行。
- 目前只是**局部計算/選項 QA 25/25**。完整教學QA 0/128，正式新增128題部署0/128；所有原題 `qa.independentTeachingReview=PENDING`、`qa.uiReview=PENDING`、`studentReleaseApproved=false`、`deploy=false`。
