# Template test

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
  series, arrays in the cells; files `{config}_{name}_{datafile}.pkl`).
- Add one command per figure to `input/plots/<list>_scripts.txt`.
- Name configurations and samples in `config/style.json`.
- Freeze the data of a publication with `python scripts/data_manifest.py --write`.
