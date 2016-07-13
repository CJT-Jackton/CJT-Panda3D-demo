#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ViewMatrixInverse;
uniform mat4 p3d_ProjectionMatrixInverse;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexDiffuse;
uniform sampler2D TexNormal;
//uniform sampler2D TexSpecular;
//uniform sampler2D TexIrradiance;

uniform struct p3d_LightSourceParameters{
    vec4 color;
    vec4 specular;
    vec4 position;
} DirectionalLight;

void main()
{
    vec4 albedo = texture(TexDiffuse, fTexCoord);
    vec3 normal = (texture(TexNormal, fTexCoord).rbg - 0.5) * 2;

    vec3 direction_world = DirectionalLight.position.xyz;

    vec3 direction = normalize(mat3(p3d_ViewMatrix) * direction_world);

    vec4 diffuse = DirectionalLight.color * max(dot(-direction, normal), 0.0);
    vec4 color = albedo * diffuse;

    fColor = color;
}
