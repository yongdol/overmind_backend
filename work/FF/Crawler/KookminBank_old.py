# -*- coding: utf-8 -*-
import sys,time
import traceback
from BAKookminBank_old import login
from bs4 import BeautifulSoup
url = "https://obank1.kbstar.com/quics?page=C018897&QViewPC=Y"

def get_attempt(job_info, creds_encoded=True):
    (driver,e_msg,tb_msg,e_obj) = login(url,job_info,creds_encoded)
    print e_msg
    if e_msg is not "OK":
        print "Login Failed"
        return (None,e_msg,tb_msg,e_obj)

    time.sleep(5)

    #query accounts
    script_str ="location.href='/quics?page=C019088&QSL=F'; return false;"
    elem_acc_list = driver.find_element_by_class_name('accountList')
    elem_acc_rows = elem_acc_list.find_elements_by_class_name('accountNum')

    parsed_data = []
    for elem_acc_num in elem_acc_rows:
        acc_num = elem_acc_num.get_text().strip().replace("-","")
        if job_info['creds']['cred_acc_no'] == acc_num or job_info['creds']['cred_acc_no'] == "all":

            acc_ul = driver.find_element_by_xpath("//ul[starts-with(@id,'accountFree')]")
            query_btn = acc_ul.find_element_by_link_text("조회")
            script_str = query_btn.get_attribute("onclick")

            script_str = "scr_dateTerm(8);"
            driver.execute_script(script_str)
            script_str= "uf_GoSubmit();"
            (data,e_msg,tb_msg,e_obj)=parse_acc_page(job_info,driver.page_source)

            parsed_data.append(data)
            driver.get("")

    print e_msg
    return (driver,e_msg,tb_msg,e_obj)

def parse_acc_page(job_info,page_source):
    try:
        soup = BeautifulSoup(page_source,"html.parser")

        acc_owner = soup.find("li", class_="h_btn h_userName").get_text().strip()
        acc_owner_name = acc_owner[:-1]

        acc_no_text = soup.find("span",class_="acct_num").get_text()
        acc_no = acc_no_text.replace("-","").strip()

        list_account = soup.find('dl',class_='list_account')
        balance_li = list_account.find('ul',class_='list_type1 acct_list')
        balance = balance_li.find('strong').get_text()

        cashable = balance_li.find('strong').findNext('strong').get_text()

        (history,e_msg,tb_msg,e_obj) = parse_history_table(soup)


    except:
        pass
def parse_history_table(soup):
    history = []

    history_table = soup.find('table',class_='tType01')
    rows = history_table.find_all("tr")
    for rowidx in range(1,len(rows)):
        row = rows[rowidx]
        cols = row.find_all("td")



def get(job_info, creds_encoded=True):
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


if __name__ == "__main__":

    job_info ={'creds':{'cred_user_id':'zakk95','cred_user_pw':'TPSXL40'}}

    (driver,e_msg,tb_msg_e_obj) = get(job_info,creds_encoded=False)