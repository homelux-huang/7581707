# 7581707｜128 題教學發布逐題證據閘門與正式交接（2026-10-23）

## 本輪發布授權與現況

使用者已授權：**完整逐題教學＋UI 驗收與 Same-SHA 發布檢查通過後，可自動整合現有 main、發行正式 GitHub Pages；不再需要逐批詢問。** 這只取代舊文件「草稿先不發布」的程序性限制，**不降低任何真實 QA 門檻**。

- 固定範圍：128 題，**不增加年度、科目或題號**；採 `progress.json.items` 作為唯一集合。
- 128/128 已有教學草稿、原圖逐題目視紀錄（含英文 2 份共用圖片）、官方最終標準答案與確認說明核實證據。
- 128/128 的獨立完整教學審查及 V4 內容 UI 審查仍為 **PENDING**；`fullyAccepted=0/128`；本批新的教學正式部署 `0/128`。
- 既有 main 原本已核准的 115 數學 B 02、03、04、09 **4 題可作答**是另一份已核准 QA 的來源，不代表本 128 題草稿已完成教學審核，也不可直接以其正式資料倒推草稿發布。
- [GitHub read-only run #39955543950](https://github.com/homelux-huang/7581707/actions/runs/39955543950)：原圖/公告/步驟完整性 SUCCESS、來源新聞近三年日期 6 件合成測試 SUCCESS、逐題發布防偽 9 件合成測試 SUCCESS，dry-run **`releaseEligibleCount=0`、`blockedCount=128`**。這是正確 fail-closed 結果。

## 新的獨立發布候選稽核

由 `scripts/audit_preview_128_teaching_candidates.py` （唯讀）執行，**保留**舊有 `scripts/audit_preview_teaching_drafts.py` 草稿完整性稽核與全部隔離旗標。未通過的題目不能放行。

一題欲成為正式候選，必須全部具備：
1. 凍結題號與年份、題號對應的單題 WebP 實體 SHA256 與來源 manifest 完全一致，確有四選項各自老師/國小雙層解說。
2. TCTE 官方標準答案／疑義核實，不得與 AI 初解未定或不一致。首次 AI 不同但看過答案才更正者仍保留獨立複核阻塞，不偷改首次解答。
3. 有計算的題目逐步式、結果、單位與正解相符；無計算者 UI 不出現空框，需完整教育內容的獨立驗證。
4. 單題 `qa.independentTeachingReview=PASS`，`qa.uiReview=PASS`，`qa.textHighlightRendering=PASS`；不能由結構成功或答案字母一致推算。
5. 獨立簽核憑證 `release-certificates-128.json`：以題目 ID、WebP SHA、教學內容 canonical digest SHA256 綁定；老師與 UI 審核獨立證據應具備 reviewer、日期、可核實檔案路徑及其實際 SHA256。
6. 真實 V4 題目/正解/記憶/共用文章、錯題復習、底部操作及警告，**8 個 RWD 尺寸 × 2 個主題**均 PASS；憑證對應每項具體測試記錄，不可僅憑 35 題 Demo 成功推斷新的 128 題內容。
7. 彰化高商適用的 114 學年度教材、章節、頁碼未查證必須如實「待核對」，自編時事例句不得冒充新聞；來源型英文例句必須在近 3 年、日期不能在未來、實際重點字形必須出現在句中。
8. 草稿本身 `studentReleaseApproved=false`、`deploy=false` 不更動；正式新核准輸出應另走增量 staging + 原本 main 的 QA admission and release gates，且一次僅放行逐題通過者。若沒有單題合格，**不發布**。

**實際阻塞分群（以本輪連續證據為準）：**

- 真正 AI 與官方答案仍不同或未決 **3 題**：`115-09-1-07`、`115-09-1-33`、`115-09-2-28`。官方最終答案 B/A/A 均已確認，剩教材定義／教學裁決；上述警語和歷史不可刪。
- 已知原 AI 首次判讀與公告不同、看過候選後才改成相符的**至少3題**：`115-09-2-06`、`115-09-2-12`、`115-09-2-15`。這三題現在 `aiAnswer` 與官方相等，但 `conflictWarningRequired=true`，**仍待獨立非事後驗證**。最新實際 dry-run #39956497768 還揭露 **總共21題**「現行字母相同但仍有警示／旗標不是明確 false」；另18題不能擅自推斷皆屬首次錯答，應讀各題明細逐一審核。加上現行 AI 字母仍不同的3題，共 **24個非完整教學可放行案例**（沒有重複ID，未完成的完整內容/ UI證據另有128題），絕不可只看6題就把剩下122題視為合格。
- 全部 128 題尚待獨立內容 QA、8×2 UI/互動 QA、逐題 SHA-bound 正式教學 release certificate；`releaseEligibleCount=0`。
- 正式 V4 `sudu/v4-115-multisubject-review-demo.html` 與 `sudu/verified-questions-runtime.js` 目前只承接 `sudu/data/approved` 的已核准資料。公開 build allowlist 排除草稿，**目前沒有新128題正式 V4 教學快照的 UI 渲染／8×2證據**。草稿工作流程只在隔離環境跑既有 35題 Demo smoke，不能誤當這 128 題的個別 UI QA。

## 本輪具體修復

- [Commit `9b0c4cd6`](https://github.com/homelux-huang/7581707/commit/9b0c4cd6f28071e0915b3712465ed5d81ec74a3d)：115 數學B02/03/04/09 直接讀既有單題 WebP，獨立算式與 A-D 選項局部覆核；將目前錯誤過時「最終答案待回讀」文案更新，舊文保存在 `qa.mathContentRecheck20261023.previousNotice`，不新增完整教學QA、不變更 `solution-steps-128.js` 和 approved 學生資料。
- [Commit `7163cbf0`](https://github.com/homelux-huang/7581707/commit/7163cbf004293079bfeedea0025b57820ba95c6f)：來源型英文時事例句嚴格驗證 ISO 日期在「近三年且不超過今日」；6 項合成回歸 PASS。英文 22／28 有來源型改寫新聞語境，其餘6題仍標自編示例。
- [Commit `6990025a`](https://github.com/homelux-huang/7581707/commit/6990025a62cb1ace4abfa16ff3b2b60eb2abfb97)：新增個別教學+UI證書 fail-closed 稽核、9 項 synthetic regressions，沒有修改任何 releaseApproved、QA PASS 或正式 UI。
- 本批後續修正把「真正字母不同」與「舊初解差異尚未盲核」分開列 blockers；兩種均不得放行，不得用變更警示來解鎖。

## 後續自動續作優先級

1. 最新 HEAD 重新讀取、跑草稿完整性與逐題 eligibility dry-run、確保 128 與 2 shared WebP SHA 不變，不覆寫其他 Session。
2. 優先 115 數學B已有確實原圖及公式的題，逐題完成教師解說與四選項獨立複核、教材確認（無來源即待核），做**真正 V4 對應題目內容**的 8×2 Chromium/UI 截圖、答後跳正解、一眼記住、highlight及觸控、錯題複習並存測試可追溯 SHA。
3. 三題硬爭議與三題歷史初解差異保持阻塞，能確定教材與官方使用術語時才逐題核實；不為解鎖造數字或偷改 `aiAnswer`。
4. 英文其餘6題若沒有真實新聞來源，保留自編；不把來源不足當成有新聞。各科精確課本版本章節頁數不足保持待核。
5. 只有有單題真正合格的 certificate、QA source 合格且正式 public allowlist 僅增量加入時，建立非衝突 PR、同 SHA 全部 Playwright/browser/CI SUCCESS 後依最新授權安全 squash merge，最後檢查 Pages verify/build/deploy/verify_live 及 Live `release.json` SHA 一致。沒合格題目不可提交「空發布」冒充128已上線。


## 最新修正後的同 SHA 驗證證據

- [GitHub Actions #39956497768](https://github.com/homelux-huang/7581707/actions/runs/39956497768) 同一 commit `c5079f453968aebaa756a42ea06972d5d738f419`：日期檢查 6/6、個別發佈防偽回歸 11/11、官方資料及原圖整體結構檢查 PASS；dry-run releaseEligible **0/128**。
- 稽核結果顯示真正字母不一致 **3**、其他相同字母但警示未清 **21**，分開統計不再含混。下次從新 CI 結果的 `answerDisagreementIds` 逐題檢查警示的原由與證據；不得僅因 AI 現在字母等於官方就清除首次推理分歧。
