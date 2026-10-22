"""A private database or student backup must never enter a public Pages artifact."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("public_build", Path(__file__).resolve().parents[1] / "scripts/build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class PublicBuildPrivacy(unittest.TestCase):
    def test_public_allowlist(self):
        for path in ["sudu/data/approved/114.json", "sudu/data/approved/115.json", "sudu/data/approved/progress.json", "sudu/data/approved/preview/114.json", "sudu/data/approved/preview/115.json", "sudu/data/approved/webp/115/115-09-2-27.webp", "sudu/data/approved/webp/115/115-00-E-SHARED-21-24.webp", "index.html", "原工具.html", "assets/share.js", "sudu/admin.html", "sudu/data/years/115.json", "sudu/data/original/114/09-2/p001-abcd.webp", "sudu/data/original/answers/114/09-2/p001-abcd.webp"]:
            self.assertTrue(build.included(Path(path)), path)
        for path in ["sudu/data/processed/115/questions.json", "sudu/data/processed/114/question-bank.sqlite3", "sudu/data/approved/webp/115/private.webp", "backend/private.sqlite3", "backend/private.sqlite3-wal", ".env", "render-admin.yaml", "tests/private.json", "sudu/student-backup.json", "sudu/data/student-backup.json", "sudu/data/years/secrets.json", "assets/private.json", "assets/.env", "sudu/data/original/private.sqlite3", "docs/SUDU_HANDOFF.md"]:
            self.assertFalse(build.included(Path(path)), path)

    def test_build_never_copies_private_files(self):
        previous = build.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            build.ROOT = Path(tmp)
            for name, content in {
                "index.html": '<script id="catalog" type="application/json">[]</script>',
                "sudu/index.html": "<title>速讀</title>",
                "sudu/data/index.json": "{}",
                "backend/private.sqlite3": "private student records",
                "backend/private.sqlite3-wal": "private uncheckpointed records",
                "sudu/data/student-backup.json": '{"accessToken":"secret"}',
                "assets/private.json": '{"password":"secret"}',
                ".env": "SUDU_ADMIN_INITIAL_PASSWORD=secret",
            }.items():
                p = build.ROOT / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
            try:
                build.build()
                published = [p.relative_to(build.ROOT / "_site").as_posix() for p in (build.ROOT / "_site").rglob("*") if p.is_file()]
                self.assertEqual(sorted(published), [".nojekyll", "index.html", "sudu/data/index.json", "sudu/index.html"])
            finally:
                build.ROOT = previous

    def test_symlink_cannot_smuggle_private_data(self):
        previous = build.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            build.ROOT = Path(tmp)
            (build.ROOT / "index.html").write_text('<script id="catalog" type="application/json">[]</script>')
            (build.ROOT / "private.sqlite3").write_text("private records")
            (build.ROOT / "leak.html").symlink_to(build.ROOT / "private.sqlite3")
            try:
                with self.assertRaises(ValueError):
                    build.build()
            finally:
                build.ROOT = previous


if __name__ == "__main__":
    unittest.main()
