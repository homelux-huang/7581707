# ROLE E｜114-00-E-07｜原始來源與獨立實質內容審查｜2026-11-15

- **Task:** `E-114-E07-SUBSTANTIVE-NOTES-V1-HOLD-20261115-01`
- **CLAIM:** Issue #36 [#6889695295](https://github.com/homelux-huang/7581707/issues/36#issuecomment-6889695295)
- **範圍:** 本對話之前只撰寫其他題號 E11、MB20–25 的 ROLE E 審查筆記，**沒有編寫、重寫或實際生成 E07 原 ROLE B 教材**；但 ChatGPT 平台真實 `reviewerSessionId` 和 B 原作者 `sourceAuthorSessionId` 均無法從本對話/ GitHub 客觀驗證，因此 `UNVERIFIED`。不能假稱已獲 V1 正式可信身分。本輪已讀官方答案，**不能冒稱 G6 首次盲解**。
- **Verified ref at start:** QA `97a68061c863c5b609586915deb0cb04f8f56af0`；protected main `ceda0a0248cb7dc99941758e9e16582e463516ca`；B author-only Draft PR207 HEAD `16c1dc1a22cfe62e3132d38a97c9614f19e5e521`，待 MASTER 負責合併，E 不觸碰 B 作者分支。
- **Policy:** `DISTINCT_AI_CONTENT_RECEIPT_V1`，protected policy GitBlob `c77ee2ec8ca1381388fbbbe6bd36e679750678eb`，`trustedAiReviewReceipts={}`；gate GitBlob `3ade3389910dba3f0ee795539cab9367d3bb215a`，publisher GitBlob `d410b10ff75ff7bfbb465098b0c2e5dd5b104978`。目前 E07 沒有可信 registry／獨立 Session 證據。

## 1. 原始 G1/G2/G3 與 SHA／GitBlob 核對

直接以 GitHub connector 讀取原始單題 WebP base64，解碼後重新計算 SHA256，並開圖逐像素視覺確認完整題幹、題號7與 A～D；另直接打開 114 4-00-E 公告答案第一頁 WebP，表格第7題為 A。原始試卷整份 PDF、答案 PDF 與更正公告整份 PDF **本輪沒有再次下載/重新雜湊**；採用 ROLE A/Work PR204 已留存的官方 PDF 原始 bytes / 公告全頁驗證，以及目前 G3 精確紀錄。更正只涉及 E26，**不影響 E07**。

- **QID:** `114-00-E-07`; year 114；官方答案 **A**。
- **Original question:** `During the night, the sensor lights in the park will              turn on by themselves when\n   someone is passing by.`
- **Original choices:** A automatically；B organically；C productively；D selfishly。原圖和 G2 逐字/字義對應，無鄰題污染。
- **WebP path:** `sudu/data/processed/114/webp-v1/00-E/114-00-E-07.webp`
- **WebP raw SHA256 (本輪重新計算):** `0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc`
- **WebP Git Blob:** `f7017cb2c5ba750c7c05b959d3d59016945d039f`
- **sourceRevision (本輪以 question/options/WebP SHA sorted canonical JSON 重新計算):** `8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c`
- **G2 issuer:** `sudu/data/processed/114/review-evidence/114-00-E-07-ocr-publisher-20261115.json`
- **G2 raw SHA256 (本輪重新計算):** `ecc2fd5e4dca51185a008d978a9dcdae9e5feeedaa0512f9841a35e764bfe2b0`；GitBlob `0f15f815042afd2520144343db6b75ef2e7dbe32`
- **G3 issuer:** `sudu/data/processed/114/review-evidence/114-00-E-07-official-publisher-20261115.json`
- **G3 raw SHA256 (本輪重新計算):** `f5519fa817883f0d6cc97ee4bb9e3ba47c75a21f03e126d7330b266b50442303`；GitBlob `02fc841c21213dd3849adce563a4d56e4a8c2e20`
- **G3 correction:** `correctionNoticeReviewed=true`, `noCorrectionForThisQuestion=true`, `namedOfficialCorrectionQuestionIds=[114-00-E-26]`。已審官方最後答案 A；原始答案 PDF SHA（來源 A 實驗）：`ebd3940a54b7059173e1fc7add3df75b59620f7efad93cf822b3ffa72d95b325`；原始更正 PDF SHA（來源 A）：`79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc`。

## 2. 作者原稿、補充與 native G5

原作者 PR21 不可與 PR31 後續補充作者 Session 混同；兩者原始 ChatGPT execution/Session `UNVERIFIED`。本輪直接讀取兩個真實 Git Blob 內容，與 PR207 native G5 `content`、`enrichment` 結構比對，未發現文字改動。

| Evidence | GitBlob SHA1 | 本輪原始 SHA256／canonical SHA256 |
|---|---|---|
| PR21 immutable original E07 teaching | `03b1686ca549f72d1f999de5b99656273e0c1e05` | raw `3ab1f4249096ff3104e74f42f1dcc5e6a396de8df4330165fc5bb430fb5e8e1d`；canonical `d40bb97b85de499b63a3eeea1aa4c808f295f8e4ae6515cf597fdf9d40152eaf` |
| PR31 original addendum | `ac26c39ddea751ed9837edf1e6875539499fab6f` | raw `59f7bc3d4c100cad7a37a6f16e2b6a27e564a01d6e96d77af23ef9987f2731c4` |
| PR207 native G5 author-only issuer | `8ec2b0b87c916f6eb04d2852a6fab50ec04dd274` | raw `83053bdbb33b5ad6a5f92eede06f58bed64fba9eb41ef33afd96a836681ee854` |

