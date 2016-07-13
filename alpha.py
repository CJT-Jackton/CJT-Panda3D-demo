#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: Alpha Team
# Date: 2016/7/12
# Version: 0.1

# Alpha version.

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
import sys
import os
import math

# 加载配置文件
loadPrcFile("config/config.prc")

class MyAmbientLight(PandaNode):
# 自定义环境光光源
    def __init__(self, name, quad):
        PandaNode.__init__(self, name)
        self.NodePath = NodePath(self)
        self.light_NP = self.NodePath.attachNewNode(AmbientLight("ambientLight"))
        self.light = self.light_NP.node()
        self.NodePath.hide(BitMask32.allOn())
        self.NodePath.show(BitMask32(Game.Mask['quad']))
        quad.instanceTo(self.light_NP)

    def initShaderInput(self):
    # 设置 shader 中的参数
        self.NodePath.setShaderInput("AmbientLight.color", self.light.getColor())

class MyDirectionalLight(PandaNode):
# 自定义平行光光源
    def __init__(self, name, quad):
        PandaNode.__init__(self, name)
        self.NodePath = NodePath(self)
        self.light_NP = self.NodePath.attachNewNode(DirectionalLight("directionalLight"))
        self.light = self.light_NP.node()
        self.NodePath.hide(BitMask32.allOn())
        self.NodePath.show(BitMask32(Game.Mask['quad']))
        quad.instanceTo(self.light_NP)

    def initShaderInput(self):
    # 设置 shader 中的参数
        self.NodePath.setShaderInput("DirectionalLight.color", self.light.getColor())
        self.NodePath.setShaderInput("DirectionalLight.specular", self.light.getSpecularColor())
        self.NodePath.setShaderInput("DirectionalLight.position", self.light.getDirection())

class MyPointLight(PandaNode):
# 自定义点光源
    def __init__(self, name, sphere):
        PandaNode.__init__(self, name)
        self.NodePath = NodePath(self)
        self.light_NP = self.NodePath.attachNewNode(PointLight("point light"))
        self.light = self.light_NP.node()
        self.NodePath.hide(BitMask32.allOn())
        self.NodePath.show(BitMask32(Game.Mask['light-volume']))
        sphere.instanceTo(self.light_NP)

    def initShaderInput(self):
    # 设置 shader 中的参数
        self.NodePath.setShaderInput("PointLight.color", self.light.getColor())
        self.NodePath.setShaderInput("PointLight.specular", self.light.getSpecularColor())
        self.NodePath.setShaderInput("PointLight.position", LVecBase4f(self.NodePath.getPos(), 1.0))
        self.NodePath.setShaderInput("PointLight.attenuation", self.light.getAttenuation())

    def calScale(self):
    # 根据光源衰减计算光实际体积大小
        color = self.light.getColor()
        intensity = max(color.x, color.y, color.z)

        attenuation = self.light.getAttenuation()
        constant = attenuation.x
        linear = attenuation.y
        quadratic = attenuation.z

        radius = (-linear + math.sqrt(linear * linear - 4 * quadratic * (constant - (256.0 / 5.0) * intensity))) \
                 / (2 * quadratic)
        self.light_NP.setScale(radius, radius, radius)

class MySpotlight(PandaNode):
# 自定义聚光灯
    def __init__(self, name, cone):
        PandaNode.__init__(self, name)
        self.NodePath = NodePath(self)
        self.light_NP = self.NodePath.attachNewNode(Spotlight("spotlight"))
        self.light = self.light_NP.node()
        self.NodePath.hide(BitMask32.allOn())
        self.NodePath.show(BitMask32(Game.Mask['light-volume']))
        cone.instanceTo(self.light_NP)

    def initShaderInput(self):
    # 设置 shader 中的参数
        self.NodePath.setShaderInput("Spotlight.color", self.light.getColor())
        self.NodePath.setShaderInput("Spotlight.specular", self.light.getSpecularColor())
        self.NodePath.setShaderInput("Spotlight.position", LVecBase4f(self.NodePath.getPos(), 1.0))
        self.NodePath.setShaderInput("Spotlight.spotDirection", )
        self.NodePath.setShaderInput("Spotlight.spotCosCutoff", self.cosCutOff)
        self.NodePath.setShaderInput("Spotlight.attenuation", self.light.getAttenuation())

    def calRadius(self):
    # 根据光源衰减计算光实际半径大小
        color = self.light.getColor()
        intensity = max(color.x, color.y, color.z)

        attenuation = self.light.getAttenuation()
        constant = attenuation.x
        linear = attenuation.y
        quadratic = attenuation.z

        radius = (-linear + math.sqrt(linear * linear - 4 * quadratic * (constant - (256.0 / 5.0) * intensity))) \
                 / (2 * quadratic)
        return radius

    def calScale(self):
    # 根据光源衰减计算光实际体积大小
        FOV = self.light.getLens().getFov().x
        FOV_rad = FOV * math.pi / 360
        self.cosCutOff = math.cos(FOV_rad)
        radius = self.calRadius()

        scale_x = radius * 2 * math.sin(FOV_rad) / math.sqrt(3)
        scale_z = radius * 2 * math.cos(FOV_rad)
        scale_y = scale_x
        self.light_NP.setScale(scale_x, scale_y, scale_z)

