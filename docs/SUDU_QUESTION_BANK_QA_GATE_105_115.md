# 7581707｜105–115 年統測商管群題庫資料工程：驗收門檻與交接規格

生效日期：2026-10-22。適用 `homelux-huang/7581707`。本文件是題庫進入正式平台前的**硬性放行條件**，不因 CI 綠燈、檔案存在或 OCR 完成而降低標準。

## 1. 年度與範圍

- 「114 年往前推 10 年內」= **105–114 年（含 114，共十個年度）**。115 年另列為持續 QA 的既有年度。
- 每年度依 TCTE 官方商業與管理群當年實際適用考科、試卷、題號、題數及計分規則；歷史科目名稱可能不同，禁止把每年強行補成 205 題或重編題號。
- 優先重用 `sudu/data/years/<year>.json`、`sudu/data/original/<year>/`、既有 OCR、已校驗 WebP 及 SHA；只補缺漏，版本化修復，不覆蓋已驗收資產。
- 官方來源：`https://www.tcte.edu.tw/index.php?mod=TVETest/down_exam4y` 與 `https://web1.tcte.edu.tw/EXAM/<year>_4y/`；保存 PDF URL、原始檔 SHA256、下載時間、版本與官方更正公告查核紀錄。

## 2. 七項必過驗收門檻

| Gate | 驗收 | 必須有的證據 |
|---|---|---|
| G0 官方原卷 | 來源為當年度 TCTE 官方 PDF；題數、原題號、科目、版本可核對 | 官方 URL、PDF SHA256、來源頁、題數稽核 |
| G1 單題 WebP | **每張只含該題號、完整題幹、A/B/C/D、必要公式／圖表／單位**；不含整頁、鄰題、頁首頁尾；跨頁完整處理；共享文章／圖表獨立裁切並關聯 | 原卷與裁切圖**逐題目視對照**、頁碼、像素座標、輸出 SHA256、QA 人員／時間／紀錄 |
| G2 OCR／文字 | 保存 raw OCR、校正後題幹與四選項、校正差異；與原卷逐項核對。公式或圖表不能可靠轉文字時保留原 WebP，不得編造 | raw、corrected、diff、文字 QA 紀錄、圖片回退策略 |
| G3 官方答案 | 每題對照 TCTE **最終官方標準答案及疑義／更正公告**，核對題號與選項；不一致須 BLOCKED | 官方答案 PDF／影像 SHA、頁碼、逐題對照值、公告版本、reviewer、時間 |
| G4 資料關聯 | `year+paperCode+originalQuestionNumber` 唯一，單題圖、OCR、答案、共用材料關聯正確，SHA 一致 | 完整 manifest、無重複與跨題關聯驗證 |
| G5 SQLite／JSON | 隔離資料庫匯入兩次仍無重複；全部讀回與 JSON、SHA、答案、題號相符；不碰正式學生資料 | 資料庫 round-trip／idempotency 報告、阻擋清單 |
| G6 整批放行 | 該年度所有題目 G0–G5 PASS、共用材料全 PASS、CI 與證據齊備，才可 `integrationReady=true` | `VALIDATION.json`、`inventory.json`、`release-manifest.json`、逐題 QA 記錄 |

**不得偷換概念：** 程式檢查尺寸／解碼／SHA 通過 **不等於** 圖片目視 QA；OCR 候選 **不等於** 題目核對；PDF 文字抽取答案一致 **不等於** 官方最終答案核實；助理初步目視答案表 **不等於** 已檢查所有更正公告。

## 3. 三個答案／題目旗標須獨立

- `answerMatched`：候選答案與某份官方答案資料的對應一致；**不是正式放行**。
- `answerVerified`：最終官方標準答案與更正公告已查核，逐題答案有來源、版本與獨立證據。
- `questionVerified`：題幹、四選項、圖表、OCR 與原卷完成逐題 QA，並且該題單題 WebP 目視 PASS。

