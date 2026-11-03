# ROLE D｜114 年英文作者中譯／重點顯示修復 + 114／115 同版 112 次 Chromium 驗收

## 原始缺陷與來源
- MASTER 控制台 Issue #36 [CLAIM #6595438652](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6595438652)；真正失敗的 114 E12 QA [PR121](https://github.com/homelux-huang/7581707/pull/121)、[Actions 41577979121](https://github.com/homelux-huang/7581707/actions/runs/41577979121) 16 個 size/theme 案例 `#guideCard .news-zh` 為 0，作者中文新聞消失，不能算 PASS。
- 原始素材 A PR116 HEAD `a25a6e43de1a8f8179d84cc2257998d3c4ad4f58`，Q12 單題 WebP SHA `99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60`，官方答案 C；B PR107 HEAD `57d969888c57fdcd2b16c933e92c7a2c9eebb3a5`，`questionRevision=0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec`、`composedTeachingSha256=fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4`。
- 正式來源 `answerVerified/questionVerified=false`，新題可信 E registry 仍空；即使技術測試成功也不核准 E12 正式上線。

## 程式變更與交錯修復保護
- 本 D Draft PR **stacked only on MASTER 已完成、但尚未合併的非計算卡 [PR113](https://github.com/homelux-huang/7581707/pull/113)** exact HEAD `16be0bf47a04cf56613b8da23cd96a829c2be7f1`。目標 branch `fix/master-v4-noncalc-gate-20261102`，不是 protected main；合併前由 MASTER 逐檔檢視及 rebase，禁止直接 merge。
- 原唯一 `sudu/v4-115-multisubject-review-demo.html` 的 `formatStudyValue`，只在 **年度英文有 canonicalId** 時使用該題自己的 `extra.新聞時事例句` 與 `extra.新聞時事中文翻譯`，根據真正存在於原英句的 `highlights` 做安全標記（HTML escape、重疊排除）。此修正沿用先前 ROLE D PR40 已完成的最小演算法，在 MASTER PR113 底版只添加 1,756 字元，不覆蓋其非計算卡修改。
- **沒有 canonicalId 的原 35-Demo** 維持原 `DEMO_LEARNING_CONFIG.englishNewsExamples[q.id]` 的原程式、新聞範例和 CSS；年度題禁止偷偷借 Demo 同數字的例句及中文翻譯。作者沒有提供中文時不能 AI 編造。
- 不修改原圖、答案、SQLite、B/C/E、approved、PR30、Publisher、main、Pages 或學生記錄。只新增兩份 D real QA test、單一 CI workflow 與本交接 MD。

## 真實驗收
- 114 E12 真實 A/B 原始單題+教學固定 SHA QA-only **16** case；測試執行同一受限年度暫時 HTTP approved 攔截，畫面有 QA ONLY NOT LIVE watermark，圖片使用原 WebP 真實位元，出版 `approved/114.json` 仍 0。
- 115 既有 approved 五題（02/03/04/05/09）在**同一新 HTML HEAD** 重跑 **80** 個真實 Chromium 答題流程，全部原答案 A/A/C/B/A、四選項解釋、所有數學步驟、原圖 SHA、錯題與獨立儲存。
- 114 正式空清單／原圖只讀及拒絕答案、評分、正式學生紀錄 **16** case。合計 **112/112** 為目標，並必須留 112 張同版 PNG、兩份 SHA JSON、CI 日誌。不可以拿原 PR117 的 96/96 截圖當這次新版 HTML 的 PASS。
- 任何一例失敗即 FAIL，保留截圖、不降低測試、不批次 READY。
- 本輪的新 READY=0、新 LIVE=0；新題必須另有正式 A G2/G3、不同作者 E 可信複核、真正 publisher emission 及 latest teaching digest D 16/16。

