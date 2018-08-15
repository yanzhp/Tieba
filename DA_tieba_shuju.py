#coding=utf-8
import pymysql#打开数据库
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

def openMySQLtoMatplotPie():
  db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders", charset='utf8',)
  sql = "SELECT sex FROM tiebaconlist"
  df = pd.read_sql(sql,db)
  #贴吧作者性别的饼图
  serr=df['sex']
  # serr.loc[serr== ''] = '0'
  serr=serr[serr!= '']
  desc = serr.value_counts()
  # print(desc)
  plt.pie(x=desc, explode=None, labels=('男', '女', '空值'),
          colors=('b', 'g', 'r'),
          autopct='%3.1f %%', pctdistance=0.6, shadow=True,
          labeldistance=1.1, startangle=90,radius=None,
          counterclock=True, wedgeprops=None, textprops=None,
    center = (0, 0), frame = False)
  plt.rcParams['font.sans-serif'] = ['SimHei']
  plt.rcParams['axes.unicode_minus'] = False
  plt.title('沈阳药科大学贴吧性别比例图', bbox={'facecolor': '0.8', 'pad': 5})
  plt.savefig("savegif/沈阳药科大学贴吧性别比例图.png")
  plt.show()
  plt.close()
  db.close()

def openMySQLtoMatplotBar():
  db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders", charset='utf8',)
  sql = "SELECT sex,authorrank FROM tiebaconlist"
  df = pd.read_sql(sql,db)

 #贴吧作者等级柱状图
  serr2=df['authorrank']
  # serr2.loc[serr2 == ''] = '0'
  serr2=serr2[serr2!='']
  desc2 = serr2.value_counts()
  name_list=[]
  for i in range(1,16):
      name_list.append(str(i))
  desc22=desc2.reindex(name_list)
  # print(desc22)
  name_list2=[]
  for level in name_list:
      name_list2.append('Level'+level)
  plt.rcParams['font.sans-serif'] = ['SimHei']
  plt.rcParams['axes.unicode_minus'] = False
  plt.title('沈阳药科大学贴吧作者等级柱状图', bbox={'facecolor': '0.8', 'pad': 5})
  plt.barh(range(len(desc22)), desc22, color='b', tick_label=name_list2)
  # plt.legend()
  plt.savefig("savegif/贴吧作者等级图.png")
  plt.show()
  plt.close()
  db.close()

def openMySQLtoMatplotMutiBar():
  db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders", charset='utf8',)
  sql1 = "SELECT sex,authorrank,author FROM tiebaconlist  WHERE sex='1' GROUP BY author"
  df1 = pd.read_sql(sql1,db)
  serr1=df1['authorrank']
  sql2="SELECT sex,authorrank,author FROM tiebaconlist  WHERE sex='2' GROUP BY author"
  df2 = pd.read_sql(sql2, db)
  serr2 = df2['authorrank']
  sql3 = "SELECT sex,authorrank,author FROM tiebaconlist  WHERE sex='0' GROUP BY author"
  df3 = pd.read_sql(sql3, db)
  serr3 = df3['authorrank']
  # print(serr3.value_counts())
 #贴吧作者等级柱状图
  desc1 = serr1.value_counts()
  desc2 = serr2.value_counts()
  desc3 = serr3.value_counts()
  # print(desc3)
  name_list=[]
  for i in range(1,16):
      name_list.append(str(i))
  desc12=desc1.reindex(name_list)
  desc22=desc2.reindex(name_list)
  desc32=desc3.reindex(name_list)
  # print(desc12,desc22,desc32)
  name_list2=[]
  for level in name_list:
      name_list2.append('Lev'+level)
  x = list(range(len(desc12)))
  total_width, n = 0.8, 3
  width = total_width / n
  plt.rcParams['font.sans-serif'] = ['SimHei']
  plt.rcParams['axes.unicode_minus'] = False
  plt.xlabel(u"贴吧作者级别")  # 指定x轴描述信息
  plt.ylabel(u"数量")  # 指定y轴描述信息
  plt.title("贴吧级别\性别统计图")  # 指定图表描述信息
  # plt.bar(x, desc12, width=width, label='男',tick_label=name_list2, fc='y')
  # for i in range(len(x)):
  #   x[i] = x[i] + width
  # plt.bar(x, desc22, width=width, label='女', tick_label=name_list2, fc='r')
  # for i in range(len(x)):
  #   x[i] = x[i] + width
  # plt.bar(x, desc32, width=width, label='不清楚', tick_label=name_list2, fc='b')
  # plt.legend()
  plt.grid()
  plt.plot(name_list2,desc12, '*-')
  plt.plot(name_list2,desc22, 'o--')
  plt.plot(name_list2,desc32,'v:')
  plt.legend(['男','女','不清楚'],loc=1)
  plt.savefig("savegif/贴吧作者性别等级图.png")
  plt.show()
  plt.close()
  db.close()

