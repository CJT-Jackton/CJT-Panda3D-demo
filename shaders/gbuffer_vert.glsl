#version 330 core

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec3 fNormal;
out vec2 fTexCoord;
out vec4 fPos_view;

uniform mat3 p3d_NormalMatrix;
// This is the upper 3x3 of the inverse transpose of the ModelViewMatrix.  It is used
// to transform the normal vector into view-space coordinates.
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

void main()
{
	//fNormal = transpose(inverse(mat3(p3d_ModelMatrix))) * p3d_Normal;
	fNormal = p3d_NormalMatrix * p3d_Normal;
	fTexCoord = p3d_MultiTexCoord0;

	fPos_view = p3d_ModelViewMatrix * vec4(p3d_Vertex.xyz, 1.0);

    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
