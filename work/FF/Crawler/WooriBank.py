# -*- coding: utf-8 -*-

import sys,logging

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
from BAConfig import DEFAULT_RETRY_COUNT
from BAWooriBank import login
from Comm import Comm

import sys,time,re,os
from datetime import datetime
import traceback


def get_attempt(comm):

    comm = login(comm)

    if comm.last_e_msg != "OK":
        return comm

    #parse all or one account
    try:
        amount_of_tr = comm.driver.execute_script("return accInfoList.length;")

        acc_nos = []
        for i in range(amount_of_tr):
            get_acc_nos_js = 'return accInfoList[' + str(i) + '].cus_use_acno'
            acc_nos.append(comm.driver.execute_script(get_acc_nos_js))

        acc_check = False
        acc_infos = []
        for i in range(len(acc_nos)):
            acc_no = acc_nos[i]
            if comm.cred_decoded['cred_acc_no'] == 'all' or comm.cred_decoded['cred_acc_no'] == acc_no:

                comm.logger.error("found cred <" + str(comm.cred_decoded['cred_acc_no']) + ">")

                script_str='detailView(' + str(i) + ');'
                comm.driver.execute_script(script_str)
                WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, 'trnsSearch')))

                comm.driver.execute_script("beforeAddDate('7');")

                comm = check_is_querying(comm)

                if comm.last_e_msg != "OK":
                    comm = logout(comm)
                    return comm

                comm = parse_acc_table(comm)

                if comm.last_e_msg != "OK":
                    comm = logout(comm)
                    return comm

                acc_infos.append(comm.acc_info)

                comm.logger.error("parse <" + str(comm.cred_decoded['cred_acc_no']) + "> is done")

                acc_check = True
                comm.driver.get("https://spib.wooribank.com/pib/Dream?withyou=PSINQ0013")

        try:
            if acc_check is False:
                raise
        except:
            comm.add_err("ERROR_DO_NOT_RETRY_wrong_acc_no", tb_msg=traceback.format_exc(), SC=True)
            comm = logout(comm)
            return comm

    except:
        comm.add_err("ERROR_RETRIABLE_error_while_parse_acc", tb_msg=traceback.format_exc(), SC=True)
        comm = logout(comm)
        return comm

    comm.set_attr(last_e_msg="OK")
    comm = logout(comm)
    return comm


def check_is_querying(comm):
    try:
        WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, 'trnsSearch')))
    except:
        comm.add_err("ERROR_RETRIABLE_error_while_querying", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm


def logout(comm):
    try:
        time.sleep(3)
        elem_popup_close = comm.driver.find_element_by_link_text("로그아웃")
        elem_popup_close.click()

        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'logOut2')))
        elem_popup_close2 = comm.driver.find_element_by_id("logOut2")
        elem_popup_close2.click()

        login_area_wrap = comm.driver.find_element_by_id("login-area-wrap")

        try:
            if login_area_wrap.find_element_by_tag_name("p").__getattribute__("text").encode('utf-8') != "안전하게 로그아웃 되었습니다.":
                raise
        except:
            comm.add_err("ERROR_RETRIABLE_error_while_logout", tb_msg=traceback.format_exc(), SC=True)
            return comm
    except:
        comm.add_err("ERROR_RETRIABLE_error_while_logout", tb_msg=traceback.format_exc(), SC=True)
        return comm

    try:
        comm.driver.quit()
        comm.driver = None
    except:
        comm.add_err("ERROR_RETRIABLE_problem_in_closing_webdriver",tb_msg=traceback.format_exc(),SC=True)
        return comm

    return comm


