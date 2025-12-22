#!/usr/bin/env python3
"""
Standalone Growth Rate Plotter

This script calculates and plots growth rates from size.csv files generated
by crystal growth simulations. It processes multiple simulation files,
calculates growth rates using linear fitting, and generates comprehensive
visualization plots.

Usage:
    python standalone_growth_rate_plotter.py --input /path/to/data --directions "100" "010" "001"

Requirements:
    - numpy
    - pandas
    - matplotlib
"""

import argparse
import logging
import re
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GrowthRatePlotter")


def build_growthrates(
    size_file_list: List[Path],
    supersat_list: List[float],
    directions: List[str],
    plot_raw_data: bool = False,
    raw_data_output: Optional[Path] = None,
) -> Optional[pd.DataFrame]:
    """
    Generate the growth rate dataframe from the size.csv files.

    Args:
        size_file_list: List of paths to size.csv files
        supersat_list: List of supersaturation values corresponding to each file
        directions: List of crystal direction strings (e.g., [" 1 0 0", " 0 1 0"])
        plot_raw_data: If True, plot raw size vs time data for each simulation
        raw_data_output: Directory to save raw data plots

    Returns:
        DataFrame with columns: Simulation Number, Supersaturation, and growth rates per direction
    """
    growth_list = []
    lengths = []
    n_size_files = len(size_file_list)

    if n_size_files == 0:
        logger.error("No size files provided")
        return None

    logger.info(f"{n_size_files} size files used to calculate growth rate data")

    if plot_raw_data and raw_data_output:
        raw_data_output = Path(raw_data_output)
        raw_data_output.mkdir(parents=True, exist_ok=True)
        logger.info(f"Raw data plots will be saved to {raw_data_output}")

    for i, f in enumerate(size_file_list):
        f = Path(f)
        logger.info(f"Processing file {i + 1}/{n_size_files}: {f.name}")

        try:
            lt_df = pd.read_csv(f, encoding="utf-8", encoding_errors="replace")
        except Exception as e:
            logger.warning(f"Failed to read file {f.name}: {e}")
            continue

        # Validate that the DataFrame has the required columns
        if "time" not in lt_df.columns:
            logger.warning(f"Skipping file {f.name}: missing 'time' column")
            continue

        # Check if all required directions are present
        missing_directions = [d for d in directions if d not in lt_df.columns]
        if missing_directions:
            logger.warning(
                f"Skipping file {f.name}: missing direction columns {missing_directions}"
            )
            continue

        x_data = lt_df["time"]
        tokens = re.findall(r"\d+", f.name)
        sim_num = int(tokens[-1]) if tokens else i

        logger.debug(f"Directions: {directions}")
        lengths = directions

        # Plot raw data if requested
        if plot_raw_data and raw_data_output:
            fig, axes = plt.subplots(len(directions), 1, figsize=(10, 3 * len(directions)))
            if len(directions) == 1:
                axes = [axes]

            supersat_val = supersat_list[i] if i < len(supersat_list) else "Unknown"
            fig.suptitle(f"Sim {sim_num} - Supersaturation: {supersat_val} kcal/mol", fontsize=14)

            for idx, direction in enumerate(directions):
                y_data = np.array(lt_df[direction])
                # Calculate fit
                model = np.polyfit(x_data, y_data, 1)
                fit_line = model[0] * x_data + model[1]

                axes[idx].scatter(x_data, y_data, s=2, alpha=0.6, label="Data")
                axes[idx].plot(
                    x_data, fit_line, "r-", linewidth=2, label=f"Fit (slope={model[0]:.6f})"
                )
                axes[idx].set_xlabel("Time")
                axes[idx].set_ylabel(f"Size [{direction}]")
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3)
                axes[idx].set_title(f"Direction: {direction}")

            plt.tight_layout()
            plot_filename = raw_data_output / f"raw_data_sim_{sim_num:03d}.png"
            plt.savefig(plot_filename, dpi=150)
            plt.close()
            logger.debug(f"Saved raw data plot: {plot_filename}")

        gr_list = [sim_num]
        for direction in lengths:
            y_data = np.array(lt_df[direction])
            # Linear fit: growth rate is the slope
            model = np.polyfit(x_data, y_data, 1)
            gr_list.append(model[0])  # model[0] is the slope

        growth_list.append(gr_list)
        logger.info(f"Calculated growth rates for simulation {sim_num}")

    if not growth_list:
        logger.error("No valid data was processed")
        return None

    logger.debug(f"Growth Rate data (list): {growth_list}")
    growth_array = np.asarray(growth_list)
    gr_df = pd.DataFrame(growth_array, columns=["Simulation Number"] + lengths)
    gr_df.insert(1, "Supersaturation", supersat_list[: len(growth_list)])

    return gr_df


