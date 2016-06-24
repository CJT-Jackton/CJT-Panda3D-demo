#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform sampler2D gDepthStencil;
uniform sampler2D gDiffuse;
uniform sampler2D gNormal;
//uniform sampler2D gSpecular;
//uniform sampler2D gIrradiance;
uniform struct p3d_LightSourceParameters {
  vec4 color;
} AmbientLight;

void main()
{
    vec4 albedo = texture(gDiffuse, fTexCoord);
    vec4 color = albedo * AmbientLight.color;

    fColor = color;
}