缺乏相應證據時，不得設為 `true`。歷史資料的 `answer` 數值、`officialAnswerCandidate` 及 `answerMatched` 只視為候選。

## 4. 必備輸出與欄位

每年輸出到 `sudu/data/processed/<year>/`：
`questions.json`、`webp-manifest.json`、`ocr-raw-candidates.json`、`official-answer-evidence.json`、`question-bank.sqlite3`、`inventory.json`、`VALIDATION.json`、`VISUAL_QA.json`、`REMAINING_QA.md`、`DATA_HANDOFF.md`、`release-manifest.json`。

每筆需保留 `questionId`、`year`、`paperCode`、`originalQuestionNumber`、`subject`、`sourceQuestionPdfUrl`、`sourceQuestionPdfSha256`、`sourceAnswerPdfUrl`、`sourceAnswerPdfSha256`、`sourcePage`、`cropPixels`、`webpPath`、`webpSha256`、`sharedMaterialIds`、`ocrRaw`、`ocrCorrected`、`answerCandidate`、`officialFinalAnswer`、`officialCorrectionChecked`、`imageQaStatus`、`textQaStatus`、`answerQaStatus`、`qaReviewer`、`qaReviewedAt`、`qaEvidencePath`、`integrationReady`。

WebP 修正須建立新版本（`webp-v2` 等），保留舊版與 SHA，不得覆蓋先前證據。共享材料應有獨立 `sharedMaterialId`、來源座標、SHA、逐張目視 QA。

## 5. 進度與 QA 狀態

- 每年度進度條僅以**已逐題目視 QA PASS 的 WebP 題數 ÷ 該年度官方實際題數**計算；答案、OCR、SQLite 另以文字說明。
- 年度總完成需 **WebP 逐題 QA 100% + 共用材料 QA 100% + OCR／文字 QA 100% + 官方最終答案及更正公告 QA 100% + SQLite/JSON/SHA/CI PASS**。
- `DRAFT`、`PENDING`、`BLOCKED`、`PASS` 不得混用。僅在實際目視比對後才允許 `imageQaStatus=PASS`。
- 未滿上述條件時 `integrationReady=false`，**禁止正式接入、合併 main、部署 LIVE**；允許在獨立 data/QA 分支建立候選、驗證與 staging DB。

## 6. 已確認的現況基準（非完成宣告）

- 114 年：205 題單題 WebP 候選已產出，既有 `inventory.json` 記載**目視 PASS 0/205**；文字選項仍有缺漏；官方答案候選表比對及最終更正查核不得視為全部驗收。
- 115 年：205 題單題 WebP 候選已產出，既有 `inventory.json` 記載**目視 PASS 133/205**，另有 72 題待目視 QA；共用材料及最終官方更正查核仍有待辦。
- 114 + 115：`sudu/data/QA_114_115_OFFICIAL_ANSWER_VISUAL_2026-10-22.json` 記載 410 題候選答案與官方答案頁的視覺比對；**不代表更正公告及獨立最終核實完成**。
- 105–113 年已有 `sudu/data/years/<year>.json`，可作來源候選與保留既有資料的起點；不能因此宣告單題 WebP、OCR、SQLite 或 QA 已完成。

## 7. 安全執行與交接順序

1. 先盤點現有 HEAD／PR／CI、每年官方題數與既有資產，產出缺漏清單，絕不重做已通過的工作。
2. 114、115 年持續逐張 QA、修正錯誤裁切、核對更正公告、補 OCR 與 DB；所有 QA 保留具體證據。
3. 113 → 105 年逐年建立候選單題 WebP、OCR、官方答案、共用材料、SQLite、驗證報告；QA 尚未做的題目維持 PENDING。
4. 逐科 commit，隔離 Draft PR；CI 失敗修原因，不刪 assert、不偽造 PASS。
5. 所有年度全部 G0–G6 PASS 才提供平台設計／版面端正式資料接入許可。

**不修改** `main`、115 年既有資料、正式平台 UI、裝置代碼、學生作答與成績、錯題紀錄；不合併 PR、不部署正式站。
