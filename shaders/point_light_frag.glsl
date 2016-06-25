#version 330 core

in vec4 fPos;

layout (location = 0) out vec4 fColor;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ViewMatrix;

uniform sampler2D gDepthStencil;
uniform sampler2D gDiffuse;
uniform sampler2D gNormal;
//uniform sampler2D gSpecular;
//uniform sampler2D gIrradiance;
uniform vec2 TexScale;
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
    vec2 fTexCoord = (fPos_clip.xy * 0.5 + 0.5) * TexScale;

    vec4 albedo = texture(gDiffuse, fTexCoord);
    vec3 normal = (texture(gNormal, fTexCoord).rbg - 0.5) * 2;
    float depth = texture(gDepthStencil, fTexCoord);

    vec3 fPos_view = (fPos_clip.xzy * TranSStoVS.xyz) / (depth + TranSStoVS.w);

    vec4 lpos_view = p3d_ViewMatrix * PointLight.position;
    vec3 lvec = vec3(lpos_view) - fPos_view;
    float ldistance = length(lvec);
    vec3 ldir = normalize(lvec);

    vec4 diffuse = PointLight.color * max(dot(normal, ldir), 0.0);
    vec4 color = albedo * diffuse;

    fColor = color;
}
