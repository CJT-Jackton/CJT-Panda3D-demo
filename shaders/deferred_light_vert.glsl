#version 330 core

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 fTexCoord;

uniform vec2 TexScale;

void main()
{
	//fPos = p3d_ModelViewMatrix * p3d_Vertex;
    //fPos.z = 0.0;
    //fTexCoord = p3d_Vertex.xz * 0.5 + 0.5;
    //fTexCoord = p3d_MultiTexCoord0 * vec2(0.625, 0.703125);
    fTexCoord = p3d_MultiTexCoord0 * TexScale;

    //gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    vec4 p = p3d_Vertex.xzyw;
    p.w = 1.0;
    gl_Position = p;
}
