# Aspect Ratio Analysis

Access via the **Calculate Aspect Ratio** button in the left panel (enabled when XYZ files are loaded).

Aspect ratio analysis quantifies the shape of each crystal frame using the Zingg classification scheme, and optionally computes the size along user-specified crystallographic directions (Crystallographic Direction Analysis, CDA).

---

## What It Computes

For every XYZ frame in the dataset:

| Output | Description |
|--------|-------------|
| S (short) | Shortest principal dimension (from PCA) |
| M (middle) | Middle principal dimension |
| L (long) | Longest principal dimension |
| S:M ratio | Short / Middle (primary aspect ratio) |
| M:L ratio | Middle / Long (secondary aspect ratio) |
| Shape | Zingg morphological class |
| Surface area | Convex hull surface area (Å²) |
| Volume | Convex hull volume (Å³) |
| SA:Vol | Surface area to volume ratio (Å⁻¹) |

See [Zingg Classification](../science/zingg-classification.md) and [Shape Metrics](../science/shape-metrics.md) for background.

---

## Analysis Options

When you click **Calculate Aspect Ratio**, a configuration dialog opens:

### Standard Shape Analysis

Check **Aspect Ratio, Surface Area, Volume...** (enabled by default) to compute the PCA-based shape metrics for every frame.

### Crystallographic Direction Analysis (CDA)

Check **Crystallographic Directions Analysis** to additionally measure the crystal extent along up to three crystallographic directions.

- Select directions from the dropdown menus (populated from the simulation's parameter file)
- Up to 3 directions can be analyzed simultaneously
- CDA results show how the crystal dimension along each direction evolves across frames

---

## Output Files

Results are saved to the `aspects_output/` folder inside the data directory:

| File | Contents |
|------|---------|
| `aspect_ratios.csv` | S, M, L, S:M, M:L, shape, SA, Vol, SA:Vol per frame |
| `cda_results.csv` | Extent along each selected direction per frame |
| `zingg_plot.png` | Zingg scatter diagram (S:M vs M:L) |

---

## Zingg Plot

The analysis automatically generates a Zingg diagram — a scatter plot with S:M on the Y-axis and M:L on the X-axis. The 2/3 threshold lines divide the plot into four quadrants corresponding to the four Zingg shape classes.

Points can be coloured by simulation variables (e.g., ΔG_cryst) using the plotting dialog after analysis.

---

## Workflow

1. Import XYZ files from a simulation folder
2. Click **Calculate Aspect Ratio**
3. Optionally check **CDA** and select directions
4. Click **OK** — analysis runs in the background
5. When complete, results open in the [Plotting Dialog](../plotting.md)
6. CSV files are saved in `aspects_output/`

---

## Notes

- At least one valid XYZ frame is required (frames with zero points are skipped)
- CDA requires the simulation parameters file to be present in the folder (it lists the available directions)
- For very large datasets (hundreds of XYZ files), analysis may take several minutes
