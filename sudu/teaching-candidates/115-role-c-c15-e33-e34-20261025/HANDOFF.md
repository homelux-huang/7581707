# 7581707｜Role C 115 年 C15／E33／E34 source-bound teaching (NO RELEASE)

## Lease, branch and provenance
- Task `C-115-C15-E33-E34-20261025-07`; Issue #36 CLAIM https://github.com/homelux-huang/7581707/issues/36#issuecomment-6394295888，GitHub server createdAt `2026-10-25T06:16:26Z`.
- Role C = GPT-6 AI 教學作者，只採「高職老師解題角度」＋國小白話，**不冒充真人教師／授權資格、不以作者自評取代 E 獨立 AI 複核**。最新使用者政策取消真人教師名錄、Ed25519 簽章、真人 GitHub APPROVED 作為教學發布前置條件；所有原始題目、答案、圖、AI E、D UI、正式 CI／LIVE 仍應分別驗證。
- Unique NEW branch `teaching/115-role-c-c15-e33-e34-after-a64-20261025`, baseSHA **Role A PR #64 source-corrected HEAD `b6c449629efc80d37fa2e6dbb9e680e321367c14`**；此 PR 應以 Role A PR64 為 base（stacked），**不得指向 main、部署或覆寫 A 資料**。
- PR64 僅修 C15 的**結構化選項 D**「拘泥禮法 ／ 不知變通」及 205-row SQLite 相應資料，完整保留 `extraction.rawOptions[3]` 的歷史跨頁混入 OCR 原文。原始 WebP 同 SHA，A 的正式官卷、原圖獨立內容 QA 仍分離。本批 C 沒有編輯來源、原圖、SQLite 或 PR30 的唯一 410 題台帳。
- Source PR64 `sudu/data/processed/115/questions.json` exact Git Blob `0128adc3f41e748950c3f5af83fca6dd1c331f5c`；`webp-manifest.json` exact Git Blob `2e204b1cca4caf8dea494bd0d8ecfccf5b93f84b`；PR30 coordination head `340471f1c821ff58c292c13410a8e081e246c2cb`.
- Previously delivered C author chain PR #41/#45/#48/#51/#55/#59 is unchanged; last PR59 exact HEAD `8910cfbbfedb638206b4b37b1b51817b75137edc`. MASTER must separately select/source-integrate these two parallel stacks; **do not overwrite or accidentally drop older C candidate lessons**.

## Three exact question digests
| QID | Answer candidate | sourceRevision (SHA256 over exact stem+4 options+individual WebP) | individual WebP SHA256 | teachingCanonicalSha256 |
|---|---|---|---|---|
| `115-00-C-15` | **B** | `29ee0b0159cef18c7b9458d4bea07cbd5acf15f787e396a2430cb613310f4485` | `74dc7bb966f1ee508456a962a6fbcff0f42a15b2ffdd8db747477a55b831405f` | `f58b554031ca18cf07db92856e2071535fb0f1d5bec87799fb5d8573ae36e056` |
| `115-00-E-33` | **B** | `d440c66050551440ca887ea3a0d910f28e93cc45d58b9e584fddbeaad7dea855` | `d8faa4637558482adde2cf28f27b681f56527a3aeb67cf7ecc3349cbd4260525` | `477fc29e7e52ae8d829cea89d7c1af953ed854576823296195c485409cdf9840` |
| `115-00-E-34` | **B** | `82de1011ed10d19453c6f9e669acc98bb282bce9f8da259f2461fc2bf3f55004` | `e02ca43b3b8e33347c0cc6c8d3c83a869a7a1d606e2be768c7eb051b977f6d74` | `ca8eb4d3304d6ea3ae1a946745ea0eae931dde67d0423a8b9c2d21e7a1a2282b` |

