# 【7581707｜ROLE A｜410 候選題來源唯讀稽核 RETURN／MB25 後續派工｜2026-11-14】

> **本文件為 GitHub Actions 真實唯讀結果與供各角色 Session 複製的 PROMPT。不是 MB24／MB25 共用 JSON／SQLite 寫入租約，不是正式 G2/G3 admission、E trusted review、READY 或 LIVE。**
>
> GitHub repo：https://github.com/homelux-huang/7581707
>
> MASTER Issue：https://github.com/homelux-huang/7581707/issues/36
>
> 唯一正式學生頁：https://homelux-huang.github.io/7581707/sudu/v4-115-multisubject-review-demo.html

## 1. 真實基準、租約與執行證據

| 欄位 | 本輪已核資料 |
|---|---|
| audit taskId | `A-114115-MB25-E03-ECON34-READONLY-BASELINE-AUDIT-20261114-01` |
| 唯讀租約 | [Issue #36 CLAIM #6876411326](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6876411326)，只允許新的 audit Python／workflow／Markdown |
| protected main | `0bc2b05ada43ef02983d56fc45ec3448189a318b` |
| official source QA HEAD | `4e365a75ed98e73223987d81041693a476196881` |
| 唯讀來源 | PR [#157](https://github.com/homelux-huang/7581707/pull/157)，HEAD `24decc38c6e16e2a22b6204207db1922ce1a1ee8` |
| 真實 Actions | [#43589104752](https://github.com/homelux-huang/7581707/actions/runs/43589104752) job `132429843665` **SUCCESS** |
| Actions artifact | [#14112041062](https://github.com/homelux-huang/7581707/actions/runs/43589104752/artifacts/14112041062)：`role-a-114115-mb25-gap-readonly-report` |
| 已知 active 115 shared DB lease | [MB24 claim #6873884674](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6873884674)，**仍未看到 RETURN/RELEASE**。本輪沒有向共享 115 資料庫寫任何資料 |
| 本輪範圍 | 完全唯讀；所有 114/115 `questions.json`、`question-bank.sqlite3`、`webp-manifest.json`、`inventory.json`、全部原始 WebP、approved、C 教學、E、D、TRUST、main、Pages 維持不變 |

第一次 CI #43588976621 套用不正確的 115 年 14 欄假設到 114 年，因此 FAIL CLOSED；第二次 #43589025139 查明 **114 真正 7 欄**；第三次 #43589060894 識別 `correctionOverlay=null` 的狀態處理錯誤；修正唯讀稽核程式後 **最終 CI #43589104752 SUCCESS**，不可把早先的 red 宣稱成功。

## 2. 真正 410 候選紀錄結構查核

| 指標 | 114 年 | 115 年 |
|---|---:|---:|
| JSON source QIDs | 205 | 205 |
| manifest QIDs | 205 | 205 |
| SQLite rows | 205 | 205 |
| SQLite columns | **7** | **14** |
| JSON payload 逐筆與 SQLite 符合（含每筆 SHA） | 205/205 | 205/205 |
| SQLite `PRAGMA integrity_check` | ok | ok |
| inventory SHA 綁定 JSON / SQLite | PASS | PASS |
| `questionVerified=true` | 3 | 5 |
| `answerVerified=true` | 2 | 81 |
| manifest `qaStatus=PASS` | 35 | 143 |

固定 410 題只是**候選覆蓋與資料庫一致性**，不代表 410 題已完成官方題目、答案、獨立 AI E、D UI、學生 READY。資料庫原始 SHA：
- 114 bank `3818a0e8b9e12c73e62e4e2ed967e7802ca13b2ad151286eec41555ab6f50c44`，SQLite `4a2e62ff2dc32f8da66e7f0e3dc8e89885b294bfaa142af446f78c11f16f61b7`。
- 115 bank `b66c12558421399641d1ce483b0228684540c07ac3b39873e9876363573ec814`，SQLite `41046eebb0b228538616b1f19c9cabbd9b8d9e19808ae34fc9703f23fd5adc17`。

## 3. MB24、MB25 真實原圖／答案／G2 差異

### 115-00-MB-24 — 原始來源已有，正式共享 admission **由另一 WORK ROLE A 持有**

- 原始單題 WebP SHA256 `c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb`，PR157 GitBlob `cfe5c8eeaf4496d5d98856f96a2c310186ef5893`；1220×478，官方 p8 原像素 `[90,614,1310,1092]` **差 0 px**。原始圖片不用重裁、重 OCR。
- 原始 A source-stage GitBlob `88faf4ee767b20c15db603e91aa250bc59eba84c`，原 ROLE C source revision `9357c0f8f30ab131f8450c8a9b45d34942fdd8207c6aac688f4f3847a55e8267`，C digest `317fe1d731f29e9634ec17f0fc1dc5c308b804de5759991a005f94f81bbffd06`。
- 正確完整原題分式：`A=110/r`；`B=log10(3)/log10(1+r/100)`。(r=8)：向上進位 (C=14)、(D=15)，故 **選項 C：D=C+1**；115 MathB 官方原答案 C，紙本無更正。
- QA base 時 `questionVerified=false`、canonical **尚不等於既有 A G2 正式完整文字**；`answerVerified=true`、image manifest PASS。不要與另一 Session 共用寫檔，等待原 MB24 Work OWNER 實際 RETURN／RELEASE、真實正反向 G1/G2/G3、205/14 SQLite 題號範圍驗收和 MASTER 合併。
  
### 115-00-MB-25 — 等 MB24 釋出後**下一個唯一來源 admission**

- 原始 WebP SHA256 `92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896`；PR157 GitBlob `10adb24ab36c35bd86b63c0d3ab4cb83b757393f`；官方 p8 原像素 `[90,1102,1310,1557]`、1220×455 **像素差 0**。
- 原始 A source-stage GitBlob `cf1ef0d369e3aced81886a518b47cdeddd4ad175`；原始 ROLE A G2 `sudu/data/processed/115/review-evidence/115-00-MB-25-image-transcription-correction-20261024.json` GitBlob `6228cca369d369c183cb578519c383257f579f8b`，與 PR157 原始 source 數據一致。
- 原 ROLE C sourceRevision `8b29dffa0c37abd1b37989878a9f8d34392ba71a04017ca1591d6fa45ec9cb6f`；C authored canonical teaching digest `a860b08a6f5b76fe1331dc4204a46a3135e511449d9b6004cc4f99be020e4d32`，**來源修正不能自行重寫 C 教學**。
- QA 現況：`questionVerified=false`、`answerVerified=true`；原始完整題目 `P=(h,7)` 與直線 L 距離 `√2`（不是 2），圓 `x²−8x+(y−7)²=a`；目前 D 選項錯帶圖（七）、【以下空白】與頁尾 `-8-`。乾淨 A-D 為 `－59`、`－16`、`－10`、`10`。
- 官方原答案 **C**，紙本 `no_objection_submitted`，配方得 `(x−4)²+(y−7)²=a+16=2`，`h=4, a=-14, h+a=-10`。
- 正式來源新版本必須更新 G2/G3 及 `questionRevision` / 14-column SQLite 單筆，205/205 roundtrip、其他 204 JSON semantic objects / entire SQLite row tuples / whole manifest 不變；真實 wrong-image / wrong-answer / wrong-announcement / OCR-intrusion / duplicate-QID 負向測試。此處只做唯讀，不暗稱 G2/G3 admission PASS。
  
## 4. 已合官方 QA 的來源版本唯讀核對

以下 QID source 資料都保有 `questionVerified=true`、`answerVerified=true`，manifest PASS、官答與既有 WebP SHA 對應：
- 114 E11：原圖 `ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0`，官答 A，revision `646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036`。
- 114 E12：原圖 `99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60`，官答 C，revision `0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec`。
- 115 MB20：原 v5 `f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf`，官答 A，revision `2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c`。
- 115 MB21：`b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693`，官答 A，revision `817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9`。
- 115 MB22：`3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55`，官答 B，revision `7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17`。
- 115 MB23：`2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51`，官答 B，revision `9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4`，原完整 2 資料列×3 欄表已在 QA。

此節只核對此版 QA 的來源與本次真實 205 bank/DB parity，**未取代獨立 E／學生正式發布**。

## 5. 其他 P2 來源缺口（真正從 115 205 bank 查得）

| QID | 狀態 | 原圖 SHA256 | 原始待查問題 |
|---|---|---|---|
| `115-00-E-03` | questionVerified=false；answerVerified=false；manifest PASS | `16c8e37d3f169f0488398844030bf4922c4f4639633ee7a4d9a9af83466d8ebd` | 舊 `reused_preexisting_demo_crop_coordinates`；題目含 `treats all her students ...`，現有 A-D carelessly / equally / instantly / silently，官答及更正必須**再查官方原圖**；不要只依文義宣告來源 PASS |
| `115-09-2-34` | questionVerified=false；answerVerified=false；manifest PASS | `5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02` | 經濟寡占 AI 伺服器題；`single_question_crop_not_yet_generated` 為歷史 issues，不能據此斷言當前圖檔不存在，先實際對照原官方卷與 manifest、共用材料、官答／公告 |

另一優先可調查 114 英文 E07／E08／E09：ROLE B [Issue #36 RETURN #6876440075](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6876440075)、[#6876440551](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6876440551)、[#6876441053](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6876441053) 已回報作者 SHA 與 source 尚未完整驗證；由 MASTER 排優先，來源與 B 教學不可互相搶寫。

---

## 6. 可複製 PROMPT — 下一個 ROLE A（MB25，等待唯一前置）

你是 7581707 的獨立 ROLE A 來源工程 Session，僅處理 **115-00-MB-25** 官方原圖／題幹選項／官答／公告／205-row JSON+14-column SQLite。

**先讀 Issue #36 active MB24 source lease #6873884674**。若尚未有真的 MB24 RETURN 與明確釋放共用 `questions.json`、`question-bank.sqlite3`、`inventory.json`，**不得 CLAIM 或寫入 MB25，也不得從舊 QA binary 建分支覆蓋 MB24**。先唯讀核 PR157 G1/G2/G3，資料見本文件第 3 節；請求 MASTER／MB24 owner 完成 RETURN 後再順序開工。

待條件達成：先刷新最新 official QA HEAD／MASTER 指令、原 MB24 最新正式 PR/CI；從已接納 MB24 的最新 QA 建新的單題隔離分支，於 Issue #36 預先單獨 CLAIM MB25，並以 Draft PR 交付。**原始 WebP SHA `92f1b7...3896` 及 1220×455 完全保留，不重新裁圖或 OCR。** 乾淨 Q25 選項 `－59／－16／－10／10`，原根號 `√2`，官方答案 C；原 C lesson sourceRevision `8b29dffa0c37abd1b37989878a9f8d34392ba71a04017ca1591d6fa45ec9cb6f`。跑真正 protected native publisher G1/G2/G3 正／負驗收、14-column SQLite 205/205 parity 與其他 204 row 值全不變、完整原 WebP/manifest SHA、official correction 范圍；只更改 Q25 與必要 issuer/evidence paths，**不得修改其他題或發佈**。完成後即 Issue #36 RETURN 完整 SHA／PR／HEAD／CI／下一 owner 並釋出租約。

## 7. 可複製 PROMPT — MASTER／下一個 A 調查 E03／經濟34

你是 MASTER 來源派工協調者，請將 **115-00-E-03** 與 **115-09-2-34** 分別安排為**唯讀 gap-check** 任務，不取得任何 MB24/MB25 共享資料庫租約。根據本文件第 5 節，檢查官方原題頁／單題 WebP 實際像素，題號／完整 A–D／跨頁共用材料，官方答案及更正公告、manifest issue history、原 C 作者是否存在同 revision。若找到真缺口，待來源共用資料庫空閒後**逐題獨立 CLAIM**，產生單 QID source G2/G3、205 JSON/SQLite 守恆、真正 CI 證據後 RETURN；如果來源早已完成請只修復狀態證據，不新建相同圖像、不盲改 approved/main。

## 8. 可複製 PROMPT — ROLE E／ROLE D

ROLE E：對真正已經 source G1/G2/G3 admission 的 114 E11／115 MB20–23 逐題獨立檢查 A–D 教學和原圖／官答，依法合 sourceRevision 與 C/B digest；真正 G6 需 provider 原始無答案首次 request/response 與可信不同執行人員，缺項維持 `G6_G7_HOLD`。不得用本 A 的 source-only audit 替代 E principal 身分。

ROLE D：正式 Publisher-emitted data 以及真正可信 E / G6 證據入庫前，僅做 V4 唯讀／非正式 UI precheck；拿到真正 emitter SHA 才在 8 viewport × light/dark 16 次 Chromium 驗證 QID、圖片、答題與教學 bytes。不得在無發行資料下把 QA-only 畫面算作正式 G8。

## 9. RETURN／發行邊界

```yaml
taskId: A-114115-MB25-E03-ECON34-READONLY-BASELINE-AUDIT-20261114-01
role: A
sourceMode: READONLY
claim: https://github.com/homelux-huang/7581707/issues/36#issuecomment-6876411326
questionIds: [115-00-MB-24, 115-00-MB-25, 115-00-E-03, 115-09-2-34]
officialQaBase: 4e365a75ed98e73223987d81041693a476196881
mainSha: 0bc2b05ada43ef02983d56fc45ec3448189a318b
ciRun: 43589104752
ciConclusion: success
artifactId: 14112041062
canonical114Rows: 205
canonical115Rows: 205
sqlite114Columns: 7
sqlite115Columns: 14
sqliteJsonParity: "205/205 each"
other204Mutated: false
newSourceG2G3Admission: false
independentETrust: UNVERIFIED
formalUi16: NOT_RUN
studentReady: false
studentLive: false
activeForeignLease: MB24-6873884674
nextOwner: MASTER / existing MB24 ROLE A; then new MB25 ROLE A
leaseStatus: READONLY_CODE_ONLY_RELEASED
```

**本輪不碰原始資料庫、獨立 E 身分、protected trust 或正式學生頁，不宣稱 G2/G3 新驗收 PASS。**
