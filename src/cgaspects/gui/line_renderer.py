import numpy as np
from OpenGL.GL import GL_FLOAT, GL_LINES
from PySide6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVertexArrayObject,
)

from OpenGL.GL import glGetError, GL_NO_ERROR

def print_gl_errors(desc):
    print("Section: ", desc)
    err_code = glGetError()
    while err_code != GL_NO_ERROR:
        err_string = {
            GL_NO_ERROR: "No error",
            0x0500: "GL_INVALID_ENUM",
            0x0501: "GL_INVALID_VALUE",
            0x0502: "GL_INVALID_OPERATION",
            0x0503: "GL_STACK_OVERFLOW",
            0x0504: "GL_STACK_UNDERFLOW",
            0x0505: "GL_OUT_OF_MEMORY",
            0x0506: "GL_INVALID_FRAMEBUFFER_OPERATION",
            0x0507: "GL_CONTEXT_LOST",
            0x8031: "GL_TABLE_TOO_LARGE"
        }.get(err_code, "Unknown error")
        
        print(f"OpenGL Error: {err_code} - {err_string}")
        err_code = glGetError()


class LineRenderer:
    vertices = None
    default_color = (52/255, 183/255, 235/255)

    def __init__(self, gl):
        self.vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec3 color;
        layout(location = 2) in float lineWidth;

        out GS_IN {
            vec3 color;
            float lineWidth;
        } gs_in;

        void main() {
            gs_in.color = color;
            gs_in.lineWidth = lineWidth;
            // Position is not modified here, just passed through to the geometry shader
            gl_Position = vec4(position, 1.0);
        }
        """

        self.geometry_shader_source = """
        #version 330 core
        layout(lines) in;
        layout(triangle_strip, max_vertices = 4) out;

        uniform mat4 u_projectionMat;
        uniform mat4 u_modelViewMat;
        uniform vec2 u_screenSize;
        uniform float u_lineScale;

        in GS_IN {
            vec3 color;
            float lineWidth;
        } gs_in[];

        out vec4 f_color;

        void main() {
            vec4 startPos = u_modelViewMat * vec4(gl_in[0].gl_Position.xyz, 1.0);
            vec4 endPos = u_modelViewMat * vec4(gl_in[1].gl_Position.xyz, 1.0);

            vec4 clipStart = u_projectionMat * startPos;
            vec4 clipEnd = u_projectionMat * endPos;

            vec2 ndcStart = clipStart.xy / clipStart.w;
            vec2 ndcEnd = clipEnd.xy / clipEnd.w;

            vec2 dir = normalize(ndcEnd - ndcStart);

            vec2 perpDir = vec2(-dir.y, dir.x);

            // Calculate line width in NDC
            float ndcThickness = u_lineScale / u_screenSize.y * 2.0; // Thickness in NDC

            vec2 offset = perpDir * ndcThickness / 2.0;
            gl_Position = vec4((ndcStart + offset) * clipStart.w, clipStart.zw);
            f_color = vec4(gs_in[0].color, 1.0);
            EmitVertex();

            gl_Position = vec4((ndcStart - offset) * clipStart.w, clipStart.zw);
            f_color = vec4(gs_in[0].color, 1.0);
            EmitVertex();

            gl_Position = vec4((ndcEnd + offset) * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, 1.0);
            EmitVertex();

            gl_Position = vec4((ndcEnd - offset) * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, 1.0);
            EmitVertex();

            EndPrimitive();
        }
        """

        self.fragment_shader_source = """
        #version 330 core
        in vec4 f_color;
        out vec4 fragColor;

        void main() {
            fragColor = vec4(f_color.rgb, 1.0);
        }
        """

        self.program = QOpenGLShaderProgram()
        self.program.addShaderFromSourceCode(
            QOpenGLShader.Vertex, self.vertex_shader_source
        )
        self.program.addShaderFromSourceCode(
            QOpenGLShader.Geometry, self.geometry_shader_source
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
        self.vertex_buffer.setUsagePattern(QOpenGLBuffer.DynamicDraw)

        stride = 4 * 7
        # position A, B
        offset = 0
        self.program.enableAttributeArray(0)
        self.program.setAttributeBuffer(0, GL_FLOAT, offset, 3, stride)
        offset += 3 * 4
        self.program.enableAttributeArray(1)
        self.program.setAttributeBuffer(1, GL_FLOAT, offset, 3, stride)
        offset += 3 * 4
        self.program.enableAttributeArray(2)
        self.program.setAttributeBuffer(2, GL_FLOAT, offset, 1, stride)

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
            GL_LINES,
            0,
            self.numberOfVertices(),
        )

    def numberOfVertices(self):
        if self.vertices is None:
            return 0
        return self.vertices.shape[0] // 7

    def setLines(self, lines):
        self.lines = lines
        self._updateBuffers()

    def _updateBuffers(self, vertex_colors=None):
        self.vertex_buffer.bind()
        self.vertices = np.empty((self.lines.shape[0], 14), dtype=np.float32)
        self.vertices[:, :3] = self.lines[:, :3] * 1.001  # v0
        self.vertices[:, 3:6] = 0.3 # color 
        self.vertices[:, 6] = 10 # line width
        self.vertices[:, 7:10] = self.lines[:, 3:6] * 1.001  # v1
        self.vertices[:, 10:13] = 0.3 # color
        self.vertices[:, 13] = 10  # line width

        self.vertices = self.vertices.flatten()
        self.vertex_buffer.allocate(self.vertices.tobytes(), self.vertices.nbytes)
        self.vertex_buffer.release()
