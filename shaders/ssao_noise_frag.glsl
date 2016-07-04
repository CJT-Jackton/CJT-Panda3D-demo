#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 TexSSAONoisy;

uniform vec2 texScale;
uniform vec2 texScaleNoise;

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ProjectionMatrixInverse;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexNormal;
uniform sampler2D TexNoise;

//uniform vec3 samples[64];

int kernelSize = 64;
float radius = 1.0;


void main()
{
	//float depth = texture(TexDepthStencil, fTexCoord).r;
    //vec4 tmp = p3d_ProjectionMatrixInverse * vec4(fPos_clip.x, fPos_clip.y, (depth * 2 - 1.0), 1.0);
    //vec3 fPos_view = tmp.xyz / tmp.w;

    vec3 normal = (texture(TexNormal, fTexCoord * texScale).rbg - 0.5) * 2;

    vec3 randomVec = texture(TexNoise, fTexCoord * texScaleNoise).xyz;

    // Create TBN change-of-basis matrix: from tangent-space to view-space
    vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TBN = mat3(tangent, bitangent, normal);

    TexSSAONoisy = vec4(randomVec, 1.0);
}
