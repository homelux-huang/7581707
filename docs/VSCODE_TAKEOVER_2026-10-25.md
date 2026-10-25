# VS Code 接手檢查點（2026-10-25，Asia/Taipei）

本批是隔離接手與測試修復，未發布新題。唯一正式頁仍為 `sudu/v4-115-multisubject-review-demo.html`。

## 工作區與來源

- 新 worktree：`D:\AI\7581707-platform`；分支 `integration/vscode-takeover-20261025`。
- 基底為現場 API 與 fetch 雙重核對的 main `57d766e841235b937babf3fe10a8ff44606c7c41`。
- `D:\AI\VS CODE`（CUSMED）及原 `D:\AI\7581707` 開始時均乾淨；沒有改寫其檔案或切換分支。原 7581707 main 留在 `946b0db`，只更新 remote refs。
- GitHub connector 已驗證登入；本機 Git push 權限須以實際 push 結果另行確認。
- 共同台帳由 PR #30 `38fb73138e7efa89d932f134cad4dff00cd739bf` 接收，410 筆保留，不能回退成空白。
- 後續現場查詢 [控制台 Issue #36](https://github.com/homelux-huang/7581707/issues/36) 指定 PR #35 為整合候選、PR #30 為唯一台帳。本分支台帳為接收／回填候選，不能自行取代 PR30 或建立平行權威；後續依題號與檔案工作租約避免重複修改。

## 最新候選接收

| PR | HEAD | 本次讀取狀態 |
| --- | --- | --- |
| 26 | `33ca5b26b333f3913a63bd0e61f75f33557c3668` | Draft；4 次 CI 成功、1 次失敗 |
| 27 | `cb215a771df74dec485774a4e74fd691fbb03e77` | Draft；3 次 CI 成功 |
| 28 | `f04b26de83931ca384443eeee72de1f9ff468423` | Draft；1 次 CI 成功 |
| 30 | `38fb73138e7efa89d932f134cad4dff00cd739bf` | Draft；未找到此 SHA workflow run |
| 31 | `2b1e48336ea103e8f114e4bf6c7a8df023cef9c4` | Draft；未找到此 SHA workflow run |
| 32 | `2e7677411749a8a32a2ab1ecc065ab7e3e971f97` | Draft；未找到此 SHA workflow run |

PR #21–#32 均未合併。本表為查詢快照，整合前仍須重查。另已 fetch 全部分支，包含後續 `qa/role-d-v4-per-question-matrix-20261025`；未讀取的證據不算驗收。

後續新增 PR #34 `1a844d71f3cc786562b56d1dcb7ac27928b5774c`（Role D 真實逐題矩陣）與 PR #35 `dc64e06ce417e8d64402f7fbdc81856616e71496`（整合候選）。PR35 已有 MB23 表格候選，但尚無本批 decode 修復；須在其最新 SHA 逐檔接入後重驗。PR34 的矩陣 run `40162016136` 失敗，抽查 job `121075377618` 將既有 data URI 圖片視為本機路徑而報 missing actual original image；不得當成 UIQA PASS。#33 與 #36 是 Issues，不是 PR。

MB23 的 PR32 候選含原始表格，台帳保存其新檔案 SHA 與含表格 revision；PR25 的文字來源 revision 仍保留，未假裝已整合。教學本文 digest 不變也不代表來源版本相同，獨立與 UI 審查仍須重新綁定。

## 本批修改與驗證語意

`tests/sudu_certified_positive_browser.cjs` 在懶載入圖片載入前直接 decode，曾造成 [PR26 run 40111871501](https://github.com/homelux-huang/7581707/actions/runs/40111871501) 失敗。本批補精確 URL、HTTP、WebP header、SHA 檢查並等待圖片載入，保留 decode 斷言，也檢查第二張圖。檔案存在與建置 allowlist 已核對；時序為目前推論，尚不能宣稱完全重現原 CI 根因。

這是 synthetic fixture 回歸，絕不是正式教學 UIQA。學生 HTML/runtime、五題正式資料、35 題 Demo、發布器及學生儲存 key 均不在本批修改範圍。

本批 CI run `40162613185` 的 job `121077228468` 實際日誌另證明：既有真實題測試固定四題清單，但 main 已有第五題 MB05。已逐段接入 PR26 的 `sudu_real_reviewed_browser.cjs` 修正，固定 MB02/03/04/05/09 與 A/A/C/B/A 答案，保留原有教學與互動斷言，補原圖 HTTP/WebP/SHA、載入等待及 decode。本機真實五題 × 8 viewport 回歸 PASS；這不是新教學或真人批准，不提升台帳的新題 UIQA。

本機 Windows／Python 3.14／Node 24／Playwright 1.51.1 檢查：台帳保留測試 PASS 5；分享測試 PASS 10；V4 年度入口回歸 PASS 8×2；修復後兩題 fixture 圖片／答題回歸 PASS 8×2；發布器 PASS（114=0、115=5）；公開 build PASS。`check_sudu.py` PASS（39 JSON、64 practice IDs、5423 official record IDs），這些為結構檢查數量，不是新增合格教學數。

35 題 Demo 完整 Chromium 回歸 PASS：35 張圖、30 個原圖 hash、5 題英文×4處呈現、35題×8 viewport×2 theme、觸控及判分後 hover。輸出在本機忽略的 `test-results/demo/`，未使用學生瀏覽器個人資料，也未將此回歸算為新題 UIQA。CI 的五題 job 顯示名稱同步修正；workflow 步驟及發布 gate 未刪減。最後修復提交推送後仍須核對該精確 SHA 的全部 CI，舊失敗紀錄不能當成修復後成功。

完整 Python suite 執行 52 項，50 項通過、1 failure、1 error：既有 cache-buster fixture 用 LF 字串預期 SHA，但 Windows write_text 產生 CRLF；既有 symlink 測試遇 WinError 1314，現有帳號缺建立符號連結權限。未跳過、未放寬測試、未更改 Windows 全域權限；須看 Linux CI 結果，不能將本機 suite 宣稱全綠。

隔離依賴位於 `.local/venv`、`.local/node_modules`、`.local/ms-playwright`，不提交 Git。瀏覽器測試前設定 `NODE_PATH` 與 `PLAYWRIGHT_BROWSERS_PATH` 為上述路徑，再以 `python -m http.server 8765 --bind 127.0.0.1 --directory _site` 提供建置產物。

既有 main 的 `check_live_release.py --attempts 1` 核對正式站 release SHA `57d766e...` PASS（114=0、115=5；圖片預覽114=9／115=119）。此舊版檢查器僅抽樣預覽圖片，不能稱為 PR26 全資產／逐題教學 digest 的完整 LIVE 稽核，也不能算本批發布。既有 Pages run `40097988371` 為 SUCCESS，未在本批重新部署。

第一批已推送 `2a6f757576c77a58a3fc2768d060e5b8c86d2836`，Draft PR [#37](https://github.com/homelux-huang/7581707/pull/37)。connector 建 PR 因登入帳號不是協作者遭422拒絕，改用已成功 push 的本機既有 Git 認證建立，未保存或輸出憑證。

## 尚未解除的阻塞

- PR26 最新 policy 仍為 `requireHumanTeacher=true`、`authorizedReviewers={}`；沒有真人教師批准。
- 需擁有者提供可核實教師 GitHub 身分／資格／科目與有效期間、公開金鑰及正式獨立審查事件；不得提交私鑰。實際審查必須綁定精確 PR HEAD、來源及教學版本。
- main branch API 顯示 `protected:false`，rulesets 為空；詳細 protection API 權限不足。須處理受控 PR 發布路徑與擁有者治理，不能稱現有人工規則是技術阻擋。
- 410 是來源分支候選數量，官方逐題編號／科目邊界仍待獨立核對。`114-00-C-19` provenance／manifest SHA 不一致仍 BLOCKED。
- 接收快照：13 題新增／增補教學候選、5 題歷史正式題；新獨立 QA／精確 digest UIQA／READY／main／LIVE 均 0。178 筆 manifest PASS 不等於完整來源 QA。
- 優先鏈仍為 114 英文07–09、115 MB20–25、115 經濟34及既有 MB02/03/04/05/09；不能以本批測試代替這些題目的實質驗收。

## 接續入口

見 [主指揮命令](114-115-DELIVERY-COMMAND.md) 與 [共同台帳接收候選](114-115-QUESTION-DELIVERY-LEDGER.json)。先完成本批精確 commit 的 CI，將可重用測試修復逐檔帶入 PR35 最新 SHA，核對其已接收的 PR27／31／32 成果後再驗證，避免重複整合；台帳回填 PR30 唯一來源。合格題仍逐題增量發布，未達門檻者繼續 BLOCKED。
