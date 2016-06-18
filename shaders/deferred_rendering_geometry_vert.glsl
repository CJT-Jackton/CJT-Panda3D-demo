#version 330 core

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec3 fNormal;
out vec2 fTexCoord;

uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
	fNormal = transpose(inverse(mat3(p3d_ModelMatrix))) * p3d_Normal;
	fTexCoord = p3d_MultiTexCoord0;

    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}