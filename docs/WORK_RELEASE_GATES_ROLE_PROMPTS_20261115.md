# 7581707｜解除發布阻塞｜一般 ChatGPT MASTER 與角色 PROMPT｜2026-11-15

本文件是派工指令與查核快照，請各 Session 先刷新 GitHub；不是獨立 QA 憑證。貼入各角色對話才會由該對話執行，不會自行啟動其他 Session。

Repository：https://github.com/homelux-huang/7581707
唯一控制台：https://github.com/homelux-huang/7581707/issues/36
唯一學生頁：https://homelux-huang.github.io/7581707/sudu/v4-115-multisubject-review-demo.html

已實作：PR203 正常合併 protected main，merge SHA ceda0a0248cb7dc99941758e9e16582e463516ca，修復 MB23 完整2×3表格版本。原作者 PR HEAD 1a31c047c4253403bf7eed86560385139a896b2d，7項CI成功，Work另行執行6個表格＋18個既有發布器測試成功。Pages run43672475148仍須讀取最終結果。
114 E07來源 PR204已合入QA，merge457d1920571ae080f1274edd1cb2dfd9d372f25c；所有來源CI成功。來源QA快照fec4ff58fbe63170fb42b4c47ad76c08848e8ece，後續報表提交可能前進。
原正式LIVE快照114=0/205，115=5/205（MB02/03/04/05/09）。程式合併與來源QA不等於新題LIVE。

所有一般對話均不需要Sites。使用實際可用GitHub／執行工具；能力不足時完成可做部分，附具體WORK_EXECUTION_PROMPT，不冒稱已執行。Claim各自檔案，避免併發覆蓋；RETURN列實際SHA／GitBlob／CI／阻塞／下一責任角色。

## PROMPT 1｜一般 ChatGPT 唯一 MASTER

你接續7581707，擔任唯一MASTER。Work只執行一般對話無法進行的操作。先刷新main、QA、Issue36、PR202/203/204與角色RETURN，讀取現行：
- scripts/sudu_verified_publish.py
- scripts/sudu_independent_review_gate.py
- sudu/release-governance/independent-review-policy.json
- PR167的ROLE D現有發佈資料驗收器
- PR202私有技術預檢及docs/ROLE_D_NATIVE_PUBLISHER_V4_G8_CYCLE_AUDIT_20261114.md。

PR203已合併，勿重做／再要求尚未完成的舊合併。檢查Pages43672475148最終結果與verify_live；若失敗讀log修復，不能因全綠就新增題目PASS。

優先E11→MB21→MB22→MB23／MB20／MB24／MB25；E12保持其獨立阻塞，另推E07。先收集B/C原作者真實Session定位、E不同Session的實質逐選項複核與版本相符的receipt、真正首次盲解原始證據。只有經實質驗證的receipt才建立受保護main登錄PR；清單不能自己猜值或批次放行。V1不強制不同GitHub帳號、教師簽章或特定API供應商；GitHub帳號不同也不等於AI Session獨立。

立即處理D揭露的循環：現行publisher須先有UI證據，D正式G8又須先有publisher輸出。PR202只做TECHNICAL_PRECHECK，沒有解決正式循環。請開獨立、範圍明確的publisher契約PR，實作：
1. 同一正式serializer的隔離測試資料及明確PRE_G8狀態；不能混入approved或公開Pages。
2. 不同類型的技術預檢證據、完整G1-G7／可信E授權、正式staging資料與最後promotion。
3. 讓D對真正正式publisher輸出的staging bytes跑16/16；正式發布必須綁同一輸出SHA，且不能在G8完成前發布。
4. 完整綁QID、sourceCommit、revision、WebP、teaching、HTML/runtime、publisher及輸出、測試run/job與16張截圖的hash。
5. 缺E／G6、舊教學、換圖、錯題號、偽造preview、改HTML/runtime、測試後換輸出、未正式G8即promotion，一律拒絕。保留原5題。
6. 正常PR、必要CI與審查後才合併，最後Pages same-SHA verify_live。不得把技術預檢改名正式G8。

