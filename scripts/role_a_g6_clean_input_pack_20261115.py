#!/usr/bin/env python3
"""Build answer-hidden, source-only inputs for a genuinely separate G6 operator.

Never feed the operator-only manifest, this script, GitHub links, or QA notes to
the answering model. Only one question.txt plus its matching original.webp.
This code neither solves questions nor produces a G6/G7 approval.
"""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G2_DIR = "sudu/data/processed/{year}/review-evidence"
PINS = {
    "114-00-E-07": ("114", "20261115", "8bfaec5c49073d81e6527011ac5bf0399b849ae66443410ed37b75ee689ccf3c", "0d1a3281ddbd71d4f2f4778711306861b73410132d8eb5f792a077c75af0fffc", "0f15f815042afd2520144343db6b75ef2e7dbe32", "f7017cb2c5ba750c7c05b959d3d59016945d039f"),
    "114-00-E-11": ("114", "20261107", "646ad13eb26e078e761a7e0e21aadcfec6fb5576f81c124f301ba55fe4c24036", "ae29a18258d0939179abb3acd16aad183d21e1b1dbbfa6f2a5c0f6fd188a1da0", "b9afe6661d89558310b930acf94afeec58464a05", "50f8fde174f4f0e66dc0f2315c11c5a73cec6b7a"),
    "114-00-E-12": ("114", "20261107", "0c7e5de97cd151539927df8c7fc778a1b853aa0367df650ad1fe081240fd40ec", "99363268828d9efa01c24952dccbd392f15ba180e8a6bfc332268b9d4c705f60", "7f1fd3c95f11cafc561d740c2bac6188ef80da5c", "def397fcc0693d90de40b051fdf4c7c85b4567ce"),
    "115-00-MB-20": ("115", "20261110", "2016fe36733d5e1ad18958ecb8a705c809e5e682744ea8a552f5c85245e9465c", "f9e68d9c5777f25464c9df59329659e94c58dd33d2eb9ba9aa418a30055cdedf", "90dfde966be01d01674f1419ab3730b9750fb451", "bd77281f8ee755074cf3b7ebcada5c06f3720c12"),
    "115-00-MB-21": ("115", "20261108", "817517b0441c94e000db44c02e3054564d3c556842ec11203fbfae774e2bf3f9", "b8414cce472ac1ce9d6b6b7ab6939b4eef933422cf5b13cc64d07731dab90693", "d738f2eec5b9337721b7a959b0418cce38b6baa6", "75d9bcf6d0d921a6f7a40fd6383d0cd4680398bf"),
    "115-00-MB-22": ("115", "20261108", "7d35b087cad2db1f01df356dd154292e60a51babc56028db7f0022b40992dd17", "3bc277802613d00f5525a3de74c7591898ac5b6c70abbb1a8cfda04e577ccb55", "234f2f77007785f8dcc06ec4f485576a1e4e81e4", "491e02cabe4110d62b510075914e083b51e58ebf"),
    "115-00-MB-23": ("115", "20261110", "9454574017bc425f8c9a1c9854ca81547ff4b210b0c3ddc786d9e00ce1cc9fd4", "2639fb90152b9bcd5b6540e33317046d833fb4be106dbb9551baf75627589d51", "58937614cce5f404f69aa05ba05a94e9f26f9ddf", "f8c1fa03e8e97b7d7dae789c8ecf9cd618058bbb"),
    "115-00-MB-24": ("115", "20261114", "9357c0f8f30ab131f8450c8a9b45d34942fdd8207c6aac688f4f3847a55e8267", "c022bdc2927532ef6ddb5601d692e2f6accc943d1cc5b0041c9515334295dfeb", "7999ac501848acd5d1898e9a9a44db44e94c857e", "cfe5c8eeaf4496d5d98856f96a2c310186ef5893"),
    "115-00-MB-25": ("115", "20261114", "8b29dffa0c37abd1b37989878a9f8d34392ba71a04017ca1591d6fa45ec9cb6f", "92f1b7b313c109b8e0a5a22bbb7396306e3c9e2ad1dcd4b4195d973645733896", "aea980db08c02d4ac1abfe4b183a78a6d7bd6cd5", "10adb24ab36c35bd86b63c0d3ab4cb83b757393f"),
}
BANK_BLOBS = {
    "114": "dd4d822b8b875a488c38518dc25b0409b1f7ed20",
    "115": "7abb956b6b4beee49513f8f8304a2d15199eb5e2",
}

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def require(cond, reason):
    if not cond:
        raise ValueError(reason)

