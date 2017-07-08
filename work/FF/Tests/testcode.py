# -*- coding: utf-8 -*-
from selenium import webdriver
import time
url = "https://www.bccard.com/app/card/MainActn.do"

user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", user_agent)
driver = webdriver.Firefox(profile)
driver.maximize_window()
driver.get(url)

time.sleep(1)
"""
driver.switch_to.frame(driver.find_element_by_name("bizMain"))

time.sleep(1)

driver.find_element_by_id("img_btn_오픈뱅킹로그인").click()
"""