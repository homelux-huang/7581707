# ROLE D｜115 年數學 B 第 23 題｜原始 2×3 價目表＋同版 C 教學 8×2 QA-only

- **MASTER 路線：** 114、115 年共 410 題先完成；104～113 年新增題庫暫停。D 一題獨占 [Issue #36 CLAIM](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6623818097)；task `D-115-MB23-2X3-A129-C143-EXACT-V4-20261104-03`。
- **整合底版：** ROLE D [PR #148](https://github.com/homelux-huang/7581707/pull/148) exact `3f42a2c33dfa47c796086b82afc247954736b91f`（已含 MASTER PR141 114/115 發布器、唯一現有 V4 與已驗的非計算/英文/數學介面）。本 PR 不改 V4 HTML、不新建第二套網站、不修改已正式發布題目或原 35Demo。
- **完整來源不能用過期 C revision：** A PR129 真實原圖＋官方答案來源 `cd6fea6682554e4b0f25d41dca79a1532de92482`，A original table evidence Git Blob `0f63d6a5f91015dd2b146731c48dce08668c1fa2`，**新 A sourceRevision SHA256 `9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4`**。原本 C 舊 sourceRevision `c3df98d4...` 已作廢。
- C 作者新的 source-bound [PR143](https://github.com/homelux-huang/7581707/pull/143) HEAD `afaba171eec77cc27c3171b8bc8282f68ade74b9`，只修來源版本指標、保留原教材內容和 teaching digest **`13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6`**。真正原始 205 題 bank 及原圖從 `fbd7756b995e3d27dc31a99ecc54fe66af4d82c6` 唯讀取得，並同步驗同版 C／A source。
- 真原第23題單題 WebP：`sudu/data/processed/115/webp-v2/00-MB/115-00-MB-23.webp`，SHA256 **`2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51`**，官方試卷 PDF SHA `e82e34d9cda67c8d28f556d7eb0cd1cd8486b66ccfbe4423d7a40857d7289082`。無重裁、無 OCR 重新開發。
- 必有 **3 欄「行程／原價／優惠」× 2 列「行程Ⅰ、行程Ⅱ」**、六個原儲存格，四選項 32000／33000／34000／35000，原官方答案 B。完整計算：行程Ⅰ `2x−3000`，行程Ⅱ `1.8(x+2000)`，相等得 `0.2x=6600` ⇒ **x=33000 元**，兩方案代回各 63000 元。每選項要有高職老師角度＋國小白話＋具體正誤原因。
- D 測試從 **A PR129 證據 GitBlob 原位元**讀取 sourceRevision seed、表格標題、3×2 全儲存格、原 WebP SHA/答案影像 SHA，和 C PR143 元資料及字串逐欄對比，再在真實 Chromium 逐題驗證同一編號、原圖真 HTTP bytes SHA/decode/比例、所有 A–D、正誤、7 步原始算式/價格驗算、hover/觸控、CJK、RWD、錯題與 Demo/115 年儲存隔離。
- 固定 360×800、375×812、390×844、412×915、430×932、768×1024、1024×768、1440×900 × Light/Dark，總 **16** 真瀏覽器案例。各案例保存 PNG，顯示清楚 `QA ONLY NOT APPROVED OR LIVE`，SHA-bound JSON 與原始失敗紀錄；不降低失敗閘門。
- 正式 `approved/115.json` 仍只含老五題，不包括 MB23。新題僅於 CI 本機以瀏覽器 request-intercept 測試，_site 暫放**已存在的原始** WebP 且測後清理，**不能被誤當正式 E 收據或真正 emission**。
- **嚴格發布阻塞仍在：** A original source G2/G3 是候選，未入 protected canonical 205題／SQLite；C 的 source revision 新綁定不等於 A/MASTER 放行；E 必須對 A **新表格來源 revision**＋C teaching SHA 做不同作者 AI 內容審查，MASTER 審身份和受信任 main receipt；D 待正式 published issuer 依相同原圖／digest 重新執行不攔截的真實 8×2，最後 MASTER 才能逐題 READY/main/Pages。新 READY/LIVE 都 0。
- 只新增三個 D 自有 test/workflow/docs，不接管 A/B/C/E/publisher/approved/PR30/main/Pages 檔案；PR 維持 Draft。
