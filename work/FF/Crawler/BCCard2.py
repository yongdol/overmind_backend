# -*- coding: utf-8 -*-

import time,sys
import traceback

# import path configuration
sys.path.append("../BankAuth/")

# encoding configuration
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup

from BABCCard import login
from Comm import Comm
from BAConfig import DEFAULT_RETRY_COUNT

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

# connect database
import pymysql
conn = pymysql.connect(host='localhost', user='outtoin', password='dlqmsdl1017', db='crawl', charset='utf8')
curs = conn.cursor()


def get_attempt(comm):

    acc_infos = []
    comm.set_attr(url="https://www.bccard.com/app/card/MainActn.do")
    comm = login(comm)
    if comm.last_e_msg != "OK":
        return comm

    ##TODO 최근명세서 항목의 파싱에대해 엄밀한 점근이 필요

    try:
        WebDriverWait(comm.driver,
         5).until(EC.presence_of_element_located((By.CLASS_NAME, 'mybc_info')))
        elem_recent_spec = comm.driver.find_element_by_class_name("price")
        time.sleep(5)
        elem_recent_spec.find_element_by_tag_name("a").click()
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'selBank')))
        time.sleep(5)

    except:
        comm.add_err("ERROR_RETRIABLE_problem_in_find_recent_spec",tb_msg=traceback.format_exc(),SC=True)
        return comm

    try:
        comm.driver.get("https://www.bccard.com/app/card/ApproveActn.do")

    except:
        comm.add_err("ERROR_RETRIABLE_problem_in_find_approve_actn", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm = parse_card_page(comm)

    if comm.last_e_msg != "OK":
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm

def parse_card_page(comm):

    try:
        WebDriverWait(comm.driver, 1000)
        time.sleep(5)

        soup = BeautifulSoup(comm.driver.page_source, "html.parser")

        card_summary_table = soup.find("table", id = "inSummaryTable")
        card_summary_tbody = card_summary_table.find("tbody")
        card_summary_tds = card_summary_tbody.find_all("td")

        num_payment_sum = card_summary_tds[1].get_text().replace(u"\uac74", "").strip()
        num_payment_lump_sum = card_summary_tds[2].get_text().replace(u"\uac74", "").strip()
        num_payment_installment = card_summary_tds[3].get_text().replace(u"\uac74", "").strip()
        num_payment_cash_service = card_summary_tds[4].get_text().replace(u"\uac74", "").strip()

        amnt_payment_sum = card_summary_tds[6].get_text().replace(",", "").replace(u"\uc6d0", "").strip()
        amnt_payment_lump_sum = card_summary_tds[7].get_text().replace(",", "").replace(u"\uc6d0", "").strip()
        amnt_payment_installment = card_summary_tds[8].get_text().replace(",", "").replace(u"\uc6d0", "").strip()
        amnt_payment_cash_service = card_summary_tds[9].get_text().replace(",", "").replace(u"\uc6d0", "").strip()

    except:
        comm.add_err("ERROR_RETRIABLE_problem_in_parse_card_summary_info",tb_msg=traceback.format_exc(),SC=True)
        return comm


    transactions = []

    # For comm.last_crawl
    is_first = True

    while True:
        try:
            soup = BeautifulSoup(comm.driver.page_source, "html.parser")

            tran_table = soup.find("table", id="inDetailTable")
            tran_rows = tran_table.find("tbody").find_all("tr") 

            elem_tran_table = comm.driver.find_element_by_id("inDetailTable")
            elem_tran_tbody = elem_tran_table.find_element_by_tag_name("tbody")
            elem_tran_trs = elem_tran_tbody.find_elements_by_tag_name("tr") 

            window_origin = comm.driver.window_handles[0]   

            # Temporary file write test
            # f = open("crawling_result2.txt", 'w')   

            print len(tran_rows)

            for i, row in enumerate(tran_rows): 

                elem_tran_tds = elem_tran_trs[i].find_elements_by_tag_name("td")    

                branch_info = {}
                approval_info = {}  

                elem_tran_tds[3].find_element_by_tag_name("a").click()  

                while True:
                    try:
                        WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, 'popCon')))
                    except TimeoutException:
                        comm.driver.switch_to_window(comm.driver.window_handles[1])
                        continue
                    else:
                        break   

                comm.driver.switch_to_window(comm.driver.window_handles[1])
                WebDriverWait(comm.driver, 10).until(EC.element_to_be_clickable((By.ID, 'popCon'))) 

                elem_aprv_info_div = comm.driver.find_element_by_id("popCon")
                elem_aprv_info_tbl = elem_aprv_info_div.find_element_by_tag_name("table")
                elem_aprv_info_trs = elem_aprv_info_tbl.find_elements_by_tag_name("tr") 

                aprv_card_type = elem_aprv_info_trs[0].find_element_by_tag_name("td").__getattribute__("text")
                aprv_card_num = elem_aprv_info_trs[1].find_element_by_tag_name("td").__getattribute__("text")
                aprv_date_time = elem_aprv_info_trs[2].find_element_by_tag_name("td").__getattribute__("text")
                aprv_payment_type = elem_aprv_info_trs[3].find_element_by_tag_name("td").__getattribute__("text")
                aprv_payment = elem_aprv_info_trs[4].find_element_by_tag_name("td").__getattribute__("text").replace(",","").replace(u"\uc6d0", "")
                aprv_VAT = elem_aprv_info_trs[5].find_element_by_tag_name("td").__getattribute__("text").replace(",","").replace(u"\uc6d0", "")
                aprv_tip = elem_aprv_info_trs[6].find_element_by_tag_name("td").__getattribute__("text").replace(",","").replace(u"\uc6d0", "")
                aprv_approval_number = elem_aprv_info_trs[7].find_element_by_tag_name("td").__getattribute__("text")
                aprv_branch_name = elem_aprv_info_trs[8].find_element_by_tag_name("td").__getattribute__("text")
                aprv_branch_addr = elem_aprv_info_trs[9].find_element_by_tag_name("td").__getattribute__("text")
                aprv_branch_num = elem_aprv_info_trs[10].find_element_by_tag_name("td").__getattribute__("text")
                aprv_corp_num = elem_aprv_info_trs[11].find_element_by_tag_name("td").__getattribute__("text")
                aprv_phone_num = elem_aprv_info_trs[12].find_element_by_tag_name("td").__getattribute__("text") 

                approval_info = {
                    'card_type' : aprv_card_type,
                    'card_num' : aprv_card_num,
                    'post_date_time' : aprv_date_time,
                    'payment_type' : aprv_payment_type,
                    'payment'    : aprv_payment,
                    'VAT' : aprv_VAT,
                    'tip' : aprv_tip,
                    'approval_number' : aprv_approval_number,
                    'branch_name' : aprv_branch_name,
                    'branch_addr' : aprv_branch_addr,
                    'branch_num' : aprv_branch_num,
                    'corp_regi_num' : aprv_corp_num,
                    'phone_num' : aprv_phone_num
                }   

                approval_query = {
                    'approval_number' : aprv_approval_number,
                    'card_type' : aprv_card_type,
                    'card_num' : aprv_card_num,
                    'post_date_time' : aprv_date_time,
                    'payment_type' : aprv_payment_type,
                    'payment' : aprv_payment,
                    'vat' : aprv_VAT,
                    'tip' : aprv_tip,
                    'branch_name' : aprv_branch_name,
                    'branch_addr' : aprv_branch_addr,
                    'branch_num' : aprv_branch_num,
                    'corp_regi_num' : aprv_corp_num,
                    'phone_num' : aprv_phone_num
                } 

                columns = ','.join(approval_query.keys())
                placeholders = ','.join(['%s'] * len(approval_query))
                query = "insert into %s (%s) values (%s)" % ('approval_info', columns, placeholders)

                curs.execute("set names utf8")
                curs.execute(query, approval_query.values())
                conn.commit()

                comm.driver.close()
                comm.driver.switch_to_window(window_origin) 

                if (comm.driver.find_element_by_id("area_clss1").is_selected()):
                    elem_tran_tds[4].find_element_by_tag_name("a").click()  

                    while True:
                        try:
                            WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID,'popCon')))
                        except TimeoutException:
                            comm.driver.switch_to_window(comm.driver.window_handles[1])
                            continue
                        else:
                            break   

                    comm.driver.switch_to_window(comm.driver.window_handles[1]) 

                    WebDriverWait(comm.driver, 10).until(EC.element_to_be_clickable((By.ID, 'popCon'))) 

                    elem_info_div = comm.driver.find_element_by_id("popCon")
                    elem_info_uls = elem_info_div.find_elements_by_tag_name("ul")   

                    ##TODO 인코딩 한번 확인해보세요    

                    name = comm.driver.find_element_by_id("icon").__getattribute__("text")
                    phone_num = elem_info_uls[0].find_elements_by_tag_name("li")[0].__getattribute__("text")[7:]
                    address = elem_info_uls[0].find_elements_by_tag_name("li")[1].__getattribute__("text")[7:]
                    homepage = elem_info_uls[0].find_elements_by_tag_name("li")[2].__getattribute__("text")[7:]     

                    corp_regi_num = elem_info_uls[2].find_elements_by_tag_name("li")[0].__getattribute__("text")[10:]
                    branch_num = elem_info_uls[2].find_elements_by_tag_name("li")[1].__getattribute__("text")[8:]
                    representative = elem_info_uls[2].find_elements_by_tag_name("li")[2].__getattribute__("text")[7:]
                    business_type = elem_info_uls[2].find_elements_by_tag_name("li")[3].__getattribute__("text")[5:]    
                        

                    branch_info = {
                        'name': name,
                        'phone_num': phone_num,
                        'address': address,
                        'homepage': homepage,
                        'corp_regi_num': corp_regi_num,
                        'branch_num': branch_num,
                        'representative': representative,
                        'business_type': business_type,
                    }   

                    comm.driver.close()
                    comm.driver.switch_to_window(window_origin) 

                else:
                    branch_info = {
                        'name': name,
                        'phone_num': '',
                        'address': '',
                        'homepage': '',
                        'corp_regi_num': '',
                        'branch_num': '',
                        'representative': '',
                        'business_type': ''
                    }   

                cols = tran_rows[i].find_all("td")  

                tr_post_date_time = cols[0].get_text().replace("<br>", " ").strip()
                tr_card = cols[1].get_text().replace("<br>", " ").strip()
                tr_card_type = cols[2].get_text().strip()
                tr_approval_info = approval_info
                tr_payment = cols[5].get_text().replace(",", "").replace(u"\uc6d0", "").strip()
                tr_payment_type = cols[6].get_text().strip()
                tr_reception_status = cols[7].get_text().strip()
                tr_payment_date = cols[8].get_text().strip()
                tr_cancel_info = cols[9].get_text().strip() 

                transaction = {
                    'post_date_time' : tr_post_date_time,
                    'card' : tr_card,
                    'card_type' : tr_card_type,
                    'approval_info' : tr_approval_info,
                    'trans_branch' : branch_info,
                    'payment' : tr_payment,
                    'payment_type' : tr_payment_type,
                    'reception_status' : tr_reception_status,
                    'payment_date' : tr_payment_date,
                    'cancel_info' : tr_cancel_info
                }

                transaction_query = {
                    'aprv_num' : tr_approval_info['approval_number'],
                    'post_date_time' : tr_post_date_time,
                    'card' : tr_card,
                    'card_type' : tr_card_type,
                    'branch_name' : branch_info['name'],
                    'payment' : tr_payment,
                    'payment_type' : tr_payment_type,
                    'reception_status' : tr_reception_status,
                    'payment_date' : tr_payment_date,
                    'cancel_info' : tr_cancel_info
                }   
                
                columns = ','.join(transaction_query.keys())
                placeholders = ','.join(['%s'] * len(transaction_query))
                query = "insert into %s (%s) values (%s)" % ('transactions', columns, placeholders)

                curs.execute("set names utf8")
                curs.execute(query, transaction_query.values())
                conn.commit()


                transactions.append(transaction)

                # For last_crawl
                if is_first:
                    comm.last_crawl = transaction
                    is_first = False

            '''
            f.close()
            '''

        except:
            comm.add_err("ERROR_RETRIABLE_problem_in_parse_card_transactions",tb_msg=traceback.format_exc(),SC=True)
            # f.close()
            return comm

        if (comm.driver.find_element_by_id("paging").find_elements_by_tag_name("a")[0].__getattribute__("text")== u'\ub2e4\uc74c'):
            comm.driver.find_element_by_id("paging").find_elements_by_tag_name("a")[0].click()

        elif (len(comm.driver.find_element_by_id("paging").find_elements_by_tag_name("a")) == 2):
            comm.driver.find_element_by_id("paging").find_elements_by_tag_name("a")[1].click()

        else:
            break

        

    print transactions

    acc_info = {
        'user': comm.cred_decoded['cred_user_id'],
        'transactions': transactions
    }



    print acc_info

    comm.acc_infos.append(acc_info)
    
    comm.set_attr(last_e_msg="OK")
    return comm

