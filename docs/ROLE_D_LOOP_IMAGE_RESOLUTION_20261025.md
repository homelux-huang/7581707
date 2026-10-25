# Role D Loop：原圖解析與圖片載入（2026-10-25）

控制台：[Issue36](https://github.com/homelux-huang/7581707/issues/36)。角色 D；只修驗收器，不是教師簽核。唯一整合候選 PR35、唯一逐題台帳 PR30；本文件不另建台帳。

## D-WEBP-RESOLUTION-20261025-VSCODE-01

- 基底：PR35 `e2cf6fe99d879d9b872e1b5b8137591e1f4f68b5`；分支 `fix/role-d-original-image-resolution-20261025`；租約留言 `6393562066`（實際 claimedAt 採 GitHub created_at，手填時間更正見 `6393563712`）。
- 範圍：測試 helper、負測、Role D matrix 的來源解析及 workflow 測試觸發；不改 HTML/runtime、題目、教學、原圖、台帳、發布器或核准旗標。
- 修復：原始內嵌 WebP 直接嚴格解碼 base64、驗 RIFF/WebP 與長度並計 SHA；生成題圖只允許既有 build 的產物，須有唯一 crop config、原始官方頁、相同題號／科目／裁切範圍與 manifest SHA。來源與公開複本同時存在時 bytes 必須一致。HTTP 原圖必須200、WebP MIME/header及相同SHA。保留原有 img.decode。
- 原圖來源 revision 為上述基底的 Demo/裁切設定；35題原圖實際SHA由 resolver負測首項逐張重算：30張官方原頁pixel crop、5張既有inline WebP。教學 bytes/digest未變；不是114/115新候選教學證書。
- 驗證：公開 build PASS；resolver PASS 7（包含實際35題，及錯誤SHA、錯裁切、缺官方頁、錯題號、非法路徑／data URI等負測）；語法／diff PASS。
- 真實瀏覽器診斷未通過：國文15個case PASS／16 FAIL，失敗為下一題圖片未解碼即進入 pre-answer layout；會計40 PASS／10 FAIL的部分報告，遇同類錯誤後人工停止，非完整矩陣。這些部分PASS不是題目8×2合格或UIQA批准。
- 本機診斷輸出：忽略的 `test-results/role-d/demo-C.json`、`demo-ACC.json` 與截圖。診斷時工作樹有測試修改，不能將其 actualCommitSha 欄位冒稱為已提交的正式精確SHA驗收；修復後必須對最終commit重跑。
- 新獨立教學QA／UIQA／READY／main／LIVE均0。下一批修布局量測前的實際圖片等待，保留所有原圖及版面斷言；之後檢查其他實際失敗。
