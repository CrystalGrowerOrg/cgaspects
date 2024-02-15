import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import os
import pandas as pd
from cgaspects.analysis import ar_dataframes
from cgaspects.analysis.ar_dataframes import (
    build_cda,
    get_cda_shape_percentage,
    build_ratio_equations,
    get_xyz_shape_percentage,
)


class TestBuildCda(unittest.TestCase):
    @patch("cgaspects.analysis.ar_dataframes.os.listdir")
    @patch(
        "cgaspects.analysis.ar_dataframes.open",
        new_callable=unittest.mock.mock_open,
        read_data="Size of crystal at frame output\nlength 5",
    )
    @patch("cgaspects.analysis.ar_dataframes.logger")
    @patch("pandas.DataFrame.from_dict")
    def test_build_cda_basic_functionality(
        self, mock_logger, mock_open, mock_listdir, mock_from_dict
    ):
        folders = ["folder1", "folder2"]
        folderpath = "test_folderpath"
        savefolder = "test_savefolder"
        directions = ["-1 0 0", " 1 1 1", " 0 0 1", " 1 1 0"]
        selected = ["-1 0 0", " 0 0 1", " 1 1 0"]

        mock_listdir.return_value = ["simulation_parameters.txt"]

        dummy_df = pd.DataFrame(
            {
                "Simulation Number": [1, 2],
                "-1 0 0": [0.1, 0.2],
                " 1 1 1": [0.3, 0.4],
                " 0 0 1": [0.5, 0.6],
                " 1 1 0": [0.7, 0.8],
            }
        )

        mock_from_dict.return_value = dummy_df

        df = build_cda(folders, folderpath, savefolder, directions, selected)

        # Perform your assertions here
        self.assertIn("Simulation Number", df.columns)
        self.assertIn(" 1 1 1", df.columns)
        self.assertIn("Ratio_-1 0 0: 0 0 1", df.columns)
        self.assertIn("Ratio_ 0 0 1: 1 1 0", df.columns)

    # Needs more tests to cover edge cases, error handling, etc.


class TestGetXyzShapePercentage(unittest.TestCase):
    @patch("cgaspects.analysis.ar_dataframes.pd.DataFrame.to_csv")
    def test_get_xyz_shape_percentage(self, mock_to_csv):
        df = pd.DataFrame({"Shape": ["lath", "needle", "plate", "lath"]})
        savefolder = Path("/tmp")

        get_xyz_shape_percentage(df, savefolder)
        mock_to_csv.assert_called_once_with(
            f"{savefolder}/shape_counts.csv", index=False
        )


class TestGetCdaShapePercentage(unittest.TestCase):
    @patch("cgaspects.analysis.ar_dataframes.pd.DataFrame.to_csv")
    def test_get_cda_shape_percentage(self, mock_to_csv):
        df = pd.DataFrame(
            {
                "CDA_Permutation": [1, 1, 2],
                "Shape": ["shape1", "shape2", "shape1"],
            }
        )
        savefolder = Path("/tmp")

        get_cda_shape_percentage(df, savefolder)
        mock_to_csv.assert_called_once()
        csv_out = mock_to_csv.call_args
        self.assertEqual(Path("/tmp/shapes_permutations.csv"), csv_out[0][0])

    # Needs more tests for different scenarios and edge cases.
    # Eg. for validating percentages, handling of unexpected shapes, etc.


class TestBuildRatioEquations(unittest.TestCase):
    @patch("cgaspects.analysis.ar_dataframes.pd.read_csv")
    @patch(
        "cgaspects.analysis.ar_dataframes.open", new_callable=unittest.mock.mock_open
    )
    def test_build_ratio_equations_with_csv(self, mock_open, mock_read_csv):
        directions = ["a", "b", "c"]
        mock_read_csv.return_value = pd.DataFrame(
            {"a": [1, 2, 3], "b": [2, 3, 1], "c": [3, 1, 2]}
        )
        filepath = "tmp/"

        df = build_ratio_equations(directions, csv="dummy.csv", filepath=filepath)
        self.assertIn("CDA_Permutation", df.columns)

    # Needs more tests for different scenarios and edge cases.


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
