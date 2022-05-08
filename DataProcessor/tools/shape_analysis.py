import os
import numpy as np
from pathlib import Path
import time
import trimesh
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
from chmpy.shape.convex_hull import transform_hull
from chmpy.shape.sht import SHT


class CrystalShape:
    
    def __init__(self, l_max=10):
        self.sht = SHT(l_max)

    def normalise_verts(self, verts):

        self.centered = verts - np.mean(verts, axis=0)
        norm = np.linalg.norm(self.centered, axis=1).max()
        self.centered /= norm

        return self.centered

    def read_XYZ(self, filepath):
        self.xyz = np.loadtxt(filepath, skiprows=2)[:, 3:]
        return self.xyz

    def get_coeffs(self, filepath):

        xyz = self.read_XYZ(filepath)
        self.hull = ConvexHull(self.normalise_verts(xyz))
        self.coeffs = transform_hull(self.sht, self.hull)

        print(self.hull)
        return self.coeffs

    def reference_shape(self, stlpath):

        mesh = trimesh.load(stlpath)
        norm_verts = self.normalise_verts(mesh.vertices)
        self.stl_hull = ConvexHull(norm_verts)

        return transform_hull(self.sht, self.stl_hull)

    def compare_shape(self, ref_coeffs, shape_coeffs):
        self.distance = np.linalg.norm(ref_coeffs - shape_coeffs)

        return self.distance

    def get_PCA(self, file, n=3):

        xyz = self.read_XYZ(filepath=file)

        pca = PCA(n_components=n)
        pca.fit(self.normalise_verts(xyz))
        # pca_vectors = pca.components_
        # pca_values = pca.explained_variance_ratio_
        pca_svalues = pca.singular_values_

        # print(pca_vectors)
        # print(pca_values)
        # print(pca_svalues)

        return pca_svalues

