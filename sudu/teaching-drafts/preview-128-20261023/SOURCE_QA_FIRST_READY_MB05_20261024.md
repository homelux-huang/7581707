# 7581707｜首筆 128 題增量正式 admission：115 數學 B 05

日期 2026-10-24。**正式主分支已經接入第05題**，待 GitHub Pages `verify_live` 再確認實際 LIVE。

## 真正的逐題證據鏈

| 審核項目 | 實際可核查證據 |
|---|---|
| 單題原圖及官方來源 | `115-00-MB-05.webp` SHA `be5bb1f0e23eddff9e8a0f17e6e116ce2ce4219205f4527d50a710fb76e20dd2` |
| 題幹、選項、SQLite來源 revision | `3b0a4236f9298edd225b445592faee3b222c8ecfc1b62425278a0de576cc1df9`；[#40084857695](https://github.com/homelux-huang/7581707/actions/runs/40084857695) |
| 事前獨立原圖推導 | Git 原始 Commit [cf6a4efe](https://github.com/homelux-huang/7581707/commit/cf6a4efede233b0e447d52498209adf1b721c13e)，先於答案比對新 commit；此為當時 AI 解題，非人類老師 |
| 官方最終標準答案及疑義 | 已在來源核對的數學 B 答案 B，PDF SHA `d705f2c3b4360962ed57b1d923a5d9168eae9eb140584ce98cb7cb1f6e27ad95`；00-MB 題卷官方「未提出疑義」 |
| 教學獨立後驗複核 | 原圖、A～D 雙層解說、兩種中點推法、完整計算，真實審查者欄位為 GPT-6 AI（已知官答後，**非人類盲審**）；教學 SHA `70063f1c4b68979aac9828cdb0dc36a7562591da4f0537bdd0e6f791609827c3` |
| 正式 V4 8種尺寸×2主題 | 原本 UI commit 已過 [#40085225320](https://github.com/homelux-huang/7581707/actions/runs/40085225320)；最新主站 UI `2b48a4a` 對同源題目/教學 [#40085323981](https://github.com/homelux-huang/7581707/actions/runs/40085323981) SUCCESS，截圖/結果 [#12556568589](https://github.com/homelux-huang/7581707/actions/runs/40085323981/artifacts/12556568589) |
| 未修改正式發布器之 staging | [#40085542771](https://github.com/homelux-huang/7581707/actions/runs/40085542771) SUCCESS，原有四題不變，MB05一題新增，source 0–115 admission = 5 |
| 正式來源 QA /資料核驗 | source head `b78a14c8cc6081a7a01613238255fce0a22ba60b`，來源 Actions [#40085605193](https://github.com/homelux-huang/7581707/actions/runs/40085605193) SUCCESS |
| `main` 正式資料接入 | 自動同步 [#40085628007](https://github.com/homelux-huang/7581707/actions/runs/40085628007) SUCCESS，main `31adda6c3973ee73387c767d4a8ba56af1fd81b8` 且實際 `sudu/data/approved/115.json` 5 筆 |
| Pages LIVE | [#40085654639](https://github.com/homelux-huang/7581707/actions/runs/40085654639) **需核實 verify_live completed/success**，不可提前宣稱已部署 |

## 兩組進度分清楚

- 128固定草稿：解說128、單圖/SHA128、官方答案128；其 `progress.json.fullyAccepted=0`／`deployed=0` 是**教學分支獨立憑證結構**的歷史狀態，不等於正式來源沒有新核准題。
- 正式 QA student-certified：原4（02/03/04/09）**+本次 MB05 1**，`verified-student-batch.json` 5個分立證書與實際檔案SHA一致。
- 正式 main 的 115 科學生可作答資料：5題；本批新增 main 接入 **1/128**，本批新增 LIVE **尚待** Pages verify_live。不可把 main 接入誤寫成 LIVE 已可讀。
- 六題 Math B20～25 雖有原圖重核與真實文字隔離預覽 8×2 PASS，尚需正式獨立文字來源 admission、可信先於官答的獨立求解證據與全項教學憑證，故不得增量發布。

## 接續阻塞

唯一學生正式 UI 是 `sudu/v4-115-multisubject-review-demo.html`。以 GitHub Source commit+正式 main+Pages LIVE SHA為三方發布檢查，當本次 LIVE 驗證成功可把新增實際 LIVE記為1；若 Pages有測試失敗，依實際 job log修復且不降低門檻。另128草稿層的全項教學 QA 與正式來源層各題核准應雙軌保存，不批次改所有 `qa.*` 布林值。
