import sys
from pathlib import Path
from typing import List
from unittest.mock import patch, mock_open

import numpy as np
import unittest

from crystalaspects.analysis.shape_analysis import CrystalShape


class TestCrystalShape(unittest.TestCase):

    def setUp(self):
        self.crystal = CrystalShape()

    def test_initialization(self):
        self.assertIsNone(self.crystal.xyz)
        self.assertTrue(hasattr(self.crystal, "shape_tuple"))

    def test_set_xyz_with_array(self):
        test_array = np.array([[1, 2, 3], [4, 5, 6]])
        self.crystal.set_xyz(xyz_array=test_array)
        np.testing.assert_array_equal(self.crystal.xyz, test_array)

    def test_set_xyz_with_filepath(self):
        test_array = np.array([[1, 2, 3], [4, 5, 6]])
        with patch("numpy.loadtxt", return_value=test_array) as mock_loadtxt:
            self.crystal.set_xyz(filepath="fakepath.txt")
            np.testing.assert_array_equal(self.crystal.xyz, test_array)
            mock_loadtxt.assert_called_once()

    def test_set_xyz_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.crystal.set_xyz()

    def test_normalise_verts(self):
        verts = np.array([[1, 2, 3], [-1, -2, -3], [4, 5, 6]])
        normalized_verts = self.crystal._normalise_verts(verts)
        # Check if the vertices are centered around the origin
        self.assertAlmostEqual(np.mean(normalized_verts), 0)
        # Check if the maximum norm is 1
        self.assertAlmostEqual(np.max(np.linalg.norm(normalized_verts, axis=1)), 1)

    def test_get_sa_vol_ratio(self):
        self.crystal.xyz = np.array(
            [
                [0, 0, 0],
                [3, 0, 0],
                [0, 3, 0],
                [0, 0, 3],
                [3, 3, 0],
                [0, 3, 3],
                [3, 0, 3],
                [3, 3, 3],
            ]
        )
        sa_vol_ratio = self.crystal.get_sa_vol_ratio()
        expected_sa = 54
        expected_vol = 27
        expected_ratio = expected_sa / expected_vol
        np.testing.assert_almost_equal(sa_vol_ratio[0], expected_sa, decimal=5)
        np.testing.assert_almost_equal(sa_vol_ratio[1], expected_vol, decimal=5)
        np.testing.assert_almost_equal(sa_vol_ratio[2], expected_ratio, decimal=5)

    def test_get_shape_class(self):
        # Test for each shape classification
        self.assertEqual(self.crystal.get_shape_class(0.5, 0.5), "Lath")
        self.assertEqual(self.crystal.get_shape_class(0.5, 0.8), "Plate")
        self.assertEqual(self.crystal.get_shape_class(0.8, 0.8), "Block")
        self.assertEqual(self.crystal.get_shape_class(0.8, 0.5), "Needle")

    def test_get_zingg_analysis(self):
        self.crystal.xyz = np.array([[0, 0, 0], [2, 0, 0], [0, 2, 0], [0, 0, 2]])
        shape_info = self.crystal.get_zingg_analysis(get_sa_vol=False)

        self.assertAlmostEqual(shape_info.x, 2)
        self.assertAlmostEqual(shape_info.y, 2)
        self.assertAlmostEqual(shape_info.z, 2)

        self.assertAlmostEqual(shape_info.aspect1, 1)
        self.assertAlmostEqual(shape_info.aspect2, 1)
        # Check if the shape classification is correct for a cube
        self.assertEqual(shape_info.shape, "Block")


if __name__ == "__main__":

    unittest.main()
