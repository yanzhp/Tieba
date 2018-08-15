#作者yanzhp，2018年7月30日
#根据已经爬取的贴吧链接，获取所有楼层的内容并保存在mySQL中
# -*- coding:utf-8 -*-
from urllib import request as urllib2
from urllib import error
import random
import re
import pymysql
import time
import socket

#去除掉表情字符，以免出现转码问题
try:
  # python UCS-4 build的处理方式
  highpoints = re.compile(u'[\U00010000-\U0010ffff]')
except re.error:
  # python UCS-2 build的处理方式
  highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

def remove_emoji(text):
    return highpoints.sub(u'', text)

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
        x=re.sub(self.removeImg,"",x)
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
    def __init__(self, baseUrl, seeLZ, floorTag):
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
        # 是否写入楼分隔符的标记
        self.floorTag = floorTag

    #根据传入的页码来获取帖子的内容
    def getPage(self,pageNum):
        url = self.baseURL + self.seeLZ + '&pn=' + str(pageNum)
        ua_list = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
            "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
        ]
        header = random.choice(ua_list)
        try:
            request = urllib2.Request(url)
            request.add_header('User-Agent', header)
            response = urllib2.urlopen(request)
            content=response.read().decode("utf-8","ignore")
            content = remove_emoji(content)
            #print(content)  #测试输出
            response.close()
            return content
        except error.URLError as e:
            print(e.reason)

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
        #pattern = re.compile('<div id="post_content_.*?>(.*?)</div>.*?<ul class="p_tail">.*?<span>(.*?)</span>', re.S)
        items = re.findall(pattern, page)
        # print(items)
        contents = []
        for item in items:
                # 将文本进行去除标签处理，同时在前后加入换行符
            content = self.tool.replace(item)
            contents.append(content)
            # print(content)
        #print(contents)
        return contents

    def setFileTitle(self, title):
            # 如果标题不是为None，即成功获取到标题，将获取的标题保存在self.TieTitle中
        if title is not None:
            # self.file = open(title + ".txt", "w+",encoding="utf-8")
            self.TieTitle=title
        else:
            # self.file = open(self.defaultTitle + ".txt", "w+",encoding="utf-8")
            self.TieTitle=self.defaultTitle

    def writeData(self, contents):
            # 向文件写入每一楼的信息
        # print(contents)
        strsave=''
        for item in contents:
             if self.floorTag == '1':
                   if str(item).strip()=="":
                    #self.file.write("\n" + str(item))
                    # #如果回复没有实质性内容，是图片或者表情，或者其它字符，就不保存了
                    # print("空")
                        strsave = strsave + str(self.floor)+"\n"
                   else:
                    #将有内容的字符串连起来
                        strsave = strsave +str(self.floor) + str(item)+"\n"
                    #print(strsave)
             self.floor += 1
        # self.file.write(strsave1)#写入文件
        return strsave
        # print(strsave)

    #将获取的数据，保存在mySQL数据库中
    def SavetoMySQL(self,mycontent):
        db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders",
                             charset='utf8mb4', )
        cursor = db.cursor()
        shorturl=re.sub('http://tieba.baidu.com','',baseURL)
        # print(shorturl)
        sql = "SELECT * FROM tiebacontents WHERE url=%s"
        cursor.execute(sql, shorturl)
        # print(cursor.rowcount)
        #如果链接已经存在，就更新内容，如果链接没有，就插入内容
        if cursor.rowcount > 0:
            sql2="UPDATE tiebacontents SET contents = %s WHERE url=%s"
            try:
                cursor.execute(sql2, (mycontent, shorturl))
                db.commit()
                print("主题为" + '"' + self.TieTitle + '"' + "的数据已更新")
            except:
                db.rollback()
        else:
            sql2 = "INSERT INTO tiebacontents(title, url,contents) values(%s,%s,%s)"
            try:
                # print(sql2)
                cursor.execute(sql2, (self.TieTitle, shorturl, mycontent))
                db.commit()
                print("主题为" + '"' + self.TieTitle + '"' + "的数据已保存")
            except:
                db.rollback()
                # continue
        db.close()

    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        strsave2=''
        if pageNum == None:
            print("URL已失效，请重试")
            return
        # try:
            # print( "该帖子共有" + str(pageNum) + "页")
        for i in range(1, int(pageNum) + 1):
                # print("正在写入第" + str(i) + "页数据")
            page = self.getPage(i)
            contents = self.getContent(page)
            strsave2=strsave2+self.writeData(contents)
        # print(strsave2)
        self.SavetoMySQL(strsave2)
        # 出现写入异常
        # except IOError as err:
        #     print("写入异常，原因" + err)
        # finally:
        #     print("写入任务完成")

if __name__ == '__main__':
    # 测试代码如下：
    # url=raw_input("raw_input:")
    # url = "http://www.tieba.baidu.com/p/4197307435"
    # seeLZ = input("input see_lz:")
    # pageNum = input("input pageNum:")
    # floorTag = raw_input("input floorTag:")
    Sql_result = openMySQL()
    #为了测试，不挨个爬取帖子
    StarNum=773
    EndNum=780
    for i in range(StarNum,len(Sql_result)):
        theme=Sql_result[i]#为了测试不挨个爬取帖子
        # print(theme)
        baseURL="http://tieba.baidu.com"+theme[3]
        # print(baseURL)
        seeLZ = 0
        floorTag = '1'
        bdtb = BDTB(baseURL, seeLZ, floorTag)
        bdtb.start()
        time.sleep(random.randint(5, 15))
        socket.setdefaulttimeout(20)
        #为了测试，不挨个爬取帖子
        i=i+1
        if i>EndNum:#len(Sql_result):
             break
