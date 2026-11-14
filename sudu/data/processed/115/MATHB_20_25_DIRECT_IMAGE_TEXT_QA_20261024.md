# 115 數學 B 20～25｜原始 WebP 逐字校正交付（2026-10-24）

本次直接讀回六張 GitHub 原始單題 WebP 位元組並目視，GitHub Actions [#40084307251](https://github.com/homelux-huang/7581707/actions/runs/40084307251) 六個 job 都 SUCCESS，原始圖像 SHA-256 與 manifest 一致。未重裁、未重新 OCR、未修改官方答案。每題源文及四選項、版面圖表說明、舊 OCR/文字候選及 SHA 對照存成分立 JSON，詳 `sudu/data/processed/115/review-evidence/MATHB_20_25_IMAGE_TEXT_CORRECTIONS_20261024.json`。

| 題號 | 逐圖文字訂正重點 | 官方答案 | 發布 |
|---|---|---|---|
| 20 | 原圖 A-D 含 √3 與加減號，選項不能混入圖（四）的 C/A/B、60°、75°、100m | A | BLOCKED |
| 21 | ∠ACB＝60°、AC＝8 km、AB＝7 km，選項為 5／4.75／4.50／4.25 | A | BLOCKED |
| 22 | 「有 ū」與「無 bô」正確字形；五張卡片示例另保留原圖；選項 32／31／16／5，去頁尾 | B | BLOCKED |
| 23 | 保留二欄兩列完整表（二），只有其中一人折 3000 元或打八折；四選項 32000～35000 | B | BLOCKED |
| 24 | A＝110/r、B＝log₁₀(3)/log₁₀(1+r/100) 分式與向上進位 C、D 完整 | C | BLOCKED |
| 25 | 原題距離是 **√2**，不是 2；圓方程 x²−8x+(y−7)²=a，去除圖後「以下空白」及頁尾 | C | BLOCKED |

**邊界**：本交付完成的是 GPT-6 AI 對原始影像之直接逐字對照與可重現文字修訂候選；沒有獨立人員二次正式簽核，也沒有看答案前新盲解。故所有欄位維持 formalIndependentHumanTextQaPass=false、independentBlindSolveCertificate=false、completeTeachingAndUIQaPass=false、studentReleaseApproved=false、deploy=false。不得把本 JSON 當作 source QA admission 或正式 READY。

後續：由獨立審查者逐字核稿，通過既有來源分支 admission 後更新 canonical source + SQLite roundtrip 與 revision；對同教學 SHA 補教學/UI 8x2 實測及憑證，最後走既有 publish gate，不能只改旗標。
