# 正式 LIVE 逐題完整覆蓋（P1）

每次 QA admission 由未修改原本 G0～G10 的 publisher 產出 `sudu/data/approved/integrity/{114,115}.json`，把通過正式來源 QA 的每題：
- canonicalId、年度、sourceQuestionRevision
- 實際教學 canonical digest、正式公開完整題目 SHA256
- 官方 A–D 答案、該題 WebP SHA256
- 正式題目全部共用材料 image path 和 SHA256
與已正式核准完整內容一併保存及發布到 Pages（原既存五題內容本身沒有改動）。

新的 `scripts/check_live_release.py` 必須先核對本地 main 的整份 approved、preview、progress 與 integrity JSON 原始 bytes，再對 LIVE **每題**單題影像及**每張**共用材料逐一下載 SHA 檢查（可以依檔案路徑去重），並執行完全相同來源 revision / content SHA / 教學 SHA / ID 的釘選比較。

LIVE checker 單獨測不出學生本機 localStorage 是否正常，需要保留另有 Playwright 真實資料兼容測試，不能宣稱 HTTP checker 已覆蓋瀏覽器內個人紀錄。

只要有人改動第5題答案卻沒更新可信發布內容，第3預覽圖或第2共用圖 SHA 錯、sourceRevision / teachingDigest 不符，必須 FAIL CLOSED；未通過 CI 不得發布新頁面。
