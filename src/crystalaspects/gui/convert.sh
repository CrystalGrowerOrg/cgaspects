#!/bin/bash

# Define file names
UI_FILE="mainwindow.ui"
RC_FILE="../../../res/qticons.qrc"
PY_FILE="load_ui.py"
RC_PY_FILE="qticons_rc.py"

# Convert .ui file to .py file
pyside6-uic $UI_FILE -o $PY_FILE

# Convert .qrc file to Python
pyside6-rcc $RC_FILE -o $RC_PY_FILE

# Modify the import statement in the .py file
# Use "" for macOS (BSD sed) or remove for Linux (GNU sed)
sed -i '' 's/import qticons_rc/from crystalaspects.gui import qticons_rc/g' $PY_FILE


echo "Conversion complete!"

