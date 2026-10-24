# 7581707｜128 題獨立正式發布稽核總報告

稽核日：2026-10-24（台灣）；稽核性質：GitHub 與部分原圖直接複核，其餘需標明未獨立重跑。正式 main 全程未修改。

## 最新讀取版本
- main: 57d766e841235b937babf3fe10a8ff44606c7c41
- QA: qa/114-115-official-visual-review @ 2c1a958b56980a7cbf49a9eb1c35cf64ced5f9ba
- 草稿: draft/preview-128-explanations-20261023 @ c4cdb10ea61f70e0184f0a078963ebb537a9cc99
- MB20-25候選: qa/mb20-25-source-text-candidate-20261024 @ 0b1343fb7853701ec847fd33321cc792c3172bbf
- 跨台帳版本: d46cd29ee7af088ae2347546ff1fe8b288f34c48

128題唯一集合直接來自草稿 progress.json.items（128 unique IDs），114國文9題、115年度119題。草稿結構128/128；草稿獨立完整教學QA 0/128；草稿發布憑證0/128。main approved/114.json=0、approved/115.json=5（MB02/03/04/05/09）。原有四題加MB05，新增LIVE題僅MB05，不能把五題算全數新增。尚無來源正式核准123/128。

## MB05_FINAL_CERTIFICATION_VERDICT
PARTIAL_PASS_EXISTING_LIVE；不批准任何新核准行為。已於本 Session 直接取得來源第3頁WebP及正式單題WebP並比較完整題幹和四選項，沒有混第6題。獨立計算 C=B+D-A=(3,-2)，BC中點=(3/2,-7/2)，B選項正確，其他A/C/D坐標不符。來源WebP SHA256 be5bb1f0e23eddff9e8a0f17e6e116ce2ce4219205f4527d50a710fb76e20dd2，questionRevision 3b0a4236f9298edd225b445592faee3b222c8ecfc1b62425278a0de576cc1df9，正式教學digest 70063f1c4b68979aac9828cdb0dc36a7562591da4f0537bdd0e6f791609827c3。事前解題記錄 cf6a4efede233b0e447d52498209adf1b721c13e（Git 提交順序支持留痕，不能證明全渠道無先看答案）。本次也閱讀 teaching/ocr/official/blind/ui 各證據JSON；數學算式和雙層四選項理由正確；現有 reviewer 為事後 GPT-6 AI，humanIndependentReviewerVerified=false，不可假冒教師簽核。既有 8x2 CI 40085323981成功，但本次未重新執行。特定114學年教材版本頁碼未查得，必須維持待核。

## 正式main / Pages
Run https://github.com/homelux-huang/7581707/actions/runs/40097988371 同main SHA，verify/build/deploy/verify_live四 jobs SUCCESS。直接讀取 verify_live job log 的 LIVE_VERIFIED，證明現有程式所查驗的公開內容符合其條件：114核准0、115核准5、114預覽9、115預覽119。但本 Session 未自行完成LIVE全部位元再下載，也發現 checker 覆蓋面缺口，不能宣稱全部正文逐題都由LIVE獨立重驗。

## ECON34_FINAL_REMEDIATION_DIRECTIVE
正式五題以外第34題不得以舊6題staging 40087595980繞過真正審稿：該成功只證明自填欄位與SHA能使發布器接納。之後 ccbb657410d60252ad98ed197d953c4de84339af 及 CI 40100870119 將核准清單退回5。此次實際查看來源第8頁與Q34單題WebP（SHA 5141e911e1925cc80d8f0f464688be2c333edb30994cce535f7c378485567b02），並讀取候選教學JSON，獨立事後判斷 A 正確：跟跌不跟漲「可能」成立；B錯把MR不連續稱膨脹缺口；C不能要求同質；D不是相同需求彈性。題目為概念題，hasExamCalculation=false、examCalculation=null。已有獨立內容複核文件 ECON34_INDEPENDENT_POST_KEY_CONTENT_REVIEW_20261024.md，但不是人類教師簽核，沒有權限自動批準。官方09-2確認文件既有SHA綁定清單只列06(D)/28(A)/44(A)，Q34未列；本次未另直接下載該原始PDF。須補審稿者身份獨立認證、正式來源與最新版本8x2、新憑證，再經同SHA流程核准發布。

## MATHB20_25_SOURCE_AND_RELEASE_FIX_DIRECTIVE
本次實際顯示原試卷第7/8頁及MB20～25六張單題WebP。MB20角度、根號與圖(四)；MB21 60度/7km/8km及大於4條件；MB22五張卡/圖六與清除頁尾；MB23表二折扣及費用；MB24對數複利分式/上取整；MB25根號二、圓方程式與圖七均可直接比對。0b1343fb源候選改正文字及SQLite，保留舊文字差異，formalTextApproval=false、studentReleaseApproved=false；CI 40100668504 log顯示205筆roundtrip與其餘199題不變，原五題仍5。這是既有CI可查記錄而非本次現場重新匯入。MB23完整表格保留在 originalSourceTableCandidate；正式UI與資料API不能因短版question忽略表格。六題正式 source text/後續 solve/teaching/UI修訂SHA未完成，維持BLOCKED。

## 發布器重大風險
P0：main scripts/sudu_verified_publish.py:484-572、196-230、250-260 會驗SHA/證據存在，無法驗證另一個真正審稿主體；歷史ECON34 6題staging成功是自簽審核可被誤放行的反例。要求獨立審稿行為及授權簽章/事件與負測，不能只更改 reviewer 字串。
P1：scripts/check_live_release.py:44-75只抽前兩個 image-preview，sharedImages[:1]；核准JSON只檢計數，沒有逐題正文/答案/教學/WebP。錯改第3預覽、第二shared、核准第5題答案而總數不變可能不被該驗證碼發現。修完整清單manifest與負測。
P1：main official_notice_scope_certified() 114年一律False；已有未合併PR22年專用核對及PR21三題來源候選，請先驗既有PR，勿另造寬鬆入口。
來源QA新版 HEAD 2c1a958b 尚晚於交接1b821838，不得用過時base覆寫。

## 實際做過/未做
已查：GitHub分支、main核准JSON、固定128唯一ID、跨台帳、CI job及部分log、publisher/Pages/check_live程式、MB05/ECON34/MB20～25原圖像素與文字、ECON34教學全欄、官方公告既有清單。未做：全面128原圖逐張、全部原始TCTE PDF官方SHA逐頁、128題完整獨立四選項審稿、205 SQLite本次重新匯入、全部8x2真實手機/browser重跑、新版LIVE全部實體位元、所有publisher合成負測。未做者皆 NOT VERIFIED，不得升PASS。

配套文件：128_QUESTION_RELEASE_GAP_MATRIX.json（128筆）、RELEASE_BLOCKER_ROOT_CAUSE_ANALYSIS.md、ECON34_INDEPENDENT_POST_KEY_CONTENT_REVIEW_20261024.md、ORIGINAL_SESSION_REMEDIATION_COMMAND.md、128_FINAL_RELEASE_AUTHORITY_VERDICT.md。

AUDIT_VERDICT=PARTIAL_PASS
RELEASE_RECOMMENDATION=BLOCKED_PENDING_FIXES（僅針對後續新增發布；不撤回目前來源／算式已查之舊五題）
