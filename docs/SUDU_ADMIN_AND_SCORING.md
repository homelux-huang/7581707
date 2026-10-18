# 7581707 統測速讀｜正式配分、歷次測驗與私人後台

更新日期：2026-10-19。學習平台：https://homelux-huang.github.io/7581707/sudu/

## 本次交付的實際界線

- 前端與伺服器計分均有可執行測試；正式題目必須分別通過原題、答案、完整配分及送出快照版本檢查，才允許正式數字分數。
- `scoring-rules.json` 已由空陣列補為 **10 份有原卷影像證據的基礎配分記錄**（114、115 年，各 5 卷）。`basePointsVerified=true`，但完整 `verified=false`：尚未逐卷完成更正／送分公告、全部原題答案及非選擇題閱卷細則覆核。這不是 10 份已可自動計分的正式試卷。
- 已實際啟動僅監聽 `127.0.0.1` 的後台，使用臨時測試資料庫驗證登入、強制改密碼、同步、改分、分享隔離與撤銷、登出及資料刪除。測試結束刪除測試資料庫，沒有上傳學生資料。
- **本次未部署 Admin API；沒有已驗證的正式 API 網址、HTTPS、持久磁碟或生產備份排程。** `render-admin.yaml` 是待設定的部署描述，GitHub Pages 的成功與後台上線是兩件事。
- 私人後台已增加安全控制及可驗證的備份／還原命令；正式服務仍需擁有者提供私密環境變數、雲端服務權限、持久儲存與資料保留政策。不得把本機通過測試稱為正式後台已上線。

## 逐卷配分證據

本次逐張覆讀 `sudu/data/original/index.json` 所列 114、115 年五種試卷第 1 頁。每份規則都保存 `sourceUrl`、`sourcePage`、`sourceImage`、`sourcePdfSha256`、覆讀範圍、時間及未完成覆核項目；不是依年度或題數猜配分。

| 年度 | 卷別 | 封面可核對的配分 | 整卷滿分 | 人工閱卷部分 | 完整規則狀態 |
| --- | --- | --- | --- | --- | --- |
| 114、115（各年獨立來源） | 09-1 專一 | 單選 50 題，每題 2 分；答錯不倒扣 | 100 | 無 | 更正／送分及答案覆核待完成 |
| 114、115（各年獨立來源） | 09-2 專二 | 單選 50 題，每題 2 分；答錯不倒扣 | 100 | 無 | 更正／送分及答案覆核待完成 |
| 114、115（各年獨立來源） | 00-MB 數學 B | 單選 25 題，每題 4 分；答錯不倒扣 | 100 | 無 | 更正／送分及答案覆核待完成 |
| 114、115（各年獨立來源） | 00-C 國文 | 單選 38 題，每題 2 分，小計 76 分 | 100 | 寫作測驗 1 題，24 分 | 非選擇題閱卷細則等待完成 |
| 114、115（各年獨立來源） | 00-E 英文 | 單選 42 題，每題 2 分，小計 84 分 | 100 | 填充 1 題 4 分、句子重組 1 題 6 分、中譯英 1 題 6 分 | 非選擇題閱卷細則等待完成 |

官方來源入口：

- https://www.tcte.edu.tw/index.php?mod=TVETest/down_exam4y
- https://web1.tcte.edu.tw/EXAM/114_4y/
- https://web1.tcte.edu.tw/EXAM/115_4y/

各卷來源的完整 downloader URL 與 PDF 雜湊直接列於 `sudu/data/scoring-rules.json`。90～113 年尚未新增已覆讀完整配分記錄，不能從上述兩年外推舊年度制度。

### 配分資料的審核欄位

`basePointsVerified` 只驗證封面題數與基礎配分。`verified` 是完整規則開關，必須包含適用年度／卷別、逐題配分、總分、題型、正式來源與覆核紀錄。`manualSections` 列出需人工評分的部分。`version` 用於追溯規則；更動版本使舊成績回到待覆核，保留原始送出紀錄。

