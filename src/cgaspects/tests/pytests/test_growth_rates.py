import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from pathlib import Path
from cgaspects.analysis.gui_threads import WorkerSignals
from cgaspects.analysis.gr_dataframes import build_growthrates


class TestBuildGrowthrates(unittest.TestCase):
    def setUp(self):
        # A generic DataFrame to use as dummy CSV data
        self.dummy_df = pd.DataFrame(
            {
                "time": np.arange(0, 10, 0.5),
                "-1 0 0": np.random.rand(20) * 10,
                " 0 0 1": np.random.rand(20) * 20,
            }
        )
        self.dummy_csv = self.dummy_df.to_csv(index=False)

    @patch("pandas.read_csv")
    def test_empty_size_file_list_returns_none(self, mock_read_csv):
        result = build_growthrates([], [], [])
        self.assertIsNone(result)

    @patch("pandas.read_csv")
    def test_progress_signal_emitted(self, mock_read_csv):
        mock_read_csv.return_value = self.dummy_df
        size_file_list = [Path("file1.csv"), Path("file2.csv")]
        supersat_list = [1.0, 1.5]
        directions = [" 0 0 1"]
        mock_signal = MagicMock(spec=WorkerSignals)
        build_growthrates(
            size_file_list, supersat_list, directions, signals=mock_signal
        )
        mock_signal.progress.emit.assert_any_call(50)
        mock_signal.progress.emit.assert_any_call(100)

    @patch("pandas.read_csv")
    def test_with_specified_directions(self, mock_read_csv):
        mock_read_csv.return_value = self.dummy_df
        size_file_list = [MagicMock(name="dummy_size.csv")]
        supersat_list = [1.0]
        directions = [" 0 0 1"]
        result = build_growthrates(size_file_list, supersat_list, directions)
        self.assertIsNotNone(result)
        # Verify that the DataFrame only includes the specified direction
        # in addition to the Simulation Number and Supersaturation
        expected_columns = ["Simulation Number", "Supersaturation", " 0 0 1"]
        self.assertListEqual(list(result.columns), expected_columns)

    @patch("pandas.read_csv")
    def test_mismatched_supersat_list_length(self, mock_read_csv):
        mock_read_csv.return_value = self.dummy_df
        size_file_list = [MagicMock(), MagicMock()]
        directions = [" 0 0 1"]
        supersat_list = [1.0]
        with self.assertRaises(ValueError):
            build_growthrates(size_file_list, supersat_list, directions)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
