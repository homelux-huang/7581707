# 統測題庫完整度稽核

產生時間：2026-10-18T20:31:50.956295+00:00。
基準 commit：`74f2ff97f1494332564faeaade4a7f98c2687ed8`。資料指紋：`5ad31acaa9f9d0d572c2a4872bcd3d3ec11b8e88856bedc1370a6dc885259911`。

重跑：`python scripts/check_tcte_corpus.py --decode-images --json sudu/data/corpus-audit.json --markdown docs/SUDU_CORPUS_AUDIT.md`。
結構檢查通過只代表格式、索引及圖檔完整性，不表示所有原題、答案、教學或計分完成。

## 實際統計

- 26 年／132 卷／5,423 原始紀錄；符合商管及共同科範圍 5,313。
- 原題核實 0，答案程式配對 4,304，具覆核紀錄 0。
- 純影像導覽 100，占位 480，封面說明疑似誤當題目 48，OCR 未覆核 92。
- 教學草稿 0／完整四選項理由 0／完整詳解草稿 0／教學核實 0／教材核實 0。
- 配分規則紀錄 10／封面基本配分已覆讀 10／完整核實配分規則 0／完整可評分試卷 0。

## 計數定義

- `rawRecords`：含占位、可疑封面及歷史誤收卷，不是已核實原題數。
- `answersMatched`：舊answerVerified或新answerMatched的有效答案配對；不是人工覆核。
- `answersReviewed`：answerVerified及answerReviewedBy/At或verification.answer皆有證據。
- `questionWebpAvailable`：該卷全部索引原頁可讀；不表示當題裁切、共享題組與頁碼已正確。
- `questionPageLocated`：候選頁碼指向存在原頁，當題內容尚待人工覆核。
- `questionMappingReviewed`：候選頁碼另有reviewedBy/At與questionVerified證據。
- `answerWebpAvailable`：該卷官方答案圖檔完整；不是逐題答案文字已核實。
- `expectedCountCandidate`：舊自動擷取expectedCount，可能誤讀或混合不同分卷題號。
- `scoreablePapers`：範圍、題數、原題、答案與官方規則全部覆核，不含人工待閱卷部分。

## 90–115 年逐年表

應有題數是既有自動擷取候選值，不能直接當成全卷已核實題數。WebP 欄計算原頁可存取之紀錄數；當題精確映射另列。

