#!/usr/bin/env python3
"""Draw every command list of the project with plotipus.

    python run.py                # every input/plots and input/tables list
    python run.py dune showcase  # only these lists

Before plotting, the toy data is written (when scripts/make_example_data.py
exists) and the data is checked against input/data/MANIFEST.csv (when it
exists). Figures go to output/plots, tables to output/tables.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIX = "_scripts.txt"


def run(*command):
    print("$", " ".join(command), flush=True)
    return subprocess.call(command, cwd=ROOT)


def lists(kind):
    return sorted(p.name[: -len(SUFFIX)] for p in (ROOT / "input" / kind).glob(f"*{SUFFIX}"))


def main():
    names = sys.argv[1:] or sorted(set(lists("plots")) | set(lists("tables")))
    failed = 0
    if (ROOT / "scripts" / "make_example_data.py").is_file():
        failed += run(sys.executable, "scripts/make_example_data.py")
    if (ROOT / "input" / "data" / "MANIFEST.csv").is_file():
        failed += run(sys.executable, "scripts/data_manifest.py")
    for name in names:
        if name in lists("plots"):
            failed += run("plotipus", "run", name)
        if name in lists("tables"):
            failed += run("plotipus", "run", name, "--tables")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
