# -*- coding: utf-8 -*-
__author__ = 'junsujung'
import os,sys,time
import traceback,logging

from BAUtils import decodeThis

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
RES_DIR = MY_DIR+"/BAWooriBankRes"
VK_RES_DIR = MY_DIR+"/BAWooriBankRes/VK"

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

LOG_LIST = []

NUMBER_OF_TRY = 0
NUMBER_OF_RETRY = 0
NUMBER_OF_SUCCESS = 0

def login_attempt(url,job_info,creds_encoded=True):

    #decode creds
    (creds_decoded,e_msg,tb_msg,e_obj) = decode_creds(job_info,creds_encoded)

    if e_msg is not "OK":
        return (None,e_msg,tb_msg,e_obj)

    #verify input format

    #create webdriver
    (driver,e_msg,tb_msg,e_obj)=create_webdriver(url)

    if e_msg is not "OK":
        return (driver,e_msg,tb_msg,e_obj)

    #find id form and sendkeys
    (driver,e_msg,tb_msg,e_obj) = login_form_input_id(driver, creds_decoded)

    if e_msg is not "OK":
        return (driver,e_msg,tb_msg,e_obj)

    #pw input
    (driver,e_msg,tb_msg,e_obj) =  login_form_input_pw(driver, creds_decoded)

    if e_msg is not "OK":
        return (driver,e_msg,tb_msg,e_obj)

    #submit and complete login
    (driver,e_msg,tb_msg,e_obj) = submit(driver)


    if e_msg is not "OK":
        return (driver,e_msg,tb_msg,e_obj)

    e_msg="OK"
    return (driver,e_msg,tb_msg,creds_decoded)

def submit(driver):

    #click login btn
    try:
        elem_login_btn = driver.find_element_by_id("id_login")
        elem_login_btn.click()
    except:
        e_msg = "ERROR_RETRIABLE_error_in_find_login_btn"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    #verifying either logined or not
    #2채널 인증 오류,비밀번호 입력 오류의 경우 ERROR_DO_NOT_RETRY

    while True:
        try:
            alert = driver.switch_to_alert()
            alert.dismiss()
        except NoAlertPresentException:
            break

    try:
        window_origin = driver.window_handles[0]
        for window in driver.window_handles[1:]:
            driver.switch_to_window(window)
            driver.close()
            time.sleep(0.1)

        driver.switch_to_window(window_origin)
    except:
        pass

    time.sleep(3)

    #로그아웃버튼이 있는지 확인합시다
    try:
        elem_logout_div = driver.find_element_by_id("gnb")
        elem_logout_btn = elem_logout_div.find_element_by_link_text("로그아웃")

    #없다면 2채널 / 미계약사용자,비밀번호오류,포맷오류,보안세션오류
    except:
        try:
            elem_error_area = driver.find_element_by_id("error-area-TopLayer")
            elem_error_msg = elem_error_area.find_elements_by_tag_name("dd")[0]
            err_msg = elem_error_msg.__getattribute__("text").encode('utf-8')

            if "미계약 이용자" in err_msg :
                e_msg = "ERROR_DO_NOT_RETRY_id_is_wrong"
                return (driver,e_msg,None,None)

            elif "이용자비밀번호불일치" in err_msg:
                e_msg ="ERROR_DO_NOT_RETRY_pw_is_wrong"
                return(driver,e_msg,None,None)
            else:
                e_msg= "ERROR_RETRIABLE_login_is_faild_cause_of_"+err_msg
                return (driver,e_msg,None,None)
        except:
            e_msg = "ERROR_RETRIABLE_security_session_error"
            tb_msg= traceback.format_exc()
            return (driver, e_msg,tb_msg,None)
    else:
        try:
            elem_popup_close = driver.find_element_by_link_text("팝업닫기")
            elem_popup_close.click()
        except:
            e_msg = "ERROR_RETRIABLE_error_in_find_popup"
            tb_msg = traceback.format_exc()
            return (driver,e_msg,tb_msg,None)


    e_msg = "OK"
    return (driver,e_msg,None,None)

