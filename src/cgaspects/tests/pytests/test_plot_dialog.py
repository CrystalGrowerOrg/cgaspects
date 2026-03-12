import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
import sys
import pandas as pd
from cgaspects.gui.dialogs.plot_dialog import PlottingDialog, format_label


class TestPlottingDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a QApplication instance
        cls.app = QApplication(sys.argv)

    def setUp(self):
        # Create a sample CSV data
        self.csv_data = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5],
                "y": [2, 4, 6, 8, 10],
                "c": ["A", "B", "A", "B", "A"],
            }
        )

    def test_plotting_dialog_functionality(self):
        # Create an instance of PlottingDialog
        dialog = PlottingDialog(self.csv_data)

        # Test if the dialog is created successfully
        self.assertIsNotNone(dialog)

        # Test if the window title is set correctly
        self.assertEqual(dialog.windowTitle(), "Plot Window")

        # Test if the geometry is set correctly
        self.assertEqual(dialog.geometry().topLeft().x(), 100)
        self.assertEqual(dialog.geometry().topLeft().y(), 100)
        self.assertEqual(dialog.geometry().width(), 850)
        self.assertEqual(dialog.geometry().height(), 1000)

        # Test if the dialog is non-modal
        self.assertEqual(dialog.windowModality(), Qt.NonModal)

        # Test if the CSV data is set correctly
        self.assertIsNotNone(dialog.csv)

        # Test if the plot defaults are set
        self.assertFalse(dialog.grid)
        self.assertIsNone(dialog.cbar)
        self.assertEqual(dialog.point_size, 12)
        self.assertEqual(dialog.plot_type, "Heatmap")
        self.assertEqual(dialog.permutation, 0)
        self.assertEqual(dialog.variable, "None")
        self.assertIsNone(dialog.custom_x)
        self.assertEqual(dialog.custom_y, [])
        self.assertEqual(dialog.custom_c, "None")
        self.assertEqual(dialog.title, "Heatmap")

        # Test if widgets are created
        # self.assertIsNotNone(dialog.findChild())

        # Add more specific tests

    def test_format_label(self):
        # Test the format_label function
        self.assertEqual(format_label("total_events"), "Total Events")
        self.assertEqual(format_label("tile_type"), "Tile Type")
        self.assertEqual(format_label("site_number"), "Site Number")
        self.assertEqual(format_label("coordination"), "Coordination")
        self.assertEqual(format_label("energy"), "Energy")
        self.assertEqual(format_label("occupation"), "Occupation")
        self.assertEqual(format_label("total_population"), "Total Population")
        self.assertEqual(format_label(""), "")
        self.assertIsNone(format_label(None))

    @classmethod
    def tearDownClass(cls):
        # Clean up the QApplication
        cls.app.quit()


if __name__ == "__main__":
    unittest.main()
