#作者yanzhp，2018年7月30日
#根据已经爬取的贴吧链接，挨个楼层获取内容、回帖作者名称、等级、发帖时间、使用设备等信息并逐条保存在mySQL中
# -*- coding:utf-8 -*-
from urllib import request as urllib2
from urllib import error
import random
import re
import pymysql
import time
import socket

proxy_list =[]
#去除掉表情字符，以免出现转码问题
try:
  # python UCS-4 build的处理方式
  highpoints = re.compile(u'[\U00010000-\U0010ffff]')
except re.error:
  # python UCS-2 build的处理方式
  highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

def remove_emoji(text):
    return highpoints.sub(u'表情', text)
def remove_quot(text):
    replacequot = re.compile('&quot;|&amp;')
    return re.sub(replacequot,'"',text)

#定义一个工具类来处理内容中的标签
class Tool:
    #去除img标签，7位长空格
    removeImg=re.compile('<img.*?>')
    #去除超链接标签
    removeAddr=re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine=re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD=re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara=re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR=re.compile('<br><br>|<br>')
    #将其余标签删除
    removeExtraTag=re.compile('<.*?>')
    def replace(self,x):
        x=re.sub(self.removeImg,"图片",x)
        x=re.sub(self.removeAddr,"",x)
        x=re.sub(self.replaceLine,"\n",x)
        x=re.sub(self.replaceTD,"\t",x)
        x=re.sub(self.replacePara,"\n  ",x)
        x=re.sub(self.replaceBR,"\n",x)
        x=re.sub(self.removeExtraTag,"",x)
        return x.strip()

#从现有的数据库TiebaList中，将需要处理的链接取出来
def openMySQL():
  #连接字符串
  db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders", charset='utf8mb4',)
  cursor = db.cursor()
  #查询所有存在的链接
  sql = "SELECT * FROM TiebaList"
  cursor.execute(sql)
  result = cursor.fetchall()
  return result
  cursor.close()
  db.close()

