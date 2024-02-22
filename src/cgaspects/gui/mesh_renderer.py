import numpy as np
from OpenGL.GL import GL_FLOAT, GL_TRIANGLES, GL_UNSIGNED_INT
from PySide6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVertexArrayObject,
)


def project_to_plane(points, plane_normal):
    projected_points = points - np.outer(np.dot(points, plane_normal), plane_normal)

    a_vector = projected_points[1] - projected_points[0]
    b_vector = np.cross(plane_normal, a_vector)

    u = np.dot(projected_points, a_vector)
    v = np.dot(projected_points, b_vector)

    return np.column_stack((u, v))


def winding_order_ccw(points):
    "return the indices to reorder the provided 2D points into CCW order"
    centroid = np.mean(points, axis=0)
    directions = points - centroid
    directions /= np.linalg.norm(directions, axis=1)[:, np.newaxis]
    idxs = list(range(points.shape[0]))
    return sorted(idxs, key=lambda x: np.arctan2(directions[x, 1], directions[x, 0]))


def ordered_facets(points, faces):
    result = []
    for i, face in enumerate(faces):
        if len(face) == 0:
            result.append([])
            continue

        # not actually a normal, just the direction from the
        # origin to the center of the face
        normal = np.mean(points[face], axis=0)
        points_2d = project_to_plane(points[face], normal)
        ccw_order = winding_order_ccw(points_2d)
        result.append([face[x] for x in ccw_order])
    return result


def order_and_triangulate_polygons(points, faces):
    ordered = ordered_facets(points, faces)

    triangles = []
    facet_indices = []
    for i, facet in enumerate(ordered):
        N = len(facet)
        if N == 0:
            continue
        t = np.column_stack((np.repeat(facet[0], N - 2), facet[1 : N - 1], facet[2:N]))
        triangles.append(t)
        facet_indices += [i] * t.shape[0]

    return ordered, np.vstack(triangles), facet_indices


def compute_vertex_normals(vertices, faces):
    edge1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    edge2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]

    face_normals = np.cross(edge1, edge2)

    face_normals = face_normals / np.linalg.norm(face_normals, axis=1)[:, np.newaxis]

    vertex_normals = np.zeros(vertices.shape, dtype=np.float32)

    np.add.at(vertex_normals, faces[:, 0], face_normals)
    np.add.at(vertex_normals, faces[:, 1], face_normals)
    np.add.at(vertex_normals, faces[:, 2], face_normals)

    vertex_normals = (
        vertex_normals / np.linalg.norm(vertex_normals, axis=1)[:, np.newaxis]
    )

    return vertex_normals


class MeshRenderer:
    faces = None
    vertices = None
    mesh = None

    def __init__(self, gl):
        self.vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec3 normal;
        layout(location = 2) in vec3 color;

        out vec4 v_color;
        out vec3 v_normal;
        uniform mat4 u_viewMat;
        uniform mat4 u_modelViewProjectionMat;

        void main() {
          v_normal = normalize(mat3(u_viewMat) * normal);
          v_color = vec4(color, 1.0f);
          gl_Position = u_modelViewProjectionMat * vec4(position, 1.0);
        }
        """

        self.fragment_shader_source = """
        #version 330 core

        in vec4 v_color;
        in vec3 v_normal;

        out vec4 fragColor;

        // Hard-coded light properties
        const vec3 lightDir = normalize(vec3(0.2, 0.5, 1.0));
        const vec3 lightColor = vec3(1.0, 1.0, 1.0);

        void main() {
            vec3 norm = normalize(v_normal);
            
            // Lambertian reflectance
            float diff = 0.7 * max(dot(norm, lightDir), 0.0);
            diff = min(0.3f + diff, 1.0f);
            
            // Combine diffuse lighting with vertex color
            vec3 color = diff * lightColor * v_color.rgb;
            
            fragColor = vec4(color, v_color.a);
        }
        """

        self.points = None
        self.program = QOpenGLShaderProgram()
        self.program.addShaderFromSourceCode(
            QOpenGLShader.Vertex, self.vertex_shader_source
        )
        self.program.addShaderFromSourceCode(
            QOpenGLShader.Fragment, self.fragment_shader_source
        )
        self.program.link()

        self.vao = QOpenGLVertexArrayObject()
        self.vao.create()
        self.vao.bind()

        self.vertex_buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.vertex_buffer.create()
        self.vertex_buffer.bind()
        self.vertex_buffer.setUsagePattern(QOpenGLBuffer.StaticDraw)

        stride = 36

        offset = 0
        self.program.enableAttributeArray(0)
        self.program.setAttributeBuffer(0, GL_FLOAT, offset, 3, stride)

        offset = 12
        self.program.enableAttributeArray(1)
        self.program.setAttributeBuffer(1, GL_FLOAT, offset, 3, stride)

        offset = 24
        self.program.enableAttributeArray(2)
        self.program.setAttributeBuffer(2, GL_FLOAT, offset, 3, stride)

        self.vertex_buffer.release()
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

    def bind(self, gl):
        self.program.bind()
        self.vao.bind()

    def release(self):
        self.vao.release()
        self.program.release()

    def draw(self, gl):
        import ctypes

        ptr = ctypes.c_void_p(0)

        gl.glDrawArrays(
            GL_TRIANGLES,
            0,
            self.numberOfVertices(),
        )

    def numberOfFaces(self):
        if self.faces is None:
            return 0
        return self.faces.shape[0]

    def numberOfVertices(self):
        if self.vertices is None:
            return 0
        return self.vertices.shape[0] // 3

    def setMesh(self, mesh):
        self.mesh = mesh
        self._updateBuffers()

    def _updateBuffers(self):
        self.vertex_buffer.bind()
        _, self.faces, _ = order_and_triangulate_polygons(
            self.mesh.vertices, self.mesh.faces
        )
        normals = compute_vertex_normals(self.mesh.vertices, self.faces)
        verts_tmp = self.mesh.vertices[self.faces].reshape(-1, 3)
        self.vertices = np.empty((verts_tmp.shape[0], 9), dtype=np.float32)
        self.vertices[:, :3] = verts_tmp
        self.vertices[:, 3:6] = normals[self.faces].reshape(-1, 3)
        self.vertices[:, 6:9] = 0.5
        self.vertices = self.vertices.flatten()
        self.vertex_buffer.allocate(self.vertices.tobytes(), self.vertices.nbytes)
        self.vertex_buffer.release()