def login_form_input_pw(driver, creds_decoded):

    try:
        global CAPS
        CAPS = False
        elem_pw_form = driver.find_element_by_id('PWD')
        elem_pw_form.click()
    except:
        e_msg = "ERROR_RETRIABLE_not_found_pw_form"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)
    try:
        elem_vkey_img = driver.find_element_by_id("imgTwinLower")

        bboxPWD = (
            elem_vkey_img.location['x'],
            elem_vkey_img.location['y'],
            elem_vkey_img.location['x']+elem_vkey_img.size['width'],
            elem_vkey_img.location['y']+elem_vkey_img.size['height']
        )

        vkey_map = driver.find_element_by_id("Tk_PWD_map")
        vkey_areas = vkey_map.find_elements_by_tag_name("area")

        for index,area in enumerate(vkey_areas):
            if index == 47:
                break
            attr_str = area.get_attribute("coords").split(",")
            coords = (int(attr_str[0]),int(attr_str[1]))
            COORDS_DICT[index] = coords

        #logger.info('coords are >> %s',COORDS_DICT)

        driver.save_screenshot(SCREENSHOT)
        vkey_lower_img=Image.open(SCREENSHOT).crop(bboxPWD)
        vkey_lower_img.save("wooriBank_vkey_lower.png")

    except:
        e_msg = "ERROR_RETRIABLE_error_in_saving_screenshot"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)
    try:

        crop_size = 5
        marked_lower_slot = []
        refimg_ = Image.open(VK_RES_DIR+"/"+"wooriBank_vkey_mark.png").convert(mode="RGB")
        refimg = refimg_.crop((5,5,38,37))

        for i in range(len(COORDS_DICT)):
            tgtbox = (COORDS_DICT[i][0]+crop_size,COORDS_DICT[i][1]+crop_size,COORDS_DICT[i][0]+43-crop_size,COORDS_DICT[i][1]+42-crop_size)
            tgtimg = vkey_lower_img.crop(tgtbox).convert(mode="RGB")
            #logger.info('diff is >> %s',ImageChops.difference(refimg,tgtimg).getbbox())
            diff = ImageChops.difference(refimg,tgtimg).getbbox()

            if diff is None or (diff[2] - diff[0])*(diff[3] - diff[1]) <= 4:
                marked_lower_slot.append(i)

        #logger.info('lowercase marked slot >> %s',marked_lower_slot)
        if len(marked_lower_slot) != 10:
            raise

        slot=0
        for letter in range(len(VK_LOWER)):
            while slot in marked_lower_slot:
                slot+=1
            VK_LOWER_DICT[VK_LOWER[letter]] = {'slot': slot, 'coord' : COORDS_DICT[slot], }
            slot+=1
        #logger.info('lowercase vk dict >> %s',VK_LOWER_DICT)
        toggle(driver)

        driver.save_screenshot(SCREENSHOT)
        vkey_upper_img=Image.open(SCREENSHOT).crop(bboxPWD)
        vkey_upper_img.save("wooriBank_vkey_upper.png")

        marked_upper_slot = []
        for i in range(len(COORDS_DICT)):
            tgtbox = (COORDS_DICT[i][0]+crop_size,COORDS_DICT[i][1]+crop_size,COORDS_DICT[i][0]+43-crop_size,COORDS_DICT[i][1]+42-crop_size)
            tgtimg = vkey_upper_img.crop(tgtbox).convert(mode="RGB")
            #logger.info('diff is >> %s',ImageChops.difference(refimg,tgtimg).getbbox())
            diff = ImageChops.difference(refimg,tgtimg).getbbox()

            if diff is None or (diff[2] - diff[0])*(diff[3] - diff[1]) <= 4:
                marked_upper_slot.append(i)

        #logger.info('uppercase marked slot >> %s',marked_upper_slot)
        if len(marked_upper_slot) != 10:
            raise

        slot=0
        for letter in range(len(VK_UPPER)):
            while slot in marked_upper_slot:
                slot+=1
            VK_UPPER_DICT[VK_UPPER[letter]] = {'slot': slot, 'coord' : COORDS_DICT[slot], }
            slot+=1
        #logger.info('uppercase vk dict >> %s',VK_UPPER_DICT)
        toggle(driver)

    except:
        e_msg = "ERROR_RETRIABLE_error_in_making_vkey_map"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    try:
        elem_vkey_lower = driver.find_element_by_id("imgTwinLower")
        elem_vkey_upper = driver.find_element_by_id("imgTwinUpper")
        """
        pw_length = 0
        for pw in creds_decoded['cred_user_pw']:
            pw_char = pw
            pw_length+=1
            found = False
            if CAPS == False:
                for lowerCH in VK_LOWER_DICT:
                    if pw_char is lowerCH:
                        found = True
                        press(driver,elem_vkey_lower,VK_LOWER_DICT[pw_char]['coord'])
                if found is not True:
                    toggle(driver)
                    press(driver,elem_vkey_upper,VK_UPPER_DICT[pw_char]['coord'])
            else:
                for upperCH in VK_UPPER_DICT:
                    if pw_char is upperCH:
                        found = True
                        press(driver,elem_vkey_upper,VK_UPPER_DICT[pw_char]['coord'])
                if found is not True:
                    toggle(driver)
                    press(driver,elem_vkey_lower,VK_LOWER_DICT[pw_char]['coord'])

            if pw_length != len(driver.find_element_by_id("PWD").get_attribute("value")):
                try:
                    raise
                except:
                    e_msg="ERROR_RETRIABLE_error_in_press_key"
                    return (driver,e_msg,None,None)
        """
        i=0
        pw_length=0
        pw = creds_decoded['cred_user_pw'][i]
        while i < len(creds_decoded['cred_user_pw']):
            pw = creds_decoded['cred_user_pw'][i]
            pw_length+=1
            found = False
            logger.error("enter >> "+pw)
            if CAPS == False:
                for lowerCH in VK_LOWER_DICT:
                    if pw is lowerCH:
                        found = True
                        press(driver,elem_vkey_lower,VK_LOWER_DICT[pw]['coord'])
                if found is not True:
                    toggle(driver)
                    press(driver,elem_vkey_upper,VK_UPPER_DICT[pw]['coord'])
            else:
                for upperCH in VK_UPPER_DICT:
                    if pw is upperCH:
                        found = True
                        press(driver,elem_vkey_upper,VK_UPPER_DICT[pw]['coord'])
                if found is not True:
                    toggle(driver)
                    press(driver,elem_vkey_lower,VK_LOWER_DICT[pw]['coord'])

            if pw_length != len(driver.find_element_by_id("PWD").get_attribute("value")):
                logger.error("입력이 안됬습니다")
                pw_length-=1
                i-=1
            i+=1


    except:
        e_msg = "ERROR_RETRIABLE_error_in_press_key"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    e_msg = "OK"
    return (driver,e_msg,None,None)


