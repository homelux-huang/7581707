# 115 學年度完整題庫｜資料工程交接與單題 WebP 強制驗收契約

- 專案：`homelux-huang/7581707`（同倉庫，不建立新網站、外部資料庫）
- 資料分支：`data/115-full-year-question-assets`；Draft PR：https://github.com/homelux-huang/7581707/pull/1
- 建立時 main 基準：`40ffa920d8efb8e7dc54471a62bb70ecb14ee096`，合併前須重新與最新 main 比較
- **資料工程只完成資料資產，不改 UI、不觸碰學習紀錄、不合併 main、不部署 LIVE、不開放全年考題**
- 本文描述生成管線與驗收契約；即使 Actions 成功也**不代表所有原題經獨立人工視覺核對**

## A. 單題 WebP 原圖強制規則（所有 205 題）

**每張單題 WebP 只能出現此題的官方原題號、完整題幹、必要條件、圖表／公式／單位、(A)～(D) 四個完整選項。不可有整頁試卷、上一題或下一題題幹與選項、非必要頁首／頁尾／頁碼。**

1. 僅從倉庫 `sudu/data/original/115/{paper}/p###-...webp` 的 **官方原卷像素** 按座標裁切，不得 AI 重畫、重排文字、以擷取後重新排版冒充官方照片。
2. 題組、共用閱讀文章、圖表、跨頁資料另外裁切獨立的 **共用原始像素 WebP**，用 `sharedMaterialId` 關聯至每個相關題目；不可把其它題號及選項放進單題圖。
3. 跨頁/多張原圖用 `assets.parts[]` 逐張與順序標示，不能為了塞進一張而遺漏必要內容。
4. 原始頁 WebP 永遠保留，不覆蓋；版本與 SHA 變更須新檔名/新資料夾，曾經有誤的舊候選版本也保留供稽核。
5. 各圖 manifest 含 `questionId/year/paperCode/originalQuestionNumber/source/sourcePage/sourceSize/crop/sourceSha256/sourcePdfSha256/output/outputSize/sha256/processingVersion/qaStatus/issues`。
6. 逐張對照原卷後才能標示 `qaStatus=PASS`：題號科目、題幹、必要條件、四選項、圖／表／公式／上下標及單位、無相鄰題、無頁首頁尾、字體清晰、WebP decode、來源 SHA 正確；記錄審查者/日期/所審核圖片的 SHA。
7. 坐標合法、檔案存在、PDF 標號對應、OCR 高信心、WebP 解碼、流水線綠燈 **都不等於人工內容核對通過**。
8. 已完成歷史 QA 的 30 張 Demo 圖：僅在圖片 SHA 與 `sudu/DEMO_VISUAL_QA.md` 的每筆 `PASS` SHA **完全相同** 時沿用歷史 QA 證據（`freshReviewInThisRun=false`）；不是本批新逐張審閱。
9. 既有會計 2～6 題 inline WebP 二進位保持原狀，新資料產物要保留來源方法及處理版本，不覆蓋原始或教學內容。
10. 存疑者 `DRAFT_AUTOMATED_NEEDS_INDIVIDUAL_VISUAL_QA`，不得誤標 `questionVerified=true`。

### 原圖版本與已找到的例外

- `webp-v1/`：初版草稿；數學B第1～4題曾誤將卷首「參考公式」當作題目，不可使用。
- `webp-v2/`：利用官方 PDF 內原題號定位，修正數學B第1～4題；第1題圖說曾被裁掉。
- `webp-v3/`：修正數學B第1題含完整座標圖及「圖（一）」圖說；將英文、國文和專業科目題組做獨立像素裁切。
- `webp-v4/shared/`：針對目視發現的共用材料圖切邊問題產生**新版本**；包括商概18～19曾混入前題尾行、商概24～25表格下緣不足、數份國文共用材料最後一行靠近切邊；舊圖保留。
- **以最新 `webp-manifest.json` 中每筆 `output` 路徑為準**。不能因為檔案版本資料夾存在就當成最新版或 QA PASS。

## B. 七個學習科目與原題號（不重新編號）

| 科目 | 官方卷碼 | 官方原題號 | 應有題數 |
|---|---|---|---:|
| 國文 | 00-C | 1–38 | 38 |
| 英文 | 00-E | 1–42 | 42 |
| 數學 B | 00-MB | 1–25 | 25 |
| 商業概論 | 09-1 | 1–25 | 25 |
| 數位科技（原卷為「數位科技概論／數位科技應用」） | 09-1 | 26–50 | 25 |
| 會計學 | 09-2 | 1–24 | 24 |
| 經濟學 | 09-2 | 25–50 | 26 |
| **合計** | **5 卷** | | **205** |

`115-09-2-25` 是經濟「機會成本」，不可按分科第1題重新編號。永久 ID = `115-{paperCode}-{officialOriginalNumber:02d}`；所有學生 `科目|原題號` 歷史紀錄接入時映射到此 ID，不得刪除或重置舊紀錄。

## C. 現有成果及其實際驗收意義

