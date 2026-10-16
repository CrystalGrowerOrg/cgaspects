#!/usr/bin/env python3
"""Radial open / enclosed porosity of CrystoGen XYZ point clouds via S₂(r).

Runs the same two-point-correlation analysis as the Clusters → Radial Profile
→ S₂ option in the GUI, outside the GUI, on one or more XYZ files:

* the points are voxelised (auto voxel = 1.5× median nearest-neighbour spacing);
* empty voxels are split by flooding from the outside: *enclosed* pores are
  sealed off by solid, *open* pores are reached by the flood but lie inside the
  crystal outline (closing + hole filling); everything else is ignored;
* for each radial shell (distance from the origin (0, 0, 0)) S₂(r) is
  computed for both pore definitions, giving porosity = 1 − S₂(0) and a
  correlation length ξ (where the normalised S₂ first drops below 1/e).

Units: XYZ coordinates are in units of the lattice a-axis. With --a-length (Å)
every length (r, voxel, max lag, lags, ξ) is converted to nm (XYZ × a / 10),
and --voxel / --max-lag are read in nm. Without it lengths stay in XYZ units.

Outputs (in --out-dir):

    s2_radial.csv       one row per (file, shell): density and both porosities / ξ
    s2_curves.csv       full S₂ curves per (file, pore definition, shell, lag)
    s2_summary.csv      per file: core porosity (unweighted and site-weighted)
                        and peak enclosed / open porosity with its radius
    <label>_profile.png stacked enclosed + open porosity and ξ versus radius
    comparison.png      core and peak porosity for every file side by side

Usage:
    python scripts/analyse_s2_porosity.py thin/*.XYZ thick/*.XYZ
    python scripts/analyse_s2_porosity.py --labels Thin Thick -o s2_out \\
        thin/thin_lastframe.XYZ thick/thick_lastframe.XYZ
    python scripts/analyse_s2_porosity.py --bins 40 --voxel 2.0 --max-lag 40 file.XYZ
    python scripts/analyse_s2_porosity.py -a 10.53 file.XYZ
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

# Allow running directly from a source checkout without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cgaspects.analysis.cluster_analysis import (  # noqa: E402
    _auto_voxel,
    radial_profile,
    two_point_profile,
    xyz_length_scale,
)
from cgaspects.fileio.xyz_file import CrystalCloud  # noqa: E402

# Same palette as the slides: enclosed amber, open brick, pale amber for core.
ENCLOSED, OPEN, CORE = "#E39B2D", "#C8553D", "#F2CB8A"
# Neutral inks: text, secondary text and recessive axes; white surface for gaps.
INK, INK_MUTED, AXIS, SURFACE = "#222222", "#6B6B6B", "#BDBDBD", "#FFFFFF"

PLOT_STYLE = {
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.titlepad": 12,
    "axes.labelsize": 10,
    "axes.labelcolor": INK_MUTED,
    "axes.edgecolor": AXIS,
    "axes.linewidth": 0.8,
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": SURFACE,
    "figure.facecolor": SURFACE,
    "text.color": INK,
    "xtick.color": AXIS,
    "ytick.color": AXIS,
    "xtick.labelcolor": INK_MUTED,
    "ytick.labelcolor": INK_MUTED,
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "legend.labelcolor": INK,
}


def analyse_file(path: Path, frame: int, nbins: int, voxel: float, max_lag: float,
                 length_scale: float):
    """Return (radial DataFrame, curves DataFrame, voxel, max_lag) for one XYZ file."""
    coords = CrystalCloud.parse_xyz_file(path)[frame].coords * length_scale
    voxel = voxel or _auto_voxel(coords)
    max_lag = max_lag or 20 * voxel

    prof = radial_profile(coords, None, None, nbins)
    edges = np.append(prof["r_lo"].to_numpy(), prof["r_hi"].iloc[-1])
    summary, curves = two_point_profile(coords, edges, voxel, max_lag)
    return pd.concat([prof, summary], axis=1), curves, voxel, max_lag


def summarise(label: str, radial: pd.DataFrame, core_frac: float) -> dict:
    """Core porosity (inner shells) and peak porosity per pore definition."""
    r_max = radial["r_mid"].max()
    core = radial[radial["r_mid"] < core_frac * r_max]
    enc = core["s2_enclosed_porosity"]
    weights = core["n_points"].where(enc.notna(), 0)
    row = {
        "label": label,
        "r_max": r_max,
        "core_cutoff": core_frac * r_max,
        "core_shells": int(enc.notna().sum()),
        "core_enclosed_unweighted": enc.mean(),
        "core_enclosed_site_weighted": (enc.fillna(0) * weights).sum() / weights.sum(),
    }
    for name in ("enclosed", "open"):
        col = radial[f"s2_{name}_porosity"]
        i = col.idxmax()
        row[f"peak_{name}"] = col[i]
        row[f"peak_{name}_r"] = radial.loc[i, "r_mid"]
    return row


def plot_profile(label: str, radial: pd.DataFrame, rmax_frac: float, unit: str,
                 path: Path) -> None:
    """Stacked enclosed + open porosity and ξ versus radius (slide-6 style)."""
    import matplotlib.pyplot as plt

    d = radial[radial["r_mid"] <= rmax_frac * radial["r_mid"].max()]
    r = d["r_mid"].to_numpy()
    enc = 100 * d["s2_enclosed_porosity"].fillna(0).to_numpy()
    opn = 100 * d["s2_open_porosity"].fillna(0).to_numpy()

    with plt.rc_context(PLOT_STYLE):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))
        ax1.stackplot(r, enc, opn, labels=["Enclosed", "Open"], colors=[ENCLOSED, OPEN],
                      edgecolor=SURFACE, linewidth=1.5)
        ax1.plot(r, enc + opn, color=INK, lw=1, alpha=0.6)
        ax1.set_title("Porosity, stacked = total")
        ax1.set_ylabel("porosity (%)")
        ax1.set_ylim(bottom=0)

        for col, colour, name in (("s2_enclosed_corr_length", ENCLOSED, "Enclosed"),
                                  ("s2_open_corr_length", OPEN, "Open")):
            ax2.plot(r, d[col], color=colour, lw=2, label=name, solid_capstyle="round")
        ax2.set_title("Correlation length ξ")
        ax2.set_ylabel(f"ξ ({unit})")
        ax2.set_ylim(bottom=0)

        for ax in (ax1, ax2):
            ax.set_xlabel(f"distance from origin r ({unit})")
            ax.set_xlim(r.min(), r.max())
            ax.spines[["left", "bottom"]].set_position(("outward", 6))
        # Title on its own strip above the legend so it can be cropped off cleanly.
        fig.suptitle(label, x=0.01, y=0.99, ha="left", va="top", fontsize=14,
                     fontweight="bold")
        fig.legend(*ax1.get_legend_handles_labels(), loc="upper right", ncols=2,
                   bbox_to_anchor=(0.98, 0.935), handlelength=1.2)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(path, dpi=150)
        plt.close(fig)


def plot_comparison(summary: pd.DataFrame, core_frac: float, path: Path) -> None:
    """Core (site-weighted) and peak porosity for each file (slide-7 style)."""
    import matplotlib.pyplot as plt

    series = [
        ("core_enclosed_site_weighted", f"Enclosed, core (r < {core_frac:g} r_max)", CORE),
        ("peak_enclosed", "Enclosed, peak shell", ENCLOSED),
        ("peak_open", "Open, peak shell", OPEN),
    ]
    x = np.arange(len(summary))
    width = 0.26
    with plt.rc_context(PLOT_STYLE):
        fig, ax = plt.subplots(figsize=(max(6, 1.9 * len(summary) + 2), 4.6))
        for k, (col, name, colour) in enumerate(series):
            vals = 100 * summary[col].to_numpy()
            bars = ax.bar(x + (k - 1) * width, vals, width, label=name, color=colour,
                          edgecolor=SURFACE, linewidth=1.5)
            ax.bar_label(bars, fmt="%.1f", fontsize=8, padding=3, color=INK_MUTED)
        ax.set_xticks(x, summary["label"])
        ax.tick_params(axis="x", length=0, labelsize=10, labelcolor=INK)
        ax.set_title("Core and peak porosity")
        ax.set_ylabel("porosity (%)")
        ax.margins(y=0.12)
        ax.spines["left"].set_position(("outward", 6))
        fig.legend(loc="lower center", ncols=len(series), handlelength=1.2)
        fig.tight_layout(rect=(0, 0.07, 1, 1))
        fig.savefig(path, dpi=150)
        plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path, help="CrystoGen XYZ file(s)")
    parser.add_argument("--labels", nargs="+", default=None,
                        help="Display name per file (default: file stem)")
    parser.add_argument("-o", "--out-dir", type=Path, default=Path("s2_output"), dest="out_dir",
                        help="Output folder (default: ./s2_output)")
    parser.add_argument("--frame", type=int, default=-1,
                        help="Frame index in each XYZ file (default: -1, last frame)")
    parser.add_argument("--bins", type=int, default=30,
                        help="Number of radial shells (default: 30)")
    parser.add_argument("-a", "--a-length", type=float, default=0.0, dest="a_length",
                        help="Lattice a-axis length in Å; converts all lengths to nm "
                             "(default: not set, lengths stay in XYZ units)")
    parser.add_argument("--voxel", type=float, default=0.0,
                        help="Voxel edge in nm, or XYZ units without --a-length "
                             "(default: auto, 1.5× NN spacing)")
    parser.add_argument("--max-lag", type=float, default=0.0, dest="max_lag",
                        help="Largest S₂ separation in nm, or XYZ units without --a-length "
                             "(default: auto, 20 voxels)")
    parser.add_argument("--core-frac", type=float, default=0.4, dest="core_frac",
                        help="Core = shells with r_mid < core_frac × r_max (default: 0.4)")
    parser.add_argument("--plot-rmax-frac", type=float, default=1.0, dest="plot_rmax_frac",
                        help="Only plot shells with r_mid ≤ this × r_max, e.g. 0.87 to drop "
                             "surface-dominated outer shells (default: 1.0, all)")
    parser.add_argument("--no-plots", action="store_true", dest="no_plots",
                        help="Write the CSVs only")
    args = parser.parse_args()

    if args.labels is not None and len(args.labels) != len(args.files):
        parser.error(f"--labels needs one name per file ({len(args.files)} files given)")
    labels = args.labels or [p.stem for p in args.files]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    length_scale, unit = xyz_length_scale(args.a_length)
    if unit != "nm":
        print("warning: no --a-length given, lengths are in XYZ units, not nm", file=sys.stderr)

    radial_frames, curve_frames, summary_rows = [], [], []
    bar = tqdm(list(zip(args.files, labels)), desc="files", unit="file")
    for path, label in bar:
        if not path.exists():
            bar.write(f"skip (not found): {path}")
            continue
        bar.set_postfix_str(path.name)
        try:
            radial, curves, voxel, max_lag = analyse_file(
                path, args.frame, args.bins, args.voxel, args.max_lag, length_scale)
        except Exception as exc:  # noqa: BLE001 - keep going through the batch
            bar.write(f"skip ({exc}): {path}")
            continue

        radial.insert(0, "label", label)
        radial.insert(1, "file", str(path))
        radial.insert(2, "length_unit", unit)
        curves.insert(0, "label", label)
        curves.insert(1, "length_unit", unit)
        radial_frames.append(radial)
        curve_frames.append(curves)
        row = summarise(label, radial, args.core_frac)
        row.update(file=str(path), length_unit=unit, a_length_angstrom=args.a_length or None,
                   voxel=voxel, max_lag=max_lag)
        summary_rows.append(row)
        bar.write(f"  {label}: voxel {voxel:.3g} {unit}, core enclosed "
                  f"{row['core_enclosed_site_weighted']:.2%} (r < {row['core_cutoff']:.3g}), "
                  f"peak enclosed "
                  f"{row['peak_enclosed']:.2%} @ r={row['peak_enclosed_r']:.3g}, peak open "
                  f"{row['peak_open']:.2%} @ r={row['peak_open_r']:.3g} {unit}")

        if not args.no_plots:
            import matplotlib

            matplotlib.use("Agg")
            plot_profile(label, radial, args.plot_rmax_frac, unit,
                         args.out_dir / f"{label.replace(' ', '_')}_profile.png")
    bar.close()

    if not summary_rows:
        return 1

    summary = pd.DataFrame(summary_rows)
    pd.concat(radial_frames, ignore_index=True).to_csv(args.out_dir / "s2_radial.csv", index=False)
    pd.concat(curve_frames, ignore_index=True).to_csv(args.out_dir / "s2_curves.csv", index=False)
    summary.to_csv(args.out_dir / "s2_summary.csv", index=False)
    if not args.no_plots:
        plot_comparison(summary, args.core_frac, args.out_dir / "comparison.png")

    print(f"\nWrote s2_radial.csv, s2_curves.csv, s2_summary.csv"
          f"{' and plots' if not args.no_plots else ''} to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
