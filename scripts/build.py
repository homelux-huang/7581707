"""Build the public site and embed a recursive HTML catalog into index.html."""

import hashlib
import json
import os
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Public deployment is opt-in. Never copy the repository wholesale: it also
# contains the private API, database, test fixtures and deployment credentials.
PUBLIC_ASSET_SUFFIXES = {".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".woff", ".woff2"}
PUBLIC_DATA_FILES = {
    "sudu/data/index.json", "sudu/data/scoring-rules.json",
    "sudu/data/official-paper-catalog.json", "sudu/data/corpus-audit.json",
    "sudu/data/hover-cards.json", "sudu/data/exam-schedule.json",
    "sudu/data/original/index.json", "sudu/data/original/answers.json",
    "sudu/data/approved/114.json", "sudu/data/approved/115.json",
    "sudu/data/approved/progress.json",
    "sudu/data/approved/preview/114.json", "sudu/data/approved/preview/115.json",
}
PRIVATE_NAME = re.compile(r"(?:^|[-_.])(?:private|secret|credentials?|tokens?|students?|backups?|restore|sessions?|\.env)(?:$|[-_.])", re.I)


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)


def included(path):
    """An explicit publish allowlist, including original tools at the root."""
    if any(part.startswith(".") or PRIVATE_NAME.search(part) for part in path.parts):
        return False
    text = path.as_posix()
    suffix = path.suffix.lower()
    if len(path.parts) == 1:
        return suffix in {".html", ".htm"}
    if path.parts[0] == "assets":
        return suffix in PUBLIC_ASSET_SUFFIXES
    if path.parts[0] != "sudu":
        return False
    if len(path.parts) == 2:
        return suffix in {".html", ".htm", ".js", ".css"}
    if text in PUBLIC_DATA_FILES:
        return True
    if re.fullmatch(r"sudu/data/approved/webp/(?:114|115)/(?:114|115)-(?:00-C|00-E|00-MB|09-1|09-2)-(?:[0-9]{2}|SHARED-[0-9]{2}-[0-9]{2})\.webp", text):
        return True
    if re.fullmatch(r"sudu/data/years/\d{2,3}\.json", text):
        return True
    if re.fullmatch(r"sudu/data/original/(?:answers/)?\d{2,3}/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+\.webp", text):
        return True
    return False


def catalog(root):
    entries = []
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix().casefold()):
        relative = path.relative_to(root)
        if (not path.is_file() or path.is_symlink() or not included(relative)
                or path.suffix.lower() not in {".html", ".htm"}
                or relative.as_posix() == "index.html"):
            continue
        parser = TitleParser()
        parser.feed(path.read_text(encoding="utf-8-sig", errors="replace"))
        title = " ".join("".join(parser.parts).split()) or path.stem
        entries.append({"title": title, "path": relative.as_posix()})
    return entries


