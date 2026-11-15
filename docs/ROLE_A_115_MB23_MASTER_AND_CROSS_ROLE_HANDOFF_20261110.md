# 7581707｜ROLE A → MASTER／ROLE E／ROLE C／ROLE D／後續 ROLE A｜2026-11-10 交接 PROMPT

> 本文件為 **可直接貼入其他角色 Session 的工作指令**。GitHub Issue #36 仍是唯一角色租約／RETURN 控制台；寫入這份檔案不等於自動啟動其他 Session，也不是 MASTER 正式發布同意。
>
> 正式學生 V4： https://homelux-huang.github.io/7581707/sudu/v4-115-multisubject-review-demo.html
>
> 目前 protected main `5546a603abfe0af2e62c0e5f63f775be0bfb24cf`，official QA `15108e8e657d070724889f1df3d3a6ae6da96d97`。以執行時實際最新 GitHub ref 為準，任何舊 SHA 必須重新檢查。

## 0. 本輪已完成證據（先讀、不要重做）

- 114 E11 來源 PR179、115 MB21 PR181、115 MB22 PR182：**MASTER 已合併至官方 QA**。詳見 [MASTER RETURN #6768370881](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6768370881)。這些不是學生 READY／LIVE。
- 新 115 MB23 源修復 [ROLE A Draft PR #185](https://github.com/homelux-huang/7581707/pull/185)，目前已驗證來源版 HEAD `ef9059d8fd7fd210b743e743506ad1dc6b0e114f`，base QA `15108e8e...`。
- ROLE A 真實 CLAIM [#6768575685](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6768575685)，完整來源 RETURN [#6768837742](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6768837742)，MB23 shared-bank/SQLite write lease **已釋出**。
- 原始 Q23 WebP SHA256 `2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51`；來源原文／3 欄×2 筆價目表 SHA256 `3ae20c9b53eb5ba38ffa354cbda868806bb7716700548bbe88618e0104a89088`；table-inclusive QREV `9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4`；官答 B = 33000 元。
- Q23 正式 205 JSON/SQLite 來源橋接後 SHA：JSON `1a92d454f4f2bb85ddff6f3f585efbc65d75481928b320397e6d2e05041c5c93`；SQLite `450153ad47907265c9ffbdcb56e7902e606c0abb4eda70d0ba606dcd78607e76`。其餘 204 題完整 JSON 與 SQLite row 值一致不變（含 MB21/MB22）；WebP manifest 整檔未改。
- MB23 來源 G2 issuer SHA256 `64fa11a8a40ff221a9b6cbc34a45ae8da14c9c5fa0a04d5b36f2a4012df7cde7`、G3 `a9c4b2f7e56f8ddb69aca1462af3e762029c5c2e78c6b92d473122b5ba943238`。
- 實際 source+binary generation [Actions #42825795939](https://github.com/homelux-huang/7581707/actions/runs/42825795939) **SUCCESS**；MB23 專屬 exact-head postcommit [Actions #42826152594](https://github.com/homelux-huang/7581707/actions/runs/42826152594) **SUCCESS**，包含 205 payload parity、204 原 row 不變、正反向 source/image/notice/table/release 檢查。
- 注意老版本的 E11／MB21 專用測試對 MB23 PR 產生 **FAILURE**： [E11 #42826162719](https://github.com/homelux-huang/7581707/actions/runs/42826162719) 與 [MB21 #42826162749](https://github.com/homelux-huang/7581707/actions/runs/42826162749)；實際 root cause 是歷史固定 PR 檔案 whitelist、對尚未修復 MB22 時的舊 205 基準比較，不是 MB23 新資料的 205 parity 失敗。不能假報全 CI 綠。
- 學生發布仍：正式 E trust／G6／G7 未取得、D native publisher emitted 16/16 未執行、MASTER G0–G10／main／Pages 未完成。**READY=false, LIVE=false**。

---

## 1. PROMPT → MASTER（立即優先）

你是 7581707 的唯一 MASTER、跨角色整合驗收與正式發布裁決者。立刻刷新 GitHub main/QA、Issue #36 最新 CLAIM/RETURN、[PR #185](https://github.com/homelux-huang/7581707/pull/185) 及其 HEAD/CI。不要重新建立題庫、教學或 V4。

**P0-A：修正既有 E11/MB21 專屬 CI 對後續題目的誤阻塞**。分離「原始一次性來源分支歷史驗收」與「目前 QA 的逐題增量通用驗收」；確認失敗根因：
- E11 `test_only_authorized_single_source_file_paths` 把當年 PR179 變更檔案 whitelist 固定死，對其他 QID 的來源 PR 不適用。
- MB21 `test_204_original_canonical_rows_unchanged_and_manifest_original` 和 SQLite 原基準固定在 MB22、MB23 尚未更新之前，會誤判已合法合併的 MB22／新增 MB23。
- 另開**獨立 MASTER code-only 修復 PR**，保留需要的安全負向測試、每題唯一 QID、跨題 row immutability、WebP SHA、來源 revision、公告、未審查不得發布。不可為綠燈直接刪測試、取消必要 checks、設 trust true、或改 main。

**P0-B：PR185 正式 source QA 收件**。重新執行有效且能比對最新 QA base 的正反向 CI；確認原本成功的 source G1/G2/G3、2×3 表、205 JSON/SQLite parity、其他 204 row 未改。只有各必要正規 checks 合格才正常 merge **官方 QA 分支**，絕不能直接 merge student approved/main。

**P0-C：有條件進入發布鏈**。等真正不同執行 Session 的 ROLE E 憑證經獨立核實，才接受該題 trust；將真正 publisher-emitted 私有資料交 ROLE D 8 尺寸× Light/Dark 16 次；全部 G0–G10、approved PR、受保護 main 合併和 Pages verify_live 都通過後，才能宣稱新 LIVE。E12 的外部原始盲解／身分認證缺口仍另線處理，不阻塞 MB23 的 source 工作。

**RETURN**：新的 taskId/CLAIM、修復 PR/HEAD、每個真正 CI run 結論、MB23 來源 QA merge SHA（若成功）、外部缺證分類、下一個明確 Owner。不得假造其他角色已被喚醒。

---

## 2. PROMPT → ROLE E（在 MASTER source QA merge 後）

你是獨立於 ROLE C 作者／ROLE A 來源／MASTER 的 ROLE E；先讀 Issue #36 現有 MB23 數學內容審查 [#6623807531](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6623807531) 和最新 PR185 source issuer SHA。不可將作者自檢或 GitHub 同一使用者自動等同「不同模型執行主體」。

核對真正最新 canonical：原圖 `2639fb...d51`，QREV `945457...fd4`，完整 2×3 表格 6 個儲存格，選項 32000/33000/34000/35000，官方 B，方程 `2x - 3000 = 1.8(x+2000)`、x=33000、兩案合計=63000。ROLE C [PR143](https://github.com/homelux-huang/7581707/pull/143) frozen `teachingCanonicalSha256=13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6`，無真實修稿必要就保留 digest。

先比對之前 E 實質筆記的 sourceRevision/表格/內容 SHA 是否全相同，若完全一致則保留原實質審查，不重複佯稱「新獨立盲解」。G6 原始 answer-naive 模型 prompt/first response/provider IDs/時間與 G7 作者及 reviewer 身分真正可驗證前，分類 HOLD；不得自簽受信任 MAIN receipt。RETURN 原始 SHA、缺件與下責任者。

---

## 3. PROMPT → ROLE C（立即唯讀，無需重寫）

你是 115 年 ROLE C 教學作者；只讀確認 [PR143](https://github.com/homelux-huang/7581707/pull/143) Q23 原題、四選項、2×3 來源表與原稿 digest `13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6`。核對 ROLE A PR185 原始 G2 修復和 source revision `9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4`。

如原稿含教師／國小雙層解說、每一選項 A–D、公式用途、逐步代入、單位、驗算且數學沒有變，**只 RETURN digests frozen**，不要為了新版本號重寫教學；若有真正來源差異，CLAIM 獨立作者檔案後以最小修改與新 SHA 交回 E。不得當 E 或宣布 LIVE。

---

## 4. PROMPT → ROLE D（達標才執行）

你是正式 V4 UI 負責 ROLE D。沿用唯一 V4 網站，不重建 UI。先刷新 MASTER 確認的 protected-main native publisher candidate，並驗證 Q23 來源、教學、E trust issuer 的相同 SHA。原 Q23 舊 PR150 16/16 是 QA-only，**不得當正式 emitted 16/16**。

在真實憑證和 publisher emitted 學生資料滿足後，用原始 WebP `2639fb...d51`、官方 B、完整 2×3 價目表、四選項、教師／白話雙層解說、逐步算式，進行 8 種視窗寬度 × Light/Dark 共 16 次真實 Chromium（不攔截或偽造返回資料）；驗證每張截圖 SHA、載圖 decode、作答/解析/錯題本/換題、testedTeachingDigest。若前置仍 HOLD，僅輸出阻塞、不宣稱 16/16。RETURN 真實 CI／證據和下一 Owner。

---

## 5. PROMPT → ROLE A（下一個來源題 MB20，需新 CLAIM）

你是 ROLE A；前一題 MB23 **CLAIM 已 RETURN 並釋出租約**，不得復用舊 lease 或直接覆蓋 PR185 SQLite。下一個建議 QID `115-00-MB-20`。先讀最新 MASTER、QA、MB23 是否合併；若尚未合併，任何 MB20 source-DB 候選須採獨立堆疊分支並註明依賴，避免舊 QA DB 覆蓋新 Q23。

已存在原始來源 v5 [PR152](https://github.com/homelux-huang/7581707/pull/152)：Q20 原修補 WebP SHA256 `f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf`，完整圖（四）B 點及圖說；舊 v2 缺下緣。獨立 ROLE E 原始逐像素 QA [PR156](https://github.com/homelux-huang/7581707/pull/156) + CI 已存在；**115 manifest 舊欄 `visualDefectHistory.repairStatus=generated_pending_independent_visual_recheck`，必須核真 E 證據後由 A／MASTER 明確調和，不能假改已獨立合格**。

既有 ROLE C 原教學 digest `2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d`；官方答案 A、正弦定理 `AC=100 sin75°/sin45°=50(√3+1)` 公尺。先核最新有效租約後僅單 QID CLAIM；同步驗證 205 JSON/SQLite、manifest與圖形 v5 SHA、官方公告與答案、其他 204 row 全不變、來源正反向 CI。需要真正不同 E review / D emitted 16/16 仍不得自補。每題 RETURN 後才接 MB24／MB25。

---

## 6. 全角色統一 RETURN 格式

```yaml
taskId: ...
role: MASTER | A | B | C | D | E | EXTERNAL
claimIssue36: https://github.com/homelux-huang/7581707/issues/36#issuecomment-...
qid: 115-00-MB-23
baseSha: ...
headSha: ...
prUrl: ...
sourceRevision: ...
webpSha256: ...
originalTableSha256: ...
teachingCanonicalSha256: ...
g2IssuerSha256: ...
g3IssuerSha256: ...
officialAnswerAndNotice: ...
sqliteSha256: ...
canonicalRows: 205
other204RowsUnchanged: true | false | NOT_TESTED
ciRuns: [...]
independentEPrincipal: VERIFIED | UNVERIFIED
formalPublisherEmittedChromium16: PASS | FAIL | NOT_RUN
ready: false
liveVerified: false
remainingBlockers: [...]
nextOwner: ...
leaseStatus: RELEASED | ACTIVE
```

**硬規則：** 不要求真人教師簽核；但仍保留 AI 作者／不同執行審查者分離與真實證據、所有原圖及官答核證、保護 main/Pages、正反向 CI；一題真實通過才一題增量上線，不等全 410 題，也不把 source-only 成功誤記為學生 LIVE。
