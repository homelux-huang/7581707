# 原始試卷與官方答案 WebP

## 本批實際交付

本文件以 `495cc92b74c9118e1935dd964897acff14ce8bfb` 為接手基準；最終離線全圖解碼時間 `2026-10-18T17:02:33.053893+00:00`，資料指紋 `295033e00c37bf22759b18df8402a86cb701b8b3cde2dab1b91191b3019e5c56`。新 commit、Actions 與 Pages 發布狀態由 [進度表](SUDU_PROGRESS_TRACKER.md) 記錄，本文件不以本機生成成功冒稱已發布。

| 項目 | 接手時 | 本批完成後 |
|---|---:|---:|
| 原題圖卷數／頁數 | 122／996 | 128／1044 |
| 原題圖目前索引檔案大小 | 154,167,944 bytes | 161,612,894 bytes |
| 官方答案圖卷數／頁數 | 111／111 | 122／122 |
| 官方答案圖目前索引檔案大小 | 6,341,592 bytes | 9,457,456 bytes |
| 可存取完整原卷之題目紀錄 | 5,013 | 5,313 |
| 可存取官方答案圖之題目紀錄 | 4,673 | 5,140 |
| 逐題原頁候選定位 | 4,849 | 5,011 |
| 已覆核逐題／跨頁映射 | 0 | 0 |

原題的「完整原卷可存取」覆蓋為 **5,313／5,313（100.00%）**，官方答案圖為 **5,140／5,313（96.74%）**。分母只取目前已收錄、符合當年商業類／商管群或共同科的紀錄；含影像導覽、占位與待核實文字。這不是 90–115 年正式應有全題數的覆蓋率：90 年數學與 92 年國文仍未入庫，其他卷正式題數仍有疑義。歷史錯收工程卷 110 題保留 ID 與舊資料，但不計入商管分母。

「候選定位」僅表示題號對應頁碼存在，**不能證明那頁確實含完整題意、共享題組、選項或跨頁圖表**。缺乏可靠定位或裁切時，前端必須提供有頁碼的全部原頁。現在不宣稱任何一題已完成精確裁切覆核。

## 本批新增與修補

- 補 98、99 年真正的 `09-1`、`09-2` 商管原卷，共 4 卷、32 頁；更正過去把 `<100` 年的 `09-*` 全數當成舊工程類的條件。
- 補 93 年真正商業類 `BIZ-1`、`BIZ-2`，各 8 頁及各 1 張官方答案圖。官方封面確認兩卷各 50 題，因此新增 100 個可導覽的純影像紀錄；題幹留空、選項留空、答案為 null，所有核實旗標為 false，沒有以猜測或 OCR 填入文字。
- 補 91 年官方跨科合併答案頁，5 卷各有可用索引。原頁是一張跨科大表，採 3500px／quality 75，保留官方顏色、科目標題及欄位，不猜逐題答案。五個卷別索引指向同一份原始 PDF，不算五份獨立官方答案來源。
- 補 98、99 年專業卷答案圖並更新其共同科答案圖；92 年專業卷答案重新以 RGB 生成。
- 發現 48 筆舊封面說明被當成題幹；加上 `original_image_required`，保留舊 ID 與文字，拒絕把封面錨點當成可靠當題位置。純影像紀錄亦採全卷 fallback。
- 原 generator 使用灰階，會失去官方紅色浮水印與答案表色彩。新 `renderVersion: 2` 一律 RGB；本批仍有原題 122 卷、答案 103 卷使用舊灰階版本，須由完整生成工作更新後再稽核，不能宣稱全庫色彩已修復。

