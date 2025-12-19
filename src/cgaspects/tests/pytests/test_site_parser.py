"""
Tests for the site parser module.
"""

import unittest
from pathlib import Path

from cgaspects.analysis.site_parser import (
    extract_file_prefix,
    get_site_summary,
    merge_site_results,
    parse_multiple_site_csvs,
    parse_site_csv,
)


class TestParseSiteCSV(unittest.TestCase):
    """Tests for parsing site CSV files."""

    def setUp(self):
        """Set up test fixtures."""
        # Get the path to the test resources directory
        self.test_dir = Path(__file__).parent.parent / "res"
        self.crystallisation_csv = self.test_dir / "test_crystallisation_events.csv"
        self.population_csv = self.test_dir / "test_populations.csv"

    def test_file_exists(self):
        """Test that test CSV files exist."""
        self.assertTrue(
            self.crystallisation_csv.exists(),
            f"Crystallisation events CSV not found at {self.crystallisation_csv}",
        )
        self.assertTrue(
            self.population_csv.exists(), f"Population CSV not found at {self.population_csv}"
        )

    def test_parse_crystallisation_events(self):
        """Test parsing crystallisation events CSV."""
        result = parse_site_csv(self.crystallisation_csv)

        # Check structure
        self.assertIn("supersaturation", result)
        self.assertIn("time", result)
        self.assertIn("iterations", result)
        self.assertIn("file_type", result)
        self.assertIn("sites", result)

        # Check file type is detected correctly
        self.assertEqual(result["file_type"], "events")

        # Check that we have data - sites should be a dictionary
        self.assertIsInstance(result["sites"], dict, "Sites should be a dictionary")
        self.assertGreater(len(result["sites"]), 0, "Should have parsed at least one site")
        self.assertGreater(len(result["supersaturation"]), 0, "Should have supersaturation data")
        self.assertGreater(len(result["time"]), 0, "Should have time data")
        self.assertGreater(len(result["iterations"]), 0, "Should have iterations data")

        # Check that lists have consistent lengths
        self.assertEqual(
            len(result["supersaturation"]),
            len(result["time"]),
            "Supersaturation and time should have same length",
        )
        self.assertEqual(
            len(result["time"]),
            len(result["iterations"]),
            "Time and iterations should have same length",
        )

    def test_parse_populations(self):
        """Test parsing populations CSV."""
        result = parse_site_csv(self.population_csv)

        # Check structure
        self.assertIn("supersaturation", result)
        self.assertIn("time", result)
        self.assertIn("iterations", result)
        self.assertIn("file_type", result)
        self.assertIn("sites", result)

        # Check file type is detected correctly
        self.assertEqual(result["file_type"], "population")

        # Check that we have data - sites should be a dictionary
        self.assertIsInstance(result["sites"], dict, "Sites should be a dictionary")
        self.assertGreater(len(result["sites"]), 0, "Should have parsed at least one site")
        self.assertGreater(len(result["supersaturation"]), 0, "Should have supersaturation data")

    def test_site_structure(self):
        """Test that sites have the expected structure."""
        result = parse_site_csv(self.crystallisation_csv)

        # Check first site has all required fields - get first site from dictionary
        first_site_num = next(iter(result["sites"]))
        first_site = result["sites"][first_site_num]
        self.assertIn("tile_type", first_site)
        self.assertIn("energy", first_site)
        self.assertIn("occupation", first_site)
        self.assertIn("coordination", first_site)
        self.assertIn("total_events", first_site)
        self.assertIn("total_population", first_site)
        self.assertIn("events", first_site)
        self.assertIn("population", first_site)

    def test_site_data_types(self):
        """Test that site data has correct types."""
        result = parse_site_csv(self.crystallisation_csv)
        first_site_num = next(iter(result["sites"]))
        first_site = result["sites"][first_site_num]

        # Check types - site_number is the key in the dictionary
        self.assertIsInstance(first_site_num, int)
        self.assertIsInstance(first_site["tile_type"], (int, type(None)))
        self.assertIsInstance(first_site["energy"], (float, type(None)))
        self.assertIsInstance(first_site["occupation"], (bool, type(None)))
        self.assertIsInstance(first_site["coordination"], (int, type(None)))
        self.assertIsInstance(first_site["total_events"], (int, type(None)))
        self.assertIsInstance(first_site["total_population"], (int, type(None)))
        # For events file, events should have data, population should be None
        self.assertIsNotNone(first_site["events"])
        self.assertIsNone(first_site["population"])

    def test_site_numbers_are_correct(self):
        """Test that site numbers match expected values."""
        result = parse_site_csv(self.crystallisation_csv)

        # From the first line of the CSV, we expect site number 2 to be present
        # Site numbers are the keys in the sites dictionary
        self.assertIn(2, result["sites"], "Site number 2 should be in the parsed data")

    def test_tile_types_are_consistent(self):
        """Test that all sites in test data have tile type 1."""
        result = parse_site_csv(self.crystallisation_csv)

        # From the CSV, all sites have tile_type = 1
        for site_data in result["sites"].values():
            if site_data["tile_type"] is not None:
                self.assertEqual(site_data["tile_type"], 1)

    def test_events_data_exists(self):
        """Test that event data is parsed correctly."""
        result = parse_site_csv(self.crystallisation_csv)

        # Check that at least some sites have events
        sites_with_events = [s for s in result["sites"].values() if s["events"] is not None and len(s["events"]) > 0]
        self.assertGreater(len(sites_with_events), 0, "At least some sites should have event data")

        # Check that events list length matches time series length for first site
        first_site_num = next(iter(result["sites"]))
        first_site = result["sites"][first_site_num]
        expected_length = len(result["time"])
        if first_site["events"] is not None:
            self.assertEqual(
                len(first_site["events"]),
                expected_length,
                f"Events list should have {expected_length} entries to match time series",
            )


