"""
Site Analysis module for processing crystallisation events and population data.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QDialog

from .site_parser import (
    get_site_summary,
    merge_site_results,
    parse_multiple_site_csvs,
    parse_site_csv,
)
from ..fileio import find_data as fd
from ..utils.data_structures import results_tuple

logger = logging.getLogger("CA:SiteAnalysis")


class SiteAnalysis:
    """
    Handler for site analysis calculations using crystallisation events
    and population CSV files.
    """

    def __init__(self, signals):
        self.input_folder = None
        self.output_folder = None
        self.information = None
        self.xyz_files: List[Path] | None = None
        self.signals = signals
        self.threadpool = QThreadPool()
        self.result_tuple = results_tuple

        self.crystallisation_files: List[Path] = []
        self.population_files: List[Path] = []
        self.parsed_data = None

    def update_progress(self, value):
        """Emit progress update signal."""
        self.signals.progress.emit(value)

    def set_folder(self, folder):
        """Set the input folder for analysis."""
        self.input_folder = Path(folder)
        logger.info("Folder set for site analysis")

    def set_information(self, information):
        """Set the file information for analysis."""
        self.information = information
        logger.info("Information set for site analysis")

    def set_xyz_files(self, xyz_files: List[Path]):
        """Set the list of XYZ files."""
        self.xyz_files = xyz_files

    def set_site_files(self, crystallisation_files: List[Path], population_files: List[Path]):
        """Set the crystallisation events and population CSV files."""
        self.crystallisation_files = crystallisation_files
        self.population_files = population_files
        logger.info(f"Set {len(crystallisation_files)} crystallisation files and "
                   f"{len(population_files)} population files")

    def calculate_site_analysis(self):
        """
        Perform site analysis by parsing crystallisation events and population CSVs.
        """
        logger.debug("Called site analysis method at directory: %s", self.input_folder)

        if not self.input_folder:
            logger.warning("Input folder not set")
            return

        if self.information is None:
            logger.warning("Method called without information, looking for information now.")
            self.information = fd.find_info(self.input_folder)

        if not (self.crystallisation_files or self.population_files):
            logger.warning("No crystallisation events or population files found")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                None,
                "No Site Data",
                "No crystallisation events or population CSV files were found in the directory.\n"
                "Please make sure the directory contains files matching:\n"
                "*_crystallisation_events.csv or *_populations.csv"
            )
            return

        logger.info("Attempting to perform Site Analysis...")

        # For now, we'll create a simple dialog to let users choose what to analyze
        # TODO: Create a proper dialog for site analysis options

        self.output_folder = fd.create_aspects_folder(self.input_folder)
        self.signals.location.emit(self.output_folder)
        self.signals.started.emit()

        try:
            # Parse all CSV files
            results_with_paths = []

            if self.crystallisation_files:
                logger.info(f"Parsing {len(self.crystallisation_files)} crystallisation event files")
                for csv_path in self.crystallisation_files:
                    try:
                        result = parse_site_csv(csv_path)
                        results_with_paths.append((result, csv_path))
                    except Exception as e:
                        logger.error(f"Error parsing {csv_path}: {e}", exc_info=True)

            if self.population_files:
                logger.info(f"Parsing {len(self.population_files)} population files")
                for csv_path in self.population_files:
                    try:
                        result = parse_site_csv(csv_path)
                        results_with_paths.append((result, csv_path))
                    except Exception as e:
                        logger.error(f"Error parsing {csv_path}: {e}", exc_info=True)

            # Merge results by file prefix
            merged_results = merge_site_results(results_with_paths)
            self.parsed_data = merged_results

            # Generate summaries
            for idx, result in enumerate(merged_results):
                summary = get_site_summary(result)
                prefix = result.get("file_prefix", f"File {idx + 1}")
                logger.info(f"{prefix}: {summary['total_sites']} sites, "
                          f"{summary['occupied_sites']} occupied, "
                          f"{summary['time_points']} time points")

            # Save parsed data summary to a file
            summary_path = self.output_folder / "site_analysis_summary.txt"
            self._save_summary(merged_results, summary_path)

            # Save parsed data as JSON for plotting
            json_path = self.output_folder / "site_analysis_data.json"
            self._save_json(merged_results, json_path)

            logger.info(f"Site analysis complete. Results saved to {self.output_folder}")

            result = self.result_tuple(
                csv=json_path,
                selected=None,
                folder=self.output_folder
            )

            self.signals.finished.emit()
            self.signals.result.emit(result)

        except Exception as e:
            logger.error(f"Error during site analysis: {e}", exc_info=True)
            self.signals.finished.emit()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Site Analysis Error",
                f"An error occurred during site analysis:\n{str(e)}"
            )

    def _save_summary(self, merged_results: List[dict], output_path: Path):
        """Save a text summary of the merged parsed data."""
        with open(output_path, 'w') as f:
            f.write("Site Analysis Summary\n")
            f.write("=" * 80 + "\n\n")

            for idx, result in enumerate(merged_results):
                summary = get_site_summary(result)
                prefix = result.get("file_prefix", f"Result {idx + 1}")
                source_files = result.get("source_files", [])

                f.write(f"Prefix: {prefix}\n")
                f.write(f"Source Files: {', '.join(source_files)}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total sites: {summary['total_sites']}\n")
                f.write(f"Occupied sites: {summary['occupied_sites']}\n")
                f.write(f"Unoccupied sites: {summary['unoccupied_sites']}\n")
                f.write(f"Sites with events data: {summary.get('sites_with_events', 'N/A')}\n")
                f.write(f"Sites with population data: {summary.get('sites_with_population', 'N/A')}\n")
                f.write(f"Sites with both: {summary.get('sites_with_both', 'N/A')}\n")
                f.write(f"Time points: {summary['time_points']}\n")
                f.write(f"Iterations: {summary['iterations']}\n")
                f.write(f"Supersaturation points: {summary['supersaturation_points']}\n")
                f.write(f"Tile types: {summary['tile_types']}\n")
                f.write(f"Energy range: {summary['energy_range']}\n")
                f.write(f"Coordination range: {summary['coordination_range']}\n")
                f.write("\n")

                # Write site details
                f.write("Site Details (first 10 sites):\n")
                site_items = list(result['sites'].items())[:10]
                for site_num, site_data in site_items:
                    energy_str = f"{site_data['energy']:.2f}" if site_data['energy'] is not None else "None"
                    events_len = len(site_data['events']) if site_data['events'] is not None else 0
                    pop_len = len(site_data['population']) if site_data['population'] is not None else 0

                    f.write(f"  Site {site_num}:\n")
                    f.write(f"    Metadata: tile_type={site_data['tile_type']}, "
                           f"energy={energy_str}, occupation={site_data['occupation']}, "
                           f"coordination={site_data['coordination']}\n")
                    f.write(f"    Events: total={site_data['total_events']}, "
                           f"data_points={events_len}\n")
                    f.write(f"    Population: total={site_data['total_population']}, "
                           f"data_points={pop_len}\n")

                if len(result['sites']) > 10:
                    f.write(f"  ... and {len(result['sites']) - 10} more sites\n")

                f.write("\n" + "=" * 80 + "\n\n")

    def _save_json(self, merged_results: List[dict], output_path: Path):
        """Save the merged parsed data as JSON for plotting."""

        def convert_to_serializable(obj):
            """Convert numpy types to Python native types for JSON serialization."""
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            return obj

        # Convert the results to JSON-serializable format
        serializable_results = convert_to_serializable(merged_results)

        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)

        logger.info(f"Saved site analysis data to {output_path}")
