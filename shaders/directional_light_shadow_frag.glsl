#version 330 core

in vec2 fTexCoord;

layout (location = 0) out vec4 fColor;

uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ViewMatrixInverse;
uniform mat4 p3d_ProjectionMatrixInverse;

uniform mat4 trans_world_to_clip_of_light;

uniform sampler2D TexDepthStencil;
uniform sampler2D TexDiffuse;
uniform sampler2D TexNormal;
//uniform sampler2D TexSpecular;
//uniform sampler2D TexIrradiance;

uniform struct p3d_LightSourceParameters{
    vec4 color;
    vec4 specular;
    vec4 position;
    // Shadow map for this light source
    //sampler2DShadow shadowMap;
    sampler2D shadowMap;
} DirectionalLight;

uniform vec2 shadowMapScale = vec2(1.0 / 1024.0, 1.0 / 1024.0);
//uniform float GaussCoef[25];

void main()
{
    vec4 albedo = texture(TexDiffuse, fTexCoord);
    vec3 normal = (texture(TexNormal, fTexCoord).rbg - 0.5) * 2;

    vec3 direction_world = DirectionalLight.position.xyz;

    vec3 direction = normalize(mat3(p3d_ViewMatrix) * direction_world);

    float fDepth = texture(TexDepthStencil, fTexCoord).a;
    vec4 tmp = p3d_ProjectionMatrixInverse * vec4((fTexCoord.x * 2 - 1.0), (fTexCoord.y * 2 - 1.0), (fDepth * 2 - 1.0), 1.0);
    vec3 fPos_view = tmp.xyz / tmp.w;
    vec4 fPos_world = p3d_ViewMatrixInverse * vec4(fPos_view, 1.0);
    //vec4 tmp2 = DirectionalLight.shadowMatrix * fPos_world;
    //vec3 fPos_light = tmp2.xyz / tmp2.w;
    //fPos_light = fPos_light * 0.5 + 0.5;

    vec4 fPos_light = trans_world_to_clip_of_light * fPos_world;
    fPos_light.xyz = fPos_light.xyz * 0.5 + 0.5;

    float fDepth_light = texture(DirectionalLight.shadowMap, fPos_light.xy).r;
    float bias = 0.006;
    //float bias = max(0.005 * (1.0 - dot(normal, -direction)), 0.0005);
    float shadow = fPos_light.z < fDepth_light + bias? 1.0 : 0.0;
    //shadow = fPos_light.z > 1.0 ? 0.0 : shadow;
    /*float shadow = 0.0;

    for(int x = -2; x <= 2; ++x)
    {
    	for(int y = -2; y <= 2; ++y)
    	{
    		float fDepth_light = texture(DirectionalLight.shadowMap, fPos_light.xy + vec2(x, y) * shadowMapScale).r;
            //shadow += (fPos_light.z < fDepth_light + bias)? 1.0 : 0.0;
            shadow += (fPos_light.z < fDepth_light + bias)? GaussCoef[(x + 2) * 5 + y + 2] : 0.0;
    	}
    }

    shadow /= 273.0;*/
    //float shadow = 1.0;

    vec4 diffuse = DirectionalLight.color * max(dot(-direction, normal), 0.0);
    vec4 color = albedo * diffuse * shadow;

    fColor = color;
}
