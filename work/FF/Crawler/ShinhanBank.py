# -*- coding: utf-8 -*-

import time,sys
import traceback

from bs4 import BeautifulSoup

from BAShinhanBank import login
from Comm import Comm
from BAConfig import DEFAULT_RETRY_COUNT

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoAlertPresentException


def get_attempt(comm):

    acc_infos = []
    comm.set_attr(url="https://open.shinhan.com/index.jsp")
    comm = login(comm)
    if comm.last_e_msg != "OK":
        return comm

    try:
        frame_check(comm)
        if comm.last_e_msg != "OK":
            return comm

        #get acc_list
        acc_list_table = comm.driver.find_element_by_id("m1_m1_grd1_body_table")
        acc_list_table_body = acc_list_table.find_element_by_id("m1_m1_grd1_body_tbody")
        acc_list_tr = acc_list_table_body.find_elements_by_tag_name("tr")

        found = False
        for row in acc_list_tr:
            acc_num_raw = row.text.split("\n")[1]
            acc_num = acc_num_raw.replace("-", "")

            if comm.cred_decoded['cred_acc_no'] == acc_num or comm.cred_decoded['cred_acc_no'] == "all":

                found = True
                comm.logger.error("found cred <" + str(comm.cred_decoded['cred_acc_no']) + ">")

                imgs = row.find_elements_by_tag_name("img")
                for img in imgs:
                    if img.get_attribute("alt").encode("utf-8") == "조회":
                        img.click()

                        frame_check(comm)
                        if comm.last_e_msg != "OK":
                            return comm

                        #페이지로딩 확인
                        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'caseb2_grp_info')))

                        #6개월 버튼
                        search_range_btn = comm.driver.find_element_by_id("text5")
                        search_range_btn.click()
                        search_btn = comm.driver.find_element_by_id("case1110_btn조회")
                        search_btn.click()

                        frame_check(comm)
                        if comm.last_e_msg != "OK":
                            return comm

                        #페이지로딩 확인
                        WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID, 'caseb2_grp_info')))

                        comm = parse_acc_page(comm)
                        if comm.last_e_msg != "OK":
                            return comm

                        frame_check(comm)
                        if comm.last_e_msg != "OK":
                            return comm

                        comm.driver.find_element_by_id("ipt_m1_m1_m1_ipt").click()
                        WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID,'m1_m1_grd1_body_table')))
                        break

        if not found:
            comm.add_err("ERROR_DO_NOT_RETRY_accnum_is_wrong", tb_msg=traceback.format_exc(), SC=True)
            return comm

    except:
        comm.add_err("ERROR_RETRIABLE_error_while_access", tb_msg=traceback.format_exc())
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm

