# ROLE A｜114 年英文第 13／14 題｜已存官方原頁與單題原像素文字完整性（2026-10-28）

**Master Issue #36** `A-114-E13-E14-SOURCE-QUESTION-FINAL-20261028-02` CLAIM #6458386819；Role A 原始官方題幹/四選項/單題原像素，不是 Role B 教學作者、E 獨立 AI 複核者、D 正式 UI 測試或唯一 MASTER 發布者。

本批在自己的前一輪 [Draft PR #110](https://github.com/homelux-huang/7581707/pull/110) HEAD `0bb49eab86fd0619b9aecb801dc570a37103e985` 新開 `qa/role-a-114-e13-e14-source-text-20261028`，只新增兩個 **Role A 原始圖文直接觀察** JSON、來源測試、唯讀 workflow、此 MD。疊加此前 PR94 114 E11/E13/E14 官方答案已確認憑證。**不改** `questions.json`、完整 SQLite、manifest、原始圖片、問答內容、作者教學、E、D、PR30、main 或 Pages；且不重新裁圖與 OCR。

## 實際官方原始圖像與題幹

114 年共同科目英文試卷 `4-00-E`，第 3 頁，原始 Git archived WebP `sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp` Git blob `5ff21a726938e64e0b7efe3bb8abda65e55e1d4f`，來源原圖 SHA256 `51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb`。已直接目視它與下列兩張既有「單題」原圖，且與 114 年原始 raw `sudu/data/years/114.json` 與 PR94 canonical `questions.json` 逐字比對，無相鄰其他題號或印刷頁首頁尾。

| 題號 | 已存在原始單題 WebP SHA256 | Git Blob SHA1 | 原頁 crop | 官答既有驗證 |
|---|---|---|---|---|
| `114-00-E-13` | `81f4487c4012456b4f1c3449aa388f16d12de19b72cc844ae6b6269be76e9be7` | `d3a37cc4ecb6c72b06fa19919a376a34203ed739` | `[90,870,1310,1120]` | **A**，PR94 原答案及更正範圍 |
| `114-00-E-14` | `388773561e436315452bdf0c28c792efa0983eb25538e8b3119926cd338f3a94` | `2ec99e4912ac49b6c70e84183caadcdb402136bb` | `[90,1118,1310,1369]` | **D**，PR94 原答案及更正範圍 |

第 13 題印刷原句含 `Vendor: These vegetables are chemical free.`、`Customer: They look great. But what about the eggs?`，後接賣家說農場每天早晨供貨，新正解 A 原選項 `Are they fresh?`；其他三項 **How much are they?／Do you plant them?／How do you cook them?** 亦完整。第 14 題人物確為 **Ken 與 July**，討論戲院排隊 `Let’s cut in line`、`No way` 與 `Let’s go to the back of the line`，原 D `How can you even think of doing that?`；原 A/B/C 也完整。兩張題圖皆無旁題、無數學表格公式、無另需拼入的閱讀共用材料。圖片無重裁，原 SHA 完全不變。CI 必須再真實 Pillow 解碼、對原始 p3 相同區塊逐像素 RGB equality，且源文字及 options 必須與 raw/main 候選**精確一致**。

已在 `sudu/data/processed/114/review-evidence/114-00-E-13-source-text-20261028.json` 和 `.../114-00-E-14-source-text-20261028.json` 留下**實際 ChatGPT Role A 原始像素/文字觀察**，並標明非不同作者 E 內容審查、非真人教師簽核、非主指揮正式來源入帳。前人相同圖 SHA 的歷史 assistant 圖像 QA 原紀錄仍保留，不新增大量無來源的 PASS。

## Canonical revision、官答與教學版本

- 第 13 題 `text_revision=074fb9847eda936d31dfd4503f3a7a12cbde9f89ddc888957d8eba4f17fa746c`，第 14 題 `text_revision=6164a310c7d38229aaaf52df678121ee88f6242cf6611310badfb5b1b46714dd`。在原本官方一對一原題及單題 WebP SHA 下，後續任何文字或圖片變更都使該 revision 失效。
- PR94 已有原官方答案像素與 114 英文確認公告的逐題 scope：**僅列 E26，未列 E13/E14**，不能宣稱全科無更正異議。E13=A、E14=D 的 `answerVerified=true` 是**先前真正 A 官方來源 QA**，本輪無再次賦值或重算。原問題 `questionVerified=false` 仍不改；原始 114 題本 PDF SHA256 `1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf` 是**歷史記錄**，本輪未重新下載 PDF 實體雜湊。
- 第 13 題原作者 B PR44 `composedTeachingDigest=e62d80dd377d6dcd8872b416f2499dc6c1c6f185f14644b5bdab188ff5a910d1`（舊教學候選）；第 14 題原作者 B 在 [Draft PR #106](https://github.com/homelux-huang/7581707/pull/106) **已僅修 Cambridge US 字典 URI**，但新的 `composedTeachingDigest=88aa9992f062197be0f930dda08ad61e71b9dcc21f1b10eb48cd12a125e07644`，而非原 PR44 `b9c464...`。**舊 E / D digest 不能借用**，須獨立 Role E 重新審查正確 URI 並與正式 publisher 產生之 V4 8×2 真正綁同修正後 digest。
- 正式學生 source 114 已批准數為 0。不得由角色 A 把 `answerVerified` 與原圖 QA 誤當 `questionVerified`、內容 E 或 READY；真教師資格／Ed25519 教師簽章不是必要條件，但專業內容及安全驗證仍是。

## 真實 CI 與交付界線

`tests/test_role_a_114_e13_e14_source_text_receipts.py` 對兩題各自驗證 Git Blob SHA1 + WebP SHA256、來源頁原像素相等、題幹／四選項原始版本、存於源 JSON 的公告 A/D 獨立 scope、原圖 QA 所屬角色、sourceRevision 錯字/變圖 SHA 篡改負測、205-row **原生 114 七欄 SQL schema** canonical payload JSON/SHA 完整比對與 PRAGMA integrity；再執行本角色前一 [PR110](https://github.com/homelux-huang/7581707/pull/110) E11 9 tests 與 [PR94](https://github.com/homelux-huang/7581707/pull/94) E11/E13/E14 官答與隔離雙次重建 SQL 8 tests，確保**不削弱、不取消原來源 QA**。Workflow `.github/workflows/role-a-114-e13-e14-source-text.yml` 只有 `contents:read`，不部署、不更新主分支或其他來源。

**本輪新 READY=0／新 main=0／新 LIVE=0**。MASTER 只接收原圖＋圖文 A 直接觀察證據，待 Role E 精確 B 教學版本內容審查、合法可信憑證、安全發布器、D 正式生成相同 source+teachingDigest 的 V4 8×2 實測、主指揮受保護 main/Pages/LIVE 才可能逐題上線。對 B 作者而言，E13/E14 原始圖片／題文不需重做；有新的 E14 字典網址版本要同步引導 E/D 重新審查。
