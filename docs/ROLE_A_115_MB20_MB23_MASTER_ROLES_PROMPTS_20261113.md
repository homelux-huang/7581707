# 7581707｜ROLE A 115 MB20／MB23 → MASTER／C／E／D／外部 G6 執行者｜2026-11-13 交接 PROMPT

> 本文件是**可複製到各角色不同 ChatGPT Session 的指令**，不是自動喚醒 Session、MASTER 發布授權，或獨立 E 執行證明。先檢查 Issue #36 最新 CLAIM/RETURN／PR HEAD／CI，任何舊 SHA 均須重新確認。
>
> Repo: https://github.com/homelux-huang/7581707
>
> 唯一正式 V4: https://homelux-huang.github.io/7581707/sudu/v4-115-multisubject-review-demo.html
>
> 工作優先順序：114／115 年、逐題 READY→LIVE，不等 410 題；104～113 新增工作仍暫停。不重新建站、不重裁合格原圖、不重寫正確教學、不自行簽 TRUST、不繞過 protected main。

## A. 已完成事實與阻塞（全角色共用）

| 項目 | 可核對證據 | 意義 |
|---|---|---|
| 114 E11 來源 | PR #179 合併 official QA | 尚非 LIVE |
| 115 MB21 來源 | PR #181 合併 official QA | 尚非 LIVE |
| 115 MB22 來源 | PR #182 合併 official QA | 尚非 LIVE |
| 115 MB23 來源 | [PR #185](https://github.com/homelux-huang/7581707/pull/185)／[Issue RETURN #6768837742](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6768837742)／[Actions #42827387639](https://github.com/homelux-huang/7581707/actions/runs/42827387639) SUCCESS | 來源 G1/G2/G3、完整 **2 資料列×3 欄價目表**、205 JSON/SQLite，**未合併** |
| 115 MB20 來源 | [PR #187](https://github.com/homelux-huang/7581707/pull/187)／[Actions #42829373105](https://github.com/homelux-huang/7581707/actions/runs/42829373105) SUCCESS／[Actions #42829744378](https://github.com/homelux-huang/7581707/actions/runs/42829744378) SUCCESS | 完整原像素 v5 圖（四），修正文句與四選項、正式官答 A、205 SQLite，**堆疊於 #185 且未合併** |
| Current QA / protected main | QA `15108e8e657d070724889f1df3d3a6ae6da96d97`, main `5546a603abfe0af2e62c0e5f63f775be0bfb24cf`（2026-11-13 重新確認） | 先刷新才能合併 |
| 114 E12 G6/G7 外部證據 | [MASTER PR #188](https://github.com/homelux-huang/7581707/pull/188) 外部提供者 harness；Issue [#6785033142](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6785033142) | 真實外部 G6 模型首次答覆、獨立身分仍 UNVERIFIED；不可用無真實 provider response 的舊嘗試冒充 |
| 舊 E11／MB21 PR-specific checks | E11 #42826162719、MB21 #42826162749 曾在新題 PR 誤報紅燈 | 兩測試使用舊固定檔案白名單／基準，不應直接以它們判定新題；需 MASTER 分離保留原斷言與最新 per-Q 增量驗收 |

### 必須維持的資料鎖定

- **115 MB23**：原始單題 WebP SHA256 `2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51`；table-inclusive revision `9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4`；官答 **B = 33000 元**，教學 digest `13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6`；來源 PR185 final known HEAD `24f8962b7fb51a8baa6f111abb1a7414a4b26420`。
- **115 MB20**：原始完整 v5 WebP SHA256 `f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf`；page 7 crop `[90,469,1310,902]` **1220×433**，舊 v2 僅 1220×386 少 47px／B 點／圖說；來源 revision `2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c`；官答 **A = 50(√3＋1) 公尺**；教學 digest `2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d`。完整 source G1 原像素與 ROLE E 獨立影像 QA [PR156](https://github.com/homelux-huang/7581707/pull/156) 同源；此**不是正式 E teaching trust receipt**。
- **MB20 橋接生成後**：bank SHA256 `b66c12558421399641d1ce483b0228684540c07ac3b39873e9876363573ec814`；SQLite `67f23da3358d27a8a439dbcdbddceb33d21754d6d37adfe4a0fbcc892aad8bb3`；manifest `5b37bd1e8e4e31df8ea3f4e1f94c1bacf40c584cee7f2a3fa44510f394a64c4e`。MB20 以 MB23 為 parent 僅修 1 QID，其他 204 題完整 JSON／SQLite row values 不變；204 個其他 manifest items 不變。G2 issuer SHA `c6f33db05c38e9fdb3abc682d27cf8f21550dbd638c84adafd396a2bf3f491e2`，G3 issuer SHA `67b554b4b1f5543d40ca0e455a209554a94792816916415002ee46d4fe59202c`。
- ROLE A source-only SOURCE_PASS 不是學生 TRUST／READY／LIVE；正式 E/G6/G7、native publisher-emitted D 8×2、MASTER G0–G10 和 Pages verify_live 仍待。

---

## PROMPT 1｜交給 MASTER：P0 合併阻塞＋可信發布鏈

你是 `homelux-huang/7581707` 的唯一 MASTER 主指揮、跨 PR 整合驗收與正式發布裁決者。**立即讀 Issue #36 最新 MASTER / A～E RETURN、PR #185、#187，及最新 protected main/official QA refs。**不得重建網站、改第二套台帳、批次 READY 或將 source-only CI 當成學生上線。

1. **先解現有 E11／MB21 退休式 PR-specific CI 錯誤**：這些測試以歷史 PR 的固定檔案白名單／舊 205 bank 為基準，在 MB22、MB23 後會誤判正常增量。保留原安全負向斷言與 true QID-only immutable checks。用獨立 MASTER code-only PR 讓歷史一次性測試只適用原本 branch/原 HEAD，並讓增量 PR 按最新 QA parent 驗證唯一 QID、其他 204 row / SHA 不變。禁止刪掉必要 gate 或偽造 pass。
2. **先處理 [PR185](https://github.com/homelux-huang/7581707/pull/185) MB23**：核其最終 HEAD、完整 2×3 價目表、WebP/G2/G3/官答、其他 204 題保持不變、205 JSON／14-column SQLite parity、專屬 Actions #42827387639 結果；修正 general required CI 的路由後，依分支保護與獨立 code review **正常 merge 至 official QA only**，不是 protected main 或 approved。
3. **後處理 [PR187](https://github.com/homelux-huang/7581707/pull/187) MB20**：它堆疊於 PR185。請先安全確認 #185 新 QA HEAD，再 retarget/rebase #187（避免重放 #185 全部變更，不能 force 覆蓋其他 Session）。核獨立 E 原 v5 像素 QA PR156，官方頁原像素差為 0，舊 v2 缺 47px；核唯一 Q20 JSON/SQLite、204 其餘 row 原值不變。真實 CI/審查過後僅合併 official QA。
4. 每題來源 QA 完成後，交真正不同執行 Session 的 ROLE E 核對實際 C digest+來源 revision+官答（包括 G6/G7 provider 原始證據）；只有 verified principal 及可信 receipt 才接受 trust。交 ROLE D 用**真正 publisher-emitted**資料跑 Chromium 8 viewport × Light/Dark（16 次，無假截圖、無 HTTP mock/intercept）。全 G0–G10 真實通過後，才建立逐題 approved PR→受保護 main→Pages build/deploy/verify_live。**不得等待 410 題全部完成**。
5. 114 E12 外部 G6 使用 active-provider path [PR188](https://github.com/homelux-huang/7581707/pull/188) 的安全 operator handoff；既有 GitHub Models 無真實模型首次 response，不可重跑舊 provider、不可使用已知 C 答案冒充盲解。

完成每項後以 Issue #36 逐題 RETURN：taskId、owner、CLAIM、base/head SHA、PR、真實 CI run、merge SHA、剩餘 G0–G10 阻塞、下一個 owner、租約釋出。**未合併／未發佈要寫清楚**。

## PROMPT 2｜交給 ROLE E：MB23／MB20 異 Session 獨立稽核

你是不同於 ROLE C 教學作者與 ROLE A 來源工程師的 ROLE E。先讀 Issue #36 最新 MASTER 指令、115 MB23 PR185、115 MB20 PR187（後者依賴前者）、來源 G1/G2/G3 和 frozen C PR118/143。不得使用本 Session 身分或 GitHub 相同帳號作為「不同執行環境」的假證明。

MB23 檢查原圖 SHA `2639fb...d51`、3 欄 2 筆費用表、官答 B：`2x−3000=1.8(x+2000)` 得 `x=33000`，雙方 63000；C frozen digest `13fa628...c7c6`。MB20 檢查原像素 v5 SHA `f9e68d...cdf`、舊 v2 缺 B 點、完整 4 選項與官答 A：`AC=100sin75°/sin45°=50(√3＋1)` 公尺；C frozen digest `2b68e16...9362d`。如先前真實 E 內容筆記 SHA 完全匹配，保留可驗證原證據，不強行產生「新盲解」。

對每題驗 QID、sourceRevision、原圖 SHA、official final / notice、C 教學 bytes SHA、A/B/C/D 高職＋國小雙層、計算用途／代入／單位／驗算。另分別驗證真正外部首次答覆原始 prompt、response、provider model/response ID、時間、不可重播、B/C 與 E reviewer 主體分離；無法證明則明確記 `UNVERIFIED / HOLD`，不得自動註冊 trusted-main receipt 或宣布 student READY。逐題向 MASTER RETURN 含失敗原因與原始證據鏈。

## PROMPT 3｜交給 ROLE C：MB20／MB23 SHA 凍結（唯讀）

你是 115 年 ROLE C 教學作者。讀最新 official QA、A PR185（MB23）、PR187（MB20）及自己的 PR118/143。確認兩題題幹、4 個選項、原圖 SHA、sourceRevision 及既有教學 digest 全部一致。

- MB23：原 2×3 旅遊價目表，其中**只有一人減 3000／只有一人打八折**，答案 B=33000 元，C teaching SHA `13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6`。
- MB20：正弦定理、完整圖（四）原 v5、逆向驗算 AB=100 公尺，答案 A，C teaching SHA `2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d`。

如果現稿已正確，**唯讀回報 freeze、不要為版本號重寫教學或變造 digest**；若實際源差異影響教學，另 CLAIM 專屬作者檔、僅最小修正，並通知 E/D 原 digest 失效。不得自評成不同 E，亦不得宣布 LIVE。

## PROMPT 4｜交給 ROLE D：正式 V4 publisher-emitted 8×2

你是 ROLE D，維持正式 V4 唯一學生頁，不建立新站。最新 MASTER 還未確認 trusted E、正式 approved-emitted 資料前，**只執行 preflight/負向 HOLD，不能用 QA-only 歷史 16/16 假冒正式 PASS**。

若 MASTER 已真的核入最新 MB23、MB20 original source、C frozen teaching digest、不同 Session E trusted receipt，請使用**正式 private publisher emitted、不得 HTTP interception/mock**的學生資料，逐題跑 Chromium 8 種 viewport × Light/Dark = 16 種；逐圖驗原 WebP（MB23 2×3 表完整、MB20 v5 B 點與圖四完整）、四選項、答案、教師＋白話雙層、計算逐步、無計算不顯示卡、字體／RWD／暗亮模式、答錯與錯題本、testedTeachingDigest == 真實內容 SHA。保存 screenshot SHA、CI run、source revision／lesson digest／UI receipt。若任何 E/provider/approved gate 未通過，保持 `HOLD`，報 MASTER 缺件而非放寬。

## PROMPT 5｜交給獨立 G6 操作員（114 E12 專用）

你是與 B/C 教學作者、ROLE E、MASTER 不同的真正外部 provider 執行操作員。先閱讀 MASTER 已建立 [PR188 外部提供者一次性 harness](https://github.com/homelux-huang/7581707/pull/188) 及 [E12 正式 operator handoff](https://github.com/homelux-huang/7581707/blob/5ccc872cb361891b92c300f5d0a587f457aff031/docs/MASTER_E12_G6_G7_ACTIVE_PROVIDER_OPERATOR_HANDOFF_20261111.md)。

在無歷史對話、無記憶、無答題提示的**真正獨立模型環境**只傳官方 G2 題幹與四選項，不得提供答案 C、GitHub Issue、教學或舊盲解。以受限 GitHub Environment secret 安全供應有效 API 金鑰，不把金鑰放進 prompt、commit、log 或 artifacts。保留第一個原始 request/response bytes、SHA、provider response ID/model、UTC time、執行者可驗身分及防重播證據。只有第一筆真實模型答覆成功保存後才能揭露官答 G3；若 provider 無法運行則如實 `UNVERIFIED`，不能用先前模型在對話中的 C 答案補造。交不同安全 reviewer 審核，MASTER 才能裁 G6/G7。**不得自行設 TRUST/READY/LIVE**。

## PROMPT 6｜交給 ROLE A（MB24／MB25 下題資料工程）

你是 ROLE A，先讀本次 MB20 的新 source-only RETURN（Issue36）、PR185、PR187。除非 MASTER 明確另指令，下一批 `115-00-MB-24`，再 `115-00-MB-25`，每題單獨 CLAIM／RETURN。因 #187 仍堆疊 #185，**先查最新 QA 是否已合併二者及共用 115 SQLite 租約是否釋出**；不要用舊 QA binary 覆蓋 MB20／MB23。

讀原始 PR #157 等既有題目來源、原始單題 WebP、官答更正、ROLE C source revision + digest，以及 E 來源 G1/G2/G3；清除僅受影響 QID 的 OCR 汙染，圖表保留完整原像素，205 JSON/SQLite roundtrip 全表一致、其他 204 整個 row 不變，原 G1/G2/G3 SHA 和所有原始 WebP bytes 不變。使用真實 GitHub Actions/負向測試核證，D/E/TRUST/READY/Pages 仍待不同 owner。每題取得 exact-head CI 後 RETURN，再處理下一題。

---

## 全角色統一 RETURN 格式

```yaml
taskId: ...
role: A | B | C | D | E | MASTER | EXTERNAL
claimIssue36: https://github.com/homelux-huang/7581707/issues/36#issuecomment-...
qid: ...
baseSha: ...
headSha: ...
pr: ...
status: SOURCE_ONLY | QA_MERGED | E_HOLD | UI_HOLD | READY | LIVE_VERIFIED
sourceRevision: ...
originalWebpSha256: ...
originalTableSha256: ...
officialAnswerAndNotice: ...
teachingCanonicalSha256: ...
g2IssuerSha256: ...
g3IssuerSha256: ...
sqliteSha256: ...
canonicalRows: 205
other204Unchanged: true | false | NOT_TESTED
ciRuns: [...]
externalG6FirstResponse: VERIFIED | UNVERIFIED
trustedDistinctEPrincipal: VERIFIED | UNVERIFIED
nativePublisherEmittedUiQa16: PASS | FAIL | NOT_RUN
pagesVerifyLive: PASS | FAIL | NOT_RUN
remainingBlockers: [...]
nextOwner: ...
leaseStatus: RELEASED | ACTIVE
```

### 安全底線

「高職老師」僅是教學角度，無真人教師簽章前置；**不同 AI 作者／審查者與外部 G6 真實隔離證據仍不可省**。原 WebP、官方更正、教師+國小完整解說、計算驗證、正反向 CI、同 SHA 真正 Chromium 與 protected main/Pages 合併均不可跳過。不會因 source-only PR SUCCESS 而自動把未核證題目標成正式學生 LIVE。
