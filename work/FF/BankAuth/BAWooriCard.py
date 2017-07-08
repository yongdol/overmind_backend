# -*- coding: cp949 -*-
import os,sys,traceback
import re

regex_upper = "^[A-Z]"
regex_shift = "^[A-Z~!@#$%^&*()]"
regex_noshift = "^[a-z0-9`]"
VK_size = (692, 271)
shift_pos = (21, 223)
max_pw_length = 10

my_dir = os.path.dirname(os.path.realpath(__file__))
res_dir = my_dir+"/BAWooriCardRes"
vk_res_dir = my_dir+"/BAWooriCardRes/VK"

from PIL import Image
from PIL import ImageGrab

from BAUtils import decodeThis
from BAUtils import moveAbsPos
from BAUtils import clickAbsPos
from BAUtils import searchSubImg
from BAUtils import VKClick, VKClickPos

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.
from bs4 import BeautifulSoup
#from pywinauto.findwindows    import find_window
#from pywinauto.win32functions import SetForegroundWindow

import sys,time,ctypes
import traceback


TEMPCSCFILE1="/BAWooriCardTempCSC1.png"
TEMPCSCFILE2="/BAWooriCardTempCSC2.png"

def login_attempt(url,job_info,creds_encoded=True):
    ##decode passwords first
    #print job_info['creds']['cred_user_id']
    #print job_info['creds']['cred_user_pw']
    #print decodeThis({'cred_acc_no': job_info['creds']['cred_acc_no'],})
    if creds_encoded:
        try:
            dcreds = decodeThis(job_info['creds'],job_info['user_id'])
        except:
            e_msg = "ERROR_DO_NOT_RETRY_could_not_decode_credentials"
            tb_msg = traceback.format_exc()
            e_obj = sys.exc_info()
            
            return (None,e_msg,tb_msg,e_obj)
        print "creds decoded"
    else:
        dcreds = job_info['creds']
    #print dcreds
    '''
    dcreds = {}
    dcreds['username'] = job_info['creds']['username']
    dcreds['pw'] = job_info['creds']['pw']
    '''
    if len(dcreds['cred_user_pw']) > max_pw_length: ##this should be filtered by input form
        dcreds['cred_user_pw'] = dcreds['cred_user_pw'][:max_pw_length] 
   
    try:
        profile = webdriver.FirefoxProfile()
        #profile = webdriver.FirefoxProfile('C:\\Users\\Administrator\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\emsx2iyb.selenium_banking')
        #user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
        user_agent = "Mozilla/5.0 (Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_0_1 like Mac OS X; fr-fr) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5G77 Safari/525.20"
        #user_agent="Mozilla/5.0 (Linux; U; Android 2.1-update1; ko-kr; Nexus One Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17"

        profile.set_preference("general.useragent.override", user_agent)
        driver = webdriver.Firefox(profile)
        driver.implicitly_wait(10)
        
        #time.sleep(1)
        driver.maximize_window()
        driver.get(url)
    except:
        
        e_msg = "ERROR_RETRIABLE_could_not_create_webdriver"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (None,e_msg,tb_msg,e_obj)

    time.sleep(1)

    try:
        ## Enter username
        ElemUsernameInput = driver.find_element_by_id("USER_ID")
    except:
        
        e_msg = "ERROR_RETRIABLE_Could Not Find username input box"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)
    
        #print "ElemAccNoInput loc", ElemAccNoInput.location
    try:
        ElemUsernameInput.click()
        
        ElemUsernameInput.send_keys(dcreds['cred_user_id'])
        time.sleep(0.5)
    except:
        
        e_msg = "ERROR_RETRIABLE_Could Not Enter username"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)
        
        

    ## Enter PW (virtual keypad)
    #time.sleep(5)
    try:
        ElemCheckPw = driver.find_element_by_id("Tk_PWD_checkbox")
        if ElemCheckPw.is_selected():
            #driver.execute_script("document.getElementById('pup02').focus();");
            print "ElemCheckPw is selected"
            
            ElemPwInput = driver.find_element_by_id("PWD")
            #driver.switch_to.window(driver.current_window_handle)
            #clickAbsPos(10,10)
            #clickAbsPos(ElemAccPwInput.location['x']+3,ElemAccPwInput.location['y']+3+69)
            
            action = webdriver.common.action_chains.ActionChains(driver)
            action.move_to_element_with_offset(ElemPwInput,3,3)
            action.click()
            action.perform()

            time.sleep(0.3)
            
            ElemPwInput.click()
            time.sleep(0.3)
            ElemPwInput.click(0.3)

            
        else:
            print "ElemCheckAccPw is not selected"
            ElemCheckPw.click()
    except:
        
        e_msg = "ERROR_RETRIABLE_Could Not Click Pw Check Box"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    
    time.sleep(5) ##Give Enough Time to virtual keyboard to pop up

    try:
        ElemTkPWD = driver.find_element_by_id("Tk_PWD_layoutLower")
        print "ElemTkPWD loc", ElemTkPWD.location
        print "ElemTkPWD size", ElemTkPWD.size
    except:
        
        e_msg = "ERROR_RETRIABLE_virtual keyboard ElemTkPWD not found.. strange"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)   

    ##TODO: I need a reliable way to check if the virtual keyboard is up
    ##Maybe Check Size?
    if ElemTkPWD.size['width'] != VK_size[0] or ElemTkPWD.size['height'] != VK_size[1]:

        e_msg = "ERROR_RETRIABLE_virtual keyboard pup 02 size mismatch.. it did not popup"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)        
    
    #driver.switch_to.window(driver.current_window_handle)
    bboxPWD = (ElemTkPWD.location['x'], ##left
                 ElemTkPWD.location['y'], ##top
                 ElemTkPWD.location['x']+ElemTkPWD.size['width'], ##right
                 ElemTkPWD.location['y']+ElemTkPWD.size['height'], ##right
                    )
  
    try:             
        #cSC.save("/testpup02.png")
        #raise

        shift_status = "DOWN"


        for accpwc in dcreds['cred_user_pw']:
            ##if uppercase, press shift ##TODO: check current shift

            sc = accpwc
            
            if re.match(regex_shift, accpwc):
                if shift_status == "DOWN":
                
                    ElemTkPWDLower = driver.find_element_by_id("Tk_PWD_layoutLower")
                    (e_msg,tb_msg,e_obj) = VKClickPos(driver,ElemTkPWDLower,shift_pos)
                
                    if not e_msg.startswith("OK"):
                        return (driver,e_msg,tb_msg,e_obj)
                    shift_status = "UP"
                    
                    ##TODO: check current shift??
                
                ##now it's up
                driver.save_screenshot(TEMPCSCFILE1)
                cSC=Image.open(TEMPCSCFILE1).crop(bboxPWD)
                
                if re.match(regex_upper, accpwc):
                    sc = sc+"u"
                elif sc == "*":
                    sc = "asterik"

                ElemTkPWDUpper = driver.find_element_by_id("Tk_PWD_layoutUpper")
                
                (e_msg,tb_msg,e_obj) = VKClick(driver,ElemTkPWDUpper,cSC,vk_res_dir,sc)
                if not e_msg.startswith("OK"):
                    return (driver,e_msg,tb_msg,e_obj)
                

                ##unshift
                '''
                (e_msg,tb_msg,e_obj) = VKClick(driver,ElemTkPWDUpper,cSC,vk_res_dir,'shift_u')
                               
                if not e_msg.startswith("OK"):
                    return (driver,e_msg,tb_msg,e_obj)
                ##TODO: check current shift
                time.sleep(0.2)
                '''
            else:
                if shift_status == "UP":
                
                    ElemTkPWDUpper = driver.find_element_by_id("Tk_PWD_layoutUpper")
                    (e_msg,tb_msg,e_obj) = VKClickPos(driver,ElemTkPWDUpper,shift_pos)
                
                    if not e_msg.startswith("OK"):
                        return (driver,e_msg,tb_msg,e_obj)
                    shift_status = "DOWN"
                    
                    ##TODO: check current shift??
                    
                driver.save_screenshot(TEMPCSCFILE1)
                cSC=Image.open(TEMPCSCFILE1).crop(bboxPWD)
                ElemTkPWDLower = driver.find_element_by_id("Tk_PWD_layoutLower")
                (e_msg,tb_msg,e_obj) = VKClick(driver,ElemTkPWDLower,cSC,vk_res_dir,sc)
                if not e_msg.startswith("OK"):
                    return (driver,e_msg,tb_msg,e_obj)
                #time.sleep(0.2)

        pwdvalue = driver.find_element_by_id("PWD").get_attribute("value")
        print len(pwdvalue), len(dcreds['cred_user_pw'])
        if len(pwdvalue) != len(dcreds['cred_user_pw']):
            raise       
        
    except:
        
        e_msg = "ERROR_RETRIABLE_something wrong while finding and clicking accpw"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)   
    ##TODO : is there any way to verify what i have entered?

    time.sleep(2)
    
    
    try:
        ElemSubmitButton = driver.find_element_by_id("id_login")
        ElemSubmitButton.click()
    except:

        e_msg = "ERROR_RETRIABLE_in submitting post data"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)   

    time.sleep(10)

    login_success = False
    try:
        logout_text = "로그아웃".decode('cp949')
        ElemLogoutButton = driver.find_element_by_link_text(logout_text)
                                                     
    except: #NoSuchElementException
        pass
        ##login somehow failed
        #e_obj = sys.exc_info()
        #return (driver,"ERROR_Login_Failed",e_obj)
    else:
        login_success = True
        return (driver,"OK",None,None)

    ##login failed!!
    ##find fail cause

    wrong_id_text = "ID를 다시 확인하시기 바랍니다.".decode('cp949')
    html = driver.page_source
    if wrong_id_text in html:
        return (driver,"ERROR_DO_NOT_RETRY_WRONG_ID",None,None)
        
   
    wrong_pw_text_01 = "비밀번호".decode('cp949')
    wrong_pw_text_02 = "회 오류입니다.".decode('cp949')
    ##<dd class="mb10 md">등록된  비밀번호와  입력된  비밀번호  불일치  ( 누적오류입력  1  회 )</dd>
    html = driver.page_source
    if wrong_pw_text_01 in html and wrong_pw_text_02 in html:
        ####wrong password (really, bad registeration)
        return (driver,"ERROR_DO_NOT_RETRY_WRONG_PASSWORD",None,None)
    
    ##all else, retry
    return (driver,"ERROR_RETRIABLE_LOGIN_FAIL",None,None)
    
    
        
