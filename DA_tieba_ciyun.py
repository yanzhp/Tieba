#coding=utf-8
import pymysql#打开数据库
import re
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
import jieba
import numpy as np
import pandas as pd
def remove(text):
  # text=text.decode("utf8")
  removeAddr = re.compile(u'表情|图片|科大|长学|顶')
  return  re.sub(removeAddr, "", text)

# 添加自己的词库分词
def add_word(list):
    for items in list:
        jieba.add_word(items)

def openMySQLtoWordCloud():
  db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders", charset='utf8',)
  cursor = db.cursor()
  sql = "SELECT context,title FROM tiebaconlist"
  cursor.execute(sql)
  results = cursor.fetchall()
  # path ="content.txt"
  # f = codecs.open(path, 'w', 'utf-8')
  # for result in results:
  #     a=result[0]
  #     a=remove(a)   # print(a)
  #     f.write(a)
  my_words_list = ['药科大学','药大']  # 在结巴的词库中添加新词
  add_word(my_words_list)
  mytext=""
  mytext2=""
  for result in results:
      mytext=mytext+remove(result[0])
      mytext2=mytext2+remove(result[1])
      # print(mytext)

  cut_text = jieba.cut(mytext, cut_all='False')
  result = " / ".join(cut_text)
  image = Image.open(r'123.png')
  graph = np.array(image)
  wc = WordCloud(font_path=r'chGBK.ttf',  # 设置字体
                 background_color="black",  # 背景颜色
                 max_words=200,  # 词云显示的最大词数
                 mask=graph,  # 设置背景图片
                 max_font_size=100,  # 字体最大值
                 random_state=42,
                 width=1000, height=860, margin=2,  # 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
                 )

  wc.generate(result)
  image_color = ImageColorGenerator(graph)
  wc.recolor(color_func=image_color)
  wc.to_file(r'savegif/内容词云图.png')
  plt.figure("词云图")
  plt.imshow(wc)
  plt.axis('off')
  plt.show()
  print("生成内容词云图完成！！")

  cut_text = jieba.cut(mytext2, cut_all='False')
  result = " / ".join(cut_text)
  image = Image.open(r'123.png')
  graph = np.array(image)
  wc = WordCloud(font_path=r'chGBK.ttf',  # 设置字体
                 background_color="black",  # 背景颜色
                 max_words=200,  # 词云显示的最大词数
                 mask=graph,  # 设置背景图片
                 max_font_size=100,  # 字体最大值
                 random_state=42,
                 width=1000, height=860, margin=2,  # 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
                 )

  wc.generate(result)
  image_color = ImageColorGenerator(graph)
  wc.recolor(color_func=image_color)
  wc.to_file(r'savegif/标题词云图.png')
  plt.figure("词云图")
  plt.imshow(wc)
  plt.axis('off')
  plt.show()
  print("生成标题词云图完成！！")
  cursor.close()
  db.close()
  # f.close()

if __name__ == '__main__':
  openMySQLtoWordCloud()
