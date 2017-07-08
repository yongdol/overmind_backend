# -*- coding: utf-8 -*-
__author__ = 'junsujung'
import os,sys,time
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
from selenium.common.exceptions import TimeoutException,NoAlertPresentException

SCREENSHOT = "BAWooriBank_Monitor.png"

MY_DIR = os.path.dirname(os.path.realpath(__file__))
RES_DIR = MY_DIR + "/BAWooriBankRes"
VK_RES_DIR = MY_DIR + "/BAWooriBankRes/VK"

VK_LOWER = ["`","1","2","3","4","5","6","7","8","9","0",
            "q","w","e","r","t","y","u","i","o","p",
            "a","s","d","f","g","h","j","k",
            "z","x","c","v","b","n","m","l"]
VK_LOWER_DICT = {}

VK_UPPER = ["~","!","@","#","$","%","^","&","*","(",")",
            "Q","W","E","R","T","Y","U","I","O","P",
            "A","S","D","F","G","H","J","K",
            "Z","X","C","V","B","N","M","L"]
VK_UPPER_DICT = {}

COORDS_DICT = {}
CAPS = False


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
        user_agent = """
                    Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us)
                    AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16
                    """
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(profile)
        comm.set_attr(driver=driver)
        comm.driver.set_window_size(1600, 900)
        #comm.driver.maximize_window()
        comm.driver.get(comm.url)

    except:
        comm.add_err("ERROR_RETRIABLE_could_not_create_webdriver", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("create webdriver is done")
    return comm


def login_form_input_id(comm):

    try:
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'USER_ID')))
        elem_user_id_form = comm.driver.find_element_by_id("USER_ID")
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
        global CAPS
        CAPS = False
        elem_pw_form = comm.driver.find_element_by_id('PWD')
        elem_pw_form.click()
    except:
        comm.add_err("ERROR_RETRIABLE_could_not_found_pw_form", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        elem_vkey_img = comm.driver.find_element_by_id("imgTwinLower")

        bboxPWD = (
            elem_vkey_img.location['x'],
            elem_vkey_img.location['y'],
            elem_vkey_img.location['x'] + elem_vkey_img.size['width'],
            elem_vkey_img.location['y'] + elem_vkey_img.size['height']
        )

        vkey_map = comm.driver.find_element_by_id("Tk_PWD_map")
        vkey_areas = vkey_map.find_elements_by_tag_name("area")

        for index, area in enumerate(vkey_areas):
            if index == 47:
                break
            attr_str = area.get_attribute("coords").split(",")
            coords = (int(attr_str[0]), int(attr_str[1]))
            COORDS_DICT[index] = coords

        comm.driver.save_screenshot(SCREENSHOT)
        vkey_lower_img = Image.open(SCREENSHOT).crop(bboxPWD)
        vkey_lower_img.save("wooriBank_vkey_lower.png")

    except:
        comm.add_err("ERROR_RETRIABLE_error_in_saving_screenshot", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        crop_size = 5
        marked_lower_slot = []
        refimg_ = Image.open(VK_RES_DIR + "/" + "wooriBank_vkey_mark.png").convert(mode="RGB")
        refimg = refimg_.crop((5, 5, 38, 37))

        for i in range(len(COORDS_DICT)):
            tgtbox = (COORDS_DICT[i][0] + crop_size, COORDS_DICT[i][1] + crop_size, COORDS_DICT[i][0] + 43 - crop_size, COORDS_DICT[i][1] + 42 - crop_size)
            tgtimg = vkey_lower_img.crop(tgtbox).convert(mode="RGB")
            diff = ImageChops.difference(refimg, tgtimg).getbbox()

            if diff is None or (diff[2] - diff[0]) * (diff[3] - diff[1]) <=4:
                marked_lower_slot.append(i)

        try:
            if len(marked_lower_slot) != 10:
                raise
        except:
            comm.add_err("ERROR_RETRIABLE_error_in_detect_lower_mark", tb_msg=traceback.format_exc(), SC=True)
            return comm

        slot = 0
        for letter in range(len(VK_LOWER)):
            while slot in marked_lower_slot:
                slot += 1
            VK_LOWER_DICT[VK_LOWER[letter]] = {'slot': slot, 'coord': COORDS_DICT[slot]}
            slot += 1

        toggle(comm.driver)

        comm.driver.save_screenshot(SCREENSHOT)
        vkey_upper_img=Image.open(SCREENSHOT).crop(bboxPWD)
        vkey_upper_img.save("wooriBank_vkey_upper.png")

        marked_upper_slot = []
        for i in range(len(COORDS_DICT)):
            tgtbox = (COORDS_DICT[i][0] + crop_size, COORDS_DICT[i][1] + crop_size, COORDS_DICT[i][0] + 43 - crop_size, COORDS_DICT[i][1] + 42 - crop_size)
            tgtimg = vkey_upper_img.crop(tgtbox).convert(mode="RGB")
            #logger.info('diff is >> %s',ImageChops.difference(refimg,tgtimg).getbbox())
            diff = ImageChops.difference(refimg, tgtimg).getbbox()

            if diff is None or (diff[2] - diff[0]) * (diff[3] - diff[1]) <= 4:
                marked_upper_slot.append(i)

        try:
            if len(marked_upper_slot) != 10:
                raise
        except:
            comm.add_err("ERROR_RETRIABLE_error_in_detect_upper_mark", tb_msg=traceback.format_exc(), SC=True)
            return comm

        slot = 0
        for letter in range(len(VK_UPPER)):
            while slot in marked_upper_slot:
                slot += 1
            VK_UPPER_DICT[VK_UPPER[letter]] = {'slot': slot, 'coord' : COORDS_DICT[slot]}
            slot += 1
        #logger.info('uppercase vk dict >> %s',VK_UPPER_DICT)
        toggle(comm.driver)

    except:
        comm.add_err("ERROR_RETRIABLE_error_in_making_vkey_map", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        elem_vkey_lower = comm.driver.find_element_by_id("imgTwinLower")
        elem_vkey_upper = comm.driver.find_element_by_id("imgTwinUpper")

        i = 0
        pw_length = 0
        pw = comm.cred_decoded['cred_user_pw'][i]
        while i < len(comm.cred_decoded['cred_user_pw']):
            pw = comm.cred_decoded['cred_user_pw'][i]
            pw_length += 1
            found = False
            if CAPS == False:
                for lowerCH in VK_LOWER_DICT:
                    if pw is lowerCH:
                        found = True
                        press(comm.driver, elem_vkey_lower, VK_LOWER_DICT[pw]['coord'])
                if found is not True:
                    toggle(comm.driver)
                    press(comm.driver, elem_vkey_upper, VK_UPPER_DICT[pw]['coord'])
            else:
                for upperCH in VK_UPPER_DICT:
                    if pw is upperCH:
                        found = True
                        press(comm.driver, elem_vkey_upper, VK_UPPER_DICT[pw]['coord'])
                if found is not True:
                    toggle(comm.driver)
                    press(comm.driver, elem_vkey_lower, VK_LOWER_DICT[pw]['coord'])

            if pw_length != len(comm.driver.find_element_by_id("PWD").get_attribute("value")):
                pw_length -= 1
                i -= 1
            i += 1

    except:
        comm.add_err("ERROR_RETRIABLE_error_in_press_key", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    comm.logger.error("input pw is done")
    return comm


def toggle(driver):
    global CAPS         #전역변수를 그냥 접근할수 없기때문에 필요하다!

    if not CAPS:
        driver.execute_script("transkey.Tk_PWD.pressMapKey(49);transkey.Tk_PWD.enterMapKey(49);")
        CAPS = True
    else:
        driver.execute_script("transkey.Tk_PWD.pressMapKey(49);transkey.Tk_PWD.enterMapKey(49);")
        CAPS = False

    time.sleep(1.5)


def press(driver,offsetElem,point):

    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(offsetElem, point[0] + 5, point[1] + 5)
    action.click()
    action.perform()
    time.sleep(0.3)


def submit(comm):

    #click login btn
    try:
        elem_login_btn = comm.driver.find_element_by_id("id_login")
        elem_login_btn.click()
    except:
        comm.add_err("ERROR_RETRIABLE_error_in_find_login_btn", tb_msg=traceback.format_exc(), SC=True)
        return comm

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

    #로그아웃버튼이 있는지 확인합시다
    try:
        elem_logout_div = comm.driver.find_element_by_id("gnb")
        elem_logout_btn = elem_logout_div.find_element_by_link_text("로그아웃")

        try:
            time.sleep(3)
            elem_popup_close = comm.driver.find_element_by_link_text("팝업닫기")
            elem_popup_close.click()
        except:
            comm.add_err("ERROR_RETRIABLE_error_in_find_popup", tb_msg=traceback.format_exc(), SC=True)
            return comm

    #없다면 2채널 / 미계약사용자,비밀번호오류,포맷오류,보안세션오류
    except:
        try:
            elem_error_area = comm.driver.find_element_by_id("error-area-TopLayer")
            elem_error_msg = elem_error_area.find_elements_by_tag_name("dd")[0]
            err_msg = elem_error_msg.__getattribute__("text").encode('utf-8')

            if "미계약 이용자" in err_msg :
                comm.add_err("ERROR_DO_NOT_RETRY_id_is_wrong", tb_msg=traceback.format_exc(), SC=True)
                return comm

            elif "이용자비밀번호불일치" in err_msg:
                comm.add_err("ERROR_DO_NOT_RETRY_pw_is_wrong", tb_msg=traceback.format_exc(), SC=True)
                return comm
            else:
                comm.add_err("ERROR_RETRIABLE_login_is_faild_cause_of_", tb_msg=traceback.format_exc(), SC=True)
                return comm
        except:
            try:
                elem_form = comm.driver.find_element_by_id("frm")
                elem_msg = elem_form.find_elements_by_tag_name("dt")[0].__getattribute__("text").encode('utf-8')

                if "우리은행 인터넷뱅킹에 가입해 주신 고객님께 감사드립니다." in elem_msg:
                    comm.add_err("ERROR_DO_NOT_RETRY_unfinished_registration", tb_msg=traceback.format_exc(), SC=True)
                    return comm
                elif "인터넷/스마트뱅킹을 정상적으로 종료하지 않아" in elem_msg:
                    comm.add_err("ERROR_DO_NOT_RETRY_2ch_auth_error", tb_msg=traceback.format_exc(), SC=True)
                    return comm
                else:
                    comm.add_err("ERROR_DO_NOT_RETRY_unknown_error", tb_msg=traceback.format_exc(), SC=True)
                    return comm
            except:
                comm.add_err("ERROR_RETRIABLE_security_session_error", tb_msg=traceback.format_exc(), SC=True)
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

    return comm

if __name__ == "__main__":

    job_info = {'creds':{'cred_user_id':'zakk95', 'cred_user_pw':'uE^9z@', 'cred_acc_no' : '1002442773027'}}
    comm = Comm(job_info=job_info)
    comm.set_attr(url = "https://spib.wooribank.com/pib/Dream?withyou=CMLGN0001",isEncoded=False)
    comm = login(comm)

