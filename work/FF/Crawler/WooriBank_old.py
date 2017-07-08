# -*- coding: utf-8 -*-
__author__ = 'junsujung'

import sys,logging

###CONFIG#####
query_elem_id_str ="trnsSearch"
query_end_value_str = "조회".decode("utf-8")
#query_end_value_str = query_end_value_str_cp949.decode('cp949')

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
from BAWooriBank import login

import sys,time,re,os
from datetime import datetime
import traceback

ErrorLog = []

def logout(driver):
    try:
        time.sleep(3)
        elem_popup_close = driver.find_element_by_link_text("로그아웃")
        elem_popup_close.click()

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID,'logOut2')))
        elem_popup_close2 = driver.find_element_by_id("logOut2")
        elem_popup_close2.click()
    except:
        pass

def check_is_querying(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'trnsSearch')))
    except:
        e_msg="ERROR in querying acc_data"

    e_msg = "OK"
    return (driver,e_msg)


def get_attempt(job_info,creds_encoded=True):
    global ErrorLog
    #login
    url = "https://spib.wooribank.com/pib/Dream?withyou=CMLGN0001"

    (driver,e_msg,tb_msg,decoded_creds,ErrorLog)=login(url,job_info,creds_encoded)
    if e_msg is not "OK":
        #logger.error("login failed")
        return (None,e_msg,tb_msg,None)

    #logger.error("login is complete")
    print "login is complete"

    #parse all or one account
    try:
        amount_of_tr=driver.execute_script("return accInfoList.length;")

        acc_nos=[]
        for i in range(amount_of_tr):
            get_acc_nos_js = 'return accInfoList['+str(i)+'].cus_use_acno'
            acc_nos.append(driver.execute_script(get_acc_nos_js))

        #logger.info("generate accinfo list is done")
        print "generate acc info list is done >>",acc_nos

        acc_no_check = False
        parsed_data=[]
        for i in range(len(acc_nos)):
            acc_no = acc_nos[i]

            if decoded_creds['cred_acc_no']  == 'all' or decoded_creds['cred_acc_no']  == acc_no:

                #logger.info("now try to parse >> " + acc_no)
                print "now try to parse >> ",acc_no
                string='detailView('+str(i)+');'
                driver.execute_script(string)
                time.sleep(5)

                driver.execute_script("beforeAddDate('7');")
                #logger.info("select date")

                time.sleep(5)

                (driver,e_msg) = check_is_querying(driver)

                if e_msg is not "OK":
                    logout(driver)
                    #logger.info("log error")
                    return (None,e_msg,)


                (data,e_msg,tb_msg,e_obj)=parse_acc_table(job_info,driver.page_source)

                if e_msg is not "OK":
                    #logger.error("parsing error")
                    return (None,e_msg,tb_msg,e_obj)

                parsed_data.append(data)
                #logger.error("parse " + acc_no + " is done")
                print "parse ",acc_no," is successful"

                acc_no_check = True
                driver.get("https://spib.wooribank.com/pib/Dream?withyou=PSINQ0013")

        try:
            if acc_no_check is False:
                raise
        except:
            e_msg = "ERROR_DO_NOT_RETRY_wrong_acc_no"

            try: ##this may fail
                logout(driver)
            except:
                print "logout failed"

            return (None,e_msg,None,None)


    except:
        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        e_msg = "ERROR_RETRIABLE_error_while_parse_acc"

        try: ##this may fail
            logout(driver)
        except:
            print "logout failed"

        return (None,e_msg,tb_msg,e_obj)

    logout(driver)
    return (parsed_data,"OK",None,None)

