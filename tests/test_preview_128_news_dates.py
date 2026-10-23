"""Release-readiness news date checks: no future or >3-year source may count."""
import importlib.util
from datetime import date
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_preview_128_release_readiness.py"
SPEC = importlib.util.spec_from_file_location("preview_readiness", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class NewsDateEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 10, 23)

    def test_three_year_lower_boundary_inclusive(self):
        self.assertTrue(mod.is_recent_news_iso_date("2023-10-23", self.today))

    def test_date_before_three_year_boundary_rejected(self):
        self.assertFalse(mod.is_recent_news_iso_date("2023-10-22", self.today))

    def test_today_valid_and_future_rejected(self):
        self.assertTrue(mod.is_recent_news_iso_date("2026-10-23", self.today))
        self.assertFalse(mod.is_recent_news_iso_date("2026-10-24", self.today))

    def test_iso_date_format_and_actual_calendar_required(self):
        for bad in ("", "2026/10/20", "20260202", "2026-02-30", "2025-10-01 ", None, False, 20260101):
            with self.subTest(bad=bad):
                self.assertFalse(mod.is_recent_news_iso_date(bad, self.today))

    def test_leap_day_three_year_cutoff(self):
        self.assertTrue(mod.is_recent_news_iso_date("2021-02-28", date(2024, 2, 29)))
        self.assertFalse(mod.is_recent_news_iso_date("2021-02-27", date(2024, 2, 29)))

    def test_real_current_source_date(self):
        self.assertTrue(mod.is_recent_news_iso_date("2025-12-12", self.today))
        self.assertTrue(mod.is_recent_news_iso_date("2026-09-17", self.today))


if __name__ == "__main__":
    unittest.main()
