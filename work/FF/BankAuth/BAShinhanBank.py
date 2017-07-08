# -*- coding: utf-8 -*-
import os,sys
import re
import traceback
import time

from PIL import Image
from PIL import ImageChops

from BAUtils import decodeThis
from Comm import Comm
from BAConfig import DEFAULT_RETRY_COUNT

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoAlertPresentException

MY_DIR = os.path.dirname(os.path.realpath(__file__))
RES_DIR = MY_DIR+"/BAShinhanBankRes"
VK_RES_DIR = MY_DIR+"/BAShinhanBankRes/VK"

SCREENSHOT="BAShinhanBank_Monitor.png"

VK_LOWER = ["`","1","2","3","4","5","6","7","8","9","0",
            "q","w","e","r","t","y","u","i","o","p",
            "a","s","d","f","g","h","j","k",
            "z","x","c","v","b","n","m","l",
            "-","=","\\","[","]",";","'",",",".","/"]

VK_UPPER = ["~","!","@","#","$","%","^","&","*","(",")",
            "Q","W","E","R","T","Y","U","I","O","P",
            "A","S","D","F","G","H","J","K",
            "Z","X","C","V","B","N","M","L",
            "_","+","|","{","}",":",'"',"<",">","?"]

VK_LOWER_DICT = {}
VK_UPPER_DICT = {}

CAPS = False ##lower case


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
    comm.logger.error("decode cred is done"+str(comm.cred_decoded))
    return comm


def verify_inputs(comm):

    id = comm.cred_decoded['cred_user_id']
    pw = comm.cred_decoded['cred_user_pw']


    if len(id) > 20 or len(id) < 4:
        comm.add_err("ERROR_DO_NOT_RETRY_length_of_id_is_wrong")
        return comm

    if len(pw) > 20 or len(pw) < 4:
        comm.add_err("ERROR_DO_NOT_RETRY_length_of_pw_is_wrong")
        return comm
    """
    filter = re.compile("[^a-zA-Z0-9]")

    if filter.search(pw):
        comm.add_err("ERROR_DO_NOT_RETRY_pw_contains_invaild_character")
        return comm
    elif filter.search(id):
        comm.add_err("ERROR_DO_NOT_RETRY_id_contains_invaild_character")
        return comm
    else:
    """
    comm.logger.error("verify input is done")
    comm.set_attr(last_e_msg="OK")
    return comm


def create_webdriver(comm):
    try:
        user_agent = """Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) \
                     AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"""

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(profile)
        comm.set_attr(driver=driver)
        comm.driver.set_window_size(1600,900)
        #comm.driver.maximize_window()
        comm.driver.get(comm.url)

        count=0
        while True:
            try:
                comm.driver.switch_to_default_content()
                WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'bizMain')))
                comm.driver.switch_to.frame(driver.find_element_by_name("bizMain"))
                comm.driver.find_element_by_id("img_btn_오픈뱅킹로그인").click()

                print "count is>>>", count
                if count == 10:
                    comm.add_err("ERROR_RETRIABLE_could_not_go_to_login_page", tb_msg= traceback.format_exc(), SC=True)
                    return comm
                count += 1
                comm.driver.switch_to_default_content()
                WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'bizMain')))
                comm.driver.switch_to.frame(driver.find_element_by_name("bizMain"))
                WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'userID')))
                break
            except:
                pass
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_create_webdriver", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("create webdriver is done")
    return comm


