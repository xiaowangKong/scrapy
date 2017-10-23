# -*- coding:utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
request = urllib2.Request("https://item.jd.com/2554856.html")
response = urllib2.urlopen(request)
soup = BeautifulSoup(response)
hidcomment = soup.find('div',attrs={'id':'hidcomment'})
item_list = hidcomment.find_all('div',attrs={'class':'item'})
for item in item_list:
    content = item.find('div',attrs={'class':'comment-content'})
    span_list = item.find_all('span')
    star = ''
    for span in span_list:
        if 'star' in span.get('class'):
            star = span.get('class')[1]
            break
    print star + '---------------------'+ content.string
    print ''
    print ''
# comment = soup. find_all(class_="comment-content")
#
# print comment