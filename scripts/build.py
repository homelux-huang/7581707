"""Build the public site and embed a recursive HTML catalog into index.html."""

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
    entries = catalog(ROOT)
    template = (ROOT / "index.html").read_text(encoding="utf-8")
    (output / "index.html").write_text(embed(template, entries), encoding="utf-8")
    (output / ".nojekyll").touch()
    revision = os.environ.get("SUDU_BUILD_SHA", "")
    if revision and re.fullmatch(r"[0-9a-f]{40}", revision):
        (output / "sudu" / "release.json").write_text(json.dumps({"commit": revision, "testsRequired": True}) + "\n", encoding="utf-8")
    print(f"PASS: public allowlist copied {copied} files; catalog generated for {len(entries)} HTML files")


if __name__ == "__main__":
    build()
