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

## D-IMAGE-READINESS-20261025-VSCODE-02

- 基底為第一批提交 `6c44ce6f7dfa45bcdd280acbd7a651ce364fe8b3`；租約留言 `6393594449`。
- 每題版面檢查前先等待正確題號與全部原圖src一致，逐張捲入視窗，等待complete及有效尺寸，再執行decode。原圖SHA、版面、題號、選項與digest斷言保留。
- 再診斷已越過原圖解析／未解碼失敗；國文、會計各至少25個真實case完成。接著發現手機深色模式回首頁時，驗收器盲目再點一次已展開的navHandle，反而收合導覽後再點視窗外的navHomeBtn。為避免重複已知失敗，診斷已停止，部分結果不能作完整UIQA。
- 真實360×800觸控重現：按themeBtn後 aria-expanded=true、navHomeBtn top=28；再tap navHandle後 aria-expanded=false、top=-235。這是驗收器的切換狀態假設，下一批將保留真實tap/click並先核對展開狀態。
- [35題bytes/digest綁定](ROLE_D_LOOP_IMAGE_BINDINGS_20261025.json)提供本批實際imageSHA與Demo欄位digest；其sourceRevision明確是Demo JSON serialization摘要，不冒充114/115官方候選題revision。教學未修改，新獨立QA/UIQA/READY/main/LIVE仍0。

## D-NAV-STATE-CI-20261025-VSCODE-03

- 基底 `0cf250848056a0cc0ec8b9f4a6102ec4a70dbba8`；租約 `6393616724`。先讀navHandle實際aria-expanded，只有收合時才真實tap/click展開，接著要求aria-expanded=true再點首頁；所有錯題復習及localStorage要求保留。
- 國文、會計各5題×8viewport×2theme本機診斷 PASS 80，各80截圖，含真實touch/mouse、原圖bytes及Demo欄位digest。這是修改工作樹中的診斷；raw report actualCommitSha為啟動時0cf2508，不可冒稱本批提交的精確SHA證書。最終SHA CI仍須重跑；未提升任何新候選UIQA。
- 唯讀Role-D workflow允許stacked PR的PR35 base；新增helper路徑觸發及resolver負測，不改發布workflow或權限。報告新增實際執行的browser test／resolver bytes SHA，並將命令引用更新為實讀PR30 `144364bc...`。
- 原先真人教師阻塞已由Issue36最新置頂政策取代；改採不同作者的可追溯AI內容複核。相關policy/publisher/審查契約由MASTER另租約修訂；本Role-D批次不改發布gate，也不以舊教師名冊作唯一阻塞。來源、官方答案、實質獨立複核與精確digest UI/CI仍須完整證據。
- 下一步：核對本PR最新精確SHA的21個年度×科目CI job，按實際失敗另領最小修復；已合格的原圖/OCR/教學不重做。來源/教學變更時舊UI結果不可沿用。

## D-EXACT-SHA-MATRIX-TRIAGE-20261025-VSCODE-04 / D-SINGLE-GUIDE-CALC-20261025-VSCODE-05

- triage精確提交 `74f26f12752fd965f20c6497ad8b141865442b64`；CI `40163474103`已讀取demo C/E/BC/IT/ACC五組SUCCESS，其餘當時仍執行；不能稱整個21矩陣完成。
- 115英文只含28張image-preview-only，完整矩陣448case，沒有可作答教學題，不能提升教學UIQA。115數學B既有5題可作答＋25張預覽，完整應480case；精確提交診斷在第一題的計算重複檢查失敗，已隔離並轉最小修復，沒有改內容或期望答案。
- 真實HTML的alignGuideToCorrectAnswer會用target.after(guide)把唯一guide放入answerCard內。測試原先要求整個answerCard內0條計算，誤把正常guide視為重複。修正要求：唯一guide、全部來源步驟逐條一致、option-detail內0條計算、整頁計算步驟數恰等於來源行數。真重複仍會失敗；既有V4位置維持不變。
- VSCODE-05租約以Issue36留言為準，基底74f26f1；修改僅本matrix與本交接。須重跑最後精確SHA，舊成功不冒用至新的測試版本。