def toggle(driver):
    global CAPS         #전역변수를 그냥 접근할수 없기때문에 필요하다!

    if CAPS == False:
        driver.execute_script("transkey.Tk_PWD.pressMapKey(49);transkey.Tk_PWD.enterMapKey(49);")
        CAPS = True
    else:
        driver.execute_script("transkey.Tk_PWD.pressMapKey(49);transkey.Tk_PWD.enterMapKey(49);")
        CAPS = False

    time.sleep(1)

def press(driver,offsetElem,point):

    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(offsetElem, point[0]+5 , point[1]+5)
    action.click()
    action.perform()
    time.sleep(0.3)
    return ("OK",None,None)

def login_form_input_id(driver, creds_decoded):

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID,'USER_ID')))
        elem_user_id_form = driver.find_element_by_id("USER_ID")
    except TimeoutException:
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
    return (driver,e_msg,None,None)

def create_webdriver(url):
    try:
        profile = webdriver.FirefoxProfile()
        user_agent = "Mozilla/5.0(iPhone;U;CPUiPhoneOS4_0likeMacOSX;en-us)AppleWebKit/532.9(KHTML,likeGecko)Version/4.0.5Mobile/8A293Safari/6531.22.7"

        profile.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(profile)

        driver.maximize_window()
        driver.get(url)
    except TimeoutException:
        e_msg = "ERROR_RETRIABLE_timeout_in_browse_page"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    e_msg = "OK"
    return (driver,e_msg,None,None)


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
    try:
        if creds_decoded['cred_user_id'] is "" or len(creds_decoded['cred_user_pw']) < 5:
            raise
    except:
        e_msg = "ERROR_DO_NOT_RETRY_id_or_pw_format_is_wrong"
        return (None,e_msg,None,None)

    e_msg="OK"
    return (creds_decoded,e_msg,None,None)


