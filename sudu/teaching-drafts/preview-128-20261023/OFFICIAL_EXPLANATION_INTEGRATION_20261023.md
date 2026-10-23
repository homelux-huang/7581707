# 官方解讀教學整合與資料完整性驗收

日期：2026-10-23（臺灣時間）。從7efc559接續，保留其他Session的會計原圖複核成果。本批不部署。

## 已完成

- 再目視商概7、數位33、會計6、經濟28、44既有單題WebP，未改圖、未OCR。
- 會計6：將期初／年度中／期末調整後的差異寫入四選項與逐步解題；說明備抵是抵銷科目，不是另存現金。無數值運算，計算區隱藏。
- 經濟44：主解說依官方說明，分主導者、工具、方向判斷擴張財政；不是所有貸款皆屬同一政策。四選項均有老師及小學生說明，無計算區。
- 經濟28：官方以MU/P均等選A；補足A、B、C、D三種商品全部比率。保留AI初解D及未列預算的疑義，不把A支出250元當題幹已知。
- 原解說及答案比較存入revisionHistory；同步既有草稿步驟bundle。

## 爭議與來源

商概7官方B；特別股固定成本與財務槓桿廣義定義有疑義。參考TEJ欄位說明：https://www.tej.com.tw/tejdoc/db-document/tw/wim4.html 。這只能提供財務用語對照，不是證明高職課本採何定義，仍保留警示。

數位33官方A；題幹把資料驗證概括為加解密，教學必須區分雜湊、簽章及加密。Bitcoin交易文件：https://developer.bitcoin.org/devguide/transactions.html 。NISTIR8202第三節提供概論，但其非對稱密碼段落也有加解密類比，不能將類比當作所有簽章演算法的精確描述。仍待教材用語對照，不解除警示。

官方確認說明來源及PDF雜湊沿用 `official-final-evidence-20261023.json`，本輪不更動原圖或原答案。

## 驗證結果

`python scripts/audit_preview_teaching_drafts.py`：128 records，0 errors。
`node --check sudu/teaching-drafts/preview-128-20261023/solution-steps-128.js`：PASS。

核查範圍是資料一致性及發布保護；沒有瀏覽器UI、真實學生操作、第三方盲解或全科教材驗收，不能標示全部完成。會計6、經濟44的核心解說有限範圍複核通過；完整驗收維持0，發布開關全false。
