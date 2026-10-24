# 115 年逐題可核實發布證據 — 2026-10-24

本輪實際執行，非發布核准。完整 205 題逐題檢查與缺件清單在 `release-evidence-115-20261024.json`。

- 來源固定 SHA：`ed832065d1eaebbb836d4264c9b32f944a2e082e`。
- 正式發布器固定 main SHA：`88b87451f776e95be05e2ecb51bcb8781ebd8b0b`，使用 main 現有 additive review adapter，避免舊教學分支發布器漏計已核准四題。
- SQLite integrity 與 205 筆 JSON/payload/payload SHA 實際逐筆比對 PASS。
- 205/205 單題 WebP 原始位元組 SHA、Pillow 解碼通過。這不是新增 205 題目視或教學驗收。
- 125/205 通過既有 image evidence 結構門檻；80 題仍缺符合該門檻的影像證據。
- 現有發布器可接納：數學 B 02、03、04、09，共 4 題；均為既有資格，不是本輪新核准。
- 其餘 201 題缺完整來源、官方最終、獨立解題、教學/UI與SHA憑證接入。官方答案已核對的旁證仍存在，缺接入不代表官答一定未核對。
- 新核准 0、新部署 0。main 的其他 Session 部署不計入本輪成果。

## 數學 B 05 本輪新增實質證據

親自開啟 `webp-v2/00-MB/115-00-MB-05.webp`：題號、完整題幹、四選項與分數均清楚，無相鄰題。位元組 SHA `be5bb1f0e23eddff9e8a0f17e6e116ce2ce4219205f4527d50a710fb76e20dd2`。

來源分支修正後 JSON/SQLite 相符；本輪保留其原始資料，另外提交 `115-00-MB-05-pedagogy-review-20261024.json`：補齊四選項 reason、計算 substitution、逐行求 a/b 與 BC 中點、國小口語說明。Python Fraction 重算 C=(3,-2)、中點=(3/2,-7/2)，符合已知官答 B。這是已知官答後複核，未冒充事前盲解。

仍缺：依既有發布介面接入 SHA/revision 相符之 OCR、官方、既存事前盲解文件；教學內容的正式審核封裝；使用實際完整題幹選項與本次教學 digest 的 8 RWD×2主題逐題 UI證據。不得把舊 E03 或 MathB19–25 的 CI 當成此題 UI憑證，也不得僅為通過檢查設定批准旗標。

## 重現

使用上述兩個精確 commit checkout；在教學分支執行：

```sh
python scripts/audit_115_release_evidence.py --source /path/to/source-checkout --publisher /path/to/main-checkout --output /tmp/release-evidence.json
cmp /tmp/release-evidence.json sudu/teaching-drafts/preview-128-20261023/release-evidence-115-20261024.json
```

新增 `115-release-evidence-audit.yml` 使用固定來源與發布器 SHA，在 GitHub Actions 重跑205題並逐位元組比對報告。CI結論必須讀取實際 run，不以 workflow 檔案存在宣稱成功。
