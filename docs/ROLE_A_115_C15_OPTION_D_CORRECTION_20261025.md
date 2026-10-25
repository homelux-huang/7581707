# Role A — 115 國文第 15 題 D 選項跨頁污染／SQLite 單筆修正（2026-10-25）

**Issue #36 任務：** `A-115-C15-OPTION-D-CROSSPAGE-SQLITE-20261025-09`。分支 `qa/role-a-115-c15-text-sqlite-correction-20261025`，以本角色既有 [Draft PR #61](https://github.com/homelux-huang/7581707/pull/61) 確認的 SHA `2bc5122a7edd4ba5a357cb62458003a2e31856d4` 為基底，**不操作 main、學生答題資料、Pages、其他角色檔案**。

## 缺失事實與精確處理

- 題號：`115-00-C-15`（115 年國文 15）。官方原始單題 WebP 的 SHA256 為 `74dc7bb966f1ee508456a962a6fbcff0f42a15b2ffdd8db747477a55b831405f`，正式圖檔路徑 `sudu/data/processed/115/webp-v2/00-C/115-00-C-15.webp`，原圖第 5 頁區域 `[90,1421,1310,1660]`；第 5 頁原圖 SHA256 為 `bf0678abeeddb131a843fe0461182a3a15ffaf836461933539dc3db1602cd98b`。
- 原始來源 QA `QA_115_C_Q06_Q11_15_DIRECT_VISUAL_20261023.json` 原 Git blob `fca5b8e9e16b390f245c93caeb420b4b86f97f60` 已歷史性記錄原題圖 A～D 完整且無混入第 16 題；此處重用已 QA 圖像原版，不冒稱本批獨立目視 PASS。
- 原 `questions.json.options[3]` 在正確選項 D 文字 **「拘泥禮法 ／ 不知變通」** 後附加不相干的第 5 頁頁尾、第 6 頁考卷頁首、`▲閱讀下文，回答第16-18 題` 及整篇其他閱讀文字。這是**結構化 OCR／PDF 文字層跨頁污染**，不是 C15 官方原圖錯誤。
- 僅把 `q.options[3]` 修正為 **`拘泥禮法 ／ 不知變通`**，其餘 A/B/C、題幹、正解 B、來源原圖 SHA、歷史答案 QA 和所有 204 題都不變。**保留 `q.extraction.rawOptions[3]` 舊全文不動**，便於回溯來源及偵測裁切與 OCR 錯誤。
- 只更新同一題 `sudu/data/processed/115/question-bank.sqlite3` 的 `payload_json` 與 `payload_sha256`（使用既有 canonical sorted JSON 規則），其他 204 筆及欄位不變。SQLite 仍保留全部 205 筆、`PRAGMA integrity_check=ok` 和 canonical JSON 同步。
- 原記錄 `answerVerified=true` 及官答 B 為前人已完成的 TCTE 原始答案圖／更正公告 QA（官方 C15 不在更正列示範圍）；不會因這次純文字手術新增另一項官答審核。**`questionVerified=false`、`integrationReady=false`、未成 READY/LIVE**。此修正也**不代表**完整文段／表格、教學四選項解說或不同作者 AI 複核已完成。

## 決定性修復與 CI 安全措施

`scripts/role_a_115_c15_option_d_fix.py` 使用**原始 WebP 實體 bytes SHA／尺寸、歷史 QA 真正 Git blob、原始題庫 Git blob、原始 205 SQLite hash** 作前置條件。若任何一項與基準不符，直接失敗，不刪檢查。修補僅替換題庫內單一選項 D JSON 字串，保留其他欄位與 204 筆語意不變，同時更新單一 DB row，產出 `QA_115_C15_OPTION_D_CROSSPAGE_CORRECTION_20261025.json`，列出舊原始選項 SHA、新選項 SHA、新舊 `text_revision`、原圖 SHA 與未完成的獨立 QA 閘門。

`tests/test_role_a_115_c15_option_d_fixed.py` 直接與 PR61 精確 Git 原始版本做比較：**205 題僅 C15 D 不同**、**SQLite 205 row 僅 C15 payload SHA 不同**、原始 OCR 污染保留、官答及所有原圖不變、負面篡改失敗、全庫讀回一致。前一批既有 `test_role_a_115_c11_15_shared_receipts.py` 中 C15 污染「保持未修」的測試，改為**已修正 D、仍保留 raw 證據且未核准**，其他 8 項圖片與官方 QA 驗證完整保留。

分支專屬 `.github/workflows/role-a-115-c15-option-d-source-fix.yml`：只在此隔離分支觸發，使用標準 GitHub Actions Token 寫入權限**僅更新這份題庫 JSON、SQLite、來源更正證據檔**；禁止對 `main` 及 Pages 部署，禁止 force-push、私人密碼與修改其他角色檔案。若 Repository 權限不允許 CI 提交則 fail-closed，記錄阻塞，不能宣稱已修好 DB。CI 後還須重新跑**實際最終 HEAD** 測試；不得沿用上一 SHA 的成功紀錄。

## 後續正式接入條件

唯一主指揮可收取此 Draft PR，但必須依最新完整來源與教學 SHA 更新單一控制台、逐題台帳及 UI/CI 測試。角色 C 應將 C15 新 `sourceRevision` 作為後續教學版本基準，角色 E 以不同 AI 作者身分檢核文字、A～D 與閱讀理解，角色 D 驗證同版原圖及現有 35 Demo V4。**無真人教師資格、簽章或 GitHub 人工 APPROVED 前置條件**，但實質內容、官方來源、完整來源及 V4 QA 仍不能省略。所有錯誤待核對題持續隔離、先接其他 READY 題。

**狀態：C15 source-text correction candidate — independent OCR/source final review pending, new READY=0, new LIVE=0。**
