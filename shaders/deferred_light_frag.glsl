#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform sampler2D gDepthStencil;
uniform sampler2D gDiffuse;
uniform sampler2D gNormal;
//uniform sampler2D gSpecular;
//uniform sampler2D gIrradiance;

void main()
{
	//vec3 SPos = fPos.xyz / fPos.w;
	//vec2 fTexCoord = (fPos * 0.5 + 0.5).xy;
	vec3 color = texture(gNormal, fTexCoord).rgb;

	//vec3 color = (fPos * 0.5 + 0.5).rgb;
	//color.b = 0.0;

    fColor = vec4(color, 1.0f);
}