多個官方接受答案由題目 `acceptedAnswers` 處理，不能把第二個接受答案算錯。送分題使用有依據的 `itemRules[number].fullCredit`。多選只有兩種已明示的計分方式可用：官方全對才給分，或完整列出的官方選項組合配分表；沒有規則即待核實，不能自行選擇公式。正式資料目前未填入任何猜測的送分／多選規則。

## 前端狀態與送出快照

`SUDU_SCORING` 在學習頁、Dashboard 使用同一套計分邏輯。

| 狀態 | 意義 | 分數 |
| --- | --- | --- |
| `incomplete`／未考完 | 目前仍有可作答題未答 | 不顯示數字 |
| `corpus-pending`／題庫待補 | 已答完目前可用題目，但原卷缺題、題數未核實或抽到了封面說明 | 不歸咎學生漏答，不稱全卷完成 |
| `ready`／已作答待送出 | 全部原卷題號都有可保存的選擇 | 未送出，不顯示數字 |
| `pending-verification`／已送出待核實 | 快照已保存；原題／答案／完整配分或版本尚未通過 | 不顯示數字 |
| `pending-marking`／已送出待閱卷 | 選擇題可算小計，但存在作文／其他非選擇題 | 小計與整卷總分分開；正式總分為空 |
| `scored`／可顯示成績 | 送出快照、完整原題、答案與整卷配分均核實 | 顯示依規則計算的分數與滿分 |

純影像正式題可依原卷 A～D 保存作答。其原卷、答案未經覆核時仍不計數字分數。`cover_instruction_extraction_suspected`／`questionPresentation=original_image_required` 的誤擷取封面不得作為全卷完整證據。

### 不覆蓋既有資料

- `attempts`、`reviewHistory`、`reviewAnswers` 與首次錯選不因重考或改分刪除。
- `examSubmissions[year/paper]` 保留第一份送出快照；`examSubmissionHistory[year/paper]` 保存後續各次測驗。
- `startNewExam` 只新增本次測驗識別與獨立 `choices`，不清除舊作答。答題時 `recordAnswer` 同步保存本次測驗事件。未完成的新測驗不被另一個開始操作覆寫。
- 每份快照保存年／卷、開始及送出日期、逐題選擇、已知作答事件、題數與原題／答案變更指紋。指紋是變更偵測，不是驗證學生身分的密碼或數位簽章。
- 沒有開始時間或有效時長的舊紀錄顯示 **N/A**。`elapsedMs` 明示包含離開網頁的經過時間；沒有量測活躍時間，`activeMs=null`，不得捏造專注秒數。
- `examSubmissionHistory` 隨原有備份匯出與還原合併。本機學習代碼維持原有識別，不因新測驗、重整或後台同步重新產生；此代碼本身不是跨裝置登入帳號。

## 私人後台安全與同步

### 帳密、Session 與請求

- 管理帳號可為 `admin`。只有 `SUDU_DEV_ALLOW_ADMIN_ADMIN=1` 本機模式允許初始化 `admin/admin`；此模式只監聽 loopback，若同時設定公網服務 URL 則拒絕啟動。
- 正式初始密碼由私密 `SUDU_ADMIN_INITIAL_PASSWORD` 提供，至少 12 字元，不寫入 Repository 或前端。初次登入必須改密碼；未改之前不能查學生或改分。
- 密碼採含隨機 salt 的 PBKDF2-SHA256（450,000 次）；Session／學生權杖／分享權杖只保存 SHA-256 雜湊。
- Session 8 小時到期；正式 Cookie 使用 HttpOnly、SameSite=Strict、Secure。改密碼旋轉 Session 並撤銷所有舊 Session。登出會在伺服器移除 Session。
- 登入限流為每來源 5 分鐘 5 次失敗；建立同步識別也有限流。CSRF token 用於管理端所有變更。學生同步採獨立 Bearer token，不以管理 Cookie 授權。
- CORS 只允許設定的來源；管理頁於 API 相同來源操作。拒絕非 JSON 內容、不合格式輸入、過大 body 與非有限數字。管理／分享回應 no-store、no-referrer，分享權杖不寫入存取日誌。
- 未登入讀取學生列表回應 401；未改初始密碼回應 403。只有持該學生權杖者可同步／撤銷／刪除自己資料。

