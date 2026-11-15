# ROLE A｜114-00-E-11｜G1/G2/G3 最小來源入站（非學生發布）｜2026-11-07

**Task:** `A-114-E11-CANONICAL-G2G3-20261107-MASTER-DISPATCH`。正式 CLAIM：[Issue #36 #6718106733](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6718106733)。

## 已核對原始資料（不重作圖片或教學）
- 來源基準：官方 QA `3408bd78b0d40cbe00fbe2a4fb4c41626f183ec2`，205 題。原 canonical E11 `questionVerified=false`、`answerVerified=false`，原圖 `imageQaStatus=PASS`。 E12 已通過來源 G1/G2/G3，本 PR 不碰其任何內容。
- 114 英文官方試卷第 3 頁 `sudu/data/original/114/00-E/p003-1b1768452e-v2-w1400-q66.webp`，Git Blob `5ff21a726938e64e0b7efe3bb8abda65e55e1d4f`，來源頁 SHA256 `51b265b41dde351f307310a16247b390fc97e9102c026082324cb22d07e965cb`。直接檢視印刷的第 11 題 Dad/Son 五輪對話、空格及 A–D，與 canonical 完全一致。
- 原單題 WebP `sudu/data/processed/114/webp-v1/00-E/114-00-E-11.webp`，Git Blob `50f8fde174f4f0e66dc0f2315c11c5a73cec6b7a`、SHA256 **`ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0`**，原裁切 `[90,275,1310,591]`，無相鄰第 12 題混入。
- 題目原 sourceRevision **`646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036`**，不更動問句、選項及 sourceRevision。
- 官方公布答案影像 p1 `sudu/data/original/114/00-E-answers/p001-ebd3940a54-v2-w1400-q66.webp` Git Blob `5f2920313607af4e756095cd3d6098c8a3ab7440`、SHA256 `a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863`，**印刷第 11 題答案 A**。官方 114 英文更正公告歷史 SHA256 `79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53cbc`，更正範圍只列 E26，不列 E11；**不能擅稱整份試卷均無任何更正**。底層 PDF 是沿用歷史 SHA，沒有在此工作重新下載與重算。
- 歷史 ROLE A E11 獨立 source-stage 收據 [PR #145](https://github.com/homelux-huang/7581707/pull/145) Git Blob `d64132d1cae7fb1a4797e89f5853f529e29f01c5`；原題文字 QA `bd90a3c3814353379eacf89759fcd3153099fa53`；官方公布答案 A 圖像 QA `bc3d19885e2ebc3d27092b673636bd84c89f65c6`。逐字／逐原圖 SHA 驗證後搬入官方 QA，並新增正式 publisher 相容的 G2/G3 文件。
- ROLE B [PR #44](https://github.com/homelux-huang/7581707/pull/44) 原完整教學已凍結，canonical teaching SHA256 `ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb`，本任務不得重寫或自審。

## 寫入與驗證邊界
僅修改 114 `questions.json` **E11 一筆**的 G2/G3 來源驗證旗標及其綁定證據、`webp-manifest.json` E11 `visualReviewEvidence.referenceSha256`、SQLite E11 一列的 `payload_json` / `payload_sha256`、`inventory.json` SQLite／JSON 真實檔案 SHA。原 204 題內容及 SQLite payload 不可有任何更動。證據檔只加入 E11 自己、與原本已驗收 Git Blob 完全一致的歷史證據，以及 E11 issuer G2/G3、SQLite QA、單題來源報告。

`scripts/role_a_114_e11_canonical_g2g3_20261107.py` 會先比對最初 QA 的 bank/manifest/inventory/SQLite Git Blob，再核對原 WebP SHA + Git Blob、原圖 G1 items[]、文字與四選項、原答案影像 A、原公告 E26 範圍；任一不符就 **SOURCE_HOLD**，不改資料。GitHub Actions 使用隔離分支、`contents:write` 在該分支實際寫入 binary SQLite，之後執行 205-row/parity、其他 204 不變、G2/G3 正向及來源／答案／公告／READY 負向驗證；合格後由 GitHub connector 建立 Draft PR 至官方 QA 分支。

**ROLE A 只可達成 SOURCE_G1/G2/G3，不能設定 E trust、blind solve、D 16/16、studentReleaseApproved、main approved 或 LIVE。** 需等 MASTER source PR 正式驗收收件，再交不同 Session 的 ROLE E 進行教學內容 QA，D 真實 publisher emit 16 次，同版本可信收據及保護分支發布。此文件不代表 CI 或 PR 已完成，請以真正 GitHub Actions run 與最終 HEAD 為準。
