from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import re
import socket
import os
import sys

driver = webdriver.Chrome()
driver.maximize_window()
WebDriverWait(driver=driver, timeout=5)

driver.get('http://www.dianping.com/shop/91008334/review_more?pageno=1')
body = driver.find_element_by_tag_name("body")
body.send_keys(Keys.CONTROL + 't')
html_code = driver.page_source
print html_code.encode('utf-8')
time.sleep(5)


driver.get('http://www.dianping.com/shop/91008334/review_more?pageno=2')
body = driver.find_element_by_tag_name("body")
body.send_keys(Keys.CONTROL + 't')
html_code = driver.page_source
print html_code.encode('utf-8')
time.sleep(5)

driver.get('http://www.dianping.com/shop/91008334/review_more?pageno=3')
body = driver.find_element_by_tag_name("body")
body.send_keys(Keys.CONTROL + 't')
html_code = driver.page_source
print html_code.encode('utf-8')

driver.close()
# WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'QM_OwnerInfo_Icon')))
# print('Login Success')
# WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'tphoto')))
# print('Please Click A Album')
# driver.switch_to_frame(driver.find_element_by_id("tphoto"))
# WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.album-info')))
