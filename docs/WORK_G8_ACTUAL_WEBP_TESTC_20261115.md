# TEST C｜原始 MB20-v5／MB23表格圖片的重封負向測試

2026-11-15（台灣）。回應 MASTER Issue36 #6891180469；接續 PR215 exact5ff60d800f8e4a47b1f513e4ba9f942970dc7f9c。只有測試、唯讀CI及此說明；不改production code、來源、教材、trust、approved、main或Pages。

## 真實使用的來源 bytes

完整凍結 QA：`3d7645b9b8c83bd09348115118920501823b3c27`，205題唯一ID，讀取前後保持clean。

| QID | 原圖版本 | 原始WebP SHA256 | QREV |
|---|---|---|---|
|115-00-MB-20|webp-v5|f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf|2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c|
|115-00-MB-23|webp-v2完整表格原圖|2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51|9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4|

測試實際讀取、重算並解碼原始WebP，核對canonical來源的原圖路徑、manifest、G2/G3/G5、canonical teachingDigest與protected publisher的QREV。MB23的G2表格必須3欄×2資料列，保留table-aware revision，不轉檔、不裁切、不重畫。原生G1 image proof／certified_visual_assets使用真正來源證據。

## 重要：權限是明確的單元測試fixture

目前真實 protected policy的E registry仍空。測試先斷言policy Blob為c77ee2ec8ca1381388fbbbe6bd36e679750678eb，並直接呼叫真正gate.certified，兩題都必須回false／distinct_ai_content_review_missing。

為測試G8驗證器對實際原圖的處理，單元測試mock `non_ui`與authority lookup呼叫邊界。原圖、教學content、native serializer、完整網站builder與validate_stage都是實際程式及凍結資料。`auditPath`明確標記SYNTHETIC_UNIT_AUTHORITY_ONLY_NOT_REAL_G1_G7，authorization/G6 hash使用零值測試placeholder，沒有捏造provider回應或可信receipt。

這些OS-temp fixture不是合格的PRE_G8_ONLY，不是positive V1，也不是G6/G7／正式G8；不能拿其資料作為學生發布候選。沒有Chromium、截圖、model call、promotion或任何trust註冊。整個test stage在測試結束刪除，CI不upload任何fixture。這個限制必須隨測試結果一起回報。

## 四項測試與實際拒絕面

1. 兩題實際原圖／G2／G5／QREV／表格來源匹配；真正未mock的V1 gate仍HOLD。
2. 在private unit fixture中，把MB20 staged v5原圖替換成真正MB23 WebP，反向亦然，讓檔案依然是有效WebP；同步重封manifest.siteFiles。生產validate_stage必須由獨立原生重建拒絕，而不是只靠自述hash。
3. 對每題變更sourceCommit、codeCommit、teachingDigest、manifest中的HTML GitBlob binding，必須在進入browser之前拒絕。
4. 實際原圖刪除並重封map、添加額外WebP並重封map、把原圖換成指向source checkout的symlink，全部必須拒絕。

版本與runtime/HTML/annual JSON/payloadPath reseal已由PR215的17個bridge test方法覆蓋；本TEST C補真實MB20/23素材，不宣稱原先已通過正式16/16。

## 執行與驗證

```bash
WORK_G8_FROZEN_SOURCE=EXACT_READONLY_QA_CHECKOUT python -m unittest discover -s tests -p 'test_work_g8_actual_webp_negative_20261115.py' -v
```

必須明確提供固定SHA的唯讀來源；沒有來源時skip，來源SHA或policy變更時失敗，不抓其他版本代替。專用workflow先checkout真實凍結QA，明確執行四項測試，並在測試後用真正current protected policy執行native stage/check，仍只能輸出歷史五題；full138 regressions及2503公開檔案雙建置比對仍保留。

本機實際四項測試成功；exact-head遠端CI與不同code reviewer verdict需另行紀錄。GitHub正式review與owner release權限不由此文件授予。缺真實B/C/E Session、隔離provider首次bytes與G7時，新題維持HOLD。E11唯一freeze不變；E12獨立HOLD。
