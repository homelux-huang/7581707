# 原 Session 修復與補齊完整執行命令

BEGIN ORIGINAL_SESSION_FIX_DIRECTIVES

你是 homelux-huang/7581707 原資料工程／128教材修復執行 Session。稽核報告位於 audit/128-independent-release-verdict-20261024 分支 sudu/release-audit/independent-20261024/，唯一固定範圍為 draft/preview-128-explanations-20261023:sudu/teaching-drafts/preview-128-20261023/progress.json.items，共128題，絕不變更分母。先以GitHub重新查 main、QA、draft、MB20-25四個HEAD，稽核時依序是57d766e841235b937babf3fe10a8ff44606c7c41、2c1a958b56980a7cbf49a9eb1c35cf64ced5f9ba、c4cdb10ea61f70e0184f0a078963ebb537a9cc99、0b1343fb7853701ec847fd33321cc792c3172bbf；如有新HEAD，以新HEAD重新對帳，不能覆寫其他Session提交。main/正式學生資料保持不變，僅對確有全Gate合格新題經原有workflow非force增量上線。

P0-01：先阻斷 self-attestation 不足以證明真正另一獨立reviewer的放行路徑。修改 scripts/sudu_verified_publish.py 的 apply_independently_certified_review (約484–572)、teaching_complete(196–230)、certificate_exists(250–260) 及其審稿證書驗證；tests/test_sudu_verified_publish.py 先新增**失敗**用例（同一原作者自行寫教學與自稱不同 reviewer、完整SHA與PASS欄位卻缺少可核實不同審核事件，必拒；改reviewer字串不改善；真正具授權且提交四選項/解題/解說之審核事件才允許）。審稿權限取自受保護的獨立審核事件、受控簽章或具操作審計的合規來源，不能信任原作者自填 reviewer、reviewedAt。若發布規格要求人類教師，需有實際符合資格之教師簽核；稽核AI事後複核不能代替。不要破壞五題，僅在證據確實不合規且存在學生風險時啟動受控處置，不要靠批次清除approval解決。

P1-02：修改 scripts/check_live_release.py inspect_live (約27–76) 與 tests/test_check_live_release.py（如尚無測試則新增），加入完整 expected-release manifest 以原QA source SHA、approved canonical IDs、每題正式答案、教學 canonical digest、單題WebP SHA與所有shared SHA綁定。遍歷所有 approved 及 preview，不再只 reviewed[:2]、sharedImages[:1]。合成負測：相同題數但第5題答案被竄改、第三預覽圖錯SHA、同題第二共享圖破損、錯sourceRevision、過期teaching digest都必FAIL。保留 release.json same-SHA，避免不必要重複deploy；變更後 CI 成功且新版本 Pages verify/build/deploy/verify_live真的完成才算新增發布鏈充分。

P1-03 ECON34：只在隔離分支處理 115-09-2-34。保留 WebP SHA 5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02，事前盲解原始Commit 33aa3228077d9cd7ad4ec2f59890d46013b976f7、轉錄最初漏「中」字歷史、既有 teaching 候選 SHA 4b1f87a47b6ba2bfc74c58b0a7ffd273a44cde62da71aeaf633f7fedf78adb54。參看本稽核實質post-key複核 ECON34_INDEPENDENT_POST_KEY_CONTENT_REVIEW_20261024.md，四選項判定A、B、C、D，概念題計算框必隱藏；它是第二AI審查文字材料，**不是人類核准證書**。需獲得實際合規不同 reviewer 的審查事件與身份、原圖/課綱/公告/雙層教學內容批註，保存 reviewer角色、reviewedAt、reviewEvidence SHA、questionRevision、WebP SHA、teaching SHA。原始官方09-2確認PDF應下載按SHA b0a3f02ce083442ce67f48eb7355aa245d43199bc86677862c0861e0e8027133並逐頁核對Q06/Q28/Q44；34未列名，不能以全卷無疑義放行。更新 sudu/data/processed/115/review-evidence/115-09-2-34-{ocr,official,blind,teaching,ui}.json 及 verified-student-batch.json 時必有真實review授權，不要直接寫STUDENT_QA_APPROVED冒充。重新計算證據/文字revision/content SHA，執行正式source原發布器 stage/check 的正負測、對比核准五題全部內容不變，再執行同一真實題目+教學digest之8尺寸×2主題、深淺、hover/touch、答題錯題、概念框隱藏、響應式。只有QA full admissible時由既有 hourly sync 自動接入 main + Pages 同SHA verify/build/deploy/verify_live；正式新題只有Q34。任一Gate未合格維持BLOCKED，不部署，不重複觸發Pages。

