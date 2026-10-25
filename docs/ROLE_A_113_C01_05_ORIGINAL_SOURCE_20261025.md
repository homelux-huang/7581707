# Role A｜113 年國文第 1～5 題｜原圖、官答候選及隔離 SQLite 來源批次

**Task ID** `A-113-104-OFFICIAL-BASELINE-20261025-10-C01-05`（主指揮 Issue #36 歷年 113→104 派工第一批）。這是角色 **A** 真實來源資料工程輸出，不是 C/B 教材、不同作者 Role E QA、人類教師簽核、V4 UI 或正式發布批准。

## 基準與來源重用

- 官方年度：113（2024），商管群適用共同科目國文，原始試卷 `00-C` 題號 01–05，保留原本 [35 題 Demo V4](https://homelux-huang.github.io/7581707/sudu/v4-115-multisubject-review-demo.html) 的國文科 renderer，**本批不改 UI**。
- 既存 `main:sudu/data/years/113.json` Git blob **`d800128217347c7c3c9c3ba1d425ef01e8b39946`**，未重新 OCR、未重擷取；國文 00-C 既存 38 題、`discoveredCount=38`、`answerCount=38`、`expectedCount=38`。全年度五卷候選實際陣列 205 筆，自報 `questionsFound=196`，相差 9 筆，與本卷 38 筆完整自報不可混淆，更不能代替官方逐頁題號確認。
- 官方 TCTE 年度公布頁：<https://web1.tcte.edu.tw/EXAM/113_4y/>；頁面記載 **113 年 5 月 10 日召開答案確認會議、同日 17:00 公布標準答案**，且明示以 PDF 為準。然而本輪執行環境未能重新連線下載該站指定兩份 PDF；下列 PDF SHA 是**先前存在於年度 JSON 的歷史來源 SHA，不是本輪直接重新計算的 PDF SHA**，不得謊稱重新驗證完整更正公告：
  - 題本 PDF 原記錄 SHA256 `67c0d477e99d07cd59af0e9c75b261692c3089fd5559185f41945de32316093f`
  - 答案 PDF 原記錄 SHA256 `9a6ce177b0aec3f22957635cc9abc21539cf3356471b2e3dec65e550e8f9559a`
- 使用實際 Git 原始像素圖而非 AI 重畫：原始題本第 2 頁 `sudu/data/original/113/00-C/p002-67c0d477e9-v2-w1400-q66.webp` Git blob **`6796adb4df977d064baae8a3e066238014d096f6`**；原始答案第 1 頁 `sudu/data/original/113/00-C-answers/p001-9a6ce177b0-v2-w1400-q66.webp` Git blob **`938f88435a9b21e257f11dfcfda71655e8a7a0c6`**。新原圖 **WebP SHA256、尺寸與 crop** 由實際讀檔 CI 計算記錄，不猜測。原始 PDF 名稱與 SHA 綁定來源元資料；原始影像本身可按 Git blob 重放。

## 官方答案候選（原始公布影像逐格讀取，非更正公告完整 QA）

| 原題號 | 官方公布影像顯示 | 既存答案候選 | 素材與文字來源狀態 |
|---|---|---|---|
| `113-00-C-01` | C | C | 題本第 2 頁，完整四選項候選 |
| `113-00-C-02` | D | D | 題本第 2 頁，完整四選項候選 |
| `113-00-C-03` | D | D | 題本第 2 頁，完整四選項候選 |
| `113-00-C-04` | C | C | 題本第 2 頁，含《富都青年》段落與四選項 |
| `113-00-C-05` | D | D | 題本第 2 頁，含琦君〈髻〉段落與四選項 |

採人工可讀視覺直接看**儲存在 GitHub 的原始題本及答案頁影像**完成這五題的圖片／候選答案對照；審查身分是 **ChatGPT Role A 來源初核**，**不是人類教師或不同作者 E 教材審查，也未檢驗所有更正說明 PDF 範圍**。如果任何邊界裁切不完整，不可把候選單題 WebP 標 PASS 或給學生使用。原始圖片、答案內容及文字擷取結果不會改變。正式資料 `answerVerified=false`、`questionVerified=false` 保持零。

## 本批獨立資料工程

1. `scripts/role_a_113_c01_05_source_pixels.py`：用 Pillow 讀取上述原始第 2 頁 WebP，**直接裁切原始來源解碼像素，重新以 WebP lossless 保存**，強制驗證裁後每個 RGB 像素與官方已存原圖裁切區域**逐像素一致**，絕不 AI 補畫、圖像合成、OCR 重產圖；記錄 5 張 Git blob/SHA256/頁次/座標/尺寸。
2. `sudu/data/processed/113/role-a-c01-05/manifest.json`：**僅五題、單批部分來源**。紀錄 canonical ID、既有題幹及 A～D、原來源 JSON 文字 hash、字面官方答案候選、先前記錄 PDF SHA、當前來源頁 WebP SHA、個別 WebP SHA 與 sourceRevisionSha256。狀態 `DRAFT_NEEDS_DIRECT_ASSISTANT_VISUAL_QA`，不給正式 PASS；更正 `PENDING_CORRECTION_PDF_SCOPE`。
3. `sudu/data/processed/113/role-a-c01-05/question-bank.sqlite3`：**五題候選資料庫，不冒充 113 全年度**；canonical JSON payload+SHA256，全數 `answer_verified/question_verified/teaching_verified/student_ready=0`；雙次隔離匯入、新建 DB 全檔 SHA256 一致、`PRAGMA integrity_check=ok`。
4. `tests/test_role_a_113_c01_05_source_receipts.py`：實測 113 年原始 5 卷 ID、205 vs 196 差異、00-C 38 題、原題 01–05 及四選項、官方候選 C/D/D/C/D、原始頁 SHA／五單題 pixel lossless、單題邊界不重疊、205 年度仍未授權、SQL 雙次可重現與篡改負測。
5. `.github/workflows/role-a-113-c01-05-source-pixels.yml`：此專屬隔離分支的 GitHub Actions 才可提交**五張單題圖 + 五題 manifest + 五列候選 SQLite**，核對所有修改路徑限制；不可寫入 `main`、Pages、原始題本、唯一 PR30 114/115 台帳或其他角色內容。驗證成功後以相同 HEAD 重新讀回、再實際目視五張裁切，若有問題只限本批局部調整並保留舊 SHAs/diff。

## 尚未完成，嚴禁混同

**此批不宣稱完整官答最終更正 QA、題目文字最終人工複查、原始 PDF 實際重新雜湊、已獨立 Role E AI 教學審查、D 真實 8×2 UIQA 或正式發布。** 原年原始第 2 頁另含第 6 題對聯與圖形，**第 6 題不屬本批**，不得混到第 5 題 WebP。只要完整 Q01–05 已 QA 合格再與主指揮進一步選可發佈題，其他題繼續。

新 READY：**0**，新 LIVE：**0**。下一批 A 依 113 原卷原始素材核第 6 題對聯及跨頁污染，再依台帳進 112→104；其他角色 B/C/E/D 要等本批真正來源、官答 final confirmation、獨立複核與 UI 同 SHA 證據，不能跨角色自批。