class TestParseMultipleSiteCSVs(unittest.TestCase):
    """Tests for parsing multiple site CSV files."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent / "res"
        self.crystallisation_csv = self.test_dir / "test_crystallisation_events.csv"
        self.population_csv = self.test_dir / "test_populations.csv"

    def test_parse_multiple_files(self):
        """Test parsing multiple CSV files."""
        csv_paths = [self.crystallisation_csv, self.population_csv]
        results = parse_multiple_site_csvs(csv_paths)

        self.assertEqual(len(results), 2, "Should have parsed 2 files")

        # Each result should have the expected structure
        for result in results:
            self.assertIn("sites", result)
            self.assertGreater(len(result["sites"]), 0)

    def test_empty_list(self):
        """Test parsing empty list of files."""
        results = parse_multiple_site_csvs([])
        self.assertEqual(len(results), 0, "Should return empty list for empty input")


class TestGetSiteSummary(unittest.TestCase):
    """Tests for the site summary function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent / "res"
        self.crystallisation_csv = self.test_dir / "test_crystallisation_events.csv"
        self.parsed_data = parse_site_csv(self.crystallisation_csv)

    def test_summary_structure(self):
        """Test that summary has expected structure."""
        summary = get_site_summary(self.parsed_data)

        expected_keys = [
            "total_sites",
            "occupied_sites",
            "unoccupied_sites",
            "time_points",
            "iterations",
            "supersaturation_points",
            "tile_types",
            "energy_range",
            "coordination_range",
        ]

        for key in expected_keys:
            self.assertIn(key, summary, f"Summary should contain '{key}'")

    def test_summary_counts(self):
        """Test that summary counts are correct."""
        summary = get_site_summary(self.parsed_data)

        # Total sites should match parsed data
        self.assertEqual(summary["total_sites"], len(self.parsed_data["sites"]))

        # Occupied + unoccupied should equal total
        self.assertEqual(
            summary["occupied_sites"] + summary["unoccupied_sites"], summary["total_sites"]
        )

        # Time points should match
        self.assertEqual(summary["time_points"], len(self.parsed_data["time"]))

    def test_energy_range(self):
        """Test that energy range is calculated correctly."""
        summary = get_site_summary(self.parsed_data)

        energy_range = summary["energy_range"]
        self.assertIsInstance(energy_range, list)
        self.assertEqual(len(energy_range), 2)

        if energy_range[0] is not None and energy_range[1] is not None:
            # Min should be less than or equal to max
            self.assertLessEqual(energy_range[0], energy_range[1])

            # Check against actual data - iterate over dictionary values
            energies = [s["energy"] for s in self.parsed_data["sites"].values() if s["energy"] is not None]
            self.assertEqual(energy_range[0], min(energies))
            self.assertEqual(energy_range[1], max(energies))

    def test_tile_types_list(self):
        """Test that tile types are extracted correctly."""
        summary = get_site_summary(self.parsed_data)

        tile_types = summary["tile_types"]
        self.assertIsInstance(tile_types, list)
        self.assertGreater(len(tile_types), 0, "Should have at least one tile type")

        # Tile types should be sorted
        self.assertEqual(tile_types, sorted(tile_types))

        # All tile types from parsed data should be in summary - iterate over dictionary values
        parsed_tile_types = set(
            s["tile_type"] for s in self.parsed_data["sites"].values() if s["tile_type"] is not None
        )
        self.assertEqual(set(tile_types), parsed_tile_types)


