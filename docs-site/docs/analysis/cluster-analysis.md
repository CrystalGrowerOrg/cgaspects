# Cluster Analysis

!!! warning "Beta feature"
    Cluster Analysis is currently in beta. Results should be interpreted with care, and the interface may change in future releases.

Cluster Analysis groups particle coordinates from XYZ simulation files into spatial clusters, helping identify how different particle types are distributed and mixed throughout a crystal.

Access via **Calculate → Cluster Analysis** in the main menu.

---

## Algorithms

| Algorithm | Description |
|-----------|-------------|
| DBSCAN | Density-based clustering; groups points that are closely packed and marks outliers as noise. Good for clusters of similar density. |
| OPTICS | Similar to DBSCAN but handles clusters of varying density. Slower but more flexible. |

---

## Parameters

| Parameter | Description |
|-----------|-------------|
| Algorithm | DBSCAN or OPTICS |
| Neighbourhood radius (ε) | Maximum distance between two points for them to be considered neighbours |
| Minimum samples | Minimum number of points required to form a cluster core |
| Frame index | Which simulation frame to analyse (`-1` = last frame, `0` = first frame) |
| Standardise coordinates | Rescale coordinates to zero mean and unit variance before clustering |
| Downsample fraction | Fraction of points to use (e.g. `0.5` uses 50%); useful for large datasets |
| Ratios only | Skip clustering and only compute particle-type ratios |

---

## What It Computes

**Global statistics:**

| Metric | Description |
|--------|-------------|
| Number of clusters | Total clusters found |
| Average cluster size | Mean number of points per cluster |
| Max cluster size | Largest cluster found |
| Noise fraction | Fraction of points not assigned to any cluster |

**Per particle type:**

| Metric | Description |
|--------|-------------|
| Cluster count | Number of clusters containing this particle type |
| Average / max size | Size statistics for clusters of this type |
| Noise fraction | Fraction of this type's points classified as noise |

**Mixed-cluster metrics:**

| Metric | Description |
|--------|-------------|
| Mixed cluster fraction | Fraction of clusters containing more than one particle type |
| Average types per cluster | Mean number of distinct particle types per cluster |

**Particle-type ratios:** ratio of each particle type count to every other type.

---

## Output

Results are saved to `aspects_output/cluster_analysis.csv`.

---

## Notes

- Cancellation takes effect at the next checkpoint (typically the start of each iteration), so there may be a short delay before the task stops. Use **Tools → Active Threads** to cancel a running analysis.
- For large datasets, use the **Downsample fraction** parameter to reduce computation time.
- If coordinates span very different scales (e.g. x in Ångströms, z in nanometres), enable **Standardise coordinates** to avoid bias in distance calculations.
- **Ratios only** mode is fast and useful when you only need the relative proportions of each particle type without full clustering.
