#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 TexSSAOBlurred;

uniform vec2 texScale;

uniform sampler2D TexSSAONoisy;

const vec2 ScreenSize = vec2(1280.0, 720.0);

void main()
{
    float Blurred = 0.0;

    for(int x = -2; x < 2; ++x)
    {
        for(int y = -2; y < 2; ++y)
        {
            vec2 offset = vec2(x, y) / ScreenSize; 
            Blurred += texture(TexSSAONoisy, (fTexCoord + offset) * texScale).r;
        }
    }

    Blurred = Blurred / (4.0 * 4.0);

    TexSSAOBlurred = vec4(Blurred, Blurred, Blurred, 1.0);
}