def plot_growth_rates(gr_df: pd.DataFrame, directions: List[str], savepath: Path):
    """
    Generate comprehensive growth rate plots.

    Creates 6 different plots:
    1. Combined growth/dissolution rates
    2. Growth rates (supersaturation >= 0)
    3. Growth rates (zoomed view)
    4. Dissolution rates (supersaturation <= 0)
    5. Dissolution rates (zoomed view)

    Args:
        gr_df: DataFrame with growth rate data
        directions: List of direction column names to plot
        savepath: Directory path where plots will be saved
    """
    savepath = Path(savepath)
    savepath.mkdir(parents=True, exist_ok=True)

    # Sort by supersaturation for proper line plot connections
    gr_df = gr_df.sort_values("Supersaturation").reset_index(drop=True)
    logger.debug("Data sorted by supersaturation")

    x_data = gr_df["Supersaturation"]

    # Plot 1: Combined growth and dissolution rates
    plt.figure(figsize=(7, 5))
    for direction in directions:
        plt.scatter(x_data, gr_df[direction], s=1.2)
        plt.plot(x_data, gr_df[direction], label=direction)
    plt.legend()
    plt.xlabel("Supersaturation (kcal/mol)")
    plt.ylabel("Growth Rate")
    plt.tight_layout()
    logger.info("Plotting growth/dissolution rates")
    plt.savefig(savepath / "growth_and_dissolution_rates.png", dpi=300)
    plt.close()

    # Plot 2: Growth rates only (supersaturation >= 0)
    growth_data = gr_df[gr_df["Supersaturation"] >= 0].sort_values("Supersaturation")
    plt.figure(figsize=(5, 5))
    for direction in directions:
        plt.scatter(growth_data["Supersaturation"], growth_data[direction], s=1.2)
        plt.plot(growth_data["Supersaturation"], growth_data[direction], label=direction)
    plt.legend()
    plt.xlabel("Supersaturation (kcal/mol)")
    plt.ylabel("Growth Rate")
    plt.tight_layout()
    logger.info("Plotting growth rates")
    plt.savefig(savepath / "growth_rates.png", dpi=300)
    plt.close()

    # Plot 3: Growth rates (zoomed)
    plt.figure(figsize=(5, 5))
    for direction in directions:
        plt.scatter(growth_data["Supersaturation"], growth_data[direction], s=1.2)
        plt.plot(growth_data["Supersaturation"], growth_data[direction], label=direction)
    plt.legend()
    plt.xlabel("Supersaturation (kcal/mol)")
    plt.ylabel("Growth Rate")
    plt.xlim(0.0, 2.5)
    plt.ylim(0.0, 0.4)
    plt.tight_layout()
    logger.info("Plotting growth rates (zoomed)")
    plt.savefig(savepath / "growth_rates_zoomed.png", dpi=300)
    plt.close()

    # Plot 4: Dissolution rates (supersaturation <= 0)
    dissolution_data = gr_df[gr_df["Supersaturation"] <= 0].sort_values("Supersaturation")
    if not dissolution_data.empty:
        plt.figure(figsize=(7, 5))
        for direction in directions:
            plt.scatter(
                dissolution_data["Supersaturation"],
                dissolution_data[direction],
                label=direction,
                s=1.2,
            )
        plt.legend()
        plt.xlabel("Supersaturation (kcal/mol)")
        plt.ylabel("Dissolution Rate")
        plt.tight_layout()
        logger.info("Plotting dissolution rates")
        plt.savefig(savepath / "dissolution_rates.png", dpi=300)
        plt.close()

        # Plot 5: Dissolution rates (zoomed)
        plt.figure(figsize=(5, 5))
        for direction in directions:
            plt.scatter(dissolution_data["Supersaturation"], dissolution_data[direction], s=1.2)
            plt.plot(
                dissolution_data["Supersaturation"], dissolution_data[direction], label=direction
            )
        plt.legend()
        plt.xlabel("Supersaturation (kcal/mol)")
        plt.ylabel("Growth Rate")
        plt.xlim(-2.5, 0.0)
        plt.ylim(-2.5, 0.0)
        plt.tight_layout()
        logger.info("Plotting dissolution rates (zoomed)")
        plt.savefig(savepath / "dissolution_rates_zoomed.png", dpi=300)
        plt.close()
    else:
        logger.info("No dissolution data available (all supersaturation >= 0)")

    logger.info(f"All plots saved to {savepath}")


def extract_sim_number(filepath: Path) -> int:
    """Extract simulation number from file path."""
    tokens = re.findall(r"\d+", filepath.name)
    return int(tokens[-1]) if tokens else 0


