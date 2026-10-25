# 7581707｜Role B 114年國文15、23題／英文10、15、20題原圖暫抄教學草稿（NO RELEASE）

本批 Task `B-114-C15-C23-E10-E15-E20-IMGTRANS-20261025-08`：Issue36 [CLAIM](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6394078700)，GitHub 官方 claimedAt `2026-10-25T05:48:35Z`；唯一 B-owned branch `teaching/114-role-b-loop-batch06-20261025` base `4e8b3065d7f1b0e71eba0928a6f5fe002ea25852`（承接 PR60），不改 main、來源 A、原題/WebP/SQLite/UI/發布程式、其他B1～B5或PR30唯一正式台帳。

**已實際讀取單題原始 WebP 像素**：英文E10、E15、E20，國文C15、C23皆為本題完整題幹與A～D；manifest `qaStatus=PASS`，既有舊QA證據實體依 SHA 可讀。這是 **G1 圖像影像QA歷史繼承**，不是本次 A 的 G2 官方 OCR 文字校正，也不是官方答案或公告的最終逐題驗收。五題原 `questions.json` 仍全部有 `last_on_page_check_possible_continuation_or_footer`，不得在本批消除 issue/設新的 questionVerified/answerVerified/READY。

## 原圖逐字抄寫 vs OCR 汙染（不可冒充正式校正）
候選 JSON `options` 完整保留官方資料處理層的**含污染原值**，`imageTranscribedOptions` 是作者比對單題 WebP 後額外製作的 **供角色 A 核對的草稿**。兩個版本並存；由 A 逐字核 original PDF + 圖表/選項，校正原始 canonical source and DB 後，**所有涉及 sourceRevision 的教學/證據/舊UI 必須以新SHA重新綁定**，不得把作者暫抄作來源 QA PASS。 `sourceRevision` hash 為 SHA256(canonical JSON of {question, options, singleQuestionWebpSha256})、`sourceImageTranscriptSha256` hash 為同一 schema 但換 `imageTranscribedOptions`；`composedTeachingSha256` 同時包含兩 revision、原 WebP SHA、teaching 及 enrichment。每份來源與教材實檔 SHA 見 batch.json。

- 英文10/15/20：原OCR四選項 **D** 後混入頁碼、下一頁頁首；英文20甚至附到下一篇21～24題文章。原單題圖 D 完整，作者版本只保留該選項。
- 國文15：原OCR第四選項D後混入下一頁16～19長篇閱讀，且原文是雙欄選項表。作者在 `imageTranscribedOptions` 以「／」分欄列出 A～D，尚未取代 canonical 表格原像素。
- 國文23：四選項的來源字串與原圖暫抄相同，但先前 `last_on_page_check_possible_continuation_or_footer` 未由角色A正式 G2 消案，不能因圖像完整就擅自取消。共享原像素 `114-00-C-SHARED-20-23` WebP SHA `7b7f592f01378a6fa9ece08d87291810420479c9529f2d5233f10ad458c47f8a` 沿用既有原QA、SHA 綁到教學 enrichment；不重裁。

## 教學與來源補充
- 英文10 C abandon = give up（放棄）；英文15 A dress properly（穿著得體）；英文20 B came up with it first?（那是誰最早想出來？），**E20愛迪生和戴維的說法僅是題中角色對網路文章的轉述**，不冒稱嚴格科技史結論。
- 英文詞彙每題初級/中級/高級，同義/相反意思、詞義用法；Cambridge 查核原形音標：abandon `/əˈbæn.dən/`、properly US `/ˈprɑː.pɚ.li/`、invent `/ɪnˈvent/`。無外部直接口音來源的片語 ipa=null，不虛構字典整句錄音。近三年自編中英對照新聞例句及正確字詞高亮，原報導 URL/年份在各稿，**新聞英文不是原文逐字引述**：2024/07/02 WHO 戒菸指引；2026 AP 面試衣著；2025/06/03 MIT 減少3D列印廢料技術。
- 國文15 B：『威寡者，則下侵上』《韓非子》字面係威信不足恐下位者冒犯，藉以讀官員執著維持威權的心態，不是「仗勢欺負弱者」；『刑罰不中，則民無所措手足』《論語》原義批評刑罰失當，使人民無所適從。官員心態分析不是合理化濫權。國文23 D：由旦視暮撫→去而復顧→甚者爪膚搖本，遞進程度與焦怒→焦愈怒一致。
- 每題有高職老師**角度**與國小口語、全A～D四選項各別推理、三步以上解法、一眼記住、原題 literal 安全 highlight；非計算題 `hasExamCalculation=false` + `examCalculation=null` 不顯示計算欄。無教師資格、簽章、真人 GitHub APPROVED 前置；也不虛構教材版次章節頁碼。

## 角色分離及驗收阻塞
1. 角色 A 針對五題 G2/OCR+表格與 G3 官方最終答覆、更正公告，完成新 sourceRevision/SQLite 一致，作者 B 依新 SHA 重新綁定教學；
2. 不同作者 E 完成來源與**教學A～D實質**雙層查核（含古文語義、新聞來源、正誤），附真實 review notes/可信 receipt；
3. D 真正將相同原圖+正確 sourceRevision/teachingDigest 接入七科 V4 35題Demo同規格，在8尺寸×深淺主題下驗收；
4. 唯一 MASTER 整合舊PR鏈，PR57 AI E gate 仍是 Draft，直到實際安全合併與現有 checks+LIVE 同SHA驗證，不可自認已上線。
目前5/5皆 `BLOCKED`，新增READY/main/LIVE = **0**；作者自我技術CI只證明可重現的未發布草稿，不代替來源和獨立審查。
