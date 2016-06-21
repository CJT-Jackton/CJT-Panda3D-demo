#version 330 core

in vec4 p3d_Vertex;

out vec4 fPos;
//out vec2 fTexCoord;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
	vec4 fPos = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    //fPos.z = fPos.w;
    //fTexCoord = p3d_MultiTexCoord0;

    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}