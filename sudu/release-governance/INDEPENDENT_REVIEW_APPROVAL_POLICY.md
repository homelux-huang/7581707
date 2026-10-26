# 128 題｜獨立審查不可自簽安全政策（P0）

新增每題正式 admissions 的「可信任不同審查者身分、實質內容、可驗證簽章」必要 Gate，不能只依靠來源 QA 分支的 reviewer 字串、PASS、文件 SHA 或相同作者自己生成的簽章。

- 公開可信審查者金鑰政策只存在正式 publisher/main 管轄的 `sudu/release-governance/independent-review-policy.json`，**絕不使用 QA source 分支替代**。
- 預設沒有已核准的外部審查者金鑰，新增題目一律 fail closed；人類教師資格是否強制，本次採最保守 `requireHumanTeacher=true`，後續應由使用者與正式稽核 Session 決定是否變更，不能默默放寬。
- 完整 Ed25519 簽名涵蓋：題號、年度、題目 revision、WebP SHA、教學完整 canonical digest、教學來源文件 SHA、不同的來源作者與審查者身分、審查日期、四選項逐項實質分析、雙層教學與計算／非計算審查、獨立審查文檔路徑及其 SHA。
- 署名 key 必須經離線角色資格確認後才能加到可信任 `main` 的金鑰名錄；不提供或產生任何私人金鑰到程式碼、QA 資料、CI log。
- 既有正式五題通過原程序且已 LIVE；為避免破壞學生現有資料，**僅將完全不變的五題**固定 2026-10-24 源文字 revision／WebP SHA／教學 JSON Git blob OID 做相容白名單。只要修改其中任何內容就立即失去歷史白名單，必須重新依新政策審核。此舊版白名單不代表五題有人類教師審查。
- 直到有真實授權外部審查者，ECON34、MB20～25 和其餘未發布題目都必須維持 BLOCKED；不能為達成新增 LIVE 而偽造 reviewer 或自行批准。
- 負測：改 signer 名字、來源作者自簽、同作者同 reviewer、擅改題幹 revision、WebP、教學 JSON、逐項審稿內容或審稿文件、錯誤簽章、無授權 signer，都必須拒絕。

這是對「證明審核主體」的安全補強，原題庫資料不更動、G0～G10 全部保留。