- C15 shared 11–15 原始 reading WebP SHA `bd9a93ab7139d9d7edd38ae661baf4b0f77170a621b1a18b151d06b532db7f66`; literal text+image revision `9d0735b8c397d8a9c384410e13eb5b83e60b32becd5022cc5f6c69092c08d18f`. **原文尾端「ˉ」是 OCR/text-layer 疑點**，不得偷偷刪除或使用舊 E/D QA；Role A 尚須修正式 source text 與新 revision，PR64 單題修正不能代替全共享文驗收。Role A PR61 有歷史原像素 QA 憑證復原的證據；PR64 manifest shared QA 欄仍 `PENDING_INDIVIDUAL_VISUAL_QA`，C 不將它改 PASS。
- E33/E34 shared 33–35 含原本 **The Revenue per Store for the US Restaurant Chains** 條形圖，**shared WebP SHA** `eb19a37ba2d85414ebe06551aac145cb7053befa6622f7adfb1d86d4e63046ea`，text/chart+image revision `7b0e5a651c1c4d6c290642b131c35baeed5734d849a17e32743b53b9724382a5`，仍 `PENDING_INDIVIDUAL_VISUAL_QA`。本輪是按 GitHub 存在的原試卷文字／manifest 紀錄撰寫，**沒有重新開啟 WebP binary/官方PDF 直接目視重驗圖表，也沒有自己把 OCR／答案官核旗標設 PASS**。A/E 必須逐像素確認條形圖全部數據、六公司及單位。
- E33 帶真實**考題計算式**：half(Din) = 27.4/2 = 13.7 ≠ 12.4；Mastro 14.5 − Nobu 10.1 = **4.4 百萬美元／店**（回代 10.1+4.4=14.5）；13.8−10.1=3.7；13.4−27.4=−14.0。每個選項都有高職專業、國小白話與原圖文字指證；`hasExamCalculation=true` + `examCalculation.given/formulaUse/substitution/steps/result/unit/option/verification`。**不得在 D V4 隱藏這個真計算區塊**。
- C15 為跨文學閱讀之反諷 B **人情淡薄／徒具儀式**；E34 B **180 stores／13 countries 是擴張成果，不是作者列出的成功原因**。兩題 `hasExamCalculation=false`, `examCalculation=null`；D V4 不得顯示不適用計算卡。
- 英文：兩題各自保存 IPA、初中高同義與相反情境詞、`highlights`、2025 真實來源英句（**author-written paraphrase, not a quote**）及中文譯文；`**revenue**`／`**successful**` 為原例句實際詞形。原真實 2025-06-06 Restaurant Business 產業新聞：https://www.restaurantbusinessonline.com/financing/soup-dumpling-chain-has-industrys-highest-auvs-its-not-even-close ，報導 2024 平均每店 $27.4m，是**統計結果**，不自動等於E34成功原因。
- 中國文學來源之教科書版次與頁碼並未核實，沒有編造；已知候選答案是來源中先讀到，**沒有宣稱事前盲解**。

## Testing, access and review/exit
- New exclusively C-owned `sudu/teaching-candidates/115-role-c-c15-e33-e34-20261025/` JSON ×3 + this HANDOFF + batch.json、`tests/test_115_role_c_c15_e33_e34_20261025.py`、read-only `.github/workflows/115-role-c-c15-e33-e34-20261025.yml`；其餘來源/題號/OCR/WebP/SQL/V4、其他角色檔案、main/Pages均不變。
- `batch.json` 同時記錄每個完整檔 SHA256、source/text SHA、單題原圖/共用材料 SHA、教學 digest。CI 要驗證**實際 PR64 修正版原始 Git Blob/205 questions、同題四選項**、各四個 A–D 雙層實質理由、英文2025高亮、E33完全可重算算式、雙路源圖 SHA 與被篡改負測及無 QA 升格。通過 CI 只代表作者候選結構一致性，**絕不代表 E 教學審核／圖表 QA／D V4／LIVE**。
- **A** 完整核原始共享圖表與 C15 尾字、同題官答與更正公告及 OCR；**E** 不同 AI 作者實質審查 C15 主題/四選項、E33 每一公司數值與運算、E34 成因／結果及時事來源，寫具名可追溯完整簽入證據但**不須真人教師簽章**；**D** 同 35 題 Demo 科目別 V4 真實 8 視窗 × 2 色 QA，精確綁 source+teaching+WebP SHA；**MASTER** 檢查 PR #57 最新新AI reviewer gate、受保護 main 與 Pages 部署、同 SHA LIVE。所有未知仍 fail-closed。
- 角色 C 的本批候選 `studentReleaseApproved=false`, `deploy=false`，**新增 READY=0、main=0、LIVE=0**；不合格隔離，完全合格題方可由 MASTER 增量發布。
