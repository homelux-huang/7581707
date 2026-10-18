"""Build the public site and embed a recursive HTML catalog into index.html."""

import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"_site", "scripts", "tests", "node_modules", "__pycache__"}


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
    return not any(part.startswith(".") or part in EXCLUDED for part in path.parts)


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

    def ignore(directory, names):
        return [name for name in names if name.startswith(".") or name in EXCLUDED
                or name in {"README.md", "LICENSE"}]

    shutil.copytree(ROOT, output, ignore=ignore, symlinks=False)
    entries = catalog(ROOT)
    template = (ROOT / "index.html").read_text(encoding="utf-8")
    (output / "index.html").write_text(embed(template, entries), encoding="utf-8")
    (output / ".nojekyll").touch()
    print(f"PASS: catalog generated for {len(entries)} HTML files")


if __name__ == "__main__":
    build()