def login_form_input_id(comm):

    try:
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'userID')))
        elem_user_id_form = comm.driver.find_element_by_id("userID")
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

    try:
        elem_pw_form = comm.driver.find_element_by_id('비밀번호')
        elem_pw_form.click()
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_found_pw_form", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        elem_vkey_img = comm.driver.find_element_by_id("tk_map_비밀번호")

        lower_vkey_div = comm.driver.find_element_by_id("비밀번호_layoutLower")
        lower_vkey_img = comm.driver.find_element_by_id("비밀번호_imgTwinLower")
        lower_vkey_areas = lower_vkey_div.find_elements_by_class_name("transkey_area")

        upper_vkey_div = comm.driver.find_element_by_id("비밀번호_layoutUpper")
        upper_vkey_img = comm.driver.find_element_by_id("비밀번호_imgTwinUpper")
        upper_vkey_areas = upper_vkey_div.find_elements_by_class_name("transkey_area")

        bboxPWD = (
            elem_vkey_img.location['x'],
            elem_vkey_img.location['y'],
            elem_vkey_img.location['x'] + elem_vkey_img.size['width'],
            elem_vkey_img.location['y'] + elem_vkey_img.size['height']
        )

        comm.driver.save_screenshot(SCREENSHOT)
        size = Image.open(SCREENSHOT).size

        vkey_sc = Image.open(SCREENSHOT).crop(bboxPWD)
        vkey_sc.save("ShinhanBank_vkey.png")

    except:
        comm.add_err("ERROR_RETRIABLE_error_in_saving_screenshot", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        dict = {}
        for index, area in enumerate(lower_vkey_areas):
            attr_str = area.get_attribute("coords").split(",")
            coords = (int(attr_str[0]), int(attr_str[1]))
            dict[index] = coords
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_generate_dict", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        marked_slot = []
        refimg = Image.open(VK_RES_DIR + "/" + "shinhan_vkey_mark.png").convert(mode="RGB")
        for i in range(len(dict)):
            tgtbox = (dict[i][0], dict[i][1], dict[i][0] + 38, dict[i][1] + 38)
            tgtimg = vkey_sc.crop(tgtbox).convert(mode="RGB")
            if ImageChops.difference(refimg, tgtimg).getbbox() is None:
                marked_slot.append(i)

    except:
        comm.add_err("ERROR_RETRIABLE_error_in_generate_marked_list", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        slot = 0
        for alphabet in range(len(VK_LOWER)):
            while slot in marked_slot:
                slot += 1
            VK_LOWER_DICT[VK_LOWER[alphabet]] = {'slot': slot, 'coord': dict[slot], }
            slot += 1

        slot = 0
        for alphabet in range(len(VK_UPPER)):
            while slot in marked_slot:
                slot += 1
            VK_UPPER_DICT[VK_UPPER[alphabet]] = {'slot': slot, 'coord': dict[slot], }
            slot += 1
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_generate_completed_dict", tb_msg=traceback.format_exc(), SC=True)
        return comm

    global CAPS
    CAPS = False

    trial_max_num = 5
    trial_num = 0
    pw_len = len(comm.cred_decoded['cred_user_pw'])
    while True:
        if trial_num >= trial_max_num:
            comm.add_err("ERROR_RETRIABLE_error_in_press_key", tb_msg=traceback.format_exc(), SC=True)
            return comm

        lower_vkey_img = comm.driver.find_element_by_id("비밀번호_imgTwinLower")
        upper_vkey_img = comm.driver.find_element_by_id("비밀번호_imgTwinUpper")

        try:
            for pw in comm.cred_decoded['cred_user_pw']:
                pw_char = pw
                print pw
                found = False
                if not CAPS:
                    for lowerCH in VK_LOWER_DICT:
                        if pw_char is lowerCH:
                            found = True
                            press(comm.driver, lower_vkey_img, VK_LOWER_DICT[pw_char]['coord'])
                    if found is not True:
                        toggle(comm)
                        for upperCH in VK_UPPER_DICT:
                            if pw_char is upperCH:
                                press(comm.driver, upper_vkey_img, VK_UPPER_DICT[pw_char]['coord'])
                else:
                    for upperCH in VK_UPPER_DICT:
                        if pw_char is upperCH:
                            found = True
                            press(comm.driver, upper_vkey_img, VK_UPPER_DICT[pw_char]['coord'])
                    if found is not True:
                        toggle(comm)
                        for lowerCH in VK_LOWER_DICT:
                            if pw_char is lowerCH:
                                press(comm.driver, lower_vkey_img, VK_LOWER_DICT[pw_char]['coord'])
        except:
            trial_num += 1
            try:
                comm.driver.switch_to_default_content()
                WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'bizMain')))
                comm.driver.switch_to_frame(comm.driver.find_element_by_name("bizMain"))
            except:
                comm.add_err("ERROR_RETRIABLE_error_while_change_frame", tb_msg=traceback.format_exc(), SC=True)
                return comm
            try:
                elem_pw_form.click()
                comm.driver.find_element_by_id("userID").click()
            except:
                comm.add_err("ERROR_RETRIABLE_could_not_found_form", tb_msg=traceback.format_exc(), SC=True)
                return comm
        else:
            if pw_len == len(elem_pw_form.get_attribute("value")):
                break
            else:
                comm.add_err("ERROR_RETRIABLE_error_in_press_key", tb_msg=traceback.format_exc(), SC=True)
                return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("input pw is done")
    return comm


