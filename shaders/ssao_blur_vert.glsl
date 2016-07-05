#version 330 core

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 fTexCoord;

void main()
{
    fTexCoord = p3d_MultiTexCoord0;

    vec4 fPos = p3d_Vertex.xzyw;
    fPos.w = 1.0;
    gl_Position = fPos;
}