- **Pure canonical teachingDigest** = `SHA256(canonical(nativeG5.content))` = `d40bb97b85de499b63a3eeea1aa4c808f295f8e4ae6515cf597fdf9d40152eaf`（MATCH）。
- **Composed enrichment digest** = `SHA256(canonical({questionId,sourceRevision,webpSha256,teaching:content,enrichment}))` = `f65c50e011f57025f2ffc9ff7df107f16f4bd6c6e3b1c64c75169bb77c35dd5b`（MATCH）。
- G5 `sourceAuthorSessionId=null`, `reviewerSessionId=null`, `sourceAuthorTaskId=UNVERIFIED`, `independentAiContentReviewed=false`, `studentReleaseApproved=false`，維持原樣，不由 E 重寫。

## 3. 四選項獨立語意 QA

原題 `sensor lights` 是「感應燈」，`turn on` 是「亮起／啟動」，`by themselves` 指「自己、無需人工操作」。句中的 `when someone is passing by` 明確提供觸發條件。從語意與副詞修飾動詞看，答案為 A。英文題幹已有 `by themselves`，再插入 `automatically` 有語義重複但**不影響四選一唯一最佳選項**；不能將其視為題目錯誤或改寫官方來源。

- **A automatically — 正確：** 表示不需人手啟動、由裝置自動開啟，精確呼應 `sensor lights`、`by themselves` 與行人經過時觸發。高職層次是 manner adverb 修飾片語 `turn on`；國小白話是「人走過燈就自己亮」。
- **B organically — 錯誤：** 意指有機地／自然形成地，用來描述發展、成長等；不能自然表達感應器偵測行人後自動亮燈。白話「自然長成的東西」不是「感應燈不用按就亮」。
- **C productively — 錯誤：** 意指富有產出、有效率地；不涉及是否需要人工啟動。白話「很有效率」和「自動開燈」不是同一種意思。
- **D selfishly — 錯誤：** 意指自私地，通常描述有意圖的行為或擬人化行動；普通感應燈不是出於自私而自行亮起。白話「燈不會因為自私才亮」。

原 B 教學四選項高職／國小層次均正確、四理由各不相同；原題引用和粗體 highlight `sensor lights`、`by themselves`、`automatically` 均見原始題圖（後者為 A 選項，非題幹字）；沒有憑空加入原題詞語。原 G5 `hasExamCalculation=false`、`examCalculation=null`、`formula=""`，英文非計算題不應渲染計算卡，符合要求。

## 4. 新聞、詞彙、IPA 與事實標示

- 原 B 增補詞彙 `automatically` = 自動地；與 `manually` 相反，`by itself`、`without manual control` 是相關說法，**不是所有句型都能逐字替換的詞性完全相同同義詞**（`by itself` 是片語，屬教學可接受近義）。
- IPA `/ˌɔː.təˈmæt.ɪ.kəl.i/` 發音表達合理；Cambridge 詞典網址有效性需受站方存取限制（本次查詢遭 403），因此不宣稱已取得詞典正文的逐字核對。
- 中央社 2024-09-28 原報導 [中市23處路口試辦行穿道照明 市府規劃擴大增設](https://www.cna.com.tw/news/aloc/202409280174.aspx) 已直接查閱，實際確認綠燈期間偵測到行人，照明亮起、設置23處的事實。新聞來源支持的是這個中文事件，**不是新聞英文原文**。
- PR31 的英文 `At some Taichung crossings, sensor lights automatically turn on when pedestrians cross during a green signal.` 為 **SELF_WRITTEN_NEWS_CONTEXT_EXAMPLE**、`notAnArticleQuote=true`，明確標示原創教學示例；英文合理、未錯稱為報導引文。<escape> </escape>「some crossings」也未錯說每個路口皆有照明。

## 5. V1 正向條件與失敗驗證預期（fail closed）

Protected main 的真實 `scripts/sudu_independent_review_gate.py` `separate_ai_content_receipt_verified` 需具備：完整 material exact SHA、不同且可驗證的 B sourceAuthorSessionId 與 E reviewerSessionId、真正 Issue #36 RETURN 時序和 GitHub 發文身份、notes SHA-bound、sourceCommit、四選項不同 findings、官方答案與更正檢查、protected-main registry 對 E JSON 原始 Git Blob 的批准及 audit 的 `independentAiContentEvidence`。目前 `trustedAiReviewReceipts={}` 且作者與 reviewer 真實 Session ID 均缺失，無法形成誠實的正向可信 receipt。

因此本次只交 **CONTENT_NOTES**，不建立會誤導為已受理的正向 E JSON；不能產生新 G6 first response，不能把 PR209 去答案包視為首次盲解。正式結果 `SOURCE_PASS=true, CONTENT_PASS=true, V1_RECEIPT_INADMISSIBLE=true, G6_UNVERIFIED=true, G7_UNVERIFIED=true, READY=false, LIVE=false`。

### Next owners

1. **MASTER／原 ROLE B Session**：回查 PR21／PR31 原始平台 conversation URL／真實執行 ID 與作者 Session；無即 `UNVERIFIED`。如無法核實，安排新可信不同原作者環境審查，**不得捏造 ID**。
2. **MASTER／獨立 E**：取得平台正式授權的 E Session 身分原始證明，供 V1 真實時間及證據綁定；同 GitHub 帳號不等於同 Session，也不是不同 Session 的證明。
3. **獨立 G6 操作員**：只取得 ROLE A 去答案來源包的 solver-only 文件，使用真正隔離新模型首次回覆並保存原始 bytes/provider ID/UTC/hash；本對話已知答案，不能執行這項盲解。
4. **MASTER／ROLE D**：先驗收真實 receipt，再決定正式 publisher-emitted G8/16、逐題 READY/LIVE；不因原圖、B native G5 或 E CONTENT_PASS 自動解除封鎖。
