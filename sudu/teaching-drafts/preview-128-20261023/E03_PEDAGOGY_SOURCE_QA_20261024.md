# 115-00-E-03｜英文第3題：完整語義、原圖與新聞出處再次檢查（AI已知官答後；非發布憑證）
 
本題題號：`115-00-E-03`，原圖 `sudu/data/approved/webp/115/115-00-E-03.webp`（SHA256 `16c8e37d3f169f0488398844030bf4922c4f4639633ee7a4d9a9af83466d8ebd`）。正式 main／教學草稿原圖 blob 一致；本次直接開圖辨識完整題幹和 A–D，未混入其他題號；文字另由 `sudu/data/years/115.json` 逐題來源欄位核對，該原始年庫題目仍標記 questionVerified=false，不冒稱原庫文字已獲獨立OCR QA。
 
**原題**：The teacher treats all her students ________, giving every student the same opportunity to succeed.
**官方最終答案 B**（E03 在官方英文確認說明非更正題），沿用 `official-final-evidence-20261023.json` 及完整證據來源。這次是看到官方答案後的 GPT-6 另一個 Session 自行複核，**不是新盲解、真人教師、外部獨立第三方**；歷史 `reasoningRecordedBeforeCandidateRead=true` 留在原資料，未修改或冒充本輪首次解答。

## 本次逐一核對選項與高低兩層教學

| 選項 | 結論 | 高職原理 | 給小學生 |
|---|---|---|---|
| A carelessly | 錯 | 意為粗心地；即使行事粗心也不代表每位學生得到**same opportunity** | 做事馬虎與是否偏心兩回事 |
| B equally | **正確** | 副詞修飾 treats：**treat all students equally** 與每位學生相同機會直接相符 | 老師讓每個人都輪得到，不偏袒任何學生 |
| C instantly | 錯 | 表立即、強調**速度**，與公平對待沒有邏輯關係 | 做得快不等於每個人得到公平機會 |
| D silently | 錯 | 表安靜地，強調**聲音方式**，不是對學生的差別待遇 | 老師聲音小不能說他有沒有偏心 |

- 一眼記住：**same opportunity → equally**；公平給機會不等於考試結果相同。
- 推理：空格為副詞，修飾 treats，透過逗號後面的 **giving every student the same opportunity** 確定所需含義。不涉及數值計算；正式 UI 不應顯示考題計算式空卡。
- 發音已查：Cambridge Advanced Learner's Dictionary /ˈiː.kwə.li/（https://dictionary.cambridge.org/us/pronunciation/english/equally）。Cambridge 本義包含平等／以相同方式對待（https://dictionary.cambridge.org/dictionary/english/equally）。**初／中／高是本站自訂教學難度，不是經 Cambridge 證明的字詞官方CEFR逐詞分級**；evenly 偏數量均等，並非所有語境都可直接替換 equally。
- 新聞來源已修正成 2026-09-17 聯合國原頁：https://www.un.org/en/desa/one-in-three-institutions-built-to-advance-gender-equality-stripped-of-power-in-just-two-years-new-un-report-reveals 。原稿引用的SDG網址無法成功取回。本題英文新聞句為**自行改寫**，不是聯合國逐字引述；其內容「婦女應同等享有決策權」與公告實際意思相符，含 equally 可被真實高亮。
- 彰化高商當屆實際採用教材／版本／章節／頁碼**待核對**；不編造。此為允許的來源頁碼缺口，非語義錯誤。
 
## 本輪 UI 證據與限界

- [前次 V4 同內容隔離測試 #40048104080](https://github.com/homelux-huang/7581707/actions/runs/40048104080) PASS：真實題號/選項，8尺寸×2主題，實際 pointer/tap，答案 B、原圖、四選項解說、強調、高亮、中英新聞例句、錯題復習。
- 這是**修正新聞URL及IPA之前**的測試。文字版本已變，必須針對新教學 SHA `c7bce2469356f95e929b19d5275cd3ca1a4ff8f2c9f89cd858b61e5c8cdc3316` 重新跑；本報告**不以先前UI PASS簽發新版憑證**。
- 測試 `tests/sudu_english03_isolated_ui.cjs` 已改為從倉庫 `sudu/data/years/115.json` 讀取 E03 原題與 A～D，不再以手寫題幹作 fixture。
- **正式 source QA 仍缺** `qa/114-115-official-visual-review` 的 E03 學生核准證明（現有該分支僅數學B 02/03/04/09）；教學分支正式 `independentTeachingReview=PENDING`、`uiReview=PENDING`；未重新取得有獨立預先解題來源的正式 admittance 憑證前，不可設 `STUDENT_QA_APPROVED` 或上線。
- 這份文件是**已確認的AI語義與來源複核**，不是將剩餘閘門偽裝成PASS。 
 
