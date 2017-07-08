# -*- coding: cp949 -*-
import os

#driverengine="Ie"
#bboxs = [ (216,544,525,813), ## left, top, right, bottom
#          (211,581,522,858), ]
#bboxs = [ (215,475,525,746), ## left, top, right, bottom
#          (215,509,525,778), ]
#coffsets = [(215-185,475-212), (215-185,509-212) ] ##from accNo (185,212)
my_dir = os.path.dirname(os.path.realpath(__file__))
res_dir = my_dir+"/BAWooriSpeedRes"
vk_res_dir = my_dir+"/BAWooriSpeedRes/VK"



from PIL import Image
from PIL import ImageGrab

from BAUtils import decodeThis
from BAUtils import moveAbsPos
from BAUtils import clickAbsPos
from BAUtils import searchSubImg

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


TEMPCSCFILE1="/BAWooriSpeedTempCSC1.png"
TEMPCSCFILE2="/BAWooriSpeedTempCSC2.png"

def login_attempt(url,job_info,creds_encoded=True):
    ##decode passwords first
    #print job_info['creds']['cred_acc_no']
    #print decodeThis({'cred_acc_no': job_info['creds']['cred_acc_no'],})
    if creds_encoded:
        try:
            dcreds = decodeThis(job_info['creds'],job_info['user_id'])
        except:
            e_msg = "ERROR_DO_NOT_RETRY_could_not_decode_credentials"
            tb_msg = traceback.format_exc()
            e_obj = sys.exc_info()
            
            return (driver,e_msg,tb_msg,e_obj)
    else:
        dcreds = job_info['creds']
   
    try:
        profile = webdriver.FirefoxProfile()
        #profile = webdriver.FirefoxProfile('C:\\Users\\Administrator\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\emsx2iyb.selenium_banking')
        user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
        #user_agent = "Mozilla/5.0 (Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_0_1 like Mac OS X; fr-fr) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5G77 Safari/525.20"
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
        return (driver,e_msg,tb_msg,e_obj)

    time.sleep(10)

    try:
        ## Enter Account Number
        ElemAccNoInput = driver.find_element_by_id("pup01")
    except:
        
        e_msg = "ERROR_RETRIABLE_Could Not Find Account Number"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)
    
        print "ElemAccNoInput loc", ElemAccNoInput.location
    try:
        ElemAccNoInput.click()
        #accno = "1002442773027"
        ElemAccNoInput.send_keys(dcreds['cred_acc_no'])
        time.sleep(3)
    except:
        
        e_msg = "ERROR_RETRIABLE_Could Not Enter Account Number"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)
        
        

    ## Enter Account PW (virtual keypad)
    time.sleep(5)
    try:
        ElemCheckAccPw = driver.find_element_by_id("Tk_pup02_checkbox")
        if ElemCheckAccPw.is_selected():
            #driver.execute_script("document.getElementById('pup02').focus();");
            print "ElemCheckAccPw is selected"
            
            ElemAccPwInput = driver.find_element_by_id("pup02")
            #driver.switch_to.window(driver.current_window_handle)
            #clickAbsPos(10,10)
            #clickAbsPos(ElemAccPwInput.location['x']+3,ElemAccPwInput.location['y']+3+69)
            
            action = webdriver.common.action_chains.ActionChains(driver)
            action.move_to_element_with_offset(ElemAccPwInput,3,3)
            action.click()
            action.perform()

            time.sleep(1)
            
            ElemAccPwInput.click()
            time.sleep(1)
            ElemAccPwInput.click()

            
        else:
            print "ElemCheckAccPw is not selected"
            ElemCheckAccPw.click()
    except:
        
        e_msg = "ERROR_RETRIABLE_Could Not Click AccPw Check Box"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)

    
    time.sleep(10) ##Give Enough Time to virtual keyboard to pop up

    try:
        ElemTkpup02 = driver.find_element_by_id("Tk_pup02_layoutSingle")
        print "ElemTkpup02 loc", ElemTkpup02.location
        print "ElemTkpup02 size", ElemTkpup02.size
    except:
        
        e_msg = "ERROR_RETRIABLE_virtual keyboard pup 02 not found.. strange"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)   

    ##TODO: I need a reliable way to check if the virtual keyboard is up
    ##Maybe Check Size?
    if ElemTkpup02.size['width'] != 315 or ElemTkpup02.size['height'] != 271:

        e_msg = "ERROR_RETRIABLE_virtual keyboard pup 02 size mismatch.. it did not popup"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)        
    
    #driver.switch_to.window(driver.current_window_handle)
    bboxpup02 = (ElemTkpup02.location['x'], ##left
                 ElemTkpup02.location['y'], ##top
                 ElemTkpup02.location['x']+ElemTkpup02.size['width'], ##right
                 ElemTkpup02.location['y']+ElemTkpup02.size['height'], ##right
                    )

    
    try:             
        driver.save_screenshot(TEMPCSCFILE1)
        cSC=Image.open(TEMPCSCFILE1).crop(bboxpup02)
        #cSC.save("/testpup02.png")

        for accpwc in dcreds['cred_acc_pw']:
            cbmp = Image.open(vk_res_dir+"/"+unicode(accpwc)+".png")
            point =  searchSubImg(cbmp,cSC)
            if not point:
                print "subImg Not Found, accpw"
                cbmp.save("cbmp_error.png")
                cSC.save("cSC_error.png")
               
                e_msg = "ERROR_RETRIABLE_subImg Not Found, accpw"
                tb_msg = traceback.format_exc()
                e_obj = sys.exc_info()
                return (driver,e_msg,tb_msg,e_obj)  
                
            #driver.switch_to.window(driver.current_window_handle)
            #clickAbsPos(10,10)
            #clickAbsPos(ElemTkpup02.location['x']+point[0],ElemTkpup02.location['y']+point[1]+69)
                
            action = webdriver.common.action_chains.ActionChains(driver)
            #action.move_to_element_with_offset(ElemAccNoInput,coffsets[0][0]+point[0] , coffsets[0][1]+point[1])
            action.move_to_element_with_offset(ElemTkpup02, point[0]+5 , point[1]+5)
            action.click()
            action.perform()
            
            #time.sleep(1)
            #action.click()
            #action.perform()
            
            #print 185+coffsets[0][0]+point[0], 212+coffsets[0][1]+point[1]
            #action.click()
            #action.click_and_hold()
            #time.sleep(1)
            #action.release()
            #action.perform()
            ##TODO: take partial screenshot what i just clicked for debug!
            time.sleep(1)
    except:
        
        e_msg = "ERROR_RETRIABLE_something wrong while finding and clicking accpw"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)   
    ##TODO : is there any way to verify what i have entered?

    
    ## Enter SSN (virtual keypad)
    try:
        ElemCheckSSN = driver.find_element_by_id("Tk_pup03_checkbox")
        if ElemCheckSSN.is_selected():
            ElemSSNInput = driver.find_element_by_id("pup03")
            ElemSSNInput.click()
            #action = webdriver.common.action_chains.ActionChains(driver)
            #action.move_to_element_with_offset(ElemSSNInput,3,3)
            #action.click()
            #action.perform()
        else:
            ElemCheckSSN.click()
    except:
        
        e_msg = "ERROR_RETRIABLE_Could Not Click CheckSSN Check Box"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)  
    time.sleep(10)

    try:    
        ElemTkpup03 = driver.find_element_by_id("Tk_pup03_layoutSingle")
        print "ElemTkpup03 loc", ElemTkpup03.location
        #driver.switch_to.window(driver.current_window_handle)
    except:
        
        e_msg = "ERROR_RETRIABLE_virtual keyboard pup03 not found.. strange"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)  

    if ElemTkpup03.size['width'] != 315 or ElemTkpup03.size['height'] != 271:
        
        e_msg = "ERROR_RETRIABLE_virtual keyboard pup 03 size mismatch.. it did not popup"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)     
    
    bboxpup03 = (ElemTkpup03.location['x'], ##left
                 ElemTkpup03.location['y'], ##top
                 ElemTkpup03.location['x']+ElemTkpup03.size['width'], ##right
                 ElemTkpup03.location['y']+ElemTkpup03.size['height'], ##right
                 )
    try:
        driver.save_screenshot(TEMPCSCFILE2)
        cSC=Image.open(TEMPCSCFILE2).crop(bboxpup03)
        #sys.exit()
        #cSC=ImageGrab.grab().crop(bboxs[1])
        cSC.save("/testpup03.png")
        #pwElem = driver.find_element_by_id("Tk_pup03_layoutSingle")
        
        for ssnc in dcreds['cred_ssn']:
            
            cbmp = Image.open(vk_res_dir+"/"+unicode(ssnc)+".png")
            point =  searchSubImg(cbmp,cSC)
            if not point:
                print "subImg Not Found, ssn"
                cbmp.save("cbmp_error.bmp")
                cSC.save("cSC_error.bmp")
                #e_obj = sys.exc_info()
                e_msg = "ERROR_RETRIABLE_subImg Not Found, ssn"
                tb_msg = traceback.format_exc()
                e_obj = sys.exc_info()
                return (driver,e_msg,tb_msg,e_obj)  
                
                
            #driver.switch_to.window(driver.current_window_handle)
            #clickAbsPos(10,10)
            #clickAbsPos(ElemTkpup03.location['x']+point[0],ElemTkpup03.location['y']+point[1]+69)
                
            #driver.switch_to.window(driver.current_window_handle)
            #clickAbsPos(bboxs[1][0]+point[0],bboxs[1][1]+point[1]+69)
            action = webdriver.common.action_chains.ActionChains(driver)    
            #action.move_to_element_with_offset(ElemAccNoInput,coffsets[1][0]+point[0] , coffsets[1][1]+point[1])
            action.move_to_element_with_offset(ElemTkpup03, point[0]+5 , point[1]+5)
            #print ssnc, ElemTkpup03.location['x']+point[0], ElemTkpup03.location['y']+point[1]
            action.click()
            action.perform()
            time.sleep(1)
    except:
        e_msg = "ERROR_RETRIABLE_something wrong while finding and clicking ssn"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)  

    try:
        #driver.execute_script("doSubmit() ;return false;")
        driver.execute_script("shotData();")
        driver.execute_script("document.getElementById('parentFrm').submit(); return false;")
    except:

        e_msg = "ERROR_RETRIABLE_in submitting post data"
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        return (driver,e_msg,tb_msg,e_obj)   

    time.sleep(10)

    login_success = False
    try:
        ElemSessionSpd = driver.find_element_by_id("sessionSpd")
        ElemClock = driver.find_element_by_class_name("gnb-member-time")
        ElemDateRange = driver.find_element_by_class_name("js-btn-date-range")
                                                      
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

    
    text = "등록된  비밀번호와  입력된  비밀번호  불일치".decode('cp949').encode('utf-8')
    ##<dd class="mb10 md">등록된  비밀번호와  입력된  비밀번호  불일치  ( 누적오류입력  1  회 )</dd>
    html = driver.page_source.encode('utf-8')
    if text in html:
        ####wrong password (really, bad registeration)
        return (driver,"ERROR_DO_NOT_RETRY_WRONG_PASSWORD",None,None)
    else:
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
    
    url = "https://spib.wooribank.com/spd/Dream?withyou=CMSPD0010"
    #job_info = json.loads(open("my_job_info_example.json","r").read())
    job_info = {}
    job_info['creds'] = {'cred_acc_no':'1002442773027', 'cred_acc_pw':'4123', 'cred_ssn' : '761001'}
    
    (driver,e_msg,tb_msg,e_obj) = login(url,job_info,creds_encoded=False)
    print e_msg
    #driver.close()
    #driver.quit()
