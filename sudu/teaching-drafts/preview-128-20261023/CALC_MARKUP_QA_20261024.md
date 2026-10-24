# 計算步驟粗體與highlight修正（2026-10-24）

基準教學HEAD fc99cbae1ad23561f229898f9a3d2c4a16045027。已確認該SHA三項CI成功，含E03更新教學digest與真實導航操作的隔離UI（40050553778）；不能視為來源層發布憑證。

發現：年度轉接器formatStudyValue針對考題計算式直接呼叫舊formatter，會把**重點算式**當普通文字，且不建立highlight。修正為保留原calculation-steps/step結構及步驟編號，逐行使用安全markup renderer；根號、平方、負號原樣保留，任意HTML先escape。

本機回歸：safeCalculationMarkup三行測試PASS，包括strong+mark、數學符號、步驟1至3、script不執行、無原始星號；既有英文詞形/去重測試及5項Oct24內容測試PASS。

隔離MathB19–25預檢增加攔截候選adapter，避免測到main舊程式卻宣稱候選修正已驗；報告綁定adapter SHA256。第25題實際calculation-first必須出現mark且無原始**。仍為loopback-only fixture，不更動approved或main。E03同一workflow繼續測8×2。

CI結果待實際完成；READY=0，不簽發正式來源、教學或UI發布憑證。既有三道爭議與文字QA隔離不變。

## CI實際結果

- 候選commit：6eb6bdeaa841076a736bd23de366aac09f25704a。
- CI實際checkout main：ba924eb39b9d59b7f41c79861700f16e583b9a86（其他Session更新，並非先前5415）。
- readiness run 40077067325：SUCCESS。
- 隔離V4 run 40077067309：SUCCESS。MathB19–25共112案例＋E03共16案例，均含真實click/tap；MathB25計算mark檢查通過。
- https://github.com/homelux-huang/7581707/actions/runs/40077067309
- artifact 12553542996；保留期限依workflow，報告綁定候選adapter SHA及E03 teaching digest。
- 一般draft audit 40077067306在記錄時仍執行中，不預先記成功。
- 此為隔離UI實證，MathB仍含原圖選項提示fixture，E03來源admission未齊。READY不變，未部署main；之後整合須重新比較最新main轉接器差異，不整檔覆寫他人變更。