def render(g2, qid):
    question = g2.get("question")
    options = g2.get("options")
    require(isinstance(question, str) and bool(question.strip()), f"{qid}: blank question")
    require(isinstance(options, list) and len(options) == 4
            and all(isinstance(x, str) and x.strip() for x in options),
            f"{qid}: not four complete choices")
    pieces = [question.rstrip("\n")]
    if qid == "115-00-MB-23":
        table = g2.get("originalSourceTable")
        require(isinstance(table, dict) and table.get("title") == "表（二）",
                "MB23: missing ORIGINAL table")
        cols, rows = table.get("columns"), table.get("rows")
        require(isinstance(cols, list) and len(cols) == 3
                and isinstance(rows, list) and len(rows) == 2
                and all(isinstance(r, list) and len(r) == 3 for r in rows),
                "MB23: ORIGINAL table is not 3 columns / 2 data rows")
        pieces += [table["title"] + "\n"
                   + "\n".join(" | ".join(map(str, r)) for r in [cols, *rows])]
    pieces += ["\n".join(f"({letter}) {option}" for letter, option in zip("ABCD", options))]
    return ("\n\n".join(pieces) + "\n").encode("utf-8")

def load_sources(repo_root=ROOT):
    banks = {}
    for year, blob in BANK_BLOBS.items():
        path = repo_root / f"sudu/data/processed/{year}/questions.json"
        raw = path.read_bytes()
        require(git_blob(raw) == blob, f"{year}: bank Git Blob changed")
        bank = json.loads(raw)
        require(len(bank.get("questions", [])) == 205, f"{year}: not 205 questions")
        ids = [q.get("questionId") for q in bank["questions"]]
        require(len(set(ids)) == 205, f"{year}: duplicate QIDs")
        banks[year] = {q["questionId"]: q for q in bank["questions"]}
    result = {}
    for qid, (year, date, revision, webp_sha, g2_blob, image_blob) in PINS.items():
        path = repo_root / G2_DIR.format(year=year) / f"{qid}-ocr-publisher-{date}.json"
        data = path.read_bytes()
        require(git_blob(data) == g2_blob, f"{qid}: G2 Git Blob mismatch")
        g2 = json.loads(data)
        require(g2.get("questionId") == qid, f"{qid}: G2 QID mismatch")
        require(g2.get("questionRevision") == revision, f"{qid}: G2 revision changed")
        require(g2.get("webpSha256") == webp_sha, f"{qid}: G2 image mismatch")
        q = banks[year].get(qid)
        require(q is not None, f"{qid}: missing canonical row")
        require(q.get("question") == g2["question"] and q.get("options") == g2["options"],
                f"{qid}: canonical text differs from G2")
        require(q.get("questionVerified") is True and q.get("answerVerified") is True,
                f"{qid}: source not admitted; do not allow G6 prep")
        image_path = q.get("assets", {}).get("singleQuestionWebp")
        require(isinstance(image_path, str) and image_path.endswith(qid + ".webp"),
                f"{qid}: incorrect original image path")
        if qid == "115-00-MB-20":
            require("/webp-v5/" in image_path, "MB20: v5 required, v1/v2 forbidden")
        if qid == "115-00-MB-23":
            tables = q.get("tables", [])
            tab = g2.get("originalSourceTable", {})
            require(len(tables) == 1
                    and tables[0].get("heading") == tab.get("columns")
                    and tables[0].get("rows") == tab.get("rows"),
                    "MB23: canonical table vs G2 mismatch")
        img = (repo_root / image_path).read_bytes()
        require(sha256(img) == webp_sha, f"{qid}: WebP bytes SHA256 mismatch")
        require(git_blob(img) == image_blob, f"{qid}: original WebP Git Blob mismatch")
        expected_sha = (q.get("assets", {}).get("sha256") if year == "115"
                        else q.get("questionProvenance", {}).get("webpSha256"))
        require(expected_sha == webp_sha, f"{qid}: bank image SHA mismatch")
        prompt_bytes = render(g2, qid)
        result[qid] = {
            "question_bytes": prompt_bytes,
            "image_bytes": img,
            "operator_record": {
                "qid": qid,
                "year": year,
                "questionRevision": revision,
                "G2GitBlob": g2_blob,
                "G2RawSha256": sha256(data),
                "webpPathInRepository": image_path,
                "webpGitBlob": image_blob,
                "webpSha256": webp_sha,
                "solverTextSha256": sha256(prompt_bytes),
                "solverFilesOnly": ["question.txt", "original.webp"],
                "firstSolveExecuted": False
            }
        }
    return result

