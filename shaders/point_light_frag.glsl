#version 330 core

in vec4 fPos;

layout (location = 0) out vec4 fColor;

uniform mat4 p3d_ViewMatrixInverse;
uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ModelViewMatrixInverse;
uniform mat3 p3d_NormalMatrix;
//uniform mat4 p3d_ProjectionMatrixInverse;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexDiffuse;
uniform sampler2D TexNormal;
uniform sampler2D TexSpecular;
//uniform sampler2D gIrradiance;
uniform vec2 texScale;
uniform vec4 TranSStoVS;
uniform struct p3d_LightSourceParameters {
  vec4 color;
  vec4 specular;
 
  // View-space position.  If w=0, this is a directional light, with
  // the xyz being -direction.
  vec4 position;
 
  vec3 attenuation;

} PointLight;

void main()
{
    vec3 fPos_clip = fPos.xyz / fPos.w;
    vec2 fTexCoord = (fPos_clip.xy * 0.5 + 0.5) * texScale;

    vec4 albedo = texture(TexDiffuse, fTexCoord);
    vec3 normal = (texture(TexNormal, fTexCoord).rbg - 0.5) * 2;
    //vec3 normal = texture(TexNormal, fTexCoord).rbg;
    float depth = texture(TexDepthStencil, fTexCoord).a;

    //vec4 tmp = p3d_ProjectionMatrixInverse * vec4(fPos_clip.x, fPos_clip.y, depth, 1.0);
    //vec3 fPos_view = tmp.xyz / tmp.w;
    //vec3 fPos_view = (fPos_clip.xyz * TranSStoVS.xyz) / (depth + TranSStoVS.w);
    vec3 fPos_view = (texture(TexSpecular, fTexCoord).rgb - 0.5) * 2;
    //vec3 fPos_view = texture(TexSpecular, fTexCoord).rgb;

    vec4 lpos = p3d_ViewMatrix * vec4(PointLight.position.xyz, 1.0);
    //lpos = vec4(lpos.xyz / lpos.w, 1.0);
    vec4 lvec = lpos - vec4(fPos_view, 1.0);
    //vec4 lvec = lpos - p3d_ViewMatrix * vec4(0.0, 0.0, 0.0, 1.0);
    float ldistance = length(lvec);
    //vec3 ldir = lvec.xyz / ldistance;
    vec3 ldir = normalize(lvec.xyz);

    float att = 1.0 / (PointLight.attenuation.x
      + PointLight.attenuation.y * ldistance
      + PointLight.attenuation.z * ldistance * ldistance);

    vec4 diffuse = PointLight.color * max(dot(normal, ldir), 0.0);
    vec4 color = albedo * diffuse;

    fColor = vec4(depth, depth, depth, 1.0);
    //fColor = color;
}
