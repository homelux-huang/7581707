# ROLE A｜113 年國文 11～15 題｜原始共用閱讀、比較表、詩與梅花宴圖像／候選 SQLite

**Task：** `A-113-C11-15-SHARED-READING-20261025-13` · [Issue #36](https://github.com/homelux-huang/7581707/issues/36) Claim #6394517446 · ROLE A 官方資料來源。精確分支 `data/role-a-113-c11-15-shared-20261025`，從已驗證 [Draft PR #77](https://github.com/homelux-huang/7581707/pull/77) 的 HEAD `1a4d0e7489256e01bd997fff399befdbb45f3697` 新建。本批沒有修改任何原始官方試卷／歷年 JSON、113 年已驗證第 1～10 題 WebP／SQLite、114/115 共同台帳、其他 Session 分支、main 或 Pages。

## 官方原始檔與多頁素材

- 題本 113 年 00-C（共同科目國文）第 4 頁原始 WebP：`sudu/data/original/113/00-C/p004-67c0d477e9-v2-w1400-q66.webp`，原 Git blob SHA1 **`789a0cfb16e7871e2fb38c1089e14face508a8ed`**，實體 WebP SHA256 **`964ada897c9d1a93fd81d21fa6a4d02e94cb91999e173906afe84b77a824ded7`**，1400×1981。
- 第 5 頁原始 WebP：`sudu/data/original/113/00-C/p005-67c0d477e9-v2-w1400-q66.webp`，Git blob **`be92fa73cef1622f9ea8990195779b0e41699caa`**，實體 SHA256 **`9f6f2e3be9f2f92eb0a647d95a38a5237890026998b51f76afb18cdf1debbadb`**，1400×1981。
- 官方公布答案影像第 1 頁：`sudu/data/original/113/00-C-answers/p001-9a6ce177b0-v2-w1400-q66.webp`，Git blob **`938f88435a9b21e257f11dfcfda71655e8a7a0c6`**，實體 SHA256 **`a3c8154f5186c925a9408e4c4b50cd9a0c2b92db2fe3375d3d13d8491b9c7bc3`**。
- 題本 PDF SHA256 `67c0d477e99d07cd59af0e9c75b261692c3089fd5559185f41945de32316093f`、答案 PDF SHA256 `9a6ce177b0aec3f22957635cc9abc21539cf3356471b2e3dec65e550e8f9559a` 是先前已保存於 113 原年度資料的**歷史記錄**，本批 **未重新下載原始 PDF 或驗算 PDF 檔案**。113 年正式更正／答案最終確認公告逐題範圍仍待核對；第 11～15 題官方答案影像上所見 **C／B／C／A／A 僅為公告候選**，不升級 `answerVerified`。

## 完整共用材料原始像素關聯

五題共用同一篇梅花宴文章（大伴旅人、山上憶良、《梅花歌序》及《蘭亭集序》），原本全文位於第 4 頁第 11 題之前。原始單獨共用材料 `sudu/data/processed/113/role-a-c11-15/shared/113-00-C-SHARED-11-15.webp` 由**第 4 頁原始像素** lossless 裁切 `[90,155,1310,951]`，WebP SHA256 **`5ec8a53ab2cefde309a7b70a52a1bc12203d85ab6212e8b644b834bb2ce21c01`**，Git blob `ccf2d2b3765b5313265917a7b9f0f88189cc667b`。包括「▲閱讀下文，回答第11–15題」、全文段落至「以雪喻梅，真是絕佳示範！」，**無第 11 題或前一題、無整張試卷**。共享 `sharedMaterialId=113-00-C-SHARED-11-15`；跨頁 4→5 關聯第 11～15 題，SQL `shared_materials` 單筆可讀回，SHA 對應相同原圖。沒有將原文用 AI 畫圖或重新 OCR。

## 五張單題原始像素 WebP 與來源 revision

| 原題號 | 原始頁／裁切 `[x1,y1,x2,y2]` | WebP SHA256 | 來源 revision | 公告答案候選 |
|---|---|---|---|---|
| 113-00-C-11 | p4 `[90,953,1310,1150]` | `fef1fa4be3d594ef7fadf774af7f475602917ddfb99a15b58f29296a69d3203f` | `e9d5169deebd85df28f61a9dc1288588581a478152e0fdb66764b9f6f04606c5` | C |
| 113-00-C-12 | p4 `[90,1154,1310,1284]` | `0370950412243fd6e2cae905c155cecfb81c90ea17eb34c995f5693a4fc87e51` | `07bdd90a06e947bdb32cb1f542abc28a8bbc9367f0dea58c02a60949fb8206a5` | B |
| 113-00-C-13 | p4 `[90,1293,1310,1810]` | `6e4f5b84f8c9e83aa1e3e22681c266a5b6b268e8551ae7266cc33c5ed94b7ad4` | `be8c57345bf5aba57a68f07f401e239767a5770ec618cce3b31fc07a909afa7f` | C |
| 113-00-C-14 | p5 `[90,165,1310,485]` | `8c0e426a3b4a40fa31e0391b74663511648f7bb3f4734824d437efbcd419abf5` | `285199fa48018d8c8cd86ae89b4315b0af6f591f8386f42882ebd136cad1792a` | A |
| 113-00-C-15 | p5 `[90,492,1310,1600]` | `c2320b02faeb81e70d9e06a001105e11a204129a23635dbd3bc40559b9085599` | `e8b5a029f0cbf08b0fa1c0d8ea454281ab864de1e10c26d2dd98277f0fa61052` | A |

本角色已**實際直接開啟原圖及上述 5+1 張 GitHub WebP 目視**並逐張核對題號／題幹／A～D／必要材料：第 11、12 題完整四選項；第 13 題原始並排雙欄大伴旅人與王羲之對照表、①～④／黑白圈標記與 A～D；第 14 題原始兩個梅詩方框及選項；第 15 題完整梅樹宴會圖、甲乙丙丁人像與四張直式歌箋、①②推論與 A～D。**沒有相鄰題混入、圖表缺漏或整頁試卷**。全部 6 張使用官方既存 WebP 解碼的 RGB 像素 lossless 裁切，CI 逐像素相等，非 AI 重畫。

驗收記錄在 `sudu/data/processed/113/role-a-c11-15/VISUAL_QA_ASSISTANT_20261025.json`，明確標示 **ChatGPT Role A 來源圖片自查**、每張圖片 Git SHA／SHA256、原始頁 SHA、共用閱讀跨頁關聯、各題完整圖表與 QA 筆記。這不是獨立 Role E 教學審查、真人教師證書或正式發布 PASS；manifest 仍維持來源 QA 的 DRAFT，原始答題頁與教材需各自完整驗收。

## 原有 OCR／文字錯誤與局部候選修復

舊 113 年 `sudu/data/years/113.json` 的第 13 題 D 選項在正確句「④與黑圈④，皆形容內心獲得愉悅和滿足」後混入**第 4 頁頁尾與第 5 頁頁首**；第 15 題 D「①錯誤，②正確」後混入**第 5 頁頁尾以及第 6 頁下一組第 16～19 題閱讀文章**。新獨立候選只去除選項 D 在首換行之後的無關跨頁內容（保留實際原文字形／符號），同時**完整保留原始污染文字與原始 SHA**於 `manifest.questions[].originalRawOptions` 供來源回溯。第 11、12、14 題全部 A～D 沿用原文字。第 13 題文字層因原版黑白圈／比較表有圖文格式問題，**尚待獨立精細題幹文字／表格 QA**；只因 WebP 圖像完整並不意味 `questionVerified=true`。

## SQLite／測試／交付限制

- 獨立候選 DB `sudu/data/processed/113/role-a-c11-15/question-bank.sqlite3` **只有本批 5 題與 1 組共享文章**，不是 113 全年度資料庫。每題 canonical JSON/payload SHA、`sharedMaterialId` 和原素材圖 SHA 可反查；**`PRAGMA integrity_check=ok`，兩次隔離全新匯入整檔 SHA256 均為 `62ad8f2e821906b6aeef69dddfa191081202894be4636a442c863a8b3c85ce09`**。所有題 `answer_verified/question_verified/teaching_verified/student_ready=0`，沒有偽造 AI E 或教師批准。
- 範圍僅 `scripts/role_a_113_c11_15_shared_original.py`、`tests/test_role_a_113_c11_15_shared_original.py`、`.github/workflows/role-a-113-c11-15-shared-original.yml`、本 MD、這六張新原始像素 WebP、來源 manifest、QA JSON、一份 5-row SQLite。只允許專屬隔離 GitHub Actions 在自己的新來源檔案下寫入 8 個初始原圖與 DB 產物，不改 main、Pages、此前 113 C01～10 或其他角色檔案。
- CI 驗證兩頁原始 Git blob、六圖 SHA 與解碼像素逐張一致、共享文章跨頁及每題完整影像 QA、原始 OCR 污染留存與 D 選項候選修正、來源 revision 篡改負測、五筆＋一共享 SQLite 2 次 SHA 和 integrity、已驗證前 10 題 regression。每輪須以**精確最新 HEAD** 實際 CI，不能引用上一版代替；最終數字依 Actions job。
- MASTER 只可接收這批 SOURCE 候選，仍需正式 113 全年官方公告／最終答案逐題更正確認、不同作者 Role E 真正雙層教學與完整四選項實質 QA、Role D 同原版來源及 teachingDigest 的 35 Demo V4 8 種尺寸×深淺 RWD QA，以及唯一 MASTER 受保護 main／Pages 正式同 SHA LIVE 驗證。**本批新增 READY 0，新增 LIVE 0**。

下一輪 ROLE A 按主指揮實際控制台以 113 年第 16 題起的原圖／跨頁材料、剩餘科目及 112→104 各年度資料缺口續作，避免在教學審核時重新裁切已驗收的原圖。
