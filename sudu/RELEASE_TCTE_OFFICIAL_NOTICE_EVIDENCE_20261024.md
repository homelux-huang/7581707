# 7581707｜114／115 統測官方確認公告、逐題證據與正式發布邊界（2026-10-24）

本文件是**官方公告證據與發布核對資料**，**不是**學生題庫核准、變更答案或佈署指令；不可直接把 `answerVerified`、`questionVerified`、`studentReleaseApproved`、`releaseApproved` 或 `deploy` 設為 true。

## 114 年：官方檔案實證完整，但答案／教學發布 QA 尚未完成

- 官方公告：https://web1.tcte.edu.tw/EXAM/114_4y/
- 官方目錄擷取 SHA256：`e6a44ca0fc8b2945924c6d6f553df19904784dadfd693263fe427c5fc94302e2`。
- 官方 PDF 四份，由 GitHub Actions [#40094431419](https://github.com/homelux-huang/7581707/actions/runs/40094431419) 成功取得；下載的 **115 年 09-2 確認 PDF** 同時作為控制組，SHA 與既有正式證據相同。
- [原始 PDF、逐頁圖片與文字的 CI 附件](https://github.com/homelux-huang/7581707/actions/runs/40094431419/artifacts/12560332353)（30 天保留）。19 頁均已用 PDF 渲染影像及文字逐頁比對，官方確認書共明列 **18 題**。
- 結構化：`sudu/data/processed/114/official-confirmation-status.json`、`sudu/data/processed/114/QA_114_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261024.json`。結構化檔案包含**完整** PDF SHA256、URL、頁數、每題題號、確認書公告答案、來源頁碼及比對聲明。

| 試卷 | 官方公告性質 | 頁數 | 官方確認書列名（題號：公告答案） | PDF SHA256 |
| --- | --- | ---: | --- | --- |
| `00-C` 國文 | 有確認說明書 | 5 | 14:A（p1-2）、24:C（p3）、28:B（p4）、30:D（p5） | `afc4ad2e67004a40539d05406813ff361d99696607cf6fc71c62484cc3001a71` |
| `00-E` 英文 | 有確認說明書 | 1 | 26:C（p1） | `79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc` |
| `00-MB` 數學 B | **官方目錄：未提出疑義** | — | 無確認書（不代表全科答案已 QA） | 不適用 |
| `09-1` 商管專一 | 有確認說明書 | 9 | 02:A、07:B、08:D、09:A、18:C、21:B、24:B、32:B、43:D（逐頁 p1–p9） | `5ea66797b68a00ea831bcbd645af747a4802298ae2fedcd5abe6a05705543246` |
| `09-2` 商管專二 | 有確認說明書 | 4 | 10:D、16:B、27:C、35:D（逐頁 p1–p4） | `70d95c1b4835c8410821543bbb4ed2fd92f3e31df502808deb5f50d72ef93762` |

這 18 個公告答案與既有 `114/official-answer-evidence.json` 的「**官方最終答案 PDF 文字擷取候選**」及 `114/questions.json` 的候選答案 **18／18 一致**。但原資料明確標為 `PDF_TEXT_ONLY_NOT_INDEPENDENT_VISUAL_VERIFICATION`、`answerVerifiedCount=0`；本次**未完成 205 題正式答案影像目視驗收**，也沒有將公告值直接寫回考題答案欄位。

> 注意：「某科有確認書」不等於「確認書所列題號必然發生答案更改」。同一科**未列名**題目不可以寫「全科未提出疑義」，只能依 SHA 綁定完整確認書的已核實題號清單，逐題推論其公告適用範圍；最終答案 PDF 仍需獨立核對。

## 115 年：沿用既有正式 SHA 證據

- 官方公告：https://web1.tcte.edu.tw/EXAM/115_4y/
- 主 QA 分支現有 `sudu/data/processed/115/official-confirmation-status.json` 與 `QA_115_TCTE_OFFICIAL_CONFIRMATION_PDFS_20261023.json` 已有官方頁碼及 SHA 綁定。
- `00-C` 10 頁：12、16、18、23、24、34；`00-E` 2 頁：34；`09-2` 3 頁：06、28、44。
- `00-MB` 與 `09-1`：官方目錄記載未提出疑義。
- `115-09-2-34` 未被列名於 09-2 官方確認書，所以其證據可宣稱「**第 34 題不在確認題號範圍內**」，**不可**宣稱「09-2 全科無疑義」。其獨立候選 QA 工作位於另一個 `qa/econ34-prekey-image-only-20261024` 分支，當前 canonical QA／main 不因本文件而增加核准題。

## 正式發布守門條件（不變）

1. 官方公告證據屬於**來源範圍**：完整 PDF SHA、頁數、確認題號、單題公告答案（若列名）必須可追溯；不能以官方目錄索引取代逐頁官方確認書。
2. 官方最終答案 PDF 的每題影像 QA／OCR 文字校正／WebP SHA 及單題完整裁切／獨立先解／教師與國小白話雙層教學／正式 UI 與 same-SHA 證據仍須各自完成。
3. **114 年 publisher 目前明確 fail closed**（`scripts/sudu_verified_publish.py:official_notice_scope_certified` 對非 115 年返回 False）。在準備新增 114 正式題目之前，需另外新增且測試 114 年限定的官方公告範圍核對 gate；本證據檔不自動變更發布資格。
4. 新核准題仍必須由原有 `qa/114-115-official-visual-review` 的真實 `STUDENT_QA_APPROVED` 證書進入 main，並通過 Pages `verify → build → deploy → verify_live`；**不能直接修改 main 的 approved JSON 或繞過 gate**。
5. 本證據分支全部為資料與唯讀核對 Action，**沒有寫入正式 main、沒有修改原始 OCR/DB/WebP、沒有執行 Pages 佈署**。

## 本次交付與下一個真正阻塞

- **公告來源核對已補齊：114 年 4 份官方 PDF / 19 頁 / 18 題，115 年沿用既有官方確認紀錄。**
- **114 年正式發布尚有阻塞：**最終答案影像 QA、逐題完整證書、教學／UI 證據，以及 114 年官方更正範圍專用的 fail-closed publisher 閘門。
- 前一次確認 main SHA：`0198a8f431401632f9b82ec8f5adc16da33f2a49`，Pages [#40089905136](https://github.com/homelux-huang/7581707/actions/runs/40089905136) 四階段成功；正式題庫仍是 **114 年 0 題、115 年 5 題**。
