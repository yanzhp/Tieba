# -*- coding:utf-8 -*-
#测试用python生成的MySQL数据表的代码，后期已经没有作用。
import pymysql
db = pymysql.connect(host='localhost',user='root',password='yjs43520100',port=3306,db="spiders", charset="utf8mb4")
cursor=db.cursor()
 # sql 语句
cursor.execute("DROP TABLE IF EXISTS TiebaList")
# #创建TiebaList表
# 创建数据表SQL语句
sql = """CREATE TABLE TiebaList (
         title  CHAR(200),
         reply char(10),
         author  CHAR(40),
         url CHAR(200)
          )"""
cursor.execute(sql)
##创建tiebaconlist表,因数据已经存在，故未运行，特别是text字段能否建立成功，是个疑问
sql2="""CREATE TABLE tiebaconlist(
     id int(10) NULLABLE ,
     sex char(2) NULLABLE ,
     authorrank char(6) NULLABLE ,
     opentype char(20) NULLABLE ,
     floor char(10) NULLABLE ,
     author char(40) NULLABLE ,
     context text NULLABLE ,
     title char(40) NULLABLE ,
     url char(20) NULLABLE ,
     """
# 关闭数据库连接
db.close()