def parse_acc_page(comm):

    try:
        acc_owner_name = comm.driver.find_element_by_id("caseb2_tbx_r1td1").text.strip()
        acc_balance = comm.driver.find_element_by_id("caseb2_tbx_r1td2").text.replace(",", "").strip()

        acc_no = comm.driver.find_element_by_id("caseb2_tbx_r2td1").text.replace("-", "").strip()
        acc_cashable = comm.driver.find_element_by_id("caseb2_tbx_r2td2").text.replace(",", "").strip()

    except:
        comm.add_err("ERROR_RETRIABLE_error_while_parse_acc_info", tb_msg=traceback.format_exc(), SC=True)
        return comm
    try:
        window_origin = comm.driver.window_handles[0]
        WebDriverWait(comm.driver, 10).until(EC.element_to_be_clickable((By.ID, 'case1110_1_전체보기')))
        comm.driver.find_element_by_id("case1110_1_전체보기").click()

        comm.driver.switch_to_window(comm.driver.window_handles[1])

        while True:
            try:
                WebDriverWait(comm.driver, 10).until(EC.presence_of_element_located((By.ID,'case1110_grd_body_tbody')))
            except TimeoutException:
                comm.driver.switch_to_window(comm.driver.window_handles[1])
                continue
            else:
                break


        """
        tran_tb_body = comm.driver.find_element_by_id("case1110_grd_body_tbody")
        rows = tran_tb_body.find_elements_by_tag_name("tr")

        transcations = []
        for row in rows:
            t0 = time.time()
            cols = row.find_elements_by_tag_name("td")

            occured_at_str = cols[0].text.strip()+" "+cols[1].text.strip()

            transcations.append({
                            'occured_at': occured_at_str,
                            'brief': cols[2].text.strip(),
                            'memo': cols[5].text.strip(),
                            'withdraw': cols[3].text.replace(",", "").strip(),
                            'deposit': cols[4].text.replace(",", "").strip(),
                            'balance': cols[6].text.replace(",", "").strip(),
                            'branch': cols[7].text.strip()
                             })
            t1 = time.time()
            print "transaction parse time>> ",t1-t0
        """

        soup = BeautifulSoup(comm.driver.page_source, "html.parser")
        trans_tb_body = soup.find("tbody", id="case1110_grd_body_tbody")
        rows = trans_tb_body.find_all("tr")

        transcations = []
        for row in rows:
            cols = row.find_all("td")

            occured_at_str = cols[0].get_text().strip() + " " + cols[1].get_text().strip()

            transcations.append(
                        {
                            'occured_at': occured_at_str,
                            'brief': cols[2].get_text().strip(),
                            'memo': cols[5].get_text().strip(),
                            'withdraw': cols[3].get_text().replace(",", "").strip(),
                            'deposit': cols[4].get_text().replace(",", "").strip(),
                            'balance': cols[6].get_text().replace(",", "").strip(),
                            'branch': cols[7].get_text().strip()
                        })

        comm.driver.close()
        comm.driver.switch_to_window(window_origin)

        acc_info = {
                'acc_no': acc_no,
                'acc_owner_name': acc_owner_name,
                'balance': acc_balance,
                'cashable': acc_cashable,
                'transactions': transcations
            }

        comm.logger.error("parse <" + str(comm.cred_decoded['cred_acc_no']) + "> is done")

        comm.acc_infos.append(acc_info)

    except:
        comm.add_err("ERROR_RETRIABLE_error_while_parse_transactions", tb_msg=traceback.format_exc(), SC=True)
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm


def frame_check(comm):
    try:
        comm.driver.switch_to_default_content()
        WebDriverWait(comm.driver, 5).until(EC.presence_of_element_located((By.ID, 'bizMain')))
        comm.driver.switch_to_frame(comm.driver.find_element_by_name("bizMain"))
    except:
        comm.add_err("ERROR_RETRIABLE_error_while_change_frame", tb_msg=traceback.format_exc(), SC=True)
        return comm


def get(job_info, **comm_kwargs):

    comm = Comm(job_info, **comm_kwargs)
    comm.set_attr(log_file_name="Shinhan_crawl_profile.log")

    for t in range(DEFAULT_RETRY_COUNT):
        comm = get_attempt(comm)

        try:
            if comm.driver:
                comm.driver.quit()
                comm.driver = None
        except:
            comm.add_err("ERROR_RETRIABLE_problem_in_webdriver", tb_msg=traceback.format_exc(), SC=True)
            return comm

        if comm.last_e_msg == "OK":
            comm.logger.error(">>>ALL PROCESS IS DONE")
            return comm
        elif "ERROR_DO_NOT_RETRY" in comm.last_e_msg:
            return comm
        else:
            time.sleep(5)
    return comm


if __name__ == "__main__":

    flag = 1
    while True:

        if flag == 1:
            job_info = {'creds':{'cred_user_id':'murane','cred_user_pw':'Tpsxl40!','cred_acc_no':'110385994336'}}
        elif flag == 2:
            job_info = {'creds':{'cred_user_id':'murane','cred_user_pw':'Tpsxl40!','cred_acc_no':'110385123416'}}   #acc no
        elif flag == 3:
            job_info = {'creds':{'cred_user_id':'mud234e','cred_user_pw':'Tpsxl40!','cred_acc_no':'110385994336'}}   #id
        elif flag == 4:
            job_info = {'creds':{'cred_user_id':'murane','cred_user_pw':'Tps32xdd34!','cred_acc_no':'110385994336'}}   #pw

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
