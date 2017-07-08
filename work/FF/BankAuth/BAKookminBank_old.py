# -*- coding: utf-8 -*-
import os, sys
import re
import traceback

from PIL import Image
from PIL import ImageChops

from selenium import webdriver

from BAUtils import decodeThis
from BAUtils import VKClick,VKClickPos

import time

regex = "^[a-zA-Z]"

VK_size = (692,297)
VK_COORDS_CHANGE = [(577,120),(529,170),(577,170),(625,170),(577,220)]
VK_COORDS_UNCHANGE = {
                        "0" : {
                            "Q":(22,70),"W":(70,70),"E":(118,70),"R":(166,70),"T":(214,70),"Y":(262,70),"U":(310,70),"I":(358,70),"O":(406,70),"P":(454,70),
                            },
                        "1": {
                            "A":(42,170),"S":(90,170),"D":(138,170),"F":(186,170),"G":(234,170),"H":(282,170),"J":(330,170),"K":(378,170),"L":(426,170)
                            },
                        "2": {
                            "Z":(22,220),"X":(70,220),"C":(118,220),"V":(166,220),"B":(214,220),"N":(262,220),"M":(310,220),"#":(358,220),
                            },
                        "numkey": {
                            "1":(529,70),"2":(577,70),"3":(625,70),"4":(529,120),"6":(625,120),
                            }
                    }
my_dir = os.path.dirname(os.path.realpath(__file__))
res_dir = my_dir+"/BAKookminBankRes"
VK_res_dir = my_dir+"/BAKookminBankRes/VK"

TEMPCSCFILE1="BAKookminBankTempCSC1.png"
#VK_res_dir="BAKookminBankRes"


def login_attempt(url, job_info, creds_encoded=True):

    #decode creds if creds are encodede decode it or pass it
    (creds_decoded,e_msg,tb_msg,e_obj) = decode_creds(job_info, creds_encoded)

    if e_msg is not "OK":
        return (None,e_msg,tb_msg,e_obj)

    #verify inputs
    (dummy,e_msg,tb_msg,e_obj) = verify_inputs(creds_decoded)

    if e_msg is not "OK":
        return (None,e_msg,tb_msg,e_obj)

    #create webdriver
    (driver,e_msg,tb_msg,e_obj)=create_webdriver(url)

    if e_msg is not "OK":
        return (None,e_msg,tb_msg,e_obj)

    #find user id form to send keys
    (driver,e_msg,tb_msg,e_obj) = login_form_input_id(driver, creds_decoded)

    if e_msg is not "OK":
        return (None,e_msg,tb_msg,e_obj)

    #click PW form to show virtual keyboard
    (driver,e_msg,tb_msg,e_obj) =  login_form_input_pw(driver, creds_decoded)

    if e_msg is not "OK":
        return (None,e_msg,tb_msg,e_obj)

    #submit and complete login
    #(driver,e_msg,tb_msg,e_obj) = submit(driver)

    if e_msg is not "OK":
        return (None,e_msg,tb_msg,e_obj)

    e_msg="OK"
    return (driver,e_msg,tb_msg,e_obj)

def submit(driver):
    try:
        submit_btn = driver.find_element_by_id("idLoginBtn")
        submit_btn.click()
    except:
        e_msg = "ERROR_SOMETHING_WRONG_IN_SUBMIT"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)
    print "login complete"
    e_msg="OK"
    return (driver,e_msg,None,None)

