#version 330 core

in vec3 fTexCoord;

out vec4 fColor;

uniform samplerCube skybox;

void main()
{
    fColor = texture(skybox, fTexCoord);
}