# 7581707｜學習工具集

線上首頁：**https://homelux-huang.github.io/7581707/**

公開分享 HTML 學習程式，首頁可搜尋並開啟全部工具。

## 現有工具

- `gemini canvas會計統測程式.html`：高職統測會計學歷屆試題測驗系統。
- `Gemini Canvas會計模擬考.html`：高職會計學歷屆模擬考與白話解題助手。

兩個檔案保留原始內容。模擬考的 Gemini AI 解題功能原本使用空白 API 金鑰，因此目前無法呼叫 AI；一般題目瀏覽與作答不受此設定影響。請勿將私人 API 金鑰填進公開 HTML。這兩支程式的樣式、字型及圖示使用外部 CDN，需要網路連線。

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
