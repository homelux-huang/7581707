# 2026-10-23｜新增英文28題詞彙/新聞來源自動驗收（僅草稿）
- 起始HEAD：`0289283219c14553142112495188d921d8853dc4`。
- 強化既有 `scripts/audit_preview_128_release_readiness.py` 唯讀稽核：28題英文必須有IPA、整句中文翻譯、A-D中文意思、初中高同義／反義詞欄位、英文自編例句與中文翻譯且highlight確實出現。
- 有`newsExampleSourceUrl`的題目才可帶來源型新聞句，必須有HTTPS URL、來源日期與標題、中英文例句、實際含highlight字、明示`PARAPHRASE`不是新聞原文引述。
- 沒有URL卻宣稱`SOURCE_VERIFIED`即 CI FAIL；實際擁有source URL的題號集合及個數必須等於`progress.partialEnglishNewsSourceLedger`紀錄。本輪 **9/28** 有來源、19題仍無。
- 靜態程式**不驗證外站內容持續存在或真假**，外部來源已人工查對、網址與日期保存；未查的19題不會因有自編例句就冒稱新聞。全部128題`independentTeachingReview`與`uiReview`尚為PENDING，正式發布核准0。
- 不增改官方答案、不改原圖、學生紀錄與main，GitHub Actions僅在草稿分支跑read-only。
