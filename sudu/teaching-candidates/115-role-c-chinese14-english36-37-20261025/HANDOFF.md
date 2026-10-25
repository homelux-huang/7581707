# 7581707 / Role C｜115 國文14、英文36／37 逐題雙層教學候選交接

## Claim / immutable base / scope
- Task `C-115-C14-E36-E37-20261025-06`, Role C GPT-6 AI 115年教學**作者**，非教師身分、非不同作者 AI 複核角色 E。Issue36 認領 https://github.com/homelux-huang/7581707/issues/36#issuecomment-6393915658；GitHub 伺服器 `created_at=2026-10-25T05:27:53Z`。
- Branch `teaching/115-role-c-chinese14-english36-37-20261025`; baseSHA `3c696903ac5b089f355885c98ab71a74cb79dced`（Role C 第五批 PR55 HEAD，該 SHA 的 push/PR 7 測試 CI 均成功）。固定 PR35 115 資料來源 HEAD `e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5`、questions Git blob `216bc43d57501bc1c3e5842b48413a8967456cda`、manifest Git blob `2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b`、PR30 唯一台帳 blob `3e2f07f8b9e1c6cd64ec18d50d27b868a1c5cfb6`。三題原台帳 teachingDraft 全部 NOT_DELIVERED，認領時全 Issue 沒有其他 role 對相同題號認領。
- 最新使用者政策：**「高職老師」只表示教學角度，不需真人教師資格、簽章、真人 GitHub APPROVED**；保留不同作者具名可追溯 AI 實質複核、官方來源/最終答案與更正公告、圖片 SHA、原文引句、完整四選項與實際 V4 8 裝置×2主題、CI 和唯一主指揮發布。原 C PR48 已將作者候選 metadata 改成待獨立 AI，不重做它。MASTER PR46 的新 AI 審查契約目前仍是**未接入發布器**的 Draft，不能視作已解除其他 QA gate。
- 本批僅新增專屬 C JSON ×3、精確 digest `batch.json`、`HANDOFF.md`、自己 Python tests 與 read-only workflow；沒有修改既有教學、A 原圖、B 年度、D UI、E 稽核、協作台帳、正式發佈器、main 或 Pages。

## 三題教學與版本
| ID | 候選答案 | Source revision | Individual WebP SHA | Teaching canonical SHA |
|---|---|---|---|---|
| 115-00-C-14 | B | `9ccbc09172a045f72a02940c61fbdce3762243a58ce424c632302cd08610a896` | `2d5d49607eb941df0f6ed272447a312723bfbf050555f53deb1e0cd675a1888e` | `6bafd4e64ab792babd902cbc079607ec1f49ad9c7b44237eb3b455a36f52a270` |
| 115-00-E-36 | D | `2a5ef83ac4daab27e63dc520087f259e4dc312dc5242fdd8cd62ae4053a771a0` | `eaae0a20b815d0b416ee5318c3c65446ba6a250227761390c4fa7e676baed245` | `4b8bb1718d949f6cc7994b002eb7064c549255ce6bdce746960e55ac772f4ab8` |
| 115-00-E-37 | D | `71604bd6b778c214db6075e841ed9890447ecd3653388e89974c82328db67701` | `072c60f80d8cb8a69df5de3aa222e22ca0fe057f0d2c08b608dafcde7cbeed53` | `23add6c41c44f27332c6091227ad6c2eebcd52142f801079f7b151140b4398e1` |

三題的每個 A、B、C、D 選項均有**高職角度正解/誤解原因**、**國小口語解說**及**原篇章具體引用片段**，搭配一眼記住、觀念、逐步推理、題幹與選項區重點 `**bold**`／`highlights`。英文另外有發音 IPA、初級/中級/高級同義／相反相關詞、近三年官方公開時事英句及中文翻譯，實際字詞的前後 `**highlight**` 對得上。**三題均非算式題**：`hasExamCalculation=false`、`examCalculation=null`，交 D 按原 35-Demo 科目 V4 自動隱藏計算框。

