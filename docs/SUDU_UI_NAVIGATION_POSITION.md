# 7581707 學習頁：導覽、浮動切題與題號

更新：2026-10-19（Asia/Taipei）

## 本次需求與實作

最新需求取代舊版「只放在白話解說後方」定位。正式切題控制為視窗底部中央的單一 `#sudu-question-dock`，內含原本 `.questionnav`、`#prev2`、`#next2` 實際節點。`app.js` 原事件綁定在節點移動後執行，並未製作失效複本。

| 控制 | 最終內容／行為 | 程式位置 |
| --- | --- | --- |
| 年度 | 90～115 學年度、自編練習及收錄狀態；不包含試卷 | `workspace.js`：`.sudu-year-filters` |
| 科目 | 依目前年度資料提供試卷及科目；選取後返回學習並收合 | `.sudu-subject-filters`，原 `#paper`、`#subject` 節點 |
| 個人學習 Dashboard | 返回逐題學習、我的 Dashboard、首次答錯、全部曾答錯、裝置設定、備份、還原、主題 | `data-sudu-menu-trigger="functions"`；內部名稱保留以相容測試及 DOM |
| Header 最右工具 | 真正的 `#export` 匯出按鈕及 `#sudu-theme-button`；有 accessible name | `.sudu-header-tools` |
| 上一題／下一題 | 固定視窗底部正中央；首尾禁用；中間為篩選後目前位置／總數 | `suduBuildQuestionDock()` |
| 全部題號 | 依 `available()` 全部建立，點擊以穩定 `q.id` 重新解析索引 | `.sudu-question-ball` |

已移除選單中的 `archive`、`source` 獨立按鈕。年度資料、Dashboard 年度進度與每題教材／官方來源仍由各自內容介面提供。

## 題號、狀態及資料保留

正式題圓球顯示 `q.number` 原卷題號，`data-original-number` 保留來源值；`data-filtered-index` 表示目前科目篩選後的陣列索引。Accessible name 同時說明「原卷第 N 題、篩選後第 M／總數、科目、作答狀態、是否目前題」。自編題使用目前集合的序號，不冒稱正式原卷題號。

- 綠球：最近有效判分為答對。
- 紅球：最近有效判分為答錯。
- 白球：尚未作答。
- 黃色虛線球及問號：已作答、答案或原題尚待核實，或尚無有效判分。

有效判分參考 `attempts`、`reviewHistory` 及目前 `reviewAnswers` 的布林判分事件；官方題須同時 `questionVerified` 及 `answerVerified`。較新的有效事件依原有日期選取，未核實題即使舊歷程曾帶 `correct:true` 仍顯示待核對。狀態除顏色外另有勾／叉／問號、圖例及 accessible name。當前題有外框、底線及 `aria-current="step"`。

跳題只更新 `ui.index` 並透過原本 `save()` 保存；不清除歷史、不更換 `sudu_device_profile_v1`，不改寫首次答錯與已送出快照。

## 浮動區與閱讀空間

`ResizeObserver` 實測浮動區高度，寫入 `--sudu-dock-height`；`.wrap` 底部空間隨題號換行、視窗調整及安全區更新。全部題號實際存在 DOM，不限制只顯示前幾題。低高度視窗的浮動區可垂直捲動存取全部圓球，使用視窗可用高度而非固定列數裁切。

淺色主題切題列為黑底白字；深色為白底黑字。禁用按鈕使用可辨識的灰字、虛線邊框及原生 `disabled`，不以透明度把文字隱藏。非學習頁每次 `render()` 都呼叫 `suduWorkspaceApply()`，移除失效浮動控制，底部預留還原為零。

## 三選單的 0ms 與鍵盤

選單收合沒有計時等待。透明 `#sudu-menu-bridge` 用實際觸發按鈕／面板座標，連接兩者之間的縫隙；該橋、觸發按鈕、面板共同構成互動區域。滑鼠離開這個區域立即更新 `aria-hidden`、`inert` 及開啟狀態。

桌面可 Hover，觸控可點按。鍵盤聚焦開啟，ArrowDown／開啟時的 Tab 可進入面板，Escape 收合並返回原觸發按鈕；點外部或選取年度／試卷／科目收合。動畫僅用於展開，`prefers-reduced-motion` 停用動畫。

## 作答後閱讀優先及自訂排序

作答流程仍為「保存 → render → `suduGoToExplanation()`」。答後只變更當次顯示順序為題目、正確答案／待核對、白話解說，接著依原設定排列延伸與來源。`sudu_layout_order_v1` 保留；不因優先顯示覆寫學生先前順序。

已作答時，排序介面說明前三個閱讀區塊暫時固定，仍能調整延伸／來源。可在未作答題目設定完整順序。原題留在頁面上方，另提供「回題目」。捲動以實測 Header 高度扣除 12px 留白，採用系統減少動態效果偏好。

## 驗收與發布證據

- 驗收程式：`tests/sudu_workspace_test.cjs`，另由根工作流程執行綜合 smoke。
- 2026-10-19 本機 Chromium 實測 **28 項通過**，以 Noto Sans CJK TC 真實繁中字寬測試 320、375、390、430、768、1024、1280、1440px × 深淺 2 主題，另驗證 320×480px 低高度視窗、Dashboard／全部錯題兩主題。測試從已建置的 `_site` 載入，非單獨語法檢查。
- 一般 8×2 寬度實測，浮動列置中、底部預留、全部題號、觸控、0ms／橋接、鍵盤、儲存與原卷題號映射全部通過，瀏覽器 `pageerror` 為 0。低高度視窗實测確保題號局部捲動時，上下題列仍留在浮動區內；所有題號均可到達。
- 原始本機證據為 `/tmp/sudu-workspace-test/results.json`，同資料夾有 320／1280px 深淺截圖。人工查看了 320px 深色及 1280px 淺色的繁中畫面；這些本機結果不代替 GitHub 同提交 Actions 與正式發布驗證。
- 最終 commit、Actions 與 Pages 對應見 `docs/SUDU_PROGRESS_TRACKER.md`。提交檔案本身不構成部署成功證明。
