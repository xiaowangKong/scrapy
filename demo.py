#!/usr/bin/env Python
# coding=utf-8
import urllib2
import urllib
import requests
from bs4 import BeautifulSoup
import socket
import random
import json
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
threshold = 95  # favorable rate

retry = 0
# read a url and save the comments on the page to file
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


# call the func save_current_page_comment to save one page
def save_current_page_comment(url, file):
    page_code = get_page_code(url)
    if page_code is None:
        return False
    html = page_code
    print html
    try:
        dic = json.loads(html)
        print dic
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
    except ValueError as e:
        print url
        print e
        return False
    except KeyError as e:
        print url
        print e
        return False
    except AttributeError as e:
        print url
        print e
        return False
    except Exception as e:
        print url
        print e
        return False
    return True


# random p pages
def get_SpecificItem_random_page(file, baseurl, productId, pageRange, p, midurl, lasturl):
    resultList = random.sample(range(0, pageRange if p>pageRange else p), p if p<pageRange else pageRange);
    for id in resultList:
        print id
        url = baseurl + productId + midurl + str(id) + lasturl
        save_current_page_comment(url, file)


def get_SpecificItem_all_page(file, baseurl, productId, midurl, lasturl):
    id = 0
    url = baseurl + productId + midurl + str(id) + lasturl
    while save_current_page_comment(url, file):
        id = id + 1
        url = baseurl + productId + midurl + str(id) + lasturl
        # print 'page_num'
        # print id

# the next is about productIds
def  get_productIdlist_by_type(baseurl, p, lasturl):  # p-skip
    id = 1
    url = baseurl + str(id) + lasturl
    page_code = get_page_code(url)
    if page_code is None:
        return []
    try:
        soup = BeautifulSoup(page_code, 'html.parser')  # id="plist"
        res = []
        hidcomment = soup.find('div', attrs={'id': 'plist'})
        item_list = hidcomment.find_all('div', attrs={'class': 'p-name'})
    # print item_list
        for item in item_list:  # href="//item.jd.com/10002531129.html"
        #  print item
          content = str(item.find('a').get('href'))
        # print  content
          id = content.split('/')[-1].split('.')[0]
          res.append(id)
        print 'item_num：'
        print len(res)
    # <span class="p-skip">
    # <em>共<b>202</b>页&nbsp;&nbsp;到第</em>
        page_num = int(soup.find('span', attrs={'class': 'p-skip'}).find('em').find('b').text)
        if page_num >= p:
           resultList = random.sample(range(2, page_num), p)
        else:
           resultList = random.sample(range(2, page_num), page_num)
        for id in resultList:
           print id
           url = baseurl + str(id) + lasturl
           page_code = get_page_code(url)
           if page_code is None:
               return []
           soup = BeautifulSoup(page_code, 'html.parser')  # id="plist"
           hidcomment = soup.find('div', attrs={'id': 'plist'})
           item_list = hidcomment.find_all('div', attrs={'class': 'p-name'})
           for item in item_list:  # href="//item.jd.com/10002531129.html"
            #  print item
              content = str(item.find('a').get('href'))
            # print  content
              id1 = content.split('/')[-1].split('.')[0]
              res.append(id1)
        return res
    except ValueError as e:
      print url
      print e
      return res
    except KeyError as e:
      print url
      print e
      return res
    except AttributeError as e:
      print url
      print e
      return res
    except Exception as e:
      print url
      print e
      return res


def get_SpecificType_RandomItem_all_page(file, baseurl, midurl, lasturl, p, commentbaseurl, commentmidurl,
                                         commentlasturl):  # baseurl like this :'https://list.jd.com/list.html?cat=652,829,10971
    shuma_base_url = baseurl + midurl  # lasturl like this '&sort=sort_totalsales15_desc&trans=1&JL=4_2_0#J_main'
    produList_per_type = get_productIdlist_by_type(shuma_base_url, p, lasturl)  # get productIdlist ,return list
    if produList_per_type is None:
        return
    for ele in produList_per_type:
        get_SpecificItem_all_page(file, commentbaseurl, ele, commentmidurl, commentlasturl)


def get_shuma_link_cat(root):  # <div class="category-item m" data-idx="3">
    page_code = get_page_code(root)
    if page_code is None:
        return []
    try:
        soup = BeautifulSoup(page_code, 'html.parser')  # id="plist"
        res = []
        hidcomment = soup.find_all('div', attrs={'class': 'category-item m'})
        # <dl class="clearfix">
        #links = hidcomment[8].find_all('dl', attrs={'class': 'clearfix'}) #  if grab clothes data
        links = hidcomment[3].find_all('dl', attrs={'class': 'clearfix'}) #  if grab shuma data
        for link in links:
            dd = link.find('dd').find_all('a')
            for d in dd:
                cur = str(d.get('href')).split('&')[0]
                if ('cat=' in cur):
                    res.append(cur.split('=')[1])
        return res
    except Exception as e:
        print root
        print e
        return res


def save_shuma_all(root, file, pagenum):
    commentbaseurl = "https://club.jd.com/comment/productPageComments.action?productId="
    commentmidurl = "&score=0&sortType=5&page="
    commentlasturl = "&pageSize=10&isShadowSku=0&fold=1"
    shuma_last_url = '&sort=sort_totalsales15_desc&trans=1&JL=4_2_0#J_main'
    shuma_mid_url = '&page='
    cats = get_shuma_link_cat(root)  # get shuma cat=? ？构成的list
    for cat in cats:
        shuma_base_url = 'https://list.jd.com/list.html?cat=' + cat
        get_SpecificType_RandomItem_all_page(file, shuma_base_url, shuma_mid_url, shuma_last_url, pagenum,
                                             commentbaseurl, commentmidurl,
                                             commentlasturl)


# the next is main function
pagenum = 5  # select pagenum pages for each item_list page
file = 'shuma.txt'  # save Resfile
if os.path.exists(file):
    os.remove(file)
root = 'https://www.jd.com/allSort.aspx'
save_shuma_all(root, file, pagenum)
# call the func save_current_page_comment to save one page
# rtn = get_SpecificItem_random_page(file,baseurl,productId,pageRange,pagenum,midurl,lasturl)
url = 'https://club.jd.com/comment/productPageComments.action?productId=3681493&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
#save_current_page_comment(url,file)
# get_SpecificItem_all_page(file,baseurl,productId,midurl,lasturl)
# the next is about productIds
# produList_per_type = get_productIdlist_by_type(shuma_base_url,10,lasturl)# get productIdlist ,return list
# get_SpecificType_RandomItem_all_page(file,shuma_base_url,shuma_last_url,pagenum,commentbaseurl,commentmidurl,commentlasturl)


