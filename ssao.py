#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: CJT
# Date: 2016/7/4

# Screen Space Ambient Occlusion.

from panda3d.core import *
loadPrcFileData('', 'window-title CJT Ambient Occlusion Demo')
loadPrcFileData('', 'win-size 1280 720')
loadPrcFileData('', 'sync-video false')
loadPrcFileData('', 'show-frame-rate-meter true')
loadPrcFileData('', 'textures-power-2 none')
loadPrcFileData('', 'texture-anisotropic-degree 16')
loadPrcFileData('', 'texture-minfilter linear-mipmap-linear')
loadPrcFileData('', 'cursor-hidden true')
#loadPrcFileData('', 'gl-coordinate-system default')

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from direct.filter.FilterManager import FilterManager
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.BufferViewer import BufferViewer
from direct.interval.MetaInterval import Sequence
import sys
import os
import math
import random

MouseSensitivity = 100
CameraSpeed = 25

class AmbientOcclusion(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.win.setClearColor(LVecBase4(0.0, 0.0, 0.0, 1))

        self.camera.setPos(0, 0, 5)

        self.disableMouse()
        self.recenterMouse()

        self.SetShaders()

        # Setup buffers
        self.gBuffer = self.makeFBO("G-Buffer", 2)
        self.SSAONoiseBuffer = self.makeFBO("SSAO Noise Buffer", 0)
        self.SSAOBlurBuffer = self.makeFBO("SSAO Blur Buffer", 0)
        self.lightBuffer = self.makeFBO("Light Buffer", 0)

        self.gBuffer.setSort(1)
        self.SSAONoiseBuffer.setSort(2)
        self.SSAOBlurBuffer.setSort(3)
        self.lightBuffer.setSort(4)
        self.win.setSort(5)

        # G-Buffer render texture
        self.tex = {}
        self.tex['DepthStencil'] = Texture()
        self.tex['DepthStencil'].setFormat(Texture.FDepthStencil)
        self.tex['DepthStencil'].setWrapU(Texture.WMClamp)
        self.tex['DepthStencil'].setWrapV(Texture.WMClamp)
        self.tex['Diffuse'] = Texture()
        self.tex['Normal'] = Texture()
        self.tex['Specular'] = Texture()
        #self.tex['Irradiance'] = Texture()
        noise = PNMImage(4, 4)
        for i in range(4):
            for j in range(4):
                noise.setXel(i, j, LVecBase3f(random.random() * 2 - 1, random.random() * 2 - 1, 0.0))

        self.tex['noise'] = Texture()
        self.tex['noise'].load(noise)
        self.tex['noise'].setFormat(Texture.FRgb16)
        self.tex['noise'].setMagfilter(Texture.FTNearest)
        self.tex['noise'].setMinfilter(Texture.FTNearest)
        self.tex['noise'].setWrapU(Texture.WMRepeat)
        self.tex['noise'].setWrapV(Texture.WMRepeat)

        self.tex['SSAONoisy'] = Texture()
        #self.tex['SSAONoisy'].setFormat(Texture.FRed)
        self.tex['SSAOBlurred'] = Texture()
        #self.tex['SSAOBlurred'].setFormat(Texture.FRed)
        self.tex['Final'] = Texture()

        #self.texScale = LVecBase2f(self.calTexScale(self.win.getProperties().getXSize()),
        #                           self.calTexScale(self.win.getProperties().getYSize()))
        self.texScale = LVecBase2f(1.0, 1.0)
        self.texScaleNoise = LVecBase2f(self.win.getProperties().getXSize() / 4.0,
                                        self.win.getProperties().getYSize() / 4.0)
        self.tranSStoVS = self.calTranSStoVS()
        self.SSAOcalRandomSample()

        self.gBuffer.addRenderTexture(self.tex['DepthStencil'],
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepthStencil)
        self.gBuffer.addRenderTexture(self.tex['Diffuse'],
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        self.gBuffer.addRenderTexture(self.tex['Normal'],
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba0)
        self.gBuffer.addRenderTexture(self.tex['Specular'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba1)

        self.SSAONoiseBuffer.addRenderTexture(self.tex['SSAONoisy'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.SSAOBlurBuffer.addRenderTexture(self.tex['SSAOBlurred'],
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.lightBuffer.addRenderTexture(self.tex['Final'],
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.cam.node().getLens().setNear(1.0)
        self.cam.node().getLens().setFar(500.0)
        lens = self.cam.node().getLens()

        self.modelMask = 1
        self.adLightMask = 2
        self.psLightMask = 4
        self.SSAOMask = 8

        self.gBufferCam = self.makeCamera(self.gBuffer, lens = lens, scene = render, mask = self.modelMask)
        self.adLightCam = self.makeCamera(self.lightBuffer, lens = lens, scene = render, mask = self.adLightMask)
        self.psLightCam = self.makeCamera(self.lightBuffer, lens = lens, scene = render, mask = self.psLightMask)
        self.SSAONoiseCam = self.makeCamera(self.SSAONoiseBuffer, lens = lens, scene = render, mask = self.SSAOMask)
        self.SSAOBlurCam = self.makeCamera(self.SSAOBlurBuffer, lens = lens, scene = render, mask = self.SSAOMask)

        self.cam.node().setActive(0)

        self.adLightCam.node().getDisplayRegion(0).setSort(1)
        self.psLightCam.node().getDisplayRegion(0).setSort(2)

        self.gBufferCam.node().getDisplayRegion(0).disableClears()
        self.adLightCam.node().getDisplayRegion(0).disableClears()
        self.psLightCam.node().getDisplayRegion(0).disableClears()
        self.SSAONoiseCam.node().getDisplayRegion(0).disableClears()
        self.SSAOBlurCam.node().getDisplayRegion(0).disableClears()
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
        self.SSAONoiseBuffer.setClearColorActive(1)
        self.SSAONoiseBuffer.setClearColor((1.0, 1.0, 1.0, 1.0))
        self.SSAOBlurBuffer.setClearColorActive(1)
        self.SSAOBlurBuffer.setClearColor((1.0, 1.0, 1.0, 1.0))

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['gBuffer'])
        self.gBufferCam.node().setInitialState(tmpnode.getState())

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShaderInput("texScale", self.texScale)
        tmpnode.setShaderInput("TexDepthStencil", self.tex['DepthStencil'])
        tmpnode.setShaderInput("TexDiffuse", self.tex['Diffuse'])
        tmpnode.setShaderInput("TexNormal", self.tex['Normal'])
        tmpnode.setShaderInput("TexSpecular", self.tex['Specular'])
        tmpnode.setShaderInput("TexAO", self.tex['SSAOBlurred'])
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

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['SSAONoise'])
        tmpnode.setShaderInput("texScale", self.texScale)
        tmpnode.setShaderInput("texScaleNoise", self.texScaleNoise)
        tmpnode.setShaderInput("TexDepthStencil", self.tex['DepthStencil'])
        tmpnode.setShaderInput("TexNormal", self.tex['Normal'])
        tmpnode.setShaderInput("TexNoise", self.tex['noise'])
        tmpnode.setShaderInput("samples", self.SSAOsamples)
        self.SSAONoiseCam.node().setInitialState(tmpnode.getState())

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['SSAOBlur'])
        tmpnode.setShaderInput("texScale", self.texScale)
        tmpnode.setShaderInput("TexSSAONoisy", self.tex['SSAONoisy'])
        self.SSAOBlurCam.node().setInitialState(tmpnode.getState())

        render.setState(RenderState.makeEmpty())

        # debug
        self.card = self.lightBuffer.getTextureCard()
        self.card.setTexture(self.tex['Final'])
        self.card.reparentTo(render2d)

        self.skyTex = loader.loadCubeMap("textures/skybox/Twilight_#.jpg")

        self.makeQuad()
        self.SetModels()
        self.SetLights()
        self.SetKeys()

        self.taskMgr.add(self.updateCamera, "Update Camera")

    def SSAOcalRandomSample(self):
        self.SSAOsamples = PTA_LVecBase4f()

        for i in range(64):
            #sample = LVecBase3f(random.random() * 2 - 1, random.random() * 2 - 1, random.random())
            sample = LVecBase3f(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(0.0, 1.0))
            sample_length = math.sqrt(sample.x * sample.x + sample.y * sample.y + sample.z * sample.z)
            sample /= sample_length
            sample *= random.random()
            sample = sample * 0.5 + 0.5
            scale = float(i) / 64.0
            scale = 0.1 + 0.9 * (scale * scale)
            sample *= scale
            self.SSAOsamples.push_back(UnalignedLVecBase4f(sample.x, sample.y, sample.z, 0.0))

    def SetShaders(self):
    	self.shaders = {}
        self.shaders['gBuffer'] = Shader.load(
        	Shader.SLGLSL, "shaders/gbuffer_vert.glsl", "shaders/gbuffer_frag.glsl")
        self.shaders['aLight'] = Shader.load(
            Shader.SLGLSL, "shaders/ambient_light_vert.glsl", "shaders/ambient_light_frag.glsl")
        self.shaders['dLight'] = Shader.load(
        	Shader.SLGLSL, "shaders/directional_light_vert.glsl", "shaders/directional_light_frag.glsl")
        self.shaders['pLight'] = Shader.load(
            Shader.SLGLSL, "shaders/point_light_vert.glsl", "shaders/point_light_frag.glsl")
        self.shaders['sLight'] = Shader.load(
            Shader.SLGLSL, "shaders/spotlight_vert.glsl", "shaders/spotlight_frag.glsl")
        self.shaders['SSAONoise'] = Shader.load(
            Shader.SLGLSL, "shaders/ssao_noise_vert.glsl", "shaders/ssao_noise_frag.glsl")
        self.shaders['SSAOBlur'] = Shader.load(
            Shader.SLGLSL, "shaders/ssao_blur_vert.glsl", "shaders/ssao_blur_frag.glsl")
        self.shaders['skybox'] = Shader.load(
        	Shader.SLGLSL, "shaders/skybox_vert.glsl", "shaders/skybox_frag.glsl")

    def SetLights(self):
    	self.ambientLight = self.adLightCam.attachNewNode(AmbientLight("ambientLight"))
        self.ambientLight.node().setColor((0.97, 0.97, 0.93, 1.0))
        self.ambientLight.setShader(self.shaders['aLight'])
        self.SetupAmbientLight(self.ambientLight)
        self.quad.instanceTo(self.ambientLight)

        self.sunLight = self.adLightCam.attachNewNode(DirectionalLight("sunLight"))
        self.sunLight.node().setColor((1.0, 1.0, 0.85, 1.0))
        self.sunLight.node().setDirection(LVecBase3f(1, -1, -0.22))
        self.sunLight.setShader(self.shaders['dLight'])
        self.SetupDirectionalLight(self.sunLight)
        #self.quad.instanceTo(self.sunLight)

        self.pointLight = self.lightRoot.attachNewNode(PointLight("pointLight"))
        self.pointLight.node().setColor((5.0, 5.0, 1.2, 1.0))
        self.pointLight.node().setSpecularColor((5.0, 5.0, 2.5, 1.0))
        self.pointLight.setPos((15, 2, 1))
        self.pointLight.node().setAttenuation((1.0, 0.7, 1.8))
        self.pointLight.setShader(self.shaders['pLight'])
        self.SetupPointLight(self.pointLight)
        #self.sphere.instanceTo(self.pointLight)
        radius = self.calLightRadius(self.pointLight)
        self.pointLight.setScale(radius, radius, radius)

        self.spotlight = self.lightRoot.attachNewNode(Spotlight("spotlight"))
        self.spotlight.node().setColor((5.0, 5.5, 0.2, 1.0))
        self.spotlight.node().setSpecularColor((1.0, 1.0, 0.0, 1.0))
        self.spotlight.node().setAttenuation((1.0, 0.7, 1.8))
        self.pointLight.setPos((0, 0, 0))
        self.spotlight.node().getLens().setFov(30)
        self.spotlight.node().getLens().setViewVector(1, 0, 0, 0, 0, 1)
        #self.spotlight.setShader(self.shaders['sLight'])
        self.SetupSpotlight(self.spotlight)
        #self.cone.instanceTo(self.spotlight)
        self.calSpotlightScale(self.spotlight)


    def SetModels(self):
        self.modelRoot = NodePath(PandaNode("model root"))
        self.modelRoot.reparentTo(self.render)
        self.modelRoot.hide(BitMask32.allOn())
        self.modelRoot.show(BitMask32(self.modelMask))

        self.lightRoot = NodePath(PandaNode("light root"))
        self.lightRoot.reparentTo(self.render)
        self.lightRoot.hide(BitMask32(self.modelMask | self.adLightMask))

    	#self.environ = self.loader.loadModel("models/environment")
        #self.environ.reparentTo(self.modelRoot)
        #self.environ.setScale(0.25, 0.25, 0.25)
        #self.environ.setPos(-8, 42, 0)

        self.sponza = self.loader.loadModel("models/sponza/sponza.bam")
        self.sponza.reparentTo(self.modelRoot)
        self.sponza.setScale(0.1, 0.1, 0.1)

        #self.bunny = self.loader.loadModel("models/bunny")
        #self.bunny.reparentTo(self.modelRoot)
        #self.bunny.setPos(0, 0, 0)
        #self.bunny.setScale(25, 25, 25)

        self.SSAONoiseQuad = self.SSAONoiseCam.attachNewNode(PandaNode("SSAONoiseQuad"))
        self.quad.instanceTo(self.SSAONoiseQuad)
        self.SSAONoiseQuad.hide(BitMask32.allOn())
        self.SSAONoiseQuad.show(BitMask32(self.SSAOMask))

        self.sphere = self.loader.loadModel("models/sphere")

        self.cone = self.loader.loadModel("models/cone")

        self.skybox = self.loader.loadModel("models/skybox")
        #self.skybox.reparentTo(self.lightRoot)
        self.skybox.setShader(self.shaders['skybox'])
        self.skybox.setShaderInput("TexSkybox", self.skyTex)
        self.skybox.setAttrib(DepthTestAttrib.make(RenderAttrib.MLessEqual))
        #self.skybox.hide(self.modelMask)
        #self.skybox.show(self.lightMask)

    def SetKeys(self):
        self.keys = {}
        for key in ['w', 'a', 's', 'd']:
            self.keys[key] = 0
            self.accept(key, self.push_key, [key, 1])
            self.accept('%s-up' % key, self.push_key, [key, 0])
        self.accept('1', self.set_card, [self.tex['Specular']])
        self.accept('2', self.set_card, [self.tex['Normal']])
        self.accept('3', self.set_card, [self.tex['Diffuse']])
        self.accept('4', self.set_card, [self.tex['SSAONoisy']])
        self.accept('5', self.set_card, [self.tex['SSAOBlurred']])
        self.accept('6', self.set_card, [self.tex['Final']])
        self.accept('escape', __import__('sys').exit, [0])

    def SetupAmbientLight(self, aLight):
        aLight.setShaderInput("TexScale", self.texScale)
        aLight.setShaderInput("AmbientLight.color", aLight.node().getColor())
        aLight.hide(BitMask32(self.modelMask | self.psLightMask))

    def SetupDirectionalLight(self, dLight):
        dLight.setShaderInput("TexScale", self.texScale)
        dLight.setShaderInput("DirectionalLight.color", dLight.node().getColor())
        dLight.setShaderInput("DirectionalLight.specular", dLight.node().getSpecularColor())
        dLight.setShaderInput("DirectionalLight.position", dLight.node().getDirection())
        dLight.hide(BitMask32(self.modelMask | self.psLightMask))

    def SetupPointLight(self, pLight):
        pLight.setShaderInput("TexScale", self.texScale)
        pLight.setShaderInput("TranSStoVS", self.tranSStoVS)
        pLight.setShaderInput("PointLight.color", pLight.node().getColor())
        pLight.setShaderInput("PointLight.specular", pLight.node().getSpecularColor())
        pLight.setShaderInput("PointLight.position", LVecBase4f(pLight.getPos(), 1.0))
        pLight.setShaderInput("PointLight.attenuation", pLight.node().getAttenuation())
        pLight.hide(BitMask32(self.modelMask | self.adLightMask))

    def SetupSpotlight(self, sLight):
        sLight.setShaderInput("Spotlight.color", sLight.node().getColor())
        sLight.setShaderInput("Spotlight.specular", sLight.node().getSpecularColor())
        sLight.setShaderInput("Spotlight.position", sLight.getPos())
        sLight.setShaderInput("Spotlight.attenuation", sLight.node().getAttenuation())

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

        X = deltaTime * CameraSpeed * (self.keys['a'] - self.keys['d'])
        Y = deltaTime * CameraSpeed * (self.keys['w'] - self.keys['s'])

        self.camera.setPos(self.camera, -X, Y, 0)
        self.updateSkybox()

        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()  # get the mouse position

            self.recenterMouse()

            newHpr = self.camera.getHpr() + (mpos.getX() * -MouseSensitivity, mpos.getY() * MouseSensitivity, 0.0)

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
              int(self.win.getProperties().getXSize() / 2),
              int(self.win.getProperties().getYSize() / 2))

app = AmbientOcclusion()
app.run()
