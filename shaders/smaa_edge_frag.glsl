#version 420 core

in vec2 fTexCoord;
in vec4 offset[3];

layout (location = 0) out vec4 TexEdge;

//uniform SMAA_RT_METRICS = vec4(1.0 / 1280.0, 1.0 / 720.0, 1280.0, 720.0);
#define SMAA_RT_METRICS vec4(1.0 / 1280.0, 1.0 / 720.0, 1280.0, 720.0)
#define SMAA_GLSL_4 1
#define SMAA_PRESET_ULTRA 1
#define SMAA_INCLUDE_VS 1

#include "SMAA.hlsl"

uniform sampler2D TexAlias;
uniform sampler2D TexPredication;

void main()
{
	vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    #if SMAA_PREDICATION
    color.rg = SMAALumaEdgeDetectionPS(fTexCoord, offset, TexAlias, TexPredication);
    #elif
    color.rg = SMAALumaEdgeDetectionPS(fTexCoord, offset, TexAlias);
    #endif
    TexEdge = color;
}
