#version 330 core

in vec3 fNormal;
in vec2 fTexCoord;

layout (location = 0) out vec4 gDiffuse;
layout (location = 1) out vec4 gNormal;
//layout (location = 2) out vec4 gSpecular;
//layout (location = 3) out vec4 gIrradiance;
//layout (location = 4) out vec4 gDepth-Stencil;

uniform sampler2D p3d_Texture0;

void main()
{
	gDiffuse = texture(p3d_Texture0, fTexCoord);
    gNormal.rgb = normalize(fNormal);
    gNormal.a = 1.0;
}