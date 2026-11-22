"""Real Git export/build regressions; authority is SYNTHETIC unit data only.

These tests do not create an E receipt, first response, formal G8 or admission.
They reproduce working-directory contamination using the real stage builder.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

from PIL import Image
from scripts import build
from scripts import sudu_g8_release_bridge as bridge
import test_sudu_g8_release_bridge as bridge_fixtures


class CommittedBuildTests(unittest.TestCase):
    def setUp(self):
        self.case = bridge_fixtures.BridgeTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.case.build_patch.stop()
        self.case.patches[4].stop()  # Use real committed code bindings.
        self.code = self.case.root / "code"
        self.code.mkdir()
        for rel in bridge.CODE:
            target = self.code / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(bridge.ROOT / rel, target)
        self.original = {
            "index.html": b'<script id="catalog" type="application/json">[]</script>',
            "assets/example.svg": b'<svg xmlns="http://www.w3.org/2000/svg"><title>Committed</title></svg>',
            "sudu/data/exam-schedule.json": b'{"origin":"committed"}\n',
            ".gitignore": b'assets/ignored.svg\n',
        }
        image = io.BytesIO()
        Image.new("RGB", (100, 100), "white").save(image, format="WEBP", lossless=True)
        self.crop_source = "sudu/data/original/115/00-MB/page.webp"
        self.original[self.crop_source] = image.getvalue()
        self.crop_config = "sudu/demo-question-crops.json"
        self.original[self.crop_config] = bridge.serialized({"crops": [{
            "source": self.crop_source, "output": "sudu/questions/115/math/q01.webp",
            "box": [5, 5, 95, 30], "subject": "Synthetic crop", "question": 1,
        }]})
        for rel, raw in self.original.items():
            target = self.code / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        for args in [("init", "-q"), ("config", "user.name", "Synthetic Test"),
                     ("config", "user.email", "synthetic@example.invalid"),
                     ("add", "-A"), ("commit", "-qm", "SYNTHETIC CODE BUILD INPUTS")]:
            subprocess.run(["git", "-C", str(self.code), *args], check=True,
                           stdout=subprocess.DEVNULL)
        self.commit = bridge.git(self.code, "rev-parse", "HEAD")
        root_patch = patch.object(bridge, "ROOT", self.code)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def stage(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.case.stage_it()
        return self.case.stage

    def validate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return bridge.validate_stage(self.case.source, self.case.stage, self.case.private)

    def test_clean_snapshot_uses_real_builder_and_exact_commit(self):
        stage = self.stage()
        manifest, _, _ = self.validate()
        self.assertEqual(manifest["codeCommit"], self.commit)
        for rel in ("assets/example.svg", "sudu/data/exam-schedule.json", self.crop_source):
            self.assertEqual((stage / "site" / rel).read_bytes(), self.original[rel])
        self.assertEqual(json.loads((stage / "site/sudu/release.json").read_bytes())["commit"], self.commit)
        self.assertTrue((stage / "site/sudu/questions/115/math/q01.webp").is_file())
        self.assertFalse((stage / "site/.gitignore").exists())

    def test_untracked_and_ignored_public_files_never_enter_expected_build(self):
        bindings = bridge.code_bindings()
        for rel in ("untracked-public.html", "assets/ignored.svg"):
            (self.code / rel).write_text("UNCOMMITTED PUBLIC CONTENT", encoding="utf-8")
        stage = self.stage()
        self.assertEqual(bridge.code_bindings(), bindings)
        self.assertEqual(bridge.git(self.code, "rev-parse", "HEAD"), self.commit)
        for rel in ("untracked-public.html", "assets/ignored.svg"):
            self.assertFalse((stage / "site" / rel).exists())
        self.assertNotIn("untracked-public.html", (stage / "site/index.html").read_text())
        self.validate()
        # The attacker cannot make the verifier admit the ignored file by resealing.
        rel = "untracked-public.html"
        (stage / "site" / rel).write_bytes(b"RESEALED EXTRA")
        manifest_path = stage / "stage.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["siteFiles"][rel] = bridge.sha(b"RESEALED EXTRA")
        manifest_path.write_bytes(bridge.serialized(manifest))
        with self.assertRaisesRegex(bridge.Hold, "reproducible native"):
            self.validate()

    def test_modified_assets_data_and_crop_inputs_do_not_change_pinned_output(self):
        clean = self.stage()
        clean_manifest = (clean / "stage.json").read_bytes()
        clean_crop = (clean / "site/sudu/questions/115/math/q01.webp").read_bytes()
        shutil.rmtree(clean)
        bindings = bridge.code_bindings()
        for rel in ("assets/example.svg", "sudu/data/exam-schedule.json", self.crop_source, self.crop_config):
            (self.code / rel).write_bytes(b"MUTABLE WORKTREE CONTENT")
        with patch.dict(os.environ, {"SUDU_BUILD_SHA": "f" * 40}):
            stage = self.stage()
            self.validate()
        self.assertEqual(bridge.code_bindings(), bindings)
        self.assertEqual((stage / "stage.json").read_bytes(), clean_manifest)
        self.assertEqual((stage / "site/sudu/questions/115/math/q01.webp").read_bytes(), clean_crop)
        # Resealing to the altered worktree asset no longer changes expected bytes.
        rel = "assets/example.svg"
        (stage / "site" / rel).write_bytes((self.code / rel).read_bytes())
        manifest_path = stage / "stage.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["siteFiles"][rel] = bridge.sha((stage / "site" / rel).read_bytes())
        manifest_path.write_bytes(bridge.serialized(manifest))
        with self.assertRaisesRegex(bridge.Hold, "reproducible native"):
            self.validate()

    def test_sparse_or_symlinked_worktree_assets_use_git_objects(self):
        (self.code / "assets/example.svg").unlink()
        (self.code / self.crop_source).unlink()
        (self.code / self.crop_source).symlink_to(self.code / "index.html")
        stage = self.stage()
        self.assertEqual((stage / "site/assets/example.svg").read_bytes(), self.original["assets/example.svg"])
        self.assertEqual((stage / "site" / self.crop_source).read_bytes(), self.original[self.crop_source])
        self.validate()

    def test_committed_symlink_or_archive_transform_is_rejected(self):
        cases = ("symlink", "export-ignore", "export-subst")
        for case in cases:
            with self.subTest(case=case):
                if case == "symlink":
                    (self.code / "bad.html").symlink_to("index.html")
                elif case == "export-ignore":
                    (self.code / "bad.html").unlink()
                    (self.code / ".gitattributes").write_text("assets/example.svg export-ignore\n")
                else:
                    (self.code / ".gitattributes").write_text("assets/example.svg export-subst\n")
                    (self.code / "assets/example.svg").write_bytes(b"$Format:%H$")
                for args in [("add", "-A"), ("commit", "-qm", "SYNTHETIC INVALID BUILD INPUT")]:
                    subprocess.run(["git", "-C", str(self.code), *args], check=True,
                                   stdout=subprocess.DEVNULL)
                commit = bridge.git(self.code, "rev-parse", "HEAD")
                with self.assertRaises(bridge.Hold):
                    bridge.build_committed_site(commit, self.case.root / ("output-" + case))


if __name__ == "__main__":
    unittest.main()
