# 115 數學 B20～25｜來源圖真實校字與 DB 準備工作分支

日期：2026-10-24。獨立分支 `qa/mb20-25-source-text-candidate-20261024`，來源為正式 QA `b78a14c8cc6081a7a01613238255fce0a22ba60b`。不可提前合併到正式 QA，避免影響正在執行的 MB05 同 SHA Pages 發布。

六題來源圖 SHA 和逐張目視已在 CI #40084307251 PASS，具體校正文字及原候選差異：`sudu/data/processed/115/review-evidence/115-00-MB-{20..25}-image-transcription-correction-20261024.json`。

此分支新增腳本 `scripts/apply_115_math_b20_25_text_candidates.py`：只在 CI 暫存 checkout 嘗試替換已由原圖核對的 canonical 問題/四選項，以 SQLite 205筆完全一致與其他199題不變為條件。原始試卷 WebP、`years/115.json`、原始 OCR、官方答案及所有學生發布旗標均不更動。

即使所有文字與 SQLite 測試通過，六題仍維持 `questionVerified=false`、正式獨立文字 admission 待核、首次獨立解題證據待核、`studentReleaseApproved=false`。後續若要進正式 QA，需另獨立逐題核驗並取得合法完整逐題 teaching+UI+source certificate，不能因改掉 OCR 污染就提前放行。

原有 student-certified 02/03/04/05/09 共5題需維持不變，正式發布器不得顯示6題新增。
