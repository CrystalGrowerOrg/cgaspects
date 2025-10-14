import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict

import numpy as np
import trimesh

from chmpy.shape.sht import SHT  # type: ignore
from scipy.spatial import ConvexHull  # pylint: disable=no-name-in-module

from .sph import transform_shape
from ..fileio.xyz_file import CrystalCloud, ShapeMetrics

LOG = logging.getLogger("CA:ShapeAnalysis")


@dataclass
class ShapeAnalyser:
    """Dataclass for spherical harmonic analysis of crystal shapes with multi-frame support."""

    l_max: int = 10
    zingg_method: Literal["bounding_box", "svd"] = "svd"
    norm_method: Optional[Literal["orthonormal", "schmidt"]] = "orthonormal"
    norm_array: Optional[np.ndarray] = None
    norm_operation: Optional[Literal["multiply", "divide"]] = "multiply"

    # Computed attributes
    sht: Optional[SHT] = field(init=False, default=None)
    points: List[np.ndarray] = field(default_factory=list)
    coeffs: Optional[np.ndarray] = None
    ref_coeffs: Optional[np.ndarray] = None

    # Multi-frame support
    frame_coeffs: Dict[int, np.ndarray] = field(default_factory=dict)
    frame_metrics: Dict[int, ShapeMetrics] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize SHT after dataclass creation."""
        self.sht = SHT(self.l_max)

    def get_coeffs(self, xyz_vals: np.ndarray, method: str = "ConvexHull") -> np.ndarray:
        """Calculate spherical harmonic coefficients from coordinates."""
        if method == "ConvexHull":
            shape_hull = ConvexHull(CrystalCloud.normalise_verts(xyz_vals))
            coeffs = transform_shape(self.sht, shape_hull)
        elif method == "PointCloud":
            coeffs = transform_shape(self.sht, CrystalCloud.normalise_verts(xyz_vals))
        else:
            raise ValueError(f"Unknown method: {method}")

        LOG.debug("Coefficients calculated from [%s]: (%s)", method, coeffs.shape)
        return coeffs

    def analyse_crystal(
        self,
        crystal: CrystalCloud,
        method: str = "ConvexHull",
        frame_idx: Optional[int] = None,
        sph: bool = False,
    ) -> None:
        """Analyse a single frame or all frames of a crystal shape."""
        if frame_idx is not None:
            # Analyse specific frame
            frame = crystal.frames[frame_idx]
            coords = frame.coords
            self.frame_metrics[frame_idx] = self.shape_info(coords)
            if sph:
                self.coeffs = self.get_coeffs(coords, method)
                self.frame_coeffs[frame_idx] = self.coeffs
        else:
            # Analyse all frames
            for idx, frame in enumerate(crystal.frames):
                coords = frame.coords
                self.frame_metrics[idx] = self.shape_info(coords)
                if sph:
                    coeffs = self.get_coeffs(coords, method)
                    self.frame_coeffs[idx] = coeffs

            # Set coeffs to last frame for compatibility
            if 0 in self.frame_coeffs:
                self.coeffs = self.frame_coeffs[-1]

    def reference_shape(
        self, shapepath: Path, method: str = "ConvexHull", normalize: bool = True
    ) -> np.ndarray:
        """Set reference shape from file."""
        shapepath = Path(shapepath)
        if not shapepath.exists():
            raise FileNotFoundError(f"Reference shape file {shapepath} not found")

        if shapepath.suffix.lower() == ".xyz":
            temp_crystal = CrystalCloud.from_file(shapepath, normalise=normalize)
            xyz = temp_crystal.coords
        else:
            mesh = trimesh.load(shapepath)
            xyz = CrystalCloud.normalise_verts(mesh.vertices) if normalize else mesh.vertices

        self.ref_coeffs = self.get_coeffs(xyz, method)
        return self.ref_coeffs

    def compare_frame_to_reference(self, frame_idx: int, **kwargs) -> float:
        """Compare a specific frame to the reference shape."""
        if self.ref_coeffs is None:
            raise ValueError("No reference shape set. Call reference_shape() first.")
        if frame_idx not in self.frame_coeffs:
            raise ValueError(f"Frame {frame_idx} not analysed. Call analyse_crystal() first.")

        return self.compare_shape(self.ref_coeffs, self.frame_coeffs[frame_idx], **kwargs)

    def compare_all_frames_to_reference(self, **kwargs) -> Dict[int, float]:
        """Compare all analysed frames to the reference shape."""
        if self.ref_coeffs is None:
            raise ValueError("No reference shape set. Call reference_shape() first.")

        return {
            frame_idx: self.compare_shape(self.ref_coeffs, coeffs, **kwargs)
            for frame_idx, coeffs in self.frame_coeffs.items()
        }

    def get_frame_metrics(self, frame_idx: int) -> Optional[ShapeMetrics]:
        """Get metrics for a specific frame."""
        return self.frame_metrics.get(frame_idx)

    def get_all_frame_metrics(self) -> Dict[int, ShapeMetrics]:
        """Get metrics for all analysed frames."""
        return self.frame_metrics.copy()

    @staticmethod
    def get_shape_class(aspect1: float, aspect2: float) -> str:
        """Determine the crystal shape based on the aspect ratios."""
        threshold = 2 / 3
        aspects = (aspect1 > threshold, aspect2 > threshold)

        shapes = {
            (False, False): "Lath",
            (False, True): "Plate",
            (True, True): "Block",
            (True, False): "Needle",
        }
        return shapes.get(aspects, "unknown")

    @staticmethod
    def get_sa_vol_ratio(xyz: np.ndarray) -> np.ndarray:
        """Returns surface area, volume, and SA:Vol ratio of a crystal shape."""
        try:
            hull = ConvexHull(xyz)
            vol_hull = hull.volume
            sa_hull = hull.area
            sa_vol = sa_hull / vol_hull
            sa_vol_ratio_array = np.array([sa_hull, vol_hull, sa_vol])
        except ValueError as ve:
            LOG.error("Encountered: %s\nHull information will be set to -1.", ve)
            sa_vol_ratio_array = np.array([-1, -1, -1])

        return sa_vol_ratio_array

    def shape_info(
        self,
        xyz_vals: np.ndarray,
        get_sa_vol: bool = True,
    ) -> ShapeMetrics:
        """Calculate comprehensive shape information for crystal coordinates."""
        # Perform PCA via SVD
        _, s, vh = np.linalg.svd(xyz_vals, full_matrices=False)
        transformed_xyz = xyz_vals @ vh.T

        # Explained variance ratios
        var = s**2 / (len(xyz_vals) - 1)
        evr = var / var.sum()

        # Axis-aligned lengths (match PC1, PC2, PC3)
        mins_pc = np.min(transformed_xyz, axis=0)
        maxs_pc = np.max(transformed_xyz, axis=0)
        lengths_pc = maxs_pc - mins_pc
        x_pc, y_pc, z_pc = lengths_pc

        # Sorted lengths for Zingg ratios
        sorted_lengths = np.sort(lengths_pc)
        if self.zingg_method == "bounding_box":
            aspect1 = sorted_lengths[0] / sorted_lengths[1] if sorted_lengths[1] != 0 else 0
            aspect2 = sorted_lengths[1] / sorted_lengths[2] if sorted_lengths[2] != 0 else 0
        elif self.zingg_method == "svd":
            aspect1 = s[2] / s[1] if s[1] != 0 else 0
            aspect2 = s[1] / s[0] if s[0] != 0 else 0
        else:
            raise ValueError(
                f"Unrecognised Zingg Ratio Calculation Mode: {self.zingg_method}. "
                "Choose either 'bounding_box' (default) or 'svd' (pca single values)"
            )

        # Determine crystal shape
        shape = self.get_shape_class(aspect1, aspect2)

        sa_hull, vol_hull, sa_vol = None, None, None
        if get_sa_vol:
            sa_vol_vals = self.get_sa_vol_ratio(xyz_vals)
            sa_hull, vol_hull, sa_vol = sa_vol_vals[0], sa_vol_vals[1], sa_vol_vals[2]

        return ShapeMetrics(
            x=x_pc,
            y=y_pc,
            z=z_pc,
            pc1=evr[0],
            pc2=evr[1],
            pc3=evr[2],
            aspect1=aspect1,
            aspect2=aspect2,
            surface_area=sa_hull,
            volume=vol_hull,
            surface_area_to_volume_ratio=sa_vol,
            shape=shape,
        )