#百度贴吧爬虫类
class BDTB:
    # 初始化，传入基地址，是否只看楼主的参数
    # def __init__(self, baseUrl, seeLZ, floorTag):
    def __init__(self, baseUrl, seeLZ):
        # base链接地址
        self.baseURL = baseUrl
        # 是否只看楼主
        self.seeLZ = '?see_lz=' + str(seeLZ)
        # HTML标签剔除工具类对象
        self.tool = Tool()
        # 全局file变量，文件写入操作对象
        self.file = None
        # 全局title变量，帖子标题操作对象
        self.TieTitle = ""
        # 楼层标号，初始为1
        self.floor = 1
        # 默认的标题，如果没有成功获取到标题的话则会用这个标题
        self.defaultTitle = u"百度贴吧"
        # 是否写入楼分隔符的标记;用来判断是否是楼主的帖子
        # self.floorTag = floorTag

    #根据传入的页码来获取帖子的内容
    def getPage(self,pageNum,httpproxy,num_retries=5):
        url = self.baseURL + self.seeLZ + '&pn=' + str(pageNum)
        ua_list = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
            "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
        ]
        header = random.choice(ua_list)
        content=None
        # header = {
        #     # 'Accept': 'application/json, text/javascript, */*; q=0.01',
        #     # 'Accept-Encoding': 'gzip, deflate',
        #     # 'Accept-Language': 'zh-CN,zh;q=0.9',
        #     # 'Connection': 'keep-alive',
        #     # 'Cookie': 'BAIDUID=785EFC151CA8D033AAEC481142EF2F7C:FG=1; BIDUPSID=785EFC151CA8D033AAEC481142EF2F7C; PSTM=1532260994; TIEBA_USERTYPE=b285b4ca0051ce75a3f25eea; TIEBAUID=cb23caae14130a0d384a57f1; bdshare_firstime=1532835334394; FP_UID=1def51958e129aeeb78b674067531a32; Hm_lvt_98b9d8c2fd6608d564bf2ac2ae642948=1533002189,1533012581,1533088436,1533170516; wise_device=0; Hm_lpvt_98b9d8c2fd6608d564bf2ac2ae642948=1533170536',
        #     # 'Host': ' tieba.baidu.com',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        #     # 'X-Requested-With': 'XMLHttpRequest'
        # }
        # header ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        try:
            timeout = 5
            socket.setdefaulttimeout(timeout)  # 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
            sleep_download_time = random.randint(5,15)
            time.sleep(sleep_download_time)  # 这里时间自己设定
            httpproxy_handler = urllib2.ProxyHandler(httpproxy)
            opener = urllib2.build_opener(httpproxy_handler)
            request = urllib2.Request(url)
            request.add_header('User-Agent', header)
            response = opener.open(request)
            # request = urllib2.Request(url)
            # response = urllib2.urlopen(request)
            content = response.read().decode("utf-8", "ignore")
            content = remove_emoji(content)
            content=remove_quot(content)
            # print(content)  #测试输出
            response.close()
            return content
        except error.URLError as e:
            print("-----urlErrorurl:", url)
            if num_retries > 0:
               # 如果不是200就重试，每次递减重试次数
                proxy = random.choice(proxy_list)
                return self.getPage(pageNum,proxy, num_retries - 1)
            else:
                return content
        except socket.error as e:
            print("-----socket timout:", url)
            if num_retries > 0:
                # 如果不是200就重试，每次递减重试次数
                proxy = random.choice(proxy_list)
                return self.getPage(pageNum,proxy, num_retries - 1)
            else:
                return content

    # 获取帖子标题
    def getTitle(self, page):
      # 得到标题的正则表达式
        pattern = re.compile('<h1 class="core_title_txt.*?>(.*?)</h1>', re.S)
        result = re.search(pattern, page)
        if result:
            # 如果存在，则返回标题
            return result.group(1).strip()
        else:
            return None

        # 获取帖子一共有多少页
    def getPageNum(self, page):
        # 获取帖子页数的正则表达式
        pattern = re.compile('<li class="l_reply_num".*?</span>.*?<span class="red".*?>(\d+)</span>', re.S)
        result = re.findall(pattern, page)
        # print(result)
        if result:
            return result[0]
        else:
            return None

        # 获取每一层楼的内容,传入页面内容
    def getContent(self, page):
            # 匹配所有楼层的内容
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        items = re.findall(pattern,page)
        pattern2=re.compile('<div class="l_post j_l_post l_post_bright.*?pb_tpoint.*?> ',re.S)
        items2 = re.findall(pattern2, page)
        for i in range(0,len(items)):
            contents={}
            keys=['sex','authorrank','opentype','datatime','floor']
            pattern3=re.compile('data-field=\'({.*?}})',re.S)
            items3 = re.findall(pattern3, items2[i])
            pattern4=re.compile('sex":(\d).*?level_id":(\d+),"level_n.*?open_type":"(.*?)","d.*?(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}).*?post_no":(\d+)',re.S)
            userInfo=re.findall(pattern4,items3[0])
            if userInfo:
                items4=userInfo[0]
            else:
                items4=['','','','','']
            j=0
            for j in range(len(items4)):
                contents[keys[j]] = items4[j]
                j=j+1
            # print(contents)
            pattern5=re.compile('r_name":"(.*?)","n',re.S)
            username = re.search(pattern5, items3[0])
            if username:
                username = username[1].encode('utf-8').decode('unicode_escape')
            else:
                username = ""
            # print(username.encode('utf-8').decode('unicode_escape'))
            content = self.tool.replace(items[i])
            shorturl = re.sub('http://tieba.baidu.com', '', baseURL)
            # contents.append(username)
            # contents.append(content)
            contents['author']=username
            contents['context']=content
            contents['title']=self.TieTitle
            contents['url']=shorturl
            # contents.append(self.TieTitle)
            # contents.append(shorturl)
            self.SavetoMySQL(contents)
            # print(contents)

            i=i+1

    def setFileTitle(self, title):
            # 如果标题不是为None，即成功获取到标题，将获取的标题保存在self.TieTitle中
        if title is not None:
            # self.file = open(title + ".txt", "w+",encoding="utf-8")
            self.TieTitle=title
        else:
            # self.file = open(self.defaultTitle + ".txt", "w+",encoding="utf-8")
            self.TieTitle=self.defaultTitle

    #将获取的数据，保存在mySQL数据库中
    def SavetoMySQL(self,mycontent):
        db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders",
                             charset='utf8mb4', )
        cursor = db.cursor()
        # print(mycontent)
        sql = "SELECT * FROM tiebaconlist WHERE url='%s' and floor='%s'"%(mycontent['url'],mycontent['floor'])
        # print(sql)
        cursor.execute(sql)
        # print(cursor.rowcount)
        #如果链接已经存在，就更新内容，如果链接没有，就插入内容
        if cursor.rowcount >0:
            sql2 = "UPDATE tiebaconlist SET context ='%s',datatime='%s' WHERE url='%s' and floor='%s'"%(mycontent['context'],mycontent['datatime'],mycontent['url'],mycontent['floor'])
            # cursor.execute(sql2)
            # db.commit()
            # print('更新2成功')
            try:
                cursor.execute(sql2)
                db.commit()
                print("主题为" + '"' + mycontent['title'] + '"' + "的数据已更新")
            except:
                db.rollback()
                print("主题为" + '"' + mycontent['title'] + '"' + "     更新失败")
        else:
             table='tiebaconlist'
             keys=','.join(mycontent.keys())
             values=','.join(['%s']*len(mycontent))
             sql2="""INSERT INTO {table} ({keys}) VALUES ({values})""".format(table=table,keys=keys,values=values)
             # sql2='INSERT INTO tiebaconlist (sex,authorrank) values (%s,%s) '
             # print(sql2,tuple(mycontent.values()))
             # val=tuple(mycontent.values())
             # cursor.execute(sql2,(val[0],str(val[1])))
             # print(sql2,val[0],str(val[1]))
             try:
                 if cursor.execute(sql2,tuple(mycontent.values())):
                     print("主题为" + '"' + mycontent['title'] + '"' + "     保存成功")
                     db.commit()
             except:
                 print("主题为" + '"' + mycontent['title'] + '"' + "     保存失败")
                 db.rollback()
        db.close()

    def start(self,httpproxy):
        indexPage = self.getPage(1,httpproxy)
        if indexPage!=None:
            pageNum = self.getPageNum(indexPage)
        # floorNum=self.getPageNum(indexPage)[1]
        # print(pageNum)
            title = self.getTitle(indexPage)
            self.setFileTitle(title)
        # strsave2=''
            if pageNum == None:
                print("URL已失效，请重试")
                return
        # try:
            # print( "该帖子共有" + str(pageNum) + "页")
            for i in range(1, int(pageNum) + 1):
                # print("正在写入第" + str(i) + "页数据")
                page = self.getPage(i,httpproxy)
                self.getContent(page)
            # strsave2=strsave2+self.writeData(contents)
        # print(strsave2)
        #self.SavetoMySQL(strsave2)
        # 出现写入异常
        # except IOError as err:
        #     print("写入异常，原因" + err)
        # finally:
        #     print("写入任务完成")
        else:
            print('URL失效或多次尝试仍未成功访问帖子，切换到下一个帖子')

