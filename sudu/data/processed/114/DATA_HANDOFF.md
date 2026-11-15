# 114 年商管群題庫｜隔離資料工程交接（不可正式放行）

資料範圍：114 年、共 205 題候選，來源 TCTE 官方試卷及既有單題 WebP。僅供 QA 分支驗證，**不得合併 main、部署 LIVE、或寫入學生資料**。

## 截至 2026-10-23 的核對基準

- 單題圖片 G1 已完成直接原頁目視 QA：**35/205**。其餘 170 題仍須檢查；不可把 decode/SHA 檢查當作目視驗收。
- 官方最終答案與疑義更正 G3：**0/205**，仍須完整逐題查核。
- 全題 OCR/文字 G2：已記錄 **1/205** 完整驗收；其餘尚未完成。C19、C23 僅已校正選項 D 的跨題／跨頁污染，未計入完整文字 PASS。
- Q19 的舊 v1 裁切混入 20–23 題共用文章，已保留為失敗證據；新的 v2 及第 20–23 題共用文章均已完成直接原頁目視與 SHA QA，且回填關聯。
- 已回填 C20–23 的共用文章關聯；其他共用材料與題號關聯 G4 仍待完善。SQLite G5 須獨立再執行雙次匯入、逐筆 JSON/SHA 讀回及紀錄。

## 重要產物

- `questions.json`：題號、答案候選、圖片及文字狀態，並不代表可正式接入。
- `webp-manifest.json`：來源原頁、裁切座標、WebP 路徑、SHA256 及圖片 QA 狀態。
- `VISUAL_QA.json`：逐題目視紀錄與證據連結。
- `qa-drafts/DIRECT_VISUAL_114_C11_15_20261023.json`：C11–C15 直接原頁目視與六張檔案 SHA256 的核查證據。
- `qa-drafts/OCR_VISUAL_114_C19_C23_20261023.json`：OCR 原文與校正、Q19 舊版圖片阻塞。
- `qa-drafts/DIRECT_VISUAL_114_C19_23_SHARED_20261023.json`：C19 修正版、C20–23 與共用文章的直接目視 SHA QA。
- `REMAINING_QA.md`：各題待辦清單與已確認缺陷。
- `release-manifest.json` 與 `VALIDATION.json`：僅顯示部分 QA 進度，releaseAllowed / integrationReady 皆為 false。

## 後續門檻

依 `docs/SUDU_QUESTION_BANK_QA_GATE_105_115.md` 完成 G0–G6；所有題目、共享材料、官方最終答案、OCR 及 SQLite 驗證都 PASS，方可另外審查是否准許整批接入。

**目前 integrationReady=false；不宣告完成，不更新正式站。**
