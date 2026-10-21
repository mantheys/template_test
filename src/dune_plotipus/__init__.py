"""DUNE plugin for plotipus.

Listed under ``plugins`` in ``plotipus.toml``, it makes every plotipus figure
follow the official DUNE plot style (https://github.com/DUNE/dune_plot_style):

* applies the ``dune.mplstyle`` sheet (Okabe-Ito colours, inward ticks, ...);
* adds ``--dune_label`` to every plot kind, drawing the DUNE watermark
  (``Simulation``, ``Preliminary``, ``Work In Progress`` or the bare
  ``DUNE`` of approved results) on the first panel of each figure;
* optionally switches the colour cycle to the DUNE-logo subset of the palette.

Project-wide defaults go in the ``[settings]`` table of ``plotipus.toml``::

    [settings]
    dune_label = "simulation"       # default --dune_label
    dune_headroom = 0.2             # fraction of the y range added on top
    dune_colors = "logo"            # or "okabe_ito" (the style default)
"""

import builtins

# dunestyle applies its style on import unless told otherwise; the style is
# applied explicitly in setup() so that plotipus' own defaults come first.
builtins.__dict__["DUNESTYLE_ENABLE_AUTOMATICALLY"] = False

import dunestyle.matplotlib as dunestyle  # noqa: E402

LABELS = {
    "simulation": dunestyle.Simulation,
    "preliminary": dunestyle.Preliminary,
    "wip": dunestyle.WIP,
    "official": dunestyle.Official,
    "simulation_side": dunestyle.SimulationSide,
}
COLORS = {
    "okabe_ito": dunestyle.SetOkabeItoColors,
    "logo": dunestyle.SetDUNELogoColors,
}


def _settings():
    from plotipus.project import load_project

    return load_project().settings


def _add_headroom(ax, fraction):
    """Raise the top of the y axis so the watermark does not cover data."""
    if fraction <= 0:
        return
    bottom, top = ax.get_ylim()
    if ax.get_yscale() == "log" and bottom > 0:
        ax.set_ylim(bottom, top * (top / bottom) ** fraction)
    else:
        ax.set_ylim(bottom, top + (top - bottom) * fraction)


def draw_dune_label(fig, args):
    """Figure hook: DUNE watermark on the first (upper-left) panel."""
    label = getattr(args, "dune_label", None)
    if not label or label == "none" or not fig.axes:
        return
    ax = fig.axes[0]
    kwargs = {"ax": ax, "fontsize": args.dune_label_size}
    if label != "simulation_side":
        _add_headroom(ax, args.dune_headroom)
        if args.dune_label_position is not None:
            kwargs["x"], kwargs["y"] = args.dune_label_position
    LABELS[label](**kwargs)


def setup(registry):
    dunestyle.enable()
    settings = _settings()
    colors = settings.get("dune_colors")
    if colors:
        COLORS[colors]()

    registry.add_argument(
        "--dune_label", choices=[*LABELS, "none"], default=settings.get("dune_label", "none"),
        help="DUNE watermark on the first panel (default from [settings] dune_label).")
    registry.add_argument(
        "--dune_label_position", nargs=2, type=float, default=None, metavar=("X", "Y"),
        help="Axes position of the watermark (default: dunestyle's upper left).")
    registry.add_argument(
        "--dune_label_size", default=settings.get("dune_label_size", "xx-large"),
        help="Font size of the watermark.")
    registry.add_argument(
        "--dune_headroom", type=float, default=float(settings.get("dune_headroom", 0.2)),
        help="Fraction of the y range added above the data to make room for the watermark (0 disables).")
    registry.add_figure_hook(draw_dune_label)
