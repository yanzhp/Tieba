# fenci.py
# -*- coding: utf-8 -*-
import pymysql#打开数据库
from matplotlib.font_manager import *
import numpy as np
import pandas as pd
import jieba
from PIL import Image
import matplotlib.pyplot as plt
# from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud, ImageColorGenerator

def readDocument():
    '''
    获取文档对象，将文档内容按段落读入，并存入doc中
    '''
    db = pymysql.connect(host='localhost', user='root', password='yjs43520100', port=3306, db="spiders",
                         charset='utf8', )
    sql = "SELECT title FROM tiebaconlist"
    df = pd.read_sql(sql, db)
    serr = df['title']
    serr=serr.drop_duplicates()
    doc=''
    for para in serr:
        # print(para)
        doc = doc + para
    db.close()
    return doc

def segment(doc):
    '''
    用jieba分词对输入文档进行分词，并保存至本地（根据情况可跳过）
    '''
    seg_list = " ".join(jieba.cut(doc, cut_all=False)) #seg_list为str类型
    document_after_segment = open('分词结果.txt', 'w+',encoding='utf-8')
    document_after_segment.write(seg_list)
    document_after_segment.close()
    return seg_list


def wordCount(segment_list):
    '''
        该函数实现词频的统计，并将统计结果存储至本地。
        在制作词云的过程中用不到，主要是在画词频统计图时用到。
    '''
    word_lst = []
    word_dict = {}
    with open('词频统计(去停用词).txt','w',encoding='utf-8') as wf2:
        word_lst.append(segment_list.split(' '))
        for item in word_lst:
            for item2 in item:
                if item2 not in word_dict:
                    word_dict[item2] = 1
                else:
                    word_dict[item2] += 1

        word_dict_sorted = dict(sorted(word_dict.items(), \
        key = lambda item:item[1], reverse=True))#按照词频从大到小排序
        for key in word_dict_sorted:
            wf2.write(key+' '+str(word_dict_sorted[key])+'\n')
    wf2.close()

def drawWordCloud(seg_list):
    '''
        制作词云
        设置词云参数
    '''
    image = Image.open(r'123.png')
    color_mask = np.array(image)
    wc = WordCloud(
        #设置字体，不指定就会出现乱码，注意字体路径
        font_path="chGBK.ttf",
        #font_path=path.join(d,'simsun.ttc'),
        #设置背景色
        background_color='black',
        #词云形状
        mask=color_mask,
        #允许最大词汇
        max_words=200,
        #最大号字体
        max_font_size=100
    )
    wc.generate(seg_list) # 产生词云
    image_color = ImageColorGenerator(color_mask)
    wc.recolor(color_func=image_color)
    wc.to_file("savegif/titleciyun.jpg") #保存图片
    #  显示词云图片
    plt.imshow(wc, interpolation="bilinear")
    plt.axis('off')
    plt.show()#这里主要为了实现词云图片按照图片颜色取色
    # plt.figure()
    # plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    # plt.axis("off")


def removeStopWords(seg_list):
    '''
    自行下载stopwords1893.txt停用词表，该函数实现去停用词
    '''
    wordlist_stopwords_removed = []

    stop_words = open('chineseStopWords.txt')
    stop_words_text = stop_words.read()

    stop_words.close()

    stop_words_text_list = stop_words_text.split('\n')
    after_seg_text_list = seg_list.split(' ')

    for word in after_seg_text_list:
        if word not in stop_words_text_list:
            wordlist_stopwords_removed.append(word)

    without_stopwords = open('分词结果(去停用词).txt', 'w',encoding='utf-8')
    without_stopwords.write(' '.join(wordlist_stopwords_removed))
    return ' '.join(wordlist_stopwords_removed)

def drawStatBarh():
    '''
    画出词频统计条形图，用渐变颜色显示，选取前N个词频
    '''
    fig, ax = plt.subplots()
    myfont = FontProperties(fname='chGBK.ttf')
    N = 20
    words = []
    counts = []
    for line in open('词频统计(去停用词).txt',encoding='utf-8'):
        line.strip('\n')
        if len(line.split()) > 1:
            words.append(line.split(' ')[0])
            counts.append(int(line.split(' ')[1].strip('\n')))

    y_pos = np.arange(N)

    colors = ['#FA8072'] #这里是为了实现条状的渐变效果，以该色号为基本色实现渐变效果
    for i in range(len(words[:N]) - 1):
        colors.append('#FA' + str(int(colors[-1][3:]) - 1))

    rects = ax.barh(y_pos, counts[:N], align='center', color=colors)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    ax.set_yticks(np.arange(N))
    ax.set_yticklabels(words[:N],fontproperties=myfont)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_title('贴吧标题高频词',fontproperties=myfont, fontsize=17)
    ax.set_xlabel(u"出现次数",fontproperties=myfont)
    plt.savefig("savegif/贴吧高频词统计图.png")
    autolabel(rects, ax)
    plt.show()


def autolabel(rects, ax):
    """
    给条形图加上文字标签
    """
    #fig, ax = plt.subplots()
    for rect in rects:
        width = rect.get_width()
        ax.text(1.03 * width, rect.get_y() + rect.get_height()/2.,
            '%d' % int(width),ha='center', va='center')

if __name__ == "__main__":
    doc = readDocument()
    segment_list = segment(doc)
    segment_list_remove_stopwords = removeStopWords(segment_list)
    drawWordCloud(segment_list_remove_stopwords)
    wordCount(segment_list_remove_stopwords)
    drawStatBarh()