# Role A｜113 年國文第 6 題｜原始對聯圖像與跨頁文字校正

**Task** `A-113-C06-ORIGINAL-DIAGRAM-OCR-20261025-11` · Issue #36 CLAIM #6394370304 · Role A 資料來源作者，非 Role B/C 教學、非 Role E 獨立審查者、非 MASTER 發布者。

## 唯一來源與安全邊界

使用前一批已通過的 [Draft PR #72](https://github.com/homelux-huang/7581707/pull/72) HEAD `481734d51928c8e47303718034479feafdf7e45e` 開新隔離分支 `data/role-a-113-c06-original-diagram-ocr-20261025`。本批**僅寫第 6 題獨立候選檔案**，不修改原始官方頁、年份 JSON、先前 5 題原圖與 SQLite、114/115 唯一台帳、另一角色檔案、正式 V4、main 或 Pages。

- 既存 Git 官方題本第 2 頁原像素：`sudu/data/original/113/00-C/p002-67c0d477e9-v2-w1400-q66.webp`，Git blob `6796adb4df977d064baae8a3e066238014d096f6`，實際 SHA256 `2fee23a8e46c17fda589989a3d32eafc032460831e83453a016aaa67b8ef6134`。
- 既存 Git 官方答案第 1 頁原像素：`sudu/data/original/113/00-C-answers/p001-9a6ce177b0-v2-w1400-q66.webp`，Git blob `938f88435a9b21e257f11dfcfda71655e8a7a0c6`，實際 SHA256 `a3c8154f5186c925a9408e4c4b50cd9a0c2b92db2fe3375d3d13d8491b9c7bc3`。
- 原始 PDF 題本 SHA256 `67c0d477e99d07cd59af0e9c75b261692c3089fd5559185f41945de32316093f`、答案 PDF SHA256 `9a6ce177b0aec3f22957635cc9abc21539cf3356471b2e3dec65e550e8f9559a`：**只有歷史 113.json 的記錄**，本輪未重新下載、計算 PDF 檔案 SHA，不能宣稱已驗證正式最終更正 PDF。

## 113-00-C-06 的真實缺陷

題幹問右圖具有**儒家內涵**的對聯，須依上下聯填「○○、□□」。右側完整原始印刷對聯圖含兩行直排文字及下方兩個空方格與圓框。四選項候選：（A）詩書、孝弟；（B）孝弟、詩書；（C）無為、齊物；（D）齊物、無為。**原始印刷標準答案頁第 6 題為 B**。這是「公告答案影像中的答案候選」，尚未逐項完整調查最終更正公告，**`answerVerified=false`**。

舊 `sudu/data/years/113.json` 的 `options[3]` 在真正的選項 D「齊物、無為」後，額外含第 2 頁頁尾及第 3 頁頁首「公告試題僅供參考」等文字。若直接上線，會把其他試卷區塊當成作答選項。這次只修**獨立候選 Q06 的結構化 D 選項**，完整保留舊 `sourceArchiveOriginalOptions` 及其 SHA256，絕不覆寫歷史原始資料或其他 204 題。

原始影像候選裁切 `[90,1472,1310,1881]` 由原始頁解碼 RGB 像素直接 lossless WebP 儲存並逐像素與官方來源比較。**必須經本批真實檢查後才能認定**題號、題幹、對聯兩行與方框圓框、A～D 四項、無相鄰題或頁尾。未完成前狀態 `DRAFT_NEEDS_DIRECT_ORIGINAL_DIAGRAM_VISUAL_QA`。原圖不 AI 重畫、不用 OCR 重新生圖，不得用整張卷代替單題圖。

## 本批產出與 QA 契約

`scripts/role_a_113_c06_source_diagram.py` 對 113 年原始 Git WebP、來源頁 SHA 和歷史 JSON 官答候選 fail closed，將唯一 Q06 的一張原像素候選圖、來源修正 manifest 與獨立**只有 1 題**候選 SQLite 寫入 `sudu/data/processed/113/role-a-c06/`。SQLite `payload_json` 使用排序 canonical JSON，兩次隔離重建整個 DB SHA 相同且 `PRAGMA integrity_check=ok`；`answer_verified/question_verified/teaching_verified/student_ready` 欄全為 0。

`tests/test_role_a_113_c06_source_diagram.py` 檢查原始 WebP Git SHA1／SHA256、圖像 decoded 原像素逐像素相等、完整選項來源 diff、保留污染過的原始文字、正解 B 僅作候選、篡改選項或 WebP 無法維持來源 revision，以及前一批第 1～5 題 SHA 完全不變。獨立 GitHub Actions `.github/workflows/role-a-113-c06-source-diagram.yml` **只允許在本獨立分支提交這 3 份新候選素材**，不能直接改 main 或部署。

本批仍有更正公告全文、PDF 實體 SHA 重查、正式文字 QA、跨作者 E AI 教學審核、原本 V4 各科樣式的 D 實際 8×2 測試以及 MASTER 正式發布驗收未完成；沒有任何理由將 `answerMatchedLegacy=true` 升級 `answerVerified` 或將來源圖像 QA 冒充 E 教學審查。**新 READY=0，新 LIVE=0**。

**主指揮接收建議：** 僅接收已通過實際 CI 及來源圖像目視 QA 的精確 Git 物件與 revision；待最新官方最終更正／答案及完整教學證據通過後才逐題增量發布。下一批 Role A 持續處理 113 年剩餘題庫，優先檢查共用文章、表格、跨頁材料及其他 OCR 跨頁污染，再依 112→104 年遞進，不重做已合格第 1～5 題。

## 真實圖片 QA 與本批結果（主指揮交接）

已逐張開啟原始官方第 2 頁與本題實際 GitHub 單題 WebP，對照原始 1400×1981 畫素。**第一次生成影像**採 `[90,1472,1310,1881]`，SHA256 `289e16a96ceeeb1c691075b0b553adbd9e31652af0821ab24ad77cf8e15daeb7`，上方對聯首字過度貼近裁切邊界、上緣有缺圖風險，已直接判 **FAIL_INCOMPLETE_TOP_RIGHT_COUPLET**、不計 QA PASS。**只局部重裁本題一次**至 `[90,1450,1310,1881]`，與先前第 5 題已驗證的 y2=1450 不重疊；第 1～5 題圖與 DB 完全不更動。

二次直接目視驗收通過的**原始單題影像** SHA256 是 `57064b9f8da602c2894216b5f0ce7577988c2e534272d5da02affd5080f1a071`，Git blob `5e53721a28fd4847430b23839554b1ff808ffd3f`；畫面保留原印刷完整兩列直書對聯文字、下方兩個方框與兩個圓框、題號 6、完整題幹及 A/B/C/D，沒有前題 5、後題 7、頁尾或整頁試卷。所有裁切像素經 Pillow 逐像素比對與原始官方頁相同；**非 AI 重畫**。實際觀察記錄 `sudu/data/processed/113/role-a-c06/VISUAL_QA_ASSISTANT_20261025.json`，綁定上述 image/source SHA、拒絕舊版及精確 reviewer：**ChatGPT Role A，來源圖片自檢，不是不同作者 Role E 教材 QA、非人工教師**。

新結構化來源 Q06 D 僅是原圖真實文字 `齊物、無為`。舊污染 OCR 原文 SHA256 `05c958fcc04582afa87cf57ea3950ff74372c8404f65afe64ceb65d3f5b119d1`，修正後單選項 D SHA256 `ef2366ace26f7bebbe455f7ad0bf1acce820bcea612ac8d0f019eeb293c6eb3c`，來源 revision **`f5dd92e4d8b3184590011569c08977d59e3454d18b7489c3d60aca01f3343730`**。舊污染的 raw 文字不刪除，存於 `manifest.questions[0].sourceArchiveOriginalOptions[3]` 可回查。原始答案圖 B 確認為公告候選，最終更正公告 PDF 仍未完整驗收，獨立 `answerVerified=false`。

候選 SQLite 為**獨立單一題號庫，並非 113 全年度 DB**：兩次隔離重建 SHA256 同為 `8c11159b98dd703688017137ec64acc05c16ebaa171e7f7ce2c0e3eac1323a30`；資料庫 `PRAGMA integrity_check=ok`、唯一一題 canonical payload 與 SHA 一致、四個發布／審查旗標仍 0。完成者僅圖片來源目視 QA，正式 PDF 更正、最終文字審核、E 雙層教材、D 同版 8×2、MASTER 發布皆尚待完成。**新 READY 0、新 LIVE 0。**

CI：針對最終修正版 `tests/test_role_a_113_c06_source_diagram.py` **8 項**與先前已完成 `tests/test_role_a_113_c01_05_source_receipts.py` **10 項**皆需要再次驗證 exact HEAD，舊 SHA 成功不能替代最終 HEAD。GitHub Actions workflow 內只允許 113 C06 manifest／WebP／一筆 SQL 三個來源產物，不可操作主平台；本批 Draft PR 由 MASTER 獨立收件。