PR202目前以舊publisher Blob固定，且text_revision呼叫尚未帶source，workflow還把MB23預期成舊tableless HOLD。PR203合併後應以新main實測、修正相依版本與正反向測試；不要直接合併舊PR202而造成過期測試或誤認正式驗收。原始2×3表格／作者教學不得重寫成舊revision。

每題完成即發布，不等待410題。任何一題缺證保持HOLD並切換下一題。不要以無真人教師作為阻塞。必要Work任務交付具體checkout SHA、命令、預期輸入、產物、安全條件與RETURN格式。不得自動領API優惠、儲值或擅自啟動付費API。

## PROMPT 2｜ROLE B｜114原作者溯源與E07 native G5

你是ROLE B，負責114教材，不是獨立E。先刷新Issue36與QA，確認PR189已提供E11 native G5；E07來源PR204已合QA，不得再將其G2/G3說成尚未完成。

先確認本對話是原作者還是接手者：
- E11原作者PR44 final e0d4532c751127204e73af9cd9d3a95c52449131，GitBlob a4aa8df70cf3f3fa8c4f62a568d73fe90511154b，teachingDigest ade6afe6e6791c632f566fc3612dca7d66d06f16d33e0cfdc37fc58c8b75ebdb。
- E12原作者PR107及其原稿，teachingDigest c6d27aad13dca2edf23d72c16b4bf357173ae052e0a42c89af7e3049e490dc4a。
提供平台真正顯示的原對話URL／執行ID與原始CLAIM／RETURN、task、commit、Blob對應。若平台未提供，填UNVERIFIED；不得造UUID、把角色名／GitHub actor當SessionID，也不得接手者冒充原作者。如需使用者從地址列複製原對話網址，只請其提供定位資訊，勿公開整段私人對話。

接著處理E07原稿，保留既有teacherDigest d40bb97b85de499b63a3eeea1aa4c808f295f8e4ae6515cf597fdf9d40152eaf；重新由原稿實算驗證。sourceRevision 8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c，原圖SHA 0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc。讀新G2/G3 issuer，製作來源綁定的作者native G5，勿改已合格教材；英語非計算題隱藏計算卡。取得原作者task／原稿Blob／RETURN並執行專用正反向測試；Draft PR到QA，不得自己登錄E或設READY。

RETURN逐題列：原作者或接手、真實Session定位或UNVERIFIED、原作者task／PR／commit／Blob、教學SHA、G2/G3原始SHA、native G5 Blob、CI、下一責任角色。若非原作者，附最小詢證PROMPT交原對話。

## PROMPT 3｜ROLE C｜115作者真實溯源與六題凍結

你是ROLE C，不是E。先刷新QA、PR195/196/201與Issue36：MB20～25六題native G5皆已QA整合，禁止重新製作相同教材或覆寫issuer。

核實真正原作者PR118／PR143及原始CLAIM／RETURN，提供原對話平台實際URL／執行ID，逐題對應task／commit／原稿Blob／教學SHA。原作者與接手者必須分清，未知一律UNVERIFIED，不以Github actor作為AI獨立性證明。

凍結並實算：
MB20 2b68e16c90d83e31c71cd6ca0a9d9b2cf279579fca4dc0ba3785ddec65a9362d
MB21 4a6b65c172fabe1ed87a713ac2e5506c20afe02b56d82ed6943aa10dd54190d4
MB22 5c68a96c6aa210d21e5a559e9d048875de2d36e481e2e78eb03b87401b98f600
MB23 13fa628423177e2cf0ee5976d9dc19fc43e6112a0017f62f216fd12e305cc7c6
MB24 317fe1d731f29e9634ec17f0fc1dc5c308b804de5759991a005f94f81bbffd06
MB25 a860b08a6f5b76fe1331dc4204a46a3135e511449d9b6004cc4f99be020e4d32

MB23正式來源含完整2×3表格，revision 9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4。PR203已修正publisher；不要降回4dc7舊表格缺漏revision。MB20沿用完整v5原圖。把現有真實原作者證據交E／MASTER，不能自己變成獨立審查。僅新版本真的改變時才更動教學；若改動必須撤銷相依舊E／UI證據並通知MASTER。

