#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Author: CJT
# Date: 2016/7/13

from panda3d.core import *
import math

class IWSpotlight(PandaNode):
# 自定义聚光灯
    def __init__(self, name, cone):
        PandaNode.__init__(self, name)
        self.NodePath = NodePath(self)
        self.light_NP = self.NodePath.attachNewNode(Spotlight("spotlight"))
        self.light = self.light_NP.node()
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
