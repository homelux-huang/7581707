# ROLE A｜114 國文第 23 題官方公布 D 答案來源核對／SQLite 單筆交付

**Issue #36**：`A-114-C23-FINAL-ANSWER-SHARED-20261026-16`，只負責單一 canonical `114-00-C-23`，不是獨立 E 教學 QA、真人教師、V4 UI 或 MASTER 發布權限。分支 `qa/role-a-114-c23-final-answer-20261026`，**精確基底**本 Role A 已成功收件的 [PR #98](https://github.com/homelux-huang/7581707/pull/98) HEAD `e448bf0c814ae3a2075faea23ba75b244519928d`；不碰 PR98、PR30、main、Pages、既有 B/C/D/E 同時工作檔案。

## 來源與疑義

- 官方考卷 114 4-00-C，原試卷第 7 頁真實 WebP SHA256 `63d68af4507fd198cd045a5a24b4efd4f33f95b1c234e991fe0f9ed65c76bfa2`；原始考題 PDF SHA256 已有歷史記錄 `f7c8a4b732136f5f2750fe840bd58cef09c142701e25f80686073bcecba0df74`，**此批未重新下載 PDF**。
- 題號 `114-00-C-23` **完整原始單題 WebP** 是 `sudu/data/processed/114/webp-v1/00-C/114-00-C-23.webp`，Git blob `ba29b99f00b9b556b834e27b88918831a5ffe35b`、SHA256 `50547b2a2daa71dea457bd11bf4ebb1a4bcc780e0443ac6cda15374829e67cc1`、原頁裁切 `[90,1582,1310,1823]`。已實際開啟，題號、完整題幹、四個選項（D：「旦視而暮撫，已去而復顧。甚者爪其膚以驗其生枯，搖其本以觀其疏密」）完整、沒有相鄰第 24 題、考卷頁尾或整頁；既有 QA `qa-drafts/DIRECT_VISUAL_114_C19_23_SHARED_20261023.json` 的單題結果為 **PASS_DIRECT_ORIGINAL_PAGE_IMAGE**，此次只補原 Git 物件**不新增另一輪人工驗證或重裁**。
- 第 20～23 題共用〈壯夫縛虎〉文章維持完全相同原圖 WebP SHA256 `7b7f592f01378a6fa9ece08d87291810420479c9529f2d5233f10ad458c47f8a`。先前 Role A 的 C20/21/22 官答個別證據、205 筆 SQL hash、原題 QA 均不更改。
- 實際官方公告答案頁 `sudu/data/original/114/00-C-answers/p001-455eae60e7-v2-w1400-q66.webp`，Git blob SHA1 `c3090e94ab1cbf7adf9f7efd0581529eff00e26b`，**真實算得 SHA256 `7a0be40000064817a59aa8d049c783004f82d7fd13ee1e0de5b20a8ed9986331`**。表中第 23 題公布 **D**；答案 PDF 歷史 SHA256 `455eae60e7c8f943ada011bac3f488520a460432310448dc531dee7f0fd9e1e0`。
- 114 國文五頁更正範圍歷史 PDF SHA `afc4ad2e67004a40539d05406813ff361d99696607cf6fc71c62484cc3001a71`，已核對記載 **14、24、28、30**，不含 **23**；**不得宣稱整卷無異議**，不因候選答案文字相等就自動批准。這次僅由 ROLE A 以實際原始公布答案像素和年別完整更正記錄核對第 23 題。

## 資料及驗收契約

- `scripts/role_a_114_c23_final_official.py` 使用前一批嚴格通過的 `role_a_114_c20_c22_final_official.py` 真正 SHA/公告閘門函式；**先重新驗證前三題和原始共用閱讀資料**，再逐題對原始第 23 題 WebP、官答格第 23 題 D、公告範圍做正反測。保留既有 C23 `issues=["last_on_page_check_possible_continuation_or_footer"]`，不藉單題 WebP QA 清空 OCR 完整文字風險。
- 只新增 `review-evidence/114-00-C-23-official.json` 及更新 `questions.json` 的 **Q23** 官答證據欄位：`answerVerified=true`、`officialFinalAnswer=D`、`officialCorrectionChecked=true`、答案原圖核對旗標及 `officialFinalQaEvidence`。其餘 **204 題**全部保持原樣。原來源 textRevision **不變**。`questionVerified=false`、`reviewStatus=needs_review` 及 C23 原 issues 保留，並沒有 E 內容 QA／教學 digest／D UIQA／READY／LIVE 升級。
- SQLite 是 114 真實既有 7 欄 schema，僅改 C23 單一 `payload_json/payload_sha256`。每批進行 `PRAGMA integrity_check=ok`、205 筆 canonical JSON hash 一致與兩份獨立 SQLite 重播全檔 SHA 相同。與精確基底 PR98 Git SHA 比較，**除了 C23 之外所有 204 筆逐筆不變**。
- `tests/test_role_a_114_c23_final_official.py` 含 7 項來源、官答、公告年別正反、完整 205 SQL、PR98 前三題不倒退、C23 end-page 文字疑義保留、錯 SHA 與 options 篡改拒絕。專屬 workflow `.github/workflows/role-a-114-c23-final-official.yml` 只寫本隔離分支三個目標成果（source JSON、SQL、C23 official JSON），不會更改正式 V4 或部署。

**後續由 MASTER：** 以精確 SHA 收件，指派 Role E 不同作者逐題教學及原題文字複核，Role D 以最新來源與教學 digest 對現有 35 題 Demo V4 做真正 8×2 瀏覽器驗證，通過完整源答／UI／CI Gate 後再逐題增量發布；不能把 Role A 公布答案 QA 當作 E 或教師核准。**本批新 READY=0；新 LIVE=0。**
