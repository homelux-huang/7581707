# 7581707 需求與驗收追蹤

更新：2026-10-19（Asia/Taipei）。B1 的 commit、Actions 與正式部署版本統一記於 [SUDU_HANDOFF.md 的批次證據](SUDU_HANDOFF.md#本次批次證據)。在該證據填入前，以下「通過」只指已執行的本機驗收。內容覆核未完成不因結構測試成功而變成完成。

| 需求 | 現況 | 待辦／阻塞 | 修改檔案 | 驗收標準 | 測試結果 | commit | 部署版本 |
|---|---|---|---|---|---|---|---|
| 最新main接續，不退回舊版 | 已核對495cc92 | 每次推送前再讀HEAD | 全批次 | 非force，保留他人更新 | 初始HEAD與Actions已讀 | B1 | 見交接證據 |
| 年度／科目／個人學習Dashboard | 已實作 | 無 | workspace.js/css、app.js | 獨立三面板、第三完整名稱、卷在科目 | Chromium通過 | B1 | 同上 |
| 移除選單歷年試卷／教材入口 | 已實作 | 每題來源與年度續答保留 | index.html、workspace.js | 無失效入口 | DOM與操作通過 | B1 | 同上 |
| 0ms收合及跨縫操作 | 已實作 | 無 | workspace.js/css | 離開即關、Hover橋接、觸控／鍵盤／Escape | 真實Chromium通過 | B1 | 同上 |
| 右側匯出與主題ICON | 已實作 | 無 | workspace.js/css | 移動原節點、8尺寸不溢出 | 8×2通過 | B1 | 同上 |
| 唯一底部浮動切題 | 已實作 | 無 | workspace.js/css、app.js | fixed正中、首尾disabled、非學習頁移除 | 8×2與320×480通過 | B1 | 同上 |
| 全部題號圓球 | 已實作 | 無 | workspace.js/css | 真實題數、ID映射、換行、accessible狀態、動態padding | 跳題／刷新／篩選通過 | B1 | 同上 |
| 答後先保存與解說捲動 | 已實作 | 未核實內容仍N/A | app.js、workspace.js | 保存先於顯示、位置不被遮、reduced-motion | 整合與P0通過 | B1 | 同上 |
| 保留自訂排序 | 已實作 | 無 | workspace.js | 設定不變、答後暫時優先閱讀 | 真實localStorage比對通過 | B1 | 同上 |
| 全站深色與自然換行 | 已實作 | 持續新增內容時沿用tokens | base.css、workspace.css、dashboard.css、admin/share | 學習／Dashboard／錯題／管理／分享不溢出、對比≥4.5 | 學習最低5.382、Admin/share32組通過 | B1 | 同上 |
| 逐題原卷WebP | 已實作前端及補卷 | 逐題頁碼、裁切與共用題組仍待覆核 | original_images.js/css、tcte_source_images.py、original/ | 真圖可讀、來源頁碼尺寸、放大、延遲載入與重試 | 整合通過，全圖decode見稽核 | B1 | 同上 |
| 官方答案WebP | 已實作前端及補卷 | 90HTML及缺漏來源；不得冒充已核實答案 | tcte_answer_images.py、answers.json | 答前無整頁，答後主動展開 | 真圖與答前隱私通過 | B1 | 同上 |
| 全庫原色RGB | 已修生成器 | 需實際bot生成與解碼後確認，不把舊灰階當原色 | tcte_source_images.py、workflows | RGB、舊版本保留、hash/尺寸正確 | 原子寫入及RGB fixture通過；全库狀態見稽核 | B1／影像bot | 同上 |
| 90–115正確商業卷別 | 已查26官方目錄 | 逐題混合科目仍待覆核 | tcte_catalog.py、official_loader.js、official-paper-catalog.json | 90–91=14、92–97=13、98+=09 | 98回歸通過，93補100純影像紀錄 | B1 | 同上 |
| 答案配對／覆核分離 | 已遷移 | 4304配對仍須獨立覆核 | tcte_verification_migrate.py、years/、loader | 保存legacy來源證據，未核實不判紅綠 | 可重複遷移／歷程保留通過 | B1 | 同上 |
| 英文／國文Hover | 互動完成，2詞有來源 | 大量語境、IPA、同反義與新聞待補 | subject_hover.js/css、hover-cards.json | 點詞不答題、資料不足N/A、不自動出聲 | 8×2及Escape／點按通過 | B1 | 同上 |
| 數學／會計／經濟／商概／科技卡 | 題目級互動可用 | 各題可靠內容仍待補 | subject_hover.js | 不做影像逐字假Hover、不把一般卡算教師解析 | 流程通過；內容未完成 | B1 | 同上 |
| 逐題教師詳解與全部選項理由 | 完整欄位和審核流程已實作 | 大量原題／答案／推理待核；草稿不可標已核實 | app.js、tcte_teaching.py、tcte_preserve_teaching.py | 正解理由＋每錯項原因＋四選項自編延伸 | 欄位／保留測試通過；數量看audit | B1／後續草稿 | 同上 |
| 教材版本章節頁碼核實 | 未完成 | 當年度彰商書單及精確章節缺乏核對證據 | app.js、ANSWER_EXPLANATIONS.md | textbookVerified獨立、未知明示待核實 | 不再顯示未核實章節為真 | B1 | 同上 |
| Dashboard兩個續答區 | 已實作 | 無 | dashboard.js | 載入正確年卷科，首未答，保留身份與答案 | 真實115卷名／狀態均通過 | B1 | 同上 |
| 累計錯誤→全部曾錯 | 已實作 | 缺失題保持占位及歷史 | app.js、dashboard.js | 事件數與不同題數分離，可篩選重答 | 首次答對後錯、後答對仍保留通過 | B1 | 同上 |
| 學習備份／還原相容 | 已實作合併 | 裝置本機不是帳號同步 | dashboard.js | 先備份、可重複、不覆蓋身份／首次／送出 | dashboard單元與瀏覽器保存通過 | B1 | 同上 |
| 正式配分非空 | 10筆基本配分有封面依據 | 完整規則0；90–113與歷年更正／送分待查 | scoring-rules.json、exam_scoring.js | 選擇小計不冒充總分，需閱卷標待閱卷 | 17情境通過 | B1 | 同上 |
| 開始／作答／送出／重考歷程 | 已實作 | 舊資料時間N/A、活躍時間尚無量測 | exam_scoring.js、app.js | 只算有效snapshot、原送出不可覆蓋 | 不完整／缺題／更版／重考通過 | B1 | 同上 |
| 授權管理員改分 | 本機真API可用 | 正式API尚未部署 | backend/server.py、admin.html | 原分新分人時理由依據、學生／標答不動 | HTTP與Chromium通過 | B1 | 未部署 |
| Admin帳密與Session安全 | 本機通過 | 正式私密初始密碼／HTTPS服務權限缺 | backend、render-admin.yaml | admin/admin僅本機、强改、限流、過期、登出、CSRF | 18真HTTP測試通過 | B1 | 未部署 |
| 同意同步／停止／刪除／撤銷 | 本機通過 | 正式持久資料庫與還原策略需驗證 | learning_sync.js、backend | 伺服器重驗、無默認上傳、可撤權 | 真HTTP與流程通過 | B1 | 未部署 |
| 分享限卷／期限／撤銷 | 本機通過 | 正式服務未配置 | backend、share.html | 隨機token、無管理權、不泄漏其他試卷 | 限卷firstWrong隔離及撤銷通過 | B1 | 未部署 |
| 私密資料不得進Pages | 已修高風險整repo複製 | 新增公開資產須進allowlist | scripts/build.py、test_public_build.py | sqlite/env/備份/token/測試不得發布，拒symlink | 3隔離測試通過 | B1 | 同上 |
| 持久DB與私密備份還原 | 程式與本機還原驗收 | 缺雲端持久卷、排程、實際異機還原 | backend/backup.py、docs | 私密備份、災難還原、撤權不復活 | 本機通過；正式阻塞 | B1 | 未部署 |
| Header下一場倒數 | 已實作 | 精確開考時刻尚未核對，以日為單位 | exam_countdown.js、exam-schedule.json | 官方116日期、Taipei、不負數、不依舊年變 | 日期／時區／過期測試通過 | B1 | 同上 |
| 同commit測試後Pages | 已修依賴鏈 | 必須等待本次Actions實際結果 | pages.yml、sudu-release-checks.yml | verify成功才build/deploy，release.json同SHA | YAML／本機入口檢查；CI見交接 | B1 | 同上 |
| 影像bot亦測試後發布 | 已實作 | 實際bot＋gate完成才驗收 | tcte-*.yml | 更新audit、提交後dispatch exactSHA | CI見交接 | B1／影像bot | 同上 |
| 九份MD及逐年稽核 | 本批建立／更新 | 發布後補精確工作連結，內容待辦持續追蹤 | docs/SUDU_*.md、corpus-audit.json | 無口頭完成宣告、逐年及逐卷證據 | 可重跑audit生成 | B1 | 同上 |

## 待辦的完成門檻

外部來源缺失不以猜測補題；官方答案修正、送分、人工閱卷及教材採用版本需要實際來源。Admin 缺部署帳號／連線時明列未部署；GitHub Pages 成功不能代替它。每批新增內容都應更新 audit 的指標，保留旧版本與學生歷史，再通過同提交的測試與發布。
