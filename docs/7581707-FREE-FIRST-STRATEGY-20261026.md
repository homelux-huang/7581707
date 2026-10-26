# 7581707｜104–115「免新增付費」優先運作方案（2026-10-26）

> **本文件只描述可驗證、可使用現有免費資源的流程，不是第二套 114/115 題庫台帳，也不是老師、E 內容 QA 或學生 READY 授權。**

## 目前實際可用與不可用

- 儲存庫 `homelux-huang/7581707` 是**公開** Repo；GitHub 標準 GitHub-hosted runner 在公開儲存庫通常不計執行分鐘費用。官方：<https://docs.github.com/en/billing/concepts/product-billing/github-actions>。仍需留意工件儲存限制、Actions rate limits、GitHub 遵循條款；不可濫用免費計算資源跑龐大模型推論。
- 之前已建立的 GitHub `CODEX_API_KEY` Secret 只代表名稱／存在性已驗證，**不是 API 模型可呼叫**。2026-10-25 使用者帳戶最後報告 OpenAI Platform credit US$0.00。未經允許不可新增付費方式、購買額度或排程 Codex API 推論。
- GitHub Models **已於 2026-07-30 全面退役**，不可以當成免費模型。官方：<https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/>。
- GitHub Copilot **Free** 可能提供有限 CLI／Agent 使用額度，但並非 288 次／日的無限 gh-aw 推論，也不保證帳號、GitHub AI Credits 或授權已配置。需在本人 Copilot/計費介面核對實際剩餘額度。官方：<https://github.com/features/copilot/plans>、<https://github.github.com/gh-aw/reference/billing/>。
- Google Gemini Developer API 有部分模型的免費層級及速率／每日額度限制，免費層級資料**可能用於改善 Google 產品**，不能用來上傳學生個資／帳號／未授權私人內容。官方：<https://ai.google.dev/gemini-api/docs/pricing?hl=zh-TW>。如需使用請另外配置最小權限 `GEMINI_API_KEY`，先核准非付費測試、確認帳戶免費層級；`gh-aw` Gemini engine 已列 deprecated，不應未測直接替換現有 Codex lock。
- 本機 `Ollama` 可在 Windows 執行開源模型，**沒有第三方逐 token 模型費用**，但要有足夠 RAM/GPU、硬碟及電力，並保持電腦開機。官方：<https://ollama.com/>。如果要自動處理工作，建議使用本機受限的 Windows 工作排程器讀 GitHub 待辦、以 `localhost` 呼叫本機模型、寫入獨立 Draft PR；**不要**把目前公開 Repo 的不可信 PR 工作直接派送到同一台私人 Windows 的自架 GitHub Runner，這有 RCE/洩漏權限風險。官方：<https://docs.github.com/en/actions/reference/security/secure-use>。如需安裝／改電腦服務或授予本機執行權限，使用者另行在 Computer Use 環境授權，這份文件不代表已安裝。
- 所有「五分鐘自主 A/B/C/D/E 免費 AI」都依賴**真正可呼叫的模型或本機電腦**；沒有該項，就先做規則式免費巡檢，不能謊稱子對話已被喚醒。

## 無需 AI 付費即可持續運作的兩種 Actions（各自分工）

### A. 5 分鐘 GitHub 唯讀工作收件
- 既有 Draft PR #82 包含腳本 `scripts/sudu_master_five_minute_watchdog.py`、定時 `2-57/5 * * * *`、`CLAIM/RETURN` 不假造、掃描全部開啟的 PR、GitHub Actions Summary + 1 天 JSON artifact。
- **啟用條件**：不同 MASTER 作者的獨立安全稽核及受保護 `main` 既有必要 PR gate 通過、再以一般 PR 合併，確認至少一次真實 `event=schedule` 及完整 artifact。Draft PR 或一次 `pull_request` SUCCESS ≠ 已啟用 cron。
- 此收件器本身無 GitHub write/model permission，不能派出會寫程式的 AI，也無權批准來源、解答、E 或 D。

