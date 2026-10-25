# 114／115 逐題獨立 AI 教學複核與正式發布準入政策

**最新授權：** [7581707 共同 Loop 控制台 Issue #36](https://github.com/homelux-huang/7581707/issues/36)，2026-10-25 使用者統一修正。本文件取代舊版真人教師／資格名錄／教師 Ed25519 簽章／真人 GitHub APPROVED 的教學前置條件；這些**不再要求**。高職老師僅指解題角度，非真人身份。

## 新題發布採不同 AI 作者獨立複核

- **角色 B/C**：撰寫「高職老師角度」及「國小學生能懂」兩層教學；逐項解釋 A／B／C／D；重點詞、字、算式需明確粗體／highlight。計算題須列公式用途、代入、完整步驟、結果、單位、驗算；非計算題隱藏計算區。
- **角色 E**：必須不同於 B/C 作者，提交實際逐題內容檢查筆記及來源核對。記錄可稽核的 role／session／taskId／Issue #36 RETURN、來源原稿 commit／questionRevision／WebP SHA、教學 digest、官方最終答案及更正公告證據 SHA。不得將作者自評、AI 複核、真人教師或「盲解」混稱。
- **角色 A**：官網原題及原始圖表／文字／A–D 選項／最終答案更正公告／WebP SHA 與 SQLite 一致性，保持每一題真正原圖完整。原圖 QA PASS 不等於內容或教學已核准。
- **角色 D**：依現有 35 題 Demo 對應科目 V4 版面，驗證 **同一個** questionRevision、WebP SHA、teachingDigest，真實 8 viewports × 2 themes、互動與 CI。舊版本的 UI 測試不得沿用新教材。
- **唯一主指揮**：只在逐題來源、官答、雙層教學、不同 AI 複核、圖像、V4 與發佈閘門確實通過後，才可增量 PR→main→Pages，並以相同 SHA 核實 LIVE。不能批次設 PASS、直接推 main、由作者自己充當獨立 E。

## 程式准入與信任邊界

本政策對應提案分支 `governance/114-115-ai-publisher-gate-20261025`，從已獨立檢驗的 PR #46 衍生，**尚未合併正式 main 或發布**。

- `independent-review-policy.json`：使用 `reviewMode=DISTINCT_AI_CONTENT_RECEIPT_V1`，不含 `authorizedReviewers` 舊真人教師名錄；`requireHumanTeacher=false` 只是一項明確語義，並非發布通行證。
- `scripts/sudu_independent_review_gate.py::certified`：新題走獨立 AI E 原始收件證據；**不得**回退舊人類簽章流程。E 複核原始證據必須經過 protected main 上保存的精確註冊資訊、真實 GitHub Issue #36 留言與來源 commit、來源／官方／教學／WebP SHA／實質四選項／計算筆記等核對；不符或查不到一律拒絕。
- `scripts/sudu_verified_publish.py`：主動確認目前政策模式，並保留 OCR／原始圖像／官方答案更正公告／獨立解題來源誠實性／所有 A–D／計算／V4 UI 與同版 CI 證據完整檢查。舊版 115 數學 B02/03/04/05/09 僅能憑原 Git Blob、版本與圖像精確一致保留。
- **重要信任界線：**「不同 AI Session」不一定代表 GitHub 帳戶不同。受保護主分支仍需可信租約／角色分配與真實 E 返還證據；不能依自由填寫 role/session 字串自批。GitHub main 保護是程式供應鏈安全，不是「教師資格認證」。

## 本批實際阻塞（不得假報）

`trustedAiReviewReceipts={}` 尚未收進可發布的新題 E 正式逐題證據。因此在本隔離 PR 中**新 READY=0、新 main=0、新 LIVE=0**；只是完成政策路由與負測。當前 main 仍維持舊程式，須由主指揮先完成隔離整合、獨立驗收後才能正式生效。不得為了自動發布，捏造審查留言、教師、盲解、簽章、官答或 UIQA，亦不得降低原本測試。
