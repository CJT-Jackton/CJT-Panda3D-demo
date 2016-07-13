# This is the config file used to configure basic settings for Panda3D.
# The pipeline loads it at startup to ensure the environment is setup properly.

# 游戏默认配置文件
# default config file

# ---------- Windows Options ----------

# 窗口标题
window-title The Game

# 默认分辨率
win-size 1280 720

# 图标文件
icon-filename resources/portal2.ico

# ---------- Misc Settings ----------

# 全屏显示
fullscreen #f

# 垂直同步
sync-video #f

# 显示帧数
show-frame-rate-meter #t

# 隐藏鼠标指针
cursor-hidden #t

# Disable the buffer viewer
show-buffers #f

# 截图文件格式
screenshot-extension png

# ---------- Graphics Settings ----------

# 纹理过滤等级，决定纹理的清晰程度
#
# 1 - 双线性过滤:
#     texture-magfilter linear
#     texture-minfilter linear
#     texture-anisotropic-degree 1
#
# 2 - 三线性过滤:
#     texture-magfilter linear
#     texture-minfilter linear-mipmap-linear
#     texture-anisotropic-degree 1
#
# 3 - 各向异性过滤 x2:
#     texture-magfilter linear
#     texture-minfilter linear
#     texture-anisotropic-degree 2
#
# 4 - 各向异性过滤 x4:
#     texture-magfilter linear
#     texture-minfilter linear
#     texture-anisotropic-degree 4
#
# 5 - 各向异性过滤 x8:
#     texture-magfilter linear
#     texture-minfilter linear
#     texture-anisotropic-degree 8
#
# 6 - 各向异性过滤 x16:
#     texture-magfilter linear
#     texture-minfilter linear
#     texture-anisotropic-degree 16

texture-magfilter linear
texture-minfilter linear
texture-anisotropic-degree 1

# This specifies a global quality level for all textures
#texture-quality-level fastest

# Don't use srgb correction
# 在最后手动做gamma校正
framebuffer-srgb #f

# Don't use multisamples
# 我们使用FXAA、SMAA两种后处理抗锯齿技术
framebuffer-multisample #f
multisamples 0

# Don't rescale textures which are no power-of-2
textures-power-2 none

# ---------- OpenGL / Performance Settings ----------

# Use the default coordinate system, this makes our matrix transformations
# faster because we don't have have to transform them to a different coordinate
# system before
#gl-coordinate-system default

# 使用硬件自动生成 mipmap
driver-generate-mipmaps #t