def login(url,job_info, creds_encoded=True):
    global  NUMBER_OF_TRY,NUMBER_OF_SUCCESS,NUMBER_OF_RETRY
    NUMBER_OF_TRY+=1

    wrong_site_count = 0
    for t in range(10):
        (driver,e_msg,tb_msg,creds_decoded) = login_attempt(url,job_info,creds_encoded)
        if e_msg == "OK":

            logger.error("OK")
            logger.error("LOGIN SUCCESS")

            NUMBER_OF_SUCCESS+=1

            return (driver,e_msg,tb_msg,creds_decoded)

        elif "ERROR_DO_NOT_RETRY" in e_msg:

            tb_log = "tb_log >> "+ tb_msg
            err_log = "e_msg >> "+ e_msg

            logger.error(err_log)
            logger.error(tb_log)

            if driver is not None:
                driver.close()
                driver.quit()
            return (None,e_msg,tb_msg,None)

        else:
            try:
                driver.close()
                driver.quit()
            except:
                pass

            if tb_msg is not None:
                tb_log = "tb_log >> "+ tb_msg
                logger.error(tb_log)

            err_log = "e_msg >> "+ e_msg
            logger.error(err_log)


            NUMBER_OF_RETRY+=1

            if e_msg == "ERROR_RETRIABLE_Could Not Find Account Number":
                wrong_site_count += 1

    if wrong_site_count >= 9:
        return (None,"ERROR_DO_NOT_RETRY_WRONG_SITE",tb_msg,None)

    return (None,"ERROR_DO_NOT_RETRY_MAXIMUM_LOGIN_RETRY_EXCEEDED",tb_msg,None)



if __name__ == "__main__":

    url = "https://spib.wooribank.com/pib/Dream?withyou=CMLGN0001"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add the handlers to the logger
    fh = logging.FileHandler("error.log")
    fh.setLevel(logging.ERROR)
    fh.formatter=formatter
    logger.addHandler(fh)

    while(True):
        NUMBER_OF_RETRY = 0
        (driver,e_msg,tb_msg,e_obj) = login(url,{'creds':{'cred_user_id':'zakk95','cred_user_pw':'uE^9z@'}},creds_encoded=False)
        if e_msg is "OK":
            try:
                time.sleep(5)
                elem_popup_close = driver.find_element_by_link_text("로그아웃")
                elem_popup_close.click()

                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID,'logOut2')))
                elem_popup_close2 = driver.find_element_by_id("logOut2")
                elem_popup_close2.click()
            except:
                logger.error("login failed by could not find elem logout")
            finally:
                driver.close()
                driver.quit()
        else:
            driver.close()
            driver.quit()

        logger.error("TRY >> "+str(NUMBER_OF_TRY)+"RETRY >> "+str(NUMBER_OF_RETRY)+"SUCESS >> "+str(NUMBER_OF_SUCCESS))
        logger.error("----------------------------------------------")
        time.sleep(5)