def parse_acc_table(comm):

    try:
        soup = BeautifulSoup(comm.driver.page_source, "html.parser")

        acc_owner_name = soup.find("a", attrs={'class': 'login-name'}).get_text()

        #parse_acc_info_table
        tables = soup.find_all('table', class_='tbl-type mb20 ui-set-tbl-type')

        if len(tables) != 2:
            comm.add_err("ERROR_PARSING_NOT_WORK_accinfo_table", tb_msg=traceback.format_exc(), SC=True)
            return comm

        acc_info_table = tables[1]
        acc_info_rows = acc_info_table.find_all("tr")

        if len(acc_info_rows) != 5:
            comm.add_err("ERROR_PARSING_NOT_WORK_acc_info_rows", tb_msg=traceback.format_exc(), SC=True)
            return comm

        #parse acc_no
        acc_no_row = acc_info_rows[1]
        acc_no = acc_no_row.find("span").get_text().strip().replace("-", "")

        #parse balance
        balance_row = acc_info_rows[2]
        balance_tds = balance_row.find_all("td")
        if len(balance_tds) != 2:
            comm.add_err("ERROR_PARSING_NOT_WORK_balance", tb_msg=traceback.format_exc(), SC=True)
            return comm
        balance_td = balance_tds[0]
        balance = wonToDigit(balance_td.get_text().strip())

        #parse cashable
        cashable_row = acc_info_rows[3]
        cashable_tds = cashable_row.find_all("td")
        if len(cashable_tds) != 2:
            comm.add_err("ERROR_PARSING_NOT_WORK_cashable", tb_msg=traceback.format_exc(), SC=True)
            return comm
        cashable_td = cashable_tds[0]
        cashable = wonToDigit(cashable_td.get_text().strip())

        #parse total withdrawal and total deposit
        total_row = acc_info_rows[4]
        total_tds = total_row.find_all("td")
        if len(total_tds) != 2:
            comm.add_err("ERROR_PARSING_NOT_WORK_total", tb_msg=traceback.format_exc(), SC=True)
            return comm
        total_withdrawal = wonToDigit(total_tds[0].get_text().strip())
        total_deposit = wonToDigit(total_tds[1].get_text().strip())

        transactions = []
        trans_table_soup = soup.find("table", id="tt")
        rows = trans_table_soup.find_all("tr")

        if len(rows) < 1:
            comm.add_err("ERROR_PARSING_NOT_WORK_transactions", tb_msg=traceback.format_exc(), SC=True)
            return comm

        for rowidx in range(1, len(rows)):
            row = rows[rowidx]
            cols = row.find_all("td")
            if len(cols) < 7:
                comm.add_err("ERROR_PARSING_NOT_WORK_trans_table_row", tb_msg=traceback.format_exc(), SC=True)
                return comm

            occured_at_raw = cols[0].get_text().replace(",", "").strip()
            occured_at_str = occured_at_raw.replace(".", "-") + ":00"
            ##todo check datetime convertable

            transactions.append(
                        {
                            'occured_at': occured_at_str,
                            'brief': cols[1].get_text().strip(),
                            'memo': cols[2].get_text().strip(),
                            'withdraw': cols[3].get_text().replace(",", "").strip(),
                            'deposit': cols[4].get_text().replace(",", "").strip(),
                            'balance': cols[5].get_text().replace(",", "").strip(),
                            'branch': cols[6].get_text().strip()
                        })
            #logger.info("  거래일시   적요   기재내용   찾으신금액   맡기신금액   거래후잔액   취급점  ")
            """
            logger.info("  "+occured_at_str+"  "+cols[1].get_text().strip()
                        +"  "+cols[2].get_text().strip()+"  "+cols[3].get_text().replace(",","").strip()
                        +"  "+cols[4].get_text().replace(",","").strip()+"  "+cols[5].get_text().replace(",","").strip()
                        +"  "+cols[6].get_text().strip()+"  ")
            """
    except:
        comm.add_err("ERROR_RETRIABLE_error_while_parse_accinfo",tb_msg=traceback.format_exc(),SC=True)
        return comm

    acc_info = {
        'acc_no': acc_no,
        'acc_owner_name': acc_owner_name,
        'balance': balance,
        'cashable': cashable,
        'total_withdrawal': total_withdrawal,
        'total_deposit': total_deposit,
        'transactions': transactions
            }

    comm.acc_infos.append(acc_info)
    comm.set_attr(last_e_msg="OK")
    return comm


def get(job_info,**comm_kwargs):

    comm = Comm(job_info, **comm_kwargs)
    comm.set_attr(url="https://spib.wooribank.com/pib/Dream?withyou=CMLGN0001", log_file_name="Woori_crawl_profile.log")

    for t in range(DEFAULT_RETRY_COUNT):
        comm = get_attempt(comm)

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
            job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'uE^9z@','cred_acc_no':'01866145102001'}}
        elif flag == 2:
            job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'uE^9z@','cred_acc_no':'01866141324343'}}       #acc_no
        elif flag == 3:
            job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'uE^9qdfq','cred_acc_no':'01866145102001'}}     #pw
        elif flag == 4:
            job_info = {'creds':{'cred_user_id':'zakk95dfq2','cred_user_pw':'uE^9z@','cred_acc_no':'01866145102001'}}   #id

        comm = get(job_info=job_info, isEncoded=False)

        if flag <= 3:
            flag += 1
        else:
            flag = 1

        comm.logger.error(">>>acc_infos :",comm.acc_infos)
        comm.logger.error("---------------------------------------------")
        comm.logger.removeHandler(comm.ch)
        comm.logger.removeHandler(comm.fh)
        del comm
        time.sleep(10)