### 伺服器不採信前端正誤與分數

`clean_state` 只接受允許的學習欄位，忽略未知的密碼、access token 等。每個作答正誤依伺服器讀取的正式題庫重新計算；未核實時 `correct=null`。裝置歷史回報的 `correct` 另存為 `reportedCorrect`，不能冒充伺服器核實結果。

裝置曾記錄的錯題不因未核實而隱藏：報告把已核實錯誤次數、待核對歷史錯選及不同錯題數分開。首次作答即錯與之後才首次答錯另有統計；分享指定卷時，題目、日期、事件次數、送出快照全部先按卷篩選。

每次同步採 append-only 合併。重新傳相同事件不重複，傳舊備份／空紀錄不能抹除已上傳的歷史，同一送出識別不能覆寫原答案。歷次快照由伺服器的正式來源重新核對，不採信客戶端傳來的 `score`。只有複習紀錄而沒有首次作答陣列的錯題也保留；若歷史事件的來源指紋已變，報告改列待覆核的歷史錯選，原始事件與當時判分證據不修改。多選事件保存完整選擇集合，由伺服器檢查集合及題型，拒絕重複選項或把多選傳成單一選項。

### 學生控制

學生先在 Dashboard 輸入私人 API 的 HTTPS 根網址並明確同意，才建立獨立的隨機同步權杖及上傳學習紀錄。沒有同意時不傳資料，也不要求下載或匯入 PDF。

- 「停止同步」只關閉後續上傳，保留權杖與伺服器資料，仍可選擇恢復／刪除。
- 「撤銷同步權杖與分享」使該權杖與其分享立即失效；伺服器學習資料仍保留。之後若要刪除，須由私人後台管理員處理，介面明確說明。
- 「刪除伺服器紀錄」刪除學生資料、人工改分及分享，撤銷權杖；不刪本機作答或備份。
- 管理員也可在詳細報表明確確認刪除該學生後台資料。

### 管理員改分與分享

改分只接受已送出試卷及指定送出識別，必須有有限數值、至少 8 字理由及 HTTPS 依據；已核實滿分存在時不得超出。每次保存原分、新分、官方計算分數、修改人、日期、理由、來源、送出識別與規則版本，並增加 audit 記錄。UI 可查看各次修改。

人工調整是另列欄位，**不修改學生選擇、官方答案，也不把人工調整冒充官方自動計算**。完整作文／非選擇題逐項人工評分與核發正式整卷分數流程尚未完成；目前只能列待閱卷和獨立的管理員調整。

分享 URL 使用高熵隨機權杖，七天到期，可於管理頁列出並撤銷。指定試卷分享會過濾原題、選項、錯題、分數、所有計數與日期，並移除學生姓名、ID 及全域同步時間。分享報告沒有管理 Session、密碼或資料庫金鑰；讀取報告不提供管理權限。

## 私有資料庫、遷移與備份

SQLite 路徑由 `SUDU_DB_PATH` 設定，檔案 owner-only 權限。既有資料庫增加送出識別、配分版本等欄位前，先以 SQLite backup 建立 `private-before-schema2-*.sqlite3` 並檢查完整性；不重建學生資料表或清除既有紀錄。

私密離線工具 `backend/backup.py`：

```bash
python backend/backup.py backup /private/path/private.sqlite3 /private/backups/sudu-20261019.sqlite3
python backend/backup.py verify /private/backups/sudu-20261019.sqlite3
python backend/backup.py restore /private/backups/sudu-20261019.sqlite3 /private/restore/new-private.sqlite3
```