class TestMergeSiteResults(unittest.TestCase):
    """Tests for merging site results by prefix."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent / "res"
        self.crystallisation_csv = self.test_dir / "test_crystallisation_events.csv"
        self.population_csv = self.test_dir / "test_populations.csv"

    def test_extract_file_prefix(self):
        """Test extracting prefix from filenames."""
        # Test crystallisation events file
        events_path = Path("run1_crystallisation_events.csv")
        self.assertEqual(extract_file_prefix(events_path), "run1")

        # Test populations file
        pop_path = Path("run1_populations.csv")
        self.assertEqual(extract_file_prefix(pop_path), "run1")

        # Test file without known suffix
        other_path = Path("some_other_file.csv")
        self.assertEqual(extract_file_prefix(other_path), "some_other_file")

    def test_merge_matching_files(self):
        """Test merging files with matching prefixes."""
        # Parse both files
        events_result = parse_site_csv(self.crystallisation_csv)
        pop_result = parse_site_csv(self.population_csv)

        # Create results with paths
        results_with_paths = [
            (events_result, self.crystallisation_csv),
            (pop_result, self.population_csv),
        ]

        # Merge
        merged = merge_site_results(results_with_paths)

        # Should have one merged result (same prefix)
        self.assertEqual(len(merged), 1)

        merged_result = merged[0]

        # Check structure
        self.assertIn("file_prefix", merged_result)
        self.assertIn("source_files", merged_result)
        self.assertIn("sites", merged_result)

        # Check that both files are listed as sources
        self.assertEqual(len(merged_result["source_files"]), 2)

        # Check that sites have both events and population data
        for site_num, site_data in merged_result["sites"].items():
            # Both fields should exist
            self.assertIn("events", site_data)
            self.assertIn("population", site_data)
            self.assertIn("total_events", site_data)
            self.assertIn("total_population", site_data)

    def test_merge_preserves_metadata(self):
        """Test that merging preserves site metadata."""
        events_result = parse_site_csv(self.crystallisation_csv)
        pop_result = parse_site_csv(self.population_csv)

        results_with_paths = [
            (events_result, self.crystallisation_csv),
            (pop_result, self.population_csv),
        ]

        merged = merge_site_results(results_with_paths)
        merged_result = merged[0]

        # Pick a site that exists in both files
        site_num = next(iter(merged_result["sites"]))
        merged_site = merged_result["sites"][site_num]

        # Metadata should be preserved from one of the files
        self.assertIsNotNone(merged_site.get("tile_type"))
        self.assertIsNotNone(merged_site.get("energy"))


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""

    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        fake_path = Path("/nonexistent/path/fake.csv")

        with self.assertRaises(FileNotFoundError):
            parse_site_csv(fake_path)

    def test_sites_is_dict(self):
        """Test that sites is returned as a dict, not a list."""
        test_dir = Path(__file__).parent.parent / "res"
        crystallisation_csv = test_dir / "test_crystallisation_events.csv"
        result = parse_site_csv(crystallisation_csv)

        self.assertIsInstance(result["sites"], dict, "Sites should be a dictionary with site numbers as keys")


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
