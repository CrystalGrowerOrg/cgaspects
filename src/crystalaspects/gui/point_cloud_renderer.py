import numpy as np
from OpenGL.GL import GL_FLOAT, GL_POINTS, GL_PROGRAM_POINT_SIZE
from PySide6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShaderProgram,
    QOpenGLShader,
    QOpenGLVertexArrayObject,
)


class SimplePointRenderer:
    point_size = 200.0

    def __init__(self):
        self.vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec3 color;

        out vec4 v_color;

        uniform mat4 u_modelViewProjectionMat;
        uniform float u_pointSize;

        float pseudoRandom(float seed) {
            return fract(sin(seed) * 43758.5453123);
        }


        void main() {
            gl_Position = u_modelViewProjectionMat * vec4(position, 1.0);
            gl_PointSize = u_pointSize;
            v_color = vec4(color, 1.0);
        }
        """

        self.fragment_shader_source = """
        #version 330 core

        in vec4 v_color;
        out vec4 fragColor;

        void main() {
            fragColor = v_color;
            vec2 center = gl_PointCoord - 0.5f;
            if (dot(center, center) > 0.25f)
            {
                    discard;
            }

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

        self.vao = QOpenGLVertexArrayObject()
        self.vao.create()
        self.vao.bind()

        self.program.bind()
        self.program.enableAttributeArray(0)
        self.program.setAttributeBuffer(0, GL_FLOAT, 0, 3, 6 * 4)
        self.program.enableAttributeArray(1)
        self.program.setAttributeBuffer(1, GL_FLOAT, 3 * 4, 3, 6 * 4)

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

    def release(self):
        self.vao.release()
        self.program.release()

    def draw(self, gl):
        n = self.numberOfPoints()
        gl.glEnable(GL_PROGRAM_POINT_SIZE)
        gl.glDrawArrays(GL_POINTS, 0, n)

    def numberOfPoints(self):
        if self.points is None:
            return 0
        return self.points.size // 6

    def setPoints(self, points):
        self.points = np.array(points, dtype=np.float32).flatten()
        self._updateBuffers()

    def _updateBuffers(self):
        self.vertex_buffer.bind()
        self.vertex_buffer.allocate(self.points.tobytes(), self.points.nbytes)
        self.vertex_buffer.release()
