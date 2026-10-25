# Role B｜114 年第三批5題教學草稿（NO RELEASE）

taskId `B-114-EN16-19-C05-20261025-04`，認領 [Issue #36 記錄](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393757201)，GitHub createdAt `2026-10-25T05:08:19Z`。舊 PR44 HEAD `e0d4532c751127204e73af9cd9d3a95c52449131` 為起點，新教學分支 `teaching/114-role-b-loop-batch03-20261025`；來源 PR21 `9944759e339ef2d3c002042798f7fe696d861d96`。既有12題教學、圖片、OCR、SQLite、V4、發布器、main均未修改。

本批新增 `114-00-C-05`、`114-00-E-16/17/18/19` 各題 JSON：教師角度與國小口語逐題解說、獨立A-D理由、步驟、重點與一眼記住，原題實際詞形安全 highlight。四題英文另有IPA、初/中級詞、同反義、語境限制、英文／中文近三年新聞語境自編句，直接核查2024亞洲奧會雙金、2025中央社優先席、2024 Hotels.com官方旅館遺失物、2025北美館官方展覽，各題記實際來源網址與報導支持範圍，不把自編例句寫成新聞引句。國文05 按①不僅→⑤更、④既→③也、③純真→②對比順序分析，正解候選B。所有題無計算，`examCalculation=null`，不使用占位字。

每題原四選項與 questionRevision、原 WebP SHA、教學 SHA 綁定；本批只沿用舊 manifest `qaStatus=PASS`，未在本輪做新的人工原圖 QA。官方最終答案影像、更正公告適用仍由來源角色 A/E 驗證。解題時官方答案候選已知，沒有虛稱盲解。

使用者最新政策明訂「高職老師」是**教學角度**，不需要真人教師、證照、Ed25519簽章或真人 GitHub APPROVED 事件；但不得用作者 B 自評取代不同作者 E 的 AI 實質審查及真實來源/UI/主指揮發布。所有5題 `BLOCKED`、`newReady=0`、`newLive=0`，獨立E review task/session/evidence 欄位皆無值。MASTER 新 AI 契約 PR46 尚未接上 publisher。PR30 是唯一台帳，不創新台帳。

檢查：`python -m unittest discover -s tests -p 'test_114_role_b_batch03_20261025.py' -v`；此驗證只證明 draft 結構與 SHA，不是正式發布審核。
