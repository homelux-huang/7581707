# 部署 Session 接續 QA：2026-10-24

基準教學 commit：f049edaac5bf7f12acd9f7996bccc305d68b7d53。
隔離 main：5415a30452cdf9020242aca16fe0ff2b6814ab4b。

## 本輪實作與證據
- 已讀 DEPLOY_SESSION_HANDOFF_128.md 與 content-review-delivery-20261024.json；本批仍非發布核准。
- tests/test_preview_128_oct24_content.py：5 tests PASS，包含10張實際WebP bytes SHA與10題teaching canonical SHA、三題爭議隔離及運算檢查。
- audit_preview_teaching_drafts.py：128 records、0 errors；僅結構驗收，非教學或UI合格憑證。
- 直接開啟數學B20、25既有原圖：20之AB=100、A=60°、B=75°與四選項一致；25之距離為√2，四選項−59/−16/−10/10。
- 獨立重算（已知官方答案，非盲解）：20得C角45°，AC=100 sin75°/sin45°=50(√3+1)，對應A；25配方得h=4、r²=a+16=2、a=−14、h+a=−10，對應C。
- 修正25選項A：刪除未證實的錯算成因猜測，改為代入h+a=−59推出a=−63、r²=−47，不可能的具體反證。保留全部未發布旗標，同步交付manifest教學SHA。
- V4隔離預檢原本只有鍵盤Enter；改為寬度<1024真實tap、桌機真實click，禁止force或DOM模擬點擊。仍測7題數學B19–25、8尺寸×2主題、原圖decode、四選項、計算、問答切換及錯題復習。
- 上述預檢仍使用QA-only route fixture，且部分選項為原圖提示佔位文字；即使PASS也不是完整教學UI憑證。不得據此放行正式資料。
- 本機首次瀏覽器啟動缺少Chromium；下載未取得可用zip，因此本機未宣稱UI PASS。交由既有read-only GitHub workflow執行，結果以實際run為準。

## 邊界與待辦
完整教學QA、完整UI QA、READY_FOR_DEPLOYMENT、新增部署均仍0。
商概07、數科33、經濟28維持隔離；math20–25候選OCR風險不解除。
仍需10題全項獨立教學審核，以及各科真實教學欄位、highlight、觸控與錯題卡的完整UI證據。
未修改main、approved、正式UI、OCR或WebP。
