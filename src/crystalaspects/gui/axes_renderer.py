import numpy as np
from OpenGL.GL import GL_FLOAT, GL_LINES
from PySide6.QtOpenGL import (QOpenGLBuffer, QOpenGLShader,
                              QOpenGLShaderProgram, QOpenGLVertexArrayObject)


class AxesRenderer:
    point_size = 200.0

    def __init__(self):
        self.vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec3 color;

        out vec4 v_color;

        uniform mat4 u_viewMat;  // Uniform for the view matrix
        uniform vec2 u_screenSize; // Uniform for screen size

        void main() {
            vec3 rotatedPos = mat3(u_viewMat) * position * 0.1;

            vec2 screenPos = vec2(0.8, 0.8); // Bottom left corner
            rotatedPos.xy -= screenPos;

            gl_Position = vec4(rotatedPos, 1.0);
            v_color = vec4(color, 1.0);
        }

        """

        self.fragment_shader_source = """
        #version 330 core

        in vec4 v_color;
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
        self.points = np.array(
            (
                (0, 0, 0, 1.0, 0.0, 0.0),
                (1, 0, 0, 1.0, 0.0, 0.0),
                (0, 0, 0, 0.0, 1.0, 0.0),
                (0, 1, 0, 0.0, 1.0, 0.0),
                (0, 0, 0, 0.0, 0.0, 1.0),
                (0, 0, 1, 0.0, 0.0, 1.0),
            ),
            dtype=np.float32,
        ).flatten()

        self.vertex_buffer.allocate(self.points.tobytes(), self.points.nbytes)

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
        gl.glDrawArrays(GL_LINES, 0, n)

    def numberOfPoints(self):
        if self.points is None:
            return 0
        return self.points.size // 6
