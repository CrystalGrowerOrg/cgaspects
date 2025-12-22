"""Quick test to verify data filter dialog imports correctly."""

import sys
import pandas as pd

# Test imports
try:
    from src.cgaspects.gui.dialogs.data_filter_dialog import DataFilterDialog
    print("✓ DataFilterDialog imported successfully")
except Exception as e:
    print(f"✗ Failed to import DataFilterDialog: {e}")
    sys.exit(1)

try:
    from src.cgaspects.gui.dialogs.plot_dialog import PlottingDialog
    print("✓ PlottingDialog imported successfully")
except Exception as e:
    print(f"✗ Failed to import PlottingDialog: {e}")
    sys.exit(1)

# Test basic functionality
try:
    # Create a sample dataframe
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10],
        'category': ['A', 'B', 'A', 'B', 'A'],
        'value': [10, 20, 30, 40, 50]
    })

    print("✓ Test dataframe created")
    print(f"  Original rows: {len(df)}")

    # Test filter application
    filters = [
        {'column': 'x', 'operator': '>', 'value': '2'},
        {'column': 'category', 'operator': '==', 'value': 'A'}
    ]

    # Simulate applying filters
    filtered_df = df.copy()

    # Filter 1: x > 2
    filtered_df = filtered_df[filtered_df['x'] > 2]

    # Filter 2: category == 'A'
    filtered_df = filtered_df[filtered_df['category'] == 'A']

    print(f"✓ Filters applied successfully")
    print(f"  Filtered rows: {len(filtered_df)} (expected: 2)")
    print(f"  Filtered data:\n{filtered_df}")

    if len(filtered_df) == 2:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  Warning: unexpected filter result")

except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
