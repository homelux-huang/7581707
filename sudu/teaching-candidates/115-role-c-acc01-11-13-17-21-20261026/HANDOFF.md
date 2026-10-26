# Role C 115 會計學五題 A–D 教學候選交接｜2026-10-26

## CLAIM／責任／版本與範圍
- 唯一 GitHub 指揮 Issue：https://github.com/homelux-huang/7581707/issues/36 。Role C 已在 https://github.com/homelux-huang/7581707/issues/36#issuecomment-6408960861 真正認領，GitHub server `created_at=2026-10-26T05:30:00Z`，taskId=`C-115-ACC-01-11-13-17-21-20261026-07`。
- 作者：GPT-6 AI 角色 C（提供高職老師專業角度與國小白話），**不是 E 不同作者 AI 複核者，也沒有假冒真人教師、教師審核、簽章、GitHub APPROVED 或事前盲解**。五題原候選答案在寫教學前就已知，計算是事後獨立帶公式驗算，沒有寫成事前盲解。
- 專屬隔離分支 `teaching/115-role-c-accounting01-11-13-17-21-20261026`，baseSHA=`8910cfbbfedb638206b4b37b1b51817b75137edc`（原 Role C 自有 Draft PR #59）；未改該舊分支任何既有檔。題目讀自 Role A 的 PR #64 官方結構化修復分支 `qa/role-a-115-c15-text-sqlite-correction-20261025` exact HEAD `b6c449629efc80d37fa2e6dbb9e680e321367c14`，該 A 改動僅修 C15、五題會計與原 PR35 相同。
- 115 `questions.json` 新來源 Git blob SHA1=`0128adc3f41e748950c3f5af83fca6dd1c331f5c`；`webp-manifest.json` Git blob=`2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b`；唯一 PR #30 410-題協作台帳 Git blob=`2d60b3e571b18063990b9824ba1e14deee91b83b`。五題皆原教學 `NOT_DELIVERED`，沒有 Issue36 重複 CLAIM；`questionVerified=false`、`answerVerified=false`。
- 僅新增 C 專屬資料夾五份 JSON + `batch.json` + `HANDOFF.md`，單獨 C tests 與 read-only workflow。**沒有**改 PR30 台帳、原圖/PDF/OCR、官方答案、SQLite、其他作者的教學、D UI、E 審查資料、MASTER policy、main、Pages 或 LIVE。

## 五題新教學候選與發布價值
| questionId | 候選答案（未獨立官答） | 核心解說 | 計算區 |
|---|---|---|---|
| 115-09-2-01 | C | 現流／權益變動／綜合損益是期間，資產負債表是特定日期 | 無計算→null |
| 115-09-2-11 | B | 定額零用金報銷與撥補可分期，不得重複認費，次期不禁補 | 無計算→null |
| 115-09-2-13 | D | 2/1票據九個月→11/1到期；50,000－49,000＝1,000元；6%反推4個月；7/1貼現 | 完整公式、代入、8步、單位驗算 |
| 115-09-2-17 | D | 政府補助合理確信／自建減損／舊屋拆除處分／設備最大現金折扣淨額法 | 無計算→null |
| 115-09-2-21 | C | X1折舊多3,000；X2借累計折舊3,000／貸追溯重編影響數3,000，不動當期折舊 | 完整借貸、權益調整、算式與驗算 |

每題保存四個選項各自**高職專業原因＋國小口語正誤說明**、答案候選與原題全文、步驟、重點字詞粗體/ `highlights`、一眼記住、初級／中級／高級專業字詞與相關範例。會計 #13、#21 應顯示真正計算；#01、#11、#17 的 `hasExamCalculation=false`、`examCalculation=null` 不應出現「公式／分錄」空卡，接續 MASTER V4 fix PR #62 後仍需 D 以實際畫面重驗。

## 逐題精確三項SHA，請 E／D 不得使用舊 digest
| 題號 | question/options/image sourceTextRevision | 單題原 WebP SHA256 | teachingCanonicalSha256 |
|---|---|---|---|
| 01 | `b53d89b8f3299cd67adb5409d6db2df9fe3fc40a9346e72d622671201d760a83` | `065531b2bca6a6a5fa8d6c7a2ef15722acb4f32e945badf48ebcc2be75c705b2` | `4b07acf56dbb2fa28c13378f8b38efb6784e0ab3fbd8366f440fb9356bdda4f5` |
| 11 | `e0b11389d7daf8964c003349b047b965cffc8b87ba20127dae872818f70544cc` | `4d26c23e9c41f7c2aeb67564834dc3a02cb36ebd20157ea7617d0d1712de2a09` | `7721820b33bf4e95fab18737998187dd1625fbff90c206b7a1e562cc72d12c37` |
| 13 | `4f1adca9d34fbd20b5e5339d62773b8376ffba54b6405d9ca0e3251d4499447f` | `d23ae731fe5590f7235d21a163054498ffb0f9a49c8f4ab3a6b8425e7db06243` | `54b0a52b3178f9d84c92e690bb6a5253b33a338e0e55c74e024cf9ac69b1a54d` |
| 17 | `a98f1c3c7f311d952702fa08a345566ef00c71429eba2580054bf9aaf3eada5d` | `189634b5ecbefed9e5b253bb66c380ca4cfe8079e8b2bf024bcd8fabb8bcd370` | `e0b776b2490d225a0fa3412b577c7d7be42e6502276e364bb512c96f1637bb19` |
| 21 | `f04f7633507952b782104985f921fa596bace3616a3d725e0eabb1f24ae394ed` | `ab84aebcc2c1c7481708884de96f15e2419f9beb767f71d2549150815e48bd07` | `6a63f2f89101f658a5d51644feaf5319717393ca844949703ba0660813f8b5c0` |

