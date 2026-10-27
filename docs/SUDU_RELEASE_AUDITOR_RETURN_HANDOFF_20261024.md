# 7581707｜原 Session 修復返還｜獨立品質驗收與正式發布裁決請求

> 2026-10-24（台灣）｜**NO RELEASE / NO DEPLOY**。此檔是本批完成事項與剩餘阻塞交接，不是全部 104～115 年、128 題教學或 V4 平台已完成的宣稱。正式 GO/NO-GO 由獨立 QA／正式發布 Session 裁定。

## A. GitHub 唯一版本及安全權限

- Repository：https://github.com/homelux-huang/7581707
- QA 分支：qa/114-115-official-visual-review；**本檔寫入前 HEAD：d4b020e990a017ba3e8ba452fac5261cfbae54aa**。寫入後必須重新讀取 HEAD。
- main：57d766e841235b937babf3fe10a8ff44606c7c41（本輪未修改）。
- 固定 128 題教學原分支：draft/preview-128-explanations-20261023；HEAD c4cdb10ea61f70e0184f0a078963ebb537a9cc99（本輪未修改）。
- Draft PR #3：https://github.com/homelux-huang/7581707/pull/3 （OPEN／Draft／未合併）。
- 英文三題來源 PR #21：https://github.com/homelux-huang/7581707/pull/21 （OPEN／未合併，head 9944759e339ef2d3c002042798f7fe696d861d96）。
- 114 年更正 Gate PR #22：https://github.com/homelux-huang/7581707/pull/22 （OPEN／未合併，head cccea517f701f2f667cc450cd7a82446f487579e）。
- 本輪僅在指定 QA 分支提交；未合併 main、未更新 approved、未部署、未碰學生歷史資料，沒有 Force Push。
- 新 QA reviewer 均為 ChatGPT assistant、independentHumanReview=false；**不是獨立真人教師審查**。

## B. 最新完整題號稽核（105～115；104 單列）

最新跨年度 source coverage CI：https://github.com/homelux-huang/7581707/actions/runs/40109241140 **SUCCESS**；最終報告位於 sudu/data/processed/104-115-QUESTION_ID_GAPS_20261024.json。

| 項目 | 已核實 |
|---|---:|
| 題庫候選 | 2,249 |
| 有題號／SHA 連結 WebP 候選 | 2,249 |
| 缺少 WebP 候選 | 0 |
| **G1 圖片目視 PASS** | **275 / 2,249 = 12.23%** |
| 仍待單題 G1 | 1,974 |
| G2 題幹／四選項／公式文字 QA | 29 |
| G3 官方最終答案證據（全部為既有） | 81 |
| G5 隔離 SQLite | 11 / 11 年 PASS |
| 年度 G6 READY | 0 / 11 年 |

| 年度 | 題庫/WebP | G1 | G2 | G3 | G5 | G6 |
|---|---|---:|---:|---:|---|---|
| 105 | 204/204 | 7 | 0 | 0 | PASS | NO RELEASE |
| 106 | 204/204 | 23 | 13 | 0 | PASS | NO RELEASE |
| 107 | 204/204 | 21 | 7 | 0 | PASS | NO RELEASE |
| 108 | 204/204 | 26 | 7 | 0 | PASS | NO RELEASE |
| 109 | 204/204 | 0 | 0 | 0 | PASS | NO RELEASE |
| 110 | 204/204 | 0 | 0 | 0 | PASS | NO RELEASE |
| 111 | 205/205 | 10 | 0 | 0 | PASS | NO RELEASE |
| 112 | 205/205 | 0 | 0 | 0 | PASS | NO RELEASE |
| 113 | 205/205 | 10 | 0 | 0 | PASS | NO RELEASE |
| 114 | 205/205 | 35 | 1 | 0 | PASS | NO RELEASE |
| 115 | 205/205 | 143 | 1 | 81 | PASS | NO RELEASE |

104 年另外有 203 筆舊來源候選，官方真正題數、原 PDF SHA、processed／WebP／SQLite 均未核定，不可補成 205 或混入上表分母。110-09-1-80 假題號繼續隔離。

上一個稽核 #40109173124 曾因 114/115 inventory 與其他年度的 G1 欄位命名不同而 FAILED；已保留所有年度逐筆核對 assert，用精確既有欄位映射修復並於 #40109241140 成功，不是降低 Gate。

## C. 本輪實際修復、證據及 CI

