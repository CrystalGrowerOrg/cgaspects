import numpy as np
from OpenGL.GL import GL_FLOAT, GL_TRIANGLES, GL_UNSIGNED_INT
from PySide6.QtOpenGL import (QOpenGLBuffer, QOpenGLShader,
                              QOpenGLShaderProgram, QOpenGLVertexArrayObject)


class SphereRenderer:
    Instance = np.dtype({"names": ["position", "color"], "formats": ["3f4", "3f4"]})
    faces = None
    vertices = None
    instances = None

    def __init__(self, gl):
        self.vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec3 vertexPosition;
        layout(location = 1) in vec3 position;
        layout(location = 2) in vec3 color;

        out vec4 v_color;
        out vec3 v_normal;
        out vec3 v_position;
        out vec3 v_spherePosition;
        uniform float u_pointSize;
        uniform mat4 u_modelViewProjectionMat;

        void main() {
          v_spherePosition = vertexPosition;

          // to enable ellipsoids later keep this here for now
          mat4 transform = mat4(
            vec4(u_pointSize, 0, 0, 0),
            vec4(0, u_pointSize, 0, 0),
            vec4(0, 0, u_pointSize, 0),
            vec4(position, 1));
          mat4 normalTransform = inverse(transpose(transform));
          vec4 posTransformed = transform * vec4(vertexPosition, 1);

          v_normal = normalize(mat3(normalTransform) * vertexPosition);
          v_position = posTransformed.xyz;
          v_color = vec4(abs(color), 1.0f);
          gl_Position = u_modelViewProjectionMat * vec4(v_position, 1.0);
        }
        """

        self.fragment_shader_source = """
        #version 330 core

        in vec4 v_color;
        in vec3 v_normal;
        in vec3 v_position;
        in vec3 v_spherePosition;
        out vec4 fragColor;

        void main() {
            fragColor = v_color;
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

        self.vertex_buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.vertex_buffer.create()
        self.vertex_buffer.bind()
        self.vertex_buffer.setUsagePattern(QOpenGLBuffer.StaticDraw)

        self.index_buffer = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        self.index_buffer.create()
        self.index_buffer.bind()

        self.loadBaseMesh()

        self.instance_buffer = QOpenGLBuffer()
        self.instance_buffer.bind()
        self.instance_buffer.setUsagePattern(QOpenGLBuffer.DynamicDraw)

        self.vertex_buffer.bind()
        self.vao = QOpenGLVertexArrayObject()
        self.vao.create()
        self.vao.bind()

        self.program.bind()
        self.program.enableAttributeArray(0)
        self.program.setAttributeBuffer(0, GL_FLOAT, 0, 3, 3 * 4)
        self.vertex_buffer.release()
        self.vao.release()

        self.instance_buffer.bind()
        self.vao.bind()
        self.program.enableAttributeArray(1)
        self.program.enableAttributeArray(2)
        self.program.enableAttributeArray(3)

        stride = self.Instance.itemsize

        offset = self.Instance.fields["position"][1]
        self.program.setAttributeBuffer(1, GL_FLOAT, offset, 3, stride)
        gl.glVertexAttribDivisor(1, 1)

        offset = self.Instance.fields["color"][1]
        self.program.setAttributeBuffer(2, GL_FLOAT, offset, 3, stride)
        gl.glVertexAttribDivisor(2, 1)

        self.instance_buffer.release()
        self.index_buffer.release()
        self.vao.release()
        self.vertex_buffer.release()
        self.program.release()

    def setUniforms(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, float):
                self.program.setUniformValue1f(k, v)
            elif isinstance(v, int):
                self.program.setUniformValue1i(k, v)
            else:
                self.program.setUniformValue(k, v)

    def bind(self):
        self.program.bind()
        self.vao.bind()
        self.index_buffer.bind()

    def release(self):
        self.index_buffer.release()
        self.vao.release()
        self.program.release()

    def draw(self, gl):
        import ctypes

        gl.glDrawElementsInstanced(
            GL_TRIANGLES,
            self.faces.size,
            GL_UNSIGNED_INT,
            ctypes.c_void_p(0),
            self.numberOfInstances(),
        )

    def numberOfInstances(self):
        if self.instances is None:
            return 0
        return self.instances.size

    def numberOfFaces(self):
        if self.mesh is None:
            return 0
        return self.mesh.faces.size // 3

    def numberOfVertices(self):
        if self.mesh is None:
            return 0
        return self.mesh.vertices.size // 3

    def setPoints(self, points):
        if points.ndim > 1:
            self.instances = np.empty(points.shape[0], dtype=self.Instance)
            self.instances["position"] = points[:, :3]
            self.instances["color"] = points[:, 3:6]
        else:
            self.instances = np.array(points, dtype=self.Instance)
        print("Set points")
        self._updateBuffers()

    def _updateBuffers(self):
        print(self.instances)
        self.instance_buffer.bind()
        self.instance_buffer.allocate(self.instances.tobytes(), self.instances.nbytes)
        self.instance_buffer.release()

    def loadBaseMesh(self, **kwargs):
        from trimesh.creation import icosphere

        mesh = icosphere(subdivisions=1)
        self.vertices = np.array(mesh.vertices, dtype=np.float32)
        self.faces = np.array(mesh.faces, dtype=np.uint32)
        print(self.vertices, self.faces)

        self.vertex_buffer.bind()
        self.index_buffer.bind()
        self.vertex_buffer.allocate(self.vertices.tobytes(), self.vertices.nbytes)
        self.index_buffer.allocate(self.faces.tobytes(), self.faces.nbytes)
