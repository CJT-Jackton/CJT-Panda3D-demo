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
    vec3 attenuation;
} PointLight;

void main()
{
    vec3 fPos_clip = fPos.xyz / fPos.w;
    vec2 fTexCoord = fPos_clip.xy * 0.5 + 0.5;

    vec4 albedo = texture(TexDiffuse, fTexCoord);
    vec3 normal = texture(TexNormal, fTexCoord).rbg * 2 - 1.0;
    //float spec = 1.0;
    float spec = texture(TexSpecular, fTexCoord).r;
    float depth = texture(TexDepthStencil, fTexCoord).r;

    vec4 tmp = p3d_ProjectionMatrixInverse * vec4(fPos_clip.x, fPos_clip.y, (depth * 2 - 1.0), 1.0);
    vec3 fPos_view = tmp.xyz / tmp.w;
    //vec3 fPos_view = (fPos_clip.xyz * TranSStoVS.xyz) / (depth + TranSStoVS.w);
    //vec3 fPos_view = (texture(TexSpecular, fTexCoord).rgb - 0.5) * 2;
    //vec3 fPos_view = texture(TexSpecular, fTexCoord).rgb;
    //vec3 fPos = (texture(TexSpecular, fTexCoord).rgb);

    vec4 lpos = p3d_ViewMatrix * vec4(PointLight.position.xyz, 1.0);
    //vec4 lpos = p3d_ViewMatrix * PointLight.position;
    //lpos = vec4(lpos.xyz / lpos.w, 1.0);
    vec3 lvec = vec3(lpos) - fPos_view;
    //vec3 lvec = mat3(p3d_ViewMatrix) * vec3(fPos - PointLight.position.xzy);

    //vec4 lvec = lpos - p3d_ViewMatrix * vec4(0.0, 0.0, 0.0, 1.0);
    float ldistance = length(lvec);
    vec3 ldir = lvec / ldistance;
    vec3 viewDir = normalize(-fPos_view);
    vec3 lhalf = normalize(ldir + viewDir);
    //vec3 ldir = normalize(lvec);

    float att = 1.0 / (PointLight.attenuation.x
      + PointLight.attenuation.y * ldistance
      + PointLight.attenuation.z * ldistance * ldistance);

    vec4 diffuse = PointLight.color * max(dot(ldir, normal), 0.0);
    vec4 specular = spec * PointLight.specular * pow(max(dot(lhalf, normal), 0.0), 64);
    vec4 color = att * albedo * (diffuse + specular);

    fColor = color;
}
