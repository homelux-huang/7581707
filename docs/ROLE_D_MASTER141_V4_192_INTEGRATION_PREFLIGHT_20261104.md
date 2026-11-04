# ROLE D｜MASTER PR141 年度公告發布器 + 現有 V4 修復的 114／115 年同版整合預檢

## 本次變更的權限、來源及限制

- 最高目標：先完成 **114、115 年各 205 題**；104～113 年**停止新增工程**。Issue #36 [本 D 獨占 CLAIM](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6623605895)，taskId：`D-PR141-V4-EXACT-CROSSBRANCH-192-20261104-01`。
- 由 MASTER 已通過六個 Actions 的年度 114／115 修正版發布器 [PR #141](https://github.com/homelux-huang/7581707/pull/141) exact HEAD `01e342b1902c030a9678836ae4de7d0f5cb3be4c` 建立獨立分支，**PR #141 正在等待獨立 Code Review，尚未合併 main**。本支線不更新原 MASTER PR。
- 於新支線**原字節、原 Git Blob**移植先前 ROLE D [PR #138](https://github.com/homelux-huang/7581707/pull/138) 連續 PR113→PR125→PR127 的唯一 `sudu/v4-115-multisubject-review-demo.html`，原 Git Blob `eb1eacc6d7d8c0f84a8d330f1fd0ce4624d06c55`；已有非計算題隱藏、正式英文作者原句中文翻譯/重點 highlight、英文對話題幹原空白與換行保留三修復。**35 題 Demo 功能/HTML 不另建第二套**。
- MASTER PR141 的 `scripts/sudu_verified_publish.py` Git Blob **`3ba5abcf41abb0a988b56f0b0ae1b83e24eb0194`** 完整保留未改。其 114/115 官方公告/年度路由、獨立 E receipt、核准限制及年別反向檢查，全部由 MASTER 權責處理。本 PR 不修改發布器任何一行、正式 approved/來源/原圖/SQLite、PR30 台帳、B/C/E 稿、main 或 Pages。
- 原 D 5 個測試腳本也由 PR #138 **Git Blob 原樣重用**（不削弱、不重寫斷言），並新增一份只讀 GitHub Actions 工作流程；這不是自寫已通過的假證據。檢驗真實結果以本新分支**最後一個 HEAD Actions**為準，不可挪用 PR #138 或 #141 的個別舊版 PASS 當作聯合 PASS。

## 192 個真實 Chromium 案例＋Demo 相容性

| 來源／題號 | 案例數 | 類別 |
|---|---:|---|
| 正式已有 115 數學 B 02/03/04/05/09 | 5 題 × 16 = 80 | **真正原 approved five、無 HTTP 攔截** |
| 114 年正式 approved=0 的原圖只讀安全模式 | 16 | **真正 HTTP approved=0，不得作答、評分或污染紀錄** |
| 114 英文 E12，A PR116 + B PR107 | 16 | **QA-only 明示拋入原圖/教材，不是新正式題** |
| 114 英文 E11/E13/E14，A PR111 + B PR106（E14 新 SHA） | 48 | **QA-only 原圖/教材來源固定，非正式 emission** |
| 115 數 B 21/22，A frozen source + C PR118 | 32 | **QA-only 原圖、算式、反驗，不是新 READY** |
| **合計** | **192** | 96 真舊版已核准／只讀 + 96 測試階段題目 |

- 8 個固定視窗：360×800、375×812、390×844、412×915、430×932、768×1024、1024×768、1440×900；每一個 Light/Dark。
- 所有新題由**真正存在的 A 原始單題 WebP 位元與來源 revision／作者 A–D 教學 SHA**構成，用本機 Playwright HTTP 暫攔截及畫面 `QA-ONLY / UNAPPROVED / NOT LIVE` 浮水印；真 HTTP WebP SHA256、decode、長寬比例，題號、四選項及答案來源、作者完整計算每一行／非計算卡自動隱藏、中文／英文與重點、hover/touch、CJK 與 RWD、錯題、35 Demo 與年度儲存隔離都須驗證。
- 另執行原有 **7 個非計算／計算卡斷言** `tests/sudu_master_noncalc_guide_20261025.cjs`，與原有 `tests/sudu_browser_smoke.cjs` 對 35 Demo／主 UI 的互動／瀏覽器安全回歸；任何失敗保留原始 log／PNG／JSON，絕不把 RED 寫成 PASS。
- **SHA 鎖定**：同一支線 HEAD、原 MASTER PR141 publisher blob、原 D V4 HTML blob，A 114 E11-14 PR111/PR116、B PR106/PR107、A 115 source `fbd7756b995e3d27dc31a99ecc54fe66af4d82c6`、C PR118 `e50198cad6821a5252008bd474d8240510832f85`；原 115 published approved GitBlob `51e7b4e73e2d46b4c8b1672c6af20477cc90d44e`，原 114 approved GitBlob `874e47c72134b79778741d0c28a4f5c638e7626d`。
- 保存含實際 D HEAD、WebP SHA256、原教學 digest/來源 SHA、每一個 8×2 格子與失敗原因的 **192 張 PNG + 三份精確 JSON**，另留 35 Demo JSON。GitHub Actions artifact 保存時間有限；正式發布必須重新於主線驗證。

## 不構成正式發布資格：待解阻塞

1. **PR141 仍需 MASTER 安全審查與受保護 main 合併。** 本 PR 是聯合分支兼容性候選，MASTER 不能因本支線 PASS 而推測 PR141 已通過正式主線審查。
2. **114 E12/E11 等未核准的 official G1-G3 /205 SQLite** 由 ROLE A 整合；B/C SHA 定版，ROLE E 不同作者獨立內容 QA 與可信 receipt 登錄由 E／MASTER 分別負責。不能因共享 GitHub 身份憑空視為異 Session。
3. **任何新題真正發布**都必須使用 MASTER publisher 所產生的原 approved JSON/WebP，而不是 QA-only HTTP 攔截。D 在新真 emitted source＋verified `testedTeachingDigest` 下重做**每題 16/16 真實 Chrome**，才交 MASTER 逐題 READY→main→Pages 上線並回測真實學生。
4. 本 PR 不改官方原稿/發布器/E 政策/已核准記錄，不繞過主線保護，不提前宣稱 410 題完成。當前正式 **114=0/205、115=5/205、合計5/410；新 READY=0、新 LIVE=0**。

## 建議合併順序

MASTER先獨立審核並通過 PR141，再逐檔檢查 ROLE D PR113→125→127 的 V4 差異和本 PR 此處原樣的 V4 Blob；**不可直接把堆疊 Draft PR138 或本支線不經 code review 批次入 main**。原有 Demo 行為與真正 approved 5 題若變更，應在重新建立發行候選前重新執行 192 組（新 main 變更要重驗），不得沿用這批新支線證據作正式發布。