def login_form_input_pw(driver, creds_decoded):
    try:
        elemPW = driver.find_element_by_id("LoginPassword")
        elemPW.click()

    except:
        e_msg = "ERROR_RETRIABLE_Could Not Click Pw Check Box"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    try:
        print "handle vkey"
        elem_vkey_div_container = driver.find_element_by_id("div_keypad")
        elem_vkey_div = elem_vkey_div_container.find_element_by_xpath("//div[starts-with(@id,'dKpd')]")
        elem_vkey_img = elem_vkey_div.find_element_by_xpath("//img[starts-with(@id,'dKpd')]")

        bboxPWD=(elem_vkey_img.location['x'], ##left
                 elem_vkey_img.location['y'], ##top
                 elem_vkey_img.location['x']+elem_vkey_img.size['width'], ##right
                 elem_vkey_img.location['y']+elem_vkey_img.size['height'], ##right
                    )
    except:
        e_msg = "ERROR_RETRIABLE_could not find virtual keyboard.."
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    if elem_vkey_img.size['width'] != VK_size[0] or elem_vkey_img.size['height'] != VK_size[1]:
        e_msg = "ERROR_RETRIABLE_virtual keyboard size mismatch.. it did not popup"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    elem_vkey_areas = elem_vkey_div.find_elements_by_tag_name("area")

    cur_vkey_ypos_array= []
    for elem_vkey_area in elem_vkey_areas:
        coords_str =  elem_vkey_area.get_attribute("coords")
        coords_l = int(coords_str.split(",")[0])
        coords_u = int(coords_str.split(",")[1])
        if coords_l == 22 or coords_l == 42:
            cur_vkey_ypos_array.append(coords_u)

    cur_vkey_ypos_array.sort()
    if len(cur_vkey_ypos_array) != 3:
        ##TODO: error handle
        raise

    cur_vkey_ypos = {}
    for i in range(len(cur_vkey_ypos_array)):
        cur_vkey_ypos[str(i)] = cur_vkey_ypos_array[i]

    #print cur_vkey_ypos
    #sys.exit()


    try:
        driver.save_screenshot(TEMPCSCFILE1)
        cSC=Image.open(TEMPCSCFILE1).crop(bboxPWD)
        cSC.save("cSC_error.png")

    except:
        e_msg = "ERROR_RETRIABLE_error_in_saving_screenshot"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    #creds_decoded['cred_user_pw'] = "WSX"
    for accpw in creds_decoded['cred_user_pw']:
        sc = accpw

        (driver,e_msg,tb_msg,e_obj) = input_vkey(driver, sc, cSC, cur_vkey_ypos, elem_vkey_areas)

        if e_msg is not "OK":
            return (None,e_msg,tb_msg,e_obj)


    e_msg="OK"
    print "input pw is done"
    return (driver,e_msg,None,None)

def input_vkey(driver, sc, cSC, cur_vkey_ypos, elem_vkey_areas):

    print "try to input : ", sc

    if re.match("[05789]",sc):

        refimg = Image.open(VK_res_dir+"/"+"kookmin_vkey_"+sc+".png").convert(mode="RGB")
        found = False
        for coord in VK_COORDS_CHANGE:
            tgtbox = (coord[0],coord[1],coord[0]+45,coord[1]+45)
            tgtimg = cSC.crop(tgtbox).convert(mode="RGB")
            if ImageChops.difference(refimg,tgtimg).getbbox() is None:

                coords_str = str(tgtbox[0])+","+str(tgtbox[1])+","+str(tgtbox[2])+","+str(tgtbox[3])
                print "found:", sc, coords_str
                for elem_vkey_area in elem_vkey_areas:
                    if elem_vkey_area.get_attribute("coords") == coords_str:
                        found = True
                        script = elem_vkey_area.get_attribute("onmousedown")
                        driver.execute_script(script)
        if not found:
            raise
    else:
        for row_key in VK_COORDS_UNCHANGE:
            row_dict = VK_COORDS_UNCHANGE[row_key]
            if sc in row_dict.keys():
                if row_key != "numkey":
                    key_pos = (row_dict[sc][0],cur_vkey_ypos[row_key],row_dict[sc][0]+45,cur_vkey_ypos[row_key]+45)
                else:
                    key_pos = (row_dict[sc][0],row_dict[sc][1],row_dict[sc][0]+45,row_dict[sc][1]+45)
                coords_str = str(key_pos[0])+","+str(key_pos[1])+","+str(key_pos[2])+","+str(key_pos[3])
                for elem_vkey_area in elem_vkey_areas:
                    if elem_vkey_area.get_attribute("coords") == coords_str:
                        found = True
                        script = elem_vkey_area.get_attribute("onmousedown")
                        driver.execute_script(script)

    e_msg="OK"
    print "input " + sc + " is OK"
    return (driver,e_msg,None,None)



