# 7581707 學習頁：上一題／下一題導覽位置

更新：2026-10-18

- 以現有的「上一題」「下一題」按鈕，直接顯示在「白話解說｜小學生也懂」區塊**下方**。
- 使用左箭頭 ← 與右箭頭 →，中間保留「目前題號／本份可讀取的總題數」。
- 保留現有上一題、下一題的事件綁定和學習進度，沒有修改 localStorage、IndexedDB、錯題或裝置代碼。
- 在 `suduWorkspaceApply()` 把同一組導覽節點移至 `data-block="explanation"` 後面；即使學生自訂區塊順序，也會緊貼白話解說區塊。
- 隱藏舊底部重複導覽列，避免學生看到兩組切題按鈕。
- 淺色與純黑主題採高對比按鈕，320–375px 手機縮小按鈕間距並保留原文可讀性。
- `tests/sudu_browser_smoke.cjs` 驗證導覽緊貼解說、無重複底部列、上下題確實能切換。
- 驗收依據：GitHub Actions [Browser smoke test Sudu](https://github.com/homelux-huang/7581707/actions/workflows/sudu-browser-test.yml)，不可在執行前宣稱通過。
