# -*- coding:utf-8 -*-
# from urllib import request as urllib2
# from urllib import error
# from bs4 import BeautifulSoup
import random
import requests
import sys

print(sys.getdefaultencoding())
url='http://tieba.baidu.com/p/5815010310'
ua_list = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
            "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
        ]
user_agent = random.choice(ua_list)
headers={
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'BAIDUID=785EFC151CA8D033AAEC481142EF2F7C:FG=1; BIDUPSID=785EFC151CA8D033AAEC481142EF2F7C; PSTM=1532260994; TIEBA_USERTYPE=b285b4ca0051ce75a3f25eea; TIEBAUID=cb23caae14130a0d384a57f1; bdshare_firstime=1532835334394; FP_UID=1def51958e129aeeb78b674067531a32; wise_device=0; Hm_lvt_98b9d8c2fd6608d564bf2ac2ae642948=1532987026,1532991472,1533002175,1533002189; Hm_lpvt_98b9d8c2fd6608d564bf2ac2ae642948=1533003262',
        'User-Agent': user_agent,
        'X-Requested-With': 'XMLHttpRequest'
}
html=requests.get(url,headers=headers)
html_text=html.text.encode('GBK').decode('latin1')
# html=html.encoding('utf-8')
# html=html.decode('utf-8')
print(html_text)




# url='http://tieba.baidu.com/p/5815010310'
# # headers = {"User-Agent": user_agent}
# # print(headers)

# request = urllib2.Request(url,headers=headers)
#             # # request.add_header('User-Agent', header)
# response = urllib2.urlopen(request)
# content=response.read().decode("utf-8",'ignore ')
# response.close()
# print(content)