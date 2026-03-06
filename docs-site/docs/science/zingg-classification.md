# Zingg Classification

The Zingg classification is a scheme for categorizing crystal morphology based on two aspect ratios. It was introduced by T. Zingg (1935) and is widely used in crystallography, sedimentology, and pharmaceutical sciences.

---

## Dimensions

For a crystal, the three principal dimensions are determined by Principal Component Analysis (PCA) of the point cloud:

| Dimension | Symbol | Description |
|-----------|--------|-------------|
| Long | L | Largest principal component extent |
| Middle | M | Intermediate principal component extent |
| Short | S | Smallest principal component extent |

The dimensions satisfy S ≤ M ≤ L.

---

## Aspect Ratios

Two ratios are computed:

| Ratio | Formula | Range | Name in CGAspects |
|-------|---------|-------|----------------------|
| Primary | S / M | 0 to 1 | Primary Aspect Ratio |
| Secondary | M / L | 0 to 1 | Secondary Aspect Ratio |

A ratio of 1 means the two dimensions are equal (equidimensional in that pair). A ratio near 0 means the crystal is very elongated or flat in that pair of dimensions.

---

## Shape Classes

A threshold value of **2/3** divides each ratio into two ranges, giving four quadrants:

```
       M/L (Secondary Aspect Ratio)
   0        2/3        1
   ├─────────┼──────────┤
 1 │  Plate  │  Block   │
   │         │          │
2/3├─────────┼──────────┤
   │  Lath   │  Needle  │
 0 │         │          │
   └─────────┴──────────┘
        S/M (Primary Aspect Ratio)
```

Wait — the axes above should be read carefully. The standard Zingg plot convention places S/M on the Y-axis and M/L on the X-axis:

```
S/M (Y axis)   M/L (X axis)
  1  ┌───────────┬───────────┐
     │           │           │
     │   Plate   │   Block   │
 2/3 ├───────────┼───────────┤
     │           │           │
     │   Lath    │  Needle   │
  0  └───────────┴───────────┘
      0         2/3           1
```

| Class | S/M | M/L | Shape Description |
|-------|-----|-----|-------------------|
| **Plate** | ≥ 2/3 | < 2/3 | Disk-like; one short dimension, two similar longer dimensions |
| **Block** | ≥ 2/3 | ≥ 2/3 | Equant, roughly cubic; all three dimensions similar |
| **Lath** | < 2/3 | < 2/3 | Elongated and flat; one long, one medium, one short dimension |
| **Needle** | < 2/3 | ≥ 2/3 | Rod-like; one very long dimension, two similar short dimensions |

---

## Examples

| Crystal | S:M | M:L | Class |
|---------|-----|-----|-------|
| Cubic crystal | ≈1 | ≈1 | Block |
| Hexagonal plate | ≈0.9 | ≈0.5 | Plate |
| Acicular (needle-like) | ≈0.9 | ≈0.2 | Needle |
| Tabular lath | ≈0.3 | ≈0.3 | Lath |

---

## Use in CGAspects

The Crystal Info panel shows the shape class for the current frame. The [Aspect Ratio Analysis](../analysis/aspect-ratios.md) produces a Zingg scatter plot where each point is one simulation run (or time step), coloured by a simulation variable (e.g., ΔG_cryst).

By plotting many simulations on the same Zingg diagram, you can see how simulation conditions map to crystal morphology — for example, how supersaturation affects whether a crystal grows as a plate or a needle.

---

## Reference

Zingg, T. (1935). *Beitrag zur Schotteranalyse*. Schweizerische Mineralogische und Petrographische Mitteilungen, 15, 39–140.
