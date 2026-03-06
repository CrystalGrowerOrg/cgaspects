# Shape Metrics

This page explains the quantitative shape metrics computed by CGAspects.

---

## Principal Component Analysis (PCA)

CGAspects uses **Principal Component Analysis (PCA)** to find the three principal dimensions of a crystal point cloud. PCA is performed via Singular Value Decomposition (SVD) of the centered coordinate matrix.

The three principal components define orthogonal directions:
- **PC1** (first principal component) — the direction of greatest extent (long axis, L)
- **PC2** — the direction of second greatest extent (middle axis, M)
- **PC3** — the direction of smallest extent (short axis, S)

The magnitudes of PC1, PC2, PC3 give the dimensions L, M, S used for Zingg classification.

### Why PCA Instead of Bounding Box?

A simple axis-aligned bounding box would give the X, Y, Z extents, which depend on crystal orientation. PCA is orientation-independent: it finds the intrinsic dimensions of the crystal regardless of how it is oriented in space.

---

## Convex Hull

The **convex hull** is the smallest convex shape that contains all points in the crystal. CGAspects uses the convex hull (via `scipy.spatial.ConvexHull`) to compute:

### Surface Area

The sum of the areas of all triangular faces on the convex hull, in Å².

### Volume

The volume enclosed by the convex hull surface, in Å³.

### SA:Vol Ratio

The surface area to volume ratio, in Å⁻¹:

```
SA:Vol = Surface Area / Volume
```

This ratio is important in dissolution: a higher SA:Vol means more surface exposed per unit of crystal mass, leading to faster dissolution. Needles and plates have higher SA:Vol ratios than blocks of the same volume.

---

## Aspect Ratios

From the PCA dimensions:

| Ratio | Formula | Name |
|-------|---------|------|
| Primary (S:M) | S / M | Short / Middle |
| Secondary (M:L) | M / L | Middle / Long |

Both ratios range from 0 to 1. See [Zingg Classification](zingg-classification.md) for how these ratios map to crystal shape classes.

---

## Crystal Extent Along Directions

When **Crystallographic Direction Analysis (CDA)** is enabled in [Aspect Ratio Analysis](../analysis/aspect-ratios.md), CGAspects additionally computes the extent of the crystal along each selected crystallographic direction.

For a direction vector **d** (unit vector), the extent is:

```
extent = max(points · d) - min(points · d)
```

where the dot product projects each point onto the direction. This gives the crystal's "width" in that specific crystallographic direction, regardless of orientation.

---

## Shape Classification

CGAspects assigns a morphological class to each crystal frame using the Zingg threshold (2/3):

| Class | S:M | M:L | Description |
|-------|-----|-----|-------------|
| Block | ≥ 2/3 | ≥ 2/3 | Equant, roughly cubic |
| Plate | ≥ 2/3 | < 2/3 | Disk-like, one thin dimension |
| Needle | < 2/3 | ≥ 2/3 | Rod-like, one elongated dimension |
| Lath | < 2/3 | < 2/3 | Elongated and flat |

---

## Summary of Computed Metrics

| Metric | Method | Unit |
|--------|--------|------|
| S, M, L dimensions | PCA / SVD | Å |
| S:M aspect ratio | PCA | dimensionless |
| M:L aspect ratio | PCA | dimensionless |
| Surface area | Convex hull | Å² |
| Volume | Convex hull | Å³ |
| SA:Vol ratio | Convex hull | Å⁻¹ |
| Shape class | Zingg threshold | — |
| Direction extent | Dot product projection | Å |