def openMySQLtoMatplotAuthorBar():
    db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders",
                         charset='utf8', )
    sql = "SELECT author FROM tiebaconlist"
    df = pd.read_sql(sql, db)

    # 贴吧作者发帖量柱状图
    serr2 = df['author']
    # desc2 = serr2.value_counts()
    # print(desc2)
    count = Counter(serr2).most_common(10)
    count_dict = dict(count)
    # print(sorted(count_dict.items(),key = operator.itemgetter(1)))
    desc=list(count_dict.values())
    desc2=desc[::-1]#列表进行反序操作
    name_list=list(count_dict.keys())
    name_list2=name_list[::-1]#列表进行反序操作
    # print(desc2,name_list)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.xlabel(u"发帖量")  # 指定x轴描述信息
    plt.ylabel(u"作者昵称")  # 指定y轴描述信息
    plt.title("贴吧发帖量前十的作者及发帖量")  # 指定图表描述信息
    plt.barh(range(len(desc2)), desc2, color='g', tick_label=name_list2)
    # plt.grid()#添加网格
    plt.savefig("savegif/贴吧发帖量前十作者及发帖数量.png")
    plt.show()
    plt.close()
    db.close()

def openMySQLtoMatplotDatatime():
    db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders",
                         charset='utf8', )
    sql = "SELECT author,datatime FROM tiebaconlist"
    df = pd.read_sql(sql, db)
    # serr1=df['author']
    serr=df['datatime']
    serr = serr[serr != '']
    dtym=[]
    dth=[]
    for dt_str in serr:
        dtym.append(dt_str[0:7])
        dth.append(dt_str[-5:-3])
    # print(dth)
    countym = Counter(dtym).most_common(12)#按照值统计频率
    counth=Counter(dth)
    # print(counth,countym)
    countym_dict=dict(countym)#count转化为字典
    counth_dict=dict(counth)
    # print(counth_dict,countym_dict)
    counth_dict_sorted=sorted(counth_dict.items())#对字典按照key进行排序，排序后为元组
    sorted_counth_dict=dict(counth_dict_sorted)#把元组转化为字典
    # print(sorted_counth_dict)
    #根据时间对发帖回帖量进行绘制曲线
    name_list=list(sorted_counth_dict.keys())
    num_list=list(sorted_counth_dict.values())
    # print(name_list,num_list)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(1)
    plt.xlabel(u"发帖时间")  # 指定x轴描述信息
    plt.ylabel(u"发帖数量")  # 指定y轴描述信息
    plt.title("贴吧分时段发帖量统计图")  # 指定图表描述信息
    plt.plot(name_list,num_list,'*-')
    plt.grid(linewidth="0.5")
    for a, b in zip(name_list, num_list):
        plt.text(a, b+10, b, ha='center', va='bottom', fontsize=10)
    # 历史发帖量前十的月份
    # print(countym_dict)
    name_list1 = list(countym_dict.keys())
    num_list1 = list(countym_dict.values())
    name_list2 = name_list1[::-1]  # 列表进行反序操作
    num_list2=num_list1[::-1]
    plt.savefig("savegif/贴吧作者分时段发帖量统计图.png")
    plt.figure(2)
    plt.xlabel(u"发帖数量")  # 指定x轴描述信息
    plt.ylabel(u"发帖月份")  # 指定y轴描述信息
    plt.title("历史发帖量前十月份统计图")  # 指定图表描述信息
    plt.barh(name_list2,num_list2)
    plt.grid(linewidth="0.5")
    plt.savefig("savegif/贴吧作者发帖量前十月份统计图.png")
    plt.show()
    plt.close()
    db.close()

def openMySQLtoMatplotTypePie():
        db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders",
                             charset='utf8', )
        sql = "SELECT opentype FROM tiebaconlist"
        df = pd.read_sql(sql, db)
        # 贴吧作者性别的饼图
        serr = df['opentype']
        serr.loc[serr== ''] = 'computer and other'
        serr.loc[serr=='ipad']='apple'
        serr.loc[serr=='webipad']='apple'
        serr.loc[serr == 'mi_2'] = 'android'
        serr.loc[serr == 'mi_2s'] = 'android'
        serr.loc[serr == 'mi_3'] = 'android'
        serr.loc[serr == 'android_bz'] = 'android'
        serr.loc[serr == 'phone'] = 'other phone'
        serr.loc[serr == '1'] = 'computer and other'
        serr.loc[serr == 'wphone'] = 'other phone'
        serr.loc[serr == '4'] = 'computer and other'
        serr.loc[serr == 'version_campus'] = 'computer and other'
        serr.loc[serr == 'xiangce'] = 'computer and other'
        serr.loc[serr == 'win8'] = 'computer and other'
        # serr = serr[serr != '']
        desc = serr.value_counts()
        # print(desc)
        plt.pie(x=desc, explode=None, labels=('安卓设备', '苹果设备', '电脑及其他','其它手机'),
                colors=('b', 'g', 'r','y'),
                autopct='%3.1f %%', pctdistance=0.6, shadow=True,
                labeldistance=1.1, startangle=90, radius=None,
                counterclock=True, wedgeprops=None, textprops=None,
                center=(0, 0), frame=False)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.title('沈阳药科大学贴吧访问设备类型比例图', bbox={'facecolor': '0.8', 'pad': 5})
        plt.savefig("savegif/沈阳药科大学贴吧访问设备类型比例图.png")
        plt.show()
        plt.close()
        db.close()

if __name__ == '__main__':
    #性别比例饼图
    openMySQLtoMatplotPie()
    # #作者等级柱状图
    openMySQLtoMatplotBar()
    # #作者等级、性别分布柱状图或者线图
    openMySQLtoMatplotMutiBar()
    # #发帖量前十的作者发帖量柱状图
    openMySQLtoMatplotAuthorBar()
    ##贴吧作者发帖时间和发帖量前十的月份分析图
    openMySQLtoMatplotDatatime()
    #贴吧作者使用设备饼图
    openMySQLtoMatplotTypePie()