import numpy as np
from OpenGL.GL import GL_FLOAT, GL_TRIANGLES, GL_UNSIGNED_INT
from PySide6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVertexArrayObject,
)


class SphereRenderer:
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
            vec4(u_pointSize*0.2, 0, 0, 0),
            vec4(0, u_pointSize*0.2, 0, 0),
            vec4(0, 0, u_pointSize*0.2, 0),
            vec4(position, 1.0));
          mat4 normalTransform = inverse(transpose(transform));
          vec4 posTransformed = transform * vec4(vertexPosition, 1);

          v_normal = normalize(mat3(normalTransform) * vertexPosition);
          v_position = posTransformed.xyz;
          v_color = vec4(color + 0.1f, 1.0f);
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

        // Hard-coded light properties
        const vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
        const vec3 lightColor = vec3(1.0, 1.0, 1.0);

        void main() {
            vec3 norm = normalize(v_normal);
            
            // Lambertian reflectance
            float diff = max(dot(norm, lightDir), 0.0);
            
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

        self.loadBaseMesh(gl)

        self.program.enableAttributeArray(0)
        self.program.setAttributeBuffer(0, GL_FLOAT, 0, 3, 3 * 4)
        self.vertex_buffer.release()

        self.instance_buffer = QOpenGLBuffer()
        self.instance_buffer.create()
        self.instance_buffer.bind()
        self.instance_buffer.setUsagePattern(QOpenGLBuffer.DynamicDraw)

        stride = 24

        offset = 0
        self.program.enableAttributeArray(1)
        self.program.setAttributeBuffer(1, GL_FLOAT, offset, 3, stride)
        gl.glVertexAttribDivisor(1, 1)

        offset = 12
        self.program.enableAttributeArray(2)
        self.program.setAttributeBuffer(2, GL_FLOAT, offset, 3, stride)
        gl.glVertexAttribDivisor(2, 1)

        self.instance_buffer.release()
        self.vertex_buffer.release()
        self.vao.release()
        self.program.release()

    def setUniforms(self, gl, **kwargs):
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

        gl.glDrawArraysInstanced(
            GL_TRIANGLES,
            0,
            self.numberOfVertices(),
            self.numberOfInstances(),
        )

    def numberOfInstances(self):
        if self.instances is None:
            return 0
        return self.instances.size // 6

    def numberOfFaces(self):
        if self.mesh is None:
            return 0
        return self.mesh.faces.size // 3

    def numberOfVertices(self):
        if self.mesh is None:
            return 0
        return self.vertices_flattened.size // 3

    def setPoints(self, points):
        self.instances = np.array(points, dtype=np.float32).flatten()
        self._updateBuffers()

    def _updateBuffers(self):
        self.instance_buffer.bind()
        self.instance_buffer.allocate(self.instances.tobytes(), self.instances.nbytes)
        self.instance_buffer.release()

    def loadBaseMesh(self, gl, **kwargs):
        from trimesh.creation import icosphere

        self.mesh = icosphere(subdivisions=1)
        self.vertices = np.array(self.mesh.vertices, dtype=np.float32)
        self.faces = np.array(self.mesh.faces, dtype=np.uint32).flatten()
        self.vertices_flattened = self.vertices[self.faces, :].flatten()
        self.vertex_buffer.allocate(
            self.vertices_flattened.tobytes(), self.vertices_flattened.nbytes
        )
