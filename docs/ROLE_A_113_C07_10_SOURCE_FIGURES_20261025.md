# ROLE A｜113 年國文第 7～10 題原始單題 WebP、圖表及結構化文字修復候選

**taskId:** `A-113-C07-10-DIAGRAM-AND-TEXT-20261025-12` · **Role A SOURCE ONLY**，非 E 內容審查、真人教師或 MASTER 發布者。主控制台 [Issue #36](https://github.com/homelux-huang/7581707/issues/36) · CLAIM #6394434214。本獨立分支 `data/role-a-113-c07-10-figures-20261025` 由本角色 Q06 已完成 [Draft PR #75](https://github.com/homelux-huang/7581707/pull/75) HEAD `fe8a7d6168f4d274465ccbde02b6a1843e950d74` 派生，不修改 main、原始歷年資料、先前十張 WebP、唯一 114/115 主台帳、V4 或其他角色分支。

## 正式來源與不可虛報的驗證

113 年國文共同科目 00-C 第 3 頁，歷史已存官方原像素 WebP：
- `sudu/data/original/113/00-C/p003-67c0d477e9-v2-w1400-q66.webp`，Git blob SHA1 `9578305e9c4181d3b339b830e23e12402f4893d3`，實際檔案 SHA256 `3ccfa972ff173e8d4cf8c40448a7dc8a8092570b943d8c9b6a8d171d60e5fc33`；寬 1400，高 1981。**全部題目 WebP 均從此官方來源原始解碼像素裁切為 lossless WebP**，逐一以 Pillow 逐像素相等驗證，不使用 AI 重畫／OCR 產生影像。
- 原始已保存官方公告答案第 1 頁 `sudu/data/original/113/00-C-answers/p001-9a6ce177b0-v2-w1400-q66.webp`，Git blob `938f88435a9b21e257f11dfcfda71655e8a7a0c6`，實際 WebP SHA256 `a3c8154f5186c925a9408e4c4b50cd9a0c2b92db2fe3375d3d13d8491b9c7bc3`。公告影像對照第 7～10 題原始候選答案 A、D、B、B。**尚未完成 113 年所有更正公告全文／正式最終答案逐題確認，不能標示 `answerVerified=true`**。
- 歷史題本 PDF SHA256 `67c0d477e99d07cd59af0e9c75b261692c3089fd5559185f41945de32316093f`、答案 PDF `9a6ce177b0aec3f22957635cc9abc21539cf3356471b2e3dec65e550e8f9559a` 是 `sudu/data/years/113.json` 舊資料，**本輪未重新下載 PDF 原檔及實際再雜湊**。舊 113 年五卷 JSON 205 題候選 vs 原擷取流程 `questionsFound=196`，差距 9 並非可直接認定缺 9 題。

## 原始單題、必要圖表、原像素 SHA

| ID | 原始單題 WebP SHA256 | 原像素裁切座標 `[x1,y1,x2,y2]` | 原始必要材料／答案候選 |
|---|---|---|---|
| 113-00-C-07 | `dc654891d368033b5b422cf01181231aefc62e9a31452ad1e64aaca478291b4a` | `[90,164,1310,502]` | 梁實秋〈講價〉五段 ①～⑤ 與完整 A～D；A |
| 113-00-C-08 | `4ea59fb90d9bbec2f255944b0a5fc6be4f9a25257e3f74caa7aa3b5e10e88e49` | `[90,505,1310,657]` | 「而」轉折語意題幹與 A～D；D |
| 113-00-C-09 | **`428585747ee518a3e2d0e2d206bffd26a9b124402081cc5c504c16bfe7d3784b`** | **`[90,661,1310,1136]`** | 完整五種談判策略原印刷 2D 示意圖（對立、合作、妥協、迴避、順應）、橫縱雙軸高低、A～D；B |
| 113-00-C-10 | **`6d02e6a8bcc051c764bd6147f9f49c5b6edee7ea6b78be3ec9c3c439cb997936`** | **`[90,1137,1310,1840]`** | 《天工開物．舟車》魚骨原因圖、原始四欄 `① / ①－1 / ② / ②－1` 完整 A～D 表格；B |

**實際人工可讀直接檢查（由 ChatGPT Role A 來源助理完成，非人類認證、也非 E 教學審查）：** 已開啟全部四張 GitHub WebP 和第 3 頁原圖目視，第 7、8 題題號／題幹／四選項完整且未重新裁切；第 9 題第一次 `[90,661,1310,1123]` 底部橫軸「配合他人的程度」過度貼近切邊、字形有截斷風險，原初圖 SHA256 `2c42042d8f75bba4123e76e151e088659d769c90ad665fb26589f3fff87c54ac` **拒絕且不得計 QA PASS**。僅局部調整 Q09 底端至 1136，連動 Q10 起端從 1125 往下移至 1137，避免混題；第一次 Q10 原 SHA256 `d4491b6806725f979615be77164a943732f511991b680fdfc6383a21190c1491` 予以作廢。最後二張新圖已目視確認 Q09 橫軸字體完整、Q10 標題與魚骨／四欄表格完整，沒有下一題、頁尾或整頁；**Q07/08 圖 bytes 未變**。實際四張 SHA-bound 逐題來源圖像 QA 在 `sudu/data/processed/113/role-a-c07-10/VISUAL_QA_ASSISTANT_20261025.json`，結果是 `PASS_ROLE_A_SOURCE_IMAGE_ONLY`。原始候選 manifest 的發布資格仍 `DRAFT_NEEDS_INDIVIDUAL_SOURCE_PIXEL_IMAGE_QA`，需保留獨立 QA 契約，禁止藉來源自評直接放行。

## 有界文字修正（保留原始 raw、並非最終內容 QA）

Q07、Q08：沿用已保存 `sudu/data/years/113.json` 原生題幹與全部四選項，無需重新 OCR。

Q09：舊 OCR `options[]` 因原圖二維策略圖的 `自我堅持程度`、`配合他人的程度` 與圖內迴避／順應詞彙混入選項文字。新獨立候選按原圖實際四列直接轉錄：A「①、②皆正確」、B「①、②皆錯誤」、C「①正確，②錯誤」、D「①錯誤，②正確」。完整原始混雜選項仍不變地保留於 `originalRawOptions`，**圖表仍由 WebP 原始像素呈現，不在文字裡重畫或丟掉圖**。

Q10：舊 `options[3]` 在真正 D 選項後混入第 4 頁整篇第 11～15 題文章；舊候選四欄表格也因擷取而把內容擠成單串。新獨立候選依 **原始印刷表格** `①,①－1,②,②－1` 對照 A～D：A「載人／重視人權／運貨／貶抑物價」、B「載人／怕走路累／運貨／互通有無」、C「北方／重視人權／南方／貶抑物價」、D「北方／怕走路累／南方／互通有無」。完整 fishbone、四欄表格、來源原句保留在官方原像素 WebP；原始含跨頁污染之文字完整保存於 `originalRawOptions`，不覆蓋舊檔。**來源修正是候選，非完成正式題幹／計算／教學 QA**。

最終來源 revision SHA256：C07 `ff4d5109a27db1bff06d28df802051167915a627ac116e75ce5c456df21dfc26`；C08 `052e45e52d7f966f0f4e249522a63dfb1813124b93c2a09239b7848c1a0298d5`；C09 **`826ea6153ea63de6a74bc95b747b88701b613df1d117f894c10844c2322d15be`**；C10 **`48154f29ead5dd768337d005273a43815bef736d59857c4415d5306af0d2bb15`**。任何教學或 V4 修正需以這些精確版重新產生 teachingDigest／UIQA，不得沿用舊 SHA 測試。

## SQL 與 CI

四題單獨候選 `sudu/data/processed/113/role-a-c07-10/question-bank.sqlite3`，**不是 113 全年題庫**：`PRAGMA integrity_check=ok`；兩次隔離全新 SQLite build **整檔 SHA256 均為 `16e835c5d7d4e81ab5773d5f5f341f912e6ec22eb65192ee32634b897a3f614c`**；四筆 canonical JSON、payload SHA、選項、圖片 SHA、sourceRevision 與 SQLite 全數讀回相等；`answer_verified/question_verified/teaching_verified/student_ready=0`，沒有一題升級。

產出路徑全部限制在自己分支：`scripts/role_a_113_c07_10_source_figures.py`、`tests/test_role_a_113_c07_10_source_figures.py`、`.github/workflows/role-a-113-c07-10-source-figures.yml`、本 MD、`sudu/data/processed/113/role-a-c07-10/` 的四張原圖、manifest、獨立 SQL 及逐題影像 QA。GitHub Actions 先嚴格比對最早六個新增資產；必要圖表修復後只允許精確四個自身 Q09／Q10 圖檔+manifest+SQLite 的改動，不能觸及第 7/8 題或其他人的任何檔案。各源圖片 CI 包含像素、圖表／表格、官方已公布答案**候選**、原始 OCR diff、負面篡改、歷史 Q01–06 SHA 回歸、SQLite 雙次獨立 SHA；最終應於 **PR 最新 HEAD** 重新驗證（不移用舊次數）。

正式官方更正公告全文／PDF SHA 實證、Role E 不同作者 AI 高職／國小兩層四選項教學內容複核、Role D 原本 35 Demo 的實際 8 尺寸×深淺主題測試、MASTER 受保護 main 及 Pages 同版 LIVE 均未完成。**新 READY=0，新 main=0，新 LIVE=0。**

**MASTER 下一步：** 只接收本源圖片及候選資料 SHA/真實 CI 成果，依官方更正公告判定是否可形成最終答案，將來源文字複核與獨立 E、D 真正相同版本驗收分別派工；缺證題維持 QUARANTINED，不因歷史自動配答批量核准。
