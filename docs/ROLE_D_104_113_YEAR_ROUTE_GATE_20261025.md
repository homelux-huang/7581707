# Role D｜104–113 舊年度於原 V4 年度選單接入（不開放未核准題庫）

## 唯一專案、角色、實際工作租約

- Repository `homelux-huang/7581707`。唯一學生頁面 `sudu/v4-115-multisubject-review-demo.html`；不建立其他頁面或七科通用重製 UI。
- 控制台 Issue #36 taskId `D-104-113-V4-YEAR-ROUTE-FAILCLOSED-20261025-01`，CLAIM [#6394288523](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6394288523)，認領時間依 GitHub 伺服器記錄。
- 專屬新 branch `ui/role-d-104-113-v4-year-route-gate-20261025`，immutable base `b417ec41e3fe7c2ce07c8f78f3f7fc60f519274e`，即 MASTER 原已交回的修正非計算題卡 [Draft PR #62](https://github.com/homelux-huang/7581707/pull/62)。它疊加原 D PR40 英文空白修復與既有 PR35 runtime；不覆蓋原始 35 Demo 與 PR38 21 個獨立驗收矩陣。
- 104–113 現存來源基準 [PR #65](https://github.com/homelux-huang/7581707/pull/65) HEAD `d80200c2aed015471ed595db22be16150d117ab9`，文件 `docs/104-113-SOURCE-BASELINE-20261025.md`。114/115 唯一逐題台帳仍是 PR30；本 PR 不改台帳。
- 原始 main（本批開始時）`57d766e841235b937babf3fe10a8ff44606c7c41`，未受保護。**Role D 不接觸 main/Pages/自動部署或發布器，也不設定 E AI、READY、teacher flag。**

## 接入現況與禁止推定的資料

- 舊年 `sudu/data/years/{104..113}.json` 全部真實存在，五卷 `00-C/00-E/00-MB/09-1/09-2`，總計 2,043 筆 **自動擷取候選**；自報 `questionsFound` 僅 1,876，差 167；自動 `answerMatched` 1,799 **非獨立官答 QA**。各題 `answerVerified`、`questionVerified`、`teachingVerified` 真正為 true 的筆數皆 0。
- 104–113 原紙考科分界尤其 `09-1/09-2` 可能隨年度不同；在 Role A 逐年官方驗證、正式 MASTER 認證後才能接實際科目，現在 runtime **拒絕舊年 09-1/09-2 的既有 115 年分題號猜測**。不能用 115 的舊閾值替舊年自行批准。
- 本批 **沒有任何一題新舊年度課程候選** 被設為可作答。無教學 digest、無原始單題 WebP SHA、無正式更正公告與 E 獨立 QA 的 104–113 題目，均不製造空白假資料或積極觸發 UIQA 通過。

## 實際隔離更新

只更新原系統的兩個既有檔及本角色新檔：
- `sudu/v4-115-multisubject-review-demo.html`：只增 104～113 年（與既有 114/115、Demo 同選單）；`pageYear/changeYear/entryYear` 正確辨識 104–115，不能把 `?year=104` 當 35 題 Demo；無核准年度顯示「尚無已核准題庫」而非永久等待。內嵌 35 題 Demo JSON **一位元未變**，不同科目各自設計、原英語間格與新版國文非計算題改善均保留。
- `sudu/verified-questions-runtime.js`：保持真實 Verified 來源路徑 `data/approved/{year}.json`，只擴大合法年份 104～115（canonical ID 對應同一年）。若讀不到真實正式核准 JSON，**拒絕進入任何作答/答案/解說/錯題頁**，清除當前無關的 Demo 題目視圖與題號，停用該年度作答與復習入口，保持選年與首頁、顯示「舊年原始資料尚未通過官方、WebP、教學與 AI QA」。**不修改先前 Demo 學習紀錄，也不自動轉用 Demo 資料**。
- NEW `tests/sudu_role_d_104_113_year_route.cjs` 真實 Playwright：先從既有 35 Demo 原始學生首頁/年度/科目開始，以真實滑鼠或手機觸控更換年別；每個年別都由真實缺少 `approved/{year}.json` 的 404 HTTP 回應進入拒絕畫面，非 fixture、非假借答題；核對實際 104–113 年來源 JSON SHA256 與 0 審核狀態。用真正 Chrome 繪製繁中字形、檢查 CJK 非 tofu、無水平捲動、錯誤狀態無任何可見／殘留 Demo 題目或 A–D 選項、當年無學生紀錄產生，Demo 記錄前後 byte-equal。另以真實 114／115 頁面做回歸（115 原有 Math B 已核准五題仍可作答）。
- NEW `.github/workflows/sudu-role-d-104-113-year-route.yml` 只讀 CI，透過舊系統原 `scripts/sudu_verified_publish.py check` + `scripts/build.py`、Chromium、Noto CJK 字型與真正本機 HTTP Server 執行，封存來源檔 SHA、HTML/runtime SHA、精確 HEAD、160 張真實年別無發布截圖、異常逐項結果。
- NEW 本交接文件。

## 8×2 範圍與「UI QA」嚴格區分

- 舊年度 104～113 共 10 個**年度路由**，每個年別用 `360×800, 375×812, 390×844, 412×915, 430×932, 768×1024, 1024×768, 1440×900` 與 light/dark 做 160 次瀏覽器操作（非 160 題作答），全測 **唯讀、不可發佈**。
- 兩主題切換使用 Demo 原始真實主題鈕；手機用真實 Playwright `.tap()` 觸控且選年觸發原生 `selectOption()` 事件、桌面用真實滑鼠 `.click()`，不以設定 DOM 任意改成 dark 求 PASS。
- 畫面可以顯示某年選單，不代表這一年題庫已可教或可作答。**此 160 次是「年度路由與不洩漏未核准題」的安全技術矩陣，完全不能替代任何 104～113 真實題目完整題幹／四選項／原圖／解說 digest 的 8×2 UIQA**。等 A/B/C/E 精確資料到位，D 再逐題 QA 原圖、教學、高亮、計算、答題、錯題紀錄與 SOURCE SHA。
- 原有 Demo 35 題獨立渲染檢查及 114/115 PR38／PR40 逐題原始 QA 不重新「設 PASS」；MASTER 獨有正式發布與同 SHA LIVE 驗證責任。

## 測試與 RETURN

- CI 每次 **只接受同 HEAD**，不借舊 CI。完整 `historical-year-gate.json` 記每個實際 `sudu/data/years/{year}.json` 的 SHA、2,043 候選與 0 E/A/B 認證、每次截圖、mobile touch/desktop click、CJK、HTML/runtime/字詞選單與歷史發布結果。
- 精確 commit、Actions run/job、ZIP SHA、錯誤、PR 和 E 待審事項於 CI 結束後寫回唯一 [Issue #36](https://github.com/homelux-huang/7581707/issues/36)；若失敗仍留所有斷言，修復同一有界任務再重跑；不得使用假證據或批次改 READY。
- 現階段：**104–113 年新 READY=0、新 LIVE=0、新官方教學 UIQA=0；114／115 原有成果與 main/Pages 一律不變**。5 分鐘 watchdog 仍為 MASTER Draft PR #66（直到 main 合併前不是真正啟用的排程），本 Session 非背景常駐執行者。


## 額外有界 V4 錯題復習隔離返修（Issue36 D-104-115-DEMO-REVIEW-SEED-SEPARATION-20261025-02）

- 第二次 CLAIM [#6394349645](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6394349645) 使用本分支前一個已完成 CI HEAD `95b5b176171f2535833b7ef26d11b10bb488aaee` 作基底。未更動其他角色租約；本改動僅原始 HTML 的 `renderReview/seedDemo` 兩段與本 D 測試、交接。
- 真實 bug：舊 `renderReview()` 以「year 不等於 114 或 115」判斷 Demo，新增 104～113 路由後會被認成 Demo。未來 A/B/C/E 逐題核准正式舊年度時，將可能把「Demo：建立跨科錯題樣本」顯示給正式學生；更嚴重的是原 `seedDemo()` 缺少 year guard，會把原學習 `state.records` 裡的跨科錯誤次數寫入正式年度歷史。不能因目前舊年度沒有已核准題而放任這個隱性錯誤。
- 修正：統一 `isDemoRoute()`，**只有網址沒有 year 或明確 `?year=demo`** 才允許 Demo 範例；舊年度 104～113、114／115，甚至不支援的 URL 都不能顯示／呼叫 `seedDemo`。不是移除原 Demo 功能，也沒有改 35 題原資料。
- 本 D 測試先真實觸控/點擊進入原 Demo 的錯題頁，確認原 `#seedDemo` 仍存在；再訪舊年度時對 `renderReview()` 和 `seedDemo()` 執行**只做拒絕的負向探針**，必須看不到 Demo 種子、同時學生 Demo 歷史逐位元不變。新加的 115 正式數學 B 5 題檢查確保也不能出現種子或改變正式作答紀錄；此程式安全負測不是虛構原題與老師 QA 證書。
- 原 104–113 160 真實 HTTP 404／8×2／CJK／觸控與 114/115 既有核准題目回歸斷言**全部保留不刪**。最新精確 HEAD 必須重跑 CI，之前成功的 `95b5b176...` 不是新修正版本的 UIQA。READY、main、LIVE 仍未增加。
