# E03／年度轉接器接入 QA（2026-10-24）

接手 draft 76252ad5d73398170135f0972876b2589715871a；main 5415a30452cdf9020242aca16fe0ff2b6814ab4b。

## 發現並修復的接入阻塞
教學分支的年度轉接器建立在較舊UI上，仍有 verifiedYearNav、verifiedImagePreview、status panel；整檔部署會恢復已移除的遮擋區塊，並缺少main首頁及單題原圖流程。以讀取的main轉接器為基底，只合入安全粗體、高亮詞界限與選項reason去重邏輯，保留main題號與SHA檢查、首頁、逐題WebP、原圖唯讀模式及localStorage分離。
本輪沒有修改正式main或approved資料。

## E03原題與測試
實際開啟115-00-E-03既有單題WebP，題目為老師對學生同等對待，線索為every student the same opportunity；四選項carelessly/equally/instantly/silently，B。語意與現有雙層說明一致。此為已知答案後的AI複核，非盲解或真人教師簽核；新聞來源、發音及詞彙分級全項審查尚未在本輪完成。

新增 tests/sudu_english03_isolated_ui.cjs：本機loopback-only、以main HTML加候選轉接器載入E03實際原題文字與四選項，不使用選項佔位文字；瀏覽器route隔離資料，原圖bytes SHA先驗。8尺寸×2主題測真實click/tap、四選項兩層說明、無重複reason、strong/mark、中文新聞翻譯、初中高標籤、計算隱藏、題目/解說切換、錯題復習與回題。截圖及摘要由CI artifact保存。

本機已通過：node markup regression、5個Oct24內容測試、128筆結構audit（0 errors）。UI結果必須讀實際workflow，不能提前標PASS。測試中的英文欄位映射目前仍為隔離fixture，後續需對正式匯出路徑做同內容驗證。

READY=0；未簽發正式逐題教學/UI發布憑證，未部署。


## 2026-10-24 來源/教學再檢補充

E03 原題已改由實際 `sudu/data/years/115.json` 取文字及四選項，並在 `E03_PEDAGOGY_SOURCE_QA_20261024.md` 實際查證劍橋發音、詞義與聯合國新聞原文；E03新聞網址修復後教學 SHA 變更，原 UI run 40048104080 不再當作新版本正式證據。正式 READY 保留0。
