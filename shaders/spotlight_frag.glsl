#version 330 core

in vec4 fPos;

layout (location = 0) out vec4 fColor;

uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ProjectionMatrixInverse;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexDiffuse;
uniform sampler2D TexNormal;
uniform sampler2D TexSpecular;
//uniform sampler2D gIrradiance;

uniform struct p3d_LightSourceParameters {
    vec4 color;
    vec4 specular;
    vec4 position;

    vec3 spotDirection;
    //float spotExponent;
    //float spotCutoff;
    float spotCosCutoff;

    vec3 attenuation;
} Spotlight;

void main()
{
    vec3 fPos_clip = fPos.xyz / fPos.w;
    vec2 fTexCoord = fPos_clip.xy * 0.5 + 0.5;

    float depth = texture(TexDepthStencil, fTexCoord).a;

    vec4 tmp = p3d_ProjectionMatrixInverse * vec4(fPos_clip.x, fPos_clip.y, (depth * 2 - 1.0), 1.0);
    vec3 fPos_view = tmp.xyz / tmp.w;

    vec4 lpos = p3d_ViewMatrix * vec4(Spotlight.position.xyz, 1.0);
    vec3 lvec = vec3(lpos) - fPos_view;

    float ldistance = length(lvec);
    vec3 ldir = lvec / ldistance;

    vec3 spotDir_view = normalize(mat3(p3d_ViewMatrix) * Spotlight.spotDirection);
    float theta = dot(ldir, -spotDir_view);

    vec4 color;

    if(theta > Spotlight.spotCosCutoff)
    {
        vec4 albedo = texture(TexDiffuse, fTexCoord);
        vec3 normal = texture(TexNormal, fTexCoord).rbg * 2 - 1.0;
        float spec = texture(TexSpecular, fTexCoord).r;

        vec3 viewDir = normalize(-fPos_view);
        vec3 lhalf = normalize(ldir + viewDir);

        float att = 1.0 / (Spotlight.attenuation.x
          + Spotlight.attenuation.y * ldistance
          + Spotlight.attenuation.z * ldistance * ldistance);

        vec4 diffuse = Spotlight.color * max(dot(ldir, normal), 0.0);
        vec4 specular = spec * Spotlight.specular * pow(max(dot(lhalf, normal), 0.0), 64);
        color = att * albedo * (diffuse + specular); // att * albedo * (diffuse + specular)
    }
    else
    {
        color = vec4(0.0);
    }

    fColor = color;
}
