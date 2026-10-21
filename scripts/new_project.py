#!/usr/bin/env python3
"""Turn a copy of this template into an empty project.

Run once in a repository created with "Use this template":

    python scripts/new_project.py "My analysis plots"

It removes the examples (toy data generator, example command lists,
gallery), writes a short README, switches CI to manual runs that fetch the
Git LFS data, and deletes itself. Kept: the DUNE plugin (src/dune_plotipus),
plotipus.toml, config/style.json, setup.sh, requirements.txt, run.py and
scripts/data_manifest.py.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    "scripts/make_example_data.py",
    "input/plots/dune_scripts.txt",
    "input/plots/showcase_scripts.txt",
    "input/tables/dune_scripts.txt",
    "input/data/examples",
    "docs/gallery",
    "output",
]
STYLE = """{
  "plot_settings": {
    "auto_title": false
  },
  "mappings": {
    "config_dict": {},
    "config_color": {},
    "name_dict": {}
  }
}
"""
COMMANDS = """# One figure per line: `plotipus <kind> [options]`, e.g.
# line --path my_study --datafile Efficiency --configs hd_1x2x6 --names marley -x Energy -y Efficiency --errory
"""
WORKFLOW = """name: plots

# Manual only: every run downloads the Git LFS data.
on:
  workflow_dispatch:

jobs:
  plots:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python run.py
      - uses: actions/upload-artifact@v4
        with:
          name: plots
          path: output/
"""
README = """# {title}

DUNE plots and tables drawn with [plotipus](https://github.com/mantheys/plotipus)
and the official [dune_plot_style](https://github.com/DUNE/dune_plot_style),
from the [matplotlib_dunestyle_examples](https://github.com/DUNE/matplotlib_dunestyle_examples)
template.

```bash
git lfs install            # once per machine (data in input/data is stored with Git LFS)
source setup.sh            # .venv with dune_plot_style + plotipus
python run.py              # every list in input/plots and input/tables -> output/
```

- Store results as pickled DataFrames under `input/data/` (one row per
  series, arrays in the cells; files `{{config}}_{{name}}_{{datafile}}.pkl`).
- Add one command per figure to `input/plots/<list>_scripts.txt`.
- Name configurations and samples in `config/style.json`.
- Freeze the data of a publication with `python scripts/data_manifest.py --write`.
"""


def main():
    title = " ".join(sys.argv[1:]) or ROOT.name
    for rel in EXAMPLES:
        path = ROOT / rel
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    (ROOT / "config" / "style.json").write_text(STYLE)
    (ROOT / "input" / "plots" / "main_scripts.txt").write_text(COMMANDS)
    (ROOT / "input" / "data").mkdir(parents=True, exist_ok=True)
    workflows = ROOT / ".github" / "workflows"
    for old in workflows.glob("*.yml"):
        old.unlink()
    (workflows / "plots.yml").write_text(WORKFLOW)
    (ROOT / "README.md").write_text(README.format(title=title))
    for leftover in ("docs",):
        path = ROOT / leftover
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    Path(__file__).unlink()
    print(f"'{title}' is ready: add data to input/data and commands to input/plots/main_scripts.txt,")
    print("then review and commit the changes (git status).")


if __name__ == "__main__":
    main()
