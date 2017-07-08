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

    comm = parse_card_page(comm)

    if comm.last_e_msg != "OK":
        return comm

    comm.set_attr(last_e_msg="OK")
    return comm

def parse_card_page(comm):

    try:
        soup = BeautifulSoup(comm.driver.page_source, "html.parser")

        ##TODO 우리카드 케이스의 경우 card_info가 4개 나왔지만 (이름,월,카드이름,결제금액) 다른 카드 검증 필요
        card_infos = soup.find("p", id="myPayment").find_all("span")

        print len(card_infos)

        card_owner_name = card_infos[0].get_text().strip()      #소유주명
        card_payment_month = card_infos[1].get_text().strip()   #결제 월
        card_name = card_infos[2].get_text().strip()            #카드 이름
        card_payment_amount = card_infos[3].get_text().strip()  #결제 금액

        card_payment_text = soup.find("div", class_="paymentTxt")

        card_payment_day = card_payment_text.find("strong").get_text().strip()
        card_payment_acc_num = card_payment_text.find("span", class_="accountNum2").get_text().strip()[7:]


        ##TODO 결제금액 테이블의 경우 BC카드 페이지 자체의 변경에 매우 취약한 구조임 주의 필요
        ##테이블 설명과 달리 할부, 일시불, 단기카드결제, 합계 까지 밖에 나타나지 않음
        card_payment_table = soup.find("table", id = "settleTable")
        card_payment_tbody = card_payment_table.find("tbody")
        card_payment_tds = card_payment_tbody.find_all("td")

        card_payment_lump_sum = card_payment_tds[0].get_text().strip()      #일시불
        card_payment_cash_service = card_payment_tds[1].get_text().strip()  #단기카드대출
        card_payment_installment = card_payment_tds[2].get_text().strip()   #할부
        card_payment_abroad = card_payment_tds[4].get_text().strip()        #해외이용액
        card_payment_sum = card_payment_tds[6].get_text().strip ()          #합계

    except:
        comm.add_err("ERROR_RETRIABLE_problem_in_parse_card_info",tb_msg=traceback.format_exc(),SC=True)
        return comm

    transactions = []

    try:
        tran_table = soup.find("table", id="cardDetailTable")
        tran_rows = tran_table.find("tbody").find_all("tr")[:-1]
        tran_row_sum = tran_table.find("tbody").find_all("tr")[-1:]

        elem_tran_table = comm.driver.find_element_by_id("cardDetailTable")
        elem_tran_tbody = elem_tran_table.find_element_by_tag_name("tbody")
        elem_tran_trs = elem_tran_tbody.find_elements_by_tag_name("tr")

        window_origin = comm.driver.window_handles[0]

        # Temporary file write tests
        f = open("crawling_result.txt", 'w')

        for i, row in enumerate(tran_rows):

            branch_info = {}

            if (tran_rows[i].find_all("td")[2].get_text().strip() == u'\uc77c\ubc18'):
                elem_tran_trs[i].find_element_by_tag_name("a").click()

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

                print name.encode('utf-8')
                
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

            else:
                branch_info = {
                    'name': tran_rows[i].find_all("td")[3].get_text().strip(),
                    'phone_num': '',
                    'address': '',
                    'homepage': '',
                    'corp_regi_num': '',
                    'branch_num': '',
                    'representative': '',
                    'business_type': ''
                }
            
            #f.write(str(branch_info))
            #f.write("\n")
            #print branch_info

            
            if (tran_rows[i].find_all("td")[2].get_text().strip() == u'\uc77c\ubc18'):
                comm.driver.close()
                comm.driver.switch_to_window(window_origin)

            cols = tran_rows[i].find_all("td")

            tr_post_date = cols[0].get_text().strip()
            tr_card = cols[1].get_text().strip()
            tr_card_type = cols[2].get_text().strip()
            tr_payment = cols[4].get_text().replace(",", "").strip()
            tr_installment_number = cols[5].get_text().strip()
            tr_monthly_principal = cols[6].get_text().replace(",", "").strip()
            tr_monthly_discount = cols[7].get_text().replace(",", "").strip()
            tr_am_ex_rate = cols[8].get_text().replace(",", "").strip()
            tr_monthly_fee = cols[9].get_text().replace(",", "").strip()
            tr_balance = cols[10].get_text().replace(",", "").strip()
            tr_top_point = cols[11].get_text().replace(",", "").strip()
            tr_installment_amount = cols[12].get_text().replace(",", "").strip()

            # tests print code
            '''
            transaction = {
                'post_date': cols[0].get_text().strip(),
                'card': cols[1].get_text().strip(),
                'card_type': cols[2].get_text().strip(),
                'trans_branch': branch_info,
                'payment': cols[4].get_text().replace(",", "").strip(),
                'installment_number': cols[5].get_text().strip(),
                'monthly_principal': cols[6].get_text().replace(",", "").strip(),
                'monthly_discount': cols[7].get_text().replace(",", "").strip(),
                'asked_amount/exchange_rate': cols[8].get_text().replace(",", "").strip(),
                'monthly_fee': cols[9].get_text().replace(",", "").strip(),
                'balance': cols[10].get_text().replace(",", "").strip(),
                'Top_point': cols[11].get_text().replace(",", "").strip(),
                'installment_amount': cols[12].get_text().replace(",", "").strip()
            }
            '''

            transaction = {
                'post_date': tr_post_date,
                'card': tr_card,
                'card_type': tr_card_type,
                'trans_branch': branch_info,
                'payment': tr_payment,
                'installment_number': tr_installment_number,
                'monthly_principal': tr_monthly_principal,
                'monthly_discount': tr_monthly_discount,
                'asked_amount/exchange_rate': tr_am_ex_rate,
                'monthly_fee': tr_monthly_fee,
                'balance': tr_balance,
                'Top_point': tr_balance,
                'installment_amount': tr_installment_amount
            }

            query_dict = {
                'id': comm.cred_decoded['cred_user_id'],
                'post_date': tr_post_date,
                'card': tr_card,
                'card_type': tr_card_type,
                'branch_name': branch_info['name'],
                'branch_phone': branch_info['phone_num'],
                'branch_address': branch_info['address'],
                'branch_homepage': branch_info['homepage'],
                'branch_corp_num': branch_info['corp_regi_num'],
                'branch_num': branch_info['branch_num'],
                'branch_representative': branch_info['representative'],
                'branch_business_type': branch_info['business_type'],
                'payment': tr_payment,
                'installment_number': tr_installment_number,
                'monthly_principal': tr_monthly_principal,
                'monthly_discount': tr_monthly_discount,
                'amount_exchange_rate': tr_am_ex_rate,
                'monthly_fee': tr_monthly_fee,
                'balance': tr_balance,
                'Top_point': tr_balance,
                'installment_amount': tr_installment_amount
            }
            
            columns = ','.join(query_dict.keys())
            placeholders = ','.join(['%s'] * len(query_dict))
            query = "insert into %s (%s) values (%s)" % ('crawl', columns, placeholders)
            
            '''
            query = "insert into crawl (id, post_date, card, card_type, branch_name, branch_phone, branch_address, branch_homepage, branch_corp_num, branch_num, branch_representative, branch_business_type, payment, installment_number, monthly_principal, monthly_discount, amount_exchange_rate, monthly_fee, balance, top_point, installment_amount) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' ,'%s', '%s')"
            '''

            f.write(str(query_dict))
            f.write("\n")

            curs.execute("set names utf8")
            curs.execute(query, query_dict.values())
            conn.commit()

            transactions.append(transaction)


        f.close()
    except:
        comm.add_err("ERROR_RETRIABLE_problem_in_parse_card_transactions",tb_msg=traceback.format_exc(),SC=True)
        f.close()
        return comm

    print transactions

    acc_info = {
        'card_owner_name': card_owner_name,
        'card_payment_month': card_payment_month,
        'card_name': card_name,
        'card_payment_amount': card_payment_amount,
        'card_payment_day': card_payment_day,
        'card_payment_acc_num': card_payment_acc_num,
        'card_payment_lump_sum': card_payment_lump_sum,
        'card_payment_cash_service': card_payment_cash_service,
        'card_payment_installment': card_payment_installment,
        'transactions': transactions
        }



    print acc_info

    comm.acc_infos.append(acc_info)
    comm.set_attr(last_e_msg="OK")
    return comm

def get(job_info,**comm_kwargs):

    #print comm_kwargs

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


    job_info = {'creds':{'cred_user_id':'zakk95','cred_user_pw':'Tpsxl80@'}}
    comm = get(job_info=job_info, isEncoded=False)
    conn.close()