### C1：106 國文 14～20，七張單題 + 三份共用閱讀／圖文

來源頁為 sudu/data/original/106/00-C/p004-93b8ec6eb3-v2-w1400-q66.webp；來源 SHA256 b7e6a32272b74c7788caa1f413919b46359589162096f72afe1050c56a4e8bc4。

本輪直接目視確認 v2 缺陷：17/18/19/20 題缺題號或開頭、15/16 混相鄰題邊界、共用文章含單題題幹、鯊魚共享圖上緣截斷。逐批 v3、v4 裁切修復，鯊魚右側圖 v5 重裁；保留 v2/v3/v4 歷史檔案和 SHA。再次逐張開啟，來源像素與 SHA、cropPixels 比對，並在本輪以 **ChatGPT assistant** reviewer 登錄七題 + 三份共用材料 G1，非外部人工。

- 證據：sudu/data/processed/106/qa-drafts/DIRECT_VISUAL_106_C14_20_AND_THREE_SHARED_20261024.json
- staging：scripts/stage_106_chinese_14_20_v3_boundary_previews.py、scripts/refine_106_c14_20_v4_source_edges.py、scripts/stage_106_c19_20_shark_shared_v5.py
- final：scripts/apply_106_c14_20_source_visual_g1_20261024.py
- CI v3 #40108267745、v4 #40108452982、鯊魚 v5 #40108575781、最終 G1/G5 [#40108709241](https://github.com/homelux-huang/7581707/actions/runs/40108709241)：全部 SUCCESS。
- 106 年 G1 16→23／204、共用素材 G1 1→4／4；**未增加官方 G3，保持 NO RELEASE。**

### C2：106 國文 16、17、19 題 G2 OCR／文字污染修正

清理 16 題第四選項混入後續閱讀文章、17 題原本未擷取占位及四選項、19 題鯊魚資訊的錯誤文字，對照官方原頁和最新 G1 WebP，保留舊 legacy/缺 raw 的 null/逐項 unified diff。

