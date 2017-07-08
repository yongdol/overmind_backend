# -*- coding: utf-8 -*-

import sys,time
import traceback

from BAKookminBank import login
from BAConfig import DEFAULT_RETRY_COUNT
from Comm import Comm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoAlertPresentException

from bs4 import BeautifulSoup


def get_attempt(comm):

    comm.set_attr(url="https://obank1.kbstar.com/quics?page=C018897&QViewPC=Y")
    comm = login(comm)

    if comm.last_e_msg != "OK":
        return comm

    try:
        btn_div = comm.driver.find_element_by_id("WPOP")
        btn_div.find_element_by_tag_name("input").click()
    except:
        pass

    try:
        #전계좌조회로
        comm.driver.get("https://obank1.kbstar.com/quics?page=C019088&QSL=F")
        WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, 'personal')))

        elem_acc_list = comm.driver.find_element_by_class_name('accountList')
        elem_acc_rows = elem_acc_list.find_elements_by_class_name('accountNum')

    except:
        comm.add_err("ERROR_RETRIABLE_error_while_to_whole_account_list_page", tb_msg=traceback.format_exc(), SC=True)
        return comm
    try:
        for elem_acc_num in elem_acc_rows:
            found = False
            acc_num = elem_acc_num.text.strip().replace("-", "")

            if comm.cred_decoded['cred_acc_no'] == acc_num or comm.cred_decoded['cred_acc_no'] == "all":

                comm.logger.error("found cred <" + str(comm.cred_decoded['cred_acc_no']) + ">")

                elem_acc_num.click()
                elem_acc_num.find_element_by_link_text("최근거래내역(당일)").click()
                WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, 'paging')))

                time.sleep(1)
                comm.driver.execute_script("scr_dateTerm(8);")
                time.sleep(1)
                comm.driver.execute_script("uf_GoSubmit();")
                WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, '계좌번호')))

                comm = parse_acc_page(comm)

                if comm.last_e_msg != "OK":
                    return comm

                comm.logger.error("parse <" + str(comm.cred_decoded['cred_acc_no']) + "> is done")

                found = True
                comm.driver.get("https://obank1.kbstar.com/quics?page=C019088&QSL=F")

            if not found:
                comm.add_err("ERROR_DO_NOT_RETRY_accnum_is_wrong", tb_msg=traceback.format_exc(), SC=True)
                return comm

    except:
        comm.add_err("ERROR_RETRIABLE_error_while_access", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm


def parse_acc_page(comm):

    try:
        soup = BeautifulSoup(comm.driver.page_source, "html.parser")

        acc_owner = soup.find("li", class_="h_btn h_userName").get_text().strip()
        acc_owner_name = acc_owner[:-1]

        acc_no_text = soup.find("span", class_="acct_num").get_text()
        acc_no = acc_no_text.replace("-", "").strip()

        list_account = soup.find('dl', class_='list_account')
        balance_li = list_account.find('ul', class_='list_type1 acct_list')
        balance = balance_li.find('strong').get_text().replace(",", "").strip()

        cashable = balance_li.find('strong').findNext('strong').get_text().replace(",", "").strip()

    except:
        comm.add_err("ERROR_RETRIABLE_error_while_parse_acc_info", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        transactions = []
        current_page = 1
        while True:

            time.sleep(10)

            ###TODO
            ###페이지가 10개이상일경우 나머지는 처리가 아직 안됨

            WebDriverWait(comm.driver, 10).until(EC.element_to_be_clickable((By.ID, 'paging')))
            elem_page_div = comm.driver.find_element_by_id("paging")
            page_num = len(elem_page_div.find_elements_by_tag_name("form"))

            tran_table = comm.driver.find_element_by_class_name("tType01")
            rows = tran_table.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")

            #print "len of rows>>>",len(rows)

            for rowidx in range(0, len(rows)):
                row = rows[rowidx]
                cols = row.find_elements_by_tag_name("td")

                transactions.append(
                            {
                                'occured_at': cols[0].__getattribute__("text").encode('utf-8').replace(".", "-").strip(),
                                'brief': cols[1].__getattribute__("text").encode('utf-8').strip(),
                                'memo': cols[2].__getattribute__("text").encode('utf-8').strip(),
                                'withdraw': cols[3].__getattribute__("text").encode('utf-8').replace(",", "").strip(),
                                'deposit': cols[4].__getattribute__("text").encode('utf-8').replace(",", "").strip(),
                                'balance': cols[5].__getattribute__("text").encode('utf-8').replace(",", "").strip(),
                                'send_info': cols[6].__getattribute__("text").encode('utf-8').strip(),
                                'branch': cols[7].__getattribute__("text").encode('utf-8').strip()
                            })
                #logger.info("  거래일시   적요   기재내용   찾으신금액   맡기신금액   거래후잔액   취급점  ")

            if page_num == 1:
                break
            elif page_num == current_page:
                break
            else:
                current_page += 1
                id_str = "pageinput" + str(current_page)
                comm.driver.find_element_by_id(id_str).click()
                WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, '계좌번호')))

    except TimeoutException:
        comm.add_err("ERROR_DO_NOT_RETRY_no_acc_info" ,tb_msg=traceback.format_exc(), SC=True)
        return comm
    except:
        comm.add_err("ERROR_RETRIABLE_error_while_parse_transactions", tb_msg=traceback.format_exc(), SC=True)
        return comm

    acc_info = {
        'acc_no': acc_no,
        'acc_owner_name': acc_owner_name,
        'balance': balance,
        'cashable': cashable,
        'transactions': transactions
        }

    comm.acc_infos.append(acc_info)
    comm.set_attr(last_e_msg="OK")
    return comm


def get(job_info,**comm_kwargs):

    #print comm_kwargs

    comm = Comm(job_info, **comm_kwargs)
    comm.set_attr(log_file_name="Kookmin_crawl_profile.log")

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

    flag = 1
    while True:

        if flag == 1:
            job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'TPSXL40','cred_acc_no':'41270101161887'}}
        elif flag == 2:
            job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'TPSXL40','cred_acc_no':'412132434133287'}}  #acc no
        elif flag == 3:
            job_info = {'creds':{'cred_user_id':'zadf395','cred_user_pw':'TPSXL40','cred_acc_no':'41270101161887'}}  #id
        elif flag == 4:
            job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'TPSdf34','cred_acc_no':'41270101161887'}}  #pw

        comm = get(job_info=job_info, isEncoded=False)

        if flag <= 3:
            flag += 1
        else:
            flag = 1
        if comm.acc_infos:
            comm.logger.error(">>>acc_infos : %s",comm.acc_infos)
        comm.logger.error("---------------------------------------------")
        comm.logger.removeHandler(comm.ch)
        comm.logger.removeHandler(comm.fh)
        del comm
        time.sleep(10)