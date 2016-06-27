#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform sampler2D gHDR;

const float gamma = 2.2;
const float exposure = 0.25;

vec3 linear(vec3 color_hdr)
{
    color_hdr *= exposure;
    return pow(color_hdr, vec3(1.0 / gamma));
}

vec3 Reinhard(vec3 color_hdr)
{
    color_hdr *= exposure;
    color_hdr = color_hdr / (1.0 + color_hdr);
    return pow(color_hdr, vec3(1.0 / gamma));
}

vec3 Jim_Richard(vec3 color_hdr)
{
    color_hdr *= exposure;
    vec3 x = max(vec3(0.0), color_hdr - 0.0004);
    return (x * (6.2 * x + 0.5)) / (x * (6.2 * x + 1.7) + 0.06);
}

float A = 0.15;
float B = 0.50;
float C = 0.10;
float D = 0.20;
float E = 0.02;
float F = 0.30;
float W = 11.2;
vec3 Uncharted2Tonemap(vec3 x)
{
    return ((x * (A * x + C * B) + D * E) / (x * (A * x + B) + D * F)) - E / F;
} 

vec3 Filmic(vec3 color_hdr)
{
    color_hdr *= exposure;
    float exposureBias = 0.5;
    vec3 curr = Uncharted2Tonemap(exposureBias * color_hdr);

    vec3 whiteScale = 1.0 / Uncharted2Tonemap(vec3(W));
    vec3 color = curr * whiteScale;

    return pow(color, vec3(1.0 / gamma));
}

void main()
{
    vec3 color_hdr = texture(gHDR, fTexCoord).rgb;
    fColor = vec4(Jim_Richard(color_hdr), 1.0);
}
