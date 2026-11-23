# ROLE D｜114／115 年現行 main 真正瀏覽器 8×2 回歸（僅隔離 QA，不發布）

- 來源：GitHub MASTER Issue #36 CLAIM #6595323090，taskId `D-114-115-CURRENT-MAIN-APPROVED-REGRESSION-20261103-01`。
- 受保護 main 原始 HEAD：`ba2f3f0757dbf81eaaf125bd610b0f38de52fea9`。
- 唯一學生網站：`sudu/v4-115-multisubject-review-demo.html`，不重做 35 Demo、不改學生紀錄。
- 只有新增 3 份 ROLE D 測試／CI／交接文件，**沒有修改原生 HTML、runtime、A/B/C/E 來源、approved、publisher、MASTER 台帳或 Pages**。
- 特別注意：MASTER PR113 正另行修正非計算卡，這個 D PR 不觸碰該 HTML。

## 實際同版資料保護

- `approved/114.json` Git Blob `874e47c72134b79778741d0c28a4f5c638e7626d`：**0 題可作答**；`preview/114.json` 原圖只讀 9 題，禁止選項、答案、評分、計算卡及新增正式學習紀錄。8 尺寸×2 主題，額外 16 個真實 Chromium 瀏覽器視覺/互動/位元原圖驗證；每個案例保留 PNG。
- `approved/115.json` **當前** Git Blob `51e7b4e73e2d46b4c8b1672c6af20477cc90d44e`，`sourceSha=16d04a0d642fb433de289417a22c3050aa3e52b6`：目前正式歷史五題 `115-00-MB-02/03/04/05/09`，答案依序 A/A/C/B/A，絕不新增 READY；測試直接連真實已核准 HTTP JSON 和 WebP bytes，不用 route.fulfill、假 author、fixture。
- 原 D PR88 Git Blob `2a378d9a2e4a390b6c9a2c2239783a018ba0c801` 和原 sourceSha `1eac8fe...` 已過時；不能用舊截圖為更新的 main 提供憑證。此批直接重新跑新版 5×8×2=80 真作答。
- 每題測試：原題/選項/解答、HTTP 原 WebP SHA256 與 decode/比例、四個選項高職/國小/理由、完整多步數學公式只有一份、手機觸控和桌面滑鼠 hover、橫向溢出、CJK glyph、錯題復習、正式 115 與 Demo 的 localStorage 隔離、原版 V4 深淺主題。
- 逐題 JSON 記錄 `headSha`、正式 approved JSON 的 Git Blob / SHA256、原圖 SHA256、實際計算步驟與 legacy QID payload SHA256、HTML/runtime SHA256、每個 screenshot 和 CI run。**原五題未附新式 `testedTeachingDigest`，因為它們依 main immutable-five legacy exception；這個技術回歸不替代新式正式新題的 E/D 授權。**

## CI 判準與限制

- 新分支 `qa/role-d-114-115-current-main-8x2-20261103`，在 exact Git SHA 的獨立 workflow 真正執行 Playwright Chromium + zh-TW Noto CJK；不修改學生資料。
- `scripts/sudu_verified_publish.py check` 和 `scripts/build.py` 必須 PASS，所有瀏覽器 case、原圖 HTTP bytes 和零分數 114 路徑皆 PASS 才能報技術驗收。
- 有任何 missing PNG/JSON、source 資料版改動、跨年度寫入學生紀錄、截字／錯誤答題即 FAIL，保留 log；不可放寬 gate。
- 這是 **D QA-only**，不是獨立 ROLE E 簽收，不設 READY、不合併 main、不宣稱 LIVE 新增。後續 114 E11/E12/E13/E14、115 C16/C17/MB23 等新題須等 A/B/C/E exact revisions 送達再分題跑正式新版 16/16。
