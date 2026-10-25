## 2026-10-25 使用者新政策優先覆蓋｜真人教師不再是門檻

依 Issue36 使用者修正，本批五題逐題均不再將真人教師資格、授權名錄、Ed25519教師簽章、真人GitHub APPROVED作為發布前置條件。仍須來源官方答案與更正公告、A-D雙層解說、不同作者角色 E AI 內容與證據複核、相同教學digest V4 8×2、主指揮正式 CI／LIVE 實測。新增 `review.independentAiContentReview.status=PENDING_DISTINCT_ROLE_E_SUBSTANTIVE_REVIEW` 且所有審查證據為null，不假造 E 已完成複核。舊欄位 `humanTeacherVerified=false` 為**非阻塞**的歷史相容資料；發布器政策遷移由 MASTER 處理，PR46為尚未啟用之 Draft 審查契約。

本批五題所有教學文字、選項、來源修訂、原 WebP SHA、teachingCanonicalSha256與composedTeachingSha256**完全不變**；僅 review metadata、手冊與檔案hash調整，仍 `BLOCKED`、READY=0、LIVE=0。Claim: https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393706001 。

# 114 Role B Loop Batch02 — NO RELEASE

- taskId: `B-114-NEXT5-E11-E14-C04-20261025-02`；Issue36 [CLAIM](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393618501)；伺服器 created_at `2026-10-25T04:51:07Z`。
- 角色 B 分支 `teaching/114-role-b-loop-batch02-20261025` 從上批 B HEAD `852c6613161f39314d87476b4e201cfe1811f783` 衍生；來源 PR21 SHA `9944759e339ef2d3c002042798f7fe696d861d96`。不重做 OCR、裁圖、SQLite、舊7題教學，也不改 main／發布器／UI。
- 五題：英文11–14、國文04。原來源題幹／選項與既有 WebP manifest PASS 一致；只是沿用影像QA，不代表本批對原圖重新目視。官方最終答案僅候選，個別答案影像QA、確認公告與不同作者角色 E AI 實質複核仍待核；原答案已知，沒有冒稱盲解。
- 教學資料：教師與國小雙層解說、四選項不同具體理由、逐題思考步驟、一眼記住、原題安全 highlight。英文另有IPA、初中級詞、同反義、語境限制以及2025–26可查報導背景中英**自編**例句（CDC、歐盟執委會、中央社、TVBS）；非新聞原句。國文04警告假檢警「國家安全帳戶」非合法匯款程序，並加入初／中／高詞彙。
- 不需運算的題 `hasExamCalculation=false,examCalculation=null`，禁止占位文字。教材版本、章節、頁碼未知欄位維持null。
- canonical source revision = SHA256(sorted `{question,options,singleQuestionWebpSha256}`)；teaching digest = SHA256(sorted `{questionId,sourceRevision,webpSha256,teaching,enrichment}`)；batch.json逐題存原sourceRevision、圖片SHA、teaching與文件SHA，來源改動須重算。
- 唯一逐題台帳在 PR30；本支不建立平行台帳。角色D仍需針對最新教學digest做真V4 8尺寸×2主題，角色 E 需執行可核對來源與教學SHA的不同作者 AI 實質複核，無真人教師授權或簽章前置要求。
- CI run: `python -m unittest discover -s tests -p 'test_114_role_b_batch02_20261025.py' -v`（來源、SHA、四選項、語境、負測和禁止發布）。即使成功也**不代表 READY**。new READY=0, new LIVE=0。
- 來源污染（英文10/15、國文06/07等）先隔離交A修復，避免拿頁首／表格誤OCR製作教學。
