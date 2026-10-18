# 7581707 統測速讀｜試卷計分、管理後台與隱私設計

更新日：2026-10-18。正式網址： https://homelux-huang.github.io/7581707/sudu/

## 前台工具列
匯出紀錄與深淺主題按鈕移入導覽同一行、最右側，保留原 id、事件綁定與資料。手機仍可操作。

## 歷年考試與計分規則
- 試卷按 **年度+卷別** 區分，原始學生答題事件儲存不變。
- 尚未完成題目：顯示「未考完」與作答題數，**完全不顯示數字分數**；完成全部且試卷題數、題幹、選項與官方答案都已核實，才顯示「可送出」。
- 送出後保存第一次考卷提交時間、開始作答時間與經過時間，另存不會被日後重練覆寫的答案快照；Dashboard 依年度與試卷顯示送出狀態。
- 送出後仍須核實 **該年該卷每一題的正式配分**，才會顯示數字分數。規則存放 `sudu/data/scoring-rules.json`，欄位 `year,paper,expectedCount,type,points,maxScore,sourceUrl,reviewedBy,reviewedAt,verified`。
- 須官方 TCTE 來源、審核人、審核日期及各題完整配分和總分一致才能啟用；未核實不得只拿「答對率×100」冒充正式成績，尤其國文、英文常有非選擇題與級分。
- 現有 90～115 年 `questionVerified` 多數仍為 `false`；尚無逐卷已核實配分，因此不能宣稱所有年度都可得正式數字分數。
- 「花費時間」記錄第一次本次作答至送出之**經過時間**，包含瀏覽器背景放置或離開，非純專注作答秒數。
- 管理員調分另存 `adjustments` 稽核資料，標註「管理員修正（非官方成績）」，不覆寫原始答案或官方原始分數。

## 私人 admin 管理服務
原先主站採 GitHub Pages 靜態部署，**公開 HTML 不可能安全地保護密碼或讀取其他瀏覽器 localStorage**。因此：
1. 管理 UI 原始檔為 `sudu/admin.html`。在 GitHub Pages 點開會顯示「尚未部署後台 API」，不能假裝已登入。
2. 真正登入須另外部署 `backend/server.py`；會從後端自己的 `/admin` 路徑提供相同管理 UI。可用 `render-admin.yaml` 作為**獨立 Render Blueprint**，原本 `render.yaml` 的靜態網站不可替換。
3. 後台使用私密 SQLite、PBKDF2-SHA256 密碼雜湊、HttpOnly / SameSite Cookie、CSRF、登入頻率限制；正式營運環境只允許 **12 字以上初始密碼**，於 Render private environment 設定 `SUDU_ADMIN_INITIAL_PASSWORD`。**admin/admin 只支援本機開發模式** `SUDU_DEV_ALLOW_ADMIN_ADMIN=1`，第一次登入強制變更密碼，不能放上公網。
4. 管理資料庫持久化須 Render persistent disk `/var/data/private.sqlite3`，以及定期私密備份。未配置 Persistent Disk 時資料可能消失；不應稱為正式持久後台。
5. 需設定 `SUDU_ADMIN_PUBLIC_URL=https://你的後台網域`，並只允許指定 `SUDU_ALLOWED_ORIGINS`。
6. 管理頁顯示學生代碼、答題進度、送出卷數、日期時間、經過時間、首次答錯、核實後教師解析及官方題目 PDF；任何精確章節沒有證據時顯示「精確章節待核實」。
7. 管理員可在已送出試卷加上「人工調整分數／理由／來源」，單獨留存且不冒充官方計分；手動產生一次性隨機字串的 7 天限期分享 URL `/share/{token}`，由學生端可讀，但含學習紀錄，需審慎分享。

## 學生同意／同步
- 學生在 Dashboard「選用：自願同步至私人管理後台」自行填 API HTTPS 網址、確認同意後才會送出學習暱稱、作答選項、日期時間及送出記錄；預設完全不傳。
- API 向學生發配對的隨機權杖，與原有本機學習代碼分開，不會將學習代碼當成登入密碼。
- 學生可停止後續同步；**停止同步並非刪除已傳資料**。伺服器端資料刪除、權杖撤銷及保留期限政策仍需正式上線前落實。
- 若選擇不使用後台，學生仍可用原有 JSON 備份還原。
- 目前獨立管理後台的 Render API 尚需由擁有者部署與設定機密，**不能宣稱已連線、學生資料已同步、或管理員可在正式站登入**。

## 測試
- GitHub Actions：`sudu-check.yml` 加入 Node JS 檢查、計分單元測試、Python admin 資料庫/密碼測試。
- `sudu-browser-test.yml` 保留 Chromium Playwright 桌面、手機、深淺主題、錯題與導覽驗收，額外確認右側工具列與未完成不顯示官方分數。
- 須以 GitHub Actions 實際狀態確認是否通過，不能僅因建立此文件而宣稱已部署或完成全部計分規則。

官方來源：https://www.tcte.edu.tw/index.php?mod=TVETest/down_exam4y
114 年各科標準答案：https://web1.tcte.edu.tw/EXAM/114_4y/index.php?page=1
115 年各科標準答案：https://web1.tcte.edu.tw/EXAM/115_4y/

注意：標準答案 PDF 不一定包含完整各題配分、非選擇題評分細則或所有年度修訂，因此每份卷別必須另外核實規則。
