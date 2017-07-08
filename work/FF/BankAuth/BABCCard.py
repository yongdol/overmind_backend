# -*- coding: utf-8 -*-

import os,sys,time,re
import traceback,logging

from BAUtils import decodeThis
from BAConfig import DEFAULT_RETRY_COUNT
from Comm import Comm

from PIL import Image
from PIL import ImageChops

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException,NoAlertPresentException

# webdriver setting
CHROMEDRIVER = "../../lib/webdriver/bin/chromedriver"
GECKODRIVER = "../../lib/webdriver/bin/geckodriver"
os.environ["webdriver.chrome.driver"] = CHROMEDRIVER
os.environ["webdriver.firefox.driver"] = GECKODRIVER

TOGGLE_DICT = {"l":(547,278),"u":(598,278),"s":(649,278)}

SCREENSHOT = "BABCCard_Monitor.png"

DIR = os.path.dirname(os.path.realpath(__file__))
RES_DIR = DIR + "/BABCCardRes"
VK_RES_DIR = DIR + "/BABCCardRes/VK"

ROW_1 = 0
ROW_2 = 0
ROW_3 = 0
VK_COORDS_CHANGE = [(598,125),(547,176),(598,176),(649,176),(598,227)]
VK_COORDS_CHANGE_CHECKED = {}
VK_COORDS_LOWER = {}
VK_COORDS_UPPER = {}
VK_COORDS_SPECIAL = {}


