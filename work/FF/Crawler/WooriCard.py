# -*- coding: cp949 -*-

###CONFIG#####
url = "https://sccd.wooribank.com/ccd/Dream?withyou=CMLGN0003"
query_elem_id_str ="cfmBtn"
query_end_value_str = "조회".decode('cp949')
#name = 'WooriCard'


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.
from bs4 import BeautifulSoup

from Utils import wonToDigit
from BAWooriCard import login

import sys,time,re
from datetime import datetime
import traceback

def check_is_querying(driver,query_elem_id_str,query_end_value_str):
    try:
        for i in range(60): ##60 sec
            ElemSubmitButton = driver.find_element_by_id(query_elem_id_str)
            if ElemSubmitButton.get_attribute("value") == query_end_value_str:
                return ("OK",None,None)
            time.sleep(1)
            
    except:
        tb_msg = traceback.format_exc()
        print tb_msg
        e_obj = sys.exc_info()
        e_msg = "ERROR_WHILE_CHECKING_QUERYING"
        return (e_msg,tb_msg,e_obj)

    else:
        return ("ERROR_QUERYING_IS_NOT_FINISHING",None,None)

def get_attempt(job_info):
    
    time.sleep(5)
    
    (driver,e_msg,tb_msg,e_obj) = login(url,job_info)
    print e_msg
    if e_msg is not "OK":
        print "Login Failed"
        return (None,e_msg,None,None)
        
    ##everything below is retriable
    ##TODO more specific error handling

    ##remove (hopefully any) popup
    try:
        popup = driver.find_element_by_xpath("//div[contains(@id, 'PUP')]")
        #close = driver.find_element_by_id("checkbox_cur_p")
        #close.click()
        driver.execute_script("oneDayClose();")
    except:
        pass
        
    

    
    
    
    try:
        driver.get("https://sccd.wooribank.com/ccd/Dream?withyou=CDMWC0012")
        driver.execute_script("setDate('B3');")
        time.sleep(1)
        ElemSubmitButton = driver.find_element_by_id("cfmBtn")
        ElemSubmitButton.click()

        time.sleep(1)
        ElemRowsizeSelect = Select(driver.find_element_by_name("CCD_REQ_SIZE"))
        ElemRowsizeSelect.select_by_value("20")
        driver.execute_script("changeSelect();")

        time.sleep(1)

        (e_msg,tb_msg,e_obj) = check_is_querying(driver,query_elem_id_str,query_end_value_str)
        
        if not e_msg.startswith("OK"):
            print "200 row query failed"
            return (None,e_msg,tb_msg,e_obj)

        html = driver.page_source
        soup = BeautifulSoup(html,"html.parser")
        summary = {}
        summary['acc_owner_name'] = soup.find("a",class_="login-name").get_text().strip()
        
        browse_timeline_text = "조회기간".decode('cp949')
        browse_timeline_row = soup.find("th",text = browse_timeline_text)
        browse_timeline_raw = browse_timeline_row.find_next_sibling("td").get_text().replace(",","").strip()
        #print browse_timeline_row, browse_timeline_raw
        #sys.exit()

        
        browse_start_date = browse_timeline_raw.split("~")[0].strip().replace(".","-")+" 00:00:00"
        browse_end_date = browse_timeline_raw.split("~")[1].strip().replace(".","-")+" 00:00:00"
        summary['browse_start_date'] = browse_start_date
        summary['browse_end_date'] = browse_end_date
        
        history = []
        next_button_avail = True

        while (next_button_avail):
            html = driver.page_source
            soup = BeautifulSoup(html,"html.parser")
            detail_table_soup = soup.find("table",class_=re.compile("tbl-type-1"))
            detail_rows = detail_table_soup.find_all("tr")
            for i in range(1,len(detail_rows)):
                detail_row = detail_rows[i]
                detail_tds = detail_row.find_all("td")
                occured_at_str = detail_tds[0].find("input")['value'].split("|")[2].replace(".","-")+":00"
                approval_no = detail_tds[2].get_text().strip()
                card_no = detail_tds[3].get_text().strip()
                supplier_name = detail_tds[4].get_text().strip()
                payment_type = detail_tds[5].get_text().strip()
                payment_length = detail_tds[6].get_text().strip()
                approval_amount = detail_tds[7].get_text().replace(",","").strip()
                cancel_info = detail_tds[8].get_text().replace(",","").strip()

                #print "cancel_info", cancel_info, len(cancel_info)

                ##TODO: i need a better way to do this
                cancel_date_str = None
                cancel_amount = cancel_info[:].replace(",","").strip() #copy

                if len(cancel_info) > 10: ##XXXX.XX.XX
                    if cancel_info[4] == "." and cancel_info[7] == ".":
                        ##it has date
                        #print "it has date"
                        cancel_date_str = cancel_info[:10].strip().replace(".","-")+" 00:00:00"
                        #print "it has date: cancel_date_str", cancel_date_str
                        cancel_amount = cancel_info[10:len(cancel_info)].replace(",","").strip()
                        #print "it has date: cancel_amount", cancel_amount
                if cancel_date_str is not None:        
                    try:
                        cancel_date = datetime.strptime(cancel_date_str,"%Y-%m-%d %H:%M:%S")
                    except:
                        tb_msg = traceback.format_exc()
                        print tb_msg
                        ##this should not happen
                        print "unidentified cancel_date_str..this should not happen"
                        cancel_date_str = None

                if not cancel_amount.isdigit():
                    ##Something is very wrong but for now..
                    tb_msg = traceback.format_exc()
                    e_obj = sys.exc_info()
                    e_msg = "ERROR_STRANGE_CANCEL_AMOUNT"
                    print "strange cancel amount", cancel_amount
                    return (None,e_msg,tb_msg,e_obj)
                    
                    
                #cancel_amount = cancel_info[1].replace(",","").strip().split()
                #cancel_amount = "0"

                #print cancel_date_str,cancel_amount

                
                
                payment_due_str = detail_tds[9].get_text().strip().replace(".","-")+" 00:00:00"
                try:
                    datetime.strptime(payment_due_str,"%Y-%m-%d %H:%M:%S")
                except:
                    ##probably not in datetime. something like "취소"
                    ##TODO: process non-datetime  info
                    print "payment_due_str", payment_due_str
                    payment_due_str = None
                        
                detail = {'occured_at_str': occured_at_str,
                          'approval_no' : approval_no,
                          'card_no' : card_no,
                          'supplier_name' : supplier_name,
                          'payment_type' : payment_type,
                          'payment_length' : payment_length,
                          'approval_amount' : approval_amount,
                          'cancel_amount' : cancel_amount,
                          'cancel_date_str' : cancel_date_str,
                          'payment_due_str' : payment_due_str,
                                }
                history.append(detail)
                #print detail

            next_button_soup = soup.find("a",class_="direction next")
            if not next_button_soup:
                next_button_avail = False
                break

            driver.execute_script("getNextPage();")
            time.sleep(1)
            (e_msg,tb_msg,e_obj) = check_is_querying(driver,query_elem_id_str,query_end_value_str)
        
            if not e_msg.startswith("OK"):
                print "200 row query failed"
                return (None,e_msg,tb_msg,e_obj)
            
        
        print "seems ok"

            
        
        data = {'summary' : summary,
                'history':history,}
                

    except:

        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        e_msg = "ERROR_RETRIABLE_in_GET"

        print tb_msg
        
        try: ##this may fail
            driver.close()
            driver.quit()
        except:
            pass
        return (None,e_msg,tb_msg,e_obj)


    ##this should not fail
    driver.close()
    driver.quit()

    return (data,"OK",None,None)

def get(job_info):
    for t in range(10):
        (data,e_msg,tb_msg,e_obj) = get_attempt(job_info)
        if e_msg == "OK":
            return (data,e_msg,tb_msg,e_obj)
        elif "ERROR_DO_NOT_RETRY" in e_msg:          
            return (data,e_msg,tb_msg,e_obj)
        else:
            print e_msg
            print "retriable error.. retrying..", t

            time.sleep(10)
            
    return (data,"ERROR_DO_NOT_RETRY_MAXIMUM_GET_RETRY_EXCEEDED",tb_msg,e_obj)

    ##upload
    ## TODO: who am i ? my key?
    '''
    user_id = 24
    instance_id = "i-d38ccb16"

    url = 'http://myserver/post_service'
    data = urllib.urlencode({'user_id' : user_id
                            , 'instance_id'  : instance_id
                            , 'balance' : balance
                            , 'cashable' : cashable })
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    print response.read()
    '''

#if __name__ == "__main__":
#    job_info = {'creds':{'username':'omsktr','pw':'Ekfldnjs121'},}
#    (bankdata,e_msg,tb_msg,e_obj) = get(job_info)
    
