import binascii
import ctypes
import json
import sys
import time
import traceback
import urllib

from Crypto.PublicKey import RSA
from PIL import Image
from PIL import ImageChops
from selenium import webdriver

import BAConfig


def VKClick(driver,offsetElem,cSC,vk_res_dir,to_click):
    try:
        cbmp = Image.open(vk_res_dir+"/"+str(to_click)+".png")
        point =  searchSubImg(cbmp,cSC)
        if not point:
            print "subImg Not Found," + str(to_click)
            cbmp.save("cbmp_error.png")
            cSC.save("cSC_error.png")
            e_msg = "ERROR_RETRIABLE_subImg Not Found, accpw"
            tb_msg = traceback.format_exc()
            e_obj = sys.exc_info()
            return (e_msg,tb_msg,e_obj)
        print to_click, point[0], point[1]
        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(offsetElem, point[0]+3 , point[1]+3)
        action.click()
        action.perform()
        time.sleep(0.5)
        return ("OK",None,None)
    except:

        e_msg = "ERROR_RETRIABLE_error_clicking_character"+str(to_click)
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (e_msg,tb_msg,e_obj)
    
def VKClickPos(driver,offsetElem,point):
    try:
        print  "clickpos:" , point[0], point[1]
        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(offsetElem, point[0]+5 , point[1]+5)
        action.click()
        action.perform()
        time.sleep(0.5)
        return ("OK",None,None)
    except:
        e_msg = "ERROR_RETRIABLE_error_clicking_character"+str(to_click)
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (e_msg,tb_msg,e_obj)
    

def getPrvkey(user_id):
    ##TODO: implement per-user private key
    try:
        prvkey_json = urllib.urlopen(BAConfig.GET_PRVKEY_URL).read()
        prvkey_dict = json.loads(prvkey_json)
        return prvkey_dict['prvkey']
    except:
        return None

def decodeThis(emsgs_dict,user_id):
    prvkey = getPrvkey(user_id)
    if prvkey is None:
        return None
    prvkeyObj = RSA.importKey(prvkey)
    dmsgs_dict = {}
    for k in emsgs_dict:
        emsg = emsgs_dict[k]
        dmsgs_dict[k] = prvkeyObj.decrypt(binascii.unhexlify(emsg))
        
    return dmsgs_dict

def moveAbsPos(x,y):
    ctypes.windll.user32.SetCursorPos(x, y)

def clickAbsPos(x,y):
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0,0) # left down
    time.sleep(0.1)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0,0) # left up
    
def searchSubImg(smallImg,bigImg,method="exact"):
    found = False
    for j in range(0,bigImg.height):
        for i in range(0,bigImg.width):
            left = i
            top = j
            right  = left + smallImg.width
            bottom = top + smallImg.height
            scanImg = bigImg.crop((left,top,right,bottom))
            if ImageChops.difference(smallImg,scanImg).getbbox() is None:
                #print "found!", i, j
                found = True
                break
        if found:
            break
    if not found:
        return None

    return (i,j)


