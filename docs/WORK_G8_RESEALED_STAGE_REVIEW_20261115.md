# G8 staged renderer reseal 漏洞：獨立審查與修正候選

2026-11-15（台灣）。接續 main→PR211→PR213→PR214，不是正式題目發布。

## 真實獨立程式審查

依使用者既有平行角色授權，由工具建立全新、未承接作者對話的程式審查代理 `/root/independent_release_security`。審查者沒有編寫被審程式，唯讀檢查 main ceda0a0248cb7dc99941758e9e16582e463516ca 至 PR214 ecfb0115af9ae1c16557ad3c8d65d3d1a5a06378 全部13個變更檔案及相關 native gate。實際跑137項既有測試（1skip）、Node語法檢查與額外再現。

這個工具代理的任務定位只作 code-review provenance；不得冒充原 B/C/E 的平台 Session、G6/G7、真人 GitHub reviewer 或正式發布簽核。

## P1：確認可再現的驗證缺口

舊 `validate_stage` 比較 served files 與同一份可寫 manifest 內的 `siteFiles`，並檢查 ROOT 的 codeBindings。若 stage owner 或被入侵的私有 runner 更換 served runtime/HTML，再更新 manifest 自述的 hash，ROOT 的 committed codeBindings 可以不變，驗證仍接受。

審查者以明確 synthetic authority fixture 實際再現：建立 stage→替換 runtime→重封其 siteFiles hash→呼叫正式 validate_stage，舊版接受。既有測試只有改檔而沒有重封 manifest，因此漏掉。

前提是可寫 stage 的身分；不是無權限外部網路攻擊。0700減少可接觸者，但不能取代原程式到實際 served bytes 的一致性驗證。

## 本修正

- 在原 source/code/auth/manifest/file/payload/row 核驗之外，從相同凍結 source 與固定 code 重新產生 native stage 到另一個私有 OS-temp 路徑。
- 與獨立重建的完整 manifest 比較，包含 canonical payload path、所有 served-file map、版本與授權關聯；再比較完整 payload bytes。
- 原輸入、教材、來源、信任政策不變。不使用額外自行宣告的 hash 解決問題，不產生假 UI PASS。
- 重建輸出僅在私有 temp，離開即清除；重建過程 stdout 不污染 verify-stage JSON。呼叫鏈 validate_stage→stage→native pub.stage，不遞迴呼叫 validate_stage。
- 新負向測試同時改 runtime／HTML／annual JSON及相應manifest hash，並測改payloadPath＋重封map；全部必須拒絕。
- Formal workflow明確增加 `actions: read`，供既有已核准題目的原 run/job metadata核驗；不增加 secrets/write/付款權限。

## 獨立復核

同一未寫程式的審查者實際確認原再現被拒絕，錯誤為 `stage differs from reproducible native source/code output`；26項 bridge/archive 測試全數成功，包括正常 synthetic same-byte native promotion與durable promotion。審查的核心修正 SHA256：

- bridge：c8952b804c5d1d397911d6925807704ee38c5b26dd5743a5b9551bd73d731f77
- bridge tests：1d5c334dc556395c0924b043d86c7bacc6f86d405236ddf86bf1cebc3450847d
- formal workflow：282a37226ff04b9f1e6b2a64f893c0690ae46b922351ed8c9e65645e1f2eac3d

P1對上述精確bytes已修正。完整GitHub exact-head CI仍須另外完成。

## 限制與發布界線

- Synthetic測試mock authority/build/codeBindings，不是真實E/G6/G8。另有專用CI對真正乾淨完整checkout重建公開baseline兩次並比對每個檔案，避免只驗證fake builder。
- 真正執行仍要求乾淨、受控的checkout與runner；其他build inputs和untracked files不得被不受信任者污染。
- Durable archive仍仰賴獨立owner在原artifact可核對時審查並pin。Capture JSON本身不是獨立的provider attestation。原真實run/job、protected main及原ZIP/PNG仍核驗。
- 本審查沒有GitHub帳號獨立核准、原作者/E平台身分、真實G6/G7、正式瀏覽器16/16或學生發布證據。
- E11原凍結有效；E12另行HOLD。所有新題仍須原V1、G0–G10、正常PR/CI/Pages same-SHA verify_live。
