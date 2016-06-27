#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: CJT
# Date: 2016/6/18

# Deferred rendering pipeline using deferred shading.

from panda3d.core import *
loadPrcFileData('', 'window-title CJT Deferred Rendering Demo')
loadPrcFileData('', 'win-size 1280 720')
loadPrcFileData('', 'sync-video false')
loadPrcFileData('', 'show-frame-rate-meter true')
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

MouseSensitivity = 100
CameraSpeed = 25

class DeferredRendering(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.win.setClearColor(LVecBase4(0.0, 0.0, 0.0, 1))

        self.camera.setPos(0, -15, 5)

        self.disableMouse()
        self.recenterMouse()

        self.SetShaders()

        # Setup buffers
        self.gBuffer = self.makeFBO("G-Buffer", 2)
        self.lightBuffer = self.makeFBO("Light Buffer", 0)
        self.finalBuffer = self.makeFBO("Final Buffer", 0)

        self.gBuffer.setSort(1)
        self.lightBuffer.setSort(2)
        self.finalBuffer.setSort(3)
        self.win.setSort(4)

        # G-Buffer render texture
        self.gDepthStencil = Texture()
        self.gDepthStencil.setFormat(Texture.FDepthStencil)
        self.gDiffuse = Texture()
        self.gNormal = Texture()
        self.gSpecular = Texture()
        #self.gIrradiance = Texture()
        self.gHDR = Texture()
        self.gHDR.setFormat(Texture.FRgba16)
        self.gFinal = Texture()

        self.texScale = LVecBase2f(self.calTexScale(self.win.getProperties().getXSize()),
                                   self.calTexScale(self.win.getProperties().getYSize()))
        self.tranSStoVS = self.calTranSStoVS()

        self.gBuffer.addRenderTexture(self.gDepthStencil,
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepthStencil)
        self.gBuffer.addRenderTexture(self.gDiffuse,
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        self.gBuffer.addRenderTexture(self.gNormal,
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba0)
        self.gBuffer.addRenderTexture(self.gSpecular,
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba1)

        self.lightBuffer.addRenderTexture(self.gHDR,
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.finalBuffer.addRenderTexture(self.gFinal,
            GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.cam.node().getLens().setNear(1.0)
        self.cam.node().getLens().setFar(500.0)
        lens = self.cam.node().getLens()

        self.modelMask = 1
        self.adLightMask = 2
        self.psLightMask = 4
        self.finalMask = 8

        self.gBufferCam = self.makeCamera(self.gBuffer, lens = lens, scene = render, mask = self.modelMask)
        self.adLightCam = self.makeCamera(self.lightBuffer, lens = lens, scene = render, mask = self.adLightMask)
        self.psLightCam = self.makeCamera(self.lightBuffer, lens = lens, scene = render, mask = self.psLightMask)
        self.finalCam = self.makeCamera(self.finalBuffer, lens = lens, scene = render, mask = self.finalMask)

        self.cam.node().setActive(0)

        self.adLightCam.node().getDisplayRegion(0).setSort(1)
        self.psLightCam.node().getDisplayRegion(0).setSort(2)

        self.gBufferCam.node().getDisplayRegion(0).disableClears()
        self.adLightCam.node().getDisplayRegion(0).disableClears()
        self.psLightCam.node().getDisplayRegion(0).disableClears()
        self.finalCam.node().getDisplayRegion(0).disableClears()
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
        self.finalBuffer.setClearColorActive(1)
        self.finalBuffer.setClearColor((0.0, 0.0, 0.0, 1.0))

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['gBuffer'])
        self.gBufferCam.node().setInitialState(tmpnode.getState())

        tmpnode = NodePath(PandaNode("tmp node"))
        #tmpnode.setShader(self.shaders['dLight'])
        tmpnode.setShaderInput("TexScale", self.texScale)
        tmpnode.setShaderInput("gDepthStencil", self.gDepthStencil)
        tmpnode.setShaderInput("gDiffuse", self.gDiffuse)
        tmpnode.setShaderInput("gNormal", self.gNormal)
        tmpnode.setShaderInput("gSpecular", self.gSpecular)
        tmpnode.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
        tmpnode.setAttrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))
        self.adLightCam.node().setInitialState(tmpnode.getState())
        self.psLightCam.node().setInitialState(tmpnode.getState())

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['hdr'])
        tmpnode.setShaderInput("TexScale", self.texScale)
        tmpnode.setShaderInput("gHDR", self.gHDR)
        self.finalCam.node().setInitialState(tmpnode.getState())

        render.setState(RenderState.makeEmpty())

        # debug
        self.card = self.lightBuffer.getTextureCard()
        self.card.setTexture(self.gFinal)
        self.card.reparentTo(render2d)

        self.skyTex = loader.loadCubeMap("textures/skybox/Twilight_#.jpg")

        self.makeQuad()
        self.SetModels()
        self.SetLights()

        self.keys = {}
        for key in ['w', 'a', 's', 'd']:
        	self.keys[key] = 0
        	self.accept(key, self.push_key, [key, 1])
        	self.accept('%s-up' %key, self.push_key, [key, 0])
        self.accept('1', self.set_card, [self.gDepthStencil])
        self.accept('2', self.set_card, [self.gDiffuse])
        self.accept('3', self.set_card, [self.gNormal])
        self.accept('4', self.set_card, [self.gSpecular])
        self.accept('5', self.set_card, [self.gFinal])
        self.accept('escape', __import__('sys').exit, [0])

        self.taskMgr.add(self.updateCamera, "Update Camera")

    def set_card(self, tex):
    	self.card.setTexture(tex)

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
        self.shaders['skybox'] = Shader.load(
        	Shader.SLGLSL, "shaders/skybox_vert.glsl", "shaders/skybox_frag.glsl")
        self.shaders['hdr'] = Shader.load(
            Shader.SLGLSL, "shaders/tone_mapping_vert.glsl", "shaders/tone_mapping_frag.glsl")

    def SetLights(self):
    	self.ambientLight = self.adLightCam.attachNewNode(AmbientLight("ambientLight"))
        self.ambientLight.node().setColor((0.37, 0.37, 0.43, 1.0))
        self.ambientLight.setShader(self.shaders['aLight'])
        self.SetupAmbientLight(self.ambientLight)
        self.quad.instanceTo(self.ambientLight)

        self.sunLight = self.adLightCam.attachNewNode(DirectionalLight("sunLight"))
        self.sunLight.node().setColor((10.0, 7.6, 4.5, 1.0))
        self.sunLight.node().setDirection(LVecBase3f(1, -1, -0.22))
        self.sunLight.setShader(self.shaders['dLight'])
        self.SetupDirectionalLight(self.sunLight)
        self.quad.instanceTo(self.sunLight)

        self.pointLight = self.lightRoot.attachNewNode(PointLight("pointLight"))
        self.pointLight.node().setColor((1.0, 1.0, 0.0, 1.0))
        self.pointLight.node().setSpecularColor((0.0, 1.0, 0.5, 1.0))
        self.pointLight.setPos((0, 0, 3))
        self.pointLight.node().setAttenuation((1.0, 0.09, 0.032))
        self.pointLight.setShader(self.shaders['pLight'])
        self.SetupPointLight(self.pointLight)
        #self.sphere.instanceTo(self.pointLight)
        #radius = self.calLightRadius(self.pointLight)
        radius = 5.0
        self.pointLight.setScale(radius, radius, radius)

        self.spotlight = self.lightRoot.attachNewNode(Spotlight("spotlight"))
        self.spotlight.node().setColor((1.0, 0.8, 0.5, 1.0))
        self.spotlight.node().setSpecularColor((1.0, 1.0, 0.0, 1.0))
        self.spotlight.node().setAttenuation((1.0, 0.09, 0.032))
        self.spotlight.node().getLens().getFov().x

    def SetModels(self):
        self.modelRoot = NodePath(PandaNode("model root"))
        self.modelRoot.reparentTo(self.render)
        self.modelRoot.hide(BitMask32(self.adLightMask | self.psLightMask | self.finalMask))

        self.lightRoot = NodePath(PandaNode("light root"))
        self.lightRoot.reparentTo(self.render)
        self.lightRoot.hide(BitMask32(self.modelMask | self.adLightMask | self.finalMask))

    	self.environ = self.loader.loadModel("models/environment")
        self.environ.reparentTo(self.modelRoot)
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)

        self.sphere = self.loader.loadModel("models/sphere")

        self.cone = self.loader.loadModel("models/cone")

        self.hdrQuad = self.finalCam.attachNewNode(PandaNode("hdrQuad"))
        self.quad.instanceTo(self.hdrQuad)

        self.skybox = self.loader.loadModel("models/skybox")
        #self.skybox.reparentTo(self.lightRoot)
        self.skybox.setShader(self.shaders['skybox'])
        self.skybox.setShaderInput("skybox", self.skyTex)
        self.skybox.setAttrib(DepthTestAttrib.make(RenderAttrib.MLessEqual))
        #self.skybox.hide(self.modelMask)
        #self.skybox.show(self.lightMask)

    def SetupAmbientLight(self, aLight):
        aLight.setShaderInput("TexScale", self.texScale)
        aLight.setShaderInput("AmbientLight.color", aLight.node().getColor())
        aLight.hide(BitMask32(self.modelMask | self.psLightMask | self.finalMask))

    def SetupDirectionalLight(self, dLight):
        dLight.setShaderInput("TexScale", self.texScale)
        dLight.setShaderInput("LightSource.color", dLight.node().getColor())
        dLight.setShaderInput("LightSource.specular", dLight.node().getSpecularColor())
        dLight.setShaderInput("LightSource.position", dLight.node().getDirection())
        dLight.hide(BitMask32(self.modelMask | self.psLightMask | self.finalMask))

    def SetupPointLight(self, pLight):
        pLight.setShaderInput("TexScale", self.texScale)
        pLight.setShaderInput("TranSStoVS", self.tranSStoVS)
        pLight.setShaderInput("PointLight.color", pLight.node().getColor())
        pLight.setShaderInput("PointLight.specular", pLight.node().getSpecularColor())
        pLight.setShaderInput("PointLight.position", LVecBase4f(pLight.getPos(), 1.0))
        pLight.setShaderInput("PointLight.attenuation", pLight.node().getAttenuation())
        pLight.hide(BitMask32(self.modelMask | self.adLightMask | self.finalMask))

    def SetupSpotlight(self, sLight):
        sLight.setShaderInput("LightSource.color", sLight.node().getColor())
        sLight.setShaderInput("LightSource.specular", sLight.node().getSpecularColor())
        sLight.setShaderInput("LightSource.position", sLight.getPos())
        sLight.setShaderInput("LightSource.attenuation", sLight.node().getAttenuation())

    def makeQuad(self):
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
        print Projection

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

    def recenterMouse(self):
        self.win.movePointer(0,
              int(self.win.getProperties().getXSize() / 2),
              int(self.win.getProperties().getYSize() / 2))

app = DeferredRendering()
app.run()
