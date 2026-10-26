# 114 年執行角色 B｜Batch 01（2026-10-25）— Draft / NO RELEASE

- 基底來源：PR #21 HEAD `9944759e339ef2d3c002042798f7fe696d861d96`，獨立教學分支 `teaching/114-role-b-sourcebound-batch01-20261025`；未更改原始 OCR、裁圖、manifest、SQLite、main、發布器及 UI。
- 每題 `source.questionRevision` 完全沿用既有 `scripts/sudu_verified_publish.py::text_revision`：SHA-256（JSON 的 question、options、singleQuestionWebpSha256；UTF-8、sort_keys、無空白）。
- 每題 `source.webpSha256` 等於 manifest PASS 原素材；`composedTeachingSha256` 是 `{questionId,sourceRevision,webpSha256,teaching,enrichment}` 的 SHA-256 canonical JSON。源文本或單題 WebP 一改就必須重算並重審。
- 英文 07～09：只存 addendum（原教學指向 PR21 的原 JSON 路徑及 Git blob SHA），**不重新產生或改寫**已完成的 teacherSummary、elementarySummary、A～D 評析、歷史 pre-key 解題證據。
- 英文 06：原圖 QA PASS 且四選項完整，新增教師／國小雙層 A～D 教學候選。**沒有**此題個別官方最終答案 PDF 影像 QA，不標 READY。
- 國文 01～03：原圖 QA PASS 且四選項完整，新增「錯別字」、「把字句」、「類字多義」教學候選。官方最終答案影像核對與獨立審查仍待來源角色、審查角色完成。
- 英文詞彙保留初級／中級／高級中文標籤、IPA、同義詞／相反意思、語境限制、原題詞形精準 highlight；2024–2025 新聞來源已由作者開啟查核，英中例句皆**自編**、不冒充新聞原句。來源：Cambridge、中央社、FTV、TVBS；全部 URL 保存於逐題 JSON。
- 國文詞語保留初級／中級／高級級別；錯字訂正詞只在解說顯示，不偽稱錯誤原題也出現正確字。
- 本批所有題目：**作者 AI 自評**，原官方答案已知，沒有冒稱本批盲解，也沒有虛構教師審核或教材章節。新 READY=0、新 LIVE=0；嚴禁將 E07～09 舊 UI 證書套用到新增 enrichments。
- 暫停英文 10：現有 OCR 第 D 選項混入後頁頁首與對話題說明；等待來源角色更正並重核 revision。114 數學 B 存在選項不全的候選，不能杜撰文字解題。
- 主指揮要求的 `docs/114-115-DELIVERY-COMMAND.md` 和共同題號台帳在本批開工檢視之 main 與 coord 分支未找到；待主指揮文件落地後應校驗指令差異與題號權屬。
- 後續由角色 E / 真正受授權的獨立教師與 GitHub 簽署進行審查；必要時角色 D 對確切新增教學 digest 執行 V4 8 尺寸 × 2 主題 QA；唯獨主指揮可決定進入正式合併發布。

驗證：`python -m unittest tests/test_114_role_b_teaching_20261025.py -v`。通過只代表資料結構與 SHA 自動檢查，不代表人工簽章或發布許可。
