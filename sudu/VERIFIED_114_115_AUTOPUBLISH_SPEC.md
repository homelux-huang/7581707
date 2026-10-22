# 7581707｜114／115 題庫自動接入與正式部署驗收規格

更新：2026-10-22（Asia/Taipei）
正式專案：homelux-huang/7581707
正式 V4：sudu/v4-115-multisubject-review-demo.html
進度頁：sudu/question-bank-progress.html

## 自動執行

- GitHub Actions：.github/workflows/sudu-verified-autopublish.yml。
- QA 分支上的官方品質 workflow SUCCESS 後自動觸發；另有每小時的 QA 更新核對及手動執行入口。更新經過審核後自動提交 main 並觸發原有 pages.yml；不要求使用者反覆核准，一般程式與部署自動進行。
- 來源：qa/114-115-official-visual-review 的 sudu/data/processed/114 和 /115。使用獨立 checkout 與 source SHA，不執行來源分支程式；不重抓原卷、不 OCR、不裁切、不改動任何原始單題 WebP、答案來源、SQLite、學習資料或 backup/Git 歷史。
- scripts/sudu_verified_publish.py 僅將通過全部關卡的個別題目複製到 sudu/data/approved/114.json、115.json 和獨立 approved/webp；全部待核對題目隔離，不列入正式作答。原始來源不會刪除。
- 自動更新成果須完整通過 .github/workflows/sudu-release-checks.yml，包括 GitHub Pages 同 SHA 稽核、原 35 Demo、Browser Smoke、8 組 RWD 雙主題、新正式年度驗收。
- 即使檔案同步成功，尚未經 Pages deploy SUCCESS 與 LIVE release.json 回讀成功，不得標記為正式部署成功。
- 若來源未變，或只有其他年度 QA 分支內容變更，使用 114/115 來源子樹 SHA 判斷是否需要更新；不得浪費發布次數。

## 教學 QA：兩個學習層次

每題不論難易，四個選項 A/B/C/D 都必須提供：
1. 「高職生理解」：像有教學經驗的技高老師，按照課綱說明本題知識、原理、選項正誤與解題關鍵。
2. 「國小學生也聽得懂」：不用艱深術語，以生活比喻、短句、具體理由，白話說清楚為什麼正確或錯誤。
3. 「一眼記住」、核心觀念、延伸閱讀／觀念、教材來源。優先彰化高商版本；無法證實頁碼標註「待核對」，禁止猜頁數。
4. 文字、算式的關鍵詞以高對比粗體標記，並在頁內方便展開，保留既有 V4 UI／深淺主題／單手大觸控按鈕。

數學、經濟學、會計學與其他需計算題：
- 指定 teaching.calculationReviewed=true；teaching.hasExamCalculation=true 時 teaching.examCalculation 必須有 given（已知）、formulaUse（公式用途）、substitution（代入數字）、steps（中間運算完整算式）、result、unit（需要時）、option（對應正確選項）。
- 觀念題 teaching.hasExamCalculation=false 時，不渲染「考題計算式」項目、空框或「本題無金額計算」占位。
- 不得自行補題目沒有的金額、利率、數量或預算。數學含非金額運算照樣顯示。經濟第28題 250 元不得冒充題目已知預算。
- 解說、正確答案、一眼記住延伸與錯題復習共用相同課程欄位。

## 發布欄位與證據

年度來源 questions.json 中每題需保留：questionId、year、paperCode、originalQuestionNumber、subject、完整題幹／四選項、assets.singleQuestionWebp、questionProvenance、answerProvenance。

放行時須同時提供，且 QA JSON 內可追查 reviewer／reviewedAt、evidencePath、evidenceSha256：
- 該 WebP 的 manifest qaStatus=PASS，原始檔 SHA256 等於 visualReviewEvidence.reviewedSha256；共用材料亦需獨立 QA PASS；真正的 QA 證據檔案（reference/referenceSha256）存在且 SHA 一致。
- questionVerified=true；textQaStatus=PASS；textQaEvidence 需與 OCR 修正後題幹選項內容和該題 WebP SHA 對應。
- 最終官方答案：answerVerified=true、officialCorrectionChecked=true、officialFinalAnswer=A/B/C/D、officialFinalQaEvidence.finalCorrectionsReviewed=true；必須匹配 PDF SHA 和實際更正來源。
- independentSolve：solvedWithoutOfficialAnswer=true、officialAnswerHiddenDuringSolve=true、解題 input 的 questionRevision、solver、solvedAt、reasoning、answer、auditEvidencePath、auditEvidenceSha256。輸入 Revision 是「題幹＋四選項＋單題圖 SHA」的雜湊，不包括官方解答；版本異動自動失效，AI 與官方不一致不能放行，警示須列雙方答案。
- teachingQaStatus=PASS、uiQaStatus=PASS、studentReleaseApproved=true，且 teachingQaEvidence、uiQaEvidence 均有 SHA 對應真實檔案；教學包含 teacherSummary、elementarySummary、memory、concept、extension、source 和四個 optionExplanations，四選項各包含 teacher、elementary、reason。
- 公式與計算欄位依本文件上節規定；所有條件均須在 QA source branch 完成，不能僅憑複製官方答案或 CI 結果假造 PASS。

