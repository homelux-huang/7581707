# ROLE E｜PR #57 independent AI publisher threat model（2026-10-25）

這是獨立的 **AI 安全 QA 草稿**，不是授權教師、真正人工 APPROVED、學生題庫內容 PASS、READY 或 LIVE。

- Role：E（非 MASTER、B/C 教學作者）。
- TaskId：E-PR57-AI-REVIEW-GATE-INDEPENDENT-AUDIT-20261025-18。
- Issue #36 CLAIM：comment 6394286443。
- 被測 PR #57 frozen HEAD：8c998e00bd60bd183b0c1b253a33511486c0d4b0；PR #46 基底：882bcaa4b5ad5e60d130e599872ce84b53b6c657。
- PR #57 原始 CI run 40165931899/job 121086853721 已 SUCCESS，與新 E 對抗負測分開。
- 實際 main 57d766e841235b937babf3fe10a8ff44606c7c41；GitHub REST main protected=false；未整合新版本。
- PR #57 trustedAiReviewReceipts 是空 dict，僅保存 115 MB02/03/04/05/09 五筆歷史入場資料。
- GitHub connector 目前登入 homelux-huang，**同一 GitHub 使用者不能單獨證明不同的 AI Session**。不虛構獨立 GitHub 帳號或正式認證。

## P0：本地歷史列表可被擴大、重新封裝

PR #57 scripts/sudu_independent_review_gate.py 第415～422行先從 **本地的** policy.legacyAlreadyPublished 查任意 ID，匹配 year/questionRevision/WebP SHA/teaching blob 後直接回傳 exact_five_historical_students_preserved。此流程沒有對照 protected main 原始政策 Git Blob，也沒有獨立的五題不可擴張 ID 集合，直接跳過第435行受保護 main AI E 驗證。

- 新對抗負測1：傳入一份只在測試記憶體加上 115-09-2-34 假「第六筆歷史」的 policy，**必須拒絕**，不可直接 E 認可。
- 新對抗負測2：傳入一份只在測試記憶體重新封裝 115-00-MB-02 舊歷史題的假 source+teaching triple，**必須拒絕**，不可將新字節當成 immutable 舊題。
- 現有 tests/test_sudu_ai_publisher_policy_migration.py 只核已簽入的政策剛好五筆；其測試第70～75行還容許修改本地歷史行再 PASS，未檢測此攻擊。

**實際工作流程邊界（重要限定）**：現行 sudu-verified-autopublish.yml 會分別 checkout main 的發布器／政策與 _source_qa 的來源題庫；只修改 QA 題庫分支不會在這條正常工作流程中自動置換本地政策。本次紅燈證實的是 certified() API 在收到*被污染的政策物件*時未 fail-closed，不是已證實正式工作流程遭到外部來源修改而放行。main 目前又未受保護，且其它呼叫路徑可能誤用此 API，因此仍需 MASTER 修正歷史信任根及補足跨流程負測，不能據此虛報實際未審題上線。

**安全補修方向**：歷史豁免只允許在可信受保護 main 真實固定五筆 ID 與原始 triplet 上做逐 byte 比對，禁止第六題、臨時改政策或用不同內容重新封裝五題。其他既有 official/source/image/OCR/teacher-style/D UI/CI gates 仍保持，不能說此 P0 已造成正式學生網站未審題被發布。

## P1：Issue36 的真實 E RETURN 文字辨識大小寫

scripts/sudu_independent_review_gate.py 第241～247行用大小寫敏感子字串 role E 或 role: E，會拒絕同樣有真實 Issue36 留言來源、GitHub user ID/commit SHA/時間/材料八欄的常用寫法 Role E 或 ROLE=E。

新 E 測試以合成 mock 的匹配身份及版本，要求 genuine-style RETURN — Role E 被接受（仍須滿足其它身分與 hash 門檻）。不能因改文字偵測而關閉 GitHub ID/Issue URL/材料 digest 斷言。

## 其他獨立 E 風險：Session 不可自行聲明為不同作者

證據 schema 只用 B/C 與 E session 字串比較；角色間共用 GitHub homelux-huang 登入時，這不足以證明實際跑過不同 AI 審查。必須用受保護、不可由作者自填/改寫的 Session 派工、執行 log、E substantive review 綁定，才能真正批准。此處僅風險報告，不自行設 PASS。

## 安全執行與退出

唯一 E-owned 新增檔案：本 MD、tests/test_role_e_pr57_adversarial_review_20261025.py，以及一個 read-only GitHub Actions workflow；不碰任何 MASTER/A/B/C/D 程式／題庫／部署。

執行：python -m unittest discover -s tests -p 'test_role_e_pr57_adversarial_review_20261025.py' -v

**真正 E CI 第一次結果**：run 40168669561 / job 121094866867，在原 E HEAD a4491027c1f4f3fe3a02d8e8f7ae1a23091e9a26 上執行 5 tests，2 PASS、3 FAIL（上述兩個歷史信任邊界拒絕失敗、一個合法 Role E 大小寫被誤拒）。失敗是安全測試中的產品程式行為，不是 checkout/ Python/語法錯誤；原 PR57 的 78 PASS 仍是真實的既有測試。

**MASTER 修正前本 E 安全回歸必須保持 RED，不刪斷言、不改 skip/continue-on-error。** 本文件補充後會觸發新 HEAD 的同一測試，最終 SHA/run 以 Issue36 RETURN 為準。