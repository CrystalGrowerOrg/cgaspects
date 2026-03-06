# Site Analysis

Access via the **Calculate Site Analysis** button in the left panel (enabled when crystallization event files are present in the loaded folder).

Site analysis examines the properties of individual lattice sites and characterises when and how they crystallized during the simulation.

---

## Input Data

The analysis auto-detects these files in the loaded folder:

| File | Contents |
|------|---------|
| Crystallization event files | Which site crystallized at which time step |
| Population/occupation files | Site occupancy over time |
| Count files | Event counting per site |
| Structure file | Site coordinates, energies |
| Simulation parameters | Direction and variable metadata |

---

## What It Computes

For each lattice site:

| Property | Description |
|----------|-------------|
| Site number | Unique site identifier |
| File prefix | Simulation run identifier |
| Energy | Site interaction energy |
| Occupation | Fraction of simulation time occupied |
| Coordination | Number of neighbouring occupied sites at crystallization |
| Total events | Number of crystallization/dissolution events |
| Total population | Cumulative occupied time steps |
| Tile type | Crystallographic face/edge/corner classification |
| Interaction patterns | Frequency of each neighbour interaction type |

---

## Filtering

The analysis result can be filtered using the **Data Filter** dialog (accessible from the plotting toolbar).

### Data Filters Tab

Add conditions on site properties:

| Column | Type | Example |
|--------|------|---------|
| site_number | Numeric | `> 100` |
| energy | Numeric | `< -50.0` |
| occupation | Numeric | `>= 0.5` |
| coordination | Numeric | `== 6` |
| total_events | Numeric | `> 10` |
| tile_type | Categorical | `== "face"` |

Multiple conditions are combined with AND logic.

### Interaction Filters Tab

Filter sites by the frequency of specific neighbour interaction types. This is useful for finding sites that preferentially form particular crystallographic contacts.

Both tabs can be active simultaneously (all conditions combined with AND).

---

## Hierarchical Clustering

The site analysis results can be visualized with hierarchical clustering in the plotting dialog, grouping sites by similarity of their interaction patterns. This reveals structurally distinct site populations within the crystal.

---

## Output

Results are saved to `aspects_output/`:

| File | Contents |
|------|---------|
| `site_analysis.csv` | All computed site properties |
| `interaction_data.csv` | Interaction frequency per site |
| Site analysis plots | Generated in the plotting dialog |

---

## Workflow

1. Import a folder containing crystallization event files
2. Click **Calculate Site Analysis**
3. The analysis runs in the background with a progress bar
4. Results open automatically in the [Plotting Dialog](../plotting.md)
5. Use the Data Filter to focus on specific site populations
6. Export filtered data or plots from the plotting dialog

---

## Notes

- Sites with zero events are included in the output but typically have zero occupation
- Very large simulations may produce large site analysis files; the filter dialog helps narrow the focus
- Hierarchical clustering requires all interaction columns to be numeric and non-null