- 程式：scripts/repair_106_c16_c17_c19_source_text_g2_20261024.py
- 證據：sudu/data/processed/106/qa-drafts/TEXT_QA_106_C16_17_19_ORIGINAL_IMAGE_20261024.json
- [CI #40109064193](https://github.com/homelux-huang/7581707/actions/runs/40109064193) SUCCESS；G2 10→13，G1=23、G3=0；SQLite 11/11 PASS。
- **106 國文第14/15/18/20的 G2、全部 G3仍 BLOCKED**。不可因 G1 PASS 把答案、教學或年度標 READY。

### C3：108 數學 B 16、17 題 G2

直接核對來源頁3、既有 v4 WebP 與完整公式：16題五塗色區 A～E、8種顏色的排列選項；17題兩個 3×3 行列式及負號、變數、A～D。保留題目來源圖、legacy 占位、corrected、unified diff，不假造 OCR raw；不重裁既有 G1。

- 程式：scripts/repair_108_math_b16_17_source_text_g2_20261024.py
- 證據：sudu/data/processed/108/qa-drafts/TEXT_QA_108_MATH_B16_17_ORIGINAL_IMAGE_20261024.json
- [CI #40108932089](https://github.com/homelux-huang/7581707/actions/runs/40108932089) SUCCESS；108 G2 5→7、G1維持26、G3=0；G5 11/11 PASS。
- 108 數學B 11～15 先前 G2 已完成（#40105194575 SUCCESS），未重做。

### C4：114 英文 7/8/9 與專用更正公告 Gate 的純 dry-run

PR21/22 都尚未合併；114 英文來源 questions.json 與 manifest 的 Git blob 與最新 QA 基線相同。PR21 三題答案候選：114-00-E-07=A、114-00-E-08=D、114-00-E-09=D，相關五證書及官方公告需獨立最終複核。

- 本輪新增 workflow：.github/workflows/114-pr21-pr22-current-qa-compatibility-no-deploy.yml
- 將 PR21 SHA 9944759... 來源與 PR22 SHA cccea... publisher **在同個 CI 隔離測試環境** stage/check，執行原嚴格發布單元／反向測試。
- [CI #40108820782](https://github.com/homelux-huang/7581707/actions/runs/40108820782) **SUCCESS**：當前 QA 114核准數=0、PR21候選模擬後114=3 A/D/D、115原有五題及 payload 全部不變。
- 無更新 114 approved、無合併 PR21/22、無 LIVE 部署。三題為 **READY_FOR_INDEPENDENT_RELEASE_AUDIT（僅送審候選，不是 GO）**；由正式發布 Session 驗證同 SHA 完整證據後決定發布。

## D. 固定128題／V4：明確保留未驗收狀態

**本輪未修改固定128題教學分支，也未對整套 V4 頁面實作新的 UI 變更或全量最新 Playwright/RWD 測試**。此項是未完成，禁止宣稱 128/128 READY、UI 完成或正式發布。

其他 Session 的隔離分支 test/128-p0-p1-plus-pr22-114-compat-20261024，HEAD d2f3bb4a4cde26abededa5f49d98e900c3d31ee5，CI [#40107114227](https://github.com/homelux-huang/7581707/actions/runs/40107114227) SUCCESS（NO DEPLOY），但**不是本批 QA HEAD 對全部128題／正式 UI 的同 SHA 端對端驗收**。

另有真實阻塞須查：
- [#40106952345](https://github.com/homelux-huang/7581707/actions/runs/40106952345) 另一分支 student UI source 預期題號集合斷言 FAILED。
- [#40106895027](https://github.com/homelux-huang/7581707/actions/runs/40106895027) 另一分支學生 overlay / UI negative tests FAILED。
- 不可因其他分支個別綠燈忽略這些失敗；須先核對新 HEAD 是否已有修復，未修則在獨立平台開發分支安全修復且保持既有 115 正式五題。

## E. 送審分類與剩餘阻塞

**READY_FOR_INDEPENDENT_RELEASE_AUDIT（並非正式核准或已 LIVE）**：
- 114-00-E-07、114-00-E-08、114-00-E-09，依 PR21 逐題憑證 + PR22 發布 Gate + 本輪 #40108820782。官方來源、最終公告與教學由獨立 Session 最後裁決；主站仍 114 approvedCount=0。

**BLOCKED**：
- 106-00-C-14～20：本批七題影像 G1 合格；16/17/19 文字 G2 合格，其餘文字及全七題官方 G3、教學、發布 QA 未齊。
- 108-00-MB-16/17：已有 G1/G2，G3、教學與發布完整證據未齊。
- 105～115 年另有 1,974 題 G1 未完成；多數 G2/G3 未核實，不能把 WebP 覆蓋100%說成 QA100%。
- 104 年來源及 processed 尚缺，官方總題數未確認。
- 固定128題與最新 V4 完整端對端測試：本輪尚未完成，不得主張 READY。

**UNCHANGED_LIVE（既有main，不是本輪新增）**：
115-00-MB-02、115-00-MB-03、115-00-MB-04、115-00-MB-05、115-00-MB-09；本輪 dry-run 確認新候選不改 115 五題 payload。

## F. 下一輪獨立驗收與裁決

1. 重新讀取 main、QA／平台分支最新 HEAD，核查 PR3、PR21、PR22、所有指定 CI 與 SHA；勿用本 MD 舊 SHA 覆蓋。
2. 逐張獨立檢查 106 七題及三份共用的新舊 WebP、公式與文字修正；108 MB16/17 G2 逐式核對。
3. PR21/22 的正式發布順序、114 7/8/9 逐題正式憑證、最終疑義更正公告與 same-SHA V4 測試要獨立複核，才有權宣布 GO。
4. 把固定128題教學、首頁／題頁／一眼記住／計算框／手機RWD／正式五題回歸納入當前分支 Playwright 和授權老師稽核，不得假設先前 CI 通過涵蓋最新版本。
5. 持續完成 106 14/15/18/20 G2、歷史年度官方 G3、104 題庫、剩餘 1,974 題 G1，所有未完成者維持 NO RELEASE。
6. 所有 G1 是 ChatGPT assistant 證據，independentHumanReview=false；未重新下載所有官方 PDF 位元，不能自動聲稱新通過全年度 G0。

> 本輪已完成的安全修復、程式、逐題 QA、G5、CI 與交接紀錄均已保存 GitHub 指定 QA 分支。沒有改 main、沒有合併 PR 或部署、沒有修改正式學生資料，也未降低 Gate。現在正式返還獨立 QA／發布 Session，請按最新 HEAD、原始來源、逐題證據與 CI 做 GO／NO-GO；在它裁決前維持 NO DEPLOY／NO RELEASE。
