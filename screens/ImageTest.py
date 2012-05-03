import datetime
import os
import socket
import psutil
from tx_g15.g15_img_screen import G15PicScreen, G15GifScreen
from tx_g15.g15_screen_mixins import LoopingCallMixin

class ImageTest(G15PicScreen):
    def __init__(self, *a, **kw):
        G15PicScreen.__init__(self, *a, **kw)
        self.loadImage("/home/e/ae.png")

class GifTest(G15GifScreen):
    def __init__(self, *a, **kw):
        G15GifScreen.__init__(self, *a, **kw)
        self.loadImage("/home/e/Dropbox/Programming/Python/pyg15/g15twisted/test2.gif")