def parse_acc_table(job_info,page_source):

    try:
        soup = BeautifulSoup(page_source,"html.parser")

        acc_owner_name = soup.find("a",attrs={'class':'login-name'}).get_text()
        #logger.info("owner_name is >> ",acc_owner_name)

        #parse_acc_info_table
        tables=soup.find_all('table',class_='tbl-type mb20 ui-set-tbl-type')

        if len(tables) != 2:
            tb_msg = traceback.format_exc()
            e_msg = "ERROR_PARSING_NOT_WORK"
            return (None,e_msg,tb_msg,None)

        acc_info_table = tables[1]
        acc_info_rows = acc_info_table.find_all("tr")

        if len(acc_info_rows) != 5:
            tb_msg = traceback.format_exc()
            e_msg = "ERROR_PARSING_NOT_WORK"
            return (None,e_msg,tb_msg,None)

        #parse acc_no
        acc_no_row = acc_info_rows[1]
        acc_no = acc_no_row.find("span").get_text().strip().replace("-","")
        #logger.info("acc_no is >> " + acc_no)
        print acc_no

        #parse balance
        balance_row = acc_info_rows[2]
        balance_tds = balance_row.find_all("td")
        if len(balance_tds) != 2:
            tb_msg = traceback.format_exc()
            e_msg = "ERROR_PARSING_NOT_WORK"
            return (None,e_msg,tb_msg,None)
        balance_td = balance_tds[0]
        balance = wonToDigit(balance_td.get_text().strip())
        #logger.info("balance is >> ",balance)
        print balance

        #parse cashable
        cashable_row = acc_info_rows[3]
        cashable_tds = cashable_row.find_all("td")
        if len(cashable_tds) != 2:
            tb_msg = traceback.format_exc()
            e_msg = "ERROR_PARSING_NOT_WORK"
            return (None,e_msg,tb_msg,None)
        cashable_td = cashable_tds[0]
        cashable = wonToDigit(cashable_td.get_text().strip())
        #logger.info("cashable is >> ",cashable)
        print cashable

        #parse total withdrawal and total deposit
        total_row = acc_info_rows[4]
        total_tds= total_row.find_all("td")
        if len(total_tds) != 2:
            tb_msg = traceback.format_exc()
            e_msg = "ERROR_PARSING_NOT_WORK"
            return (None,e_msg,tb_msg,None)
        total_withdrawal = wonToDigit(total_tds[0].get_text().strip())
        total_deposit = wonToDigit(total_tds[1].get_text().strip())
        #logger.info("total_deposit is >> ",total_deposit)
        print total_deposit

        history = []
        history_table_soup = soup.find("table",id="tt")
        rows = history_table_soup.find_all("tr")

        if len(rows) < 1:
            tb_msg = traceback.format_exc()
            e_msg = "ERROR_SOMETHING_WRONG_WITH_HISTORY_TABLE"
            return (None,e_msg,tb_msg,None)

        for rowidx in range(1,len(rows)):
            row = rows[rowidx]
            cols = row.find_all("td")
            if len(cols) < 7 :
                tb_msg = traceback.format_exc()
                e_msg = "ERROR_HISTORY_TABLE_NUMBER_OF_COLUMNS_NOT_7"
                return (None,e_msg,tb_msg,None)

            occured_at_raw = cols[0].get_text().replace(",","").strip()
            occured_at_str = occured_at_raw.replace(".","-")+":00"
            ##todo check datetime convertable

            history.append( {'occured_at' : occured_at_str,
                             'brief' : cols[1].get_text().strip(),
                             'memo' : cols[2].get_text().strip(),
                             #'send_spec' :
                             'withdraw' : cols[3].get_text().replace(",","").strip(),
                             'deposit' : cols[4].get_text().replace(",","").strip(),
                             'balance' : cols[5].get_text().replace(",","").strip(),
                             'branch' : cols[6].get_text().strip()
                             })
            #logger.info("  거래일시   적요   기재내용   찾으신금액   맡기신금액   거래후잔액   취급점  ")
            """
            logger.info("  "+occured_at_str+"  "+cols[1].get_text().strip()
                        +"  "+cols[2].get_text().strip()+"  "+cols[3].get_text().replace(",","").strip()
                        +"  "+cols[4].get_text().replace(",","").strip()+"  "+cols[5].get_text().replace(",","").strip()
                        +"  "+cols[6].get_text().strip()+"  ")
            """
        data_dict = {
                'acc_no' : acc_no,
                'acc_owner_name' : acc_owner_name,
                'balance':balance,
                'cashable':cashable,
                'total_withdrawal':total_withdrawal,
                'total_deposit':total_deposit,
                'history':history
                    }
    except:
        tb_msg = traceback.format_exc()
        e_msg = "ERROR_WHILE_PARSING"
        return (None,e_msg,tb_msg,None)

    print data_dict
    return (data_dict,"OK",None,None)

def get(job_info,creds_encoded=True):
    for t in range(10):
        (data,e_msg,tb_msg,e_obj)=get_attempt(job_info,creds_encoded)
        if e_msg == "OK":
            print "parsing is done"
            #logger.error("parsing is successful")
            ErrorLog.append("parsing is done")
            return (data,e_msg,tb_msg,ErrorLog)
        elif "ERROR_DO_NOT_RETRY" in e_msg:
            ErrorLog.append(e_msg)
            ErrorLog.append(tb_msg)
            return (data,e_msg,tb_msg,ErrorLog)
        else:
            ErrorLog.append(e_msg)
            ErrorLog.append(tb_msg)
            print e_msg
            print tb_msg
            #logger.error("ERROR >> ",e_msg)
            #logger.error("Traceback message >> ",tb_msg)
            #logger.error("retry >>",t+1,"th")

    return (data,"ERROR_DO_NOT_RETRY_MAXIMUM_GET_RETRY_EXCEEDED",tb_msg,ErrorLog)

if __name__ == "__main__":

    job_info = {}
    job_info['creds'] = {'cred_user_id':'zakk95', 'cred_user_pw':'uE^9z@', 'cred_acc_no' : '100244277302'}

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add the handlers to the #logger
    fh = logging.FileHandler("error.log")
    fh.setLevel(logging.ERROR)
    fh.formatter=formatter
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.formatter=formatter
    logger.addHandler(fh)
    logger.addHandler(ch)


    while(True):


        (data,e_msg,tb_msg,e_obj) = get(job_info,creds_encoded=False)

        #logger.error("----------------------------------------------")
        time.sleep(300)




