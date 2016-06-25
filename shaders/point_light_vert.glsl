#version 330 core

in vec4 p3d_Vertex;

out vec2 fTexCoord;

uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
	fTexCoord = vec2(0.0, 0.0);

    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
