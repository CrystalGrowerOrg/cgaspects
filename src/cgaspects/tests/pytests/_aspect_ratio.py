import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from cgaspects.analysis.aspect_ratios import AspectRatio
from cgaspects.fileio.find_data import find_info

root_test_dir = Path(__file__).parent

TEST_DIR = "src/cgaspects/tests/simulations/morphology/energies/20231110_114217"


@pytest.fixture(scope="session", autouse=True)
def qapplication():
    app = QApplication(sys.argv)
    yield app


# Fixture for AspectRatio instance
@pytest.fixture
def aspect_ratio():
    return AspectRatio()


# Fixture for mock logger to avoid actual logging during tests
@pytest.fixture
def mock_logger(monkeypatch):
    mock_logger = MagicMock()
    monkeypatch.setattr("cgaspects.analysis.aspect_ratios.logger", mock_logger)
    return mock_logger


# Fixture for mock dialog to avoid GUI interaction during tests
@pytest.fixture
def mock_dialog(monkeypatch):
    mock_dialog = MagicMock()
    monkeypatch.setattr("cgaspects.analysis.aspect_ratios.QDialog", mock_dialog)


# Fixture for mock Path to avoid file system interaction during tests
@pytest.fixture
def mock_path(monkeypatch):
    mock_path = MagicMock(spec=Path)
    monkeypatch.setattr("cgaspects.analysis.aspect_ratios.Path", mock_path)
    return mock_path


@pytest.fixture
def mock_analysis_options_dialog(monkeypatch):
    # Create a MagicMock instance for the dialog
    mock_dialog = MagicMock(
        name="cgaspects.gui.aspectratio_dialog.AnalysisOptionsDialog"
    )
    mock_dialog.exec_.return_value = QDialog.Accepted
    mock_dialog.get_options.return_value = (
        True,
        True,
        ["-1  0  1", " 0  1  1", " 1  1  0", " 0  0  1", " 0  1  0", " 1  0  0"],
        [" 0  1  1", " 1  1  0", " 0  0  1"],
        False,
    )

    monkeypatch.setattr(
        "cgaspects.gui.aspectratio_dialog.AnalysisOptionsDialog", mock_dialog
    )
    yield mock_dialog


@pytest.fixture
def mock_qmessagebox(monkeypatch):
    with monkeypatch.context() as m:
        # Mock the static methods used in your code
        m.setattr(QMessageBox, "information", MagicMock())
        yield


@pytest.fixture
def mock_plotting_dialogue(monkeypatch):
    mock_instance = MagicMock()
    monkeypatch.setattr(
        "cgaspects.visualisation.replotting.PlottingDialog", mock_instance
    )


# Tests for set_folder
def test_set_folder(aspect_ratio, mock_logger, mock_path):
    aspect_ratio.set_folder(TEST_DIR)
    mock_path.assert_called_with(TEST_DIR)
    mock_logger.info.assert_called_with("Folder set for aspect ratio calculations")


# Test finding information from folder
def test_find_informations():
    info = find_info(TEST_DIR)
    print(info)

    assert info is not None, "find_info should return an object, got None instead"
    # Type asserts
    assert isinstance(info.supersats, list), "Supersats should be a list"
    assert all(
        isinstance(x, float) for x in info.supersats
    ), "All items in supersats should be floats"
    assert isinstance(info.size_files, list | None), "Size_files should be a list"
    if info.size_files:
        assert all(
            isinstance(x, Path) for x in info.size_files
        ), "All items in size_files should be Path objects (when not None)"
    assert isinstance(info.directions, list), "Directions should be a list"
    assert isinstance(info.growth_mod, bool), "Growth_mod should be a boolean"
    assert isinstance(info.folders, list), "Folders should be a list"
    assert isinstance(
        info.summary_file, (None | Path)
    ), "Summary_file should be None or a Path object"

    # # Content asserts
    assert len(info.supersats) == 81, "There should be 81 supersaturation values"
    assert len(info.directions) == 18, "There should be 18 directions"
    assert len(info.folders) >= 81, "There should be 81 folders"
    # Specific asserts
    assert (
        100.0 in info.supersats
    ), "The known supersaturation value 100.0 should be in the list"
    assert info.directions == [
        "-1  0 -1",
        "-1  0  1",
        " 0 -1 -1",
        " 0 -1  1",
        " 0  1 -1",
        " 0  1  1",
        " 1  0 -1",
        " 1  0  1",
        "-1 -1  0",
        "-1  1  0",
        " 1 -1  0",
        " 1  1  0",
        " 0  0 -1",
        " 0  0  1",
        "-1  0  0",
        " 0 -1  0",
        " 0  1  0",
        " 1  0  0",
    ], "The direction '100' should be in the list"

    assert info.summary_file is not None, "Summary file should exist"


def test_calc_ar_no_folder(aspect_ratio, mock_logger, mock_dialog):
    # Test behavior when no input folder is set
    print(aspect_ratio.input_folder)
    aspect_ratio.calculate_aspect_ratio()
    mock_logger.debug.assert_called()


def test_calc_ar_with_mocks(
    aspect_ratio,
    mock_logger,
    mock_analysis_options_dialog,
    mock_qmessagebox,
    mock_plotting_dialogue,
    qapplication,
):
    # Set the test environment, e.g., setting the folder
    aspect_ratio.set_folder(TEST_DIR)

    # Call the method under test
    aspect_ratio.calculate_aspect_ratio()

    # Assert that the dialog was created and called correctly
    mock_analysis_options_dialog.exec_.assert_called_once()
    mock_analysis_options_dialog.get_options.assert_called_once()

    # Assert interactions with the mocked dialogs and message boxes
    mock_qmessagebox.information.assert_called_once()
    mock_plotting_dialogue.assert_called_once()