## 年度題庫與既有使用紀錄

- V4 原始 HTML、35 題 Demo、既有教學設定及學習歷史鍵維持原樣。Build 僅在部署副本附加 verified-questions-runtime.js。
- 學生由相同 V4 頁面 ?year=114、?year=115 切換已核准題庫；正式年度使用獨立 localStorage key，不覆蓋 Demo 裝置/答題/錯題紀錄。
- 數科／商概仍按 09-1 的第 1～25／26～50 題映射；會計／經濟按 09-2 的第 1～24／25～50 題映射，不更改官方原題號。
- 題庫 approved 為 0 時，年度入口會顯示「尚無通過完整 QA 的題目」，不以原 Demo 假裝年度已完成。
- QA fail/撤銷時從公開 approved 副本撤下，保留資料分支原始影像、答案與紀錄。整批 G6 年度結束仍須全數驗證，單題公開僅代表該題獨立通過全部門檻。

## 進度計算與初始現況

- 115：官方候選 205，單題 WebP 205，已逐題視覺 QA 133（64.9%），另 72 題待目視，共用材料 3/20；OCR 校正與最終標準答案更正尚未逐題完整驗收、AI 盲解與教學未完成，正式可用 0/205。
- 114：官方候選 205，單題 WebP 205，逐題視覺 QA 0/205；另有 13 題缺完整選項，最終答案、OCR 與教學未驗收，正式可用 0/205。
- 公式：年度圖片 QA 進度＝圖片逐題 PASS／預期題數；年度正式學生可用百分比＝當年度完整通過資料、AI 盲解、四選項雙層解說、計算及 UI QA 題數／預期題數。
- 進度表 sudu/question-bank-progress.html 讀取 sudu/data/approved/progress.json：這是 Pages 正式部署後的快照，不因 GitHub 綠燈或候選檔案存在就宣告完成。
- 105–113 未包含在這次自動開放規則中，其他分支的資料工程可繼續，但不得用未驗收資料覆蓋已核定題目。

## 2026-10-22 實際同步觸發修正

GitHub Actions 使用內建 `GITHUB_TOKEN` 建立的 main 提交通常不會再觸發其他 `on: push` Actions。因此同步 job 在推送最新 approved QA 快照後，必須以 `actions: write` 權限明確執行 `gh workflow run pages.yml --ref main -f target_sha=<已提交 SHA>`。這不是繞過 release gate：它只觸發原本的 Pages 同 SHA verify/build/deploy/verify_live，所有檢查保持原樣。不能因 main 有新 commit 就假稱 Pages 已經部署。


## 2026-10-22：逐題圖片 QA 完成即可先行部署

已變更成漸進式兩段放行：圖片與所需共用材料逐題目視 QA、SHA、來源證據及 WebP 解碼都通過時，只將原始影像和題號、年度、科目公開到 sudu/data/approved/preview/ 年度 JSON，於既有 V4 題庫年度模式唯讀預覽；絕不包含未核實 OCR、官方答案、教學詳解或計分。只有後續官方最終答案、獨立解題、四選項高職老師與國小白話解說、適用完整計算式與 UI QA 全過，才升級為可正式作答。年度 100% 不再是單題放行前提。同步 workflow 會在資料 QA 變動或新預覽 schema 生效時，自動逐題補入，不需使用者確認；只在 Pages 完整 release gate、部署及 LIVE SHA 回讀成功時視為已發行。

最新資料工程盤點：114 年 205 候選，9 題 WebP 圖片 QA PASS，可唯讀預覽 9 題；115 年 205 候選，135 題單題 WebP 圖片 QA PASS，經共用文章/圖表關聯確認可唯讀預覽 119 題。兩年度共 128 題可先展示原始 WebP；剩餘部分持續自動依 QA 補入。正式學生可作答仍 0 題，不能把只過圖片 QA 誤認為獨立解題或教學 QA 已過。
