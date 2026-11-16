# 114 E08／E09／E10 來源修復與交接（NO RELEASE）

Task：WORK-A-114-E08-E10-G1G2G3-SQLITE-20261116-01。接收 ROLE A Issue36 #6908560201；CLAIM #6908591711。基準 QA `3d7645b9b8c83bd09348115118920501823b3c27`，正式 publisher main `ceda0a0248cb7dc99941758e9e16582e463516ca`／Blob `d410b10ff75ff7bfbb465098b0c2e5dd5b104978`。Draft PR 僅 target QA，不直接合併。

已重新從原官方 URL 下載 question／answer／notice PDF，逐一驗證完整原始 bytes SHA256：

|PDF|SHA256|
|---|---|
|question|1b1768452e5870d1a746f09e4d5583c7b166a2888ef632532ad4466364ff1dcf|
|answer|ebd3940a54b7059173e1fc7add3df75b59620f7efad93cf822b3ffa72d95b325|
|notice|79040d0ebfca3d4800fe63898f0b09e38151cd47c90401197af53d6cefa53cbc|

實際渲染並目視檢查原題PDF第2頁、官答第1頁與完整1頁確認公告；確認官答 E08 D、E09 D、E10 C。公告列名 E26，不能推論整份試卷無申疑。原封存官答 WebP 實際重算 SHA256 為 `a1725a12c39ad748ebc38a0dab878836f59be4352da3fffa10d3cecb6a07d863`。

E08／E09 的題幹與四選項不改；E09 原圖下劃線 Apparently、E10 abandon 保留。E10 原圖選項 D 只有 `run into`；刪除 canonical D 選項附帶的頁尾 -2-／下一頁標頭／第11至20題說明，並消除該題已解決的頁尾疑慮標記。三題原圖 bytes、路徑、裁切保持原樣，解碼後逐RGB像素與封存原頁同區完全一致。

三題新增 native G2（去答案）、G3（操作員官答證據）及來源報告；questionVerified／answerVerified 僅表示來源核實。沒有改教學、獨立E信任或發布資料。114 SQLite 僅更新三題 payload_json／payload_sha256；其餘202完整SQL tuple與完整canonical record不變，所有205資料逐題roundtrip及SHA、integrity_check通過。115 processed全體tracked檔案逐bytes不變。原始 E11 record／WebP／issuer 與原凍結commit不變，不更新或替換solver-only包。

本機10項測試成功，包括：原生G1/G2/G3與205完整性、footer重入、錯答案、其他canonical或SQL row變動、WebP/PDF位元組變動、notice過度推論、issuer錯題／非法路徑，以及來源不足以發布。正式 main native publisher 判定三題 certificates_complete=false。遠端 CI 須在exact-head重新下載原PDF後重跑，結果以Issue36 RETURN為準。

## NEXT OWNER：可直接複製的工作指派

### MASTER／ROLE A

請刷新此Draft PR與exact-head CI，檢查E10 D僅為run into、三題native G2/G3、205-row parity、原圖及其餘202與115不變。正常審核後才決定合入QA；不得把來源PASS當作READY／LIVE，不改E11凍結版本。

### ROLE B（一般對話，不需Sites／Work）

請在來源PR正式接納後刷新E08／E09既有教學，依新QREV核對原教學digest及原始作者證據。內容未變不得重寫或借用新Session冒充原作者；E10若缺教材另領有界task。每個A-D選項保留教師角度及白話雙層說明，原圖下劃線與詞義題意完整。不得自審、發E receipt、READY或LIVE。

### ROLE E（一般對話，不需Sites／Work）

請保留既有內容PASS，等正式來源及作者provenance可核實後才驗V1。E08/E09/E10本次只是來源證據，不是獨立內容receipt；作者或reviewer平台識別不足填UNVERIFIED。不得以GitHub actor或新UUID取代。G6首次provider bytes／獨立G7及正式G8仍分別HOLD。

### G6／ROLE D

保持E11唯一凍結指派；本次來源處理不構成新G6指派。沒有真實非UI憑證前，不產正式staging或16/16 G8，不使用測試fixture／技術preview代替。E12獨立HOLD。

沒有付費API、secret、付款、Sites、main、approved或Pages變更。新READY=0、新LIVE=0。作者／reviewer Session證據UNVERIFIED，G6/G7／正式G8 NOT_EXECUTED。