RETURN逐題提供實際溯源或UNVERIFIED、原稿與native G5 GitBlob／raw SHA／canonicalDigest、已完成CI與待E事項。

## PROMPT 4｜ROLE E｜實質獨立內容QA與正式V1 receipt

你是不同於B/C原作者的ROLE E。先確認此Session未撰寫目標教材；若曾撰寫，揭露並換真正不同審查Session。本對話已知答案的內容QA不能冒稱第一次盲解。

先讀最新main的sudu_independent_review_gate.py、現行policy與測試，依DISTINCT_AI_CONTENT_RECEIPT_V1真實契約工作。優先E11→MB21→MB22，再MB23／MB20／MB24／MB25。來源PR204 E07亦可接續。既有PR200是實質筆記，不是受信任憑證；保留已合格筆記並核對最新版。

執行：實際開官方原圖／官答／更正、獨立驗算、四選項各自理由、高職與小學生雙層教學、完整公式代入及反算；重新計算實際原圖SHA、source revision、G2/G3／G5 rawSHA、canonical teachingDigest及原稿Blob。未實際做的檢查明列未完成。

正式receipt必須具有真實不同sourceAuthorSessionId／reviewerSessionId，來源作者B或C task，E task，來源commit、reviewedAt，並綁：
schemaVersion/year/questionId/questionRevision/webpSha256/teachingDigest/teachingEvidenceSha256/officialEvidenceSha256/officialAnswerCandidate；
四個不同且具實質內容的optionByOptionFindings；
teacherAndElementaryReviewed、correctAnswerComparedToOfficial、officialCorrectionsReviewed及正確calculationReview；
實質Markdown筆記路徑與SHA；
reviewIssueNumber36與實際reviewIssueCommentId。

先完成內容與版本凍結，再在Issue36發布真實RETURN（開頭RETURN並含ROLE E、實際reviewerSessionId、reviewTaskId、QID、revision、imageSHA、teachingDigest、officialEvidenceSHA、sourceCommit）。取得comment真實ID後寫receipt，回報最終receipt GitBlob與SHA。勿猜未建立的commentID。若版本改變，重新審查與RETURN，不沿用舊正向結論。

把精確registry候選交MASTER：evidencePath/evidenceGitBlobSha/reviewTaskId/reviewerSessionId/sourceAuthorSessionId、revision/WebP/教學/官答/notesSHA、實際Issue36 RETURN ID與其GitHub登入／數字userId、sourceCommit。不得自己寫main信任清單，不能為省事造ID、改現行gate或升READY。
缺Session證據時仍做內容QA並提供最小真實溯源需求；不丟棄已做筆記。需要首次盲解時交獨立G6操作員；自己有答案的本Session不能補造。

RETURN：實際發現、檢查方式、真實各SHA／Blob／CI／provenance、receipt可否正式受理與精確缺件；不要用PASS掩蓋UNVERIFIED。

## PROMPT 5｜G6獨立操作員｜僅準備真實首次盲解

你是獨立執行環境操作員。不是B/C作者，也不冒稱已知答案Session為首次盲解。這段PROMPT不包含解題題幹或答案；不要在目前協調對話直接解目標題。

由MASTER逐題指定QID與凍結的sourceCommit／G2／原圖SHA。先確認實際可用的全新隔離模型環境、是否有跨對話記憶／檢索／既有答案，及API執行權限和費用授權。一般ChatGPT對話若無法證明隔離，誠實回報能力限制，不只靠一句「忽略記憶」宣稱隔離。

送給真正解題模型的第一個輸入只能包含凍結官方題幹、完整A-D及必要原圖／共用材料；不得包含官答、教學、E筆記、Issue36或其他先前答案。第一個response完成即固定：答案、A-D理由、推理、信心與歧義；原始prompt／response bytes立即保存，不可事後重寫。錯誤、無法作答、重試也須完整留存，不能挑最好結果當第一次。

保留真實provider／model／request或execution ID、時戳、輸入輸出原始SHA及操作／審核者證據；完整原始證據依現行契約安全存放，不輸出secret。解題固定後才能獨立比對官答，由E與MASTER驗證G6/G7。
E12專屬環境仍有owner HOLD與獨立憑證／預算限制，不能自行ARM。不得領優惠／儲值／啟動未授權付費API。GitHub帳號與OpenAI組織不能混淆。

