#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: CJT
# Date: 2016/6/16

# A simple skybox.

from panda3d.core import loadPrcFileData
loadPrcFileData('', 'window-title CJT Skybox Demo')
loadPrcFileData('', 'win-size 1280 720')
loadPrcFileData('', 'sync-video true')
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
import sys
import os
from math import *

MouseSensitivity = 100
CameraSpeed = 25
zoomRate = 5
 
class Skybox(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.win.setClearColor(LVecBase4(0.0, 0.0, 0.0, 1))

        self.keys = {}
        for key in ['w', 'a', 's', 'd']:
        	self.keys[key] = 0
        	self.accept(key, self.push_key, [key, 1])
        	self.accept('%s-up' %key, self.push_key, [key, 0])
        self.accept('wheel_up', self.zoom, [1])
        self.accept('wheel_down', self.zoom, [-1])
        self.accept('escape', __import__('sys').exit, [0])

        self.len = self.cam.node().getLens()
        self.camera.setPos(0, -15, 5)

        self.disableMouse()
        self.recenterMouse()

        # Load skybox shaders
        sha = Shader.load(Shader.SLGLSL, "shaders/skybox_vert.glsl", "shaders/skybox_frag.glsl")

        self.skyTex = loader.loadCubeMap("textures/skybox/Twilight_#.jpg")

        # Light setting
        #self.ambientLight = render.attachNewNode(AmbientLight("ambientLight"))
        #self.ambientLight.node().setColor((0.1, 0.1, 0.1, 1.0))

        #self.sun = render.attachNewNode(DirectionalLight("sun"))
        #self.sun.node().setColor((1.0, 1.0, 1.0, 1.0))
        #self.sun.node().setDirection(LVector3(1, -1, -1))

        #render.setLight(self.ambientLight)
        #render.setLight(self.sun)

        self.environ = self.loader.loadModel("models/environment")
        self.environ.reparentTo(self.render)
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)

        self.skybox = self.loader.loadModel("models/skybox")
        self.skybox.reparentTo(self.render)
        self.skybox.setShader(sha)
        self.skybox.setShaderInput("skybox", self.skyTex)
        self.skybox.setAttrib(DepthTestAttrib.make(RenderAttrib.MLessEqual))

        self.taskMgr.add(self.updateCamera, "Update Camera")
 
    def updateCamera(self, task):
        deltaTime = globalClock.getDt()  # To get the time (in seconds) since the last frame was drawn

        X = deltaTime * CameraSpeed * (self.keys['a'] - self.keys['d'])
        Y = deltaTime * CameraSpeed * (self.keys['w'] - self.keys['s'])

        self.camera.setPos(self.camera, -X, Y, 0)
        self.skybox.setPos(self.camera.getPos())

        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()  # get the mouse position

            self.recenterMouse()

            zhpr = self.camera.getHpr() + (mpos.getX() * -MouseSensitivity, mpos.getY() * MouseSensitivity, 0.0)

            if zhpr.y > 90.0:
            	zhpr.y = 90.0
            elif zhpr.y < -90.0:
            	zhpr.y = -90.0

            self.camera.setHpr(zhpr)

        return Task.cont

    def zoom(self, offset):
        newFov = self.len.getFov().x + offset * zoomRate

        if newFov < 10:
            newFov = 10
        elif newFov > 120:
            newFov = 120

        self.len.setFov(newFov)

    def push_key(self, key, value):
    	self.keys[key] = value

    def recenterMouse(self):
        self.win.movePointer(0, 
              int(self.win.getProperties().getXSize() / 2),
              int(self.win.getProperties().getYSize() / 2))

app = Skybox()
app.run()