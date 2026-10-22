# 115 全年度題庫資料工程交接 / DATA_HANDOFF

基準 main SHA: `40ffa920d8efb8e7dc54471a62bb70ecb14ee096`. Branch: `data/115-full-year-question-assets`.
本 PR **只有資料工程，不可被當作主平台已接入、全年題庫已公開、已做完整裁切或全部 OCR 完成**。

## 單題 WebP 強制驗收契約（115 年全部 205 題）

**此要求是硬性限制，不能以僅有檔案、裁切座標合法或 WebP 可解碼當作通過。** 每題必須保留 *官方原題號*、原始題幹全部文字及條件、完整 (A)(B)(C)(D) 選項、相關圖表/公式/單位，但 **WebP 絕不能包含整張試卷頁、前後題題幹選項、公告頁首、頁碼頁尾等非必要內容**。裁切圖來源只能是 `sudu/data/original/115/<paper>/p###-...webp` 官方原卷對應頁的真實像素；不可 AI 製圖、重新排版或在原卷中重寫題目。

共用閱讀材料、跨頁內容必須 **獨立** 裁切成多張有順序的原圖並用 `sharedMaterialId` 關聯，不得把別題塞進當題圖，也不能只留下答案而缺共享閱讀材料。若跨頁需要兩張題圖，使用 `assets.parts[]` 及順序；每張都是真實原始官方頁面裁切。原始圖片和已通過歷史 QA 的會計第 2–6 題永久保留，不以未覆核裁切覆寫。

生成圖片預設 `qaStatus=DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA`；只有逐張目視對比原卷並確認以下 10 項才可記錄 `qaStatus=PASS`，另需記錄審查者/審查日期/該圖片 SHA-256，避免改圖後仍顯示舊驗證：正確科目與題號、題幹完整、所有必要條件、A–D 四選項完整、共用圖/表/公式/單位與附註完整、無前題內容、無後題內容、無不必要頁首/頁尾、比例與小字清晰、WebP decode 及來源 SHA-256 正確。**任何一項無法確認就標記 `NEEDS_VISUAL_REVIEW`，不能標為 verified。**

推薦每題原圖結構：
```json
{
  "questionId":"115-09-2-28",
  "paperCode":"09-2",
  "originalQuestionNumber":28,
  "source":"sudu/data/original/115/09-2/p007-fc88e0109e-v2-w1400-q66.webp",
  "sourcePage":7,
  "crop":[90,780,1310,1220],
  "output":"sudu/data/processed/115/webp-v1/09-2/115-09-2-28.webp",
  "sha256":"calculated_at_generation",
  "qaStatus":"DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA",
  "issues":[]
}
```
範例中的座標只是示意，**不得當成已測量、已製作或已通過 QA 的正式座標**。

圖片產出、圖片真正逐張 QA 通過、原文 OCR 完成、答案候選配對、獨立核對官方答案、SQLite 寫入與讀回成功、平台接入與部署，都是**七種不同的驗收狀態**，不可混成同一個「已完成」數字。

## 本批已交付（2026-10-22）
- `sudu/data/processed/115/questions.json`: 205 個 canonical ID 的**候選題庫**。保留 5 試卷原題號、科目索引、舊擷取文字、答案候選、來源 PDF SHA-256、原頁 WebP、問題清單與未覆核狀態。
- `sudu/data/processed/115/corrections.json`: 15 筆人工視覺擷取的非破壞式修正，含數學公式、09-1/09-2 第 2、4 題封面說明錯配及英語 21-28 題；2 個英文共同材料。**人工轉錄不等於 OCR**。
- `sudu/data/processed/115/inventory.json`: 各科缺圖、缺選項、待複核原因、待處理 ID。
- `scripts/build_115_question_bank.py`: 唯一寫入**獨立題庫 SQLite** 的重建工具，並另輸出 JSON；不觸碰學生 SQLite、教學欄位及平台資產。
- 本批不覆蓋 `sudu/data/years/115.json`、既有會計第 2-6 題圖、`sudu/demo-question-crops.json`、`scripts/build.py` 或任何學生資料。
- 完整單題圖 **尚未完成或提交**。既有 30 張 Demo 圖由 `scripts/build.py` 在建置時依座標產生；原始 35 圖 QA 是歷史記錄，不可當作本次逐張 QA。

