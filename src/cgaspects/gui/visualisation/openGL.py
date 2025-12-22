import logging
from pathlib import Path

import numpy as np
from matplotlib import cm
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST
from PySide6 import QtCore
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtOpenGL import QOpenGLDebugLogger, QOpenGLFramebufferObject
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from ...fileio.xyz_file import CrystalCloud
from .axes_renderer import AxesRenderer
from .camera import Camera
from .point_cloud_renderer import SimplePointRenderer
from .sphere_renderer import SphereRenderer
from .mesh_renderer import MeshRenderer
from .line_renderer import LineRenderer
from ..widgets.overlay_widget import TransparentOverlay
import trimesh
from scipy.spatial import ConvexHull


logger = logging.getLogger("CA:OpenGL")


class VisualisationWidget(QOpenGLWidget):
    style = "Spheres"
    show_mesh_edges = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rightMouseButtonPressed = False
        self.lastMousePosition = QtCore.QPoint()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.camera = Camera()
        self.restrict_axis = None
        self.geom = self.geometry()
        self.centre = self.geom.center()
        print(self.geom)
        print(self.geom.getRect())

        self.xyz_path_list = []
        self.sim_num = 0
        self.point_cloud_renderer = None
        self.sphere_renderer = None
        self.mesh_renderer = None
        self.axes_renderer = None

        self.xyz = None
        # self.object = 0

        self.colormap = "Viridis"
        self.color_by = "Layer"
        self.single_color = QColor(128, 128, 128)  # Default grey color

        self.viewInitialized = False
        self.point_size = 6.0
        self.point_type = "Point"
        self.backgroundColor = QColor(Qt.white)

        self.overlay = TransparentOverlay(self)
        self.overlay.setGeometry(self.geometry())
        self.overlay.showIcon()

        self.lattice_parameters = None

        self.availableColormaps = {
            "Viridis": cm.viridis,
            "Cividis": cm.cividis,
            "Plasma": cm.plasma,
            "Inferno": cm.inferno,
            "Magma": cm.magma,
            "Twilight": cm.twilight,
            "HSV": cm.hsv,
        }

        self.columnLabelToIndex = {
            "Atom/Molecule Type": 0,
            "Atom/Molecule Number": 1,
            "Layer": 2,
            "Single Colour": -1,
            "Site Number": 6,
            "Particle Energy": 7,
        }

        self.availableColumns = {}

        # Site highlighting - support multiple groups
        self.highlight_groups = []  # List of (site_set, color) tuples
        self.background_color_override = None  # Background color for non-highlighted sites

    def pass_XYZ(self, xyz):
        self.xyz = xyz
        logger.debug("XYZ coordinates passed on OpenGL widget")

    def pass_XYZ_list(self, xyz_path_list):
        self.xyz_path_list = xyz_path_list
        logger.info("XYZ file paths (list) passed to OpenGL widget")

    def get_XYZ_from_list(self, value):
        if self.sim_num != value:
            self.sim_num = value
            self.crystal = CrystalCloud.from_file(self.xyz_path_list[value])
            self.xyz = self.crystal.get_raw_frame_coords(0)
            self.initGeometry()
            self.update()

    def set_fractional_axes(self, crystallography):
        """Set the axes to fractional coordinates using the provided crystallography object."""
        if self.axes_renderer is not None:
            self.axes_renderer.set_crystallography(crystallography)
            self.update()
            logger.info("Axes set to fractional coordinates")

    def set_cartesian_axes(self):
        """Reset the axes to Cartesian coordinates."""
        if self.axes_renderer is not None:
            self.axes_renderer.set_cartesian()
            self.update()
            logger.info("Axes reset to Cartesian coordinates")

    def highlight_sites(self, highlight_groups, background_color=None):
        """Highlight multiple groups of sites with different colors.

        Args:
            highlight_groups: List of (site_numbers, color) tuples
                             Each color is RGB array or list [r, g, b] in range [0, 1]
                             site_numbers can be a single number, list, or set
            background_color: RGB color for non-highlighted sites [r, g, b] in range [0, 1]
                            If None, uses original coloring
        """
        self.highlight_groups = []
        for site_numbers, color in highlight_groups:
            if color is None:
                color = [1.0, 0.0, 0.0]  # Red by default

            # Handle single number, list, or set
            if isinstance(site_numbers, (int, np.integer)):
                site_set = {site_numbers}
            elif isinstance(site_numbers, set):
                site_set = site_numbers
            else:
                site_set = set(site_numbers)

            color_array = np.array(color, dtype=np.float32)
            self.highlight_groups.append((site_set, color_array))

        if background_color is not None:
            self.background_color_override = np.array(background_color, dtype=np.float32)
        else:
            self.background_color_override = None

        total_sites = sum(len(sites) for sites, _ in self.highlight_groups)
        logger.info(
            f"Highlighting {len(self.highlight_groups)} groups with {total_sites} total sites"
        )

        # Re-initialize geometry to apply the highlighting
        self.initGeometry()
        self.update()

    def clear_highlighted_sites(self):
        """Clear all highlighted sites."""
        self.highlight_groups.clear()
        self.background_color_override = None
        logger.info("Cleared all highlighted sites")
        self.initGeometry()
        self.update()

    def saveRenderDialog(self):
        # First ask user what type of export they want
        export_options = ["2D Image (PNG)", "3D Mesh"]

        # Only allow 3D mesh export if not in Points mode
        if self.style == "Points":
            export_options = ["2D Image (PNG)"]

        export_type, ok = QInputDialog.getItem(
            self, "Select Export Type", "Export as:", export_options, 0, False
        )

        if not ok:
            return

        if export_type == "2D Image (PNG)":
            # Original image export workflow
            options = ["1x", "2x", "4x"]
            resolution, ok = QInputDialog.getItem(
                self, "Select Resolution", "Resolution:", options, 0, False
            )

            if ok:
                file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Images (*.png)")
                if file_name:
                    self.saveRender(file_name, resolution)

                    # Confirmation dialog
                    msgBox = QMessageBox(self)
                    msgBox.setWindowTitle("Render Saved")
                    msgBox.setText(f"Image saved to:\n{file_name}")
                    msgBox.setStandardButtons(QMessageBox.Open | QMessageBox.Cancel)
                    msgBox.setDefaultButton(QMessageBox.Open)

                    open_folder_button = msgBox.addButton("Open Folder", QMessageBox.ActionRole)

                    result = msgBox.exec_()

                    if result == QMessageBox.Open:
                        QDesktopServices.openUrl(QUrl.fromLocalFile(file_name))
                    elif msgBox.clickedButton() == open_folder_button:
                        QDesktopServices.openUrl(QUrl.fromLocalFile(Path(file_name).parent))

        elif export_type == "3D Mesh":
            # 3D mesh export workflow
            self.saveMeshDialog()

    def renderToImage(self, scale):
        self.makeCurrent()
        w = self.width() * scale
        h = self.height() * scale
        gl = self.context().functions()
        gl.glViewport(0, 0, w, h)
        fbo = QOpenGLFramebufferObject(w, h, QOpenGLFramebufferObject.CombinedDepthStencil)

        fbo.bind()
        gl.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw(gl)
        fbo.release()
        result = fbo.toImage()
        self.doneCurrent()
        return result

    def saveRender(self, file_name, resolution):
        image = self.renderToImage(float(resolution[0]))
        image.save(file_name)

    def saveMeshDialog(self):
        # Ask user for mesh file format
        mesh_formats = [".obj", ".stl", ".ply", ".glb", ".off"]
        file_format, ok = QInputDialog.getItem(
            self, "Select Mesh Format", "Format:", mesh_formats, 0, False
        )

        if not ok:
            return

        # Ask user for mesh resolution (sphere subdivision level)
        resolution_options = {
            "Low (Fast)": 1,
            "Medium (Balanced)": 2,
            "High (Detailed)": 3,
            "Ultra (Slow)": 4,
        }
        resolution_choice, ok = QInputDialog.getItem(
            self,
            "Select Mesh Resolution",
            "Resolution (sphere detail):",
            list(resolution_options.keys()),
            1,  # Default to "Medium"
            False,
        )

        if not ok:
            return

        subdivision_level = resolution_options[resolution_choice]

        # Get file name from user
        filter_str = f"3D Mesh (*{file_format})"
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Mesh", "", filter_str)

        if file_name:
            # Ensure file has correct extension
            if not file_name.endswith(file_format):
                file_name += file_format

            try:
                self.saveMesh(file_name, subdivision_level=subdivision_level)

                # Confirmation dialog
                msgBox = QMessageBox(self)
                msgBox.setWindowTitle("Mesh Saved")
                msgBox.setText(f"3D mesh saved to:\n{file_name}")
                msgBox.setStandardButtons(QMessageBox.Open | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Open)

                open_folder_button = msgBox.addButton("Open Folder", QMessageBox.ActionRole)

                result = msgBox.exec_()

                if result == QMessageBox.Open:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_name))
                elif msgBox.clickedButton() == open_folder_button:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(Path(file_name).parent))

            except Exception as e:
                logger.error("Failed to save mesh: %s", e)
                msgBox = QMessageBox(self)
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setWindowTitle("Export Failed")
                msgBox.setText(f"Failed to export mesh:\n{str(e)}")
                msgBox.exec_()

    def saveMesh(self, file_name, subdivision_level=2):
        """Export the current visualization as a 3D mesh file

        Args:
            file_name: Path to save the mesh file
            subdivision_level: Level of sphere subdivision detail (1-4, default 2)
        """
        mesh = None

        if self.style == "Spheres":
            # Generate mesh from sphere instances with colors
            mesh = self._generateSphereMesh(subdivision_level=subdivision_level)
        elif self.style == "Convex Hull":
            # Use the existing convex hull mesh (without colors)
            mesh = self.mesh_renderer.mesh

        if mesh is None:
            raise ValueError(f"Cannot export mesh in '{self.style}' mode")

        # Export using trimesh
        mesh.export(file_name)
        logger.info("Mesh exported to %s with subdivision level %d", file_name, subdivision_level)

    def _generateSphereMesh(self, subdivision_level=2):
        """Generate a combined mesh from all sphere instances with colors

        Args:
            subdivision_level: Level of icosphere subdivision (1-4)
                1 = 42 vertices (low detail, fast)
                2 = 162 vertices (medium detail)
                3 = 642 vertices (high detail)
                4 = 2562 vertices (ultra detail, slow)
        """
        if self.sphere_renderer.numberOfInstances() <= 0:
            raise ValueError("No spheres to export")

        # Get the point cloud data (positions and colors)
        varray = self.updatePointCloudVertices()
        if varray is None or len(varray) == 0:
            raise ValueError("No point cloud data available")

        # Create base sphere mesh
        from trimesh.creation import icosphere

        base_sphere = icosphere(subdivisions=subdivision_level, radius=1.0)

        # Scale the sphere by point size (matching the shader: u_pointSize * 0.2)
        scale_factor = self.point_size * 0.2

        all_vertices = []
        all_faces = []
        all_vertex_colors = []
        vertex_offset = 0

        # For each point, create a transformed sphere with its color
        for point_data in varray:
            position = point_data[:3]
            color = point_data[3:6]

            # Transform sphere vertices to this position
            transformed_vertices = base_sphere.vertices * scale_factor + position

            # Create color array for all vertices of this sphere (same color for all vertices)
            num_vertices = len(base_sphere.vertices)
            vertex_colors = np.tile(color, (num_vertices, 1))

            all_vertices.append(transformed_vertices)
            all_faces.append(base_sphere.faces + vertex_offset)
            all_vertex_colors.append(vertex_colors)
            vertex_offset += num_vertices

        # Combine all meshes
        combined_vertices = np.vstack(all_vertices)
        combined_faces = np.vstack(all_faces)
        combined_colors = np.vstack(all_vertex_colors)

        # Convert colors from [0,1] float to [0,255] uint8 for better compatibility
        combined_colors_uint8 = (combined_colors * 255).astype(np.uint8)

        mesh = trimesh.Trimesh(
            vertices=combined_vertices, faces=combined_faces, vertex_colors=combined_colors_uint8
        )
        return mesh

    def setBackgroundColor(self, color):
        self.backgroundColor = QColor(color)
        self.makeCurrent()
        gl = self.context().functions()
        gl.glClearColor(color.redF(), color.greenF(), color.blueF(), 1)
        self.doneCurrent()

    def updateSettings(self, **kwargs):
        if not kwargs:
            return

        def present_and_changed(key, prev_val):
            return (key in kwargs) and (prev_val != kwargs[key])

        needs_reinit = False
        if present_and_changed("Color Map", self.colormap):
            self.colormap = kwargs["Color Map"]
            needs_reinit = True

        if present_and_changed("Style", self.style):
            self.style = kwargs["Style"]
            needs_reinit = True

        if present_and_changed("Show Mesh Edges", self.show_mesh_edges):
            self.show_mesh_edges = kwargs["Show Mesh Edges"]
            needs_reinit = True

        if present_and_changed("Background Color", self.backgroundColor):
            color = kwargs["Background Color"]
            self.setBackgroundColor(color)

        if present_and_changed("Color By", self.color_by):
            self.color_by = kwargs.get("Color By", self.color_by)
            needs_reinit = True

        if present_and_changed("Single Color", self.single_color):
            self.single_color = kwargs.get("Single Color", self.single_color)
            needs_reinit = True

        if present_and_changed("Point Size", self.point_size):
            self.point_size = float(kwargs["Point Size"])

        if "Axes Thickness" in kwargs:
            if self.axes_renderer is not None:
                self.axes_renderer.set_axes_thickness(float(kwargs["Axes Thickness"]))

        if needs_reinit:
            self.initGeometry()

        self.update()

    def resizeGL(self, width, height):
        super().resizeGL(width, height)
        self.aspect_ratio = width / float(height)
        self.screen_size = width, height

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(self.geometry())

    def wheelEvent(self, event):
        degrees = event.angleDelta() / 8

        steps = degrees.y() / 15

        self.camera.zoom(steps)
        self.update()

    def mousePressEvent(self, event):
        self.lastMousePosition = event.pos()
        if event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonPressed = True

    def keyPressEvent(self, event):
        dx, dy = 0, 0
        self.restrict_axis = None
        modifiers = event.modifiers()

        if event.key() == Qt.Key_W:
            dy -= 10
        if event.key() == Qt.Key_S:
            dy += 10

        if event.key() == Qt.Key_A:
            dx -= 10
        if event.key() == Qt.Key_D:
            dx += 10

        if event.key() == Qt.Key_C:
            self.camera.storeOrientation()

        if event.key() == Qt.Key_R:
            self.camera.resetOrientation()

        # Check for Shift + X, Y, or Z
        if modifiers & Qt.ShiftModifier:
            if event.key() == Qt.Key_X:
                self.restrict_axis = "shift_x"
            elif event.key() == Qt.Key_Y:
                self.restrict_axis = "shift_y"
            elif event.key() == Qt.Key_Z:
                self.restrict_axis = "shift_z"
        else:
            # Regular X, Y, Z without Shift
            if event.key() == Qt.Key_X:
                self.restrict_axis = "x"
            elif event.key() == Qt.Key_Y:
                self.restrict_axis = "y"
            elif event.key() == Qt.Key_Z:
                self.restrict_axis = "z"
        super().keyPressEvent(event)

        self.camera.orbit(
            dx,
            dy,
        )
        self.update()

    def keyReleaseEvent(self, event):
        if event.key() in (Qt.Key_X, Qt.Key_Y, Qt.Key_Z):
            self.restrict_axis = None
        super().keyReleaseEvent(event)

    def mouseMoveEvent(self, event):
        dx = event.pos().x() - self.lastMousePosition.x()
        dy = event.pos().y() - self.lastMousePosition.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            if self.restrict_axis in {"x", "y", "z"}:
                self.rotatePointCloud(dx, self.restrict_axis)
            else:
                self.camera.orbit(
                    dx,
                    dy,
                    restrict_axis=self.restrict_axis,
                    event_pos=event.pos() - self.geometry().center(),
                )

        elif self.rightMouseButtonPressed:
            self.camera.pan(-dx, dy)  # Negate dx to get correct direction

        self.lastMousePosition = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonPressed = False

    def rotatePointCloud(self, dx, axis):
        if self.xyz is None:
            return

        angle = np.radians(dx * self.camera.rotationSpeed)
        cos_a, sin_a = np.cos(angle), np.sin(angle)

        # Define rotation matrices for X, Y, and Z axes
        if axis == "x":
            rotation_matrix = np.array(
                [[1, 0, 0], [0, cos_a, -sin_a], [0, sin_a, cos_a]], dtype=np.float32
            )
        elif axis == "y":
            rotation_matrix = np.array(
                [[cos_a, 0, sin_a], [0, 1, 0], [-sin_a, 0, cos_a]], dtype=np.float32
            )
        elif axis == "z":
            rotation_matrix = np.array(
                [[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]], dtype=np.float32
            )
        else:
            return

        # Apply rotation to the XYZ points
        points = self.xyz[:, 3:6]
        rotated_points = points @ rotation_matrix.T

        # Update the point cloud with rotated points
        self.xyz[:, 3:6] = rotated_points
        self.initGeometry()

    def initGeometry(self):
        if self.point_cloud_renderer is None:
            return

        varray = self.updatePointCloudVertices()
        self.point_cloud_renderer.setPoints(varray)
        self.sphere_renderer.setPoints(varray)

        if self.style == "Convex Hull":
            hull = ConvexHull(varray[:, :3])
            mesh = trimesh.Trimesh(vertices=varray[:, :3], faces=hull.simplices)
            # can pass vertex colors here, but I wouldn't
            self.mesh_renderer.setMesh(mesh)

            if self.show_mesh_edges:
                self.line_renderer.setLines(self.mesh_renderer.getLines())

        self.update()

    def updatePointCloudVertices(self):
        self.overlay.setVisible(False)
        logger.debug("Loading Vertices")
        logger.debug(".XYZ shape: %s", self.xyz.shape[0])
        layers = self.xyz[:, 2]
        max_layers = int(np.nanmax(layers[layers < 99]))

        # Loading the point cloud from file
        def vis_pc(xyz, color_axis):
            pcd_points = xyz[:, 3:6]
            pcd_colors = None

            if xyz.shape[1] <= 6 and color_axis >= 6:
                logger.warning(
                    "Old CrystalGrower version! %s option not available for colouring.",
                    self.color_by,
                )
                color_axis = 3

            if color_axis == 3:
                axis_vis = np.arange(0, xyz.shape[0], dtype=np.float32)
            else:
                axis_vis = xyz[:, color_axis]

            if color_axis == 2:
                min_val = 1
                max_val = max_layers
            elif color_axis == -1:
                # Single color mode - use custom color
                min_val = 0
                max_val = 0
                axis_vis = np.zeros_like(axis_vis)
                # Convert QColor to RGB values in [0, 1] range
                single_color_rgb = np.array([
                    self.single_color.redF(),
                    self.single_color.greenF(),
                    self.single_color.blueF()
                ], dtype=np.float32)
            else:
                min_val = np.nanmin(axis_vis)
                max_val = np.nanmax(axis_vis)

            # Avoid division by zero in case all values are the same
            range_val = max_val - min_val if max_val != min_val else 1

            normalized_axis_vis = (axis_vis - min_val) / range_val

            if color_axis == -1:
                # Use the custom single color for all points
                pcd_colors = np.tile(single_color_rgb, (xyz.shape[0], 1))
            else:
                pcd_colors = self.availableColormaps[self.colormap](normalized_axis_vis)[:, 0:3]

            return (pcd_points, pcd_colors)

        points, colors = vis_pc(self.xyz, self.columnLabelToIndex[self.color_by])

        if not self.viewInitialized:
            self.camera.fitToObject(points)
            self.viewInitialized = True

        points = np.asarray(points).astype("float32")
        colors = np.asarray(colors).astype("float32")

        # Apply site highlighting if any groups are defined
        if self.highlight_groups and self.xyz.shape[1] > 6:
            # Column 6 is Site Number (0-indexed)
            site_numbers = self.xyz[:, 6]

            # First, apply background color override to all sites if specified
            if self.background_color_override is not None:
                colors[:] = self.background_color_override

            # Then apply highlight colors for each group (later groups override earlier ones)
            for site_set, highlight_color in self.highlight_groups:
                # Create a mask for particles belonging to sites in this group
                mask = np.isin(site_numbers, list(site_set))
                colors[mask] = highlight_color

        try:
            attributes = np.concatenate((points, colors), axis=1)

            return attributes
        except ValueError as exc:
            logger.error(
                "%s\n XYZ %s POINTS %s COLORS %s TYPE %s",
                exc,
                self.xyz.shape,
                points.shape,
                colors.shape,
                self.color_by,
            )
            return

    def initializeGL(self):
        logger.debug("Initialized OpenGL, version info: %s", self.context().format().version())
        debug = False
        if debug:
            self.logger = QOpenGLDebugLogger(self.context())
            if self.logger.initialize():
                self.logger.messageLogged.connect(self.handleLoggedMessage)
            else:
                ext = self.context().hasExtension(QtCore.QByteArray("GL_KHR_debug"))
                logger.debug("Debug logger not initialized, have extension GL_KHR_debug: %s", ext)

        color = self.backgroundColor
        gl = self.context().extraFunctions()
        self.point_cloud_renderer = SimplePointRenderer()
        self.sphere_renderer = SphereRenderer(gl)
        self.mesh_renderer = MeshRenderer(gl)
        self.line_renderer = LineRenderer(gl)
        self.axes_renderer = AxesRenderer()
        gl.glEnable(GL_DEPTH_TEST)
        gl.glClearColor(color.redF(), color.greenF(), color.blueF(), 1)

    def handleLoggedMessage(self, message):
        logger.debug(
            "Source: %s, Type: %s, Message: %s",
            message.source(),
            message.type(),
            message.message(),
        )

    def _draw_points(self, gl, uniforms):
        if self.point_cloud_renderer.numberOfPoints() <= 0:
            return
        self.point_cloud_renderer.bind()
        self.point_cloud_renderer.setUniforms(**uniforms)

        self.point_cloud_renderer.draw(gl)
        self.point_cloud_renderer.release()

    def _draw_spheres(self, gl, uniforms):
        if self.sphere_renderer.numberOfInstances() <= 0:
            return
        self.sphere_renderer.bind(gl)
        self.sphere_renderer.setUniforms(**uniforms)

        self.sphere_renderer.draw(gl)
        self.sphere_renderer.release()

    def _draw_mesh(self, gl, uniforms):
        if self.mesh_renderer.numberOfVertices() <= 0:
            return
        self.mesh_renderer.bind(gl)
        self.mesh_renderer.setUniforms(**uniforms)

        self.mesh_renderer.draw(gl)
        self.mesh_renderer.release()

    def _draw_lines(self, gl, uniforms):
        if self.line_renderer.numberOfVertices() <= 0:
            return
        self.line_renderer.bind(gl)
        self.line_renderer.setUniforms(**uniforms)

        self.line_renderer.draw(gl)
        self.line_renderer.release()

    def draw(self, gl):
        from PySide6.QtGui import QMatrix4x4, QVector2D

        mvp = self.camera.modelViewProjectionMatrix(self.aspect_ratio)
        view = self.camera.viewMatrix()
        proj = self.camera.projectionMatrix(self.aspect_ratio)
        modelView = self.camera.modelViewMatrix()
        axes = QMatrix4x4()
        screen_size = QVector2D(*self.screen_size)

        uniforms = {
            "u_viewMat": view,
            "u_modelViewProjectionMat": mvp,
            "u_pointSize": self.point_size,
            "u_axesMat": axes,
            "u_screenSize": screen_size,
            "u_projectionMat": proj,
            "u_modelViewMat": modelView,
            "u_scale": self.camera.scale,
            "u_lineScale": 2.0,
        }

        if self.style == "Points":
            self._draw_points(gl, uniforms)
        elif self.style == "Spheres":
            self._draw_spheres(gl, uniforms)
        elif self.style == "Convex Hull":
            self._draw_mesh(gl, uniforms)
            if self.show_mesh_edges:
                self._draw_lines(gl, uniforms)

        self.axes_renderer.bind()
        self.axes_renderer.setUniforms(**uniforms)
        self.axes_renderer.draw(gl)
        self.axes_renderer.release()

    def paintGL(self):
        gl = self.context().extraFunctions()
        gl.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw(gl)
