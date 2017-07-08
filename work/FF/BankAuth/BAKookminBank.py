# -*- coding: utf-8 -*-
import os
import re,time
import traceback

from PIL import Image
from PIL import ImageChops

from selenium import webdriver

from BAUtils import decodeThis
from BAConfig import DEFAULT_RETRY_COUNT

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoAlertPresentException

from Comm import Comm

VK_SIZE = (692,297)
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

DIR = os.path.dirname(os.path.realpath(__file__))
RES_DIR = DIR + "/BAKookminBankRes"
VK_RES_DIR = DIR + "/BAKookminBankRes/VK"

SCREENSHOT = "BAKookminBank_Monitor.png"


def login_attempt(comm):

    #decode creds if creds are encodede decode it or pass it
    comm = decode_creds(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

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
    comm = login_form_input_pw(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

    #submit and complete login
    comm = submit(comm)

    if not comm.last_e_msg.startswith("OK"):
        return comm

    comm.last_e_msg = "OK"
    return comm


def decode_creds(comm):
    #print "isEncoded", comm.isEncoded
    if comm.isEncoded:
        try:
            cred_decoded = decodeThis(comm.job_info['creds'], comm.job_info['user_id'])
            comm.set_attr(cred_decoded=cred_decoded)
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

    id = id.upper()
    comm.cred_decoded["id"] = id

    if len(id) < 6 or len(id) > 12:
        comm.add_err("ERROR_DO_NOT_RETRY_length_of_id_is_wrong")
        return comm

    if len(pw) < 6 or len(pw) > 12:
        comm.add_err("ERROR_DO_NOT_RETRY_length_of_pw_is_wrong")
        return comm

    filter = re.compile("[^A-Z0-9]")

    if filter.search(pw):
        comm.add_err("ERROR_DO_NOT_RETRY_pw_contains_invaild_character")
        return comm
    elif filter.search(id):
        comm.add_err("ERROR_DO_NOT_RETRY_id_contains_invaild_character")
        return comm
    else:
        comm.logger.error("verify input is done")
        comm.set_attr(last_e_msg="OK")
        return comm


def create_webdriver(comm):

    try:
        #user agent should be configurable per bank module

        user_agent = "Mozilla/5.0(iPhone;U;CPUiPhoneOS4_0likeMacOSX;en-us)AppleWebKit/532.9(KHTML,likeGecko)Version/4.0.5Mobile/8A293Safari/6531.22.7"

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(profile)
        comm.set_attr(driver=driver)

        comm.driver.maximize_window()
        comm.driver.get(comm.url)
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'txtWWWBnkgLginID')))

    except:
        comm.add_err("ERROR_RETRIABLE_could_not_create_webdriver", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("create webdriver is done")
    return comm


def login_form_input_id(comm):

    try:
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'txtWWWBnkgLginID')))
        elem_user_id_form = comm.driver.find_element_by_id("txtWWWBnkgLginID")
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_found_id_form", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        elem_user_id_form.click()
        elem_user_id_form.send_keys(comm.cred_decoded['cred_user_id'])
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_enter_id", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("input id is done")
    return comm


def login_form_input_pw(comm):

    #click pw form
    try:

        elem_idpw_input_box = comm.driver.find_element_by_id("login_box_idpw")
        elem_inputs = elem_idpw_input_box.find_elements_by_tag_name("input")

        if elem_inputs[3].is_selected():
            comm.driver.find_element_by_id("LoginPassword").click()
        else:
            elem_inputs[3].click()

    except:
        comm.add_err("ERROR_RETRIABLE_could_not_click_pw_form", tb_msg=traceback.format_exc(), SC=True)
        return comm

    #get vkey elem img and bbox size tuple
    try:
        WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, 'div_keypad')))
        elem_vkey_div_wrap = comm.driver.find_element_by_id("div_keypad")
        elem_vkey_div = elem_vkey_div_wrap.find_element_by_xpath("//div[starts-with(@id,'dKpd')]")
        elem_vkey_img = elem_vkey_div.find_element_by_xpath("//img[starts-with(@id,'dKpd')]")

        bboxPWD = (elem_vkey_img.location['x'], #left
                 elem_vkey_img.location['y'], #top
                 elem_vkey_img.location['x'] + elem_vkey_img.size['width'], #right
                 elem_vkey_img.location['y'] + elem_vkey_img.size['height'], #right
                    )
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_found_vkey", tb_msg=traceback.format_exc(), SC=True)
        return comm

    #if elem_vkey_img.size['width'] != VK_SIZE[0] or elem_vkey_img.size['height'] != VK_SIZE[1]:
    #    comm.add_err("ERROR_RETRIABLE_vksize_mismatch", tb_msg=traceback.format_exc(), SC=True)
    #    return comm

    elem_vkey_areas = elem_vkey_div.find_elements_by_tag_name("area")

    cur_vkey_ypos_array = []
    for elem_vkey_area in elem_vkey_areas:
        coords_str = elem_vkey_area.get_attribute("coords")
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

    try:
        comm.driver.save_screenshot(SCREENSHOT)
        vkey_sc = Image.open(SCREENSHOT).crop(bboxPWD)
        vkey_sc.save("KookminBank_vkey.png")
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_saving_screenshot", tb_msg=traceback.format_exc(), SC=True)
        return comm

    #creds_decoded['cred_user_pw'] = "WSX"
    for pw in comm.cred_decoded['cred_user_pw']:
        comm = input_vkey(comm, vkey_sc, cur_vkey_ypos, elem_vkey_areas, pw)

        if not comm.last_e_msg.startswith("OK"):
            return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("input pw is done")
    return comm


