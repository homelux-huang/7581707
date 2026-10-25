# 7581707｜學習工具集

線上首頁：**https://homelux-huang.github.io/7581707/**

公開分享 HTML 學習程式，首頁可搜尋並開啟全部工具。

114／115 題庫與 V4 開發接續請先讀 [VS Code 接手檢查點](docs/VSCODE_TAKEOVER_2026-10-25.md) 與 [共同交付命令](docs/114-115-DELIVERY-COMMAND.md)。候選接收、教學 QA 與正式發布分開記錄；正式頁為 `sudu/v4-115-multisubject-review-demo.html`。

## 現有工具

- [7581707 統測速讀平台](https://homelux-huang.github.io/7581707/sudu/)：`sudu/index.html`。

會計模擬考與會計統測兩支舊程式已從目前倉庫檔案及發布網站移除。

## 分享程式

首頁各工具卡片都有「分享」按鈕。支援系統分享的裝置會開啟分享選單，可選擇裝置提供的 LINE、訊息、Email 或其他管道；其他瀏覽器會顯示公開網址，按「複製連結」後即可貼到任意平台。若瀏覽器禁止自動複製，仍可長按或手動選取複製。取消分享不會傳送任何內容。

只分享程式名稱與公開網址，不分享個人答案、分數或 AI 對話。未來新增的 HTML 也會自動取得首頁卡片的分享按鈕；程式內部的頁首按鈕則需要該 HTML 自己引用共用 `assets/share.js` 與 `assets/share.css`。

## 之後如何新增 HTML

1. 在本倉庫按 **Add file → Upload files**。
2. 上傳 `.html` 或 `.htm` 檔案，放在根目錄或一般子資料夾都可以；相關圖片、CSS、JavaScript 請一起上傳並保留相對路徑。
3. 按 **Commit changes**，將檔案提交到 `main`。
4. 等待 **Actions → Update HTML catalog and publish website** 成功完成，再重新整理線上首頁。

網站建置會自動掃描所有 HTML，以檔案內的 `<title>` 作為工具名稱；沒有標題時使用檔名。不用手改首頁連結，刪除或更名也會在下次成功發布時反映。中文、空格、巢狀資料夾與大寫副檔名均可使用。

根目錄 `index.html` 為首頁，請勿以其他程式覆蓋。隱藏資料夾、`scripts`、`tests`、`node_modules` 與 `_site` 不列入清單。只會列出已提交至 `main` 的檔案，其他分支需合併後才發布。

## 自動更新方式

GitHub Actions 在每次 `main` 更新時執行 `scripts/build.py`，產生 `_site/index.html` 並發布至 GitHub Pages。完整自動清單存在發布後的首頁；倉庫內的 `index.html` 保留初始清單及首頁樣板，不由機器人追加提交。瀏覽者不需要登入 GitHub，也不需要呼叫 GitHub API。

本機預覽：

```sh
python scripts/build.py
python -m http.server 8000 --directory _site
```

開啟 `http://localhost:8000`。此倉庫只提供靜態網頁託管，不提供後端或 AI API 代理。