def embed(template, entries):
    data = json.dumps(entries, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    pattern = r'(<script id="catalog" type="application/json">).*?(</script>)'
    result, count = re.subn(pattern, lambda m: m[1] + data + m[2], template, flags=re.DOTALL)
    if count != 1:
        raise ValueError("Expected exactly one catalog placeholder")
    return result



def generate_demo_question_crops(output):
    """Generate single-question WebP assets from existing official page WebPs.

    This is a pixel crop only: no OCR, redraw, interpolation, or content rewrite.
    The crop map is reviewable in sudu/demo-question-crops.json.
    """
    config_path = ROOT / "sudu" / "demo-question-crops.json"
    if not config_path.exists():
        return []
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to generate demo single-question WebPs") from exc

    data = json.loads(config_path.read_text(encoding="utf-8"))
    manifest = []
    seen_outputs = set()
    for item in data.get("crops", []):
        source_rel = Path(item["source"])
        output_rel = Path(item["output"])
        if source_rel.suffix.lower() != ".webp" or output_rel.suffix.lower() != ".webp":
            raise ValueError(f"Question crop must use WebP: {item}")
        if output_rel.as_posix() in seen_outputs:
            raise ValueError(f"Duplicate question crop output: {output_rel}")
        seen_outputs.add(output_rel.as_posix())
        if not output_rel.as_posix().startswith("sudu/questions/115/"):
            raise ValueError(f"Unexpected crop output path: {output_rel}")

        source = ROOT / source_rel
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"Missing official source WebP: {source_rel}")
        box = tuple(int(v) for v in item["box"])
        if len(box) != 4:
            raise ValueError(f"Invalid crop box: {item}")
        left, top, right, bottom = box

        with Image.open(source) as image:
            width, height = image.size
            if image.format != "WEBP":
                raise ValueError(f"Official source is not WebP: {source_rel}")
            if not (0 <= left < right <= width and 0 <= top < bottom <= height):
                raise ValueError(f"Crop exceeds source bounds {width}x{height}: {item}")
            crop_width, crop_height = right - left, bottom - top
            # Reject accidental whole-page publication. q30 is the tallest because
            # its official diagram is shared with q31, but the crop still excludes q31.
            if crop_height >= int(height * 0.60) or crop_width < int(width * 0.70):
                raise ValueError(f"Crop does not look like a single-question strip: {item}")
            cropped = image.crop(box)
            target = output / output_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            cropped.save(target, format="WEBP", lossless=True, method=6)

        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        manifest.append({
            "subject": item["subject"],
            "question": item["question"],
            "source": source_rel.as_posix(),
            "crop": list(box),
            "sourceSize": [width, height],
            "output": output_rel.as_posix(),
            "outputSize": [crop_width, crop_height],
            "sha256": digest,
            "ocrPerformed": False,
        })

    manifest_path = output / "sudu" / "questions" / "115" / "crop-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({
        "year": 115,
        "generatedCount": len(manifest),
        "rule": "single-question pixel crops from existing official WebP pages; no OCR",
        "items": manifest,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest

def build():
    output = ROOT / "_site"
    # _site is always generated; never remove any source file.
    if output.exists():
        shutil.rmtree(output)

    output.mkdir(parents=True)
    copied = 0
    for source in sorted(ROOT.rglob("*")):
        relative = source.relative_to(ROOT)
        if not source.is_file() or not included(relative):
            continue
        # Reject symlinked files AND parent directories before reading any bytes.
        if source.is_symlink() or any(parent.is_symlink() for parent in source.parents if parent != ROOT.parent):
            raise ValueError(f"Refusing public symlink: {relative}")
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
    # Apply a progressive, QA-gated adapter to the existing V4 file at build
    # time. The source HTML, embedded 35-question Demo, and its keys stay intact.
    v4 = output / "sudu" / "v4-115-multisubject-review-demo.html"
    if v4.is_file():
        original_v4 = v4.read_text(encoding="utf-8")
        needle = "</body>"
        if original_v4.count(needle) != 1:
            raise ValueError("Missing unique V4 closing body tag")
        adapter = output / "sudu" / "verified-questions-runtime.js"
        if not adapter.is_file():
            raise ValueError("Verified V4 adapter missing from public artifact")
        # GitHub Pages/browser caches must never keep showing an old UI script.
        adapter_revision = hashlib.sha256(adapter.read_bytes()).hexdigest()[:12]
        v4.write_text(original_v4.replace(
            needle,
            f'<script src="./verified-questions-runtime.js?v={adapter_revision}"></script>\n</body>'
        ), encoding="utf-8")
    crop_manifest = generate_demo_question_crops(output)
    entries = catalog(ROOT)
    template = (ROOT / "index.html").read_text(encoding="utf-8")
    (output / "index.html").write_text(embed(template, entries), encoding="utf-8")
    (output / ".nojekyll").touch()
    revision = os.environ.get("SUDU_BUILD_SHA", "")
    if revision and re.fullmatch(r"[0-9a-f]{40}", revision):
        (output / "sudu" / "release.json").write_text(json.dumps({"commit": revision, "testsRequired": True}) + "\n", encoding="utf-8")
    print(f"PASS: public allowlist copied {copied} files; generated {len(crop_manifest)} single-question WebPs; catalog generated for {len(entries)} HTML files")


if __name__ == "__main__":
    build()