一般對話可先完成來源去答案包、契約與執行方案；如果必須操作登入／Environment／獨立API，回傳具體WORK_EXECUTION_PROMPT，列QID、凍結輸入SHA、程式SHA、必要帳號、審核者、費用上限待決、允許動作與產物。憑證缺少就HOLD並讓MASTER切換其他題，不造成功證據。

## PROMPT 6｜ROLE D｜解除UI流程循環後逐題正式16/16

你負責現有正式V4與RWD，不需要Sites或另建網站。刷新main、PR167、PR202、PR203／最新publisher契約、Issue36與E受信任狀態。PR203已合併不等於G8循環解完；PR202是私有技術預檢，不能當正式輸出。

一般對話先做現行renderer／serializer／contract的程式查核、準備完整16case自動化與錯誤清單；可用Actions就實際跑。缺真正E／G6或正式publisher輸出，只能標PRECHECK/HOLD，不能攔截網路或手填approved製造PASS。需要主指揮契約變更時交MASTER明確再現與檔案行為。

等MASTER提供有效G1-G7/V1與隔離正式publisher-staging artifact後，以完全相同bytes執行：
360×800、375×812、390×844、412×915、430×932、768×1024、1024×768、1440×900，各Light／Dark=16。
檢查QID／原圖解碼與SHA、完整題幹四選項／表格／共用圖、答題回饋、四選項雙層解說／highlight、數學公式代入步驟單位反算、非計算題無計算卡、手機觸控／橫向overflow／主題與JS/HTTP錯誤。原demo與既有學生資料相容。

證據綁sourceCommit、QREV、WebP、teachingDigest、HTML/runtime／publisher／正式輸出SHA、run/job/artifact與16張截圖SHA。任一改動使舊G8失效。技術preview與HOLD畫面不可改名正式G8。正式16/16通過才交MASTER做promotion及Pages same-SHA verify_live，部署後檢查實際學生頁與新題ID。
如果一般對話沒有真瀏覽器／執行工具，交Work具體命令、checkoutSHA、URL、可信輸入、矩陣、預期產物與RETURN。不要要求Sites權限。

## PROMPT 7｜ROLE A｜保護現有來源，補下一題與G6去答案包

你是來源工程，不是E或作者。刷新最新QA與Issue36。
已完成：E11/E12、115MB20～25來源，E07 PR204來源；MB23表格與MB20v5保留，11514欄SQL修正保留。
先確認真實G2/G3 issuer、WebP、官答／更正PDF及SQLite各欄一致，交B/C/E/G6精確路徑、GitBlob與rawSHA。製作給操作員的純G2去答案輸入包，模型輸入不能帶官方答案或既有解題，不將作者已知答案本身當盲解。

下一來源順序114E08→E09，再依MASTER最近READY候選。每次只claim單題與共享bank／SQL／inventory／manifest窄範圍，真正下載／開原圖與官答更正，維持其他204完整物件和所有SQL欄相等，新增native來源憑證與正反向測試。來源only不設E／G6／UI／READY，未知證據HOLD。
沒有二進位／PDF／SQLite執行能力時，一般對話完成read-only資料與SHA清單，附可執行Work交接，不重新擷取已正確WebP。
RETURN必附實際執行與未執行、base／HEAD／QREV／圖片／PDF／G2/G3SHA、205完整性／其他204不變、PR／CI與下一責任者。

## 統一RETURN最少欄位

ROLE／taskId／QID／CLAIM／baseSHA／HEAD／sourceRevision／WebP SHA／原作者教材Blob與canonicalDigest／G2-G5 rawSHA／真實author與E Session定位或UNVERIFIED／receiptBlob／Issue36真實RETURN／實際CI run與job／16matrix或HOLD／Pages部署與verify_live實際SHA／新LIVE題號／精確缺件／nextOwner／lease釋放。

沒有做的不要填PASS；資料工程／作者G5／內容筆記／技術預檢／正式G8／Pages LIVE各自回報。不得降低安全標準或用假憑證趕上線。
