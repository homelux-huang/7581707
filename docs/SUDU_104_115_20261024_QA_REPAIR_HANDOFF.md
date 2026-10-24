# 7581707｜104–115 年題庫獨立稽核後修復交接（2026-10-24）

**最高規則：QA ONLY / NO RELEASE。不得修改 main、合併 Draft PR #3、部署 LIVE、改學生資料或把 G1 視為 G6。**

## 唯一 GitHub 與真實覆蓋

- Repository：https://github.com/homelux-huang/7581707
- 本工作唯一寫入分支：qa/114-115-official-visual-review
- 追蹤用 Draft PR：https://github.com/homelux-huang/7581707/pull/3
- 開始 SHA：1b82183827af78e64785d4d9f9a03d40fc7393cc
- 主分支交接 SHA：57d766e841235b937babf3fe10a8ff44606c7c41（本 Session 未寫入）
- 真正最新數據以 GitHub HEAD 的 sudu/data/processed/104-115-QUESTION_ID_GAPS_20261024.json 為準。

**已重新稽核：105–115 年共 2,249 題候選，SHA 驗證且題號關聯的單題 WebP 2,249，缺圖 0，已登錄來源目視 G1 266 題（11.83%），剩下 1,983 題 G1 未完成；G5 11／11 年 PASS，G6 放行 0／11 年。**

104 年僅有 203 筆舊來源候選；官方真正題數尚未核實，processed 題庫也未建立，不能併入上述分母。

| 年度 | 候選 | 已連結 WebP | G1 PASS | G2 PASS | 官方最終 G3 | G5 | G6 |
|---|---:|---:|---:|---:|---:|---|---|
| 105 | 204 | 204 | 7 | 0 | 0 | PASS | NO RELEASE |
| 106 | 204 | 204 | 16 | 10 | 0 | PASS | NO RELEASE |
| 107 | 204 | 204 | 19 | 5 | 0 | PASS | NO RELEASE |
| 108 | 204 | 204 | 26 | 0 | 0 | PASS | NO RELEASE |
| 109 | 204 | 204 | 0 | 0 | 0 | PASS | NO RELEASE |
| 110 | 204 | 204 | 0 | 0 | 0 | PASS | NO RELEASE |
| 111 | 205 | 205 | 10 | 0 | 0 | PASS | NO RELEASE |
| 112 | 205 | 205 | 0 | 0 | 0 | PASS | NO RELEASE |
| 113 | 205 | 205 | 10 | 0 | 0 | PASS | NO RELEASE |
| 114 | 205 | 205 | 35 | 1 | 0 | PASS | NO RELEASE |
| 115 | 205 | 205 | 143 | 1 | 81 | PASS | NO RELEASE |

最終重新覆蓋稽核：https://github.com/homelux-huang/7581707/actions/runs/40103533097 （SUCCESS）。
110-09-1-80 為先前已隔離的假題號，不得重新加入。

## 本次真正完成與證據

### 106 國文 C35–38
- 106-00-C-35 舊 v1 圖包含第 36–38 題共用文章，已保留舊圖、另建立官方第 7 頁原像素 WebP v4，直接 G1 PASS。36–38 題現有跨頁 G1 有 SHA 證據，沒有不必要重裁。
- 國文 35、36、37、38 原頁 OCR/文字核對新增 G2 4 題，保留舊版未確認文字與逐項差異；未出現真實 raw OCR 者保持 null，不偽造 Tesseract。
- 年度 G1 16、G2 10、G3 0。
- CI：https://github.com/homelux-huang/7581707/actions/runs/40101621628 、 https://github.com/homelux-huang/7581707/actions/runs/40101769478

### 107 英文 E32–35
- 既有四張單題與兩份共用 WebP 對照官方第 6 頁，沒有發現必須重裁的缺漏；新增四題 G2，清理 E33、E35 選項受相鄰題／頁首污染。
- 36、37 題仍需本題獨立 G1，不能因共用文章驗收而自動 PASS。
- CI：https://github.com/homelux-huang/7581707/actions/runs/40100621692

