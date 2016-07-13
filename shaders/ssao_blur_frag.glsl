#version 330 core

in vec2 fTexCoord;

layout (location = 0) out float TexSSAOBlurred;

uniform sampler2D TexSSAONoisy;

uniform ivec2 ScreenSize = ivec2(1280, 720);

void main()
{
    float Blurred = 0.0;

    for(int x = -2; x < 2; ++x)
    {
        for(int y = -2; y < 2; ++y)
        {
            vec2 offset = vec2(x, y) / ScreenSize; 
            Blurred += texture(TexSSAONoisy, (fTexCoord + offset)).r;
        }
    }

    Blurred = Blurred / (4.0 * 4.0);

    TexSSAOBlurred = Blurred;
}
