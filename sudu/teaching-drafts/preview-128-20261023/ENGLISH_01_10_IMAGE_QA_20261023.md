# 2026-10-23｜115英文01–10原圖SHA256與字彙局部QA（不發布）

基準HEAD：`4a27b09cfb10d87cc5ed8840b8083c6daa1b34c1`。本批10張原WebP實際下載二進位，以SHA256實算並開圖目視題號、完整A-D選項及題幹。sharedImages皆空。初次對6–10題運行Base64 helper有解碼瑕疵，隨即以標準測試向量校正並對照manifest重新計算，**僅校正後全部PASS的雜湊列為有效證據**。

|題號|WebP SHA256|原圖與字彙局部查核|
|---|---|---|
|115-00-E-01|`0aaf917f21ae7dbd99ee088592350ee4cfa4096f4208e245f2a44f029e57db3d`|wet（仍濕）所以需要晾乾，官方D。|
|115-00-E-02|`e62968113b52267811a43d63a85c40a58e5fbb307b053a132fe237f7055618c8`|join the swimming team過去式joined，官方B。|
|115-00-E-03|`16c8e37d3f169f0488398844030bf4922c4f4639633ee7a4d9a9af83466d8ebd`|treat all students equally，官方B。|
|115-00-E-04|`d78ba6137913c629b215b80374cc5295d5d9f109d289e5283e9d3d756be512e4`|walking distance海灘適合放鬆suitable，官方D。|
|115-00-E-05|`5d5891fec314de437acdb2239a0b41a0d881424edbb0e2d8bb5a875971cf194e`|折扣吸引顧客attract more customers，官方A。|
|115-00-E-06|`ff9ea99d6429f227548512bcea8e2f179ac37aea01bd47a9dfc1178dd83997f5`|預報大多數時間正確→accurate，官方A。|
|115-00-E-07|`ac938e9496f6cce069f2f16e538e973e81ce78f80a2fb0d8b0626fee40d0fd8b`|measure body temperature，官方D。|
|115-00-E-08|`5939346b4af8996ff5db93f2936e665b0dd0a8dad17364069628a91cea372d34`|award presenter announced Shu Qi as winner，官方A。|
|115-00-E-09|`1892de5b1da92e28d02aeb457efae4628c617d4461058d55684a0399916c0689`|原題同義詞option≈choice，非填空，官方A。|
|115-00-E-10|`b79ab2d5652e1fef2545561cc68896d663112d1b07e40aea51360fe825459b5e`|原題extremely moved=deeply moved，官方C；OCR D選項後混頁只記錄不改原始OCR。|

總實體原圖去重110/128，餘18張英文11-28含21-28共用文章；本批不代表IPA、分級詞彙、新聞例句與教材出處全獨立QA。官方答案128/128沿用既有核實，教學全項QA0/128，部署0。