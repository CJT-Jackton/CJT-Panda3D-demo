#version 420 core

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 fTexCoord;
out vec4 offset;

//uniform SMAA_RT_METRICS = vec4(1.0 / 1280.0, 1.0 / 720.0, 1280.0, 720.0);
#define SMAA_RT_METRICS vec4(1.0 / 1280.0, 1.0 / 720.0, 1280.0, 720.0)
#define SMAA_GLSL_4 1
#define SMAA_PRESET_ULTRA 1
#define SMAA_INCLUDE_VS 1
#define SMAA_INCLUDE_PS 0

void SMAANeighborhoodBlendingVS(vec2 texcoord,
                                out vec4 offset) {
    offset = fma(SMAA_RT_METRICS.xyxy, vec4( 1.0, 0.0, 0.0,  1.0), texcoord.xyxy);
}

uniform vec2 texScale;

void main()
{
    fTexCoord = p3d_MultiTexCoord0 * texScale;

    SMAANeighborhoodBlendingVS(fTexCoord, offset);

    vec4 pos = p3d_Vertex.xzyw;
    pos.w = 1.0;
    gl_Position = pos;
}