### 107 商管專業（一）49、50 題
- 官方第 8 頁原始像素 WebP 補齊兩題，重新目視後兩題 G1 PASS；49 題 Visual Basic 題幹／程式及 A–D 校正為 G2 PASS。50 題含圖形選項，G2 仍待獨立校正。
- CI：https://github.com/homelux-huang/7581707/actions/runs/40102001395 、 https://github.com/homelux-huang/7581707/actions/runs/40102238160

### 107 國文 8～16、35～38 題
- 補齊原本缺少的 13 張單題 WebP，另分離三組共用文章及表格：107-00-C-SHARED-13-14、107-00-C-SHARED-15-16、107-00-C-SHARED-36-38。
- 首次逐張目視發現第 13 題缺 D 選項、第 14 題混入第 13 題尾、第 15 題混入共用註解、第 16/37 題邊界污染及共用詩文註解截斷；保留舊版，新增 v4 修正版，重新來源目視。
- 本批 13 題及 3 共用材料已登錄助理直接目視 G1，年度 G1 合計 19。
- CI：https://github.com/homelux-huang/7581707/actions/runs/40102414785 、 https://github.com/homelux-huang/7581707/actions/runs/40102598721 、 https://github.com/homelux-huang/7581707/actions/runs/40103140710

### 108 年全部 26 題原缺圖
- 數學 B 11～17（7）、專業（一）15～18 與 26～33（12）、專業（二）23～29（7），從官方四張來源頁建立單題原像素 WebP，另分離會計 24～25 設備交換共用條件。
- 首批圖片目視發現數學 16/17 行列式頂端、第 28/29 題跨選項 D、會計 24/25 邊界等問題，均版本化保留舊圖，修到 v3／v4。
- 26 題與一份共用材料經第二輪比對已登錄助理 G1 PASS；**108 年 G2=0、G3=0，禁止放行。**
- CI：https://github.com/homelux-huang/7581707/actions/runs/40102786402 、 https://github.com/homelux-huang/7581707/actions/runs/40102989026 、 https://github.com/homelux-huang/7581707/actions/runs/40103306523 、 https://github.com/homelux-huang/7581707/actions/runs/40103444802

## 質量限制與不可偷換

1. 所有本輪新 G1 的 reviewer 為 ChatGPT assistant，independentHumanReview=false；**這不是獨立第三方真人驗收**。
2. 使用了 GitHub 已保存的來源原頁 raster、PDF SHA、原 WebP 像素、輸出 SHA 和裁切座標，並逐張直接目視；本輪未逐份重新下載官方 PDF 位元組，因此不能宣稱已新完成獨立 G0。
3. G1 只管圖片，**G2／G3／G6 完全分離**。本輪未新增最終官方答案驗證（answerVerified）。
4. 原有 114／115 單題發布流程不動；本 QA 分支全部未符合年度 G6 的 releaseAllowed 和 integrationReady 仍必須是 false。
5. 各批 workflow 使用非強制 push 與 QA HEAD SHA lease，執行 SQLite 雙次匯入／讀回、PRAGMA integrity_check，未動正式學生資料。

## 交接後立即處理

- **P0：**重新檢查所有年度 release-manifest、準備發佈／答案旗標；無完整 G6 就維持 NO RELEASE，勿覆蓋 114／115 合法上線的單題流程。
- **P1：**104 年須先核對五份 TCTE 官方原卷、真實題數及 PDF/最終公告，203 僅為來源候選；之後建立 processed、WebP、OCR、SQLite。
- **P1：**107/108 按原圖逐題補 G2 文字與公式，保存 legacy/raw、修正版與 diff，尤其圖形選項不可自行猜文字。
- **P1：**按年度官方標準答案及最終疑義／更正公告逐題查核 G3，保存官方 PDF SHA、頁碼、版本；不得只採 answerMatched。
- **P1：**105～115 其餘 1,983 題仍缺逐題目視 G1，不可把 WebP 100% 誤報為 G1 100%。
- **P2：**按 SHA lease 提交本 QA 分支、確認 CI 日誌、雙次 SQLite G5、報告與 PR #3；真正通過全部必要品質閘門前不合併、不部署。

**最終結論：資料候選圖覆蓋 2,249/2,249，G1 僅 266/2,249（11.83%），G5 11/11，年度 G6 0/11；NO RELEASE。**
