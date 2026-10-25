# 7581707 / Role C：115 國文第11、12、13、16、17題逐題雙層教學候選

## 最新使用者政策與工作租約（2026-10-25）
- Issue36 最新頂部政策：https://github.com/homelux-huang/7581707/issues/36 。**「高職老師」是教學角度，不需真人教師資格、授權名錄、簽章或真人 GitHub APPROVED。**依此保留高職老師角度＋國小口語的 A～D 四選項教學、粗體與 `highlights`，不捏造教師身分、盲解或審查。
- AI 教學作者為 GPT-6 Role C；**獨立 AI 複核仍必須由不同作者（角色 E）**，核實每題原圖、文字、選項、官答／更正公告及逐項理據，留下實際具名與 SHA 綁定審查筆記；不可讓作者自己標 QA PASS。
- TaskId `C-115-C11-13-C16-17-DUAL-LEVEL-20261025-05`。認領 GitHub 事件 https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393860961，server `created_at=2026-10-25T05:20:54Z`。新獨立分支 `teaching/115-role-c-chinese11-13-16-17-20261025`，baseSHA `3c13c12f8dbaf92f23f9fbb58cde3916f9e6b088`（上一輪 Role C PR51 的成功 CI HEAD）。
- 原始 source PR35 固定 HEAD `e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5`。115 題庫 questions.json Git blob `216bc43d57501bc1c3e5842b48413a8967456cda`，單題 webp-manifest.json blob `2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b`。唯一協作台帳 PR30 blob `3e2f07f8b9e1c6cd64ec18d50d27b868a1c5cfb6`。五題在認領時 `teachingDraft=NOT_DELIVERED`，未被他人認領。
- **新增教學僅是作者候選**；本批沒有更動官方 PDF、原圖 WebP、OCR、SQLite、校正公告、PR30 協作台帳、發布器、其他角色資料、main 或 GitHub Pages。五題原題答案讀入後才撰寫說明，**不是盲解**，沒有自行設定 `questionVerified`、`answerVerified` 或 `studentReleaseApproved`。

## 五題教學摘要與固定原始來源
| 題號 | 題意／選項答案候選 | sourceTextRevision | 單題 WebP SHA256 | 教學 SHA256 |
|---|---|---|---|---|
| 115-00-C-11 | 甲乙子女送終，D | `8802bc8fa44af457c25fcca5a784aec60b0c05bfa9969cac4eca9d431cabee71` | `101bcdaf6b77f421fa0a20a2220a0e592e7fdd6a28595f0b58ec46eda4c767ce` | `7c4c6600c300897153ad0d320af214889c83db27b7cb9885cf08612a27d5e0fc` |
| 115-00-C-12 | 甲返家後與乙返家途中，C | `c4e6891c02cd68e3b0af38b178cbd96a9453b057fc88092398fd03af9bc3fa92` | `ac9b20198dea3530262fa9c35b2ecd46e17d1ef8a05a705d2c4255a243dc7f5e` | `2e919b259b8fe386f707547c8ef2217c5a00027137bb81f2699b8e6b5efe414a` |
| 115-00-C-13 | ①～④原句、無奈與反諷，D | `5261e86bcd01822edc85c38b4df86be4f1477fa885310d8be37abec183e65225` | `575c1ecd856e31d4c861f675225ecc553c2c4d4060ba7534a8eaa24fa0eba82f` | `7f8f4be3a52e0906c68438b65e882a6998f76af11632ac98f2a67d143be0b107` |
| 115-00-C-16 | 探春自我認識與負責任管家，A | `f0e790fbeb37aef0ba1a9ffbfb5dc40c9cdaad4a29ed1820b8d671973cf1dcd4` | `cc874e5f44e18ff05e7bb121e346eb4d1430a42dd8b061ad97b27f8339d5bff8` | `c34f1e8ad5313ae6da22921578c3b3b12cf7006c66ee3e6d3368b9a99f1527e1` |
| 115-00-C-17 | 趙姨娘借例外恩賞要求破例，C | `9ad6510639e7506f7d35ebc7ec01b68ddb6bbeb3eff8bc1c01201aa41190896a` | `074a9f792c7b011f59606394ea2c521c2190143bce9d013fdf79b8703dbdad8a` | `f9e7683ba1e5f3d7eb4fb1506a1b20a37f45963b0037d0424f4f94e784261919` |

