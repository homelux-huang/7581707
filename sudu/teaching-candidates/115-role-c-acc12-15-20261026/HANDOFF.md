# Role C｜115 會計學第12、15題原始來源綁定教學候選｜2026-10-26

**Claim** https://github.com/homelux-huang/7581707/issues/36#issuecomment-6409284734，GitHub actual createdAtUTC **2026-10-26T05:56:08Z**；taskId `C-115-ACC-12-15-20261026-09`。作者 GPT‑6 Role C AI，**不是**獨立 Role E、真人老師或唯一發布 MASTER。答案候選先取得才事後推導，不是假裝事前盲解。

**Only source** Role A PR64 `b6c449629efc80d37fa2e6dbb9e680e321367c14`；questions Git Blob `0128adc3f41e748950c3f5af83fca6dd1c331f5c`、WebP manifest `2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b`。PR30 410題唯一台帳 Git Blob `2d60b3e571b18063990b9824ba1e14deee91b83b`，兩題原教學 NOT_DELIVERED、原文四選項完整、沒有共有素材、`issues=[]`、原單題 WebP 歷史 QA PASS、`answerVerified=false`、`questionVerified=false`。本批不重裁圖、不OCR、不改原卷/SQLite/主台帳/main/Pages。

**Branch** `teaching/115-role-c-acc12-15-20261026`，baseSHA 前批角色 C PR91 `75cc7dd9fbe2891da6b9e2e690034af33f1713b6`，所有檔案在本批獨有新路徑。教學均完成高職專業/國小白話、A～D 各自正誤與觀念、`**粗體**`、`highlights`、一眼記住與初級/中級/高級，待 E 獨立實質複核。

|題號|候選解答|sourceTextRevision|單題 WebP SHA256|teachingCanonicalSha256|
|---|---|---|---|---|
|115-09-2-12|A（②⑤）|`e431011f012171ed2c5786802cbb7db7dd124796b331ecea26edb4a4ff29e714`|`53fe56b7680c29c8b1da0589569f2308630b78fcaa417214c01fa7474e432cf0`|`68facef95164bcddaa876a1ddafc9bf85ac2d878c8836b87605f662627bbc6fe`|
|115-09-2-15|C（①②）|`70c519812540ee29e2fd72a1764d92aa35489a9f59688f7ad66eac55883f62be`|`6a9840a517f22334743662035ce9553f77b5ab3e062fbfe5b66766d18b6b00fb`|`ce78551604f0198195603c46d04ce98dc1610ba766b7585389a8f3f700e53ead`|

Q12 **銀行調節表無實際數值計算，examCalculation=null**：①同額仍可能有互抵未達、②銀行保付支票已保留資金/通常無一般調節、③公司調整後等銀行「調節後」而非原對帳單、④在途存款銀行側調節而非公司重新借記、⑤上月在途正常於本月銀行登列；僅②⑤正確→A。需 E 以原題會計教材檢核保付支票的特殊銀行實務前提。

Q15 **完整計算卡**：可售=200＋300－20=480件，淨銷=280－30=250，帳面應餘230，實盤210，**盤虧20件×50＝1,000元，非盤盈**；定期COGS=(480−210)×50=13,500，永續法淨銷成本250×50=12,500，加本題按正常盤虧歸屬COGS的20×50=1,000，合計13,500；期末210×50=10,500。①②對③錯，C。**必須由E核實當年度學校教材將正常盤虧併列COGS而非其他損失的科目分類**；不能把實際不尋常短少都一概稱COGS。每個計算附公式用途、代入、逐步結果、單位及驗算。

**批次完整 JSON SHA** 與逐題題目＋A-D＋原始單題圖片 SHA、teaching SHA 全記在同路徑 `batch.json`；原 09-2 PDF SHA 引用來源 manifest `fc88e0109ec074c625f255883ac9980785248edffb2a75264a721330f8a2a14e`，**C 沒有實際打開原PDF重新雜湊，也沒有自行核准官方答案**。本批不包含源圖變更；未獲 E 審查、D 真實 8 viewport×2 theme 同版 V4、MASTER 發布等必要證據。

**接手**：A逐張原圖及官方最終答案更正公告；E不同作者對 Q12 保付支票／銀行調節、Q15 盤虧入COGS與四選項作實質 AI 複核並綁原圖／來源／教學／官方SHA；D沿用原35題 Demo 會計 V4/Q12 無計算自隱/Q15 完整步驟同版8×2；MASTER僅全部通過後逐題 READY→STAGE→protected main→Pages→LIVE 相同SHA。**新增 READY/STAGED/main/LIVE = 0/0/0/0**、`studentReleaseApproved=false`、`deploy=false`，不等待其他題完成也不跳過門檻。

測試 `tests/test_115_role_c_acc12_15.py` 與獨立 read-only workflow `.github/workflows/115-role-c-acc12-15.yml` 驗完整檔與 canonical digests、全部 A–D 高職和小學雙層理由、銀行調節五項正誤、存貨數值及短少方向、文字選項圖像教學改動的負向失效、未核准 flags。**CI 通過只證明作者候選完整，絕不取代官方原圖、官答、E/D或主指揮LIVE驗收**。
