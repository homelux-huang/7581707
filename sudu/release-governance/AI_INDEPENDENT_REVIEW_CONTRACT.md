# 7581707｜獨立 AI E 內容複核證據契約（隔離發布器提案）

**最新權限：** Issue #36 使用者 2026-10-25 統一指令取消真人教師資格、授權簽章／名錄與 GitHub 真人 APPROVED 的教學前置條件。「高職老師」只代表教學角度。此文件屬 **Draft PR**；不代表審查通過或 main 已上線。

## 實作狀態與繼承邊界

- 基礎：已經角色 E 唯讀檢核並補足其 P0 負測之 Draft PR #46，原代碼 `separate_ai_content_receipt_verified()` 驗證真實 Issue #36 留言、原始來源 commit、官方答案證據的內容（不僅是 SHA）、獨立 A–D 筆記與 protected-main 信任；測試中的虛構 GitHub API 回應均為隔離 mock，非真實 E 核准。
- 此隔離分支 `governance/114-115-ai-publisher-gate-20261025` 在 **`certified()` 與 `sudu_verified_publish.py` 實際引入 `reviewMode=DISTINCT_AI_CONTENT_RECEIPT_V1`**。只有當 E 的原始複核完整且被精確版本註冊於受保護的 main 時，新題才可能通過「內容審查階段」。不再以授權教師、簽章或真人 GitHub APPROVED 事件作為新題前置條件。
- 此新模式對 B/C 的 `humanTeacherVerified` 舊資料欄位不予判斷：false／缺值都不代表教學不合格；true 也不得自動批准。
- 已存在正式版本的五題仍需完整比對各自的 **questionRevision、WebP SHA、teaching Git Blob**，不能將 5 題例外擴張為新題發布。

## 真實獨立 AI 複核證據

`trustedAiReviewReceipts` 僅允許經正常 main 治理接納的 **真實 Role E** 原始 JSON Git Blob 和逐題狀態，不從可修改的來源 QA 分支取得授權。

每張證書綁定：`year`、`questionId`、`questionRevision`、`webpSha256`、`teachingDigest`、`teachingEvidenceSha256`、`officialEvidenceSha256`、官答候選、B/C 作者 session/task、**不同** E reviewer session/task、來源 commit、Issue #36 真實 RETURN comment ID 與 GitHub 帳戶、4 個彼此不同且具實質內容的選項理由、計算驗算（或確實非計算）、高職／國小雙層內容審查、官方更正範圍及可讀 MD 複核筆記 SHA。

單看主檔 reviewer 字串、簽章或 PASS、任意整數留言 ID 都不足以核准。對新題的 trusted registry 必須與**protected main 真實 GitHub Blob**完全一致；不是從作者 PR 可任意改寫的本地 JSON。若 main 未受保護、API 不可用、身分／session／SHA 不一致，仍須 fail-closed，這是**程式碼可信度**而非教師資格要求。

**仍應後續完善：** 若多個 AI Session 共用同一 GitHub login，GitHub 身分只能證明 API 回傳者帳號，不能獨自證明 Session 的獨立性；主指揮仍須將任務租約、真實 E 留言和 reviewer／作者 session 狀態納入不可由同作者改寫的可信配對。僅不同選項文字或 SHA 通過機器檢查並不等於 E 做了實質內容複核。

## 發布仍保留的獨立閘門

`sudu_verified_publish.py` 的逐題 OCR／原圖尺寸裁切／表格／圖像 SHA、官方最終答案及更正公告、不得捏造的來源解題證據、雙層 4 選項、計算完整性、V4 同 revision／digest 的 8×2 實際互動與 CI 及最終 Pages LIVE 同版驗證皆獨立保留。

**尚未發布：** 本 Draft 新政策 registry 初始為 `{}`，實際未具備可驗收的新 E 複核憑證，故新 READY=0、main=0、LIVE=0。不得直接改 main、自己設 true、移除 fail assertion 或重用不同教學版本的舊 UIQA。須由唯一主指揮在各題確實完整通過後分題增量部署。
