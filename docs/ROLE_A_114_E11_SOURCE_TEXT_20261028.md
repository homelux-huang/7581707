# ROLE A｜114 英文第 11 題｜正式原頁文字與單題原像素 QA 收件（2026-10-28）

**Issue #36 TASK** `A-114-E11-SOURCE-QUESTION-FINAL-20261027-01` · CLAIM #6458226202 · ROLE A 原卷／OCR／WebP 資料來源審查，非 Role B 教學作者、Role E 不同作者教材 QA、Role D 同版 UI 操作審查，非唯一 MASTER 發布者。最新使用者取消真人教師身分／資格／簽章要求，但保留實質獨立 AI 內容複核。

本批承接既有原始來源 PR50、官方答案與更正範圍 PR94 HEAD `a6da19064b0603da498c015300504095bfc4ca61`；獨立分支 `qa/role-a-114-e11-final-source-text-20261028`、**Draft PR stacked on PR94**，不更動 `main`、既有來源資料、205-row SQLite、114/115 唯一 PR30 台帳、Role B/C/E/D 分支、受保護發布政策或 Pages。

## 原始來源與直接目視結果

**精確 canonical ID `114-00-E-11`。** 114 年國文之外的英文共同科目，正式題本 `4-00-E`，頁次 3，段落 II「對話題第 11 至 20 題」。已實際打開本分支保存的官方原始第3頁、原單題 WebP 和原官方答案 p1 三張影像，逐行核對：

- 題幹五段 Dad/Son 對話，爸爸先提醒沉迷手機、兒子說看影片玩遊戲、爸爸提醒傷眼、兒子留空格、爸爸接著說 **“Yeah, let’s go jogging. It’s more fun.”**。所有英文標點、撇號（you’re／let’s）、問句與底線原樣保留，源 JSON 沒有重寫。
- 原 A：「Then I should use it less.」；原 B：「Should I use a new phone?」；原 C：「Do you like to watch videos, too?」；原 D：「So you should play online games.」。**四選項都完整、與 archived 114 原始 JSON 及 PR94 canonical JSON 完全相同**，沒有數學運算、圖表或另需共用文章。
- 真實原始 p3 WebP `sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp` GitBlob SHA1 `5ff21a726938e64e0b7efe3bb8abda65e55e1d4f`、SHA256 `51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb`。
- 已歷史 PASS 且完全不重做的單題 WebP `sudu/data/processed/114/webp-v1/00-E/114-00-E-11.webp`，GitBlob SHA1 `50f8fde174f4f0e66dc0f2315c11c5a73cec6b7a`，SHA256 `ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0`，裁切原頁像素 `[90,275,1310,591]`、1220×316。完整 Q11 及四選項、不含 Q12、未顯示整張試卷、沒有頁首頁尾。CI 真實 Pillow 解碼，對應原頁逐個 RGB 像素一致；未使用 AI 重畫、重新 OCR、重新裁圖。
- 原始題本 PDF **歷史記錄 SHA256** `1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf`；本次只重讀官方來源**已儲存的 PDF 派生像素檔**及其 Git SHA，不重新下載 PDF 實體／重新計算 PDF bytes，不可宣稱已完成完整 PDF 法定來源核准。
- 獨立來源 `text_revision`（實際 `scripts/sudu_verified_publish.py::text_revision`，僅包含題幹、四選項與原單題 WebP SHA，無答案洩漏）：`646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036`。變更字詞/選項或 WebP SHA 必導致 revision 改變。

新增**誠實的 Role A 來源像素與文字審查憑證** `sudu/data/processed/114/review-evidence/114-00-E-11-source-text-20261028.json`（新檔，原本的 QA 結果和 source bank 不變）。審查方法為本對話 ChatGPT Role A **直接閱讀**保存的原始官方像素與單題圖，並非獨立 Role E 教學審核，更不是人工教師認證。新收件狀態 `PASS_ROLE_A_DIRECT_ARCHIVED_SOURCE_PIXEL_AND_TEXT_MATCH_ONLY`，不會因新檔自動把 `questionVerified` 設成 true。