def login(url,job_info,creds_encoded=True):

    wrong_site_count = 0
    for t in range(10):
        (driver,e_msg,tb_msg,e_obj) = login_attempt(url,job_info,creds_encoded)
        if e_msg == "OK":
            return (driver,e_msg,tb_msg,e_obj)
        elif "ERROR_DO_NOT_RETRY" in e_msg:
            driver.quit()
            del driver
            return (None,e_msg,tb_msg,e_obj)
        else:
        
            print e_msg
            print tb_msg
            print "retriable error.. retrying..", t
            driver.quit()
            del driver
            if e_msg == "ERROR_RETRIABLE_Could Not Find Account Number":
                wrong_site_count = wrong_site_count + 1
            time.sleep(10)
            

    driver.quit()    
    del driver

    if wrong_site_count >= 9:
        return (None,"ERROR_DO_NOT_RETRY_WRONG_SITE",tb_msg,e_obj)
    
    return (None,"ERROR_DO_NOT_RETRY_MAXIMUM_LOGIN_RETRY_EXCEEDED",tb_msg,e_obj)

    

    ##TODO: check login success
    
if __name__ == "__main__":
    import json
    time.sleep(5)
    
    url = "https://sccd.wooribank.com/ccd/Dream?withyou=CMLGN0003"
    #job_info = json.loads(open("my_job_info_example.json","r").read())
    #(driver,e_msg,tb_msg,e_obj) = login(url,job_info)
    (driver,e_msg,tb_msg,e_obj) = login(url,{'creds':{'cred_user_id':'omsktr','cred_user_pw':'tpsxl40'}},creds_encoded=False)
    #(driver,e_msg,tb_msg,e_obj) = login(url,{'username':'omsktr','pw':'tpsxl40'})
    
    print e_msg
    #driver.close()
    #driver.quit()
