# 114 Role B Loop Batch02 — NO RELEASE

- taskId: `B-114-NEXT5-E11-E14-C04-20261025-02`；Issue36 [CLAIM](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393618501)；伺服器 created_at `2026-10-25T04:51:07Z`。
- 角色 B 分支 `teaching/114-role-b-loop-batch02-20261025` 從上批 B HEAD `852c6613161f39314d87476b4e201cfe1811f783` 衍生；來源 PR21 SHA `9944759e339ef2d3c002042798f7fe696d861d96`。不重做 OCR、裁圖、SQLite、舊7題教學，也不改 main／發布器／UI。
- 五題：英文11–14、國文04。原來源題幹／選項與既有 WebP manifest PASS 一致；只是沿用影像QA，不代表本批對原圖重新目視。官方最終答案僅候選，個別答案影像QA、確認公告與獨立教師簽核仍待核；原答案已知，沒有冒稱盲解。
- 教學資料：教師與國小雙層解說、四選項不同具體理由、逐題思考步驟、一眼記住、原題安全 highlight。英文另有IPA、初中級詞、同反義、語境限制以及2025–26可查報導背景中英**自編**例句（CDC、歐盟執委會、中央社、TVBS）；非新聞原句。國文04警告假檢警「國家安全帳戶」非合法匯款程序，並加入初／中／高詞彙。
- 不需運算的題 `hasExamCalculation=false,examCalculation=null`，禁止占位文字。教材版本、章節、頁碼未知欄位維持null。
- canonical source revision = SHA256(sorted `{question,options,singleQuestionWebpSha256}`)；teaching digest = SHA256(sorted `{questionId,sourceRevision,webpSha256,teaching,enrichment}`)；batch.json逐題存原sourceRevision、圖片SHA、teaching與文件SHA，來源改動須重算。
- 唯一逐題台帳在 PR30；本支不建立平行台帳。角色D仍需針對最新教學digest做真V4 8尺寸×2主題，角色E及授權不同作者教師仍需審查/有效簽章。
- CI run: `python -m unittest discover -s tests -p 'test_114_role_b_batch02_20261025.py' -v`（來源、SHA、四選項、語境、負測和禁止發布）。即使成功也**不代表 READY**。new READY=0, new LIVE=0。
- 來源污染（英文10/15、國文06/07等）先隔離交A修復，避免拿頁首／表格誤OCR製作教學。