| 產物 | 用途 | 不表示 |
|---|---|---|
| `questions.json` | 205 筆 canonical ID、原題 OCR／擷取與校正、選項、答案候選、來源、圖片/共用材料連結 | 已教學、可正式計分 |
| `corrections.json` | 21 筆依官方影像人工文字校正（含數學B、會計第8題及英文題組） | 重新跑 OCR、已有人工第二次覆核 |
| `webp-manifest.json` | 205 張正式候選單題原始像素圖之座標、SHA、版本、圖片狀態 | 205 張全部逐題目視 QA PASS |
| `anchor-report.json` | 官方 PDF 內數字/座標候選與歧義清單 | 文字無錯或答案正確 |
| `ocr-raw-candidates.json` | Tesseract chi_tra+eng 需要辨識的 raw OCR 紀錄，保留引擎與時間；其餘沿用既有 PDF 文字層 | 所有公式已核對 |
| `official-answer-evidence.json` | 5 卷官方答案 PDF SHA-pinned 文字解析，205/205 與候選字母一致 | 獨立人工核對（仍為0） |
| `question-bank.sqlite3` | 離線題庫，**獨立於**學生資料庫的 SQLite | 已在公開 API 建線上 DB |
| `pages-questions.json` | GitHub Pages 形式的候選 JSON 匯出，未列入公開 build allowlist | 主平台已發布 |
| `inventory.json`、`VALIDATION.json` | 分科生成/OCR/QA/答案/DB 分開列、嚴格核對 | 全年學生已可作答 |

共用材料 **19 組**：英文7、國文7、商概4、會計1。圖片 QA 必須和題目獨立核對，不可只以題目圖片有連結就通過。未經獨立覆核的 `questionVerified`／`answerVerified` 一律 `false`。

## D. 來源及重要疑點

- 官方唯一版本入口：https://web1.tcte.edu.tw/EXAM/115_4y/，所有 PDF SHA-256 與來源寫在題庫／manifest。PDF 版本如有變更，停止沿用舊 QA。
- 國文第2題 D「梯航萬國，能使帝京元氣充然」不可摘要丟字；第9題保存全部①～⑤。
- 數學B第9題完整 L₁ 與 L₂、#12 完整聯立方程組，#13 A～D 是圖像選項必須靠原始 WebP。
- 商概第3題官方 D 是**「會增加經營風險」**，LIVE Demo 曾寫成「不會增加」，主開發須修正 Demo（本分支不能動 UI）；第7題官方候選 B，需另查官方疑義/更正公告。
- 經濟學第28題效用表與價格已保留；原卷沒有「250元預算」，不可虛構。
- 會計第2、4題舊資料誤讀封面說明已以原卷人工校正，第8題另校正；既有第2～6題圖和教學不被此管線覆蓋。

## E. 主開發跨 Session 接入步驟（不在本資料分支部署）

1. 從 **Draft PR 的指定 SHA** checkout；先 `git fetch origin main data/115-full-year-question-assets`，核對主開發最新 main 改動與資料 PR 無衝突。
2. 執行 `python scripts/build_115_question_bank.py` **兩次**，確保重匯入後仍為205題並完整讀回；資料庫只在 `sudu/data/processed/115/question-bank.sqlite3`。
3. 執行 `python scripts/audit_115_processed.py`；讀取 `inventory.json` 各科照片生成／真正視覺 QA／OCR／答案比對／入庫讀回數，不能混為完成率。
4. 將 `questions.json` 題目按 `questionId` 配對 `webp-manifest.json` 的最新版 `output`，載入題幹後顯示**該題自己的圖片**；如 `sharedMaterialId` 存在，額外載入共用材料圖並依需要置於題前。
5. **不得將 `sudu/data/original/115/.../p###...` 整頁試卷設為正式單題圖**。找不到個別 crop 就標待處理，不能偷用整頁。
6. `scripts/build.py` 目前公開檔案 allowlist 不含 `sudu/data/processed/115/`；由主開發在獨立回歸測試與使用者批准全年開放後自行擴充 publish allowlist。此 PR 不擅改主平台公開。
7. 驗收需檢查 `python scripts/check_sudu.py`、`python scripts/check_tcte_corpus.py`、`node tests/sudu_demo_acceptance.cjs`、Playwright、35 題 Demo 和所有 localStorage/IndexedDB 首次錯題及成績紀錄，確保不影響既有教材與學生資料。
8. 主平台**維持每科5題、35題 LIVE Demo**，直到使用者另行授權開放全年資料。本分支不能合併 PR 或正式部署。

## F. 嚴格進度與交付界線

- 雲端生成單題圖和官方答案文字層比對可以自動化；**OCR 校正、圖表完整、每題的視覺 QA，以及官方疑義更正文件仍需要逐題核對**。
- 已完成歷史 QA 的 30 張 Demo 圖僅在其 SHA **不變** 時可沿用其 PASS；其他 175 張和 19 份共用材料都應在缺少目視證據時維持草稿。
- 產生檔案 ≠ 提交 PR ≠ 寫入 SQLite ≠ 教學詳解完成 ≠ 主平台接入 ≠ 正式 LIVE 部署。
- 本分支只新增/修改資料工程相關檔案與專屬資料 workflow，主開發檔案和其他年度均維持原樣。
