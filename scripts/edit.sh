#!/bin/bash

# Replace these with your actual module names
old_module_name="PlottingDialogue"
new_module_name="PlottingDialog"

# Loop through all subdirectories and files
for file in $(find . -type f -name "*.py")
do
    # Replace the module name in each file (macOS version of sed)
    sed -i '' "s/$old_module_name/$new_module_name/g" "$file"
done

echo "Module names have been updated."

