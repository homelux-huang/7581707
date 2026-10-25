## 2026-10-25 Role E IPA 獨立證據返修（三詞最小差分）

角色 E 對本稿之獨立實質審核 [Issue #36 留言 #6393906377](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393906377) 指出 114 E16/E17/E18 IPA 與 Cambridge 引文所列 UK/US 口音不一致。角色 B 依字典 [teamwork](https://dictionary.cambridge.org/pronunciation/english/teamwork)、[offer](https://dictionary.cambridge.org/pronunciation/english/offer)、[lost](https://dictionary.cambridge.org/pronunciation/english/lost) 所列美式發音修正：E16 teamwork `/ˈtiːm.wɝːk/`、E17 offered his seat `/ˈɑː.fɚd hɪz siːt/`、E18 lost `/lɑːst/`。E17 字典**僅直接列 offer 原形**，offered 過去式 + /d/、his seat 為明示教學推導，絕不誤稱 Cambridge 錄製整句。新增US accent與 IPA 引用範圍，保留 E19/C05 及其他單字。

這是詞彙 `enrichment` 最小差分：原題、原四選項、既有選項詳解、國小白話、sourceRevision、WebP SHA、teachingCanonicalSha256 均未動；三題 composedTeachingSha256、原JSON fileSHA、batch 更新。原版 D 8×2/教學 digest 證據**不可自動沿用**，修改後角色 E 不同作者仍須重核新 SHA，角色 A 官答公告、D 精確V4、MASTER publisher/Pages依序待驗。全批 BLOCKED、READY/LIVE=0，不需真人教師簽章。

# Role B｜114 年第三批5題教學草稿（NO RELEASE）

taskId `B-114-EN16-19-C05-20261025-04`，認領 [Issue #36 記錄](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393757201)，GitHub createdAt `2026-10-25T05:08:19Z`。舊 PR44 HEAD `e0d4532c751127204e73af9cd9d3a95c52449131` 為起點，新教學分支 `teaching/114-role-b-loop-batch03-20261025`；來源 PR21 `9944759e339ef2d3c002042798f7fe696d861d96`。既有12題教學、圖片、OCR、SQLite、V4、發布器、main均未修改。

本批新增 `114-00-C-05`、`114-00-E-16/17/18/19` 各題 JSON：教師角度與國小口語逐題解說、獨立A-D理由、步驟、重點與一眼記住，原題實際詞形安全 highlight。四題英文另有IPA、初/中級詞、同反義、語境限制、英文／中文近三年新聞語境自編句，直接核查2024亞洲奧會雙金、2025中央社優先席、2024 Hotels.com官方旅館遺失物、2025北美館官方展覽，各題記實際來源網址與報導支持範圍，不把自編例句寫成新聞引句。國文05 按①不僅→⑤更、④既→③也、③純真→②對比順序分析，正解候選B。所有題無計算，`examCalculation=null`，不使用占位字。

每題原四選項與 questionRevision、原 WebP SHA、教學 SHA 綁定；本批只沿用舊 manifest `qaStatus=PASS`，未在本輪做新的人工原圖 QA。官方最終答案影像、更正公告適用仍由來源角色 A/E 驗證。解題時官方答案候選已知，沒有虛稱盲解。

使用者最新政策明訂「高職老師」是**教學角度**，不需要真人教師、證照、Ed25519簽章或真人 GitHub APPROVED 事件；但不得用作者 B 自評取代不同作者 E 的 AI 實質審查及真實來源/UI/主指揮發布。所有5題 `BLOCKED`、`newReady=0`、`newLive=0`，獨立E review task/session/evidence 欄位皆無值。MASTER 新 AI 契約 PR46 尚未接上 publisher。PR30 是唯一台帳，不創新台帳。

檢查：`python -m unittest discover -s tests -p 'test_114_role_b_batch03_20261025.py' -v`；此驗證只證明 draft 結構與 SHA，不是正式發布審核。
