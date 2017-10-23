#!/usr/bin/env Python
# coding=utf-8
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import urllib2
import urllib
import requests
from bs4 import BeautifulSoup
import socket
import random
import json
import os
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')
threshold = 98  # favorable rate

retry = 0

driver = webdriver.Chrome()
driver.maximize_window()
# read a url and save the comments on the page to file
# 通过url读取一个页面的内容并返回
def get_page_code(url):# get the encode of the url

    request = urllib2.Request(url)
    request.add_header('User-Agent',
                       'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/47.0.2526.73 Chrome/47.0.2526.73 Safari/537.36')
    try:
        response = urllib2.urlopen(request, timeout=2)
        page_code = response.read()
        global retry
        retry = 0
        return page_code.decode('utf-8')
    except urllib2.URLError as e:
        print('网络错误:%s' % url)
        if retry < 5:
            retry += 1
            get_page_code(url)
    except UnicodeDecodeError as e:
        #print(e)
        try:
            return page_code.decode('gbk')
        except UnicodeDecodeError as ee:
            print(ee)
    except socket.timeout:
        print('超时:%s' % url)
        if retry < 5:
            retry += 1
            get_page_code(url)
    except Exception as e:
        print('其他错误 URL:' + url)
        if retry < 5:
            retry += 1
            get_page_code(url)


def get_page_code_from_chrome(url):  # get the encode of the url
    try:
        driver.get(url)
        body = driver.find_element_by_tag_name("body")
        body.send_keys(Keys.CONTROL + 't')
        page_code = driver.page_source
        global retry
        retry = 0
        return page_code
                # return page_code.decode('gb2312')
    except urllib2.URLError as e:
        print('网络错误:%s' % url)
        print page_code
        if retry < 5:
           retry += 1
           get_page_code(url)
    except UnicodeDecodeError as e:
        try:
            return page_code.decode('gbk')
        except UnicodeDecodeError as ee:
            print(ee)
    except socket.timeout:
        print('超时:%s' % url)
        if retry < 5:
            retry += 1
            get_page_code(url)
    except Exception as e:
        print('其他错误 URL:' + url)
        if retry < 5:
            retry += 1
            get_page_code(url)


# call the func save_current_page_comment to save one page
def save_current_page_comment(url, file):
    page_code = get_page_code(url)
    if page_code is None:
        return False
    html = page_code
    try:
        sidx = str(html).find('{')
        eidx = str(html).rfind('}')
        html = str(html)[sidx: (eidx+1)]
        dic = json.loads(html)
        ratio = int(str(dic[u'productCommentSummary'][u'goodRateShow']))
        if (ratio > threshold):
            return False
        con = dic[u'comments']
        if con is None or len(con) == 0:
            return False
        f = open(file, 'a')
        for c in con:
            f.write(str(c[u'score']))
            f.write('\t')
            f.write(str(c[u'content']).replace('\n', ' ') + '\n')
        f.close()
        print("*****get comment from " + url + "*******")
    except ValueError as e:
        print(url)
        print(e)
        return False
    except KeyError as e:
        print(url)
        print(e)
        return False
    except AttributeError as e:
        print(url)
        print(e)
        return False
    except Exception as e:
        print(url)
        print(e)
        return False
    return True


def save_dianping_review(url, file):
    page_code = get_page_code_from_chrome(url)  #######################修改抓取函数###########################################
    if page_code is None:
        return False
    if '下一页' not in page_code:# the  last page
        return False
    try:
        soup = BeautifulSoup(page_code, 'lxml')  # id="plist"
        res = []
        comment = soup.find('div', attrs={'class': 'main'}).find('div', attrs={'class': 'comment-mode'}).find('div', attrs={'class': 'comment-list'})
        reviews = comment.find('ul').find_all('li', recursive=False)
        f = open(file, 'a')
        for review in reviews:
            content = review.find('div', attrs={'class': 'content'})
            #print(content.find('div', attrs={'class': 'user-info'}).find('span').get('class'))
            rate = str(content.find('div', attrs={'class': 'user-info'}).find('span').get('class')[1])[-2]
            content_txt = content.find('div', attrs={'class': 'comment-txt'})
            ccontent_txt_str = content_txt.find('div', attrs={'class': 'J_brief-cont'}).contents[0]
            f.write(rate + "\t" + str(ccontent_txt_str) + "\n")
            #time.sleep(2)
        f.close()
        print("*****get comment from " + url + "*******")
        return True   ###之前少了返回值，导致只能抓取一页
    except Exception as e:
        print(url)
        print(e)
        return True


# random p pages
def get_SpecificItem_random_page(file, baseurl, productId, pageRange, p, midurl, lasturl):
    resultList = random.sample(range(0, pageRange if p>pageRange else p), p if p<pageRange else pageRange);
    for id in resultList:
        print(id)
        url = baseurl + productId + midurl + str(id) + lasturl
        save_current_page_comment(url, file)