同時每個候選 JSON 保存完整官方題幹、A～D、每選項獨立的高職／國小解說、原文引句提示 `sourceEvidence`、逐題學習步驟、初／中／高字詞、重點 `**粗體**` 與 `highlights` 及可核對的源原文 `sharedMaterial.sourceText`。無計算的國文題 `hasExamCalculation=false`、`examCalculation=null`，供 D 的 V4 自動隱藏計算區塊。

## 非常重要的共用原圖 QA 限制
- **甲乙閱讀原文** `115-00-C-SHARED-11-15`：原始共用 WebP `bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66`；全文文字＋此圖片的 `sharedMaterialRevision=9d0735b8c397d8a9c384410e13eb5b83e60b32becd5022cc5f6c69092c08d18f`。**共用原圖狀態 `PENDING_INDIVIDUAL_VISUAL_QA`，不是 PASS**。影響第11、12、13題。
- **紅樓夢中人閱讀原文** `115-00-C-SHARED-16-18`：原始共用 WebP `708a7236cdf91753bb86f385603922090105ace1a9f792c13b40869fd3686d45`；文字＋圖片 `sharedMaterialRevision=f23678717fa4b5ffb6be1226d2f7d800adcf5b6cd7e825de3d3058cac793678d`。共用原圖同樣 **PENDING**，影響第16、17題。
- 個別單題 WebP 在既有 manifest 是**歷史候選 QA PASS**，並不等同 A／E 完成官方整頁像素、文字層／圖像及共享原圖獨立 QA。Role C 本輪只讀來源資料，**沒有實際獨立打開／重新雜湊 WebP 二進位與官方答案 PDF**；「原圖 SHA」是原 manifest 存在的數值。全數 `sourceQuestionVerified=false`；第11～13題雖歷史 `answerVerified=true`，仍不能據此視為整題可發布；第16～17題歷史 `answerVerified=false`，官答更正公告必須由 A 直接驗證。
- Q11～13 `assets.visualQa` 仍有 PENDING，雖 manifest PASS；差異留交 A 調和，**不得批次設 PASS**。
- Q13 正文①②③④與選項/語境必須由 A 對原始像素逐行核實；只能暫採現存官方文本候選，不自行重畫或臆造原文。
- 社會情緒學習探春第16題，表述『想有所表現』為從「皆因夫人看重」「尚未做出一樁半件」推論，**不是原文逐字直述**，獨立 AI 審查時要確認推論強弱。

## 角色分工與結案標準
1. **A SOURCE**：原始 WebP／共用材料像素單題 QA，官方題/四選項、最終答案/更正公告版本及文字層核實，必要時建立有來源 SHA 的校正 PR，不覆寫本作者原文。若文字或素材修改，五題 sourceRevision 或 sharedMaterialRevision 必須重新計算並使舊教學/UI憑證失效。
2. **E distinct AI**：不同作者逐項實質核對五題 A～D，特別是第13題畫線語境、第16題推論；登錄真實身分／session、官方證據 SHA、題號、當前原圖/來源/教學 SHA、充分審查筆記。不准作者 C 自批／假裝人工教師。現行 MASTER PR46 只是獨立 AI 契約草稿，正式發佈器採用要主指揮另行驗證。
3. **D UI**：沿用已有 35 題 Demo 國文 V4 樣式，驗證相同 `sourceTextRevision`、`teachingCanonicalSha256` 與單題／共用圖片 SHA 的實際畫面／互動，8 viewport×2 theme，文字與選項分隔、正確解說、重點 highlight、無計算自隱、無多題整頁 WebP。
4. **唯一 MASTER**：獨立收件、官方/內容/UI/CI 逐題 QA 過才可增量發布 main/Pages，驗證部署同 SHA LIVE。此批 **新增 READY=0、LIVE=0**；不得合併或部署本作者 draft 直接生效。

## CI 與完整性
`batch.json` 精確記錄每題完整 JSON SHA256、問題文字 revision、單題 WebP SHA256、兩組共享圖片+文字 revision 與教學 canonical SHA256；`tests/test_115_role_c_chinese_11_13_16_17.py` 對來源、教學、中文各選項雙層理由、節點及共用圖片 QA PENDING 做 fail-closed/資料改動負測。只在本 C 作者分支的新 workflow 跑 read-only CI；即使 tests SUCCESS 也只證明作者候選一致性，**絕非 E 內容QA、A 官方來源、D 瀏覽器證據、MASTER 合格 READY 或 LIVE**。