if __name__ == '__main__':
    # 测试代码如下：
    # url=raw_input("raw_input:")
    # url = "http://www.tieba.baidu.com/p/4197307435"
    # seeLZ = input("input see_lz:")
    # pageNum = input("input pageNum:")
    # floorTag = raw_input("input floorTag:")
    Sql_result = openMySQL()
    #为了测试，不挨个爬取帖子
    f = open("ip.txt")  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    while line:
        # print line,                 # 在 Python 2中，后面跟 ',' 将忽略换行符
        ip = line.split()
        proxy_list.append({"http": "http://"+ip[0], "https": "https://"+ip[0]})  # 代理ip
        # print(line, end='')  # 在 Python 3中使用
        line = f.readline()
    f.close()
    proxy = random.choice(proxy_list)
    # StarNum=int(input('请输入开始帖子数：'))
    # EndNum=int(input('请输入结束帖子数：'))
    StarNum=5259
    EndNum=5500
    time_start = time.time()
    for i in range(StarNum,len(Sql_result)):
        theme=Sql_result[i]#为了测试不挨个爬取帖子
        # print(theme)
        baseURL="http://tieba.baidu.com"+theme[3]
        print(baseURL,i)
        seeLZ = 0
        # floorTag = '2'
        # bdtb = BDTB(baseURL, seeLZ, floorTag)
        bdtb = BDTB(baseURL, seeLZ)
        bdtb.start(proxy)
        #为了测试，不挨个爬取帖子
        i=i+1
        if i>EndNum:#len(Sql_result):
             break
    time_end = time.time()
    print('totally cost', time_end - time_start)
