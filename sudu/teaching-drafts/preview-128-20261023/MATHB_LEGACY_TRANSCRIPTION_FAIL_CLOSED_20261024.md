# 2026-10-24｜數學B20–25原始文字污染：逐題發布閘門補強

基準 HEAD：`36b932b896ce8ab6a04cbc5232e3b4c4ebb3213d`。在草稿六題 `qa.legacyCandidateTextRisk20261023` 已保存詳細風險，當前 `formalTextQaPass=false`。補強唯讀 `scripts/audit_preview_128_teaching_candidates.py`：凡有此隔離紀錄、且未完成獨立逐字對照者，額外列出 `legacy_candidate_text_not_independently_approved` 阻塞；即使有人只附上形式完整的 certificate 也不能繞過。

- MB20：根號字形／附圖選項混題；MB21：角度符號與圖中文字；MB22：卡片圖與頁尾；MB23：價目表扁平化；MB24：複合對數分式跨行破壞；MB25：根號2誤變數字2，極高風險。
- 不新增任何已QA文字；不重OCR、不修改原始WebP、不修改正式main及studentReleaseApproved。
- 兩個 synthetic 回歸測試：有明確`formalTextQaPass=false`或缺此欄時，即使其他驗收證書齊全仍不具發布資格。
- 這只修復防止錯誤文字發布的技術門檻。影像128/128、官答128/128、完整獨立教學QA0/128、READY0/128、正式新增部署0/128。
- 要解除文字隔離，須從已驗WebP逐選項人工重建官方符號／公式／表格的**獨立逐字 QA 證據**；只改布林值為true或只通過一般CI不得視為有效人工核實。
