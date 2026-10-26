# ROLE D｜115 年目前已發布 5 題數學 B｜真正 approved 資料 8×2 V4 全算式回歸

## 真實已發佈資料 vs 新代碼未上線

- 控制台 [Issue #36](https://github.com/homelux-huang/7581707/issues/36) taskId `D-115-MB02-05-MB09-REAL-APPROVED-V4-8X2-20261026-02`，CLAIM `6409040668`（時間以 GitHub 伺服器建立時間為準）。Role D 技術 UI/browser QA，非 A 原始圖片、B/C 教學、E 獨立 AI 複核或 MASTER 發布者。
- 唯一原版學生頁面 `sudu/v4-115-multisubject-review-demo.html`，原七科各自的 35 Demo 樣式、已修補的英文原題空白、國文非計算卡及其他互動不得改成通用樣式，也不得另開網站。
- 本次新隔離分支 `qa/role-d-115-mathb-five-approved-real-v4-20261026` 從先前已完成 D [Draft PR #84](https://github.com/homelux-huang/7581707/pull/84) HEAD `0d810e0ca41e4a7d8f60ff3055e91a8924d06895` 建立，Draft PR 疊加於 PR84，**沒有 main/Pages 更動**。不同於 114 E11/13/14 QA-only 截流，本批瀏覽器**直接讀真正已發布且版控內存在的** `sudu/data/approved/115.json` 原值，Playwright 不能 route.fulfill 假冒或改寫 approved 115。
- 本批原始 five GitBlob `2a378d9a2e4a390b6c9a2c2239783a018ba0c801`，原 approved `sourceSha=1eac8fe1869ff6956e929b71b62cbd83debb58ed`。 `approvedCount=5`，原本就已發布，**不是這輪新增 5 題 READY**。

## 固定對應題目與原實際答案

| 115 數學 B 原始題號 | 官方既有已發布答案 | 原單題 WebP SHA256 |
|---|---|---|
| `115-00-MB-02` | A | `c159f4f02a503c998f57213d73f6069acdeaf6ab521aca1cc9719a04a83e8a1d` |
| `115-00-MB-03` | A | `03d5f494eb30b1fc452586e5bf1d1de5a917ba2cc98291e8bace8273b8a6872b` |
| `115-00-MB-04` | C | `0fa2c98cf699f4d4dab11680416d812efcad34eaf9faf6ed5f7de8030ec17562` |
| `115-00-MB-05` | B | `be5bb1f0e23eddff9e8a0f17e6e116ce2ce4219205f4527d50a710fb76e20dd2` |
| `115-00-MB-09` | A | `f2c0430dfea667e165f7961b7318e0cde0d28f3f2007fccc4aed4e4ac6ca2b10` |

每筆原 approved 包含 A–D 的高職老師角度、國小白話、選項 why，`examCalculation.hasExamCalculation=true`，有確切不少於 6 行公式／代入／解題／結果／選項等計算資料。並非出題模型臨時生出、圖片重繪或以 Demo 證明正式題庫。

## 真正安全 QA，非新出版

- 測試程式只讀 GitBlob pinned 的 **同一份** `sudu/data/approved/115.json`（若 Blob 已變，測試一開始必須 FAIL 並重新稽核來源），從 `scripts/sudu_verified_publish.py check` + `scripts/build.py` 建置、真正 HTTP `data/approved/115.json` 讀取，逐位元比對下載 SHA、原正確答案、四選項、所有高職/國小/理由、各獨立實際 WebP 的 HTTP SHA256 / `img.decode` / 不變比例。
- 原 V4 內單題 `考題計算式` **必須恰好出現一次**，行數必須與 `examCalculation.lines` 完全一致，每一行公式、代入、計算及結果都要在可見畫面呈現且不裁字，不得用泛用 `公式` 或記憶卡取代。
- 真實 Chrome/Playwright 80 個答題檢查：5 題 × 實際 `360×800,375×812,390×844,412×915,430×932,768×1024,1024×768,1440×900` × 淺/深兩主題；真滑鼠 hover/click、手機真 touch、答錯時正解綠與錯誤紅、上下題、錯題診療室列出五題、正式 115 年專用學生歷史寫回且與 Demo 歷史逐位元隔離、CJK 字形非 tofu，畫面不水平溢出。
- CI 產出 JSON：exact HEAD、原始 approved JSON GitBlob+SHA256、HTML/runtime 版本、每題原圖 SHA/計算步驟數、80 張實際 115 原頁截圖 + 逐筆 PASS/FAIL。此是 **真實舊五題在新 Draft V4 的技術回歸**，仍不可把分支未合併的結果當成 main/Pages 最新正式部署 LIVE_VERIFIED。
- 原 35 Demo 一律保持既有表現；PR #84 的 114 E11/13/14 和 E12 保留其隔離與確實 E 缺失。本批不編輯任何 approved 資料、圖片、OCR、來源 revision、教學或 E 標章，不發佈。
- 沒有符合發布安全門檻的其餘 114／115 題由 MASTER 自己增量釋出；D 只能在真實 E-A-B-C/正式來源驗收後綁新 digest 做逐題 8×2。真正 main 最新已有 PR protection，仍須由唯一 MASTER 做 formal PR 與 LIVE 同版本驗證。