### B. 12 年零模型「候選來源／已核准名單」進度稽核（本 PR）
- `scripts/sudu_free_first_progress.py` 讀**main 分支存在的原始年度** `sudu/data/years/{104..115}.json`、僅 114／115 `sudu/data/approved/{year}.json`，逐年度列出：原始5個試卷檔、陣列實際題數、歷史 `questionsFound` 差異、自動答案配對（**非 verified**）、legacy `questionVerified/answerVerified/teachingVerified` 旗標、原題有疑義、已在 main approved allowlist 的題數、待 A 來源核查的下一批候選 ID。
- **沒有**把任何原始來源、含糊 OCR 或自動配對升級成 PASS，也不會依歷史 205 題推定 104～113 的官方完整題數；專業科目試卷需要年份別七科來源映射，不把五原試卷當七個教學科目。
- `approvedCount` 僅代表 **main allowlist**，不能直接等於學生可作答 LIVE；必須另查 `sudu/release.json`、既有 Pages 發布／實際瀏覽器相同 SHA 證據。腳本對 `newReadyNotProven/newLiveNotProven` 明確保留 `null`，而非自動標 0 或 100。
- GitHub Actions Workflow `.github/workflows/sudu-free-first-progress.yml` 使用公開 Repo 標準 Ubuntu Runner、**只讀** `contents:read`、每 6 小時及官方/approved JSON 變更時觸發，產生 1 天 artifact，沒有任何 AI API 呼叫與 secrets 使用、推送／合併／部署能力。
- `tests/test_sudu_free_first_progress.py` 的來源 ID、SHA、答案混淆、approved schema 與防止自動 READY 的對抗測試必須通過。若官方來源不一致 FAIL CLOSED，不能為求綠燈更改來源或減少 assert。

### C. 已存在的嚴格發布器（避免重新造輪子）
- 現有 main `.github/workflows/sudu-verified-autopublish.yml` 已會檢查經 QA 批准的增量資料（定時／來源變更觸發），並保留嚴格 `scripts/sudu_verified_publish.py`。新的免費稽核只幫助收件、找缺漏，**不覆蓋發布器，也不批次 READY**。
- 真正逐題准入仍需要正確官方題號、原始單題 WebP/共用材料原像素與 SHA、OCR/SQLite 一致、官方最後答案與更正、四選項高職＋國小雙層解說、必要計算驗算、不同作者 E AI 內容稽核、對應 35 題 Demo **該科 V4** 的 8 尺寸×深淺色 UIQA、正確 revision/digest、受保護 main、Pages、LIVE 相同 SHA。
- 未達到以上條件的題目仍可在 Draft PR 續作、由角色 A～E RETURN，不能假裝已在網站。遇到有疑義的題先隔離，**下一題合格時不用等全年度才發布**。

## 免付費工作優先順序

1. **114／115**：保留已在正式平台的五題，不回退。把現有 A/B/C/D/E 的 Draft PR 真實 RETURN 由 Issue #36 逐筆收件：來源 → 完整教學 → 不同作者獨立 E → D 真實 8×2 → MASTER 單題 READY 裁決；先已 QA 的題目發布，其他持續補。
2. **104～113**：復用原官方年度 JSON，不重建 OCR／WebP。先由 A 補官方來源、原始圖表裁切與年度專科對應，B/C 以來源 SHA 撰寫逐題雙層教學，E 獨立審查，D 使用既有 35 Demo **科目專屬 UI**。依一批 1～5 題分次完成。
3. 每輪先比對 Issue #36 真正的 CLAIM/RETURN 與各 PR 最新 HEAD、CI、來源和教學 SHA；不重做 SHA 未變且有正式 QA 證據的已驗收題目。原有 114／115 唯一逐題台帳 `docs/114-115-QUESTION-DELIVERY-LEDGER.json` 仍在 PR #30，這裡**不新建第二套題庫台帳**。
4. **沒有模型服務／本機 GPU 時**：保持免費定時程式持續輸出來源缺口、可審查候選與已核准名單；待有免費模型額度的 ROLE Session / 本機 Ollama 真實執行後，再處理 AI 說明及獨立審查。不得在免費計算平台啟動未獲准的付費模型 API。
5. 本 PR 作者是 MASTER，不是 E；本 PR 是候選進度工具，需另一 ROLE E 完成獨立程式／安全驗證，不能作者自行批准。永遠不把這份來源自動稽核當成官方教師/答案/單題照片的替代品。

## 關於額度
- GitHub Actions 免費只包括公開標準 Runner 計算，仍有限流／執行與工件儲存上限；本工具已刻意每6小時跑一次、每次保留 artifact 1天。
- 真正每5分鐘執行 288 次/天的 AI 推論**不保證免費**，即使 GitHub Actions 計算免費，Copilot / Gemini / OpenAI 仍有各自配額、限流或付費條件。
- 完成任務的證據優先存入 Issue #36 及 Draft PR SHA；任何服務過期或配額耗盡，**fail-closed + 接續下一項可以免費完成的工作**。

