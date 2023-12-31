import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import List
from crystalaspects.analysis.aspect_ratios import AspectRatio
from crystalaspects.fileio.find_data import find_info

root_test_dir = Path(__file__).parent

TEST_DIR = "src/crystalaspects/tests/simulations/morphology/energies/20231110_114217"

# Fixture for AspectRatio instance
@pytest.fixture
def aspect_ratio():
    return AspectRatio()

# Fixture for mock logger to avoid actual logging during tests
@pytest.fixture
def mock_logger(monkeypatch):
    mock_logger = MagicMock()
    monkeypatch.setattr('crystalaspects.analysis.aspect_ratios.logger', mock_logger)
    return mock_logger

# Fixture for mock dialog to avoid GUI interaction during tests
@pytest.fixture
def mock_dialog(monkeypatch):
    mock_dialog = MagicMock()
    monkeypatch.setattr('crystalaspects.analysis.aspect_ratios.QDialog', mock_dialog)

# Fixture for mock Path to avoid file system interaction during tests
@pytest.fixture
def mock_path(monkeypatch):
    mock_path = MagicMock(spec=Path)
    monkeypatch.setattr('crystalaspects.analysis.aspect_ratios.Path', mock_path)
    return mock_path

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
    # assert isinstance(info.supersats, list), "Supersats should be a list"
    # assert all(isinstance(x, float) for x in info.supersats), "All items in supersats should be floats"
    # assert isinstance(info.size_files, List[Path] | None), "Size_files should be a list of path objects (if not None)"
    # assert isinstance(info.directions, list), "Directions should be a list"
    # assert isinstance(info.growth_mod, bool), "Growth_mod should be a boolean"
    # assert isinstance(info.folders, List[Path]), "Folders should be a list"
    # assert isinstance(info.summary_file, Path | None), "Summary_file should be None or a Path object"
    # # Content asserts
    # assert len(info.supersats) == 1, "There should be at least one supersaturation value"
    # assert len(info.size_files) >= 1, "There should be at least one size file"
    # assert len(info.directions) >= 1, "There should be at least one direction"
    # assert len(info.folders) >= 1, "There should be at least one folder"
    # # Specific asserts
    # assert 0.5 in info.supersats, "The known supersaturation value 0.5 should be in the list"
    # assert '100' in info.directions, "The direction '100' should be in the list"
    # assert info.summary_file is not None, "Summary file should exist"
    # assert info.growth_mod is True or info.growth_mod is False, "Growth modifier should be a boolean value"


# Example test for calculate_aspect_ratio

def test_calculate_aspect_ratio_no_folder(aspect_ratio, mock_logger, mock_dialog):
    # Test behavior when no input folder is set
    aspect_ratio.calculate_aspect_ratio()
    mock_logger.debug.assert_called()