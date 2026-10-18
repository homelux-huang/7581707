# 7581707 統測速讀接手文件

更新：2026-10-19（Asia/Taipei）。沿用 [homelux-huang/7581707](https://github.com/homelux-huang/7581707)，未重建另一個網站。

## 發布位置與接手基準

- 學習平台：https://homelux-huang.github.io/7581707/sudu/
- 主網址：https://homelux-huang.github.io/7581707/ （保留導向 `/sudu/`）
- 原工具集：https://homelux-huang.github.io/7581707/?tools=1
- 重新讀取 main 的接手基準：`495cc92b74c9118e1935dd964897acff14ce8bfb`，不是歷史的 99157ce。
- 該基準 Pages 工作 [39139018174](https://github.com/homelux-huang/7581707/actions/runs/39139018174) 成功，但不能代表本次修改或所有需求完成。
- **正式 Admin API：未部署／沒有可驗證的公開 API 網址。** 本機真 HTTP 測試成功與正式服務是不同狀態。

<!-- SUDU_RELEASE_EVIDENCE -->
### 本次批次證據

B1 為本文件所屬實作批次。提交前的本機測試已執行；本節將在實際 GitHub Actions 與 Pages 完成後補入精確 SHA、工作連結與公開檔案比對結果。此段不是部署成功宣告。Pages 必須讀取 `sudu/release.json` 並與通過 gate 的 SHA 一致；更新後再做公開站實際載入驗證。
<!-- /SUDU_RELEASE_EVIDENCE -->

## 已實作並有本機驗收的範圍

1. 三個 Header 選單分離為年度、科目、個人學習 Dashboard；试卷移至科目，刪除選單獨立的歷年試卷／教材來源入口，保留每題來源及 Dashboard 年度續答。
2. 真正的匯出與主題按鈕移到最右；唯一浮動上下題列固定底部中央，全部實際題號可換行、點選，動態保留底部空間；320×480 低高度時仍可捲到最後題。
3. 先保存，再顯示解答／白話解說並捲動。自訂區塊排序資料保留，答後閱讀暫時優先題目、正解、解說。未核實題保留選擇但顯示待核對，沒有紅綠亂判。
4. 深淺主題涵蓋學習、Dashboard、錯題、Admin、分享；原卷不反相。移除舊 workspace CSS 多版本覆蓋。
5. 原卷／答案 WebP 的真實前端、延遲載入、頁碼標示、放大、失敗重試、答案原頁答前不呈現。沒有可靠裁切時保留完整原頁，跨頁內容可展開。
6. Dashboard 年度卷名與進度狀態可續答第一個未答題；已完成則檢視。全部曾錯頁保存歷史，與首次作答即錯的複習集合分開，可按年度／卷／科篩選並重答。
7. 學習卡互動與來源欄位；目前 2 筆詞條，其他內容 N/A，不能宣稱全科詞庫完成。
8. 17 項計分與送出快照情境、伺服器重新驗證、限卷分享及改分留痕、公開建置 allowlist。114–115 年共 10 卷基本配分有封面證據，完整正式規則仍待核实。
9. 116 統測日期倒數：官方公告 2027-04-24～25，Asia/Taipei，以日數顯示；未核對開考時刻，不假設秒級目標。來源在 `data/exam-schedule.json`。

## 不可誤讀的資料狀態

以 `sudu/data/corpus-audit.json` 和 [SUDU_CORPUS_AUDIT.md](SUDU_CORPUS_AUDIT.md) 為數據權威。批次初始重新稽核 5,323 筆；本批新增 93 年商業類兩卷的 100 個純影像導覽紀錄後共 **5,423 筆原始紀錄**。其中 110 筆歷史誤收卷保留 ID 與資料，但不當成本範圍商業類學習題；適用範圍 5,313 筆。

舊 `answerVerified=true` 的 4,304 筆實際為程式配對，遷移為 `answerMatched=true` 並保留 `answerVerificationLegacy`、來源版本及舊證據。沒有獨立審核的 `answerVerified` 不再自動 true。此遷移不讀寫學生儲存區，不更換题目 ID 或刪除作答。

原卷可讀覆蓋以「該卷完整索引原頁存在」計算，不能當成逐題裁切／頁碼已覆核。完整教學、逐選項理由、教材章節與完整配分規則應分項計數；任何 AI 新解析只算草稿。

90–91 商業類代碼 14、92–97 代碼 13、98 起代碼 09；以 26 年官方目錄證據處理。98／99 年不得因 `<100` 的舊判斷而排除，也不能套用 115 年數位科技考科。已核對封面科目放在 `official-paper-catalog.json`，尚未可靠逐題劃分的科目保持待核實。

## 學生資料相容性

保留 `sudu_sites_ui`、`sudu_sites_state`、`sudu_device_profile_v1`、`sudu_layout_order_v1`、`sudu_theme_v1` 和既有 IndexedDB `7581707-sudu-profile-backup`。不清空 attempts、reviewHistory、reviewAnswers、首次錯誤、已送出快照。

备份仍識別 `sudu-backup-1`，新增欄位相容。還原先寫本機與 IndexedDB 還原前快照，使用可重複的合併，不取代既有裝置代碼或已送出測驗。重考建立新 session 和 submission history；舊資料無時間則 N/A。儲存失敗有可見警告及匯出提示，不說已持久保存。

本機學習代碼只是瀏覽器識別。跨裝置必須使用備份／還原或明確同意且真正可用的後端同步，不宣稱代碼本身永久同步。

## 測試入口

```sh
python scripts/check_sudu.py
node --test tests/share.test.cjs
node tests/sudu_dashboard_test.cjs
node tests/sudu_scoring_test.cjs
node tests/sudu_countdown_test.cjs
python -m unittest discover -s backend/tests -v
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/check_tcte_corpus.py --decode-images
python scripts/build.py
```

啟動 `_site` 的 loopback 測試伺服器後，以 Playwright 1.51.1／Chromium 執行：

```sh
node tests/sudu_browser_smoke.cjs
node tests/sudu_workspace_test.cjs
node tests/sudu_admin_browser.cjs
```

CI 安裝真正的繁中字型，包含 8 種寬度 × 深淺主題；測試會保留 JSON 與截圖 artifacts。不要用 Node 語法通過替代 Chromium 驗收。Pages 的 verify→build→deploy 為同一指定 SHA；bot 提交也要 dispatch 對應 SHA 的 Pages gate，不能跳過測試直接發布。

## 阻塞與下一批順序

1. 完成全庫 RGB 原頁再生並重跑解碼；保留原灰階檔版本，只有實際生成成功才可宣稱原色覆蓋。零位元組、尺寸與hash不符會阻止發布。
2. 官方原題、答案和多頁題組人工／獨立覆核；90 年答案為官方 HTML 表，部分92／93來源缺漏，不可假裝有 PDF。應有題數未知的卷先對封面查證。
3. 小批次教師草稿逐項核對，核實原題／答案／推理／教材章節要分開。精確教科書版本、冊次、章節、頁碼未知顯示待核實。
4. 補 90–113 各卷配分、送分／更正、作文與英文非選擇評分；目前 10 筆基本配分不等於完整正式計分完成。
5. Admin 需要可用雲端帳號／部署連線、私密初始密碼、HTTPS、持久資料庫、私密備份與還原驗證。公開服務不得 admin/admin。現有本機安全測試不能代替正式部署。

九份交付文件互相對照：[進度](SUDU_PROGRESS_TRACKER.md)、[RWD](SUDU_UI_RWD_AND_ACCESSIBILITY.md)、[導覽](SUDU_UI_NAVIGATION_POSITION.md)、[詳解](SUDU_ANSWER_EXPLANATIONS.md)、[Hover](SUDU_SUBJECT_HOVER_GUIDE.md)、[原圖](SUDU_ORIGINAL_IMAGES.md)、[題庫](SUDU_CORPUS_AUDIT.md)、[Admin與計分](SUDU_ADMIN_AND_SCORING.md)。
