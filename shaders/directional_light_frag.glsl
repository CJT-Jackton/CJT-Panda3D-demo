#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexDiffuse;
uniform sampler2D TexNormal;
//uniform sampler2D TexSpecular;
//uniform sampler2D TexIrradiance;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ViewMatrix;
uniform struct p3d_LightSourceParameters {
  // Primary light color.
  vec4 color;
 
  // Light color broken up into components, for compatibility with legacy shaders.
  vec4 ambient;
  vec4 diffuse;
  vec4 specular;
 
  // View-space position.  If w=0, this is a directional light, with
  // the xyz being -direction.
  vec4 position;
 
  // Spotlight-only settings
  vec3 spotDirection;
  float spotExponent;
  float spotCutoff;
  float spotCosCutoff;
 
  // Individual attenuation constants
  float constantAttenuation;
  float linearAttenuation;
  float quadraticAttenuation;
 
  // constant, linear, quadratic attenuation in one vector
  vec3 attenuation;

} LightSource;

void main()
{
    //vec4 pos = vec4(fTexCoord, texture(gDepthStencil, fTexCoord).r, 1.0);
    vec4 albedo = texture(TexDiffuse, fTexCoord);
    vec3 normal = (texture(TexNormal, fTexCoord).rbg - 0.5) * 2;

    //vec4 direction_world = vec4(LightSource.position.xyz, 1.0);
    vec3 direction_world = LightSource.position.xyz;

    //vec3 direction = normalize(p3d_ViewMatrix * direction_world - p3d_ViewMatrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
    vec3 direction = normalize(mat3(p3d_ViewMatrix) * direction_world);

    vec4 diffuse = LightSource.color * max(dot(-direction, normal), 0.0);
    vec4 color = albedo * diffuse;

    fColor = color;
}
