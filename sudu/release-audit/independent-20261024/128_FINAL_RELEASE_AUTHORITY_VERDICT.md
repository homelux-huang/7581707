# 7581707｜128題正式發布稽核裁決書

日期：2026-10-24 台灣時區。稽核對象：固定128題；本次僅進行獨立可重現GitHub與部分圖片/教學核對，非完整128題全新真人教學驗收。

AUDIT_VERDICT = PARTIAL_PASS

RELEASE_RECOMMENDATION = BLOCKED_PENDING_FIXES

發布建議僅對**下一批新增題目**而言；不得錯誤宣稱現有主站五題不存在或未上線。現有 main SHA 57d766e841235b937babf3fe10a8ff44606c7c41，Pages run 40097988371 verify/build/deploy/verify_live四jobs SUCCESS，官方 approved/115.json五題含115-00-MB-05；approved/114.json 0題。LIVE checker的檢查範圍不夠覆蓋每題全部內容，本次未自行完成LIVE外站每題 HTTP 全位元查驗。

1. MB05：原圖第3頁/單題均本次直接目視，獨立解得C=(3,-2)、BC中點(3/2,-7/2)，官方既有B一致；雙層教學四選項實際閱讀無發現計算錯誤。事前Git blind commit cf6a4ef 與事後 AI 憑證分離。技術上已來源核准與LIVE，不重新部署；人類教師簽核不存在，不冒稱已合格真人審核。是否強制人類核准須由發布 Gate 的明確角色政策決定。MB05_FINAL_CERTIFICATION_VERDICT=PARTIAL_PASS_EXISTING_LIVE。
2. ECON34：當前不得新增。原圖、概念答案A、事前AI原圖解答、雙層四選項教學、舊隔離8x2有成果，但真正不同reviewer授權審核與新來源/正式版本UI憑證尚缺。已產生專門獨立事後內容複核文件；不等於人類教師核准。ECON34_FINAL_REMEDIATION_DIRECTIVE=BLOCKED_PENDING_CERTIFIED_DISTINCT_REVIEWER_AND_GATES。
3. MB20-25：六張原題WebP相符；0b1343fb候選文字/SQLite歷史CI205筆通過但 formalTextApproval=false，須正式來源文字審核、舊教學digest作廢、重算版本、新16測與完整QA。MB23的原價優惠表不能在正式UI遺失。
4. 已READY：目前正式 main 五題具有 source approval及歷史LIVE驗證；本稽核沒有完成其餘四題的當輪完整獨立解題/圖片檢驗，故不對五題一律新發「全Gate稽核PASS」。
5. 仍BLOCKED：固定128中其餘123題均未有 main student approved；其中草稿128/128結構完成卻獨立正式教學QA0、release certificate0。
6. 發布器重大誤放行風險：同一AI可自填教學審核證明而SHA仍有效，歷史ECON34六題暫存證實；此為gate認證弱點，非已發生正式LIVE事故。需真實審查身份/審查事件負測。
7. LIVE檢查不足：check_live_release.py只查前二 preview、第一shared，未逐題比對approved內容/答案。要擴充驗證並補負測。
8. 114年官方通知閘門需現存PR22年別專用修復，禁止混用115規則。
9. 目前未發現可憑本輪證據判斷應立即從 LIVE 撤除五題的具體錯答案／混圖事故；如來源獨立複核後有實質錯誤，應啟動P0控制，絕不可為數字漂亮擅自改旗標。
10. 下一批10題候選排序（需個別再核對完整來源）：115-09-2-34、115-00-MB-06、07、08、10、11、12、13、14、115-00-E-03。這是針對已知風險/草稿文件的優先處置次序，**不是READY或精確逐題工作量排名**。
11. 所有128正式發布前必具來源官方G0-G3、真實先答推理或相應獨立審核、不同審稿者實質四選項雙層教學、計算/概念判別、來源年別公告、WebP及共用原圖SHA、真實16組正式 V4、publisher 正負gate與來源/教學/UI SHA綁定、main+Pages+LIVE同一commit、原學生localStorage相容性。
12. 任何 OCR文字、公式、表格、WebP 或教材內容更動，舊 sourceRevision、teachingCanonicalSha256、UI證書應視依賴關係失效後重測，不允許沿用舊版本合法PASS。

本報告沒有調整 main、studentReleaseApproved、deploy 或真正學生紀錄，且沒有自行部署。稽核資料位於 audit/128-independent-release-verdict-20261024 分支 sudu/release-audit/independent-20261024/。

最終：**此時不批准新的第六題發布；維持現有經既有流程核准的五題，先修P0認證及P1 LIVE驗證的風險，再讓每題用真正獨立證書逐步解除阻塞。**
