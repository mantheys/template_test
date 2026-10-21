#!/usr/bin/env python3
"""Checksums of the project data (input/data/MANIFEST.csv).

Freezes the result files a publication was made from: size, MD5 and a
free-text origin per file. input/data/examples (generated toy data) is skipped.

    python scripts/data_manifest.py          # verify every file against the manifest
    python scripts/data_manifest.py --write  # refresh sizes/checksums (keeps the origin notes)
"""

import argparse
import csv
import hashlib
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "input" / "data"
MANIFEST = DATA / "MANIFEST.csv"
FIELDS = ["path", "bytes", "md5", "origin"]
SKIPPED = ("examples",)


def data_files():
    return sorted(p for p in DATA.rglob("*.pkl") if p.relative_to(DATA).parts[0] not in SKIPPED)


def md5(path):
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_manifest():
    if not MANIFEST.is_file():
        return {}
    with open(MANIFEST, newline="") as handle:
        return {row["path"]: row for row in csv.DictReader(handle)}


def write():
    old = read_manifest()
    rows = []
    for path in data_files():
        rel = path.relative_to(DATA).as_posix()
        rows.append({"path": rel, "bytes": path.stat().st_size, "md5": md5(path),
                     "origin": old.get(rel, {}).get("origin", "")})
    with open(MANIFEST, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} files, {sum(int(r['bytes']) for r in rows) / 1e6:.1f} MB -> {MANIFEST.name}")


def verify():
    rows = read_manifest()
    if not rows:
        print("No input/data/MANIFEST.csv yet (python scripts/data_manifest.py --write)")
        return 0
    bad = 0
    for rel, row in rows.items():
        path = DATA / rel
        if not path.is_file():
            print(f"missing: {rel}")
            bad += 1
        elif path.stat().st_size < 1024 and path.read_bytes().startswith(b"version https://git-lfs"):
            print(f"LFS pointer (run `git lfs pull`): {rel}")
            bad += 1
        elif md5(path) != row["md5"]:
            print(f"changed: {rel}")
            bad += 1
    extra = {p.relative_to(DATA).as_posix() for p in data_files()} - set(rows)
    for rel in sorted(extra):
        print(f"not in manifest: {rel}")
    print(f"{len(rows) - bad}/{len(rows)} files match the manifest")
    return 1 if bad or extra else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    sys.exit(write() if parser.parse_args().write else verify())
