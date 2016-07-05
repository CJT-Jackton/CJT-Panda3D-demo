#version 330 core

in vec4 fPos;
in vec2 fTexCoord;

layout (location = 0) out vec4 TexSSAONoisy;

uniform vec2 texScale;
uniform vec2 texScaleNoise;

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ProjectionMatrixInverse;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexNormal;
uniform sampler2D TexNoise;

uniform vec4 samples[64];

int kernelSize = 64;
float radius = 3.0;

const float NEAR = 1.0; // Projection matrix's near plane distance
const float FAR = 500.0; // Projection matrix's far plane distance
float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0;
    return (2.0 * NEAR * FAR) / (FAR + NEAR - z * (FAR - NEAR));    
}

void main()
{
	float depth = texture(TexDepthStencil, fTexCoord * texScale).r;
    vec4 tmp = p3d_ProjectionMatrixInverse * vec4(fPos.x, fPos.y, (depth * 2 - 1.0), 1.0);
    vec3 fPos_view = tmp.xyz / tmp.w;

    vec3 normal = normalize(texture(TexNormal, fTexCoord * texScale).rbg * 2 - 1);

    vec3 randomVec = normalize(texture(TexNoise, fTexCoord * texScaleNoise).xyz * 2 - 1);

    // Create TBN change-of-basis matrix: from tangent-space to view-space
    vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TangentMatrix = mat3(tangent, bitangent, normal);

    float AmbientOcclusion = 0.0;

    for(int i = 0; i < kernelSize; ++i)
    {
        vec3 sampleVec = TangentMatrix * samples[i].xyz;
        vec3 sample_view = fPos_view + sampleVec * radius;

        vec4 offset = vec4(sample_view, 1.0);
        offset = p3d_ProjectionMatrix * offset;
        offset.xyz /= offset.w;
        offset.xyz = offset.xyz * 0.5 + 0.5;

        float sample_depth = -texture(TexDepthStencil, offset.xy * texScale).r;

        float rangeCheck = smoothstep(0.0, 1.0, radius / abs(fPos_view.z - sample_depth));
        
        if(LinearizeDepth(sample_depth) >= sample_view.z)
            AmbientOcclusion += 1.0 * rangeCheck;
    }

    AmbientOcclusion = 1.0 - (AmbientOcclusion / 64.0);

    TexSSAONoisy = vec4(AmbientOcclusion, AmbientOcclusion, AmbientOcclusion, 1.0);
}
