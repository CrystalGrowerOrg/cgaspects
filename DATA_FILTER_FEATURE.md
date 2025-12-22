# Data Filter Feature

## Overview

A new data filtering feature has been added to the Plot Dialog that allows users to filter the X and Y data displayed in plots based on custom conditions.

## Features

### Filter Dialog
- **Multiple Filters**: Add multiple filter conditions that are combined with AND logic
- **Column Selection**: Choose any column from your dataset
- **Operator Support**:
  - Numeric comparisons: `==`, `!=`, `>`, `>=`, `<`, `<=`
  - String operations: `contains`, `not contains`
- **Dynamic Validation**: See how many data points will remain after applying filters
- **Persistent Filters**: Filter configurations are preserved when switching between plot types

### User Interface

#### Filter Button
- Located in the main toolbar between "Add Trendline" and "Customize Labels..."
- Shows count of active filters: "Filter Data... (3)" when filters are applied
- Click to open the filter dialog

#### Filter Dialog Components
1. **Add Filter Button**: Add a new filter row
2. **Clear All Button**: Remove all filters at once
3. **Filter Rows**: Each row contains:
   - Column dropdown: Select the column to filter
   - Operator dropdown: Select the comparison operator
   - Value input: Enter the value to compare against
   - Remove button: Delete this specific filter
4. **Status Label**: Shows how many data points will pass the filters
5. **OK/Cancel Buttons**: Apply or discard filter changes

## Usage

### Basic Example

1. Click the "Filter Data..." button in the plot dialog
2. Select a column (e.g., "temperature")
3. Choose an operator (e.g., ">")
4. Enter a value (e.g., "25")
5. Click "OK" to apply

This will show only data points where temperature > 25.

### Multiple Filters Example

To show data where temperature > 25 AND energy < 100:

1. Click "Filter Data..."
2. First filter: Column="temperature", Operator=">", Value="25"
3. Click "Add Filter"
4. Second filter: Column="energy", Operator="<", Value="100"
5. Click "OK"

### String Filtering Example

To show only data containing a specific solvent:

1. Click "Filter Data..."
2. Column="solvent", Operator="contains", Value="water"
3. Click "OK"

## Implementation Details

### Files Modified

1. **plot_dialog.py**
   - Added filter button and dialog integration
   - Implemented `_apply_data_filters()` method
   - Stores original dataframe (`df_original`) to allow filter changes
   - Preserves filters across plot updates

2. **data_filter_dialog.py** (NEW)
   - `DataFilterDialog`: Main dialog class
   - `FilterRow`: Individual filter row widget
   - Filter application logic with error handling

### Data Flow

```
Original Data (df_original)
    ↓
Apply Filters (_apply_data_filters)
    ↓
Filtered Data (df)
    ↓
Plot Rendering
```

### Filter Persistence

- Filters are stored in `self.data_filters` as a list of dictionaries
- Each filter dictionary contains: `{'column': str, 'operator': str, 'value': str}`
- Filters persist when:
  - Changing plot types
  - Adjusting plot settings
  - Reopening the filter dialog

### Operator Behavior

| Operator | Numeric | String | Description |
|----------|---------|--------|-------------|
| `==` | ✓ | ✓ | Equal to |
| `!=` | ✓ | ✓ | Not equal to |
| `>` | ✓ | - | Greater than |
| `>=` | ✓ | - | Greater than or equal |
| `<` | ✓ | - | Less than |
| `<=` | ✓ | - | Less than or equal |
| `contains` | - | ✓ | String contains (case-insensitive) |
| `not contains` | - | ✓ | String does not contain (case-insensitive) |

### Error Handling

- Invalid numeric values: Logged as error, filter skipped
- Missing columns: Logged as warning, filter skipped
- Empty filter values: Automatically excluded from application
- Type mismatches: Automatic string conversion attempted

## Technical Notes

### Performance
- Filters are applied once per plot update
- Original dataframe is preserved in memory (small memory overhead)
- Filtering uses pandas boolean indexing (efficient for most datasets)

### Compatibility
- Works with all plot types: Custom, Heatmap, Site Analysis, Zingg, CDA, etc.
- Compatible with existing features: permutations, variables, custom axes
- Filters apply to the base dataframe before plot-specific data extraction

### Logging
- Filter application: `INFO` level with row counts
- Column not found: `WARNING` level
- Filter errors: `ERROR` level with exception details

## Future Enhancements (Potential)

- [ ] OR logic support (currently only AND)
- [ ] Save/load filter presets
- [ ] Regular expression support for string matching
- [ ] Visual filter builder with preview
- [ ] Export filtered data to CSV
- [ ] Filter based on derived/calculated columns
- [ ] Date/time specific operators

## Testing

Run the test script to verify installation:

```bash
python test_filter.py
```

Expected output:
```
✓ DataFilterDialog imported successfully
✓ PlottingDialog imported successfully
✓ Test dataframe created
  Original rows: 5
✓ Filters applied successfully
  Filtered rows: 2 (expected: 2)
✅ All tests passed!
```

## Troubleshooting

### Filter not working
- Check that the column name is correct (case-sensitive)
- Verify the value type matches the column type
- Check the console/logs for error messages

### No data shown after filtering
- Filters may be too restrictive
- Click "Clear All" to reset filters
- Check filter values for typos

### Button not visible
- Ensure you're using the latest version of plot_dialog.py
- Check that the button is not hidden due to window size
- Verify imports are correct