備份使用 SQLite 一致性備份，不直接複製可能未合併 WAL 的主檔；完整性檢查通過後產生私密 SHA-256 sidecar。還原先驗雜湊與資料庫結構，只能寫入新的目的檔，不覆蓋正在服務的資料庫。HTTP 不提供資料庫／備份下載路由。

**正式營運尚待完成：**雲端持久磁碟的故障／重啟驗證、私密異地備份排程與保留期限，以及還原舊備份後如何重播最近的撤銷／刪除紀錄。不可還原舊資料後讓已刪學生、已撤銷分享／權杖復活；需要獨立、持久的刪除／撤銷流水帳及運維驗收。本次有備份／還原測試工具，沒有建立雲端定期備份排程。

## 公開發布的隱私保護與同版本驗收

`scripts/build.py` 使用明確 allowlist，只複製根層公開 HTML、`assets` 靜態資產、`sudu` 前端程式及核准的官方 JSON／WebP。不複製 `backend`、資料庫／WAL／SHM、環境檔、學生備份、tests、docs 或部署 yaml；拒絕可把私密資料偽裝成 HTML 的 symlink。

Pages 的 `verify → build → deploy` 依賴同一 `target_sha`：JavaScript／JSON、Dashboard、計分、倒數、Python provenance／後台／防洩漏測試、全部 WebP 解碼稽核及 Chromium 全數通過，才建置並發布。瀏覽器測試服務 `_site`，以驗證真正的 allowlist 產物。`sudu/release.json` 回報正式產物的 commit。

原題／答案 bot 與教學 bot 提交後，明確 dispatch 完整 Pages gate 並帶入 `git rev-parse HEAD`，不能靠 bot push 自動觸發其他工作。影像變更與其導致的原題／答案覆核失效、manifest 與稽核報告在同一 commit 提交。三個會寫題庫的 bot 共用 `tcte-corpus-update` concurrency 並在執行時 checkout 最新 `main`，避免彼此同時修改索引及覆核狀態。

## 已執行測試與待驗證項目

| 驗收 | 本次執行方式／結果 |
| --- | --- |
| 前端計分及資料保存 | `node tests/sudu_scoring_test.cjs`：17 項情境通過；未考完、缺題、無規則、待閱卷、官方多答案、送分、多選明示部分給分、未知時間、版本變更、新測驗及快照不可覆寫 |
| 私人 HTTP／資料庫 | `python -m unittest discover -s backend/tests -v`：18 項通過；真實 loopback HTTP、Session、CSRF/CORS、獨立伺服器判分、分享隔離、改分、刪除／撤銷、私密備份還原、遷移前備份、跨執行環境來源指紋一致、待核對歷史錯選不遺失、只有複習紀錄仍可分享、來源變更後歷史待覆核、多選事件保存 |
| 公開 build 隱私 | `tests/test_public_build.py`：3 項通過；私密資料／環境檔／學生 JSON／symlink 不進公開產物 |
| Admin／分享真實瀏覽器 | `node tests/sudu_admin_browser.cjs`：真實 API 登入→改密碼→同步→改分→分享→撤銷→登出；320、375、390、430、768、1024、1280、1440 × 深淺主題 × 2 頁，檢查不溢出及一般文字／按鈕對比至少 4.5:1 |
| 正式 Admin HTTPS／持久磁碟 | **未部署、未驗證**；無正式網址或可用私密雲端部署設定 |
| 全年度完整配分／正式整卷成績 | **未完成**；10 份封面基礎配分覆讀，完整規則 verified 仍為 0，完整可評分試卷仍為 0 |

以上本機測試不可代替正式發布證據；本批 commit、GitHub Actions 與 Pages 實際狀態由 `SUDU_HANDOFF.md`／`SUDU_PROGRESS_TRACKER.md` 的同版本證據欄記錄。
