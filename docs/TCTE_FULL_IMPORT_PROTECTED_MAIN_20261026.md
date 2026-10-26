# Protected-main staging for TCTE original images

Run 40231846450 successfully rendered and audited the corpus (128 papers, 1,044 pages, 5,313 question links, zero reported image errors), then failed only because the workflow attempted a direct push to protected main.

This candidate keeps the no-OCR and decode audit. Changed source artifacts are pushed with a remote-SHA force-with-lease to `automation/tcte-original-image-candidate`, then exposed through a Draft PR opened by the authorized MASTER connector. GitHub Actions is intentionally not allowed to create or approve pull requests in this repository; the workflow reports the staged branch instead of weakening that policy. It does not dispatch Pages or promote any question. The Draft PR is only a reviewable source candidate; per-question source QA, official-answer review, teaching, independent E, V4 UI, READY and LIVE remain separate.

The workflow checkout remains pinned to main so a run triggered while reviewing this infrastructure patch cannot copy the patch itself into the generated source candidate. Protected-main integration of this workflow still requires the normal PR check.

