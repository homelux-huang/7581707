# 2026-10-23｜局部教學 QA 必須逐題有證據的 CI 門檻

基準 HEAD：`8cd3abae97b139028e9b5483e17cf0ddb0f5a333`。已將唯讀驗收腳本 `scripts/audit_preview_128_release_readiness.py` 更新以下檢查：

1. `progress.partialEnglishLexicalReviewLedger.questionIds` 需與每一題 JSON 的 `qa.lexicalAndFourOptionReview20261023` 完全一致、不可重複，且 `reviewedQuestionCount` 要與實際項目相符。
2. 每筆英文局部QA必須屬英文科、狀態僅為 `PARTIAL_...`、有官方答案及獨立複核文字，不能暗示發布批准。
3. `progress.partialTeachingReviewLedger.reviewedQuestionIds` 與各題 `qa.sourceLinkedCalculationRecheck20261023` 逐一相等、不可重複；已審5題必須屬會計、包含實際列式清單、官方答案與獨立稽核文件。
4. 仍沿用實體原圖＋共用文章SHA256、四選項結構、官方答案、新聞來源類型與學生發布隔離的所有原檢查。
5. 報表分開輸出局部英文及局部會計數目，但 **不得**因這些計數增加 `fullyAccepted` 或 `deployed`。教學獨立全項QA目前0/128，非本批CI能自動准予通過。

當前預期 English partial = 28/28、Accounting numeric partial = 5/128、news source = 22/28、image = 128/128、official = 128/128、fully accepted = 0/128、deployed = 0/128。實際 CI 結果請以該 HEAD 的 GitHub Actions 為準。
