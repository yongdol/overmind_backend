# -*- coding: utf-8 -*-
from selenium import webdriver

url = "https://spib.wooribank.com/pib/Dream?withyou=CMLGN0001"
#condition = "IE"
#condition = "Chorme"
condition = "Firefox"

if condition == "IE":
    driver = webdriver.Ie()
    driver.get(url)
    driver.maximize_window()
elif condition == "Chrome":
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()
elif condition == "Firefox":

    user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(profile)

    driver.get(url)
    driver.maximize_window()



