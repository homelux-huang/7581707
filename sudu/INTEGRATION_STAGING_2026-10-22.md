# 7581707｜115 題庫隔離接入盤點與發行閘門（2026-10-22）

## 掛載與限制

此檔隨 integration/115-qa-gated-20261022 分支提供。母版本 main 2cb057f60867824cf06e943adfce97b12634ae77；資料取自 data/115-full-year-question-assets 10d7a795c8b885f5a23148091a0e1603cddd3ef4；獨立答案頁初查來源 qa/114-115-official-visual-review db201acd54ce0ff64990be1cad50eb8c9a0256b5。

本分支借用同倉庫原有 blob/tree（相同 SHA）接入 sudu/data/processed/115，保留 115 單題 WebP、OCR 候選、questions.json、SQLite、manifest、QA 原件。沒有重抓 PDF、重做 OCR、裁圖或更動來源紀錄。此為「工程 staging」，不是通過資料 G0–G6 全部驗收，更不是學生可用。

核心程式 scripts/sudu_integration_gate.py 採唯讀載入，逐題核對年度／試卷／題號唯一 ID、逐張影像 QA 原始 SHA、共用材料、文字、最終官方答案、資料庫與獨立 AI 解題；在無證據時一律 FAIL CLOSED。sudu/verified_question_adapter.js 可將待核對、AI／官方不一致、已比對但其他 QA 不足分為不同狀態；不一致警示與官方、AI 答案可置題目最上方，答題按鈕必須停用。不修改 main 的 35 題 Demo 或學生的 localStorage、裝置代碼、學習紀錄。

## 結果（待 GitHub Actions 重跑確認）

| 年度／科目 | 預期／候選 | 單題 WebP 已產 | 有 manifest 逐題目視 QA PASS | 待圖片目視 |
|---|---:|---:|---:|---:|
| 115 國文 | 38 | 38 | 7 | 31 |
| 115 英文 | 42 | 42 | 42 | 0 |
| 115 數學 B | 25 | 25 | 25 | 0 |
| 115 商業概論 | 25 | 25 | 5 | 20 |
| 115 數位科技 | 25 | 25 | 7 | 18 |
| 115 會計學 | 24 | 24 | 23 | 1 |
| 115 經濟學 | 26 | 26 | 24 | 2 |
| **115 合計** | **205** | **205** | **133** | **72** |
| 114 七科候選（尚未引入此 staging） | 205 | 205 | 0 | 205 |

115 共用材料：20 張有產出，其中 3 張目視 PASS、17 張待查；已有 WebP SHA／解碼檢查不代替圖片目視。

115 OCR 原始候選共 205 筆，但「逐字、數值、負號、公式與選項」核對未有逐題合格證據，計入 OCR QA PASS 為 0；115 已與原標準答案 PDF 抽取比對 205 筆，QA 分支另初步目視標準答案頁 205 筆，但疑義／更正公告最終內容未完成覆核，正式答案 QA PASS 為 0；AI 真正盲解比對 0 一致、0 不一致、205 未核對；正式教學／UI QA 尚未對新 205 題執行，因此新題學生可用 0。

114 候選 205：13 題缺完整文字四選項（詳見 data/114-full-year-question-assets 的 inventory.json）；5 題舊 PDF 文字答案缺失或落差（五份試卷各第 15 題），QA 分支目視答題頁初查已配對，但最終疑義／更正尚未核實；OCR、圖像 QA 不過，不匯入學生端。

主 UI 的 35 題 Demo 原封保留，不把 demo 的答案文字視為獨立盲解成功。既有 35 題原 key 如「會計學|2」映射為「115-09-2-02」，只讀轉換，不重寫任何歷史答題記錄。

## 來源與逐題定位

- 115 追蹤：sudu/data/processed/115/{inventory.json,VALIDATION.json,webp-manifest.json,VISUAL_QA_2026-10-22.json,REMAINING_VISUAL_QA_CHECKLIST_2026-10-22.md,DATA_HANDOFF.md}。
- 114 追蹤：data/114-full-year-question-assets 分支的 sudu/data/processed/114/{inventory.json,VISUAL_QA.json,webp-manifest.json}。
- 答案頁初查：sudu/data/QA_114_115_OFFICIAL_ANSWER_VISUAL_2026-10-22.json；此報告本身明記 officialRevisionDocumentsReviewed=false。
- 合格總門檻：docs/SUDU_QUESTION_BANK_QA_GATE_105_115.md。
- 發布沿用 .github/workflows/pages.yml + sudu-release-checks.yml，不調整、不繞過。
- scripts/build.py public allowlist 排除 sudu/data/processed 與答案 QA 表，因此即使 staging 分支包含候選資料，也不會被打包進 GitHub Pages；本分支沒有變更 Pages workflow。

## 缺件回交資料工程

- 115 單題 WebP：依 remaining QA checklist 72 題、共享材料 17 張逐張目視；沒有真實 source-to-crop 對照不可補寫 PASS。
- 114 單題 WebP：205 題及共享材料尚待 QA，先修補文件列出的 13 題選項與第 15 題文字異常，補最後標準答案更正查核。
- 115／114：OCR 逐字核對，最終官方答案更正比對，DB/JSON 讀回證據，盲解與四選項教學、八組 RWD；每一步保存題號、來源路徑、SHA、reviewer、時間。
- 105–113 尚未正式接入；由資料工程獨立繼續，這個分支不合併或覆蓋其進度。

## 發布策略

只有在 G0–G6 全過，且每題官方最終答案核對、獨立 AI 盲解一致、四選項解說、介面測試均 PASS 後，才允許把該題加入 main 學生題庫。現有 205 候選不得因庫存或 CI 綠燈自動入學生作答流程；遇 AI 官方不一致必顯示精確警示並停用判分。此分支 PR 為 Draft，未授權自動合併。