def find_size_files_and_supersats(input_folder: Path) -> tuple[List[Path], List[float]]:
    """
    Find all size.csv files and extract supersaturation from simulation_parameters.txt files.

    Args:
        input_folder: Path to search for files

    Returns:
        Tuple of (size_files, supersaturation_values), both sorted by simulation number
    """
    input_folder = Path(input_folder)

    # Find all size files
    size_files = list(input_folder.rglob("*size.csv"))
    logger.info(f"Found {len(size_files)} size files")

    # Create a mapping of simulation number to size file and supersaturation
    sim_data = {}

    for size_file in size_files:
        sim_num = extract_sim_number(size_file)

        # Look for simulation_parameters.txt in the same directory
        param_file = list(size_file.parent.glob("*simulation_parameters.txt"))[0]
        supersat = None

        if param_file.exists():
            try:
                with open(param_file, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if line.startswith("Starting delta mu value (kcal/mol):"):
                            supersat = float(line.split()[-1])
                            break
            except Exception as e:
                logger.warning(f"Failed to read {param_file}: {e}")

        if supersat is None:
            logger.warning(f"No supersaturation found for {size_file.name}, using 0.0")
            supersat = 0.0

        sim_data[sim_num] = {"size_file": size_file, "supersat": supersat}

    # Sort by simulation number
    sorted_sim_nums = sorted(sim_data.keys())

    sorted_size_files = [sim_data[num]["size_file"] for num in sorted_sim_nums]
    sorted_supersats = [sim_data[num]["supersat"] for num in sorted_sim_nums]

    logger.info(
        f"Extracted {len(sorted_supersats)} supersaturation values from simulation_parameters.txt files"
    )
    logger.info(
        f"Supersaturation range: {min(sorted_supersats):.2f} to {max(sorted_supersats):.2f} kcal/mol"
    )

    return sorted_size_files, sorted_supersats


def main():
    parser = argparse.ArgumentParser(
        description="Calculate and plot growth rates from crystal growth simulation data"
    )
    parser.add_argument(
        "--input", "-i", type=str, required=True, help="Input folder containing size.csv files"
    )
    parser.add_argument(
        "--directions",
        "-d",
        nargs="+",
        required=True,
        help='Crystal directions to analyze (e.g., " 1 0 0" " 0 1 0" " 0 0 1")',
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output folder for plots and CSV (default: input_folder/growth_rate_analysis)",
    )
    parser.add_argument(
        "--supersats",
        "-s",
        nargs="+",
        type=float,
        default=None,
        help="Supersaturation values for each file (optional, will auto-detect if not provided)",
    )
    parser.add_argument(
        "--plot-raw",
        action="store_true",
        help="Plot raw size vs time data for each simulation to investigate fitting",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Setup paths
    input_folder = Path(args.input)
    if not input_folder.exists():
        logger.error(f"Input folder does not exist: {input_folder}")
        return

    if args.output:
        output_folder = Path(args.output)
    else:
        output_folder = input_folder / "growth_rate_analysis"

    output_folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output will be saved to: {output_folder}")

    # Find size files and extract supersaturation values
    if args.supersats:
        # Manual supersaturation override - still need to find and sort size files
        logger.info("Using manually provided supersaturation values")
        size_files, _ = find_size_files_and_supersats(input_folder)
        supersat_list = args.supersats
        if len(supersat_list) != len(size_files):
            logger.warning(
                f"Number of supersaturation values ({len(supersat_list)}) "
                f"does not match number of files ({len(size_files)})"
            )
    else:
        # Automatic extraction from simulation_parameters.txt files
        logger.info("Auto-extracting supersaturation from simulation_parameters.txt files")
        size_files, supersat_list = find_size_files_and_supersats(input_folder)

    if not size_files:
        logger.error("No size files found!")
        return

    # Build growth rates dataframe
    logger.info(f"Calculating growth rates for directions: {args.directions}")

    # Setup raw data output folder if needed
    raw_data_folder = None
    if args.plot_raw:
        raw_data_folder = output_folder / "raw_data_plots"
        logger.info("Raw data plotting enabled")

    gr_df = build_growthrates(
        size_files,
        supersat_list,
        args.directions,
        plot_raw_data=args.plot_raw,
        raw_data_output=raw_data_folder,
    )

    if gr_df is None or gr_df.empty:
        logger.error("Failed to calculate growth rates")
        return

    # Save growth rates CSV
    csv_path = output_folder / "growthrates.csv"
    gr_df.to_csv(csv_path, index=False)
    logger.info(f"Growth rates saved to: {csv_path}")

    # Display DataFrame
    print("\nGrowth Rates DataFrame:")
    print(gr_df.to_string())

    # Generate plots
    logger.info("Generating growth rate summary plots...")
    plot_growth_rates(gr_df, args.directions, output_folder)

    if args.plot_raw:
        logger.info(f"Raw data plots saved to: {raw_data_folder}")

    logger.info("Done! Check the output folder for results.")


if __name__ == "__main__":
    main()