## 題數與科目邊界（本批保留、仍待全卷逐題二次覆核）
| 科目 | 試卷 | 原題號 | 現有候選題 |
| --- | --- | --- | ---: |
| 國文 | 00-C | 1–38 | 38 |
| 英文 | 00-E | 1–42 | 42 |
| 數學B | 00-MB | 1–25 | 25 |
| 商業概論 | 09-1 | 1–25 | 25 |
| 數位科技（原卷數位科技概論／數位科技應用） | 09-1 | 26–50 | 25 |
| 會計學 | 09-2 | 1–24 | 24 |
| 經濟學 | 09-2 | 25–50 | 26 |

共 205 筆候選，192 筆既有自動答案配對；**官方獨立覆核為 0**。官方標準答案原頁已在 `sudu/data/original/115/*-answers/`，不能由自動配對提升為 `answerVerified=true`。已核對原頁第 28 題經濟效用表沒有「250 元預算」條件，不可加料。

## 主開發接入與回歸指引（需主開發批准）
1. 從此 PR 指定 commit 取得資料，不要覆蓋主程式或 `main`；先比較最新 main。
2. 檢查 `sudu/data/processed/115/inventory.json`；所有 `reviewStatus` 均非正式覆核，待核對內容不參與正式評分。
3. 執行：
   ```sh
   python scripts/build_115_question_bank.py
   python scripts/build_115_question_bank.py
   ```
   第二次執行應仍為 205 題並讀回完全一致；SQLite 路徑為 `sudu/data/processed/115/question-bank.sqlite3`，靜態匯出為 `sudu/data/processed/115/pages-questions.json`。這是離線候選題庫**不是已部署的雲端資料庫**。
4. **靜態站發布 allowlist**：既有 `scripts/build.py` 不會公開 `sudu/data/processed/115/`。由主開發決定何時納入新 JSON，且必須另外指定 WebP 公開資產。
5. 題圖必須使用各題 `assets.singleQuestionWebp` 加 QA 過關才公開。現有 `existingDemoCropBox` 僅為舊 Demo 的座標，不代表本批新圖已存在。
6. 學習紀錄：共用卷唯一鍵 `115-{paperCode}-{number:02d}`，對照舊 Demo `subject|id` 時使用 subject + originalQuestionNumber。不得將合卷重新編流水號；既有 `09-2` 第 2–6 題仍是 `115-09-2-02` 至 `06`。
7. 主平台維持七科每科五題，合計 35 題。待主開發自行跑既有 `scripts/check_sudu.py`、`scripts/check_tcte_corpus.py`、`tests/sudu_demo_acceptance.cjs`、`tests/sudu_browser_smoke.cjs`、學生歷史與評分回歸，通過且使用者另行授權後才考慮全年公開。
8. 此 PR 不包含部署、資料合併、主 UI 更新或教學詳解。

## 嚴格待辦與缺口
- 170 張左右的新增單題裁切（現有 demo 30 裁切配置＋會計 5 既有題圖；本次分支不含全部實體裁切圖）；逐張 WebP decode、內容視覺 QA、座標/大小/輸出 SHA-256 manifest 尚未完成。
- 英文 21–28 題及封面錯題、數學式本批人工轉錄須逐題複核；尚無 OCR 引擎輸出的新原始文字紀錄。
- 數學與閱讀題組需補獨立共用材料切片、上下文及跨頁順序；所有圖、式、表未完成完整獨立檢查。
- 09-1 第 3 題官方 D 為「會增加」；Demo 寫「不會增加」。**此分支不修改 UI**，請主開發後續修正 Demo。
- 09-1 第 7 題官方答案圖為 B，尚未證實有無後續官方更正或疑義公告。
- 數學 B 第 9/12 題本批有校正文字，仍需二次視覺複核。
- 原稿待核對的 `questionVerified` / `answerVerified` 一律 false；官方修正查核尚未完成。
- 目前腳本未在 GitHub Actions / 本機執行成功驗證；不能宣稱完整入庫及回讀完成。

**官方卷頁視覺核對補正：**09-2 第 25 題是「機會成本」（經濟學），故此合卷科目分界為會計 1–24、經濟 25–50；保留第 25 題 ID `115-09-2-25`。
