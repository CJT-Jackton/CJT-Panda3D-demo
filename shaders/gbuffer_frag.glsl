#version 330 core

in vec3 fNormal;
in vec2 fTexCoord;
in vec4 fPos_view;

layout (location = 0) out vec4 TexDiffuse;
layout (location = 1) out vec4 TexNormal;
layout (location = 2) out vec4 TexSpecular;
//layout (location = 3) out vec4 TexIrradiance;
//layout (location = 4) out vec4 TexDepthStencil;

uniform sampler2D p3d_Texture0;

const float NEAR = 1.0f; // Projection matrix's near plane distance
const float FAR = 500.0f; // Projection matrix's far plane distance
float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // Back to NDC 
    return (2.0 * NEAR * FAR) / (FAR + NEAR - z * (FAR - NEAR));	
}


void main()
{
	TexDiffuse = texture(p3d_Texture0, fTexCoord);
    TexNormal.rbg = normalize(fNormal) * 0.5 + 0.5;
    TexNormal.a = 1.0;

    TexSpecular.rgb = fPos_view.xyz;
    TexSpecular.a = LinearizeDepth(gl_FragCoord.z);
}