| 年 | 卷數 | raw／範圍內 | 題數候選／未明卷 | 題幹核實 | 答案配對／覆核 | 原題 WebP／候選頁 | 答案 WebP | 草稿／選項理由 | 教學／教材核實 | 規則／可評分卷 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 90 | 4 | 141／141 | 0／4 | 0 | 139／0 | 141／141 | 0 | 0／0 | 0／0 | 0／0 |
| 91 | 7 | 257／167 | 215／2 | 0 | 0／0 | 167／158 | 167 | 0／0 | 0／0 | 0／0 |
| 92 | 4 | 175／175 | 175／0 | 0 | 127／0 | 175／164 | 150 | 0／0 | 0／0 | 0／0 |
| 93 | 7 | 227／207 | 205／2 | 0 | 29／0 | 207／20 | 200 | 0／0 | 0／0 | 0／0 |
| 94 | 5 | 225／225 | 225／0 | 0 | 180／0 | 225／210 | 225 | 0／0 | 0／0 | 0／0 |
| 95 | 5 | 225／225 | 225／0 | 0 | 180／0 | 225／223 | 225 | 0／0 | 0／0 | 0／0 |
| 96 | 5 | 215／215 | 215／0 | 0 | 179／0 | 215／215 | 215 | 0／0 | 0／0 | 0／0 |
| 97 | 5 | 215／215 | 215／0 | 0 | 183／0 | 215／214 | 215 | 0／0 | 0／0 | 0／0 |
| 98 | 5 | 225／225 | 225／0 | 0 | 190／0 | 225／225 | 225 | 0／0 | 0／0 | 0／0 |
| 99 | 5 | 213／213 | 213／0 | 0 | 189／0 | 213／212 | 213 | 0／0 | 0／0 | 0／0 |
| 100 | 5 | 213／213 | 213／0 | 0 | 181／0 | 213／213 | 213 | 0／0 | 0／0 | 0／0 |
| 101 | 5 | 213／213 | 213／0 | 0 | 187／0 | 213／213 | 213 | 0／0 | 0／0 | 0／0 |
| 102 | 5 | 213／213 | 213／0 | 0 | 180／0 | 213／202 | 213 | 0／0 | 0／0 | 0／0 |
| 103 | 5 | 213／213 | 213／0 | 0 | 180／0 | 213／204 | 213 | 0／0 | 0／0 | 0／0 |
| 104 | 5 | 203／203 | 203／0 | 0 | 179／0 | 203／196 | 203 | 0／0 | 0／0 | 0／0 |
| 105 | 5 | 204／204 | 204／0 | 0 | 180／0 | 204／198 | 204 | 0／0 | 0／0 | 0／0 |
| 106 | 5 | 204／204 | 204／0 | 0 | 168／0 | 204／191 | 204 | 0／0 | 0／0 | 0／0 |
| 107 | 5 | 204／204 | 204／0 | 0 | 178／0 | 204／196 | 204 | 0／0 | 0／0 | 0／0 |
| 108 | 5 | 204／204 | 204／0 | 0 | 165／0 | 204／188 | 204 | 0／0 | 0／0 | 0／0 |
| 109 | 5 | 204／204 | 204／0 | 0 | 181／0 | 204／204 | 204 | 0／0 | 0／0 | 0／0 |
| 110 | 5 | 205／205 | 204／0 | 0 | 180／0 | 205／205 | 205 | 0／0 | 0／0 | 0／0 |
| 111 | 5 | 205／205 | 205／0 | 0 | 191／0 | 205／204 | 205 | 0／0 | 0／0 | 0／0 |
| 112 | 5 | 205／205 | 205／0 | 0 | 187／0 | 205／205 | 205 | 0／0 | 0／0 | 0／0 |
| 113 | 5 | 205／205 | 205／0 | 0 | 190／0 | 205／205 | 205 | 0／0 | 0／0 | 0／0 |
| 114 | 5 | 205／205 | 205／0 | 0 | 189／0 | 205／203 | 205 | 0／0 | 0／0 | 0／0 |
| 115 | 5 | 205／205 | 205／0 | 0 | 192／0 | 205／204 | 205 | 0／0 | 0／0 | 0／0 |

## 官方類群代碼證據

