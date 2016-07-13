#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform sampler2D TexDiffuse;

uniform struct p3d_LightSourceParameters {
    vec4 color;
} AmbientLight;

void main()
{
    vec3 albedo = texture(TexDiffuse, fTexCoord).rgb;
    vec4 color = vec4(albedo, 1.0) * AmbientLight.color;

    fColor = color;
}
