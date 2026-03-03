"""Renderer for crystallographic directions in world space.

Supports Line, Arrow, and Cylinder rendering styles (same as AxesRenderer)
but renders in world space using the MVP matrix rather than screen-corner space.
"""

import numpy as np
from OpenGL.GL import GL_BLEND, GL_FLOAT, GL_LINES, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA
from PySide6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVertexArrayObject,
)


class DirectionRenderer:
    def __init__(self):
        self.rendering_style = "cylinder"
        self.directions = []
        self.points = None

        # Vertex shader: passes position and color to geometry shader
        self.vertex_shader_source = """
        #version 330 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec3 color;
        layout(location = 2) in float alpha;

        out GS_IN {
            vec3 color;
            float alpha;
        } gs_in;

        void main() {
            gs_in.color = color;
            gs_in.alpha = alpha;
            gl_Position = vec4(position, 1.0);
        }
        """

        # Line geometry shader - world space
        self.geometry_shader_line = """
        #version 330 core
        layout(lines) in;
        layout(triangle_strip, max_vertices = 4) out;

        uniform mat4 u_modelViewProjectionMat;
        uniform vec2 u_screenSize;
        uniform float u_dirThickness;

        in GS_IN {
            vec3 color;
            float alpha;
        } gs_in[];

        out vec4 f_color;

        void main() {
            vec4 clipStart = u_modelViewProjectionMat * gl_in[0].gl_Position;
            vec4 clipEnd = u_modelViewProjectionMat * gl_in[1].gl_Position;

            vec2 ndcStart = clipStart.xy / clipStart.w;
            vec2 ndcEnd = clipEnd.xy / clipEnd.w;

            vec2 dir = normalize(ndcEnd - ndcStart);
            vec2 perpDir = vec2(-dir.y, dir.x);
            float ndcThickness = u_dirThickness / u_screenSize.y * 2.0;
            vec2 offset = perpDir * ndcThickness / 2.0;

            gl_Position = vec4((ndcStart + offset) * clipStart.w, clipStart.zw);
            f_color = vec4(gs_in[0].color, gs_in[0].alpha);
            EmitVertex();

            gl_Position = vec4((ndcStart - offset) * clipStart.w, clipStart.zw);
            f_color = vec4(gs_in[0].color, gs_in[0].alpha);
            EmitVertex();

            gl_Position = vec4((ndcEnd + offset) * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, gs_in[1].alpha);
            EmitVertex();

            gl_Position = vec4((ndcEnd - offset) * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, gs_in[1].alpha);
            EmitVertex();

            EndPrimitive();
        }
        """

        # Arrow geometry shader - world space
        self.geometry_shader_arrow = """
        #version 330 core
        layout(lines) in;
        layout(triangle_strip, max_vertices = 10) out;

        uniform mat4 u_modelViewProjectionMat;
        uniform vec2 u_screenSize;
        uniform float u_dirThickness;

        in GS_IN {
            vec3 color;
            float alpha;
        } gs_in[];

        out vec4 f_color;

        void main() {
            vec4 clipStart = u_modelViewProjectionMat * gl_in[0].gl_Position;
            vec4 clipEnd = u_modelViewProjectionMat * gl_in[1].gl_Position;

            vec2 ndcStart = clipStart.xy / clipStart.w;
            vec2 ndcEnd = clipEnd.xy / clipEnd.w;

            vec2 dir = normalize(ndcEnd - ndcStart);
            vec2 perpDir = vec2(-dir.y, dir.x);
            float ndcThickness = u_dirThickness / u_screenSize.y * 2.0;

            float totalLength = length(ndcEnd - ndcStart);
            float arrowLength = totalLength * 0.2;
            vec2 shaftEnd = ndcEnd - dir * arrowLength;
            vec2 offset = perpDir * ndcThickness / 2.0;

            // Shaft
            gl_Position = vec4((ndcStart + offset) * clipStart.w, clipStart.zw);
            f_color = vec4(gs_in[0].color, gs_in[0].alpha);
            EmitVertex();

            gl_Position = vec4((ndcStart - offset) * clipStart.w, clipStart.zw);
            f_color = vec4(gs_in[0].color, gs_in[0].alpha);
            EmitVertex();

            gl_Position = vec4((shaftEnd + offset) * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, gs_in[1].alpha);
            EmitVertex();

            gl_Position = vec4((shaftEnd - offset) * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, gs_in[1].alpha);
            EmitVertex();

            EndPrimitive();

            // Arrowhead — width proportional to head length for consistent aspect ratio
            vec2 arrowOffset = perpDir * arrowLength * 0.5;

            gl_Position = vec4((shaftEnd + arrowOffset) * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, gs_in[1].alpha);
            EmitVertex();

            gl_Position = vec4((shaftEnd - arrowOffset) * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, gs_in[1].alpha);
            EmitVertex();

            gl_Position = vec4(ndcEnd * clipEnd.w, clipEnd.zw);
            f_color = vec4(gs_in[1].color, gs_in[1].alpha);
            EmitVertex();

            EndPrimitive();
        }
        """

        # Cylinder geometry shader - world space with 3D lighting
        self.geometry_shader_cylinder = """
        #version 330 core
        layout(lines) in;
        layout(triangle_strip, max_vertices = 128) out;

        uniform mat4 u_modelViewProjectionMat;
        uniform mat4 u_viewMat;
        uniform vec2 u_screenSize;
        uniform float u_dirThickness;

        in GS_IN {
            vec3 color;
            float alpha;
        } gs_in[];

        out vec4 f_color;
        out vec3 v_normal;
        out vec3 v_fragPos;

        const int segments = 12;
        const float PI = 3.14159265359;

        void emitCylinder(vec3 start, vec3 end, float radius, vec3 color, float alpha) {
            vec3 dir = normalize(end - start);

            vec3 up = abs(dir.y) < 0.99 ? vec3(0, 1, 0) : vec3(1, 0, 0);
            vec3 right = normalize(cross(up, dir));
            vec3 forward = cross(dir, right);

            for (int i = 0; i <= segments; i++) {
                float angle = float(i) * 2.0 * PI / float(segments);
                float ca = cos(angle);
                float sa = sin(angle);

                vec3 normal = normalize(right * ca + forward * sa);
                vec3 offset = normal * radius;

                vec3 pos1 = start + offset;
                gl_Position = u_modelViewProjectionMat * vec4(pos1, 1.0);
                v_normal = mat3(u_viewMat) * normal;
                v_fragPos = pos1;
                f_color = vec4(color, alpha);
                EmitVertex();

                vec3 pos2 = end + offset;
                gl_Position = u_modelViewProjectionMat * vec4(pos2, 1.0);
                v_normal = mat3(u_viewMat) * normal;
                v_fragPos = pos2;
                f_color = vec4(color, alpha);
                EmitVertex();
            }
            EndPrimitive();
        }

        void emitCone(vec3 base, vec3 tip, float baseRadius, vec3 color, float alpha) {
            vec3 dir = normalize(tip - base);

            vec3 up = abs(dir.y) < 0.99 ? vec3(0, 1, 0) : vec3(1, 0, 0);
            vec3 right = normalize(cross(up, dir));
            vec3 forward = cross(dir, right);

            for (int i = 0; i <= segments; i++) {
                float angle = float(i) * 2.0 * PI / float(segments);
                float ca = cos(angle);
                float sa = sin(angle);

                vec3 normal = normalize(right * ca + forward * sa + dir);
                vec3 offset = (right * ca + forward * sa) * baseRadius;

                vec3 pos1 = base + offset;
                gl_Position = u_modelViewProjectionMat * vec4(pos1, 1.0);
                v_normal = mat3(u_viewMat) * normal;
                v_fragPos = pos1;
                f_color = vec4(color, alpha);
                EmitVertex();

                gl_Position = u_modelViewProjectionMat * vec4(tip, 1.0);
                v_normal = mat3(u_viewMat) * dir;
                v_fragPos = tip;
                f_color = vec4(color, alpha);
                EmitVertex();
            }
            EndPrimitive();
        }

        void main() {
            vec3 start = gl_in[0].gl_Position.xyz;
            vec3 end = gl_in[1].gl_Position.xyz;
            vec3 color = gs_in[0].color;
            float alpha = gs_in[0].alpha;

            float radius = u_dirThickness * 0.02;

            float totalLength = length(end - start);
            float arrowLength = totalLength * 0.2;
            vec3 dir = normalize(end - start);
            vec3 shaftEnd = end - dir * arrowLength;
            float coneRadius = max(radius * 2.5, arrowLength * 0.35);

            emitCylinder(start, shaftEnd, radius, color, alpha);
            emitCone(shaftEnd, end, coneRadius, color, alpha);
        }
        """

        # Fragment shader (flat)
        self.fragment_shader_source = """
        #version 330 core
        in vec4 f_color;
        out vec4 fragColor;

        void main() {
            fragColor = f_color;
        }
        """

        # Fragment shader (3D with lighting)
        self.fragment_shader_3d = """
        #version 330 core
        in vec4 f_color;
        in vec3 v_normal;
        in vec3 v_fragPos;
        out vec4 fragColor;

        void main() {
            vec3 lightDir = normalize(vec3(0.5, 0.5, 1.0));
            vec3 normal = normalize(v_normal);
            float ambient = 0.8;
            float diff = max(dot(normal, lightDir), 0.0);
            float diffuse = 0.5 * diff;
            float lighting = ambient + diffuse;
            fragColor = vec4(f_color.rgb * lighting, f_color.a);
        }
        """

        # Create shader programs
        self.programs = {}

        self.programs["line"] = QOpenGLShaderProgram()
        self.programs["line"].addShaderFromSourceCode(
            QOpenGLShader.Vertex, self.vertex_shader_source
        )
        self.programs["line"].addShaderFromSourceCode(
            QOpenGLShader.Geometry, self.geometry_shader_line
        )
        self.programs["line"].addShaderFromSourceCode(
            QOpenGLShader.Fragment, self.fragment_shader_source
        )
        self.programs["line"].link()

        self.programs["cylinder"] = QOpenGLShaderProgram()
        self.programs["cylinder"].addShaderFromSourceCode(
            QOpenGLShader.Vertex, self.vertex_shader_source
        )
        self.programs["cylinder"].addShaderFromSourceCode(
            QOpenGLShader.Geometry, self.geometry_shader_cylinder
        )
        self.programs["cylinder"].addShaderFromSourceCode(
            QOpenGLShader.Fragment, self.fragment_shader_3d
        )
        self.programs["cylinder"].link()

        self.programs["arrow"] = QOpenGLShaderProgram()
        self.programs["arrow"].addShaderFromSourceCode(
            QOpenGLShader.Vertex, self.vertex_shader_source
        )
        self.programs["arrow"].addShaderFromSourceCode(
            QOpenGLShader.Geometry, self.geometry_shader_arrow
        )
        self.programs["arrow"].addShaderFromSourceCode(
            QOpenGLShader.Fragment, self.fragment_shader_source
        )
        self.programs["arrow"].link()

        self.program = self.programs["cylinder"]

        self.vertex_buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.vertex_buffer.create()

        self.vao = QOpenGLVertexArrayObject()
        self.vao.create()

    def set_directions(self, directions, crystallography=None, max_extent=1.0):
        """Set direction data from list of direction dicts.

        Each dict has: vector, origin, fractional, style, thickness, length, color, alpha
        length is a relative multiplier; actual world-space length = length * max_extent.
        """
        self.directions = directions
        if not directions:
            self.points = None
            return

        # Build vertex data: each direction is 2 vertices (origin, endpoint)
        # Vertex format: x, y, z, r, g, b, alpha = 7 floats
        all_points = []

        for d in directions:
            vec = np.array(d.vector, dtype=np.float64)
            origin = np.array(d.origin, dtype=np.float64)

            # Convert fractional to Cartesian if needed
            if d.fractional and crystallography is not None:
                vec = crystallography.frac_to_cart(vec.reshape(1, -1))[0]

            # Normalize and apply length (d.length is a relative multiplier)
            length = np.linalg.norm(vec)
            if length > 1e-10:
                vec = vec / length * (d.length * max_extent)

            endpoint = origin + vec
            r, g, b = d.color
            alpha = d.alpha

            all_points.extend([
                origin[0], origin[1], origin[2], r, g, b, alpha,
                endpoint[0], endpoint[1], endpoint[2], r, g, b, alpha,
            ])

        self.points = np.array(all_points, dtype=np.float32)
        self._upload_data()

    def _upload_data(self):
        if self.points is None or len(self.points) == 0:
            return

        self.vertex_buffer.bind()
        self.vertex_buffer.allocate(self.points.tobytes(), self.points.nbytes)

        self.vao.bind()
        self.program.bind()

        stride = 7 * 4  # 7 floats * 4 bytes
        self.program.enableAttributeArray(0)
        self.program.setAttributeBuffer(0, GL_FLOAT, 0, 3, stride)
        self.program.enableAttributeArray(1)
        self.program.setAttributeBuffer(1, GL_FLOAT, 3 * 4, 3, stride)
        self.program.enableAttributeArray(2)
        self.program.setAttributeBuffer(2, GL_FLOAT, 6 * 4, 1, stride)

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
        if self.points is None or len(self.points) == 0:
            return

        # Group directions by rendering style and draw each group
        # For simplicity with the current design, we draw all with the same style
        # determined by the first direction (or we could iterate)
        n = len(self.points) // 7
        gl.glDrawArrays(GL_LINES, 0, n)

    def draw_directions(self, gl, uniforms, directions):
        """Draw directions grouped by rendering style."""
        if not directions or self.points is None:
            return

        # Group directions by style
        style_groups = {}
        for i, d in enumerate(directions):
            if d.style not in style_groups:
                style_groups[d.style] = []
            style_groups[d.style].append(i)

        for style, indices in style_groups.items():
            if style in self.programs:
                self.program = self.programs[style]

            self._upload_data()
            self.bind()
            self.setUniforms(**uniforms)

            # Set per-style thickness from first direction in group
            self.program.setUniformValue1f("u_dirThickness", directions[indices[0]].thickness)

            # Draw only the lines for this style group
            for idx in indices:
                gl.glDrawArrays(GL_LINES, idx * 2, 2)

            self.release()

    def numberOfPoints(self):
        if self.points is None:
            return 0
        return len(self.points) // 7
