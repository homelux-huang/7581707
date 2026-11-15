# G8 原始證據長期保存與固定程式版本讀取政策｜候選契約

日期：2026-11-15（台灣）。接續 PR211＋PR213，不直接修改 main、信任清單或學生資料。

## 解決的程式問題

1. 原始 Actions artifact 有保存期限。若每次重新產生學生資料都要求該 artifact 仍未到期，未來會失去已完成的 G8。
2. PR213 正確要求正式測試和 promotion 使用同一 codeCommit。但該版本本機政策不含稍後才經 owner 核准的 G8；只讀舊 checkout 的政策會使 promotion 永遠 HOLD。

新增 `scripts/sudu_g8_archive.py`，並在既有 bridge 中接入。bridge 從 GitHub 實際 protected main 讀取當前政策。Native publisher 只接受明確傳入、且再核對與 GitHub protected main 完全一致的 `review_policy`；舊呼叫不傳入時，行為不變。沒有 CLI「授權」開關，也沒有改寫本機或遠端政策。任何網路／政策核驗失敗均 HOLD，不退回過期政策。

## 長期保存流程與信任界線

1. 真正 G1–G7、正式 Chromium16/16 完成後，先取得原始 artifact.zip 及其真實 run/job/artifact ID。
2. artifact 尚未到期時，執行 capture。程式向 GitHub 實際核對成功的 main 手動 formal workflow、job、artifact SHA256、原始 report 及16PNG。確認 report → artifact建立 → capture → expiry 的時序。
3. 只產生 `CAPTURED_PENDING_INDEPENDENT_OWNER_REVIEW`。這不是 PASS、信任核准或部署。
4. 原始 ZIP 不重新壓縮，保留同一 bytes。僅允許 report.json 和16個指定 PNG；不接受其他檔案、重名、路徑、symlink、超大內容或錯尺寸 PNG。
5. 經真正獨立審查後，以正常受保護 PR 保存：
   - `sudu/release-governance/g8-archives/QID/ARTIFACT_SHA256/capture.json`
   - 同路徑 `original.zip`
   - 對應 owner 審查後的 protected `trustedG8Receipts[QID].durableArchive`。
6. `capture.json` 保留必要的、capture 時從 GitHub 查得的 run/job/artifact metadata，以及完整原 G8 receipt 綁定。排除 GitHub 個人資料、URL/token、模型 request/response、API Key、原始私有 G6 及整個 staging 網站。
7. 後續 native/promotion 核驗時，**仍向 GitHub 即時核對原成功 run/job 與 capture 完全一致**，不能僅憑 snapshot 捏造執行；只有會到期的 artifact 儲存由受保護原始 GitBlob 替代。必須重新證明目前受保護政策仍保有完全相同的 receipt，並沿 protected main commit 的 Git tree 逐層確認 capture/ZIP 的 regular-file GitBlob。重新核對原 ZIP SHA256、capture 時序、原 run/job/未到期 artifact metadata，以及 report、所有PNG／16矩陣／codeCommit／HTML/runtime/serializer bindings。
8. 因為原始 bytes 已在 owner 核准的 protected Git 歷史中保存，且原成功 run/job 仍可即時核驗，Actions artifact 後來到期不撤銷原始測試；owner 移除或改變 receipt、GitBlob 變動、來源／教學／程式不符、GitHub protected-main 讀取失敗，仍會 HOLD。

**不以任何本機 snapshot 自動授權。** Capture 候選可能被修改，owner 與獨立審查必須在 artifact 仍可核對時，對實際 API、ZIP、manifest、PR exact head 作審查。受保護 main 中的精確 owner pin 是長期可信根，不是操作者自行寫的 PASS。若未完成及時 capture／獨立核驗，artifact 已到期，不能事後偽造 metadata；必須重新執行合格的正式 G8。

## 指令

只有真實 G8 完成後才可執行，現在不得用範例資料當正式證據：

```bash
python -m scripts.sudu_g8_archive --entry REAL_PROPOSED_G8_RECEIPT.json --qid MASTER_ASSIGNED_QID --archive ORIGINAL_AUTHENTIC_ARTIFACT.zip --dest /tmp/sudu-g8-UNIQUE_CAPTURE
```

候選會產生兩個待 PR 審查的原始證據檔，以及 `G8_OWNER_REVIEW_CANDIDATE.json`。程式不會上傳、修改政策、建立信任條目、merge、部署或呼叫模型。

Promotion 仍須使用真正 formal run 的**同一 codeCommit**，讀取當前 protected policy 並通過全部原有 G0–G10。原始 ZIP 必須保留在正式 report 目錄供 promotion 的 bytes 比對。沒有 durableArchive 的既有候選，繼續用原有即時 Actions artifact 驗證，不能偷偷降級成未驗證離線模式。

## 保存與安全風險

- 只保存原本可公開的題目呈現 report/PNG；含私人資訊的截圖不得提交。未實際產生真實截圖前不宣稱已確認可公開。
- 這使用現有 Git 儲存，不建立付費資源。公開 screenshot ZIP 的實際大小及長期 repo 容量須在首個真實 archive 後量測；目前沒有用量或費用數字。
- GitHub API outage／policy revocation 仍 HOLD；這不是不需 GitHub 的離線授權。
- 存在資料競爭時，protected policy equality 或 commit/tree binding 失敗會 HOLD。讀取已固定 SHA 的 Git tree 可在程序內快取，當前主分支／政策不快取。
- 使用 Actions 的唯讀 GITHUB_TOKEN 時不輸出 token。沒有建立或讀出任何 OpenAI API Key。

## 測試與剩餘條件

新增 archive 測試全部是明確的 synthetic 權限、ZIP、PNG 和 metadata。涵蓋到期前捕捉、未授權不核准、失敗／錯 run／過期／錯 digest、受保護 owner 撤銷、原 bytes 變動、到期後原證據可讀、時序、額外 ZIP、tree path/symlink、固定程式讀取新政策及拒絕偽造 override。這些不是實際 E/G6/G8。

仍須獨立 code/security 審查；真實作者／E session；真正隔離首次 G6 與 G7；授權 private runner；正式16/16；真實 capture＋審查＋protected trust PR；最後逐題 publisher PR、CI、Pages、same-SHA verify_live。E12 維持獨立 HOLD。
