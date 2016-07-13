#version 330 core

//in vec3 fNormal;
in vec2 fTexCoord0;
in vec2 fTexCoord1;
in vec4 fPos_view;
in mat3 TangentMatrix;

layout (location = 0) out vec4 TexDiffuse;
layout (location = 1) out vec4 TexNormal;
layout (location = 2) out vec4 TexSpecular;
//layout (location = 3) out vec4 TexIrradiance;
//layout (location = 4) out vec4 TexDepthStencil;

uniform sampler2D p3d_Texture0; // Diffuse texture
uniform sampler2D p3d_Texture1; // Normal mapping
uniform sampler2D p3d_Texture2; // Specular texture

uniform mat3 p3d_ViewMatrix;

void main()
{
    TexDiffuse = texture(p3d_Texture0, fTexCoord0);

    //vec3 fNormal = vec3(0.0, 0.0, 1.0);
    //vec3 fNormal = TangentMatrix * normalize(texture(p3d_Texture1, fTexCoord1).rbg);
    vec3 fNormal = texture(p3d_Texture1, fTexCoord1).rgb * 2.0 - 1.0;
    fNormal = (fNormal == vec3(0.0, 0.0, 0.0))? vec3(0.0, 0.0, 1.0): fNormal;
    //TexNormal.rgb = normalize(fNormal) * 0.5 + 0.5;
    TexNormal.rbg = (TangentMatrix * normalize(fNormal)) * 0.5 + 0.5;
    TexNormal.a = 1.0;

    TexSpecular.rgb = texture(p3d_Texture2, fTexCoord0).rgb;
    TexSpecular.a = 1.0;
}
