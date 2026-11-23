# ROLE D｜114 英文第12題：原始來源與最新版教學 SHA 的隔離 8×2 UIQA

- Claim：[Issue #36 #6595387223](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6595387223)。**僅 D 獨立技術驗收，不是正式發布。**
- 唯一 V4 HTML 沿用正式 main `ba2f3f0757dbf81eaaf125bd610b0f38de52fea9`，35 Demo 原版不變。
- ROLE A [PR116](https://github.com/homelux-huang/7581707/pull/116) HEAD `a25a6e43de1a8f8179d84cc2257998d3c4ad4f58`，Q12 真 WebP SHA256 `99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60`；官方答案 C、公告具名僅 E26；正式來源 `answerVerified=false`、`questionVerified=false`，必須 HOLD。
- ROLE B [PR107](https://github.com/homelux-huang/7581707/pull/107) HEAD `57d969888c57fdcd2b16c933e92c7a2c9eebb3a5`，新版完整 composedTeachingSha256 `fd503a9cbe82da0838859d059951988835d12604cffc95d8b0a8d76d34a9d9c4`，原來源 revision `0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec`。E substantive content 同版複核 #6555967123 PASS，但尚無 main 正式 trusted AI receipt。
- 此測試從固定 A/B Git HEAD checkout 真文字／原圖和教學、逐檔 SHA 重算，**只在 CI Chromium HTTP 暫時攔截 114 approved 檔** 以驗證學生介面，並暫放原 WebP 到 _site，測完清理；原 main `approved/114.json` 永遠保持 0 題。
- 固定 8 尺寸×淺/深共16個真實 Playwright case，逐題 A–D、原圖 SHA/原題號、雙層解說、非計算卡隱藏、英文／中文新聞例句、實際關鍵字 highlight、選項 hover/觸控及 RWD。每張截圖會標示 QA ONLY NOT LIVE。
- 若 main UI 仍遺失 B 作者中文新聞／highlight，CI 必須 FAIL 並保留截圖和 JSON；**不得降低斷言或誤當正式 READY**，應另由 D 領取不與 MASTER #113 重疊的 renderer 修復並重測。
- 本 PR 只有新 test/workflow/docs，沒有變更 HTML、runtime、A/B/C/E/MASTER、approved/Publisher、main 或 Pages；正式 E/G2/G3/逐題 admission 仍待 MASTER 驗收。
