# ROLE D｜115 年數學 B 第 20 題｜新版逆向驗算與修正版 v5 原始 WebP 8×2 QA-only

**Task** `D-115-MB20-NEW-CALC-DIGEST-8X2-20261104-02`，Issue #36 [Claim #6623727852](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6623727852)，僅 ROLE D 一題技術檢測。依使用者最新指令先完成 114/115，104～113 年新增工程凍結。

## 原始來源與不同作者教學 SHA

| 欄位 | 固定 SHA／狀態 |
|---|---|
| 官方 A source Git HEAD | `fbd7756b995e3d27dc31a99ecc54fe66af4d82c6` |
| 官方原題號 | `115-00-MB-20`，115 數學 B 第20題，歷史官方答案影像 A |
| 原圖 WebP SHA256 | `f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf` |
| 原試卷 PDF SHA256 | `e82e34d9cda67c8d28f556d7eb0cd1cd8486b66ccfbe4423d7a40857d7289082` |
| 原圖路徑 | `sudu/data/processed/115/webp-v5/00-MB/115-00-MB-20.webp` |
| 原題 sourceRevision | `2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c` |
| 作者 C PR118 HEAD | `e50198cad6821a5252008bd474d8240510832f85` |
| C 最新 teaching digest | `2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d` |
| E 不同作者內容核對 | [Issue #36 #6623654829](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6623654829) 最新 digest 實質計算 PASS；**尚非受保護 main 可信 E receipt** |

**已知來源缺陷不可遮掩：** 舊 v2 題圖曾裁掉圖（四）下緣／說明。現 v5 manifest 雖 `qaStatus=PASS`，其 `visualDefectHistory.repairStatus=generated_pending_independent_visual_recheck`；這表示仍需要 A 確認修正後的獨立來源 G2/官答 G3，而非本 D 可宣稱正式原圖內容審核 PASS。

## 真正數學內容與 UI 斷言

- 正式原題：AB＝100 公尺，∠A＝60°，∠B＝75°；∠C＝45°，AC = 100 × sin75° ÷ sin45° = **50(√3＋1) 公尺 ≈136.60254 公尺**，選 A。
- 新版逆向驗算：AC × sin45° ÷ sin75° = AB = 100 公尺；且 ∠B＝75° ＞ ∠C＝45°，故 AC ＞ AB，大小合理。
- 四個 A–D 選項應完整保留 C 高職原理、國小白話與正誤原因，不可使用舊 digest 或示範教材代替。UI計算區塊必須顯示完整 7 段作者推導及公式用途、代入、結果與逆驗；不可缺失或重複。
- 真實 360×800、375×812、390×844、412×915、430×932、768×1024、1024×768、1440×900，Light／Dark，**1 題×16 次 Chromium**：原始單題 WebP HTTP bytes SHA、decode、圖片比例、題號／選項、實際 hover/touch、正誤切換、錯題記錄、CJK/英文文字、RWD/學生與 Demo localStorage 隔離。
- 每張截圖均有 QA-only watermark，含原 sourceRevision、完整 C digest 及 D/test HEAD 的 JSON 結果；遇錯必須紅燈和保存失敗 PNG，不可假報。

## 非正式發布限制

- Base 是已 192/192 技術 PASS 的 D [PR142](https://github.com/homelux-huang/7581707/pull/142) exact HEAD `a0c9a87fd284494de9efb9e0de203add835b9131`，疊在 MASTER [PR141](https://github.com/homelux-huang/7581707/pull/141) strict 114/115 來源年度公告發布器，**兩個 PR 均未合併 main**。
- 測試固定原 115 `approved/115.json` 只有原五題，不把 MB20 寫入正式已核准資料；僅 CI 本機以 Chrome HTTP request interception 將真 A 原題 + C 新版教材暫時顯示，WebP 暫放 `_site`，結束移除。
- E 內容確認與數學算對並不代表 A canonical 205 row、SQLite、官方更正公告 G3 或 E trusted registry 已完成；來源變更需重做教學 digest/E/D。正式獲准後，D 還需對真正 `approved` emitter **同一教學 SHA** 做一次完全不攔截的真實 16/16，才可交 MASTER 決定 READY→main→Pages LIVE。現階段的新 READY=0、新 LIVE=0。
- 本 PR 只新增測試／工作流程／本文三個 D 自有檔案，不寫 A/B/C/E、新正式 approved/main/Pages／PR30，不重做 OCR/圖片，不建第二套網站。
