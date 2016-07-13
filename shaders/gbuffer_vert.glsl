#version 330 core

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;
in vec2 p3d_MultiTexCoord1;
in vec3 p3d_Tangent;
in vec3 p3d_Binormal;

//out vec3 fNormal;
out vec2 fTexCoord0;
out vec2 fTexCoord1;
out mat3 TangentMatrix;

uniform mat3 p3d_NormalMatrix;
// This is the upper 3x3 of the inverse transpose of the ModelViewMatrix.  It is used
// to transform the normal vector into view-space coordinates.
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    vec3 fNormal = normalize(p3d_NormalMatrix * p3d_Normal);
    vec3 fTangent = normalize(p3d_NormalMatrix * p3d_Tangent);
    vec3 fBinormal = normalize(p3d_NormalMatrix * p3d_Binormal);
    
    TangentMatrix = mat3(fTangent, fBinormal, fNormal);

    fTexCoord0 = p3d_MultiTexCoord0;
    fTexCoord1 = p3d_MultiTexCoord1;

    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
