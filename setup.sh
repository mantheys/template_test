#!/bin/bash
# Create .venv with the official DUNE plot style and plotipus.
#   source setup.sh            # pinned dune_plot_style release (requirements.txt)
#   source setup.sh --latest   # latest dune_plot_style release instead
# Data in input/data is stored with Git LFS: fetch it if the clone has only pointers
if command -v git-lfs >/dev/null 2>&1; then
    git lfs install --local >/dev/null && git lfs pull
else
    echo "warning: git-lfs not found; data files stored with Git LFS will be missing"
fi
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r requirements.txt
if [ "$1" == "--latest" ]; then
    TAG=$(curl --silent "https://api.github.com/repos/DUNE/dune_plot_style/releases" \
        | python3 -c "import json, sys; print(next(r['tag_name'] for r in json.load(sys.stdin) if not r['prerelease']))")
    python3 -m pip install --quiet --force-reinstall --no-deps \
        "dune_plot_style @ https://github.com/DUNE/dune_plot_style/archive/refs/tags/${TAG}.tar.gz"
    echo "dune_plot_style ${TAG} installed"
fi
echo "Environment ready: run 'python run.py'"
