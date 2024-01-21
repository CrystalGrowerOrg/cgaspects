import sys
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from crystalaspects.analysis.shape_analysis import CrystalShape


class TestCrystalShape:
    @pytest.fixture
    def crystal(self):
        """Fixture to create a CrystalShape instance with sample data."""
        c = CrystalShape()
        c.set_xyz(xyz_array=np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]))
        return c

    def test_set_xyz(self, crystal):
        """Test the set_xyz method."""
        assert crystal.xyz is not None
        assert crystal.xyz.shape == (3, 3)

    def test_normalise_verts(self, crystal):
        """Test the _normalise_verts method."""
        normalized = crystal._normalise_verts(crystal.xyz)
        assert np.isclose(np.linalg.norm(normalized, axis=1).max(), 1)

    def test_read_XYZ(self, tmp_path):
        """Test the read_XYZ method."""
        # Create a temporary XYZ file
        pwf = Path(__file__).parents[4] / "example" / "normal"

        xyz, xyz_movie, progress_num = CrystalShape.read_XYZ(p)
        assert xyz.shape == (3, 3)
        assert xyz_movie == {}
        assert progress_num == 100

    def test_get_pca(self, crystal):
        """Test the get_pca method."""
        pca_svalues = crystal.get_pca()
        assert len(pca_svalues) == 3
        assert all(isinstance(value, float) for value in pca_svalues)

    def test_get_sa_vol_ratio(self, crystal):
        """Test the get_sa_vol_ratio method."""
        sa_vol_ratio_array = crystal.get_sa_vol_ratio()
        assert sa_vol_ratio_array.shape == (1, 3)

    def test_get_oba(self, crystal):
        """Test the get_oba method."""
        oba_array = crystal.get_oba()
        assert oba_array.shape == (1, 6)

    def test_get_shape_class(self, crystal):
        """Test the get_shape_class method."""
        assert crystal.get_shape_class(0.5, 0.5) == "Lath"
        assert crystal.get_shape_class(0.8, 0.5) == "Needle"
        assert crystal.get_shape_class(0.8, 0.8) == "Block"
        assert crystal.get_shape_class(0.5, 0.8) == "Plate"
        assert crystal.get_shape_class(-1, -1) == "unknown"

    def test_get_all(self, crystal):
        """Test the get_all method."""
        shape_info = crystal.get_all()
        assert isinstance(shape_info, tuple), "Output should be a tuple"
        assert len(shape_info) == 5, "Tuple should contain five elements"
        assert 0 <= shape_info.aspect1 <= 1, "Aspect ratio 1 should be in [0, 1]"
        assert 0 <= shape_info.aspect2 <= 1, "Aspect ratio 2 should be in [0, 1]"
        assert shape_info.sa > 0
        assert shape_info.vol > 0
        assert shape_info.sa_vol > 0
