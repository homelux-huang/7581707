# Role A｜114 英文第 11、13、14 題：官方最終答案影像 QA 與公告適用範圍正式接入

**taskId** `A-114-E11-E13-E14-FINAL-OFFICIAL-ANSWER-20261026-14` · Issue #36 CLAIM #6409257900 · 新隔離 branch `qa/role-a-114-e11-e13-e14-final-answers-20261026`，以 Role A 已交付 [PR #50](https://github.com/homelux-huang/7581707/pull/50) 精確 HEAD `47afa7108b92cbd37b81e0f2d9369a4a3c226ab1` 為基底。**NO MAIN / NO DEPLOY / NO READY。**

## 真的讀取到的原始來源

已透過 GitHub 直接開啟並目視原始 114 英文完整題本 **第 3 頁**，以及原始公告答案 **第 1 頁**。三題皆有完整對話、A～D、唯一題號、無其他題號混入既有原像素單題 WebP。角色 A 是來源及官方答核對者，不是不同作者獨立 E 教學 reviewer，也不是人類教師。

- 原題頁 `sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp`，Git blob `5ff21a726938e64e0b7efe3bb8abda65e55e1d4f`，WebP SHA256 `51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb`。
- 原公告答案頁 `sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp`，Git blob `5f2920313607af4e756095cd3d6098c8a3ab7440`，WebP SHA256 `a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863`。
- 原 114 英文題本 PDF SHA256（既有不可變來源記錄）`1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf`；官方最終答案 PDF SHA256 `ebd3940a54b7059173e1fc7add3df75b59620f7efad93cf822b3ffa72d95b325`。此兩 PDF 的實體 bytes **本輪未重新下載或計算 SHA**，沿用先前來源憑證；既存官方答案 PDF 下載/QA 工作流程為 [#40097216703](https://github.com/homelux-huang/7581707/actions/runs/40097216703)。
- [TCTE 114 學年度四技二專統測正式網站](https://web1.tcte.edu.tw/EXAM/114_4y/) 明載 2025-05-09 召開答案確認會議，同日 17:00 正式公布標準答案，並強調以 **PDF** 為準。公告說明不是 AI 教學的發布核准。

| canonical 題號 | 已實際目視官方答案格 | 原像素單題 WebP SHA256 | 上一批單題原始圖像 QA |
|---|---|---|---|
| `114-00-E-11` | **A** | `ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0` | PASS（Role A assistant source image） |
| `114-00-E-13` | **A** | `81f4487c4012456b4f1c3449aa388f16d12de19b72cc844ae6b6269be76e9be7` | PASS（Role A assistant source image） |
| `114-00-E-14` | **D** | `388773561e436315452bdf0c28c792efa0983eb25538e8b3119926cd338f3a94` | PASS（Role A assistant source image） |

前一批原像素逐題驗證紀錄仍是 `sudu/data/processed/114/QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json`，Git blob `c1154562fa30cb4b2720a6000a970cf09ef460ff`，**不改圖、不重新 OCR、不重新裁切**。

## 官方更正說明的精確適用範圍

沿用已實際下載、SHA 核對並逐頁目視過的**整份 114 英文確認說明 PDF**：在 [2026-10-24 QA 憑證](../sudu/data/processed/114/QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json) 中，114 英文 `00-E` 只有一頁、實際列出 **`114-00-E-26`**，沒有 E11/E13/E14。確認 PDF SHA256 `79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc`，既有 all-pages QA 工作 [#40094431419](https://github.com/homelux-huang/7581707/actions/runs/40094431419)。原公告 `official-confirmation-status.json` 與確認 PDF 全頁清單 `QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json` 的 Git blobs `ecfb5663d5af6008fb71f721ec5f23c69d557f5f` 與 `6b9a919f224bec8dc3659052a404b4173b6ef366` 必須精確一致。

**不可將「這三題未列入更正」誤稱「114 英文全卷未提出疑義」。** 本批每題只允許 `noCorrectionForThisQuestion=true`，同時 `noObjectionForPaper=false`；官方指定第 26 題一旦無列示更正而想套用相同核准證據，既有 `scripts/sudu_verified_publish.py::official_notice_scope_certified` 必須嚴格拒絕。

## 資料工程實際修正範圍與測試

本批只對**確實目視的三題**做官方答閘門更新：

- 只在原始 `sudu/data/processed/114/questions.json` 中對 E11/E13/E14 設 `answerVerified=true`、`officialFinalAnswer`、`officialCorrectionChecked=true`、`answerProvenance.independentVisualVerification=true`、`officialFinalQaEvidence`（綁題號／官方 PDF SHA／審核身分／收據路徑）。
- 新增三份獨立真實來源憑證於 `sudu/data/processed/114/review-evidence/114-00-E-{11,13,14}-official.json`，明確記錄**本輪曾開啟官方已存答案 WebP 原圖，而非本輪重新渲染官方答案 PDF**、驗證者是 GPT-6 Role A source QA、非真人教師/非 Role E、公告命中僅 E26、各題答 A/A/D。
- `questionVerified=false`、`reviewStatus=needs_review`、`studentReleaseApproved` 未設定；E12（已有 IPA 問題）及其餘 **202 題完全不修改**。既有來源題幹、四選項、WebP SHA、shared 原圖、OCR raw 也不更動。
- SQLite `question-bank.sqlite3` 只更新上述三題 `payload_json` 與 `payload_sha256`；**114 原庫實際 schema 只有 7 欄（`question_id/year/paper_code/original_number/subject/payload_json/payload_sha256`），不存在獨立 `answer_verified` 展開欄**，答案驗證旗標只存在經過 SHA256 驗證的完整 `payload_json` 內。其餘 202 筆及所有 SQL 既有欄位 **與精確 base Git 版本逐欄比較不變**。維持 205 筆 `PRAGMA integrity_check=ok`、canonical JSON/DB 讀回全部一致、兩次隔離重新匯入來源完全一致的整庫 SHA。
- `scripts/sudu_verified_publish.text_revision()` 特意只綁定題幹、A～D、原圖 SHA：此批**只修答案驗證**，不應更改 Role B 已撰教學 sourceRevision 或 D 既有相同題幹的 UI renderer digest；仍必須由 MASTER 與 D/E 重新對最新合法 CI 認證，不能直接移用舊 UIQA 當發布票。
- 新腳本 `scripts/role_a_114_e11_e13_e14_final_official.py`、回歸 `tests/test_role_a_114_e11_e13_e14_final_official.py`，隔離分支專屬 Action `.github/workflows/role-a-114-e11-e13-e14-final-official.yml`。包含 205 題對 Git 原始 PR50 **唯一三筆 diff**、SQL 展開欄位限制、官方 E26 反向測試、錯誤圖片 SHA／答案負測，禁止批次設 PASS、不得自認 E AI 內容審核。

## 發布狀態

本輪 A 可以修補**官方公布答案逐題核對與更正範圍**這一關；它**不是**完整來源／解說與同版 UI 的最後批准。後續 B 教學新版本 digest 必須完整 A-D／雙層解說並由不同 Session E AI 以真實記錄逐題複核，D 以 35 題 Demo 相同科目 V4 進行同來源+教學摘要 8×2，MASTER 檢查保護 main、PR CI、Pages 真正發布及 LIVE 實際作答。未檢驗則隔離，已合格者可分題發布而不等整年。新 READY=0，新 LIVE=0。

**下一批 ROLE A：** 優先處理 114 E12 官方答來源（仍不得把有疑義 IPA/教學當過關）、115 C15 已修結構化 D 的來源對接，以及 115 SQLite 81 題既有展開欄位落差；再依 113→104 年順序查缺補漏。

### 實際來源結構稽核補充

本輪最初 CI [#40277072937](https://github.com/homelux-huang/7581707/actions/runs/40277072937) 在**任何 Git 提交前**因預期 115 型態 SQL 展開旗標而停止。隨後明確診斷 [#40277165369](https://github.com/homelux-huang/7581707/actions/runs/40277165369) 證實 114 原 SQLite 資料表 `questions` 僅上述七個欄位，與 115 年資料表不同。沒有為了通過測試去新增虛假欄位、修改教學或批准資料；已改為保留 114 原 schema，僅根據真正核對的 3 題更改其 canonical `payload_json` / payload SHA，並維持**205 題**及原驗收的十進位原題號、年度等欄位。測試同時加強對資料表七欄完整精確比對與另 202 題逐欄不動的回歸要求。**必須取得修補後最新 SHA 的真正 CI SUCCESS 才算本批交付。**