def login_form_input_id(driver, creds_decoded):
    try:
        elem_user_id_form = driver.find_element_by_id("txtWWWBnkgLginID")
    except:
        e_msg = "ERROR_RETRIABLE_Could Not Find username input box"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    try:
        elem_user_id_form.click()
        elem_user_id_form.send_keys(creds_decoded['cred_user_id'])
    except:
        e_msg = "ERROR_RETRIABLE_Could Not Enter username"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    e_msg = "OK"
    print "find login form and enter id is done"
    return (driver,e_msg,None,None)



def create_webdriver(url):
    try:
        profile = webdriver.FirefoxProfile()
        #user_agent = "Mozilla/5.0 (Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_0_1 like Mac OS X; fr-fr) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5G77 Safari/525.20"
        user_agent = "Mozilla/5.0(iPhone;U;CPUiPhoneOS4_0likeMacOSX;en-us)AppleWebKit/532.9(KHTML,likeGecko)Version/4.0.5Mobile/8A293Safari/6531.22.7"

        profile.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(profile)
        driver.implicitly_wait(10)

        driver.maximize_window()
        driver.get(url)
    except:
        e_msg = "ERROR_RETRIABLE_could_not_create_webdriver"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (None,e_msg,tb_msg,e_obj)

    e_msg="OK"
    print "create webdriver is done"
    return (driver,e_msg,None,None)


def verify_inputs(creds_decoded):
    pw = creds_decoded['cred_user_pw']

    if re.match("[^A-Z0-9#]",pw):
        e_msg = "ERROR_DO_NOT_RETRY_pw_contains_invaild_character"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (None,e_msg,tb_msg,e_obj)
    else:
        e_msg="OK"
        return (None,e_msg,None,None)

def decode_creds(job_info,creds_encoded):
    if creds_encoded:
        try:
            creds_decoded = decodeThis(job_info['creds'],job_info['user_id'])
        except:
            e_msg = "ERROR_DO_NOT_RETRY_could_not_decode_credentials"
            tb_msg = traceback.format_exc()
            e_obj = sys.exc_info()
            return (None,e_msg,tb_msg,e_obj)
    else:
        creds_decoded = job_info['creds']

    e_msg="OK"
    print "decode cred is done"
    return (creds_decoded,e_msg,None,None)

def login(url,job_info,creds_encoded=True):

    wrong_site_count = 0

    for t in range(10):
        (driver,e_msg,tb_msg,e_obj) = login_attempt(url,job_info,creds_encoded)
        if e_msg == "OK":
            return (driver,e_msg,tb_msg,e_obj)
        elif "ERROR_DO_NOT_RETRY" in e_msg:
            return (None,e_msg,tb_msg,e_obj)
        else:
            print e_msg
            print tb_msg
            print "retriable error.. retrying..", t
            if e_msg == "ERROR_RETRIABLE_Could Not Find Account Number":
                wrong_site_count += 1

    if wrong_site_count >= 9:
        return (None,"ERROR_DO_NOT_RETRY_WRONG_SITE",tb_msg,e_obj)

    return (None,"ERROR_DO_NOT_RETRY_MAXIMUM_LOGIN_RETRY_EXCEEDED",tb_msg,e_obj)


if __name__ == "__main__":
    url = "https://obank1.kbstar.com/quics?page=C018897&QViewPC=Y"

    (driver,e_msg,tb_msg,e_obj) = login(url,{'creds':{'cred_user_id':'zakk95','cred_user_pw':'TPSXL40'}},creds_encoded=False)
    print e_msg