def login_attempt(comm):

    #decode creds if creds are encodede decode it or pass it
    comm = decode_creds(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

    #verify inputs
    comm = verify_inputs(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

    #create webdriver
    comm = create_webdriver(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

    #find user id form to send keys
    comm = login_form_input_id(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

    #click PW form to show virtual keyboard
    comm =  login_form_input_pw(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

    #submit and complete login
    comm = submit(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

    comm.last_e_msg = "OK"
    return comm

def decode_creds(comm):
    if comm.isEncoded:
        try:
            comm.set_attr(cred_decoded=decodeThis(comm.job_info['creds'], comm.job_info['user_id']))
        except:
            comm.add_err("ERROR_DO_NOT_RETRY_could_not_decode_cred", tb_msg=traceback.format_exc())
            return comm
    else:
        comm.set_attr(cred_decoded=comm.job_info['creds'])

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("decode cred is done" + str(comm.cred_decoded))
    return comm

def verify_inputs(comm):

    id = comm.cred_decoded['cred_user_id']
    pw = comm.cred_decoded['cred_user_pw']

    if len(id) == 0:
        comm.add_err("ERROR_DO_NOT_RETRY_length_of_id_is_wrong")
        return comm

    if len(pw) == 0:
        comm.add_err("ERROR_DO_NOT_RETRY_length_of_pw_is_wrong")
        return comm

    comm.logger.error("verify input is done")
    comm.set_attr(last_e_msg="OK")
    return comm

def create_webdriver(comm):

    try:
        user_agent = """
                   Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us)
                   AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16
                   """
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(firefox_profile=profile, executable_path=GECKODRIVER)

        # Extensions
        INI_path = '../../lib/extensions/1.0.1.12_0.crx'

        #chrome_options = Options()
        #chrome_options.add_extension(INI_path)

        # ChromeDriver Settings
        #driver = webdriver.Chrome(executable_path=CHROMEDRIVER, chrome_options=chrome_options)

        comm.set_attr(driver=driver)
        comm.driver.set_window_size(1600, 900)
        comm.driver.get(comm.url)

    except:
        comm.add_err("ERROR_RETRIABLE_could_not_create_webdriver", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("create webdriver is done")
    return comm

def login_form_input_id(comm):

    try:
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'login')))
        elem_login_link = comm.driver.find_element_by_class_name("login")
        elem_login_link.click()
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_found_login_link", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'loginId')))
        elem_user_id_form = comm.driver.find_element_by_id("loginId")
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_found_id_form", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        #elem_user_id_form.click()
        elem_user_id_form.send_keys(comm.cred_decoded['cred_user_id'])
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_enter_id", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("input id is done")
    return comm

def login_form_input_pw(comm):

    try:
        elem_login_link = comm.driver.find_element_by_id("loginPw")
        elem_login_link.click()
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_found_pw_form", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        elem_key_pad = comm.driver.find_element_by_id("DIV_KEYPAD")
        elem_vkey_imgs = elem_key_pad.find_elements_by_tag_name("img")
        bboxPWD = (elem_vkey_imgs[0].location['x'], #left
                 elem_vkey_imgs[0].location['y'], #top
                 elem_vkey_imgs[0].location['x'] + elem_vkey_imgs[0].size['width'], #right
                 elem_vkey_imgs[0].location['y'] + elem_vkey_imgs[0].size['height'], #right
                    )
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_found_vkey", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        comm.driver.save_screenshot(SCREENSHOT)
        vkey_sc = Image.open(SCREENSHOT).crop(bboxPWD)
        vkey_sc.save("BCCard_vkey.png")
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_saving_screenshot", tb_msg=traceback.format_exc(), SC=True)
        return comm

    vk_change = [0,5,7,8,9]
    try:
        for vk in vk_change:
            refimg = Image.open(VK_RES_DIR + "/" + "BCCard_vkey_" + str(vk) + ".png").convert(mode="RGB")

            for coord in VK_COORDS_CHANGE:
                tgtbox = (coord[0], coord[1], coord[0] + 45, coord[1] + 45)
                tgtimg = vkey_sc.crop(tgtbox).convert(mode="RGB")

                if ImageChops.difference(refimg, tgtimg).getbbox() is None:
                    VK_COORDS_CHANGE_CHECKED[str(vk)] = coord
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_check_vk_mark", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        for i in [1, 2, 3, 4, 5]:
            refimg = Image.open(RES_DIR + "/" + "BCCard_vkey_" + str(i) + ".png")

            size = (0,0,500,260)

            print ImageChops.difference(refimg.crop(size), vkey_sc.crop(size)).getbbox()

            if ImageChops.difference(refimg.crop(size), vkey_sc.crop(size)).getbbox() is None:
                global ROW_1
                global ROW_2
                global ROW_3

                if i == 1:
                    ROW_1 = 125
                    ROW_2 = 176
                    ROW_3 = 227
                elif i == 2:
                    ROW_1 = 74
                    ROW_2 = 176
                    ROW_3 = 227
                elif i == 3:
                    ROW_1 = 74
                    ROW_2 = 125
                    ROW_3 = 227
                elif i == 4 or i == 5:
                    ROW_1 = 74
                    ROW_2 = 125
                    ROW_3 = 176
                break
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_check_vk", tb_msg=traceback.format_exc(), SC=True)
        return comm

    global VK_COORDS_SPECIAL, VK_COORDS_LOWER, VK_COORDS_UPPER

    VK_COORDS_LOWER = {
                    "q": [23,ROW_1],"w":[74,ROW_1],"e":[125,ROW_1],"r":[176,ROW_1],"t":[227,ROW_1],"y":[278,ROW_1],"u":[329,ROW_1],"i":[380,ROW_1],"o":[431,ROW_1],"p":[482,ROW_1],
                    "a": [49, ROW_2], "s": [100,ROW_2],"d":[151,ROW_2],"f":[202,ROW_2],"g":[253,ROW_2],"h":[304,ROW_2],"j":[355,ROW_2],"k":[406,ROW_2],"l":[457,ROW_2],
                    "z":[74,ROW_3],"x":[125,ROW_3],"c":[176,ROW_3],"v":[227,ROW_3],"b":[278,ROW_3],"n":[329,ROW_3],"m":[380,ROW_3],
                    "1":[547,74],"2":[598,74],"3":[649,74],"4":[547,125],"6":[649,125]
                }
    VK_COORDS_UPPER = {
                    "Q":[23,ROW_1],"W":[74,ROW_1],"E":[125,ROW_1],"R":[176,ROW_1],"T":[227,ROW_1],"Y":[278,ROW_1],"U":[329,ROW_1],"I":[380,ROW_1],"O":[431,ROW_1],"P":[482,ROW_1],
                    "A":[49,ROW_2],"S":[100,ROW_2],"D":[151,ROW_2],"F":[202,ROW_2],"G":[253,ROW_2],"H":[304,ROW_2],"J":[355,ROW_2],"K":[406,ROW_2],"L":[457,ROW_2],
                    "Z":[74,ROW_3],"X":[125,ROW_3],"C":[176,ROW_3],"V":[227,ROW_3],"B":[278,ROW_3],"N":[329,ROW_3],"M":[380,ROW_3],
                    "1":[547,74],"2":[598,74],"3":[649,74],"4":[547,125],"6":[649,125]
                }
    VK_COORDS_SPECIAL = {
                    "-":[23,ROW_1],"_":[74,ROW_1],"=":[125,ROW_1],"+":[176,ROW_1],"\\":[227,ROW_1],"|":[278,ROW_1],"{":[329,ROW_1],"}":[380,ROW_1],"[":[431,ROW_1],"]":[482,ROW_1],
                    ";":[49,ROW_2],":":[100,ROW_2],"'":[151,ROW_2],"\"":[202,ROW_2],",":[253,ROW_2],".":[304,ROW_2],"<":[355,ROW_2],">":[406,ROW_2],"$":[457,ROW_2],
                    "~":[74,ROW_3],"`":[125,ROW_3],"!":[176,ROW_3],"@":[227,ROW_3],"#":[278,ROW_3],"/":[329,ROW_3],"?":[380,ROW_3],
                    "%":[598,125],"^":[649,125],"&":[547,ROW_3],"*":[598,176],"(":[649,176],")":[598,227]
                }

    print ROW_1, ROW_2, ROW_3

    print VK_COORDS_LOWER, VK_COORDS_UPPER, VK_COORDS_SPECIAL

    for pw in comm.cred_decoded['cred_user_pw']:
        print "input >>", pw
        comm = input_pw(comm, pw)
        print "length is>>", len(elem_login_link.get_attribute("value"))

        if not comm.last_e_msg.startswith("OK"):
            return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("input pw is done")
    return comm


def input_pw(comm, pw):

    print "click>>",pw

    try:
        elem_div_keypad = comm.driver.find_element_by_id("DIV_KEYPAD")
        elem_divs = elem_div_keypad.find_elements_by_tag_name("div")
        elem_vkey_divs = elem_divs[2:]
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_find_vkey_divs", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        if re.match("[0-9a-z]", pw):      #lower case
            comm = toggle(comm, "l")
            for vk_key in VK_COORDS_LOWER:
                if vk_key == pw:
                    press(comm.driver,elem_vkey_divs[0],VK_COORDS_LOWER[vk_key])
                    break
            if re.match("[05789]", pw):
                press(comm.driver,elem_vkey_divs[0],VK_COORDS_CHANGE_CHECKED[pw])

        elif re.match("[0-9A-Z]", pw):    #upper case
            comm = toggle(comm, "u")
            for vk_key in VK_COORDS_UPPER:
                if vk_key == pw:
                    press(comm.driver,elem_vkey_divs[1],VK_COORDS_UPPER[vk_key])
                    break
            if re.match("[05789]", pw):
                press(comm.driver,elem_vkey_divs[0],VK_COORDS_CHANGE_CHECKED[pw])

        else:                               #special case
            comm = toggle(comm, "s")
            for vk_key in VK_COORDS_SPECIAL:
                if vk_key == pw:
                    press(comm.driver,elem_vkey_divs[2],VK_COORDS_SPECIAL[vk_key])
                    break
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_matching_pw", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm


def toggle(comm, flag):

    try:
        elem_div_keypad = comm.driver.find_element_by_id("DIV_KEYPAD")
        elem_divs = elem_div_keypad.find_elements_by_tag_name("div")
        elem_vkey_divs = elem_divs[2:]
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_find_vkey_divs", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        for vkey_div in elem_vkey_divs:
            if "display: block" in vkey_div.get_attribute("style").strip():
                press(comm.driver, vkey_div, TOGGLE_DICT[flag])
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_press_toggle_key", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm


def press(driver, offsetElem, point):

    print "try to click", point
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(offsetElem, point[0] + 5, point[1] + 5)
    action.click()
    action.perform()
    time.sleep(0.5)


def submit(comm):

    try:
        comm.driver.execute_script("javascript:sendPWD();")
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_click_login_btn", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'clock')))
    except:
        err = comm.driver.find_element_by_id("errorPage3")
        err_msg = err.__getattribute__("text").encode('utf-8')

        if "인터넷 회원으로 등록되어 있지 않습니다" in err_msg:
            comm.add_err("ERROR_DO_NOT_RETRY_wrong_id", SC=True)
            return comm
        elif "비밀번호 5회 이상 오류시,로그인이 차단됩니다" in err_msg:
            comm.add_err("ERROR_DO_NOT_RETRY_wrong_pw", SC=True)
            return comm
        else :
            comm.add_err("ERROR_DO_NOT_RETRY_unknown_error_" + err_msg, SC=True)
            return comm

    comm.set_attr(last_e_msg="OK")
    return comm


def login(comm):

    for t in range(DEFAULT_RETRY_COUNT):
        comm = login_attempt(comm)

        if comm.last_e_msg == "OK":
            comm.logger.error(">>>LOGIN IS SUCCESSFUL")
            return comm
        elif "ERROR_DO_NOT_RETRY" in comm.last_e_msg:
            time.sleep(10)
            try:
                if comm.driver:
                    comm.driver.quit()
                    comm.driver = None
            except:
                comm.add_err("ERROR_DO_NOT_RETRY_problem_in_webdriver",tb_msg=traceback.format_exc(),SC=True)
                return comm
            return comm
        else:
            time.sleep(10)
            try:
                if comm.driver:
                    comm.driver.quit()
                    comm.driver = None
            except:
                comm.add_err("ERROR_DO_NOT_RETRY_problem_in_webdriver",tb_msg=traceback.format_exc(),SC=True)
                return comm
    comm.add_err("ERROR_DO_NOT_RETRY_retrial_num_excess", tb_msg=traceback.format_exc())
    return comm

if __name__ == "__main__":

    job_info = {'creds':{'cred_user_id':'zakk95', 'cred_user_pw':'Tpsxl80@'}}
    comm = Comm(job_info=job_info)
    comm.set_attr(url = "https://www.bccard.com/app/card/MainActn.do",isEncoded=False)
    comm = login(comm)

    """
    flag = 1
    while True:

        if flag == 1:
            job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'Tpsxl80@'}}
        elif flag == 2:
            job_info = {'creds':{'cred_user_id':'zakk9512','cred_user_pw':'Tpsxl80@'}}  #id
        elif flag == 3:
            job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'Tpsxl80@ef1'}}  #pw

        comm = Comm(job_info=job_info)
        comm.set_attr(url = "https://www.bccard.com/app/card/MainActn.do",isEncoded=False)
        comm = login(comm)

        if flag <= 2:
            flag += 1
        else:
            flag = 1

        comm.logger.error("---------------------------------------------")
        comm.logger.removeHandler(comm.ch)
        comm.logger.removeHandler(comm.fh)
        del comm
        time.sleep(10)
        """