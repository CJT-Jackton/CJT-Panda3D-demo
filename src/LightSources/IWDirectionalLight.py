#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: CJT
# Date: 2016/7/13

from panda3d.core import *

class IWDirectionalLight(PandaNode):
# 自定义平行光光源
    def __init__(self, name, quad):
        PandaNode.__init__(self, name)
        self.NodePath = NodePath(self)
        self.light_NP = self.NodePath.attachNewNode(DirectionalLight("directionalLight"))
        self.light = self.light_NP.node()
        quad.instanceTo(self.light_NP)

    def initShaderInput(self):
    # 设置 shader 中的参数
        self.NodePath.setShaderInput("DirectionalLight.color", self.light.getColor())
        self.NodePath.setShaderInput("DirectionalLight.specular", self.light.getSpecularColor())
        self.NodePath.setShaderInput("DirectionalLight.position", self.light.getDirection())
