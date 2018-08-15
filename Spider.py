#作者yanzhp 2018年7月29日完成
#获取百度贴吧任意指定贴吧和指定页面的主题、作者和链接，并保存到MySQL数据库中
# -*- coding:utf-8 -*-
from urllib import request as urllib2
from urllib import parse
import random
import re
import pymysql
import time
import socket
#from bs4 import BeautifulSoup

#去除表情图标的代码及函数
try:
  # python UCS-4 build的处理方式
  highpoints = re.compile(u'[\U00010000-\U0010ffff]')
except re.error:
  # python UCS-2 build的处理方式
  highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

def remove_emoji(text):
    return highpoints.sub(u'??', text)

def loadPage(url, page):
  '''
  根据url获取服务器响应文件
  url:需要爬取的url
  '''
  print('---------正在下载页面%d-------' % page)
  #print('---------正在下载页面%s-------' %url)
  ua_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
  ]
  header = random.choice(ua_list)
  request = urllib2.Request(url)
  request.add_header('User-Agent', header)
  response = urllib2.urlopen(request)
  html = response.read()
  #每个页面爬取完成之后，有一个5-15秒的随机等待时间
  time.sleep(random.randint(5,15))
  response.close()#要及时关闭
  return html

def writetoMySQL(html):
  '''
  通过正则，从页面获取指定内容，并将获取到的数据保存到MySQL数据库中
  '''
  #打开数据库
  db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders", charset='utf8mb4',)
  cursor = db.cursor()

  #将返回的网页代码转码为utf-8
  html=html.decode('utf-8')
  html=remove_emoji(html)
  #print("沈阳药科大学吧" + "\n" + " 主题              发帖人       回复人数     链接 ")

  #编写正则表达式，直接提取需要的内容成为列表
  tag = re.findall(r'<li class=" j_thread_list clearfix" .*?reply_num.*?(\d).*?is_bakan.*?col2_right j_threadlist_li_right .*?<a.*?href="(.*?)" title="(.*?)".*?<span class="tb_icon_author ".*?:(.*?)".*?</li>', html, re.S)
  #print(tag[0])
  for tag_one in tag:
    #print(tag_one)
    #分别列出正则表达式
    # m_reply = re.findall(r'reply_num.*?(\d).*?is_bakan',tag_one,re.S)[0]
    # m_author = re.findall(r'<span class="tb_icon_author ".*?:(.*?)"',tag_one,re.S)[0]
    # m_link = re.findall(r'<a.*?href="(.*?)" title',tag_one,re.S)[0]
    # m_title =re.findall(r'<a.*?title="(.*?)" target',tag_one,re.S)[0]
    # print(m_title )
    m_reply = tag_one[0]
    m_link = tag_one[1]
    m_title =tag_one[2]
    m_author = tag_one[3]
    #print("主题为" + m_title + "的数据将要保存")
    sql="SELECT * FROM TiebaList WHERE url=%s"
    #try:
    cursor.execute(sql,m_link)
    #print(cursor.rowcount)
    #根据链接地址判断，是否已经存在，存在的话就跳过，不存在的话插入新数据
    if cursor.rowcount>0:
        print("链接为"+m_link+"的数据已经存在")
    else:
        sql2 = "INSERT INTO TiebaList(title, author, url,reply) values(%s,%s,%s,%s)"
        try:
          cursor.execute(sql2,(m_title,m_author,m_link,m_reply))
          db.commit()
          print("主题为"+'"'+ m_title + '"'+"的数据已保存")
        except:
          db.rollback()
          #continue
  db.close()

def tiebaSpider(url, kw, begin, end):
  '''
  爬取贴吧信息
  '''
  words = {
    'kw':kw
  }
  #根据贴吧名称，补全网址
  kw = parse.urlencode(words)
  url = url % (kw)
  #从第一页开始，爬取主题
  for page in range(begin, end + 1):
    #贴吧为每增加一页，pn增加50
    pn = ((page-1)*50)
    ful_url = url + "&pn="+str(pn)
    #爬取页面内容
    html = loadPage(ful_url, page)
    #在页面找到指定内容，保存到数据库
    writetoMySQL(html)
if __name__ == '__main__':
  # kw = input('请输入爬取贴吧名:')#可以变成输入贴吧名称
  kw="沈阳药科大学吧"
  #beginPage = int(input('请输入起始页:'))#输入开始爬取的页面
  #endPage = int(input('请输入结束页:'))#输入结束爬取的页面
  beginPage = 1
  endPage = 4
  url = r'http://tieba.baidu.com/f?%s&ie=utf-8'
  tiebaSpider(url, kw, beginPage, endPage)
  socket.setdefaulttimeout(20)#如果出现socket挂起，20秒之后重新开始
