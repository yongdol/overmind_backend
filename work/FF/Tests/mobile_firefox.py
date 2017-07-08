# -*- coding: utf-8 -*-
from selenium import webdriver

url = "https://open.shinhan.com/index.jsp"
#url = "https://open.shinhan.com/websquare/websquare.jsp?w2xPath=/oib/login/oib_login.xml"
user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
#user_agent = "Mozilla/5.0 (Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_0_1 like Mac OS X; fr-fr) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5G77 Safari/525.20"
#user_agent="Mozilla/5.0 (Linux; U; Android 2.1-update1; ko-kr; Nexus One Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17"


profile = webdriver.FirefoxProfile()
#profile = webdriver.FirefoxProfile('C:₩₩Users₩₩Administrator₩₩AppData₩₩Roaming₩₩Mozilla₩₩Firefox₩₩Profiles₩₩emsx2iyb.selenium_banking')

profile.set_preference("general.useragent.override", user_agent)
driver = webdriver.Firefox(profile)
driver.implicitly_wait(10)

#time.sleep(1)
driver.maximize_window()
driver.get(url)
