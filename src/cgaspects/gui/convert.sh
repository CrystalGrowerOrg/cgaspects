#!/bin/bash

UI_FILE="window.ui"
RC_FILE="../../../res/qticons.qrc"
PY_FILE="load_ui.py"
RC_PY_FILE="utils/qticons_rc.py"

# Convert main .ui file to .py file
pyside6-uic $UI_FILE -o $PY_FILE

# Convert .qrc file to Python
pyside6-rcc $RC_FILE -o $RC_PY_FILE

# Modify the import statement in the .py file
# Use "" for macOS (BSD sed) or remove for Linux (GNU sed)
sed -i '' 's/import qticons_rc/from cgaspects.gui.utils import qticons_rc/g' $PY_FILE

# Process additional .ui files in the dialogs folder
for file in dialogs/*.ui; do
    echo "Converting $file"
    # Define the output Python file name based on the UI file
    dialog_py_file=$(echo $file | sed 's/\.ui/_ui.py/')

    # Convert .ui file to .py file
    pyside6-uic $file -o $dialog_py_file

    # Modify the import statement in the .py file
    sed -i '' 's/import qticons_rc/from cgaspects.gui.utils import qticons_rc/g' $dialog_py_file
done

echo "Conversion complete!"