def toggle(comm):
    global CAPS         #전역변수를 그냥 접근할수 없기때문에 필요하다!
    lower_vkey_img = comm.driver.find_element_by_id("비밀번호_imgTwinLower")
    upper_vkey_img = comm.driver.find_element_by_id("비밀번호_imgTwinUpper")

    if not CAPS:
        press(comm.driver, lower_vkey_img, (13, 196))
        CAPS = True
    else:
        press(comm.driver, upper_vkey_img, (13, 196))
        CAPS = False


def press(driver, offsetElem, point):

    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(offsetElem, point[0] + 5, point[1] + 5)
    action.click()
    action.perform()
    time.sleep(0.5)


def submit(comm):

    try:
        script_str = 'javascript:OB_doIDLogin_BO("1");'
        comm.driver.execute_script(script_str)
    except:
        comm.add_err("ERROR_RETRIABLE_submit_error", tb_msg=traceback.format_exc(), SC=True)
        return comm

    time.sleep(10)

    while True:
        try:
            alert = comm.driver.switch_to_alert()
            alert.dismiss()
        except NoAlertPresentException:
            break

        time.sleep(1)

    time.sleep(5)

    try:
        window_origin = comm.driver.window_handles[0]
        for window in comm.driver.window_handles[1:]:
            comm.driver.switch_to_window(window)
            comm.driver.close()
            time.sleep(0.5)

        comm.driver.switch_to_window(window_origin)
    except:
        pass

    try:
        comm.driver.switch_to.frame(comm.driver.find_element_by_name("bizMain"))
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'userName')))
    except:
        try:
            time.sleep(3)
            comm.driver.switch_to_frame(comm.driver.find_element_by_id("iframeFloat"))
            err = comm.driver.find_element_by_id("msg")
            err_msg = err.__getattribute__("text").encode('utf-8')

            if "비밀번호가 일치하지 않습니다." in err_msg:
                comm.add_err("ERROR_DO_NOT_RETRY_wrong_pw", SC=True)
                return comm
            elif "고객님께서 요청하신 거래의 입력항목의 값이 잘못 입력되었습니다." in err_msg:
                comm.add_err("ERROR_DO_NOT_RETRY_wrong_id", SC=True)
                return comm
            elif "등록되지 않은 아이디이거나, 아이디 또는 비밀번호를 잘못 입력하셨습니다." in err_msg:
                comm.add_err("ERROR_DO_NOT_RETRY_wrong_id", SC=True)
                return comm
            elif "이용자 비밀번호 등록[비밀번호찾기(재설정)버튼] 후 이용하여 주시기 바랍니다." in err_msg:
                comm.add_err("ERROR_DO_NOT_RETRY_plaese_set_pw", SC=True)
                return comm
            else:
                comm.add_err("ERROR_RETRIABLE_unknown_error_" + err_msg, SC=True)
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
            time.sleep(10)
            try:
                if comm.driver:
                    comm.driver.quit()
                    comm.driver = None
            except:
                comm.add_err("ERROR_DO_NOT_RETRY_problem_in_webdriver", tb_msg=traceback.format_exc(), SC=True)
                return comm
            return comm
        else:
            time.sleep(10)
            try:
                if comm.driver:
                    comm.driver.quit()
                    comm.driver = None
            except:
                comm.add_err("ERROR_DO_NOT_RETRY_problem_in_webdriver", tb_msg=traceback.format_exc(), SC=True)
                return comm

    return comm

if __name__ == "__main__":

    job_info = {'creds': {'cred_user_id': 'murane', 'cred_user_pw': 'Tpsxl40!', 'cred_acc_no': '110385994336'}}
    comm = Comm(job_info)
    comm.set_attr(url="https://open.shinhan.com/index.jsp", isEncoded=False)
    comm = login(comm)

    print comm.last_e_msg




