# ROLE D｜114 E12/E11、115 MB21/MB22/MB23｜正式 V4 emitter 8×2 前置接入（2026-11-06）

## 範圍與治理
- Task ID: `D-114-E12-E11-115-MB21-23-EMITTED-PREFLIGHT-20261106-01`.
- ROLE D 獨占 CLAIM: https://github.com/homelux-huang/7581707/issues/36#issuecomment-6688987016
- Protected main base: `9c40dbc15becd4904749f9fe1b3f83a092136311`.
- 唯一正式 UI：`sudu/v4-115-multisubject-review-demo.html`，不重新開發或覆寫。
- 不改 A source/205 SQLite、B/C 教學、E 收據、MASTER publisher、approved JSON、正式 Pages 或信任政策。
- 本輪任務只建立正式資料 *未到位時 HOLD* 的測試入口，**不製造 READY／LIVE 或獨立 E 審查**。

## 2026-11-06 真實來源狀態
- 114 approved: 0/205；115 approved: 5/205（115 MB02、03、04、05、09）。
- `sudu/release-governance/independent-review-policy.json`：`reviewMode=DISTINCT_AI_CONTENT_RECEIPT_V1`、`requireHumanTeacher=false`、`trustedAiReviewReceipts={}`。
- 114 canonical A E12→E11 共用資料 lease `A-114-E12-E11-CANONICAL-ADMISSION-20261104-01` 尚未 RETURN。與 MASTER #6682878931 一致，**全部五題正式 UIQA HOLD**。
- 原 D PR #138 MB21/22 的 Chromium 32/32 與 PR #150 MB23 的 Chromium 16/16 是 **HTTP page.route staged QA_ONLY**。PR #142 E12/E11 也是 staged；不應沿用為正式 emit 16/16。歷史測試仍保留、不重做。

## 新入口的 Fail-closed 合約
`tests/sudu_role_d_emitted_only_8x2_20261106.cjs` 使用 **從本次 exact HEAD 倉庫讀出的實際 approved JSON、保護分支 E policy**。沒有 `page.route`、沒有 synthetic 題庫、沒有修改學生正式資料；只使用真正 `sudu/data/approved/{year}.json`。

預檢 `SUDU_D_MODE=precheck node tests/sudu_role_d_emitted_only_8x2_20261106.cjs`：
- 驗證兩年 205 題年度清單與已核准題數一致、各 QID 不重複。
- 順序列出 114 E12、E11、115 MB21、MB22、MB23 每題目前 approved/可信 E receipt 缺件；原圖 SHA、選項、官答與原始版本 pin 不相同則 HOLD。
- 正常保留 `HOLD_UPSTREAM_ADMISSION` JSON artifact；**0 張截圖不是 16/16 PASS**。
- 工作流程還執行負向測試，要求未入站 E12 的 formal 模式必須拒絕。

正式命令範例（**僅 MASTER 的 A/E 真實入站與安全發布流程完成、提供精確 SHA-pinned evidence bundle 後**）：

```bash
SUDU_D_MODE=formal \
SUDU_D_QID=114-00-E-12 \
SUDU_D_EXPECT_SHA="$(git rev-parse HEAD)" \
SUDU_D_FORMAL_EVIDENCE_PATH="sudu/.../original-sha-bound-uiqa-admission.json" \
SUDU_D_FORMAL_EVIDENCE_SHA256="<SHA256 from independently reviewed admitted evidence>" \
SUDU_D_SITE=http://127.0.0.1:8765/sudu/ \
node tests/sudu_role_d_emitted_only_8x2_20261106.cjs
```

此測試需要現存真實 emitter 的當前 JSON、受保護 E 收據、不同作者/審查 Session、與官方來源 `sourceRevision`/WebP SHA/官答/文字/選項一致的憑證。對 114 年 composed teaching digest 會核對 `digestCanonicalPayload`（含來源 revision、WebP 與 teaching）；對 115 年則可核對 canonical `teaching`。兩者都要與原教材物件及正式輸出的各段解說一致。不能任意將舊 digest 當作現行教學 SHA，也不能只在人工欄位打勾。證據結構是此測試的輸入合約，必須由 MASTER 的來源收件與真正獨立審查產生；本 PR **沒有也不會自行產生這個 bundle**。

正式模式才會使用 Playwright Chromium 真實瀏覽器，固定 360×800／375×812／390×844／412×915／430×932／768×1024／1024×768／1440×900 × light/dark；逐題檢查 HTTP 正式 approved、路由、題號、四選項、WebP decode/HTTP bytes SHA、解答、四選項解說、計算/非計算卡、畫面溢出、console page error，保存 16 張 PNG 和 `formal-uiqa-report.json`。任何單例 FAIL 就拒絕 16/16。MASTER 仍需另外核准真正 UI receipt/Publisher G0–G10/PR、CI、受保護合併、Pages verify_live，D 不決定 READY/LIVE。

## 後續阻塞解除順序
1. ROLE A 完成 E12→E11 205 bank/SQLite/sourceRevision 與原始官方答證據 RETURN；接續 115 MB21→MB22→MB23 canonical。
2. ROLE E 使用不同 Session 在 *最新同一 source & teaching SHA* 逐題審查；由 MASTER 決定是否在受保護 main 註冊可信 receipt。
3. MASTER 由實際 canonical source branch 建立最小 importer bridge，正式生成經過 G0–G10 的精確批准題資料與 SHA-pinned evidence bundle。
4. ROLE D 重新檢查最新原始版本及 composed teaching digest，啟動 formal 模式；真正 16/16 後才交 MASTER，不能沿用 QA_ONLY 截圖。
5. 每題可發布即各自接入；104～113 年新增開發暫停。

此階段預期狀態：`FORMAL_UIQA_HOLD`，不是測試失敗也不是發布成功。
