# 固定128題｜2026-10-23 新增5題實體原圖、SHA256與部分教學複核（不發布）

- 工作分支：`draft/preview-128-explanations-20261023`
- 本批對照來源HEAD：`b6b0771f3669c1522f22380dd8f675a22461fea3`
- 須區分：歷史逐題目視128/128；本次工作週期實際從GitHub下載原WebP位元組、目視及重算SHA256，從21/128提升至**26/128**。本批5題與先前21題無重複。
- SHA256獨立實作曾以標準 `abc` 測試向量 `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` 比對通過；本批5張皆對照固定manifest雜湊一致。
- 此次複核**已知既有候選答案**，不能稱為首次盲解。保留個別JSON之首次答案、修改與分歧史。沒有重新OCR／裁切，也沒有修改原圖／approved。
- 下列屬部分原圖核實及教學重算／邏輯複核，**並未通過官方最終答案PDF、更正公告、教材版本章節頁數、完整四選項獨立教學QA、真實Playwright/RWD**。正式核准數保持0。

| 題目 | 實際二進位 SHA256 | 圖像核實 | 初次答案爭議 |
|---|---|---|---|
| `115-09-2-03` | `16e5634a17680ca04fc76d82f72ef1e76c423aa5e5ed80062c0cec63b7c05163` | PASS：題號、題幹、選項，無sharedImages | 首次與候選不同，未解除QA |
| `115-09-2-06` | `260ff739935f3ac116b51e4b81f3c0397c4dfcb142e50a60002a4861fca2c900` | PASS：題號、題幹、選項，無sharedImages | 首次與候選不同，未解除QA |
| `115-09-2-12` | `53fe56b7680c29c8b1da0589569f2308630b78fcaa417214c01fa7474e432cf0` | PASS：題號、題幹、選項，無sharedImages | 首次與候選不同，未解除QA |
| `115-09-2-15` | `6a9840a517f22334743662035ce9553f77b5ab3e062fbfe5b66766d18b6b00fb` | PASS：題號、題幹、選項，無sharedImages | 首次與候選不同，未解除QA |
| `115-09-1-01` | `da86b958242f46bb5c8cfce60a0bf9b79a72d33f3bb049c1ac801be9109ff799` | PASS：題號、題幹、選項，無sharedImages | 候選邏輯與教材用語待QA |

## 逐題實證與未結案部分

### 115-09-2-03

原圖C明確寫「購入汽車以供出售」而非「出租」。C為候選，符合存貨持有供出售定義；A薪資非純內部調整、B地震不構成對外交換交易、D必要進貨運費不能逕列一般營業費用。首次把出售讀成出租的歷史必須保留。

輔助參考：https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode=J0080010（並非當年度官方最終答案；教材版次／頁碼未核准）。QA狀態：`PARTIAL_POST_CANDIDATE_RECHECK`；official/teaching/release仍待核對。

### 115-09-2-06

原圖X1與X2年末應收款分別為500,000／600,000。①前一年調整後貸餘結轉年初、②期間沖銷可能使餘額借餘、③依非零預期信用損失調整後一般貸餘，候選D有會計邏輯；仍需正式課本定義與最終答案。首次B→D修改歷史保留。

輔助參考：尚無可正式核准的教材出處。QA狀態：`PARTIAL_POST_CANDIDATE_RECHECK`；official/teaching/release仍待核對。

### 115-09-2-12

原圖③要求調整後公司帳與『原銀行對帳單』相同，並非調節後正確餘額，因此③不成立。④在途存款應加銀行側，非公司重複借記；②保付支票一般已由銀行扣款、⑤上月在途款本月通常入銀行帳，候選A(②⑤)合理。初次D→A歷史保留。

輔助參考：https://pic.tasker.com.tw/file/1/339/1802535/1528899109177467114.pdf（並非當年度官方最終答案；教材版次／頁碼未核准）。QA狀態：`PARTIAL_POST_CANDIDATE_RECHECK`；official/teaching/release仍待核對。

### 115-09-2-15

原圖①銷貨成本13500、②存貨10500、③聲稱『盤盈1000』。獨立重算可供售480件、淨售250件、帳存230件、實存210件、盤虧20件×50=1000元；期末存貨210×50=10500、定期成本(480-210)×50=13500；永續原銷貨成本250×50=12500，盤虧1000若併銷貨成本為13500。候選C有依據，但永續盤虧的列報方式須按教材獨立QA；初次D→C歷史保留。

輔助參考：https://0800280280.sme.gov.tw/accounting/run.php?file=detail&id=339&name=kw（並非當年度官方最終答案；教材版次／頁碼未核准）。QA狀態：`PARTIAL_POST_CANDIDATE_RECHECK`；official/teaching/release仍待核對。

### 115-09-1-01

原圖②自主使用再生能源減碳可列CSR；①社區講座非當然法定強制；③成本增加不自動等於最基本倫理違反；④『利潤受損即未善盡經濟責任』過於絕對。候選D(②④)的命題課程分類仍有概念疑義，不得標教學QA PASS。

輔助參考：尚無可正式核准的教材出處。QA狀態：`PARTIAL_POST_CANDIDATE_RECHECK`；official/teaching/release仍待核對。


## 官方最終答案PDF與疑義存取

- 官方入口：https://web1.tcte.edu.tw/EXAM/115_4y/ 與 https://web1.tcte.edu.tw/EXAM/114_4y/。官網可確認115最終公告日期115年5月8日17:00（2026-05-08），**這不代表實際逐題讀取PDF**。
- 既有草稿記錄的115商管專二最終檔案下載器連結：`https://web1.tcte.edu.tw/EXAM/115_4y/downloader.php?obj=MTE1LTR5LTA5LTItc3RhbmRhcmQucGRm`。本輪網頁讀取端直接開啟時回覆無法存取，工作容器網路DNS也失敗；不能宣稱PDF或疑義說明成功下載、開圖或逐題比對。
- 官網的115「09商管專一」確認說明欄標『未提出疑義』，商管專二有確認說明入口；**此欄不能代替專二PDF細讀**。官方最終核實仍0/128。
- GitHub `candidateProvenance` 舊有PDF雜湊只屬歷史來源欄位，本次沒有拿到PDF bytes，沒有重驗該雜湊，不將其提升為official verified。

## 不可修改及後續優先

- 原三題 `115-09-1-07`、`115-09-1-33`、`115-09-2-28` 繼續BLOCKED；會計03/06/12/15保留首次解答差異；商概01、03、05需獨立教材用語複核。
- 全部128題的 `studentReleaseApproved=false`，正式 `deployed=0`、`fullyAccepted=0`、`officialFinalCorrectionVerified=0`。本批不修改main、正式V4、approved、Pages與學習紀錄。
- 後續仍須官方最終PDF逐卷查證、剩餘102題本工作週期實際WebP重驗、教材與四選項教學QA及獨立browser測試。
