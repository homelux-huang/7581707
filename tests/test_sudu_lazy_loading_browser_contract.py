"""Protect real original WebP decode: do not replace with mock success or catch errors."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
JS=(ROOT/"tests"/"sudu_certified_positive_browser.cjs").read_text(encoding="utf-8")


class LazyOriginalWebpContract(unittest.TestCase):
    def test_trigger_lazy_load_before_actual_decode(self):
        scroll=JS.index("await img.scrollIntoViewIfNeeded()")
        wait=JS.index("await page.waitForFunction",scroll)
        complete=JS.index("el.complete && el.naturalWidth>0",wait)
        decode=JS.index("await el.decode()",complete)
        assert scroll<wait<complete<decode
        self.assertIn("await page.waitForFunction",JS)
        self.assertIn("{timeout:20000}",JS)
        self.assertIn("img.evaluate(async el=>{await el.decode();return el.naturalWidth>0}",JS)

    def test_no_qa_bypass_or_fake_image(self):
        # Keep actual approved original WebP request, and fail closed on
        # missing/corrupt pixels rather than swallowing decode exceptions.
        self.assertIn("image:'data/approved/webp/115/115-00-MB-03.webp'",JS)
        self.assertIn("imageSha256:'03d5f494eb30b1fc452586e5bf1d1de5a917ba2cc98291e8bace8273b8a6872b'",JS)
        self.assertIn("await el.decode()",JS)
        self.assertNotIn("catch(()=>true)",JS)
        self.assertNotIn("catch { return true",JS)
        self.assertNotIn("naturalWidth || 1",JS)

    def test_two_positive_student_questions_and_noncalc_gate_remain(self):
        self.assertIn("const conceptual=",JS)
        self.assertIn("assert.equal(await page.locator('#guideCard .calculation-step').count(),0",JS)
        self.assertIn("for(const [width,height] of sizes)",JS)
        self.assertIn("for(const theme of ['light','dark'])",JS)


    def test_original_approved_five_not_old_four_and_all_decode(self):
        real = (ROOT/"tests"/"sudu_real_reviewed_browser.cjs").read_text(encoding="utf-8")
        self.assertIn("const IDs=['115-00-MB-02','115-00-MB-03','115-00-MB-04','115-00-MB-05','115-00-MB-09']", real)
        self.assertIn("const answers=['A','A','C','B','A']", real)
        self.assertIn("assert.equal(source.approvedCount,IDs.length)", real)
        self.assertIn("for(let i=0;i<IDs.length;i++)", real)
        self.assertIn("i===IDs.length-1", real)
        self.assertIn("i<IDs.length-1", real)
        self.assertIn("await img.scrollIntoViewIfNeeded()", real)
        self.assertIn("await el.decode();return el.naturalWidth>0&&el.naturalHeight>0", real)
        self.assertNotIn("source.approvedCount,4", real)
        self.assertNotIn("for(let i=0;i<4;i++)", real)
        self.assertNotIn("catch(()=>true)", real)

if __name__=="__main__":
    unittest.main()
