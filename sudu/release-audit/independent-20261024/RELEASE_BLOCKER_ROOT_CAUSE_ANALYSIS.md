# 7581707｜固定128題正式發布阻塞根因

稽核日期：2026-10-24（台灣），main SHA 57d766e841235b937babf3fe10a8ff44606c7c41；QA HEAD 2c1a958b56980a7cbf49a9eb1c35cf64ced5f9ba。此報告將**安全設計可被繞過的證據**與**已發生的正式網站錯誤**明確區分：沒有證據證明已發生錯誤LIVE教材事故。

| Issue | 分級 | 實證與根本原因 | 必須修正／PASS 條件 |
|---|---|---|---|
| P0-01 | P0誤放行風險 | main 的 scripts/sudu_verified_publish.py:484–572 對欄位、SHA及證據文件有校驗，但無可核驗的**審稿主體與原作者職責分離**；teaching_complete:196–230僅查 reviewer字串/日期等；前一次 ECON34 5→6 staging run 40087595980 成功接納 AI 自填事後複核，是實際反例，**不是第六題已LIVE** | 先新增負測：同一原作者填寫「Independent reviewer」、生成合法SHA證明但未有不同審查事件，必須FAIL；設計不可憑同一作者偽造的審核權限／簽章或獨立可稽核事件，並檢查四選項、內容、教學digest。實際授權不同 reviewer 的實質審核可PASS |
| P1-02 | P1 | scripts/check_live_release.py:44–75 只以題數驗證approved JSON，preview只遍歷 reviewed[:2]，sharedImages只查[:1]，**所有正式核准題的實際WebP、教學正文與完整ID未逐題校驗**；run 40097988371 LIVE_VERIFIED 只代表既有 checker 閘門 | LIVE比對全 approved canonicalId、答案、教學 canonical digest、完整WebP SHA、所有 shared SHA、進度；建立「相同題數不同內容」、「第三預覽圖錯」、「第二共享圖錯」負測均FAIL |
| P1-03 | P1 | ECON34原圖/事前解題/教學/8x2 staging 有，但缺真正不同審查者的實質教學 QA；ccbb6574 已退回原五題、安全 40100870119 PASS | 取得分離審查、來源PDF公告、SHA證書及重新8x2同內容正式UI，且維持另外五題完全不變；未通過則維持 BLOCKED |
| P1-04 | P1 | MB20–25原題文字污染已由候選 commit 0b1343fb 隔離修正，正式來源admission仍 false；修改文本會改 questionRevision、令舊 teaching/UI證書失效 | 每題原圖/表格/公式審查，原始diff保留，205筆SQLite隔離雙次匯入、其餘199題不變，重新計算rev/teaching/UI SHA再提交來源 QA；六題不直接READY |
| P1-05 | P1 | main scripts/sudu_verified_publish.py:412–414 對 year!=115 一律 return False，114公告准入無合法通道；已有未合併 PR #22 修年專用閘門 | 獨立驗PR22+PR21之114官方四文件及更正題清單、錯SHA/缺頁/跨年負測，確認115不退步、非force合併由原Session處理 |
| P1-06 | P1 | 固定128草稿完整128，但獨立教學QA0、草稿release certificate0；現有來源已批准的5題與草稿完成不同 | 逐題閱讀原圖、官方公告/答案、盲解/論證、四選項雙層教學、計算/非計算、特化來源、8×2正式UI與SHA並保存不同審查者證據；單題通過才新增 source certificate |
| P2-07 | P2 | MB23表格以 originalSourceTableCandidate 新欄位保存，主問題字串不再包括表格，若 publisher/UI 漏序列化則學生只能看到不完整條件 | tests必須確認表二列三欄有 schema+WebP關聯且 UI可讀，不能只檢查question字串；禁止舊臨時文字直接進正式來源 |
| P2-08 | P2 | MB05沒有證明人類教師獨立簽核，教材學校版次頁碼未核實 | 釐清現行是否強制人類審查；若強制則取得真正教師審查。無依據時保留「待核」，不直接撤回本次獨立解題正確、已LIVE的既有5題 |
| P2-09 | P2 | 英文03/28、商概07、數科33、經濟28、會計06/12/15、國文18的首次判斷和教材術語/來源警示需要逐題獨立裁定；經濟28原題沒有250元總預算 | 保留歷史初解及官方差異，獨立讀公告／教材與來源文字，錯誤未排除之前不要清除警語或核准 |
| P2-10 | P2 | 固定跨台帳的歷史 main/QA SHA 可能與後續新 source 提交不同 | 每次來源/教學/UI改版重新計算 source revision、content digest、證書SHA；不把先前CI SUCCESS當新版本PASS |
| P3-11 | P3 | 測試證據/教材版次有的只存在舊Actions artifact或待核，難以學校實務複查 | 補可追溯截圖、差異、真正教材版本，無可證來源不造假；不得升為不必要的假阻塞 |

## 反向測試必須實作

1. Reviewer自填「別人」，但無第三方實質審核/認證事件：**拒絕**。證據檔SHA一致也不等於審稿獨立。
2. 修改單題 WebP、OCR、官方PDF SHA、教學內容digest、來源 revision，任何不一致：**拒絕**。
3. 114／115官方公告不可混用，09-2 Q06/28/44列名、第34未列；錯PDF SHA、漏頁、重複題號、錯官方答案：**拒絕**。
4. LIVE approved第5題答案或內容被改、預覽第3題WebP被改、第二個 shared WebP被改，題數未變：**拒絕**。
5. 計算題必有逐步算式；ECON34概念題沒有空計算框；16組8尺寸×2主題無溢出、所有答題/錯題復習互動正常。

所有新測試在隔離 Audit/修復分支運行，**不得為測試污染正式 source/學生資料**。未現場完整執行者維持 NOT VERIFIED。不得刪 assert、降 Gate、批改全體 PASS。

可信相關證據：[40087595980](https://github.com/homelux-huang/7581707/actions/runs/40087595980)（技術6題暫存）；[40100870119](https://github.com/homelux-huang/7581707/actions/runs/40100870119)（糾正為安全5題）；[40097988371](https://github.com/homelux-huang/7581707/actions/runs/40097988371)（現行LIVE verify）；[PR #22](https://github.com/homelux-huang/7581707/pull/22)（未合併的114年度規則修正）。
