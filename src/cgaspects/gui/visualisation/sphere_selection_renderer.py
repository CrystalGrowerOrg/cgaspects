"""Renderer for the transparent sphere used during sphere-based point selection."""

import numpy as np
from OpenGL.GL import GL_FLOAT, GL_TRIANGLES
from PySide6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVertexArrayObject,
)
from PySide6.QtGui import QVector3D


class SphereSelectionRenderer:
    """Renders a transparent selection sphere to visualise sphere-based point picking.

    The sphere is drawn with a Fresnel rim effect — the silhouette is more
    opaque than the interior — so the user can clearly see the selection
    boundary without it occluding the point cloud too heavily.
    """

    vertex_shader_source = """
    #version 330 core
    layout(location = 0) in vec3 vertexPosition;

    uniform mat4 u_modelViewProjectionMat;
    uniform mat4 u_modelViewMat;
    uniform vec3 u_sphereCenter;
    uniform float u_sphereRadius;

    out vec3 v_normal_vs;
    out vec3 v_position_vs;

    void main() {
        vec3 worldPos = vertexPosition * u_sphereRadius + u_sphereCenter;
        // Transform normal and position into view space for rim calculation
        v_normal_vs   = mat3(u_modelViewMat) * vertexPosition;
        v_position_vs = (u_modelViewMat * vec4(worldPos, 1.0)).xyz;
        gl_Position   = u_modelViewProjectionMat * vec4(worldPos, 1.0);
    }
    """

    fragment_shader_source = """
    #version 330 core
    in vec3 v_normal_vs;
    in vec3 v_position_vs;

    out vec4 fragColor;

    void main() {
        vec3 norm    = normalize(v_normal_vs);
        vec3 viewDir = normalize(-v_position_vs);

        // Fresnel-like rim: edges more opaque than the interior
        float rim   = 1.0 - max(dot(viewDir, norm), 0.0);
        rim         = pow(rim, 1.5);
        float alpha = 0.05 + rim * 0.45;

        // Cyan-blue selection colour
        vec3 color = vec3(0.1, 0.72, 1.0);
        fragColor  = vec4(color, alpha);
    }
    """

    def __init__(self):
        self.center = np.zeros(3, dtype=np.float32)
        self.radius = 0.0
        self.num_vertices = 0

        self.program = QOpenGLShaderProgram()
        self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, self.vertex_shader_source)
        self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, self.fragment_shader_source)
        self.program.link()

        self.vao = QOpenGLVertexArrayObject()
        self.vao.create()
        self.vao.bind()

        self.vertex_buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.vertex_buffer.create()
        self.vertex_buffer.bind()
        self.vertex_buffer.setUsagePattern(QOpenGLBuffer.StaticDraw)

        self._load_mesh()

        self.program.enableAttributeArray(0)
        self.program.setAttributeBuffer(0, GL_FLOAT, 0, 3, 3 * 4)

        self.vertex_buffer.release()
        self.vao.release()
        self.program.release()

    def _load_mesh(self):
        from trimesh.creation import icosphere

        mesh = icosphere(subdivisions=2)
        faces = np.array(mesh.faces, dtype=np.uint32).flatten()
        verts = np.array(mesh.vertices, dtype=np.float32)
        verts_flat = verts[faces, :].flatten()
        self.num_vertices = len(faces)
        self.vertex_buffer.allocate(verts_flat.tobytes(), verts_flat.nbytes)

    def set_sphere(self, center, radius):
        self.center = np.array(center, dtype=np.float32)
        self.radius = float(radius)

    def bind(self):
        self.program.bind()
        self.vao.bind()

    def release(self):
        self.vao.release()
        self.program.release()

    def setUniforms(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, float):
                self.program.setUniformValue1f(k, v)
            elif isinstance(v, int):
                self.program.setUniformValue1i(k, v)
            else:
                self.program.setUniformValue(k, v)

    def draw(self, gl):
        if self.radius <= 0:
            return
        self.program.setUniformValue("u_sphereCenter", QVector3D(*self.center))
        self.program.setUniformValue1f("u_sphereRadius", self.radius)
        gl.glDrawArrays(GL_TRIANGLES, 0, self.num_vertices)
