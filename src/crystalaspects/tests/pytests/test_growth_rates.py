import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from crystalaspects.analysis.gr_dataframes import build_growthrates


class TestBuildGrowthrates(unittest.TestCase):
    def setUp(self):
        # A generic DataFrame to use as dummy CSV data
        self.dummy_df = pd.DataFrame(
            {
                "time": np.arange(0, 10, 0.5),
                "length1": np.random.rand(20) * 10,
                "length2": np.random.rand(20) * 20,
            }
        )
        self.dummy_csv = self.dummy_df.to_csv(index=False)

    @patch("pandas.read_csv")
    def test_empty_size_file_list_returns_none(self, mock_read_csv):
        result = build_growthrates([], [])
        self.assertIsNone(result)

    @patch("pandas.read_csv")
    def test_single_file_with_no_directions(self, mock_read_csv):
        # Mock to return the dummy DataFrame when any string path is passed
        mock_read_csv.return_value = self.dummy_df
        # Use a string to represent the file path instead of MagicMock
        dummy_file = MagicMock()
        dummy_file.name = "dummy_size.csv"
        size_file_list = [dummy_file]
        supersat_list = [1.0]
        result = build_growthrates(size_file_list, supersat_list)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)

        mock_read_csv.assert_called_with(dummy_file)
        # Check if DataFrame has expected columns
        expected_columns = [
            "Simulation Number",
            "Supersaturation",
            "length1",
            "length2",
        ]
        self.assertListEqual(list(result.columns), expected_columns)

    @patch("pandas.read_csv")
    def test_progress_signal_emitted(self, mock_read_csv):
        mock_read_csv.return_value = self.dummy_df
        size_file_list = [MagicMock(name="file1.csv"), MagicMock(name="file2.csv")]
        supersat_list = [1.0, 1.5]
        mock_signal = MagicMock()
        build_growthrates(size_file_list, supersat_list, signals=mock_signal)
        # Ensure the progress signal was emitted with expected values
        mock_signal.progress.emit.assert_any_call(50)
        mock_signal.progress.emit.assert_any_call(100)

    @patch("pandas.read_csv")
    def test_with_specified_directions(self, mock_read_csv):
        mock_read_csv.return_value = self.dummy_df
        size_file_list = [MagicMock(name="dummy_size.csv")]
        supersat_list = [1.0]
        directions = ["length1"]
        result = build_growthrates(size_file_list, supersat_list, directions=directions)
        self.assertIsNotNone(result)
        # Verify that the DataFrame only includes the specified direction in addition to the Simulation Number and Supersaturation
        expected_columns = ["Simulation Number", "Supersaturation", "length1"]
        self.assertListEqual(list(result.columns), expected_columns)

    @patch("pandas.read_csv")
    def test_mismatched_supersat_list_length(self, mock_read_csv):
        mock_read_csv.return_value = self.dummy_df
        size_file_list = [MagicMock(), MagicMock()]
        supersat_list = [1.0]  # Only one supersaturation value provided
        with self.assertRaises(
            ValueError
        ):  # Assuming function raises ValueError for mismatch
            build_growthrates(size_file_list, supersat_list)

    @patch("pandas.read_csv")
    def test_file_reading_error_handling(self, mock_read_csv):
        mock_read_csv.side_effect = [
            pd.DataFrame({"time": [0, 1], "length1": [1, 2]}),
            Exception("File read error"),
        ]
        size_file_list = [MagicMock(), MagicMock()]
        supersat_list = [1.0, 2.0]
        # Assuming the function is designed to skip files that it cannot read
        result = build_growthrates(size_file_list, supersat_list)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)  # Only one row for the successful read
        # Alternatively, if your function raises an exception, replace the above with:
        # with self.assertRaises(Exception):
        #     build_growthrates(size_file_list, supersat_list)


if __name__ == "__main__":
    import pytest

    pytest.main()