正式來源：[年度試題總入口](https://www.tcte.edu.tw/index.php?mod=TVETest/down_exam4y)、[91 年合併答案](https://web1.tcte.edu.tw/EXAM/091_4y/91-4y-answer-new.pdf)、[93 年專一](https://web1.tcte.edu.tw/EXAM/093_4y/93-4y-13-1.pdf)、[93 年專二](https://web1.tcte.edu.tw/EXAM/093_4y/93-4y-13-2.pdf)、[98 年目錄](https://web1.tcte.edu.tw/EXAM/098_4y/)、[99 年目錄](https://web1.tcte.edu.tw/EXAM/099_4y/)。26 個年度目錄皆已實際取得，來源、抓取時間與 HTML SHA256 保存在 `sudu/data/official-paper-catalog.json`；其成功抓取不等同卷內內容覆核。

## 索引格式與版本保留

原題索引沿用 `sudu/data/original/index.json`，答案索引沿用 `sudu/data/original/answers.json`，不得猜其他路徑。

| 欄位 | 定義 |
|---|---|
| `papers[year/paper]` | 當年度實際卷別的 key；舊 `BIZ-*` ID 沿用 |
| `source`、`pdfSha256` | 官方 HTTPS 來源及實際 PDF 內容雜湊 |
| `generatedAt`、`sourceBytes` | 實際產生時間、下載 PDF 大小；舊版本缺漏仍列待補 |
| `renderVersion`、`renderSettings` | renderer 版本、width、quality、RGB、壓縮 method |
| `pages[].page/src/width/height/bytes/sha256` | 1 起算原頁、平台相對路徑、實際尺寸、大小與影像雜湊 |
| `questions[id].page` | 候選頁碼，未知為 null；不是核實旗標 |
| `candidatePages`、`contextStatus` | 原生文字層錨點候選，以及共享題組／跨頁待覆核狀態 |
| `mapping` | 原生文字錨點、舊頁碼候選、封面拒絕或全卷 fallback 的原因 |
| `history` | 先前 PDF／render 版本的索引與圖檔證據 |

檔名帶 PDF SHA 前綴、renderer 版本、寬度與品質，例如 `p001-<sha>-v2-w1400-q66.webp`。舊版檔案不刪除，避免破壞既有證據。相同 PDF 的重新壓縮可保留已有人名與日期的頁碼覆核；像素裁切不直接沿用不同尺寸。PDF 內容真的改變時，先保存 `verificationHistory`，把受影響的原題／答案／教學／教材與計分狀態改回待核實；保留原答案與學生作答資料。

圖片逐頁由 PyMuPDF 原樣 rasterize，不使用 AI 重畫、不做 OCR。新寫入先在記憶體完整編碼與解碼，再同目錄暫存、fsync、atomic replace，並比對寫入後完整 bytes。最終稽核曾攔下 4 張剛生成的 0-byte 圖，已從原始 PDF 補回並改成上述原子寫入；原因未能證實，不歸因於使用者。修補後全部 1,166 頁通過完整 Pillow 解碼、尺寸、大小與索引比對。

## 明確缺漏與下一批

| 範圍 | 原因／下一步 |
|---|---|
| 90 年數學 | 官方舊頁採逐頁圖片入口，未被現有 PDF-only 匯入器收錄；需保留官方圖片順序與來源，再無損語義轉 WebP |
| 92 年國文 | 目前年度資料未收錄；需從已取得的年度目錄追正式來源與題數 |
| 90 年四卷答案 | 真正來源是 `answer.htm` HTML 表，不是 PDF；本次明確記錄 `official_source_is_html_table_not_pdf`，沒有把 HTML 當作 PDF 假造答案圖 |
| 92／93 年 `00-M-OLD` 答案 | 舊制分卷對應尚未可靠識別；記錄 `official_answer_source_not_identified`，不可拿其他數學卷答案硬配 |
| 候選頁碼、共享題組與跨頁 | 0 題有完整覆核證據；優先視讀數學、科技、計算題，必要時顯示全卷 |
| 舊灰階版本 | 完整 image bot 使用預設全年度參數重新生成 v2，保留舊圖並再跑完整解碼 gate |
| 93 年新增 100 題 | 可看原卷、可導覽；逐題定位、文字、選項、官方答案配對及教師解析待核實 |

目前答案索引共 6 項缺漏，詳見 `answers.json.errors`；沒有把「有年度資料夾」當作已完成年度。

## 可重現驗收

```sh
python scripts/tcte_catalog.py
python scripts/tcte_source_images.py
python scripts/tcte_answer_images.py
python scripts/tcte_manifest.py
python scripts/check_tcte_corpus.py --decode-images --json sudu/data/corpus-audit.json --markdown docs/SUDU_CORPUS_AUDIT.md
python -m unittest discover -s tests -p 'test_tcte_provenance.py' -v
```

生成依賴 requests、beautifulsoup4（catalog）、PyMuPDF、Pillow；基本離線結構稽核只需 Python，完整解碼需 Pillow。網路下載失敗會留在索引 errors，不抹去其他年度錯誤。`--years`／`--papers` 可用於小批；預設不跳過舊 `renderVersion: 1`。完整 source 與 answer 須順序執行，避免互相覆蓋年度失效紀錄。

本批結果：15 個 provenance／renderer 回歸案例通過；manifest 通過；完整解碼 1044 張原題圖、122 張答案圖，結構錯誤 0。瀏覽器真實載入、手機縮放、斷網重試、答案圖答前收合由前端測試及 [RWD 驗收文件](SUDU_UI_RWD_AND_ACCESSIBILITY.md) 記錄，不能用 Python 解碼取代 UI 驗收。

影像 bot 在同一提交內保存原圖索引、年度資料中的來源失效記錄、manifest、audit JSON 及稽核 MD，再跑測試與發布 gate。若來源變動而失效 flags 沒有一起提交，該批不得算完整發佈。
