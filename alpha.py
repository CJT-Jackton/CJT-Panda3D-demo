#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: Alpha Team
# Date: 2016/7/12
# Version: 0.1

# Alpha version.

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from src import *
import sys
import os
import math
import random

# 加载配置文件
loadPrcFile("config/config.prc")

class Game(ShowBase):
    # 窗口大小
    Win_Size_X = 0
    Win_Size_Y = 0

    # 纹理过滤质量
    # 1 - 双线性过滤
    # 2 - 三线性过滤
    # 3 - 各向异性过滤 2x
    # 4 - 各向异性过滤 4x
    # 5 - 各向异性过滤 8x
    # 6 - 各向异性过滤 16x
    Texture_Filter = 6

    # 阴影质量
    # 0 - 关闭
    # 1 - 低
    # 2 - 中
    # 3 - 高
    Shadow_Quality = 0
    Shadow_Map_Size = 1024

    # 环境光遮蔽
    # 0 - 关闭
    # 1 - SSAO
    # 2 - HBAO+ 3.0 //TODO
    Ambient_Occlusion = 0

    # 抗锯齿
    # 0 - 关闭
    # 1 - FXAA
    # 2 - SMAA 1x
    # 3 - SMAA T2x //TODO
    # 4 - SMAA 4x  //TODO
    Anti_Aliasing = 0

    # 鼠标灵敏度
    Mouse_Sensitivity = 100

    # 镜头移动速度
    Camera_Speed = 25

    def __init__(self):
        ShowBase.__init__(self)
        self.InitRenderPipeline()

        self.recenterMouse()

        self.taskMgr.add(self.updateCamera, "Update Camera")

    def InitRenderPipeline(self):
        self.InitCamera()
        self.InitGameVariable()
        self.InitMasks()
        self.InitShaders()
        self.InitBuffers()
        self.InitModels()
        self.InitLights()
        self.InitKeysBinding()

    def InitCamera(self):
        self.disableMouse()

        self.camera.setPos(-3.5, 1.5, 5)
        self.camera.setHpr(90, 0, 0)
        self.camLens.setNearFar(1.0, 500.0)
        self.camLens.setFov(90)

    def InitGameVariable(self):
        Game.Win_Size_X = self.win.getProperties().getXSize()
        Game.Win_Size_Y = self.win.getProperties().getYSize()

        if Game.Texture_Filter == 2:
            loadPrcFileData('', 'texture-minfilter linear-mipmap-linear')
        elif Game.Texture_Filter == 3:
            loadPrcFileData('', 'texture-anisotropic-degree 2')
        elif Game.Texture_Filter == 4:
            loadPrcFileData('', 'texture-anisotropic-degree 4')
        elif Game.Texture_Filter == 5:
            loadPrcFileData('', 'texture-anisotropic-degree 8')
        elif Game.Texture_Filter == 6:
            loadPrcFileData('', 'texture-anisotropic-degree 16')

        if Game.Shadow_Quality == 1:
            Game.Shadow_Map_Size = 512
        elif Game.Shadow_Quality == 2:
            Game.Shadow_Map_Size = 1024
        elif Game.Shadow_Quality == 3:
            Game.Shadow_Map_Size = 2048

    def InitMasks(self):
    # Camera masks
        self.mask = {
            # 全部不透明模型
            'model': 1,
            # 屏幕大小的四边形
            'quad': 2,
            # 光体积
            'light-volume': 4,
            # 天空盒
            'skybox': 8
        }

    def InitBuffers(self):
    # Initialize off screen buffers
        self.buffers = {}
        self.bufferTex = {}
        self.bufferCam = {}

        self.InitBufferGBuffer()
        if Game.Shadow_Quality != 0:
            self.InitBufferShadow()
        if Game.Ambient_Occlusion == 1:
            self.InitBufferSSAONoise()
            self.InitBufferSSAOBlur()
        #elif Game.Ambient_Occlusion == 2:
        self.InitBufferLight()
        self.InitBufferSkybox()
        self.InitBufferWin()

        self.buffers['skybox'].shareDepthBuffer(self.buffers['gBuffer'])

    def InitBufferGBuffer(self):
    # g-Buffer
        self.buffers['gBuffer'] = self.makeFBO("gBuffer", 2)
        self.buffers['gBuffer'].setSort(1)

        self.InitBufferGBufferTex()
        self.InitBufferGBufferCam()

        self.buffers['gBuffer'].addRenderTexture(self.bufferTex['DepthStencil'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepthStencil)
        self.buffers['gBuffer'].addRenderTexture(self.bufferTex['Diffuse'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        self.buffers['gBuffer'].addRenderTexture(self.bufferTex['Normal'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba0)
        self.buffers['gBuffer'].addRenderTexture(self.bufferTex['Specular'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba1)

        self.buffers['gBuffer'].disableClears()
        self.buffers['gBuffer'].setClearColorActive(1)
        self.buffers['gBuffer'].setClearDepthActive(1)
        self.buffers['gBuffer'].setClearActive(GraphicsOutput.RTPAuxRgba0, 1)
        self.buffers['gBuffer'].setClearActive(GraphicsOutput.RTPAuxRgba1, 1)
        self.buffers['gBuffer'].setClearColor(LVecBase4f(0.0, 0.0, 0.0, 1.0))

    def InitBufferGBufferTex(self):
        self.bufferTex['DepthStencil'] = Texture()
        self.bufferTex['DepthStencil'].setFormat(Texture.FDepthStencil)
        self.bufferTex['Diffuse'] = Texture()
        self.bufferTex['Normal'] = Texture()
        self.bufferTex['Specular'] = Texture()
        #self.bufferTex['Irradiance'] = Texture()

    def InitBufferGBufferCam(self):
        self.bufferCam['gBuffer'] = self.makeCamera(
            self.buffers['gBuffer'], lens = self.camLens, scene = self.render, mask = self.mask['model'])

        self.bufferCam['gBuffer'].node().getDisplayRegion(0).disableClears()

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['gBuffer'])
        self.bufferCam['gBuffer'].node().setInitialState(tmpnode.getState())

    def InitBufferShadow(self):
    # Shadow buffer
        self.buffers['shadow'] = self.makeShadowFBO("Shadow Buffer", Game.Shadow_Map_Size)
        self.buffers['shadow'].setSort(2)

        self.InitBufferShadowTex()
        self.InitBufferShadowCam()

        self.buffers['shadow'].addRenderTexture(self.bufferTex['Shadow'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)

        self.buffers['shadow'].setClearDepthActive(1)

    def InitBufferShadowTex(self):
        self.bufferTex['Shadow'] = Texture()
        self.bufferTex['Shadow'].setFormat(Texture.FDepthComponent16)
        self.bufferTex['Shadow'].setMagfilter(Texture.FTNearest)  # FTShadow
        self.bufferTex['Shadow'].setMinfilter(Texture.FTNearest)  # FTShadow
        self.bufferTex['Shadow'].setWrapU(Texture.WMBorderColor)
        self.bufferTex['Shadow'].setWrapV(Texture.WMBorderColor)
        self.bufferTex['Shadow'].setBorderColor(LVecBase4f(1.0, 1.0, 1.0, 1.0))

    def InitBufferShadowCam(self):
        orthoLen = OrthographicLens()
        orthoLen.setFilmSize(150, 150)
        self.bufferCam['shadow'] = NodePath(Camera("shadowCam"))
        self.bufferCam['shadow'].node().setLens(orthoLen)
        self.bufferCam['shadow'].node().setScene(self.render)
        self.bufferCam['shadow'].node().setCameraMask(self.mask['model'])
        self.camList.append(self.bufferCam['shadow'])
        dr = self.buffers['shadow'].makeDisplayRegion((0, 1, 0, 1))
        dr.setSort(0)
        dr.setClearDepthActive(1)
        dr.setCamera(self.bufferCam['shadow'])

        self.bufferCam['shadow'].setPos(0, 0, 0)
        self.bufferCam['shadow'].lookAt(-1, -0.75, -4.52)
        self.bufferCam['shadow'].node().getLens().setNearFar(-90, 20)

        self.bufferCam['shadow'].node().getDisplayRegion(0).disableClears()

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['shadow_mapping'])
        self.bufferCam['shadow'].node().setInitialState(tmpnode.getState())

    def InitBufferSSAONoise(self):
    # SSAO Noise pass buffer
        self.buffers['SSAONoise'] = self.makeFBO("SSAO Noise Buffer", 0)
        self.buffers['SSAONoise'].setSort(3)

        self.InitBufferSSAONoiseTex()
        self.InitBufferSSAONoiseCam()

        self.buffers['SSAONoise'].addRenderTexture(self.bufferTex['SSAONoisy'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.buffers['SSAONoise'].setClearColorActive(1)
        self.buffers['SSAONoise'].setClearColor(LVecBase4f(1.0, 1.0, 1.0, 1.0))

    def InitBufferSSAONoiseTex(self):
        self.bufferTex['SSAONoisy'] = Texture()
        self.bufferTex['SSAONoisy'].setFormat(Texture.FRed)

        # 生成一个4x4的随机噪声贴图
        noise = PNMImage(4, 4)
        for i in range(4):
            for j in range(4):
                noise.setXel(i, j, LVecBase3f(random.random() * 2 - 1, random.random() * 2 - 1, 0.0))

        self.bufferTex['SSAOnoise'] = Texture()
        self.bufferTex['SSAOnoise'].load(noise)
        self.bufferTex['SSAOnoise'].setFormat(Texture.FRgb16)
        self.bufferTex['SSAOnoise'].setMagfilter(Texture.FTNearest)
        self.bufferTex['SSAOnoise'].setMinfilter(Texture.FTNearest)
        self.bufferTex['SSAOnoise'].setWrapU(Texture.WMRepeat)
        self.bufferTex['SSAOnoise'].setWrapV(Texture.WMRepeat)

    def InitBufferSSAONoiseCam(self):
        self.bufferCam['SSAONoise'] = self.makeCamera(
            self.buffers['SSAONoise'], lens = self.camLens, scene = self.render, mask = self.mask['quad'])

        self.bufferCam['SSAONoise'].node().getDisplayRegion(0).disableClears()

        SSAOsamples = PTA_LVecBase4f()
        for i in range(64):
            # sample = LVecBase3f(random.random() * 2 - 1, random.random() * 2 - 1, random.random())
            sample = LVecBase3f(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(0.0, 1.0))
            sample_length = math.sqrt(sample.x * sample.x + sample.y * sample.y + sample.z * sample.z)
            sample /= sample_length
            sample *= random.random()
            sample = sample * 0.5 + 0.5
            scale = float(i) / 64.0
            scale = 0.1 + 0.9 * (scale * scale)
            sample *= scale
            SSAOsamples.push_back(UnalignedLVecBase4f(sample.x, sample.y, sample.z, 0.0))

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['SSAONoise'])
        tmpnode.setShaderInput("texScaleNoise", LVecBase2f(Game.Win_Size_X / 4.0, Game.Win_Size_Y / 4.0))
        tmpnode.setShaderInput("TexDepthStencil", self.bufferTex['DepthStencil'])
        tmpnode.setShaderInput("TexNormal", self.bufferTex['Normal'])
        tmpnode.setShaderInput("TexNoise", self.bufferTex['SSAOnoise'])
        tmpnode.setShaderInput("NEAR", self.camLens.getNear())
        tmpnode.setShaderInput("FAR", self.camLens.getFar())
        tmpnode.setShaderInput("samples", SSAOsamples)
        self.bufferCam['SSAONoise'].node().setInitialState(tmpnode.getState())

    def InitBufferSSAOBlur(self):
    # SSAO blur pass buffer
        self.buffers['SSAOBlur'] = self.makeFBO("SSAO Blur Buffer", 0)
        self.buffers['SSAOBlur'].setSort(4)

        self.InitBufferSSAOBlurTex()
        self.InitBufferSSAOBlurCam()

        self.buffers['SSAOBlur'].addRenderTexture(self.bufferTex['SSAOBlur'],
                GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.buffers['SSAOBlur'].setClearColorActive(1)
        self.buffers['SSAOBlur'].setClearColor(LVecBase4f(1.0, 1.0, 1.0, 1.0))

    def InitBufferSSAOBlurTex(self):
        self.bufferTex['SSAOBlur'] = Texture()
        self.bufferTex['SSAOBlur'].setFormat(Texture.FRed)

    def InitBufferSSAOBlurCam(self):
        self.bufferCam['SSAOBlur'] = self.makeCamera(
            self.buffers['SSAOBlur'], lens = self.camLens, scene = self.render, mask = self.mask['quad'])

        self.bufferCam['SSAOBlur'].node().getDisplayRegion(0).disableClears()

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['SSAOBlur'])
        tmpnode.setShaderInput("TexSSAONoisy", self.bufferTex['SSAONoisy'])
        tmpnode.setShaderInput("ScreenSize", LVecBase2i(Game.Win_Size_X, Game.Win_Size_X))
        self.bufferCam['SSAOBlur'].node().setInitialState(tmpnode.getState())

    def InitBufferLight(self):
    # Lighting calculation buffer
        self.buffers['light'] = self.makeFBO("Light Buffer", 0)
        self.buffers['light'].setSort(5)

        self.InitBufferLightTex()
        self.InitBufferLightCam()

        self.buffers['light'].addRenderTexture(self.bufferTex['Light'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.buffers['light'].setClearColorActive(1)
        self.buffers['light'].setClearColor(LVecBase4f(0.0, 0.0, 0.0, 1.0))

    def InitBufferLightTex(self):
        self.bufferTex['Light'] = Texture()

    def InitBufferLightCam(self):
        self.bufferCam['light_AD'] = self.makeCamera(
            self.buffers['light'], lens = self.camLens, scene = self.render, mask = self.mask['quad'])
        self.bufferCam['light_PS'] = self.makeCamera(
            self.buffers['light'], lens = self.camLens, scene = self.render, mask = self.mask['light-volume'])

        self.bufferCam['light_AD'].node().getDisplayRegion(0).setSort(1)
        self.bufferCam['light_PS'].node().getDisplayRegion(0).setSort(2)
        self.bufferCam['light_AD'].node().getDisplayRegion(0).disableClears()
        self.bufferCam['light_PS'].node().getDisplayRegion(0).disableClears()

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShaderInput("TexDepthStencil", self.bufferTex['DepthStencil'])
        tmpnode.setShaderInput("TexDiffuse", self.bufferTex['Diffuse'])
        tmpnode.setShaderInput("TexNormal", self.bufferTex['Normal'])
        tmpnode.setShaderInput("TexSpecular", self.bufferTex['Specular'])
        if Game.Shadow_Quality != 0:
            tmpnode.setShaderInput("light", self.bufferCam['shadow'])
        tmpnode.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
        tmpnode.setAttrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))
        self.bufferCam['light_AD'].node().setInitialState(tmpnode.getState())

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShaderInput("TexDepthStencil", self.bufferTex['DepthStencil'])
        tmpnode.setShaderInput("TexDiffuse", self.bufferTex['Diffuse'])
        tmpnode.setShaderInput("TexNormal", self.bufferTex['Normal'])
        tmpnode.setShaderInput("TexSpecular", self.bufferTex['Specular'])
        tmpnode.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
        tmpnode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
        tmpnode.setAttrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))
        self.bufferCam['light_PS'].node().setInitialState(tmpnode.getState())

    def InitBufferSkybox(self):
        self.buffers['skybox'] = self.makeFBO("skybox", 0)
        self.buffers['skybox'].setSort(6)

        self.InitBufferSkyboxTex()
        self.InitBufferSkyboxCam()

        self.buffers['skybox'].addRenderTexture(self.bufferTex['Skybox'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.buffers['skybox'].setClearColorActive(1)
        self.buffers['skybox'].setClearColor(LVecBase4f(0.0, 0.0, 0.0, 1.0))

    def InitBufferSkyboxTex(self):
        self.bufferTex['Skybox'] = Texture()

        self.skyTex = self.loader.loadCubeMap("textures/skybox/Highnoon_#.jpg")

    def InitBufferSkyboxCam(self):
        self.bufferCam['skybox'] = self.makeCamera(
            self.buffers['skybox'], lens = self.camLens, scene = self.render, mask = self.mask['skybox'])

        self.bufferCam['skybox'].node().getDisplayRegion(0).disableClears()

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['skybox'])
        tmpnode.setShaderInput("TexSkybox", self.skyTex)
        tmpnode.setAttrib(DepthTestAttrib.make(RenderAttrib.MLessEqual))
        self.bufferCam['skybox'].node().setInitialState(tmpnode.getState())

    def InitBufferWin(self):
        self.win.setSort(7)

        self.InitBufferWinCam()

        self.win.disableClears()
        self.win.setClearColor(LVecBase4f(0.0, 0.0, 0.0, 1.0))

    def InitBufferWinCam(self):
        self.cam.node().setActive(0)
        self.cam.node().getDisplayRegion(0).disableClears()
        self.cam2d.node().getDisplayRegion(0).disableClears()

        self.render.setState(RenderState.makeEmpty())

    def InitShaders(self):
    # Initialize shaders
        self.shaders = {}

        self.shaders['gBuffer'] = Shader.load(
            Shader.SLGLSL, "shaders/gbuffer_vert.glsl", "shaders/gbuffer_frag.glsl")

        self.shaders['ambient_light'] = Shader.load(
            Shader.SLGLSL, "shaders/ambient_light_vert.glsl", "shaders/ambient_light_frag.glsl")
        self.shaders['directional_light'] = Shader.load(
            Shader.SLGLSL, "shaders/directional_light_vert.glsl", "shaders/directional_light_frag.glsl")
        self.shaders['point_light'] = Shader.load(
            Shader.SLGLSL, "shaders/point_light_vert.glsl", "shaders/point_light_frag.glsl")
        self.shaders['spotlight'] = Shader.load(
            Shader.SLGLSL, "shaders/spotlight_vert.glsl", "shaders/spotlight_frag.glsl")

        if Game.Shadow_Quality != 0:
            self.shaders['directional_light'] = Shader.load(
                Shader.SLGLSL, "shaders/directional_light_vert.glsl", "shaders/directional_light_shadow_frag.glsl")
            self.shaders['shadow_mapping'] = Shader.load(
                Shader.SLGLSL, "shaders/shadow_mapping_vert.glsl", "shaders/shadow_mapping_frag.glsl")

        if Game.Ambient_Occlusion != 0:
            if Game.Ambient_Occlusion == 1:
            # SSAO
                self.shaders['ambient_light'] = Shader.load(
                    Shader.SLGLSL, "shaders/ambient_light_vert.glsl", "shaders/ambient_light_ao_frag.glsl")
                self.shaders['SSAONoise'] = Shader.load(
                    Shader.SLGLSL, "shaders/ssao_noise_vert.glsl", "shaders/ssao_noise_frag.glsl")
                self.shaders['SSAOBlur'] = Shader.load(
                    Shader.SLGLSL, "shaders/ssao_blur_vert.glsl", "shaders/ssao_blur_frag.glsl")
            #elif Game.Ambient_Occlusion == 2:
            # HBAO+

        self.shaders['skybox'] = Shader.load(
            Shader.SLGLSL, "shaders/skybox_vert.glsl", "shaders/skybox_frag.glsl")

        self.shaders['tone_mapping'] = Shader.load(
            Shader.SLGLSL, "shaders/tone_mapping_vert.glsl", "shaders/tone_mapping_frag.glsl")

        if Game.Anti_Aliasing != 0:
            if Game.Anti_Aliasing == 1:
                # FXAA
                self.shaders['FXAA'] = Shader.load(
                    Shader.SLGLSL, "shaders/fxaa_vert.glsl", "shaders/fxaa_frag.glsl")
            elif Game.Anti_Aliasing == 2:
                # SMAA 1x
                self.shaders['SMAAEdge'] = Shader.load(
                    Shader.SLGLSL, "shaders/smaa_edge_vert.glsl", "shaders/smaa_edge_frag.glsl")
                self.shaders['SMAABlend'] = Shader.load(
                    Shader.SLGLSL, "shaders/smaa_blend_vert.glsl", "shaders/smaa_blend_frag.glsl")
                self.shaders['SMAANeighborhood'] = Shader.load(
                    Shader.SLGLSL, "shaders/smaa_neighborhood_vert.glsl", "shaders/smaa_neighborhood_frag.glsl")

    def InitLights(self):
    # 初始化光源
        self.ambientLight = IWAmbientLight("ambientLight", self.quad)
        self.ambientLight.light.setColor(LVecBase4f(0.37, 0.37, 0.43, 1.0))
        self.ambientLight.NodePath.setShader(self.shaders['ambient_light'])
        self.ambientLight.initShaderInput()
        if Game.Ambient_Occlusion != 0:
            self.ambientLight.NodePath.setShaderInput("TexAO", self.bufferTex['SSAOBlur'])
        self.ambientLight.NodePath.reparentTo(self.quadRoot)

        self.sunLight = IWDirectionalLight("sunLight", self.quad)
        self.sunLight.light.setColor(LVecBase4f(1.0, 1.0, 0.85, 1.0))
        self.sunLight.light.setDirection(LVecBase3f(-1, -1, -0.52))
        self.sunLight.NodePath.setShader(self.shaders['directional_light'])
        self.sunLight.initShaderInput()
        if Game.Shadow_Quality != 0:
            self.sunLight.NodePath.setShaderInput("light", self.bufferCam['shadow'])
            self.sunLight.NodePath.setShaderInput("DirectionalLight.shadowMap", self.bufferTex['Shadow'])
            self.sunLight.NodePath.setShaderInput("shadowMapScale", LVecBase2f(1.0 / Game.Shadow_Map_Size))
        self.sunLight.NodePath.reparentTo(self.quadRoot)

        self.pointLight = IWPointLight("pointLight", self.sphere)
        self.pointLight.light.setColor(LVecBase4f(5.0, 5.0, 1.2, 1.0))
        self.pointLight.light.setSpecularColor(LVecBase4f(5.0, 5.0, 2.5, 1.0))
        self.pointLight.NodePath.setPos(LVecBase3f(15, 0, 1))
        self.pointLight.light.setAttenuation(LVecBase3f(1.0, 0.7, 1.8))
        self.pointLight.NodePath.setShader(self.shaders['point_light'])
        self.pointLight.initShaderInput()
        self.pointLight.calScale()
        self.pointLight.NodePath.reparentTo(self.lightVolumeRoot)

    def InitModels(self):
        # 初始化模型根节点
        self.InitModelRoots()
        # 加载杂项模型
        self.InitModelMisc()

        # 将最后的结果显示在一个屏幕大小的四边形上
        self.finalQuad = self.render2d.attachNewNode(PandaNode("finalQuad"))
        self.quad.instanceTo(self.finalQuad)
        self.finalQuad.setTexture(self.bufferTex['Light'])

        self.sponza = self.loader.loadModel("models/sponza/sponza.bam")
        self.sponza.reparentTo(self.modelRoot)
        self.sponza.setScale(0.1, 0.1, 0.1)

    def InitModelRoots(self):
        # 全部不透明模型的根节点
        self.modelRoot = NodePath(PandaNode("model root"))
        self.modelRoot.reparentTo(self.render)
        self.modelRoot.hide(BitMask32.allOn())
        self.modelRoot.show(BitMask32(self.mask['model']))

        # 全部满屏幕四边形的根节点
        self.quadRoot = NodePath(PandaNode("quad root"))
        self.quadRoot.reparentTo(self.camera)
        self.quadRoot.hide(BitMask32.allOn())
        self.quadRoot.show(BitMask32(self.mask['quad']))

        # 全部有体积的光源（点光源/聚光灯）的根节点
        self.lightVolumeRoot = NodePath(PandaNode("light root"))
        self.lightVolumeRoot.reparentTo(self.render)
        self.lightVolumeRoot.hide(BitMask32.allOn())
        self.lightVolumeRoot.show(BitMask32(self.mask['light-volume']))

    def InitModelMisc(self):
        # 屏幕大小四边形
        self.quad = self.makeQuad()
        self.quad.reparentTo(self.quadRoot)

        # 球体（点光源）
        self.sphere = self.loader.loadModel("models/misc/sphere")

        # 光椎（聚光灯）
        self.cone = self.loader.loadModel("models/misc/cone")

        # 天空盒
        self.skybox = self.loader.loadModel("models/misc/skybox")
        self.skybox.reparentTo(self.camera)
        self.skybox.hide(BitMask32.allOn())
        self.skybox.show(BitMask32(self.mask['skybox']))

    def InitKeysBinding(self):
        self.keys = {}

        for key in ['w', 'a', 's', 'd']:
            self.keys[key] = 0
            self.accept(key, self.push_key, [key, 1])
            self.accept('%s-up' % key, self.push_key, [key, 0])

        # Debug
        self.accept('1', self.set_card, [self.bufferTex['Skybox']])
        self.accept('2', self.set_card, [self.bufferTex['Diffuse']])
        self.accept('3', self.set_card, [self.bufferTex['Normal']])
        self.accept('4', self.set_card, [self.bufferTex['Specular']])
        if Game.Shadow_Quality != 0:
            self.accept('4', self.set_card, [self.bufferTex['Shadow']])
        self.accept('5', self.set_card, [self.bufferTex['Light']])

        self.accept('escape', __import__('sys').exit, [0])

    def makeQuad(self):
    # Make a full screen quad.
        vdata = GeomVertexData("vdata", GeomVertexFormat.getV3t2(),Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        texcoord = GeomVertexWriter(vdata, 'texcoord')

        # vertex.addData3f(-1, 0, 1)
        # texcoord.addData2f(0, 1)
        vertex.addData3f(-1, 0, 3)
        texcoord.addData2f(0, 2)

        # vertex.addData3f(-1, 0, -1)
        # texcoord.addData2f(0, 0)
        vertex.addData3f(-1, 0, -1)
        texcoord.addData2f(0, 0)

        # vertex.addData3f(1, 0, -1)
        # texcoord.addData2f(1, 0)
        vertex.addData3f(3, 0, -1)
        texcoord.addData2f(2, 0)

        # vertex.addData3f(1, 0, 1)
        # texcoord.addData2f(1, 1)

        prim = GeomTriangles(Geom.UHStatic)

        prim.addVertices(0, 1, 2)
        # prim.addVertices(0, 2, 3)

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        node = GeomNode('quad')
        node.addGeom(geom)

        return NodePath(node)

    def makeFBO(self, name, auxrgba, rgbabit = 8):
    	winprops = WindowProperties()
    	props = FrameBufferProperties()
    	props.setRgbColor(True)
    	props.setRgbaBits(rgbabit, rgbabit, rgbabit, rgbabit)
    	props.setDepthBits(1)
    	props.setAuxRgba(auxrgba)
        return self.graphicsEngine.makeOutput(
        	self.pipe, name, -2, props, winprops,
        	GraphicsPipe.BFSizeTrackHost | GraphicsPipe.BFCanBindEvery |
        	GraphicsPipe.BFRttCumulative | GraphicsPipe.BFRefuseWindow,
        	self.win.getGsg(), self.win)

    def makeShadowFBO(self, name, size):
        winprops = WindowProperties.size(size, size)
        props = FrameBufferProperties()
        props.setRgbColor(True)
        props.setDepthBits(1)
        return self.graphicsEngine.makeOutput(
            self.pipe, name, -2, props, winprops,
            GraphicsPipe.BFRefuseWindow,
            self.win.getGsg(), self.win)

    def updateCamera(self, task):
        deltaTime = globalClock.getDt()  # To get the time (in seconds) since the last frame was drawn

        X = deltaTime * Game.Camera_Speed * (self.keys['a'] - self.keys['d'])
        Y = deltaTime * Game.Camera_Speed * (self.keys['w'] - self.keys['s'])

        self.camera.setPos(self.camera, -X, Y, 0)

        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()  # get the mouse position

            self.recenterMouse()

            newHpr = self.camera.getHpr() + (mpos.getX() * -Game.Mouse_Sensitivity, mpos.getY() * Game.Mouse_Sensitivity, 0.0)

            if newHpr.y > 90.0:
            	newHpr.y = 90.0
            elif newHpr.y < -90.0:
            	newHpr.y = -90.0

            self.camera.setHpr(newHpr)

        return Task.cont

    def push_key(self, key, value):
    	self.keys[key] = value

    def set_card(self, tex):
    	self.finalQuad.setTexture(tex)

    def recenterMouse(self):
        self.win.movePointer(0,
              int(Game.Win_Size_X / 2),
              int(Game.Win_Size_Y / 2))

game = Game()
game.run()