## 官方答案沿用（不重做）

PR94 在先前獨立官方答案 QA 中對 114 00-E 第 11 題讀取原公布答案表右第二對題號 **11=A**（原答案頁 SHA256 `a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863`、Git SHA1 `5f2920313607af4e756095cd3d6098c8a3ab7440`），且正式英文更正確認文件已由既有來源全頁核對，**僅列第 26 題，並未列第 11 題**。確認 PDF SHA256 歷史記錄 `79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc`。這是**個別題號未列入更正**，絕不改寫成該科整份卷「無異議」或重新批次核准。本批沿用 PR94 `answerVerified=true` 的 E11 A 原答案證據，不重新檢查或改寫該值；來源 `questionVerified=false` 保持。

原已存在的 B 作者候選 [Draft PR #44](https://github.com/homelux-huang/7581707/pull/44) Git HEAD `e0d4532c751127204e73af9cd9d3a95c52449131`，其 E11 authored `composedTeachingDigest=3d250e8ecd621eda0f14f1839e6cf89b70b3649a1af0298611fedd9bbf57ceee` 綁同 `text_revision`。**教學候選本批未修改且未執行 Role E 最終可信內容複核、也尚未有正式發布器產生的 8×2 UIQA 同版憑證**；先前 QA-only 模擬不能冒充正式發佈。

## 實際測試契約

`tests/test_role_a_114_e11_final_source_text_receipt.py` 逐項驗證：

1. 原始全頁、單題、答案 WebP 真實 RIFF/Pillow 解碼，SHA256 與 Git blob SHA1，原像素裁切全 RGB 一致。
2. 正式 114 00-E p3 第 11 題完整原文與全部 A～D **精確**等於 `main:sudu/data/years/114.json` 與本分支 `questions.json`，共用材料空、四選項有意義。
3. 舊版 `QA_114_EN_Q06_Q20_SHA_BOUND_DIRECT_VISUAL_20261023.json` 確實對同圖 SHA 記 AI 原圖 PASS、絕非真人或 Role E 教材核准。
4. 原 PR94 官答 A 憑證及更正 PDF **僅 E26** 正向／SHA 篡改負向；官方答案原圖不因本 source-only QA 重核。
5. **205 筆**原生 114 SQLite 既有**七欄** schema、`PRAGMA integrity_check=ok`、每列完整 canonical JSON payload 和 `payload_sha256` 與 source questions.json 一致；只讀，不更新任何 row。
6. 原有 source JSON、manifest、114 year raw、原圖 QA、官答 evidence、原 SQLite 的 GitBlob SHA **完全不變**。
7. 篡改選項／題幹／圖像 SHA 的 `text_revision` 不可錯誤沿用，且審查不自行標 E 教學、D UI、main/READY/LIVE。

另外執行**原 PR94 已驗證的 8 項官方 A11/A13/A14＋205 SQL 不變性 regression**，本批新 9 項 + 原 8 項由新 Workflow CI 重新於**相同 HEAD** 實際測試。工作流 `.github/workflows/role-a-114-e11-final-source-text.yml` **只有 contents:read**，沒有 secrets、更新、部署及 main push；即使舊受保護主分支更新，也不能把本來源憑證當成已提交正式 MAIN。

### MASTER 下一步

此單題可提供 Role B 依**相同原題號、WebP SHA、text revision**維持既有 A～D 教學候選，**不是對新題來源完全發布核准**。MASTER 需另行審核 source questionVerified admission 與官方原卷 PDF 位元組記錄、不同作者 Role E 對 PR44 原教學/IPA/選項完整內容的可信憑證、正式 publisher 投影並綁原圖/教學 digest 的 D 8×2 實測、正常受保護 main CI 及同 commit Pages LIVE。

**本批新增 READY=0、MAIN 學生題=0、LIVE 學生題=0；不得省略 Role E/D gates 或捏造真人教師簽章。**