def validate_output(out, sources):
    solver = out / "solver-input"
    require(solver.is_dir(), "missing solver-input")
    require({x.name for x in solver.iterdir()} == set(sources), "unexpected QID folder")
    for qid, obj in sources.items():
        folder = solver / qid
        require({x.name for x in folder.iterdir()} == {"question.txt", "original.webp"},
                f"{qid}: forbidden sidecar / metadata / answer leakage")
        require((folder / "question.txt").read_bytes() == obj["question_bytes"],
                f"{qid}: solver text changed")
        require((folder / "original.webp").read_bytes() == obj["image_bytes"],
                f"{qid}: original image changed")
    return True

def build(out, sources):
    require(not out.exists(), "output already exists: do not merge with stale material")
    solver = out / "solver-input"
    solver.mkdir(parents=True)
    for qid, obj in sources.items():
        folder = solver / qid
        folder.mkdir()
        (folder / "question.txt").write_bytes(obj["question_bytes"])
        (folder / "original.webp").write_bytes(obj["image_bytes"])
    op = out / "operator-only"
    op.mkdir()
    manifest = {
        "IMPORTANT": "OPERATOR ONLY. NEVER PASS MANIFEST OR REPOSITORY TO SOLVER.",
        "modelInput": "Exactly ONE question.txt plus SAME-QID original.webp",
        "sourceClaim": "G1/G2/G3 source only; not independent first-solve or E review",
        "records": [sources[k]["operator_record"] for k in sorted(sources)],
    }
    (op / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    validate_output(out, sources)
    return manifest

def expect_failure(fn):
    try:
        fn()
    except (ValueError, FileNotFoundError):
        return
    raise AssertionError("negative test unexpectedly passed")

def selftest(sources):
    require(sha256(b"abc") ==
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            "SHA256 selftest")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        build(out, sources)
        first = next(iter(sources))
        txt = out / "solver-input" / first / "question.txt"
        original = txt.read_bytes()
        txt.write_bytes(original + b"\nOfficial answer: A\n")
        expect_failure(lambda: validate_output(out, sources))
        txt.write_bytes(original)
        rogue = out / "solver-input" / first / "teaching.json"
        rogue.write_text('{"answer":"A"}', encoding="utf-8")
        expect_failure(lambda: validate_output(out, sources))
        rogue.unlink()
        img = out / "solver-input" / first / "original.webp"
        image = img.read_bytes()
        img.write_bytes(b"tampered")
        expect_failure(lambda: validate_output(out, sources))
        img.write_bytes(image)
        invalid = dict(sources["115-00-MB-23"])
        require("行程".encode("utf-8") in invalid["question_bytes"], "MB23 2x3 table missing")
        require(b"\\u" not in invalid["question_bytes"], "MB23 escaped Unicode in prompt")
        validate_output(out, sources)
    print("PASS source banks 205x2; nine exact G2/image pins; MB20 v5; MB23 2x3; "
          "answer-free allowlist; altered text/metadata/image negative cases")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path)
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    require(args.selftest or args.out is not None, "specify --selftest or --out")
    sources = load_sources()
    if args.selftest:
        selftest(sources)
    if args.out:
        manifest = build(args.out, sources)
        print(f"BUILT {len(manifest['records'])} isolated solver QIDs at {args.out}")
        print("G6/G7 not executed. Source-only; no E/content approval.")
if __name__ == "__main__":
    main()
