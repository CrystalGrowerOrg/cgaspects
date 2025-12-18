import logging
from typing import Optional
import numpy as np
from dataclasses import dataclass

LOG = logging.getLogger("MD-CORD")


@dataclass
class Cell:
    a: float
    b: float
    c: float
    alpha: float
    beta: float
    gamma: float


class Crystallography:
    def __init__(self, cell: Cell = None) -> None:
        self.cell: Cell = cell

        self.a: float = cell
        self.b: float = cell
        self.c: float = cell
        self.alpha_rad: float = None
        self.beta_rad: float = None
        self.gamma_rad: float = None
        self.alpha_star_rad: float = None

        self.volume: float = None

        self.direct: np.ndarray = None
        self.inverse: np.ndarray = None

        if self.cell is not None:
            self.set_cryst(cell)

    def set_cryst(self, cell: list):
        self.cell = cell

        self.alpha_rad = np.deg2rad(self.cell.alpha)
        self.beta_rad = np.deg2rad(self.cell.beta)
        self.gamma_rad = np.deg2rad(self.cell.gamma)

        LOG.debug(
            "Cell Parameters Set to: \n    a: %s  b: %s  c: %s\n    α  %.2f  β  %.2f  γ  %.2f \n",
            self.cell.a,
            self.cell.b,
            self.cell.a,
            self.alpha_rad,
            self.beta_rad,
            self.gamma_rad,
        )

        self.alpha_star_rad = self.alpha_star(self.alpha_rad, self.beta_rad, self.gamma_rad)

        self.volume = self.get_volume(self.cell)
        self.set_tranformation_matrix()

    def __repr__(self) -> str:
        if self.cell:
            return (
                f"Crystallography( a: {self.cell.a}, b: {self.cell.b}, c: {self.cell.c}, "
                f"α: {self.alpha_rad:.2f} rad, β: {self.beta_rad:.2f} rad, γ: {self.gamma_rad:.2f} rad )"
            )
        else:
            return "Crystallography(None)"

    def __str__(self) -> str:
        if self.cell:
            return (
                f"Crystallography( a: {self.cell.a}, b: {self.cell.b}, c: {self.cell.c}, "
                f"α: {self.alpha_rad:.4f} rad, β: {self.beta_rad:.4f} rad, γ: {self.gamma_rad:.4f} rad )"
            )
        else:
            return "Crystallography(None)"

    @staticmethod
    def get_volume(box):
        """
        Compute volume(s) from unit cell parameters.

        Parameters:
        - box: np.ndarray of shape (6,) or (N, 6) or (6, N)
        Format: [a, b, c, alpha, beta, gamma] in degrees.

        Returns:
        - float or np.ndarray: Volume(s) of the unit cell(s).
        """
        box = np.array(box)

        if box.ndim == 1:
            a, b, c, alpha, beta, gamma = box
            alpha = np.radians(alpha)
            beta = np.radians(beta)
            gamma = np.radians(gamma)

        elif box.ndim == 2:
            if box.shape[1] != 6:
                if box.shape[0] == 6:
                    box = box.T
                else:
                    raise ValueError("Input box must have 6 parameters per unit cell.")
            a, b, c = box[:, 0], box[:, 1], box[:, 2]
            alpha = np.radians(box[:, 3])
            beta = np.radians(box[:, 4])
            gamma = np.radians(box[:, 5])
        else:
            raise ValueError(f"Input box must be 1D or 2D array. Not {box}")

        # Calculate the volume using lattice parameters
        volume = (
            a
            * b
            * c
            * np.sqrt(
                1
                - np.cos(alpha) ** 2
                - np.cos(beta) ** 2
                - np.cos(gamma) ** 2
                + 2 * (np.cos(beta) * np.cos(gamma) * np.cos(gamma))
            )
        )

        return np.abs(volume)

    @staticmethod
    def alpha_star(alpha, beta, gamma, unit="rad"):
        # Calculate cos(alpha_star)
        cos_alpha_star = (np.cos(beta) * np.cos(gamma) - np.cos(alpha)) / (
            np.sin(beta) * np.sin(gamma)
        )
        # Calculate alpha_star in radians
        alpha_star = np.arccos(cos_alpha_star)

        # Convert radians to degrees
        if unit == "deg":
            alpha_star = np.rad2deg(alpha_star)

        return alpha_star

    def set_tranformation_matrix(self):
        a, b, c = self.cell.a, self.cell.b, self.cell.c
        ca, cb, cg = np.cos([self.alpha_rad, self.beta_rad, self.gamma_rad])
        sg = np.sin(self.gamma_rad)
        self.direct = np.transpose(
            [
                [a, b * cg, c * cb],
                [0, b * sg, c * (ca - cb * cg) / sg],
                [0, 0, self.volume / (a * b * sg)],
            ]
        )
        r = [
            [1 / a, 0.0, 0.0],
            [-cg / (a * sg), 1 / (b * sg), 0],
            [
                b * c * (ca * cg - cb) / self.volume / sg,
                a * c * (cb * cg - ca) / self.volume / sg,
                a * b * sg / self.volume,
            ],
        ]
        self.inverse = np.array(r)

        LOG.debug("Setting Direct and Inverse Matrices")
        LOG.debug("Direct Matrix: \n%s \nInverse Matrix: \n%s", self.direct, self.inverse)

    def cart_to_frac(self, coords=None):
        # Convert the cartesian coordinates to fractional coordinates
        fractional_coords = np.dot(coords, self.inverse)

        return fractional_coords

    def frac_to_cart(self, coords: np.ndarray = None) -> np.ndarray:
        # Convert the fractional coordinates to cartesian coordinates
        cartesian_coords = np.dot(coords, self.direct)

        return cartesian_coords
