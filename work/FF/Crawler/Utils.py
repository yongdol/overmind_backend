# -*- coding: cp949 -*-

import ctypes
from PIL import Image
from PIL import ImageGrab
from PIL import ImageChops

def wonToDigit(raw,asInt=False):
    digitstr = raw.replace("원".decode('cp949'),"").replace(",","").strip()
    if asInt:
        return int(digitstr)
    return digitstr
