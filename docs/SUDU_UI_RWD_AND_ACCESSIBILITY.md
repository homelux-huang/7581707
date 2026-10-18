# 7581707 響應式與無障礙驗收

更新：2026-10-19（Asia/Taipei）

## 樣式結構

`base.css` 保留既有基礎樣式；`dashboard.css` 使用共用顏色變數，`workspace.css` 在兩者後載入，提供單一主題變數及目前互動規則。原 workspace 的 V15～V19 重複導覽、兩套深色與舊 inline 切題覆寫已整併，沒有繼續疊加互相衝突的主題宣告。少數 `!important` 只用於通用 `[hidden]` 及覆蓋尚存於歷史 base compact 規則的 Header 字級／間距。

| 區塊 | 淺色 | 深色 |
| --- | --- | --- |
| 頁面 | `#f5f7fb` | `#050505` |
| 一般面板 | `#ffffff` | `#141414` |
| 題目 | `#f0f7ff` | `#141d28` |
| 答案 | `#f2edfa` | `#251e32` |
| 解說 | `#fff5e8` | `#292116` |
| 延伸 | `#edf8f1` | `#152a20` |
| 來源 | `#f1effa` | `#202036` |
| 主要／次要文字 | `#22364c`／`#50637a` | `#f2f2f2`／`#c4ccd6` |
| 一般操作按鈕 | 白底深字 | 白底黑字 |
| 浮出選單 | 黑底白字 | 黑底白字 |
| 浮動切題 | 黑底白字 | 白底黑字 |

Dashboard 歡迎區、計數、展開列表、裝置／同步設定、觀念及來源面板都使用同一組變數。可點的錯誤次數面板是白底按鈕，其內數字及描述明確繼承深字，避免次要文字在白底上變成淺色。原卷圖像保留原始顏色，沒有套用反相濾鏡。

管理／分享頁是獨立 HTML，需另依 `docs/SUDU_ADMIN_AND_SCORING.md` 的實際驗證結果判定；主學習站樣式檢查不能代表這兩頁已驗收。

## 排版與輸入

- Header 以 CSS grid 配置品牌、倒數及最右工具，三選單獨立一行。760px 以下將倒數置於獨立中間列，320px 保留完整「個人學習 Dashboard」文字。
- 320、375、390、430、768、1024、1280、1440px 均列入 Chromium 測試；同一測試各跑深淺兩種主題。
- 中文使用 `line-break:strict` 與自然換行；一般文字不使用 `word-break:break-all`、省略號或 line-clamp。只有 URL、代碼允許必要的任意斷行，公式容器可局部水平捲動。
- 題號數字為不換行、固定圓形 30×30px，容器緊湊由左至右換行；外框與符號不更改題號文字。極低視窗高度可捲動浮動區，而非隱藏後段題號。
- 低高度浮動區內的上下題列採 `position:sticky`，局部捲動題號時仍可操作。圓球的捲動留白避免聚焦後被這列遮住。
- 切題列高度及 Header 高度由實際尺寸更新，頁面底部留白與答後定位隨畫面改變。
- 區塊排序提供鍵盤按鈕，並保留滑鼠拖拉；作答後的閱讀優先限制及已保存順序在 UI 中說明。

## 無障礙互動

選單 trigger 設定 `aria-expanded`、`aria-controls`；未開啟面板 `inert` 並 `aria-hidden=true`。0ms 收合使用共同互動區域及透明橋接，不依靠延遲掩蓋縫隙。提供鍵盤 ArrowDown／Tab、Escape、外部點按、觸控關閉鈕。

題號的 accessible name 包含原卷題號、篩選位置、科目與狀態；當前題有 `aria-current`、外框及底線，紅綠判分亦有文字及符號。Header 匯出與主題 icon 不依賴圖像辨識，皆有 accessible name 與 title。原生禁用切題按鈕維持文字對比。