def input_vkey(comm, vkey_sc, cur_vkey_ypos, elem_vkey_areas, pw):

    try:
        found = False
        if re.match("[05789]", pw):
            refimg = Image.open(VK_RES_DIR + "/" + "kookmin_vkey_" + pw + ".png").convert(mode="RGB")
            for coord in VK_COORDS_CHANGE:
                tgtbox = (coord[0], coord[1], coord[0] + 45, coord[1] + 45)
                tgtimg = vkey_sc.crop(tgtbox).convert(mode="RGB")
                if ImageChops.difference(refimg, tgtimg).getbbox() is None:
                    coords_str = str(tgtbox[0]) + "," + str(tgtbox[1]) + "," + str(tgtbox[2]) + "," + str(tgtbox[3])
                    for elem_vkey_area in elem_vkey_areas:
                        if elem_vkey_area.get_attribute("coords") == coords_str:
                            found = True
                            script = elem_vkey_area.get_attribute("onmousedown")
                            comm.driver.execute_script(script)
        else:
            for row_key in VK_COORDS_UNCHANGE:
                row_dict = VK_COORDS_UNCHANGE[row_key]
                if pw in row_dict.keys():
                    if row_key != "numkey":
                        key_pos = (row_dict[pw][0], cur_vkey_ypos[row_key], row_dict[pw][0] + 45, cur_vkey_ypos[row_key] + 45)
                    else:
                        key_pos = (row_dict[pw][0], row_dict[pw][1], row_dict[pw][0] + 45, row_dict[pw][1] + 45)

                    coords_str = str(key_pos[0]) + "," + str(key_pos[1]) + "," + str(key_pos[2]) + "," + str(key_pos[3])
                    for elem_vkey_area in elem_vkey_areas:
                        if elem_vkey_area.get_attribute("coords") == coords_str:
                            found = True
                            script = elem_vkey_area.get_attribute("onmousedown")
                            comm.driver.execute_script(script)

        if not found:
            comm.add_err("ERROR_RETRIABLE_could_not_found_key", tb_msg=traceback.format_exc(), SC=True)
            return comm
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_press_key", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm


def submit(comm):

    try:
        submit_btn = comm.driver.find_element_by_id("idLoginBtn")
        submit_btn.click()
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_submit", tb_msg=traceback.format_exc(), SC=True)
        return comm

    time.sleep(3)

    while True:
        try:
            alert = comm.driver.switch_to_alert()
            alert.dismiss()
        except NoAlertPresentException:
            break

    try:
        window_origin = comm.driver.window_handles[0]
        for window in comm.driver.window_handles[1:]:
            comm.driver.switch_to_window(window)
            comm.driver.close()
            time.sleep(0.1)

        comm.driver.switch_to_window(window_origin)
    except:
        pass

    try:
        comm.driver.find_element_by_id("LOGIN_PAGE_FORM")
    except:
        try:
            err = comm.driver.find_element_by_id("errMsg")
            err_msg = err.__getattribute__("text").encode('utf-8')
            if "인터넷뱅킹ID를 확인바랍니다." in err_msg:
                comm.add_err("ERROR_DO_NOT_RETRY_wrong_id", SC=True)
                return comm
            elif "사용자암호 입력오류입니다." in err_msg:
                comm.add_err("ERROR_DO_NOT_RETRY_wrong_pw", SC=True)
                return comm
            else:
                comm.add_err("ERROR_DO_NOT_RETRY_unknown_error_"+err_msg, SC=True)
                return comm
        except:
            comm.add_err("ERROR_DO_NOT_RETRY_unknown_error", SC=True)
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
            try:
                if comm.driver is not None:
                    comm.driver.quit()
                    comm.driver = None
            except:
                comm.add_err("ERROR_DO_NOT_RETRY_problem_in_webdriver", tb_msg=traceback.format_exc(), SC=True)
                return comm
            return comm
        else:
            time.sleep(100)
            try:
                if comm.driver:
                    comm.driver.quit()
                    comm.driver = None
            except:
                comm.add_err("ERROR_DO_NOT_RETRY_problem_in_webdriver", tb_msg=traceback.format_exc(), SC=True)
                return comm

    try:
        if comm.driver:
            comm.driver.quit()
            comm.driver = None
    except:
        comm.add_err("ERROR_DO_NOT_RETRY_problem_in_webdriver", tb_msg=traceback.format_exc(), SC=True)
        return comm

    return comm

if __name__ == "__main__":

    job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'TPSXL40','cred_acc_no':'46543138745124'}}
    comm = Comm(job_info)
    comm.set_attr(url="https://obank1.kbstar.com/quics?page=C018897&QViewPC=Y", isEncoded=False)
    comm = login(comm)

    print comm.last_e_msg


