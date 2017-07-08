# -*- coding: cp949 -*-

###CONFIG#####
url = "https://spib.wooribank.com/spd/Dream?withyou=CMSPD0010"
#name = 'WooriSpeed'


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.
from bs4 import BeautifulSoup

from Utils import wonToDigit
from BAWooriSpeed import login

import sys,time,re
from datetime import datetime
import traceback

def get_attempt(job_info,creds_encoded=True):
    
    time.sleep(5)
    
    (driver,e_msg,tb_msg,e_obj) = login(url,job_info,creds_encoded)
    print e_msg
    if e_msg is not "OK":
        print "Login Failed"
        return (None,e_msg,None,None)
        
    ##everything below is retriable
    ##TODO more specific error handling
    
    try:
            

        ### list last 3 months
        driver.execute_script("setToday();setCalTerm(true, 'INQ_EDT_10', 'INQ_SDT_10', 'M', 3);return false;")
        time.sleep(1)
        driver.execute_script("doSubmit(); return false")
        time.sleep(5)

        ###

        #print driver.page_source

        html = BeautifulSoup(driver.page_source,"html.parser")

        acc_owner_name_text_cp949 = "고객명"
        acc_owner_name_text = acc_owner_name_text_cp949.decode('cp949')
        acc_owner_name_row = html.find("th",text=acc_owner_name_text)
        acc_owner_name = acc_owner_name_row.find_next_sibling("td").get_text().replace(",","").strip()

        acc_no_text_cp949 = "계좌번호"
        acc_no_text = acc_no_text_cp949.decode('cp949')
        acc_no_row = html.find("th",text=acc_no_text)
        acc_no = acc_no_row.find_next_sibling("td").get_text().replace(",","").strip()
        #trs = html.find_all("tr")
        #for tr in trs:

        balance_text_cp949 = "현재잔액"
        balance_text = balance_text_cp949.decode('cp949')
        balance_row = html.find("th",text=balance_text)
        balance = wonToDigit(balance_row.find_next_sibling("td").get_text().replace(",","").strip())
        print balance


        cashable_text_cp949 = "출금가능액"
        cashable_text = cashable_text_cp949.decode('cp949')
        cashable_row = html.find("th",text=cashable_text)
        cashable = wonToDigit(cashable_row.find_next_sibling("td").get_text().replace(",","").strip())
        print cashable


        #찾으신 금액 합계
        total_withdrawal_text_cp949 = "찾으신금액 합계"
        total_withdrawal_text = total_withdrawal_text_cp949.decode('cp949')
        total_withdrawal_row = html.find("th",text=total_withdrawal_text)
        total_withdrawal = wonToDigit(total_withdrawal_row.find_next_sibling("td").get_text().replace(",","").strip())
        print total_withdrawal

        #맡기신 금액 합계
        total_deposit_text_cp949 = "맡기신금액 합계"
        total_deposit_text = total_deposit_text_cp949.decode('cp949')
        total_deposit_row = html.find("th",text=total_deposit_text)
        total_deposit = wonToDigit(total_deposit_row.find_next_sibling("td").get_text().replace(",","").strip())
        print total_deposit

        ##history_table
        history = []
        #history_table_soup = html.find("table",class_="tbl-type-1 mb20")
        #"tbl-type-1 mb20 ui-set-tbl-type"
        history_table_soup = html.find("table",class_="tbl-type-1 mb20 ui-set-tbl-type")
        rows = history_table_soup.find_all("tr")
        ##TODO: if no rows? 1 rows?
        for rowidx in range(1,len(rows)):
            row = rows[rowidx]
            cols = row.find_all("td")
            occured_at_raw = cols[0].get_text().replace(",","").strip()
            occured_at_str = occured_at_raw.replace(".","-")
            occured_at = datetime.strptime(occured_at_str,"%Y-%m-%d %H:%M:%S")

            balance = cols[5].get_text().replace(",","").strip()
            if not balance.isdigit():
                print "balance is not digit:", balance
                raise

            #print occured_at_str


            ##check if i am to break
            found_old = False
            if job_info['plan'] != "onetime":
                print "this is not onetime", job_info['plan'], job_info['last_crawl']
                if len(job_info['last_crawl']) > 0:
                    for last_crawl in job_info['last_crawl']:
                        if last_crawl['acc_no'] == acc_no:
                            if (occured_at_str == last_crawl['occured_at'] and
                                    balance == str(last_crawl['balance'])
                                ) :
                                print "found duplicate. break"
                                ##we have duplicate. skip.. ##TODO: do i have to record even if the balance did not change?
                                found_old = True
                                break
                            #elif occured_at_str < last_crawl['occured_at']:
                            #    print "older record found. break"
                            #    break
                    if found_old:
                        break

                #if occured_at > last_occured_at:

            history.append( {'occured_at' : occured_at_str,
                             'brief' : cols[1].get_text().replace(",","").strip(),
                             'memo' : cols[2].get_text().replace(",","").strip(),
                             'withdraw' : cols[3].get_text().replace(",","").strip(),
                             'deposit' : cols[4].get_text().replace(",","").strip(),
                             'balance' : cols[5].get_text().replace(",","").strip(),
                             'branch' : cols[6].get_text().replace(",","").strip(),
                             'rowidx' : rowidx, ##to sort
                              })
                
        history.sort(key=lambda k: k['rowidx'], reverse=True)
        #print history
        data = [{'acc_no' : acc_no,
                'acc_owner_name' : acc_owner_name,
                'balance':balance,
                'cashable':cashable,
                'total_withdrawal':total_withdrawal,
                'total_deposit':total_deposit,
                'history':history,},]
        print data

    except:

        tb_msg = traceback.format_exc()
        e_obj = sys.exc_info()
        e_msg = "ERROR_RETRIABLE_in_GET"
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

def get(job_info,creds_encoded=True):
    for t in range(10):
        (data,e_msg,tb_msg,e_obj) = get_attempt(job_info,creds_encoded)
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

if __name__ == "__main__":
    job_info = {}
    job_info['creds'] = {'cred_acc_no':'1002442773027', 'cred_acc_pw':'4123', 'cred_ssn' : '761001'}
    (driver,e_msg,tb_msg,e_obj) = get(job_info,creds_encoded=False)