`prefers-reduced-motion` 關閉選單動畫並改用直接閱讀定位。發音、Hover 卡片與原圖放大的鍵盤／觸控行為由相應模組測試另行記錄。

## 可重跑的驗收

```sh
SUDU_TEST_URL=http://127.0.0.1:8765/sudu/ node tests/sudu_workspace_test.cjs
```

可用 `SUDU_BROWSER_EXECUTABLE` 指定 Chromium；`SUDU_TEST_OUTPUT` 指定測試輸出資料夾。預設輸出為 `/tmp/sudu-workspace-test`，包含 JSON 結果與 320／1280px 深淺截圖；失敗另輸出截圖及當時錯誤。

測試從當下 `available()` 和真實題目取得題數、正確與錯誤選項，沒有硬編 8／50／64。會驗證：

1. 三選單內容分離、試卷所在面板、已移除入口、原匯出／主題控制。
2. Hover 跨縫隙、立即收合、鍵盤及 Escape。
3. 作答保存、解說定位、最近有效判分、首次錯誤不被答對覆蓋。
4. 上下題首尾邊界、全部題號、點選／刷新／學習代碼不變。
5. 答後優先順序與自訂設定同時保留。
6. 8 種寬度及 2 種主題無整頁水平溢出、浮動置中、底部預留、字不跑出球。
7. 實際 computed style 主要文字／背景對比至少 4.5:1；不以設定值代替實際渲染值。
8. 非學習頁移除失效切題列。
9. 114 年真實題庫之原卷題號／科目篩選映射、待核實題作答保留及待核對狀態。
10. 手機觸控開啟／關閉與右上主題。
11. Dashboard 與全部錯題頁的深淺主題嵌套文字、白底按鈕內文對比。
12. 320×480px 低高度視窗的最後一顆題號可存取，局部捲動時主要切題列仍可見。

## 本次執行狀態

2026-10-19：`node --check sudu/workspace.js`、`node --check tests/sudu_workspace_test.cjs`、`git diff --check` 通過。`python scripts/build.py` 成功建立公開 allowlist；以 `_site` 啟動本機伺服器後，**28 項 Chromium 驗收全部通過，瀏覽器 pageerror 為 0**。

| 畫面寬度 | 淺色 | 深色 |
| --- | --- | --- |
| 320px | 通過 | 通過 |
| 375px | 通過 | 通過 |
| 390px | 通過 | 通過 |
| 430px | 通過 | 通過 |
| 768px | 通過 | 通過 |
| 1024px | 通過 | 通過 |
| 1280px | 通過 | 通過 |
| 1440px | 通過 | 通過 |

各寬度採 900px 高度；另以 375×812px 觸控及 320×480px 低高度驗證。8×2 學習頁實際 computed style 的最小對比為 **5.382:1**；Dashboard／全部錯題頁另以各自渲染文字驗證至少 4.5:1。這個數字是測試選取元素的最低對比，不聲稱涵蓋網站所有可能動態內容。

測試環境初次缺少中文字型，最初截圖出現方框，未作為最終視覺證明。已從 Noto 官方 `notofonts/noto-cjk` 下載繁體中文 `NotoSansCJKtc-Regular.otf` 到測試專用 `/tmp/sudu-fonts`，以 `FONTCONFIG_FILE=/tmp/sudu-fonts/fonts.conf` 確認 `fc-list :lang=zh` 可見後重跑全部測試。已人工檢視 320px 深色、1280px 淺色之最終繁中截圖。

本機 JSON 證據：`/tmp/sudu-workspace-test/results.json`；畫面檔：`workspace-320-light.png`、`workspace-320-dark.png`、`workspace-1280-light.png`、`workspace-1280-dark.png`。CI 可使用系統 `fonts-noto-cjk` 等同來源字型；其部署結果須看實際同提交工作。

本機通過不代表已發布。最終同提交 Actions、正式 Pages 版本與公開站對應驗證集中在 `docs/SUDU_PROGRESS_TRACKER.md`。
