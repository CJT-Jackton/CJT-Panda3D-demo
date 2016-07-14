#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: CJT
# Date: 2016/7/13

from panda3d.core import *
import math

class IWPointLight(PandaNode):
# 自定义点光源
    def __init__(self, name, sphere):
        PandaNode.__init__(self, name)
        self.NodePath = NodePath(self)
        self.light_NP = self.NodePath.attachNewNode(PointLight("point light"))
        self.light = self.light_NP.node()
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