## 原始共用材料、來源差異與科學措辭
- C14 的甲乙文本共用 `115-00-C-SHARED-11-15` 原始像素 WebP SHA `bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66`，全文+此圖 revision `9d0735b8c397d8a9c384410e13eb5b83e60b32becd5022cc5f6c69092c08d18f`。**QA=PENDING_INDIVIDUAL_VISUAL_QA**。另外題幹有「第一人稱／第三人稱全知」兩欄圖表，**需要 A 實際逐行對官方表格原圖核對，純文字重排不算原圖已 QA**。q.questionVerified=false，歷史 q.answerVerified=true 不等於可放行；單題 q.assets.visualQa 仍 PENDING 而 manifest C14 個圖 QA PASS 不該透過批次默默抹平。
- E36/E37 的共用 `115-00-E-SHARED-36-38` 原始像素 WebP SHA `180430801f1b7c0775f2ff360c80d0b8d1828e26b95742ca52f57e72c5f4e418`、原文+圖 revision `d8ebd1565ed82e09a3022f80a088201fb32010901d8e6686c22cfbf8c8b617c5`，同樣 `QA=PENDING_INDIVIDUAL_VISUAL_QA`。英文單題 manifest QA PASS 為歷史候選；兩題 q.questionVerified=false，q.answerVerified=false。此作者**沒有親眼檢查或重新雜湊原始 WebP/PDF 二進位，也沒有重新查正式官方答案影像**；記錄的 SHA 由來源 manifest 而來。
- 英文閱讀是在問文章對 Jonathan Haidt 說法的**篇章結論與文中主張**。為避免向學生錯誤宣稱強因果，特意區分新聞科學延伸：2025年6月 UNICEF Innocenti《Childhood in a Digital World》指出 **screen time alone 沒有明確直接造成心理健康問題的證據**，傷害經驗、網路霸凌等因素有較明顯關聯。官方資訊 https://www.unicef.org/innocenti/reports/childhood-digital-world 。E37 `anxiety` 的時事例句按其原意自行改寫，標示**非來源逐字引述**；沒有宣稱每個使用手機的人必然焦慮。
- E36 `outdoor play` 時事例句，取自 UNICEF 歐洲暨中亞區域 2025-05-01《The importance of outdoor play (and how to support it)》 https://www.unicef.org/eca/stories/importance-outdoor-play-and-how-support-it ，支持戶外遊戲對兒童學習、身心與情緒發展的重要性。英中例句是**作者自己的教學改寫**，且醒目重點詞形真的出現。
- 無虛構教科書版次／頁碼；所有 answerCandidate 已知才著手解釋，**不冒稱盲解、真人教師或不同作者 E 審查**。

## 後續獨立收件與阻塞
1. A 逐題與共用原始圖片直接對官方 PDF 的圖表與閱讀材料，確定 C14 的第一人稱/第三人稱對照表完好，E36/E37 的共享閱讀未缺頁、不混題，核對 115 最終官方答案及更正公告 SHA；必要校正須帶版本重算 source/image/teaching SHA，不能私改 QA 狀態。
2. E 不同作者 AI 需獨立確認 C14 **B為不適當敘述** 的敘事觀點證據，E36/E37 四項理由和 passage factual/cause 的用字，以及時事來源真的支持文句。須留下真實 reviewer 身分、sourceRevision／sharedImageSha／teachingDigest／官方證據SHA 與每題具體複核理由；不能由 C 作者自批。
3. D 原 35題 Demo 的國文/英文 V4；在 8 種螢幕×深/淺兩主題檢查真實題號/單題原圖與共享材料、hover、四選項、正解白話、高亮字詞、英文新聞英中翻譯、沒計算時隱藏、同來源/教學SHA和無截斷。
4. MASTER 確認 PR46 AI policy/publisher 整合不留真人教師隱性阻擋，完整收件與獨立稽核合格題才增量發布 main/Pages，依相同 SHA 驗證 LIVE。此批 **新增 READY 0、LIVE 0**，`studentReleaseApproved=false`，`deploy=false`。

`batch.json` 記錄完整 JSON SHA256、sourceTextRevision、individual 原圖 SHA、原始共享圖全文 SHA 與 teaching canonical SHA；獨立 Role C-only Python 測試含防篡改負測、四選項兩層完整性、E36/37 UNICEF 例句實際高亮、C14 表格文字存在、無計算自隱、共用原圖與 E QA PENDING、無批准/部署。Tests 就算通過只代表資料工程一致性，不能替代真正來源、AI、UI、LIVE 複核。
