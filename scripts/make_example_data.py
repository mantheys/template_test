#!/usr/bin/env python3
"""Write the toy DataFrames drawn by the command lists in input/.

This plays the role of an analysis: it produces results (histograms, fits,
per-event arrays) and stores them as pickled pandas DataFrames, one row per
series with whole arrays in the cells. Plotting is left to plotipus.

The first five files reproduce the examples of the official dune_plot_style
package (examples/matplotlib/example.py); the others show what a typical
DUNE analysis stores (detector configurations, efficiencies, resolutions).

Usage: python scripts/make_example_data.py [--output input/data/examples]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

N_HISTS = 8  # exhibits every colour of the Okabe-Ito cycle


def gauss(x, a, mu, sigma):
    return a * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def hist1d(rng):
    """dune_plot_style Hist1D: one array of raw values."""
    return pd.DataFrame([{"Values": rng.normal(0, 1, 1000), "Sample": "Hist", "Variable": "x"}])


def data_fit(rng):
    """dune_plot_style DataMC: binned data with a stored Gaussian fit."""
    counts, edges = np.histogram(rng.normal(0, 1, 1000), bins=50, range=(-5, 5))
    centers = 0.5 * (edges[:-1] + edges[1:])
    errors = np.sqrt(counts)
    mask = counts > 0
    params, cov = curve_fit(gauss, centers[mask], counts[mask], p0=[counts.max(), 0, 1], sigma=errors[mask])
    model = gauss(centers[mask], *params)
    # Empty bins are left out of the plot (NaN), as in the dunestyle example.
    shown = np.where(mask, counts, np.nan)
    return pd.DataFrame([{
        "Bins": centers, "Counts": shown, "CountsError": np.where(mask, errors, np.nan), "Sample": "Data", "Variable": "x",
        "FitFunctionLabel": "Gaussian", "Params": params, "ParamsError": np.sqrt(np.diag(cov)),
        "ParamsLabel": ["$A$", r"$\mu$", r"$\sigma$"],
        "Chi2": float(((counts[mask] - model) ** 2 / model).sum()),
    }])


def throws_2d(rng):
    """dune_plot_style Hist2DContour: correlated 2D throws and a chi2 grid
    (the Mahalanobis distance) for the 1, 2, 3 sigma contours."""
    cov = np.array([[0.5, -0.5], [-0.5, 1.0]])
    throws = rng.multivariate_normal((0, 0), cov, 1_000_000)
    grid = np.linspace(-5, 5, 201)
    xx, yy = np.meshgrid(grid, grid)
    inv = np.linalg.inv(cov)
    chi2 = inv[0, 0] * xx**2 + 2 * inv[0, 1] * xx * yy + inv[1, 1] * yy**2
    events = pd.DataFrame([{"X": throws[:, 0], "Y": throws[:, 1], "Sample": "Throws", "Variable": "xy"}])
    contour = pd.DataFrame([{"XGrid": grid, "YGrid": grid, "Chi2": chi2, "Config": "toy", "Name": "throws",
                             "Variable": "xy"}])
    return events, contour


def hist_family(rng, nbins=100):
    """dune_plot_style HistStacked/HistOverlay: eight shifted Gaussians,
    stored both binned (for stacking) and raw (for histogramming)."""
    extent = N_HISTS - 1
    binned, raw = [], []
    edges = np.linspace(-2 * (N_HISTS / 2 + 2), 2 * N_HISTS, nbins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    for i, mu in enumerate(range(-extent, extent + 2, 2)):
        values = rng.normal(mu, 1, 10000)
        counts, _ = np.histogram(values, bins=edges)
        name = f"Hist #{i + 1}"
        binned.append({"Bins": centers, "Counts": counts.astype(float), "Sample": name, "Variable": "x"})
        raw.append({"Values": values, "Sample": name, "Variable": "x"})
    return pd.DataFrame(binned), pd.DataFrame(raw)


def detector_studies(rng):
    """Beyond the official examples: efficiency curves per detector
    configuration, per-event energies and a summary for a table."""
    energy = np.arange(1.0, 30.0, 1.0)
    configs = {"hd_1x2x6": (0.95, 3.0), "vd_1x8x14": (0.92, 4.0)}
    efficiency, events, summary = [], [], []
    for config, (plateau, turn_on) in configs.items():
        for name, shift in (("marley", 0.0), ("gamma", 2.0)):
            eff = 100 * plateau * (1 - np.exp(-(energy - shift).clip(0) / turn_on))
            efficiency.append({"Energy": energy, "Efficiency": eff, "EfficiencyError": np.full_like(energy, 1.5),
                               "Config": config, "Name": name, "Variable": "Efficiency"})
        true = rng.uniform(2, 30, 20000)
        sigma = 0.05 + (0.3 if config.startswith("hd") else 0.25) / np.sqrt(true)
        reco = true * rng.normal(1, sigma)
        events.append({"TrueEnergy": true, "RecoEnergy": reco, "Resolution": (reco - true) / true,
                       "Config": config, "Variable": "Energy"})
        for variable, value in (("Efficiency", 100 * plateau), ("Purity", 88.0 + 4 * plateau),
                                ("Resolution", 100 * np.std((reco - true) / true))):
            summary.append({"Config": config, "Variable": variable, "Value": value, "ValueError": 0.02 * value})
    return pd.DataFrame(efficiency), pd.DataFrame(events), pd.DataFrame(summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", default=Path(__file__).resolve().parents[1] / "input" / "data" / "examples", type=Path)
    parser.add_argument("--seed", type=int, default=89)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    events_2d, contour_2d = throws_2d(rng)
    binned, raw = hist_family(rng)
    efficiency, events, summary = detector_studies(rng)
    frames = {
        "Hist1D": hist1d(rng),
        "DataFit": data_fit(rng),
        "Throws2D": events_2d,
        "HistFamily": binned,
        "HistFamilyRaw": raw,
        "Events": events,
        "Summary": summary,
    }
    for name, frame in frames.items():
        frame.to_pickle(args.output / f"{name}.pkl")
    # Per configuration/sample files are named {config}_{name}_{datafile}.pkl
    contour_2d.to_pickle(args.output / "toy_throws_Contour2D.pkl")
    for (config, name), rows in efficiency.groupby(["Config", "Name"]):
        rows.reset_index(drop=True).to_pickle(args.output / f"{config}_{name}_Efficiency.pkl")
    print(f"Example data written to {args.output}")


if __name__ == "__main__":
    main()
