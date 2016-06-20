#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: CJT
# Date: 2016/6/18

# Deferred rendering pipeline using deferred shading.

from panda3d.core import loadPrcFileData
loadPrcFileData('', 'window-title CJT Deferred Rendering Demo')
loadPrcFileData('', 'win-size 1280 720')
loadPrcFileData('', 'sync-video false')
loadPrcFileData('', 'show-frame-rate-meter true')
loadPrcFileData('', 'texture-minfilter linear-mipmap-linear')
loadPrcFileData('', 'cursor-hidden true')
 
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.BufferViewer import BufferViewer
from direct.interval.MetaInterval import Sequence
import sys
import os
from math import *

MouseSensitivity = 100
CameraSpeed = 25
zoomRate = 5
 
class DeferredRendering(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.win.setClearColor(LVecBase4(0.0, 0.0, 0.0, 1))

        self.keys = {}
        for key in ['w', 'a', 's', 'd']:
        	self.keys[key] = 0
        	self.accept(key, self.push_key, [key, 1])
        	self.accept('%s-up' %key, self.push_key, [key, 0])
        self.accept('escape', __import__('sys').exit, [0])

        self.camera.setPos(0, -15, 5)

        self.disableMouse()
        self.recenterMouse()

        self.SetShaders()

        # Setup buffers
        self.gBuffer = self.makeFBO("G-Buffer", 1)
        self.lightBuffer = self.makeFBO("Light Buffer", 0)

        self.gBuffer.setSort(1)
        self.lightBuffer.setSort(2)
        self.win.setSort(3)

        # G-Buffer render texture
        self.gDiffuse = Texture()
        self.gNormal = Texture()
        #self.gSpecular = Texture()
        #self.gIrradiance = Texture()
        #self.gDepth-Stencil = Texture()
        #self.gDepth-Stencil.setFormat(Texture.FDepthStencil)
        self.gFinal = Texture()

        self.gBuffer.addRenderTexture(self.gDiffuse,
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        self.gBuffer.addRenderTexture(self.gNormal,
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPAuxRgba0)

        self.lightBuffer.addRenderTexture(self.gFinal,
        	GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        lens = self.cam.node().getLens()
        
        self.gBufferMask = 1
        self.lightMask = 2

        self.gBufferCam = self.makeCamera(self.gBuffer, lens = lens, scene = render, mask = self.gBufferMask)
        self.lightCam = self.makeCamera(self.lightBuffer, lens = lens, scene = render, mask = self.lightMask)

        #self.cam.node().setActive(0)

        self.gBufferCam.node().getDisplayRegion(0).disableClears()
        self.lightCam.node().getDisplayRegion(0).disableClears()
        self.cam.node().getDisplayRegion(0).disableClears()
        self.cam2d.node().getDisplayRegion(0).disableClears()
        self.gBuffer.disableClears()
        #self.win.disableClears()

        self.gBuffer.setClearColorActive(1)
        self.gBuffer.setClearDepthActive(1)
        self.lightBuffer.setClearColorActive(1)
        self.lightBuffer.setClearColor((0.0, 0.0, 0.0, 1.0))

        tmpnode = NodePath(PandaNode("tmp node"))
        tmpnode.setShader(self.shaders['gBuffer'])
        self.gBufferCam.node().setInitialState(tmpnode.getState())

        #tmpnode = NodePath(PandaNode("tmp node"))
        #tmpnode.setShader(shaders['light'])
        #tmpnode.setShaderInput()
        #self.lightCam.node().setInitialState(tmpnode.getState())

        self.skyTex = loader.loadCubeMap("textures/skybox/Twilight_#.jpg")

        self.SetLights()
        self.SetModels()

        self.taskMgr.add(self.updateCamera, "Update Camera")

    def SetShaders(self):
    	self.shaders = {}
        self.shaders['gBuffer'] = Shader.load(
        	Shader.SLGLSL, "shaders/deferred_rendering_geometry_vert.glsl", "shaders/deferred_rendering_geometry_frag.glsl")
        self.shaders['light'] = Shader.load(
        	Shader.SLGLSL, "shaders/deferred_rendering_geometry_vert.glsl", "shaders/deferred_rendering_geometry_frag.glsl")
        self.shaders['skybox'] = Shader.load(
        	Shader.SLGLSL, "shaders/skybox_vert.glsl", "shaders/skybox_frag.glsl")

    def SetLights(self):
    	self.ambientLight = render.attachNewNode(AmbientLight("ambientLight"))
        self.ambientLight.node().setColor((0.37, 0.37, 0.43, 1.0))

        self.sun = render.attachNewNode(DirectionalLight("sun"))
        self.sun.node().setColor((1.0, 0.76, 0.45, 1.0))
        self.sun.node().setDirection(LVector3(1, -1, -0.22))

        render.setLight(self.ambientLight)
        render.setLight(self.sun)

    def SetModels(self):
    	self.environ = self.loader.loadModel("models/environment")
        self.environ.reparentTo(self.render)
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)

        self.skybox = self.loader.loadModel("models/skybox")
        self.skybox.reparentTo(self.render)
        self.skybox.setShader(self.shaders['skybox'])
        self.skybox.setShaderInput("skybox", self.skyTex)
        self.skybox.setAttrib(DepthTestAttrib.make(RenderAttrib.MLessEqual))

    def makeFBO(self, name, auxrgba):
    	winprops = WindowProperties()
    	props = FrameBufferProperties()
    	props.setRgbColor(True)
    	props.setRgbaBits(8, 8, 8, 8)
    	props.setDepthBits(1)
    	props.setAuxRgba(auxrgba)
        return self.graphicsEngine.makeOutput(
        	self.pipe, name, -2, props, winprops,
        	GraphicsPipe.BFSizeTrackHost | GraphicsPipe.BFCanBindEvery |
        	GraphicsPipe.BFRttCumulative | GraphicsPipe.BFRefuseWindow,
        	self.win.getGsg(), self.win)
 
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