def get_SpecificItem_all_page(file, baseurl, productId, scoreurl, score, midurl, lasturl):
    id = 1
    url = baseurl + productId + midurl + str(id)
    #while save_current_page_comment(url, file):
    while save_dianping_review(url, file):
        id = id + 1
        url = baseurl + productId + midurl + str(id)
        # print 'page_num'
        # print id

# the next is about productIds
# 随机获取若干个页面的产品id并返回
def  get_productIdlist_by_type(baseurl, p, lasturl):  # p-skip
    id = 1
    url = baseurl + lasturl + str(id)
    page_code = get_page_code(url)
    if page_code is None:
        return []
    try:
        soup = BeautifulSoup(page_code, 'lxml')  # id="plist"
        res = []
        hidcomment = soup.find('div', attrs={'class': 'content-wrap'}).find('div', attrs={'class': 'shop-wrap'}).find('div', attrs={'class':'content'})
        hidcomment = hidcomment.find('div', attrs={'id': 'shop-all-list'})
        item_list = hidcomment.find('ul').find_all('li', recursive=False)
        for item in item_list:
          content = str(item.find('div', attrs={'class': 'pic'}).find('a').get('href'))
          id = content.split('/')[-1]
          if id not in res:
            res.append(id)
        print('item_num')
        print(len(res))

        resultList = range(2, p)
        for id in resultList:
           #print id
           url = baseurl + lasturl + str(id)
           page_code = get_page_code(url)
           if page_code is None:
               return []
           soup = BeautifulSoup(page_code, 'lxml')
           hidcomment = soup.find('div', attrs={'class': 'content-wrap'}).find('div',attrs={'class': 'shop-wrap'}).find('div',attrs={'class': 'content'})
           hidcomment = hidcomment.find('div', attrs={'id': 'shop-all-list'})
           item_list = hidcomment.find('ul').find_all('li', recursive=False)
           for item in item_list:
               content = str(item.find('div', attrs={'class': 'pic'}).find('a').get('href'))
               id = content.split('/')[-1]
               if id not in res:
                   res.append(id)
        return res
    except ValueError as e:
        print(url)
        print(e)
        return res
    except KeyError as e:
        print(url)
        print(e)
        return res
    except AttributeError as e:
        print(url)
        print(e)
        return res
    except Exception as e:
        print(url)
        print(e)
        return res


def get_SpecificType_RandomItem_all_page(file, baseurl, midurl, lasturl, p, commentbaseurl, commentscoreurl, commentmidurl,
                                         commentlasturl):  # baseurl like this :'https://list.jd.com/list.html?cat=652,829,10971
    shuma_base_url = baseurl + midurl  # lasturl like this '&sort=sort_totalsales15_desc&trans=1&JL=4_2_0#J_main'
    produList_per_type = get_productIdlist_by_type(shuma_base_url, p, lasturl)  # get productIdlist ,return list
    if produList_per_type is None:
        return
    for ele in produList_per_type:
        score = 1
        while score <= 1:
            print("get data from " + baseurl + " for product " + ele + " for score=" + str(score))
            get_SpecificItem_all_page(file, commentbaseurl, ele, commentscoreurl, score, commentmidurl, commentlasturl)
            score += 1


# 从url页面中解析出数码产品下所有的类别号并返回
def get_shuma_link_cat(root, category):  # <div class="category-item m" data-idx="3">
    page_code = get_page_code(root)
    if page_code is None:
        return []
    try:
        soup = BeautifulSoup(page_code, 'lxml')  # id="plist"
        res = []
        hidcomment = soup.find_all('li', attrs={'class': 'nc_li'})
        links = hidcomment[category].find_all('li')
        for link in links:
            dd = link.find('a')
            cat_str = str(dd.get('href')).split('/')[-1]
            if cat_str not in res:
                res.append(cat_str)
        return res
    except Exception as e:
        print(root)
        print(e)
        return res


def save_shuma_all(root, file, pagenum, category):
    commentbaseurl = "http://www.dianping.com/shop/"
    commentscoreurl = ""
    commentpageurl = "/review_more?pageno="
    commentlasturl = ""

    ctg_category_url = 'http://www.dianping.com/search/category/2/35/o10'
    ctg_mid_url = ''
    ctg_page_url = "p"

    ctg_base_url = ctg_category_url
    get_SpecificType_RandomItem_all_page(file, ctg_base_url, ctg_mid_url, ctg_page_url, pagenum,
                                         commentbaseurl, commentscoreurl, commentpageurl,
                                         commentlasturl)
def main():
    #'''
    pagenum = 100  # select pagenum pages for each item_list page
    category = 1
    # file = '/media/data/Project/CrawlData/data/food/travel.txt'  # save Resfile
    file = 'travel_xiaowang.txt'  # save Resfile
    if os.path.exists(file):
        os.remove(file)
    WebDriverWait(driver=driver, timeout=2) #######这里设置超时参数
    root = ''
    save_shuma_all(root, file, pagenum, category)
    driver.close()
    #''''''

main()