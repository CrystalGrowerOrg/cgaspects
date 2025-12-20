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

        out GS_IN {
            vec3 color;
        } gs_in;

        void main() {
            gs_in.color = color;
            gl_Position = vec4(position, 1.0);
        }

        """

        self.geometry_shader_source = """
        #version 330 core
        layout(lines) in;
        layout(triangle_strip, max_vertices = 4) out;

        uniform mat4 u_viewMat;
        uniform vec2 u_screenSize;
        uniform float u_axesThickness;

        in GS_IN {
            vec3 color;
        } gs_in[];

        out vec4 f_color;

        void main() {
            // Apply view matrix rotation to positions
            vec3 rotatedStart = mat3(u_viewMat) * gl_in[0].gl_Position.xyz * 0.1;
            vec3 rotatedEnd = mat3(u_viewMat) * gl_in[1].gl_Position.xyz * 0.1;

            // Offset to corner
            vec2 screenPos = vec2(0.8, 0.8);
            rotatedStart.xy -= screenPos;
            rotatedEnd.xy -= screenPos;

            vec4 clipStart = vec4(rotatedStart, 1.0);
            vec4 clipEnd = vec4(rotatedEnd, 1.0);

            vec2 ndcStart = clipStart.xy;
            vec2 ndcEnd = clipEnd.xy;

            vec2 dir = normalize(ndcEnd - ndcStart);
            vec2 perpDir = vec2(-dir.y, dir.x);

            // Calculate line width in NDC
            float ndcThickness = u_axesThickness / u_screenSize.y * 2.0;

            vec2 offset = perpDir * ndcThickness / 2.0;
            gl_Position = vec4((ndcStart + offset), clipStart.zw);
            f_color = vec4(gs_in[0].color, 1.0);
            EmitVertex();

            gl_Position = vec4((ndcStart - offset), clipStart.zw);
            f_color = vec4(gs_in[0].color, 1.0);
            EmitVertex();

            gl_Position = vec4((ndcEnd + offset), clipEnd.zw);
            f_color = vec4(gs_in[1].color, 1.0);
            EmitVertex();

            gl_Position = vec4((ndcEnd - offset), clipEnd.zw);
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
            fragColor = f_color;
        }
        """

        self.points = None
        self.crystallography = None  # Store crystallography object for fractional coords
        self.axes_thickness = 2.0  # Default thickness
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

        self.vertex_buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.vertex_buffer.create()

        # Initialize with Cartesian axes
        self._initialize_axes()

    def _initialize_axes(self, axes_type='cartesian'):
        """Initialize axes based on type (cartesian or fractional)."""
        self.vertex_buffer.bind()

        if axes_type == 'cartesian' or self.crystallography is None:
            # Standard Cartesian axes
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
        else:
            # Fractional axes - convert from fractional to Cartesian
            # Fractional unit vectors
            frac_a = np.array([1, 0, 0])
            frac_b = np.array([0, 1, 0])
            frac_c = np.array([0, 0, 1])

            # Convert to Cartesian using the transformation matrix
            cart_a = self.crystallography.frac_to_cart(frac_a.reshape(1, -1))[0]
            cart_b = self.crystallography.frac_to_cart(frac_b.reshape(1, -1))[0]
            cart_c = self.crystallography.frac_to_cart(frac_c.reshape(1, -1))[0]

            # Normalize for display
            max_length = max(np.linalg.norm(cart_a), np.linalg.norm(cart_b), np.linalg.norm(cart_c))
            cart_a = cart_a / max_length
            cart_b = cart_b / max_length
            cart_c = cart_c / max_length

            self.points = np.array(
                (
                    (0, 0, 0, 1.0, 0.0, 0.0),
                    (cart_a[0], cart_a[1], cart_a[2], 1.0, 0.0, 0.0),
                    (0, 0, 0, 0.0, 1.0, 0.0),
                    (cart_b[0], cart_b[1], cart_b[2], 0.0, 1.0, 0.0),
                    (0, 0, 0, 0.0, 0.0, 1.0),
                    (cart_c[0], cart_c[1], cart_c[2], 0.0, 0.0, 1.0),
                ),
                dtype=np.float32,
            ).flatten()

        self.vertex_buffer.allocate(self.points.tobytes(), self.points.nbytes)

        if not hasattr(self, 'vao') or not self.vao.isCreated():
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

    def set_crystallography(self, crystallography):
        """Set the crystallography object and update axes to fractional coordinates."""
        self.crystallography = crystallography
        self._initialize_axes('fractional')

    def set_cartesian(self):
        """Reset axes to Cartesian coordinates."""
        self.crystallography = None
        self._initialize_axes('cartesian')

    def set_axes_thickness(self, thickness):
        """Set the thickness of the axes lines."""
        self.axes_thickness = thickness

    def setUniforms(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, float):
                self.program.setUniformValue1f(k, v)
            elif isinstance(v, int):
                self.program.setUniformValue1i(k, v)
            else:
                self.program.setUniformValue(k, v)
        # Always set axes thickness
        self.program.setUniformValue1f("u_axesThickness", self.axes_thickness)

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
