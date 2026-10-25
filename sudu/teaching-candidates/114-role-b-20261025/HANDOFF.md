## 2026-10-25 使用者政策修正｜以本段為準

本批七題已刪除所有「必須有真人教師資格、簽章、授權名錄或 GitHub APPROVED」之阻塞項；**高職老師僅是解說角度**。保留既有 PR21 教學、原 WebP、來源revision與 composedTeachingSha256，未重新擷取或再生合格內容。新的必要內容關卡是**不同作者的角色 E AI 實質逐題複核**（不允許 B 自評充當）、官方最終答案與更正公告確認、同教學 digest 的 V4 8×2 回歸及主指揮發布驗證。所有逐題 `review.independentAiContentReview.status=PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW`，reviewerTask/notes SHA 均為 null，沒有偽稱 E 已批准。

相容性舊欄位 `review.humanTeacherVerified=false` **僅為歷史資訊，不能當成發布前置條件**；publisher/registry 綁定改造由 MASTER 負責。PR46 AI 憑證契約仍為 Draft **未接正式發布器**。所有題 `BLOCKED` 是尚缺真實來源／不同作者 AI／UI／主指揮批准，與是否有真人教師無關。Issue36 claim: https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393706001 。

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
- 主指揮命令與唯一台帳已在協作分支 `coord/114-115-delivery-command-20261025`（PR30）可讀；正文舊版中要求真人教師的項目已由 Issue36 首段使用者最新政策取代。
- 後續由不同作者的角色 E 執行可核對來源、官方答案、每選項及教學 SHA 的 AI 實質複核；必要時角色 D 對確切新增教學 digest 執行 V4 8 尺寸 × 2 主題 QA；唯獨主指揮可決定進入正式合併發布。

驗證：`python -m unittest tests/test_114_role_b_teaching_20261025.py -v`。通過只代表資料結構與 SHA 自動檢查，不代表獨立 AI 複核通過或發布許可。

## Issue #36 Loop｜Role B 原作者返修（taskId `B-114-OPTION-REASONS-20261025-01`）

- 控制台：https://github.com/homelux-huang/7581707/issues/36 ，認領留言 #6393593834；GitHub 伺服器建立時間：**2026-10-25T04:47:58Z**（12:47:58 臺北）。
- 指揮文件現位於 `coord/114-115-delivery-command-20261025` PR #30；逐題唯一台帳 `docs/114-115-QUESTION-DELIVERY-LEDGER.json` 共 410 個**候選**，非 410 個可發布；以 PR #30 管理，不在本分支建立第二本台帳。
- 確認 PR #31 留言 #6393532719 與 #35 真實失敗 run #40162791292：英文08 B、英文09 A/B/C、國文03 A/B/D 的 `reason` 空泛／太短；舊 Python 測試 `git_blob_sha()` 中 NUL header 的 escape 也錯誤。
- 原有 PR #21 英文07～09 `baseTeachingEvidencePath`、原 Git Blob SHA、原四選項老師／國小解說與原始 `baseTeachingCanonicalSha256` **未變更**。本批英文08/09 只加 `optionReasonOverrides` 覆寫實際候選教學 `optionExplanations[A-D].reason`；renderer/角色 D 要先以 PR21 原內容複製再局部套入，不得將原來源當已變更。
- 國文03 只修改原候選 `teaching.optionExplanations[A-D].reason`，逐選項各有具體語境或詞義；不修改題幹、來源、單題 WebP、教材、正式答案旗標。
- **新 canonical digest 不是僅對原 base raw teaching 計算**：`sha256(canonical_json({questionId,sourceRevision,webpSha256,teaching:effectiveBaseAfterReasonOverrides,enrichment}))`。原出處 Git Blob SHA 另獨立驗證，舊 digest 失效，角色 D／E 只可驗新 digest。
- 適用驗證：`python -m unittest discover -s tests -p 'test_114_role_b_teaching_20261025.py' -v`，包含六個 test methods，負向禁止泛稱／重複及舊原文 Git Blob 篡改（測試通過不等於來源、不同作者 AI 複核、V4或LIVE QA）。
- 最新使用者命令取消真人教師／授權名錄／簽章前置要求；舊 `authorizedReviewers={}` 和 `requireHumanTeacher=true` 是主指揮尚待修復的歷史發布器政策，不再作為本角色的教學審查阻塞。角色 E 不同作者 AI 實質複核仍待完成；所有 `review.status=BLOCKED`、new READY=0、LIVE=0。
- 下個候選教學批次應由角色 B 另立 taskId、先檢查 Issue36 租約，再選已具完整原圖、文字 A–D、官方來源可對應的 114 題目；源不完整的英文10與數學B候選先不放行。

先前 handoff 中「coord 主指揮文件不存在」乃第一版檢視時的舊狀態，**以上新狀態覆蓋該說法**。