def get(job_info,**comm_kwargs):

    #print comm_kwargs
    print job_info

    comm = Comm(job_info, **comm_kwargs)
    comm.set_attr(log_file_name="BCCard_crawl_profile.log")

    for t in range(DEFAULT_RETRY_COUNT):
        comm = get_attempt(comm)

        try:
            if comm.driver:
                comm.driver.quit()
                comm.driver = None
        except:
            comm.add_err("ERROR_RETRIABLE_problem_in_closing_webdriver", tb_msg=traceback.format_exc(), SC=True)
            return comm

        if comm.last_e_msg == "OK":
            comm.logger.error(">>>ALL PROCESS IS DONE")
            return comm
        elif "ERROR_DO_NOT_RETRY" in comm.last_e_msg:
            return comm
        else:
            time.sleep(5)
    comm.add_err("ERROR_DO_NOT_RETRY_retry_count_exceed")
    return comm

if __name__ == "__main__":


    job_info = {u'status': None, u'scraper_id': None, u'user_id': None, u'job_id': None, u'last_crawl': None, u'subsc_id': None, u'subsc_status': None, u'VPC_IP': u'172.31.38.134', u'acc_type': u'card', u'disp_name': u'\ube44\uc528\uce74\ub4dc', u'instance_id': u'i-0ba239e83b3f0da12', u'platform': u'aws', u'VPN_IP': None, u'is_scraper': True, u'is_free': True, u'mod_name': u'BCCard', u'plan': u'onetime', u'dsource_id': 6, u'creds': {u'cred_user_id': u'zakk95', u'cred_user_pw': u'Tpsxl80@', u'cred_acc_no': u'1234'}, u'ded_subsc': None}
    comm = get(job_info=job_info, isEncoded=False)
    conn.close()