- [90](https://web1.tcte.edu.tw/EXAM/090_4y/)及[91](https://web1.tcte.edu.tw/EXAM/091_4y/)年度目錄：14 商業類。
- [92](https://web1.tcte.edu.tw/EXAM/092_4y/)、[93](https://web1.tcte.edu.tw/EXAM/093_4y/)、[94](https://web1.tcte.edu.tw/EXAM/094_4y/)、[95](https://web1.tcte.edu.tw/EXAM/095_4y/)、[96](https://web1.tcte.edu.tw/EXAM/096_4y/)、[97](https://web1.tcte.edu.tw/EXAM/097_4y/)年度目錄：13 商業類。
- [98](https://web1.tcte.edu.tw/EXAM/098_4y/)及[99](https://web1.tcte.edu.tw/EXAM/099_4y/)已改為 09 商管群，不能用 `<100` 一律排除。歷史錯收工程卷保留 ID 與作答歷史，不當作商管卷。

## 逐卷證據與待辦

| 年／卷 | 範圍 | raw／應有候選 | 答案配對／覆核 | 原頁／候選映射 | 答案頁 | 占位／封面疑義 | 待辦 |
|---|---|---:|---:|---:|---:|---:|---|
| 90/00-C | 商管／共同科 | 6／待核實 | 5／0 | 7／6 | 0 | 0／0 | answer_webp_missing_or_incomplete；automatic_answer_pairing_requires_independent_review；missing_nonconsecutive_questions；official_question_count_not_reviewed |
| 90/BIZ-2 | 商管／共同科 | 50／待核實 | 50／0 | 7／50 | 0 | 0／0 | answer_webp_missing_or_incomplete；automatic_answer_pairing_requires_independent_review；official_question_count_not_reviewed |
| 90/00-E | 商管／共同科 | 35／待核實 | 35／0 | 7／35 | 0 | 0／0 | answer_webp_missing_or_incomplete；automatic_answer_pairing_requires_independent_review；missing_nonconsecutive_questions；official_question_count_not_reviewed |
| 90/BIZ-1 | 商管／共同科 | 50／待核實 | 49／0 | 7／50 | 0 | 0／0 | answer_webp_missing_or_incomplete；automatic_answer_pairing_requires_independent_review；ocr_pages_6,7；official_question_count_not_reviewed |
| 91/00-C | 商管／共同科 | 7／待核實 | 0／0 | 8／7 | 1 | 0／0 | missing_nonconsecutive_questions；official_answer_pdf_not_identified；official_question_count_not_reviewed |
| 91/00-E | 商管／共同科 | 35／待核實 | 0／0 | 8／34 | 1 | 0／1 | cover_instructions_misparsed_as_question；missing_nonconsecutive_questions；official_answer_pdf_not_identified；official_question_count_not_reviewed |
| 91/00-M-OLD | 商管／共同科 | 25／25 | 0／0 | 8／23 | 1 | 1／2 | OCR_extracted_24_of_25；cover_instructions_misparsed_as_question；official_answer_pdf_not_identified |
| 91/BIZ-1 | 商管／共同科 | 50／50 | 0／0 | 8／47 | 1 | 0／3 | cover_instructions_misparsed_as_question；official_answer_pdf_not_identified |
| 91/BIZ-2 | 商管／共同科 | 50／50 | 0／0 | 8／47 | 1 | 0／3 | cover_instructions_misparsed_as_question；official_answer_pdf_not_identified |
| 91/09-1 | 歷史誤收保留 | 50／50 | 0／0 | 0／0 | 0 | 1／3 | OCR_extracted_49_of_50；cover_instructions_misparsed_as_question；official_answer_pdf_not_identified；old_09_engineering_record_preserved_not_commerce |
| 91/09-2 | 歷史誤收保留 | 40／40 | 0／0 | 0／0 | 0 | 0／3 | cover_instructions_misparsed_as_question；ocr_pages_8；official_answer_pdf_not_identified；old_09_engineering_record_preserved_not_commerce |
| 92/00-E | 商管／共同科 | 50／50 | 33／0 | 8／47 | 1 | 15／3 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；ocr_pages_8 |
| 92/00-M-OLD | 商管／共同科 | 25／25 | 0／0 | 8／23 | 0 | 0／2 | answer_webp_missing_or_incomplete；cover_instructions_misparsed_as_question；official_answer_pdf_not_identified |
| 92/BIZ-1 | 商管／共同科 | 50／50 | 47／0 | 8／47 | 1 | 0／3 | automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；incomplete_answer_pdf_extraction |
| 92/BIZ-2 | 商管／共同科 | 50／50 | 47／0 | 8／47 | 1 | 0／3 | automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；incomplete_answer_pdf_extraction |
| 93/00-C | 商管／共同科 | 50／50 | 10／0 | 8／9 | 1 | 39／2 | OCR_extracted_11_of_50；automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；ocr_pages_1,2,3,4,5,6,7,8 |
| 93/00-E | 商管／共同科 | 50／50 | 5／0 | 8／5 | 1 | 45／0 | OCR_extracted_5_of_50；automatic_answer_pairing_requires_independent_review；ocr_pages_1,2,3,4,5,6,7,8 |
| 93/00-M-OLD | 商管／共同科 | 7／5 | 0／0 | 8／6 | 0 | 1／0 | OCR_extracted_6_of_5；answer_webp_missing_or_incomplete；expected_5_found_7；expected_count_or_number_extraction_conflict；missing_nonconsecutive_questions；ocr_pages_1,2,3,4,5,6,7,8；official_answer_pdf_not_identified |
| 93/09-1 | 歷史誤收保留 | 13／待核實 | 10／0 | 0／0 | 0 | 0／2 | automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；missing_nonconsecutive_questions；ocr_pages_1,2,3,4,5,6,7,8；official_question_count_not_reviewed；old_09_engineering_record_preserved_not_commerce |
| 93/09-2 | 歷史誤收保留 | 7／待核實 | 4／0 | 0／0 | 0 | 0／2 | automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；missing_nonconsecutive_questions；ocr_pages_1,2,3,4,5,6,7,8；official_question_count_not_reviewed；old_09_engineering_record_preserved_not_commerce |
| 93/BIZ-1 | 商管／共同科 | 50／50 | 0／0 | 8／0 | 1 | 0／0 | official_image_only_no_ocr；question_page_mapping_pending_review |
| 93/BIZ-2 | 商管／共同科 | 50／50 | 0／0 | 8／0 | 1 | 0／0 | official_image_only_no_ocr；question_page_mapping_pending_review |
| 94/00-C | 商管／共同科 | 50／50 | 46／0 | 8／47 | 1 | 0／3 | automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；incomplete_answer_pdf_extraction |
| 94/00-E | 商管／共同科 | 50／50 | 32／0 | 8／47 | 1 | 15／3 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；incomplete_answer_pdf_extraction |
| 94/00-MB | 商管／共同科 | 25／25 | 16／0 | 4／22 | 1 | 2／3 | OCR_extracted_23_of_25；automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；incomplete_answer_pdf_extraction |
| 94/BIZ-1 | 商管／共同科 | 50／50 | 40／0 | 8／47 | 1 | 0／3 | automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；incomplete_answer_pdf_extraction |
| 94/BIZ-2 | 商管／共同科 | 50／50 | 46／0 | 8／47 | 1 | 0／3 | automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 95/00-C | 商管／共同科 | 50／50 | 46／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 95/00-E | 商管／共同科 | 50／50 | 32／0 | 8／50 | 1 | 15／0 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 95/00-MB | 商管／共同科 | 25／25 | 14／0 | 4／23 | 1 | 5／1 | OCR_extracted_20_of_25；automatic_answer_pairing_requires_independent_review；cover_instructions_misparsed_as_question；incomplete_answer_pdf_extraction |
| 95/BIZ-1 | 商管／共同科 | 50／50 | 45／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 95/BIZ-2 | 商管／共同科 | 50／50 | 43／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 96/00-C | 商管／共同科 | 50／50 | 47／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 96/00-E | 商管／共同科 | 50／50 | 33／0 | 8／50 | 1 | 15／0 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 96/00-MB | 商管／共同科 | 25／25 | 15／0 | 4／25 | 1 | 2／0 | OCR_extracted_23_of_25；automatic_answer_pairing_requires_independent_review |
| 96/BIZ-1 | 商管／共同科 | 50／50 | 47／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 96/BIZ-2 | 商管／共同科 | 40／40 | 37／0 | 8／40 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 97/00-C | 商管／共同科 | 50／50 | 47／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 97/00-E | 商管／共同科 | 50／50 | 33／0 | 8／50 | 1 | 15／0 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 97/00-MB | 商管／共同科 | 25／25 | 17／0 | 4／24 | 1 | 2／0 | OCR_extracted_23_of_25；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 97/BIZ-1 | 商管／共同科 | 50／50 | 48／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 97/BIZ-2 | 商管／共同科 | 40／40 | 38／0 | 8／40 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；ocr_pages_8 |
| 98/00-C | 商管／共同科 | 50／50 | 48／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 98/00-E | 商管／共同科 | 50／50 | 33／0 | 8／50 | 1 | 15／0 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review |
| 98/00-MB | 商管／共同科 | 25／25 | 17／0 | 4／25 | 1 | 3／0 | OCR_extracted_22_of_25；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 98/09-1 | 商管／共同科 | 50／50 | 46／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_7,8 |
| 98/09-2 | 商管／共同科 | 50／50 | 46／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 99/00-C | 商管／共同科 | 38／38 | 35／0 | 8／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 99/00-E | 商管／共同科 | 50／50 | 48／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 99/00-MB | 商管／共同科 | 25／25 | 17／0 | 4／24 | 1 | 3／0 | OCR_extracted_22_of_25；automatic_answer_pairing_requires_independent_review；ocr_pages_4 |
| 99/09-1 | 商管／共同科 | 50／50 | 43／0 | 8／50 | 1 | 4／0 | OCR_extracted_46_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 99/09-2 | 商管／共同科 | 50／50 | 46／0 | 8／50 | 1 | 2／0 | OCR_extracted_48_of_50；automatic_answer_pairing_requires_independent_review |
| 100/00-C | 商管／共同科 | 38／38 | 35／0 | 8／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 100/00-E | 商管／共同科 | 50／50 | 33／0 | 8／50 | 1 | 15／0 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 100/00-MB | 商管／共同科 | 25／25 | 22／0 | 4／25 | 1 | 1／0 | OCR_extracted_24_of_25；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 100/09-1 | 商管／共同科 | 50／50 | 45／0 | 8／50 | 1 | 2／0 | OCR_extracted_48_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 100/09-2 | 商管／共同科 | 50／50 | 46／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 101/00-C | 商管／共同科 | 38／38 | 38／0 | 8／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；ocr_pages_1 |
| 101/00-E | 商管／共同科 | 50／50 | 33／0 | 8／50 | 1 | 15／0 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；ocr_pages_1,8 |
| 101/00-MB | 商管／共同科 | 25／25 | 19／0 | 4／25 | 1 | 1／0 | OCR_extracted_24_of_25；automatic_answer_pairing_requires_independent_review；ocr_pages_1 |
| 101/09-1 | 商管／共同科 | 50／50 | 50／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；ocr_pages_1,7,8 |
| 101/09-2 | 商管／共同科 | 50／50 | 47／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_1 |
| 102/00-C | 商管／共同科 | 38／38 | 31／0 | 8／32 | 1 | 6／0 | OCR_extracted_32_of_38；automatic_answer_pairing_requires_independent_review；ocr_pages_4 |
| 102/00-E | 商管／共同科 | 50／50 | 35／0 | 8／50 | 1 | 15／0 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；ocr_pages_8 |
| 102/00-MB | 商管／共同科 | 25／25 | 15／0 | 4／20 | 1 | 10／0 | OCR_extracted_15_of_25；automatic_answer_pairing_requires_independent_review；ocr_pages_3 |
| 102/09-1 | 商管／共同科 | 50／50 | 50／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 102/09-2 | 商管／共同科 | 50／50 | 49／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 103/00-C | 商管／共同科 | 38／38 | 38／0 | 8／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 103/00-E | 商管／共同科 | 50／50 | 35／0 | 8／50 | 1 | 15／0 | OCR_extracted_35_of_50；automatic_answer_pairing_requires_independent_review；ocr_pages_8 |
| 103/00-MB | 商管／共同科 | 25／25 | 17／0 | 4／24 | 1 | 5／0 | OCR_extracted_20_of_25；automatic_answer_pairing_requires_independent_review |
| 103/09-1 | 商管／共同科 | 50／50 | 41／0 | 8／42 | 1 | 8／0 | OCR_extracted_42_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_5 |
| 103/09-2 | 商管／共同科 | 50／50 | 49／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_8 |
| 104/00-C | 商管／共同科 | 38／38 | 31／0 | 8／31 | 1 | 7／0 | OCR_extracted_31_of_38；automatic_answer_pairing_requires_independent_review；ocr_pages_5,6,8 |
| 104/00-E | 商管／共同科 | 40／40 | 30／0 | 8／40 | 1 | 10／0 | OCR_extracted_30_of_40；automatic_answer_pairing_requires_independent_review；ocr_pages_8 |
| 104/00-MB | 商管／共同科 | 25／25 | 21／0 | 4／25 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 104/09-1 | 商管／共同科 | 50／50 | 47／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 104/09-2 | 商管／共同科 | 50／50 | 50／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；ocr_pages_6 |
| 105/00-C | 商管／共同科 | 38／38 | 35／0 | 8／35 | 1 | 3／0 | OCR_extracted_35_of_38；automatic_answer_pairing_requires_independent_review；ocr_pages_6 |
| 105/00-E | 商管／共同科 | 41／41 | 31／0 | 8／41 | 1 | 10／0 | OCR_extracted_31_of_41；automatic_answer_pairing_requires_independent_review；ocr_pages_8 |
| 105/00-MB | 商管／共同科 | 25／25 | 18／0 | 4／25 | 1 | 1／0 | OCR_extracted_24_of_25；automatic_answer_pairing_requires_independent_review |
| 105/09-1 | 商管／共同科 | 50／50 | 49／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 105/09-2 | 商管／共同科 | 50／50 | 47／0 | 8／47 | 1 | 3／0 | OCR_extracted_47_of_50；automatic_answer_pairing_requires_independent_review；ocr_pages_8 |
| 106/00-C | 商管／共同科 | 38／38 | 29／0 | 8／31 | 1 | 8／0 | OCR_extracted_30_of_38；automatic_answer_pairing_requires_independent_review；ocr_pages_2,4,8 |
| 106/00-E | 商管／共同科 | 41／41 | 25／0 | 8／35 | 1 | 16／0 | OCR_extracted_25_of_41；automatic_answer_pairing_requires_independent_review；ocr_pages_3 |
| 106/00-MB | 商管／共同科 | 25／25 | 16／0 | 4／25 | 1 | 4／0 | OCR_extracted_21_of_25；automatic_answer_pairing_requires_independent_review |
| 106/09-1 | 商管／共同科 | 50／50 | 49／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 106/09-2 | 商管／共同科 | 50／50 | 49／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 107/00-C | 商管／共同科 | 38／38 | 31／0 | 8／31 | 1 | 7／0 | OCR_extracted_31_of_38；automatic_answer_pairing_requires_independent_review；ocr_pages_3,4,8 |
| 107/00-E | 商管／共同科 | 41／41 | 31／0 | 8／41 | 1 | 10／0 | OCR_extracted_31_of_41；automatic_answer_pairing_requires_independent_review；ocr_pages_6 |
| 107/00-MB | 商管／共同科 | 25／25 | 17／0 | 4／25 | 1 | 3／0 | OCR_extracted_22_of_25；automatic_answer_pairing_requires_independent_review |
| 107/09-1 | 商管／共同科 | 50／50 | 49／0 | 8／49 | 1 | 1／0 | OCR_extracted_49_of_50；automatic_answer_pairing_requires_independent_review；ocr_pages_8 |
| 107/09-2 | 商管／共同科 | 50／50 | 50／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 108/00-C | 商管／共同科 | 38／38 | 37／0 | 8／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 108/00-E | 商管／共同科 | 41／41 | 29／0 | 8／41 | 1 | 10／0 | OCR_extracted_31_of_41；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 108/00-MB | 商管／共同科 | 25／25 | 13／0 | 4／18 | 1 | 8／0 | OCR_extracted_17_of_25；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_3 |
| 108/09-1 | 商管／共同科 | 50／50 | 39／0 | 8／42 | 1 | 9／0 | OCR_extracted_41_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_4,6 |
| 108/09-2 | 商管／共同科 | 50／50 | 47／0 | 8／49 | 1 | 1／0 | OCR_extracted_49_of_50；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction；ocr_pages_5 |
| 109/00-C | 商管／共同科 | 38／38 | 37／0 | 12／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 109/00-E | 商管／共同科 | 41／41 | 29／0 | 8／41 | 1 | 10／0 | OCR_extracted_31_of_41；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 109/00-MB | 商管／共同科 | 25／25 | 19／0 | 4／25 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 109/09-1 | 商管／共同科 | 50／50 | 48／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 109/09-2 | 商管／共同科 | 50／50 | 48／0 | 8／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 110/00-C | 商管／共同科 | 38／38 | 36／0 | 12／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 110/00-E | 商管／共同科 | 41／41 | 30／0 | 8／41 | 1 | 10／0 | OCR_extracted_31_of_41；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 110/00-MB | 商管／共同科 | 25／25 | 19／0 | 4／25 | 1 | 3／0 | OCR_extracted_22_of_25；automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 110/09-1 | 商管／共同科 | 51／50 | 47／0 | 8／51 | 1 | 2／0 | OCR_extracted_49_of_50；automatic_answer_pairing_requires_independent_review；expected_50_found_51；expected_count_or_number_extraction_conflict；incomplete_answer_pdf_extraction；missing_nonconsecutive_questions |
| 110/09-2 | 商管／共同科 | 50／50 | 48／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 111/00-C | 商管／共同科 | 38／38 | 37／0 | 12／38 | 1 | 1／0 | OCR_extracted_37_of_38；automatic_answer_pairing_requires_independent_review |
| 111/00-E | 商管／共同科 | 42／42 | 32／0 | 12／41 | 1 | 10／0 | OCR_extracted_32_of_42；automatic_answer_pairing_requires_independent_review |
| 111/00-MB | 商管／共同科 | 25／25 | 23／0 | 8／25 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 111/09-1 | 商管／共同科 | 50／50 | 49／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 111/09-2 | 商管／共同科 | 50／50 | 50／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 112/00-C | 商管／共同科 | 38／38 | 37／0 | 12／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 112/00-E | 商管／共同科 | 42／42 | 32／0 | 12／42 | 1 | 10／0 | OCR_extracted_32_of_42；automatic_answer_pairing_requires_independent_review |
| 112/00-MB | 商管／共同科 | 25／25 | 20／0 | 8／25 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 112/09-1 | 商管／共同科 | 50／50 | 48／0 | 12／50 | 1 | 1／0 | OCR_extracted_49_of_50；automatic_answer_pairing_requires_independent_review |
| 112/09-2 | 商管／共同科 | 50／50 | 50／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 113/00-C | 商管／共同科 | 38／38 | 38／0 | 12／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 113/00-E | 商管／共同科 | 42／42 | 34／0 | 12／42 | 1 | 8／0 | OCR_extracted_34_of_42；automatic_answer_pairing_requires_independent_review |
| 113/00-MB | 商管／共同科 | 25／25 | 22／0 | 8／25 | 1 | 1／0 | OCR_extracted_24_of_25；automatic_answer_pairing_requires_independent_review |
| 113/09-1 | 商管／共同科 | 50／50 | 46／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review；incomplete_answer_pdf_extraction |
| 113/09-2 | 商管／共同科 | 50／50 | 50／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 114/00-C | 商管／共同科 | 38／38 | 36／0 | 12／38 | 1 | 1／0 | OCR_extracted_37_of_38；automatic_answer_pairing_requires_independent_review |
| 114/00-E | 商管／共同科 | 42／42 | 33／0 | 12／42 | 1 | 8／0 | OCR_extracted_34_of_42；automatic_answer_pairing_requires_independent_review |
| 114/00-MB | 商管／共同科 | 25／25 | 20／0 | 8／23 | 1 | 2／0 | OCR_extracted_23_of_25；automatic_answer_pairing_requires_independent_review |
| 114/09-1 | 商管／共同科 | 50／50 | 50／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 114/09-2 | 商管／共同科 | 50／50 | 50／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 115/00-C | 商管／共同科 | 38／38 | 38／0 | 12／38 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 115/00-E | 商管／共同科 | 42／42 | 34／0 | 12／41 | 1 | 8／0 | OCR_extracted_34_of_42；automatic_answer_pairing_requires_independent_review |
| 115/00-MB | 商管／共同科 | 25／25 | 23／0 | 8／25 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 115/09-1 | 商管／共同科 | 50／50 | 49／0 | 12／50 | 1 | 0／0 | automatic_answer_pairing_requires_independent_review |
| 115/09-2 | 商管／共同科 | 50／50 | 48／0 | 12／50 | 1 | 1／0 | OCR_extracted_49_of_50；automatic_answer_pairing_requires_independent_review |

## 優先覆核清單

- 90：official_math_paper_missing。
- 91/00-E 封面疑義：91-00-E-02；保留 ID，以完整原卷核對題幹。
- 91/00-M-OLD 封面疑義：91-00-M-OLD-02, 91-00-M-OLD-03；保留 ID，以完整原卷核對題幹。
- 91/BIZ-1 封面疑義：91-BIZ-1-01, 91-BIZ-1-02, 91-BIZ-1-03；保留 ID，以完整原卷核對題幹。
- 91/BIZ-2 封面疑義：91-BIZ-2-01, 91-BIZ-2-02, 91-BIZ-2-03；保留 ID，以完整原卷核對題幹。
- 91/09-1 封面疑義：91-09-1-01, 91-09-1-02, 91-09-1-03；保留 ID，以完整原卷核對題幹。
- 91/09-2 封面疑義：91-09-2-01, 91-09-2-02, 91-09-2-03；保留 ID，以完整原卷核對題幹。
- 92：official_chinese_paper_missing。
- 92/00-E 封面疑義：92-00-E-01, 92-00-E-02, 92-00-E-03；保留 ID，以完整原卷核對題幹。
- 92/00-M-OLD 封面疑義：92-00-M-OLD-01, 92-00-M-OLD-04；保留 ID，以完整原卷核對題幹。
- 92/BIZ-1 封面疑義：92-BIZ-1-01, 92-BIZ-1-02, 92-BIZ-1-03；保留 ID，以完整原卷核對題幹。
- 92/BIZ-2 封面疑義：92-BIZ-2-01, 92-BIZ-2-02, 92-BIZ-2-03；保留 ID，以完整原卷核對題幹。
- 93/00-C 封面疑義：93-00-C-02, 93-00-C-03；保留 ID，以完整原卷核對題幹。
- 93/00-M-OLD 有 2 個題號超出候選 expectedCount，須核對封面與分卷。
- 93/09-1 封面疑義：93-09-1-01, 93-09-1-03；保留 ID，以完整原卷核對題幹。
- 93/09-2 封面疑義：93-09-2-01, 93-09-2-03；保留 ID，以完整原卷核對題幹。
- 94/00-C 封面疑義：94-00-C-01, 94-00-C-02, 94-00-C-03；保留 ID，以完整原卷核對題幹。
- 94/00-E 封面疑義：94-00-E-01, 94-00-E-02, 94-00-E-03；保留 ID，以完整原卷核對題幹。
- 94/00-MB 封面疑義：94-00-MB-01, 94-00-MB-02, 94-00-MB-03；保留 ID，以完整原卷核對題幹。
- 94/BIZ-1 封面疑義：94-BIZ-1-01, 94-BIZ-1-02, 94-BIZ-1-03；保留 ID，以完整原卷核對題幹。
- 94/BIZ-2 封面疑義：94-BIZ-2-01, 94-BIZ-2-02, 94-BIZ-2-03；保留 ID，以完整原卷核對題幹。
- 95/00-MB 封面疑義：95-00-MB-01；保留 ID，以完整原卷核對題幹。
- 110/09-1 有 1 個題號超出候選 expectedCount，須核對封面與分卷。

## 驗收及阻塞

- 結構錯誤 0；完整影像解碼：已執行。
- 缺乏原題、答案、教材覆核證據的旗標不可自動改為 true；教學草稿不算教師核實。
- 自動文字錨點不代表共享題組及跨頁內容已齊全；未可靠裁切時保留全卷原頁。
- 90 年官方答案為 HTML；91 年為跨科共用單頁，須保留完整標題及科目對照，不猜逐題答案。
- 精確教材章節、逐題教師覆核和各卷正式配分需補外部證據；N/A／待核實持續保留。
- 本報告不宣稱部署完成；commit／Actions／Pages 證據見 SUDU_PROGRESS_TRACKER.md。

