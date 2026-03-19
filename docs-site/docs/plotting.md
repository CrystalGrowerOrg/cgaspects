# Plotting

Open the Plotting dialog with **File → Plotting Dialog**, or it opens automatically after a successful analysis.

The plotting dialog provides interactive data visualisation for all analysis outputs: aspect ratios, growth rates, site analysis, and any imported CSV data.

---

## Plot Types

| Type | Description |
|------|-------------|
| Scatter | X/Y scatter with optional colour variable |
| Line | Connected line plot |
| Histogram | Distribution of a single variable |
| Heatmap | 2D density or value map |
| Time series | Line plot with time on the X-axis |
| 3D Scatter | 3D scatter plot with an optional fourth variable mapped to colour |

---

## 3D Scatter / 4D Mode

When the data has three or more numeric columns, the **3D Scatter** plot type becomes available.

- **X / Y / Z axes** — select three data columns for the spatial dimensions
- **Colour by** — an optional fourth variable mapped to the colourmap, creating a "4D" view

| Control | Description |
|---------|-------------|
| Elevation slider | Rotate the view vertically |
| Azimuth slider | Rotate the view horizontally |
| Invert X / Y / Z | Flip individual axes |

If no colour variable is selected, points are coloured by the Z-axis values.

---

## Data Selection

Use the dropdown menus to select:
- **X axis** — column for the horizontal axis
- **Y axis** — column for the vertical axis
- **Colour by** — column mapped to the colourmap (for scatter plots)

The available columns depend on which analysis was performed.

---

## Colourmap

When using **Colour by**, a colourmap maps the chosen column's values to colours. The same colourmaps available in the 3D viewport are available here (Viridis, Plasma, Inferno, etc.).

---

## Multiple Permutations

For Aspect Ratio and CDA analyses, the plotting dialog can generate plots for all combinations of selected variables. This produces a series of plots that can be browsed or exported together.

---

## Hierarchical Clustering

In Site Analysis mode, the plotting dialog supports hierarchical clustering to group sites by the similarity of their interaction patterns. Clusters are shown as colour-coded groups in scatter plots.

---

## Trendlines

Add a trendline to any scatter or line plot:
- **Linear fit** — straight line through the data
- **Polynomial fit** — configurable degree polynomial

The trendline equation and R² value are shown in the plot legend.

---

## Data Filtering

Click the **Filter** button to open the [Data Filter dialog](analysis/site-analysis.md#filtering). Filters apply in real time and update the plot immediately.

The filter status bar shows how many records are shown vs. total.

---

## Labels & Title

Click **Labels** to open the label customization dialog:
- Custom **plot title**
- Custom **X axis label**
- Custom **Y axis label**
- Custom **colorbar label**
- Or click **Use Defaults** to restore automatic labels

---

## Smoothing (Growth Rate Mode)

When plotting growth rate data, a **Smoothing** button opens the smoothing/interpolation dialog. See [Growth Rate Analysis → Smoothing](analysis/growth-rates.md#smoothing-and-interpolation).

---

## Interactive Features

- **Zoom / Pan / Home** — standard matplotlib navigation toolbar
- **Click a point** — highlights the corresponding site in the 3D viewport (when in Site Analysis mode)
- **Hover tooltip** — shows data values for the point under the cursor

---

## Exporting Plots

Click **Save** on the navigation toolbar, or use the plot save dialog:
- **Format**: PNG, PDF, EPS, SVG
- **Resolution**: Configurable DPI (default 300 for publication quality)
- **Filename and location**: Choose where to save

Plots are also automatically saved to `aspects_output/CGPlots/` after each analysis.

---

## Importing CSV Data

You can plot any CSV file directly without running an analysis:
- **File → Import CSV for Plotting** — browse for a file
- **File → Import CSV from Clipboard** (`Ctrl+Shift+C`) — paste CSV text

The columns are automatically detected and populated in the X/Y/Colour dropdowns.
