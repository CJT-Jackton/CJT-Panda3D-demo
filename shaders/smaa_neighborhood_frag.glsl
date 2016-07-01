#version 420 core

in vec2 fTexCoord;
in vec4 offset;

layout (location = 0) out vec4 TexSMAA;

//uniform SMAA_RT_METRICS = vec4(1.0 / 1280.0, 1.0 / 720.0, 1280.0, 720.0);
#define SMAA_RT_METRICS vec4(1.0 / 1280.0, 1.0 / 720.0, 1280.0, 720.0)
#define SMAA_GLSL_4 1
#define SMAA_PRESET_ULTRA 1
#define SMAA_INCLUDE_VS 0
#define SMAA_INCLUDE_PS 1

#ifndef SMAA_REPROJECTION
#define SMAA_REPROJECTION 0
#endif

#ifndef SMAA_DECODE_VELOCITY
#define SMAA_DECODE_VELOCITY(sample) sample.rg
#endif

#define SMAA_FLATTEN

void SMAAMovc(bvec2 cond, inout vec2 variable, vec2 value) {
    SMAA_FLATTEN if (cond.x) variable.x = value.x;
    SMAA_FLATTEN if (cond.y) variable.y = value.y;
}

void SMAAMovc(bvec4 cond, inout vec4 variable, vec4 value) {
    SMAAMovc(cond.xy, variable.xy, value.xy);
    SMAAMovc(cond.zw, variable.zw, value.zw);
}

vec4 SMAANeighborhoodBlendingPS(vec2 texcoord,
                                vec4 offset,
                                sampler2D colorTex,
                                sampler2D blendTex 
                                #if SMAA_REPROJECTION
                                , sampler2D velocityTex
                                #endif
                                ) {
    // Fetch the blending weights for current pixel:
    vec4 a;
    a.x = texture(blendTex, offset.xy).a; // Right
    a.y = texture(blendTex, offset.zw).g; // Top
    a.wz = texture(blendTex, texcoord).xz; // Bottom / Left

    // Is there any blending weight with a value greater than 0.0?

    if (dot(a, vec4(1.0, 1.0, 1.0, 1.0)) < 1e-5) {
        vec4 color = textureLod(colorTex, texcoord, 0.0);

        #if SMAA_REPROJECTION
        vec2 velocity = SMAA_DECODE_VELOCITY(textureLod(velocityTex, texcoord, 0.0));

        // Pack velocity into the alpha channel:
        color.a = sqrt(5.0 * length(velocity));
        #endif

        return color;
    } else {
        bool h = max(a.x, a.z) > max(a.y, a.w); // max(horizontal) > max(vertical)

        // Calculate the blending offsets:
        vec4 blendingOffset = vec4(0.0, a.y, 0.0, a.w);
        vec2 blendingWeight = a.yw;
        SMAAMovc(bvec4(h, h, h, h), blendingOffset, vec4(a.x, 0.0, a.z, 0.0));
        SMAAMovc(bvec2(h, h), blendingWeight, a.xz);
        blendingWeight /= dot(blendingWeight, vec2(1.0, 1.0));

        // Calculate the texture coordinates:
        vec4 blendingCoord = fma(blendingOffset, vec4(SMAA_RT_METRICS.xy, -SMAA_RT_METRICS.xy), texcoord.xyxy);

        // We exploit bilinear filtering to mix current pixel with the chosen
        // neighbor:
        vec4 color = blendingWeight.x * textureLod(colorTex, blendingCoord.xy, 0.0);
        color += blendingWeight.y * textureLod(colorTex, blendingCoord.zw, 0.0);

        #if SMAA_REPROJECTION
        // Antialias velocity for proper reprojection in a later stage:
        vec2 velocity = blendingWeight.x * SMAA_DECODE_VELOCITY(textureLod(velocityTex, blendingCoord.xy, 0.0));
        velocity += blendingWeight.y * SMAA_DECODE_VELOCITY(textureLod(velocityTex, blendingCoord.zw, 0.0));

        // Pack velocity into the alpha channel:
        color.a = sqrt(5.0 * length(velocity));
        #endif

        return color;
    }
}

uniform sampler2D TexAlias;
uniform sampler2D TexBlend;

void main()
{
    TexSMAA = SMAANeighborhoodBlendingPS(fTexCoord, offset, TexAlias, TexBlend);
}
