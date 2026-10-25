# 7581707 Role B｜114 國文 Batch04（5題）— Draft / NO RELEASE

## 來源及任務
- taskId `B-114-C08-C11-14-20261025-05`，Issue36 [CLAIM](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393867768)，GitHub server claimedAt `2026-10-25T05:21:47Z`。branch `teaching/114-role-b-loop-batch04-20261025` based on `641fc7d108dd02578cd3c24a995b3ad8111d0d34`（Role B PR52；不修改 main）。
- 僅新建 `114-00-C-08`、`114-00-C-11/12/13/14` 五題教學、批次SHA、唯讀 CI 與本交接，不變更任何既有B1/B2/B3教材、原OCR、原WebP、裁圖、SQLite、UI、publisher 或其他角色租約。
- 官方原試題資料沿用 PR21 `9944759e339ef2d3c002042798f7fe696d861d96` 的 `questions.json` Git Blob `074bff8cbb9ca7bbc0aefd8580454892d21f7d6b`、`webp-manifest.json` Git Blob `249a41d5a64558ccaa3084b21f915922a55c6a1b`。五題均有全部四選項、問題及選項清晰、來源零issue、manifest QA PASS；**manifest PASS不是本次新通過官方答案驗證**。
- C11–14 除題號專屬單題 WebP，**作者只讀查看未修改之原始原卷第四／第五頁 WebP**：p004 Git Blob `84980ba031aa5d9da12402f3bb0b11b3e558d753`、p005 Git Blob `381f2df6bb4b8e35691db229d611bb4681f1bd5c`。甲文賴和〈一桿秤仔〉、乙文改寫自賴和〈不如意的過年〉；讀頁只為取回文章語境，**沒有OCR再生成、裁切或修改原圖**。原頁第五頁 SHA256 `6925c630949ad1e62a01924b274c5efcecc92bee1a1309aab4267e04c26a91f7`，既有四題單圖QA檔 Git Blob `6e43a9d11eba03a76f16192983c2e3920cc82524`，獨立QA通過與教材審查未在本批新增。
- C08 街頭巷尾／互別苗頭；C11 查大人立官威而帶孩童問話；C12 民眾同情反使孩童更不幸；C13 甲外在言行與乙內心；C14 諷刺Ⅰ②／Ⅱ①③。官方候選答案 **事先已知**：B/D/D/B/A，絕不冒稱先解後看答案的盲解。

## 教學契約、政策與阻塞
- 每題有高職老師**教學角度**的正解推理、國小生口語白話、A～D四個獨特 teacher/elementary/reason/isCorrect、逐步解題及「一眼記住」。中文詞彙初／中／高分級；highlight僅標記真正出現於官方題幹或選項的原文字形，輸出原始文字與 safe bold/highlight boolean，不放任意HTML。
- 不需計算題 `hasExamCalculation=false`, `examCalculation=null`，沒有「本題無金額計算」占位。教材出版社／版本／章節／頁碼不知維持null、待核，不捏造來源。
- SHA：sourceRevision = sha256(canonical sorted JSON `{question,options,singleQuestionWebpSha256}`)；teachingCanonicalSha256=sha256(canonical teaching)；composedTeachingSha256=sha256(canonical `{questionId,sourceRevision,webpSha256,teaching,enrichment}`)；整檔fileSha256記錄於 `batch.json`。每題也保存原圖／原頁 Git Blob／官方PDF已知來源SHA。
- Issue36使用者最新要求**取消真人教師、資格、Ed25519簽章或真人GitHub APPROVED作為教學必要門檻**；但 E 必須是不同作者的 AI 實質內容及每選項查核、真實審查筆記+trusted証據，A 的官方最終答案與更正公告仍須核，D 必須對同SHA跑35題Demo七科V4原操作8×2，MASTER改好尚未上線的publisher AI reviewer gate，才能由主指揮正式增量發布。
- 本批全部 `BLOCKED`，reviewerSessionId/taskId/Issue comment/notesSHA 為null；作者B自評不能充當E複核、未知不能設PASS。新 READY=0、新LIVE=0，沒有修改正式main或部署。

## 測試
`python -m unittest discover -s tests -p 'test_114_role_b_batch04_20261025.py' -v`。測試每題 real WebP bytes SHA、來源原文章兩頁 Git Blob、歷史單圖 QA 實體證據、text revision、teaching digest、全部四選項與非計算區塊、highlight字形安全、否定冒稱E/人工/官答批准及禁止發布；**測試通過只代表作者候選格式與依據一致，不構成發布證書**。
