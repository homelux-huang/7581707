# 2026-10-23｜修正3題官方答案選項標籤與新增雙重 SHA 檢查（僅草稿）
起始HEAD：`23729f99db52a55bc3863f459ac1c6167fc7bcd7`。

## 原本的實際資料矛盾
- 3道教學 BLOCKED：`115-09-1-07`官方B、`115-09-1-33`官方A、`115-09-2-28`官方A。各題原 `teaching.optionExplanations.A/B/C/D.isCorrect` **全部為false**，與已驗證官方標準答案不一致。保留教學BLOCKED有必要，但不能把官方選項也誤標為錯誤。
- 本批僅把3題官方選項`isCorrect`調為true，並補該選項的雙層解說，清楚區分官方解答／專業術語歧義／尚未獨立教學QA。
- 先前被覆蓋的`isCorrect,teacher,elementary,reason`完整保存在 `qa.optionCorrectnessAlignment20261023.before`，保留原AI盲解歷史、不改其他選項、`aiAnswer`、答案比對、`status`或部署旗標。
- 商概07固定特別股股利與財務槓桿理論、數科33雜湊與加解密、經濟28無預算的TU比較等概念仍維持 `BLOCKED_TEACHING_REVIEW`；不因UI標籤符合官方就假裝內容已通過QA。

## 自動驗收加強
- `scripts/audit_preview_teaching_drafts.py` 新增從`progress.json.items`重新驗固定128題題號／圖片路徑／SHA。
- 除了每題主 WebP 的真正位元組SHA256，也**實際對兩份共有文章的 WebP 位元組計算 SHA256**（不是只檢查曾經驗收的布林值）。同路徑共用影像只hash一次。
- 每題四選項嚴格需 **恰好一個 isCorrect=true 且等於官方最終選項**；若未對齊就讓CI FAIL，不掩飾新問題。
- 檢查 `qa.officialFinalEvidence.officialAnswer` 與PDF證據索引相同；原本發布隔離及A-D雙層說明等查核不變。
- 此為可重現的**自動資料完整性驗收**，不是教學內容／教材出處／真實頁面排版的核可。本批教學完整QA0/128，正式核准0/128，部署0。

## 說明
每次 push 到草稿分支後由唯讀 `preview-128-draft-qa.yml` 自動重跑稽核與 Chromium smoke；測試結果以實際GitHub Actions為準，未取得PASS不能擅稱。