# The game
class Game(ShowBase):
    # 窗口大小
    Win_Size_X = 0
    Win_Size_Y = 0

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

    # Camera masks
    Mask = {
        # 全部不透明模型
        'model': 1,
        # 屏幕大小的四边形
        'quad': 2,
        # 光体积
        'light-volume': 4,
        # 天空盒
        'skybox': 8
    }

    def __init__(self):
        ShowBase.__init__(self)
        self.win.setClearColor(LVecBase4f(0.0, 0.0, 0.0, 1.0))
        self.InitCamera()
        self.InitGameVar()

        #self.camera.setPos(-3.5, 1.5, 5)
        #self.camera.setHpr(90, 0, 0)

        #self.disableMouse()
        self.recenterMouse()

        self.InitShaders()

        # Setup buffers
        self.gBuffer = self.makeFBO("G-Buffer", 2)
        self.lightBuffer = self.makeFBO("Light Buffer", 0)

        self.gBuffer.setSort(1)
        self.lightBuffer.setSort(2)
        self.win.setSort(3)

        # G-Buffer render texture
        self.tex = {}
        self.tex['DepthStencil'] = Texture()
        self.tex['DepthStencil'].setFormat(Texture.FDepthStencil)
        self.tex['Diffuse'] = Texture()
        self.tex['Normal'] = Texture()
        self.tex['Specular'] = Texture()
        #self.tex['Irradiance'] = Texture()
        self.tex['Final'] = Texture()

        self.texScale = LVecBase2f(1.0, 1.0)
        self.tranSStoVS = self.calTranSStoVS()

        self.gBuffer.addRenderTexture(self.tex['DepthStencil'],
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepthStencil)
        self.gBuffer.addRenderTexture(self.tex['Diffuse'],
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        self.gBuffer.addRenderTexture(self.tex['Normal'],
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba0)
        self.gBuffer.addRenderTexture(self.tex['Specular'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba1)

        self.lightBuffer.addRenderTexture(self.tex['Final'],
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        #self.cam.node().getLens().setNear(1.0)
        #self.cam.node().getLens().setFar(500.0)
        #self.cam.node().getLens().setFov(90)
        #self.camLens.setNearFar(1.0, 500.0)
        #self.camLens.setFov(90)
        lens = self.cam.node().getLens()

        self.modelMask = 1
        self.adLightMask = 2
        self.psLightMask = 4

        self.gBufferCam = self.makeCamera(self.gBuffer, lens = lens, scene = render, mask = self.modelMask)
        self.adLightCam = self.makeCamera(self.lightBuffer, lens = lens, scene = render, mask = self.adLightMask)
        self.psLightCam = self.makeCamera(self.lightBuffer, lens = lens, scene = render, mask = self.psLightMask)

        self.cam.node().setActive(0)

        self.adLightCam.node().getDisplayRegion(0).setSort(1)
        self.psLightCam.node().getDisplayRegion(0).setSort(2)

        self.gBufferCam.node().getDisplayRegion(0).disableClears()
        self.adLightCam.node().getDisplayRegion(0).disableClears()
        self.psLightCam.node().getDisplayRegion(0).disableClears()
        self.cam.node().getDisplayRegion(0).disableClears()
        self.cam2d.node().getDisplayRegion(0).disableClears()
        self.gBuffer.disableClears()
        self.win.disableClears()

        self.gBuffer.setClearColorActive(1)
        self.gBuffer.setClearDepthActive(1)
        self.gBuffer.setClearActive(GraphicsOutput.RTPAuxRgba0, 1)
        self.gBuffer.setClearActive(GraphicsOutput.RTPAuxRgba1, 1)
        self.gBuffer.setClearColor((0.0, 0.0, 0.0, 1.0))
        self.lightBuffer.setClearColorActive(1)
        self.lightBuffer.setClearColor((0.0, 0.0, 0.0, 1.0))

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['gBuffer'])
        self.gBufferCam.node().setInitialState(tmpnode.getState())

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShaderInput("texScale", self.texScale)
        tmpnode.setShaderInput("TexDepthStencil", self.tex['DepthStencil'])
        tmpnode.setShaderInput("TexDiffuse", self.tex['Diffuse'])
        tmpnode.setShaderInput("TexNormal", self.tex['Normal'])
        tmpnode.setShaderInput("TexSpecular", self.tex['Specular'])
        tmpnode.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
        tmpnode.setAttrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))
        self.adLightCam.node().setInitialState(tmpnode.getState())

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShaderInput("texScale", self.texScale)
        tmpnode.setShaderInput("TexDepthStencil", self.tex['DepthStencil'])
        tmpnode.setShaderInput("TexDiffuse", self.tex['Diffuse'])
        tmpnode.setShaderInput("TexNormal", self.tex['Normal'])
        tmpnode.setShaderInput("TexSpecular", self.tex['Specular'])
        tmpnode.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
        tmpnode.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullCounterClockwise))
        tmpnode.setAttrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))
        self.psLightCam.node().setInitialState(tmpnode.getState())

        render.setState(RenderState.makeEmpty())

        # debug
        self.card = self.lightBuffer.getTextureCard()
        self.card.setTexture(self.tex['Final'])
        self.card.reparentTo(render2d)

        self.skyTex = loader.loadCubeMap("textures/skybox/Twilight_#.jpg")

        self.makeQuad()
        self.InitModels()
        #self.SetLights()
        self.InitLights()
        self.SetKeys()

        #self.quad.setTexture(self.tex['Final'])
        #self.quad.reparentTo(render2d)

        self.taskMgr.add(self.updateCamera, "Update Camera")

    def InitCamera(self):
        self.disableMouse()

        self.camera.setPos(-3.5, 1.5, 5)
        self.camera.setHpr(90, 0, 0)
        self.camLens.setNearFar(1.0, 500.0)
        self.camLens.setFov(90)

    def InitGameVar(self):
        Game.Win_Size_X = self.win.getProperties().getXSize()
        Game.Win_Size_Y = self.win.getProperties().getYSize()

        if Game.Shadow_Quality == 1:
            Game.Shadow_Map_Size = 512
        elif Game.Shadow_Quality == 2:
            Game.Shadow_Map_Size = 1024
        elif Game.Shadow_Quality == 3:
            Game.Shadow_Map_Size = 2048

    def InitBuffers(self):
    # Initialize off screen buffers
        self.buffers = {}
        self.bufferTex = {}
        self.bufferCam = {}

        self.InitBufferGBuffer()

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
        self.buffers['gBuffer'].setClearColor((0.0, 0.0, 0.0, 1.0))

    def InitBufferGBufferTex(self):
        self.bufferTex['DepthStencil'] = Texture()
        self.bufferTex['DepthStencil'].setFormat(Texture.FDepthStencil)
        self.bufferTex['Diffuse'] = Texture()
        self.bufferTex['Normal'] = Texture()
        self.bufferTex['Specular'] = Texture()
        #self.bufferTex['Irradiance'] = Texture()

    def InitBufferGBufferCam(self):
        self.bufferCam['gBuffer'] = self.makeCamera(
            self.buffers['gBuffer'], lens = self.camLens, scene = self.render, mask = Game.Mask['model'])

        self.bufferCam['gBuffer'].node().getDisplayRegion(0).disableClears()

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['gBuffer'])
        self.bufferCam['gBuffer'].node().setInitialState(tmpnode.getState())

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
            self.shaders['shadow_mapping'] = Shader.load(
                Shader.SLGLSL, "shaders/shadow_mapping_vert.glsl", "shaders/shadow_mapping_frag.glsl")

        if Game.Ambient_Occlusion != 0:
            if Game.Ambient_Occlusion == 1:
            # SSAO
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
    #初始化光源
        self.ambientLight = MyAmbientLight("ambientLight", self.quad)
        self.ambientLight.light.setColor(LVecBase4f(0.37, 0.37, 0.43, 1.0))
        self.ambientLight.NodePath.setShader(self.shaders['ambient_light'])
        self.ambientLight.initShaderInput()
        self.ambientLight.NodePath.reparentTo(self.adLightCam)

        self.sunLight = MyDirectionalLight("sunLight", self.quad)
        self.sunLight.light.setColor(LVecBase4f(1.0, 1.0, 0.85, 1.0))
        self.sunLight.light.setDirection(LVecBase3f(-1, -1, -0.52))
        self.sunLight.NodePath.setShader(self.shaders['directional_light'])
        self.sunLight.initShaderInput()
        #self.sunLight.NodePath.reparentTo(self.adLightCam)

        self.pointLight = MyPointLight("pointLight", self.sphere)
        self.pointLight.light.setColor(LVecBase4f(5.0, 5.0, 1.2, 1.0))
        self.pointLight.light.setSpecularColor(LVecBase4f(5.0, 5.0, 2.5, 1.0))
        self.pointLight.NodePath.setPos(LVecBase3f(15, 0, 1))
        self.pointLight.light.setAttenuation(LVecBase3f(1.0, 0.7, 1.8))
        self.pointLight.NodePath.setShader(self.shaders['point_light'])
        self.pointLight.initShaderInput()
        self.pointLight.calScale()
        self.pointLight.NodePath.reparentTo(self.lightVolumeRoot)

    def SetLights(self):
    	self.ambientLight = self.adLightCam.attachNewNode(AmbientLight("ambientLight"))
        self.ambientLight.node().setColor((0.37, 0.37, 0.43, 1.0))
        self.ambientLight.setShader(self.shaders['ambient_light'])
        self.SetupAmbientLight(self.ambientLight)
        self.quad.instanceTo(self.ambientLight)

        self.sunLight = self.adLightCam.attachNewNode(DirectionalLight("sunLight"))
        self.sunLight.node().setColor((1.0, 1.0, 0.85, 1.0))
        self.sunLight.node().setDirection(LVecBase3f(-1, -1, -0.52))
        self.sunLight.setShader(self.shaders['directional_light'])
        self.SetupDirectionalLight(self.sunLight)
        #self.quad.instanceTo(self.sunLight)

        #self.pointLight = self.lightVolumeRoot.attachNewNode(PointLight("pointLight"))
        #self.pointLight.node().setColor((5.0, 5.0, 1.2, 1.0))
        #self.pointLight.node().setSpecularColor((5.0, 5.0, 2.5, 1.0))
        #self.pointLight.setPos((15, 2, 1))
        #self.pointLight.node().setAttenuation((1.0, 0.7, 1.8))
        #self.pointLight.setShader(self.shaders['pLight'])
        #self.SetupPointLight(self.pointLight)
        #self.sphere.instanceTo(self.pointLight)
        #radius = self.calLightRadius(self.pointLight)
        #self.pointLight.setScale(radius, radius, radius)

        self.pointLight_ph = self.lightVolumeRoot.attachNewNode(PandaNode("pointLight placeholder"))
        self.pointLight = self.pointLight_ph.attachNewNode(PointLight("pointLight"))
        self.pointLight.node().setColor((5.0, 5.0, 1.2, 1.0))
        self.pointLight.node().setSpecularColor((5.0, 5.0, 2.5, 1.0))
        self.pointLight_ph.setPos((15, 0, 1))
        self.pointLight.node().setAttenuation((1.0, 0.7, 1.8))
        self.pointLight_ph.setShader(self.shaders['point_light'])
        self.pointLight_ph.setShaderInput("TexScale", self.texScale)
        #self.pointLight_ph.setShaderInput("TranSStoVS", self.tranSStoVS)
        self.pointLight_ph.setShaderInput("PointLight.color", self.pointLight.node().getColor())
        self.pointLight_ph.setShaderInput("PointLight.specular", self.pointLight.node().getSpecularColor())
        self.pointLight_ph.setShaderInput("PointLight.position", LVecBase4f(self.pointLight_ph.getPos(), 1.0))
        self.pointLight_ph.setShaderInput("PointLight.attenuation", self.pointLight.node().getAttenuation())
        #self.pointLight_ph.hide(BitMask32(self.modelMask | self.adLightMask))
        self.pointLight_ph.hide(BitMask32.allOn())
        self.pointLight_ph.show(BitMask32(Game.Mask['light-volume']))
        self.sphere.instanceTo(self.pointLight)
        radius = self.calLightRadius(self.pointLight)
        self.pointLight_ph.setScale(radius, radius, radius)

        #self.spotlight = self.lightVolumeRoot.attachNewNode(Spotlight("spotlight"))
        #self.spotlight.node().setColor((5.0, 5.5, 0.2, 1.0))
        #self.spotlight.node().setSpecularColor((1.0, 1.0, 0.0, 1.0))
        #self.spotlight.node().setAttenuation((1.0, 0.7, 1.8))
        #self.pointLight.setPos((0, 0, 0))
        #self.spotlight.node().getLens().setFov(30)
        #self.spotlight.node().getLens().setViewVector(1, 0, 0, 0, 0, 1)
        #self.spotlight.setShader(self.shaders['sLight'])
        #self.SetupSpotlight(self.spotlight)
        #self.cone.instanceTo(self.spotlight)
        #self.calSpotlightScale(self.spotlight)

        self.spotlight_ph = self.lightVolumeRoot.attachNewNode(PandaNode("spotlight placeholder"))
        self.spotlight = self.spotlight_ph.attachNewNode(Spotlight("spotlight"))
        self.spotlight.node().setColor((5.0, 5.5, 5.2, 1.0))
        self.spotlight.node().setSpecularColor((1.0, 1.0, 1.0, 1.0))
        self.spotlight.node().setAttenuation((1.0, 0.7, 1.8))
        self.spotlight_ph.setPos((-1, 0, 0.1))
        self.spotlight_ph.setHpr(-90, 0, -90)
        self.spotlight.node().getLens().setFov(30)
        cosCutOff = math.cos(30 * math.pi / 360)
       #self.spotlight.node().getLens().setViewVector(1, 0, 0, 0, 0, 1)
        self.spotlight_ph.setShader(self.shaders['spotlight'])
        self.spotlight_ph.setShaderInput("Spotlight.color", self.spotlight.node().getColor())
        self.spotlight_ph.setShaderInput("Spotlight.specular", self.spotlight.node().getSpecularColor())
        self.spotlight_ph.setShaderInput("Spotlight.position", LVecBase4f(self.spotlight_ph.getPos(), 1.0))
        self.spotlight_ph.setShaderInput("Spotlight.spotDirection", LVecBase3f(0.0, 1.0, 0.0))
        self.spotlight_ph.setShaderInput("Spotlight.spotCosCutoff", cosCutOff)
        self.spotlight_ph.setShaderInput("Spotlight.attenuation", self.spotlight.node().getAttenuation())
        self.spotlight_ph.hide(BitMask32(self.modelMask | self.adLightMask))
        #self.SetupSpotlight(self.spotlight)
        self.cone.instanceTo(self.spotlight)
        self.calSpotlightScale(self.spotlight)

    def InitModels(self):
        # 初始化模型根节点
        self.InitModelRoots()
        # 加载杂项模型
        self.InitModelMisc()

        self.sponza = self.loader.loadModel("models/sponza/sponza.bam")
        self.sponza.reparentTo(self.modelRoot)
        self.sponza.setScale(0.1, 0.1, 0.1)

    def InitModelRoots(self):
        # 全部不透明模型的根节点
        self.modelRoot = NodePath(PandaNode("model root"))
        self.modelRoot.reparentTo(self.render)
        self.modelRoot.hide(BitMask32.allOn())
        self.modelRoot.show(BitMask32(Game.Mask['model']))

        # 全部有体积的光源（点光源/聚光灯）的根节点
        self.lightVolumeRoot = NodePath(PandaNode("light root"))
        self.lightVolumeRoot.reparentTo(self.render)
        self.lightVolumeRoot.hide(BitMask32.allOn())
        self.lightVolumeRoot.show(BitMask32(Game.Mask['light-volume']))

    def InitModelMisc(self):
        # 球体（点光源）
        self.sphere = self.loader.loadModel("models/sphere")

        # 光椎（聚光灯）
        self.cone = self.loader.loadModel("models/cone")

        # 天空盒
        self.skybox = self.loader.loadModel("models/skybox")

    def SetKeys(self):
        self.keys = {}
        for key in ['w', 'a', 's', 'd']:
            self.keys[key] = 0
            self.accept(key, self.push_key, [key, 1])
            self.accept('%s-up' % key, self.push_key, [key, 0])
        self.accept('1', self.set_card, [self.tex['DepthStencil']])
        self.accept('2', self.set_card, [self.tex['Diffuse']])
        self.accept('3', self.set_card, [self.tex['Normal']])
        self.accept('4', self.set_card, [self.tex['Specular']])
        self.accept('5', self.set_card, [self.tex['Final']])
        self.accept('escape', __import__('sys').exit, [0])

    def makeQuad(self):
        # Make a full screen quad.
        vdata = GeomVertexData("vdata", GeomVertexFormat.getV3t2(),Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        vertex.addData3f(-1, 0, 1)
        texcoord.addData2f(0, 1)

        vertex.addData3f(-1, 0, -1)
        texcoord.addData2f(0, 0)

        vertex.addData3f(1, 0, -1)
        texcoord.addData2f(1, 0)

        vertex.addData3f(1, 0, 1)
        texcoord.addData2f(1, 1)

        prim = GeomTriangles(Geom.UHStatic)

        prim.addVertices(0, 1, 2)
        prim.addVertices(0, 2, 3)

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        node = GeomNode('quad')
        node.addGeom(geom)

        self.quad = NodePath(node)

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

    def calLightRadius(self, light):
        color = light.node().getColor()
        intensity = max(color.x, color.y, color.z)

        attenuation = light.node().getAttenuation()
        constant = attenuation.x
        linear = attenuation.y
        quadratic = attenuation.z

        radius = (-linear + math.sqrt(linear * linear - 4 * quadratic * (constant - (256.0 / 5.0) * intensity)))\
            /(2 * quadratic)

        return radius

    def calSpotlightScale(self, spotlight):
        FOV = spotlight.node().getLens().getFov().x
        FOV_rad = FOV * math.pi / 360
        radius = self.calLightRadius(spotlight)

        scale_x = radius * 2 * math.sin(FOV_rad) / math.sqrt(3)
        scale_z = radius * 2 * math.cos(FOV_rad)
        scale_y = scale_x

        spotlight.setScale(scale_x, scale_y, scale_z)

    def calTexScale(self, length):
        pow_of_2 = (0, 1, 2, 4, 8, 16 ,32 ,64, 128, 256, 512, 1024, 2048, 4096)

        if length > 4096 or length < 0:
            return float(1.0)

        i = 13
        while pow_of_2[i] >= length and i >= 0:
            if pow_of_2[i - 1] < length:
                return float(length) / pow_of_2[i]
            i -= 1

        return float(1.0)

    def calTranSStoVS(self):
        # Calculate the transform vector form screen-space to view-space
        Projection = self.cam.node().getLens().getProjectionMat()

        y = 0.5 * Projection[3][2]
        x = y / Projection[0][0]
        z = y / Projection[2][1]
        w = -0.5 - 0.5 * Projection[1][2]

        return LVecBase4f(x, y, z, w)

    def updateCamera(self, task):
        deltaTime = globalClock.getDt()  # To get the time (in seconds) since the last frame was drawn

        X = deltaTime * Game.Camera_Speed * (self.keys['a'] - self.keys['d'])
        Y = deltaTime * Game.Camera_Speed * (self.keys['w'] - self.keys['s'])

        self.camera.setPos(self.camera, -X, Y, 0)
        self.updateSkybox()

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

    def updateSkybox(self):
    	self.skybox.setPos(self.camera.getPos())

    def push_key(self, key, value):
    	self.keys[key] = value

    def set_card(self, tex):
    	self.card.setTexture(tex)

    def recenterMouse(self):
        self.win.movePointer(0,
              int(Game.Win_Size_X / 2),
              int(Game.Win_Size_Y / 2))

game = Game()
game.run()
