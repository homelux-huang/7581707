# 128 題雙台帳與 MB05 同 SHA 正式 LIVE 審核

本次專用唯讀證據分支從正式 `main` SHA `57d766e841235b937babf3fe10a8ff44606c7c41` 派生，不修改原題庫、不授予任何 QA PASS/READY，亦不重新發布。腳本 `scripts/audit_128_release_lineage_20261024.py` 對固定 `progress.json.items` 128 題建立逐題欄位：

`questionId | draftTeachingDigest | sourceQuestionRevision | sourceTeachingDigest | sourceCertificatePathsAndSha | approvedContentDigest | uiTestedDigest | mainCommit | pagesRun | liveVerifiedAt`。

另直接驗證：
1. MB05 事前第一次盲解原檔 Git blob 仍與原 Commit `cf6a4efe` 相同，該 commit 是來源核准 commit `b78a14c8` 祖先。
2. 原圖 WebP、canonical source revision、原 QA 文件、SQLite payload 和五個完整來源 admission 都必須相符。
3. MB05 所見教學 digest 綁定 CI #40085323981，正式 V4 HTML/runtime bytes 與接受測試時的原版本 `2b48a4a` 完全相同。
4. 原四題學生公開物件必須與原正式部署前 4 題完全一致。
5. 從 GitHub Pages 直接取回 `release.json`、正式 `115.json`、MB05 WebP 與 runtime（附 cache bust），必須逐個和正式 `main` 比對一致；Pages #40097988371 必須 SUCCESS 且 head_sha 精確一致。
6. 如非完成**真正不同審查者**的教學複核，即使來源曾經以 AI 複核發布，`sourceIndependentHumanTeacherCertified=false` 不可強行寫成 true。原本 5 題只核歷史狀態，新的題目不得拿它來冒充人類獨立認證。

此報告保留草稿 128 題的 `fullyAccepted=0` 與正式來源 5 題兩種事實，不可批次填入相同完成率。若任何真實 LIVE 或內容 SHA 不符，CI 必須 FAILURE 並保留阻塞。
