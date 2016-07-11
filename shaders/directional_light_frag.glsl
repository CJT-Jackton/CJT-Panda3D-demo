#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform mat4 p3d_ViewMatrix;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexDiffuse;
uniform sampler2D TexNormal;
//uniform sampler2D TexSpecular;
//uniform sampler2D TexIrradiance;

uniform struct p3d_LightSourceParameters{
    vec4 color;
    vec4 specular;
    vec4 position;
    // Shadow map for this light source
    sampler2DShadow shadowMap;
    // Transforms vertex coordinates to shadow map coordinates
    mat4 shadowMatrix;
} DirectionalLight;

void main()
{
    float fDepth = texture(TexDepthStencil, fTexCoord * texScale).a;
    vec4 tmp = p3d_ProjectionMatrixInverse * vec4((fTexCoord.x * 2 - 1.0), (fTexCoord.y * 2 - 1.0), (fDepth * 2 - 1.0), 1.0);
    vec3 fPos_view = tmp.xyz / tmp.w;
    vec3 fPos_world = p3d_ViewMatrixInverse * fPos_view;
    vec4 tmp = DirectionalLight.shadowMatrix * vec4(fPos_world, 1.0);
    vec3 fPos_light = tmp.xyz / tmp.w;
    fPos_light = fPos_light * 0.5 + 0.5;

    float fDepth_light = texture(shadowMap, fPos_light.xy).r;
    float bias = 0.005;
    float shadow = fPos_light.z > fDepth_light + bias ? 1.0 : 0.0;

    vec4 albedo = texture(TexDiffuse, fTexCoord);
    vec3 normal = (texture(TexNormal, fTexCoord).rbg - 0.5) * 2;

    vec3 direction_world = DirectionalLight.position.xyz;

    vec3 direction = normalize(mat3(p3d_ViewMatrix) * direction_world);

    vec4 diffuse = DirectionalLight.color * max(dot(-direction, normal), 0.0);
    vec4 color = albedo * diffuse * shadow;

    fColor = color;
}