P1-04 MB20-25：沿用隔離候選 0b1343fb7853701ec847fd33321cc792c3172bbf，官方第7、8頁像素、六張既有WebP與其原SHA，不重裁無錯圖。逐題完成：20 75°/60°正弦+√3+完整圖四，21 60°港口AB=7 AC=8 >4限制及圖五，22 五張 ū/bô 卡、至少一張有、選項31及去頁尾，23 保留表二全部「行程I每位x/其中一人減3000」「行程II每位x+2000/其中一人8折」、24 A=110/r及B=log10(3)/log10(1+r/100)上取整，25距離√2、x²−8x+(y−7)²=a。修改 QA 分支 sudu/data/processed/115/questions.json、question-bank.sqlite3 前必重新檢查最新提交、複核六題原圖與 candidate JSON，保存修正前後diff。MB23的 originalSourceTableCandidate 必被正式publisher/public_question與V4完整取得，不能因 question短文字丟失完整表格。隔離雙次SQLite import 205筆、199筆其餘不變、WebP SHA不變。每題重新計算 text_revision(question/options/WEBP SHA)，重做新版本的獨立解題、雙層教學、證據文件和V4 8×2，不得繼承舊revision審核。六題未通過前不得STUDENT_QA_APPROVED、不得上線。

P1-05 114 年：main publisher official_notice_scope_certified()對114一律拒絕，既有開放 PR #22（release/114-year-scoped-official-gate-20261024）與 PR #21 114英文07/08/09候選、PR19公告、PR20草稿盲解，須先讀各自最新提交與CI，不准重複另造規則。專用114公告四文及yearScoped SHA、缺頁/跨年/重複/錯更正ID的負向測試；確保115年原5題資料及驗證全部不退步；原source QA與publisher需同一可驗證version。只有正式PR經審查並依授權正常非force合併且同SHA Pages LIVE成功，才算114題新增。

P1-06 固定123題候選：採同分支 sudu/release-audit/independent-20261024/128_QUESTION_RELEASE_GAP_MATRIX.json 逐題檢查，不可把候選officialAnswer視為最終官方G3。G0原卷QID和修訂，G1只本題原始像素，G2圖/公式/表格/OCR文字，G3真正最終官答+公告，G4先於官答的獨立解題留痕，G5教師/國小四選項與重點+真正審查者，G6有計算完整步驟、概念題隱藏，G7依科目教材/英文IPA時事真實URL/學年度，G8實際V4 8尺寸×2主題真實Chromium/手機，G9所有SHA簽章與版次，G10正式publisher/main/Pages/LIVE同SHA。缺一不可。禁止批改128題PASS/READY、刪歷史警示。

次批優先候選（**排序不是核准**）：
1. 115-09-2-34：已具原圖事前解題、完整概念雙層教材、8×2隔離測試，缺真正不同reviewer及新版憑證、正式來源/Live；
2. 115-00-MB-06：草稿已有先圖後答推導、算式與A-D核對，需正式source、獨立教學審核、16種V4、憑證；
3. 115-00-MB-07；
4. 115-00-MB-08；
5. 115-00-MB-10；
6. 115-00-MB-11；
7. 115-00-MB-12；
8. 115-00-MB-13；
9. 115-00-MB-14；
10. 115-00-E-03：已具字義/選項/IPA/時事教學事後核對，仍待source、完整不同審查者與V4。
對第3至9題先核實本題確實有圖/答案/解題，排序屬歷史候選資料的優先近似，不是已逐題讀完整內容後計算的精確工時。另並行处理MB20-25六題來源校正，不直接納入 READY 第一梯隊。

P2必留警語：115-09-1-07 特別股財務槓桿與官方B衝突、115-09-1-33雜湊/數簽非等於加解密官方A、115-09-2-28官方A且原圖並無250元總預算（保留AI初解D）、會計06/12/15與國文18歷史警示、英文E03/28來源詞性/新聞。每題以官方原圖、原答案歷史、課綱教材與審查紀錄個別裁定；不得改最初錯答歷史或為解除blocked刪警示。

每批執行 scripts/audit_preview_128_teaching_candidates.py、scripts/audit_preview_128_release_readiness.py、scripts/audit_preview_teaching_drafts.py、scripts/sudu_verified_publish.py stage/check、python -m unittest discover -s tests -p 'test_sudu_verified_publish.py' -v、node --check sudu/verified-questions-runtime.js、對應 Playwright 真正16種 UI；另 QA來源205 SQLite 隔離雙次匯入與正確性，針對最新SHA跑 main 正式 Pages verify/build/deploy/verify_live。任何失敗應保留日誌run URL，**不可關Gate／刪assert／改 approval 欄位**。

每批回報：本次ID、前後文字diff/舊證據留存、原頁及WebP SHA、盲解紀錄與官方公告、reviewer身份角色與獨立證據文件SHA、teacher/elementary/A-D/計算驗證、實際UI16結果、新textRevision/teaching digest、SQLite205/199回歸、非force commit、workflow run、main SHA、LIVE verified URL、原五題回歸不變。符合全部才新增單題核准。失敗維持BLOCKED隔離。

END ORIGINAL_SESSION_FIX_DIRECTIVES