全部五題 original `09-2` paper PDF SHA256（沿用既有 manifest，C 本輪未打開重新計算原 PDF bytes）=`fc88e0109ec074c625f255883ac9980785248edffb2a75264a721330f8a2a14e`。沒有共用原文材料。本輪既有單題兩處歷史 QA flags 皆為 PASS、零來源 issues，表示較適合優先獨立核查，**不等於本人已做原始像素的獨立 QA，也非最終官答確認**。`batch.json` 還有五個完整候選 JSON file SHA256，任何改變必須重算並使 E/UI 憑證失效。

## 必須保留的個別風險與差異
- **會計 Q21 台帳版本不一致（新增隔離）**：唯一 PR30 歷史 `source.questionRevision=817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9`，而對最新版與 PR35 原始 Q21 題幹、A-D、WebP SHA 重新計算的作者 sourceTextRevision 為 `f04f7633507952b782104985f921fa596bace3616a3d725e0eabb1f24ae394ed`。GitHub 逐字比較 PR35、PR64 及原 QA branch 的 Q21 題幹/四選項/原圖 SHA **完全相同**，故本輪尚不能判定是台帳產生演算法差異還是原文歷史訂版錯誤；C 已在 Q21 JSON 留 `coordinatorLedgerPriorRevisionMatchesCurrentSource=false` 與額外 `Q21_..._RECONCILIATION_REQUIRED` 阻塞，**請 A／MASTER 查證**，未修正不得把舊 E/UI 證明套到新 revision。
- **會計 Q17 台灣教材用語/準則風險**：教材「買入設備以最大可取得現金折扣後淨額列成本；未享差額為營業外支出」是本題考法，D 作候選。但 IAS 20 政府土地補助須按合理確信條件認列，不是事後所有條件完成才認；資產分類及其他不同準則可能有例外。附 <https://www.ifrs.org/issued-standards/list-of-standards/ias-20-accounting-for-government-grants-and-disclosure-of-government-assistance/> 背景供 E 對照，不能宣稱它就是官方統測答案核對。
- **會計 Q11 年底報銷未撥補**：可於次期撥補，不能把同一張憑證再認費用一次。財會諮詢正式文章 <https://0800280280.sme.gov.tw/accounting/run.php?file=detail&id=329&name=kw> 支持期末結帳與次期回補之區分；來源例證仍不替代官方題目圖片與答案公告。

## 每題排除發佈的硬門檻
1. **A**：用官方原圖 PDF 及原像素 WebP 自己核對題號、完整四選項、原圖/原頁 SHA、已發布最終答案影像及適用更正公告；提供真的逐題 evidence SHA。五題 `answerVerified=false`, `questionVerified=false` 原封不動。Q21 ledger revision 必須與 MASTER 合作消除來源歷史差異（不任意讓 hash 相等）。
2. **E（與 C 不同作者）**：獨立驗算 Q13 計算、Q21 借貸和前期錯誤、Q17 PPE 特殊折扣，逐一實質核驗所有 A–D 理由、教學與官答證據；附真實 E reviewer/session、當前 sourceRevision、單題 WebP SHA、teachingDigest、官方最終答案SHA、具體審查筆記，不能由 C 自批。
3. **D**：原 35 題 Demo **會計學對應樣式**，同版本教學及來源 digest 進行 8 種實機視窗 × 深淺 2 色、選題、圖片、選項作答、完整計算、無計算隱藏、答錯複習、RWD/手機操作。PR #62 非計算 UI 修復尚需獨立 UIQA，不能沿用對舊資料的簽收。
4. **MASTER**：在保護 main 的正式 PR CI 與 AI-E可信憑證 policy gate 真正上線後，才可逐題 STAGE→READY→main→Pages→`LIVE_VERIFIED` 同 SHA。此 Draft PR 自己不部署，**新增 READY=0、STAGED=0、main=0、LIVE=0**。若任一題解答/選項存在爭議，僅該題 QUARANTINED，其餘繼續驗收。

## 獨立作者測試／限制
新 `tests/test_115_role_c_acc01_11_13_17_21.py` 使用 Python `unittest` 真正讀本資料，驗證每一完整 JSON+source+image+teaching SHA、四選項高職及國小解說、分級字詞、概念重點，Q13用 `fractions.Fraction` 反推4月與所有候選日、Q21前期借貸額與 direction，另外測原題文字／四選項／圖 SHA／教學記憶內容任一改動則 hash 不符、不得自批及不得提前 READY。單獨 read-only GitHub Actions 工作流只檢作者結構／算式，不代表 A 原卷、E 審查、D 真實瀏覽器或 LIVE PASS。若 CI 初次失敗，保留失敗 run 與根因；不得刪除斷言求綠燈。
