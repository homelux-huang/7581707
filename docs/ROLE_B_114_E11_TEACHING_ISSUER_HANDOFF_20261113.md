# ROLE B｜114 英文 E11 原作者教學 SHA issuer｜2026-11-13

> AUTHOR-ONLY / NO RELEASE / NO E TRUST / NO UI PASS

## 任務與範圍
- Task ID：`B-114-E11-NATIVE-TEACHING-ISSUER-20261113-01`。
- GitHub Issue #36 CLAIM：https://github.com/homelux-huang/7581707/issues/36#issuecomment-6849116273
- Author source：PR #44 `e0d4532c751127204e73af9cd9d3a95c52449131`；原始 E11 lesson Git Blob `a4aa8df70cf3f3fa8c4f62a568d73fe90511154b`。
- QA 來源（起點）：`15108e8e657d070724889f1df3d3a6ae6da96d97`，E11 official G1/G2/G3 已由 PR #179 合併。Protected main `5546a603abfe0af2e62c0e5f63f775be0bfb24cf` 不變。

## 冻結來源與教學
- QID：`114-00-E-11`；官方答案 A（原始官方答案，來源 ROLE A）。
- Source revision：`646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036`。
- 原始單題 WebP SHA256：`ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0`。
- 原作者原始 JSON SHA256：`6b365291eb43fd37377891149470f3bff9d8a6db5997eaff13295fb36fc402e8`。
- 原始教學 canonical SHA256：`ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb`。
- 原始 composed teaching SHA256：`3d250e8ecd621eda0f14f1839e6cf89b70b3649a1af0298611fedd9bbf57ceee`。
- 官方 G2 issuer file SHA256：`f8d316fcf6c44dbce476f394e5537692ea7b45bf957dd2187c547e74bae5c034`。
- 官方 G3 issuer file SHA256：`e767d4c5eb60dced6b2a86b73b29167b8d7b47430925da60f13a1bb6c7c8cbbf`。

## 本分支新增內容
- `sudu/data/processed/114/review-evidence/114-00-E-11-teaching-publisher-20261113.json`：將原作者已完成的高職＋國小雙層教學原文完整寫入正式 publisher 可讀 schema；不改動原作者 PR #44。
- `tests/test_role_b_114_e11_teaching_issuer_20261113.py`：核對 canonical SHA、205 題來源與原始 WebP、官方 G2/G3、四選項、重點詞、非計算欄位及負向拒絕案例。
- `.github/workflows/role-b-114-e11-teaching-issuer-20261113.yml`：指定分支 CI，只做作者證據檢查，不改動正式題庫。

## 獨立性與發布限制
- 原始 ChatGPT 作者 Session ID／對話 URL 不能可靠取得：`B_AUTHOR_SESSION_ID_UNVERIFIED`，不得從共享 GitHub 帳號推斷不同 Session。
- 本筆證據只確認原有 ROLE B 教學內容及 SHA，不代表 ROLE E 獨立複核、G6 盲解、G7 trusted receipt、ROLE D 正式 V4 16/16、MASTER 批准或 LIVE。
- E11 教學 `source` 文字保留原作者歷史提示「官方最終答案影像…待核」；來源後來已由 A 修復，MASTER／ROLE E 可評估是否以不改舊作者內容的 metadata/展示層標記最新 verified 狀態，不得悄悄重寫此 teaching digest。
- 僅在 QA 分支供驗收；不編輯 205 原題來源／WebP／SQLite／原作者教學／PR #173／V4／approved／trusted registry／main／Pages。

## 後續派工
1. MASTER：核驗本 PR 最終 HEAD 的作者 CI 成功後，可正常 PR merge **僅到**官方 QA source；不得單憑這個 CI 設 READY。
2. ROLE E：用原始 E11 題目和正解 A、完整 A–D 與最新 issuer SHA 獨立複核，保留真實 Session／blind provenance 缺口；須由不同於 B 的執行環境執行。
3. ROLE D：待 issuer 和 formal trust 及 publisher-emitted candidate 真正成立，使用原正式 V4 逐題 8 尺寸 × Light/Dark 16 次測試；非計算題須**實際隱藏**計算卡。
4. MASTER：全部 G0–G10 成立後才由受保護 main/Pages 增量上線、逐題 verify_live；已完成的 E12 教學 SHA 無需重寫。

## CI 狀態
- 本文建立時：尚未觸發最終 HEAD CI；以 GitHub Actions 的實際 final-head run 更新 RETURN，不能先寫成功。
