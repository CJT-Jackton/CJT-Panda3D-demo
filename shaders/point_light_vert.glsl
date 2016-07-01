#version 330 core

in vec4 p3d_Vertex;

out vec4 fPos;

uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    fPos = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fPos.z = fPos.w;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
