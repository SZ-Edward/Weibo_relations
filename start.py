#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Aurora Wu
# Author: Aurora Wu
# Contact: wuxy91@gmail.com

import urllib2
import config
import weibo_login as login
from BeautifulSoup import BeautifulSoup
from datetime import datetime

def get_followers_list(url, fans, page):
    response = urllib2.urlopen(url)
    soup = BeautifulSoup(response.read())
    #解析HTML中的粉丝列表
    fans_list = str(soup.findAll('script')[6])
    index = '<script>STK &amp;&amp; STK.pageletM &amp;&amp; STK.pageletM.view('
    data = parse_script_data(fans_list, index)
    soup = BeautifulSoup(data)
    soup = soup.findAll('li', attrs={'class': 'clearfix S_line5', 'action-type': 'itmeClick'})
    #将粉丝的uid和昵称写入Followers.txt
    following_list = file('Followers.txt', 'a')
    sentence = str(datetime.now())[:19] + "的粉丝列表，总数：【%s】，第【%s】页\n" % (fans, page)
    following_list.write(sentence)
    for li in soup:
        strong = li.find('strong')
        a = str(strong.find('a', attrs={'target': '_blank', 'class': 'W_f14 S_func1'})).split(' ')
        uid = a[2][(a[2].index('id=')+3): (len(a[2])-1)]
        nickname = a[3][(a[3].index('=')+2): (len(a[3])-1)]
        sentence = "uid=【%s】, nickname=【%s】 \n" % (uid, nickname)
        following_list.write(sentence)
    following_list.write("==========================================================\n")
    following_list.close()

def get_following_list(url, following, page):
    response = urllib2.urlopen(url)
    soup = BeautifulSoup(response.read())
    #解析HTML中的关注者列表
    follow_list = str(soup.findAll('script')[6])
    index = '<script>STK &amp;&amp; STK.pageletM &amp;&amp; STK.pageletM.view('
    data = parse_script_data(follow_list, index)
    soup = BeautifulSoup(data)
    #将关注者的uid和昵称写入Following.txt
    following_list = file('Following.txt', 'a')
    sentence = str(datetime.now())[:19] + "的关注者列表，总数：【%s】，第【%s】页\n" % (following, page)
    following_list.write(sentence)
    soup = soup.findAll('div', attrs={'action-type': 'user_item', 'class': 'myfollow_list S_line2 SW_fun'})
    for div in soup:
        a = div.find('ul', attrs={'class': 'info'}).find('a', attrs={'target': '_blank', 'class': 'S_func1', 'node-type': 'screen_name'})
        nickname = a.string
        uid = str(a['usercard']).split('=')[1]
        sentence = "uid=【%s】, nickname=【%s】 \n" % (str(uid), str(nickname))
        following_list.write(sentence)
    following_list.write("==========================================================\n")
    following_list.close()

def get_user_info(url):
    response = urllib2.urlopen(url)
    soup = BeautifulSoup(response.read())
    scripts = soup.findAll('script')
    CONFIG = str(scripts[2])
    CONFIG = CONFIG[CONFIG.index('$CONFIG[\'islogin\'] = \'1\';'): CONFIG.index('</script>')]
    CONFIG = CONFIG[CONFIG.index('$CONFIG[\'uid\']'): CONFIG.index('$CONFIG[\'location\'] = \'home\';')]
    CONFIG = CONFIG.split(';')
    uid = CONFIG[0].split(' = ')[1]       #当前用户uid
    nickname = CONFIG[1].split(' = ')[1]  #当前用户昵称
    numbers = str(scripts[14])
    index = '<script>FM.view('
    data = parse_script_data(numbers, index)
    soup = BeautifulSoup(data)
    follow = soup.find('strong', attrs={'node-type': 'follow'})  #关注者数目
    fans = soup.find('strong', attrs={'node-type': 'fans'})      #粉丝数目
    return uid, nickname, int(follow.string), int(fans.string)

def parse_script_data(script, index):
    offset = ')</script>'
    index = script.index(index) + len(index)
    offset = script.index(offset)
    data = script[index: offset]
    index = data.index('html') + 7
    data = data[index: (len(data) - 2)]
    data = data.replace("&gt;", ">")
    data = data.replace("&lt;", "<")
    data = data.replace("\\n", "")
    data = data.replace("\\r", "")
    data = data.replace("\\", "")
    return data

def main():
    rs = login.main()
    if rs == 0:
        uid, nickname, following, fans = get_user_info(config.weibo_url)
        follow_page = following/20 + 1
        fans_page = fans/20 + 1
        #获取关注者列表
        for i in range(1, follow_page):
            get_following_list((config.following_url % (uid, i)).replace('\'', ''), following, i)
        #获取粉丝列表
        for i in range(1, fans_page):
            get_followers_list((config.followers_url % (uid, i)).replace('\'', ''), fans, i)
    else:
        return u"登录微博失败！"

if __name__ == "__main__":
    main()
