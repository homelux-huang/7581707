# 2026-10-23｜固定128題全部原圖QA完成（英文21-28共用文章與選項）

- 對照HEAD：`77d85d901b6b925fb3e90931536ac55aafb60204`。此輪實際下載英文21-28八張單題選項WebP、兩張共享閱讀全文WebP，重算原二進位SHA256且直接開圖目視，十張影像均與凍結清單匹配。
- 21-24同讀《International Day for Women in Maritime》；25-28同讀《Tamkang Bridge》，共享文章**本身是另一張必需影像**，不可被裁成題目選項圖，也不可只顯示短選項而省略上下文。
- 目前128個凍結題號獨立原圖全部已在本週期逐張實際驗二進位SHA256及目視；其中8題需對應2份不同sharedImages並也已獨立驗原圖SHA256。總原圖達**128/128**；共享2/2 PASS。
- 官方最終答案另有128/128已核實的保存證據；但原圖與官方答案完成不等於整體教學內容完整QA，完整獨立教學QA仍0/128、正式發布合格0/128、部署0。候選答案已知，本輪不是首次盲解；不改OCR、main、approved、studentReleaseApproved或GitHub Pages。

## 共享文章與 SHA256
- E21–24：`data/approved/webp/115/115-00-E-SHARED-21-24.webp`，SHA256：`a6a17a954dd9a8aac78c54977be3c428d8a5f4cc5ea280d0a7408082fe5ec1a7`；原文含女性航海員比例4%、260人、引水人工作艱難、運油船長與性別友善職場。
- E25–28：`data/approved/webp/115/115-00-E-SHARED-25-28.webp`，SHA256：`fe20804241ad196d516addcac2652aae89859ddd4f626f2f533deb43782fad9e`；原文含淡江大橋、交通往來、特殊設計與旅遊效益。

|題號|單題選項圖SHA256|根據共用文章的局部解說查核|
|---|---|---|
|E21|`50cb3ade513346aa98daa7587d4716cc68e1e0c28a2d675e0803bb0c126aae28`|Among the 260 women seafarers語意為其中許多人，官方A。|
|E22|`d6412daa205b2fbfbb264d7a83862f49dfc371eaa97bba283a93d3e361d3bca4`|大浪中登移動船舶需冒風險，所以tough，官方D。|
|E23|`b79e98edba696dac9c399ca813e9dcbbda515180f28fb388528018579456d18f`|即使天氣惡劣也可靠運油，even when，官方A。|
|E24|`1c2dae86309523155b33b605ee9ea7bc45061efd6e83b009b5e5e5c500f2e6f7`|性別友善職場目的to improve women's employment，官方C。|
|E25|`c35665f575c84b35391ebeaf1e782e639754c419f0c9b35027e3b57c5373d51b`|淡江大橋讓兩地交通車流順暢，traffic flow，官方B。|
|E26|`d60fe5fe2573515efd40bf92aa6ad56448e57e92471f155ac68ea3ef0bd8617f`|橋被國際設計競賽選中，過去分詞selected，官方A。|
|E27|`5fec3e12dbc2e20a0e8b5e558313eb8d79ee7159775711f8e6179aa4f3c3c392`|橋塔像舞者舉雙手，as if ... were lifting，官方A。|
|E28|`486a14735f252bda4ea068e779a8337ce2f842c8736e3f3e11fe1478ccefb377`|縮短交通時間且吸引觀光，transportation and tourism，官方D。|

### 仍未完成的教學/發布門檻
- 128題每題A-D高職/小學解說的獨立專家QA、教材版本章節與頁碼核實、英文IPA、同反義詞分級與新聞真實來源、所有科目反向題及計算逐步理由逐項確認、Playwright RWD/主題/解答跳轉/重複項目測試。
- 三題商概7/數科33/經濟28雖已有官方正解，教學概念歧義仍須隔離，不能改為發布PASS。
