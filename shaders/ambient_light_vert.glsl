#version 330 core

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 fTexCoord;

uniform vec2 texScale;

void main()
{
    fTexCoord = p3d_MultiTexCoord0 * texScale;

    vec4 pos = p3d_Vertex.xzyw;
    pos.w = 1.0;
    gl_Position = pos;
}
