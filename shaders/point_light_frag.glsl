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
  vec4 specular;
 
  // View-space position.  If w=0, this is a directional light, with
  // the xyz being -direction.
  vec4 position;
 
  vec3 attenuation;

} PointLight;

void main()
{
    vec4 diffuse = PointLight.color;
    vec4 color = diffuse;

    fColor = color;
}
