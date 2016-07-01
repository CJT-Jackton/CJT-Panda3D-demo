#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexDiffuse;
uniform sampler2D TexNormal;
//uniform sampler2D TexSpecular;
//uniform sampler2D TexIrradiance;

uniform struct p3d_LightSourceParameters {
    vec4 color;
} AmbientLight;

void main()
{
    vec4 albedo = texture(TexDiffuse, fTexCoord);
    vec4 color = albedo * AmbientLight.color;

    fColor = color;
}
